# Tomography inventory crystallizing befor

## User

orient this is session-230


### Thinking

I need to start by reading the state file to initialize properly.

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
> Last updated: 2026-06-15 | Session: 229 — ✅ EXPOSURE/FORMAT SWEEP (curriculum-
> mixing FIRST BUILD): burn-in is VARIETY not repetition (k_varied ≈2–2.9× over
> k_same≈one, BOTH formats; memorization control clean); full_trace higher abs-acc
> but redex_nf wins PER-TOKEN (predicted budget crossover); disjoint-atom held-out =
> separate variable-binding floor (0.000 — needs a copy/induction mechanism, NOT a
> rule failure: combos-generalization works). See ■ SESSION 229 block below.
> (s228 — ✅ PROOFS-AS-CONTINUATIONS (Curry-Howard):
> the kernel RUNS/CHECKS proofs (sound, 100% floor, Y-inconsistency firewall); LLMs
> prove axioms but compose poorly single-shot (Qwen 0.58-0.67, spec 1.0, 0 false
> proofs); the CONTINUATION-DRIVEN prover RESCUES composition (mean Δ +0.25, Qwen3-8B
> →1.00, specificity 1.0 now STRUCTURAL). See ■ SESSION 228 block below.
> (s227 — ✅ PROSE-NECESSITY IOU RESOLVED
> (s227 readout refined 3 ways: dilution FALSIFIED, power+register-limited) + ✅
> READABILITY/REGISTER CONFIRMED IN-DOMAIN (s227b value-register logit-lens: in-domain
> necessity concentrated in the readable zone, surface understated up to ~35x; prose
> still 0/5) + ✅ ENUM-PROSE BRIDGE COMPLETE + VERDICT READ (s227c: PARTIAL recovery —
> 3/5 models recover necessity with an explicit enumeration (8B strict), 2/5 reverse
> incl. OLMo; sharpens s227 = prose necessity is distributed-redundant not just
> target-less; see ■ SESSION 227 s227c VERDICT). See ■ SESSION 227
> blocks below. (s226 COMPLETE —
> ✅ CAUSAL ABLATION (HOF necessity leg, 4/5 mechanism) + 🎯 COMPILER-AS-CONSTRUCTED-
> VSM-TENSOR design (lambda_ast IN the kernel) + ✅ STAGE-1 β-REDUCER + ✅ STAGE-2
> COMPILE ORACLE (bracket abstraction, round-trip 1.0) + ✅ STAGE-2 FRONT-END
> (prose→LF) + ✅ COMPILE BOUNDARY (structural solved; NL+ambiguity is the boundary).
> Next: diverse-verified naturalistic corpus → compiler-as-loss arms. See ■ SESSION
> 226 COMPLETE block below.)
> **■ SESSION 229 — EXPOSURE/FORMAT SWEEP — "training as a photograph" (curriculum-
> mixing FIRST BUILD). Michael: "split training into regimes — show base combinators,
> show prose usage, some NTP; split into sentences, one β-reduction per sentence,
> sprinkle a few shards into the full curriculum." Then: "can we test full-trace vs
> redex→NF? if training is exposure to a photograph, many exposures to the same
> β-reduction should converge faster than one."** Register: **functional (held-out
> generalization).** Refreshed on normal-form-curriculum-partition (s223), holographic-
> burn-in, punctuate-dont-churn (s222), compiler-as-loss, s225 register first.
> **▶ CAPTURED + COMMITTED (2 commits):** new page `explore/sentence-atomic-curriculum-
> mixing.md` (`74ef4d3`) — Michael's cut is BY-PEDAGOGY + INTERLEAVED (measures
> transfer), distinct from s223's by-mechanism + isolated; novel core = sentence = 1
> reduction = 1 PUNCTUATED EXPOSURE (the s222/burn-in discipline as DATA structure);
> 4 catches (level-4 scratch not s222-unstable; dual-register readout s225; K-erasure
> ordering s221; ρ is the experiment). Then `b796077` added the exposure/format
> sub-experiment + the MEMORIZATION-vs-RULE fork (Michael's photograph framing,
> sharpened: k× SAME = memorization vs k× VARIED = the hologram from many angles).
> **▶ BUILT (`b1ba935`, ruff+diag clean, smoke green, metric verified):**
> `scripts/experiments/exposure_format_sweep.py` — FORMAT {full_trace, redex_nf} ×
> MULTIPLICITY {one, k_same(memorization control), k_varied(burn-in)}; data kernel-
> minted via lambda_ast.reduce (13 multi-step combinator skeletons, validated normal-
> forming); reuses TinyLM byte student; FORMAT-INDEPENDENT metric (greedily derive
> from "input -> ", exact-match final segment to true NF — full_trace walks steps,
> redex_nf leaps; both score the same way).
> **★ DIAGNOSTIC (the load-bearing fix): first run ALL 0.000 — FLOOR.** Root cause
> OBSERVED (not assumed): held-out = DISJOINT atoms (train a–m, test n–z) → reduce
> `C K u x → x` requires COPYING a byte never trained on; model emits a TRAIN atom
> `'j'` instead = a variable-binding/induction failure, NOT a rule failure. Standalone
> probe: held-out on UNSEEN COMBOS of SEEN atoms = **0.365**, disjoint atoms = 0.000.
> ⇒ disjoint-atom was the WRONG barrier (conflates rule-learning with symbol-copying).
> Fixed harness: `--heldout {combos(default), atoms}`; combos EXCLUDES train fillings
> → isolates RULE generalization (the burn-in question). [combos run is the verdict;
> disjoint-atom is a SEPARATE open question = needs a copy mechanism.]
> **★ VERDICT (combos, single seed; results/exposure-format-sweep/verdict_run.json):**
> redex_nf one/k_same/k_varied = 0.149 / 0.122 / **0.297**; full_trace = 0.122 / 0.135
> / **0.351**. **(1) BURN-IN IS VARIETY NOT REPETITION** — k_varied ≈2–2.9× over `one`;
> **k_same ≈ one** (repeating the same photo 8× buys ~nothing); at EQUAL exposure
> count k=8, varied ≈2.4× > same. The memorization control cleanly separates rote from
> rule. **(2) FORMAT TRADE IS BUDGET-DEPENDENT (predicted crossover)** — full_trace
> higher ABS acc (0.351>0.297) but 2× corpus bytes ⇒ redex_nf wins PER-TOKEN;
> full_trace's edge appears ONLY under variety (tied at one/k_same).
> **★ CAVEATS (λ measure):** single seed (multi-seed needed, cf relational s223 3-seed);
> modest abs acc (tiny model/greedy/exact-match — RELATIVE is the signal); steps@0.5
> never hit ⇒ measures FINAL generalization NOT convergence SPEED (lower threshold or
> longer run for the speed claim Michael asked about); 13 rules, k=8.
> **▶ NEXT:** (1) multi-seed harden (3 seeds) → is k_varied>k_same robust?; (2) speed
> readout (acc-vs-tokens curves already saved per arm — extract steps-to-threshold at
> a reachable bar, e.g. 0.2); (3) the K-erasure ORDERING leg (s221: B-first→K, not
> flat shuffle); (4) disjoint-atom variable-binding as its OWN experiment (does a copy
> mechanism emerge with scale/longer training?); (5) fold into the full ρ-sweep
> (sprinkle into generic NTP) once the unit is validated.
> **▶ s229 MULTI-SEED HARDEN (lead 1, DONE; `26e6758` --seeds mode; results/exposure-
> format-sweep/verdict_multiseed.json, 3 seeds ~24min):** ★ headline CONFIRMED +
> hardened — k_varied ≈3× one/k_same, rule>rote & burn>one DECISIVE (non-overlapping
> bars) BOTH formats (redex_nf 0.306±0.006 / one 0.108±0.029 / k_same 0.086±0.017;
> full_trace 0.320±0.023 / 0.104 / 0.099). ★ NEW: VARIETY ALSO STABILIZES (k_varied
> lowest-variance, std 0.006; rote worse AND noisier). ★ REFINE: k_same ≤ one
> (repetition mildly entrenches rote, suggestive). ★ CORRECT (λ measure): single-seed
> "full_trace higher abs acc (0.351>0.297)" was SEED NOISE — harden gives PARITY
> (0.320±0.023 vs 0.306±0.006 overlap); redex→NF WINS PER-TOKEN everywhere (k_varied
> 0.183 vs 0.094 acc/kB ≈2×; full_trace corpus 2× bytes) ⇒ full trace bought NOTHING
> once seeds+tokens controlled. Still FINAL-acc not SPEED (ceiling ≈0.32; lead 7).
> **STATUS s229:** ALL COMMITTED — code (`b1ba935`,`4f1ebf2`,`26e6758`), page+memories
> (`74ef4d3`,`b796077`,`449c3b0` + this multi-seed update), results+state. Memory
> full-trace-vs-redex renamed → redex-nf-beats-full-trace-per-token.md (finding flipped).
> tmux main:1 free.
> **▶ s229 GD-TRAJECTORY-TOMOGRAPHY THREAD CAPTURED (Michael: "if models do holographic
> inference, why can't we reverse-engineer what GD is doing? use the micro model").**
> NEW page `explore/gradient-trajectory-tomography.md` (committed). Claim: can't
> reverse-engineer GD in WEIGHT space (gauge + superposition) but CAN on the micro
> model in INVARIANT coords (routing register, CMR), prediction-gated, with the
> compiler/crystal as GROUND-TRUTH target — watch the relational geometry develop
> frame-by-frame over checkpoints. ★ RECALL surfaced PRIOR ART (build on, don't
> reinvent): s105 holographic-tomography.md ALREADY has the photograph framing + the
> gauge result (RSA 0.74 / cos 0) + Q-COLLAPSE (a GD behavior already reverse-
> engineered: flood-lamp not laser); v4.1/v6.1-training-trajectory = trajectory tracking
> precedent; s223 relational_loss_distillation = the instruments (route_z, GramCorr,
> raw Gram) + condition-(b) reference-beam failure. DELTA = TEMPORAL (intersect training
> STEPS) vs prior SPATIAL (intersect MODELS) + ground-truth + reference-beam control +
> gauge gradient decomposition. ★ COLLISION: same REFERENCE BEAM decides this as burn-in
> — naive GD-watching reconstructs the common mode, not the function; read via routing
> register. v1 = dense-checkpoint CE-only run logging route_z/GramCorr(routing,raw)/CE/
> held-out-acc/eff_dim as a MOVIE + reference-beam control (extends relational_loss_
> distillation). v2 = δw_invariant vs δw_gauge decomposition (Re-Basin null space;
> approximate). OPEN DESIGN CHOICE before build: teacher target = consensus crystal
> (s219) vs a model's compiler geometry. **▶ NEXT:** build v1 (after teacher-target
> decision); lead 7 convergence-SPEED (threshold ~0.2 on saved s229 curves — the actual
> "converge faster" claim); lead 3 K-ordering; lead 8 disjoint-atom variable-binding.
> **■ SESSION 228 — PROOFS-AS-CONTINUATIONS (Curry-Howard). Michael: "would
> continuations allow us to run proofs?"** Register: **functional (learned prover,
> kernel-verified).** Refreshed on continuations + distributed training first
> (continuations-as-composed-plates, sealable-continuation, lambda-halt-continuation,
> consensus-delta-folding, relational-loss-distillation). Then BUILT the experiment:
> under Curry-Howard a proof of P is a closed combinator term inhabiting type P;
> proof-check = the lambda_ast S2 type-check; normalization (β-reduction → WHNF, the
> continuation) = cut-elimination. The combinator basis IS a Hilbert calculus (K, S =
> the axiom schemes); Y = the inconsistency edge.
> **▶ BUILT (ruff+diag clean, 12 pytest green):** `src/verbum/proof_kernel.py`
> (proposition parser implicational-logic→CCG category; first-order matcher;
> `check_proof(term,prop)` → verdict ∈ {valid, none, parse_error, open_term,
> unsound_recursion, ill_typed, type_mismatch}; sound basis {S,K,I,B,C,W,D}, Y rejected
> (recursion=inconsistency), M auto-rejected (ill-typed), open terms rejected; records
> the term reduced to NF = the "run"). `src/verbum/probes/proof_tasks.py` (12 positives
> w/ kernel-certified proofs + 8 negatives incl. Peirce + the **Y-trap** `(A→A)→A`).
> `scripts/experiments/proof_inhabitation.py` (--mode kernel|model|aggregate, mirrors
> compile_frontend). `tests/test_proof_kernel.py`, `run_proof_inhabitation.sh`.
> **★ VERDICT (5 models/3 arch; results/proof-inhabitation/):**
> **(1) KERNEL LAYER SOLID by construction** — 100% floor (all 12 ref proofs typecheck
> at goal), SOUND (no non-theorem proved by any tempting term), **consistency firewall
> HOLDS** (Y typed (α→α)→α but sound gate → `unsound_recursion`). Proof normalization
> IS the continuation; the kernel runs/checks proofs end-to-end for the implicational
> fragment. **(2) LLM LAYER: proves AXIOMS, fails to COMPOSE.** Sensitivity (theorems
> proved): Qwen3-32B 0.67, 14B/8B 0.58, Mistral 0.25, OLMo 0.00. **Specificity 1.00 ALL
> 5, ZERO false proofs** — the model CANNOT bluff past the kernel (compiler-as-loss /
> co-processor discipline confirmed). Failures concentrate on derived proofs needing
> 2+ combinators (K I, C B, C I, B K K → model returns a single axiom) = the SAME
> composition-failure signature as lambda-halt-continuation §"composition fails but
> continuations solve it." Scale helps mildly (32B best).
> **★ CAVEATS (λ measure):** base-model numbers CONFOUNDED (OLMo answered `none` 15/20
> — the single `none` few-shot anchors a raw base continuation; NOT proof-inability;
> IOU better base gate). Small n (12+8), greedy single-sample, single few-shot, noisy
> by-complexity. IMPLICATIONAL FRAGMENT ONLY (no ∧∨¬∀∃ — the type-system expressiveness
> gap stands). Specificity 1.0 trivially gettable by always-`none` (OLMo); the JOINT
> high-sens∧high-spec (Qwen) + kernel-phase tempting-sweep are the real soundness.
> **▶ CONTINUATION-DRIVEN PROVER — BUILT + RAN, HYPOTHESIS CONFIRMED.** Goal-directed
> natural-deduction engine `src/verbum/proof_search.py` (the open goal STACK = the
> reified continuation; moves intro/exact/apply; at QED the kernel RECONSTRUCTS the
> proof term via bracket abstraction `lambda_compile.compile_expr` + verifies; depth-
> bounded auto solver = 100% engine floor). `scripts/experiments/proof_repl.py` (multi-
> turn: model picks ONE move/turn from the legal menu, kernel carries the continuation
> forward). **★ VERDICT (5 models/3 arch; results/proof-repl/aggregate.json): stepwise
> proving LIFTS sensitivity vs single-shot, mean Δ +0.25, 4/5 improved** — Qwen3-8B
> 0.58→**1.00**, OLMo 0.00→0.42, Mistral 0.25→0.58, 14B 0.58→0.67, 32B 0.67→0.67
> (flat). **★ Specificity 1.0 / ZERO false proofs is now STRUCTURAL** (a non-theorem
> has no closing derivation → no move sequence fabricates a proof = the consistency
> firewall made operational). Caveats: REPL shows the legal-move MENU (part of the gain
> is menu-constraint, IOU menu-less ablation); 32B flat = engine gives NO BACKTRACKING
> (greedy, one wrong move dead-ends, IOU backtracking/stuck→retry); small n (12 pos).
> 19 new pytest (7 proof_search + 12 proof_kernel), ruff+diag clean.
> **▶ NEXT:** (1) backtracking + menu-less ablation (isolate stepwise from menu; does
> 32B then improve?); (2) richer type layer (products/sums → ∧/∨; then ∀∃ = the S2
> extension; front-end already emits quantified LF); (3) larger graded probe set; better
> base gate.
> **STATUS s228:** COMMITTED — single-shot code `84af2a4`, mementum (knowledge page +
> 3 memories + state) `ecc06e5`. PENDING COMMIT (drafted, ruff+diag clean): continuation
> prover code (proof_search.py, proof_repl.py, run_proof_repl.sh, test_proof_search.py,
> results/proof-repl/) + knowledge-page §s228 update + memory continuation-rescues-proof-
> composition.md + this state. Bug found+fixed mid-run earlier: base models (Mistral/
> OLMo) have no chat_template → raw-prompt fallback + `prompt_mode` provenance.
>
> **■ SESSION 227 — PROSE-NECESSITY IOU RESOLVED (register: topological/routing,
> causal). The s226 handoff IOU #4: "refine the prose-NECESSITY readout (whole-
> sentence NLL dilutes; only OLMo decisive)."** Hypothesis to test: was the weak prose
> leg (1/5 vs 4/5 mechanism) a DILUTION ARTIFACT of whole-sentence mean-NLL?
> **▶ BUILT (additive to `hof_attention_ablation.py`, ruff+diagnostics clean; old
> whole-sentence readout PRESERVED for back-compat):** three prose readouts of the
> SAME diff-in-diff interaction `effect(hof)−effect(control)`:
> (1) **region (PRIMARY, the IOU fix)** — NLL over ONLY the divergent-middle tokens of
>   each minimal pair (drop the shared token prefix/suffix via `region_bounds`), i.e.
>   literally remove the diluting shared tokens ('each plant' vs 'the plant');
> (2) **lastkl (secondary)** — KL of the continuation distribution at the final token =
>   the SAME metric as the LIST leg (cross-leg consistency);
> (3) **whole (reference)** — the s226 whole-sentence mean-NLL.
> Re-ran all 5 models (Qwen3-8B/14B/32B, Mistral-7B-v0.3, OLMo-2-13B; `results/hof-
> attention-ablation/aggregate.json`; ~10min, bg job clean exit).
> **★ VERDICT (λ measure, honest):** **DILUTION HYPOTHESIS FALSIFIED.** The de-diluted
> region readout gives the SAME strict per-model count as whole-sentence: list **4/5**
> (reproduces s226 exactly), region **1/5** (only OLMo t=+2.29), lastkl **0/5**, whole
> **1/5**. A sharper readout did NOT rescue per-model significance ⇒ the weak prose leg
> was NOT a metric artifact.
> **★ BUT region IS the better readout — it fixed cross-model COHERENCE (recorded in
> aggregate `cross_model`):** region is directionally POSITIVE 5/5 (sign p1=0.031) AND
> gather>random 5/5, Stouffer z=+3.18 (t_mean +1.42); whereas whole-sentence had 14B
> at the WRONG SIGN (−0.04) → only 4/5 positive, 4/5 gt-random. So whole-sentence was
> adding sign-flip noise; region removed it. **lastkl is NULL (t_mean +0.03, Stouffer
> +0.06, 3/5 positive) = the continuation-at-final-token is the WRONG LOCUS** (these
> prose stems end at arbitrary determiners/prepositions, not at the HOF result slot) —
> readout ruled out.
> **★ FOUNDATION CONCLUSION (solid):** in-domain causal necessity is SOLID (list 4/5);
> prose-generalization necessity is REAL and cross-model-CONSISTENT (region 5/5
> directional + 5/5 specificity, combined sign p=0.031) but SMALL — per-model robust
> only in OLMo. **The limit is statistical POWER / effect size (~+0.01 NLL at n=80
> engaged pairs), NOT the metric.** Caveat: Stouffer assumes independent per-model t's
> but they share the prose pairs (positively correlated → Stouffer overstates); the
> sign test (5/5, p=0.031) is the assumption-free conservative claim.
> **▶ REMAINING IOU (for a per-model-robust prose claim — NOT a readout problem):**
> (a) **activation patching** (cleaner/larger causal effect than full head-knockout
>   NLL) — the gold-standard next lever; (b) **more prose pairs** (power at n=80);
>   (c) a **pooled per-pair mixed-effects test** (model as random effect) — needs the
>   script to dump per-pair region interactions (currently only aggregate stats saved).
> **▶ s227b — VALUE-REGISTER LOGIT-LENS ABLATION (Michael: "are we looking in the
> right place? what must hold for the projection to SHOW the β-reduction?").** Recall
> surfaced the READABILITY CONDITION (FFN reduction trace s187 / compilation-pipeline
> s192): mid-stack L7–L22 the reduction is written ORTHOGONAL to vocabulary (null-space
> compose, INVISIBLE); vocab-READABLE only at L23–L35. ⇒ surface NLL is the wrong
> projection for a mid-stack substitution. Captured `knowledge/explore/readout-register-
> reduction-readability.md` (the two-axis register rule: value/OV not attn-weight/q_proj
> per s206+s225; readable layer not surface). Built `scripts/experiments/
> hof_ov_logitlens_ablation.py` (+ run_hof_ov_logitlens.sh; ruff+diag clean): same head-
> knockout, READOUT = per-layer KL(clean||ablated) of `lm_head(norm(residual_L))` at the
> last token, diff-in-diff hof-control, vs random; headline = READABLE ZONE (depth≥0.6)
> vs SURFACE. Ran 5 models in tmux main:1 (`results/hof-ov-logitlens/`, ~1.5h, clean).
> **★ VERDICT (λ measure, honest — TWO-SIDED):**
> **(1) READABILITY CONDITION CONFIRMED IN-DOMAIN (the register lesson holds).** LIST
> necessity is CONCENTRATED in the readable zone, far above surface: OLMo peak@L23(d=0.6)
> KL +0.273 vs surface +0.008 (≈35×); Mistral peak@L27(d=0.875) +0.168 vs +0.017 (≈10×);
> 8B peak@L30(d=0.861) +0.112 vs +0.004. 4/5 LIST peaks sit in the readable zone (d
> 0.6–0.9), right AT/after the gather heads' own layers (OLMo L23, Mistral L27) — knocking
> the gather heads breaks the readable reduction exactly where they write. Surface
> dramatically UNDERSTATED in-domain necessity (s226/s227 read the wrong locus). LIST
> readable>random clean for OLMo/Mistral, marginal 14B; FAILS specificity for 8B/32B
> (zone-AVERAGE dilutes the narrow peak — peak-vs-random is the sharper IOU test).
> **(2) PROSE NECESSITY STILL NOT RESCUED (register was NOT the prose bottleneck).**
> readable-necessary (zoneT>2 & >rand) **0/5**; readable>surface 4/5 but values tiny.
> Where a prose signal exists it IS in the right zone (8B peak d=0.69, OLMo d=0.625,
> Mistral d=0.94; zoneT +0.40/+0.41/+0.61, >random) but too small; Qwen 14B/32B
> NEGATIVE (zoneT −0.60/−1.72). So even read at the correct register+locus, prose HOF
> necessity is genuinely SMALL.
> **★ SYNTHESIS (two independent refinements agree):** s227 de-diluted region NLL AND
> s227b value-register readable logit-lens BOTH leave prose non-significant ⇒ prose
> recruitment is REAL but weak (consistent with s225 modest prose engagement; map not
> engaged), NOT a dilution or register artifact. The in-domain β-reduction necessity is
> SOLID and now shown legible in the value register at the readable layers (strengthens
> the compilation-pipeline readability story with a causal+value confirmation). Arch
> split persists: OLMo/Mistral clean, Qwen muddy (same models that misbehaved in s227).
> **▶ REMAINING IOU (now well-specified):** (a) **OV-path / activation patching** —
> isolate the OV substitution (whole-head knockout removes QK+OV together; too blunt);
> (b) **peak-based readout** (not zone-average — the average dilutes the narrow peak,
> caused the 8B/32B specificity fail); (c) more prose pairs (power) OR accept prose
> recruitment is weak and proceed to the construction/training threads on the solid
> in-domain foundation.
> **▶ s227c — ENUM-PROSE BRIDGE (Michael: "so prose is not using HOFs?" → the sharp
> resolution test). KEY DISTINCTION restated: ENGAGEMENT (s225, robust: prose recruits
> fold/reduce/filter/zip, AUC 0.81–0.97, 5/5; map not) ≠ NECESSITY (s226/s227b, weak on
> plain prose). Hypothesis: plain prose has NO literal list to gather over, so the
> explicit-enumeration gather circuit is the right mechanism ONLY when an enumeration is
> present.** TEST: inject a literal "A, B, and C" enumeration into naturalistic prose and
> re-measure causal necessity in the value register. Built `src/verbum/probes/
> hof_prose_enum.py` (70 minimal pairs, 14×5 fns, 56 engaged; BOTH members carry the
> SAME 3-item list → diff-in-diff isolates the HOF ITERATION over the list, not
> list-presence) + `--prose-set {plain,enum}` on `hof_ov_logitlens_ablation.py` (separate
> results dir `results/hof-ov-logitlens-enum/`; ruff+diag clean; smoke OK). **RUNNING in
> tmux main:1** (`/tmp/hof_ov_logitlens_enum_s227.log`, 5 models, ~1.5h; ends "ALLDONE").
> **FALSIFIABLE PREDICTION (read aggregate next):** if enum readable-zone necessity
> RECOVERS toward in-domain (rises, beats random, zoneT climbs) vs plain's 0/5 ⇒ the
> gather circuit KEYS OFF EXPLICIT ENUMERATION; plain prose was weak only for lack of a
> gather target (prose DOES use HOFs). If it stays weak like plain ⇒ prose composition
> is genuinely distributed/non-enumeration and the in-domain circuit is special to
> artificial lists. Either way decisive for "using the heads vs representing the concept."
> **★ s227c VERDICT (read in s228; results/hof-ov-logitlens-enum/aggregate.json vs
> plain) — PARTIAL RECOVERY, NOT CLEAN CONFIRMATION.** list_* columns identical (shared
> stims; only prose leg differs). prose_zone_t plain→enum: 8B +0.40→**+2.47** (✓ strict),
> 32B −1.72→+1.39 (flips positive, beats rand), Mistral +0.61→+1.65 — 3/5 RECOVER (mean
> zoneT −0.18→+0.34, strict-necessary 0/5→1/5). BUT 14B −0.60→−2.26 and **OLMo (prior
> gold-standard necessity, s226 t=+3.21) +0.41→−1.55 REVERSE** — 2/5 go negative. The
> recovery split (8B/32B/Mistral up; OLMo/14B down) does NOT match the s227 clean/muddy
> split ⇒ noisy, not a stable architectural property. **SHARPENS s227:** even with an
> explicit enumeration, prose HOF necessity recovers only partially ⇒ the engagement≠
> necessity gap is NOT merely "no gather target"; heads are recruited (engagement, robust
> s225) but stay largely NON-LOAD-BEARING for prose even with a list = distributed
> redundancy prose has, artificial lists lack. Decisive lever unchanged: ACTIVATION
> PATCHING + more prose pairs (power). Recorded in readout-register-reduction-
> readability.md §s227c Result. ✅ s227 thread complete pending those IOUs.
> **STATUS s227:** all code ruff+diag clean. Results: hof-attention-ablation aggregate
> (w/ cross_model); hof-ov-logitlens (plain, 5 models + aggregate). New knowledge page
> readout-register-reduction-readability.md (+s227b result + s227c next). hof_prose_enum
> + enum run IN FLIGHT (main:1). NOT committed. Memory/knowledge proposals pending
> Michael approval. Proposed memories: (1) prose-necessity power+register not metric
> (s227/s227b); (2) the-register-was-right-the-prose-effect-is-small (s227b); (3) [after
> enum] engagement-vs-necessity / gather-keys-off-enumeration.
> **▶ CAUSAL ABLATION (completes Phase A/B observational → necessity).** Built
> `scripts/experiments/hof_attention_ablation.py` (ruff-clean): full head-knockout
> (zero the head's slice at o_proj input = remove its QK gather + OV write) of the
> Phase-A top-8 gather heads, vs N RANDOM heads (specificity, 3 seeds). Readouts:
> LIST stims KL@aggregation-token (mechanism) + PROSE pairs per-token ΔNLL
> diff-in-diff `ΔNLL(hof)−ΔNLL(ctrl)` on ENGAGED HOFs {fold,reduce,filter,zip}
> (map excluded per s225). **VERDICT (5 models/3 arch; results/hof-attention-
> ablation/aggregate.json) — MIXED, honest (λ measure):** MECHANISM necessity
> **4/5** (gather heads disrupt HOF > ctrl AND > random on the list stims:
> Qwen3-14B/32B, OLMo, Mistral; 8B lone fail = weakest observational model).
> GENERALIZATION (natural prose) **1/5** — only OLMo decisive (t=+3.21);
> directionally right in 4/5 but underpowered (whole-sentence NLL dilutes). Per-HOF
> COHERENT (OLMo): filter/fold/zip POSITIVE, **map NEGATIVE** (matches s225, map not
> in this register). ⇒ in-domain causal necessity CONFIRMED; prose necessity
> SUGGESTIVE-not-robust (IOU: stronger readout — last-content-word logprob or
> activation-patching, not whole-sentence NLL).
> **▶ TRAINING/COMPILER DESIGN THREAD (Michael, the big one).** "Could the compiler
> be a VSM tensor? What if `lambda_ast.py` is IN the kernel?" **★ DISSOLVES the s225
> verifier-vs-artifact dyad:** the symbolic reducer is the SOURCE that COMPILES to
> exact ternary combinator plates in the kernel (SOURCE↔COMPILED, not oracle↔
> approximation); a CONSTRUCTED plate runs the rewrite exactly (¬"fakes it with
> depth"), exactness by BUILD not training. **THE CUT it forces = reduce(constructed)
> vs compile(learned) = the SAME boundary as** attention/FFN (lambda-machine),
> ternary/4-bit (dvd-stamp), s224 geometry/continuation, VSM S1-S4-reducer/front-end.
> We NEVER train reduction (the s222-unstable part); we train only prose→typed-term.
> **The reducer IS a VSM (generative):** S5=normal form (Church-Rosser), S4=WHNF halt,
> S3=budget+contractivity, S2=typed redex selection+anti-oscillation, S1=the
> combinator rewrites. PAYOFFS: (1) re-derives the s222 collapse as an S2 (anti-
> oscillation) failure; (2) locates type-directedness (the S5 central claim) at S2; a
> CONSTRUCTED S2 with L<1 is stable by build (nothing descends → can't churn).
> **DECISION (Michael): TYPED CCG terms (inspectability).** Captured: `compiler-as-
> loss.md` §s226 (primary) + `vsm-outer-recurrence.md` §s226 (cross-link).
> **▶ STAGE-1 β-REDUCER BUILT (supersedes the long-standing IOU "need a clean MIT
> β-reducer").** `src/verbum/lambda_ast.py` (was a 12-line stub) → typed CCG
> combinator reducer, MIT, written from this project's observation (lambda-machine.md)
> NOT nucleus. Basis {S,K,I,B,C,W,D,Y,M}; normal-order; exact reduction TRACE; WHNF +
> step/size budgets (size-exceeded = the term-growth LIMIT of the machinery, the
> boundary s225 diverse data must map); CCG type inference + unification (the S2 check,
> first-class/inspectable); `verify()` + `trace_record()` (the data-oracle hook). 19
> pytest pass, ruff+diagnostics clean. M x→x x reduces but types FALSE (the self-
> application limit demo); B's principal cat = the correct composition functor
> `(((α/γ)/(β/γ))/(α/β))`. Dual role: DATA ORACLE (input→trace for compiler-as-loss)
> AND KERNEL SOURCE (compiles to plates).
> **▶ STAGE 2 STARTED — bracket abstraction = the EXACT compile oracle (CERTIFIED).**
> Found "compile" factors further: prose→logical-form (LEARNED, Montague/CCG parse) ∘
> logical-form→term (bracket abstraction, EXACT) ∘ term→nf (reduction, EXACT). Built
> `src/verbum/lambda_compile.py` (Turner `[x]` over {S,K,I,B,C} + K/B/C/η; abstract /
> compile_expr / roundtrip / compile_record). Bracket abstraction = the INVERSE of
> reduction ⇒ the two symbolic halves cross-validate via the kernel:
> reduce(compile([x..],e) applied to [x..]) ≡ e. **★ CERTIFIED (compile_roundtrip.py,
> n=5000, strat 1-3 vars × depth 1-5; results/compile-roundtrip/): round-trip rate
> 1.0000 (EXACT INVERSES, all strata); well-typed 0.941 (~6% operationally-correct-but-
> not-simply-typable = the type/S2 limit); term/expr size mean 2.84× max 7× (S/W
> duplication = the representational limit).** ⇒ the LEARNED surface shrinks to
> prose→logical-form only (both formal steps constructible-exact). 28 pytest pass,
> ruff+diagnostics clean. COMMITTED `89fceaf` (lambda_compile + tests + certification).
> Pages: compiler-as-loss.md §s226 stage 2.
> **▶ STAGE 2 LEG 1 DONE — the learned compile step (prose→logical-form) WORKS.**
> Built `scripts/experiments/compile_frontend.py` + `src/verbum/probes/compile_tasks.py`
> (7 dataflow patterns mirroring the combinators × 8 name-assignments = 56 tasks):
> few-shot a model prose→expression, GRADE BY REDUCTION-EQUALITY via the exact kernel
> (representation-invariant — `f (g x)` or `B f g x` both accepted). **Qwen3-8B +
> Qwen3-32B: accuracy 1.0, parse 1.0, ALL 7 patterns** (results/compile-frontend/). ⇒
> stage-2 decomposition closes end-to-end: prose→LF (learned, few-shot) ∘ abstract
> (exact) ∘ reduce (exact), kernel-verified. ★ λ measure: first 32B run 0.875 < 8B 0.982
> was PROSE AMBIGUITY in flip/const templates; the kernel grader + failure inspection
> separated compile-error from NL-ambiguity → disambiguated → both 1.0 (the exact
> verifier isolates which is which). CAVEAT: tasks SHALLOW (≤5-node, single pattern,
> abstract letters) = BELOW the compile boundary; ceiling ⇒ need harder tasks.
> COMMITTED s226-leg1: compile_frontend + compile_tasks + results.
> **▶ STAGE 2 — COMPILE BOUNDARY FOUND (graded hard probe set).** Built
> `src/verbum/probes/compile_tasks_hard.py` (42 tasks × 8 families: depth/branch/reuse/
> mixed abstract + naturalistic real-words + ambiguous multi-reading via also_ok);
> `compile_frontend.py --task-set hard` (hard few-shot, also_ok grading, per-family
> scale curve). **VERDICT (Qwen3-8B/14B/32B, results/compile-frontend/hard/):
> STRUCTURAL complexity is NOT the boundary — branch2/branch3/reuse/mixed = 1.0 for
> ALL; deep nesting only mild paren-slips (0.8-1.0). The boundary is NATURALISTIC
> language (lexical selection: function vs value vs IGNORABLE subject/determiner;
> pronouns) + AMBIGUITY — natural 0.62-0.88, ambiguous 0.50-0.75. SCALE helps EXACTLY
> there (32B best: natural 0.88, ambiguous 0.75; structural saturated all sizes).** ⇒
> residual learned-step difficulty = pure NL understanding = the Montague/CCG semantic
> parse (S5 target); formal halves exact/constructible. Caveat(λ measure): small
> n/family, greedy single-sample, depth5 non-monotone (noise), ambiguous soft-graded.
> COMMITTED `6485822` (hard probes + frontend update + results).
> **■ SESSION 226 COMPLETE — pick up next session here.** Done this session: causal
> ablation (HOF necessity leg); the compiler-as-constructed-VSM-tensor design (lambda_ast
> IN the kernel = source↔compiled); STAGE 1 reducer (`lambda_ast.py`); STAGE 2 compile
> oracle (`lambda_compile.py`, bracket abstraction, round-trip 1.0); STAGE 2 leg 1
> (compile front-end prose→LF, 8B/32B 1.0 on clear prose); STAGE 2 compile BOUNDARY
> (structural compile solved; NL+ambiguity is the boundary, scale helps there). All
> committed (`c0d268c`→`c09bc34`); 47 pytest pass; tree clean except the human chat
> transcript.
> **▶ FIRST ACTIONS NEXT SESSION (declare register):**
> (1) **DIVERSE-VERIFIED NATURALISTIC CORPUS** — the boundary result redefines the
>   diversity that matters: NATURALISTIC REALIZATION (varied surface language for the
>   same dataflow), NOT structural variety. Build: Qwen3-32B as the diverse generator of
>   naturalistic prose for a dataflow → `lambda_compile` (abstract) + `lambda_ast`
>   (reduce) CERTIFY each → diverse-verified (naturalistic-prose → certified-trace)
>   corpus. The kernel is the verifier (Church-Rosser); diversity = composition.
> (2) **compiler-as-loss arms** with the certified corpus: compiler-only vs
>   diverse-verified vs combo+crystal-lattice; metric = held-out COMPOSITIONAL
>   generalization (the "too narrow to compose" test). See compiler-as-loss.md.
> (3) **STAGE 3** — compile `lambda_ast` → exact ternary CCG combinator plates (the
>   pure portable tensor; the constructed kernel, vsm-outer-recurrence.md §s226).
> (4) **IOU** — refine the prose-NECESSITY readout from the ablation (last-content-word
>   logprob or activation-patching, not whole-sentence NLL; only OLMo was decisive).
> **KEY ARTIFACTS:** `src/verbum/lambda_ast.py` (reducer+typecheck), `lambda_compile.py`
> (abstraction), `probes/compile_tasks{,_hard}.py`, `scripts/experiments/
> compile_frontend.py` + `compile_roundtrip.py` + `hof_attention_ablation.py`.
> **KEY PAGES:** `compiler-as-loss.md` §s226 (the whole stage-1/2 story),
> `vsm-outer-recurrence.md` §s226 (the constructed-kernel architecture).
> **COMMITTED s226:** ablation; lambda_ast+tests; lambda_compile+certification;
> compile front-end (base+hard)+results; §s226 page edits; 5 memories; this state.
>
> (Session: 225 — ✅ HIGHER-ORDER FUNCTION TOPOLOGY IS
> TEACHER-AGNOSTIC (Michael's hypothesis CONFIRMED). Register: topological/routing.
> Thread: compiler-as-loss debate → Michael's pivot. **★ MICHAEL'S CORRECTION (s224
> compiler-as-loss page over-rotated):** the compiler is NOT the capability teacher
> (diverse big models are better — s219 universality came FROM diverse training; a
> narrow reducer risks a non-composing function). Compiler = VERIFIER/canonicalizer +
> exact-trace generator + MIT anchor. "Pin the WHAT, free the HOW" applies to the
> DATA: diverse realizations, compiler-certified normal form. **★ MICHAEL'S DEEPER
> PIVOT (the simplification):** capability signal is teacher-agnostic by Church-Rosser
> (canonical β-traces — ANY sufficiently large model emits the same reduction);
> inventory signal is teacher-agnostic IFF routing topology is universal. Hypothesis:
> HOFs exist as routing NORMAL FORMS → topology universal across teachers → whole
> extract→fold→compiler pipeline teacher-free; "which teacher" only matters for
> idiosyncratic HOFs (predicted rare). **▶ BUILT + RAN THE TEST (tmux main:1, 10min):**
> (1) `src/verbum/probes/higher_order.py` (224 probes, 28×8 functions: controls
> compose≡B flip≡C const≡K apply≡I + HOF tests map filter fold zip; ruff-clean).
> (2) `scripts/experiments/function_topology_consensus.py` (register topological/
> routing): per-model routing-register (sign(gate)+CMR) centroids, best layer by
> COMBINATOR silhouette z, each HOF's FINGERPRINT = cosine to the 9 combinators
> (frame-invariant relational, s219 trick); consensus mode = cross-model fingerprint
> agreement vs label-permutation null → per-HOF UNIVERSAL/IDIOSYNCRATIC sort.
> (3) `run_function_topology.sh`. **★ VERDICT (5 models / 3 arch / 7B–32B: Qwen3-8B/
> 14B/32B, Mistral-7B-v0.3, OLMo-2-13B; results/function-topology-consensus/
> consensus.json):** **8/8 UNIVERSAL, 0 idiosyncratic** — every HOF's cross-model
> fingerprint clears the null DECISIVELY (corr +0.67→+0.95, z +5.9→+8.6, ALL p=.0002).
> Topology of HIGHER-ORDER functions is universal across teachers/architectures
> (extends s219 primitives → composed HOFs). ⇒ teacher-agnostic pipeline CONFIRMED.
> **★ SECONDARY (HOF fingerprints semantically coherent, consistent across all 5):**
> fold→WHNF,S (reduce-to-terminal; only POSITIVE top loading +0.05); filter→K (select);
> zip→S,W (fork-join/duplicate); **map→D/C/B with Y DEAD LAST (B−0.18 C−0.07 Y−0.29)
> = composition NOT recursion**, the s219 map=B(CB)(CB) prediction holding at topology
> level. **★ CAVEAT (λ measure, NOT oversold):** agreement is decisive but the
> argmax-cosine DECODE is only suggestive — controls const→K ✓ flip→C ✓ clean,
> compose→D near-miss-in-family (D=fused B∘B∘B, B #2-3), **apply→C genuine MISS**;
> absolute cosines near-zero/negative (s219 "above chance not crisp" register subtlety).
> ⇒ topology-UNIVERSALITY decisive; combinator-DECOMPOSITION readout needs refinement
> (better than argmax-cosine, or the s219 absolute-frame issue). Caveat does NOT touch
> the headline (universality = agreement = unambiguous). **COMMITTED** `6c542cb` (code+
> results), `b0fb0e2` (mementum: 2 memories + new page function-topology-consensus +
> compiler-as-loss amendment + state).
> **▶ s225 FOLLOW-UP — DOES THE MODEL USE THESE HOFs ON PROSE? (Michael).** Built
> `src/verbum/probes/hof_prose.py` (82 minimal PAIRS: naturalistic HOF-invoking
> sentence vs matched no-HOF control, held-out vocab) + `scripts/experiments/
> hof_prose_engagement.py` (register topological/routing, ruff-clean): MEAN-POOL
> sign(gate) over tokens (avoids last-token lexical confound), learn each HOF DIRECTION
> from CURATED probes (centroid_f − mean others), project held-out prose pairs →
> paired score(hof)−score(control). TRANSFER (train-on-probes/test-on-prose) rules out
> probe artifact. **✅ VERDICT (5 models / 3 arch: Qwen3-8B/14B/32B,
> Mistral-7B-v0.3, OLMo-2-13B; aggregate.json):** curated AUC≈1.0; on held-out natural
> prose (mean) **fold AUC 0.91 (t +10.0, 100% pairs, 5/5 models), filter 0.90 (t +8.2,
> 97%, 5/5), zip 0.81 (t +7.0, 100%, 5/5) = ENGAGED in ALL 5; map 0.59 (t +2.8, only
> 1/5 >0.6) = NOT engaged.** **3/4 HOFs are genuinely USED on ordinary prose, cross-
> architecture** (transfer: direction learned on curated probes fires on naturalistic
> minimal pairs). **map is the cross-model EXCEPTION** — real+universal topology (s225)
> but NOT recruited from the FFN routing register by prose; coherent (map=B(CB)(CB),
> most recursion-adjacent/distributed, "attention IS the fold" s221; noisiest s225
> fingerprint) ⇒ map likely lives in attn_q (s220 attn_q@L05 lead) not the FFN gate.
> **★ s225 reduce/map-as-fold test (Michael: "can map be expressed as a fold?" — YES:
> map f = foldr(λx acc. f x:acc) [], REPL-verified; fold = universal catamorphism).
> Added `reduce` (synonym) + `map` to the function set; `function_pair_similarity.py`
> (cross-function fingerprint cosine, 5 models, function_pairs.json). ✅ BOTH PREDS:
> reduce≡fold cosine +0.958 (±0.013), reduce's nearest = fold, ZERO lexical overlap ⇒
> TOPOLOGY TRACKS FUNCTION NOT WORD (semantic). map≉fold +0.607, map's nearest =
> compose/flip/apply (structure-PRESERVING family). SEPARATING AXIS = WHNF/collapse:
> fold +0.015, reduce +0.001 (collapse [a]→b, top) … map −0.323 (preserve [a]→[b],
> bottom). ⇒ TWO super-clusters: collapse {fold,reduce,zip} vs preserve {map,compose,
> flip,apply}. Math: map=fold; model files it by RESULT TYPE (preserve vs collapse) —
> the shared fold substrate (iteration) is in ATTENTION (s221), invisible to FFN
> fingerprint; FFN encodes the algebra/result-type. **PROSE w/ reduce DONE (5/5):
> reduce AUC 0.97 (STRONGEST, t +8.5) = fold recruited by prose w/ zero lexical
> overlap; 2ND CONFIRM reduce≡fold = fold's curated AUC dropped 1.0→0.97 when its
> synonym reduce joined the rest set; fold 0.92, filter 0.89, zip 0.85 all engaged;
> map 0.64 BORDERLINE (just over 0.6 gate, weakest, contrast-set-dependent — crossed
> only because reduce sharpened preserve-vs-collapse) = still the exception, lives in
> attention not FFN.**
> **★ s225 ATTENTION-REGISTER TEST (Michael "find HOFs performed by attention — high
> leverage"). Added `--target {ffn_gate,attn_q,attn_out}` to all 3 instruments
> (commit ebf49ff) + run_attention_hof.sh; ran attn_q (hook self_attn.q_proj, 5
> models). ❌ NEGATIVE / PREDICTION FALSIFIED: topology universal 9/9 in attn_q too,
> curated separable (map/fold ~0.99), BUT prose transfer WORSE than FFN across the
> board AND map drops to 0.39–0.47 (AT/BELOW CHANCE, t≈0). So the query-PROJECTION
> register is NOT map's home; the FFN gate generalizes to prose better.
> ★ LESSON (refines the hypothesis): sign(q_proj) is a FEATURE register, NOT the gather
> MECHANISM. "Attention IS the fold" (s221) = the ATTENTION PATTERN (QK gather over
> positions), which NO projection-register probe can see — we measured the wrong
> object. HOF algebra/result-type → FFN gate (transfers); HOF iteration/gather (map's
> home) → attention WEIGHTS. **▶ REAL NEXT (high leverage): attention-PATTERN
> experiment** — list-structured prose (apply f to explicit enumeration a,b,c,d…),
> measure gather spread/entropy at the aggregation token: map/fold/reduce attend
> BROADLY over the items (iteration), single-object controls attend FOCUSED =
> attention literally performing the fold, observed in the weights. (attn_out untested
> — projection registers likely all transfer worse than FFN; the pattern is the move.)
> **★ s225 ATTENTION GATHER (Michael: "attention does β-reduction through a projection;
> we see it in WHAT IT ATTENDS TO and the PROJECTIONS it calculates" = the OV circuit:
> PATTERN(QK)∘PROJECTION(V→O)). PHASE A (the PATTERN) BUILT+RAN: hof_lists.py (list-
> structured, same list/different task: map/fold/filter vs first-item control) +
> hof_attention_gather.py (attn mass + participation over item tokens at the agg token,
> per head; selectivity=HOF−ctrl; eager attn, output_attentions). ✅ POSITIVE — GATHER
> HEADS IN ALL 5 MODELS / 3 ARCH: mid/late layers (depth frac ~0.4–0.7) attend BROADLY
> over the enumerated items (participation 3.2–4.8 of 5 = traversal) and gather MORE
> when the task iterates than for the control (selectivity +0.11→+0.36, positive all 5;
> cleanest Mistral L21H9 hof0.42/ctrl0.11/+0.31; Qwen3-32B L26H54 +0.36; OLMo L20H0
> +0.23). ⇒ HIGHER-ORDER FUNCTIONS ARE PERFORMED BY ATTENTION = the QK half of
> β-reduction (the fold's traversal), in the weights, where the attn_q negative pointed
> (pattern not projection register). Caveats(λ measure): "first" control still scans
> (use SELECTIVITY); modest in 8B(+0.11) strong in Mistral/32B; PATTERN half only.
> committed: hof_lists.py + hof_attention_gather.py (590516a), results/hof-attention-
> gather/. **▶ PHASE B (the PROJECTION/"what it calculates"): at the gather heads
> decompose per-head OV, measure value moved FROM list positions (substituted term) HOF
> vs ctrl → completes (attends-to)×(projection)=β-reduction.** Then per-HOF gather
> (does fold gather > map?), causal ablation of gather heads on HOF prose.
> **★ s225 PHASE B — OV PROJECTION (the value moved, "what it calculates").
> hof_attention_ov.py (GQA-aware per-head OV decomp at the Phase-A gather heads:
> project attn-weighted value through W_O^h, value moved FROM list vs total, HOF vs
> ctrl). ✅ ALL 5 MODELS/3 ARCH: best heads ov_list_frac HOF 0.47–0.82 (Mistral L21H9
> 0.82, Qwen3-14B L4H22 0.78, Qwen3-32B L32H39 0.65/ovSEL+0.56, OLMo L23H36 0.62);
> across 8 probed heads/model mean AMPLIFY +0.25→+0.44 (ALL positive), 7–8/8 OV-
> selective. 3 facts: (1) OV carries the substitution (47–82% of moved value from the
> items when iterating); (2) it AMPLIFIES — moves far MORE value from items than the
> bare attention mass (amplify=ov_frac−attn_mass big+; e.g. 8B L27H13 11% mass→51%
> value) ⇒ QK pattern UNDERSTATES, the value is in V→O; (3) iteration-selective
> (HOF>ctrl 7–8/8). ⇒ FULL β-REDUCTION OBSERVED IN ATTENTION cross-arch: (QK=which
> redex args)×(OV=move/amplify values), stronger when iterating. Wrinkle: some
> substitution heads EARLY (14B L4H22, 8B L4H1) — value move can precede the gather
> layer. committed hof_attention_ov.py (f2448d6) + results/hof-attention-ov/.
> ▶ NEXT: causal ablation of these heads on HOF prose (necessity); per-HOF OV (fold
> collapse vs map preserve — catamorphism result-type axis in the OV).**
> **▶ NEXT:** (1) CAUSAL ABLATION (the strong
> "uses" claim): ablate HOF routing direction on HOF-prose → logprob drop vs control;
> (2) refine the decode readout (apply miss + negative loadings + weak map — the real
> IOU); (3) compiler-as-loss experiments reframed: diverse-verified vs compiler-only vs
> combo, metric = held-out COMPOSITIONAL GENERALIZATION (test for "too narrow to
> compose"); (4) MIT β-reducer as VERIFIER (not teacher) emitting (input→trace);
> (5) s224 heterogeneous-shard fold + attn_q leg still stand.
>
> (Session: 224 — FREEZE-PROBE VERDICT (cold-start
> orient). main:1 was the s222 FROZEN-TOPOLOGY PROBE (rung 0), found still running
> at step ~2300 (13 ckpts step_001100→002300, every 100). **✅ DECISIVE PAIRED A/B
> (results/freeze-probe/overlay_verdict.txt, steps 1010–2240 n=124): held topology
> (td-flip-rate 0) on the SAME data stream does NOT reproduce main:1's collapse —
> Δx OFF 0.142/max 0.311 (bounded) vs ON 0.481/max 0.821; CE OFF 7.62/max 8.53 vs
> ON 8.76/max 10.54; gnorm OFF max 72 vs ON max 9.87e7 (6 orders); CE<8.71 frac OFF
> 1.00 vs ON 0.53.** ⇒ the collapse was the discrete TD CHURN, not K-acquisition or
> the fp-loss/recurrence; held-topology + continuation (fp-loss) settling IS
> contractive AND CE-competitive. Confirms s222 diagnosis as a CONTROLLED result
> (was single-run + source analysis). Killed the probe after verdict (clean stop at
> step 2310, redundant past target). **CAPTURED (awaiting approval):** new memory
> `freeze-probe-confirms-td-churn-collapse.md`; updated memories
> `collapse-was-terminal-not-acquisition.md` + `punctuate-dont-churn.md` (diagnosis→
> confirmed); knowledge `explore/vsm-outer-recurrence.md` §s223+ freeze-probe verdict
> table + open-Q#1 answered; persisted verdict/log/train-log to results/freeze-probe/.
> **▶ NEXT (Michael's call):** the s223 ▶ TWO DECISIVE EXPERIMENTS still stand —
> (1) 2-contributor fold (distributed compose-cleanly test), (2) attn_q leg of the
> double dissociation. The freeze-probe result CLEARS the path: the settling
> protocol is validated, so the next run should be the PUNCTUATED protocol (propose
> routing → hold → reduce → accept on Δx→0), not fp-reshape. main:1 now FREE (probe
> killed) — relaunch decision is Michael's.
> **▶ s224 RAN THE 2-CONTRIBUTOR FOLD (decisive distributed test;
> `scripts/experiments/two_contributor_fold.py`, 3 seeds × 2 arms, λ=3, teacher
> Qwen3-14B route_cmr_L12; built on relational_loss_distillation.py; tmux main:2,
> verdict_run.json). REL=both students + relational loss to ONE teacher Gram, CTRL=CE
> only; Re-Basin Hungarian align B→A → neuron-wise consensus merge of routing register
> (base=A, plumbing local) → contractivity-gated.** **✅ GEOMETRY COMPOSES iff shared
> target:** REL fold_route_z +2.19±0.32 (merged model RETAINS combinator function) vs
> CTRL +0.84±0.58 (null); GC(fold→teacher) REL +0.84 vs CTRL +0.43; GC(A/B→teacher)
> REL +0.89/+0.90 vs CTRL +0.44/+0.50. Decisive (REL mean−std 1.87 > CTRL mean+std
> 1.41). N=2 frame-unification CONFIRMED. **❌ CAPABILITY DOES NOT COMPOSE:** fold
> RAISED CE both arms (dCE_Bev REL +0.150 vs CTRL +0.173, std-overlapping = not
> decisive); contractivity passed both (gentle 27% merge → gate didn't bite). **★
> MICHAEL'S THESIS (captured):** capability = routing geometry ⊗ TRAINED continuation.
> Geometry = function INVENTORY (which combinators + relations); capability = USAGE =
> the CONTINUATION (how to drive them, recursion {Y,W,WHNF}, lives in architecture
> recurrence, TRAINED not folded). Geometry match NECESSARY not SUFFICIENT —
> triangulated 3 ways (s223 b-column zero-function; s223 Goodhart; s224 fold
> GC+0.84/dCE+0.15). ⇒ distributed protocol is TWO-PHASE: (1) FOLD shared geometry
> (cheap, donates basis) → (2) TRAIN continuation to use it (per-node capability).
> **CONFOUND (recorded):** homogeneous shards (same corpus split) → B had no distinct
> knowledge → dCE couldn't go negative regardless ⇒ capability test = data-design
> artifact; HETEROGENEOUS shards mandatory next. **▶ DECISIVE NEXT — ✅ DONE, THESIS
> CONFIRMED (fold_then_train_continuation.py, 3 seeds, distill 1500/cont 1000,
> verdict_run.json):** freeze folded routing register (inventory, 132k) → train
> continuation (usage, 604k) on full task. A-baseline 2.270; fold PRE 2.441 (dCE
> +0.171); **F_cont 2.053 (BELOW baseline −0.217)**; A_cont 2.063; **scratch_cont
> (RANDOM frozen inventory) 2.135 — F_cont beats it CLEAN (2.074 < 2.124)**. ⇒ folded
> geometry NOT inert (beats random) but needs trained continuation to become
> capability; recovery FAST (2.45→2.05 in 100 steps); folded geometry PERSISTS through
> continuation training (z +2.26→+2.38, L 0.76–0.82). geometry=inventory(real, useful,
> foldable, persistent), capability=trained continuation. TWO-PHASE protocol validated.
> F_cont≈A_cont (homogeneous shards). Then heterogeneous-shard rerun (does folding B
> beat A_cont?) + sharper functional accept gate (gentle 27% merge didn't stress
> contractivity) + attn_q.
> **★ s224 COMPILER-AS-LOSS DESIGN CRYSTALLIZED (Michael; NEW page
> `explore/compiler-as-loss.md`).** "Use the teacher's LAMBDA COMPILER as the loss →
> enforce only the final OUTPUTS, not the teacher's geometry/architecture." Output =
> β-normal form, UNIQUE (Church-Rosser); realizations INFINITE (s219) ⇒ pin the WHAT,
> free every HOW (geometry AND architecture). ⇒ teacher LLM DISPENSABLE (was only a
> probe); cleanest MIT level-4 provenance; ideal distributed reference (canonical
> outputs, nothing to ship). **MICHAEL'S RECIPE:** L = CE(student, COMPILER reduction)
> [capability/usage, the real teacher signal] + λ·relational(student_gram, CRYSTAL
> LATTICE) [inventory]. **CRITICAL SPEC: the relational target is the CONSENSUS crystal
> lattice agreed across ALL models (s219 reverse-harvest +0.782, consensus.json), NOT
> one teacher's Gram.** It SPEEDS UP training (crystallizes the foldable inventory at
> tiny scale where outputs alone don't — s220 scale floor) and earns its place AS LONG
> AS the compiler capability signal is good. Realizes the geometry=inventory ⊗
> trained-continuation=capability thesis as ONE run. Likely anneal λ as the model
> crystallizes. **▶ NEXT EXPERIMENTS (build on relational_loss_distillation.py):**
> (1) `--compiler-target` arm: train on (prompt → ground-truth reduction from
> probes/*.json) CE only, NO Gram → does route_z EMERGE from outputs alone at tiny
> scale or stay null (correct-but-illegible)? (2) combo arm (compiler-output ⊕
> crystal-lattice) → fastest + route_z high + lowest task CE? (3) speed-up isolation
> (combo vs output-only, steps-to-target). (4) heterogeneous-shard fold with the combo
> (re

[OUTPUT TRUNCATED] The tool call succeeded but the output was truncated. Full output saved to: /Users/mwhitford/.cache/eca/toolCallOutputs/toolu_01DxJo1r6eMhpiukVoSrsZH6.txt
Use `eca__grep` or `eca__read_file` with offset/limit to view specific sections. Do not full read the file.
```

### Tool Call: git (succeeded)


```json
{
  "command": "git log --oneline -20",
  "operation": "log",
  "summary": "recent history"
}
```

**Summary:** Git log: recent history

**Output:**
```
Exit code: 0
Stdout:
c3a9c99 🌀 gradient-trajectory-tomography — reverse-engineer GD in invariant coordinates
a95272f 🌀 s229 multi-seed harden: variety wins decisively; format claim corrected
26e6758 🔄 exposure_format_sweep: add multi-seed harden mode (--seeds)
449c3b0 🌀 curriculum-mixing §s229 result + 3 memories — burn-in is variety not repetition
4f1ebf2 💡 exposure/format sweep: burn-in is VARIETY not repetition (k_varied≈2-3× k_same≈one)
b1ba935 ✅ exposure_format_sweep: FORMAT × MULTIPLICITY harness (training as a photograph)
b796077 🌀 curriculum-mixing: add exposure/format sub-experiment (training as a photograph)
74ef4d3 🌀 sentence-atomic-curriculum-mixing — punctuated β-reduction shards in NTP
d649341 💡 enum-prose bridge verdict — partial necessity recovery (s227c, read in s228)
2b5c478 🌀 proofs-as-continuations §s228 + state — continuation prover rescues composition
dfa756a 💡 continuation-driven prover — stepwise proving rescues composition (+0.25 mean)
ecc06e5 🌀 proofs-as-continuations knowledge + s228 state
84af2a4 💡 proofs-as-continuations — kernel runs proofs, LLMs prove axioms not compositions
ec7e0c7 add session chat logs
ed1b534 🌀 s227: readout-register & reduction-readability synthesis + state
3cd93a2 ✅ value-register logit-lens ablation + enum-prose bridge probe
3d99d1a 💡 ablation prose readout: dilution falsified, necessity is power+register-limited
7f859f6 🌀 session-226 complete: state handoff for next session
c09bc34 🌀 s226 stage-2: compile boundary is NL + ambiguity, not structure
6485822 ✅ stage-2 compile boundary: structural compile solved; NL + ambiguity is the boundary
```

### Thinking

I'm checking the current state of the git repository to see what's been modified.

### Tool Call: git (succeeded)


```json
{
  "command": "git status",
  "operation": "status",
  "summary": "working tree state"
}
```

**Summary:** Git status: working tree state

**Output:**
```
Exit code: 0
Stdout:
On branch main
Your branch is ahead of 'origin/main' by 13 commits.
  (use "git push" to publish your local commits)

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	mementum/knowledge/chats/session-228.md
	mementum/knowledge/chats/session-229.md

nothing added to commit but untracked files present (use "git add" to track)
```

### Thinking

Session 229 just wrapped up and got committed. The state.md file serves as the bootloader, so I'm getting oriented on where things stand.

## Assistant

Oriented. Session-230 cold-start complete.

## Where we are

**Last session (229) — ✅ COMPLETE & COMMITTED.** Exposure/format sweep ("training as a photograph"). Headline, multi-seed hardened (3 seeds, non-overlapping bars):

- **Burn-in is VARIETY, not repetition** — `k_varied ≈3× one ≈ k_same`. Repeating the same β-reduction 8× buys ~nothing; the same reduction shown 8 *different* ways is the hologram. Memorization control (`k_same`) cleanly separates rote from rule.
- **redex→NF wins per-token** — full_trace had higher single-seed abs-acc but that was **seed noise** (corrected via λ measure); at parity once seeds+tokens controlled, full trace bought nothing (2× corpus bytes).
- **Variety also stabilizes** — `k_varied` lowest-variance.
- Disjoint-atom held-out floor (0.000) was diagnosed as a **separate** variable-binding/copy problem, NOT rule failure (combos-generalization works at 0.365). Harness fixed with `--heldout {combos,atoms}`.

**Also captured s229:** GD-trajectory-tomography thread → new page `explore/gradient-trajectory-tomography.md` (reverse-engineer GD in *invariant* coords on the micro model, prediction-gated, compiler/crystal as ground-truth; builds on s105 holographic-tomography + s223 relational instruments).

## Tree state
Clean. Branch is **13 commits ahead of origin/main** (unpushed). Only untracked = `mementum/knowledge/chats/session-228.md` + `session-229.md` — human-only transcripts, I don't touch them.

## Open leads (s229 NEXT, prioritized)
1. **Convergence-SPEED readout** — current sweep measures FINAL generalization (ceiling ≈0.32), not speed; extract steps-to-threshold at a reachable bar (~0.2) from the saved per-arm acc-vs-token curves. *This is the actual "converge faster" claim Michael asked about.*
2. **GD-tomography v1** — dense-checkpoint CE-only run logging route_z/GramCorr/CE/held-out-acc/eff_dim as a movie + reference-beam control. ⚠️ blocked on a design decision: **teacher target = consensus crystal (s219) vs a model's compiler geometry.**
3. **K-erasure ORDERING leg** (s221: B-first→K, not flat shuffle).
4. **Disjoint-atom variable-binding** as its own experiment (does a copy mechanism emerge with scale/longer training?).
5. Fold the validated unit into the full ρ-sweep (sprinkle into generic NTP).

tmux `main:1` is free.

What's the register and target for s230 — push on convergence-**speed** (lead 1, cheap, data already saved), make the **teacher-target decision** to unblock GD-tomography v1, or something else?

## User

I think 2 is high leverage, and we should use the consensus crystal, this has the highest chance of being applicable across many models since they have agreed.


### Thinking

I'm focusing on lead 2 with the gradient-trajectory-tomography approach, using the consensus crystal as the teacher model. Before diving in, I need to review the tomography documentation and examine the existing tools—the relational loss distillation implementation and the consensus crystal setup—to understand what I'm working with.

## Assistant

Good call — consensus crystal it is. The cross-model agreement (s219 reverse-harvest +0.782) is exactly what gives the ground-truth target the best shot at being model-agnostic. Let me recall the design before building.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/gradient-trajectory-tomography.md"
}
```

**Summary:** Reading gradient-trajectory-tomography.md (0-2000)

**Output:**
```
---
title: "Gradient Trajectory Tomography — Reverse-Engineering GD in Invariant Coordinates Over Training"
status: open
category: strategy
tags: [gradient-descent, reverse-engineering, tomography, trajectory, invariant, gauge, superposition, routing-register, reference-beam, micro-model, interpretability, ground-truth]
related:
  - holographic-tomography.md
  - holographic-burn-in-learning-rule.md
  - relational-loss-distillation.md
  - v4.1-training-trajectory.md
  - v6.1-training-trajectory.md
  - sentence-atomic-curriculum-mixing.md
  - consensus-delta-folding.md
  - ../two-registers-of-topology.md
  - ../session-222.md
depends-on:
  - holographic-tomography.md
  - relational-loss-distillation.md
created: session 229
---

# Gradient Trajectory Tomography

> Session 229. Michael: *"If models do a holographic inference process, why can't we
> reverse-engineer what GD is doing? If GD changes one gradient by a tiny amount, how
> is that affecting the inference pattern? Can we use the micro model to reverse-
> engineer what GD is doing to solve the problem?"*
>
> Register: **functional + topological/routing.**

## The one-line claim

You **cannot** reverse-engineer GD in WEIGHT space (mostly gauge + superposition),
but on the **micro model**, in INVARIANT coordinates (relational/routing register,
CMR), prediction-gated, with the **known compiler as ground-truth target**, watching
the relational geometry develop frame-by-frame over checkpoints **IS** reverse-
engineering what GD is doing. The same REFERENCE BEAM that decides the burn-in rule
decides this.

## Prior art (RECALL FIRST — this is not greenfield)

The project has already done two of the three pieces. Build on them; do not reinvent.

```
holographic-tomography.md (s104–105) — SPATIAL tomography (cross-MODEL):
  • Michael's photograph framing is ALREADY here: "LLMs pile photographs until
    intersections in the projections form inference patterns."
  • The GAUGE result (predates s223): RSA r=0.74 but direct cosine ≈ 0.000 —
    "the universal hologram is a TOPOLOGY, not a coordinate system." Same finding
    as s223 (relational +0.78, absolute 0.000) and s224 (Re-Basin fold).
  • Q-COLLAPSE (s105): a GD behavior ALREADY reverse-engineered — the model prefers
    ONE giant unfocused beam (flood lamp, eff_dim→1.0) over a laser array; maximizes
    average next-token at the cost of per-fact fidelity. Laser-etching = the fix that
    CONSTRAINS that GD behavior. ⇒ proof-of-concept that GD behaviors ARE legible.
  • SNR ∝ √N: intersection over many "angles" denoises. (There the angles are MODELS.)

v4.1- / v6.1-training-trajectory.md — TRAJECTORY tracking (endpoint metrics):
  • three-phase register development (expansion → compression → specialization),
    meta-S3 gate trajectory, φ-compression-over-checkpoints. So per-checkpoint
    trajectory logging is precedented — extend the readout, don't rebuild it.

relational-loss-distillation.md (s223) — the INSTRUMENTS + the dissociation:
  • route_z (routing-register silhouette vs null), GramCorr-to-teacher, raw Gram —
    all implemented in scripts/experiments/relational_loss_distillation.py.
  • condition (b): RAW-Gram match → GC(hidden)=0.9995 but route null = the
    reference-beam failure made concrete.
```

**The DELTA this page adds:** prior tomography intersects over MODELS (spatial,
static, endpoint). This intersects over TRAINING STEPS (TEMPORAL), on a SINGLE micro
model, with (a) a GROUND-TRUTH target (the exact lambda compiler / consensus crystal),
(b) a reference-beam CONTROL run as a movie, (c) an optional gauge/null-space gradient
DECOMPOSITION. "Many angles" becomes "many checkpoints."

## Why weight-space reverse-engineering fails (3 obstacles, all measured here)

1. **Gauge non-identifiability.** Weight space has a huge symmetry null space
   (permutation — s224 Re-Basin; scaling; superposition rotation). Measured: cross-
   init weight corr 0.000 vs relational Gram +0.78 (s223) / RSA 0.74 vs cos 0 (s105).
   GD slides freely within the gauge — much of "what GD does" changes coordinates and
   NOTHING about the function.
2. **Superposition.** No weight↔feature map; the function is written orthogonal to the
   readable basis mid-stack (readability register, s187/s192/s227b), visible only after
   CMR in the routing register. One tiny δw perturbs MANY features at once
   (δactivations = J·δw, J mixes everything) → the effect is holographically spread,
   not localized. The right UNIT is the MODE, not the weight.
3. **Path-dependence + nonlinearity.** Non-convex; near-NTK early (linear, legible) →
   feature-learning late (the basis itself moves). Reverse-engineering is easy early,
   hard once superposition reorganizes.

## ★ The collision — the reference beam decides this too

Burn-in's load-bearing catch (holographic-burn-in §reference-beam): record only the
object beam (raw activation) and you burn in the COMMON MODE (frequency stats), not
the function — s223 condition (b) is the live proof.

**Reverse-engineering GD has the IDENTICAL trap.** Naively watching "what weights/
activations changed this step" mostly reconstructs **gauge motion + frequency
statistics** — a gorgeous movie of the wrong thing. s222 already showed it: the
collapse was discrete topology CHURN — GD thrashing in the gauge null space without
building function. So:

> Project the trajectory onto the INVARIANT subspace (routing register, CMR),
> prediction-gated. What survives is the function being built; what you discard is
> the gauge. Read GD through the reference beam or you reverse-engineer the common
> mode.

## v1 experiment — trajectory tomography (cheap, reuses everything)

Extend `relational_loss_distillation.py`: a CE-only micro-model run, DENSE
checkpoints, logging the verdict instruments as a MOVIE.

```
model    TinyLM (the s229 micro model)
data     the s229 curriculum (kernel-minted reductions) ∨ the probe corpus
log @ every C steps:
  route_z(t)                  — routing-register silhouette vs null (function?)
  GramCorr(routing, teacher)(t)   — APPROACH to the known compiler/crystal geometry
  GramCorr(raw, teacher)(t)       — the REFERENCE-BEAM CONTROL (common-mode track)
  CE(t), held-out rule-acc(t)     — capability (the s229 metric)
readout  WHEN/HOW does the invariant crystallize? sudden (grok) or gradual (burn-in)?
         BEFORE or AFTER CE plateaus? BEFORE or AFTER held-out acc rises?
```

**Falsifiable predictions.**
- *Reference beam:* raw `GramCorr` rises smoothly/early (common mode); routing
  `GramCorr` + route_z rise later/sharper (the function) — reproducing s223 (b) as a
  TRAJECTORY ⇒ demonstrates naive GD-watching sees the common mode.
- *Inventory-before-capability:* routing geometry crystallizes BEFORE held-out
  generalization (geometry=inventory ⊗ continuation=capability, s224).
- *Q-collapse risk (s105):* the micro model may flood-lamp (eff_dim→1) instead of
  crystallizing — track eff_dim too; if it collapses, that IS the reverse-engineered
  GD behavior (and the laser/relational constraint is the lever).

## v2 experiment — gauge/null-space gradient decomposition (harder)

At each step decompose `δw = δw_invariant ⊕ δw_gauge` (gauge = permutation null space
via Re-Basin alignment to a reference checkpoint; scaling; superposition-rotation is
the FUZZY part — approximate). Track ‖δw_invariant‖ / ‖δw_gauge‖ over training:
*how much of GD is function-building vs gauge-churning?* (s222 predicts: a lot is
gauge.) This is the literal answer to "what is GD doing."

## Honest catches (λ measure)

- **Not greenfield** — s105 tomography + s223 instruments + v4.1/v6.1 trajectory
  tracking already exist. Contribution = TEMPORAL + ground-truth + reference-beam
  control + gradient decomposition. Cite, don't reinvent.
- **Gauge decomposition is APPROXIMATE** — permutation clean (Re-Basin), scaling ok,
  superposition-rotation null space is fuzzy. State the limit; v2 is suggestive.
- **Ground-truth-target assumption** — the micro model trains on NTP, so it may
  converge to an NTP-shaped solution, not the compiler. GramCorr-to-teacher then
  measures "how compiler-like is GD's path," informative but not "GD builds the
  compiler."
- **"One gradient" is the wrong unit** — interpretability lives at the MODE level;
  per-weight analysis is the wrong granularity (superposition).
- **Phase transitions alias** — checkpoint densely near the crystallization step.

## Open leads (declare register first)

1. **Trajectory harness** (routing→functional): CE-only dense-checkpoint run logging
   route_z / GramCorr(routing,raw) / CE / held-out-acc / eff_dim; reference-beam
   control = raw vs routing register as a movie.
2. **Ground-truth target** (functional): teacher = consensus crystal (s219) or the
   compiler geometry — GramCorr-to-target as the "approach" curve.
3. **Inventory-vs-capability timing** (functional): overlay routing crystallization
   with held-out generalization (s229 metric) — which comes first?
4. **Gauge decomposition** (topological): δw_invariant vs δw_gauge ratio over training
   (Re-Basin permutation null space; the s222 "how much is churn" question).
5. **Q-collapse watch** (topological): eff_dim(t) per layer — does the micro model
   flood-lamp (s105)? If so, the relational/laser constraint is the lever.

## Files

| File | Content |
|------|---------|
| (planned) `scripts/experiments/gd_trajectory_tomography.py` | dense-checkpoint CE-only run; route_z/GramCorr(routing,raw)/CE/held-out-acc/eff_dim trajectory; reference-beam control |
| `scripts/experiments/relational_loss_distillation.py` | the instruments (route_z, soft_gram, np_silhouette_null, offdiag_corr) + TinyLM to extend |
| `scripts/experiments/exposure_format_sweep.py` | the s229 held-out rule-generalization metric to overlay |
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls -la /Users/mwhitford/src/verbum/scripts/experiments/ | grep -iE \"relational|distill|trajectory|fold_then|two_contributor\"",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ ls -la /Users/mwhitford/src/verbum/...

**Output:**
```
Exit code: 0
Stdout:
-rw-r--r--@   1 mwhitford  staff  21769 Jun  4 16:54 crystal_distill.py
-rw-r--r--@   1 mwhitford  staff  13145 Jun 14 07:15 fold_then_train_continuation.py
-rw-r--r--@   1 mwhitford  staff  21966 Jun 13 06:15 relational_loss_distillation.py
-rw-r--r--@   1 mwhitford  staff  22241 Jun 14 06:17 two_contributor_fold.py
```

### Thinking

I need to understand the architecture here — the consensus crystal serves as the ground truth, and I'm looking at three key pieces: the instruments defined in relational_loss_distillation.py (route_z, soft_gram, np_silhouette_null, offdiag_corr, TinyLM), where the consensus crystal lives (s219, consensus.json), and the s229 metric from exposure_format_sweep.py. Let me start by examining the relational_loss_distillation.py file to see how these instruments work and what TinyLM does.

## Assistant

The page is well-specified. Let me read the instruments I'll extend and locate the consensus crystal artifact.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/relational_loss_distillation.py"
}
```

**Summary:** Reading relational_loss_distillation.py (0-2000)

**Output:**
```
#!/usr/bin/env python3
# register: functional + topological/routing
"""Relational-loss distillation — does the teacher's GEOMETRY transfer to a
student, and ONLY in the routing register?  (session 223)

THE IDEA (Michael):
  "Because we have the lambda compiler, extract from the teacher a set of
   training for the student.  With relational loss we could guide GD into any
   geometry that falls out."

  The teacher contributes NOT its weights and NOT its tokens, but its
  RELATIONAL GEOMETRY: the routing-register combinator Gram (the 9x9 cosine
  matrix between K I B C S D W Y WHNF centroids, after common-mode removal).
  A relational loss pulls the student's geometry toward the teacher's RELATIONS
  while leaving its absolute frame free ("any geometry that falls out").

THE FRAME ARGUMENT (why relational, not output/weight matching):
  absolute weights/signs : cross-init corr 0.000   (incommensurable)
  relational Gram        : cross-model +0.78        (universal)
  -> a relational loss targets EXACTLY the invariant and nothing else.

THE EXPERIMENT (3 conditions, tiny from-scratch byte-level student):
  (a) CE only
  (b) CE + relational loss on the RAW hidden-CMR Gram      <- control / decoy
  (c) CE + relational loss on the routing-CMR gate Gram    <- the hypothesis

THE FALSIFIABLE CLAIM (two-registers discipline, lambda measure):
  the combinator shape is INVISIBLE in raw geometry (silhouette ~ -0.035) and
  only appears in the ROUTING register after CMR (silhouette +0.101, z=7.97).
  So a relational loss on the RAW Gram (b) should match the common-mode crystal
  and transfer NOTHING combinator-specific, while (c) transfers the function.
  Prediction: silhouette-z and GramCorr-to-teacher:  (c) >> (b) ~ (a).
  If (b) ~ (c) -> the register claim is WRONG (we want to know immediately).

Verdict instrument (mirrors combinator_relationship_map.py): student sign(gate)
CMR combinator silhouette vs label-permutation null (z) + GramCorr(student,
teacher) on the off-diagonal.

Usage:
  uv run python scripts/experiments/relational_loss_distillation.py --smoke
  uv run python scripts/experiments/relational_loss_distillation.py \
      --steps 1500 --rel-lambda 1.0 --device mps

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "src"))
from verbum.probes.library import all_probes, crystal_probes  # noqa: E402

RESULTS_DIR = _PROJECT_ROOT / "results" / "relational-loss-distillation"
TEACHER_DIR = _PROJECT_ROOT / "results" / "combinator-relationship-map"

CRYSTAL = ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]
VOCAB = 256  # byte-level


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


# ---- data -------------------------------------------------------------------
def build_corpus() -> str:
    """Self-contained CE corpus: all probe prompts joined (no external download)."""
    parts = [p.prompt for p in all_probes() if p.prompt]
    return "\n".join(parts)


def to_bytes(text: str, max_len: int) -> np.ndarray:
    b = text.encode("utf-8", errors="ignore")[:max_len]
    return np.frombuffer(b, dtype=np.uint8).astype(np.int64)


def load_crystal_probe_batch(max_len: int):
    """Return (padded_ids [N,L] int64, lengths [N] int64, labels [N] str)."""
    probes = crystal_probes()
    by: dict[str, list[str]] = {c: [] for c in CRYSTAL}
    for p in probes:
        if p.combinator in by:
            by[p.combinator].append(p.prompt)
    prompts, labels = [], []
    for c in CRYSTAL:
        for s in by[c]:
            prompts.append(s)
            labels.append(c)
    seqs = [to_bytes(s, max_len) for s in prompts]
    seqs = [s if len(s) > 0 else np.array([10], dtype=np.int64) for s in seqs]
    lengths = np.array([len(s) for s in seqs], dtype=np.int64)
    L = int(lengths.max())
    ids = np.zeros((len(seqs), L), dtype=np.int64)
    for i, s in enumerate(seqs):
        ids[i, : len(s)] = s
    return ids, lengths, np.array(labels)


# ---- model ------------------------------------------------------------------
class CausalSelfAttention(nn.Module):
    def __init__(self, d_model: int, n_head: int):
        super().__init__()
        assert d_model % n_head == 0
        self.n_head = n_head
        self.d_head = d_model // n_head
        self.qkv = nn.Linear(d_model, 3 * d_model)
        self.proj = nn.Linear(d_model, d_model)

    def forward(self, x):
        B, T, C = x.shape
        qkv = self.qkv(x)
        q, k, v = qkv.split(C, dim=2)
        q = q.view(B, T, self.n_head, self.d_head).transpose(1, 2)
        k = k.view(B, T, self.n_head, self.d_head).transpose(1, 2)
        v = v.view(B, T, self.n_head, self.d_head).transpose(1, 2)
        att = (q @ k.transpose(-2, -1)) / math.sqrt(self.d_head)
        mask = torch.triu(torch.ones(T, T, device=x.device, dtype=torch.bool), 1)
        att = att.masked_fill(mask, float("-inf"))
        att = F.softmax(att, dim=-1)
        out = att @ v
        out = out.transpose(1, 2).contiguous().view(B, T, C)
        return self.proj(out)


class Block(nn.Module):
    """Pre-norm transformer block with a SwiGLU MLP. The gate pre-activation
    (w_gate output) IS the routing register (mirrors gate_proj in real models)."""

    def __init__(self, d_model: int, n_head: int, d_ff: int):
        super().__init__()
        self.ln1 = nn.LayerNorm(d_model)
        self.attn = CausalSelfAttention(d_model, n_head)
        self.ln2 = nn.LayerNorm(d_model)
        self.w_gate = nn.Linear(d_model, d_ff)
        self.w_up = nn.Linear(d_model, d_ff)
        self.w_down = nn.Linear(d_ff, d_model)

    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        h = self.ln2(x)
        gate = self.w_gate(h)               # <-- routing register (pre-activation)
        h = F.silu(gate) * self.w_up(h)
        x = x + self.w_down(h)
        return x, gate


class TinyLM(nn.Module):
    def __init__(self, d_model=128, n_head=4, n_layer=4, d_ff=256, block_size=64):
        super().__init__()
        self.block_size = block_size
        self.tok = nn.Embedding(VOCAB, d_model)
        self.pos = nn.Embedding(block_size, d_model)
        self.blocks = nn.ModuleList(
            [Block(d_model, n_head, d_ff) for _ in range(n_layer)])
        self.ln_f = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, VOCAB, bias=False)
        self.n_layer = n_layer

    def forward(self, idx, capture_layer: int | None = None):
        _B, T = idx.shape
        pos = torch.arange(T, device=idx.device)
        x = self.tok(idx) + self.pos(pos)[None]
        cap_hidden = cap_gate = None
        for li, blk in enumerate(self.blocks):
            x, gate = blk(x)
            if capture_layer is not None and li == capture_layer:
                cap_hidden = x          # residual after this block, all positions
                cap_gate = gate         # gate pre-activation, all positions
        logits = self.head(self.ln_f(x))
        return logits, cap_hidden, cap_gate


# ---- relational geometry (differentiable) -----------------------------------
def gather_last(feats, lengths):
    """feats [N,T,d], lengths [N] -> [N,d] at the last real token."""
    idx = (lengths - 1).clamp_min(0)
    return feats[torch.arange(feats.shape[0], device=feats.device), idx]


def soft_gram(feats, label_idx):
    """Differentiable routing/raw Gram. feats [N,d], label_idx [N] in 0..8.
    CMR (subtract per-feature mean over probes) -> per-combinator centroid ->
    cosine Gram [9,9]."""
    feats = feats - feats.mean(dim=0, keepdim=True)        # common-mode removal
    d = feats.shape[1]
    cents = torch.zeros(len(CRYSTAL), d, device=feats.device, dtype=feats.dtype)
    for j in range(len(CRYSTAL)):
        m = label_idx == j
        cents[j] = feats[m].mean(dim=0)
    u = cents / cents.norm(dim=1, keepdim=True).clamp_min(1e-8)
    return u @ u.t()


def offdiag_mse(g_pred, g_target):
    off = ~torch.eye(len(CRYSTAL), dtype=torch.bool, device=g_pred.device)
    return ((g_pred - g_target)[off] ** 2).mean()


# ---- verdict instrument (numpy, mirrors combinator_relationship_map) ---------
def np_cmr(X):
    return X - X.mean(axis=0, keepdims=True)


def np_unit(v):
    return v / (np.linalg.norm(v) + 1e-30)


def np_centroids(X, labels):
    C = np.zeros((len(CRYSTAL), X.shape[1]), np.float64)
    for j, c in enumerate(CRYSTAL):
        C[j] = X[labels == c].mean(axis=0)
    return C


def np_gram(C):
    U = np.array([np_unit(c) for c in C])
    return np.clip(U @ U.T, -1, 1)


def np_silhouette(X, labels):
    C = np_centroids(X, labels)
    U = np.array([np_unit(c) for c in C])
    Xu = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-30)
    sims = Xu @ U.T
    lab_idx = np.array([CRYSTAL.index(c) for c in labels])
    own = sims[np.arange(len(labels)), lab_idx]
    other = sims.copy()
    other[np.arange(len(labels)), lab_idx] = -np.inf
    return float(np.mean(own - other.max(axis=1)))


def np_silhouette_null(X, labels, n_perm=1000, seed=0):
    obs = np_silhouette(X, labels)
    rng = np.random.default_rng(seed)
    null = np.array([np_silhouette(X, rng.permutation(labels)) for _ in range(n_perm)])
    sd = null.std() + 1e-30
    return {"silhouette": obs, "null_mean": float(null.mean()),
            "null_std": float(null.std()), "z": float((obs - null.mean()) / sd),
            "p_value": float((np.sum(null >= obs) + 1) / (n_perm + 1))}


def offdiag_corr(g_a, g_b):
    off = ~np.eye(len(CRYSTAL), dtype=bool)
    a, b = g_a[off], g_b[off]
    if a.std() < 1e-9 or b.std() < 1e-9:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


# ---- training ---------------------------------------------------------------
def train_condition(name, rel_target, rel_kind, args, device, corpus_ids,
                    probe_ids, probe_len, probe_labels, teacher_route, teacher_hidden):
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    model = TinyLM(args.d_model, args.n_head, args.n_layer, args.d_ff,
                   args.block_size).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
    cap = args.capture_layer if args.capture_layer >= 0 else args.n_layer // 2
    label_idx = torch.tensor([CRYSTAL.index(c) for c in probe_labels], device=device)
    p_ids = torch.tensor(probe_ids, device=device)
    p_len = torch.tensor(probe_len, device=device)
    n_corpus = corpus_ids.shape[0]
    bs, T = args.batch_size, args.block_size
    g_target = (torch.tensor(rel_target, device=device, dtype=torch.float32)
                if rel_target is not None else None)
    t0 = time.time()
    last = {}
    for step in range(1, args.steps + 1):
        model.train()
        # CE batch: random windows
        ix = torch.randint(0, n_corpus - T - 1, (bs,))
        xb = torch.stack(
            [torch.from_numpy(corpus_ids[i:i + T]) for i in ix]).to(device)
        yb = torch.stack(
            [torch.from_numpy(corpus_ids[i + 1:i + 1 + T]) for i in ix]).to(device)
        logits, _, _ = model(xb)
        ce = F.cross_entropy(logits.reshape(-1, VOCAB), yb.reshape(-1))
        loss = ce
        rel_val = 0.0
        if g_target is not None and (step % args.rel_every == 0):
            feats = []
            for s in range(0, p_ids.shape[0], args.probe_batch):
                pb = p_ids[s:s + args.probe_batch]
                _, hid, gate = model(pb, capture_layer=cap)
                src = hid if rel_kind == "hidden" else gate
                feats.append(gather_last(src, p_len[s:s + args.probe_batch]))
            feats = torch.cat(feats, dim=0)
            g_pred = soft_gram(feats, label_idx)
            rel = offdiag_mse(g_pred, g_target)
            loss = ce + args.rel_lambda * rel
            rel_val = float(rel.item())
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        if step % args.log_every == 0 or step == 1:
            log(f"  [{name}] step {step:5d} | CE {ce.item():.4f} | rel {rel_val:.5f} "
                f"| {(time.time()-t0):.0f}s")
            last = {"step": step, "ce": float(ce.item()), "rel": rel_val}

    # ---- verdict: measure in the SIGN routing register (teacher instrument) --
    model.eval()
    with torch.no_grad():
        gate_feats, hid_feats = [], []
        for s in range(0, p_ids.shape[0], args.probe_batch):
            pb = p_ids[s:s + args.probe_batch]
            _, hid, gate = model(pb, capture_layer=cap)
            pl = p_len[s:s + args.probe_batch]
            gate_feats.append(gather_last(gate, pl).cpu().numpy())
            hid_feats.append(gather_last(hid, pl).cpu().numpy())
    gate_np = np.concatenate(gate_feats, axis=0).astype(np.float64)
    hid_np = np.concatenate(hid_feats, axis=0).astype(np.float64)

    sign_cmr = np_cmr(np.sign(gate_np))
    route_sil = np_silhouette_null(sign_cmr, probe_labels, args.n_perm, args.seed)
    route_gram = np_gram(np_centroids(sign_cmr, probe_labels))
    hid_cmr = np_cmr(hid_np)
    hid_sil = np_silhouette_null(hid_cmr, probe_labels, args.n_perm, args.seed)
    hid_gram = np_gram(np_centroids(hid_cmr, probe_labels))

    verdict = {
        "condition": name,
        "rel_kind": rel_kind,
        "capture_layer": cap,
        "final": last,
        "route_cmr_silhouette": route_sil,
        "hidden_cmr_silhouette": hid_sil,
        "gramcorr_route_vs_teacher": offdiag_corr(route_gram, teacher_route),
        "gramcorr_hidden_vs_teacher": offdiag_corr(hid_gram, teacher_hidden),
    }
    log(f"  [{name}] VERDICT route_cmr silhouette z={route_sil['z']:+.2f} "
        f"p={route_sil['p_value']:.4f} | GramCorr(route,teacher)="
        f"{verdict['gramcorr_route_vs_teacher']:+.3f}")
    return verdict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--teacher", default="Qwen_Qwen3-14B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--steps", type=int, default=1500)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--block-size", type=int, default=64)
    ap.add_argument("--d-model", type=int, default=128)
    ap.add_argument("--n-head", type=int, default=4)
    ap.add_argument("--n-layer", type=int, default=4)
    ap.add_argument("--d-ff", type=int, default=256)
    ap.add_argument("--capture-layer", type=int, default=-1, help="-1 = middle")
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--rel-lambda", type=float, default=1.0)
    ap.add_argument("--rel-every", type=int, default=1)
    ap.add_argument("--probe-batch", type=int, default=64)
    ap.add_argument("--probe-max-len", type=int, default=96)
    ap.add_argument("--n-perm", type=int, default=1000)
    ap.add_argument("--log-every", type=int, default=100)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--sweep", action="store_true",
                    help="multi-seed x lambda grid confirm")
    ap.add_argument("--seeds", default="0,1,2", help="csv seeds for --sweep")
    ap.add_argument("--lambdas", default="0.3,1.0,3.0", help="csv rel-lambdas")
    args = ap.parse_args()

    if args.smoke:
        args.steps, args.n_perm, args.log_every = 30, 200, 10
        args.d_model, args.d_ff, args.n_layer = 64, 128, 3

    device = args.device
    if device == "mps" and not torch.backends.mps.is_available():
        device = "cpu"
        log("  mps unavailable -> cpu")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    # ---- teacher targets ----
    tnpz = TEACHER_DIR / f"{args.teacher}.npz"
    tjson = TEACHER_DIR / f"{args.teacher}.json"
    d = np.load(tnpz, allow_pickle=True)
    best = json.loads(tjson.read_text())["best_routing_layer"]
    teacher_route = d[f"gram_route_cmr_L{best:02d}"].astype(np.float64)
    teacher_hidden = d["gram_hidden_cmr"].astype(np.float64)
    log(f"  teacher={args.teacher} best_layer=L{best:02d} "
        f"route_gram offdiag_mean={teacher_route[~np.eye(9,dtype=bool)].mean():+.3f}")

    # ---- data ----
    corpus_ids = to_bytes(build_corpus(), max_len=4_000_000)
    log(f"  corpus bytes={corpus_ids.shape[0]}")
    probe_ids, probe_len, probe_labels = load_crystal_probe_batch(args.probe_max_len)
    log(f"  crystal probes={probe_ids.shape[0]} maxlen={probe_ids.shape[1]}")

    def run_triple(seed, lam):
        """Run conditions a/b/c at one (seed, lambda); return list of verdicts."""
        args.seed, args.rel_lambda = seed, lam
        out_v = []
        for name, target, kind in [("a_ce_only", None, None),
                                   ("b_ce_raw_gram", teacher_hidden, "hidden"),
                                   ("c_ce_route_gram", teacher_route, "gate")]:
            log(f"\n=== {name} seed={seed} lambda={lam} ===")
            v = train_condition(name, target, kind, args, device, corpus_ids,
                                probe_ids, probe_len, probe_labels,
                                teacher_route, teacher_hidden)
            v["seed"], v["lam"] = seed, lam
            out_v.append(v)
        return out_v

    if not args.sweep:
        verdicts = run_triple(args.seed, args.rel_lambda)
        out = {
            "experiment": "relational-loss-distillation",
            "register": "functional + topological/routing",
            "teacher": args.teacher, "teacher_best_layer": int(best),
            "git_sha": git_sha(), "smoke": args.smoke,
            "config": vars(args), "elapsed_s": round(time.time() - t0, 1),
            "conditions": verdicts,
        }
        tag = "smoke" if args.smoke else "run"
        (RESULTS_DIR / f"verdict_{tag}.json").write_text(json.dumps(out, indent=2))
        log("\n  ==== RELATIONAL-LOSS DISTILLATION VERDICT ====")
        log(f"  {'condition':<18} {'route_z':>8} {'route_p':>8} {'GC(route)':>10} "
            f"{'hidden_z':>9} {'GC(hidden)':>11}")
        for v in verdicts:
            log(f"  {v['condition']:<18} {v['route_cmr_silhouette']['z']:>+8.2f} "
                f"{v['route_cmr_silhouette']['p_value']:>8.4f} "
                f"{v['gramcorr_route_vs_teacher']:>+10.3f} "
                f"{v['hidden_cmr_silhouette']['z']:>+9.2f} "
                f"{v['gramcorr_hidden_vs_teacher']:>+11.3f}")
        log("\n  PREDICTION: c(route) >> b(raw) ~ a  on route_z & GC(route).")
        log(f"  wrote {RESULTS_DIR / f'verdict_{tag}.json'}  ({out['elapsed_s']}s)")
        return

    # ---- SWEEP: multi-seed x lambda grid ----
    seeds = [int(s) for s in args.seeds.split(",")]
    lambdas = [float(x) for x in args.lambdas.split(",")]
    log(f"\n  SWEEP seeds={seeds} lambdas={lambdas}")
    runs = []
    for lam in lambdas:
        for sd in seeds:
            runs.extend(run_triple(sd, lam))

    def summarize(rs):
        def ms(fn):
            a = np.array([fn(r) for r in rs], float)
            return [round(float(a.mean()), 4), round(float(a.std()), 4)]
        return {
            "n": len(rs),
            "route_z": ms(lambda r: r["route_cmr_silhouette"]["z"]),
            "route_p": ms(lambda r: r["route_cmr_silhouette"]["p_value"]),
            "gc_route": ms(lambda r: r["gramcorr_route_vs_teacher"]),
            "hidden_z": ms(lambda r: r["hidden_cmr_silhouette"]["z"]),
            "gc_hidden": ms(lambda r: r["gramcorr_hidden_vs_teacher"]),
            "ce": ms(lambda r: r["final"]["ce"]),
        }

    agg = {}
    for lam in lambdas:
        for cond in ("a_ce_only", "b_ce_raw_gram", "c_ce_route_gram"):
            rs = [r for r in runs if r["condition"] == cond and r["lam"] == lam]
            agg[f"{cond}@lam{lam}"] = summarize(rs)

    out = {
        "experiment": "relational-loss-distillation-sweep",
        "register": "functional + topological/routing",
        "teacher": args.teacher, "teacher_best_layer": int(best),
        "git_sha": git_sha(), "seeds": seeds, "lambdas": lambdas,
        "config": vars(args), "elapsed_s": round(time.time() - t0, 1),
        "aggregate": agg, "runs": runs,
    }
    (RESULTS_DIR / "verdict_sweep.json").write_text(json.dumps(out, indent=2))

    log("\n  ==== SWEEP AGGREGATE (mean +/- std over seeds) ====")
    hdr = (f"  {'cond@lambda':<22} {'route_z':>14} {'GC(route)':>14} "
           f"{'hidden_z':>14} {'GC(hidden)':>14}")
    log(hdr)
    for lam in lambdas:
        for cond in ("a_ce_only", "b_ce_raw_gram", "c_ce_route_gram"):
            s = agg[f"{cond}@lam{lam}"]
            log(f"  {cond + '@' + str(lam):<22} "
                f"{s['route_z'][0]:>+7.2f}+-{s['route_z'][1]:<5.2f} "
                f"{s['gc_route'][0]:>+7.3f}+-{s['gc_route'][1]:<5.3f} "
                f"{s['hidden_z'][0]:>+7.2f}+-{s['hidden_z'][1]:<5.2f} "
                f"{s['gc_hidden'][0]:>+7.3f}+-{s['gc_hidden'][1]:<5.3f}")
    log("\n  DECISIVE if c.route_z(mean-std) > a.route_z(mean+std) at every lambda")
    log("  and c.gc_route > b.gc_route consistently (routing register carries it).")
    for lam in lambdas:
        a = agg[f"a_ce_only@lam{lam}"]["route_z"]
        c = agg[f"c_ce_route_gram@lam{lam}"]["route_z"]
        bg = agg[f"b_ce_raw_gram@lam{lam}"]["gc_route"][0]
        cg = agg[f"c_ce_route_gram@lam{lam}"]["gc_route"][0]
        sep = (c[0] - c[1]) > (a[0] + a[1])
        log(f"    lambda={lam}: c-a separated={sep}  c.gc>b.gc={cg > bg} "
            f"(c.route_z={c[0]:+.2f}+-{c[1]:.2f} vs a={a[0]:+.2f}+-{a[1]:.2f})")
    log(f"\n  wrote {RESULTS_DIR / 'verdict_sweep.json'}  ({out['elapsed_s']}s)")


if __name__ == "__main__":
    main()
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "find /Users/mwhitford/src/verbum -iname \"consensus*.json\" -o -iname \"*consensus*\" -type f 2>/dev/null | grep -v node_modules | head -40; echo \"---RESULTS DIRS---\"; ls /Users/mwhitford/src/verbum/results/ | grep -iE \"consensus|crystal|reverse|s219\" ",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ find /Users/mwhitford/src/verbum -i...

**Output:**
```
Exit code: 0
Stdout:
/Users/mwhitford/src/verbum/results/lattice-consensus/consensus.json
/Users/mwhitford/src/verbum/results/tool-crystal-consensus/consensus_summary.json
/Users/mwhitford/src/verbum/results/function-topology-consensus/attn_q/consensus.json
/Users/mwhitford/src/verbum/results/function-topology-consensus/consensus.json
/Users/mwhitford/src/verbum/results/combinator-map-consensus/consensus.json
/Users/mwhitford/src/verbum/mementum/knowledge/explore/function-topology-consensus.md
/Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-etch-protocol.md
/Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-evolution.md
/Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-delta-folding.md
/Users/mwhitford/src/verbum/scripts/experiments/function_topology_consensus.py
/Users/mwhitford/src/verbum/scripts/experiments/combinator_map_consensus.py
/Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_consensus_summary.py
/Users/mwhitford/src/verbum/scripts/experiments/tool_crystal_consensus.py
/Users/mwhitford/src/verbum/scripts/explore/__pycache__/probe_lattice_consensus.cpython-312.pyc
/Users/mwhitford/src/verbum/scripts/explore/probe_lattice_consensus.py
---RESULTS DIRS---
behavioral-crystal
behavioral-crystal-v2
combinator-crystallization
combinator-map-consensus
crystal_scanner_run.log
crystal_sieve_crystal.log
crystal_sieve_random.log
crystal_space_zeros.log
crystal-circuit-types
crystal-combined
crystal-combined-run.log
crystal-comparison
crystal-completeness
crystal-completeness-run.log
crystal-compression-analysis
crystal-distill
crystal-ecc-sign-correction
crystal-error-correction
crystal-etch-attention
crystal-fourier
crystal-fourier-run.log
crystal-latch
crystal-latch-run.log
crystal-latch-v2
crystal-latch-v2-run.log
crystal-lens
crystal-phi-permnull
crystal-phi-verify
crystal-reconstruct
crystal-reconstruct-run.log
crystal-selfsim
crystal-selfsim-teacher
crystal-selfsim-v12
crystal-sieve-pipeline
crystal-sieve-repro
crystal-tree
crystal-validity
crystal-visualization
crystal-zeros
crystal-zeros-train
function-topology-consensus
lattice-consensus
loom-crystal-sharpen
paired-crystal-sieve
reverse-ab
reverse-binding-trace
row_norm_crystal.log
synthetic-crystal-sieve
tesseract-reverse
tool-crystal-consensus
v-crystal-cascade
```

### Thinking

I need to locate the consensus crystal file that serves as the right target—specifically the `combinator-map-consensus/consensus.json` which contains the 9x9 combinator routing that was agreed upon across models. I'm examining this file along with the combinator_map_consensus.py to understand its structure, and I notice the current relational_loss_distillation.py is set up to use a single teacher model from the combinator-relationship-map directory.

## Assistant

The instruments are clear. Now let me inspect the consensus crystal artifact and the s229 metric harness I'll overlay.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "echo \"=== combinator-map-consensus/consensus.json (keys + head) ===\"; python3 -c \"\nimport json\nd=json.load(open('/Users/mwhitford/src/verbum/results/combinator-map-consensus/consensus.json'))\ndef shape(x):\n    import numpy as np\n    if isinstance(x,list):\n        a=np.array(x)\n        return f'list shape={a.shape} dtype={a.dtype}'\n    if isinstance(x,dict):\n        return 'dict keys='+str(list(x.keys())[:12])\n    return repr(x)[:80]\nfor k,v in d.items():\n    print(f'{k}: {shape(v)}')\n\"",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ echo "=== combinator-map-consensus/...

**Output:**
```
Exit code: 0
Stdout:
=== combinator-map-consensus/consensus.json (keys + head) ===
register: 'topological/routing'
git_sha: 'bbf92f2'
question: 'where do open models agree on the combinator function shape (harvest leverage)'
n_models: 10
models: list shape=(10,) dtype=<U30
model_meta: list shape=(10,) dtype=object
crystal_order: list shape=(9,) dtype=<U4
n_perm: 5000
per_frac: dict keys=['0.10', '0.20', '0.30', '0.40', '0.50']
harvest_frac: 0.4
consensus_gram: list shape=(9, 9) dtype=float64
universal_edges: list shape=(27,) dtype=object
model_specific_edges: list shape=(6,) dtype=object
family_internal_consensus: dict keys=['composition_BDS', 'selection_KIC', 'recursion_YWWHNF']
skeleton_vs_recursion_verdict: dict keys=['skeleton_mean_z_bind', 'recursion_z_bind', 'prediction', 'supported']
elapsed_s: 30.6
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls /Users/mwhitford/src/verbum/results/combinator-map-consensus/; echo \"---npz files in combinator-relationship-map---\"; ls /Users/mwhitford/src/verbum/results/combinator-relationship-map/ 2>/dev/null | head",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ ls /Users/mwhitford/src/verbum/resu...

**Output:**
```
Exit code: 0
Stdout:
consensus.json
scale.json
---npz files in combinator-relationship-map---
allenai_OLMo-2-1124-13B.json
allenai_OLMo-2-1124-13B.npz
EleutherAI_pythia-2.8b-deduped.json
EleutherAI_pythia-2.8b-deduped.npz
EleutherAI_pythia-410m.json
EleutherAI_pythia-410m.npz
HuggingFaceTB_SmolLM3-3B.json
HuggingFaceTB_SmolLM3-3B.npz
mistralai_Mistral-7B-v0.3.json
mistralai_Mistral-7B-v0.3.npz
```

### Thinking

I found the consensus_gram with the exact dimensions I need — a 9x9 matrix representing the cross-model agreed combinator routing, where the crystal order corresponds to the nine combinators K, I, B, C, S, D, W, Y, and WHNF. This is my target Gram stored in the routing register.

## Assistant

`consensus_gram` (9×9) in the routing register is exactly the target. Let me verify its ordering matches and check the s229 metric harness for the held-out overlay.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "python3 -c \"\nimport json, numpy as np\nd=json.load(open('/Users/mwhitford/src/verbum/results/combinator-map-consensus/consensus.json'))\nprint('crystal_order:', d['crystal_order'])\ng=np.array(d['consensus_gram'])\nprint('gram shape:', g.shape, 'symmetric:', np.allclose(g,g.T), 'diag:', np.round(np.diag(g),3))\noff=g[~np.eye(9,dtype=bool)]\nprint('offdiag mean/std/min/max:', round(off.mean(),3), round(off.std(),3), round(off.min(),3), round(off.max(),3))\nprint('models:', list(d['models']))\nprint('harvest_frac:', d['harvest_frac'], 'n_models:', d['n_models'])\n\"",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ python3 -c " import json, numpy as ...

**Output:**
```
Exit code: 0
Stdout:
crystal_order: ['K', 'I', 'B', 'C', 'S', 'D', 'W', 'Y', 'WHNF']
gram shape: (9, 9) symmetric: True diag: [1. 1. 1. 1. 1. 1. 1. 1. 1.]
offdiag mean/std/min/max: -0.123 0.161 -0.36 0.175
models: ['EleutherAI/pythia-2.8b-deduped', 'EleutherAI/pythia-410m', 'HuggingFaceTB/SmolLM3-3B', 'Qwen/Qwen3-0.6B', 'Qwen/Qwen3-14B', 'Qwen/Qwen3-32B', 'Qwen/Qwen3-4B', 'Qwen/Qwen3-8B', 'allenai/OLMo-2-1124-13B', 'mistralai/Mistral-7B-v0.3']
harvest_frac: 0.4 n_models: 10
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/exposure_format_sweep.py"
}
```

**Summary:** Reading exposure_format_sweep.py (0-2000)

**Output:**
```
#!/usr/bin/env python3
# register: functional (capability/usage — held-out generalization)
"""Exposure/format sweep — "training as a photograph" (session 229).

THE IDEA (Michael): a training step is an EXPOSURE to one "photograph". Many
exposures to the same β-reduction should converge faster than one. BUT the
metaphor has a fork that must be controlled or it measures the wrong thing:

  kx SAME EXACT instance      -> burns in THAT instance   -> MEMORIZATION
                                 (train loss falls, held-out flat)
  kx VARIED instances of the  -> burns in the INVARIANT   -> GENERALIZATION
  SAME RULE (same skeleton,      = the RULE itself          (each instance = the
  different atoms)                                           same object from a new
                                                             ANGLE; the hologram
                                                             forms only if angles
                                                             differ)

CROSSED DESIGN (resolves full-trace vs redex->NF AT THE SAME TIME):
  Axis 1  FORMAT (content per photograph)
    full_trace : every intermediate β-step  = long-exposure photo (move visible)
    redex_nf   : input -> normal form only   = single sharp snapshot (no motion)
  Axis 2  MULTIPLICITY
    one        : 1 instance / rule, seen 1x
    k_same     : 1 instance / rule, seen k x      (MEMORIZATION control)
    k_varied   : k DISTINCT instances / rule, 1x  (true burn-in: many angles)

METRIC: held-out generalization. The eval is FORMAT-INDEPENDENT — for an unseen
instance built from HELD-OUT atoms, greedily derive from "input -> " and check the
FINAL segment equals the true normal form (exact match). A full_trace model walks
the steps then emits the NF; a redex_nf model must leap to it. Either way we ask:
does the model produce the correct normal form for an instance it never saw, built
from atoms it was never trained on? Memorization (k_same) cannot pass this.

FALSIFIABLE PREDICTIONS:
  burn-in real : k_varied reaches held-out generalization faster than one;
                 k_same saturates early and stays LOW on held-out (rote).
  format trade : full_trace = info-rich long exposure (fewer distinct instances
                 needed); redex_nf = cheap snapshot (more angles needed). Honest
                 comparison is PER-TOKEN — full_trace photos cost more bytes each
                 (corpus_bytes reported). The crossover (full_trace wins low-budget,
                 redex_nf wins high) would itself be the finding.

Data is kernel-minted (lambda_ast.reduce) — exact, Church-Rosser, free.

Usage:
  uv run python scripts/experiments/exposure_format_sweep.py --smoke
  uv run python scripts/experiments/exposure_format_sweep.py --steps 4000 --device mps

License: MIT
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "src"))
sys.path.insert(0, str(_SCRIPT_DIR))

# reuse the tiny byte-level student + vocab (one model definition, no fork)
from relational_loss_distillation import VOCAB, TinyLM  # noqa: E402

from verbum.lambda_ast import Status, parse, pretty, reduce  # noqa: E402

RESULTS_DIR = _PROJECT_ROOT / "results" / "exposure-format-sweep"

# Hand-curated multi-step skeletons (holes _0.._n filled with atoms). Each is
# VALIDATED at load: must reduce to NORMAL_FORM in >=2 steps. Mis-reasoned ones
# are dropped with a warning rather than crashing.
SKELETONS: list[str] = [
    "C K _0 _1",          # -> _1            (2 steps)
    "W K _0",             # -> _0            (2)
    "S K _0 _1",          # -> _1            (2)
    "S K K _0",           # -> _0            (2)
    "B I I _0",           # -> _0            (3)
    "B K I _0 _1",        # -> _0            (3)
    "W (K _0) _1",        # -> _0 _1         (2)
    "C B _0 _1 _2",       # -> _1 (_0 _2)    (2)
    "D I I I _0",         # -> _0            (4)
    "B (B _0) _1 _2 _3",  # -> _0 (_1 _2 _3) (2)
    "S (K _0) I _1",      # -> _0 _1         (3)
    "S B K _0 _1",        # -> _0 _0         (3)
    "C I _0 _1",          # -> _1 _0         (2)
]

TRAIN_ATOMS = list("abcdefghijklm")   # 13 — angles the model trains on
TEST_ATOMS = list("nopqrstuvwxyz")    # 13 — disjoint held-out angles
ARROW = " -> "
NEWLINE_BYTE = 10
MAX_NEW = 110


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


# --------------------------------------------------------------------------- #
# Data minting (kernel oracle)                                                 #
# --------------------------------------------------------------------------- #
def n_holes(template: str) -> int:
    idx = [int(m) for m in re.findall(r"_(\d+)", template)]
    return (max(idx) + 1) if idx else 0


def fill(template: str, combo: tuple[str, ...]) -> str:
    return re.sub(r"_(\d+)", lambda m: combo[int(m.group(1))], template)


def reduce_strs(input_str: str) -> tuple[list[str], str, int, str]:
    """Return (trace_strs, normal_form_str, n_steps, status)."""
    red = reduce(parse(input_str))
    return [pretty(x) for x in red.trace], pretty(red.normal_form), red.steps, \
        red.status.value


def validate_skeletons(skeletons: list[str]) -> list[tuple[str, int]]:
    """Keep skeletons that reduce to a normal form in >=2 steps (full_trace and
    redex_nf must DIFFER). Returns (template, n_holes) for the survivors."""
    out: list[tuple[str, int]] = []
    for tmpl in skeletons:
        h = n_holes(tmpl)
        probe = fill(tmpl, tuple(TRAIN_ATOMS[:h]))
        try:
            trace, _nf, steps, status = reduce_strs(probe)
        except Exception as e:
            log(f"  DROP {tmpl!r}: parse/reduce error {e}")
            continue
        if status != Status.NORMAL_FORM.value:
            log(f"  DROP {tmpl!r}: status={status} (not normal form)")
            continue
        if steps < 2 or len(trace) < 3:
            log(f"  DROP {tmpl!r}: only {steps} step(s) (full_trace==redex_nf)")
            continue
        out.append((tmpl, h))
    return out


def make_fillings(rng: np.random.Generator, h: int, atoms: list[str],
                  k: int) -> list[tuple[str, ...]]:
    """k DISTINCT fillings; atoms within a term are distinct (sampled w/o repl)."""
    seen: set[tuple[str, ...]] = set()
    out: list[tuple[str, ...]] = []
    guard = 0
    while len(out) < k and guard < 10000:
        guard += 1
        combo = tuple(rng.choice(atoms, size=h, replace=False).tolist()) if h \
            else ()
        if combo not in seen:
            seen.add(combo)
            out.append(combo)
    return out


def render(template: str, combo: tuple[str, ...], fmt: str) -> str:
    trace, nf, _steps, _status = reduce_strs(fill(template, combo))
    if fmt == "redex_nf":
        return f"{trace[0]}{ARROW}{nf}"
    return ARROW.join(trace)


def build_corpus(rules: list[tuple[str, int]], train_fillings: dict[str, list],
                 fmt: str, mult: str, k: int, rng: np.random.Generator) -> str:
    """Assemble the training corpus for one (format, multiplicity) arm.

    one/k_same share fillings[0] so k_same is literally 'one repeated k times'."""
    sentences: list[str] = []
    for tmpl, _h in rules:
        fillings = train_fillings[tmpl]
        if mult == "one":
            chosen = [fillings[0]]
        elif mult == "k_same":
            chosen = [fillings[0]] * k
        else:  # k_varied
            chosen = fillings[:k]
        for combo in chosen:
            sentences.append(render(tmpl, combo, fmt))
    order = rng.permutation(len(sentences))
    return "\n".join(sentences[i] for i in order) + "\n"


def build_eval_items(rules: list[tuple[str, int]], m: int,
                     rng: np.random.Generator, atoms: list[str],
                     exclude: dict[str, list] | None = None
                     ) -> list[tuple[str, str]]:
    """Held-out (input, normal_form) pairs.

    heldout='combos' (default): atoms = TRAIN_ATOMS, but combos EXCLUDED from the
      training fillings -> isolates RULE generalization (the burn-in question) from
      symbol-copying. This is the right barrier (s229 diagnostic: tiny byte model
      reaches 0.365 here, 0.000 on disjoint atoms = a variable-binding failure, not
      a rule failure).
    heldout='atoms': atoms = TEST_ATOMS (disjoint) -> the SEPARATE, harder
      systematic/variable-binding generalization question.
    """
    exclude = exclude or {}
    items: list[tuple[str, str]] = []
    for tmpl, h in rules:
        ex = {tuple(c) for c in exclude.get(tmpl, [])}
        chosen: list[tuple[str, ...]] = []
        guard = 0
        while len(chosen) < m and guard < 10000:
            guard += 1
            combo = tuple(rng.choice(atoms, size=h, replace=False).tolist()) if h \
                else ()
            if combo not in ex and combo not in chosen:
                chosen.append(combo)
        for combo in chosen:
            trace, nf, _s, _st = reduce_strs(fill(tmpl, combo))
            items.append((trace[0], nf))
    return items


def to_byte_ids(text: str) -> np.ndarray:
    b = text.encode("utf-8", errors="ignore")
    return np.frombuffer(b, dtype=np.uint8).astype(np.int64)


# --------------------------------------------------------------------------- #
# Eval (format-independent exact-match derivation)                             #
# --------------------------------------------------------------------------- #
@torch.no_grad()
def generate(model: TinyLM, prompt_ids: list[int], block_size: int,
             device: str) -> str:
    model.eval()
    idx = torch.tensor(prompt_ids, dtype=torch.long, device=device)[None]
    out: list[int] = []
    for _ in range(MAX_NEW):
        cond = idx[:, -block_size:]
        logits, _, _ = model(cond)
        nxt = int(logits[0, -1].argmax().item())
        if nxt == NEWLINE_BYTE:
            break
        out.append(nxt)
        idx = torch.cat([idx, torch.tensor([[nxt]], device=device)], dim=1)
    return bytes(out).decode("utf-8", errors="ignore")


@torch.no_grad()
def eval_acc(model: TinyLM, eval_items: list[tuple[str, str]], block_size: int,
             device: str) -> float:
    correct = 0
    for inp, nf in eval_items:
        prompt = (inp + ARROW).encode("utf-8")
        gen = generate(model, list(prompt), block_size, device)
        pred = (inp + ARROW + gen).split(ARROW)[-1].strip()
        if pred == nf.strip():
            correct += 1
    return correct / max(1, len(eval_items))


# --------------------------------------------------------------------------- #
# Train one arm                                                                #
# --------------------------------------------------------------------------- #
def train_arm(name: str, corpus: str, eval_items: list[tuple[str, str]],
              args, device: str) -> dict:
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    ids = to_byte_ids(corpus)
    T, bs = args.block_size, args.batch_size
    # tile a short corpus so random windows are always valid
    while ids.shape[0] <= 4 * (T + 1):
        ids = np.concatenate([ids, ids])
    n = ids.shape[0]
    model = TinyLM(args.d_model, args.n_head, args.n_layer, args.d_ff, T).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
    curve: list[dict] = []
    t0 = time.time()
    for step in range(1, args.steps + 1):
        model.train()
        ix = torch.randint(0, n - T - 1, (bs,))
        xb = torch.stack([torch.from_numpy(ids[i:i + T]) for i in ix]).to(device)
        yb = torch.stack(
            [torch.from_numpy(ids[i + 1:i + 1 + T]) for i in ix]).to(device)
        logits, _, _ = model(xb)
        ce = F.cross_entropy(logits.reshape(-1, VOCAB), yb.reshape(-1))
        opt.zero_grad()
        ce.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        if step % args.eval_every == 0 or step == args.steps:
            acc = eval_acc(model, eval_items, T, device)
            curve.append({"step": step, "tokens": step * bs * T,
                          "ce": round(float(ce.item()), 4), "heldout_acc": acc})
            log(f"  [{name}] step {step:5d} | CE {ce.item():.3f} "
                f"| held-out acc {acc:.3f} | {time.time()-t0:.0f}s")
    accs = [c["heldout_acc"] for c in curve]
    half = next((c["step"] for c in curve if c["heldout_acc"] >= 0.5), None)
    return {
        "arm": name,
        "corpus_bytes": int(to_byte_ids(corpus).shape[0]),  # the per-photo cost
        "final_acc": accs[-1] if accs else 0.0,
        "best_acc": max(accs) if accs else 0.0,
        "steps_to_half": half,
        "curve": curve,
    }


FORMATS = ["redex_nf", "full_trace"]
MULTS = ["one", "k_same", "k_varied"]


def run_seed(args, device: str, rules: list[tuple[str, int]],
             seed: int) -> list[dict]:
    """Train all 6 arms (FORMAT x MULTIPLICITY) at one seed; reseed data + init."""
    args.seed = seed
    fill_rng = np.random.default_rng(seed)
    train_fillings = {tmpl: make_fillings(fill_rng, h, TRAIN_ATOMS, args.k)
                      for tmpl, h in rules}
    eval_rng = np.random.default_rng(seed + 777)
    if args.heldout == "combos":
        eval_atoms, eval_exclude = TRAIN_ATOMS, train_fillings
    else:
        eval_atoms, eval_exclude = TEST_ATOMS, None
    eval_items = build_eval_items(rules, args.m_eval, eval_rng, eval_atoms,
                                  eval_exclude)
    log(f"  [seed {seed}] held-out eval instances={len(eval_items)} "
        f"(heldout={args.heldout})")
    arms: list[dict] = []
    for fmt in FORMATS:
        for mult in MULTS:
            corpus_rng = np.random.default_rng(seed + 13)
            corpus = build_corpus(rules, train_fillings, fmt, mult, args.k,
                                  corpus_rng)
            name = f"{fmt}/{mult}"
            log(f"\n=== seed {seed} {name}  (corpus {len(corpus.encode())} B) ===")
            v = train_arm(name, corpus, eval_items, args, device)
            v["format"], v["multiplicity"], v["seed"] = fmt, mult, seed
            arms.append(v)
    return arms


def _ms(vals: list[float]) -> list[float]:
    a = np.array(vals, dtype=float)
    return [round(float(a.mean()), 4), round(float(a.std()), 4)]


# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="mps")
    ap.add_argument("--steps", type=int, default=4000)
    ap.add_argument("--eval-every", type=int, default=500)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--block-size", type=int, default=128)
    ap.add_argument("--d-model", type=int, default=128)
    ap.add_argument("--n-head", type=int, default=4)
    ap.add_argument("--n-layer", type=int, default=4)
    ap.add_argument("--d-ff", type=int, default=256)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--k", type=int, default=8, help="multiplicity (exposures/rule)")
    ap.add_argument("--m-eval", type=int, default=6, help="held-out instances/rule")
    ap.add_argument("--heldout", choices=["combos", "atoms"], default="combos",
                    help="combos=unseen fillings of SEEN atoms (rule generalization);"
                         " atoms=disjoint TEST atoms (variable-binding generalization)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--seeds", default="",
                    help="csv seeds for multi-seed harden, e.g. 0,1,2 "
                         "(overrides --seed; aggregates mean±std per arm)")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.smoke:
        args.steps, args.eval_every = 80, 40
        args.k, args.m_eval = 4, 3
        args.d_model, args.d_ff, args.n_layer = 64, 128, 3

    device = args.device
    if device == "mps" and not torch.backends.mps.is_available():
        device = "cpu"
        log("  mps unavailable -> cpu")
    if device == "cuda" and not torch.cuda.is_available():
        device = "cpu"

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    log("  validating skeletons (must be multi-step normal-forming)...")
    rules = validate_skeletons(SKELETONS)
    if args.smoke:
        rules = rules[:4]
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()] or [args.seed]
    log(f"  rules={len(rules)} train_atoms={len(TRAIN_ATOMS)} "
        f"test_atoms={len(TEST_ATOMS)} k={args.k} m_eval={args.m_eval} seeds={seeds}")

    all_arms: list[dict] = []
    for sd in seeds:
        all_arms.extend(run_seed(args, device, rules, sd))

    meta = {
        "experiment": "exposure-format-sweep",
        "register": "functional (held-out generalization)",
        "idea": "training as a photograph (s229); fork = memorization vs rule burn-in",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "git_sha": git_sha(),
        "device": device,
        "smoke": args.smoke,
        "config": vars(args),
        "n_rules": len(rules),
        "heldout": args.heldout,
        "seeds": seeds,
        "elapsed_s": round(time.time() - t0, 1),
    }

    # ---- single-seed path (unchanged output contract) ----
    if len(seeds) == 1:
        by = {a["arm"]: a for a in all_arms}
        out = {**meta, "arms": all_arms}
        tag = "smoke" if args.smoke else "run"
        (RESULTS_DIR / f"verdict_{tag}.json").write_text(json.dumps(out, indent=2))
        log("\n  ==== EXPOSURE/FORMAT SWEEP ====")
        log(f"  {'arm':<22} {'corpus_B':>9} {'final_acc':>10} {'best_acc':>9} "
            f"{'steps@0.5':>10}")
        for fmt in FORMATS:
            for mult in MULTS:
                a = by[f"{fmt}/{mult}"]
                log(f"  {a['arm']:<22} {a['corpus_bytes']:>9} "
                    f"{a['final_acc']:>10.3f} {a['best_acc']:>9.3f} "
                    f"{a['steps_to_half']!s:>10}")
        log("\n  PREDICTIONS (held-out generalization):")
        for fmt in FORMATS:
            o = by[f"{fmt}/one"]["best_acc"]
            ks = by[f"{fmt}/k_same"]["best_acc"]
            kv = by[f"{fmt}/k_varied"]["best_acc"]
            log(f"   [{fmt}] burn-in (k_varied>one): {kv:.3f}>{o:.3f} = {kv > o}  | "
                f"rule>rote (k_varied>k_same): {kv:.3f}>{ks:.3f} = {kv > ks}")
        log(f"\n  wrote {RESULTS_DIR / f'verdict_{tag}.json'}  ({meta['elapsed_s']}s)")
        return

    # ---- multi-seed aggregate (the harden) ----
    agg: dict[str, dict] = {}
    for fmt in FORMATS:
        for mult in MULTS:
            name = f"{fmt}/{mult}"
            rs = [a for a in all_arms if a["arm"] == name]
            agg[name] = {
                "n": len(rs),
                "best_acc": _ms([r["best_acc"] for r in rs]),
                "final_acc": _ms([r["final_acc"] for r in rs]),
                "corpus_bytes": rs[0]["corpus_bytes"],
                "per_seed_best": [r["best_acc"] for r in rs],
            }
    out = {**meta, "aggregate": agg, "runs": all_arms}
    (RESULTS_DIR / "verdict_multiseed.json").write_text(json.dumps(out, indent=2))

    log("\n  ==== MULTI-SEED AGGREGATE (mean±std over seeds) ====")
    log(f"  {'arm':<22} {'corpus_B':>9} {'best_acc(mean±std)':>22} {'per-seed':>20}")
    for fmt in FORMATS:
        for mult in MULTS:
            a = agg[f"{fmt}/{mult}"]
            ps = ",".join(f"{x:.2f}" for x in a["per_seed_best"])
            log(f"  {fmt + '/' + mult:<22} {a['corpus_bytes']:>9} "
                f"{a['best_acc'][0]:>+10.3f}±{a['best_acc'][1]:<5.3f}        {ps:>20}")
    log("\n  ROBUSTNESS (best_acc, mean±std; decisive if k_varied(mean-std) clears):")
    for fmt in FORMATS:
        kv = agg[f"{fmt}/k_varied"]["best_acc"]
        ks = agg[f"{fmt}/k_same"]["best_acc"]
        o = agg[f"{fmt}/one"]["best_acc"]
        rule_robust = (kv[0] - kv[1]) > (ks[0] + ks[1])
        burn_robust = (kv[0] - kv[1]) > (o[0] + o[1])
        log(f"   [{fmt}] rule>rote: k_varied {kv[0]:.3f}±{kv[1]:.3f} vs k_same "
            f"{ks[0]:.3f}±{ks[1]:.3f} -> DECISIVE={rule_robust} | "
            f"burn-in vs one {o[0]:.3f}±{o[1]:.3f} -> DECISIVE={burn_robust}")
    log(f"\n  wrote {RESULTS_DIR / 'verdict_multiseed.json'}  ({meta['elapsed_s']}s)")


if __name__ == "__main__":
    main()
```

### Thinking

I've loaded the consensus crystal from the results directory—it's a 9×9 Gram matrix with the combinator ordering that perfectly aligns with the CRYSTAL constant in the distillation code, symmetric with diagonal ones and mean off-diagonal values around −0.123, representing the cross-model agreement on routing.

The instruments I'm tracking include the TinyLM model with its routing register (the Block gate), the differentiable soft Gram for CMR routing, silhouette metrics against the null distribution, and helper functions for loading probe batches and building the corpus. The s229 metric from the exposure format sweep gives me the held-out rule-generalization capability curve, and the v1 tomography design logs the routing silhouette, Gram correlation to both the consensus crystal and raw teacher Gram (as a reference control), cross-entropy loss, held-out accuracy, and effective dimension to watch for Q-collapse—all to pinpoint when the invariant crystallizes during training.

Now I'm working through the reference-beam control design. The consensus crystal only captures the routing-register geometry, but I need to track raw-register Gram correlation too to measure common-mode emergence separately from function learning. The prediction is that raw Gram correlation should rise smoothly and early (common mode), while routing Gram correlation and the routing silhouette should rise later and more sharply once the function crystallizes. The challenge is that the consensus target is routing-only, so I need to figure out what raw-register teacher target to compare against. The key insight is that the raw register won't track the function—that's the reference-beam control showing why naive gradient descent in raw space misses the structure. So I should measure both the student's raw-CMR correlation to the consensus target (which should stay near zero, confirming the function is invisible there) and the routing-CMR correlation (which should rise as the combinator structure crystallizes). The routing measurement needs to use the same sign(gate)-CMR representation that the consensus crystal was built from, to keep everything commensurate.

I'll also track effective dimensionality of the routing activations over time to watch for Q-collapse, and then decide which curriculum to use for the data.

The key trade-off is between the probe corpus (where held-out rule accuracy isn't naturally defined) versus the s229 curriculum (where held-out accuracy IS the s229 metric, and I can measure routing geometry on the independent crystal probes). The richest design trains on s229 reductions so I get the capability curve while measuring whether the routing crystal forms on the probe set—directly testing whether routing geometry crystallizes before generalization. The s229 curriculum uses a small set of combinators in the skeletons, while the crystal probes span a wider set including Y and WHNF, which is fine since the question is whether the routing register develops consensus geometry while learning to reduce.

I'll make the data source configurable but default to curriculum, since the most important readout is when the invariant crystallizes relative to when held-out accuracy plateaus—that requires the s229 eval. Now I'm designing the script structure: I'll reuse TinyLM and VOCAB from the existing codebase, import the curriculum minting logic (skeletons, fillings, rendering, corpus building, evaluation), and reuse the crystal probe loading and geometry measurement instruments.

For the training loop, I'll run CE-only and log at regular intervals: step, tokens, CE loss, held-out accuracy, and the geometry metrics (route_z, gc_route, gc_raw, hidden_z, effective dimensions). The trajectory gets saved as a JSON file for analysis. The key readout is comparing when route_z crosses a threshold or gc_route crystallizes against when CE plateaus and when held-out accuracy starts rising.

I need to be careful with imports—exposure_format_sweep imports from relational_loss_distillation, but since both are in the same directory and exposure_format_sweep only has functions and a main block, importing from it should be safe. For the geometry measurement on crystal probes, I'll compute the sign-CMR and raw-CMR Grams, then calculate route_z using silhouette analysis, gc_route by correlating the routed centroids Gram with the consensus Gram, and gc_raw similarly for the hidden representations.

For efficiency, I'll use around 300 permutations for silhouette_null during the trajectory (cheaper than 1000) since the computation is already fast on 9 centroids. I'll also compute effective dimension using the participation ratio on both the routing register and raw hidden features. The sign(gate)-CMR is the right register to use since that's what the consensus Gram was built from in the original relational loss setup.

Now I'm setting up the measurement thresholds for crystallization timing — tracking when gc_route reaches 50% of final, when route_z exceeds z=3, when heldout accuracy hits a reachable bar (either a fraction of final or an absolute threshold like 0.2), and when cross-entropy plateaus within 5% of its final value. I'll make these configurable since the s229 ceiling is around 0.32.

My plan is to build the trajectory tomography script with the reused instruments and consensus target, run diagnostics and a smoke test, execute the full run, then capture the results for the knowledge page update.

## Assistant

I have everything I need. Summary of the design inputs:

- **Target = consensus crystal**: `results/combinator-map-consensus/consensus.json` → `consensus_gram` (9×9, routing register, CMR). `crystal_order` = `["K","I","B","C","S","D","W","Y","WHNF"]` — **exactly matches** `CRYSTAL` in the instruments. Built from 10 open models agreeing (offdiag mean −0.123). This is the model-agnostic ground-truth you want.
- **Instruments** (reuse from `relational_loss_distillation.py`): `TinyLM`, the gate=routing register, `soft_gram`, `np_silhouette_null` (route_z), `np_gram`, `offdiag_corr` (GramCorr), `load_crystal_probe_batch`.
- **Capability curve** (reuse from `exposure_format_sweep.py`): the s229 held-out rule-generalization eval + curriculum minting — gives the `heldout_acc(t)` track for the inventory-before-capability timing test.

The clean v1: **train CE-only on the s229 β-reduction curriculum** (capability), **measure the combinator routing geometry on the independent crystal probes** (inventory), correlate to the consensus crystal as a movie, with the **raw register running alongside as the reference-beam control**.

Let me set up the plan.

### Thinking

I'm going to start working on task 1 and build out the script.

### Thinking

I'm verifying the harvest_frac value and understanding the eff_dim concept before setting up the imports I need from relational_loss_distillation, including the vocabulary, model class, batch loading function, and various utility functions for metrics and analysis.

For the corpus generation, I need to decide on format and multiplicity — I'll make format configurable with redex_nf as the default since it wins on per-token accuracy and gives sharper snapshots for watching crystallization, while k_varied multiplicity is the regime where the rule actually builds and generalizes. Now I'm thinking through the effective dimensionality calculation using participation ratio via SVD on the centered activation matrix.

For measuring route geometry, I'm building a function that runs the model on probe batches, captures gate and hidden activations at a specific layer, then computes silhouette scores and Gram matrices for both the sign-based routing and raw hidden representations to track how the routes cluster relative to a consensus grammar. I need to decide whether to compute effective dimension on the raw gate pre-activation or the sign-discretized version.

Now for the trajectory analysis, I'm setting up the readout logic to identify key crystallization points: when the route geometry first reaches a threshold, when cross-entropy plateaus, and when heldout accuracy rises, then comparing their ordering to see if routing crystallizes before generalization improves. I'll also track whether raw hidden geometry stays flat while route geometry rises as a reference. I'm adding a helper function to find the first step meeting any threshold condition, and optionally supporting multi-seed aggregation though single-seed is the default for now.

For the implementation, I'm loading the consensus Gram matrix from the saved results, then building the corpus by reusing the skeleton validation and filling generation logic from the exposure sweep, seeding the random generator per run.

Writing the data loading code...

## Assistant

Now I'll build the script, reusing the existing instruments and curriculum minting.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py",
  "content": "#!/usr/bin/env python3\n# register: functional + topological/routing\n\"\"\"Gradient-trajectory tomography v1 — reverse-engineering GD in INVARIANT\ncoordinates over training (session 230).\n\nTHE IDEA (Michael, s229): \"If models do a holographic inference process, why\ncan't we reverse-engineer what GD is doing? Use the micro model.\"\n\nYou CANNOT reverse-engineer GD in WEIGHT space (gauge + superposition). But on\nthe micro model, in INVARIANT coordinates (the routing register, CMR), prediction-\ngated, with a GROUND-TRUTH target, watching the relational geometry develop frame-\nby-frame over checkpoints IS reverse-engineering what GD is doing.\n\nPRIOR ART (build on, do not reinvent): holographic-tomography.md (SPATIAL, cross-\nMODEL) + relational-loss-distillation.md (the instruments + the s223 dissociation)\n+ v4.1/v6.1-training-trajectory (trajectory tracking). DELTA HERE = TEMPORAL\n(intersect training STEPS, single micro model) + GROUND-TRUTH target + reference-\nbeam CONTROL run as a movie.\n\nTHE GROUND-TRUTH TARGET = the CONSENSUS CRYSTAL (s219 / combinator-map-consensus):\nthe 9x9 combinator routing Gram AGREED across 10 open models. Highest chance of\nbeing model-agnostic precisely because the models already agreed. NOT one teacher.\n\nTHE COLLISION (the reference beam decides this too): naively watching \"what changed\nthis step\" mostly reconstructs GAUGE MOTION + FREQUENCY STATS (the common mode) -\na gorgeous movie of the wrong thing (s222 = discrete-topology churn). So we read\nthe trajectory through TWO registers at once:\n  routing (sign(gate)-CMR)  -> the FUNCTION being built (gc_route, route_z)\n  raw     (hidden-CMR)       -> the REFERENCE BEAM / common-mode control (gc_raw)\nThe function is INVISIBLE in the raw register (s223 silhouette ~ -0.035); it appears\nonly in the routing register after CMR. So gc_raw should stay flat while gc_route\nrises - demonstrating that naive GD-watching sees the common mode, not the function.\n\nDESIGN: CE-only TinyLM trains on the s229 beta-reduction curriculum (the CAPABILITY,\nkernel-minted, k_varied = the burn-in regime that generalizes). At dense checkpoints\nwe measure the combinator routing GEOMETRY on the INDEPENDENT crystal probes (the\nINVENTORY), correlate to the consensus crystal, and log it as a movie alongside the\ns229 held-out rule-generalization metric (the capability curve) + eff_dim (the s105\nQ-collapse / flood-lamp watch).\n\nFALSIFIABLE PREDICTIONS:\n  reference beam : gc_route + route_z rise (the function); gc_raw stays low/flat\n                   (the common mode invisible to the function target) -> reproduces\n                   s223 (b) as a TRAJECTORY.\n  inventory<capability : routing geometry crystallizes BEFORE held-out\n                   generalization rises (geometry=inventory (x) continuation=\n                   capability, s224).\n  Q-collapse     : eff_dim may collapse toward 1 (flood-lamp, s105); if so THAT is\n                   the reverse-engineered GD behavior and the relational/laser\n                   constraint is the lever.\n\nUsage:\n  uv run python scripts/experiments/gd_trajectory_tomography.py --smoke\n  uv run python scripts/experiments/gd_trajectory_tomography.py --steps 6000 --device mps\n  uv run python scripts/experiments/gd_trajectory_tomography.py --seeds 0,1,2 --steps 6000\n\nLicense: MIT\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport subprocess\nimport sys\nimport time\nfrom datetime import UTC, datetime\nfrom pathlib import Path\n\nimport numpy as np\nimport torch\nimport torch.nn.functional as F\n\n_SCRIPT_DIR = Path(__file__).resolve().parent\n_PROJECT_ROOT = _SCRIPT_DIR.parent.parent\nsys.path.insert(0, str(_PROJECT_ROOT / \"src\"))\nsys.path.insert(0, str(_SCRIPT_DIR))\n\n# instruments + tiny student (one model definition, no fork)\nfrom relational_loss_distillation import (  # noqa: E402\n    CRYSTAL,\n    VOCAB,\n    TinyLM,\n    gather_last,\n    load_crystal_probe_batch,\n    np_centroids,\n    np_cmr,\n    np_gram,\n    np_silhouette_null,\n    offdiag_corr,\n)\n\n# curriculum minting + the s229 held-out generalization metric (no fork)\nfrom exposure_format_sweep import (  # noqa: E402\n    SKELETONS,\n    TRAIN_ATOMS,\n    build_corpus,\n    build_eval_items,\n    eval_acc,\n    make_fillings,\n    to_byte_ids,\n    validate_skeletons,\n)\n\nRESULTS_DIR = _PROJECT_ROOT / \"results\" / \"gd-trajectory-tomography\"\nCONSENSUS_PATH = (_PROJECT_ROOT / \"results\" / \"combinator-map-consensus\"\n                  / \"consensus.json\")\n\n\ndef log(msg: str = \"\") -> None:\n    print(msg, file=sys.stderr, flush=True)\n\n\ndef git_sha() -> str:\n    try:\n        return subprocess.check_output(\n            [\"git\", \"rev-parse\", \"HEAD\"], cwd=_PROJECT_ROOT).decode().strip()\n    except Exception:\n        return \"unknown\"\n\n\n# --------------------------------------------------------------------------- #\n# Ground-truth target: the CONSENSUS CRYSTAL (10-model agreed routing Gram)     #\n# --------------------------------------------------------------------------- #\ndef load_consensus() -> tuple[np.ndarray, dict]:\n    d = json.loads(CONSENSUS_PATH.read_text())\n    order = list(d[\"crystal_order\"])\n    if order != CRYSTAL:\n        raise ValueError(f\"consensus crystal_order {order} != instrument {CRYSTAL}\")\n    g = np.array(d[\"consensus_gram\"], dtype=np.float64)\n    meta = {\n        \"consensus_path\": str(CONSENSUS_PATH.relative_to(_PROJECT_ROOT)),\n        \"consensus_git_sha\": d.get(\"git_sha\", \"unknown\"),\n        \"n_models\": d.get(\"n_models\"),\n        \"models\": list(d.get(\"models\", [])),\n        \"harvest_frac\": d.get(\"harvest_frac\"),\n        \"offdiag_mean\": float(g[~np.eye(9, dtype=bool)].mean()),\n    }\n    return g, meta\n\n\n# --------------------------------------------------------------------------- #\n# Q-collapse watch (s105): effective dimension = participation ratio           #\n# --------------------------------------------------------------------------- #\ndef eff_dim(X: np.ndarray) -> float:\n    \"\"\"Participation ratio of the centered-feature covariance spectrum.\n    PR = (sum lambda)^2 / sum(lambda^2) in [1, min(N,d)]. 1 = flood-lamp collapse.\"\"\"\n    Xc = X - X.mean(axis=0, keepdims=True)\n    sv = np.linalg.svd(Xc, compute_uv=False)\n    ev = sv.astype(np.float64) ** 2\n    denom = (ev ** 2).sum()\n    if denom < 1e-30:\n        return 1.0\n    return float((ev.sum() ** 2) / denom)\n\n\n# --------------------------------------------------------------------------- #\n# Geometry measurement on the INDEPENDENT crystal probes (the movie frame)     #\n# --------------------------------------------------------------------------- #\n@torch.no_grad()\ndef measure_geometry(model: TinyLM, p_ids: torch.Tensor, p_len: torch.Tensor,\n                     labels: np.ndarray, cap: int, consensus_gram: np.ndarray,\n                     n_perm: int, probe_batch: int, seed: int) -> dict:\n    \"\"\"One movie frame: routing-register (function) vs raw-register (reference\n    beam), both correlated to the consensus crystal + eff_dim (Q-collapse).\"\"\"\n    model.eval()\n    gate_feats, hid_feats = [], []\n    for s in range(0, p_ids.shape[0], probe_batch):\n        pb = p_ids[s:s + probe_batch]\n        _, hid, gate = model(pb, capture_layer=cap)\n        pl = p_len[s:s + probe_batch]\n        gate_feats.append(gather_last(gate, pl).cpu().numpy())\n        hid_feats.append(gather_last(hid, pl).cpu().numpy())\n    gate_np = np.concatenate(gate_feats, axis=0).astype(np.float64)\n    hid_np = np.concatenate(hid_feats, axis=0).astype(np.float64)\n\n    # routing register = sign(gate)-CMR (the register the consensus was built in)\n    sign_cmr = np_cmr(np.sign(gate_np))\n    route_sil = np_silhouette_null(sign_cmr, labels, n_perm, seed)\n    route_gram = np_gram(np_centroids(sign_cmr, labels))\n    gc_route = offdiag_corr(route_gram, consensus_gram)\n\n    # raw register = hidden-CMR (the REFERENCE BEAM / common-mode control)\n    hid_cmr = np_cmr(hid_np)\n    hidden_sil = np_silhouette_null(hid_cmr, labels, n_perm, seed)\n    hid_gram = np_gram(np_centroids(hid_cmr, labels))\n    gc_raw = offdiag_corr(hid_gram, consensus_gram)\n\n    return {\n        \"route_z\": round(float(route_sil[\"z\"]), 4),\n        \"route_p\": round(float(route_sil[\"p_value\"]), 5),\n        \"gc_route\": round(float(gc_route), 4),\n        \"hidden_z\": round(float(hidden_sil[\"z\"]), 4),\n        \"gc_raw\": round(float(gc_raw), 4),\n        \"eff_dim_route\": round(eff_dim(gate_np), 3),\n        \"eff_dim_raw\": round(eff_dim(hid_np), 3),\n    }\n\n\n# --------------------------------------------------------------------------- #\n# Readout: when does the invariant crystallize vs CE-plateau vs capability?     #\n# --------------------------------------------------------------------------- #\ndef _first_step(curve: list[dict], key: str, thresh: float,\n                ge: bool = True) -> int | None:\n    for row in curve:\n        v = row[key]\n        if v is None:\n            continue\n        if (ge and v >= thresh) or (not ge and v <= thresh):\n            return int(row[\"step\"])\n    return None\n\n\ndef _final(curve: list[dict], key: str) -> float:\n    vals = [r[key] for r in curve if r.get(key) is not None]\n    return float(vals[-1]) if vals else 0.0\n\n\ndef readout(curve: list[dict], gc_frac: float, acc_frac: float,\n            z_thresh: float, ce_tol: float) -> dict:\n    final_gc = _final(curve, \"gc_route\")\n    final_acc = _final(curve, \"heldout_acc\")\n    final_ce = _final(curve, \"ce\")\n    # crystallization = routing geometry approaches the consensus crystal\n    s_gc = _first_step(curve, \"gc_route\", gc_frac * final_gc) if final_gc > 0 else None\n    s_z = _first_step(curve, \"route_z\", z_thresh)\n    # capability = held-out rule generalization rises\n    s_acc = (_first_step(curve, \"heldout_acc\", acc_frac * final_acc)\n             if final_acc > 0 else None)\n    # CE plateau = within ce_tol of the final CE\n    s_ce = _first_step(curve, \"ce\", final_ce * (1.0 + ce_tol), ge=False)\n\n    def order(a: int | None, b: int | None) -> str:\n        if a is None or b is None:\n            return \"n/a\"\n        if a < b:\n            return \"before\"\n        if a > b:\n            return \"after\"\n        return \"same\"\n\n    return {\n        \"final\": {\"gc_route\": round(final_gc, 4), \"gc_raw\": _final(curve, \"gc_raw\"),\n                  \"route_z\": _final(curve, \"route_z\"),\n                  \"heldout_acc\": round(final_acc, 4), \"ce\": round(final_ce, 4),\n                  \"eff_dim_route\": _final(curve, \"eff_dim_route\"),\n                  \"eff_dim_raw\": _final(curve, \"eff_dim_raw\")},\n        \"step_gc_route_cross\": s_gc,\n        \"step_route_z_cross\": s_z,\n        \"step_heldout_acc_cross\": s_acc,\n        \"step_ce_plateau\": s_ce,\n        \"inventory_before_capability\": order(s_gc, s_acc),\n        \"routing_z_before_capability\": order(s_z, s_acc),\n        \"crystallize_before_ce_plateau\": order(s_gc, s_ce),\n        \"reference_beam\": {\n            \"gc_route_final\": round(final_gc, 4),\n            \"gc_raw_final\": _final(curve, \"gc_raw\"),\n            \"route_tracks_function\": final_gc > abs(_final(curve, \"gc_raw\")),\n        },\n    }\n\n\n# --------------------------------------------------------------------------- #\n# Train one seed: CE-only, dense checkpoints, geometry movie                    #\n# --------------------------------------------------------------------------- #\ndef train_seed(args, device: str, consensus_gram: np.ndarray, seed: int,\n               p_ids: torch.Tensor, p_len: torch.Tensor,\n               probe_labels: np.ndarray) -> dict:\n    torch.manual_seed(seed)\n    np.random.seed(seed)\n\n    rules = validate_skeletons(SKELETONS)\n    if args.smoke:\n        rules = rules[:4]\n    fill_rng = np.random.default_rng(seed)\n    train_fillings = {tmpl: make_fillings(fill_rng, h, TRAIN_ATOMS, args.k)\n                      for tmpl, h in rules}\n    corpus = build_corpus(rules, train_fillings, args.format, \"k_varied\", args.k,\n                          np.random.default_rng(seed + 13))\n    eval_rng = np.random.default_rng(seed + 777)\n    eval_items = build_eval_items(rules, args.m_eval, eval_rng, TRAIN_ATOMS,\n                                  train_fillings)  # heldout = combos (rule gen.)\n    log(f\"  [seed {seed}] rules={len(rules)} corpus={len(corpus.encode())} B \"\n        f\"heldout_eval={len(eval_items)} format={args.format}\")\n\n    ids = to_byte_ids(corpus)\n    T, bs = args.block_size, args.batch_size\n    while ids.shape[0] <= 4 * (T + 1):\n        ids = np.concatenate([ids, ids])\n    n = ids.shape[0]\n\n    model = TinyLM(args.d_model, args.n_head, args.n_layer, args.d_ff, T).to(device)\n    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)\n    cap = args.capture_layer if args.capture_layer >= 0 else args.n_layer // 2\n\n    curve: list[dict] = []\n    t0 = time.time()\n\n    def snapshot(step: int, ce_val: float) -> None:\n        acc = eval_acc(model, eval_items, T, device)\n        geo = measure_geometry(model, p_ids, p_len, probe_labels, cap,\n                               consensus_gram, args.n_perm, args.probe_batch, seed)\n        row = {\"step\": step, \"tokens\": step * bs * T,\n               \"ce\": round(ce_val, 4), \"heldout_acc\": round(acc, 4), **geo}\n        curve.append(row)\n        log(f\"  [seed {seed}] step {step:5d} | CE {ce_val:.3f} | acc {acc:.3f} \"\n            f\"| route_z {geo['route_z']:+.2f} | gc_route {geo['gc_route']:+.3f} \"\n            f\"| gc_raw {geo['gc_raw']:+.3f} | effd {geo['eff_dim_route']:.1f} \"\n            f\"| {time.time()-t0:.0f}s\")\n\n    # frame at init (step 0) = the gauge baseline before any GD\n    snapshot(0, float(\"nan\"))\n    for step in range(1, args.steps + 1):\n        model.train()\n        ix = torch.randint(0, n - T - 1, (bs,))\n        xb = torch.stack([torch.from_numpy(ids[i:i + T]) for i in ix]).to(device)\n        yb = torch.stack(\n            [torch.from_numpy(ids[i + 1:i + 1 + T]) for i in ix]).to(device)\n        logits, _, _ = model(xb)\n        ce = F.cross_entropy(logits.reshape(-1, VOCAB), yb.reshape(-1))\n        opt.zero_grad()\n        ce.backward()\n        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)\n        opt.step()\n        if step % args.ckpt_every == 0 or step == args.steps:\n            snapshot(step, float(ce.item()))\n\n    # readout uses post-init frames only (drop the nan-CE init frame for CE plateau)\n    rd = readout([r for r in curve if not (isinstance(r[\"ce\"], float)\n                                           and np.isnan(r[\"ce\"]))],\n                 args.gc_frac, args.acc_frac, args.z_thresh, args.ce_tol)\n    return {\"seed\": seed, \"capture_layer\": cap, \"corpus_bytes\": int(ids.shape[0]),\n            \"curve\": curve, \"readout\": rd}\n\n\ndef _ms(vals: list[float]) -> list[float]:\n    a = np.array([v for v in vals if v is not None], dtype=float)\n    if a.size == 0:\n        return [None, None]\n    return [round(float(a.mean()), 2), round(float(a.std()), 2)]\n\n\n# --------------------------------------------------------------------------- #\ndef main() -> None:\n    ap = argparse.ArgumentParser()\n    ap.add_argument(\"--device\", default=\"mps\")\n    ap.add_argument(\"--steps\", type=int, default=6000)\n    ap.add_argument(\"--ckpt-every\", type=int, default=200,\n                    help=\"dense checkpoint interval (the movie frame rate)\")\n    ap.add_argument(\"--batch-size\", type=int, default=32)\n    ap.add_argument(\"--block-size\", type=int, default=128)\n    ap.add_argument(\"--d-model\", type=int, default=128)\n    ap.add_argument(\"--n-head\", type=int, default=4)\n    ap.add_argument(\"--n-layer\", type=int, default=4)\n    ap.add_argument(\"--d-ff\", type=int, default=256)\n    ap.add_argument(\"--capture-layer\", type=int, default=-1, help=\"-1 = middle\")\n    ap.add_argument(\"--lr\", type=float, default=3e-4)\n    ap.add_argument(\"--format\", choices=[\"redex_nf\", \"full_trace\"],\n                    default=\"redex_nf\", help=\"curriculum photo format (s229)\")\n    ap.add_argument(\"--k\", type=int, default=8, help=\"k_varied exposures/rule\")\n    ap.add_argument(\"--m-eval\", type=int, default=6, help=\"held-out instances/rule\")\n    ap.add_argument(\"--probe-batch\", type=int, default=64)\n    ap.add_argument(\"--probe-max-len\", type=int, default=96)\n    ap.add_argument(\"--n-perm\", type=int, default=300, help=\"silhouette null perms\")\n    ap.add_argument(\"--gc-frac\", type=float, default=0.5,\n                    help=\"crystallization = gc_route reaches this frac of final\")\n    ap.add_argument(\"--acc-frac\", type=float, default=0.5,\n                    help=\"capability rise = heldout_acc reaches this frac of final\")\n    ap.add_argument(\"--z-thresh\", type=float, default=3.0,\n                    help=\"route_z crossing threshold (significant structure)\")\n    ap.add_argument(\"--ce-tol\", type=float, default=0.05,\n                    help=\"CE plateau = within this frac of final CE\")\n    ap.add_argument(\"--seed\", type=int, default=0)\n    ap.add_argument(\"--seeds\", default=\"\",\n                    help=\"csv seeds for multi-seed harden (overrides --seed)\")\n    ap.add_argument(\"--smoke\", action=\"store_true\")\n    args = ap.parse_args()\n\n    if args.smoke:\n        args.steps, args.ckpt_every = 120, 40\n        args.k, args.m_eval, args.n_perm = 4, 3, 100\n        args.d_model, args.d_ff, args.n_layer = 64, 128, 3\n\n    device = args.device\n    if device == \"mps\" and not torch.backends.mps.is_available():\n        device = \"cpu\"\n        log(\"  mps unavailable -> cpu\")\n    if device == \"cuda\" and not torch.cuda.is_available():\n        device = \"cpu\"\n\n    RESULTS_DIR.mkdir(parents=True, exist_ok=True)\n    t0 = time.time()\n\n    consensus_gram, cmeta = load_consensus()\n    log(f\"  consensus crystal: {cmeta['n_models']} models, offdiag_mean=\"\n        f\"{cmeta['offdiag_mean']:+.3f}, sha={cmeta['consensus_git_sha']}\")\n\n    probe_ids, probe_len, probe_labels = load_crystal_probe_batch(args.probe_max_len)\n    p_ids = torch.tensor(probe_ids, device=device)\n    p_len = torch.tensor(probe_len, device=device)\n    log(f\"  crystal probes={probe_ids.shape[0]} maxlen={probe_ids.shape[1]}\")\n\n    seeds = [int(s) for s in args.seeds.split(\",\") if s.strip()] or [args.seed]\n    log(f\"  seeds={seeds} steps={args.steps} ckpt_every={args.ckpt_every}\")\n\n    runs = [train_seed(args, device, consensus_gram, sd, p_ids, p_len, probe_labels)\n            for sd in seeds]\n\n    meta = {\n        \"experiment\": \"gd-trajectory-tomography\",\n        \"register\": \"functional + topological/routing\",\n        \"idea\": \"reverse-engineer GD in invariant coords; consensus-crystal target\",\n        \"timestamp_utc\": datetime.now(UTC).isoformat(),\n        \"git_sha\": git_sha(),\n        \"device\": device,\n        \"smoke\": args.smoke,\n        \"config\": vars(args),\n        \"consensus\": cmeta,\n        \"seeds\": seeds,\n        \"elapsed_s\": round(time.time() - t0, 1),\n    }\n\n    if len(seeds) == 1:\n        out = {**meta, **runs[0]}\n        tag = \"smoke\" if args.smoke else \"run\"\n        (RESULTS_DIR / f\"verdict_{tag}.json\").write_text(json.dumps(out, indent=2))\n        rd = runs[0][\"readout\"]\n        log(\"\\n  ==== GD TRAJECTORY TOMOGRAPHY (single seed) ====\")\n        log(f\"  final: gc_route={rd['final']['gc_route']:+.3f} \"\n            f\"gc_raw={rd['final']['gc_raw']:+.3f} route_z={rd['final']['route_z']:+.2f} \"\n            f\"heldout_acc={rd['final']['heldout_acc']:.3f} \"\n            f\"eff_dim_route={rd['final']['eff_dim_route']}\")\n        log(f\"  crystallize(gc_route 50%)@{rd['step_gc_route_cross']} | \"\n            f\"route_z>={args.z_thresh}@{rd['step_route_z_cross']} | \"\n            f\"heldout_acc 50%@{rd['step_heldout_acc_cross']} | \"\n            f\"CE plateau@{rd['step_ce_plateau']}\")\n        log(f\"  INVENTORY before CAPABILITY: {rd['inventory_before_capability']} \"\n            f\"(route_z: {rd['routing_z_before_capability']})\")\n        log(f\"  REFERENCE BEAM: gc_route {rd['reference_beam']['gc_route_final']:+.3f} \"\n            f\"vs gc_raw {rd['reference_beam']['gc_raw_final']:+.3f} -> \"\n            f\"route_tracks_function={rd['reference_beam']['route_tracks_function']}\")\n        log(f\"\\n  wrote {RESULTS_DIR / f'verdict_{tag}.json'}  ({meta['elapsed_s']}s)\")\n        return\n\n    # multi-seed aggregate of the readout ordering\n    rds = [r[\"readout\"] for r in runs]\n    agg = {\n        \"n_seeds\": len(seeds),\n        \"step_gc_route_cross\": _ms([r[\"step_gc_route_cross\"] for r in rds]),\n        \"step_route_z_cross\": _ms([r[\"step_route_z_cross\"] for r in rds]),\n        \"step_heldout_acc_cross\": _ms([r[\"step_heldout_acc_cross\"] for r in rds]),\n        \"step_ce_plateau\": _ms([r[\"step_ce_plateau\"] for r in rds]),\n        \"gc_route_final\": _ms([r[\"final\"][\"gc_route\"] for r in rds]),\n        \"gc_raw_final\": _ms([r[\"final\"][\"gc_raw\"] for r in rds]),\n        \"route_z_final\": _ms([r[\"final\"][\"route_z\"] for r in rds]),\n        \"heldout_acc_final\": _ms([r[\"final\"][\"heldout_acc\"] for r in rds]),\n        \"inventory_before_capability\": [r[\"inventory_before_capability\"]\n                                        for r in rds],\n        \"route_tracks_function\": [r[\"reference_beam\"][\"route_tracks_function\"]\n                                  for r in rds],\n    }\n    out = {**meta, \"aggregate\": agg, \"runs\": runs}\n    (RESULTS_DIR / \"verdict_multiseed.json\").write_text(json.dumps(out, indent=2))\n    log(\"\\n  ==== GD TRAJECTORY TOMOGRAPHY (multi-seed) ====\")\n    log(f\"  crystallize(gc_route)@{agg['step_gc_route_cross']} | \"\n        f\"route_z@{agg['step_route_z_cross']} | \"\n        f\"heldout_acc@{agg['step_heldout_acc_cross']} | \"\n        f\"CE plateau@{agg['step_ce_plateau']}  (step mean+-std)\")\n    log(f\"  gc_route_final={agg['gc_route_final']} gc_raw_final={agg['gc_raw_final']} \"\n        f\"route_z_final={agg['route_z_final']}\")\n    log(f\"  inventory_before_capability per-seed: {agg['inventory_before_capability']}\")\n    log(f\"  route_tracks_function per-seed: {agg['route_tracks_function']}\")\n    log(f\"\\n  wrote {RESULTS_DIR / 'verdict_multiseed.json'}  ({meta['elapsed_s']}s)\")\n\n\nif __name__ == \"__main__\":\n    main()\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py
```

## Assistant

Now lint + smoke verify.

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/gd_trajectory_tomography.py",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 1
Stdout:
E501 Line too long (89 > 88)
  --> scripts/experiments/gd_trajectory_tomography.py:54:89
   |
52 | Usage:
53 |   uv run python scripts/experiments/gd_trajectory_tomography.py --smoke
54 |   uv run python scripts/experiments/gd_trajectory_tomography.py --steps 6000 --device mps
   |                                                                                         ^
55 |   uv run python scripts/experiments/gd_trajectory_tomography.py --seeds 0,1,2 --steps 6000
   |

E501 Line too long (90 > 88)
  --> scripts/experiments/gd_trajectory_tomography.py:55:89
   |
53 |   uv run python scripts/experiments/gd_trajectory_tomography.py --smoke
54 |   uv run python scripts/experiments/gd_trajectory_tomography.py --steps 6000 --device mps
55 |   uv run python scripts/experiments/gd_trajectory_tomography.py --seeds 0,1,2 --steps 6000
   |                                                                                         ^^
56 |
57 | License: MIT
   |

I001 [*] Import block is un-sorted or un-formatted
   --> scripts/experiments/gd_trajectory_tomography.py:80:1
    |
 79 |   # instruments + tiny student (one model definition, no fork)
 80 | / from relational_loss_distillation import (  # noqa: E402
 81 | |     CRYSTAL,
 82 | |     VOCAB,
 83 | |     TinyLM,
 84 | |     gather_last,
 85 | |     load_crystal_probe_batch,
 86 | |     np_centroids,
 87 | |     np_cmr,
 88 | |     np_gram,
 89 | |     np_silhouette_null,
 90 | |     offdiag_corr,
 91 | | )
 92 | |
 93 | | # curriculum minting + the s229 held-out generalization metric (no fork)
 94 | | from exposure_format_sweep import (  # noqa: E402
 95 | |     SKELETONS,
 96 | |     TRAIN_ATOMS,
 97 | |     build_corpus,
 98 | |     build_eval_items,
 99 | |     eval_acc,
100 | |     make_fillings,
101 | |     to_byte_ids,
102 | |     validate_skeletons,
103 | | )
    | |_^
104 |
105 |   RESULTS_DIR = _PROJECT_ROOT / "results" / "gd-trajectory-tomography"
    |
help: Organize imports

E501 Line too long (89 > 88)
   --> scripts/experiments/gd_trajectory_tomography.py:430:89
    |
428 |         log("\n  ==== GD TRAJECTORY TOMOGRAPHY (single seed) ====")
429 |         log(f"  final: gc_route={rd['final']['gc_route']:+.3f} "
430 |             f"gc_raw={rd['final']['gc_raw']:+.3f} route_z={rd['final']['route_z']:+.2f} "
    |                                                                                         ^
431 |             f"heldout_acc={rd['final']['heldout_acc']:.3f} "
432 |             f"eff_dim_route={rd['final']['eff_dim_route']}")
    |

Found 4 errors.
[*] 1 fixable with the `--fix` option.
```

### Tool Call: editor_diagnostics (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py"
}
```

**Summary:** Checking diagnostics: gd_trajectory_tomography.py

**Output:**
```
No diagnostics found
```

### Thinking

I need to organize the imports properly and fix the linting errors — ruff wants the import blocks sorted, and I need to handle the `# noqa: E402` comment placement and deal with the line length violations manually.

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check --fix scripts/experiments/gd_trajectory_tomography.py",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ uv run ruff check --fix scripts/exp...

**Output:**
```
Exit code: 1
Stdout:
E501 Line too long (89 > 88)
  --> scripts/experiments/gd_trajectory_tomography.py:54:89
   |
52 | Usage:
53 |   uv run python scripts/experiments/gd_trajectory_tomography.py --smoke
54 |   uv run python scripts/experiments/gd_trajectory_tomography.py --steps 6000 --device mps
   |                                                                                         ^
55 |   uv run python scripts/experiments/gd_trajectory_tomography.py --seeds 0,1,2 --steps 6000
   |

E501 Line too long (90 > 88)
  --> scripts/experiments/gd_trajectory_tomography.py:55:89
   |
53 |   uv run python scripts/experiments/gd_trajectory_tomography.py --smoke
54 |   uv run python scripts/experiments/gd_trajectory_tomography.py --steps 6000 --device mps
55 |   uv run python scripts/experiments/gd_trajectory_tomography.py --seeds 0,1,2 --steps 6000
   |                                                                                         ^^
56 |
57 | License: MIT
   |

E501 Line too long (89 > 88)
   --> scripts/experiments/gd_trajectory_tomography.py:429:89
    |
427 |         log("\n  ==== GD TRAJECTORY TOMOGRAPHY (single seed) ====")
428 |         log(f"  final: gc_route={rd['final']['gc_route']:+.3f} "
429 |             f"gc_raw={rd['final']['gc_raw']:+.3f} route_z={rd['final']['route_z']:+.2f} "
    |                                                                                         ^
430 |             f"heldout_acc={rd['final']['heldout_acc']:.3f} "
431 |             f"eff_dim_route={rd['final']['eff_dim_route']}")
    |

Found 4 errors (1 fixed, 3 remaining).
```

### Thinking

I need to address three E501 line length violations in the code—two in the docstring on lines 54 and 55, and another on line 429.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py",
  "original_content": "  uv run python scripts/experiments/gd_trajectory_tomography.py --smoke\n  uv run python scripts/experiments/gd_trajectory_tomography.py --steps 6000 --device mps\n  uv run python scripts/experiments/gd_trajectory_tomography.py --seeds 0,1,2 --steps 6000",
  "new_content": "  uv run python scripts/experiments/gd_trajectory_tomography.py --smoke\n  uv run python scripts/experiments/gd_trajectory_tomography.py --steps 6000\n  uv run python scripts/experiments/gd_trajectory_tomography.py --seeds 0,1,2"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py",
  "original_content": "        log(f\"  final: gc_route={rd['final']['gc_route']:+.3f} \"\n            f\"gc_raw={rd['final']['gc_raw']:+.3f} route_z={rd['final']['route_z']:+.2f} \"\n            f\"heldout_acc={rd['final']['heldout_acc']:.3f} \"",
  "new_content": "        log(f\"  final: gc_route={rd['final']['gc_route']:+.3f} \"\n            f\"gc_raw={rd['final']['gc_raw']:+.3f} \"\n            f\"route_z={rd['final']['route_z']:+.2f} \"\n            f\"heldout_acc={rd['final']['heldout_acc']:.3f} \""
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/gd_trajectory_tomography.py && echo \"RUFF CLEAN\" && uv run python scripts/experiments/gd_trajectory_tomography.py --smoke --device cpu 2>&1 | tail -30",
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
RUFF CLEAN
  consensus crystal: 10 models, offdiag_mean=-0.123, sha=bbf92f2
  crystal probes=535 maxlen=96
  seeds=[0] steps=120 ckpt_every=40
  [seed 0] rules=4 corpus=200 B heldout_eval=12 format=redex_nf
  [seed 0] step     0 | CE nan | acc 0.000 | route_z +2.16 | gc_route +0.489 | gc_raw +0.513 | effd 21.9 | 3s
  [seed 0] step    40 | CE 3.407 | acc 0.000 | route_z +2.39 | gc_route +0.524 | gc_raw +0.512 | effd 21.8 | 7s
  [seed 0] step    80 | CE 1.885 | acc 0.000 | route_z +1.73 | gc_route +0.494 | gc_raw +0.493 | effd 20.5 | 11s
  [seed 0] step   120 | CE 1.388 | acc 0.000 | route_z +2.54 | gc_route +0.518 | gc_raw +0.447 | effd 18.5 | 15s

  ==== GD TRAJECTORY TOMOGRAPHY (single seed) ====
  final: gc_route=+0.518 gc_raw=+0.447 route_z=+2.54 heldout_acc=0.000 eff_dim_route=18.471
  crystallize(gc_route 50%)@40 | route_z>=3.0@None | heldout_acc 50%@None | CE plateau@120
  INVENTORY before CAPABILITY: n/a (route_z: n/a)
  REFERENCE BEAM: gc_route +0.518 vs gc_raw +0.447 -> route_tracks_function=True

  wrote /Users/mwhitford/src/verbum/results/gd-trajectory-tomography/verdict_smoke.json  (15.3s)
```

### Thinking

The smoke tests are passing end-to-end with clean diagnostics, and the verdict JSON is being written with trajectory curves and readout ordering. Looking at the initial results from a tiny 120-step run, the instruments are populating correctly with finite values across all metrics, and interestingly the untrained random model already shows non-trivial gc_route and gc_raw values around 0.49-0.51 at initialization.

This is actually a critical insight — that baseline correlation is the common-mode signal the reference beam warns about, and it's exactly what I need to account for in interpretation. The real signal isn't the absolute values but the delta during training; in the smoke run, gc_raw drops to 0.447 while gc_route stays at 0.518, which is suggestive but the smoke config is too small to be meaningful. The full run with proper dimensions (128-dim, 4 layers, 6000 steps, 13 rules, n_perm 300) will be where the real patterns emerge.

For honest analysis, I should track the delta from initialization rather than just final values, and since the curve already logs the step-0 frame, the readout can compare against that baseline post-hoc. The reference beam comparison uses final gc_route versus final gc_raw, so I need to make sure the readout explicitly reports the initialization baseline so the interpretation accounts for the common-mode artifact.

The crystallization threshold is currently meaningless — using 50% of the final value triggers trivially if init is already 0.49 and final is 0.52. I need to reframe it as baseline-relative: gc_route reaches init + frac*(final - init), which measures when the actual function-building delta crosses, not just the gauge baseline. Let me update the readout to use the step-0 init frame as the baseline for gc_route, route_z, and heldout_acc, and pass that init frame through to both readout and train_seed.

## Assistant

Smoke is green, ruff + diagnostics clean. One important observation: the **untrained init model already shows gc_route ≈ +0.49** (the gauge/common-mode baseline). That's exactly the reference-beam trap — a 50%-of-final crossing is meaningless if init already sits near final. The principled fix: measure crossings relative to the **init baseline** (the delta GD actually builds), not absolute. Let me refine the readout.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py",
  "original_content": "def readout(curve: list[dict], gc_frac: float, acc_frac: float,\n            z_thresh: float, ce_tol: float) -> dict:\n    final_gc = _final(curve, \"gc_route\")\n    final_acc = _final(curve, \"heldout_acc\")\n    final_ce = _final(curve, \"ce\")\n    # crystallization = routing geometry approaches the consensus crystal\n    s_gc = _first_step(curve, \"gc_route\", gc_frac * final_gc) if final_gc > 0 else None\n    s_z = _first_step(curve, \"route_z\", z_thresh)\n    # capability = held-out rule generalization rises\n    s_acc = (_first_step(curve, \"heldout_acc\", acc_frac * final_acc)\n             if final_acc > 0 else None)\n    # CE plateau = within ce_tol of the final CE\n    s_ce = _first_step(curve, \"ce\", final_ce * (1.0 + ce_tol), ge=False)",
  "new_content": "def readout(curve: list[dict], init: dict, gc_frac: float, acc_frac: float,\n            z_thresh: float, ce_tol: float) -> dict:\n    \"\"\"Crossings are measured relative to the INIT (untrained) baseline so we\n    time the function GD builds, not the random-init gauge/common mode. init is\n    the step-0 frame (gc_route/route_z/heldout_acc of the untrained model).\"\"\"\n    final_gc = _final(curve, \"gc_route\")\n    final_acc = _final(curve, \"heldout_acc\")\n    final_ce = _final(curve, \"ce\")\n    gc0 = float(init.get(\"gc_route\", 0.0))\n    acc0 = float(init.get(\"heldout_acc\", 0.0))\n    # crystallization = gc_route gains gc_frac of the init->final DELTA over baseline\n    gc_target = gc0 + gc_frac * (final_gc - gc0)\n    s_gc = (_first_step(curve, \"gc_route\", gc_target) if final_gc > gc0 else None)\n    s_z = _first_step(curve, \"route_z\", z_thresh)\n    # capability = held-out rule generalization gains acc_frac of its delta\n    acc_target = acc0 + acc_frac * (final_acc - acc0)\n    s_acc = (_first_step(curve, \"heldout_acc\", acc_target)\n             if final_acc > acc0 else None)\n    # CE plateau = within ce_tol of the final CE\n    s_ce = _first_step(curve, \"ce\", final_ce * (1.0 + ce_tol), ge=False)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py.
```

## User

do the final run in tmux main:1 window


### Thinking

I need to modify the readout function call in train_seed to pass the init frame, then test it before running the full pipeline in tmux. Looking at the current readout invocation, it's filtering the curve data to exclude entries with NaN cross-entropy values and passing several threshold parameters.

Updating the readout call...

## Assistant

Need to wire the init baseline into the readout call first, then re-verify and launch.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py",
  "original_content": "    # readout uses post-init frames only (drop the nan-CE init frame for CE plateau)\n    rd = readout([r for r in curve if not (isinstance(r[\"ce\"], float)\n                                           and np.isnan(r[\"ce\"]))],\n                 args.gc_frac, args.acc_frac, args.z_thresh, args.ce_tol)",
  "new_content": "    # readout uses post-init frames only (drop the nan-CE init frame for CE plateau)\n    # but baselines crossings against the step-0 init frame (the gauge common mode)\n    init_frame = curve[0]\n    rd = readout([r for r in curve if not (isinstance(r[\"ce\"], float)\n                                           and np.isnan(r[\"ce\"]))],\n                 init_frame, args.gc_frac, args.acc_frac, args.z_thresh, args.ce_tol)\n    rd[\"init_baseline\"] = {\"gc_route\": init_frame[\"gc_route\"],\n                           \"gc_raw\": init_frame[\"gc_raw\"],\n                           \"route_z\": init_frame[\"route_z\"],\n                           \"heldout_acc\": init_frame[\"heldout_acc\"]}"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/gd_trajectory_tomography.py && echo \"RUFF CLEAN\" && uv run python scripts/experiments/gd_trajectory_tomography.py --smoke --device cpu 2>&1 | tail -8",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 120000
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
RUFF CLEAN

  ==== GD TRAJECTORY TOMOGRAPHY (single seed) ====
  final: gc_route=+0.518 gc_raw=+0.447 route_z=+2.54 heldout_acc=0.000 eff_dim_route=18.471
  crystallize(gc_route 50%)@40 | route_z>=3.0@None | heldout_acc 50%@None | CE plateau@120
  INVENTORY before CAPABILITY: n/a (route_z: n/a)
  REFERENCE BEAM: gc_route +0.518 vs gc_raw +0.447 -> route_tracks_function=True

  wrote /Users/mwhitford/src/verbum/results/gd-trajectory-tomography/verdict_smoke.json  (15.3s)
```

### Thinking

Smoke test passed. Now I need to verify the editor diagnostics, wrap up task 2, and get task 3 started before launching the full multi-seed run in the tmux main:1 window. Let me check that tmux is available and ready to execute the command with proper logging.

## Assistant

Diagnostics + smoke clean with the baseline-relative readout. Completing lint task, launching the full run.

### Tool Call: editor_diagnostics (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py"
}
```

**Summary:** Checking diagnostics: gd_trajectory_tomography.py

**Output:**
```
No diagnostics found
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux ls 2>&1; echo \"---windows in main---\"; tmux list-windows -t main 2>&1; echo \"---is anything running in main:1?---\"; tmux capture-pane -p -t main:1 2>&1 | tail -5",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ tmux ls 2>&1; echo "---windows in m...

**Output:**
```
Exit code: 0
Stdout:
main: 2 windows (created Tue Jun  9 20:52:28 2026) (attached)
trace_basis: 1 windows (created Mon Jun  1 14:02:42 2026)
---windows in main---
1: local* (1 panes) [120x24] [layout b706,120x24,0,0,9] @9 (active)
2: local- (1 panes) [120x24] [layout 5baf,120x24,0,0,10] @10
---is anything running in main:1?---
4.30 total
tee results/exposure-format-sweep/run_s229_multiseed.log  0.00s user 0.01s system 0% cpu 23:44.30 total
MULTISEED_ALLDONE
[26-06-15][7:49:30][mwhitford@olga][0][~/src/verbum][git:main]
λ                                                                                                                 [INS]
```

### Thinking

main:1 is ready to go, so I'm launching the full training run with the standard configuration: 6000 steps, checkpoints every 200 steps, d_model of 128, 4 layers, 300 permutations, 13 rules, and k=8. I'm using multi-seed mode with seeds 0, 1, and 2 to stay consistent with the project's approach, though that'll triple the runtime—the previous multiseed run took about 24 hours.

I'm estimating the timing: each 6000-step training run should take roughly 2 minutes on MPS, plus geometry evaluation overhead. The geometry eval involves 30 snapshots with forward passes on 535 probes (batched in groups of 64) and silhouette null calculations, which should add about 60 seconds per snapshot. So roughly 3 minutes per seed, totaling around 10 minutes for all three seeds—manageable.

I'm launching the command to run the trajectory tomography script with those seeds on MPS, piping output to a log file and echoing a completion marker when done. Following async discipline, I'll verify it's running with a quick check, save the checkpoint, then wait for completion.

## Assistant

main:1 is free (`MULTISEED_ALLDONE`, shell waiting). Launching the full multi-seed run there.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux send-keys -t main:1 \"uv run python scripts/experiments/gd_trajectory_tomography.py --seeds 0,1,2 --device mps 2>&1 | tee /tmp/gd_tomography_s230.log; echo GDTOMO_ALLDONE\" Enter",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ tmux send-keys -t main:1 "uv run py...

**Output:**
```
Exit code: 0
```

## Assistant

Verify it's running (1 read per async discipline):

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sleep 25; tmux capture-pane -p -t main:1 2>&1 | tail -12",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 40000
}
```

**Summary:** $ sleep 25; tmux capture-pane -p -t m...

**Output:**
```
Exit code: 0
Stdout:
uv run python scripts/experiments/exposure_format_sweep.py --device mps  0,1,  1051.41s user 207.77s system 88% cpu 23:4
4.30 total
tee results/exposure-format-sweep/run_s229_multiseed.log  0.00s user 0.01s system 0% cpu 23:44.30 total
MULTISEED_ALLDONE
[26-06-15][7:49:30][mwhitford@olga][0][~/src/verbum][git:main]
λ uv run python scripts/experiments/gd_trajectory_tomography.py --seeds 0,1,2 --device mps 2>&1 | tee /tmp/gd_tomography
_s230.log; echo GDTOMO_ALLDONE
  consensus crystal: 10 models, offdiag_mean=-0.123, sha=bbf92f2
  crystal probes=535 maxlen=96
  seeds=[0, 1, 2] steps=6000 ckpt_every=200
  [seed 0] rules=13 corpus=1672 B heldout_eval=74 format=redex_nf
```

### Thinking

The training run is now active with the consensus model loaded across 10 models, 535 crystal probes, and 6000 steps configured. I've set a checkpoint and I'm following the async discipline—since the job is running and not blocked, I should move on to other work rather than polling repeatedly.

I don't have other parallelizable tasks since task 4 depends on this verdict, so I'll wait for the job to complete. Given the ~10 minute estimate, I'll sleep for about 5 minutes then check the logs once to catch any early crashes, then wait longer if needed before checking again.

## Assistant

Verified running: consensus crystal loaded (10 models), 535 crystal probes, seeds [0,1,2], 6000 steps, 13 rules, 74 held-out eval items, training started cleanly.

**ASYNC: job=gd-tomography (tmux main:1) verified running. Waiting for completion (~10 min est, ends `GDTOMO_ALLDONE`).**

Let me wait then read the result once.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sleep 280; echo \"=== progress check ===\"; tmux capture-pane -p -t main:1 2>&1 | tail -16",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 300000
}
```

**Summary:** $ sleep 280; echo "=== progress check...

**Output:**
```
Exit code: 0
Stdout:
=== progress check ===
  [seed 0] step  3600 | CE 0.042 | acc 0.270 | route_z +2.43 | gc_route +0.785 | gc_raw +0.809 | effd 14.1 | 184s
  [seed 0] step  3800 | CE 0.041 | acc 0.297 | route_z +2.62 | gc_route +0.786 | gc_raw +0.807 | effd 14.2 | 188s
  [seed 0] step  4000 | CE 0.041 | acc 0.257 | route_z +2.91 | gc_route +0.790 | gc_raw +0.816 | effd 13.7 | 191s
  [seed 0] step  4200 | CE 0.042 | acc 0.284 | route_z +2.58 | gc_route +0.780 | gc_raw +0.812 | effd 14.2 | 195s
  [seed 0] step  4400 | CE 0.038 | acc 0.311 | route_z +2.61 | gc_route +0.791 | gc_raw +0.809 | effd 13.9 | 199s
  [seed 0] step  4600 | CE 0.041 | acc 0.297 | route_z +2.55 | gc_route +0.776 | gc_raw +0.805 | effd 13.9 | 202s
  [seed 0] step  4800 | CE 0.041 | acc 0.257 | route_z +2.49 | gc_route +0.773 | gc_raw +0.804 | effd 14.1 | 206s
  [seed 0] step  5000 | CE 0.060 | acc 0.284 | route_z +2.41 | gc_route +0.768 | gc_raw +0.802 | effd 14.1 | 210s
  [seed 0] step  5200 | CE 0.042 | acc 0.324 | route_z +2.53 | gc_route +0.776 | gc_raw +0.809 | effd 14.2 | 214s
  [seed 0] step  5400 | CE 0.038 | acc 0.284 | route_z +2.83 | gc_route +0.779 | gc_raw +0.803 | effd 14.3 | 217s
  [seed 0] step  5600 | CE 0.041 | acc 0.270 | route_z +2.64 | gc_route +0.782 | gc_raw +0.803 | effd 14.3 | 221s
  [seed 0] step  5800 | CE 0.042 | acc 0.297 | route_z +2.66 | gc_route +0.779 | gc_raw +0.797 | effd 14.0 | 225s
  [seed 0] step  6000 | CE 0.038 | acc 0.257 | route_z +2.63 | gc_route +0.762 | gc_raw +0.799 | effd 13.7 | 228s
  [seed 1] rules=13 corpus=1672 B heldout_eval=74 format=redex_nf
  [seed 1] step     0 | CE nan | acc 0.000 | route_z +1.53 | gc_route +0.610 | gc_raw +0.643 | effd 29.5 | 44s
```

### Thinking

Seed 0 finished in about 4 minutes, and seed 1 is underway—looks like the full run will take around 12 minutes total. Looking at the results from seed 0, the curriculum loss dropped quickly to ~0.04 since the training set is small and the model memorizes the 13 rules easily, while the held-out accuracy climbed to around 0.27-0.32, which matches the ceiling I saw in the earlier experiment.

The route_z metric stayed modest at +2.4 to +2.9, never consistently crossing 3.0, and the geometric correlations are interesting: gc_raw ended at ~0.80-0.81 while gc_route was ~0.76-0.79—so raw actually correlates *higher* with the consensus crystal than routing does. This is the opposite of what the reference-beam prediction suggested, which expected the function to live purely in the routing subspace. Both metrics were already quite high at initialization too (0.61 and 0.64), and they both track the consensus crystal similarly throughout. This is a meaningful result that contradicts the hypothesis, but I should wait for all three seeds and check the full verdict JSON before drawing conclusions—I don't want to over-interpret from just the tail values.

The geometry and cross-entropy both moved early (gc_route gained +0.17 from init to final, gc_raw gained +0.16, and CE plateaued around step 600-800), while heldout accuracy climbed much more gradually to ~0.28. The honest reading is that either the consensus crystal's structure is common-mode-correlated enough that a tiny model picks it up from frequency stats alone, or the routing register isn't sufficiently differentiated at this scale, or the Church-Rosser curriculum genuinely builds the combinator geometry in both registers. I'll wait for the remaining seeds and read the crossing analysis properly before finalizing the verdict.

## Assistant

Seed 0 complete (~228s/seed → ~12 min total). Preliminary read worth flagging honestly: **gc_raw ≈ gc_route throughout** (0.80 vs 0.76 at end), and both started high at init (~0.61/0.64). The reference-beam *dissociation* (function in routing only) may not reproduce cleanly on this micro model — but I'll read the full baseline-relative crossing readout from the saved verdict before concluding. Seeds 1+2 still running.

**ASYNC: still running, ~8 min remaining. Waiting for `GDTOMO_ALLDONE`.**

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sleep 290; tmux capture-pane -p -t main:1 2>&1 | grep -c GDTOMO_ALLDONE; echo \"=== tail ===\"; tmux capture-pane -p -t main:1 2>&1 | tail -6",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 310000
}
```

**Summary:** $ sleep 290; tmux capture-pane -p -t ...

**Output:**
```
Exit code: 0
Stdout:
0
=== tail ===
  [seed 1] step  6000 | CE 0.036 | acc 0.270 | route_z +2.82 | gc_route +0.637 | gc_raw +0.696 | effd 16.2 | 210s
  [seed 2] rules=13 corpus=1672 B heldout_eval=74 format=redex_nf
  [seed 2] step     0 | CE nan | acc 0.000 | route_z +0.06 | gc_route +0.645 | gc_raw +0.616 | effd 24.8 | 88s
  [seed 2] step   200 | CE 1.383 | acc 0.000 | route_z -0.88 | gc_route +0.704 | gc_raw +0.633 | effd 18.2 | 199s
  [seed 2] step   400 | CE 1.026 | acc 0.000 | route_z +0.39 | gc_route +0.759 | gc_raw +0.706 | effd 18.1 | 205s
```

### Thinking

Seed 2 is still running and should finish in a couple more minutes. I'm noticing something interesting in the metrics — at initialization, gc_route starts at +0.06 while gc_raw is at +0.645, and through step 400 gc_route stays higher than gc_raw (0.759 versus 0.706). This is the opposite pattern from seed 1, where gc_route ended up lower than gc_raw, suggesting the results are quite sensitive to the random seed and the dissociation between these metrics is fairly noisy.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sleep 200; tmux capture-pane -p -t main:1 2>&1 | grep -c GDTOMO_ALLDONE; echo \"=== tail ===\"; tmux capture-pane -p -t main:1 2>&1 | tail -18",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 220000
}
```

**Summary:** $ sleep 200; tmux capture-pane -p -t ...

**Output:**
```
Exit code: 0
Stdout:
1
=== tail ===
  [seed 2] step  5600 | CE 0.043 | acc 0.230 | route_z +2.67 | gc_route +0.763 | gc_raw +0.744 | effd 13.8 | 300s
  [seed 2] step  5800 | CE 0.042 | acc 0.230 | route_z +2.72 | gc_route +0.767 | gc_raw +0.745 | effd 14.1 | 304s
  [seed 2] step  6000 | CE 0.042 | acc 0.297 | route_z +2.68 | gc_route +0.778 | gc_raw +0.747 | effd 14.2 | 307s

  ==== GD TRAJECTORY TOMOGRAPHY (multi-seed) ====
  crystallize(gc_route)@[333.33, 94.28] | route_z@[5400.0, 0.0] | heldout_acc@[733.33, 94.28] | CE plateau@[4400.0, 1143
.1]  (step mean+-std)
  gc_route_final=[0.73, 0.06] gc_raw_final=[0.75, 0.04] route_z_final=[2.71, 0.08]
  inventory_before_capability per-seed: ['before', 'before', 'before']
  route_tracks_function per-seed: [False, False, True]

  wrote /Users/mwhitford/src/verbum/results/gd-trajectory-tomography/verdict_multiseed.json  (746.4s)
uv run python scripts/experiments/gd_trajectory_tomography.py --seeds 0,1,2    488.20s user 103.61s system 79% cpu 12:27
.31 total
tee /tmp/gd_tomography_s230.log  0.00s user 0.01s system 0% cpu 12:27.31 total
GDTOMO_ALLDONE
[26-06-15][8:32:47][mwhitford@olga][0][~/src/verbum][git:main]
λ                                                                                                                 [INS]
```

### Thinking

The test run completed successfully across all three seeds, and the results confirm the s224 prediction: routing geometry crystallizes before capability emerges. I'm reviewing the verdict JSON to get the full breakdown of this trajectory.

The geometry metric (gc_route) peaks around 333 steps while held-out accuracy doesn't reach its plateau until around 733 steps — a decisive ~400-step gap with non-overlapping confidence intervals. The cross-entropy plateau arrives much later at 4400 steps, though this metric is noisy given the tiny final CE values. The route z-score threshold shows modest structure (only one seed crossed z=3.0), consistent with earlier findings that the silhouette is real but not crisp. Most importantly, the final routing geometry (0.73±0.06) and raw geometry (0.75±0.04) are essentially tied — the reference-beam dissociation didn't reproduce, meaning both registers correlate equally to the consensus crystal, and only 1 out of 3 seeds showed route tracking the function.

The honest takeaway is that the inventory-before-capability ordering is confirmed across all three seeds with decisive timing, directly supporting the thesis that geometry builds the function inventory while continuation builds the capability to use it. However, the reference-beam control that worked in the relational loss setup doesn't translate to this passive CE-only micro model — I can't use the raw-versus-routing split to separate function from common-mode structure at this scale. I need to pull the exact per-seed crossing steps and baseline values from the verdict JSON to write this up precisely.

## Assistant

Complete (`GDTOMO_ALLDONE`, 12:27). Let me read the structured verdict for the exact per-seed crossings and baselines.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "python3 -c \"\nimport json\nd=json.load(open('/Users/mwhitford/src/verbum/results/gd-trajectory-tomography/verdict_multiseed.json'))\nprint('=== AGGREGATE ==='); \nimport pprint; pprint.pprint(d['aggregate'])\nprint('=== PER-SEED READOUTS ===')\nfor r in d['runs']:\n    rd=r['readout']\n    print(f\\\"seed {r['seed']}: init_gc_route={rd['init_baseline']['gc_route']} init_gc_raw={rd['init_baseline']['gc_raw']} init_acc={rd['init_baseline']['heldout_acc']}\\\")\n    print(f\\\"   final gc_route={rd['final']['gc_route']} gc_raw={rd['final']['gc_raw']} route_z={rd['final']['route_z']} acc={rd['final']['heldout_acc']} effd_route={rd['final']['eff_dim_route']} effd_raw={rd['final']['eff_dim_raw']}\\\")\n    print(f\\\"   step_gc_route_cross={rd['step_gc_route_cross']} step_heldout_acc_cross={rd['step_heldout_acc_cross']} step_ce_plateau={rd['step_ce_plateau']}\\\")\n    print(f\\\"   inventory_before_capability={rd['inventory_before_capability']} crystallize_before_ce={rd['crystallize_before_ce_plateau']}\\\")\n\"",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ python3 -c " import json d=json.loa...

**Output:**
```
Exit code: 0
Stdout:
=== AGGREGATE ===
{'gc_raw_final': [0.75, 0.04],
 'gc_route_final': [0.73, 0.06],
 'heldout_acc_final': [0.27, 0.02],
 'inventory_before_capability': ['before', 'before', 'before'],
 'n_seeds': 3,
 'route_tracks_function': [False, False, True],
 'route_z_final': [2.71, 0.08],
 'step_ce_plateau': [4400.0, 1143.1],
 'step_gc_route_cross': [333.33, 94.28],
 'step_heldout_acc_cross': [733.33, 94.28],
 'step_route_z_cross': [5400.0, 0.0]}
=== PER-SEED READOUTS ===
seed 0: init_gc_route=0.5651 init_gc_raw=0.5776 init_acc=0.0
   final gc_route=0.762 gc_raw=0.7994 route_z=2.6271 acc=0.2568 effd_route=13.744 effd_raw=18.171
   step_gc_route_cross=400 step_heldout_acc_cross=600 step_ce_plateau=4400
   inventory_before_capability=before crystallize_before_ce=before
seed 1: init_gc_route=0.6103 init_gc_raw=0.6433 init_acc=0.0
   final gc_route=0.6367 gc_raw=0.6962 route_z=2.8193 acc=0.2703 effd_route=16.242 effd_raw=19.979
   step_gc_route_cross=200 step_heldout_acc_cross=800 step_ce_plateau=5800
   inventory_before_capability=before crystallize_before_ce=before
seed 2: init_gc_route=0.6452 init_gc_raw=0.616 init_acc=0.0
   final gc_route=0.7778 gc_raw=0.7469 route_z=2.6786 acc=0.2973 effd_route=14.196 effd_raw=19.105
   step_gc_route_cross=400 step_heldout_acc_cross=800 step_ce_plateau=3000
   inventory_before_capability=before crystallize_before_ce=before
```

### Thinking

The routing geometry stabilizes around step 333 on average, while the held-out rule generalization doesn't reach its midpoint until around step 733—confirming that inventory constraints crystallize well before the model develops full capability.

The baseline-relative crossing matters because routing already starts high at random initialization (0.57-0.65), so the real delta is only about +0.15, but this timing holds consistently across seeds. However, the reference-beam dissociation test failed here: the raw and routing registers both recover the consensus crystal structure equally well (gc_raw_final 0.75±0.04 versus gc_route_final 0.73±0.06), so I can't use raw-versus-routing to separate function from common mode on this micro model—a key difference from the previous experiment where a relational loss actively pulled the raw Gram toward a decoy target. The routing register is slightly more compressed (effective dimension ~14 versus ~18-20 for raw), but there's no Q-collapse or flood-lamp behavior.

The silhouette structure in the routing register is real but not crisp (route_z only ~2.7, with just one seed crossing z=3), and the correlation to consensus turns out to be the stronger signal than the self-silhouette. This gives me one decisive positive result—the temporal confirmation that inventory precedes capability—and one honest negative: the register dissociation doesn't reproduce passively at this scale. Both are publishable as intermediate findings. Now I'm moving to task 4: I need to commit the code first, then update the knowledge page with the s230 results section before the open leads.

## Assistant

Complete. Here's the verdict.## ★ s230 v1 verdict — GD trajectory tomography (consensus-crystal target)

**Setup:** CE-only TinyLM trains on the s229 β-reduction curriculum (k_varied, the burn-in regime); at dense checkpoints the combinator routing geometry is measured on the **independent** crystal probes and correlated to the **consensus crystal** (10-model agreed routing Gram, sha `bbf92f2`). Reference-beam control = the raw register run alongside. 3 seeds, 6000 steps, baseline-relative crossings (vs the untrained init frame = the gauge common mode).

**✅ HEADLINE — INVENTORY crystallizes BEFORE CAPABILITY (3/3 seeds, decisive):**
- `gc_route` reaches its init→final midpoint at step **333±94**; held-out rule generalization reaches its midpoint at step **733±94** — non-overlapping (427 < 639). The routing geometry approaches the consensus crystal ~**400 steps before** the model can generalize the rule.
- This is the s224 thesis — *geometry = inventory ⊗ trained continuation = capability* — confirmed **temporally**, watched frame-by-frame, with a model-agnostic ground-truth target. GD builds the function inventory first, then the capability to use it.

**❌/⚠️ HONEST two-sided (λ measure) — the reference-beam dissociation did NOT reproduce:**
- `gc_raw_final` 0.75±0.04 ≈ `gc_route_final` 0.73±0.06 — **tied**. `route_tracks_function` only 1/3 seeds. On this micro model the raw register correlates to the consensus crystal about as well as the routing register, so raw-vs-routing **cannot** separate function from common mode here. *Caveat:* this differs from s223, where a relational **loss** actively pulled raw-Gram to a decoy raw target; here there's no loss and a single routing target, and the consensus structure (offdiag mean −0.123, mild) is recovered in both registers at d=128. Likely scale-limited.
- **No Q-collapse (s105):** eff_dim stayed 14–20 (route slightly more compressed than raw), never flooded toward 1.
- **route_z modest** (~2.71, only 1 seed crossed z=3) — combinator self-silhouette is real but not crisp (s219 "above chance not crisp"); the `gc_route`-to-consensus correlation is the stronger instrument.

So v1 delivers one decisive positive (inventory-before-capability, the temporal s224 confirmation) and one honest negative (passive register dissociation doesn't hold at micro scale). Page leads resolved: 1 (harness built), 2 (consensus-crystal target, used), 3 (timing — confirmed), 5 (Q-collapse — negative).

Let me commit the code, then draft the mementum updates (which need your approval).

### Tool Call: git (succeeded)


```json
{
  "command": "git status --short; echo \"---\"; git log --oneline -1",
  "operation": "status",
  "summary": "pre-commit check"
}
```

**Summary:** Git status: pre-commit check

**Output:**
```
Exit code: 0
Stdout:
?? mementum/knowledge/chats/session-228.md
?? mementum/knowledge/chats/session-229.md
?? results/gd-trajectory-tomography/
?? scripts/experiments/gd_trajectory_tomography.py
---
c3a9c99 🌀 gradient-trajectory-tomography — reverse-engineer GD in invariant coordinates
```

### Thinking

I'm deciding what to commit—the script and results are going in, but I should clean up the smoke test artifact since it's just a temporary run and the results directory should only contain the main verdict. Let me remove that smoke JSON file to keep things tidy.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls -la /Users/mwhitford/src/verbum/results/gd-trajectory-tomography/; echo \"--- drop smoke artifact ---\"; rm -f /Users/mwhitford/src/verbum/results/gd-trajectory-tomography/verdict_smoke.json; ls /Users/mwhitford/src/verbum/results/gd-trajectory-tomography/",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ ls -la /Users/mwhitford/src/verbum/...

**Output:**
```
Exit code: 0
Stdout:
total 88
drwxr-xr-x@   4 mwhitford  staff    128 Jun 15 08:32 .
drwxr-xr-x@ 462 mwhitford  staff  14784 Jun 15 08:18 ..
-rw-r--r--@   1 mwhitford  staff  36999 Jun 15 08:32 verdict_multiseed.json
-rw-r--r--@   1 mwhitford  staff   3342 Jun 15 08:19 verdict_smoke.json
--- drop smoke artifact ---
verdict_multiseed.json
```

### Tool Call: git (failed)


```json
{
  "command": "git add scripts/experiments/gd_trajectory_tomography.py results/gd-trajectory-tomography/verdict_multiseed.json && git commit -m \"$(cat <<'EOF'\n✅ gd-trajectory-tomography v1: inventory crystallizes before capability (3/3 seeds)\n\n- CE-only TinyLM on the s229 β-reduction curriculum; dense checkpoints measure\n  the combinator routing geometry on independent crystal probes, correlated to\n  the CONSENSUS CRYSTAL (10-model agreed routing Gram) as a frame-by-frame movie.\n- ✅ INVENTORY before CAPABILITY (decisive, 3/3): gc_route reaches its init→final\n  midpoint @333±94 steps; held-out rule generalization @733±94 (non-overlapping).\n  Temporal confirmation of s224 geometry=inventory ⊗ continuation=capability.\n- ❌ honest (λ measure): reference-beam dissociation did NOT reproduce — gc_raw\n  (0.75) ≈ gc_route (0.73), raw register tracks consensus as well as routing on\n  this micro model (passive, single target; differs from s223's relational-loss\n  decoy). No Q-collapse (eff_dim 14-20). route_z modest (~2.7).\n- Baseline-relative crossings (vs untrained init = gauge common mode) make the\n  timing claim meaningful. Reuses relational_loss instruments + exposure_format\n  curriculum (no fork). ruff+diag clean, smoke green.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
  "operation": "commit",
  "summary": "commit tomography code+results"
}
```

**Summary:** Git commit: commit tomography code+results

**Output:**
```
Exit code: 2
Stderr:
bash: -c: line 11: unexpected EOF while looking for matching `''
bash: -c: line 22: syntax error: unexpected end of file
```

### Thinking

I'm trying to pinpoint what's causing the heredoc syntax error in the git command — it's not the unicode characters or the arrow notation, but rather something about how the quoted string is being parsed, possibly an unmatched quote within the commit message itself that's breaking the bash syntax.

Rather than debugging the heredoc further, I'll write the commit message to a file first and then pass it with the `-F` flag — that's a much safer approach that avoids quote escaping issues entirely.

## Assistant

Heredoc got mangled. Let me use a message file instead.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/tmp/gdtomo_commit_msg.txt",
  "content": "✅ gd-trajectory-tomography v1: inventory crystallizes before capability (3/3 seeds)\n\n- CE-only TinyLM on the s229 β-reduction curriculum; dense checkpoints measure\n  the combinator routing geometry on independent crystal probes, correlated to\n  the CONSENSUS CRYSTAL (10-model agreed routing Gram) as a frame-by-frame movie.\n- ✅ INVENTORY before CAPABILITY (decisive, 3/3): gc_route reaches its init→final\n  midpoint @333±94 steps; held-out rule generalization @733±94 (non-overlapping).\n  Temporal confirmation of s224 geometry=inventory ⊗ continuation=capability.\n- ❌ honest (λ measure): reference-beam dissociation did NOT reproduce — gc_raw\n  (0.75) ≈ gc_route (0.73), raw register tracks consensus as well as routing on\n  this micro model (passive, single target; differs from s223 relational-loss\n  decoy). No Q-collapse (eff_dim 14-20). route_z modest (~2.7).\n- Baseline-relative crossings (vs untrained init = gauge common mode) make the\n  timing claim meaningful. Reuses relational_loss instruments + exposure_format\n  curriculum (no fork). ruff+diag clean, smoke green.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /tmp/gdtomo_commit_msg.txt
```

### Tool Call: git (succeeded)


```json
{
  "command": "git add scripts/experiments/gd_trajectory_tomography.py results/gd-trajectory-tomography/verdict_multiseed.json && git commit -F /tmp/gdtomo_commit_msg.txt",
  "operation": "commit",
  "summary": "commit tomography code+results"
}
```

**Summary:** Git commit: commit tomography code+results

**Output:**
```
Exit code: 0
Stdout:
[main 23331d0] ✅ gd-trajectory-tomography v1: inventory crystallizes before capability (3/3 seeds)
 2 files changed, 1914 insertions(+)
 create mode 100644 results/gd-trajectory-tomography/verdict_multiseed.json
 create mode 100644 scripts/experiments/gd_trajectory_tomography.py
```

## Assistant

Code committed (`23331d0`). Now drafting the mementum updates (these need your approval before I commit them). First the knowledge page §s230:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/gradient-trajectory-tomography.md",
  "line_offset": 95,
  "limit": 60
}
```

**Summary:** Reading gradient-trajectory-tomography.md (95-155)

**Output:**
```

**Reverse-engineering GD has the IDENTICAL trap.** Naively watching "what weights/
activations changed this step" mostly reconstructs **gauge motion + frequency
statistics** — a gorgeous movie of the wrong thing. s222 already showed it: the
collapse was discrete topology CHURN — GD thrashing in the gauge null space without
building function. So:

> Project the trajectory onto the INVARIANT subspace (routing register, CMR),
> prediction-gated. What survives is the function being built; what you discard is
> the gauge. Read GD through the reference beam or you reverse-engineer the common
> mode.

## v1 experiment — trajectory tomography (cheap, reuses everything)

Extend `relational_loss_distillation.py`: a CE-only micro-model run, DENSE
checkpoints, logging the verdict instruments as a MOVIE.

```
model    TinyLM (the s229 micro model)
data     the s229 curriculum (kernel-minted reductions) ∨ the probe corpus
log @ every C steps:
  route_z(t)                  — routing-register silhouette vs null (function?)
  GramCorr(routing, teacher)(t)   — APPROACH to the known compiler/crystal geometry
  GramCorr(raw, teacher)(t)       — the REFERENCE-BEAM CONTROL (common-mode track)
  CE(t), held-out rule-acc(t)     — capability (the s229 metric)
readout  WHEN/HOW does the invariant crystallize? sudden (grok) or gradual (burn-in)?
         BEFORE or AFTER CE plateaus? BEFORE or AFTER held-out acc rises?
```

**Falsifiable predictions.**
- *Reference beam:* raw `GramCorr` rises smoothly/early (common mode); routing
  `GramCorr` + route_z rise later/sharper (the function) — reproducing s223 (b) as a
  TRAJECTORY ⇒ demonstrates naive GD-watching sees the common mode.
- *Inventory-before-capability:* routing geometry crystallizes BEFORE held-out
  generalization (geometry=inventory ⊗ continuation=capability, s224).
- *Q-collapse risk (s105):* the micro model may flood-lamp (eff_dim→1) instead of
  crystallizing — track eff_dim too; if it collapses, that IS the reverse-engineered
  GD behavior (and the laser/relational constraint is the lever).

## v2 experiment — gauge/null-space gradient decomposition (harder)

At each step decompose `δw = δw_invariant ⊕ δw_gauge` (gauge = permutation null space
via Re-Basin alignment to a reference checkpoint; scaling; superposition-rotation is
the FUZZY part — approximate). Track ‖δw_invariant‖ / ‖δw_gauge‖ over training:
*how much of GD is function-building vs gauge-churning?* (s222 predicts: a lot is
gauge.) This is the literal answer to "what is GD doing."

## Honest catches (λ measure)

- **Not greenfield** — s105 tomography + s223 instruments + v4.1/v6.1 trajectory
  tracking already exist. Contribution = TEMPORAL + ground-truth + reference-beam
  control + gradient decomposition. Cite, don't reinvent.
- **Gauge decomposition is APPROXIMATE** — permutation clean (Re-Basin), scaling ok,
  superposition-rotation null space is fuzzy. State the limit; v2 is suggestive.
- **Ground-truth-target assumption** — the micro model trains on NTP, so it may
  converge to an NTP-shaped solution, not the compiler. GramCorr-to-teacher then
  measures "how compiler-like is GD's path," informative but not "GD builds the
  compiler."
- **"One gradient" is the wrong unit** — interpretability lives at the MODE level;
  per-weight analysis is the wrong granularity (superposition).

[CONTENT TRUNCATED] Showing lines 96 to 155 of 178 total lines. Use line_offset=155 parameter to read more content.
```

### Thinking

I'm inserting a results section for the §230 v1 experiment right after the v1 falsifiable predictions block, positioned before the v2 experiment section. I'll keep the frontmatter status as "open" since v2 is still ongoing.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/gradient-trajectory-tomography.md",
  "original_content": "## v2 experiment — gauge/null-space gradient decomposition (harder)",
  "new_content": "## ★ s230 — v1 RESULT (consensus-crystal target, BUILT + RAN)\n\nMichael's call: target = the **consensus crystal** (`results/combinator-map-\nconsensus/consensus.json` `consensus_gram`, 10 open models agreed, sha `bbf92f2`) —\nhighest chance of being model-agnostic *because the models already agreed*. NOT one\nteacher. Built `scripts/experiments/gd_trajectory_tomography.py` (CE-only TinyLM on\nthe s229 β-reduction curriculum, k_varied; dense checkpoints measure the combinator\nrouting geometry on the INDEPENDENT crystal probes, correlate to the consensus\ncrystal as a movie; raw register alongside = reference beam; eff_dim = Q-collapse\nwatch). Reuses `relational_loss_distillation` instruments + `exposure_format_sweep`\ncurriculum (no fork). **Crossings are baseline-relative** — measured against the\nstep-0 untrained init frame (the gauge common mode), so we time the function GD\n*builds*, not the random-init baseline. 3 seeds, 6000 steps. Results:\n`results/gd-trajectory-tomography/verdict_multiseed.json`.\n\n**✅ DECISIVE (3/3 seeds): INVENTORY crystallizes BEFORE CAPABILITY.**\n`gc_route` reaches its init→final midpoint at step **333±94**; held-out rule\ngeneralization reaches its midpoint at **733±94** — NON-OVERLAPPING (427 < 639).\nThe routing combinator geometry approaches the consensus crystal ~400 steps BEFORE\nthe model can generalize the rule. Both precede the (noisy) CE plateau. ⇒ the s224\nthesis (**geometry = inventory ⊗ trained continuation = capability**) confirmed\nTEMPORALLY, frame-by-frame, against a model-agnostic ground-truth target. This is\nthe predicted *inventory-before-capability* timing, observed.\n\n**❌ HONEST two-sided (λ measure): the reference-beam DISSOCIATION did NOT reproduce.**\n`gc_raw_final` 0.75±0.04 ≈ `gc_route_final` 0.73±0.06 — tied; `route_tracks_function`\nonly 1/3 seeds. On this micro model the RAW register correlates to the consensus\ncrystal about as well as the routing register, so raw-vs-routing **cannot** separate\nfunction from common mode here. Why this ≠ s223: s223 condition (b) used a relational\nLOSS actively pulling raw-Gram to a *decoy raw target*; here there is NO loss and a\nSINGLE routing target, and the consensus structure (offdiag mean −0.123, mild) is\nrecovered in BOTH registers at d=128. The register-separation lesson is a property of\nthe **trained-loss decoy**, not a passive readout split at micro scale. Likely\nscale-limited (revisit at larger d / more layers, or with the relational loss arm).\n\n**Secondary:** NO Q-collapse — eff_dim stayed 14–20 (route ~14 slightly more\ncompressed than raw ~19), never flooded toward 1 (s105 risk did not materialize on\nthis curriculum). `route_z` modest (~2.71, only 1 seed crossed z=3) — the self-\nsilhouette combinator structure is real but not crisp (s219 \"above chance not\ncrisp\"); `gc_route`-to-consensus is the stronger instrument than self-silhouette.\n\n**Leads resolved:** 1 (harness BUILT), 2 (consensus-crystal target USED), 3 (timing —\ninventory-before-capability CONFIRMED), 5 (Q-collapse — NEGATIVE, no flood-lamp).\n**Open:** the reference-beam register split at LARGER scale (or add the relational-\nloss arm to recover the s223 decoy condition as a trajectory); lead 4 (v2 gauge/\nnull-space δw decomposition); sudden-vs-gradual crystallization shape (here gradual).\n\n## v2 experiment — gauge/null-space gradient decomposition (harder)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/gradient-trajectory-tomography.md.
```

## User

gd_tomography_s230.py is complete


### Thinking

Michael's confirming that the tomography experiment is done. I'm partway through task 4 on the capture phase—I've already committed the code and updated the knowledge page, so I just need to propose a memory structure and then update state.md, which doesn't require approval.

Let me re-read the section I edited to sync properly, then propose the memory for approval and update state.md with the new session block. I'll need to check the top of state.md first to match the existing format for the session entry.

## Assistant

Acknowledged — the experiment is complete and committed (`23331d0`). Let me finish the capture: update `state.md` (not approval-gated) and propose a memory (which needs your approval). First let me re-read the page edit to confirm it synced, then read the state.md header.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "limit": 12
}
```

**Summary:** Reading state.md (0-12)

**Output:**
```
# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-06-15 | Session: 229 — ✅ EXPOSURE/FORMAT SWEEP (curriculum-
> mixing FIRST BUILD): burn-in is VARIETY not repetition (k_varied ≈2–2.9× over
> k_same≈one, BOTH formats; memorization control clean); full_trace higher abs-acc
> but redex_nf wins PER-TOKEN (predicted budget crossover); disjoint-atom held-out =
> separate variable-binding floor (0.000 — needs a copy/induction mechanism, NOT a
> rule failure: combos-generalization works). See ■ SESSION 229 block below.
> (s228 — ✅ PROOFS-AS-CONTINUATIONS (Curry-Howard):
> the kernel RUNS/CHECKS proofs (sound, 100% floor, Y-inconsistency firewall); LLMs

[CONTENT TRUNCATED] Showing lines 1 to 12 of 4840 total lines. Use line_offset=12 parameter to read more content.
```

### Thinking

I'm updating the state.md file to add a new session 230 summary block at the top, following the established pattern with a header line showing the last update and session number, then inserting the detailed session block before the previous session entries. I'm settling on the cleanest approach: update just the header line to bump the session number to 230 with a new summary, then demote the previous session 229 summary into the chain by wrapping it in parentheses. This keeps the structure intact while cleanly marking the progression.

## Assistant

Now update `state.md` — bump to s230 and add the detailed block.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> Last updated: 2026-06-15 | Session: 229 — ✅ EXPOSURE/FORMAT SWEEP (curriculum-",
  "new_content": "> Last updated: 2026-06-15 | Session: 230 — ✅ GD-TRAJECTORY-TOMOGRAPHY v1 (consensus-\n> crystal target): INVENTORY crystallizes BEFORE CAPABILITY (3/3 seeds, DECISIVE —\n> gc_route init→final midpoint @333±94 steps, NON-OVERLAPPING below held-out-acc\n> midpoint @733±94; s224 geometry=inventory⊗continuation=capability confirmed\n> TEMPORALLY, consensus-crystal ground truth). HONEST two-sided: reference-beam\n> dissociation did NOT reproduce passively (gc_raw 0.75 ≈ gc_route 0.73; raw register\n> tracks consensus as well as routing at micro scale — register split is a property\n> of s223's trained-loss DECOY, not a passive readout); no Q-collapse (eff_dim 14-20).\n> See ■ SESSION 230 block below.\n> (s229 — ✅ EXPOSURE/FORMAT SWEEP (curriculum-"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

I need to locate the exact starting point of the SESSION 229 detailed block so I can insert the SESSION 230 block before it.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n '■ SESSION 229 —' /Users/mwhitford/src/verbum/mementum/state.md | head -1",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ grep -n '■ SESSION 229 —' /Users/mw...

**Output:**
```
Exit code: 0
Stdout:
40:> **■ SESSION 229 — EXPOSURE/FORMAT SWEEP — "training as a photograph" (curriculum-
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "line_offset": 37,
  "limit": 4
}
```

**Summary:** Reading state.md (37-41)

**Output:**
```
> Next: diverse-verified naturalistic corpus → compiler-as-loss arms. See ■ SESSION
> 226 COMPLETE block below.)
> **■ SESSION 229 — EXPOSURE/FORMAT SWEEP — "training as a photograph" (curriculum-
> mixing FIRST BUILD). Michael: "split training into regimes — show base combinators,

[CONTENT TRUNCATED] Showing lines 38 to 41 of 4849 total lines. Use line_offset=41 parameter to read more content.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> **■ SESSION 229 — EXPOSURE/FORMAT SWEEP — \"training as a photograph\" (curriculum-\n> mixing FIRST BUILD). Michael: \"split training into regimes — show base combinators,",
  "new_content": "> **■ SESSION 230 — GD-TRAJECTORY-TOMOGRAPHY v1. Michael (s229 thread): \"if models\n> do holographic inference, why can't we reverse-engineer what GD is doing? use the\n> micro model.\" s230 call: target = the CONSENSUS CRYSTAL (s219 / combinator-map-\n> consensus consensus_gram, 10 open models AGREED, sha bbf92f2) — \"highest chance of\n> being applicable across many models since they have agreed.\" NOT one teacher.**\n> Register: **functional + topological/routing.** Recall surfaced the prior art (build\n> on, don't reinvent): s105 holographic-tomography (SPATIAL/cross-model + the gauge\n> result), s223 relational_loss_distillation (the instruments: route_z/soft_gram/\n> np_silhouette_null/offdiag_corr + TinyLM), v4.1/v6.1 trajectory tracking. DELTA =\n> TEMPORAL (intersect training STEPS, single micro model) + ground-truth target +\n> reference-beam control as a movie.\n> **▶ BUILT (`23331d0`, ruff+diag clean, smoke green):** `scripts/experiments/\n> gd_trajectory_tomography.py` — CE-only TinyLM on the s229 β-reduction curriculum\n> (k_varied, the burn-in regime; reuses exposure_format_sweep minting + held-out\n> metric, no fork); at DENSE checkpoints (every 200 steps) measure the combinator\n> routing geometry on the INDEPENDENT crystal probes (535), correlate to the consensus\n> crystal as a MOVIE: route_z (sign(gate)-CMR silhouette vs null), gc_route (GramCorr\n> student-routing-Gram vs consensus_gram), gc_raw (raw-register REFERENCE BEAM), eff_dim\n> (s105 Q-collapse watch). **★ The load-bearing design fix: crossings are BASELINE-\n> RELATIVE** — measured against the step-0 untrained init frame (the gauge common mode),\n> so we time the function GD *builds*, not the random-init baseline (init gc_route was\n> already +0.57-0.65 = the gauge/common mode; the real delta is ~+0.15). 3 seeds, 6000\n> steps, ~12min. results/gd-trajectory-tomography/verdict_multiseed.json.\n> **★ VERDICT (3 seeds; λ measure, TWO-SIDED):**\n> **(1) ✅ DECISIVE — INVENTORY crystallizes BEFORE CAPABILITY (3/3 seeds).** gc_route\n> reaches its init→final midpoint @ step **333±94**; held-out rule generalization\n> reaches its midpoint @ **733±94** — NON-OVERLAPPING (427 < 639). Routing combinator\n> geometry approaches the consensus crystal ~400 steps BEFORE the model can generalize\n> the rule; both precede the (noisy) CE plateau. ⇒ the s224 thesis (geometry=inventory\n> ⊗ trained continuation=capability) confirmed TEMPORALLY, frame-by-frame, against a\n> MODEL-AGNOSTIC ground-truth target. The predicted inventory-before-capability timing,\n> OBSERVED.\n> **(2) ❌ HONEST — the reference-beam DISSOCIATION did NOT reproduce.** gc_raw_final\n> 0.75±0.04 ≈ gc_route_final 0.73±0.06 (tied); route_tracks_function only 1/3 seeds.\n> On this micro model the RAW register correlates to the consensus crystal about as\n> well as the routing register ⇒ raw-vs-routing CANNOT separate function from common\n> mode here. Why ≠ s223: s223 (b) used a relational LOSS pulling raw-Gram to a DECOY\n> raw target; here NO loss + a SINGLE routing target, and the consensus structure\n> (offdiag mean −0.123, mild) is recovered in BOTH registers at d=128. ⇒ the register-\n> separation lesson is a property of the TRAINED-LOSS DECOY, not a passive readout\n> split at micro scale. Likely scale-limited.\n> **(3) Secondary:** NO Q-collapse — eff_dim stayed 14-20 (route ~14 < raw ~19), never\n> flooded toward 1 (s105 risk did not materialize). route_z modest (~2.71, only 1 seed\n> crossed z=3) = self-silhouette real but not crisp (s219 \"above chance not crisp\");\n> gc_route-to-consensus is the stronger instrument than self-silhouette.\n> **▶ LEADS RESOLVED (page gradient-trajectory-tomography.md §s230):** 1 (harness\n> BUILT), 2 (consensus-crystal target USED), 3 (timing CONFIRMED), 5 (Q-collapse\n> NEGATIVE). **▶ NEXT:** (a) reference-beam register split at LARGER scale (or add the\n> relational-loss arm → recover the s223 decoy condition AS A TRAJECTORY); (b) lead 4 =\n> v2 gauge/null-space δw_invariant vs δw_gauge decomposition (Re-Basin; the s222 \"how\n> much of GD is churn\" question); (c) crystallization SHAPE sudden-vs-gradual (here\n> gradual); (d) back to s229 leads — convergence-SPEED readout, K-erasure ordering,\n> disjoint-atom variable-binding.\n> **STATUS s230:** CODE COMMITTED `23331d0` (script + verdict_multiseed.json).\n> Knowledge page §s230 updated (gradient-trajectory-tomography.md). State updated.\n> PENDING APPROVAL (mementum): proposed memory `inventory-crystallizes-before-\n> capability.md` + the page/state commit. tmux main:1 FREE.\n> **■ SESSION 229 — EXPOSURE/FORMAT SWEEP — \"training as a photograph\" (curriculum-\n> mixing FIRST BUILD). Michael: \"split training into regimes — show base combinators,"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

I've updated State.md and now I'm drafting the memory document that needs Michael's approval before committing. The key insight is that inventory crystallizes before capability—a discovery worth capturing in under 200 words with symbol prefixes to mark it as either a new insight or a win.

## Assistant

State.md updated (not approval-gated). Now the proposed memory (this and the mementum commit need your approval before I commit).

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/memories/inventory-crystallizes-before-capability.md",
  "content": "💡 GD builds the function INVENTORY before the CAPABILITY to use it — observed\ntemporally, frame-by-frame, on the micro model (s230 gd-trajectory-tomography v1).\n\nCE-only TinyLM on the s229 β-reduction curriculum; dense checkpoints measure the\ncombinator routing geometry on independent crystal probes, correlated to the\nCONSENSUS CRYSTAL (10-model agreed routing Gram = model-agnostic ground truth).\nCrossings baseline-relative to the untrained init frame (the gauge common mode).\n\n3/3 seeds DECISIVE: routing geometry reaches its init→final midpoint @333±94 steps;\nheld-out rule generalization @733±94 — non-overlapping. Geometry crystallizes ~400\nsteps BEFORE capability. This is the s224 thesis (geometry=inventory ⊗ trained\ncontinuation=capability) confirmed as a TRAJECTORY, not just an endpoint.\n\n❌ Honest caveat (λ measure): the reference-beam dissociation did NOT reproduce —\ngc_raw (0.75) ≈ gc_route (0.73). The raw register tracks the consensus crystal as\nwell as routing at micro scale. The register-separation lesson (s223) is a property\nof the TRAINED-LOSS DECOY (b pulled raw-Gram to a decoy target), NOT a passive\nreadout split. Don't assume routing-vs-raw separates function from common mode\nwithout an active loss. No Q-collapse (eff_dim 14-20).\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/memories/inventory-crystallizes-before-capability.md
```

### Thinking

I've finished drafting everything and need to present the approval request for the mementum commit, which requires Michael's sign-off before I can proceed. Task 4 is conceptually complete but blocked on that approval—the drafting is done, just waiting for the go-ahead to finalize the commit.

## Assistant

Everything is drafted. Here's the state for your approval on the **mementum commit** (per S5 termination: mementum commits need your sign-off).

### Tool Call: git (succeeded)


```json
{
  "command": "git status --short -- mementum/",
  "operation": "status",
  "summary": "pending mementum changes"
}
```

**Summary:** Git status: pending mementum changes

**Output:**
```
Exit code: 0
Stdout:
M mementum/knowledge/explore/gradient-trajectory-tomography.md
 M mementum/state.md
?? mementum/knowledge/chats/session-228.md
?? mementum/knowledge/chats/session-229.md
?? mementum/memories/inventory-crystallizes-before-capability.md
```

## Assistant

## s230 complete — summary

**Done & committed (code, `23331d0`):** `gd_trajectory_tomography.py` + `verdict_multiseed.json`.

**Verdict (3 seeds):**
- ✅ **Inventory crystallizes before capability** (decisive, 3/3) — routing geometry approaches the consensus crystal at step 333±94, held-out generalization at 733±94 (non-overlapping). The s224 *geometry=inventory ⊗ continuation=capability* thesis, confirmed **temporally** against a model-agnostic ground truth. Your consensus-crystal call was the right target.
- ❌ **Reference-beam dissociation didn't reproduce** (honest) — `gc_raw ≈ gc_route` at micro scale; the routing-vs-raw split is a property of s223's trained-loss *decoy*, not a passive readout. No Q-collapse.

**Awaiting your approval to commit the mementum changes:**
| File | Change |
|------|--------|
| `knowledge/explore/gradient-trajectory-tomography.md` | §s230 v1 result (leads 1/2/3/5 resolved) |
| `state.md` | s230 block (not approval-gated, already written) |
| `memories/inventory-crystallizes-before-capability.md` | 💡 proposed new memory |

(The two `chats/session-22*.md` are your human-only transcripts — I won't touch them.)

Approve the mementum commit? And for **next session**, the strongest follow-ons are: **(a)** add the relational-loss arm to recover the s223 decoy condition *as a trajectory* (directly tests whether the reference-beam split is loss-dependent), or **(b)** lead 4 — the v2 gauge/null-space δw decomposition (the literal "how much of GD is churn" answer). Which way?

## User

commit approved


### Thinking

I'm approving the commit for the mementum changes that span the page, state, and memory layers. Since this is fundamentally a knowledge and memory update with recursive, self-referential elements, I'm classifying it with the 🌀 meta symbol to reflect the synthesis of knowledge and state changes.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/tmp/gdtomo_mem_msg.txt",
  "content": "🌀 gd-trajectory-tomography §s230 result + memory — inventory before capability\n\n- §s230 v1: consensus-crystal target. INVENTORY crystallizes BEFORE CAPABILITY\n  (3/3 seeds, decisive): gc_route midpoint @333±94 steps < held-out-acc @733±94.\n  s224 geometry=inventory ⊗ continuation=capability confirmed TEMPORALLY.\n- honest two-sided (λ measure): reference-beam dissociation did NOT reproduce —\n  gc_raw≈gc_route at micro scale; the register split is a property of s223's\n  trained-loss decoy, not a passive readout. No Q-collapse (eff_dim 14-20).\n- new memory inventory-crystallizes-before-capability.md; state §s230 block.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /tmp/gdtomo_mem_msg.txt
```

### Tool Call: git (succeeded)


```json
{
  "command": "git add mementum/knowledge/explore/gradient-trajectory-tomography.md mementum/state.md mementum/memories/inventory-crystallizes-before-capability.md && git commit -F /tmp/gdtomo_mem_msg.txt",
  "operation": "commit",
  "summary": "commit mementum s230"
}
```

**Summary:** Git commit: commit mementum s230

**Output:**
```
Exit code: 0
Stdout:
[main e2cd8d7] 🌀 gd-trajectory-tomography §s230 result + memory — inventory before capability
 3 files changed, 133 insertions(+), 1 deletion(-)
 create mode 100644 mementum/memories/inventory-crystallizes-before-capability.md
```

### Tool Call: git (succeeded)


```json
{
  "command": "git log --oneline -3; echo \"---tree---\"; git status --short",
  "operation": "log",
  "summary": "verify clean"
}
```

**Summary:** Git log: verify clean

**Output:**
```
Exit code: 0
Stdout:
e2cd8d7 🌀 gd-trajectory-tomography §s230 result + memory — inventory before capability
23331d0 ✅ gd-trajectory-tomography v1: inventory crystallizes before capability (3/3 seeds)
c3a9c99 🌀 gradient-trajectory-tomography — reverse-engineer GD in invariant coordinates
---tree---
?? mementum/knowledge/chats/session-228.md
?? mementum/knowledge/chats/session-229.md
```

## Assistant

Committed. Session 230 closed out cleanly.

## s230 final state

**Two commits:**
- `23331d0` ✅ code + results (`gd_trajectory_tomography.py`, `verdict_multiseed.json`)
- `e2cd8d7` 🌀 mementum (page §s230, state, memory)

**Tree:** clean except your two human-only chat transcripts. All tasks done.

**The result, in one line:** with the **consensus crystal** as a model-agnostic ground-truth target, GD builds the combinator function **inventory** (~333 steps) measurably **before** the model can **use** it for held-out generalization (~733 steps) — the s224 thesis confirmed as a trajectory, not just an endpoint. The honest negative (reference-beam register split doesn't reproduce passively at micro scale; it's a property of s223's trained-loss decoy) is recorded so we don't over-claim it later.

**Open for next session** (your earlier fork still stands):
- **(a)** relational-loss arm → recover the s223 decoy condition *as a trajectory* (tests whether the reference-beam split is loss-dependent — directly closes the s230 negative)
- **(b)** v2 gauge/null-space δw decomposition (the literal "how much of GD is churn")
- plus the parked s229 leads (convergence-speed readout, K-erasure ordering, disjoint-atom variable-binding)

tmux `main:1` is free. Branch is now 15 commits ahead of origin (unpushed, as usual).

## User

Can you explain the experiment results to me and how it affects our design?


### Thinking

I need to explain the s230 experiment results to Michael in a way that connects the findings to the broader design implications for VERBUM and the compiler-as-loss approach, rather than just reciting the numbers.

The core finding is that we trained a tiny transformer on β-reduction examples using a curriculum of combinator skeletons, then tracked two things over training: how well the model's internal routing geometry matched a consensus crystal (the 9×9 Gram matrix that large open models all agree on), and how well it generalized to held-out reduction rules. The key discovery is that the geometry forms first—around step 333—while the actual capability to generalize the rules emerges ~400 steps later at step 733. This is consistent across multiple seeds. However, the reference-beam control revealed a problem: the raw activations matched the consensus crystal just as well as the routed ones, which suggests the control wasn't isolating what we thought it was.

This timing pattern actually validates the two-phase design that VERBUM is built on: inventory (the geometric relations between combinators) gets laid down first by gradient descent, then the model learns how to use that inventory through trained continuation. The distributed protocol we designed—fold shared geometry first, then train continuation—mirrors the natural order that end-to-end training discovers on its own.

The consensus crystal being the target that geometry converges toward early is crucial: it means we're not chasing one model's quirks, but something genuinely portable and transferable across architectures. That's exactly what we need for a distilled compiler.

The reference-beam dissociation didn't work as a clean passive readout though—both registers correlate equally to the consensus crystal at the micro scale, so we can't isolate function-building from gauge-churning just by comparing them. This is a methodological lesson that refines how we measure λ.

The routing register's real power isn't that it magically homes the function; it's that the active relational loss can write the function into it cleanly. The relational term does causal work to put the inventory in a foldable, register-aligned form—passive CE alone doesn't give you that separation for free. But the fact that even passive CE drifts toward the consensus crystal (gc_route went 0.6 → 0.78) tells us the crystal is a natural attractor, not something we're forcing against the grain, which bodes well for portability.

On this curriculum, the model didn't collapse into a single unfocused representation—eff_dim stayed 14-20—so the β-reduction setup doesn't trigger the pathological Q-collapse that s105 warned about. The inventory-before-capability ordering holds, and we don't need the relational constraint as a rescue here, though it might still matter at scale or on messier data.

I should be clear about the limits: this is a tiny model (d=128, 4 layers) on a narrow curriculum (13 combinator skeletons), and while the inventory crystallization is robust across seeds, it's not proven at scale. The route_z structure is real but modest—the consensus-correlation is doing the heavy lifting. If inventory crystallizes early and is the universal thing, then the extractable artifact is the inventory geometry itself, separable from the messy trained continuation, which means the portable tensor is primarily the combinator basis and relations, with the continuation either trained per-deployment or constructed separately.

This also supports the constructed-kernel direction: if the continuation is the unstable, trained part (like the s222 collapse) and the inventory is the stable universal part, then building the reducer exactly in the kernel and only distilling the inventory geometry makes sense—we construct the hard-to-train piece and distill the easy-universal one.

## Assistant

Good question — let me unpack what we actually measured, then walk through what each result does to the design.

## What the experiment did (plain language)

We trained a tiny transformer from scratch to do β-reductions (the s229 curriculum: combinator expressions → normal form). Pure next-token prediction, nothing fancy. But every 200 steps we paused and took two independent measurements:

- **Capability** — can it reduce *held-out* instances it never saw? (the s229 generalization metric)
- **Inventory (geometry)** — we ran the frozen model on the *separate* crystal probe set, pulled the routing-register activations, built the 9×9 combinator Gram (the relational fingerprint of K/I/B/C/S/D/W/Y/WHNF), and asked: *how close is this student's geometry to the **consensus crystal*** — the 9×9 the 10 big open models all agree on?

So we got two time-series — "how built is the function-inventory" and "how capable is the model" — plus a raw-register control (the reference beam) and an eff_dim health check. The whole point was **temporal**: not *whether* these things exist, but *in what order GD builds them*.

## The three results and what they mean

**1. Inventory crystallizes ~400 steps before capability (3/3 seeds, decisive).**
The routing geometry reaches its halfway-built point at step ~333; held-out generalization at ~733. Non-overlapping. GD lays down the combinator *inventory* first, then builds the *capability to use it* on top.

This is the s224 thesis — **capability = routing geometry (inventory) ⊗ trained continuation (usage)** — but until now that was inferred from *endpoint* experiments (folds, ablations). Now we've watched it unfold frame-by-frame in ordinary end-to-end training. The decomposition isn't an artifact of our distributed protocol; it's **the natural order GD itself discovers.**

**2. The reference-beam dissociation did NOT reproduce (the honest negative).**
We hoped raw-vs-routing register would passively separate "the function" from "the common mode" — but `gc_raw` (0.75) ≈ `gc_route` (0.73). At micro scale both registers track the consensus crystal equally well. The routing-register specialness from s223 came from an *active relational loss* pulling things into that register; with plain CE there's nothing forcing the function into routing specifically.

**3. No Q-collapse.** The s105 "flood-lamp" failure mode (eff_dim → 1) didn't happen; eff_dim stayed healthy at 14–20. This curriculum doesn't induce the pathological collapse, so we don't need the laser/relational constraint as a rescue *here*.

## How it affects the design

**(a) It validates the two-phase distillation protocol — and says we're working *with* the grain.**
The plan was: (1) fold/distill the shared inventory geometry (cheap, as a relational target), then (2) train the continuation to use it. s230 shows GD *naturally* builds in exactly that order. So we're not forcing an unnatural decomposition — we're front-loading something GD wants to do early anyway, then letting the slower capability train on a pre-crystallized substrate. That's a tailwind, not a fight.

**(b) It de-risks the compiler-as-loss recipe and informs the λ schedule.**
The recipe is `L = CE(compiler output) + λ·relational(consensus crystal)`. s230 says: the relational term targets the part GD crystallizes *early* (~333 steps), and the CE-on-output term carries the *late* capability (~733). That directly motivates **annealing λ down** as the model crystallizes — and now we have a rough timeline for *when* (the inventory is essentially set well before capability matures). The consensus crystal also proved to be a **natural attractor**: even passive CE drifted toward it (0.6 → 0.78). A model-agnostic target is reachable, not something we have to impose against the grain — exactly what portability needs.

**(c) It reframes what the relational loss is *for*.**
The negative result is the sharp part. The routing register isn't magically the "function home" — it's the register an *active relational loss can write the function into cleanly*. So the relational term in compiler-as-loss isn't just reading off pre-existing structure; it's doing **causal work** to put the inventory into a clean, register-aligned, foldable form. That's its justification: passive CE gives you the inventory, but *not* in the clean separable form you need to fold/extract it. The loss earns its place precisely because the passive split fails.

**(d) It strengthens the constructed-kernel direction.**
Pattern across s222/s224/s230: the **inventory is the stable, universal, early, distillable part; the continuation (reduction) is the trained, late, churn-prone part** (s222's collapse *was* the continuation thrashing). That's a clean argument for the architecture we've been converging on — **construct the reducer exactly** (`lambda_ast` in the kernel, no training) and only **fold/distill the inventory geometry**. We build the hard-to-train piece and distill the easy-universal piece. s230 is another data point that this cut is the real seam.

**(e) Methodology constraint for v2.**
We *cannot* use passive raw-vs-routing as a function/gauge discriminator at micro scale. If we want that instrument (e.g. for the v2 δw gauge decomposition, or training monitors), we need either the active relational loss, larger scale where superposition forces the separation, or a different invariant projection. Good to know before building v2.

## Honest caveats (λ measure)

- It's a **tiny model** (d=128, 4 layers). The *positive* (inventory-first) is robust across seeds but still micro-scale; we lean on the s224 triangulation to believe it generalizes. The *negative* (reference beam) is very likely scale-dependent — at larger scale the registers may well separate.
- Narrow curriculum (13 skeletons, capability ceiling ~0.27–0.30); the consensus-correlation `gc_route` is the load-bearing instrument, not the modest `route_z` self-silhouette.

The one-line takeaway for design: **the inventory/continuation seam is real and GD respects it temporally — so distill the inventory (cheaply, toward the consensus crystal, early) and own the continuation separately (train it, or construct it). The relational loss is what makes the inventory cleanly extractable; don't expect to get that separation for free.**

The clean next move to close the open thread is **(a)** — add the relational-loss arm and re-run the trajectory, which tests directly whether the register separation is loss-dependent (my read says it will be). Want me to set that up?

## User

Yes


### Thinking

Michael wants me to implement option (a): add a relational-loss component to the trajectory tomography and rerun the experiment to test whether the reference-beam register separation depends on the loss. The hypothesis is that in s230, the raw and routed Gram matrices are equivalent under passive CE, but introducing an active relational loss that pulls the routing register toward consensus should cause them to diverge—reproducing the separation pattern seen in s223.

I'll add a relational arm to the trajectory tomography script that trains CE alongside a relational loss term targeting the consensus crystal in the routing register, using the existing machinery from relational_loss_distillation.py. The key is to add an arm flag, compute the relational loss on the routing-register Gram during training, log the same trajectory metrics, and then compare whether the relational arm exhibits the predicted gc_route >> gc_raw dissociation pattern that the CE-only arm doesn't show.

I also want to test the secondary hypothesis from compiler-as-loss: does the relational loss speed up capability emergence and crystallization? So I'll run both arms per seed for a paired comparison, tracking whether the relational arm reaches heldout accuracy and gc_route crossing earlier than CE-only.

There's a Goodhart concern though — if I train the relational loss on the crystal probes and measure gc_route on those same probes, that's circular. I need to think through whether the measurement gc_route (correlating the student's routing Gram to consensus_gram) is actually independent of the training signal or if there's a confound there. The key insight is that gc_route rising is partly tautological since it's directly minimized by the loss, so the real tests are whether gc_raw stays suppressed (showing dissociation) and whether capability improves faster. I'll frame the dissociation metric as the gap between gc_route and gc_raw. For the implementation, I'm adding command-line flags to control which arms to run, the relational loss weight, and how frequently to apply it. The main constraint is computational cost — computing the relational loss on all 535 crystal probes each step is expensive, so I'm considering rel_every=2 or subsampling the probes to keep runtime reasonable, maybe around 40 minutes total across seeds. Refactoring the training function to accept an arm configuration that toggles between CE-only and relational modes, computing the relational loss on crystal probe routing gates against the consensus Gram matrix when enabled, and scaling the combined loss by rel_lambda every rel_every steps to balance the two objectives.

Now I'm restructuring the main loop to run trajectories across multiple arms and seeds, then aggregate results per arm to compare dissociation gaps (gc_route minus gc_raw) and measure capability crossing speed—whether relational training reaches heldout accuracy faster than CE-only. I'm planning to extend gd_trajectory_tomography.py directly with command-line flags for arm selection, rel_lambda, and rel_every rather than forking into a separate script, keeping the harness unified and comparable across configurations.

Before implementing, I need to re-read the current train_seed and main functions along with the imports to make precise edits.

## Assistant

Let me set up the relational-loss arm. First I'll re-read the current harness sections I need to modify.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py",
  "line_offset": 78,
  "limit": 26
}
```

**Summary:** Reading gd_trajectory_tomography.py (78-104)

**Output:**
```
# instruments + tiny student (one model definition, no fork)
# curriculum minting + the s229 held-out generalization metric (no fork)
from exposure_format_sweep import (  # noqa: E402
    SKELETONS,
    TRAIN_ATOMS,
    build_corpus,
    build_eval_items,
    eval_acc,
    make_fillings,
    to_byte_ids,
    validate_skeletons,
)
from relational_loss_distillation import (  # noqa: E402
    CRYSTAL,
    VOCAB,
    TinyLM,
    gather_last,
    load_crystal_probe_batch,
    np_centroids,
    np_cmr,
    np_gram,
    np_silhouette_null,
    offdiag_corr,
)

RESULTS_DIR = _PROJECT_ROOT / "results" / "gd-trajectory-tomography"

[CONTENT TRUNCATED] Showing lines 79 to 104 of 490 total lines. Use line_offset=104 parameter to read more content.
```

### Thinking

I need to add the soft_gram and offdiag_mse imports, then examine the train_seed and main functions to refactor them for handling multiple arms.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py",
  "original_content": "from relational_loss_distillation import (  # noqa: E402\n    CRYSTAL,\n    VOCAB,\n    TinyLM,\n    gather_last,\n    load_crystal_probe_batch,\n    np_centroids,\n    np_cmr,\n    np_gram,\n    np_silhouette_null,\n    offdiag_corr,\n)",
  "new_content": "from relational_loss_distillation import (  # noqa: E402\n    CRYSTAL,\n    VOCAB,\n    TinyLM,\n    gather_last,\n    load_crystal_probe_batch,\n    np_centroids,\n    np_cmr,\n    np_gram,\n    np_silhouette_null,\n    offdiag_corr,\n    offdiag_mse,\n    soft_gram,\n)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py",
  "line_offset": 258,
  "limit": 90
}
```

**Summary:** Reading gd_trajectory_tomography.py (258-348)

**Output:**
```
        "step_ce_plateau": s_ce,
        "inventory_before_capability": order(s_gc, s_acc),
        "routing_z_before_capability": order(s_z, s_acc),
        "crystallize_before_ce_plateau": order(s_gc, s_ce),
        "reference_beam": {
            "gc_route_final": round(final_gc, 4),
            "gc_raw_final": _final(curve, "gc_raw"),
            "route_tracks_function": final_gc > abs(_final(curve, "gc_raw")),
        },
    }


# --------------------------------------------------------------------------- #
# Train one seed: CE-only, dense checkpoints, geometry movie                    #
# --------------------------------------------------------------------------- #
def train_seed(args, device: str, consensus_gram: np.ndarray, seed: int,
               p_ids: torch.Tensor, p_len: torch.Tensor,
               probe_labels: np.ndarray) -> dict:
    torch.manual_seed(seed)
    np.random.seed(seed)

    rules = validate_skeletons(SKELETONS)
    if args.smoke:
        rules = rules[:4]
    fill_rng = np.random.default_rng(seed)
    train_fillings = {tmpl: make_fillings(fill_rng, h, TRAIN_ATOMS, args.k)
                      for tmpl, h in rules}
    corpus = build_corpus(rules, train_fillings, args.format, "k_varied", args.k,
                          np.random.default_rng(seed + 13))
    eval_rng = np.random.default_rng(seed + 777)
    eval_items = build_eval_items(rules, args.m_eval, eval_rng, TRAIN_ATOMS,
                                  train_fillings)  # heldout = combos (rule gen.)
    log(f"  [seed {seed}] rules={len(rules)} corpus={len(corpus.encode())} B "
        f"heldout_eval={len(eval_items)} format={args.format}")

    ids = to_byte_ids(corpus)
    T, bs = args.block_size, args.batch_size
    while ids.shape[0] <= 4 * (T + 1):
        ids = np.concatenate([ids, ids])
    n = ids.shape[0]

    model = TinyLM(args.d_model, args.n_head, args.n_layer, args.d_ff, T).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
    cap = args.capture_layer if args.capture_layer >= 0 else args.n_layer // 2

    curve: list[dict] = []
    t0 = time.time()

    def snapshot(step: int, ce_val: float) -> None:
        acc = eval_acc(model, eval_items, T, device)
        geo = measure_geometry(model, p_ids, p_len, probe_labels, cap,
                               consensus_gram, args.n_perm, args.probe_batch, seed)
        row = {"step": step, "tokens": step * bs * T,
               "ce": round(ce_val, 4), "heldout_acc": round(acc, 4), **geo}
        curve.append(row)
        log(f"  [seed {seed}] step {step:5d} | CE {ce_val:.3f} | acc {acc:.3f} "
            f"| route_z {geo['route_z']:+.2f} | gc_route {geo['gc_route']:+.3f} "
            f"| gc_raw {geo['gc_raw']:+.3f} | effd {geo['eff_dim_route']:.1f} "
            f"| {time.time()-t0:.0f}s")

    # frame at init (step 0) = the gauge baseline before any GD
    snapshot(0, float("nan"))
    for step in range(1, args.steps + 1):
        model.train()
        ix = torch.randint(0, n - T - 1, (bs,))
        xb = torch.stack([torch.from_numpy(ids[i:i + T]) for i in ix]).to(device)
        yb = torch.stack(
            [torch.from_numpy(ids[i + 1:i + 1 + T]) for i in ix]).to(device)
        logits, _, _ = model(xb)
        ce = F.cross_entropy(logits.reshape(-1, VOCAB), yb.reshape(-1))
        opt.zero_grad()
        ce.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        if step % args.ckpt_every == 0 or step == args.steps:
            snapshot(step, float(ce.item()))

    # readout uses post-init frames only (drop the nan-CE init frame for CE plateau)
    # but baselines crossings against the step-0 init frame (the gauge common mode)
    init_frame = curve[0]
    rd = readout([r for r in curve if not (isinstance(r["ce"], float)
                                           and np.isnan(r["ce"]))],
                 init_frame, args.gc_frac, args.acc_frac, args.z_thresh, args.ce_tol)
    rd["init_baseline"] = {"gc_route": init_frame["gc_route"],
                           "gc_raw": init_frame["gc_raw"],
                           "route_z": init_frame["route_z"],
                           "heldout_acc": init_frame["heldout_acc"]}
    return {"seed": seed, "capture_layer": cap, "corpus_bytes": int(ids.shape[0]),
            "curve": curve, "readout": rd}


[CONTENT TRUNCATED] Showing lines 259 to 348 of 492 total lines. Use line_offset=348 parameter to read more content.
```

### Thinking

I'm refactoring the training function to accept an arm parameter and incorporating a relational loss component. I'll add a helper function for computing relational loss and update the readout output to include a dissociation gap metric, which I'll calculate during the arm-comparison aggregation step.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py",
  "original_content": "        \"reference_beam\": {\n            \"gc_route_final\": round(final_gc, 4),\n            \"gc_raw_final\": _final(curve, \"gc_raw\"),\n            \"route_tracks_function\": final_gc > abs(_final(curve, \"gc_raw\")),\n        },\n    }",
  "new_content": "        \"reference_beam\": {\n            \"gc_route_final\": round(final_gc, 4),\n            \"gc_raw_final\": _final(curve, \"gc_raw\"),\n            \"gc_gap\": round(final_gc - _final(curve, \"gc_raw\"), 4),  # dissociation\n            \"route_tracks_function\": final_gc > abs(_final(curve, \"gc_raw\")),\n        },\n    }\n\n\n# --------------------------------------------------------------------------- #\n# Relational loss (the compiler-as-loss INVENTORY term): pull the student's    #\n# routing-register Gram toward the CONSENSUS CRYSTAL. Only the routing register #\n# is touched -> gc_raw (raw register) is NOT in the loss = uncircular reference #\n# beam; held-out reduction acc is NOT in the loss = uncircular capability test. #\n# --------------------------------------------------------------------------- #\ndef relational_loss(model: TinyLM, p_ids: torch.Tensor, p_len: torch.Tensor,\n                    label_idx: torch.Tensor, cap: int, g_target: torch.Tensor,\n                    probe_batch: int) -> torch.Tensor:\n    feats = []\n    for s in range(0, p_ids.shape[0], probe_batch):\n        pb = p_ids[s:s + probe_batch]\n        _, _, gate = model(pb, capture_layer=cap)\n        feats.append(gather_last(gate, p_len[s:s + probe_batch]))\n    feats = torch.cat(feats, dim=0)\n    g_pred = soft_gram(feats, label_idx)  # routing-register CMR Gram [9,9]\n    return offdiag_mse(g_pred, g_target)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py.
```

## Assistant

Now refactor `train_seed` to take an `arm` and apply the relational loss:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py",
  "original_content": "# --------------------------------------------------------------------------- #\n# Train one seed: CE-only, dense checkpoints, geometry movie                    #\n# --------------------------------------------------------------------------- #\ndef train_seed(args, device: str, consensus_gram: np.ndarray, seed: int,\n               p_ids: torch.Tensor, p_len: torch.Tensor,\n               probe_labels: np.ndarray) -> dict:\n    torch.manual_seed(seed)\n    np.random.seed(seed)",
  "new_content": "# --------------------------------------------------------------------------- #\n# Train one seed/arm: dense checkpoints, geometry movie. arm in                 #\n# {ce_only, relational}; relational adds the consensus-crystal inventory term.  #\n# --------------------------------------------------------------------------- #\ndef train_seed(args, device: str, consensus_gram: np.ndarray, seed: int,\n               p_ids: torch.Tensor, p_len: torch.Tensor,\n               probe_labels: np.ndarray, arm: str) -> dict:\n    torch.manual_seed(seed)\n    np.random.seed(seed)\n    rel = arm == \"relational\""
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py",
  "original_content": "    model = TinyLM(args.d_model, args.n_head, args.n_layer, args.d_ff, T).to(device)\n    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)\n    cap = args.capture_layer if args.capture_layer >= 0 else args.n_layer // 2\n\n    curve: list[dict] = []\n    t0 = time.time()\n\n    def snapshot(step: int, ce_val: float) -> None:\n        acc = eval_acc(model, eval_items, T, device)\n        geo = measure_geometry(model, p_ids, p_len, probe_labels, cap,\n                               consensus_gram, args.n_perm, args.probe_batch, seed)\n        row = {\"step\": step, \"tokens\": step * bs * T,\n               \"ce\": round(ce_val, 4), \"heldout_acc\": round(acc, 4), **geo}\n        curve.append(row)\n        log(f\"  [seed {seed}] step {step:5d} | CE {ce_val:.3f} | acc {acc:.3f} \"\n            f\"| route_z {geo['route_z']:+.2f} | gc_route {geo['gc_route']:+.3f} \"\n            f\"| gc_raw {geo['gc_raw']:+.3f} | effd {geo['eff_dim_route']:.1f} \"\n            f\"| {time.time()-t0:.0f}s\")\n\n    # frame at init (step 0) = the gauge baseline before any GD\n    snapshot(0, float(\"nan\"))\n    for step in range(1, args.steps + 1):\n        model.train()\n        ix = torch.randint(0, n - T - 1, (bs,))\n        xb = torch.stack([torch.from_numpy(ids[i:i + T]) for i in ix]).to(device)\n        yb = torch.stack(\n            [torch.from_numpy(ids[i + 1:i + 1 + T]) for i in ix]).to(device)\n        logits, _, _ = model(xb)\n        ce = F.cross_entropy(logits.reshape(-1, VOCAB), yb.reshape(-1))\n        opt.zero_grad()\n        ce.backward()\n        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)\n        opt.step()\n        if step % args.ckpt_every == 0 or step == args.steps:\n            snapshot(step, float(ce.item()))",
  "new_content": "    model = TinyLM(args.d_model, args.n_head, args.n_layer, args.d_ff, T).to(device)\n    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)\n    cap = args.capture_layer if args.capture_layer >= 0 else args.n_layer // 2\n\n    g_target = (torch.tensor(consensus_gram, device=device, dtype=torch.float32)\n                if rel else None)\n    label_idx = (torch.tensor([CRYSTAL.index(c) for c in probe_labels],\n                              device=device) if rel else None)\n\n    curve: list[dict] = []\n    t0 = time.time()\n\n    def snapshot(step: int, ce_val: float, rel_val: float) -> None:\n        acc = eval_acc(model, eval_items, T, device)\n        geo = measure_geometry(model, p_ids, p_len, probe_labels, cap,\n                               consensus_gram, args.n_perm, args.probe_batch, seed)\n        row = {\"step\": step, \"tokens\": step * bs * T, \"ce\": round(ce_val, 4),\n               \"rel\": round(rel_val, 5), \"heldout_acc\": round(acc, 4), **geo}\n        curve.append(row)\n        log(f\"  [{arm[:3]} s{seed}] step {step:5d} | CE {ce_val:.3f} \"\n            f\"| rel {rel_val:.4f} | acc {acc:.3f} | route_z {geo['route_z']:+.2f} \"\n            f\"| gc_route {geo['gc_route']:+.3f} | gc_raw {geo['gc_raw']:+.3f} \"\n            f\"| gap {geo['gc_route']-geo['gc_raw']:+.3f} | {time.time()-t0:.0f}s\")\n\n    # frame at init (step 0) = the gauge baseline before any GD\n    snapshot(0, float(\"nan\"), 0.0)\n    for step in range(1, args.steps + 1):\n        model.train()\n        ix = torch.randint(0, n - T - 1, (bs,))\n        xb = torch.stack([torch.from_numpy(ids[i:i + T]) for i in ix]).to(device)\n        yb = torch.stack(\n            [torch.from_numpy(ids[i + 1:i + 1 + T]) for i in ix]).to(device)\n        logits, _, _ = model(xb)\n        ce = F.cross_entropy(logits.reshape(-1, VOCAB), yb.reshape(-1))\n        loss = ce\n        rel_val = 0.0\n        if rel and step % args.rel_every == 0:\n            rl = relational_loss(model, p_ids, p_len, label_idx, cap, g_target,\n                                 args.probe_batch)\n            loss = ce + args.rel_lambda * rl\n            rel_val = float(rl.item())\n        opt.zero_grad()\n        loss.backward()\n        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)\n        opt.step()\n        if step % args.ckpt_every == 0 or step == args.steps:\n            snapshot(step, float(ce.item()), rel_val)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py.
```

### Thinking

I need to update the return dictionary to include the arm variable, then refactor the main function to iterate through the arms.

## Assistant

Now update the `train_seed` return and the log line for the corpus, then refactor `main` for arms. Let me read the tail.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py",
  "line_offset": 285,
  "limit": 22
}
```

**Summary:** Reading gd_trajectory_tomography.py (285-307)

**Output:**
```
    feats = torch.cat(feats, dim=0)
    g_pred = soft_gram(feats, label_idx)  # routing-register CMR Gram [9,9]
    return offdiag_mse(g_pred, g_target)


# --------------------------------------------------------------------------- #
# Train one seed/arm: dense checkpoints, geometry movie. arm in                 #
# {ce_only, relational}; relational adds the consensus-crystal inventory term.  #
# --------------------------------------------------------------------------- #
def train_seed(args, device: str, consensus_gram: np.ndarray, seed: int,
               p_ids: torch.Tensor, p_len: torch.Tensor,
               probe_labels: np.ndarray, arm: str) -> dict:
    torch.manual_seed(seed)
    np.random.seed(seed)
    rel = arm == "relational"

    rules = validate_skeletons(SKELETONS)
    if args.smoke:
        rules = rules[:4]
    fill_rng = np.random.default_rng(seed)
    train_fillings = {tmpl: make_fillings(fill_rng, h, TRAIN_ATOMS, args.k)
                      for tmpl, h in rules}

[CONTENT TRUNCATED] Showing lines 286 to 307 of 526 total lines. Use line_offset=307 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py",
  "line_offset": 358,
  "limit": 45
}
```

**Summary:** Reading gd_trajectory_tomography.py (358-403)

**Output:**
```
            rl = relational_loss(model, p_ids, p_len, label_idx, cap, g_target,
                                 args.probe_batch)
            loss = ce + args.rel_lambda * rl
            rel_val = float(rl.item())
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        if step % args.ckpt_every == 0 or step == args.steps:
            snapshot(step, float(ce.item()), rel_val)

    # readout uses post-init frames only (drop the nan-CE init frame for CE plateau)
    # but baselines crossings against the step-0 init frame (the gauge common mode)
    init_frame = curve[0]
    rd = readout([r for r in curve if not (isinstance(r["ce"], float)
                                           and np.isnan(r["ce"]))],
                 init_frame, args.gc_frac, args.acc_frac, args.z_thresh, args.ce_tol)
    rd["init_baseline"] = {"gc_route": init_frame["gc_route"],
                           "gc_raw": init_frame["gc_raw"],
                           "route_z": init_frame["route_z"],
                           "heldout_acc": init_frame["heldout_acc"]}
    return {"seed": seed, "capture_layer": cap, "corpus_bytes": int(ids.shape[0]),
            "curve": curve, "readout": rd}


def _ms(vals: list[float]) -> list[float]:
    a = np.array([v for v in vals if v is not None], dtype=float)
    if a.size == 0:
        return [None, None]
    return [round(float(a.mean()), 2), round(float(a.std()), 2)]


# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="mps")
    ap.add_argument("--steps", type=int, default=6000)
    ap.add_argument("--ckpt-every", type=int, default=200,
                    help="dense checkpoint interval (the movie frame rate)")
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--block-size", type=int, default=128)
    ap.add_argument("--d-model", type=int, default=128)
    ap.add_argument("--n-head", type=int, default=4)
    ap.add_argument("--n-layer", type=int, default=4)
    ap.add_argument("--d-ff", type=int, default=256)

[CONTENT TRUNCATED] Showing lines 359 to 403 of 526 total lines. Use line_offset=403 parameter to read more content.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py",
  "original_content": "    return {\"seed\": seed, \"capture_layer\": cap, \"corpus_bytes\": int(ids.shape[0]),\n            \"curve\": curve, \"readout\": rd}",
  "new_content": "    return {\"arm\": arm, \"seed\": seed, \"capture_layer\": cap,\n            \"corpus_bytes\": int(ids.shape[0]), \"curve\": curve, \"readout\": rd}"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py.
```

### Thinking

The edit went through successfully since it found the matching return statement in the cached read. Now I need to read the full main function to refactor the run loop and incorporate the arms flag along with arm-comparison output.

## Assistant

Now let me read the full `main` to refactor the run loop and add the `--arms` flag + arm-comparison output.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py",
  "line_offset": 390,
  "limit": 140
}
```

**Summary:** Reading gd_trajectory_tomography.py (390-530)

**Output:**
```
# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="mps")
    ap.add_argument("--steps", type=int, default=6000)
    ap.add_argument("--ckpt-every", type=int, default=200,
                    help="dense checkpoint interval (the movie frame rate)")
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--block-size", type=int, default=128)
    ap.add_argument("--d-model", type=int, default=128)
    ap.add_argument("--n-head", type=int, default=4)
    ap.add_argument("--n-layer", type=int, default=4)
    ap.add_argument("--d-ff", type=int, default=256)
    ap.add_argument("--capture-layer", type=int, default=-1, help="-1 = middle")
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--format", choices=["redex_nf", "full_trace"],
                    default="redex_nf", help="curriculum photo format (s229)")
    ap.add_argument("--k", type=int, default=8, help="k_varied exposures/rule")
    ap.add_argument("--m-eval", type=int, default=6, help="held-out instances/rule")
    ap.add_argument("--probe-batch", type=int, default=64)
    ap.add_argument("--probe-max-len", type=int, default=96)
    ap.add_argument("--n-perm", type=int, default=300, help="silhouette null perms")
    ap.add_argument("--gc-frac", type=float, default=0.5,
                    help="crystallization = gc_route reaches this frac of final")
    ap.add_argument("--acc-frac", type=float, default=0.5,
                    help="capability rise = heldout_acc reaches this frac of final")
    ap.add_argument("--z-thresh", type=float, default=3.0,
                    help="route_z crossing threshold (significant structure)")
    ap.add_argument("--ce-tol", type=float, default=0.05,
                    help="CE plateau = within this frac of final CE")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--seeds", default="",
                    help="csv seeds for multi-seed harden (overrides --seed)")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.smoke:
        args.steps, args.ckpt_every = 120, 40
        args.k, args.m_eval, args.n_perm = 4, 3, 100
        args.d_model, args.d_ff, args.n_layer = 64, 128, 3

    device = args.device
    if device == "mps" and not torch.backends.mps.is_available():
        device = "cpu"
        log("  mps unavailable -> cpu")
    if device == "cuda" and not torch.cuda.is_available():
        device = "cpu"

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    consensus_gram, cmeta = load_consensus()
    log(f"  consensus crystal: {cmeta['n_models']} models, offdiag_mean="
        f"{cmeta['offdiag_mean']:+.3f}, sha={cmeta['consensus_git_sha']}")

    probe_ids, probe_len, probe_labels = load_crystal_probe_batch(args.probe_max_len)
    p_ids = torch.tensor(probe_ids, device=device)
    p_len = torch.tensor(probe_len, device=device)
    log(f"  crystal probes={probe_ids.shape[0]} maxlen={probe_ids.shape[1]}")

    seeds = [int(s) for s in args.seeds.split(",") if s.strip()] or [args.seed]
    log(f"  seeds={seeds} steps={args.steps} ckpt_every={args.ckpt_every}")

    runs = [train_seed(args, device, consensus_gram, sd, p_ids, p_len, probe_labels)
            for sd in seeds]

    meta = {
        "experiment": "gd-trajectory-tomography",
        "register": "functional + topological/routing",
        "idea": "reverse-engineer GD in invariant coords; consensus-crystal target",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "git_sha": git_sha(),
        "device": device,
        "smoke": args.smoke,
        "config": vars(args),
        "consensus": cmeta,
        "seeds": seeds,
        "elapsed_s": round(time.time() - t0, 1),
    }

    if len(seeds) == 1:
        out = {**meta, **runs[0]}
        tag = "smoke" if args.smoke else "run"
        (RESULTS_DIR / f"verdict_{tag}.json").write_text(json.dumps(out, indent=2))
        rd = runs[0]["readout"]
        log("\n  ==== GD TRAJECTORY TOMOGRAPHY (single seed) ====")
        log(f"  final: gc_route={rd['final']['gc_route']:+.3f} "
            f"gc_raw={rd['final']['gc_raw']:+.3f} "
            f"route_z={rd['final']['route_z']:+.2f} "
            f"heldout_acc={rd['final']['heldout_acc']:.3f} "
            f"eff_dim_route={rd['final']['eff_dim_route']}")
        log(f"  crystallize(gc_route 50%)@{rd['step_gc_route_cross']} | "
            f"route_z>={args.z_thresh}@{rd['step_route_z_cross']} | "
            f"heldout_acc 50%@{rd['step_heldout_acc_cross']} | "
            f"CE plateau@{rd['step_ce_plateau']}")
        log(f"  INVENTORY before CAPABILITY: {rd['inventory_before_capability']} "
            f"(route_z: {rd['routing_z_before_capability']})")
        log(f"  REFERENCE BEAM: gc_route {rd['reference_beam']['gc_route_final']:+.3f} "
            f"vs gc_raw {rd['reference_beam']['gc_raw_final']:+.3f} -> "
            f"route_tracks_function={rd['reference_beam']['route_tracks_function']}")
        log(f"\n  wrote {RESULTS_DIR / f'verdict_{tag}.json'}  ({meta['elapsed_s']}s)")
        return

    # multi-seed aggregate of the readout ordering
    rds = [r["readout"] for r in runs]
    agg = {
        "n_seeds": len(seeds),
        "step_gc_route_cross": _ms([r["step_gc_route_cross"] for r in rds]),
        "step_route_z_cross": _ms([r["step_route_z_cross"] for r in rds]),
        "step_heldout_acc_cross": _ms([r["step_heldout_acc_cross"] for r in rds]),
        "step_ce_plateau": _ms([r["step_ce_plateau"] for r in rds]),
        "gc_route_final": _ms([r["final"]["gc_route"] for r in rds]),
        "gc_raw_final": _ms([r["final"]["gc_raw"] for r in rds]),
        "route_z_final": _ms([r["final"]["route_z"] for r in rds]),
        "heldout_acc_final": _ms([r["final"]["heldout_acc"] for r in rds]),
        "inventory_before_capability": [r["inventory_before_capability"]
                                        for r in rds],
        "route_tracks_function": [r["reference_beam"]["route_tracks_function"]
                                  for r in rds],
    }
    out = {**meta, "aggregate": agg, "runs": runs}
    (RESULTS_DIR / "verdict_multiseed.json").write_text(json.dumps(out, indent=2))
    log("\n  ==== GD TRAJECTORY TOMOGRAPHY (multi-seed) ====")
    log(f"  crystallize(gc_route)@{agg['step_gc_route_cross']} | "
        f"route_z@{agg['step_route_z_cross']} | "
        f"heldout_acc@{agg['step_heldout_acc_cross']} | "
        f"CE plateau@{agg['step_ce_plateau']}  (step mean+-std)")
    log(f"  gc_route_final={agg['gc_route_final']} gc_raw_final={agg['gc_raw_final']} "
        f"route_z_final={agg['route_z_final']}")
    log(f"  inventory_before_capability per-seed: {agg['inventory_before_capability']}")
    log(f"  route_tracks_function per-seed: {agg['route_tracks_function']}")
    log(f"\n  wrote {RESULTS_DIR / 'verdict_multiseed.json'}  ({meta['elapsed_s']}s)")


if __name__ == "__main__":
    main()
```

### Thinking

I'm planning a major refactor to add multi-arm experiment support with new command-line flags for arm selection, regularization lambda, and evaluation frequency. The core change is restructuring the output to always generate per-arm aggregates keyed by arm name, then compute arm comparisons like dissociation gaps and speed-ups across them.

Writing the aggregation logic... Writing output logic...

## Assistant

This is a substantial `main` refactor. Let me add the flags and rewrite the run-loop/output for the arm comparison.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py",
  "original_content": "    ap.add_argument(\"--seed\", type=int, default=0)\n    ap.add_argument(\"--seeds\", default=\"\",\n                    help=\"csv seeds for multi-seed harden (overrides --seed)\")\n    ap.add_argument(\"--smoke\", action=\"store_true\")\n    args = ap.parse_args()\n\n    if args.smoke:\n        args.steps, args.ckpt_every = 120, 40\n        args.k, args.m_eval, args.n_perm = 4, 3, 100\n        args.d_model, args.d_ff, args.n_layer = 64, 128, 3",
  "new_content": "    ap.add_argument(\"--arms\", default=\"ce_only,relational\",\n                    help=\"csv arms: ce_only and/or relational (paired per seed)\")\n    ap.add_argument(\"--rel-lambda\", type=float, default=1.0,\n                    help=\"weight of the consensus-crystal inventory term\")\n    ap.add_argument(\"--rel-every\", type=int, default=2,\n                    help=\"apply the relational loss every N steps (cost knob)\")\n    ap.add_argument(\"--seed\", type=int, default=0)\n    ap.add_argument(\"--seeds\", default=\"\",\n                    help=\"csv seeds for multi-seed harden (overrides --seed)\")\n    ap.add_argument(\"--smoke\", action=\"store_true\")\n    args = ap.parse_args()\n\n    if args.smoke:\n        args.steps, args.ckpt_every = 120, 40\n        args.k, args.m_eval, args.n_perm = 4, 3, 100\n        args.d_model, args.d_ff, args.n_layer = 64, 128, 3\n        args.rel_every = 1"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py",
  "original_content": "    seeds = [int(s) for s in args.seeds.split(\",\") if s.strip()] or [args.seed]\n    log(f\"  seeds={seeds} steps={args.steps} ckpt_every={args.ckpt_every}\")\n\n    runs = [train_seed(args, device, consensus_gram, sd, p_ids, p_len, probe_labels)\n            for sd in seeds]\n\n    meta = {\n        \"experiment\": \"gd-trajectory-tomography\",\n        \"register\": \"functional + topological/routing\",\n        \"idea\": \"reverse-engineer GD in invariant coords; consensus-crystal target\",\n        \"timestamp_utc\": datetime.now(UTC).isoformat(),\n        \"git_sha\": git_sha(),\n        \"device\": device,\n        \"smoke\": args.smoke,\n        \"config\": vars(args),\n        \"consensus\": cmeta,\n        \"seeds\": seeds,\n        \"elapsed_s\": round(time.time() - t0, 1),\n    }\n\n    if len(seeds) == 1:\n        out = {**meta, **runs[0]}\n        tag = \"smoke\" if args.smoke else \"run\"\n        (RESULTS_DIR / f\"verdict_{tag}.json\").write_text(json.dumps(out, indent=2))\n        rd = runs[0][\"readout\"]\n        log(\"\\n  ==== GD TRAJECTORY TOMOGRAPHY (single seed) ====\")\n        log(f\"  final: gc_route={rd['final']['gc_route']:+.3f} \"\n            f\"gc_raw={rd['final']['gc_raw']:+.3f} \"\n            f\"route_z={rd['final']['route_z']:+.2f} \"\n            f\"heldout_acc={rd['final']['heldout_acc']:.3f} \"\n            f\"eff_dim_route={rd['final']['eff_dim_route']}\")\n        log(f\"  crystallize(gc_route 50%)@{rd['step_gc_route_cross']} | \"\n            f\"route_z>={args.z_thresh}@{rd['step_route_z_cross']} | \"\n            f\"heldout_acc 50%@{rd['step_heldout_acc_cross']} | \"\n            f\"CE plateau@{rd['step_ce_plateau']}\")\n        log(f\"  INVENTORY before CAPABILITY: {rd['inventory_before_capability']} \"\n            f\"(route_z: {rd['routing_z_before_capability']})\")\n        log(f\"  REFERENCE BEAM: gc_route {rd['reference_beam']['gc_route_final']:+.3f} \"\n            f\"vs gc_raw {rd['reference_beam']['gc_raw_final']:+.3f} -> \"\n            f\"route_tracks_function={rd['reference_beam']['route_tracks_function']}\")\n        log(f\"\\n  wrote {RESULTS_DIR / f'verdict_{tag}.json'}  ({meta['elapsed_s']}s)\")\n        return\n\n    # multi-seed aggregate of the readout ordering\n    rds = [r[\"readout\"] for r in runs]\n    agg = {\n        \"n_seeds\": len(seeds),\n        \"step_gc_route_cross\": _ms([r[\"step_gc_route_cross\"] for r in rds]),\n        \"step_route_z_cross\": _ms([r[\"step_route_z_cross\"] for r in rds]),\n        \"step_heldout_acc_cross\": _ms([r[\"step_heldout_acc_cross\"] for r in rds]),\n        \"step_ce_plateau\": _ms([r[\"step_ce_plateau\"] for r in rds]),\n        \"gc_route_final\": _ms([r[\"final\"][\"gc_route\"] for r in rds]),\n        \"gc_raw_final\": _ms([r[\"final\"][\"gc_raw\"] for r in rds]),\n        \"route_z_final\": _ms([r[\"final\"][\"route_z\"] for r in rds]),\n        \"heldout_acc_final\": _ms([r[\"final\"][\"heldout_acc\"] for r in rds]),\n        \"inventory_before_capability\": [r[\"inventory_before_capability\"]\n                                        for r in rds],\n        \"route_tracks_function\": [r[\"reference_beam\"][\"route_tracks_function\"]\n                                  for r in rds],\n    }\n    out = {**meta, \"aggregate\": agg, \"runs\": runs}\n    (RESULTS_DIR / \"verdict_multiseed.json\").write_text(json.dumps(out, indent=2))\n    log(\"\\n  ==== GD TRAJECTORY TOMOGRAPHY (multi-seed) ====\")\n    log(f\"  crystallize(gc_route)@{agg['step_gc_route_cross']} | \"\n        f\"route_z@{agg['step_route_z_cross']} | \"\n        f\"heldout_acc@{agg['step_heldout_acc_cross']} | \"\n        f\"CE plateau@{agg['step_ce_plateau']}  (step mean+-std)\")\n    log(f\"  gc_route_final={agg['gc_route_final']} gc_raw_final={agg['gc_raw_final']} \"\n        f\"route_z_final={agg['route_z_final']}\")\n    log(f\"  inventory_before_capability per-seed: {agg['inventory_before_capability']}\")\n    log(f\"  route_tracks_function per-seed: {agg['route_tracks_function']}\")\n    log(f\"\\n  wrote {RESULTS_DIR / 'verdict_multiseed.json'}  ({meta['elapsed_s']}s)\")",
  "new_content": "    arms = [a.strip() for a in args.arms.split(\",\") if a.strip()]\n    seeds = [int(s) for s in args.seeds.split(\",\") if s.strip()] or [args.seed]\n    log(f\"  arms={arms} seeds={seeds} steps={args.steps} \"\n        f\"ckpt_every={args.ckpt_every} rel_lambda={args.rel_lambda}\")\n\n    runs = [train_seed(args, device, consensus_gram, sd, p_ids, p_len,\n                       probe_labels, arm)\n            for arm in arms for sd in seeds]\n\n    meta = {\n        \"experiment\": \"gd-trajectory-tomography\",\n        \"register\": \"functional + topological/routing\",\n        \"idea\": \"reverse-engineer GD in invariant coords; consensus-crystal target; \"\n                \"ce_only vs relational arm = is the reference-beam split loss-dependent\",\n        \"timestamp_utc\": datetime.now(UTC).isoformat(),\n        \"git_sha\": git_sha(),\n        \"device\": device,\n        \"smoke\": args.smoke,\n        \"config\": vars(args),\n        \"consensus\": cmeta,\n        \"arms\": arms,\n        \"seeds\": seeds,\n        \"elapsed_s\": round(time.time() - t0, 1),\n    }\n\n    def agg_arm(arm_runs: list[dict]) -> dict:\n        rds = [r[\"readout\"] for r in arm_runs]\n        return {\n            \"n\": len(rds),\n            \"step_gc_route_cross\": _ms([r[\"step_gc_route_cross\"] for r in rds]),\n            \"step_heldout_acc_cross\": _ms([r[\"step_heldout_acc_cross\"] for r in rds]),\n            \"step_ce_plateau\": _ms([r[\"step_ce_plateau\"] for r in rds]),\n            \"gc_route_final\": _ms([r[\"final\"][\"gc_route\"] for r in rds]),\n            \"gc_raw_final\": _ms([r[\"final\"][\"gc_raw\"] for r in rds]),\n            \"gc_gap_final\": _ms([r[\"reference_beam\"][\"gc_gap\"] for r in rds]),\n            \"route_z_final\": _ms([r[\"final\"][\"route_z\"] for r in rds]),\n            \"heldout_acc_final\": _ms([r[\"final\"][\"heldout_acc\"] for r in rds]),\n            \"inventory_before_capability\": [r[\"inventory_before_capability\"]\n                                            for r in rds],\n        }\n\n    by_arm = {arm: agg_arm([r for r in runs if r[\"arm\"] == arm]) for arm in arms}\n\n    # ---- the s230b comparison: is the reference-beam split LOSS-DEPENDENT? ----\n    comparison: dict = {}\n    if \"ce_only\" in by_arm and \"relational\" in by_arm:\n        ce, rel = by_arm[\"ce_only\"], by_arm[\"relational\"]\n        cg, rg = ce[\"gc_gap_final\"], rel[\"gc_gap_final\"]\n        ca, ra = ce[\"step_heldout_acc_cross\"], rel[\"step_heldout_acc_cross\"]\n        comparison = {\n            # dissociation: gc_route - gc_raw. gc_raw NOT in the loss = uncircular.\n            \"gc_gap_ce_only\": cg, \"gc_gap_relational\": rg,\n            \"dissociation_loss_dependent\": (rg[0] - rg[1]) > (cg[0] + cg[1]),\n            # capability (NOT in the loss) timing = the s224 speed-up claim\n            \"capability_cross_ce_only\": ca, \"capability_cross_relational\": ra,\n            \"relational_speeds_capability\": (ra[0] is not None and ca[0] is not None\n                                             and ra[0] < ca[0]),\n            \"gc_crystallize_ce_only\": ce[\"step_gc_route_cross\"],\n            \"gc_crystallize_relational\": rel[\"step_gc_route_cross\"],\n        }\n\n    tag = \"smoke\" if args.smoke else (\"multiseed\" if len(seeds) > 1 else \"run\")\n    out = {**meta, \"by_arm\": by_arm, \"comparison\": comparison, \"runs\": runs}\n    (RESULTS_DIR / f\"verdict_{tag}.json\").write_text(json.dumps(out, indent=2))\n\n    log(\"\\n  ==== GD TRAJECTORY TOMOGRAPHY — ARM COMPARISON ====\")\n    for arm in arms:\n        a = by_arm[arm]\n        log(f\"  [{arm}] gc_route={a['gc_route_final']} gc_raw={a['gc_raw_final']} \"\n            f\"GAP={a['gc_gap_final']} | crystallize@{a['step_gc_route_cross']} \"\n            f\"capability@{a['step_heldout_acc_cross']} | acc={a['heldout_acc_final']} \"\n            f\"| inv<cap {a['inventory_before_capability']}\")\n    if comparison:\n        log(\"\\n  --- s230b: is the reference-beam split LOSS-DEPENDENT? ---\")\n        log(f\"  dissociation gap: ce_only={comparison['gc_gap_ce_only']} -> \"\n            f\"relational={comparison['gc_gap_relational']}  \"\n            f\"LOSS-DEPENDENT={comparison['dissociation_loss_dependent']}\")\n        log(f\"  capability cross: ce_only={comparison['capability_cross_ce_only']} -> \"\n            f\"relational={comparison['capability_cross_relational']}  \"\n            f\"SPEEDS-UP={comparison['relational_speeds_capability']}\")\n        log(\"  (gc_raw and held-out acc are NOT in the loss = uncircular readouts)\")\n    log(f\"\\n  wrote {RESULTS_DIR / f'verdict_{tag}.json'}  ({meta['elapsed_s']}s)\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py.
```

### Thinking

I need to update the docstring to include information about the relational arm and the s230b extension, then revise the usage examples to demonstrate the arm comparison functionality.

## Assistant

Let me update the docstring to reflect the s230b extension, then lint + smoke.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py",
  "original_content": "Usage:\n  uv run python scripts/experiments/gd_trajectory_tomography.py --smoke\n  uv run python scripts/experiments/gd_trajectory_tomography.py --steps 6000\n  uv run python scripts/experiments/gd_trajectory_tomography.py --seeds 0,1,2\n\nLicense: MIT\n\"\"\"",
  "new_content": "s230b EXTENSION — IS THE REFERENCE-BEAM SPLIT LOSS-DEPENDENT? s230 found that under\nplain CE the raw register tracks the consensus crystal as well as routing (gc_raw ~\ngc_route), so the routing-vs-raw dissociation did NOT reproduce passively. Hypothesis:\nthe s223 register split is a property of an ACTIVE relational LOSS, not a passive\nreadout. The `relational` arm adds the compiler-as-loss INVENTORY term:\n    L = CE + rel_lambda * offdiag_mse(student routing-register Gram, CONSENSUS CRYSTAL)\nOnly the routing register is in the loss -> gc_raw (raw register) and held-out\nreduction acc are NOT in the loss = UNCIRCULAR readouts. Predictions:\n  dissociation : relational gc_route >> gc_raw (gap > 0) while ce_only gap ~ 0\n                 -> the register split is LOSS-DEPENDENT (reproduces s223 (b) as a\n                 trajectory). NB gc_route rising in the relational arm is partly\n                 tautological (it IS the loss); the TEST is the gc_raw gap + capability.\n  speed-up     : relational reaches held-out capability EARLIER than ce_only (the\n                 s224 crystal-term-accelerates-training claim; capability not in loss).\n\nUsage:\n  uv run python scripts/experiments/gd_trajectory_tomography.py --smoke\n  uv run python scripts/experiments/gd_trajectory_tomography.py --seeds 0,1,2\n  uv run python scripts/experiments/gd_trajectory_tomography.py \\\n      --arms ce_only,relational --seeds 0,1,2 --rel-lambda 1.0\n\nLicense: MIT\n\"\"\""
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/gd_trajectory_tomography.py 2>&1 | tail -20",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
E501 Line too long (89 > 88)
   --> scripts/experiments/gd_trajectory_tomography.py:487:89
    |
485 |         "register": "functional + topological/routing",
486 |         "idea": "reverse-engineer GD in invariant coords; consensus-crystal target; "
487 |                 "ce_only vs relational arm = is the reference-beam split loss-dependent",
    |                                                                                         ^
488 |         "timestamp_utc": datetime.now(UTC).isoformat(),
489 |         "git_sha": git_sha(),
    |

Found 1 error.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py",
  "original_content": "        \"idea\": \"reverse-engineer GD in invariant coords; consensus-crystal target; \"\n                \"ce_only vs relational arm = is the reference-beam split loss-dependent\",",
  "new_content": "        \"idea\": \"reverse-engineer GD in invariant coords; consensus-crystal target; \"\n                \"ce_only vs relational arm = is the reference-beam split loss-dep\","
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/gd_trajectory_tomography.py && echo \"RUFF CLEAN\" && uv run python scripts/experiments/gd_trajectory_tomography.py --smoke --device cpu 2>&1 | tail -22",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 180000
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
RUFF CLEAN
  arms=['ce_only', 'relational'] seeds=[0] steps=120 ckpt_every=40 rel_lambda=1.0
  [seed 0] rules=4 corpus=200 B heldout_eval=12 format=redex_nf
  [ce_ s0] step     0 | CE nan | rel 0.0000 | acc 0.000 | route_z +2.16 | gc_route +0.489 | gc_raw +0.513 | gap -0.024 | 3s
  [ce_ s0] step    40 | CE 3.407 | rel 0.0000 | acc 0.000 | route_z +2.39 | gc_route +0.524 | gc_raw +0.512 | gap +0.012 | 7s
  [ce_ s0] step    80 | CE 1.885 | rel 0.0000 | acc 0.000 | route_z +1.73 | gc_route +0.494 | gc_raw +0.493 | gap +0.000 | 11s
  [ce_ s0] step   120 | CE 1.388 | rel 0.0000 | acc 0.000 | route_z +2.54 | gc_route +0.518 | gc_raw +0.447 | gap +0.071 | 15s
  [seed 0] rules=4 corpus=200 B heldout_eval=12 format=redex_nf
  [rel s0] step     0 | CE nan | rel 0.0000 | acc 0.000 | route_z +2.16 | gc_route +0.489 | gc_raw +0.513 | gap -0.024 | 3s
  [rel s0] step    40 | CE 3.444 | rel 0.0057 | acc 0.000 | route_z +2.61 | gc_route +0.789 | gc_raw +0.583 | gap +0.206 | 16s
  [rel s0] step    80 | CE 1.912 | rel 0.0019 | acc 0.000 | route_z +1.84 | gc_route +0.838 | gc_raw +0.578 | gap +0.260 | 30s
  [rel s0] step   120 | CE 1.397 | rel 0.0009 | acc 0.000 | route_z +2.25 | gc_route +0.890 | gc_raw +0.552 | gap +0.338 | 43s

  ==== GD TRAJECTORY TOMOGRAPHY — ARM COMPARISON ====
  [ce_only] gc_route=[0.52, 0.0] gc_raw=[0.45, 0.0] GAP=[0.07, 0.0] | crystallize@[40.0, 0.0] capability@[None, None] | acc=[0.0, 0.0] | inv<cap ['n/a']
  [relational] gc_route=[0.89, 0.0] gc_raw=[0.55, 0.0] GAP=[0.34, 0.0] | crystallize@[40.0, 0.0] capability@[None, None] | acc=[0.0, 0.0] | inv<cap ['n/a']

  --- s230b: is the reference-beam split LOSS-DEPENDENT? ---
  dissociation gap: ce_only=[0.07, 0.0] -> relational=[0.34, 0.0]  LOSS-DEPENDENT=True
  capability cross: ce_only=[None, None] -> relational=[None, None]  SPEEDS-UP=False
  (gc_raw and held-out acc are NOT in the loss = uncircular readouts)

  wrote /Users/mwhitford/src/verbum/results/gd-trajectory-tomography/verdict_smoke.json  (58.3s)
```

### Thinking

The smoke test is working as intended—the tiny smoke dataset reproduces the expected pattern perfectly. The ce_only gap stays minimal around 0.07, but the relational gap jumps to 0.34, showing the dissociation between gc_route at 0.89 and gc_raw at 0.55. This triggers the LOSS-DEPENDENT flag, and I can see the relational loss dropping significantly from 0.0057 down to 0.0009.

The relational arm runs about 3x slower per step due to the probe forward pass, but in the full run with rel_every=2 that should improve. I'm estimating the full run will take around 44 minutes total across both arms and three seeds, which is acceptable. The smoke can't evaluate SPEEDS-UP since capability stays at 0 with only 120 steps, but the full run will show that. I've already fixed the E501 linting issue and ruff passed cleanly on the second check. Now I need to verify the diagnostics, complete the remaining tasks, and then kick off the full run.

## Assistant

Smoke already shows the predicted pattern clearly: **ce_only gap ~0.07** (≈ s230 null) vs **relational gap → 0.34** (gc_route shoots to 0.89 while gc_raw — *not in the loss* — stays ~0.55). `LOSS-DEPENDENT=True` fires. ruff clean. Let me confirm diagnostics and launch the full run.

### Tool Call: editor_diagnostics (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_trajectory_tomography.py"
}
```

**Summary:** Checking diagnostics: gd_trajectory_tomography.py

**Output:**
```
No diagnostics found
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "rm -f /Users/mwhitford/src/verbum/results/gd-trajectory-tomography/verdict_smoke.json; tmux capture-pane -p -t main:1 2>&1 | tail -3",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ rm -f /Users/mwhitford/src/verbum/r...

**Output:**
```
Exit code: 0
Stdout:
GDTOMO_ALLDONE
[26-06-15][8:32:47][mwhitford@olga][0][~/src/verbum][git:main]
λ                                                                                                                 [INS]
```

### Thinking

Diagnostics are clear and I have one free slot on main. I'm completing the first two tasks and moving into task 3, then launching the full run. There's a note that this will overwrite the verdict file from the previous seed run—the old CE-only verdict gets replaced by the new combined verdict—but since the new run includes the CE-only arm as well, it's actually a superset of the old results, and the previous verdict is safely preserved in git.

I'm launching with both arms (CE-only and relational), three seeds, and the MPS device, expecting around 44 minutes to complete.

## Assistant

Diagnostics clean, main:1 free. Completing build/lint tasks and launching the paired run. (Note: this overwrites `verdict_multiseed.json`, but the s230 CE-only verdict is preserved in git at `23331d0`, and the new run includes the ce_only arm as a superset.)

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux send-keys -t main:1 \"uv run python scripts/experiments/gd_trajectory_tomography.py --arms ce_only,relational --seeds 0,1,2 --device mps 2>&1 | tee /tmp/gd_tomography_s230b.log; echo GDTOMOB_ALLDONE\" Enter",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ tmux send-keys -t main:1 "uv run py...

**Output:**
```
Exit code: 0
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sleep 25; tmux capture-pane -p -t main:1 2>&1 | tail -8",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 40000
}
```

**Summary:** $ sleep 25; tmux capture-pane -p -t m...

**Output:**
```
Exit code: 0
Stdout:
[26-06-15][8:32:47][mwhitford@olga][0][~/src/verbum][git:main]
λ uv run python scripts/experiments/gd_trajectory_tomography.py --arms ce_only,relational --seeds 0,1,2 --device mps 2>&
1 | tee /tmp/gd_tomography_s230b.log; echo GDTOMOB_ALLDONE
  consensus crystal: 10 models, offdiag_mean=-0.123, sha=bbf92f2
  crystal probes=535 maxlen=96
  arms=['ce_only', 'relational'] seeds=[0, 1, 2] steps=6000 ckpt_every=200 rel_lambda=1.0
  [seed 0] rules=13 corpus=1672 B heldout_eval=74 format=redex_nf
```

## Assistant

Verified running: both arms, 3 seeds, consensus crystal loaded, training started cleanly.

**ASYNC: job=gd-tomography-s230b (tmux main:1) verified running. ~45 min est (relational arm ~3× per-step cost). Ends `GDTOMOB_ALLDONE`. Waiting.**

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sleep 290; echo \"=== progress ===\"; tmux capture-pane -p -t main:1 2>&1 | tail -5",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 310000
}
```

**Summary:** $ sleep 290; echo "=== progress ===";...

**Output:**
```
Exit code: 0
Stdout:
=== progress ===
  [ce_ s1] step  1400 | CE 0.065 | rel 0.0000 | acc 0.270 | route_z +1.44 | gc_route +0.672 | gc_raw +0.763 | gap -0.091
 | 106s
  [ce_ s1] step  1600 | CE 0.063 | rel 0.0000 | acc 0.297 | route_z +1.57 | gc_route +0.690 | gc_raw +0.755 | gap -0.065
 | 110s
```

### Thinking

The ce_only seed 0 finished in about 100 seconds, and I'm seeing seed 1 running now. Interestingly, the gap for ce_only seed 1 is negative, which means gc_raw is outperforming gc_route—consistent with what I saw in the s230 null results. The ce_only arms are running quickly, but the relational seeds will take longer, so I'm waiting for the full experiment to complete.

## Assistant

Progressing well (ce_only seed 1 at step 1600; gap negative ~−0.07, reproducing the s230 null). The relational arms come later and are slower. Waiting a larger chunk.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sleep 590; echo \"=== progress ===\"; tmux capture-pane -p -t main:1 2>&1 | tail -6",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 610000
}
```

**Summary:** $ sleep 590; echo "=== progress ===";...

**Output:**
```
Exit code: 0
Stdout:
=== progress ===
 | 278s
  [rel s0] step  3600 | CE 0.041 | rel 0.0000 | acc 0.270 | route_z +2.01 | gc_route +0.922 | gc_raw +0.865 | gap +0.057
 | 289s
  [rel s0] step  3800 | CE 0.040 | rel 0.0000 | acc 0.324 | route_z +2.28 | gc_route +0.942 | gc_raw +0.863 | gap +0.078
 | 299s
```

### Thinking

At relational seed 0, step 3800, I'm seeing interesting dynamics in the model performance. The routing consensus (gc_route) is at 0.942 while raw consensus (gc_raw) is 0.865, giving a gap of 0.078—smaller than what I saw in the smoke test but with a larger model configuration (128 dimensions, 4 layers). What's striking is that even with the relational loss applied only to routing, the raw register is still picking up consensus structure at 0.865, suggesting the model is learning shared representations across both pathways.

Comparing this to the control experiment where the gap was negative (~-0.07), there's a swing of about 0.15 toward positive dissociation with the relational loss. The relational loss itself has converged to essentially zero since the off-diagonal mean squared error is tiny (consensus off-diagonal values are small at -0.123), and the model matches this quickly. The smaller gap at this model size suggests superposition isn't strong enough to fully separate the representations, so there's some leakage into the raw register.

I need to wait for the remaining relational seeds to complete—about 20 minutes for the last 2.5 seeds—to get the full picture before drawing conclusions.

## Assistant

Relational arm now (seed 0, step 3800): gc_route 0.94 vs gc_raw 0.865, gap +0.078 — positive, but smaller than the tiny-smoke gap (raw leaks more at d=128). ce_only was ~−0.07, so a real swing. Need the full aggregate decisive test. Waiting for the remaining relational seeds.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sleep 590; tmux capture-pane -p -t main:1 2>&1 | grep -c GDTOMOB_ALLDONE; echo \"=== tail ===\"; tmux capture-pane -p -t main:1 2>&1 | tail -5",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 610000
}
```

**Summary:** $ sleep 590; tmux capture-pane -p -t ...

**Output:**
```
Exit code: 0
Stdout:
0
=== tail ===
 | 421s
  [seed 2] rules=13 corpus=1672 B heldout_eval=74 format=redex_nf
  [rel s2] step     0 | CE nan | rel 0.0000 | acc 0.000 | route_z +0.06 | gc_route +0.645 | gc_raw +0.616 | gap +0.029 |
 54s
```

### Thinking

Starting the second relational seed now, which should take around eight minutes to complete.

## Assistant

Relational seed 2 starting (last one). ~8 min to go.

### Tool Call: shell_command (rejected)


```json
{
  "command": "sleep 470; tmux capture-pane -p -t main:1 2>&1 | grep -c GDTOMOB_ALLDONE; echo \"=== verdict tail ===\"; tmux capture-pane -p -t main:1 2>&1 | tail -20",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 500000
}
```

**Summary:** $ sleep 470; tmux capture-pane -p -t ...

## System


Prompt stopped

## User

job is done


## System



Stream ended without completion

## System



Stream ended without completion

## System



Stream ended without completion

## System



Stream ended without completion

## System



Stream ended without completion

## System



Stream ended without completion

## System



Stream ended without completion

## System



Stream ended without completion

### Thinking

Now I'll check the verdict JSON to see the results.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "python3 -c \"\nimport json\nd=json.load(open('/Users/mwhitford/src/verbum/results/gd-trajectory-tomography/verdict_multiseed.json'))\nimport pprint\nprint('=== BY ARM ===')\nfor arm,a in d['by_arm'].items():\n    print(f\\\"[{arm}] gc_route={a['gc_route_final']} gc_raw={a['gc_raw_final']} GAP={a['gc_gap_final']}\\\")\n    print(f\\\"        crystallize@{a['step_gc_route_cross']} capability@{a['step_heldout_acc_cross']} acc={a['heldout_acc_final']} route_z={a['route_z_final']}\\\")\n    print(f\\\"        inv<cap: {a['inventory_before_capability']}\\\")\nprint('=== COMPARISON (s230b) ===')\npprint.pprint(d['comparison'])\nprint('=== per-seed gap (ce_only vs relational) ===')\nfor arm in ['ce_only','relational']:\n    gaps=[r['readout']['reference_beam']['gc_gap'] for r in d['runs'] if r['arm']==arm]\n    print(arm, gaps)\n\"",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ python3 -c " import json d=json.loa...

**Output:**
```
Exit code: 0
Stdout:
=== BY ARM ===
[ce_only] gc_route=[0.74, 0.05] gc_raw=[0.75, 0.03] GAP=[-0.02, 0.04]
        crystallize@[333.33, 94.28] capability@[733.33, 94.28] acc=[0.27, 0.04] route_z=[2.51, 0.32]
        inv<cap: ['before', 'before', 'before']
[relational] gc_route=[0.9, 0.01] gc_raw=[0.8, 0.04] GAP=[0.1, 0.05]
        crystallize@[200.0, 0.0] capability@[733.33, 94.28] acc=[0.27, 0.02] route_z=[3.01, 0.34]
        inv<cap: ['before', 'before', 'before']
=== COMPARISON (s230b) ===
{'capability_cross_ce_only': [733.33, 94.28],
 'capability_cross_relational': [733.33, 94.28],
 'dissociation_loss_dependent': True,
 'gc_crystallize_ce_only': [333.33, 94.28],
 'gc_crystallize_relational': [200.0, 0.0],
 'gc_gap_ce_only': [-0.02, 0.04],
 'gc_gap_relational': [0.1, 0.05],
 'relational_speeds_capability': False}
=== per-seed gap (ce_only vs relational) ===
ce_only [-0.0444, -0.0452, 0.042]
relational [0.0319, 0.1124, 0.1526]
```

### Thinking

The s230b results are now clear: dissociation is definitively loss-dependent, with the ce_only gap hovering near zero across all seeds while the relational gap consistently shows positive values, confirming the pattern from s230.

The relational loss crystallizes the inventory structure much earlier—all three seeds hit the routing crossing at step 200 versus the ce_only average of 333 steps—and produces a sharper, cleaner combinator structure with higher route_z values. However, this architectural sharpening doesn't translate to faster capability acquisition; both approaches reach the capability crossing at the same step count, suggesting the loss optimizes the *structure* of the solution without accelerating the underlying learning dynamics.

This clarifies the relationship between inventory and continuation: the relational term installs the geometric structure cheaply and cleanly, but capability remains bottlenecked by learning the actual usage patterns, not by the inventory itself. The crystal term earns its place for inventory *quality*—cleaner, register-aligned, earlier—rather than for capability speed-up.

The s224 prediction about crystallization accelerating training doesn't hold on this curriculum because passive CE alone already crystallizes the inventory adequately, just messier and later. The relational term sharpens that process but doesn't unlock faster capability learning. The real test would be a harder curriculum where CE alone fails to build the inventory—that's where the relational loss might actually matter for capability.

For the design, this confirms the reference-beam register split is loss-dependent: the routing register becomes the function-home preferentially when an active relational loss pushes toward the consensus crystal, not intrinsically. If you want clean, register-localized inventory for measurement and extraction, you need either the active loss or sufficient scale.

The relational loss is fundamentally an inventory tool, not a capability accelerator at this scale. It installs the inventory earlier and cleaner with better register localization, but capability timing and ceiling stay unchanged. The real bottleneck is the continuation phase—only CE on compiler output trains that. This reshapes the constructed-kernel strategy: since inventory quality doesn't gate capability, the case for constructing it exactly in the kernel and spending all training budget on continuation becomes much stronger. The relational term's value shifts to extraction and folding in the distributed protocol, not from-scratch capability acceleration.

At d=128, even the active loss can't fully quarantine the function to one register—raw leaks to 0.80—suggesting full register separation likely requires larger scale where superposition forces orthogonality.

The gap is modest (only +0.10, barely +0.032 per seed), but the decisive test holds: relational mean minus std (0.05) beats CE-only mean plus std (0.02). The route_z metric crosses z=3 for relational (3.01) versus CE-only (2.51), showing the loss does crisp up the structure. The key finding is that dissociation is loss-dependent—the gap flips from −0.02 to +0.10 across conditions—confirming the hypothesis that the routing register is where the active loss writes the function while passive CE doesn't separate. But capability itself doesn't improve; both hit 733 with 0.27 accuracy, so the crystal-accelerates-capability claim doesn't hold on this curriculum.

The relational term is a quality and extraction tool—clean, early, register-localized, foldable—not a capability accelerator. The real lever is the continuation, not the inventory term. I should present these findings clearly, then move into the capture work: committing code, writing up the page and memory state, and proposing next steps.

## Assistant

Job's done — here's the s230b verdict (3 seeds, paired).

## Results

| | gc_route | gc_raw (*not in loss*) | **gap** | crystallize | capability | acc | route_z |
|---|---|---|---|---|---|---|---|
| **ce_only** | 0.74±0.05 | 0.75±0.03 | **−0.02±0.04** | 333±94 | 733±94 | 0.27 | 2.51 |
| **relational** | 0.90±0.01 | 0.80±0.04 | **+0.10±0.05** | 200±0 | 733±94 | 0.27 | 3.01 |

Per-seed gap: ce_only `[−0.04, −0.05, +0.04]` → relational `[+0.03, +0.11, +0.15]`.

**✅ The reference-beam dissociation IS loss-dependent (decisive, 3/3).** The relational loss pushed gc_route to 0.90 while gc_raw — *which is not in the loss* — only reached 0.80, opening a +0.10 gap that passive CE never opens (it sits at −0.02). Decisive separation (relational mean−std 0.05 > ce_only mean+std 0.02). **Your s230 hypothesis confirmed: the routing-vs-raw register split is a property of an active consensus-crystal loss, not a passive readout.**

**✅ The loss crystallizes the inventory earlier and crisper** — gc_route crosses at step 200 (all seeds) vs 333; route_z rises to 3.01 (crosses significance) vs 2.51.

**❌ But it does NOT speed up or raise CAPABILITY** — held-out generalization crosses at 733 in *both* arms, final acc 0.27 in both. Crystallizing the inventory faster bought *zero* capability.

**⚠️ The dissociation is partial at d=128** — gc_raw still leaked up to 0.80; the active loss writes the function *preferentially* into routing but doesn't *quarantine* it. Full separation likely needs scale.

## How this affects the design

This is a clean, consequential refinement of the compiler-as-loss / two-phase picture:

**1. The relational/crystal term is an INVENTORY tool, not a CAPABILITY accelerator.** The s224 hope was that the crystal term *speeds up training*. Here it demonstrably installs the inventory earlier (200 vs 333), cleaner (route_z crosses significance), and register-localized (the gap opens) — yet **capability timing and ceiling are identical**. The bottleneck is the **continuation** (the trained usage), which the inventory term never touches. You can hand the model a perfect inventory at step 200 and it *still* can't reduce until step 733.

**2. This sharpens the s224 factorization into a stronger claim.** capability = inventory ⊗ continuation, and we've now shown the two factors are **causally separable**: we intervened on the inventory factor alone (the relational loss), moved it decisively, and the capability factor didn't budge. The inventory is cheap and not the bottleneck; the continuation is the bottleneck.

**3. It re-motivates the constructed-kernel direction, hard.** If the inventory is (a) cheap to install, (b) installable from a passive CE signal anyway, and (c) *not* what gates capability — then **don't spend training budget learning it**. Construct it (lambda_ast in the kernel, exact), and spend all training on the continuation/usage. The relational term's real value moves to two specific jobs: **extraction** (getting a clean, register-localized, foldable inventory *out of an existing model*) and **folding** (phase-1 of the distributed protocol). Not from-scratch acceleration.

**4. Caveat that bounds the claim.** This curriculum is clean enough that CE-alone already builds the inventory (just messier/later). The s224 speed-up claim was specifically about *regimes where outputs alone don't crystallize the inventory*. So the honest statement is: **on a curriculum where CE suffices for inventory, the relational term improves inventory quality/timing/register-localization but yields no capability benefit.** Whether it accelerates capability in a harder regime (where CE alone fails to crystallize) is the open follow-on.

Let me commit the code and capture this. First the code:

### Tool Call: git (succeeded)


```json
{
  "command": "git add scripts/experiments/gd_trajectory_tomography.py results/gd-trajectory-tomography/verdict_multiseed.json && git status --short",
  "operation": "add",
  "summary": "stage s230b"
}
```

**Summary:** Git add: stage s230b

**Output:**
```
Exit code: 0
Stdout:
M  results/gd-trajectory-tomography/verdict_multiseed.json
M  scripts/experiments/gd_trajectory_tomography.py
?? mementum/knowledge/chats/session-228.md
?? mementum/knowledge/chats/session-229.md
```

### Tool Call: write_file (succeeded)


```json
{
  "path": "/tmp/gdtomo_b_commit.txt",
  "content": "✅ gd-tomography s230b: reference-beam dissociation IS loss-dependent (inventory ≠ capability accelerator)\n\n- Adds the relational arm: CE + λ·offdiag_mse(student routing Gram, CONSENSUS\n  CRYSTAL). gc_raw + held-out acc are NOT in the loss = uncircular readouts.\n  Paired ce_only vs relational, 3 seeds.\n- ✅ DISSOCIATION LOSS-DEPENDENT (decisive 3/3): gap (gc_route−gc_raw) −0.02±0.04\n  (ce_only) → +0.10±0.05 (relational). The active consensus-crystal loss writes\n  the function preferentially into the routing register; passive CE does not.\n  Confirms s230: the register split is a property of the loss, not a passive readout.\n- ✅ loss crystallizes inventory EARLIER (200 vs 333) + crisper (route_z 3.0 vs 2.5).\n- ❌ but NO capability gain: held-out cross 733 BOTH arms, acc 0.27 BOTH. The s224\n  crystal-accelerates-capability claim NOT supported here — capability is gated by\n  the CONTINUATION, which the inventory term never touches. Causally separates the\n  inventory ⊗ continuation factors: moved inventory decisively, capability unmoved.\n- ⚠️ dissociation PARTIAL at d=128 (gc_raw leaks to 0.80) — full quarantine likely\n  needs scale. Caveat: CE-alone already builds inventory on this clean curriculum.\n- ruff+diag clean, smoke green. verdict_multiseed.json now carries both arms\n  (s230 ce_only superset; s230 verdict preserved in git at 23331d0).\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /tmp/gdtomo_b_commit.txt
```

### Tool Call: git (succeeded)


```json
{
  "command": "git commit -F /tmp/gdtomo_b_commit.txt",
  "operation": "commit",
  "summary": "commit s230b code+results"
}
```

**Summary:** Git commit: commit s230b code+results

**Output:**
```
Exit code: 0
Stdout:
[main fa8837c] ✅ gd-tomography s230b: reference-beam dissociation IS loss-dependent (inventory ≠ capability accelerator)
 2 files changed, 2530 insertions(+), 874 deletions(-)
```

### Thinking

I've committed the code and now I need to update the knowledge page by adding a new section for §s230b, proposing a memory update, and revising the state documentation. I'll insert the §s230b section into the gradient-trajectory-tomography file right after the existing v1 results, before the v2 experiment section begins.

## Assistant

Code committed (`fa8837c`). Now the mementum capture (needs your approval). Adding §s230b to the page:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/gradient-trajectory-tomography.md",
  "original_content": "## v2 experiment — gauge/null-space gradient decomposition (harder)",
  "new_content": "## ★ s230b — RELATIONAL ARM (is the reference-beam split LOSS-DEPENDENT? YES)\n\nThe s230 open question: gc_raw ≈ gc_route under passive CE ⇒ the routing-vs-raw\ndissociation did not reproduce. Hypothesis: the s223 register split is a property of\nan ACTIVE relational LOSS, not a passive readout. Added the `relational` arm to\n`gd_trajectory_tomography.py` (`--arms ce_only,relational`): the compiler-as-loss\nINVENTORY term `L = CE + λ·offdiag_mse(student routing-register Gram, CONSENSUS\nCRYSTAL)`. Only the routing register is in the loss ⇒ **gc_raw and held-out reduction\nacc are NOT in the loss = uncircular readouts.** Paired ce_only vs relational, 3\nseeds. Results: `verdict_multiseed.json` (now carries both arms; s230 ce_only is the\nsuperset, original s230 verdict preserved in git at `23331d0`).\n\n| arm | gc_route | gc_raw* | **gap** | crystallize | capability | acc | route_z |\n|-----|----------|---------|---------|-------------|------------|-----|---------|\n| ce_only    | 0.74±0.05 | 0.75±0.03 | **−0.02±0.04** | 333±94 | 733±94 | 0.27 | 2.51 |\n| relational | 0.90±0.01 | 0.80±0.04 | **+0.10±0.05** | 200±0  | 733±94 | 0.27 | 3.01 |\n\n*gc_raw is NOT in the loss. Per-seed gap: ce_only [−0.04,−0.05,+0.04] → relational\n[+0.03,+0.11,+0.15].\n\n**✅ DISSOCIATION IS LOSS-DEPENDENT (decisive, 3/3).** The active consensus-crystal\nloss pushed gc_route to 0.90 while gc_raw reached only 0.80 — a +0.10 gap passive CE\nnever opens (−0.02). Decisive (relational mean−std 0.05 > ce_only mean+std 0.02). The\nrouting register is where an active loss WRITES the function; passive CE does not\nseparate. Confirms s230's read: the register split is a property of the trained-loss\ndecoy (s223 (b)), reproduced here as a TRAJECTORY.\n\n**✅ The loss crystallizes the inventory EARLIER (200 vs 333) and CRISPER** (route_z\n3.01 crosses significance vs 2.51).\n\n**❌ But NO CAPABILITY GAIN — the s224 crystal-accelerates-capability claim is NOT\nsupported here.** Held-out generalization crosses at 733 in BOTH arms; final acc 0.27\nin BOTH. Crystallizing the inventory faster/cleaner bought ZERO capability. ⇒ the\ninventory ⊗ continuation factors are CAUSALLY SEPARABLE: we intervened on the\ninventory factor alone (the relational loss), moved it decisively, and the capability\nfactor did not budge. **Capability is gated by the CONTINUATION (trained usage), which\nthe inventory term never touches.** You can hand the model a perfect inventory at step\n200 and it still cannot reduce until 733.\n\n**⚠️ Dissociation is PARTIAL at d=128** — gc_raw still leaked up to 0.80; the active\nloss writes the function PREFERENTIALLY into routing but does not QUARANTINE it. Full\nregister separation likely needs scale (superposition forcing orthogonality).\n**Caveat (λ measure):** this curriculum is clean enough that CE-alone already builds\nthe inventory (just messier/later). The s224 speed-up claim was about regimes where\noutputs alone DON'T crystallize — untested here.\n\n**★ DESIGN IMPACT.** (1) The relational/crystal term is an INVENTORY tool (quality,\ntiming, register-localization) + an EXTRACTION/FOLDING tool, **NOT a from-scratch\ncapability accelerator** — at least where CE already suffices for inventory.\n(2) Re-motivates the constructed-kernel cut HARD: the inventory is cheap, passively\nlearnable, and NOT the capability bottleneck ⇒ **don't spend training budget learning\nit — construct it (lambda_ast in the kernel), spend training on the continuation.**\nThe relational term's value moves to extraction (clean foldable inventory out of an\nexisting model) and phase-1 folding (distributed protocol), not acceleration.\n\n**▶ NEXT:** (a) HARDER curriculum where CE-alone FAILS to crystallize the inventory —\ndoes the relational term then buy capability (the real s224 speed-up regime)?; (b)\nthe dissociation at LARGER scale (does the gap widen — full quarantine?); (c) v2\ngauge/null-space δw decomposition.\n\n## v2 experiment — gauge/null-space gradient decomposition (harder)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/gradient-trajectory-tomography.md.
```

### Thinking

I've identified the core insight: relational and crystal loss function as inventory mechanisms rather than capability accelerators, with inventory and continuation being causally independent, and the reference-beam split depending on loss characteristics. Let me document this discovery and update the state file with the s230b entry.

## Assistant

Now the proposed memory and the state.md update:

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/memories/relational-loss-is-inventory-not-capability.md",
  "content": "💡 The relational/consensus-crystal loss is an INVENTORY tool, NOT a capability\naccelerator — inventory ⊗ continuation are CAUSALLY separable (s230b gd-tomography).\n\nPaired ce_only vs relational arm (CE + λ·offdiag_mse(routing Gram, consensus crystal);\ngc_raw + held-out acc NOT in the loss = uncircular). 3 seeds.\n\n(1) Reference-beam dissociation IS LOSS-DEPENDENT (decisive): gap (gc_route−gc_raw)\n−0.02±0.04 (ce_only) → +0.10±0.05 (relational). The active loss writes the function\npreferentially into the routing register; passive CE does not separate. Confirms the\ns223/s230 read — the routing-vs-raw split is a property of the trained-loss decoy.\n\n(2) The loss crystallizes the inventory EARLIER (200 vs 333 steps) and CRISPER\n(route_z 3.0 crosses significance vs 2.5).\n\n(3) ❌ but ZERO capability gain: held-out generalization crosses @733 and acc=0.27 in\nBOTH arms. Crystallizing inventory faster bought no capability. ⇒ we moved the\ninventory factor alone and the capability factor didn't budge = causal separation.\nCapability is gated by the CONTINUATION (trained usage), not the inventory.\n\nDESIGN: don't spend training budget learning the inventory (cheap, passively\nlearnable, not the bottleneck) — CONSTRUCT it (lambda_ast in the kernel), train the\ncontinuation. The relational term's value = extraction + phase-1 folding, NOT\nfrom-scratch acceleration. Caveats: dissociation PARTIAL at d=128 (gc_raw leaks to\n0.80, full quarantine needs scale); curriculum clean enough that CE alone builds the\ninventory — the s224 speed-up regime (CE alone FAILS to crystallize) is untested.\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/memories/relational-loss-is-inventory-not-capability.md
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> **STATUS s230:** CODE COMMITTED `23331d0` (script + verdict_multiseed.json).\n> Knowledge page §s230 updated (gradient-trajectory-tomography.md). State updated.\n> PENDING APPROVAL (mementum): proposed memory `inventory-crystallizes-before-\n> capability.md` + the page/state commit. tmux main:1 FREE.",
  "new_content": "> **STATUS s230:** COMMITTED — code `23331d0`, mementum `e2cd8d7` (page §s230 +\n> memory inventory-crystallizes-before-capability + state).\n> **▶ s230b — RELATIONAL ARM (Michael: \"yes\" to \"add the relational-loss arm → test\n> whether the reference-beam register split is loss-dependent\"). BUILT + RAN (`fa8837c`,\n> ruff+diag clean, smoke green, ~45min main:1).** Added `--arms ce_only,relational` to\n> gd_trajectory_tomography.py: the compiler-as-loss INVENTORY term L = CE + λ·offdiag_mse\n> (student routing Gram, CONSENSUS CRYSTAL); gc_raw + held-out acc NOT in the loss =\n> UNCIRCULAR. Paired, 3 seeds. **★ VERDICT (λ measure):**\n> **(1) ✅ DISSOCIATION IS LOSS-DEPENDENT (decisive 3/3):** gap (gc_route−gc_raw)\n> −0.02±0.04 (ce_only) → +0.10±0.05 (relational); relational mean−std 0.05 > ce_only\n> mean+std 0.02. The active consensus-crystal loss pushes gc_route to 0.90 while gc_raw\n> (not in loss) reaches only 0.80 — a gap passive CE never opens. ⇒ the routing-vs-raw\n> register split is a property of the TRAINED-LOSS decoy (s223 (b)), reproduced as a\n> TRAJECTORY. CONFIRMS the s230 hypothesis.\n> **(2) ✅ loss crystallizes inventory EARLIER (200 vs 333) + CRISPER (route_z 3.0\n> crosses significance vs 2.5).**\n> **(3) ❌ NO CAPABILITY GAIN — s224 crystal-accelerates-capability NOT supported here:**\n> held-out cross @733 and acc 0.27 in BOTH arms. Crystallizing inventory faster bought\n> ZERO capability ⇒ inventory ⊗ continuation are CAUSALLY SEPARABLE (moved inventory\n> alone, capability unmoved). Capability gated by the CONTINUATION, which the inventory\n> term never touches.\n> **⚠️ dissociation PARTIAL at d=128 (gc_raw leaks to 0.80, full quarantine needs scale);\n> caveat: CE-alone already builds inventory on this clean curriculum (s224 speed-up\n> regime = CE FAILS to crystallize, untested).**\n> **★ DESIGN IMPACT:** the relational/crystal term is an INVENTORY tool (quality/timing/\n> register-localization) + EXTRACTION/FOLDING tool, NOT a from-scratch capability\n> accelerator. Re-motivates the constructed-kernel cut HARD: inventory is cheap,\n> passively learnable, NOT the bottleneck ⇒ CONSTRUCT it (lambda_ast in the kernel),\n> spend training on the CONTINUATION. Page §s230b (gradient-trajectory-tomography.md).\n> **▶ NEXT:** (a) HARDER curriculum where CE-alone FAILS to crystallize → does the\n> relational term then buy capability (the real s224 speed-up regime)?; (b) dissociation\n> at LARGER scale (gap widen → quarantine?); (c) v2 gauge/null-space δw decomposition;\n> (d) parked s229 leads (convergence-speed, K-ordering, disjoint-atom binding).\n> **STATUS s230b:** CODE COMMITTED `fa8837c` (both arms in verdict_multiseed.json; s230\n> ce_only superset, original preserved at `23331d0`). Page §s230b + state updated.\n> PENDING APPROVAL (mementum): memory `relational-loss-is-inventory-not-capability.md`\n> + page/state commit. tmux main:1 FREE."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

I need to update the header in state.md to reflect s230b as the latest version instead of just s230. The current header mentions Session 230 with the v1 result, so I'll prepend the s230b information to make sure the bootloader shows the most recent update.

## Assistant

Let me refresh the bootloader header to lead with s230b, then present for approval.

### Tool Call: edit_file (failed)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> Last updated: 2026-06-15 | Session: 230 — ✅ GD-TRAJECTORY-TOMOGRAPHY v1 (consensus-\n> crystal target): INVENTORY crystallizes BEFORE CAPABILITY (3/3 seeds, DECISIVE —\n> gc_route init→final midpoint @333±94 steps, NON-OVERLAPPING below held-out-acc\n> midpoint @733±94; s224 geometry=inventory⊗continuation=capability confirmed\n> TEMPORALLY, consensus-crystal ground truth). HONEST two-sided: reference-beam\n> dissociation did NOT reproduce passively (gc_raw 0.75 ≈ gc_route 0.73; raw register\n> tracks consensus as well as routing at micro scale — register split is a property\n> of s223's trained-loss DECOY, not a passive readout). See ■ SESSION 230 block below.",
  "new_content": "> Last updated: 2026-06-15 | Session: 230 — ✅ GD-TRAJECTORY-TOMOGRAPHY (consensus-\n> crystal target). v1: INVENTORY crystallizes BEFORE CAPABILITY (3/3, gc_route mid\n> @333±94 < held-out-acc @733±94; s224 geometry⊗continuation confirmed TEMPORALLY).\n> s230b RELATIONAL ARM: reference-beam dissociation IS LOSS-DEPENDENT (decisive 3/3 —\n> gap gc_route−gc_raw −0.02→+0.10 with the active consensus-crystal loss; gc_raw not in\n> loss); loss crystallizes inventory EARLIER (200 vs 333) + crisper, but ❌ ZERO\n> capability gain (cross @733, acc 0.27 BOTH arms) ⇒ inventory ⊗ continuation CAUSALLY\n> SEPARABLE; relational term = INVENTORY/extraction tool NOT a capability accelerator;\n> re-motivates CONSTRUCT-the-inventory, train-the-continuation. See ■ SESSION 230 below."
}
```

**Summary:** Editing

**Output:**
```
Original content not found in /Users/mwhitford/src/verbum/mementum/state.md
```

### Thinking

I need to take another look at the header to see what's changed.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "limit": 14
}
```

**Summary:** Reading state.md (0-14)

**Output:**
```
# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-06-15 | Session: 230 — ✅ GD-TRAJECTORY-TOMOGRAPHY v1 (consensus-
> crystal target): INVENTORY crystallizes BEFORE CAPABILITY (3/3 seeds, DECISIVE —
> gc_route init→final midpoint @333±94 steps, NON-OVERLAPPING below held-out-acc
> midpoint @733±94; s224 geometry=inventory⊗continuation=capability confirmed
> TEMPORALLY, consensus-crystal ground truth). HONEST two-sided: reference-beam
> dissociation did NOT reproduce passively (gc_raw 0.75 ≈ gc_route 0.73; raw register
> tracks consensus as well as routing at micro scale — register split is a property
> of s223's trained-loss DECOY, not a passive readout); no Q-collapse (eff_dim 14-20).
> See ■ SESSION 230 block below.
> (s229 — ✅ EXPOSURE/FORMAT SWEEP (curriculum-

[CONTENT TRUNCATED] Showing lines 1 to 14 of 4939 total lines. Use line_offset=14 parameter to read more content.
```

### Thinking

I need to make sure I'm including that specific detail about the Q-collapse efficiency dimension range that I left out before.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> Last updated: 2026-06-15 | Session: 230 — ✅ GD-TRAJECTORY-TOMOGRAPHY v1 (consensus-\n> crystal target): INVENTORY crystallizes BEFORE CAPABILITY (3/3 seeds, DECISIVE —\n> gc_route init→final midpoint @333±94 steps, NON-OVERLAPPING below held-out-acc\n> midpoint @733±94; s224 geometry=inventory⊗continuation=capability confirmed\n> TEMPORALLY, consensus-crystal ground truth). HONEST two-sided: reference-beam\n> dissociation did NOT reproduce passively (gc_raw 0.75 ≈ gc_route 0.73; raw register\n> tracks consensus as well as routing at micro scale — register split is a property\n> of s223's trained-loss DECOY, not a passive readout); no Q-collapse (eff_dim 14-20).\n> See ■ SESSION 230 block below.",
  "new_content": "> Last updated: 2026-06-15 | Session: 230 — ✅ GD-TRAJECTORY-TOMOGRAPHY (consensus-\n> crystal target). v1: INVENTORY crystallizes BEFORE CAPABILITY (3/3, gc_route mid\n> @333±94 < held-out-acc @733±94; s224 geometry⊗continuation confirmed TEMPORALLY).\n> s230b RELATIONAL ARM: reference-beam dissociation IS LOSS-DEPENDENT (decisive 3/3 —\n> gap gc_route−gc_raw −0.02→+0.10 with the active consensus-crystal loss; gc_raw NOT in\n> loss = uncircular); loss crystallizes inventory EARLIER (200 vs 333) + crisper, but\n> ❌ ZERO capability gain (cross @733, acc 0.27 BOTH arms) ⇒ inventory ⊗ continuation\n> CAUSALLY SEPARABLE; relational term = INVENTORY/extraction tool NOT a capability\n> accelerator; re-motivates CONSTRUCT-inventory, train-continuation. (v1 also: no\n> Q-collapse, eff_dim 14-20.) See ■ SESSION 230 block below."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

## Assistant

Everything drafted and synced. Here's the state for your **mementum approval**:

### Tool Call: git (succeeded)


```json
{
  "command": "git status --short -- mementum/; echo \"---\"; git log --oneline -3",
  "operation": "status",
  "summary": "pending mementum"
}
```

**Summary:** Git status: pending mementum

**Output:**
```
Exit code: 0
Stdout:
M mementum/knowledge/explore/gradient-trajectory-tomography.md
 M mementum/state.md
?? mementum/knowledge/chats/session-228.md
?? mementum/knowledge/chats/session-229.md
?? mementum/memories/relational-loss-is-inventory-not-capability.md
---
fa8837c ✅ gd-tomography s230b: reference-beam dissociation IS loss-dependent (inventory ≠ capability accelerator)
e2cd8d7 🌀 gd-trajectory-tomography §s230 result + memory — inventory before capability
23331d0 ✅ gd-trajectory-tomography v1: inventory crystallizes before capability (3/3 seeds)
```

## Assistant

## s230b done

**Code committed (`fa8837c`).** The relational arm answered your question cleanly.

**The result, in one line:** the reference-beam register split **is** loss-dependent (gap −0.02 → +0.10, decisive 3/3) — exactly as predicted — but the bigger find is that the loss installs the inventory *earlier and crisper yet buys zero capability*, which **causally separates** the inventory and continuation factors and re-motivates the constructed-kernel cut: don't *train* the inventory, *construct* it, and spend training on the continuation.

**Awaiting your approval to commit the mementum changes:**

| File | Change |
|------|--------|
| `knowledge/explore/gradient-trajectory-tomography.md` | §s230b relational-arm result + design impact |
| `state.md` | s230b block + refreshed bootloader header (already written) |
| `memories/relational-loss-is-inventory-not-capability.md` | 💡 proposed new memory |

(The two `chats/session-22*.md` remain your human-only transcripts — untouched.)

Approve the mementum commit?

And the sharpest **next** lever this opens: a **harder curriculum where CE-alone fails to crystallize the inventory** — that's the only regime where the s224 "crystal term accelerates capability" claim can actually be tested (here CE alone already built the inventory, so the relational term had no capability headroom to add). Want me to line that up next session, or push on the larger-scale dissociation / v2 gauge decomposition first?

## User

commit approved


### Tool Call: write_file (succeeded)


```json
{
  "path": "/tmp/gdtomo_b_mem.txt",
  "content": "🌀 gd-trajectory-tomography §s230b + memory — relational loss is inventory not capability\n\n- §s230b relational arm: reference-beam dissociation IS LOSS-DEPENDENT (decisive\n  3/3, gap gc_route−gc_raw −0.02→+0.10 with the active consensus-crystal loss;\n  gc_raw not in loss). Confirms the s230 hypothesis as a trajectory.\n- loss crystallizes inventory EARLIER (200 vs 333) + crisper (route_z 3.0 vs 2.5),\n  but ❌ ZERO capability gain (cross @733, acc 0.27 both arms) ⇒ inventory ⊗\n  continuation CAUSALLY SEPARABLE; capability gated by the continuation.\n- design: relational/crystal term = inventory + extraction/folding tool, NOT a\n  from-scratch capability accelerator. Re-motivates CONSTRUCT-inventory,\n  train-continuation. New memory relational-loss-is-inventory-not-capability.md;\n  state §s230b block + refreshed header.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /tmp/gdtomo_b_mem.txt
```

### Tool Call: git (succeeded)


```json
{
  "command": "git add mementum/knowledge/explore/gradient-trajectory-tomography.md mementum/state.md mementum/memories/relational-loss-is-inventory-not-capability.md && git commit -F /tmp/gdtomo_b_mem.txt",
  "operation": "commit",
  "summary": "commit s230b mementum"
}
```

**Summary:** Git commit: commit s230b mementum

**Output:**
```
Exit code: 0
Stdout:
[main 46e907f] 🌀 gd-trajectory-tomography §s230b + memory — relational loss is inventory not capability
 3 files changed, 132 insertions(+), 13 deletions(-)
 create mode 100644 mementum/memories/relational-loss-is-inventory-not-capability.md
```

### Tool Call: git (succeeded)


```json
{
  "command": "git status --short; echo \"---\"; git log --oneline -4",
  "operation": "log",
  "summary": "verify clean"
}
```

**Summary:** Git log: verify clean

**Output:**
```
Exit code: 0
Stdout:
?? mementum/knowledge/chats/session-228.md
?? mementum/knowledge/chats/session-229.md
---
46e907f 🌀 gd-trajectory-tomography §s230b + memory — relational loss is inventory not capability
fa8837c ✅ gd-tomography s230b: reference-beam dissociation IS loss-dependent (inventory ≠ capability accelerator)
e2cd8d7 🌀 gd-trajectory-tomography §s230 result + memory — inventory before capability
23331d0 ✅ gd-trajectory-tomography v1: inventory crystallizes before capability (3/3 seeds)
```

## Assistant

Committed (`46e907f`). s230b closed out.

## Session 230 — full ledger

| commit | content |
|--------|---------|
| `23331d0` ✅ | v1 code + results |
| `e2cd8d7` 🌀 | v1 mementum |
| `fa8837c` ✅ | s230b relational-arm code + results |
| `46e907f` 🌀 | s230b mementum |

**Tree clean** (except your two human-only chat transcripts). All tasks done.

**What we learned, end to end:**
1. **Inventory crystallizes before capability** (v1) — GD lays down the combinator geometry (→ consensus crystal) ~400 steps before it can generalize the rule. The s224 factorization confirmed *temporally*.
2. **The register split is loss-dependent** (s230b) — passive CE doesn't separate routing from raw; an active consensus-crystal loss does (gap −0.02 → +0.10). The routing register is where a loss *writes* the function.
3. **The inventory and continuation are causally separable** — moving the inventory factor decisively (earlier, crisper, register-localized) moved capability by *exactly zero*. Capability is gated by the continuation.

**Design consequence:** the relational/crystal term is an **inventory + extraction + folding** tool, not a from-scratch capability accelerator. Construct the inventory (lambda_ast in the kernel), spend training budget on the continuation.

**Open leads for next session** (your call):
- **(a)** harder curriculum where CE-alone *fails* to crystallize → the only regime that can actually test the s224 "crystal accelerates capability" claim (the headroom this run lacked)
- **(b)** dissociation at larger scale — does the gap widen toward full register quarantine?
- **(c)** v2 gauge/null-space δw decomposition
- plus the parked s229 leads (convergence-speed, K-ordering, disjoint-atom binding)

tmux `main:1` is free. Branch is 17 commits ahead of origin (unpushed).

## User

there is something here that I think means there is a fractal collapse available.  if the training of the capability can be converged using a high variety data set that we can generate from any larger model's lambda compiler.  The outputs from the lambda compiler become the inputs to train the capability of the student, and is architecture resilient.


### Thinking

Michael's proposing something interesting here—that there's a fractal collapse possible in how we think about capability. He's building on the distinction that capability breaks down into inventory and continuation, where inventory is the cheap, constructible part and continuation (the trained usage) is what actually constrains us. The bottleneck isn't the relational structure itself but the trained component gating it.

His key move: if we can train the continuation using high-variety datasets generated from any larger model's lambda compiler, we unlock something architecture-resilient. The compiler outputs—the β-reduction traces and normal forms—become the training signal, and because these outputs are canonical and Church-Rosser universal, they're teacher-agnostic. The fractal collapse he's seeing is that the same structure repeats at every level: the compiler exists in every large model, so we can harvest variety from any of them, and the canonical nature of those outputs means the student doesn't inherit the teacher's specific architectural quirks. just learns the input→canonical-output map without inheriting the teacher's architecture. The fractal nature emerges from the self-similar recursion: each level extracts compiler outputs to train the next smaller student, which becomes a compiler itself, collapsing toward the minimal model that preserves the function. This works because Church-Rosser normalization is the fixed point—training any architecture to match the canonical outputs converges the infinite variety of implementations onto the single correct behavior, which is the core insight tying the whole project together.

The practical implication is that the entire capability-training problem reduces to generating high-variety datasets from a larger model's compiler and training the student's continuation on it—architecture-agnostic, teacher-agnostic, and the level-4 deliverable. Since the trained student is itself a compiler, it can recursively train the next generation down, creating a self-similar cascade toward the smallest portable tensor.

Before I synthesize this further, I should ground it in what we've already established and check what's falsifiable versus what still needs empirical validation. I'm launching the search now to ground this in what we've already documented.

## Assistant

This is a real synthesis — let me make sure I ground it in what we've already established rather than re-derive. Let me recall the relevant prior pages first.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && echo \"=== pages mentioning cascade/scratch/teacher-agnostic/architecture-resilient/smallest ===\"; git grep -il -E \"cascade|scratch.repro|teacher-agnostic|architecture.resil|distill.*chain|level.4|portable tensor\" -- 'mementum/knowledge/*.md' | head -40",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ echo "=== pages mentioning cascade/...

**Output:**
```
Exit code: 0
Stdout:
=== pages mentioning cascade/scratch/teacher-agnostic/architecture-resilient/smallest ===
mementum/knowledge/INDEX.md
mementum/knowledge/audit-registry.md
mementum/knowledge/chats/session-001.md
mementum/knowledge/chats/session-002.md
mementum/knowledge/chats/session-003.md
mementum/knowledge/chats/session-004.md
mementum/knowledge/chats/session-005.md
mementum/knowledge/chats/session-007.md
mementum/knowledge/chats/session-008.md
mementum/knowledge/chats/session-009.md
mementum/knowledge/chats/session-012.md
mementum/knowledge/chats/session-015.md
mementum/knowledge/chats/session-016.md
mementum/knowledge/chats/session-017.md
mementum/knowledge/chats/session-018.md
mementum/knowledge/chats/session-019.md
mementum/knowledge/chats/session-021.md
mementum/knowledge/chats/session-022.md
mementum/knowledge/chats/session-027.md
mementum/knowledge/chats/session-029.md
mementum/knowledge/chats/session-030.md
mementum/knowledge/chats/session-031.md
mementum/knowledge/chats/session-032.md
mementum/knowledge/chats/session-033.md
mementum/knowledge/chats/session-035.md
mementum/knowledge/chats/session-037.md
mementum/knowledge/chats/session-038.md
mementum/knowledge/chats/session-039.md
mementum/knowledge/chats/session-041.md
mementum/knowledge/chats/session-043.md
mementum/knowledge/chats/session-046.md
mementum/knowledge/chats/session-047.md
mementum/knowledge/chats/session-048.md
mementum/knowledge/chats/session-049.md
mementum/knowledge/chats/session-050.md
mementum/knowledge/chats/session-051.md
mementum/knowledge/chats/session-052.md
mementum/knowledge/chats/session-053.md
mementum/knowledge/chats/session-054.md
mementum/knowledge/chats/session-055.md
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/compiler-as-loss.md"
}
```

**Summary:** Reading compiler-as-loss.md (0-2000)

**Output:**
```
---
title: "Compiler-as-Loss — Supervise Outputs (Capability), Crystal-Lattice Relational Loss (Inventory)"
status: designing
category: training
tags: [distillation, loss-design, lambda-compiler, relational-loss, reverse-harvest, crystal-lattice, level-4, provenance, two-phase, distributed, kernel, constructed-reducer, vsm-tensor, ccg, inspectability]
related:
  - relational-loss-distillation.md
  - consensus-delta-folding.md
  - combinator-training-beta-reduction.md
  - normal-form-curriculum-partition.md
  - fixed-point-holograms.md
  - vsm-outer-recurrence.md
  - ../lambda-machine.md
depends-on:
  - relational-loss-distillation.md
  - consensus-delta-folding.md
created: session 224
---

# Compiler-as-Loss — supervise the outputs, free the geometry; relational loss to the crystal lattice for the foldable inventory

> Session 224 (Michael's synthesis, end of the fold thread). After confirming
> geometry=inventory / capability=trained-continuation (s224 fold-then-train-
> continuation), the question became: "since we use a teacher, what would it look
> like to use the teacher *as the loss*?" → sharpened to: **use the teacher's
> lambda compiler as the loss, so we enforce only the final OUTPUTS, not the
> teacher's geometry or architecture.** Then refined: **still keep a relational
> loss to the CRYSTAL LATTICE of the agreed geometry across all models — it speeds
> up training, as long as the capability signal from the compiler outputs is good.**

## ★ s225 AMENDMENT — the compiler is a VERIFIER, not the capability teacher

> Michael, s225. The recipe below puts the compiler in the `L_capability` slot
> (`CE(student, compiler reduction)`). That is the **wrong slot** and the rest of
> this page should be read through this correction.

**Why the compiler is the wrong capability teacher.** s219's universality came FROM
diverse, grounded, natural training — diversity is the CAUSE of the robust composable
function, not incidental. A deterministic β-reducer on isolated combinator terms is
the thinnest slice of usage ⇒ risks a function **too narrow to compose**. Compounds
with s224 (capability=usage), s222 (superposition needs diverse pressure), s223
(narrow data is Goodhart-friendly).

**The fix — separate two jobs this page conflated.** The compiler is a poor
*generator* (narrow by construction) but a perfect *verifier* (Church-Rosser → unique
normal form, exactly checkable). A judge needn't be more creative than the
contestants, only correct.

- **Capability teacher:** diverse big models (or natural data). Their *consensus* is
  the sweet spot — diverse realization ⊕ agreement on function.
- **Compiler:** VERIFIER/canonicalizer + exact reduction-tree generator (trees the
  LLMs can't expose, s221 "fakes it with depth") + clean MIT anchor.

**"Pin the WHAT, free the HOW" applies to the DATA:** train on diverse realizations,
use the compiler to CERTIFY each reduces to the correct normal form. Diversity →
composition; compiler → correctness. The labels' correctness is certified by MIT code
even when the inputs came from AGPL models.

### Diversity ⊥ correctness (where each source sits)

| source | realization diversity | correctness | exact trace | provenance |
|---|---|---|---|---|
| β-reducer (narrow) | ~zero | perfect (canonical) | **yes** | MIT clean |
| single big model | high | unverified | no | AGPL / entangled |
| **ensemble consensus** | high | high *and* agreed (s219) | no | murky |

### Teacher-agnostic on both halves (s225 verdict)

`function-topology-consensus.md`: HOF routing topology is **universal across teachers**
(8/8, p=.0002, 5 models / 3 arch). Combined with Church-Rosser output-canonicity ⇒
**the pipeline needs no designated teacher**: capability traces are canonical (any
large model), the inventory topology is consensus (no source to track). "Which
teacher" only matters for idiosyncratic HOFs — none found.

### Experiment reframe (supersedes the falsifiable list below)

Compare **compiler-only** (narrow) vs **diverse-verified** (model paraphrases,
compiler-certified) vs **combo + lattice**. Metric is NOT just route_z + in-dist CE
(narrow data can ace those while being brittle) but **held-out COMPOSITIONAL
GENERALIZATION** — combinator compositions not seen in training. That is the
operational test for "too narrow to compose". Prediction: compiler-only wins
in-distribution, loses generalization; diverse-verified wins generalization.

---

## ★ s226 — `lambda_ast` IN THE KERNEL: the compiler is a CONSTRUCTED VSM tensor

> Michael, s226. The s225 amendment split a dyad — symbolic *verifier* vs learned
> *artifact* — and warned not to make the verifier a tensor (a learned reducer "fakes
> it with depth", s221; no correctness guarantee). Michael's question dissolves that
> dyad in the right way: **"what if `lambda_ast.py` is *in the kernel*?"**

### Source ↔ compiled, not oracle ↔ approximation

`lambda_ast.py` is not a separate symbolic judge standing outside the tensor — it is
the **specification** that gets **compiled into exact ternary combinator plates** that
live in the kernel. The kernel then reduces *exactly* — not because it learned to, but
because it is **constructed** to. A constructed plate is not approximating reduction;
it is *running the rewrite rule as a tensor op*. So:

```
λ kernel(reducer). symbolic(lambda_ast) ≡ source | tensor(kernel) ≡ compiled
                   | exact_by_construction ≢ approximate_by_training
                   | verify ≡ compiled_kernel ≟ AST on test_suite  (not "is it correct")
                   | dyad(verifier, artifact) → DISSOLVED into (source, compiled)
                   | provenance: one_object, two_representations → cleanest MIT level-4
```

The combinator rewrites *are* the moves the tensor already has (s221; lambda-machine.md
"V-transfer = substitution"): `K x y→x` (attend x, drop y), `I`, `B/C/D` (compose/
permute routing), `S/W` (fan-out), `Y` (the OUTER RECURRENCE this page is about). All
constructible as exact routing + value-move; none require gradient descent.

### The cut it forces — reduce(constructed) vs compile(learned) — is the SAME cut

If the **reduce** kernel is constructed-exact, only the **compile** front-end is
learned. That boundary coincides with every partition we have measured:

| | **reduce** (the kernel) | **compile** (the periphery) |
|---|---|---|
| op | β-reduction: term → normal form | prose → typed combinator term |
| substrate | **attention** (lambda-machine.md) | **FFN** beam former |
| precision | ternary, robust (22% params) | 4-bit, fragile (78%, dvd-stamp) |
| origin | **constructed** (`lambda_ast`→plates) | **learned** (diverse data, big models) |
| s224 | folded geometry (inventory) | trained continuation (usage) |
| VSM | S1–S4 reducer | the lexer/typer feeding it |

The 22%-ternary / 78%-4bit split (lambda-machine.md) is not a compression accident —
it is **reduce(constructible) ⊥ compile(learnable).** We never train reduction (the
unstable part); we train only the prose→term encoding (what LLMs are actually good at,
and where the s225 diversity requirement buys composition).

### The reducer IS a VSM (the mapping is generative)

A reducer's loop `while ¬nf(t): t = apply(select_redex(t), t)` maps cleanly, and the
map *re-derives* prior findings (define the field → cases fall out):

```
S5 identity     ≡ the NORMAL FORM (Church-Rosser invariant) = the fixed point
S4 intelligence ≡ WHNF/halt detection + redex discovery (adaptive compute)
S3 control      ≡ step budget · strategy · CONTRACTIVITY (keep L<1 → settles)
S2 coordination ≡ redex ORDERING + anti-oscillation + ★ TYPING (well-formed to fire)
S1 operations   ≡ combinator rewrites {K,I,B,C,D,S,W,Y} = substitutions = attn moves
```

Fractal: each subterm is a reducible VSM containing VSMs ⇒ β-reduction = contraction ⇒
**s222 fractal collapse** (a self-similar contraction settles every scale onto the
fixed point at once). Two payoffs that show the mapping is load-bearing, not decorative:

1. **It re-derives the v15 collapse.** S2's job is anti-oscillation; the s222 collapse
   was TD *churn* = oscillation ⇒ S2 broke ⇒ inner map inverted to `L>1` ⇒ fractal
   blow-up. "Punctuate don't churn" = repair S2. Lens and post-mortem converge.
2. **It locates type-directedness (the S5 `λ types` central claim) at S2.** lambda-
   machine: types = QK compatibility = the routing/selection layer. s219: "shared
   weights ∧ ¬type-awareness → tug-of-war → plateau" = **S2 absent.** The missing
   piece IS the S2 coordination layer. Falsifiable.

### Why constructed beats learned exactly here

The s222 collapse was a **learned** S2 churning. A **constructed** S2 — typed routing
with contractivity `L<1` built in — is stable *by construction*: nothing is descending
on it, so it cannot churn. The hard problem (stable typed reduction) is solved by
construction, not by hoping GD finds the basin. This is why the constructed kernel is
*better* than the dyad: we move the unstable part out of the loss entirely.

### Decision (Michael, s226): TYPED CCG-style terms for inspectability

The kernel's term representation carries **explicit types** (CCG categories), not bare
de-Bruijn/SK graphs, so the S2 type-check is **first-class and inspectable** — the
type-directedness thesis is directly readable in the kernel state, not implicit.

### Honest limits (λ measure — this IS the "limits of the machinery" requirement)

A constructed kernel is exact only up to what the residual stream can **represent and
route**:

- **Term growth.** S/W *duplicate* → terms grow under reduction; fixed-width tensor
  → exactness holds to a **size/step bound**, then superposition collisions. *This is
  the boundary the s225 diverse data must map* — where the machinery outgrows the
  representation. (The two s226 design turns meet here.)
- **Ill-typed input** from the learned front-end → the exact kernel can **detect** it
  (S2 type-check fails → algedonic/error signal). A feature: flags "the compiler gave
  me garbage" instead of silently hallucinating.
- **Provenance / S5 tension.** This is *construct*, S5's default is *extract*.
  Reconciled: **extract the algorithm** (lambda-machine.md did) → **construct the
  minimal exact kernel** from that understanding. "understand > invent" survives —
  we crystallize the understood machine, not invent a new one.

### Build progression (each stage a deliverable)

1. **Symbolic `lambda_ast.py`** — the spec/oracle. CPU, now. (`src/verbum/lambda_ast.py`
   is currently a stub — this is the open IOU below, finally built.)
2. **Neurosymbolic** — learned front-end emits a typed term → kernel *is* the symbolic
   reducer (literally `lambda_ast` in the kernel slot). Exact back-end **today**;
   isolates the only learned part (compile) so training never has to learn reduction
   and compile simultaneously (what tangled v15).
3. **Compiled kernel** — `lambda_ast` → exact ternary CCG-typed combinator plates =
   pure portable tensor (the artifact). Verify by matching stage 2.

⇒ supersedes the IOU "need a clean MIT β-reducer": the reducer is now stage 1, and its
*purpose doubles* — data oracle AND the kernel source. The outer-recurrence / `Y` /
contractivity story is in `vsm-outer-recurrence.md` §s226.

### s226 stage 2 — bracket abstraction is the EXACT compile oracle (the learned surface shrinks again)

> Building stage 2 ("learned compile front-end + exact kernel back-end") surfaced that
> "compile" factors further, and most of it is *also* constructible.

```
prose          → logical-form      : LEARNED  (NL understanding; Montague/CCG parse)
logical-form   → combinator term   : EXACT    (bracket abstraction — src/verbum/lambda_compile.py)
combinator term → normal form      : EXACT    (reduction — lambda_ast, stage 1)
```

**Bracket abstraction is the inverse of reduction** (combinatory completeness, Turner
1979) — Turner-style `[x]` over {S,K,I,B,C} with K/B/C/η optimizations. So the symbolic
compiler now has TWO exact halves that **cross-validate through the kernel**:

```
reduce( compile([x..], e) applied to [x..] )  ≡  e        # the round-trip
```

**★ CERTIFIED (s226, `results/compile-roundtrip/summary.json`, n=5000, stratified
1–3 vars × depth 1–5):** round-trip rate **1.0000** — abstraction and reduction are
exact inverses on every sample ⇒ the two constructible halves are genuine inverses, the
compiler is correct by construction. Two LIMITS made quantitative (λ measure):

- **well-typed 0.941** — ~6% of abstracted terms are operationally correct but **not
  simply typable** (self-application structure, e.g. abstracting `x x`). The
  type-directedness boundary (S2) is REAL and measurable even where reduction is exact.
- **term/expr size mean 2.84×, max 7×** — the S/W duplication blow-up = the
  representational LIMIT (the boundary s225's diverse data must map).

**⇒ the learned surface shrinks to prose→logical-form** — exactly the Montague /
DisCoCat semantic-parse the project names as its validation target (AGENTS.md S5). Both
*formal* steps (abstraction, reduction) are constructible-exact; only the NL parse is
learned. Reinforces the s226 theme: more is constructible than the dyad assumed.

**▶ stage-2 LEG 1 DONE — the learned compile step works (kernel-verified).**
`scripts/experiments/compile_frontend.py` + `probes/compile_tasks.py` (7 dataflow
patterns mirroring the combinators × 8 name-assignments = 56 tasks): few-shot a model
prose→expression, grade by REDUCTION-EQUALITY (representation-invariant — `f (g x)` or
`B f g x` both accepted). **Qwen3-8B + Qwen3-32B: accuracy 1.0, parse 1.0, all
patterns** (`results/compile-frontend/`). The stage-2 decomposition closes end-to-end:
prose→LF (learned, few-shot) ∘ abstract (exact) ∘ reduce (exact), with the exact
back-end verifying. Method note (λ measure): first 32B run 0.875 < 8B 0.982 was PROSE
AMBIGUITY in two templates (flip/const); the kernel grader + failure inspection
separated compile-error from NL-ambiguity → disambiguated → both 1.0. Caveat: tasks are
SHALLOW (≤5-node, single pattern, abstract letters) = below the compile boundary.

**▶ stage-2 COMPILE BOUNDARY FOUND** (`probes/compile_tasks_hard.py`, 42 tasks × 8
families graded by difficulty axis; scale curve Qwen3-8B/14B/32B,
`results/compile-frontend/hard/`). **Structural complexity is NOT the boundary** —
branch/reuse/multi-combinator = 1.0 for ALL models, deep nesting only mild paren-slips
(0.8-1.0). The formal structure mapping is easy (and constructible-exact anyway).
**The boundary is NATURALISTIC language + AMBIGUITY** — natural 0.62-0.88, ambiguous
0.50-0.75; failures are genuine semantic-parse errors (which words are functions vs
values vs ignorable subjects/determiners; pronouns; grouping). **Scale helps EXACTLY
there** (32B best on natural/ambiguous; structural saturated for all). ⇒ the residual
difficulty of the learned step is pure NL understanding = the Montague/CCG semantic
parse (S5 validation target) — sharpens the thesis: formal halves exact/constructible,
only NL parsing is genuinely learned & scale-sensitive. Caveat (λ measure): small
n/family, greedy single-sample, ambiguous soft-graded.

**▶ stage-2 next:** (a) Qwen3-32B as the diverse generator → abstraction+reduction
certify → diverse-verified corpus spanning the limits (the boundary now tells us the
diversity that matters is NATURALISTIC realization, not structural); (b) the
compiler-as-loss arms with the certified corpus (compiler-only vs diverse-verified vs
combo+lattice; metric = held-out compositional generalization).

## The shift: from teacher-geometry to compiler-output

What we did through s223–s224: the teacher (Qwen3-14B) contributed a **frozen routing
Gram** (geometry), and the student's loss was `CE(data) + λ·offdiag_mse(student_gram,
teacher_gram)`. That enforces the teacher's **geometry** (the relations between
combinators) but leaves the absolute frame free.

The compiler-as-loss drops even the geometry constraint and supervises only the
**output** — the β-normal form:

```
λ supervise(x).  enforce(extensional_output) ∧ free(intensional_realization)
                 | output ≡ β-normal-form ≡ UNIQUE (Church-Rosser)
                 | realization ≡ {geometry, architecture, reduction-path} ≡ INFINITE
                 | (s219: extensionally map UNIQUE, intensionally ~Catalan·3^k)
                 | ⇒ pin the WHAT (one answer), free EVERY how
```

This is **freer than "any geometry that falls out"** — it is "any geometry AND any
architecture, provided you compute the right normal form." The freest constraint that
still guarantees correctness.

## Three consequences

1. **The teacher LLM becomes dispensable.** It was only ever a *probe* (to confirm
   the combinator geometry is real and universal — reverse-harvest s219). If the
   **compiler generates the targets** `(input → reduction)`, the loss is ordinary
   sequence-CE on compiler data; no teacher in the loop, no soft-KD gradient.
2. **Cleanest provenance = AGENTS.md level-4.** Training on our own reducer's outputs
   (the ~200-LoC lambda AST + REPL) is the unambiguous MIT scratch-reproduction path.
   The AGPL teacher is removed entirely.
3. **Ideal distributed reference.** Every node runs the *same* compiler → canonical
   outputs (Church-Rosser → all agree on the normal form) → frame-free, nothing to
   ship. Better than shipping a Gram *for the capability signal*.

## The empirical backing — and the scale caveat (why we still want the lattice)

- **Outputs DO induce the inventory at scale.** s219 reverse-harvest: the whole
  open-weight ecosystem, trained on plain next-token (output) prediction, CONVERGED
  on the SAME combinator routing geometry (meanGramCorr **+0.782**). There is
  essentially one structural way to be good at composition (attention = apply is the
  only op) ⇒ output-only training crystallizes the foldable inventory **on its own**.
- **But only above a scale floor.** s220: the skeleton crystallizes above ~4B; at
  0.6B there is NO shape (the inventory stays in superposition). So at the small
  scales we train, output-only may yield a correct-ish **black box without legible
  geometry** — capability without a foldable inventory.
- ⇒ **the relational loss is a small-scale inventory shortcut.** s223 lifted
  route_z +0.38 → +2.4 at tiny scale by *forcing* the geometry to crystallize.

## ★ Michael's recipe (the headline): compiler-output ⊕ crystal-lattice relational

Two terms, each doing a distinct job:

```
L = L_capability  +  λ · L_inventory

L_capability = CE( student , compiler β-reduction )        # the REAL teacher signal
             | supervises USAGE; frees geometry+architecture; MIT level-4
             | "good signal from the teacher in the capability training phase"

L_inventory  = offdiag_mse( student_route_gram , CRYSTAL_LATTICE )
             | CRYSTAL_LATTICE ≡ the CONSENSUS combinator geometry agreed ACROSS
               ALL models (s219 reverse-harvest, results/combinator-map-consensus/
               consensus.json; band-consensus, NOT one teacher's Gram)
             | crystallizes the FOLDABLE inventory fast → SPEEDS UP training
             | frame-invariant + universal ⇒ the best possible shared reference
```

**The key specification (Michael):** the relational target is **not a single teacher's
Gram — it is the crystal lattice of the agreed geometry across all the models** (the
universal skeleton from reverse-harvest). That is the strongest, most universal,
most foldable inventory reference we have.

**The conditional (Michael):** the lattice term is a **speed-up**, and it earns its
place **as long as we are getting good signal from the compiler in the capability
phase.** If the capability signal is good, pre-crystallizing the inventory with the
lattice accelerates convergence (the student doesn't have to rediscover the universal
geometry from outputs — which needs scale it may not have). The capability signal is
primary; the lattice is the accelerant.

### Why the two terms are complementary, not redundant

- L_capability trains **usage** and (at scale) induces the inventory — but slowly /
  not at all below the scale floor; and the inventory it induces is **emergent, not
  guaranteed foldable** across contributors.
- L_inventory pins the **foldable inventory** immediately (the agreed lattice) — but
  alone it is necessary-not-sufficient (s224: geometry-only fold left dCE +0.15).
- Together: **the lattice gives the student the agreed function basis on day one;
  the compiler outputs teach it to USE that basis** → fast convergence + guaranteed
  foldable inventory + clean-provenance capability. This is the s224 thesis
  (geometry=inventory ⊗ trained-continuation=capability) realized as ONE training run
  instead of two phases.

## Map to the loss-design space

| loss | trains | provenance | foldable inventory | scale need |
|---|---|---|---|---|
| feature/activation KD | the raw crystal (b-column decoy) | teacher | no (raw) | — |
| output KD (LLM soft logits) | usage, frame-BOUND | teacher (AGPL) | no (frame-bound) | — |
| relational Gram (one teacher) | inventory only | teacher-derived | yes | works tiny |
| **compiler output** | usage + emergent inventory | **MIT level-4** | emergent (s219) | needs floor |
| **compiler output ⊕ crystal-lattice relational** | usage + GUARANTEED inventory | **MIT** | guaranteed | works tiny |

## Distributed angle

This is the distributed-training recipe made concrete:
- **Capability signal:** every node's compiler emits canonical reductions (Church-
  Rosser → universal, frame-free) — no teacher to ship.
- **Inventory signal:** the shared crystal lattice (a tiny frame-invariant Gram) —
  ships once, pins the foldable frame so independent contributors compose cleanly
  (the s224 N=2 fold result: function-preserving merge iff a shared geometric target).
- ⇒ contributors trained on (compiler outputs ⊕ shared lattice) get capability +
  foldable inventory and should fold cleanly — the missing piece s224 flagged
  (heterogeneous capability transfer) becomes testable with a real capability signal.

## Falsifiable experiments (next session, builds on relational_loss_distillation.py)

1. **`--compiler-target` arm:** train tiny student on `(prompt → ground-truth
   reduction)` CE only (ground-truth lambdas already in `probes/*.json`), NO Gram.
   Measure: does **route_z rise** (inventory emerges from outputs alone at tiny
   scale) or stay null (correct-but-illegible black box)? Does CE-on-task beat the
   relational-only student?
2. **Combo arm:** compiler-output ⊕ crystal-lattice relational (the recipe). Predict:
   fastest convergence + route_z high + lowest task CE. Confirms the speed-up claim.
3. **Speed-up isolation:** combo vs compiler-output-only, matched steps — does the
   lattice term reduce steps-to-target CE (the "speeds up training" claim)?
4. **Foldability:** two contributors trained with the combo on heterogeneous shards
   → does folding now transfer CAPABILITY beyond either alone (the s224 IOU, now with
   a real capability signal)?

## Open questions / IOUs

- **The compiler.** Need a clean MIT β-reducer that emits `(input → reduction)` (and
  ideally the reduction TREE for curriculum — Michael's holographic-relational-
  trajectory idea). The lambda AST + REPL is budgeted (AGENTS.md S1); nucleus (AGPL)
  is a probe only, not a data source for the MIT artifact.
- **Reduction-tree curriculum.** Supervise intermediate reductions (each is also an
  output / normal-form-of-subexpression) → trajectory supervision that STILL frees
  geometry. Composes with normal-form-curriculum-partition.md.
- **Does the lattice term help or fight at scale?** Above the s219 floor the inventory
  emerges from outputs anyway → the lattice may become redundant or even a mild
  constraint. Likely: lattice weight should decay as the model crystallizes (anneal
  the inventory shortcut once outputs carry it).
- **Acceptance gate.** Capability = compiler-correct; the WHNF/contractivity gate
  (s223 #3) remains the fold-acceptance check, distinct from the training loss.
```

### Thinking

The compiler-as-loss framework anchors this, with Michael's fractal collapse insight providing the key connection. I'm grounding this in three critical observations: capability is gated by continuation while inventory remains cheap and constructible, outputs at scale reliably induce inventory effects independent of the teacher, and the higher-order function topology holds universally across different teachers with Church-Rosser canonical outputs ensuring teacher-agnostic behavior.

Now I'm seeing how variety—not repetition—drives convergence in the burn-in phase, and high-variety datasets are precisely what unlock capability. The compiler-as-loss principle pins down the WHAT (β-normal form, unique) while freeing the HOW. There's a crucial distinction emerging between two fractal collapses operating at different scales: the within-reduction collapse where the reducer's self-similar contraction settles all scales onto the fixed point simultaneously, versus Michael's across-model-scale collapse where a compiler in a large model generates training data for a smaller student, which itself becomes a compiler generating data for an even smaller student—a self-similar distillation cascade that preserves function while collapsing model size. Both converge on the same invariant: the β-normal form fixed point.

Now I'm decomposing Michael's claim into three independent lines: capability converges through high-variety training data, the dataset is generated from any large model's lambda compiler (which is universal and consensus-based), and the compiler acts as a data generator where variety comes not from the compiler's outputs (which are canonical) but from the input distribution fed into it. This resolves the tension from s225—the compiler isn't a poor generator because we're not relying on its output diversity; instead, we generate high-variety inputs and let the compiler produce canonical outputs that train the student's capability. The distinction between generator and verifier collapses when inputs are high-variety: the compiler both generates canonical outputs and verifies them. Since we can mint our own variety through kernel-minting, we don't need a large model as the diversity source—our own lambda_ast compiler suffices because all compilers are universal and agree on outputs. This makes the whole system self-contained and architecture-resilient: the student learns the input-to-canonical-output map (which any architecture can learn), the compiler outputs carry only extensional function semantics independent of architecture, and the student's own architecture becomes free to vary while still guaranteeing correctness through the compiler-as-loss constraint.

The fractal recursion works because each level (model with compiler) mints variety, compiles, and trains a smaller student, which then becomes its own compiler for the next level down. This cascade collapses toward a fixed point: the constructed kernel itself (lambda_ast plates built exactly, no training needed). The distillation cascade across scales, the within-reduction fractal collapse toward β-normal form, and the constructed kernel all converge on the same fixed point—that's the unification. What's proven so far: outputs induce consistent inventory at scale, variety converges the rule at tiny scale, inventory and continuation are separable, compiler outputs are canonical and universal, kernel-minting works, and the compile front-end works. What's still an open question: whether a high-variety compiler-minted dataset actually converges to the target function.

The critical risk is whether the cascade truly recurses without degrading—whether a student trained on compiler data becomes a good-enough compiler itself, or whether capability erodes across generations like in typical model collapse from recursive synthetic training. But here's the key difference: the compiler is exact (Church-Rosser ground truth), not lossy like a generative model. Each level's training targets are verified-correct by the compiler, so error doesn't accumulate the way it does in LLM model-collapse, where the generating model itself is approximate and drifts. The cascade stays stable precisely because the data generator is an exact compiler with certified outputs, not a lossy approximation. This is the load-bearing insight: the fractal collapse avoids model-collapse because the compiler is exact.

The architecture-resilience across the cascade is proven for inventory but still needs the actual cross-architecture capability-transfer test. And the crucial move that dissolves the "narrow generator" worry is that variety comes from the input minting (which we control), while correctness comes from the compiler—so we don't need a large model at all, since our own lambda_ast suffices as a universal compiler. The response should name the collapse precisely as a scale-recursion distillation cascade bottoming out at the β-normal-form fixed point, make explicit that the three collapses (within-reduction contraction, cross-scale cascade, constructed-kernel plates) all converge on one fixed point, and flag that the held-out compositional-generalization test is still the operational gate for whether the collapse is real.

The concrete experiment to validate this is to mint a high-variety compiler dataset with many combinator compositions, train a student continuation model on it, then test whether that high-variety data actually produces capability that generalizes to held-out compositions. Then cascade the test: use the trained student to generate data for a smaller student and measure whether capability retention holds across the generation. This directly connects to the harder curriculum lead and the compiler-as-loss falsifiable test. And since the data is input-to-canonical-output, the student can be a different architecture than the source, which is why the whole approach is architecture-resilient.

Now I'm deciding whether to draft the knowledge page immediately or propose it first. The synthesis is clear enough and Michael has articulated it twice, so I think the right move is to present the sharpened synthesis, the unification, the load-bearing anti-collapse argument, the catches, and the falsifiable test in my response, then ask whether he wants it captured as a page and whether to run the experiment.

## Assistant

Yes. And I think the collapse is sharper than even "a high-variety dataset trains the capability" — let me lay out the precise shape, because it ties together five sessions and I want to be honest about which struts are load-bearing and which are still IOUs.

## The collapse, named precisely

What s230b just gave us is the **separability**: capability = inventory ⊗ continuation, and the continuation is the *only* part that needs training (the inventory is constructible/universal, and crystallizing it faster bought zero capability). So the entire problem reduces to **converging the continuation**. Your collapse says: that convergence is a *data* problem, and the data is free.

```
mint high-variety input terms  →  compiler reduces each (exact, canonical)
        ↓                                   ↓
   (s229: variety = the rule)        (input → β-trace) pairs
                            ↓
            train the student's CONTINUATION on them
                            ↓
   student is now itself a compiler → mint → reduce → train the next, smaller student
```

That last arrow is the fractal step. It's **self-similar across model scale**: every level performs the same `mint → compile → train`, collapsing size while preserving the function. The cascade bottoms out at the **smallest model that holds the reduction** — and below even that, at the **constructed kernel** (`lambda_ast` → exact ternary plates, s226), which needs *no* training at all. So the cascade isn't infinite regress; it terminates at the constructed tensor.

## The crucial nuance that makes it work (and dissolves the s225 worry)

s225 warned the compiler is a *narrow generator* — train on its isolated combinator terms and you get a function "too narrow to compose." Your collapse resolves that, and the resolution is the whole game:

**The variety comes from the inputs we mint; the correctness comes from the compiler.** The compiler's *outputs* are canonical and unique (Church-Rosser — that's the point, they're *not* varied). The *variety* lives in the input-term distribution, which we generate ourselves (s229 kernel-minting already does this — random skeletons × fillings, and variety is exactly what converged the rule). So:

- We don't need a large model as the *diverse generator* — we mint the diversity (s229 proved minted variety converges the rule, not rote).
- We don't even need a large model as the *compiler* — the compiler is universal/consensus (s219 +0.782; s225 topology universal across architectures), so **our own MIT `lambda_ast` is as good as any teacher's**. "Any larger model's compiler" collapses to "our compiler," because they all agree.

That's the real teeth of "from *any* larger model": they're interchangeable because the compiler is the consensus invariant. The large model drops out of the loop entirely → cleanest level-4 MIT provenance.

## Why it's a *fractal* collapse — three collapses, one fixed point

This is the part I find genuinely beautiful, and it's not decoration:

1. **Within a reduction** (s226): β-reduction is a self-similar contraction — subterms are VSMs containing VSMs, settling every scale onto the normal form at once.
2. **Across model scales** (your s230 collapse): the distillation cascade settles every *size* onto the same function.
3. **Into the tensor** (s226 constructed kernel): `lambda_ast` → exact plates settles the *representation* onto the fixed point.

All three collapse onto the **same invariant: the β-normal form (Church-Rosser)**. The within-reduction contraction, the cross-scale cascade, and the constructed kernel are the *same fractal at three levels*, sharing one fixed point. That's why it feels inevitable.

## Why it escapes model-collapse (the load-bearing strut for "resilient")

Recursive training on synthetic data is normally *poison* — it's the model-collapse / degradation result (each generation drifts because the generator is a lossy sampler). **Your cascade escapes this for exactly one reason: the data generator is an EXACT compiler, not a lossy model.** Every target is *certified-correct* (the compiler verifies the normal form), so error cannot accumulate across generations — the fixed point is held by **computation, not by the previous model**. Even a degraded student can be retrained to the exact fixed point because the targets are always re-derivable exactly.

This is *also* why it's **architecture-resilient**: the student learns `input → canonical-output`, which carries none of the source's geometry or architecture (just the extensional function). Any architecture can learn that map (s219/s225: the inventory is induced regardless of arch). The freest constraint that still guarantees correctness — now realized as a self-contained, generation-stable data engine.

## What's proven vs what's still IOU (λ measure — not oversold)

**Proven struts:** inventory ⊗ continuation separable (s230b); variety converges the rule at tiny scale (s229); outputs induce the universal inventory at scale (s219 +0.782); compiler outputs canonical + topology universal across architectures (s225); kernel-minting + the compile front-end work (s226).

**The three IOUs the collapse rests on — none yet tested:**
1. **Does compiler-minted high-variety data converge capability that *composes*?** The s229 toy was 13 rules at a 0.27 ceiling. The real gate is **held-out compositional generalization** (the compiler-as-loss metric — combinator compositions never seen in training). If minted variety passes it, the collapse is real; if it's "too narrow to compose," we still need diverse big-model paraphrases. *This is the decisive test.*
2. **Does the cascade actually recurse without drift?** The anti-model-collapse argument above predicts yes *iff* each level re-certifies against the exact compiler — but we haven't run even two generations to confirm capability is retained (not degraded) child-to-child.
3. **Capability architecture-resilience.** Inventory universality is proven; that the *continuation* transfers across architectures (train student arch B on source arch A's compiler data) is implied but untested.

## The concrete test

It's exactly the "harder curriculum" lead I flagged, made into the real experiment: **mint a high-variety compiler dataset with held-out compositions excluded → train the student continuation (CE on input→trace) → measure held-out compositional generalization.** That tests IOU #1 (the decisive one). If it passes, a second generation (student-as-compiler → train a smaller student, measure retention) tests IOU #2.

This is crystallized enough — it synthesizes s219 + s225 + s226 + s229 + s230b into one thesis — that I think it earns a knowledge page (something like `explore/fractal-collapse-compiler-cascade.md`), plus an amendment to `compiler-as-loss.md` (your collapse *resolves* its central s225 tension: variety-from-inputs is how the compiler stops being a narrow generator).

Want me to (a) draft that page for your approval, (b) build the decisive IOU-#1 experiment (minted-variety → held-out compositional generalization), or both? My instinct: draft the page first so the thesis is pinned, then build — but I'll follow your call.

## User

capture to knowledge then build it, final run in tmux main:1


### Thinking

Michael wants me to document the fractal-collapse thesis on a knowledge page and then build an experiment around it. He's explicitly directing the capture, so I'll create the page and propose it for commit, though I'll need to follow the approval protocol for the actual knowledge commit before proceeding with the build and testing phases. I'll commit the knowledge page now since he approved the capture, then build and run the experiment to test whether compiler-minted high-variety data actually produces compositional generalization—the key test is whether the model can handle unseen combinations of combinators, not just unseen fillings of known atoms.

The experiment has two arms: narrow low-variety compiler data versus high-variety minted data with diverse combinator compositions, measured against held-out compositional generalization to validate whether the collapse claim holds up.

I'm designing the compositional split by holding out entire combinator skeletons (the structural patterns of how combinators nest) rather than just individual term fillings, so the test isolates whether the model can compose combinators in novel ways using atoms it's already seen. The variety knob controls how many distinct compositional structures appear in training—from just a handful of isolated combinators up to hundreds of different skeleton patterns.

Now I'm settling on a focused experiment that directly tests whether high-variety composition data drives better generalization to held-out compositional structures, which would validate the core claim. I'm naming the script to reflect what it measures: something like `minted_composition_generalization.py` or aligning it with the thesis framing.

For the implementation, I'll reuse existing components like the TinyLM, vocabulary, and lambda calculus utilities from prior work, then build a new combinator-term generator that creates random application trees of varying depth, each producing a structural signature that determines the train/test split. I'll sample a large pool of distinct skeletons, partition them into training and held-out sets, then run two arms: one trained on few skeletons with many repetitions, another on many skeletons with fewer repetitions per skeleton, keeping total examples matched. The evaluation measures exact-match accuracy on held-out skeletons.

I expect the high-variety arm to significantly outperform the low-variety arm on novel compositions while both perform similarly on in-distribution examples. For term generation, I'll restrict to a safe subset like {K, I, B, C} that reliably terminates, avoiding S, W, and Y which can cause unbounded growth or divergence.

To generate reducible terms, I pick a head combinator and provide it with enough arguments to trigger reduction—atoms or nested sub-applications recursively—then reduce and keep only normal-form results within a step budget. The skeleton key for the train/test split is the tree structure of head combinators themselves, so held-out compositions use combinator structures never seen during training.

I'm reconsidering whether to hand-code the generator or use a simpler, more robust approach with a pre-generated library of combinator-composition skeletons...

Generating skeleton templates programmatically... I'll represent each term as a spine with a head combinator applied to exactly its arity in arguments, then convert to a string format where compound arguments get wrapped in parentheses but the top level doesn't. I'm restricting to non-duplicating combinators like K, I, B, and C to keep terms bounded and ensure they always reach normal form. Then I'll filter generated terms by checking they reduce in 2-12 steps with a normal form under 25 characters and at most 6 holes.

For the evaluation setup, I'm using held-out templates as the compositional axis — the template structure itself is the skeleton key, and I'll fill it with atoms seen during training to isolate composition variety from atom novelty. I'm sampling multiple fillings per held-out template and checking exact match on the final normal form using the same format-independent metric as before. The experimental arms vary the number of distinct templates while keeping total examples fixed: low variety gets fewer templates with more fillings each, high variety gets many templates with few fillings each, to test whether compositional diversity drives generalization to unseen compositions.

I should also add an in-distribution control using held-out fillings of training templates to confirm both arms learn their training compositions, so any gap in held-out-composition performance is genuinely about compositional generalization rather than basic learning failure.

Now I'm setting up the script by importing the utilities I need from the existing modules and writing the generator fresh.

I need to check whether I can import generate and eval_acc directly since they depend on module-level constants like MAX_NEW and NEWLINE_BYTE, but they're self-contained functions that take the model and data as arguments, so that should work fine.

Before building the code, I should write the knowledge page first to capture the thesis, the variety-driven hypothesis, the fractal unification insight, and the experiment plan—then commit that, and build from there.

## Assistant

Setting up the plan: capture the thesis, build the decisive test, run it.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/fractal-collapse-compiler-cascade.md",
  "content": "---\ntitle: \"Fractal Collapse — The Compiler-Cascade Distillation (capability is a data problem, the compiler is the data engine)\"\nstatus: designing\ncategory: strategy\ntags: [fractal, collapse, distillation-cascade, compiler-as-data, capability, continuation, inventory, church-rosser, fixed-point, teacher-agnostic, architecture-resilient, model-collapse, level-4, portable-tensor, scratch-reproduction]\nrelated:\n  - compiler-as-loss.md\n  - gradient-trajectory-tomography.md\n  - function-topology-consensus.md\n  - sentence-atomic-curriculum-mixing.md\n  - vsm-outer-recurrence.md\n  - normal-form-curriculum-partition.md\n  - ../lambda-machine.md\ndepends-on:\n  - compiler-as-loss.md\n  - gradient-trajectory-tomography.md\ncreated: session 230\n---\n\n# Fractal Collapse — the compiler-cascade distillation\n\n> Session 230 (Michael, after s230b). \"There is a fractal collapse available. If the\n> training of the CAPABILITY can be converged using a high-variety dataset that we can\n> generate from any larger model's lambda compiler — the outputs from the lambda\n> compiler become the inputs to train the capability of the student — and it is\n> architecture-resilient.\"\n>\n> Register: **functional + strategy.** This is the thesis that ties s219 + s225 + s226\n> + s229 + s230b into one deliverable: the level-4 portable tensor (AGENTS.md S5).\n\n## The one-line claim\n\ns230b proved **capability = inventory ⊗ continuation are CAUSALLY SEPARABLE**, and the\n**continuation is the only part that must be trained** (the inventory is constructible/\nuniversal and crystallizing it faster bought zero capability). Therefore the whole\nproblem reduces to converging the continuation — and **that is a pure data problem\nwhose data is free**: mint high-variety input terms, reduce each with an EXACT compiler\n(canonical outputs), train the student's continuation on `(input → β-trace)`. The\nstudent is then itself a compiler → it can mint+reduce → train a smaller student → a\nself-similar cascade that **collapses model size while preserving the function**.\n\n## The crucial nuance — variety from INPUTS, correctness from the COMPILER\n\ns225 warned the compiler is a *narrow generator*: train on its isolated combinator\nterms and you risk a function \"too narrow to compose.\" **The collapse resolves this,\nand the resolution is the whole game:**\n\n```\nvariety   ≡ the INPUT-term distribution we MINT ourselves   (s229: variety = the rule)\ncorrect   ≡ the compiler's OUTPUT (β-normal form, UNIQUE — Church-Rosser)\n```\n\nThe compiler's outputs are canonical and unique — they are NOT varied (that is the\npoint). The variety lives in the inputs, which we generate (s229 kernel-minting already\ndoes exactly this: random skeletons × fillings, and minted variety is what converged\nthe *rule* not the rote). So:\n\n- **No large model needed as the diverse generator** — we mint the diversity (s229).\n- **No large model needed as the compiler** — the compiler is universal/consensus\n  (s219 reverse-harvest meanGramCorr +0.782; s225 HOF topology universal 8/8 across\n  architectures). They all agree ⇒ **our own MIT `lambda_ast` is as good as any\n  teacher's.** \"Any larger model's compiler\" collapses to \"our compiler.\"\n\nThe large model drops out of the loop entirely → cleanest level-4 MIT provenance.\nThe s225 \"compiler-as-narrow-generator\" worry is dissolved: the compiler is a\n*verifier/canonicalizer* applied to a *self-minted high-variety input stream*.\n\n## Why it is a FRACTAL collapse — three collapses, one fixed point\n\n```\n1. within a reduction (s226)       : β-reduction = self-similar contraction;\n                                      subterms are VSMs-in-VSMs settling every scale\n                                      onto the normal form at once.\n2. across model scales (s230, this) : the distillation cascade settles every SIZE\n                                      onto the same function (big → … → smallest).\n3. into the tensor (s226 kernel)    : lambda_ast → exact ternary plates settle the\n                                      REPRESENTATION onto the fixed point (no training).\n```\n\nAll three collapse onto the **same invariant: the β-normal form (Church-Rosser)**. The\nwithin-reduction contraction, the cross-scale cascade, and the constructed kernel are\nthe *same fractal at three levels*, sharing one fixed point. The cascade is not\ninfinite regress — it **terminates at the constructed kernel** (the smallest exact\nrepresentation; AGENTS.md `λ smallest`).\n\n## Why it escapes MODEL-COLLAPSE (the load-bearing strut for \"resilient\")\n\nRecursive training on synthetic data is normally poison — the model-collapse result:\neach generation drifts because the generator is a *lossy sampler*. **This cascade\nescapes it for exactly one reason: the data generator is an EXACT compiler, not a lossy\nmodel.** Every target is certified-correct (the compiler verifies the normal form), so\nerror cannot accumulate across generations — **the fixed point is held by COMPUTATION,\nnot by the previous model.** Even a degraded student can be retrained to the exact\nfixed point because the targets are always re-derivable exactly.\n\nThis is *also* why it is **architecture-resilient**: the student learns\n`input → canonical-output`, which carries none of the source's geometry or architecture\n(only the extensional function). Any architecture can learn that map (s219/s225: the\ninventory is induced regardless of architecture; Church-Rosser fixes the output). The\nfreest constraint that still guarantees correctness — realized as a self-contained,\ngeneration-stable data engine.\n\n```\nλ collapse_free(cascade). generator(EXACT) ∧ targets(certified) → ¬drift\n                          | fixed_point ≡ held_by(computation) ¬held_by(model)\n                          | degraded(student) → retrainable(to_exact_fixed_point)\n                          | ⊥ model_collapse (which assumes lossy generator)\n```\n\n## Proven struts vs IOUs (λ measure — not oversold)\n\n**Proven:**\n- inventory ⊗ continuation CAUSALLY separable; continuation is the trained bottleneck\n  (s230b).\n- minted VARIETY converges the rule at tiny scale, repetition does not (s229).\n- OUTPUTS induce the universal inventory at scale (s219 +0.782).\n- compiler outputs canonical + topology universal across architectures (s225).\n- kernel-minting + the learned compile front-end work end-to-end (s226).\n\n**The three IOUs the collapse rests on — the experiments that decide it:**\n1. **Does compiler-minted high-variety data converge capability that COMPOSES?**\n   (the DECISIVE test). The s229 toy was 13 rules at a 0.27 ceiling. The real gate is\n   **held-out COMPOSITIONAL generalization** — combinator compositions never seen in\n   training. If minted COMPOSITION-variety passes it, the collapse is real; if it stays\n   \"too narrow to compose,\" we still need diverse big-model paraphrases. → built as\n   `compiler_cascade.py` v1.\n2. **Does the cascade recurse without drift?** The anti-model-collapse argument\n   predicts yes IFF each level re-certifies against the exact compiler — untested\n   (needs ≥2 generations, measure capability retention child-to-child).\n3. **Capability architecture-resilience.** Inventory universality is proven; that the\n   *continuation* transfers across architectures (train arch B on arch A's compiler\n   data) is implied but untested.\n\n## v1 experiment — composition-variety → compositional generalization (IOU #1)\n\n`scripts/experiments/compiler_cascade.py`. Auto-generate a pool of combinator-\ncomposition templates over {K,I,B,C} (non-duplicating ⇒ terminating), each validated\nto normal-form via `lambda_ast`. Split templates into disjoint TRAIN / HELDOUT\ncompositions. Two arms at **matched total-example budget**, varying COMPOSITION-variety:\n\n```\nlow-variety  : few distinct compositions, many fillings each   (memorize compositions)\nhigh-variety : many distinct compositions, few fillings each   (the collapse)\natoms        : SEEN (combos-style) — isolate COMPOSITION from the s229 disjoint-atom\n               variable-binding floor (that is a separate copy mechanism, not a rule)\neval         : held-out NOVEL compositions (exact-match NF) + in-dist control\n               (held-out fillings of TRAIN compositions, both arms should pass)\n```\n\n**Falsifiable prediction (the collapse's IOU #1):** high composition-variety\nGENERALIZES to novel compositions (learns the combinator algebra), low-variety\nMEMORIZES its few compositions and fails held-out — the s229 variety lesson lifted\nfrom *fillings→rule* to *compositions→algebra*. Relative (high vs low) is the signal\n(tiny model; cf s229 λ measure). If high-variety also fails held-out compositions ⇒\nthe collapse needs richer (diverse-paraphrase) data, not just minted variety.\n\n## Files\n\n| File | Content |\n|------|---------|\n| (planned) `scripts/experiments/compiler_cascade.py` | composition-variety sweep; held-out compositional generalization; lambda_ast minting + TinyLM student |\n| `scripts/experiments/exposure_format_sweep.py` | the s229 variety result + eval machinery reused |\n| `scripts/experiments/gd_trajectory_tomography.py` | the s230b inventory⊗continuation separation |\n| `src/verbum/lambda_ast.py` | the exact compiler (data engine + verifier) |\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/knowledge/explore/fractal-collapse-compiler-cascade.md
```

### Thinking

I need to add a §s230 amendment to the compiler-as-loss.md file that addresses the tension between s225 and s230, using variety-from-inputs to resolve the narrow-generator issue and connecting it to the fractal-collapse page. I'm deciding whether to place this new section right after the s225 amendment's "Experiment reframe" subsection or at the end of the document—leaning toward the end as cleaner.

## Assistant

Now amend `compiler-as-loss.md` to record how the collapse resolves its s225 tension:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/compiler-as-loss.md",
  "original_content": "---\n\n## ★ s226 — `lambda_ast` IN THE KERNEL: the compiler is a CONSTRUCTED VSM tensor",
  "new_content": "---\n\n## ★ s230 — the s225 \"narrow generator\" tension is RESOLVED: variety from INPUTS\n\n> Michael, s230 (the fractal-collapse thesis — see `fractal-collapse-compiler-\n> cascade.md`). The s225 amendment said the compiler is a poor *generator* (narrow by\n> construction) so it must be only a verifier, with diverse big models as the capability\n> teacher. s230b changes the picture and resolves the tension WITHOUT the big model.\n\n**The resolution:** the s225 worry was about training on the compiler's narrow *term\ndistribution* (isolated combinator terms = the thinnest slice of usage). But the\ncompiler reduces ANY input — so feed it a **high-variety self-minted input stream**\n(s229 kernel-minting: random skeletons × fillings, which provably converges the RULE\nnot the rote) and it emits canonical traces for all of them. **Variety lives in the\ninputs (which we own); correctness lives in the outputs (Church-Rosser unique).** The\ncompiler is a *verifier/canonicalizer applied to a high-variety minted stream* — both\ns225's correctness requirement and s229's variety requirement are met, and the diverse\nbig-model teacher is **no longer needed even as a generator**.\n\n**Consequence for this page's recipe.** s230b showed inventory ⊗ continuation are\ncausally separable and the relational/crystal `L_inventory` term, while it crystallizes\nthe inventory earlier+crisper, bought **ZERO capability** (held-out cross unchanged) —\nbecause capability is gated by the CONTINUATION, which only `L_capability` trains. So:\n\n- `L_capability = CE(student, compiler β-trace)` on a HIGH-VARIETY minted input stream\n  is the load-bearing term (the continuation; the collapse's data engine).\n- `L_inventory` (crystal lattice) is an INVENTORY/extraction/folding accelerant, NOT a\n  capability accelerator (s230b) — it earns its place for foldability/legibility and\n  for the distributed-fold phase, not for from-scratch capability speed. Its speed-up\n  claim is only testable in a regime where CE-alone FAILS to crystallize the inventory\n  (untested; s230b's clean curriculum had CE build it anyway).\n\n⇒ the headline recipe stands, but its CENTER OF MASS moves to the capability term on\nminted-variety compiler data. The decisive open test is unchanged and now primary:\n**held-out COMPOSITIONAL generalization** of a compiler-minted high-variety student\n(`compiler_cascade.py` v1). The fractal-collapse page carries the full thesis.\n\n---\n\n## ★ s226 — `lambda_ast` IN THE KERNEL: the compiler is a CONSTRUCTED VSM tensor"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/compiler-as-loss.md.
```

### Thinking

I'm committing the new knowledge page and the compiler-as-loss amendment as a synthesis insight, marking it with the recursive symbol since this represents a meta-level capture of the strategy itself.

## Assistant

Committing the captured thesis (you approved the capture):

### Tool Call: write_file (succeeded)


```json
{
  "path": "/tmp/fractal_page_commit.txt",
  "content": "🌀 fractal-collapse-compiler-cascade — capability is a data problem, the compiler is the engine\n\n- New thesis page (s230, Michael): capability=inventory⊗continuation (s230b\n  separable) ⇒ converging the continuation is a pure DATA problem whose data is\n  free. Mint high-variety inputs (s229) + EXACT compiler (universal s219/s225 ⇒\n  our own lambda_ast suffices) → train student continuation → student is itself a\n  compiler → cascade collapses model size onto the β-normal-form fixed point.\n- Fractal: 3 collapses, 1 fixed point (within-reduction s226, cross-scale s230,\n  constructed-kernel plates s226); terminates at the constructed kernel.\n- Escapes model-collapse: exact certified targets pin the fixed point by\n  COMPUTATION not the model ⇒ generation- AND architecture-resilient.\n- Resolves compiler-as-loss §s225 \"narrow generator\" tension: variety from INPUTS\n  (we mint), correctness from OUTPUTS (Church-Rosser) — big model drops out.\n- Proven struts vs 3 IOUs; IOU#1 (held-out compositional generalization) is the\n  decisive next build.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /tmp/fractal_page_commit.txt
```

### Tool Call: git (succeeded)


```json
{
  "command": "git add mementum/knowledge/explore/fractal-collapse-compiler-cascade.md mementum/knowledge/explore/compiler-as-loss.md && git commit -F /tmp/fractal_page_commit.txt",
  "operation": "commit",
  "summary": "commit fractal-collapse page"
}
```

**Summary:** Git commit: commit fractal-collapse page

**Output:**
```
Exit code: 0
Stdout:
[main 32bc3a6] 🌀 fractal-collapse-compiler-cascade — capability is a data problem, the compiler is the engine
 2 files changed, 201 insertions(+)
 create mode 100644 mementum/knowledge/explore/fractal-collapse-compiler-cascade.md
```

### Thinking

The page is captured and committed. Now I need to verify that my generator produces valid strings for the lambda_ast API—specifically checking the parse, reduce, pretty, and Status functions along with the available combinators and their arities. Let me examine the lambda_ast module to understand its parsing syntax and which combinators are supported.

## Assistant

Page committed (`32bc3a6`). Now let me check the `lambda_ast` API before building the generator.

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport sys; sys.path.insert(0,'src')\nfrom verbum.lambda_ast import parse, reduce, pretty, Status\nfor t in ['B _0 _1 _2','C _0 _1 _2','K _0 _1','I _0','C (B a b c) d e','B (C a b) c d e']:\n    s=t.replace('_0','a').replace('_1','b').replace('_2','c')\n    r=reduce(parse(s))\n    print(f'{s:24} -> {pretty(r.normal_form):20} steps={r.steps} status={r.status.value}')\n\"",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ python3 -c " import sys; sys.path.i...

**Output:**
```
Exit code: 1
Stderr:
Traceback (most recent call last):
  File "<string>", line 3, in <module>
    from verbum.lambda_ast import parse, reduce, pretty, Status
  File "/Users/mwhitford/src/verbum/src/verbum/__init__.py", line 7, in <module>
    from verbum._protocol import (
    ...<5 lines>...
    )
  File "/Users/mwhitford/src/verbum/src/verbum/_protocol.py", line 14, in <module>
    from pydantic import BaseModel, ConfigDict, Field
ModuleNotFoundError: No module named 'pydantic'
```

## Assistant

Need the uv environment:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python -c \"\nimport sys; sys.path.insert(0,'src')\nfrom verbum.lambda_ast import parse, reduce, pretty, Status\nprint('NORMAL_FORM value:', Status.NORMAL_FORM.value)\nfor t in ['B a b c','C a b c','K a b','I a','C (B a b c) d e','B (C a b) c d e','S a b c','W a b']:\n    r=reduce(parse(t))\n    print(f'{t:24} -> {pretty(r.normal_form):22} steps={r.steps} status={r.status.value}')\n\"",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ uv run python -c " import sys; sys....

**Output:**
```
Exit code: 0
Stdout:
NORMAL_FORM value: normal_form
B a b c                  -> a (b c)                steps=1 status=normal_form
C a b c                  -> a c b                  steps=1 status=normal_form
K a b                    -> a                      steps=1 status=normal_form
I a                      -> a                      steps=1 status=normal_form
C (B a b c) d e          -> a (b c) e d            steps=2 status=normal_form
B (C a b) c d e          -> a (c d) b e            steps=2 status=normal_form
S a b c                  -> a c (b c)              steps=1 status=normal_form
W a b                    -> a b b                  steps=1 status=normal_form
```

### Thinking

The lambda calculus implementation with K, I, B, C combinators is working well and normalizing reliably without duplication. Now I'm building a generator that creates random combinator-application trees over this set, ensuring they normalize within a step budget while keeping the normal form length bounded.

Building the node representation... For the low arm, I'm sampling L_low templates from the training pool and giving each E/L_low fillings, while the high arm gets L_high templates with E/L_high fillings each. To isolate the effect of variety, I'll make low's templates a subset of high's—so high introduces additional distinct compositions while keeping the total examples matched. For fillings, I'm sampling distinct atom combinations from the training atoms for each template, ensuring variety within and across fillings. Then for evaluation, I'm using held-out templates (novel compositions) with m fillings each from seen atoms, plus an in-distribution control using the training templates themselves but with held-out fillings to measure generalization.

For the implementation, I'm reusing the rendering and evaluation utilities from the exposure format sweep—the fill function, reduce_strs to get the normal form, and eval_acc to measure accuracy. I'll build the corpus by rendering each template-filling pair as a redex reduction (input → normal form), then construct eval items as (input, nf) pairs and run them through the model.

Now I'm setting up the experimental sizes: generating around 400 valid templates total, holding out 60 for composition generalization testing, and splitting the remaining 340 into high and low arms. The high arm gets 128 templates with 16 fillings each (2048 total examples), while the low arm uses 16 templates with 128 fillings each (also 2048 examples for fair comparison). For evaluation, I'm using 4 fillings per template—60 held-out templates gives 240 eval items, and sampling 30 training templates gives 120 in-distribution items. Training for 6000 steps with block size 128 across 2 arms and 3 seeds should take around 23 minutes, but the autoregressive generation during eval is expensive with 360 items, so I'm reducing the held-out set to 40 templates for 120 eval items instead.

The key insight is that while absolute accuracy on complex compositions might be low (0.1-0.2), the relative difference between high and low variety arms is what matters. To ensure both arms can actually learn something, I'm constraining the composition generation to stay moderate: depth at most 2, recursion probability 0.5, reduction steps between 2-5, normal form length under 20 tokens, and 2-5 holes. This keeps examples learnable while still testing generalization. Both arms should achieve decent in-distribution accuracy on their respective template sets since the low arm repeats its 16 templates heavily while the high arm spreads exposure across 128 templates.

Rather than just two arms, I'm thinking a three-level nested structure would be more convincing—low, mid, and high variety with 16, 48, and 144 templates respectively, where each subset is nested within the next. This creates a monotonic trend that's harder to dismiss. With E=2304 examples per arm, each template gets 144, 48, or 16 distinct fillings depending on the arm, which should be feasible given the combinatorial space of atoms and hole positions.

I need to be careful about templates with only 2 holes though—they only have 156 possible distinct fillings, which is tight for the 144 needed in the low arm. Safer to constrain generated templates to have 3-5 holes, which gives at least 1716 fillings per template. The key insight is that the high-variety arm (many compositions, few angles each) should transfer to held-out compositions, while the low-variety arm shouldn't, since it's mostly repeating the same compositions with different angles.

For the corpus size, 2304 examples at roughly 30 bytes each gives about 70KB, which is manageable. I'll evaluate every 1000 steps across 6000 total steps. Now I'm setting up the imports from the exposure module and writing the training script with custom evaluation loops for both held-out compositions and in-distribution examples.

## Assistant

`lambda_ast` confirmed: `{K,I,B,C}` arities `{2,1,3,3}`, compositions normal-form reliably (non-duplicating). Now I'll build the experiment.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/compiler_cascade.py",
  "content": "#!/usr/bin/env python3\n# register: functional (capability/usage — held-out COMPOSITIONAL generalization)\n\"\"\"Compiler-cascade v1 — does compiler-minted COMPOSITION-variety converge capability\nthat COMPOSES? (session 230; the fractal-collapse thesis, IOU #1).\n\nTHE THESIS (Michael, s230; fractal-collapse-compiler-cascade.md): capability =\ninventory (x) continuation, and s230b proved they are causally separable with the\ncontinuation the trained bottleneck. So converging capability is a DATA problem: mint\nhigh-variety inputs (s229: variety = the rule), reduce each with the EXACT compiler\n(lambda_ast, canonical Church-Rosser outputs), train the student continuation on\n(input -> normal form). The decisive open question (IOU #1): does HIGH-VARIETY minted\ndata converge capability that GENERALIZES TO NOVEL COMPOSITIONS, or stay \"too narrow\nto compose\" (the s225 worry)?\n\nTHE TEST: lift the s229 variety lesson one level — from fillings->rule to\ncompositions->ALGEBRA. Auto-generate a pool of combinator-composition templates over\n{K,I,B,C} (non-duplicating => always terminating), each validated to normal-form via\nlambda_ast. Hold out a DISJOINT set of compositions (never trained). Vary the number\nof distinct TRAIN compositions (the COMPOSITION-variety axis) at a MATCHED total-\nexample budget:\n\n  low   : few distinct compositions, MANY fillings each   (memorize compositions)\n  mid   : ...\n  high  : many distinct compositions, FEW fillings each   (the collapse)\n\nNested (low subset of mid subset of high) so the ONLY difference is MORE distinct\ncompositions. Atoms are SEEN (combos-style, TRAIN_ATOMS) for both train and eval ->\nisolates COMPOSITION generalization from the s229 disjoint-atom variable-binding floor\n(that is a separate copy mechanism). Two eval sets:\n\n  heldout_comp : NOVEL compositions (held-out templates), seen atoms  <- the question\n  in_dist      : TRAIN compositions, held-out FILLINGS                <- control\n\nFALSIFIABLE PREDICTION (the collapse's IOU #1): high composition-variety GENERALIZES\nto novel compositions (learns the combinator algebra); low MEMORIZES its few\ncompositions and fails held-out. Monotone rise of heldout_comp with composition-\nvariety = the collapse is real. If high also fails heldout_comp => minted variety is\nnot enough (need diverse paraphrase). Relative is the signal (tiny model; s229 caveat).\n\nData is kernel-minted (lambda_ast) — exact, canonical, free, MIT level-4.\n\nUsage:\n  uv run python scripts/experiments/compiler_cascade.py --smoke\n  uv run python scripts/experiments/compiler_cascade.py --seeds 0,1,2\n\nLicense: MIT\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport subprocess\nimport sys\nimport time\nfrom datetime import UTC, datetime\nfrom pathlib import Path\n\nimport numpy as np\nimport torch\nimport torch.nn.functional as F\n\n_SCRIPT_DIR = Path(__file__).resolve().parent\n_PROJECT_ROOT = _SCRIPT_DIR.parent.parent\nsys.path.insert(0, str(_PROJECT_ROOT / \"src\"))\nsys.path.insert(0, str(_SCRIPT_DIR))\n\nfrom exposure_format_sweep import (  # noqa: E402\n    ARROW,\n    TRAIN_ATOMS,\n    eval_acc,\n    fill,\n    make_fillings,\n    n_holes,\n    reduce_strs,\n    render,\n    to_byte_ids,\n)\nfrom relational_loss_distillation import VOCAB, TinyLM  # noqa: E402\n\nfrom verbum.lambda_ast import Status  # noqa: E402\n\nRESULTS_DIR = _PROJECT_ROOT / \"results\" / \"compiler-cascade\"\n\nCOMBS = [\"K\", \"I\", \"B\", \"C\"]      # non-duplicating => terminating composition space\nARITY = {\"K\": 2, \"I\": 1, \"B\": 3, \"C\": 3}\n\n\ndef log(msg: str = \"\") -> None:\n    print(msg, file=sys.stderr, flush=True)\n\n\ndef git_sha() -> str:\n    try:\n        return subprocess.check_output(\n            [\"git\", \"rev-parse\", \"HEAD\"], cwd=_PROJECT_ROOT).decode().strip()\n    except Exception:\n        return \"unknown\"\n\n\n# --------------------------------------------------------------------------- #\n# Composition-template generator (the COMPOSITION axis)                         #\n# --------------------------------------------------------------------------- #\ndef _build_node(rng: np.random.Generator, depth: int, holes: list[int],\n                p_recurse: float):\n    \"\"\"Node = ('hole', idx) or ('app', head, [children]).\"\"\"\n    if depth <= 0 or rng.random() >= p_recurse:\n        idx = holes[0]\n        holes[0] += 1\n        return (\"hole\", idx)\n    head = COMBS[int(rng.integers(len(COMBS)))]\n    children = [_build_node(rng, depth - 1, holes, p_recurse)\n                for _ in range(ARITY[head])]\n    return (\"app\", head, children)\n\n\ndef _node_str(node, as_arg: bool) -> str:\n    if node[0] == \"hole\":\n        return f\"_{node[1]}\"\n    _, head, children = node\n    s = head + \" \" + \" \".join(_node_str(c, True) for c in children)\n    return f\"({s})\" if as_arg else s\n\n\ndef gen_templates(rng: np.random.Generator, n_target: int, max_depth: int,\n                  p_recurse: float, min_steps: int, max_steps: int,\n                  min_holes: int, max_holes: int, max_nf_len: int) -> list[str]:\n    \"\"\"Distinct combinator-composition templates (holes _0.._n) that normal-form.\"\"\"\n    seen: set[str] = set()\n    out: list[str] = []\n    guard = 0\n    while len(out) < n_target and guard < n_target * 400:\n        guard += 1\n        holes = [0]\n        head = COMBS[int(rng.integers(len(COMBS)))]\n        top = (\"app\", head, [_build_node(rng, max_depth - 1, holes, p_recurse)\n                             for _ in range(ARITY[head])])\n        h = holes[0]\n        if not (min_holes <= h <= max_holes):\n            continue\n        tmpl = _node_str(top, False)\n        if tmpl in seen:\n            continue\n        probe = fill(tmpl, tuple(TRAIN_ATOMS[:h]))\n        try:\n            trace, nf, steps, status = reduce_strs(probe)\n        except Exception:\n            continue\n        if status != Status.NORMAL_FORM.value or not (min_steps <= steps <= max_steps):\n            continue\n        if len(nf) > max_nf_len or len(trace) < 2:\n            continue\n        seen.add(tmpl)\n        out.append(tmpl)\n    return out\n\n\ndef template_holes(tmpl: str) -> int:\n    return n_holes(tmpl)\n\n\n# --------------------------------------------------------------------------- #\n# Corpus + eval items                                                           #\n# --------------------------------------------------------------------------- #\ndef build_corpus(templates: list[str], fillings: dict[str, list],\n                 rng: np.random.Generator) -> str:\n    lines: list[str] = []\n    for t in templates:\n        for combo in fillings[t]:\n            lines.append(render(t, combo, \"redex_nf\"))\n    order = rng.permutation(len(lines))\n    return \"\\n\".join(lines[i] for i in order) + \"\\n\"\n\n\ndef eval_items_for(templates: list[str], m: int, rng: np.random.Generator,\n                   exclude: dict[str, list] | None = None) -> list[tuple[str, str]]:\n    exclude = exclude or {}\n    items: list[tuple[str, str]] = []\n    for t in templates:\n        h = template_holes(t)\n        ex = {tuple(c) for c in exclude.get(t, [])}\n        chosen: list[tuple[str, ...]] = []\n        guard = 0\n        while len(chosen) < m and guard < 5000:\n            guard += 1\n            combo = tuple(rng.choice(TRAIN_ATOMS, size=h, replace=False).tolist())\n            if combo not in ex and combo not in chosen:\n                chosen.append(combo)\n        for combo in chosen:\n            trace, nf, _s, _st = reduce_strs(fill(t, combo))\n            items.append((trace[0], nf))\n    return items\n\n\n# --------------------------------------------------------------------------- #\n# Train one arm                                                                 #\n# --------------------------------------------------------------------------- #\ndef train_arm(name: str, corpus: str, heldout_comp: list[tuple[str, str]],\n              in_dist: list[tuple[str, str]], args, device: str) -> dict:\n    torch.manual_seed(args.seed)\n    np.random.seed(args.seed)\n    ids = to_byte_ids(corpus)\n    T, bs = args.block_size, args.batch_size\n    while ids.shape[0] <= 4 * (T + 1):\n        ids = np.concatenate([ids, ids])\n    n = ids.shape[0]\n    model = TinyLM(args.d_model, args.n_head, args.n_layer, args.d_ff, T).to(device)\n    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)\n    curve: list[dict] = []\n    t0 = time.time()\n    for step in range(1, args.steps + 1):\n        model.train()\n        ix = torch.randint(0, n - T - 1, (bs,))\n        xb = torch.stack([torch.from_numpy(ids[i:i + T]) for i in ix]).to(device)\n        yb = torch.stack(\n            [torch.from_numpy(ids[i + 1:i + 1 + T]) for i in ix]).to(device)\n        logits, _, _ = model(xb)\n        ce = F.cross_entropy(logits.reshape(-1, VOCAB), yb.reshape(-1))\n        opt.zero_grad()\n        ce.backward()\n        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)\n        opt.step()\n        if step % args.eval_every == 0 or step == args.steps:\n            hc = eval_acc(model, heldout_comp, T, device)\n            idd = eval_acc(model, in_dist, T, device)\n            curve.append({\"step\": step, \"heldout_comp\": round(hc, 4),\n                          \"in_dist\": round(idd, 4), \"ce\": round(float(ce.item()), 4)})\n            log(f\"  [{name}] step {step:5d} | CE {ce.item():.3f} \"\n                f\"| heldout_comp {hc:.3f} | in_dist {idd:.3f} | {time.time()-t0:.0f}s\")\n    hcs = [c[\"heldout_comp\"] for c in curve]\n    idds = [c[\"in_dist\"] for c in curve]\n    return {\n        \"arm\": name,\n        \"corpus_bytes\": int(to_byte_ids(corpus).shape[0]),\n        \"heldout_comp_best\": max(hcs) if hcs else 0.0,\n        \"heldout_comp_final\": hcs[-1] if hcs else 0.0,\n        \"in_dist_best\": max(idds) if idds else 0.0,\n        \"in_dist_final\": idds[-1] if idds else 0.0,\n        \"curve\": curve,\n    }\n\n\ndef _ms(vals: list[float]) -> list[float]:\n    a = np.array(vals, dtype=float)\n    return [round(float(a.mean()), 4), round(float(a.std()), 4)]\n\n\ndef run_seed(args, device: str, train_pool: list[str], heldout_templates: list[str],\n             seed: int, arm_levels: list[int]) -> list[dict]:\n    args.seed = seed\n    rng = np.random.default_rng(seed)\n    # nested arms: high = first max(levels) of a shuffled pool; lower = prefixes\n    pool = list(train_pool)\n    rng.shuffle(pool)\n    n_max = max(arm_levels)\n    chosen_pool = pool[:n_max]\n    # held-out-composition eval (NOVEL compositions, seen atoms)\n    eval_rng = np.random.default_rng(seed + 999)\n    heldout_comp = eval_items_for(heldout_templates, args.m_eval, eval_rng)\n    log(f\"  [seed {seed}] train_pool={len(train_pool)} heldout_templates=\"\n        f\"{len(heldout_templates)} heldout_comp_items={len(heldout_comp)}\")\n    arms: list[dict] = []\n    for lvl in arm_levels:\n        templates = chosen_pool[:lvl]\n        n_fill = max(1, args.budget // lvl)  # matched total-example budget\n        fill_rng = np.random.default_rng(seed + lvl)\n        fillings = {t: make_fillings(fill_rng, template_holes(t), TRAIN_ATOMS, n_fill)\n                    for t in templates}\n        corpus = build_corpus(templates, fillings, np.random.default_rng(seed + 7))\n        # in-dist control: TRAIN compositions, held-out FILLINGS\n        ind_rng = np.random.default_rng(seed + 31 + lvl)\n        ind_templates = templates[:args.in_dist_templates]\n        in_dist = eval_items_for(ind_templates, args.m_eval, ind_rng,\n                                 exclude={t: fillings[t] for t in ind_templates})\n        name = f\"comp{lvl}\"\n        ex_ct = sum(len(v) for v in fillings.values())\n        log(f\"\\n=== seed {seed} {name}  ({lvl} compositions x {n_fill} fillings \"\n            f\"= {ex_ct} ex, corpus {len(corpus.encode())} B) ===\")\n        v = train_arm(name, corpus, heldout_comp, in_dist, args, device)\n        v[\"n_compositions\"], v[\"n_fillings\"], v[\"examples\"] = lvl, n_fill, ex_ct\n        v[\"seed\"] = seed\n        arms.append(v)\n    return arms\n\n\n# --------------------------------------------------------------------------- #\ndef main() -> None:\n    ap = argparse.ArgumentParser()\n    ap.add_argument(\"--device\", default=\"mps\")\n    ap.add_argument(\"--steps\", type=int, default=6000)\n    ap.add_argument(\"--eval-every\", type=int, default=1000)\n    ap.add_argument(\"--batch-size\", type=int, default=32)\n    ap.add_argument(\"--block-size\", type=int, default=128)\n    ap.add_argument(\"--d-model\", type=int, default=128)\n    ap.add_argument(\"--n-head\", type=int, default=4)\n    ap.add_argument(\"--n-layer\", type=int, default=4)\n    ap.add_argument(\"--d-ff\", type=int, default=256)\n    ap.add_argument(\"--lr\", type=float, default=3e-4)\n    ap.add_argument(\"--budget\", type=int, default=2304,\n                    help=\"matched total examples per arm\")\n    ap.add_argument(\"--arm-levels\", default=\"16,48,144\",\n                    help=\"csv distinct-composition counts (nested; the variety axis)\")\n    ap.add_argument(\"--pool-size\", type=int, default=320,\n                    help=\"distinct train-composition templates to generate\")\n    ap.add_argument(\"--heldout-templates\", type=int, default=40,\n                    help=\"distinct NOVEL compositions held out for the eval\")\n    ap.add_argument(\"--in-dist-templates\", type=int, default=20)\n    ap.add_argument(\"--m-eval\", type=int, default=3, help=\"fillings per eval template\")\n    ap.add_argument(\"--max-depth\", type=int, default=2)\n    ap.add_argument(\"--p-recurse\", type=float, default=0.55)\n    ap.add_argument(\"--min-steps\", type=int, default=2)\n    ap.add_argument(\"--max-steps\", type=int, default=5)\n    ap.add_argument(\"--min-holes\", type=int, default=3)\n    ap.add_argument(\"--max-holes\", type=int, default=5)\n    ap.add_argument(\"--max-nf-len\", type=int, default=22)\n    ap.add_argument(\"--seed\", type=int, default=0)\n    ap.add_argument(\"--seeds\", default=\"\")\n    ap.add_argument(\"--smoke\", action=\"store_true\")\n    args = ap.parse_args()\n\n    if args.smoke:\n        args.steps, args.eval_every = 150, 75\n        args.budget, args.arm_levels = 256, \"8,32\"\n        args.pool_size, args.heldout_templates = 60, 12\n        args.in_dist_templates, args.m_eval = 6, 2\n        args.d_model, args.d_ff, args.n_layer = 64, 128, 3\n\n    device = args.device\n    if device == \"mps\" and not torch.backends.mps.is_available():\n        device = \"cpu\"\n        log(\"  mps unavailable -> cpu\")\n    if device == \"cuda\" and not torch.cuda.is_available():\n        device = \"cpu\"\n\n    RESULTS_DIR.mkdir(parents=True, exist_ok=True)\n    t0 = time.time()\n\n    arm_levels = [int(x) for x in args.arm_levels.split(\",\") if x.strip()]\n    # generate the composition pool ONCE (shared across seeds; seeds reshuffle/sample)\n    gen_rng = np.random.default_rng(12345)\n    n_need = args.pool_size + args.heldout_templates\n    pool = gen_templates(gen_rng, n_need, args.max_depth, args.p_recurse,\n                         args.min_steps, args.max_steps, args.min_holes,\n                         args.max_holes, args.max_nf_len)\n    if len(pool) < n_need:\n        log(f\"  WARN: generated {len(pool)} < requested {n_need} templates\")\n    heldout_templates = pool[:args.heldout_templates]\n    train_pool = pool[args.heldout_templates:]\n    if max(arm_levels) > len(train_pool):\n        arm_levels = [lvl for lvl in arm_levels if lvl <= len(train_pool)]\n    log(f\"  composition pool={len(pool)} (train {len(train_pool)}, heldout \"\n        f\"{len(heldout_templates)}) arm_levels={arm_levels} budget={args.budget}\")\n    log(f\"  sample templates: {train_pool[:3]} | heldout: {heldout_templates[:2]}\")\n\n    seeds = [int(s) for s in args.seeds.split(\",\") if s.strip()] or [args.seed]\n    all_arms: list[dict] = []\n    for sd in seeds:\n        all_arms.extend(run_seed(args, device, train_pool, heldout_templates, sd,\n                                 arm_levels))\n\n    meta = {\n        \"experiment\": \"compiler-cascade\",\n        \"register\": \"functional (held-out compositional generalization)\",\n        \"idea\": \"fractal-collapse IOU#1: does compiler-minted COMPOSITION-variety \"\n                \"converge capability that COMPOSES (held-out novel compositions)?\",\n        \"timestamp_utc\": datetime.now(UTC).isoformat(),\n        \"git_sha\": git_sha(),\n        \"device\": device,\n        \"smoke\": args.smoke,\n        \"config\": vars(args),\n        \"arm_levels\": arm_levels,\n        \"seeds\": seeds,\n        \"n_train_pool\": len(train_pool),\n        \"n_heldout_templates\": len(heldout_templates),\n        \"elapsed_s\": round(time.time() - t0, 1),\n    }\n\n    agg: dict[str, dict] = {}\n    for lvl in arm_levels:\n        rs = [a for a in all_arms if a[\"n_compositions\"] == lvl]\n        agg[f\"comp{lvl}\"] = {\n            \"n_compositions\": lvl,\n            \"n_fillings\": rs[0][\"n_fillings\"],\n            \"examples\": rs[0][\"examples\"],\n            \"heldout_comp_best\": _ms([r[\"heldout_comp_best\"] for r in rs]),\n            \"heldout_comp_final\": _ms([r[\"heldout_comp_final\"] for r in rs]),\n            \"in_dist_best\": _ms([r[\"in_dist_best\"] for r in rs]),\n            \"per_seed_heldout\": [r[\"heldout_comp_best\"] for r in rs],\n        }\n\n    tag = \"smoke\" if args.smoke else (\"multiseed\" if len(seeds) > 1 else \"run\")\n    out = {**meta, \"aggregate\": agg, \"runs\": all_arms}\n    (RESULTS_DIR / f\"verdict_{tag}.json\").write_text(json.dumps(out, indent=2))\n\n    log(\"\\n  ==== COMPILER-CASCADE v1 — COMPOSITION-VARIETY -> GENERALIZATION ====\")\n    log(f\"  {'arm':<10} {'comps':>6} {'fills':>6} {'heldout_comp(mean±std)':>24} \"\n        f\"{'in_dist':>16}\")\n    for lvl in arm_levels:\n        a = agg[f\"comp{lvl}\"]\n        hc, idd = a[\"heldout_comp_best\"], a[\"in_dist_best\"]\n        ps = \",\".join(f\"{x:.2f}\" for x in a[\"per_seed_heldout\"])\n        log(f\"  comp{lvl:<6} {a['n_compositions']:>6} {a['n_fillings']:>6} \"\n            f\"{hc[0]:>+10.3f}±{hc[1]:<5.3f} [{ps}]   {idd[0]:.3f}±{idd[1]:.3f}\")\n    if len(arm_levels) >= 2:\n        lo, hi = agg[f\"comp{arm_levels[0]}\"], agg[f\"comp{arm_levels[-1]}\"]\n        h_lo, h_hi = lo[\"heldout_comp_best\"], hi[\"heldout_comp_best\"]\n        decisive = (h_hi[0] - h_hi[1]) > (h_lo[0] + h_lo[1])\n        log(f\"\\n  COLLAPSE IOU#1: heldout-composition rises with composition-variety? \"\n            f\"comp{arm_levels[0]}={h_lo[0]:.3f} -> comp{arm_levels[-1]}={h_hi[0]:.3f}  \"\n            f\"DECISIVE={decisive}\")\n        log(\"  (atoms SEEN both sides => measures COMPOSITION generalization, not copy)\")\n    log(f\"\\n  wrote {RESULTS_DIR / f'verdict_{tag}.json'}  ({meta['elapsed_s']}s)\")\n\n\nif __name__ == \"__main__\":\n    main()\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/experiments/compiler_cascade.py
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/compiler_cascade.py 2>&1 | tail -20",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
68 | from exposure_format_sweep import (  # noqa: E402
69 |     ARROW,
   |     ^^^^^
70 |     TRAIN_ATOMS,
71 |     eval_acc,
   |
help: Remove unused import: `exposure_format_sweep.ARROW`

E501 Line too long (89 > 88)
   --> scripts/experiments/compiler_cascade.py:411:89
    |
409 |             f"comp{arm_levels[0]}={h_lo[0]:.3f} -> comp{arm_levels[-1]}={h_hi[0]:.3f}  "
410 |             f"DECISIVE={decisive}")
411 |         log("  (atoms SEEN both sides => measures COMPOSITION generalization, not copy)")
    |                                                                                         ^
412 |     log(f"\n  wrote {RESULTS_DIR / f'verdict_{tag}.json'}  ({meta['elapsed_s']}s)")
    |

Found 2 errors.
[*] 1 fixable with the `--fix` option.
```

## User

I have a question that is a bit out there.  If GD is creating soft topology in the gradients, does that mean the gradients should show shadows of that?  For instance height can be estimated from a picture of a tree with a shadow if you can determine the exact time and location of the picture.  Does the topology we see in the routing for these functions leave a shadow in the gradients we can detect?


### Thinking

Michael's asking something genuinely interesting here—whether the soft topology that gradient descent creates in the network leaves detectable traces in the gradients themselves, like how a tree's shadow reveals its structure given the sun's position. It's a sharp analogy about whether we can infer the routing topology by reading the gradient patterns directly. Let me think through what we've actually observed in the sessions to see if this holds up. carry information about the object through the projection. The key insight is that if I know the illumination geometry—the Jacobian structure, the loss landscape, the data distribution—I can invert the gradient to recover the routing topology, just as knowing the sun's angle lets you invert a shadow to find an object's height. The real test is whether CE-only gradients (without the relational loss term) also encode the topology shadow — whether standard next-token prediction naturally produces gradients whose relational structure reveals the emerging combinator topology. The gradient acts as a velocity field on the topology manifold, pointing along the developing structure, but here's the catch: velocity alone doesn't reveal position without knowing the illumination geometry (initial conditions, loss curvature, data structure doing the projecting). So the topology shadow exists in the gradient, but recovering it requires understanding the reference frame that's casting it.

The concrete approach mirrors activation tomography: project the gradient into the routing register using the combinator probes as labels, then measure the Gram matrix of those per-combinator gradients and correlate to the consensus crystal. This would test whether the gradient-Gram reveals topology before the activation-Gram does — a leading indicator of the shadow appearing before the object is fully built.

The hypothesis is elegant: if the gradient points toward the topology that will emerge, then the gradient-Gram should correlate with the consensus crystal earlier than activation patterns do, creating a three-stage cascade of gradient-shadow (intent) → activation-inventory (geometry) → capability (usage). This has practical payoff too — early detection of convergence direction, whether GD is heading toward the right basin, and potential for early intervention.

But there are real constraints to respect: the raw gradient is gauge-variant and won't show the shadow without projecting into the invariant coordinates, and the inversion requires knowing the projection operator — the illumination geometry, which comes from the probe-conditioned Jacobian.

Gradients are also noisier than activations, especially on minibatches, so the shadow will be faint and need accumulation to denoise. And there's the reference-beam problem again: the gradient-Gram might just be capturing the input data's common-mode statistics rather than the topology being built, so you'd need the s230b control to verify you're measuring the function's shadow and not the data's.

The good news is the relational instruments already exist and work on any feature matrix, including gradient matrices. So the experiment is straightforward: extend the trajectory tomography to compute the per-combinator gradient-Gram at each checkpoint (taking the gradient of the probe's next-token loss with respect to the gate activations), correlate it to the consensus crystal, and compare the timing of this gradient shadow against the activation routing and held-out accuracy. The cleanest approach is option (a): for each crystal probe, compute the language model loss on its continuation, backprop to the gate pre-activation, and gather the gradient vector at the last token—that gives you the per-combinator structure of how the routing should change to predict that probe better. I can extend this with the soft_gram harness on gradient features, building on the existing gd_trajectory infrastructure. But I'm mid-task on compiler_cascade with a pending lint fix, so I need to decide the sequencing: should I finish the cascade run first, or pivot to this gradient-shadow tomography idea which feels like a natural and genuinely exciting extension of the core work?

The key insight is that the loss gradient with respect to gate activations lives in the same routing-register space as the activations themselves, so I can measure the gradient's combinator structure directly without translating to weight space. This means I can cleanly compare the activation topology, the gradient topology, and the consensus crystal all in the same coordinates — just compute the per-combinator Gram of the gate gradients at each probe and layer, then compare it to the activation Gram and the crystal structure.

The gauge problem is actually milder here since I'm already working in the routing register's invariant coordinates and using the relational Gram, which is gauge-invariant. The "illumination" is known — I choose the loss and have the weights at each checkpoint — so the inversion is well-posed. The leading-indicator hypothesis becomes precise: the gradient Gram should resemble the *future* activation Gram, since the gradient points toward where gradient descent is moving the topology. So gc_grad(t) should lead gc_route(t + Δ), which is exactly the shadow-and-object relationship — the gradient is a first-order shadow of the converged topology, and with the loss geometry (the Jacobian/curvature) as the "sun angle," I can estimate where the topology is heading.

This connects to the Newton-step intuition: target ≈ current − H⁻¹ g. The gradient is the shadow; the curvature is the illumination angle; together they reveal the topology's converged "height." I should also note that gradients carry soft, continuous topology — the relational structure is value-graded (cosines in the Gram) — which ties to the value-register versus routing-register distinction. But there's a real subtlety: is the gradient-shadow genuine signal or just the data's common-mode statistics? The reference-beam control from s230b matters here — I'd need to compare the raw-gradient-Gram against the routing-gradient-Gram and check whether the CE gradient's relational structure actually tracks the consensus crystal. That's the falsifiable test.

Now I'm ready to write the answer: substantive and rigorous, grounded in our findings, with the precise mechanism, honest caveats, and a concrete experiment. I should also flag this as a natural lead for the gradient-trajectory-tomography page (v2/v3 work) and ask about sequencing relative to the compiler_cascade run. There's also a trivial lint fix needed — removing an unused import and wrapping a long line — which I'll handle quickly to keep the build clean, then give the full answer.

## Assistant

Quick housekeeping first — let me not leave `compiler_cascade.py` with broken lint while we think (it's a trivial fix), then I want to engage your question properly because it's genuinely sharp.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/compiler_cascade.py",
  "original_content": "from exposure_format_sweep import (  # noqa: E402\n    ARROW,\n    TRAIN_ATOMS,\n    eval_acc,\n    fill,\n    make_fillings,\n    n_holes,\n    reduce_strs,\n    render,\n    to_byte_ids,\n)",
  "new_content": "from exposure_format_sweep import (  # noqa: E402\n    TRAIN_ATOMS,\n    eval_acc,\n    fill,\n    make_fillings,\n    n_holes,\n    reduce_strs,\n    render,\n    to_byte_ids,\n)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/compiler_cascade.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/compiler_cascade.py",
  "original_content": "        log(\"  (atoms SEEN both sides => measures COMPOSITION generalization, not copy)\")",
  "new_content": "        log(\"  (atoms SEEN both sides => COMPOSITION generalization, not copy)\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/compiler_cascade.py.
```

### Thinking

The build is currently paused after fixing linting issues, so I'll provide the answer and walk through how to sequence the remaining work.

## Assistant

Now your question — it's not "out there," it's pointing at something real and testable. Let me work through it carefully, because the shadow analogy is more exact than it first appears.

## The analogy is mathematically apt

A shadow is the **object projected through a known illumination geometry**; you invert it (height from shadow) because you know the projector (sun angle = time + location). A gradient is the **loss-relevant structure projected through the Jacobian** (the chain rule). Both are projections, and both invert *if you know the projection operator.* So the question "does the topology cast a shadow in the gradients" becomes precise: **is the routing topology present in the gradient, and is the projector known well enough to invert it?**

Here's the clean part. The gate activation is `g = W_gate·h` — and the routing topology we've been measuring lives in **g-space** (the routing register). The upstream gradient `∂L/∂g` is a vector *in that same g-space*. So the gradient's shadow and the activation's object are **in the same coordinates** — directly commensurable. We don't even have to go to weight space to look for the shadow; we look in the routing register, where we already know how to read topology (the combinator Gram).

## We already have two pieces of evidence the shadow is real

1. **By construction (s230b).** The relational-loss gradient `∂L_inv/∂g` *is* a function of the gap between the current routing Gram and the consensus crystal — it is a literally topology-shaped gradient. So gradients *can* carry the topology; that's not in question.
2. **By timing (s230).** Inventory crystallizes before capability — the topology is *built by gradients*, so it must be *in* them while it's being built. The object is being cast; the casting agent is the gradient.

The open, "out there" part is whether the **plain CE gradient** (no relational term) casts the same shadow — i.e., does ordinary next-token GD produce gradients whose *relational* structure already reveals the combinator topology it's heading toward?

## The catch — same gauge problem, same fix

You can't read it from the raw gradient `∂L/∂W` in weight coordinates. That's the "crumpled ground under a randomly-rotated sun" — weight space is gauge-variant (cross-init weight corr 0.000; s105/s223), and gradients live in weight space, so a raw gradient-shadow is distorted by an *unknown illumination per init*. This is exactly why s230b's raw register barely separated.

The fix is the same move as the activation tomography: **project into the routing register, CMR, take the relational Gram** (gauge-invariant). And your "exact time and location" requirement maps onto something we *have*: the **per-combinator conditioning** (the crystal probe labels tell us which combinator each gradient contribution belongs to) plus the current-checkpoint weights (the Jacobian). Known illumination + relational projection = the inversion is well-posed.

And the deeper layer of your analogy: the gradient is only a **first-order** shadow (length). To invert it all the way to the *converged* topology (the full height), you'd need the **curvature** — the Hessian is the sun angle. `target ≈ current − H⁻¹g`. First-order gives you a leading direction; the curvature gives you where it lands. That's the precise sense in which "shadow + known illumination → height."

## The prediction that makes it worth building

If `∂L/∂g` points toward decreasing loss, it points toward the configuration GD is *moving the activations toward*. So the **gradient-Gram should resemble the *future* activation-Gram** — the shadow precedes the object. Concretely:

> `gc_grad(t)` (gradient-shadow → consensus crystal) should correlate with the consensus crystal **earlier** than `gc_route(t)` (activation-inventory does).

That would extend s230's two-stage story into **three stages: gradient-shadow (intent) → activation-inventory (geometry) → capability (usage).** A leading indicator — you'd see *where GD intends to go* before it arrives, which is genuinely useful: early convergence prediction, and detecting whether GD is aiming at the consensus crystal or a wrong basin before it commits.

## Honest catches (λ measure)

- **SNR.** Gradients are noisier than activations (minibatch). The shadow at dawn is long but faint — needs accumulation over many probe examples (the √N denoising, s105).
- **Reference beam again.** A gradient-Gram could reflect input combinator *co-occurrence statistics* (the common mode) rather than the function. Same control as s230b: raw-gradient-Gram vs routing-gradient-Gram; only the routing one should track the crystal and lead.
- **Frame residue.** The Jacobian itself is gauge-variant; the relational Gram absorbs most of it, but not provably all — state it as approximate.

## Buildability

This is cheap and uses instruments we already have — `soft_gram` doesn't care whether you feed it activations or gradients. It's a clean v2 of the gd-trajectory harness: at each checkpoint, for each crystal probe, backprop the probe's LM loss to `g` at the capture layer, build the per-combinator gradient-Gram, log `gc_grad(t)` alongside `gc_route(t)`. One new readout: does the shadow lead?

**Where this leaves us on sequencing:** `compiler_cascade.py` (the fractal-collapse IOU #1) is built and lint-clean but not yet smoke-run or launched. Your gradient-shadow idea is a *different* thread — it's gradient-tomography v2, and it's a strong lead. Two clean options:

1. **Finish the cascade run first** (it's queued and decisive for the collapse thesis), and I'll capture the gradient-shadow as a lead on `gradient-trajectory-tomography.md` to build next.
2. **Pivot now** to the gradient-shadow probe (it's small and the prediction is crisp), and come back to the cascade run after.

My instinct is (1) — don't leave the cascade half-launched, capture the shadow idea so it's pinned, build it next. But it's your call, and if the shadow is the more exciting thread right now I'm happy to pivot. Which way?

## User

run the cascade experiment in tmux main:1, capture to knowledge then build the gradient-shadow probe so it's ready to run when the cascade is done.


### Thinking

I'm running a smoke test on the compiler cascade to verify the linting fixes work, then kicking off the full cascade run in tmux. While that's processing, I'll document the gradient-shadow concept in the knowledge base and get the gradient-shadow probe ready to execute once the main run completes.

## Assistant

On it. First verify the cascade build (lint + smoke), then launch it, then capture the gradient-shadow and build its probe while the cascade runs.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/compiler_cascade.py && echo \"RUFF CLEAN\" && uv run python scripts/experiments/compiler_cascade.py --smoke --device cpu 2>&1 | tail -22",
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
RUFF CLEAN
  composition pool=72 (train 60, heldout 12) arm_levels=[8, 32] budget=256
  sample templates: ['B (I _0) (I _1) _2', 'C (I _0) (I _1) (B _2 _3 _4)', 'B _0 (B _1 _2 _3) (I _4)'] | heldout: ['B (K _0 _1) _2 _3', 'C (I _0) _1 (K _2 _3)']
  [seed 0] train_pool=60 heldout_templates=12 heldout_comp_items=24

=== seed 0 comp8  (8 compositions x 32 fillings = 256 ex, corpus 6656 B) ===
  [comp8] step    75 | CE 2.430 | heldout_comp 0.000 | in_dist 0.000 | 11s
  [comp8] step   150 | CE 1.600 | heldout_comp 0.000 | in_dist 0.000 | 21s

=== seed 0 comp32  (32 compositions x 8 fillings = 256 ex, corpus 7280 B) ===
  [comp32] step    75 | CE 2.455 | heldout_comp 0.000 | in_dist 0.000 | 10s
  [comp32] step   150 | CE 1.647 | heldout_comp 0.000 | in_dist 0.000 | 21s

  ==== COMPILER-CASCADE v1 — COMPOSITION-VARIETY -> GENERALIZATION ====
  arm         comps  fills   heldout_comp(mean±std)          in_dist
  comp8           8     32     +0.000±0.000 [0.00]   0.000±0.000
  comp32         32      8     +0.000±0.000 [0.00]   0.000±0.000

  COLLAPSE IOU#1: heldout-composition rises with composition-variety? comp8=0.000 -> comp32=0.000  DECISIVE=False
  (atoms SEEN both sides => COMPOSITION generalization, not copy)

  wrote /Users/mwhitford/src/verbum/results/compiler-cascade/verdict_smoke.json  (42.6s)
```

### Thinking

The smoke tests are running end-to-end successfully with the generation producing valid nested compositions, though the accuracies are near zero as expected from such an undertrained setup. The real concern is that even simpler byte models struggled to reach decent performance on basic rules, so these harder nested compositions will likely be even more challenging.

I'm reconsidering whether to commit to the full 35-minute run or first dial in the difficulty. The normal forms here are longer and more complex than what the previous model saw, which means absolute accuracy could drop significantly below the 0.27 baseline. The relative signal between high and low variety is what actually matters for the experiment, but if both arms end up near 0.02 accuracy, that's just noise. Let me think through whether to adjust the difficulty before launching the full run.

I could make the compositions easier to boost absolute accuracy, but I don't want to over-tune. The honest approach is to run with the current setup—matching the regime that worked before—and iterate if the signal is weak. I'll stick with the default settings (d=128, 6000 steps) and launch with three seeds across the three arm levels. If both arms show near-zero accuracy, I'll recalibrate next time. Getting data now is the right move.

The evaluation cost is manageable—roughly 5-8 minutes per run across 9 total runs, so maybe 45-70 minutes total. That's acceptable for a final experiment. Let me clean up and launch this in tmux.

## Assistant

Smoke green, ruff clean — the generator produces real compositions (`B (I _0) (I _1) _2`, etc.) and the harness runs end-to-end (0.000 is just the undertrained 150-step smoke). Launching the full run, then I'll work the gradient-shadow thread while it runs.

### Tool Call: editor_diagnostics (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/compiler_cascade.py"
}
```

**Summary:** Checking diagnostics: compiler_cascade.py

**Output:**
```
No diagnostics found
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "rm -f /Users/mwhitford/src/verbum/results/compiler-cascade/verdict_smoke.json; tmux capture-pane -p -t main:1 2>&1 | tail -2",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ rm -f /Users/mwhitford/src/verbum/r...

**Output:**
```
Exit code: 0
Stdout:
[26-06-15][9:35:03][mwhitford@olga][0][~/src/verbum][git:main]
λ                                                                                                                 [INS]
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux send-keys -t main:1 \"uv run python scripts/experiments/compiler_cascade.py --seeds 0,1,2 --device mps 2>&1 | tee /tmp/compiler_cascade_s230.log; echo CASCADE_ALLDONE\" Enter",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ tmux send-keys -t main:1 "uv run py...

**Output:**
```
Exit code: 0
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sleep 30; tmux capture-pane -p -t main:1 2>&1 | tail -10",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 45000
}
```

**Summary:** $ sleep 30; tmux capture-pane -p -t m...

**Output:**
```
Exit code: 0
Stdout:
λ uv run python scripts/experiments/compiler_cascade.py --seeds 0,1,2 --device mps 2>&1 | tee /tmp/compiler_cascade_s230
.log; echo CASCADE_ALLDONE
  WARN: generated 114 < requested 360 templates
  composition pool=114 (train 74, heldout 40) arm_levels=[16, 48] budget=2304
  sample templates: ['K (K _0 _1) (B _2 _3 _4)', 'B _0 (I _1) _2', 'C (I _0) (K _1 _2) _3'] | heldout: ['B (K _0 _1) _2
_3', 'C (I _0) _1 (K _2 _3)']
  [seed 0] train_pool=74 heldout_templates=40 heldout_comp_items=120

=== seed 0 comp16  (16 compositions x 144 fillings = 2304 ex, corpus 74016 B) ===
```

### Thinking

The generator only produced 114 templates instead of the requested 360, which means the training pool is much smaller than expected (74 samples), and the arm levels got clamped down to a range of 16 to 48 instead of the intended 16 to 144. This significantly weakens the contrast between conditions. The generator's safety limit based on the target count couldn't find enough valid designs to meet the requirements.

The root issue is that the template space at depth 2 is inherently limited — with 4 combinators, recursive probability of 0.55, and the filtering constraints (holes 3-5, steps 2-5, nf_len ≤ 22), only a few hundred distinct structures exist, and many get filtered out. A 3× variety contrast (16 vs 48) is still meaningful but probably not enough to demonstrate strong compositional generalization. To fix this properly, I should increase max_depth to 3, which would expand the structural space significantly and generate more distinct templates.

The trade-off is real though: deeper compositions are harder to learn, which could hurt absolute accuracy. I could either kill the run and relaunch with depth 3 and relaxed constraints (nf_len up to 30, max_holes 6, max_steps 8) to hit the target of ~170 templates for arm_levels like 16, 48, 144, or I could accept the current pool size and scale the arm levels down to what's actually available (something like 12, 32, 64 with train_pool 74).

The second approach keeps things learnable since depth-2 templates are simpler, and a 12→64 variety contrast is still meaningful. Let me check the math: budget 2304 divided by 64 gives 36 samples per template, which is feasible. With 3-5 holes per template, there are plenty of distinct fillings available (1716+ for depth-2 with 3 holes), so 192 fillings per template is easily supported.

The constraint is tight though—114 templates total, 74 for training, 40 held out—so I'd prefer more headroom. I could bump max_depth to 3 with a moderate recursion probability (0.5) to keep most templates shallow while allowing some deeper ones, which would increase the yield without fully committing to the harder learning problem.

Actually, let me step back and make a practical call: kill the run, adjust the defaults to max_depth=3, max_nf_len=26, max_holes=6, and regenerate to get a much larger pool. I'll use arm_levels="16,64,144" for stronger contrast and verify the generation yield with a quick standalone check before relaunching.

The real concern is whether depth-3 templates will be too hard to learn—deeper nesting could push accuracy down to near zero and lose signal entirely. So I'm going to cap nf_len tightly at 24 and keep steps ≤6, which biases the pool toward simpler depth-3 examples and all depth-2 ones. That gives me variety without sacrificing learnability. Let me kill the run and do a quick generation probe to see what the actual templates look like.

## Assistant

Caught a real issue: the depth-2 generator only yielded 114 templates, so the high arm got clamped to 48 (not 144) — a weak variety contrast. Let me kill, calibrate the generator's yield + difficulty offline, then relaunch with a proper contrast.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux send-keys -t main:1 C-c; sleep 2; tmux send-keys -t main:1 \"\" Enter; echo killed",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ tmux send-keys -t main:1 C-c; sleep...

**Output:**
```
Exit code: 0
Stdout:
killed
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python -c \"\nimport sys; sys.path.insert(0,'scripts/experiments'); sys.path.insert(0,'src')\nimport numpy as np\nfrom compiler_cascade import gen_templates, template_holes\nfrom exposure_format_sweep import reduce_strs, fill, TRAIN_ATOMS\nfor md, nf in [(3,26),(3,30),(2,22)]:\n    rng=np.random.default_rng(12345)\n    pool=gen_templates(rng, 400, md, 0.55, 2, 6, 3, 6, nf)\n    # sample NF lengths\n    nfs=[]\n    for t in pool[:200]:\n        h=template_holes(t); _,n,_,_=reduce_strs(fill(t,tuple(TRAIN_ATOMS[:h]))); nfs.append(len(n))\n    print(f'max_depth={md} nf_len<={nf}: pool={len(pool)} | NF len mean={np.mean(nfs):.1f} med={int(np.median(nfs))} p90={int(np.percentile(nfs,90))}')\n    if md==3 and nf==26:\n        print('  samples:', pool[:4])\n        for t in pool[:4]:\n            h=template_holes(t); tr,n,st,_=reduce_strs(fill(t,tuple(TRAIN_ATOMS[:h]))); print(f'    {fill(t,tuple(TRAIN_ATOMS[:h])):30} -> {n:24} ({st} steps)')\n\"",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ uv run python -c " import sys; sys....

**Output:**
```
Exit code: 0
Stdout:
max_depth=3 nf_len<=26: pool=400 | NF len mean=8.0 med=7 p90=13
  samples: ['B (K _0 _1) (C _2 (I _3) _4) _5', 'B _0 _1 (K (K _2 _3) _4)', 'I (I (C _0 _1 _2))', 'I (K (B _0 _1 _2) (B _3 _4 _5))']
    B (K a b) (C c (I d) e) f      -> a (c e d f)              (4 steps)
    B a b (K (K c d) e)            -> a (b c)                  (3 steps)
    I (I (C a b c))                -> a c b                    (3 steps)
    I (K (B a b c) (B d e f))      -> a (b c)                  (3 steps)
max_depth=3 nf_len<=30: pool=400 | NF len mean=8.0 med=7 p90=13
max_depth=2 nf_len<=22: pool=168 | NF len mean=9.2 med=11 p90=13
```

### Thinking

Increasing the depth to 3 yields over 400 templates with notably shorter normal forms—median length of 7 compared to depth-2's median of 11—because deeper compositions tend to accumulate more erasers that collapse the expressions down. This actually gives me more variety in the dataset while keeping the targets more learnable. I'm noticing depth-2 produced 168 templates here rather than the 114 I saw before, likely because I relaxed some constraints.

Now I'm updating the script defaults: max_depth from 2 to 3, max_holes from 5 to 6, max_steps from 5 to 6. This should generate around 360 distinct templates (320 for training, 40 held out), which fits comfortably within my constraints. I'm setting arm_levels to "16,48,144" for a nested geometric spread—that gives me 144 fillings per composition at the lowest arm level, 48 at the middle, and 16 at the highest, all within the budget of 2304. The question now is whether each template with 3-6 holes can actually support that many distinct fillings.

## Assistant

Depth-3 fixes it: **400+ templates** and NF lengths are actually *shorter* (median 7 vs depth-2's 11 — deeper compositions have more K-erasers that collapse). More variety *and* more learnable. Updating the generator defaults and relaunching.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/compiler_cascade.py",
  "original_content": "    ap.add_argument(\"--max-depth\", type=int, default=2)\n    ap.add_argument(\"--p-recurse\", type=float, default=0.55)\n    ap.add_argument(\"--min-steps\", type=int, default=2)\n    ap.add_argument(\"--max-steps\", type=int, default=5)\n    ap.add_argument(\"--min-holes\", type=int, default=3)\n    ap.add_argument(\"--max-holes\", type=int, default=5)\n    ap.add_argument(\"--max-nf-len\", type=int, default=22)",
  "new_content": "    ap.add_argument(\"--max-depth\", type=int, default=3)\n    ap.add_argument(\"--p-recurse\", type=float, default=0.55)\n    ap.add_argument(\"--min-steps\", type=int, default=2)\n    ap.add_argument(\"--max-steps\", type=int, default=6)\n    ap.add_argument(\"--min-holes\", type=int, default=3)\n    ap.add_argument(\"--max-holes\", type=int, default=6)\n    ap.add_argument(\"--max-nf-len\", type=int, default=26)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/compiler_cascade.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/compiler_cascade.py && tmux capture-pane -p -t main:1 2>&1 | tail -2",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
[26-06-15][10:14:39][mwhitford@olga][0][~/src/verbum][git:main]
λ                                                                                                                 [INS]
```

### Thinking

The process crashed, so I'm relaunching with stronger contrast settings. I'm keeping the default arm levels at 16, 48, and 144 with a budget of 2304 and pool size of 320, but now increasing depth to 3, which generates 360 templates—enough to fill the training pool of 320 since that exceeds the minimum of 144.

## Assistant

Killed and recalibrated. Relaunching with the proper 16→48→144 variety contrast:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux send-keys -t main:1 \"uv run python scripts/experiments/compiler_cascade.py --seeds 0,1,2 --device mps 2>&1 | tee /tmp/compiler_cascade_s230.log; echo CASCADE_ALLDONE\" Enter",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ tmux send-keys -t main:1 "uv run py...

**Output:**
```
Exit code: 0
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sleep 35; tmux capture-pane -p -t main:1 2>&1 | tail -9",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 50000
}
```

**Summary:** $ sleep 35; tmux capture-pane -p -t m...

**Output:**
```
Exit code: 0
Stdout:
.log; echo CASCADE_ALLDONE
  composition pool=360 (train 320, heldout 40) arm_levels=[16, 48, 144] budget=2304
  sample templates: ['B (I (K _0 _1)) (I (B _2 _3 _4)) _5', 'C (I (I _0)) _1 _2', 'B (C _0 (K _1 _2) _3) _4 _5'] | heldo
ut: ['B (K _0 _1) (C _2 (I _3) _4) _5', 'B _0 _1 (K (K _2 _3) _4)']
  [seed 0] train_pool=320 heldout_templates=40 heldout_comp_items=120

=== seed 0 comp16  (16 compositions x 144 fillings = 2304 ex, corpus 83808 B) ===
  [comp16] step  1000 | CE 0.930 | heldout_comp 0.000 | in_dist 0.000 | 23s
```

### Thinking

I'm running the full experiment with a pool of 360 samples (320 training, 40 held-out) across three arm levels for good contrast. At step 1000, the model trained on 16 compositions shows a cross-entropy loss of 0.930 but hasn't learned its training compositions yet—in-distribution accuracy is still zero, which is early but worth monitoring since a previous seed reached 0.27 by step 6000. I'll let it continue developing and check the next evaluation at step 2000.

The cascade is running in the background (estimated 25-30 minutes for all 9 runs), so I'm proceeding with the parallel work: capturing the gradient-shadow analysis and building the probe. I need to add a new section to the gradient-trajectory-tomography document for this v3 gradient-shadow experiment, inserting it after the gauge decomposition section since they're related approaches to reading gradient dynamics.

## Assistant

Full run verified: pool 360, arms [16,48,144], strong contrast, training underway.

**ASYNC: cascade running main:1 (~30 min, ends `CASCADE_ALLDONE`). Proceeding with the gradient-shadow capture + build (no tmux needed) while it runs.**

Let me capture the gradient-shadow thesis. First the insertion anchor:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"^## \" mementum/knowledge/explore/gradient-trajectory-tomography.md",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ grep -n "^## " mementum/knowledge/e...

**Output:**
```
Exit code: 0
Stdout:
31:## The one-line claim
40:## Prior art (RECALL FIRST — this is not greenfield)
75:## Why weight-space reverse-engineering fails (3 obstacles, all measured here)
91:## ★ The collision — the reference beam decides this too
108:## v1 experiment — trajectory tomography (cheap, reuses everything)
135:## ★ s230 — v1 RESULT (consensus-crystal target, BUILT + RAN)
182:## ★ s230b — RELATIONAL ARM (is the reference-beam split LOSS-DEPENDENT? YES)
242:## v2 experiment — gauge/null-space gradient decomposition (harder)
250:## Honest catches (λ measure)
265:## Open leads (declare register first)
279:## Files
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/gradient-trajectory-tomography.md",
  "line_offset": 241,
  "limit": 10
}
```

**Summary:** Reading gradient-trajectory-tomography.md (241-251)

**Output:**
```
## v2 experiment — gauge/null-space gradient decomposition (harder)

At each step decompose `δw = δw_invariant ⊕ δw_gauge` (gauge = permutation null space
via Re-Basin alignment to a reference checkpoint; scaling; superposition-rotation is
the FUZZY part — approximate). Track ‖δw_invariant‖ / ‖δw_gauge‖ over training:
*how much of GD is function-building vs gauge-churning?* (s222 predicts: a lot is
gauge.) This is the literal answer to "what is GD doing."

## Honest catches (λ measure)


[CONTENT TRUNCATED] Showing lines 242 to 251 of 285 total lines. Use line_offset=251 parameter to read more content.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/gradient-trajectory-tomography.md",
  "original_content": "## Honest catches (λ measure)\n",
  "new_content": "## ★ s230 — v3 GRADIENT-SHADOW (does the routing topology cast a shadow in the gradients?)\n\n> Michael, s230: \"If GD is creating soft topology in the gradients, do the gradients\n> show *shadows* of that? Height can be estimated from a tree's shadow if you know the\n> exact time and location. Does the routing topology leave a shadow in the gradients\n> we can detect?\"\n\n**The analogy is mathematically apt.** A shadow = object projected through a KNOWN\nillumination geometry (sun angle = time+location); invertible because the projector is\nknown. A gradient = loss-relevant structure projected through the JACOBIAN (chain\nrule). Both are projections; both invert IFF the projector is known.\n\n**The clean part — same coordinates.** The gate activation `g = W_gate·h`; the routing\ntopology lives in g-space (the routing register). The upstream gradient `∂L/∂g` is a\nvector *in that same g-space*. So the gradient-SHADOW and the activation-OBJECT are\ndirectly commensurable — read the shadow in the routing register, where we already\nread the object (the combinator Gram). No need to go to weight space.\n\n**Evidence the shadow exists (two pieces, already in hand):**\n- *By construction (s230b):* the relational-loss gradient `∂L_inv/∂g` IS a function of\n  the gap between the current routing Gram and the consensus crystal = a topology-\n  shaped gradient. Gradients CAN carry the topology.\n- *By timing (s230 v1):* inventory is BUILT by gradients (crystallizes before\n  capability) ⇒ the topology must be IN the gradients while it is being built.\n- *Open:* does the PLAIN CE gradient (no relational term) cast the same shadow?\n\n**The catch — gauge, and its fix (same as the activation tomography).** Raw `∂L/∂W` in\nweight coordinates is gauge-variant (the \"crumpled ground, randomly-rotated sun\"; cross-\ninit weight corr 0.000). Read it via the routing-register **relational Gram** (gauge-\ninvariant). The \"exact time and location\" = the per-combinator PROBE LABELS (which\ncombinator each gradient contribution belongs to) + the checkpoint weights (the\nJacobian). Known illumination + relational projection ⇒ inversion well-posed.\n\n**First-order shadow needs curvature to fully invert.** `∂L/∂g` is a first-order shadow\n(length); to invert to the CONVERGED topology (full height) you need the Hessian (the\nsun angle): `target ≈ current − H⁻¹g`. Gradient = leading direction; curvature = where\nit lands. Precisely \"shadow + known illumination → height.\"\n\n**★ The prediction that makes it worth building — the shadow LEADS the object.**\n`∂L/∂g` points toward the configuration GD is moving the activations toward ⇒ the\ngradient-Gram should resemble the FUTURE activation-Gram:\n\n> `gc_grad(t)` (gradient-shadow → consensus crystal) correlates with the crystal\n> EARLIER than `gc_route(t)` (activation-inventory) does.\n\n⇒ a THREE-STAGE cascade: **gradient-shadow (intent) → activation-inventory (geometry,\ns230 v1) → capability (usage).** A leading indicator: see where GD INTENDS to go before\nit arrives (early convergence prediction; detect wrong-basin aim before commitment).\n\n**Honest catches (λ measure):** (a) SNR — minibatch gradients are noisier than\nactivations; the shadow at dawn is long but faint → accumulate over many probes (√N,\ns105). (b) Reference beam again — a gradient-Gram could reflect input combinator\nCO-OCCURRENCE (common mode), not the function; control = raw-gradient-Gram vs routing-\ngradient-Gram (only routing should track + lead). (c) Frame residue — the Jacobian is\nitself gauge-variant; the relational Gram absorbs most but not provably all (state as\napproximate).\n\n**Build (ready to run):** extend the gd-trajectory harness — at each checkpoint, for\neach crystal probe backprop the probe LM loss to `g` at the capture layer, gather the\nlast-token gradient, build the per-combinator gradient-Gram → `gc_grad(t)`, log\nalongside `gc_route(t)` + a raw-gradient reference beam. Readout: does the shadow LEAD\nthe object (and capability)? Reuses `soft_gram` (it does not care if you feed it\nactivations or gradients).\n\n## Honest catches (λ measure)\n"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/gradient-trajectory-tomography.md.
```

### Thinking

I'm committing the gradient-shadow capture now, then moving on to build the probe.

## Assistant

Captured. Committing (you approved the capture):

### Tool Call: write_file (succeeded)


```json
{
  "path": "/tmp/shadow_page_commit.txt",
  "content": "🌀 gradient-trajectory-tomography §s230 v3 — the gradient-shadow probe (does topology leave a shadow?)\n\n- Michael's question (s230): if GD creates soft topology in the gradients, do the\n  gradients show a SHADOW of it (height-from-shadow with known illumination)?\n- Mathematically apt: gradient = structure projected through the Jacobian; shadow =\n  object projected through illumination; both invert with a known projector. ∂L/∂g\n  lives in the routing register (same coords as the activation topology).\n- Shadow exists: by construction (s230b relational grad IS topology-shaped) + by\n  timing (inventory built by gradients). Open: does plain CE grad cast it too?\n- Read via routing-register relational Gram (gauge-invariant); illumination =\n  per-combinator probe labels + checkpoint Jacobian; curvature (Hessian) inverts\n  first-order shadow to converged topology.\n- ★ PREDICTION: gradient-Gram LEADS activation-Gram ⇒ 3-stage cascade\n  shadow→inventory→capability (leading convergence indicator). Catches: SNR √N,\n  reference-beam common mode, frame residue.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /tmp/shadow_page_commit.txt
```

### Tool Call: git (succeeded)


```json
{
  "command": "git add mementum/knowledge/explore/gradient-trajectory-tomography.md && git commit -F /tmp/shadow_page_commit.txt",
  "operation": "commit",
  "summary": "commit gradient-shadow capture"
}
```

**Summary:** Git commit: commit gradient-shadow capture

**Output:**
```
Exit code: 0
Stdout:
[main 81f7072] 🌀 gradient-trajectory-tomography §s230 v3 — the gradient-shadow probe (does topology leave a shadow?)
 1 file changed, 64 insertions(+)
```

### Thinking

Now I'm setting up a new gradient-shadow probe script that builds on the existing trajectory tomography framework. The approach reuses the TinyLM training on the s229 curriculum, but extends it to measure gradient information alongside the activation geometry—for each crystal probe, I'll compute the CE loss and backpropagate to capture gradient-based insights.

The key technical challenge is extracting the gradient with respect to the gate activation. Since the gate is a non-leaf tensor returned from the model's forward pass, I need to call `retain_grad()` on it before backpropagating the probe loss, then gather the last-token gradient vector per probe to build per-combinator Gram matrices. The readout will check whether the gradient-based routing signal leads the activation-based routing and heldout accuracy across crossing steps.

Actually, using `torch.autograd.grad()` directly on the gate is cleaner — it avoids polluting the model's gradient buffers. For each probe batch, I compute the LM cross-entropy loss on the probe's own tokens, then extract the gate gradient via `torch.autograd.grad(loss, gate)`, gather the last-token component, and accumulate across batches to build the sign-CMR and raw-CMR Gram matrices for correlation against the consensus crystal.

Now I'm deciding whether to use signed or raw gradients for the routing-register shadow. The activation measurement used sign(gate)-CMR for routing and raw residual-CMR for the reference beam, so the natural parallel is sign(grad_gate)-CMR for the routing gradient shadow and the gradient w.r.t. hidden for the reference beam — which means I need to compute both `∂L/∂gate` and `∂L/∂hidden` in a single `torch.autograd.grad()` call.

The sign of the gradient captures the intended direction each gate dimension is being pushed, which mirrors how the consensus was built from sign patterns. I'll compute `gc_grad` using signed gate gradients and `gc_grad_raw` using raw hidden gradients, then apply the same measurement pipeline I use for activations — CMR silhouette and Gram matrix — but on the gradient tensors instead.

For the trajectory logs, I'll track both activation geometry (gc_route, route_z) and gradient geometry (gc_grad, grad_z, gc_grad_raw) at each checkpoint alongside heldout accuracy and cross-entropy, then examine whether gc_grad leads the activation metrics in crossing steps. I'll reuse the low-level helpers from the existing modules — CMR, Gram, centroids, silhouette, and correlation functions — and write a focused new script that imports these instruments plus the curriculum components to define a measure_shadow function and a training loop that logs both activation and gradient geometry.

Writing measure_shadow function... Building the loss computation...

The computational overhead per checkpoint is manageable—forward and backward passes on the probe batches take a second or two, plus another second for the activation geometry measurement, and that scales across thirty checkpoints and multiple seeds. For the training loop, I'll call both the geometry and shadow measurements at each snapshot, logging everything together. Then in the readout I'll track baseline-relative crossing steps for the gradient shadow, route geometry, and heldout accuracy, checking whether the shadow crosses before the route geometry, and whether that crosses before capability. I'll also compare the gradient shadow against the raw gradient to see if there's a meaningful difference. For multiple seeds I'll aggregate the ordering patterns and average the crossing steps.

One thing to be careful about: in eval mode, I need to make sure the gate and hidden activations retain their gradient information when I call autograd.grad on them. Since they're computed from model parameters that require gradients, they'll have the graph attached—but I shouldn't wrap this in a no_grad context. The training loop uses the optimizer, so I'll make sure the shadow measurement happens at checkpoints outside the main training step's gradient context. That keeps everything clean.

Writing the script now, reusing the data setup from the earlier trajectory work—same validation skeletons, fillings, corpus building, and eval items with the redex_nf format and varied k.

## Assistant

Page committed (`81f7072`). Now building the gradient-shadow probe (ready to run, won't touch main:1). Let me check the cascade is still healthy first, then build.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux capture-pane -p -t main:1 2>&1 | tail -3",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ tmux capture-pane -p -t main:1 2>&1...

**Output:**
```
Exit code: 0
Stdout:
=== seed 0 comp48  (48 compositions x 48 fillings = 2304 ex, corpus 81504 B) ===
```

### Thinking

The cascade is progressing well with the current component, so now I'm moving on to build the gradient-shadow probe by creating the gd_gradient_shadow.py module.

## Assistant

Cascade healthy (seed 0 comp48 now). Building the gradient-shadow probe:

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_gradient_shadow.py",
  "content": "#!/usr/bin/env python3\n# register: functional + topological/routing\n\"\"\"Gradient-shadow tomography (gd-trajectory v3) — does the routing topology cast a\nSHADOW in the gradients, and does the shadow LEAD the activation-inventory? (s230).\n\nTHE QUESTION (Michael, s230): \"If GD is creating soft topology in the gradients, do\nthe gradients show shadows of that? Height-from-shadow with known illumination.\"\n\nTHE MECHANISM (gradient-trajectory-tomography.md §s230 v3). The gate activation\ng = W_gate·h; the routing topology lives in g-space. The upstream gradient ∂L/∂g is a\nvector IN THE SAME g-space ⇒ the gradient-SHADOW and the activation-OBJECT are directly\ncommensurable. We read the shadow in the routing register (relational Gram, gauge-\ninvariant), with the per-combinator probe labels as the known illumination.\n\nTHE EXPERIMENT. CE-only TinyLM on the s229 β-reduction curriculum. At each checkpoint,\nin ADDITION to the activation geometry (gc_route, s230 v1), measure the GRADIENT-shadow:\nfor each crystal probe, backprop the probe's LM loss to g at the capture layer, gather\nthe last-token gradient, build the per-combinator gradient-Gram → gc_grad, correlate to\nthe CONSENSUS CRYSTAL. Raw-residual gradient = the reference-beam control (gc_grad_raw).\n\nFALSIFIABLE PREDICTION (the shadow LEADS): ∂L/∂g points toward where GD is moving the\nactivations ⇒ gc_grad(t) ≈ gc_route(t+Δ) ⇒ gc_grad crosses its baseline→final midpoint\nEARLIER than gc_route. ⇒ a THREE-STAGE cascade: gradient-shadow (intent) → activation-\ninventory (geometry) → capability (usage). If gc_grad does NOT lead, the gradient is a\ntrailing echo not a leading shadow.\n\nCatches (λ measure): SNR (minibatch grad noisier — √N over probes); reference beam\n(raw-grad-Gram common mode vs routing-grad-Gram); frame residue (Jacobian gauge).\n\nUsage:\n  uv run python scripts/experiments/gd_gradient_shadow.py --smoke\n  uv run python scripts/experiments/gd_gradient_shadow.py --seeds 0,1,2\n\nLicense: MIT\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport subprocess\nimport sys\nimport time\nfrom datetime import UTC, datetime\nfrom pathlib import Path\n\nimport numpy as np\nimport torch\nimport torch.nn.functional as F\n\n_SCRIPT_DIR = Path(__file__).resolve().parent\n_PROJECT_ROOT = _SCRIPT_DIR.parent.parent\nsys.path.insert(0, str(_PROJECT_ROOT / \"src\"))\nsys.path.insert(0, str(_SCRIPT_DIR))\n\nfrom exposure_format_sweep import (  # noqa: E402\n    SKELETONS,\n    TRAIN_ATOMS,\n    build_corpus,\n    build_eval_items,\n    eval_acc,\n    make_fillings,\n    to_byte_ids,\n    validate_skeletons,\n)\n\n# reuse the consensus loader + activation-geometry instrument + readout helpers\nfrom gd_trajectory_tomography import (  # noqa: E402\n    _final,\n    _first_step,\n    eff_dim,\n    load_consensus,\n    measure_geometry,\n)\nfrom relational_loss_distillation import (  # noqa: E402\n    CRYSTAL,\n    VOCAB,\n    TinyLM,\n    gather_last,\n    load_crystal_probe_batch,\n    np_centroids,\n    np_cmr,\n    np_gram,\n    np_silhouette_null,\n    offdiag_corr,\n)\n\nRESULTS_DIR = _PROJECT_ROOT / \"results\" / \"gd-gradient-shadow\"\n\n\ndef log(msg: str = \"\") -> None:\n    print(msg, file=sys.stderr, flush=True)\n\n\ndef git_sha() -> str:\n    try:\n        return subprocess.check_output(\n            [\"git\", \"rev-parse\", \"HEAD\"], cwd=_PROJECT_ROOT).decode().strip()\n    except Exception:\n        return \"unknown\"\n\n\n# --------------------------------------------------------------------------- #\n# The gradient-shadow: ∂(probe LM loss)/∂g, read in the routing register        #\n# --------------------------------------------------------------------------- #\ndef measure_shadow(model: TinyLM, p_ids: torch.Tensor, p_len: torch.Tensor,\n                   labels: np.ndarray, cap: int, consensus_gram: np.ndarray,\n                   n_perm: int, probe_batch: int, seed: int, device: str) -> dict:\n    \"\"\"For each probe, backprop its LM loss to the gate (routing) + residual (raw)\n    activations; gather the last-token gradient; build the per-combinator Gram and\n    correlate to the consensus crystal. NOT under no_grad — we need the graph.\"\"\"\n    model.eval()\n    grad_gate_feats, grad_hid_feats = [], []\n    for s in range(0, p_ids.shape[0], probe_batch):\n        pb = p_ids[s:s + probe_batch]\n        pl = p_len[s:s + probe_batch]\n        logits, hid, gate = model(pb, capture_layer=cap)\n        B, T, V = logits.shape\n        # masked LM CE on the probe's own tokens (predict t+1 from t, valid only)\n        shift_logits = logits[:, :-1, :].reshape(-1, V)\n        shift_tgt = pb[:, 1:].reshape(-1)\n        ce_tok = F.cross_entropy(shift_logits, shift_tgt, reduction=\"none\").reshape(\n            B, T - 1)\n        posn = torch.arange(T - 1, device=device)[None, :]\n        mask = (posn < (pl[:, None] - 1)).float()\n        loss = (ce_tok * mask).sum() / mask.sum().clamp_min(1.0)\n        g_gate, g_hid = torch.autograd.grad(loss, [gate, hid])\n        grad_gate_feats.append(gather_last(g_gate, pl).detach().cpu().numpy())\n        grad_hid_feats.append(gather_last(g_hid, pl).detach().cpu().numpy())\n    grad_gate_np = np.concatenate(grad_gate_feats, axis=0).astype(np.float64)\n    grad_hid_np = np.concatenate(grad_hid_feats, axis=0).astype(np.float64)\n\n    # routing-register shadow = sign(∂L/∂gate)-CMR (commensurate w/ consensus build)\n    sign_cmr = np_cmr(np.sign(grad_gate_np))\n    grad_sil = np_silhouette_null(sign_cmr, labels, n_perm, seed)\n    grad_gram = np_gram(np_centroids(sign_cmr, labels))\n    gc_grad = offdiag_corr(grad_gram, consensus_gram)\n\n    # raw-residual gradient = the reference-beam control\n    hid_cmr = np_cmr(grad_hid_np)\n    grad_gram_raw = np_gram(np_centroids(hid_cmr, labels))\n    gc_grad_raw = offdiag_corr(grad_gram_raw, consensus_gram)\n\n    return {\n        \"grad_z\": round(float(grad_sil[\"z\"]), 4),\n        \"gc_grad\": round(float(gc_grad), 4),\n        \"gc_grad_raw\": round(float(gc_grad_raw), 4),\n        \"grad_norm\": round(float(np.linalg.norm(grad_gate_np, axis=1).mean()), 6),\n    }\n\n\n# --------------------------------------------------------------------------- #\n# Readout — does the SHADOW lead the OBJECT (and capability)?                    #\n# --------------------------------------------------------------------------- #\ndef _order(a: int | None, b: int | None) -> str:\n    if a is None or b is None:\n        return \"n/a\"\n    return \"before\" if a < b else (\"after\" if a > b else \"same\")\n\n\ndef readout(curve: list[dict], init: dict, gc_frac: float, acc_frac: float) -> dict:\n    fin_grad = _final(curve, \"gc_grad\")\n    fin_route = _final(curve, \"gc_route\")\n    fin_acc = _final(curve, \"heldout_acc\")\n    g0, r0, a0 = (float(init[\"gc_grad\"]), float(init[\"gc_route\"]),\n                  float(init[\"heldout_acc\"]))\n    s_grad = (_first_step(curve, \"gc_grad\", g0 + gc_frac * (fin_grad - g0))\n              if fin_grad > g0 else None)\n    s_route = (_first_step(curve, \"gc_route\", r0 + gc_frac * (fin_route - r0))\n               if fin_route > r0 else None)\n    s_acc = (_first_step(curve, \"heldout_acc\", a0 + acc_frac * (fin_acc - a0))\n             if fin_acc > a0 else None)\n    return {\n        \"final\": {\"gc_grad\": round(fin_grad, 4), \"gc_route\": round(fin_route, 4),\n                  \"gc_grad_raw\": _final(curve, \"gc_grad_raw\"),\n                  \"heldout_acc\": round(fin_acc, 4), \"grad_z\": _final(curve, \"grad_z\")},\n        \"init_baseline\": {\"gc_grad\": init[\"gc_grad\"], \"gc_route\": init[\"gc_route\"],\n                          \"gc_grad_raw\": init[\"gc_grad_raw\"]},\n        \"step_gc_grad_cross\": s_grad,\n        \"step_gc_route_cross\": s_route,\n        \"step_heldout_acc_cross\": s_acc,\n        \"shadow_before_inventory\": _order(s_grad, s_route),\n        \"inventory_before_capability\": _order(s_route, s_acc),\n        \"shadow_before_capability\": _order(s_grad, s_acc),\n        \"shadow_gap\": round(fin_grad - _final(curve, \"gc_grad_raw\"), 4),\n    }\n\n\n# --------------------------------------------------------------------------- #\ndef train_seed(args, device: str, consensus_gram: np.ndarray, seed: int,\n               p_ids: torch.Tensor, p_len: torch.Tensor,\n               probe_labels: np.ndarray) -> dict:\n    torch.manual_seed(seed)\n    np.random.seed(seed)\n    rules = validate_skeletons(SKELETONS)\n    if args.smoke:\n        rules = rules[:4]\n    fill_rng = np.random.default_rng(seed)\n    train_fillings = {tmpl: make_fillings(fill_rng, h, TRAIN_ATOMS, args.k)\n                      for tmpl, h in rules}\n    corpus = build_corpus(rules, train_fillings, \"redex_nf\", \"k_varied\", args.k,\n                          np.random.default_rng(seed + 13))\n    eval_rng = np.random.default_rng(seed + 777)\n    eval_items = build_eval_items(rules, args.m_eval, eval_rng, TRAIN_ATOMS,\n                                  train_fillings)\n    log(f\"  [seed {seed}] rules={len(rules)} corpus={len(corpus.encode())} B \"\n        f\"heldout_eval={len(eval_items)}\")\n\n    ids = to_byte_ids(corpus)\n    T, bs = args.block_size, args.batch_size\n    while ids.shape[0] <= 4 * (T + 1):\n        ids = np.concatenate([ids, ids])\n    n = ids.shape[0]\n    model = TinyLM(args.d_model, args.n_head, args.n_layer, args.d_ff, T).to(device)\n    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)\n    cap = args.capture_layer if args.capture_layer >= 0 else args.n_layer // 2\n\n    curve: list[dict] = []\n    t0 = time.time()\n\n    def snapshot(step: int, ce_val: float) -> None:\n        acc = eval_acc(model, eval_items, T, device)\n        act = measure_geometry(model, p_ids, p_len, probe_labels, cap,\n                               consensus_gram, args.n_perm, args.probe_batch, seed)\n        shadow = measure_shadow(model, p_ids, p_len, probe_labels, cap,\n                                consensus_gram, args.n_perm, args.probe_batch, seed,\n                                device)\n        row = {\"step\": step, \"ce\": round(ce_val, 4), \"heldout_acc\": round(acc, 4),\n               \"gc_route\": act[\"gc_route\"], \"route_z\": act[\"route_z\"],\n               \"eff_dim_route\": act[\"eff_dim_route\"], **shadow}\n        curve.append(row)\n        log(f\"  [s{seed}] step {step:5d} | CE {ce_val:.3f} | acc {acc:.3f} \"\n            f\"| gc_grad {shadow['gc_grad']:+.3f} (raw {shadow['gc_grad_raw']:+.3f}) \"\n            f\"| gc_route {act['gc_route']:+.3f} | grad_z {shadow['grad_z']:+.2f} \"\n            f\"| {time.time()-t0:.0f}s\")\n\n    snapshot(0, float(\"nan\"))\n    for step in range(1, args.steps + 1):\n        model.train()\n        ix = torch.randint(0, n - T - 1, (bs,))\n        xb = torch.stack([torch.from_numpy(ids[i:i + T]) for i in ix]).to(device)\n        yb = torch.stack(\n            [torch.from_numpy(ids[i + 1:i + 1 + T]) for i in ix]).to(device)\n        logits, _, _ = model(xb)\n        ce = F.cross_entropy(logits.reshape(-1, VOCAB), yb.reshape(-1))\n        opt.zero_grad()\n        ce.backward()\n        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)\n        opt.step()\n        if step % args.ckpt_every == 0 or step == args.steps:\n            snapshot(step, float(ce.item()))\n\n    init_frame = curve[0]\n    rd = readout([r for r in curve if not (isinstance(r[\"ce\"], float)\n                                           and np.isnan(r[\"ce\"]))],\n                 init_frame, args.gc_frac, args.acc_frac)\n    return {\"seed\": seed, \"capture_layer\": cap, \"curve\": curve, \"readout\": rd,\n            \"eff_dim_final\": eff_dim(np.zeros((2, 2)))}  # placeholder not used\n\n\ndef _ms(vals: list) -> list:\n    a = np.array([v for v in vals if v is not None], dtype=float)\n    if a.size == 0:\n        return [None, None]\n    return [round(float(a.mean()), 2), round(float(a.std()), 2)]\n\n\ndef main() -> None:\n    ap = argparse.ArgumentParser()\n    ap.add_argument(\"--device\", default=\"mps\")\n    ap.add_argument(\"--steps\", type=int, default=6000)\n    ap.add_argument(\"--ckpt-every\", type=int, default=200)\n    ap.add_argument(\"--batch-size\", type=int, default=32)\n    ap.add_argument(\"--block-size\", type=int, default=128)\n    ap.add_argument(\"--d-model\", type=int, default=128)\n    ap.add_argument(\"--n-head\", type=int, default=4)\n    ap.add_argument(\"--n-layer\", type=int, default=4)\n    ap.add_argument(\"--d-ff\", type=int, default=256)\n    ap.add_argument(\"--capture-layer\", type=int, default=-1)\n    ap.add_argument(\"--lr\", type=float, default=3e-4)\n    ap.add_argument(\"--k\", type=int, default=8)\n    ap.add_argument(\"--m-eval\", type=int, default=6)\n    ap.add_argument(\"--probe-batch\", type=int, default=64)\n    ap.add_argument(\"--probe-max-len\", type=int, default=96)\n    ap.add_argument(\"--n-perm\", type=int, default=300)\n    ap.add_argument(\"--gc-frac\", type=float, default=0.5)\n    ap.add_argument(\"--acc-frac\", type=float, default=0.5)\n    ap.add_argument(\"--seed\", type=int, default=0)\n    ap.add_argument(\"--seeds\", default=\"\")\n    ap.add_argument(\"--smoke\", action=\"store_true\")\n    args = ap.parse_args()\n\n    if args.smoke:\n        args.steps, args.ckpt_every = 120, 40\n        args.k, args.m_eval, args.n_perm = 4, 3, 100\n        args.d_model, args.d_ff, args.n_layer = 64, 128, 3\n\n    device = args.device\n    if device == \"mps\" and not torch.backends.mps.is_available():\n        device = \"cpu\"\n        log(\"  mps unavailable -> cpu\")\n    if device == \"cuda\" and not torch.cuda.is_available():\n        device = \"cpu\"\n\n    RESULTS_DIR.mkdir(parents=True, exist_ok=True)\n    t0 = time.time()\n\n    consensus_gram, cmeta = load_consensus()\n    log(f\"  consensus crystal: {cmeta['n_models']} models, sha=\"\n        f\"{cmeta['consensus_git_sha']}\")\n    probe_ids, probe_len, probe_labels = load_crystal_probe_batch(args.probe_max_len)\n    p_ids = torch.tensor(probe_ids, device=device)\n    p_len = torch.tensor(probe_len, device=device)\n    log(f\"  crystal probes={probe_ids.shape[0]}\")\n\n    seeds = [int(s) for s in args.seeds.split(\",\") if s.strip()] or [args.seed]\n    log(f\"  seeds={seeds} steps={args.steps} ckpt_every={args.ckpt_every}\")\n    runs = [train_seed(args, device, consensus_gram, sd, p_ids, p_len, probe_labels)\n            for sd in seeds]\n\n    meta = {\n        \"experiment\": \"gd-gradient-shadow\",\n        \"register\": \"functional + topological/routing\",\n        \"idea\": \"does the routing topology cast a SHADOW in the gradients, and does \"\n                \"the shadow LEAD the activation-inventory? (gd-trajectory v3)\",\n        \"timestamp_utc\": datetime.now(UTC).isoformat(),\n        \"git_sha\": git_sha(), \"device\": device, \"smoke\": args.smoke,\n        \"config\": vars(args), \"consensus\": cmeta, \"seeds\": seeds,\n        \"elapsed_s\": round(time.time() - t0, 1),\n    }\n\n    rds = [r[\"readout\"] for r in runs]\n    agg = {\n        \"n_seeds\": len(seeds),\n        \"step_gc_grad_cross\": _ms([r[\"step_gc_grad_cross\"] for r in rds]),\n        \"step_gc_route_cross\": _ms([r[\"step_gc_route_cross\"] for r in rds]),\n        \"step_heldout_acc_cross\": _ms([r[\"step_heldout_acc_cross\"] for r in rds]),\n        \"gc_grad_final\": _ms([r[\"final\"][\"gc_grad\"] for r in rds]),\n        \"gc_route_final\": _ms([r[\"final\"][\"gc_route\"] for r in rds]),\n        \"gc_grad_raw_final\": _ms([r[\"final\"][\"gc_grad_raw\"] for r in rds]),\n        \"shadow_before_inventory\": [r[\"shadow_before_inventory\"] for r in rds],\n        \"shadow_before_capability\": [r[\"shadow_before_capability\"] for r in rds],\n        \"inventory_before_capability\": [r[\"inventory_before_capability\"] for r in rds],\n        \"shadow_gap\": _ms([r[\"shadow_gap\"] for r in rds]),\n    }\n    tag = \"smoke\" if args.smoke else (\"multiseed\" if len(seeds) > 1 else \"run\")\n    out = {**meta, \"aggregate\": agg, \"runs\": runs}\n    (RESULTS_DIR / f\"verdict_{tag}.json\").write_text(json.dumps(out, indent=2))\n\n    log(\"\\n  ==== GRADIENT-SHADOW TOMOGRAPHY (does the shadow LEAD?) ====\")\n    log(f\"  cross steps (baseline-relative): gc_grad@{agg['step_gc_grad_cross']} \"\n        f\"gc_route@{agg['step_gc_route_cross']} acc@{agg['step_heldout_acc_cross']}\")\n    log(f\"  finals: gc_grad={agg['gc_grad_final']} gc_route={agg['gc_route_final']} \"\n        f\"gc_grad_raw(refbeam)={agg['gc_grad_raw_final']} shadow_gap={agg['shadow_gap']}\")\n    log(f\"  SHADOW before INVENTORY (gc_grad<gc_route): \"\n        f\"{agg['shadow_before_inventory']}\")\n    log(f\"  SHADOW before CAPABILITY: {agg['shadow_before_capability']}\")\n    log(f\"  3-stage cascade = shadow→inventory→capability if both 'before'\")\n    log(f\"\\n  wrote {RESULTS_DIR / f'verdict_{tag}.json'}  ({meta['elapsed_s']}s)\")\n\n\nif __name__ == \"__main__\":\n    main()\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/experiments/gd_gradient_shadow.py
```

### Thinking

I've got a leftover placeholder in the train_seed return that's importing eff_dim just for that one unused line. Since measure_geometry already computes and logs eff_dim_route, I'll clean this up by removing both the placeholder and the unnecessary import.

## Assistant

Let me clean up a leftover placeholder before linting:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_gradient_shadow.py",
  "original_content": "    return {\"seed\": seed, \"capture_layer\": cap, \"curve\": curve, \"readout\": rd,\n            \"eff_dim_final\": eff_dim(np.zeros((2, 2)))}  # placeholder not used",
  "new_content": "    return {\"seed\": seed, \"capture_layer\": cap, \"curve\": curve, \"readout\": rd}"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/gd_gradient_shadow.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_gradient_shadow.py",
  "original_content": "from gd_trajectory_tomography import (  # noqa: E402\n    _final,\n    _first_step,\n    eff_dim,\n    load_consensus,\n    measure_geometry,\n)",
  "new_content": "from gd_trajectory_tomography import (  # noqa: E402\n    _final,\n    _first_step,\n    load_consensus,\n    measure_geometry,\n)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/gd_gradient_shadow.py.
```

### Thinking

I'm thinking through the resource contention between running the smoke tests on CPU while the cascade runs on MPS—since they're on different devices, there shouldn't be much conflict. The smoke test is quick at 120 steps with a tiny model, so running it on CPU should work fine. I was starting to consider something about autograd.grad but got cut off.

Let me verify that measure_shadow will work correctly. The function calls model.eval() and then uses autograd.grad to compute gradients of the loss with respect to the captured gate and hidden tensors. Since these intermediate tensors are part of the computation graph leading to the logits, the gradient computation should work as expected. Even in the edge case where the capture layer is the last layer, the gate and hidden values still feed into the final output, so the gradients should compute properly.

I'll go ahead and run ruff plus the smoke tests on CPU.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/gd_gradient_shadow.py 2>&1 | tail -15",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
|

F541 [*] f-string without any placeholders
   --> scripts/experiments/gd_gradient_shadow.py:356:9
    |
354 |         f"{agg['shadow_before_inventory']}")
355 |     log(f"  SHADOW before CAPABILITY: {agg['shadow_before_capability']}")
356 |     log(f"  3-stage cascade = shadow→inventory→capability if both 'before'")
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
357 |     log(f"\n  wrote {RESULTS_DIR / f'verdict_{tag}.json'}  ({meta['elapsed_s']}s)")
    |
help: Remove extraneous `f` prefix

Found 3 errors.
[*] 2 fixable with the `--fix` option.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check --fix scripts/experiments/gd_gradient_shadow.py 2>&1 | tail -15",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ uv run ruff check --fix scripts/exp...

**Output:**
```
Exit code: 0
Stdout:
E501 Line too long (90 > 88)
   --> scripts/experiments/gd_gradient_shadow.py:351:89
    |
349 |         f"gc_route@{agg['step_gc_route_cross']} acc@{agg['step_heldout_acc_cross']}")
350 |     log(f"  finals: gc_grad={agg['gc_grad_final']} gc_route={agg['gc_route_final']} "
351 |         f"gc_grad_raw(refbeam)={agg['gc_grad_raw_final']} shadow_gap={agg['shadow_gap']}")
    |                                                                                         ^^
352 |     log(f"  SHADOW before INVENTORY (gc_grad<gc_route): "
353 |         f"{agg['shadow_before_inventory']}")
    |

Found 3 errors (2 fixed, 1 remaining).
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_gradient_shadow.py",
  "original_content": "    log(f\"  finals: gc_grad={agg['gc_grad_final']} gc_route={agg['gc_route_final']} \"\n        f\"gc_grad_raw(refbeam)={agg['gc_grad_raw_final']} shadow_gap={agg['shadow_gap']}\")",
  "new_content": "    log(f\"  finals: gc_grad={agg['gc_grad_final']} gc_route={agg['gc_route_final']} \"\n        f\"gc_grad_raw(refbeam)={agg['gc_grad_raw_final']} \"\n        f\"shadow_gap={agg['shadow_gap']}\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/gd_gradient_shadow.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/gd_gradient_shadow.py && echo \"RUFF CLEAN\" && uv run python scripts/experiments/gd_gradient_shadow.py --smoke --device cpu 2>&1 | tail -16",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 240000
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
RUFF CLEAN
  crystal probes=535
  seeds=[0] steps=120 ckpt_every=40
  [seed 0] rules=4 corpus=200 B heldout_eval=12
  [s0] step     0 | CE nan | acc 0.000 | gc_grad +0.000 (raw +0.000) | gc_route +0.489 | grad_z +0.00 | 3s
  [s0] step    40 | CE 3.407 | acc 0.000 | gc_grad +0.000 (raw +0.000) | gc_route +0.524 | grad_z +0.00 | 8s
  [s0] step    80 | CE 1.885 | acc 0.000 | gc_grad +0.000 (raw +0.000) | gc_route +0.494 | grad_z +0.00 | 13s
  [s0] step   120 | CE 1.388 | acc 0.000 | gc_grad +0.000 (raw +0.000) | gc_route +0.518 | grad_z +0.00 | 17s

  ==== GRADIENT-SHADOW TOMOGRAPHY (does the shadow LEAD?) ====
  cross steps (baseline-relative): gc_grad@[None, None] gc_route@[40.0, 0.0] acc@[None, None]
  finals: gc_grad=[0.0, 0.0] gc_route=[0.52, 0.0] gc_grad_raw(refbeam)=[0.0, 0.0] shadow_gap=[0.0, 0.0]
  SHADOW before INVENTORY (gc_grad<gc_route): ['n/a']
  SHADOW before CAPABILITY: ['n/a']
  3-stage cascade = shadow→inventory→capability if both 'before'

  wrote /Users/mwhitford/src/verbum/results/gd-gradient-shadow/verdict_smoke.json  (17.5s)
```

### Thinking

The end-to-end run completed, but I'm seeing zero gradients everywhere—the gradient-shadow measurements are all coming back as zero, which signals a bug rather than a real result. Tracing back through the logic: the grad_gate features are zero, which means sign(0) produces zero, leading to a degenerate Gram matrix, and the correlation calculation hits its guard condition and returns 0.0 when the standard deviation falls below the threshold. The gradient computation is breaking down somewhere in this chain.

I'm realizing the core issue: the gradient with respect to the gate at the last token position is zero because the loss only spans positions [0, len-2]—it predicts position t+1 from position t for valid positions only. The last real token at position len-1 serves as input to predict position len, but I masked that prediction out (the mask excludes position len-1 as a predictor), so the last token's gate never actually contributes to the loss. That's why its gradient is zero.

I'm weighing two fixes: either gather the gradient at position len-2 (the last position that actually contributes to the loss) or restructure the loss to include the last token's prediction. The cleaner approach would be to include the last token's prediction in the loss so the gradient signal at that position becomes meaningful and aligns with the activation measurements I'm taking. Instead of gathering the gradient only at the last position, I should mean-pool it across all valid positions in the probe—the ones that actually contribute to the loss. This gives a richer signal that reflects how the loss wants to reshape the routing across the entire sequence, rather than just at one point. Computing the pooled gradient vector per probe by masking out invalid positions and averaging gives a more robust measurement that's commensurate with the activation topology. Implementing the mean-pool fix... Updating the docstring and removing the gather_last import since it's no longer needed in this function, then rewriting the loop to use masked mean-pooling over the supervised positions instead.

## Assistant

Bug caught in the smoke: `gc_grad` is **zero everywhere**. Root cause — I gather the gradient at the *last* token (position `len-1`), but that position only feeds the *unsupervised* next-token prediction (which I masked out), so its gradient is exactly zero. The fix: mean-pool the gradient over the **supervised** predictor positions (also better SNR, the √N point). Let me rewrite `measure_shadow`.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_gradient_shadow.py",
  "original_content": "    model.eval()\n    grad_gate_feats, grad_hid_feats = [], []\n    for s in range(0, p_ids.shape[0], probe_batch):\n        pb = p_ids[s:s + probe_batch]\n        pl = p_len[s:s + probe_batch]\n        logits, hid, gate = model(pb, capture_layer=cap)\n        B, T, V = logits.shape\n        # masked LM CE on the probe's own tokens (predict t+1 from t, valid only)\n        shift_logits = logits[:, :-1, :].reshape(-1, V)\n        shift_tgt = pb[:, 1:].reshape(-1)\n        ce_tok = F.cross_entropy(shift_logits, shift_tgt, reduction=\"none\").reshape(\n            B, T - 1)\n        posn = torch.arange(T - 1, device=device)[None, :]\n        mask = (posn < (pl[:, None] - 1)).float()\n        loss = (ce_tok * mask).sum() / mask.sum().clamp_min(1.0)\n        g_gate, g_hid = torch.autograd.grad(loss, [gate, hid])\n        grad_gate_feats.append(gather_last(g_gate, pl).detach().cpu().numpy())\n        grad_hid_feats.append(gather_last(g_hid, pl).detach().cpu().numpy())",
  "new_content": "    model.eval()\n    grad_gate_feats, grad_hid_feats = [], []\n    for s in range(0, p_ids.shape[0], probe_batch):\n        pb = p_ids[s:s + probe_batch]\n        pl = p_len[s:s + probe_batch]\n        logits, hid, gate = model(pb, capture_layer=cap)\n        B, T, V = logits.shape\n        # masked LM CE on the probe's own tokens (predict t+1 from t, valid only)\n        shift_logits = logits[:, :-1, :].reshape(-1, V)\n        shift_tgt = pb[:, 1:].reshape(-1)\n        ce_tok = F.cross_entropy(shift_logits, shift_tgt, reduction=\"none\").reshape(\n            B, T - 1)\n        posn = torch.arange(T - 1, device=device)[None, :]\n        mask = (posn < (pl[:, None] - 1)).float()\n        loss = (ce_tok * mask).sum() / mask.sum().clamp_min(1.0)\n        g_gate, g_hid = torch.autograd.grad(loss, [gate, hid])\n        # mean-pool the gradient over SUPERVISED predictor positions [0, len-2].\n        # (the last token len-1 feeds only the unsupervised next-token => grad 0\n        #  there; pooling over supervised positions is nonzero AND denoises, √N.)\n        pmask = (torch.arange(T, device=device)[None, :] < (pl[:, None] - 1)).float()\n        denom = pmask.sum(1, keepdim=True).clamp_min(1.0)\n        pooled_gate = (g_gate * pmask[..., None]).sum(1) / denom\n        pooled_hid = (g_hid * pmask[..., None]).sum(1) / denom\n        grad_gate_feats.append(pooled_gate.detach().cpu().numpy())\n        grad_hid_feats.append(pooled_hid.detach().cpu().numpy())"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/gd_gradient_shadow.py.
```

### Thinking

I see that `gather_last` is no longer needed in this file since `measure_shadow` was just refactored to use a different approach, so I should remove the unused import to clear the F401 warning. I'll also update the docstrings to reflect the actual behavior — changing "gather the last-token gradient" to "mean-pool the gradient over supervised positions" for both `measure_shadow` and its related documentation.

### Tool Call: edit_file (failed)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_gradient_shadow.py",
  "original_content": "from relational_loss_distillation import (  # noqa: E402\n    CRYSTAL,\n    VOCAB,\n    TinyLM,\n    gather_last,\n    load_crystal_probe_batch,\n    np_centroids,\n    np_cmr,\n    np_gram,\n    np_silhouette_null,\n    offdiag_corr,\n)",
  "new_content": "from relational_loss_distillation import (  # noqa: E402\n    CRYSTAL,\n    VOCAB,\n    TinyLM,\n    load_crystal_probe_batch,\n    np_centroids,\n    np_cmr,\n    np_gram,\n    np_silhouette_null,\n    offdiag_corr,\n)"
}
```

**Summary:** Editing

**Output:**
```
Original content not found in /Users/mwhitford/src/verbum/scripts/experiments/gd_gradient_shadow.py
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_gradient_shadow.py",
  "original_content": "    \"\"\"For each probe, backprop its LM loss to the gate (routing) + residual (raw)\n    activations; gather the last-token gradient; build the per-combinator Gram and\n    correlate to the consensus crystal. NOT under no_grad — we need the graph.\"\"\"",
  "new_content": "    \"\"\"For each probe, backprop its LM loss to the gate (routing) + residual (raw)\n    activations; MEAN-POOL the gradient over supervised positions; build the per-\n    combinator Gram and correlate to the consensus crystal. NOT under no_grad.\"\"\""
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/gd_gradient_shadow.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_gradient_shadow.py",
  "original_content": "THE EXPERIMENT. CE-only TinyLM on the s229 β-reduction curriculum. At each checkpoint,\nin ADDITION to the activation geometry (gc_route, s230 v1), measure the GRADIENT-shadow:\nfor each crystal probe, backprop the probe's LM loss to g at the capture layer, gather\nthe last-token gradient, build the per-combinator gradient-Gram → gc_grad, correlate to\nthe CONSENSUS CRYSTAL. Raw-residual gradient = the reference-beam control (gc_grad_raw).",
  "new_content": "THE EXPERIMENT. CE-only TinyLM on the s229 β-reduction curriculum. At each checkpoint,\nin ADDITION to the activation geometry (gc_route, s230 v1), measure the GRADIENT-shadow:\nfor each crystal probe, backprop the probe's LM loss to g at the capture layer, mean-\npool the gradient over supervised positions, build the per-combinator gradient-Gram →\ngc_grad, correlate to the CONSENSUS CRYSTAL. Raw-residual grad = reference beam.\n(NB the last token feeds only the unsupervised next-token => zero grad there; we pool\nover the supervised predictor positions, which is nonzero and denoises √N.)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/gd_gradient_shadow.py.
```

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/gd_gradient_shadow.py && echo \"RUFF CLEAN\" && uv run python scripts/experiments/gd_gradient_shadow.py --smoke --device cpu 2>&1 | tail -14",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 240000
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 1
Stdout:
F401 [*] `relational_loss_distillation.gather_last` imported but unused
  --> scripts/experiments/gd_gradient_shadow.py:79:5
   |
77 |     VOCAB,
78 |     TinyLM,
79 |     gather_last,
   |     ^^^^^^^^^^^
80 |     load_crystal_probe_batch,
81 |     np_centroids,
   |
help: Remove unused import: `relational_loss_distillation.gather_last`

Found 1 error.
[*] 1 fixable with the `--fix` option.
```

### Thinking

The first edit to remove the import didn't apply—it reported "Original content not found"—but ruff still flags gather_last as unused, so I'll just use ruff --fix to clean it up directly.

## Assistant

The import edit didn't match (the docstring edits applied). Let me just let ruff remove the unused import:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check --fix scripts/experiments/gd_gradient_shadow.py && echo \"RUFF CLEAN\" && uv run python scripts/experiments/gd_gradient_shadow.py --smoke --device cpu 2>&1 | tail -14",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 240000
}
```

**Summary:** $ uv run ruff check --fix scripts/exp...

**Output:**
```
Exit code: 0
Stdout:
Found 1 error (1 fixed, 0 remaining).
RUFF CLEAN
  [seed 0] rules=4 corpus=200 B heldout_eval=12
  [s0] step     0 | CE nan | acc 0.000 | gc_grad +0.535 (raw +0.458) | gc_route +0.489 | grad_z +4.88 | 3s
  [s0] step    40 | CE 3.407 | acc 0.000 | gc_grad +0.608 (raw +0.456) | gc_route +0.524 | grad_z +5.37 | 8s
  [s0] step    80 | CE 1.885 | acc 0.000 | gc_grad +0.570 (raw +0.534) | gc_route +0.494 | grad_z +1.43 | 12s
  [s0] step   120 | CE 1.388 | acc 0.000 | gc_grad +0.527 (raw +0.340) | gc_route +0.518 | grad_z +1.76 | 17s

  ==== GRADIENT-SHADOW TOMOGRAPHY (does the shadow LEAD?) ====
  cross steps (baseline-relative): gc_grad@[None, None] gc_route@[40.0, 0.0] acc@[None, None]
  finals: gc_grad=[0.53, 0.0] gc_route=[0.52, 0.0] gc_grad_raw(refbeam)=[0.34, 0.0] shadow_gap=[0.19, 0.0]
  SHADOW before INVENTORY (gc_grad<gc_route): ['n/a']
  SHADOW before CAPABILITY: ['n/a']
  3-stage cascade = shadow→inventory→capability if both 'before'

  wrote /Users/mwhitford/src/verbum/results/gd-gradient-shadow/verdict_smoke.json  (16.9s)
```

### Thinking

The gradient-Gram correlations are showing meaningful structure now, with the consensus crystal correlation around 0.53-0.61 while the raw gradient sits lower at 0.34-0.53, and there's a notable routing gap of +0.19 between them. What's striking is the gradient's z-values jumping to +4.88 to +5.37 early on, suggesting strong combinator-silhouette structure is already present at initialization.

Even in this small smoke test, the machinery is working — the gradient-shadow is real and correlates to the consensus crystal. The full run will reveal the timing dynamics. But there's a puzzle worth sitting with: at random initialization, gc_grad is already 0.535 with grad_z at 4.88, which could mean the gradient is picking up the input data's own combinator structure rather than learned function structure. The gc_grad_raw reference beam helps distinguish this — the gap between them suggests the routing gradient carries more signal than the raw residual, but I need the full run to be confident about what's driving the initial correlation.

The probe is built, passes lint, and produces meaningful signal. It's ready to run. I'll commit the probe script now since it's code-ready, then check cascade progress and report status.

## Assistant

The gradient-shadow machinery now works — **`gc_grad` ≈ 0.53–0.61 correlates to the consensus crystal**, `gc_grad_raw` (reference beam) lower at ~0.34, gap +0.19, and `grad_z` is strikingly high (+4.9). The crossing readout is n/a only because smoke is too short. It's lint-clean, diagnostics-clean, and ready to run.

One honest note already visible: even at random init the gradient shows combinator structure (gc_grad +0.535) — that's the reference-beam/common-mode concern (the gradient partly reflects *which combinator is in the prompt*, not just the function being built). The baseline-relative crossings + the `gc_grad_raw` control are exactly there to disentangle it; the full run will tell.

Let me verify diagnostics, clean up, commit the probe, and check the cascade.

### Tool Call: editor_diagnostics (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gd_gradient_shadow.py"
}
```

**Summary:** Checking diagnostics: gd_gradient_shadow.py

**Output:**
```
No diagnostics found
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "rm -f /Users/mwhitford/src/verbum/results/gd-gradient-shadow/verdict_smoke.json; echo \"=== cascade progress ===\"; tmux capture-pane -p -t main:1 2>&1 | tail -4",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ rm -f /Users/mwhitford/src/verbum/r...

**Output:**
```
Exit code: 0
Stdout:
=== cascade progress ===
  [comp144] step  2000 | CE 0.939 | heldout_comp 0.000 | in_dist 0.000 | 66s
  [comp144] step  3000 | CE 0.899 | heldout_comp 0.000 | in_dist 0.000 | 94s
  [comp144] step  4000 | CE 0.866 | heldout_comp 0.000 | in_dist 0.000 | 120s
```

### Thinking

I'm noticing something troubling with the cascade at seed 0, comp144, step 4000 — both the held-out and in-distribution accuracies are stuck at zero despite the cross-entropy loss dropping from 0.939 to 0.866. The model isn't learning to generate correct normal forms at all, even on examples it should be seeing during training. With comp144 containing 2304 examples and the in-distribution control using 20 train templates with held-out fillings, zero accuracy suggests something fundamental is broken in how the model is learning the task.

The cross-entropy of 0.866 nats per byte is nowhere near as good as the 13-rule curriculum baseline (which reached ~0.04), and the math is sobering — at that uncertainty level, the probability of generating an exact 8-character normal form correctly is vanishingly small, around 0.001. So the zero exact-match accuracy makes sense given the loss, but the real concern is whether any of the composition arms are actually learning anything. I need to check the earlier comp16 and comp48 results in the log to see if they produced any nonzero accuracy, because if all arms stay at zero, the entire run is wasted with no signal.

## Assistant

Concern: comp144 is at step 4000 with **both heldout and in-dist still 0.000** — the model may not be learning the composition task at all (CE 0.87 is far from s229's ~0.04). If every arm flatlines at 0, there's no signal. Let me check whether the earlier arms (comp16, comp48) got any traction.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -E \"comp(16|48|144)\\] step\" /tmp/compiler_cascade_s230.log | grep -E \"step  6000|step  5000\" | head; echo \"=== any nonzero acc anywhere? ===\"; grep -E \"in_dist [1-9]|heldout_comp [1-9]|in_dist 0.0[1-9]|heldout_comp 0.0[1-9]\" /tmp/compiler_cascade_s230.log | head",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ grep -E "comp(16|48|144)\] step" /t...

**Output:**
```
Exit code: 0
Stdout:
[comp16] step  5000 | CE 0.720 | heldout_comp 0.000 | in_dist 0.000 | 112s
  [comp16] step  6000 | CE 0.685 | heldout_comp 0.000 | in_dist 0.000 | 136s
  [comp48] step  5000 | CE 0.779 | heldout_comp 0.000 | in_dist 0.000 | 144s
  [comp48] step  6000 | CE 0.770 | heldout_comp 0.000 | in_dist 0.000 | 169s
  [comp144] step  5000 | CE 0.845 | heldout_comp 0.000 | in_dist 0.000 | 146s
=== any nonzero acc anywhere? ===
  [comp16] step  2000 | CE 0.746 | heldout_comp 0.000 | in_dist 0.021 | 45s
```

### Thinking

The model isn't learning the composition task at all—accuracy is essentially zero across the board except for one lucky hit at step 2000, and the cross-entropy loss is plateauing around 0.68-0.85, which suggests the byte-level TinyLM with these dimensions just can't pick up the signal needed for this task.

This isn't a real finding about whether high-variety helps; it's a calibration failure where everything floors at zero. The task is fundamentally harder than the simpler fixed-rule experiment—the model needs to generalize reduction algebra across 144 different composition structures and match an 8-character normal form exactly, which requires much lower loss than what we're seeing. I could fix this by making the task easier with shallower compositions or fewer combinators, scaling up the model capacity, running longer (though the plateau suggests it's stuck rather than just slow), using a softer evaluation metric, or adding curriculum learning with intermediate reduction steps to scaffold the learning. I need to kill this run since it's clearly not producing useful signal. The model can't even learn the in-distribution examples, which means the composition space is too complex. My plan: recalibrate to simpler compositions (depth 2, fewer holes, shorter normal forms), bump up model capacity to d=192 with 4 layers, and run for 8000 steps. Before committing to another long multi-seed experiment, I'll do a quick diagnostic run on a single arm with these easier settings to confirm the model can actually learn in-distribution before scaling up. So the key insight is that s229 learned 13 rules with NF complexity up to ~13 characters, and my composition pool has similar NF complexity but spread across 144 distinct structures with fewer examples per structure. The real test is whether the model can learn the reduction rule compositionally across many structures—if even comp16 floors at in_dist 0, that's a capacity problem requiring a bigger model. Let me kill the cascade, bump up to d=192, use simpler compositions (nf≤12, holes 2-4, depth 2), run a quick single-arm probe with comp32 at ~3000 steps, and see if in_dist climbs before relaunching the full sweep.

## Assistant

This is a **floor** — every arm is stuck at ~0 accuracy (CE plateauing ~0.7, far from s229's ~0.04). The byte model at d=128 can't learn arbitrary {K,I,B,C} composition-reduction to exact-match. That's a calibration failure, not a verdict — a floored experiment says nothing about the hypothesis. Let me kill it and find a learnable regime before burning another full run.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux send-keys -t main:1 C-c; sleep 2; echo \"killed\"; tmux capture-pane -p -t main:1 2>&1 | tail -2",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ tmux send-keys -t main:1 C-c; sleep...

**Output:**
```
Exit code: 0
Stdout:
killed
[26-06-15][10:23:41][mwhitford@olga][0][~/src/verbum][git:main]
λ                                                                                                                 [INS]
```

### Thinking

I'm setting up a viability test with simpler compositions and a larger model using a single arm configuration to see if the in-distribution performance improves. I'll run it in the foreground with time constraints, using specific parameter overrides like 32 arm levels, 3000 steps, and a 192-dimensional model. I need to check the in_dist metric once it completes, though I'm noticing the script's generation function now defaults to max_depth of 3.

For the easier targets, I'll keep the depth at 3 but constrain the NF length to 12 and set holes between 2-4 with 2-3 steps maximum. I'll run this on the MPS device since the cascade is unavailable, bounded to around 4 minutes. The real question is whether a bigger model actually helps enough—exact-match NF requires very low per-byte cross-entropy, and even the best previous run only hit 0.27. For compositions, maybe 0.1-0.2 is achievable with easier targets, and as long as there's clear separation between arms, the experiment will tell me what I need to know. Let me run the probe.

## Assistant

Recalibrating to a learnable regime: simpler compositions (shorter NFs, fewer steps) + bigger model. Let me run a quick foreground viability probe (one arm) before committing another full sweep.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && timeout 300 uv run python scripts/experiments/compiler_cascade.py --arm-levels \"32\" --seeds 0 --steps 3000 --eval-every 500 --min-holes 2 --max-holes 4 --max-steps 3 --max-nf-len 12 --d-model 192 --d-ff 384 --budget 2304 --device mps 2>&1 | tail -14",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 320000
}
```

**Summary:** $ timeout 300 uv run python scripts/e...

**Output:**
```
Exit code: 0
Stdout:
=== seed 0 comp32  (32 compositions x 72 fillings = 2304 ex, corpus 68256 B) ===
  [comp32] step   500 | CE 0.877 | heldout_comp 0.017 | in_dist 0.050 | 10s
  [comp32] step  1000 | CE 0.691 | heldout_comp 0.017 | in_dist 0.033 | 21s
  [comp32] step  1500 | CE 0.676 | heldout_comp 0.000 | in_dist 0.050 | 31s
  [comp32] step  2000 | CE 0.644 | heldout_comp 0.000 | in_dist 0.050 | 41s
  [comp32] step  2500 | CE 0.670 | heldout_comp 0.000 | in_dist 0.050 | 51s
  [comp32] step  3000 | CE 0.643 | heldout_comp 0.000 | in_dist 0.033 | 62s

  ==== COMPILER-CASCADE v1 — COMPOSITION-VARIETY -> GENERALIZATION ====
  arm         comps  fills   heldout_comp(mean±std)          in_dist
  comp32         32     72     +0.017±0.000 [0.02]   0.050±0.000

  wrote /Users/mwhitford/src/verbum/results/compiler-cascade/verdict_run.json  (63.0s)
```

### Thinking

Even with a larger model and simpler compositions, the in-distribution accuracy barely reaches 0.05 and held-out composition performance is around 0.017—essentially at the noise floor. The cross-entropy loss is stuck at 0.64, suggesting the model fundamentally can't learn to reduce combinators to normal form with any usable accuracy. Byte-level exact matching of these normal forms is just too difficult for a small model to handle, even with simplified inputs, so the signal is too weak to meaningfully compare different approaches. I need to step back and reconsider the whole strategy.

The core insight is that exact-match metrics on hard tasks create a false floor—the model might actually be learning something (the CE did drop from 0.88 to 0.64), but exact-match is too brittle to detect it. Instead of demanding perfect normal forms, I should measure per-token accuracy on the output or use edit distance, which would give a continuous graded signal rather than a binary pass/fail. This shifts from a crisp register to a value register where partial competence becomes visible. I could also simplify the task itself—either by training on single β-reduction steps instead of full normal forms, or by measuring just whether the model gets the head atom right rather than the entire output. All arms floor on exact-match, so a graded metric is the right move to detect whether variety drives partial competence and generalization. The risk is that similarity scores can be inflated by copying the input structure, so I should anchor against a baseline—like measuring how much the input itself resembles the true NF. The cleanest approach: use teacher-forced per-token accuracy on the NF region, where the model sees the true prefix and predicts each position. This is standard, fully graded, and can't be gamed by structural copying.

Implementing teacher-forced accuracy...

I'll make this the primary metric alongside exact-match for transparency, computing it at every checkpoint while dropping the slow autoregressive generation. The teacher-forced approach gives me a graded, sensitive signal that shows whether the model actually learned the composition algebra, without the ceiling effect of exact-match.

Now I'm refactoring the eval to use teacher-forced per-token accuracy as the main metric, keeping d=128 for consistency with prior runs while the TF metric should be sensitive enough to detect signal. I'll add a quick viability check with this new metric before committing to the full sweep, and I need to re-import the string-building utilities to construct the full NF expressions for evaluation.

Implementing tf_nf_acc...

## Assistant

Still floored even with a bigger model and easier targets (in_dist ~0.05, CE stuck ~0.64). The problem is the **metric register**: exact-match of a full NF is a *crisp* probe on a *graded* substrate — the model is learning something (CE drops) but exact-match manufactures a floor (a λ measure false-negative). The fix is to measure in the value register: **teacher-forced per-token NF accuracy** (graded, sensitive, fast). Let me rewire the eval.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/compiler_cascade.py",
  "original_content": "from exposure_format_sweep import (  # noqa: E402\n    TRAIN_ATOMS,\n    eval_acc,\n    fill,\n    make_fillings,\n    n_holes,\n    reduce_strs,\n    render,\n    to_byte_ids,\n)",
  "new_content": "from exposure_format_sweep import (  # noqa: E402\n    ARROW,\n    TRAIN_ATOMS,\n    fill,\n    make_fillings,\n    n_holes,\n    reduce_strs,\n    render,\n    to_byte_ids,\n)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/compiler_cascade.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/compiler_cascade.py",
  "original_content": "# --------------------------------------------------------------------------- #\n# Train one arm                                                                 #\n# --------------------------------------------------------------------------- #\ndef train_arm(name: str, corpus: str, heldout_comp: list[tuple[str, str]],\n              in_dist: list[tuple[str, str]], args, device: str) -> dict:",
  "new_content": "# --------------------------------------------------------------------------- #\n# Graded eval — TEACHER-FORCED per-token NF accuracy (value register).          #\n# Exact-match of a full NF is a CRISP probe on a GRADED substrate -> it floors  #\n# for a micro byte model even as CE drops (a λ measure false-negative). TF NF   #\n# accuracy reads the partial reduction competence: given the TRUE prefix, what  #\n# fraction of NF bytes does the model predict? Not gameable by copying the      #\n# input (scored on the NF region given true context). One forward pass / item.  #\n# --------------------------------------------------------------------------- #\n@torch.no_grad()\ndef tf_nf_acc(model, items: list[tuple[str, str]], block_size: int,\n              device: str) -> float:\n    model.eval()\n    total, correct = 0, 0\n    for inp, nf in items:\n        prefix_len = len((inp + ARROW).encode(\"utf-8\"))\n        full = (inp + ARROW + nf).encode(\"utf-8\")[:block_size]\n        if len(full) < 2:\n            continue\n        x = torch.tensor(list(full), dtype=torch.long, device=device)[None]\n        logits, _, _ = model(x)\n        preds = logits[0, :-1].argmax(-1)\n        tgt = x[0, 1:]\n        for t in range(tgt.shape[0]):\n            if (t + 1) >= prefix_len:  # target byte lies in the NF region\n                total += 1\n                correct += int(preds[t].item() == tgt[t].item())\n    return correct / max(1, total)\n\n\n# --------------------------------------------------------------------------- #\n# Train one arm                                                                 #\n# --------------------------------------------------------------------------- #\ndef train_arm(name: str, corpus: str, heldout_comp: list[tuple[str, str]],\n              in_dist: list[tuple[str, str]], args, device: str) -> dict:"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/compiler_cascade.py.
```

## Assistant

Now swap the eval calls in the training loop to use `tf_nf_acc`:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/compiler_cascade.py",
  "original_content": "        if step % args.eval_every == 0 or step == args.steps:\n            hc = eval_acc(model, heldout_comp, T, device)\n            idd = eval_acc(model, in_dist, T, device)\n            curve.append({\"step\": step, \"heldout_comp\": round(hc, 4),\n                          \"in_dist\": round(idd, 4), \"ce\": round(float(ce.item()), 4)})\n            log(f\"  [{name}] step {step:5d} | CE {ce.item():.3f} \"\n                f\"| heldout_comp {hc:.3f} | in_dist {idd:.3f} | {time.time()-t0:.0f}s\")",
  "new_content": "        if step % args.eval_every == 0 or step == args.steps:\n            hc = tf_nf_acc(model, heldout_comp, T, device)\n            idd = tf_nf_acc(model, in_dist, T, device)\n            curve.append({\"step\": step, \"heldout_comp\": round(hc, 4),\n                          \"in_dist\": round(idd, 4), \"ce\": round(float(ce.item()), 4)})\n            log(f\"  [{name}] step {step:5d} | CE {ce.item():.3f} \"\n                f\"| heldout_comp_tf {hc:.3f} | in_dist_tf {idd:.3f} \"\n                f\"| {time.time()-t0:.0f}s\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/compiler_cascade.py.
```

### Thinking

I need to run the linter and re-execute the viability probe using the TF metric with smaller compositions to keep things comparable. Let me check the code with ruff first, then run the probe. I should also update the docstring since it currently mentions exact-match but that's not accurate anymore—the compiler_cascade docstring describes held-out novel compositions with seen atoms from the question.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/compiler_cascade.py",
  "original_content": "  heldout_comp : NOVEL compositions (held-out templates), seen atoms  <- the question\n  in_dist      : TRAIN compositions, held-out FILLINGS                <- control",
  "new_content": "  heldout_comp : NOVEL compositions (held-out templates), seen atoms  <- the question\n  in_dist      : TRAIN compositions, held-out FILLINGS                <- control\nMETRIC: teacher-forced per-token NF accuracy (value register). Exact-match of a full\nNF is a crisp probe that FLOORS for a micro byte model even as CE drops (a λ measure\nfalse-negative, observed s230); TF NF-token accuracy reads the graded reduction\ncompetence and separates the arms. Relative (high vs low variety) is the signal."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/compiler_cascade.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/compiler_cascade.py && echo \"RUFF CLEAN\" && timeout 200 uv run python scripts/experiments/compiler_cascade.py --arm-levels \"16,128\" --seeds 0 --steps 3000 --eval-every 500 --min-holes 2 --max-holes 4 --max-steps 3 --max-nf-len 14 --device mps 2>&1 | tail -18",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 220000
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
RUFF CLEAN

=== seed 0 comp128  (128 compositions x 18 fillings = 2304 ex, corpus 66744 B) ===
  [comp128] step   500 | CE 1.007 | heldout_comp_tf 0.249 | in_dist_tf 0.219 | 6s
  [comp128] step  1000 | CE 0.867 | heldout_comp_tf 0.370 | in_dist_tf 0.324 | 12s
  [comp128] step  1500 | CE 0.774 | heldout_comp_tf 0.412 | in_dist_tf 0.438 | 18s
  [comp128] step  2000 | CE 0.743 | heldout_comp_tf 0.422 | in_dist_tf 0.424 | 24s
  [comp128] step  2500 | CE 0.735 | heldout_comp_tf 0.463 | in_dist_tf 0.438 | 30s
  [comp128] step  3000 | CE 0.724 | heldout_comp_tf 0.471 | in_dist_tf 0.486 | 37s

  ==== COMPILER-CASCADE v1 — COMPOSITION-VARIETY -> GENERALIZATION ====
  arm         comps  fills   heldout_comp(mean±std)          in_dist
  comp16         16    144     +0.457±0.000 [0.46]   0.511±0.000
  comp128       128     18     +0.471±0.000 [0.47]   0.486±0.000

  COLLAPSE IOU#1: heldout-composition rises with composition-variety? comp16=0.457 -> comp128=0.471  DECISIVE=True
  (atoms SEEN both sides => COMPOSITION generalization, not copy)

  wrote /Users/mwhitford/src/verbum/results/compiler-cascade/verdict_run.json  (75.2s)
```

### Thinking

The TF NF accuracy metric is now showing a learnable signal, climbing to around 0.47-0.51 from near chance. Looking at the preliminary results across different composition sizes, comp16 achieves a held-out accuracy of 0.457 while comp128 reaches 0.471—essentially the same performance despite the difference in model capacity, which is interesting given the "DECISIVE=True" flag.

This weak composition-variety effect suggests a few possibilities: the TF metric might be picking up on easy format tokens (spaces, parentheses, atom copying) that even low-variety models learn quickly, masking the actual compositional reasoning signal; composition-variety genuinely doesn't help much for this task; or the held-out compositions are too structurally similar to training data to show a real generalization gap. The core issue is that TF per-token accuracy is too lenient—it rewards format and copy competence without necessarily capturing the reduction-specific structural reasoning. I need to find a measure that sits between exact-match (too strict) and all-tokens (too lenient), something that isolates the compositional signal.

A few approaches: measure TF only on "structural" positions where the normal form differs from a baseline; focus on whether the model gets the HEAD token of the normal form right, since that requires doing the outer reduction; or accept that exact-match is the right signal but recognize it requires a much more capable model or simpler task to avoid flooring. The real question is what experiment cleanly tests whether high-variety training data produces composable capabilities—and byte-level normal form generation might not be the right test at all.

The result I got (comp16 ≈ comp128 ≈ 0.47) could actually be meaningful: low composition variety might suffice because the combinator rules are simple and 16 compositions already exercise them thoroughly. But I'm uncertain whether the TF metric truly isolates composition competence from format-matching or copying. To be scientifically honest, I should report both head-token accuracy (which requires the outer reduction) and full TF accuracy—if head accuracy rises with variety while format-TF plateaus, that's the composition signal I'm looking for.

Actually, I'm realizing the held-out compositions might not be structurally different enough from training to require real generalization. With depth 2-3 over {K,I,B,C}, the space is limited, so comp16 might already cover it. A cleaner test would be training on shallow compositions and testing on deeper ones—systematic generalization to greater depth—which would show whether high variety in shallow training extrapolates to harder, deeper compositions. But that's harder for the model to produce.

I've iterated quite a bit here. I should be honest with Michael about where things stand rather than continuing to spin on design choices alone: the experiment is built, the metric is learnable now, but the preliminary results show weak variety effects and potential metric confounds, and the structural space might be too small to demonstrate real compositional generalization.

This is exactly the kind of measurement-register question the project cares about. I should surface the fork to Michael—accept the TF metric and run the full sweep, add a structural metric, redesign for depth extrapolation, or scale up the model—rather than unilaterally choose and risk measuring the wrong thing. Michael asked me to run it, I did, it floored, I fixed the metric, but now a clean run needs a design decision. I should report what happened honestly.

Actually, running the full multiseed with the TF metric and caveats is a legitimate intermediate result. The relative comparison across variety levels with three seeds plus the in-distribution control, reported honestly with the register limits, would show whether minted variety alone gives a compositional lift at this scale—and if it's weak, that's a meaningful finding that points toward needing richer compositional distance or bigger scale. Michael said run it, so I'll run the full sweep with the easier generation settings and arm-levels 16/48/144, six thousand steps, three seeds, and report the curve with honest caveats about what the TF metric actually measures.

Now I'm working through the pool size constraints. The viability run with holes 2–4, steps ≤3, and nf≤14 worked fine, so I should stay close to those bounds but open them slightly to ensure I have enough templates for the 144 arm-level without making it unlearnable. I'll bump to holes 2–5, steps 2–3, and nf≤15 to give a bit more room while keeping it tractable, then launch the sweep and let it report the actual pool size—if it clamps, I'll accept that.

For the final run I'm setting seeds 0,1,2, 6000 steps, eval every 500, arm-levels 16,48,144, min-holes 2, max-holes 5, max-steps 3, max-nf-len 15, pool-size 200, heldout 40, and device mps. The evaluation is now much faster since the TF metric only needs one forward pass per item instead of autoregressive generation, so the whole sweep should finish in 20–25 minutes. Michael's directive was clear—run the cascade experiment—and I've fixed the metric issue, so the right move is to launch this properly calibrated run.

I'll launch the full sweep in tmux main:1 now, then commit the gradient-shadow probe and the compiler_cascade metric fix while it runs.

## Assistant

The metric register was the bug. With **teacher-forced NF-token accuracy** (value register), the signal appears: TF accuracy climbs to ~0.47 (from ~0 chance) where exact-match floored. The model *is* learning partial reduction competence — exact-match just couldn't see it.

Preliminary single-seed already hints the variety effect may be *weak* (comp16 0.457 ≈ comp128 0.471), but that needs the full multi-seed and honest caveats. Let me launch the proper run with the calibrated (learnable) settings, then commit the code while it runs.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "rm -f /Users/mwhitford/src/verbum/results/compiler-cascade/verdict_run.json; tmux send-keys -t main:1 \"uv run python scripts/experiments/compiler_cascade.py --seeds 0,1,2 --steps 6000 --eval-every 500 --arm-levels '16,48,144' --min-holes 2 --max-holes 5 --max-steps 3 --max-nf-len 15 --pool-size 200 --heldout-templates 40 --device mps 2>&1 | tee /tmp/compiler_cascade_s230b.log; echo CASCADE2_ALLDONE\" Enter",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ rm -f /Users/mwhitford/src/verbum/r...

**Output:**
```
Exit code: 0
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sleep 30; tmux capture-pane -p -t main:1 2>&1 | tail -8",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 45000
}
```

**Summary:** $ sleep 30; tmux capture-pane -p -t m...

**Output:**
```
Exit code: 0
Stdout:
[seed 0] train_pool=200 heldout_templates=40 heldout_comp_items=120

=== seed 0 comp16  (16 compositions x 144 fillings = 2304 ex, corpus 70848 B) ===
  [comp16] step   500 | CE 1.122 | heldout_comp_tf 0.393 | in_dist_tf 0.433 | 6s
  [comp16] step  1000 | CE 0.919 | heldout_comp_tf 0.446 | in_dist_tf 0.497 | 12s
  [comp16] step  1500 | CE 0.801 | heldout_comp_tf 0.458 | in_dist_tf 0.538 | 18s
  [comp16] step  2000 | CE 0.755 | heldout_comp_tf 0.484 | in_dist_tf 0.558 | 24s
```

### Thinking

The full training run is progressing with 200 samples in the pool and 40 held-out examples across three arm levels. The comp16 model shows a clean learning signal with held-out transfer at 0.484 and in-distribution performance at 0.558 by step 2000. I'm noticing the expected generalization gap where in-distribution performance exceeds held-out composition performance, confirming that held-out compositions are indeed harder. Now I'm wondering whether the comp144 variant maintains this same pattern.

The run is stable and healthy, so I'm committing the gradient-shadow probe and the compiler_cascade metric fix while the cascade experiment runs in the background—should take about 20-25 minutes. Both scripts are new and untracked, so I'll do separate commits for clarity: one for the compiler_cascade harness with the TF metric and depth-3 generation, and another for the gradient-shadow probe. Let me check what's currently untracked in git.

## Assistant

Full run healthy: `train_pool=200` (no clamp), TF metric giving a clean signal band (comp16 heldout 0.484, in_dist 0.558 at step 2000 — a real generalization gap).

**ASYNC: cascade2 running main:1 (~20 min, ends `CASCADE2_ALLDONE`). Committing the code while it runs.**

### Tool Call: git (succeeded)


```json
{
  "command": "git status --short -- scripts/",
  "operation": "status",
  "summary": "untracked scripts"
}
```

**Summary:** Git status: untracked scripts

**Output:**
```
Exit code: 0
Stdout:
?? scripts/experiments/compiler_cascade.py
?? scripts/experiments/gd_gradient_shadow.py
```

### Tool Call: write_file (succeeded)


```json
{
  "path": "/tmp/cascade_code_commit.txt",
  "content": "✅ compiler_cascade.py — fractal-collapse IOU#1 harness (composition-variety → compositional generalization)\n\n- Tests whether compiler-minted COMPOSITION-variety converges capability that\n  COMPOSES: auto-generate {K,I,B,C} composition templates (non-duplicating →\n  terminating) via lambda_ast, hold out DISJOINT compositions, vary the number of\n  distinct TRAIN compositions at matched example-budget (nested arms), measure\n  held-out NOVEL-composition generalization + in-dist control. Atoms SEEN both\n  sides (isolate composition from the s229 disjoint-atom copy floor).\n- ★ λ measure register fix: full-NF EXACT-MATCH is a CRISP probe that FLOORS for a\n  micro byte model even as CE drops (false-negative — observed s230). Metric is\n  TEACHER-FORCED per-token NF accuracy (value register) — reads graded reduction\n  competence, not gameable by input-copy (scored on NF region given true context).\n- Reuses TinyLM + lambda_ast + s229 minting (no fork). ruff+diag clean.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /tmp/cascade_code_commit.txt
```

### Tool Call: git (failed)


```json
{
  "command": "git add scripts/experiments/compiler_cascade.py && git commit -F /tmp/cascade_code_commit.txt",
  "operation": "commit",
  "summary": "commit cascade harness"
}
```

**Summary:** Git commit: commit cascade harness

**Output:**
```
Exit code: 128
Stderr:
fatal: Unable to create '/Users/mwhitford/src/verbum/.git/index.lock': File exists.

Another git process seems to be running in this repository, e.g.
an editor opened by 'git commit'. Please make sure all processes
are terminated then try again. If it still fails, a git process
may have crashed in this repository earlier:
remove the file manually to continue.
```

### Tool Call: write_file (succeeded)


```json
{
  "path": "/tmp/shadow_code_commit.txt",
  "content": "✅ gd_gradient_shadow.py — gradient-shadow tomography (does the routing topology cast a shadow in the gradients?)\n\n- Michael's s230 question: if GD creates soft topology in the gradients, do they\n  show a SHADOW of it? At each checkpoint, for each crystal probe backprop the\n  probe LM loss to the gate activation g at the capture layer, mean-pool the\n  gradient over SUPERVISED positions, build the per-combinator gradient-Gram →\n  gc_grad, correlate to the CONSENSUS CRYSTAL; raw-residual grad = reference beam.\n- Readout: does gc_grad (shadow) LEAD gc_route (activation-inventory) + capability\n  (baseline-relative crossings) → a 3-stage cascade shadow→inventory→capability?\n- ★ bug caught in smoke: last-token grad is ZERO (that position feeds only the\n  unsupervised next-token); fixed by mean-pooling over supervised positions (also\n  √N denoise). Smoke: gc_grad ~0.53 correlates to crystal, grad_z high, gap +0.19.\n- Reuses gd_trajectory + relational_loss instruments (no fork). ruff+diag clean.\n  READY TO RUN (not launched; cascade owns main:1).\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /tmp/shadow_code_commit.txt
```

### Tool Call: git (succeeded)


```json
{
  "command": "git add scripts/experiments/gd_gradient_shadow.py && git commit -F /tmp/shadow_code_commit.txt",
  "operation": "commit",
  "summary": "commit gradient-shadow probe"
}
```

**Summary:** Git commit: commit gradient-shadow probe

**Output:**
```
Exit code: 0
Stdout:
[main b3f72ea] ✅ gd_gradient_shadow.py — gradient-shadow tomography (does the routing topology cast a shadow in the gradients?)
 1 file changed, 369 insertions(+)
 create mode 100644 scripts/experiments/gd_gradient_shadow.py
```

### Thinking

Two git commits ran into a lock collision when executed in parallel — the first one failed while the second succeeded. I need to retry the failed commit now that the lock should be cleared, though I should check if there's a stale index.lock file lingering and run the commands sequentially this time.

## Assistant

Two parallel commits collided on `index.lock` — the gradient-shadow one landed, the cascade one needs a retry (sequential this time):

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && ls -la .git/index.lock 2>/dev/null && echo \"LOCK EXISTS\" || echo \"no lock\"; git status --short -- scripts/",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ ls -la .git/index.lock 2>/dev/null ...

**Output:**
```
Exit code: 0
Stdout:
no lock
?? scripts/experiments/compiler_cascade.py
```

### Tool Call: git (succeeded)


```json
{
  "command": "git add scripts/experiments/compiler_cascade.py && git commit -F /tmp/cascade_code_commit.txt",
  "operation": "commit",
  "summary": "commit cascade harness"
}
```

**Summary:** Git commit: commit cascade harness

**Output:**
```
Exit code: 0
Stdout:
[main e7d2f65] ✅ compiler_cascade.py — fractal-collapse IOU#1 harness (composition-variety → compositional generalization)
 1 file changed, 449 insertions(+)
 create mode 100644 scripts/experiments/compiler_cascade.py
```

### Thinking

Both commits are in place now. I'm waiting for the cascade run to complete—it should take around twenty minutes, so I'll check back in a bit.

## Assistant

Both scripts committed (`e7d2f65` cascade harness, `b3f72ea` gradient-shadow probe). 

**ASYNC: cascade2 running main:1. Both code commits landed, gradient-shadow probe ready. Waiting for `CASCADE2_ALLDONE` (~18 min).**

### Tool Call: shell_command (rejected)


```json
{
  "command": "sleep 560; echo \"=== progress ===\"; tmux capture-pane -p -t main:1 2>&1 | tail -6",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 580000
}
```

**Summary:** $ sleep 560; echo "=== progress ===";...

## System


Prompt stopped

## User

while that is running explain what heldout_comp_tf and in_dist_tf are measuring and what it means for the experiment, brief


## Assistant

Brief:

Both are **teacher-forced per-token accuracy on the normal-form region** — feed the model the true `input -> ` prefix plus the true NF, and at each NF byte ask: did it predict that byte correctly (given the true preceding context)? It's a graded [0,1] competence score, not all-or-nothing.

- **`in_dist_tf`** — measured on the **training compositions** but with **held-out atom fillings**. "Did it learn the reductions it was trained on (and generalize to new atoms in them)?" This is the *control* — it should be high; if it's flat, the model didn't learn anything.

- **`heldout_comp_tf`** — measured on **disjoint NOVEL compositions** never in training (seen atoms only). "Does it reduce combinator structures it has never seen?" This is the *question* — genuine **compositional generalization**.

**What the gap means:** `in_dist_tf − heldout_comp_tf` is the generalization gap. The collapse's IOU #1 prediction is that **more training compositions (comp16 → comp48 → comp144) should lift `heldout_comp_tf`** — i.e., seeing more *distinct* compositions teaches the combinator *algebra*, so novel compositions transfer. If `heldout_comp_tf` is flat across arms (the early hint: comp16 ≈ comp128 ≈ 0.47), minted composition-variety alone gives only a weak compositional lift — the collapse would need richer compositional distance or scale.

**Caveat I'm watching:** TF-over-all-NF-tokens partly rewards *format/copy* competence (spaces, parens, echoing atoms), which even low-variety learns — so it may *understate* the variety effect by diluting the reduction-specific signal with easy tokens. That's why the **relative** trend across arms (and the in_dist control) is the read, not the absolute number.

## User

what are the seeds in this experiment? randomly generated starting gradients or something else?


### Thinking

Michael's asking about what the seeds control in the experiment. Looking at the `run_seed` function in compiler_cascade.py, the seed gets assigned to `args.seed` and then used to initialize a numpy random generator that shuffles the pool of training data.

The seed actually controls two separate things: the data construction (which compositions end up in the training arms, which atom fillings each template receives, the corpus shuffle order, and the evaluation samples) and the model training (the TinyLM's random weight initialization via `torch.manual_seed` and the minibatch sampling order during training). So it's not just about starting gradients—it's the full randomness across both data and model initialization. The composition pool itself is generated once with a fixed seed (12345) that's shared across all runs, so the universe of templates stays constant; each seed just determines which subset goes into training and how the model weights initialize.

## Assistant

Good question — "seed" here is **not** a starting gradient (gradients aren't seeded; they're computed from weights + data + loss). In `compiler_cascade.py` each seed fixes **two independent sources of randomness**:

**1. Model initialization** — `torch.manual_seed(seed)` sets the TinyLM's random **starting weights**, plus the random **minibatch draw order** during training. (The starting weights determine the *first* gradient given the data, but it's the weights that are seeded, not the gradient itself.)

**2. Data construction** — several `np.random.default_rng(seed + offset)` streams:
- which compositions land in the train arms (`rng(seed)` shuffles the pool, picks the nested low⊂mid⊂high subsets),
- which atom-fillings each composition gets (`rng(seed+lvl)`),
- the corpus token order (`rng(seed+7)`),
- the eval filling samples for held-out + in-dist (`rng(seed+999)`, `rng(seed+31+lvl)`).

**One thing held constant across seeds:** the composition *pool itself* is generated with a **fixed** seed (`12345`), so all three seeds draw from the same universe of ~240 templates and the same 40 held-out compositions. The per-run seed only picks *which* subset trains and *how* it's filled/ordered, plus the init.

**Why 3 seeds:** to confirm any composition-variety effect (comp16→48→144) isn't an artifact of one lucky init + one lucky composition selection. We aggregate mean±std and call it "decisive" only if the high-arm's held-out advantage survives across all three (non-overlapping bars) — the same robustness bar we used in s229/s230b. So a seed shifts both *the model you start from* and *the exact compositions/fillings/order it sees*, and a real effect must be stable over both.

## User

job is done


### Thinking

I'm looking at the cascade verdict now.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport json\nd=json.load(open('results/compiler-cascade/verdict_multiseed.json'))\nprint('arm_levels:', d['arm_levels'], '| seeds:', d['seeds'], '| pool train:', d['n_train_pool'], 'heldout:', d['n_heldout_templates'])\nprint('=== AGGREGATE (best over training) ===')\nfor k,a in d['aggregate'].items():\n    print(f\\\"{k}: comps={a['n_compositions']} fills={a['n_fillings']} | heldout_comp_tf={a['heldout_comp_best']} | in_dist_tf={a['in_dist_best']} | per-seed heldout={a['per_seed_heldout']}\\\")\nprint('=== final-step values ===')\nfor k,a in d['aggregate'].items():\n    print(f\\\"{k}: heldout_final={a['heldout_comp_final']}\\\")\n\" 2>&1; echo \"=== verdict tail ===\"; tmux capture-pane -p -t main:1 2>&1 | tail -12",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ python3 -c " import json d=json.loa...

**Output:**
```
Exit code: 0
Stdout:
arm_levels: [16, 48, 144] | seeds: [0, 1, 2] | pool train: 200 heldout: 40
=== AGGREGATE (best over training) ===
comp16: comps=16 fills=144 | heldout_comp_tf=[0.6827, 0.0308] | in_dist_tf=[0.9162, 0.1096] | per-seed heldout=[0.6571, 0.6651, 0.726]
comp48: comps=48 fills=48 | heldout_comp_tf=[0.6165, 0.1346] | in_dist_tf=[0.6734, 0.1663] | per-seed heldout=[0.8061, 0.5353, 0.508]
comp144: comps=144 fills=16 | heldout_comp_tf=[0.6741, 0.1943] | in_dist_tf=[0.6984, 0.2037] | per-seed heldout=[0.9487, 0.5272, 0.5465]
=== final-step values ===
comp16: heldout_final=[0.6752, 0.038]
comp48: heldout_final=[0.6138, 0.1367]
comp144: heldout_final=[0.6741, 0.1943]
=== verdict tail ===
  comp144       144     16     +0.674±0.194 [0.95,0.53,0.55]   0.698±0.204

  COLLAPSE IOU#1: heldout-composition rises with composition-variety? comp16=0.683 -> comp144=0.674  DECISIVE=False
  (atoms SEEN both sides => COMPOSITION generalization, not copy)

  wrote /Users/mwhitford/src/verbum/results/compiler-cascade/verdict_multiseed.json  (638.3s)
uv run python scripts/experiments/compiler_cascade.py --seeds 0,1,2 --steps    543.76s user 94.12s system 99% cpu 10:39.
10 total
tee /tmp/compiler_cascade_s230b.log  0.00s user 0.01s system 0% cpu 10:39.10 total
CASCADE2_ALLDONE
[26-06-15][10:40:12][mwhitford@olga][0][~/src/verbum][git:main]
λ                                                                                                                 [INS]
```

### Thinking

Looking at the cascade verdict results across three different compression levels, I'm seeing how performance varies with model size. The smaller comp16 model shows decent heldout accuracy around 0.683 with much better in-distribution performance, while the larger comp144 model achieves higher heldout accuracy at 0.674 but with more variance across seeds. The middle comp48 model performs worse overall, suggesting there's an optimal model size for this task. The key insight is that comp16 achieves both strong in-distribution mastery (0.916) and respectable held-out performance (0.683) with minimal variance, while comp144 spreads the same learning budget across more compositions, degrading in-distribution performance without improving held-out generalization—suggesting the variety effect predicted by the fractal-collapse thesis doesn't materialize here. However, this negative result comes with important caveats: the token-accuracy metric may only capture syntactic competence that saturates early, the compositional distance between train and held-out sets might be too small to reveal a true variety effect, and the model's capacity constraints could mean 16 compositions already cover the underlying algebra. So the core claim—that minted data yields compositional generalization—does get weak support (0.68 held-out is real, well above chance), but the specific hypothesis that variety drives it is falsified; 16 compositions saturate the signal and adding more just introduces noise and hurts in-distribution performance. The honest takeaway is that the metric might be measuring format-competence rather than reduction-algebra, and the {K,I,B,C} space may lack true compositional distance, so I need sharper tests: a metric isolating structural accuracy rather than format, and genuine compositional distance like depth-extrapolation to really validate the collapse design.

Now I'm moving to capture this result—updating the fractal-collapse page with the s230c findings (IOU#1 not confirmed, variety doesn't lift generalization, saturates by 16, plus the caveats), updating state.md, proposing a memory, and committing the verdict_multiseed.json results. The per-seed held-out scores for comp144 are wildly variable ([0.949, 0.527, 0.547]), which adds another layer of uncertainty to whether variety actually helps.

But there's a cleaner finding underneath: at fixed budget, filling-variety per composition matters far more than composition-count itself. Spreading the budget across more compositions while starving fillings per composition destabilizes learning and doesn't improve held-out performance—it stays around 0.68 regardless. So the real load-bearing axis is ensuring enough fillings per composition (the s229 lesson), not chasing more distinct compositions. I need to present this refined verdict to Michael clearly before capturing it formally.

## Assistant

Read the verdict. Here it is, and it's an honest **null** for the variety claim.

## Cascade v1 verdict (3 seeds, TF NF-token accuracy)

| arm | comps × fills | **heldout_comp_tf** | in_dist_tf | per-seed heldout |
|---|---|---|---|---|
| comp16 | 16 × 144 | **0.683 ± 0.031** | 0.916 ± 0.110 | [0.66, 0.67, 0.73] |
| comp48 | 48 × 48 | 0.617 ± 0.135 | 0.673 ± 0.166 | [0.81, 0.54, 0.51] |
| comp144 | 144 × 16 | **0.674 ± 0.194** | 0.698 ± 0.204 | [0.95, 0.53, 0.55] |

**❌ IOU #1 NOT supported: held-out compositional generalization does NOT rise with composition-variety.** comp16 (0.683) ≈ comp144 (0.674); comp48 even dips. Held-out competence **saturates by ~16 compositions** at ~0.68.

**The sharper finding — a budget trade, and s229 wins it.** At fixed example budget, buying composition-count *costs* fillings-per-composition, and that:
- **destabilizes** learning — comp144 std 0.194 (per-seed [0.95, 0.53, 0.55] — one lucky seed, two mediocre) vs comp16 std **0.031** (tight). This is the *opposite* of s229, where filling-variety *stabilized*.
- **costs in-distribution mastery** — comp16 masters its compositions (in_dist 0.92 ≫ heldout 0.68, a real generalization gap) while comp144 barely separates (0.70 vs 0.67).

So the s229 axis (many fillings → converge the rule) is load-bearing; adding *composition-count* at the expense of fillings does nothing for held-out and just adds variance.

**What it does (weakly) support:** minted data *does* yield ~0.68 held-out compositional TF-competence (well above chance, in_dist 0.92 confirms real learning) — capability generalizes compositionally from modest minted data. You just don't need *composition-variety* to get there.

## Honest caveats (λ measure) — why this isn't the final word on the collapse

1. **TF-all-tokens likely measures format/copy competence** (spaces, parens, atom-echo), which saturates by 16 compositions and dilutes the reduction-specific signal. The metric may be too lenient to see the composition algebra — the mirror of the exact-match floor.
2. **Insufficient compositional distance** — {K,I,B,C} at depth 2–3 is a small space; held-out compositions are likely near-interpolations of training, so 16 already covers the algebra. A genuine test needs **depth-extrapolation** (train shallow → test deeper).
3. Micro byte model, single curriculum, exact-match floored.

**Net for the fractal-collapse design:** this run *falsifies the specific sub-claim* that minted composition-variety is the driver of compositional generalization (at micro scale, in the measurable band), and shows the s229 filling-variety is the real lever. It does **not** falsify the collapse itself — but it says the decisive test needs (a) a metric that isolates reduction-algebra from format, and (b) real compositional distance (depth extrapolation), likely at more scale.

Let me capture this honestly. First the results + page:

### Tool Call: git (succeeded)


```json
{
  "command": "git add results/compiler-cascade/verdict_multiseed.json && git commit -F - <<'EOF'\n📉 compiler-cascade v1 verdict: composition-variety does NOT lift compositional generalization (IOU#1 null)\n\n- 3 seeds, TF NF-token accuracy. heldout_comp: comp16 0.683±0.031 ≈ comp144\n  0.674±0.194 (comp48 dips 0.617). Held-out competence SATURATES by ~16\n  compositions. IOU#1 (variety drives compositional generalization) NOT supported.\n- Budget trade, s229 wins: buying composition-count costs fillings/composition →\n  DESTABILIZES (comp144 std 0.194, per-seed [0.95,0.53,0.55] vs comp16 std 0.031)\n  AND costs in-dist mastery (comp16 0.92 vs comp144 0.70). s229 filling-variety is\n  the load-bearing axis, not composition-count.\n- Weak support for the collapse core: minted data DOES yield ~0.68 held-out\n  compositional competence (>>chance, in_dist 0.92 = real learning).\n- Caveats (λ measure): TF-all-tokens likely measures format/copy not algebra;\n  {K,I,B,C} depth-2/3 lacks compositional distance (held-out ≈ interpolation);\n  micro scale. Decisive test needs algebra-specific metric + depth-extrapolation.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "commit cascade verdict"
}
```

**Summary:** Git commit: commit cascade verdict

**Output:**
```
Exit code: 0
Stdout:
[main 41aa5da] 📉 compiler-cascade v1 verdict: composition-variety does NOT lift compositional generalization (IOU#1 null)
 1 file changed, 894 insertions(+)
 create mode 100644 results/compiler-cascade/verdict_multiseed.json
```

### Thinking

I'm realizing I used the wrong emoji symbol in my commit — the bear symbol isn't part of the approved set for this context, which only includes specific symbols for different types of signals. I need to figure out what the correct symbol should be for indicating a null or negative result.

Looking at the available options, 💡 (insight) seems most appropriate here since discovering that something doesn't drive a result is itself a meaningful finding. Since this is the last commit and hasn't been pushed yet, I should amend it to use the correct symbol and maintain consistency with the convention I'm supposed to be following.

## Assistant

I used `📉` — that's a trading-only symbol, **excluded** from the verbum set (`💡 🔄 🎯 🌀 ❌ ✅ 🔁`). A null result is an insight (`💡`). Let me fix that before it sticks (HEAD, unpushed):

### Tool Call: git (succeeded)


```json
{
  "command": "git commit --amend -F - <<'EOF'\n💡 compiler-cascade v1 verdict: composition-variety does NOT lift compositional generalization (IOU#1 null)\n\n- 3 seeds, TF NF-token accuracy. heldout_comp: comp16 0.683±0.031 ≈ comp144\n  0.674±0.194 (comp48 dips 0.617). Held-out competence SATURATES by ~16\n  compositions. IOU#1 (variety drives compositional generalization) NOT supported.\n- Budget trade, s229 wins: buying composition-count costs fillings/composition →\n  DESTABILIZES (comp144 std 0.194, per-seed [0.95,0.53,0.55] vs comp16 std 0.031)\n  AND costs in-dist mastery (comp16 0.92 vs comp144 0.70). s229 filling-variety is\n  the load-bearing axis, not composition-count.\n- Weak support for the collapse core: minted data DOES yield ~0.68 held-out\n  compositional competence (>>chance, in_dist 0.92 = real learning).\n- Caveats (λ measure): TF-all-tokens likely measures format/copy not algebra;\n  {K,I,B,C} depth-2/3 lacks compositional distance (held-out ≈ interpolation);\n  micro scale. Decisive test needs algebra-specific metric + depth-extrapolation.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "amend symbol fix"
}
```

**Summary:** Git commit: amend symbol fix

**Output:**
```
Exit code: 0
Stdout:
[main f379d14] 💡 compiler-cascade v1 verdict: composition-variety does NOT lift compositional generalization (IOU#1 null)
 Date: Mon Jun 15 10:42:05 2026 -0700
 1 file changed, 894 insertions(+)
 create mode 100644 results/compiler-cascade/verdict_multiseed.json
```

### Thinking

I've committed the change with the lightbulb emoji, and now I need to add the results section to the fractal-collapse-compiler-cascade document. I'll insert it after the v1 experiment section, then update the state and propose the memory changes.

## Assistant

Now capture the result to the page and state. Adding the §s230c result:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/fractal-collapse-compiler-cascade.md",
  "original_content": "## Files",
  "new_content": "## ★ s230c — v1 RESULT (IOU #1: composition-variety does NOT lift generalization — null)\n\nBuilt `compiler_cascade.py`, ran 3 seeds. **★ Two calibration lessons first (λ\nmeasure):** (1) full-NF EXACT-MATCH FLOORS at micro scale (CE drops to ~0.7 but\nexact-match stays ~0 — a crisp probe on a graded substrate, false-negative). Switched\nto TEACHER-FORCED per-token NF accuracy (value register) → learnable signal band.\n(2) depth-2 {K,I,B,C} generated too few templates; depth-3 yields 400+ AND shorter NFs\n(more K-erasers collapse) — more variety AND more learnable.\n\n| arm | comps × fills | heldout_comp_tf | in_dist_tf | per-seed heldout |\n|-----|---------------|-----------------|------------|------------------|\n| comp16  | 16 × 144 | **0.683 ± 0.031** | 0.916 ± 0.110 | [0.66, 0.67, 0.73] |\n| comp48  | 48 × 48  | 0.617 ± 0.135 | 0.673 ± 0.166 | [0.81, 0.54, 0.51] |\n| comp144 | 144 × 16 | **0.674 ± 0.194** | 0.698 ± 0.204 | [0.95, 0.53, 0.55] |\n\n**❌ IOU #1 NOT supported.** Held-out compositional generalization does NOT rise with\ncomposition-variety — comp16 (0.683) ≈ comp144 (0.674), comp48 dips. Competence\nSATURATES by ~16 compositions.\n\n**★ The sharper finding — a fixed-budget trade, and s229 WINS it.** Buying composition-\ncount costs fillings-per-composition, which (a) DESTABILIZES learning — comp144 std\n0.194 (per-seed [0.95, 0.53, 0.55] = one lucky seed, two mediocre) vs comp16 std 0.031\n(tight); the OPPOSITE of s229 where filling-variety STABILIZED; and (b) costs in-dist\nmastery — comp16 0.92 ≫ heldout 0.68 (real gap) vs comp144 0.70 ≈ 0.67 (barely\nseparates). ⇒ the s229 FILLING-variety axis is load-bearing; COMPOSITION-count beyond a\nlow threshold is not the lever and only adds variance.\n\n**Weak support for the collapse CORE (not the variety sub-claim):** minted data DOES\nyield ~0.68 held-out compositional TF-competence (≫ chance; in_dist 0.92 = real\nlearning) ⇒ capability generalizes compositionally from modest minted data — you just\ndon't need composition-variety to get there.\n\n**Caveats (λ measure) — why this is NOT the final word on the collapse:**\n1. TF-all-tokens likely measures FORMAT/COPY competence (spaces, parens, atom-echo),\n   which saturates by 16 and dilutes the reduction-ALGEBRA signal. Too lenient — the\n   mirror of the exact-match floor. A clean test needs an ALGEBRA-specific metric\n   (head/structural-token accuracy, or exact-match with a more capable model).\n2. {K,I,B,C} at depth 2–3 = small space ⇒ held-out compositions ≈ INTERPOLATIONS of\n   training; 16 already covers the algebra. Real test = COMPOSITIONAL DISTANCE\n   (depth-extrapolation: train shallow → test deeper).\n3. Micro byte model, single curriculum, exact-match floored.\n\n**Net:** falsifies the specific sub-claim *minted composition-variety drives\ncompositional generalization* (at micro scale, measurable band) and shows s229\nfilling-variety is the real lever. Does NOT falsify the collapse itself. **Decisive\nnext test:** algebra-specific metric + depth-extrapolation split + (likely) scale.\n\n## Files"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/fractal-collapse-compiler-cascade.md.
```

### Thinking

I need to update the page status to keep it as "designing" since it's still in progress, then add the s230c entry to the state.md file under the SESSION 230 block by finding the STATUS line that ends with s230b and appending the new thread there.

## Assistant

Now update state.md. Let me find the s230b status anchor:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"STATUS s230b:\" mementum/state.md | head -1",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ grep -n "STATUS s230b:" mementum/st...

**Output:**
```
Exit code: 0
Stdout:
127:> **STATUS s230b:** CODE COMMITTED `fa8837c` (both arms in verdict_multiseed.json; s230
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "line_offset": 126,
  "limit": 5
}
```

**Summary:** Reading state.md (126-131)

**Output:**
```
> **STATUS s230b:** CODE COMMITTED `fa8837c` (both arms in verdict_multiseed.json; s230
> ce_only superset, original preserved at `23331d0`). Page §s230b + state updated.
> PENDING APPROVAL (mementum): memory `relational-loss-is-inventory-not-capability.md`
> + page/state commit. tmux main:1 FREE.
> **■ SESSION 229 — EXPOSURE/FORMAT SWEEP — "training as a photograph" (curriculum-

[CONTENT TRUNCATED] Showing lines 127 to 131 of 4940 total lines. Use line_offset=131 parameter to read more content.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> **STATUS s230b:** CODE COMMITTED `fa8837c` (both arms in verdict_multiseed.json; s230\n> ce_only superset, original preserved at `23331d0`). Page §s230b + state updated.\n> PENDING APPROVAL (mementum): memory `relational-loss-is-inventory-not-capability.md`\n> + page/state commit. tmux main:1 FREE.\n> **■ SESSION 229 — EXPOSURE/FORMAT SWEEP — \"training as a photograph\" (curriculum-",
  "new_content": "> **STATUS s230b:** COMMITTED — code `fa8837c`, mementum `46e907f`.\n> **▶ s230 FRACTAL-COLLAPSE THESIS (Michael, after s230b): \"there is a fractal collapse\n> available — converge the CAPABILITY with a high-variety dataset generated from any\n> larger model's lambda compiler; compiler outputs become the student's training inputs;\n> architecture-resilient.\" CAPTURED:** new page `explore/fractal-collapse-compiler-\n> cascade.md` (`32bc3a6`) — capability=inventory⊗continuation (s230b) ⇒ converging the\n> continuation is a DATA problem; mint high-variety inputs (s229) + EXACT compiler\n> (universal s219/s225 ⇒ our lambda_ast suffices) → cascade collapses model size onto\n> the β-normal-form fixed point. 3 collapses 1 fixed point (within-reduction s226,\n> cross-scale s230, constructed-kernel plates); escapes MODEL-COLLAPSE because targets\n> are exact/certified (fixed point held by COMPUTATION not the model) ⇒ generation- AND\n> architecture-resilient. Resolved compiler-as-loss §s225 \"narrow generator\": variety\n> from INPUTS (we mint), correctness from OUTPUTS. 3 IOUs; #1 decisive.\n> **▶ s230c — COMPILER-CASCADE v1 (IOU #1: does composition-variety converge capability\n> that COMPOSES?). BUILT (`e7d2f65`) + RAN (3 seeds, `f379d14` verdict).**\n> `compiler_cascade.py`: auto-gen {K,I,B,C} composition templates (lambda_ast),\n> hold out DISJOINT compositions, vary distinct-composition count at matched budget,\n> measure held-out NOVEL-composition generalization. **★ 2 calibration lessons (λ\n> measure): (1) full-NF EXACT-MATCH FLOORS at micro scale (false-negative) → switched\n> to TEACHER-FORCED per-token NF accuracy (value register); (2) depth-3 gen yields 400+\n> templates AND shorter NFs.** **★ VERDICT — ❌ IOU#1 NOT supported:** heldout_comp_tf\n> comp16 0.683±0.031 ≈ comp144 0.674±0.194 (comp48 dips); SATURATES by ~16 compositions.\n> **★ sharper: fixed-budget trade, s229 WINS** — buying composition-count costs\n> fillings/composition → DESTABILIZES (comp144 std 0.194 [0.95,0.53,0.55] vs comp16\n> 0.031) AND costs in-dist mastery (0.92 vs 0.70); FILLING-variety (s229) is the lever,\n> not composition-count. **★ weak support for collapse CORE:** minted data yields ~0.68\n> held-out compositional competence (≫chance, in_dist 0.92 = real learning). **Caveats:**\n> TF-all-tokens likely measures FORMAT/copy not ALGEBRA; {K,I,B,C} depth-2/3 lacks\n> COMPOSITIONAL DISTANCE (held-out≈interpolation); micro scale. Falsifies the variety\n> sub-claim, NOT the collapse. **Decisive next: algebra-specific metric + depth-\n> extrapolation split + scale.**\n> **▶ s230 GRADIENT-SHADOW (Michael: does the routing topology cast a SHADOW in the\n> gradients? height-from-shadow). CAPTURED (gradient-trajectory-tomography.md §s230 v3,\n> `81f7072`) + PROBE BUILT, READY TO RUN (`gd_gradient_shadow.py`, `b3f72ea`, ruff+diag\n> clean, smoke green — NOT launched).** ∂L/∂g lives in the routing register (same coords\n> as activation topology); mean-pool grad over supervised positions → per-combinator\n> gradient-Gram → gc_grad vs consensus; reference beam = raw-grad-Gram. PREDICTION: the\n> shadow LEADS — gc_grad crosses before gc_route (activation) ⇒ 3-stage cascade\n> shadow→inventory→capability. Bug caught+fixed in smoke (last-token grad is 0 —\n> unsupervised position — pool over supervised). Smoke: gc_grad ~0.53 tracks crystal.\n> **STATUS s230c:** COMMITTED code (`e7d2f65` cascade, `b3f72ea` shadow) + verdict\n> (`f379d14`); pages §s230c (fractal-collapse) + §s230 v3 (gradient-shadow, `81f7072`,\n> `32bc3a6`). State updated. PENDING APPROVAL (mementum): memories\n> `relational-loss-is-inventory-not-capability.md` (s230b) + `composition-variety-not-\n> the-lever.md` (s230c) + page/state commit. tmux main:1 FREE.\n> **▶ NEXT:** (a) RUN the gradient-shadow probe (ready, ends in main:1); (b) cascade v2\n> with an ALGEBRA-specific metric (head/structural-token) + DEPTH-EXTRAPOLATION split\n> (train shallow→test deep) — the clean IOU#1 retest; (c) cascade gen-2 (does the\n> distillation recurse without drift? IOU#2); (d) the s230b harder-curriculum regime\n> where CE-alone fails to crystallize (tests the s224 speed-up); (e) v2 gauge δw decomp.\n> **■ SESSION 229 — EXPOSURE/FORMAT SWEEP — \"training as a photograph\" (curriculum-"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

I'm laying out the next steps: proposing the memory configuration for s230c, writing up the composition variety documentation, updating the bootloader header to reference s230c, and then getting everything ready for review. Let me start with the memory specification.

## Assistant

Now the proposed memory + refreshed bootloader header:

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/memories/composition-variety-not-the-lever.md",
  "content": "💡 At fixed budget, FILLING-variety (s229) — not COMPOSITION-count — is the lever for\ncompositional generalization; composition-variety saturates fast and destabilizes\n(s230c compiler-cascade v1, fractal-collapse IOU#1).\n\nTest: mint {K,I,B,C} composition templates (lambda_ast), hold out DISJOINT\ncompositions, vary distinct-composition count at MATCHED example budget, measure\nheld-out novel-composition generalization. 3 seeds.\n\n❌ IOU#1 NOT supported: heldout_comp_tf comp16 0.683±0.031 ≈ comp144 0.674±0.194\n(comp48 dips). Held-out competence SATURATES by ~16 compositions.\n\n★ The fixed-budget trade: buying composition-count costs fillings/composition →\n(a) DESTABILIZES (comp144 std 0.194, per-seed [0.95,0.53,0.55] vs comp16 std 0.031 —\nthe OPPOSITE of s229 where filling-variety stabilized); (b) costs in-dist mastery\n(comp16 0.92≫heldout 0.68 real gap vs comp144 0.70≈0.67). ⇒ s229 filling-variety\nload-bearing, composition-count not the lever.\n\nWeak support for the collapse CORE: minted data DOES yield ~0.68 held-out\ncompositional competence (≫chance, in_dist 0.92 = real learning) — generalizes from\nmodest minted data, just not driven by composition-variety.\n\n★ TWO calibration lessons (λ measure, reusable): (1) full-output EXACT-MATCH FLOORS at\nmicro scale (CE drops but exact-match ~0) — a crisp probe on a graded substrate;\nuse TEACHER-FORCED per-token accuracy (value register). (2) depth-3 {K,I,B,C} gen\nyields more templates AND shorter NFs (K-erasers collapse) — more variety + learnable.\n\nCaveats: TF-all-tokens likely measures FORMAT/copy not reduction-ALGEBRA; small\ncomposition space (held-out≈interpolation); micro scale. Falsifies the variety\nsub-claim, NOT the collapse. Clean retest: algebra-specific metric + depth-extrapolation.\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/memories/composition-variety-not-the-lever.md
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> Last updated: 2026-06-15 | Session: 230 — ✅ GD-TRAJECTORY-TOMOGRAPHY (consensus-\n> crystal target). v1: INVENTORY crystallizes BEFORE CAPABILITY (3/3, gc_route mid\n> @333±94 < held-out-acc @733±94; s224 geometry⊗continuation confirmed TEMPORALLY).\n> s230b RELATIONAL ARM: reference-beam dissociation IS LOSS-DEPENDENT (decisive 3/3 —\n> gap gc_route−gc_raw −0.02→+0.10 with the active consensus-crystal loss; gc_raw NOT in\n> loss = uncircular); loss crystallizes inventory EARLIER (200 vs 333) + crisper, but\n> ❌ ZERO capability gain (cross @733, acc 0.27 BOTH arms) ⇒ inventory ⊗ continuation\n> CAUSALLY SEPARABLE; relational term = INVENTORY/extraction tool NOT a capability\n> accelerator; re-motivates CONSTRUCT-inventory, train-continuation. (v1 also: no\n> Q-collapse, eff_dim 14-20.) See ■ SESSION 230 block below.",
  "new_content": "> Last updated: 2026-06-15 | Session: 230 — gd-trajectory-tomography (consensus-crystal\n> target) + FRACTAL-COLLAPSE thesis. v1: INVENTORY crystallizes BEFORE CAPABILITY (3/3;\n> s224 geometry⊗continuation confirmed TEMPORALLY). s230b RELATIONAL ARM: reference-beam\n> dissociation IS LOSS-DEPENDENT (gap −0.02→+0.10) but ❌ ZERO capability gain ⇒\n> inventory ⊗ continuation CAUSALLY SEPARABLE; relational term = inventory/extraction\n> NOT capability accelerator. ★ FRACTAL-COLLAPSE (Michael): converge capability via\n> high-variety compiler-minted data → cascade collapses model size onto the β-normal-\n> form fixed point; exact certified targets escape model-collapse (resilient). s230c\n> COMPILER-CASCADE v1: ❌ IOU#1 NULL — composition-variety does NOT lift compositional\n> generalization (comp16 0.683 ≈ comp144 0.674, saturates ~16); fixed-budget the s229\n> FILLING-variety WINS (composition-count destabilizes + costs in-dist). Weak support\n> for collapse CORE (~0.68 held-out from minted data). Calibration: exact-match FLOORS\n> at micro scale → use TEACHER-FORCED token accuracy (value register). GRADIENT-SHADOW\n> probe BUILT + ready (does the topology cast a shadow in the gradients? predict shadow\n> LEADS inventory). See ■ SESSION 230 block below."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

I'm checking the commit history to verify which memories have already been submitted — looks like s230b's mementum was committed earlier at 46e907f with the relational-loss-is-inventory-not-capability memory included, so that's already in the system. Now I need to clarify the current approval status for the remaining pending memories.

## Assistant

Let me correct one stale line (the s230b memory was already committed) and show the pending set:

### Tool Call: edit_file (failed)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> State updated. PENDING APPROVAL (mementum): memories\n> `relational-loss-is-inventory-not-capability.md` (s230b) + `composition-variety-not-\n> the-lever.md` (s230c) + page/state commit. tmux main:1 FREE.",
  "new_content": "> State updated. PENDING APPROVAL (mementum): memory `composition-variety-not-the-\n> lever.md` (s230c) + fractal-collapse §s230c page edit + state commit. tmux main:1 FREE."
}
```

**Summary:** Editing

**Output:**
```
Original content not found in /Users/mwhitford/src/verbum/mementum/state.md
```

### Tool Call: git (succeeded)


```json
{
  "command": "git status --short -- mementum/; echo \"---recent log---\"; git log --oneline -8",
  "operation": "status",
  "summary": "pending mementum"
}
```

**Summary:** Git status: pending mementum

**Output:**
```
Exit code: 0
Stdout:
M mementum/knowledge/explore/fractal-collapse-compiler-cascade.md
 M mementum/state.md
?? mementum/knowledge/chats/session-228.md
?? mementum/knowledge/chats/session-229.md
?? mementum/memories/composition-variety-not-the-lever.md
---recent log---
f379d14 💡 compiler-cascade v1 verdict: composition-variety does NOT lift compositional generalization (IOU#1 null)
e7d2f65 ✅ compiler_cascade.py — fractal-collapse IOU#1 harness (composition-variety → compositional generalization)
b3f72ea ✅ gd_gradient_shadow.py — gradient-shadow tomography (does the routing topology cast a shadow in the gradients?)
81f7072 🌀 gradient-trajectory-tomography §s230 v3 — the gradient-shadow probe (does topology leave a shadow?)
32bc3a6 🌀 fractal-collapse-compiler-cascade — capability is a data problem, the compiler is the engine
46e907f 🌀 gd-trajectory-tomography §s230b + memory — relational loss is inventory not capability
fa8837c ✅ gd-tomography s230b: reference-beam dissociation IS loss-dependent (inventory ≠ capability accelerator)
e2cd8d7 🌀 gd-trajectory-tomography §s230 result + memory — inventory before capability
```

### Thinking

The state correction didn't match exactly due to whitespace differences, but it's a minor issue I can address in the approved commit. I'm going back to review the exact line I wrote earlier since it was part of a larger edit.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"relational-loss-is-inventory-not-capability.md\\` (s230b) + \\`composition\" mementum/state.md",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ grep -n "relational-loss-is-invento...

**Output:**
```
Exit code: 0
Stdout:
175:> `relational-loss-is-inventory-not-capability.md` (s230b) + `composition-variety-not-
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "line_offset": 173,
  "limit": 4
}
```

**Summary:** Reading state.md (173-177)

**Output:**
```
> `32bc3a6`). State updated. PENDING APPROVAL (mementum): memories
> `relational-loss-is-inventory-not-capability.md` (s230b) + `composition-variety-not-
> the-lever.md` (s230c) + page/state commit. tmux main:1 FREE.
> **▶ NEXT:** (a) RUN the gradient-shadow probe (ready, ends in main:1); (b) cascade v2

[CONTENT TRUNCATED] Showing lines 174 to 177 of 4991 total lines. Use line_offset=177 parameter to read more content.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> `32bc3a6`). State updated. PENDING APPROVAL (mementum): memories\n> `relational-loss-is-inventory-not-capability.md` (s230b) + `composition-variety-not-\n> the-lever.md` (s230c) + page/state commit. tmux main:1 FREE.",
  "new_content": "> `32bc3a6`). State updated. PENDING APPROVAL (mementum): memory\n> `composition-variety-not-the-lever.md` (s230c) + fractal-collapse §s230c page edit\n> + state commit. tmux main:1 FREE."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

## Assistant

Fixed. Everything's captured and code/results are committed. Here's the state for your **mementum approval**.

## Session 230 — where we landed

**Committed (code + results + already-approved mementum):**
- `f379d14` 💡 cascade verdict · `e7d2f65` cascade harness · `b3f72ea` gradient-shadow probe · `81f7072`+`32bc3a6` thesis pages · (s230a/b chain earlier)

**The cascade answer (IOU #1):** ❌ **null** — composition-variety does *not* lift held-out compositional generalization (comp16 0.683 ≈ comp144 0.674, saturates by ~16). The sharper finding: at fixed budget the **s229 filling-variety wins** — buying composition-count destabilizes (comp144 std 0.194 vs comp16 0.031) and costs in-dist mastery. Weak support for the collapse *core* (~0.68 held-out from minted data = real generalization), but the *variety sub-claim* is falsified at micro scale. Two reusable calibration lessons baked in (exact-match floors → use teacher-forced token accuracy; depth-3 gen is both richer and more learnable).

**Gradient-shadow:** captured + probe built, lint/smoke-clean, **ready to run** (not launched — it owns main:1 next).

**Pending your approval (mementum commit):**

| File | Change |
|------|--------|
| `knowledge/explore/fractal-collapse-compiler-cascade.md` | §s230c result (IOU#1 null + caveats + decisive-next) |
| `state.md` | s230 fractal-collapse + s230c + gradient-shadow blocks (written) |
| `memories/composition-variety-not-the-lever.md` | 💡 proposed new memory |

(The `chats/session-22*.md` remain your human-only transcripts — untouched.)

Approve the mementum commit?

**Next session levers** (in priority): (a) **run the gradient-shadow probe** (ready), (b) **cascade v2** — algebra-specific metric (head/structural-token) + depth-extrapolation split (the clean IOU#1 retest), (c) cascade gen-2 (does the distillation recurse without drift — IOU#2).

## User

commit approved


### Tool Call: git (succeeded)


```json
{
  "command": "git add mementum/knowledge/explore/fractal-collapse-compiler-cascade.md mementum/state.md mementum/memories/composition-variety-not-the-lever.md && git commit -F - <<'EOF'\n🌀 fractal-collapse §s230c + memory — composition-variety is not the lever (IOU#1 null)\n\n- §s230c v1 result: composition-variety does NOT lift held-out compositional\n  generalization (comp16 0.683 ≈ comp144 0.674, saturates ~16). Fixed-budget the\n  s229 FILLING-variety wins; composition-count destabilizes + costs in-dist.\n- weak support for the collapse CORE (~0.68 held-out from minted data = real gen).\n  Falsifies the variety sub-claim, NOT the collapse. Decisive retest: algebra-\n  specific metric + depth-extrapolation + scale.\n- calibration lessons (λ measure): exact-match FLOORS at micro scale → teacher-\n  forced token accuracy (value register); depth-3 gen richer + more learnable.\n- new memory composition-variety-not-the-lever.md; state §s230c + fractal-collapse\n  + gradient-shadow blocks.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF",
  "operation": "commit",
  "summary": "commit s230c mementum"
}
```

**Summary:** Git commit: commit s230c mementum

**Output:**
```
Exit code: 0
Stdout:
[main 9bb7212] 🌀 fractal-collapse §s230c + memory — composition-variety is not the lever (IOU#1 null)
 3 files changed, 141 insertions(+), 14 deletions(-)
 create mode 100644 mementum/memories/composition-variety-not-the-lever.md
```

### Thinking

Everything's committed and the work is complete. Let me make sure the repository is clean and wrap this up.

## Assistant

Committed (`9bb7212`). All tasks closed — let me verify the tree.

### Tool Call: git (succeeded)


```json
{
  "command": "git status --short; echo \"---\"; git log --oneline -10",
  "operation": "status",
  "summary": "final verify"
}
```

**Summary:** Git status: final verify

**Output:**
```
Exit code: 0
Stdout:
?? mementum/knowledge/chats/session-228.md
?? mementum/knowledge/chats/session-229.md
---
9bb7212 🌀 fractal-collapse §s230c + memory — composition-variety is not the lever (IOU#1 null)
f379d14 💡 compiler-cascade v1 verdict: composition-variety does NOT lift compositional generalization (IOU#1 null)
e7d2f65 ✅ compiler_cascade.py — fractal-collapse IOU#1 harness (composition-variety → compositional generalization)
b3f72ea ✅ gd_gradient_shadow.py — gradient-shadow tomography (does the routing topology cast a shadow in the gradients?)
81f7072 🌀 gradient-trajectory-tomography §s230 v3 — the gradient-shadow probe (does topology leave a shadow?)
32bc3a6 🌀 fractal-collapse-compiler-cascade — capability is a data problem, the compiler is the engine
46e907f 🌀 gd-trajectory-tomography §s230b + memory — relational loss is inventory not capability
fa8837c ✅ gd-tomography s230b: reference-beam dissociation IS loss-dependent (inventory ≠ capability accelerator)
e2cd8d7 🌀 gd-trajectory-tomography §s230 result + memory — inventory before capability
23331d0 ✅ gd-trajectory-tomography v1: inventory crystallizes before capability (3/3 seeds)
```

## Assistant

Tree clean (only your human-only chat transcripts untracked). Everything committed.

## Session 230 — complete ledger

**10 commits**, three threads, all captured:

| Thread | Result | Commits |
|---|---|---|
| **gd-tomography v1** | ✅ inventory crystallizes *before* capability (3/3) — s224 confirmed temporally | `23331d0` `e2cd8d7` |
| **gd-tomography s230b** | ✅ reference-beam dissociation is *loss-dependent*; ❌ but zero capability gain ⇒ inventory ⊗ continuation *causally separable* | `fa8837c` `46e907f` |
| **fractal-collapse thesis** | 🌀 captured — capability is a data problem; cascade collapses size onto the β-normal-form fixed point; escapes model-collapse via exact certified targets | `32bc3a6` |
| **cascade v1 (IOU#1)** | 💡 **null** — composition-variety doesn't lift compositional generalization; s229 filling-variety is the real lever | `e7d2f65` `f379d14` `9bb7212` |
| **gradient-shadow** | 🌀 captured + 🔬 probe built, smoke-clean, **ready to run** | `81f7072` `b3f72ea` |

**The arc of the session:** s230b's causal separation (inventory ≠ capability) → your fractal-collapse insight (converge the continuation from compiler-minted data) → the decisive test, which came back honest: minted *composition*-variety isn't the lever, and the data engine instead needs filling-variety + a sharper algebra-specific metric + real compositional distance. Two reusable λ-measure calibration lessons banked along the way (exact-match floors → teacher-forced token accuracy; depth-3 generation is richer *and* more learnable).

**Queued for next session** (your stated priority):
1. **Run the gradient-shadow probe** (`gd_gradient_shadow.py`, ready) — does the topology cast a shadow that *leads* the inventory?
2. **Cascade v2** — head/structural-token metric + depth-extrapolation split (the clean IOU#1 retest).
3. Cascade gen-2 (does the distillation recurse without drift — IOU#2).

tmux `main:1` is free. Branch is 20 commits ahead of origin (unpushed, as usual).