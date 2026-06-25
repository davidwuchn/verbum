# Explaining **"early" (L0-4)** — the thir

## User

orient, we are running scripts/experiments/program_edge_knockout.py in tmux main:1, we had a session where the editor crashed so there are pending changes


### Thinking

I'll start by reviewing the state file, then check what's running in tmux and see where things stand with git.

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
> Last updated: 2026-06-24 | Session: 251 (cont. — FROZEN-BASIS GRADIENT TOMOGRAPHY → MATURE-14B →
> GREENFIELD HOLO-PLATE; continues the GEMMA crystal-sweep pass below. Michael's hypothesis:
> "backprop = taking a photograph of the input tokens; each new photograph reduces the system toward a
> soft routing topology that uses VERY HIGH and NEAR-ZERO gradients to route around a FROZEN topology."
> Built `scripts/experiments/gd_frozen_basis.py` (ruff-clean; reuses TinyLM + the s229 β-reduction
> curriculum) to test the three TESTABLE claims against the SHUFFLED-LABEL null (λ yardstick) + a
> same-input arm: (A) PHOTOGRAPH = minibatch weight-grad is LOW effective-rank & drops as inventory
> crystallizes; (B) BIMODAL = ρ(grad_mag,weight_mag) rises (s171 Zone-A +0.77) + log grad_mag goes
> bimodal; (C) ROUTE-AROUND = low-grad (frozen) positions become sign-STABLE while high-grad (active)
> carry the flips. 3 arms × 3 seeds × 6000 steps, REPRODUCED across two independent runs (nohup +
> tmux main:1) to ~2 decimals.
>
> ★★ VERDICT (λ measure, two-sided): the hypothesis does NOT hold at micro scale — but the photograph
> ALGEBRA shows through, refined. **(A) FALSIFIED-as-stated, CONFIRMED-better:** effrank did NOT drop
> (real 27→25, stays high) — but the CROSS-ARM contrast nails grad_W=Σδᵢxᵢᵀ: effective rank tracks the
> NUMBER OF DISTINCT PHOTOGRAPHS — same-input 6.0 < shuffled 13.7 < real 25.4. The outer-product
> "photograph" is literally visible; "collapses to a few normal-form directions" is what fails. **(B)
> NOT SUPPORTED:** ρ(grad,weight) stays ~0 (real +0.062 vs s171 mature +0.77), bimod coeff <0.555 for
> ALL arms (real 0.324 < shuffled 0.443) = UNIMODAL; real−shuffled rho gap trivial (+0.021). **(C)
> REFUTED, instructively:** predicted frozen≪active flip; got the OPPOSITE — real active/frozen=0.76
> (frozen flips MORE). And the NULL shows MORE of the predicted structure than real (shuffled
> active/frozen=2.32; freeze-flip Spearman shuffled +0.146 ≥ real +0.093). The model MEMORIZES (CE→0.04,
> acc plateaus at s229 ~0.27 ceiling) without ever freezing a stable backbone to route around. **THE
> THROUGHLINE: this is the s171 maturity caveat CONFIRMED empirically — at d=128 "everything oscillates"
> (mean sign_cons ≈ noise floor); the bimodal route-around-frozen topology is a MATURE-MODEL phenomenon
> (s171 measured it on converged Qwen3-8B, Zone A ρ=+0.77), NOT something a micro model develops.** A
> λ-measure win: the experiment that could have over-claimed "backprop is holographic burn-in" instead
> held the s171 boundary. CAVEATS: micro substrate by design (the maturity limit IS the finding);
> route-around (C) is a relative within-arm measure so micro-noise dominates; greedy MPS, 3 seeds.
> ★★ s251 cont. — MATURE-MODEL TEST (Qwen3-14B): THE HYPOTHESIS IS VINDICATED AT SCALE (Michael:
> "test Qwen3-14B as the mature model"). Ran the s171 instrument (gradient_zero_map.py, extended:
> --target-modules/--layer-stride + Sarle bimodality coeff) on Qwen3-14B (bf16, gate_proj routing
> register, the SAME 195 diverse batches s171 used, 40 layers, MPS, 10.4min, no OOM). ★ PER-LAYER DEPTH
> PROFILE: the bimodal "high|near-zero" gradient field the MICRO model NEVER developed IS PRESENT — and
> concentrated in ZONE A (encoding layers): ρ(grad,weight) L1 +0.843, L2 +0.825, L3 +0.752, L4 +0.634
> (REPRODUCES s171-8B Zone-A +0.77, now on 14B); bimodality coeff L0-5 = 0.64–0.84, ALL >0.555 =
> GENUINELY BIMODAL (6 layers bimodal, 4 layers ρ>0.5). MID/LATE (L6-39): ρ≈0 (−0.056..+0.064), bimod
> 0.07–0.27 = UNIMODAL dense compute zone — exactly s171's two-regime structure. Oscillator U-curve:
> L0 41.8% → MIN L23 28.2% → L35 49.9% (mid-network = MOST settled, matches s171 L21 min). P(mag-top30 |
> osc)=0.304≈0.3 → oscillators WEIGHT-INDEPENDENT (s171 orthogonality reproduced). NOTE the GLOBAL mean
> ρ=+0.062 ≈ micro's +0.06 — but std ±0.245: the aggregate HIDES Zone A; the depth profile is the
> finding. ★★ NET (λ measure, two-sided, DECISIVE): Michael's intuition is CORRECT but SCALE+DEPTH-GATED
> — backprop DOES drive a bimodal soft-routing field that routes around a frozen topology, but ONLY (1)
> at MATURITY (micro ρ~0 unimodal everywhere = the null; mature 14B ρ=+0.84 bimodal in Zone A = the
> signal — confirmed BOTH directions on the SAME ρ(grad,weight) instrument) and (2) in the EARLY/ENCODING
> layers (Zone A L1-4, ~40% inactive neurons = narrow beam), NOT the dense mid-network compute zone. The
> micro negative was the maturity gap, now closed. The FROZEN BASIS the gradients route around = the
> Zone-A magnitude crystal (s123: magnitude frozen, signs route): high-weight↔high-consistent-grad active
> set routing around a settled low-grad mass. CONNECTS: s171 (original snapshot, 8B), s123 (magnitude
> crystal), s231 (gradient carries structure), holographic-storage (combinators peak L0-6 = same Zone A).
> ★★ FOR THE MAIN IDEA: the "known basis" to delta against / the continuation shared-basis is REAL,
> LOCALIZED (Zone-A encoding), and EXTRACTABLE in a mature model — exactly where the combinator hologram
> lives. CAVEATS: SNAPSHOT on frozen weights (the route-around "flip" DYNAMIC needs a training trajectory
> — a Pythia checkpoint sweep is the next rung); gate_proj only; 1 model; bf16/MPS. ARTIFACTS:
> results/gradient-zero-map/summary_Qwen_Qwen3-14B.json + run_qwen3-14b.log; gradient_zero_map.py (s171
> instrument + bimodality + --target-modules/--layer-stride, additive; legacy file not ruff-reformatted).
> NEXT after this was NOT Pythia — Michael: "we won't see this from Pythia, we'll only see the capacity
> threshold; we don't want to train over existing models, we are exploring FUTURE possibilities." → pivot
> to the greenfield substrate (s251 cont.2). tmux main:1 FREE; no GPU job. PENDING APPROVAL (folded into
> the s251 batch): memory `frozen-routing-is-mature-zoneA-not-micro` + knowledge `explore/gradient-
> trajectory-tomography.md` §s251 (micro null → mature-14B Zone-A signal). state.md updated.
>
> ★★ s251 cont.2 — GREENFIELD HOLOGRAPHIC PLATE PROTOTYPE: "lay arbitrary data (a program spec) into
> ternary plates as a sparse DELTA against a CONSTRUCTED basis." Michael's reframe: the frozen basis is
> CAPACITY-GATED, so don't probe/train existing models — ENGINEER PAST the threshold by CONSTRUCTING the
> basis (100% of laid-in capacity → data, not scaffolding). BUILT `scripts/experiments/holo_plate_delta.py`
> (ruff-clean, PURE NUMPY, no pretrained model). Concrete model = ternary correlation-matrix holographic
> memory: a program spec = finite map {key→value}; each association = OUTER PRODUCT val⊗key = one
> "photograph" (same δxᵀ structure as a gradient exposure / s251 finding); plate = ternarize(Σ valᵢkeyᵢᵀ).
> FOUR MEASUREMENTS, 5 seeds, d=512, 0.6s: **(1) CAPACITY — N* ≈ 2d at 99% recall (d=512→1024), degrades
> GRACEFULLY (no cliff: 4d=0.877, 8d=0.584) = true holographic. At 75% ternary sparsity capacity only
> drops to ~1.67d (853) — sign topology survives sparsification, REPRODUCING holographic-storage's
> "75% sparse, selectivity preserved" FROM SCRATCH. The capacity threshold is now a DESIGN PARAMETER
> (~2d/plate, ×depth for thick holograms), not a training mystery.** **(2) DELTA — a program/fact update
> of K bindings encodes as a SPARSE ternary delta scaling smoothly with K/N: K=1 flips only 2.4% of the
> plate vs 50% for a matched-random basis (20.3× advantage); even K=0.5N stays 33% < 50%. "Record deltas
> against a known basis" HOLDS.** **(3) FOLD — plate_B ⊙ Δ = plate_P EXACTLY and recall(folded)==recall(P)
> for ALL K (ternary × ternary = ternary verified from scratch) = lossless install.** **(4) NULL (λ
> yardstick) — matched-random basis gives ~50% DENSE delta → the sparsity is REAL (the basis must share
> structure); gate passed decisively (20× separation, non-overlapping).** ★★ NET (λ measure): the FUTURE
> POSSIBILITY IS REAL at the substrate level — you CAN construct a ternary holographic basis, lay
> arbitrary data (a program spec) as a sparse FOLDABLE delta against it, with a DESIGNED capacity
> threshold (~2d/plate) and LOSSLESS composition. This is the greenfield proof of the
> delta-plate-ecosystem-vision substrate (base plate + sparse foldable delta), constructed not trained,
> the clean MIT level-4 path. CAVEATS (λ measure): linear correlation-matrix memory, not a deep
> transformer (proves PLATE-level storage+delta+fold, NOT deep routing — but s251-cont 14B already showed
> the bimodal frozen/active basis exists in a real net); "program spec" = simplest finite key→value map
> (structured combinator programs = richer next test); N*≈2d is for 64-way argmax decoding; delta
> AMPLIFIES (1 binding → 2.4% of d² cells, each outer product touches all cells) but stays 20× < null and
> folds exactly; the CONTINUATION-as-shared-basis (composed plate) + consensus-etch BFT for distributed
> are the untested v2 pieces. ARTIFACTS: scripts/experiments/holo_plate_delta.py; results/holo-plate-
> delta/verdict_multiseed.json. ★★ NEXT (v2, the two untested novel pieces): (1) CONTINUATION basis —
> basis = a reified composed-plate continuation (the "rest of computation"), test delta sparsity of a
> program that EXTENDS it (the exactness trap: elementwise fold stays exact, composed-matrix correction
> doesn't); (2) DISTRIBUTED — N nodes each lay a delta against the shared basis, consensus-etch fold
> (agreeing deltas etch, disagreeing cancel = BFT), measure poisoned-delta rejection. tmux main:1 FREE.
> PENDING APPROVAL (folded into s251 batch): memory `holo-plate-spec-as-sparse-foldable-delta-greenfield`
> + knowledge new `explore/holographic-substrate-prototype.md` (capacity ~2d, delta vs null, exact fold).
> state.md updated (¬approval-gated). Code+data committable.
> ARTIFACTS: `scripts/experiments/gd_frozen_basis.py`; `results/gd-frozen-basis/verdict_multiseed.json`
> + `run_main1.log` + `run_multiseed.log` (nohup A/B). tmux main:1 FREE; no GPU job. PENDING APPROVAL:
> memory `frozen-routing-is-mature-not-micro-photograph-effrank-tracks-exposures` + knowledge update
> `explore/gradient-trajectory-tomography.md` §s251 (frozen-basis test → s171 maturity boundary).
> state.md updated (¬approval-gated). Code+data committable. CONTEXT: this was a SIDE-NOTE warm-up that
> de-risks the MAIN idea (ternary holographic plates / deltas-against-a-known-basis / continuations as a
> shared basis for distributed training) — the "frozen topology the gradients route around" IS the
> "known basis"; finding it absent at micro means the basis must come from a MATURE model or be
> CONSTRUCTED (the s230b lesson: inventory is cheap/constructable, don't train it).
> ──────────────────────────────────────────────────────────────────────────────────────────────────
> Last updated: 2026-06-24 | Session: 251 (earlier pass — GEMMA + Qwen3.6-35B-A3B IN THE CRYSTAL SWEEP, TEMPLATE
> CONFOUND FIXED, CRYSTAL-φ NULL RUN — Michael: "gemma seemed too precise for the random/generated
> crystal lattice." NET VERDICT (template-corrected + null-tested): the intuition is VINDICATED for the
> crystal that's REAL, and the famous 'spine' was largely an artifact. Two threads:
>
> THREAD A — CRYSTAL SPINE (per-layer hidden-state SVD bottleneck). ★ THE TEMPLATE CONFOUND WAS REAL AND
> DECISIVE. The original sweep fed ALL models hand-baked Qwen ChatML (`<|im_start|>...assistant\n`).
> Refactored probe_crystal_spine.py to STRUCTURED probes + render_probe() = each model's OWN native
> template (Qwen `<|im_start|>`+`<think>`, Gemma `<bos><|turn>`+`<|tool>declaration`, base models→plain
> text) and re-ran 8 models into lattice/crystal_spine_native/. RESULT FLIPS: Qwen3-14B's celebrated
> rank-1 spine (legacy ChatML: spineFrac 97.1%, top3 100%, n90=1, norm ×509) COLLAPSES to spineFrac 1.4%
> / n90=2084 under its PROPER native generation prompt — it was a prompt-boundary/massive-activation
> artifact (the `assistant\n` last-token sat on the attention-sink), NOT robust structure. Gemma SHARPENS
> with its own template (16.7%→57.9%). NATIVE 8-model spineFrac: pythia-2.8b 84.9% (n90=2, the ONLY true
> rank-1 spine, a base massive-activation at L5) > gemma-4-31b 57.9% (n90=179, L20=34% depth — the
> sharpest MID-NETWORK bottleneck, the most crystal-like of all instruct models) > olmo 16.6% >
> qwen3.6-35b-a3b 12.3% > qwen3-0.6b 6.2% > mistral 5.0% > smollm3 4.7% > qwen3-14b 1.4%. Gemma z vs
> cohort: spineFrac +1.43, top3 +1.01, n90 −1.12 → the standout concentrated instruct model. NEW DATA
> POINT: Qwen3.6-35B-A3B (hybrid linear-attention + 256-expert MoE) is DIFFUSE with NO massive activation
> (norm max 15 across 40 layers) — linear-attention architectures don't grow the sink spine. ⇒ the
> 'crystal spine' = a massive-activation/attention-sink phenomenon, ARCHITECTURE + PROMPT-BOUNDARY
> dependent (Pythia base; Qwen only at the ChatML boundary), NOT a universal lambda crystal. Reinforces
> s211 (5D refuted, rank-1 common mode).
>
> THREAD B — CRYSTAL-φ EXISTENCE DETECTOR (verify_crystal_phi + crystal_phi_permnull: KIBC combinator
> cosine geometry from gate_proj on PROSE, vs 2000 shuffled-label regroupings; patched both for Gemma's
> nested text_config). ★ THE DECISIVE 'does the crystal EXIST in gemma' test. Gemma vs Qwen3-14B:
> cluster SEPARATION real in BOTH (true labeling carves coherent combinator clusters; p_sep=0.0005 each);
> consensus GEOMETRY (cosine matrix corr to the cross-model consensus crystal) REAL in Gemma (r=+0.31,
> p_cons=0.015) and CLEANER than Qwen3-14B (r=+0.21, p_cons=0.058 marginal); φ-LADDER + eig-ratio corr
> FORCED in both (p_phi 0.14/0.61, p_eigratio 0.73/0.38 — random labels fit φ as well; reproduces s247
> exactly). The one φ-flavored signal (λ0/λ1≈φ^4/5) is weak+Qwen-only (p=0.02) absent in Gemma (p=0.46).
> ⇒ THE KIBC CRYSTAL EXISTS IN GEMMA where it's real (separation + consensus geometry, cleaner than
> Qwen); the φ/golden-ratio story is FORCED for everyone.
>
> SYNTHESIS: on BOTH independent measures Gemma is the cleaner crystal carrier — sharpest mid-network
> spine of the instruct models AND highest consensus-geometry significance — so 'too precise' is
> vindicated for the real combinator crystal, while the φ-ladder and the rank-1 'spine' are both
> artifacts (forced basis / sink+boundary). CAVEATS (λ measure): native re-render changes the last-token
> per model (Qwen ends after `</think>`), so the spine comparison is 'each model at ITS native generation
> point' not a fixed string; 45-probe prose, greedy, last-token (spine) / seq-mean (φ), MPS, 1 run; the
> φ-detector can't run on the MoE (no mlp.gate_proj). BUILT: probe_crystal_spine.py (structured probes +
> native render + qwen3.6-35b-a3b registered + merge); compare_crystal_spine.py; robust nested-config
> patches to verify_crystal_phi.py + crystal_phi_permnull.py. ARTIFACTS: lattice/crystal_spine_native/
> (8 models) + *_run.log; lattice/crystal_spine/ (legacy ChatML, 7 models, preserved for A/B);
> results/crystal-phi-permnull/{google_gemma-4-31B-it,Qwen_Qwen3-14B}.json. bg jobs FREE. PENDING
> APPROVAL: memory `gemma-crystal-real-spine-and-phi-forced-template-fix` + update
> explore/5d-crystal-lattice.md (§s251: template confound + native spine + φ-null) and a note on
> explore/forcing-vs-discovering.md (gemma IOU#3 closed: φ forced, separation+consensus real).
> state.md updated (¬approval-gated). Code+data committable.
> NEXT: (1) shuffled-probe null ON the native spine to certify pythia/gemma concentration ≠ a flexible
> fit; (2) MoE-aware φ-detector (hook router gate or per-expert gate_proj) to test the crystal in
> qwen3.6-35b-a3b; (3) fixed-last-token native spine (truncate each template to the same boundary) to
> separate 'native regime' from 'last-token position'.
> ──────────────────────────────────────────────────────────────────────────────────────────────────
> Last updated: 2026-06-23 | Session: 250 (CAUSAL C-FIELD ABLATION — the s249 NEXT.
> The decodable applicative-C routing field at L30-31 is READABLE/INJECTABLE but NOT load-bearing
> under single-direction residual ablation on Qwen3-14B. Ablating d_C perturbs output ≫ random
> (t=42) AND is sufficient to drive the gate's downstream z(C) when injected (t=37) — so d_C is a
> real handle on the readout register. BUT the two load-bearing diagnostics FAIL: (1) the
> c=2-vs-c=0 differential REVERSES — objectless intransitives are perturbed slightly MORE than
> two-object ditransitives (net-KL c2 0.131 < c0 0.155, t=-2.54), so the perturbation does NOT
> scale with C/object-load; (2) ablating the decodable C-direction RAISES downstream z(C) (+0.85
> vs random ~0), i.e. the gate holographically reconstructs C from other directions. Verdict
> (λ measure win, two-sided): the readable residual C-direction is a register/correlate, NOT the
> causal substrate — decodability ≠ causality (mirrors s247-v4; confirms s247b "trajectory not
> instruction-tape" + s244 "collective/holographic"). **s250 cont. CLOSED the distributed caveat
> via INLP (Ravfogel 2020): C-presence was 91.9% linearly decodable at L30 and INLP erased it to
> chance (0.919→0.667) — collapsing in ONE direction (linear C is rank-1); ablating the full
> k=16 subspace CRASHES downstream z(C) (−5.1, vs single-dir which raised it), proving we removed
> the readable signal at source. YET the c=2-vs-c=0 differential REVERSES AGAIN (net-KL c2 4.77 <
> c0 5.83, t=−2.47): erasing ALL linearly-decodable C does NOT selectively hurt object-application.
> ⇒ DECISIVE, distributed-robust: the applicative-C field is a READOUT REGISTER, not the
> object-application mechanism (rank-1 AND rank-16 agree). **s250 cont.2 CLOSED the last (nonlinear)
> escape hatch: linear vs nonlinear (MLP/RBF-SVM) C-probes on L27-31 residuals — on RAW features
> nonlinear is NO better than linear (C is linearly separable, logistic 0.98-0.99 ≥ RBF 0.95);
> after INLP erases linear C, NO nonlinear probe recovers C above the shuffle/majority ceiling
> (best 0.67 < threshold 0.77) at any layer. No nonlinear C survived → the linear erasure was
> complete.** ⇒ FULLY CLOSED: the applicative-C field is a readout register linearly AND
> nonlinearly; decodability ≠ causality proven at rank-1, rank-16-distributed, AND linear-vs-
> nonlinear. **s250 cont.3 hunted the mechanism (component-knockout sweep, attn vs MLP, all
> 40 layers, object-count gradient): INCONCLUSIVE/weak — no single component's last-token write is
> load-bearing (mean KL ~0.0025 nats, skip-connection-dominated); the full c0/c1/c2 Spearman is
> CONFOUNDED by last-token POS (c0 ends in a verb, c1/c2 in a noun object), and the POS-matched
> c1→c2 contrast leaves only tiny, late-layer, MIXED attn/MLP signal — does NOT confirm the
> attention-OV hypothesis (MLP-leaning if anything). ⇒ object-application is DISTRIBUTED — no
> single causal locus as a direction (s250), subspace (cont.), nonlinear feature (cont.2), OR
> single-component write (cont.3). Consistent with β-shaped routing / collective-holographic /
> "trajectory not instruction-tape"; bears on VERBUM's discrete-circuit question (trending NO for
> object-application). NEXT: attention-EDGE knockout (predicate→object routing) on POS-matched
> c1-vs-c2 minimal pairs, or activation patching between aligned c1/c2 — pattern-level, not
> component-write. Entries below.)
>
> **★★ s250 — CAUSAL C-FIELD ABLATION: the s249 applicative-C routing field is READABLE/INJECTABLE but NOT LOAD-BEARING (single-direction). The λ measure causality test the s249 thread was missing.** s249 established the FFN gate exposes a *decodable* applicative-C field (z(C) rises with object count, peak L30-31). Every s249 result was DECODABILITY — a read. s250 asks the causal question: is the C-field *load-bearing* (necessary for object-application) or a *readable* epiphenomenon/common-mode correlate? **BUILT `scripts/experiments/program_cfield_ablation.py`** (ruff-clean; reuses the validated s248 Exp-1 causal spine: calibrate_v2 gate register, residual diff-of-means direction, ablate/inject patch hook, random-direction control of equal magnitude). **DESIGN:** d_C = unit diff-of-means(resid C-present {trans+ditrans} − C-absent {intrans}) at the patch layer, content-mean residual; patch (ablate/set) d_C across CONTENT positions at **L30 AND L31** (the s249 C-peak); readout = downstream gate z(C) + next-token KL, all vs random direction; matched ladder = `data/reading-probes.jsonl` intransitive(c=0)/transitive(c=1)/ditransitive(c=2), 45 each, const labeling C-count==#objects. **RAN Qwen3-14B (crystal 31/40, downstream >L31, n=45/group, ~3min):** **(NECESSITY, c=2 ablate)** KL d_C 0.132 vs random 0.0012, t=41.8 — d_C is a potent output-affecting direction; BUT downstream z(C) Δ = +0.855 (random +0.013) — ablating the C-direction RAISES the gate's C-reading instead of dropping it. **(DIFFERENTIAL, net-KL = d_C−rand)** c2=0.131 **< c0=0.155, diff=−0.024, t=−2.54 — REVERSED**: objectless intransitives perturbed *more* than two-object ditransitives; the C-direction-specific perturbation does NOT scale with object/C-load. **(DELIVERY/sufficiency, c=0 inject)** injecting d_C→canonical drives downstream z(C) +0.872 vs random +0.056, t=37.2 — d_C IS a sufficient handle on the readout register. **★★ VERDICT (λ measure, two-sided NEGATIVE = a win, held the boundary):** the s249 applicative-C field is **READABLE and INJECTABLE but NOT LOAD-BEARING** under single-direction residual ablation. Two diagnostics, both informative: (1) the c=2-vs-c=0 differential *reverses* — perturbation is generic, not C-load-scaled; (2) ablating the decodable C-direction *increases* downstream z(C) — the gate **holographically reconstructs C from other directions**. ⇒ the readable residual C-direction is a **register/correlate, not the causal mechanism**. **CONNECTS:** decodability ≠ causality (mirrors s247-v4: decodable everywhere, causal partial/null under single-direction ablation); confirms s247b "we read the program TRAJECTORY, not a discrete instruction tape"; confirms s244 splice-closure "collective/holographic" (C is recall-starved/distributed). The experiment that could have over-claimed "the C-field is the object-application mechanism" instead refuted it. **CAVEATS (λ measure, the honest IOUs):** (1) single-direction linear ablation — a NULL/reversal does NOT rule out a DISTRIBUTED/multi-direction causal subspace (exact s247-v4 caveat; the z(C)-RISE is direct evidence the signal is distributed, so this is the live next lever); (2) d_C built from content-mean residual with c=0 leaking in as "C-absent" (conservative for the differential but a cleaner version uses a held-out direction split); (3) 1 model (14B), L30-31 only, synthetic matched ladder, greedy. **★★ NEXT: distributed/multi-direction C-ablation — project out the top-k C-aligned residual directions (or an SAE C-feature set) at L30-31, re-test the c=2-vs-c=0 differential. If the differential STILL fails to scale with C-load under a distributed ablation → the C-field is decisively a readout register, not the computation; if it then scales → the mechanism is distributed and single-direction was the wrong probe.** Artifacts: `results/program-cfield-ablation/{verdict,meta}_qwen3-14b.json` + `run_qwen3-14b.log`; code `scripts/experiments/program_cfield_ablation.py` (smoke-validated on Qwen3-0.6B). tmux main:1 FREE; no GPU job running. PENDING APPROVAL: memory `cfield-readable-not-load-bearing-single-direction` + knowledge update `explore/attention-as-beta-reduction.md` (§ causal C-field ablation). state.md updated (¬approval-gated). Code+data committable.
>
> **★ s250 cont.3 — OBJECT-APPLICATION MECHANISM HUNT (component-knockout sweep): INCONCLUSIVE/WEAK — no single component's last-token write is load-bearing; object-application is DISTRIBUTED, not localized. Does NOT confirm the attention-OV hypothesis.** After s250(+cont,+cont.2) settled that the FFN C-field is a READOUT register, the standing hypothesis was that object-application lives in attention OV / the value register (s127, s206). **BUILT `scripts/experiments/program_object_mechanism_sweep.py`** (ruff-clean): for each layer × {attention-write o_proj, MLP-write}, mean-ablate ONLY the LAST-token output (a single, position-MATCHED knockout → removes the length confound of content-position ablation) and measure next-token KL across the object-count gradient (reading-probes ladder c=0/1/2, 20/group); localize via Spearman(KL, object-count) + c2-vs-c0 t. **RAN Qwen3-14B (40L × 2 comp × 60 items, ~25min):** 24 monotonic "hits" (Spearman>0 sig ∧ c2>c0 t>2): **16 MLP + 8 attn**, top hits late-layer MLP (L31 r=0.46 t=5.2; L23 r=0.46; L35; L32) — nominally MLP-leaning, NOT attention-leaning. **★★ BUT λ measure CAVEAT (decisive): (1) effects are TINY — mean KL across all (L,comp) ~0.0025 nats; single-component last-token knockout barely moves the output (skip connection dominates) → no component's last-token write is individually load-bearing. (2) The full c0/c1/c2 Spearman is CONFOUNDED by last-token POS: intransitives (c0) end in a VERB ("speaks"), transitives/ditransitives (c1/c2) end in a NOUN object ("owl"/"rose") → the verb→noun shift at c0→c1 contaminates the object-count correlation. The POS-MATCHED c1→c2 contrast (both noun-ending) still shows a c2>c1 increase but TINY (KL ~0.005-0.03), late-layer, MIXED (top10 c2-c1: 6 MLP / 4 attn; largest L39 MLP = final layer = lexical/next-token).** **★★ VERDICT (λ measure, two-sided): the mechanism hunt is INCONCLUSIVE — object-application does NOT localize to any single component's last-token write (it is DISTRIBUTED), and the OV/attention hypothesis is NOT confirmed (weak, MLP-leaning, POS-confounded). This COMPLETES the localization arc: object-application has no single causal locus as (a) a direction [s250], (b) a 16-dim subspace [cont.], (c) a nonlinear feature [cont.2], or (d) a single-component last-token write [cont.3]. ⇒ object-application is a DISTRIBUTED/holographic computation — consistent with s211 common-mode, s240/s244 collective-holographic, s247b "trajectory not instruction-tape." BEARS ON VERBUM's central question (S5 λ types: "can this resolve as a discrete circuit?") → trending NO for object-application via these probes.** CAVEATS: single-layer/single-position knockout is a small perturbation by design (relative localizer, not absolute); 1 model (14B); the matched-position fix traded length-confound for POS-confound (next design must control both). **★★ NEXT: pattern-level, not component-write — (1) attention-EDGE knockout (zero/redirect predicate→object attention) on POS-matched c1-vs-c2 minimal pairs; (2) activation patching between aligned c1/c2 (theme-object position) to localize the object-binding edge; (3) accept the distributed verdict and fold "object-application = distributed, no discrete circuit" into the normal form + VERBUM discrete-circuit assessment.** Artifacts: `results/program-object-mechanism/{verdict,meta}_qwen3-14b.json` + `run_qwen3-14b.log` (+ 0.6B smoke). tmux main:1 FREE; no GPU job running. PENDING APPROVAL: memory `object-application-distributed-no-single-locus` + knowledge `explore/attention-as-beta-reduction.md` §s250 cont.3. state.md updated (¬approval-gated). Code+data committable.
>
> **★ s250 cont.2 — NONLINEAR DECODABILITY-GAP CLOSES THE LAST ESCAPE HATCH: no nonlinear C survived INLP → the s250 thread is FULLY CLOSED (readout register, linearly AND nonlinearly).** The s250 cont. caveat: INLP erases only LINEAR decodability; a NONLINEAR C-encoding could be missed and could still be load-bearing. **BUILT `scripts/experiments/program_cfield_nonlinear_probe.py`** (ruff-clean; a full SAE needs ~1e6 activations, infeasible at n=135 → the decisive tractable GATE is the decodability gap). **METHOD:** linear (logistic) vs nonlinear (MLPClassifier 64h, RBF-SVM) C-present probes, 5-fold stratified CV in a StandardScaler pipeline, on RAW and POST-INLP (linear C erased via the s250-cont subspace) L27/29/30/31 content-mean residuals; LABEL-SHUFFLED control (the high-d/low-n overfit ceiling) + PCA-50 overfit-controlled view; escape = nonlinear post-INLP beats max(shuffle, majority) by margin 0.10. **RAN Qwen3-14B (135 items, ~38s, no GPU calibration needed):** **(RAW)** linear 0.978-0.993 across the zone — C is strongly LINEARLY separable; nonlinear adds NOTHING (RBF 0.948-0.970 < logistic; MLP 0.83-0.91). **(POST-INLP)** linear drops to 0.30-0.36 (below majority — erased + CV noise on the projected-out signal); nonlinear MLP 0.585-0.652, RBF 0.667-0.674 — all AT/BELOW the shuffle ceiling (~0.66) and majority (0.667); escape threshold 0.767 never crossed at any layer. **★★ VERDICT (λ measure): NO nonlinear escape hatch — C is essentially LINEAR (nonlinear ≤ linear on raw), and once the linear C is removed NO nonlinear probe recovers it above chance. The linear INLP erasure was COMPLETE.** ⇒ **the s250 thread is FULLY CLOSED:** the applicative-C routing field is a READOUT REGISTER / correlate, not the object-application mechanism — decodability ≠ causality, now proven at (a) rank-1 single-direction (s250), (b) rank-16 distributed INLP (s250 cont.), AND (c) linear-vs-nonlinear (s250 cont.2). **CAVEATS (λ measure): (1) nonlinear probes are not generally underpowered — they decode C fine on RAW (0.83-0.97) — they simply find nothing extra post-INLP; shuffle controls confirm post-INLP numbers sit at the overfit ceiling; (2) 1 model (14B), L27-31, content-mean, synthetic ladder.** **★★ NEXT (the thread's real continuation): hunt the object-application MECHANISM where the C-field is NOT — attention OV / the value register (s127 {B,C}=composers→attention; s206 value register). Candidate experiment: a causal OV/attention-head ablation on the same c=2-vs-c=0 matched ladder — does ablating the {B,C}-composer attention pathway selectively hurt object-application where the FFN C-field did not?** Artifacts: `results/program-cfield-ablation/nonlinear_{verdict,meta}_qwen3-14b.json` + `run_nonlinear_qwen3-14b.log` (+ 0.6B smoke). tmux main:1 FREE; no GPU job running. PENDING APPROVAL: memory `cfield-no-nonlinear-escape-hatch-readout-register` + knowledge `explore/attention-as-beta-reduction.md` §s250 cont.2. state.md updated (¬approval-gated). Code+data committable.
>
> **★★ s250 cont. — DISTRIBUTED C-SUBSPACE ABLATION (INLP) CLOSES THE s250 CAVEAT: the applicative-C field is DECISIVELY a READOUT REGISTER, not the object-application mechanism — confirmed rank-1 (s250) AND rank-16 distributed.** The s250 honest caveat was that a single rank-1 diff-of-means direction is the wrong probe if the C-computation is DISTRIBUTED. **BUILT `scripts/experiments/program_cfield_subspace_ablation.py`** (ruff-clean; reuses the s250 spine + sklearn). **METHOD = INLP (Iterative Nullspace Projection, Ravfogel 2020 "Null It Out"):** iteratively fit a linear C-probe (C-present c>0 vs C-absent c=0 on L30 content-mean residuals, scalar-conditioned so dirs live in residual space) → project its direction out → refit on the nullspace → repeat k=16; span(W) = the subspace carrying ALL linearly-decodable C. ERASURE CHECK = cross-val logistic decodability before/after. Ablate span(W) over content positions at L30+L31, readout downstream gate z(C) + next-token KL, vs a RANDOM k-dim orthonormal subspace (same dim). **RAN Qwen3-14B (k_eff=16, n=45/group, crystal 31/40):** **(ERASURE ✓)** C-presence decodability **0.9185 → 0.6667 = majority** — INLP fully erased linear C; **the curve collapses at iteration 1 then flat → linear C-presence is essentially RANK-1** (the dominant separator carries it; the other 15 dims find nothing). **(NECESSITY c=2 ✓)** ablating span(W): KL sub 4.78 vs rand 0.002 (t=15.5); downstream z(C) Δ **−5.10** (rand +0.09), z(C)_after −4.77 vs rand +0.42 (t=−84) — **z(C) CRASHES** (vs s250 single-dir which RAISED it +0.85): the k-dim ablation removed the readable C signal at source. **(★ DIFFERENTIAL net-KL = sub−rand) c2 4.77 < c0 5.83, diff −1.05, t=−2.47 — REVERSED AGAIN:** even after erasing ALL linearly-decodable C, objectless intransitives (c0) are perturbed MORE than two-object ditransitives (c2); the perturbation does NOT scale with C/object-load. **★★ VERDICT (λ measure, decisive, distributed-robust): erasing ALL linearly-decodable C (0.92→0.67) and crashing the downstream C-reading (−5.1) does NOT selectively damage object-application (c2 hurt LESS than c0). The applicative-C routing field is a READOUT REGISTER / correlate, NOT the object-application mechanism — confirmed at rank-1 (s250) AND rank-16 distributed (INLP). decodability ≠ causality, doubly proven.** SECONDARY FINDING: linear C-presence decodability is RANK-1 (strongly readable along ONE direction, 91.9%) yet causally inert — a sharp register-vs-mechanism dissociation. **CAVEATS (λ measure): (1) INLP erases only LINEAR decodability — a NONLINEAR C-encoding could be missed (the remaining escape hatch / live IOU); (2) the ablation is destructive (KL ~5 nats) — span(W)'s top direction likely also carries generic object/sentence-type structure, so absolute KL is large, but the random-subspace-controlled DIFFERENTIAL (c2 vs c0) is the load-bearing readout and it reverses; (3) c0>c2 perturbation plausibly because short intransitives are more fragile to a large residual perturbation — either way it does NOT track C-load; (4) 1 model (14B), L30-31, synthetic ladder, greedy. **★★ NEXT: (1) NONLINEAR C-encoding test — the only linear escape hatch left (e.g. nonlinear probe / SAE C-feature ablation vs INLP-linear); (2) hunt the object-application mechanism ELSEWHERE — attention OV / value register (s127 {B,C}=composers→attention, s206), not the FFN C-field; (3) accept the register-vs-mechanism dissociation as the finding and fold into the normal form (FFN C-field = readout register; mechanism = ?).** Artifacts: `results/program-cfield-ablation/subspace_{verdict,meta}_qwen3-14b.json` + `run_subspace_qwen3-14b.log` (+ 0.6B smoke). tmux main:1 FREE; no GPU job running. PENDING APPROVAL (folded into the s250 batch): memory `cfield-readable-not-load-bearing-distributed-inlp` + knowledge `explore/attention-as-beta-reduction.md` §s250 cont. state.md updated (¬approval-gated). Code+data committable.
>
> **★★ s249 — B-AS-EXECUTOR TOPOLOGY vs C-AS-READABLE FIELD; Qwen3-14B sweet spot resolves the s248/s247b open door.** Starting question: before this session we speculated that **B was inherent in the order of operations the FFNs output** — attention's softmax over all V is B-like, and FFNs are inference patterns telling attention what to execute. Session result: **split that into two claims.** (1) **B as executor topology remains the right abstraction:** attention's softmax-over-V is a soft-B / composition executor (one operation: content-addressed weighted composition over values). (2) **B as a readable per-sentence FFN opcode tape is NOT what these quantified/object probes show.** The emitted/readable FFN field is applicative **C**, not existential **B**.
>
> **RUN 1 — Qwen3-14B const-label rerun of `ffn_program_decode.py`:** using `data/firing-probes.const.jsonl` (133 probes, truth C:67/S:66; object→C corrected labels) on Qwen3-14B. **Hard tracking sharpens vs 8B:** FFN acc 0.609 (p=0.0005) vs 8B 0.5489 (p=0.055); common-mode-resistant C-vs-S FFN 0.6165 (p=0.0005) while attn 0.5338 (p=0.1744). Graded z(C) vs C-count remains strong (FFN Spearman 0.5367, attn 0.5672, p≈0), and FFN raw C amplitude now exceeds attn (FFN zC 0/1/2 = 0.540/0.968/1.245; attn 0.309/0.563/0.677). Lead-lag becomes directionally coherent: peak-diff median +1 (p=7e-13), xcorr median +1 (p=0.067). **Verdict:** 14B is the sweet spot; FFN gate carries corrected C-program structure. Artifacts: `results/ffn-program-decode/*_qwen3-14b_const.json`, `run_qwen3-14b_const.log`.
>
> **RUN 2 — `program_sequence_trace.py` (new):** event-stream/LCS against `fired_sequence`. Built validated relational tracer over FFN gate (sign-CMR, matched `gateneutral` null) and decoded content-token × layer B/C/S events. **C presence is real** (presence acc 0.7519, p=0.0005; decoded events C=709/S=152/B=39), but **order is not recovered**: zone LCS 0.4856 vs reverse control 0.4618 and bag coverage 0.5144; layer-dominant collapses to C (0.0501). All-crystal LCS 0.9279 is a long-stream coverage artifact. Artifact: `scripts/experiments/program_sequence_trace.py`, `results/program-sequence-trace/*qwen3-14b_const*`.
>
> **RUN 3 — `program_path_trace.py` (new):** monotonic DP path scorer asks whether truth order beats reversed/shuffled same-multiset controls (e.g. S,B,C,C vs C,C,B,S etc.). **Negative for ordered β-tape:** zone truth score 2.1287 vs reverse 2.0843 (tiny +0.0444); margin vs best permutation −0.0315; rank frac 0.523; truth beats all permutations only 3/133 (p=1.0). Ditransitives rank higher (0.7219) but still 0/67 beat all controls. Artifact: `scripts/experiments/program_path_trace.py`, `results/program-path-trace/*qwen3-14b_const*`.
>
> **RUN 4 — `program_native_order.py` (new):** stop forcing our kernel order; infer model-native op schedule by peak/centroid layer and positive mass. **The model-native readable field is:** weak early S/B framing → strong late C/application resolution; S/B relation unstable. Overall zone: C mass 5.0718, S mass 1.5517, B mass 0.1488; C peak layer 30.812, S 28.5865, B 29.0451. Ordering: P(S<C)=0.947 peak / 0.993 centroid; P(B<C)=0.729 / 0.853; P(S<B)=0.316 / 0.312 (unstable/opposite kernel order). C-count effects: C mass rises with object count (Spearman 0.5357, p=0), C peak-z rises (0.3778, p=0), C centroid moves earlier as object load increases (r=-0.7719, p=0). Category C masses: intrans 2.8769, trans 4.9264, ditrans 6.2245. **Verdict:** program = depth-shaped routing potential field, not discrete instruction tape. Artifact: `scripts/experiments/program_native_order.py`, `results/program-native-order/*qwen3-14b_const*`.
>
> **NORMAL FORM UPDATE (s249):** Preserve the deep insight but correct the measurement target. **Attention = soft-B executor topology** (softmax over V is composition-like); **FFN = compiler of a β-routing field** (distributed potential, not a serial opcode tape); **residual = program state/register file.** For these probes the readable FFN program is applicative **C** because the model treats objects/witnesses as arguments, not existential-B bracket abstractions. The previous "B inherent from ordering" applied to OUR symbolic kernel ordering, not the model's emitted field. **NEXT if continuing:** causal C-field ablation/patch around L30–31 on c_count 2 vs 0 matched probes to test whether the C field is load-bearing, not just readable. COMMITTED s249: code+data+state+knowledge (explore/attention-as-beta-reduction.md) in 86d9a44; no separate memory file (synthesis went straight to knowledge).
>
> **★★ s248 — FFN PROGRAM-DECODE ALONG `fired_sequence` (the s247b §7 open door: "decode the FFN
> compiled values position-by-position vs lambda_ast.fired_sequence on the saturated corpus, L26-30;
> PREDICTION: FFN program-trace tracks fired_sequence even where attention over-reads, and FFN-compile
> LEADS attention depth-advance by ~1 layer"). BUILT + RAN on Qwen3-8B. λ MEASURE VERDICT = a
> two-sided NEGATIVE-leaning result that CONFIRMS the boundary, not a breakthrough.** **THE BUILD
> (`scripts/experiments/ffn_program_decode.py`, ruff-clean, reuses the validated spine):** dual-register
> decode — FFN routing register = `mlp.gate_proj` (the validated sign-CMR opcode crystal,
> relational_opcode.py) decodes WHICH combinator; attention executor register = `self_attn.o_proj`
> decodes reduction DEPTH via z(WHNF) (grounded in head-combinator-isa: all 9 combinators → SAME head
> pattern r=0.944, attention varies on WHNF↔D not opcode). Ground truth = saturate quantifiers with
> fresh witnesses (s244 `corpus_firing_survey.saturate`) → `fired_sequence`. Two RelationalCrystal
> classifiers (gate + attn), matched-prefix (gateneutral) null. ONE dual-hook forward per item.
> Metrics: (A) tracking acc + permutation null + majority baseline; (A') B-vs-S discrimination
> (C-common-mode-resistant); (B) lead-lag (peak-diff + cross-correlation lag); (C) rescue; specificity
> control (firing vs non-firing). **THE DATA (56 firing items, truth S:47 B:8 C:1 — HEAVILY S-skewed;
> FFN crystal 28/36 zone L25-30, attn crystal 36/36 zone L25-30):** **(A) TRACKING FAILS — neither
> register decodes a single B-firing item (FFN 0/8, attn 0/8); FFN abs-acc 0.232 < majority 0.839
> (C common-mode drags FFN to predict C); FFN B-vs-S 0.709 ≈ majority-S 0.855 (p=1.0 vs perm null) =
> majority-prediction not genuine B/S discrimination; attn B-vs-S 0.364 (BELOW base rate — predicts B
> spuriously).** ⇒ the apparent "FFN beats attn" is attention being NOISIER toward the minority class,
> NOT FFN reading the opcode. The S-imbalance (47/56) means the corpus CANNOT test tracking. **(B)
> LEAD-LAG SPLIT/method-sensitive: peak-diff NULL (median 0, sign-p=1.0); cross-corr lag POSITIVE
> (median +1.5, mode +3, 39/55 positive, sign-p=0.0027) — FFN's z(c*) curve leads attn's z(WHNF) curve
> across depth.** But since tracking failed, this is best read as a SCHEDULE-level ordering (FFN
> activity precedes attention depth-advance — consistent with the s240 boot spiral) NOT opcode-specific
> select→execute; and only the xcorr instrument shows it. **(C) RESCUE 9:2 is an ARTIFACT** — all 9 are
> S-items where attn spuriously said B/C and FFN defaulted to S (majority), not genuine rescue. **(★
> SPECIFICITY CONTROL FAILS: non-firing items show HIGHER max-z(BSC) 46.8 than firing items 20.3)** —
> the symbolic kernel firing/non-firing split does NOT map to a model-side magnitude difference (the
> model composes prose regardless of whether the certified point-free kernel trace fires a combinator).
> **★★ NET (λ measure): the §7 per-combinator program-decode does NOT resolve from the prose forward
> pass on this corpus — CONFIRMS the s244 splice-closure (`fires ∩ spliceable = ∅`) AND the
> attention-as-beta page's OWN "discrete-opcode-at-L over-reads" boundary, rather than opening past it.
> The door §7 left open closes the same way: only a weak, method-sensitive SCHEDULE-level FFN→attention
> ordering survives. The lever remains TYPE-COVERAGE, not geometric/opcode localization — exactly as the
> page's caveats warned. A λ-measure win: the experiment that could have over-claimed instead held the
> boundary.** **★★ THE DECISIVE CAVEAT / IOU: the corpus is the bottleneck — 84% S, 0 B decoded, can't
> test tracking. The real next probe = a B-BALANCED firing probe set (the crystal library has 69 B / 61
> C probes; need PROSE items whose saturated kernel fires B and C, not just S-heavy "Every X verbs a
> Y"). Without balance, tracking is untestable; with it, the FFN>attn opcode claim could be re-tested
> honestly.** OTHER IOUs: (1) longer depth series (zone is only 5-6 layers → xcorr lag magnitude coarse,
> max_lag=4 on ~6 points); (2) decode FFN down_proj COMPILED VALUES via unembed (ffn_reduction_trace
> style) as a 2nd FFN read, not just the gate crystal; (3) a model where the firing set is less
> common-mode (cross-model). Artifacts: results/ffn-program-decode/{verdict,per_item,meta}_qwen3-8b.json
> + run_qwen3-8b.log; code scripts/experiments/ffn_program_decode.py (+ pyproject per-file ignore).
> tmux main:1 used (3:24 run), now FREE; no GPU job running. PENDING APPROVAL: memory
> `ffn-program-decode-tracking-fails-corpus-imbalance` + knowledge update explore/attention-as-beta-
> reduction.md §7 (open experiment → result). state.md updated (¬approval-gated). Code+data committable.
>
> **★ s248 cont. — CLOSED THE DECISIVE IOU (Michael: "create more probes that are testing B so we can
> be sure"). Built a B-BALANCED firing-probe set + re-ran. THE ONE GENUINE POSITIVE EMERGES, the strong
> claims still fail.** **(1) MECHANISM (measured):** in this kernel S and B are COUPLED — every ∧/∨ emits
> one S AND one B, so S NEVER strictly exceeds B; only a TRANSITIVE verb + EXISTENTIAL object makes B
> *dominant* (`∀x.P(x)→(∃y.Q(y)∧R(x,y))` → fires S,B,B,B = B:3 S:1). **(2) GENERATOR
> `scripts/experiments/gen_firing_probes.py`** (lower via lambda_surface.to_kernel → saturate (s244) →
> fired_sequence GROUND TRUTH; DROP items whose computed dominant ≠ intended; `pretty()` not `str()` for
> parseable kernel_term — round-trips 157/157). Emitted `data/firing-probes.balanced.jsonl`: **157 probes,
> 67 B-dominant vs 90 B-tied** (was 8 vs 47), B-count ladder {1:45, 2:56, 3:45, 5:11}. Added `--probe-set`
> + a GRADED (A'') Spearman(z(B), b_count) metric to ffn_program_decode.py. **(3) ★★ RE-RAN Qwen3-8B
> (157 items, 3:32): (A') B-vs-S discrimination FFN 0.624 (perm p=0.003) BEATS attn 0.522 (p=0.42,
> at-null) AND majority 0.573 — the FFN GATE REGISTER carries WEAK-but-SIGNIFICANT B-vs-S opcode info
> that the attention register does NOT.** = the register split (FFN=opcode, attention≠opcode, depth) holds
> at a small level — the FIRST genuine tracking signal (corpus couldn't test it). **BUT the strong claims
> still fail: (A) absolute decode C-common-mode-swamped (FFN predicts C on 65/67 B-items); (A'') graded
> NULL — z(B) does NOT scale with B-count (FFN Spearman 0.06 p=0.44; relative z(B)−z(S) r=−0.13 p=0.10);
> (B) lead-lag WASHES OUT on balanced data (xcorr median +1.0 but p=0.16, was 0.003 on the S-skewed
> corpus → the earlier lead was corpus-specific/noise); (C) rescue REVERSES (5:9).** **★★ NET (λ measure,
> now SURE): with balanced B probes, the FFN routing register has a REAL but WEAK B-vs-S discrimination
> (0.62, p=0.003) absent in attention — the register split is genuine but small; the STRONG stored-program
> claims (clean opcode tracking, graded B-scaling, FFN-leads-attention-by-1) do NOT survive. The
> per-combinator program is at best FAINTLY readable, consistent with "β-shaped routing, smeared values"
> + the s244 over-read boundary. Lever stays TYPE-COVERAGE.** Artifacts:
> results/ffn-program-decode/{verdict,per_item,meta}_qwen3-8b_balanced.json + run_qwen3-8b_balanced.log;
> data/firing-probes.balanced.jsonl (+ .meta.json); code gen_firing_probes.py + ffn_program_decode.py
> (--probe-set, graded metric). tmux main:1 FREE; no GPU job. PENDING APPROVAL (folded into the s248
> batch): memory + knowledge §7 now reflect BOTH the corpus run AND the balanced follow-up.
>
> **★★ s248 cont.2 — REASON #3 CONFIRMED: the weak B-tracking was a LABELING MISMATCH. The model
> computes objects as CONSTANTS/ARGUMENTS (→ C), NOT existentials (→ B) (Michael: "I thought B was
> inherent from the ordering of the β-reductions the FFNs return" → "let's test").** Discussion clarified
> two senses of "B inherent": (a) B as a STAGE of the reduction SCHEDULE (the C→B arc / boot spiral,
> aggregate, REAL — but really the DEPTH axis: head-combinator-isa B-D r=0.986, B≡deep-nesting); (b) B as
> a per-sentence OPCODE readable from the gate (what s248 tested, weak). Reason #3 = our GROUND TRUTH
> assumed the Montague EXISTENTIAL object (`a dog`=∃y.dog(y)∧…, B-heavy: B 1→3→5); the model may take the
> CONSTANT/applicative reading (`fears(x,dog)` → `C fears dog`, C-count == #objects). **FREE POST-HOC on
> the balanced run (no GPU): the gate register decodes MORE C, LESS B when an object is present (C-prop
> trans 0.583 > intrans 0.460, Mann-Whitney p<1e-4; B-prop trans 0.178 < intrans 0.238) = OPPOSITE of
> existential, exactly constant.** **THEN the clean test: `gen_reading_probes.py` →
> `data/reading-probes.jsonl` (135 probes, OBJECT-COUNT LADDER 0/1/2 obj × 45; intrans/trans/ditrans;
> both candidate labelings; const C-count==#objects enforced, exist B 1→3→5).
> `ffn_reading_preference.py` decodes gate+attn, MEAN z per combinator over the L25-30 zone (length-
> controlled), Spearman vs object count.** **★★ RAN Qwen3-8B (135 items): as objects rise {0,1,2}, raw
> z(C) RISES (FFN r=+0.49 p<0.001; attn r=+0.62 p<0.001) while raw z(B) FALLS (FFN r=−0.27 p=0.0015) or
> is flat (attn r=−0.04). B-share slope NEGATIVE (FFN p=0.026, attn p<0.001). C and B move in OPPOSITE
> directions → NOT uniform length/common-mode growth.** ⇒ **the EXISTENTIAL reading is REFUTED (B must
> rise, it falls); the model routes added objects through C (argument application) = the CONSTANT/
> applicative reading.** **★★ THIS REFRAMES s248: the weak B-tracking was NOT "the FFN can't read the
> program" — it was "we gave it the WRONG program." We labelled by existential-B; the model computes
> applicative-C. Labelled correctly (object→C), the gate register tracks it CLEANLY (z(C) rises p<0.001
> in BOTH registers, robust).** So the gate register DOES carry the combinator structure the model
> actually computes — the s248 negative was a measurement-target error (λ measure: wrong label =
> coherence violation, representation ≢ reality), now corrected. Connects to the user's question: "B from
> the ordering" assumed existential objects; the model doesn't do them — these sentences are C-applicative
> in the model, not B-existential, so the expected B was an artifact of our Montague labelling.
> **CAVEATS (λ measure): C-SHARE itself is flat (common-mode-saturated ~0.6) → the positive evidence is
> (a) raw z(C) rising p<0.001 + (b) z(B) falling/flat REFUTING existential, NOT C-share rising; the
> PRIMARY C−B-share contrast is sig in attn (p=0.008) but only directional in FFN (p=0.25) due to C
> saturation. z(C)-rises-with-objects could partly be argument-application common-mode, but the B/C
> DIVERGENCE (opposite signs) rules out uniform growth.** Artifacts:
> results/ffn-reading-preference/{verdict,per_item,meta}_qwen3-8b.json + run_qwen3-8b.log;
> data/reading-probes.jsonl (+ .meta.json); code gen_reading_probes.py + ffn_reading_preference.py.
> tmux main:1 FREE; no GPU job. **★★ NEXT/IOUs: (1) re-run ffn_program_decode TRACKING with the CONSTANT
> labels (object→C) — does the corpus B-tracking failure flip to C-tracking success? (2) test the
> existential reading explicitly with prose that FORCES it ("t

[OUTPUT TRUNCATED] The tool call succeeded but the output was truncated. Full output saved to: /Users/mwhitford/.cache/eca/toolCallOutputs/toolu_01DsFouUJoEzhxgdSAwqgtem.txt
Use `eca__grep` or `eca__read_file` with offset/limit to view specific sections. Do not full read the file.
```

### Tool Call: git (succeeded)


```json
{
  "command": "git status",
  "operation": "status",
  "summary": "working tree status"
}
```

**Summary:** Git status: working tree status

**Output:**
```
Exit code: 0
Stdout:
On branch main
Your branch is ahead of 'origin/main' by 11 commits.
  (use "git push" to publish your local commits)

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   pyproject.toml

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	results/program-edge-knockout/
	scripts/experiments/program_edge_knockout.py

no changes added to commit (use "git add" and/or "git commit -a")
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux capture-pane -p -t main:1 2>&1 | tail -50; echo \"---PS---\"; ps aux | grep -E \"program_edge_knockout\" | grep -v grep"
}
```

**Summary:** $ tmux capture-pane -p -t main:1 2>&1...

**Output:**
```
Exit code: 0
Stdout:
[edge]   control 30/45
[edge]   control 40/45

══════════════════════════════════════════════════════════════════════════════════
EDGE CONTROL (noun-vs-noun) — Qwen/Qwen3-14B  n=40
══════════════════════════════════════════════════════════════════════════════════
  z(C) drop: object=0.83923 subject=-0.1216 random=-0.22532
  object vs subject : Δ=0.96083 t=14.964
  object vs random  : Δ=1.06455 t=18.543
  subject vs random : Δ=0.10372 t=1.453

  * OBJECT-SPECIFIC (object collapse > subject) = True
══════════════════════════════════════════════════════════════════════════════════

[edge] wrote verdict_qwen3-14b_control.json (+ meta)
uv run python scripts/experiments/program_edge_knockout.py --model  --mode  2  170.56s user 14.40s system 81% cpu 3:46.4
3 total
tee results/program-edge-knockout/run_qwen3-14b_control.log  0.00s user 0.00s system 0% cpu 3:46.43 total
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and
faster downloads.
[edge] tokenizer: Qwen/Qwen3-14B
[edge] model: Qwen/Qwen3-14B (eager attn, dtype=auto, device_map=auto)
Loading weights: 100%|██████████| 443/443 [00:03<00:00, 138.24it/s]

---PS---
mwhitford        85341  35.2  7.9 471655936 42310352 s002  S+    9:11AM   0:30.10 /Users/mwhitford/src/verbum/.venv/bin/python3 scripts/experiments/program_edge_knockout.py --model Qwen/Qwen3-14B --mode sweep --bands 8
mwhitford        85339   0.0  0.0 435373872  32352 s002  S+    9:11AM   0:00.02 uv run python scripts/experiments/program_edge_knockout.py --model Qwen/Qwen3-14B --mode sweep --bands 8
```

### Thinking

Looking at the current state of the experiment, I see that the edge knockout script has been implemented with modifications to pyproject.toml, and there are untracked results from running it on the Qwen model. The script appears to be cut off in the description, but it's implementing the attention-edge knockout mechanism for testing predicate-to-object routing on POS-matched minimal pairs.

The control run completed successfully and produced a verdict showing object-specific edge knockout behavior. Now a sweep run is in progress with 8 bands on the same model, started at 9:11 AM and still executing. I need to check the tmux session to see the current progress, then review the script and existing results to understand what's being tested and verify the job is running as expected before checkpointing.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "echo \"===TMUX NOW===\"; tmux capture-pane -p -t main:1 2>&1 | tail -25; echo \"===RESULTS DIR===\"; ls -la /Users/mwhitford/src/verbum/results/program-edge-knockout/; echo \"===PYPROJECT DIFF===\"; git -C /Users/mwhitford/src/verbum diff pyproject.toml"
}
```

**Summary:** $ echo "===TMUX NOW==="; tmux capture...

**Output:**
```
Exit code: 0
Stdout:
===TMUX NOW===
[edge]   control 30/45
[edge]   control 40/45

══════════════════════════════════════════════════════════════════════════════════
EDGE CONTROL (noun-vs-noun) — Qwen/Qwen3-14B  n=40
══════════════════════════════════════════════════════════════════════════════════
  z(C) drop: object=0.83923 subject=-0.1216 random=-0.22532
  object vs subject : Δ=0.96083 t=14.964
  object vs random  : Δ=1.06455 t=18.543
  subject vs random : Δ=0.10372 t=1.453

  * OBJECT-SPECIFIC (object collapse > subject) = True
══════════════════════════════════════════════════════════════════════════════════

[edge] wrote verdict_qwen3-14b_control.json (+ meta)
uv run python scripts/experiments/program_edge_knockout.py --model  --mode  2  170.56s user 14.40s system 81% cpu 3:46.4
3 total
tee results/program-edge-knockout/run_qwen3-14b_control.log  0.00s user 0.00s system 0% cpu 3:46.43 total
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and
faster downloads.
[edge] tokenizer: Qwen/Qwen3-14B
[edge] model: Qwen/Qwen3-14B (eager attn, dtype=auto, device_map=auto)
Loading weights: 100%|██████████| 443/443 [00:03<00:00, 138.24it/s]

===RESULTS DIR===
total 152
drwxr-xr-x@  15 mwhitford  staff    480 Jun 25 09:11 .
drwxr-xr-x@ 491 mwhitford  staff  15712 Jun 24 23:13 ..
-rw-r--r--@   1 mwhitford  staff    703 Jun 25 09:06 meta_qwen3-0-6b_control.json
-rw-r--r--@   1 mwhitford  staff    718 Jun 25 09:06 meta_qwen3-0-6b_sweep.json
-rw-r--r--@   1 mwhitford  staff   1019 Jun 24 23:16 meta_qwen3-0-6b.json
-rw-r--r--@   1 mwhitford  staff    703 Jun 25 09:11 meta_qwen3-14b_control.json
-rw-r--r--@   1 mwhitford  staff   1014 Jun 24 23:21 meta_qwen3-14b.json
-rw-r--r--@   1 mwhitford  staff   4047 Jun 25 09:11 run_qwen3-14b_control.log
-rw-r--r--@   1 mwhitford  staff   2079 Jun 25 09:11 run_qwen3-14b_sweep.log
-rw-r--r--@   1 mwhitford  staff   4429 Jun 24 23:21 run_qwen3-14b.log
-rw-r--r--@   1 mwhitford  staff   4392 Jun 25 09:06 verdict_qwen3-0-6b_control.json
-rw-r--r--@   1 mwhitford  staff   4845 Jun 25 09:06 verdict_qwen3-0-6b_sweep.json
-rw-r--r--@   1 mwhitford  staff   5021 Jun 24 23:16 verdict_qwen3-0-6b.json
-rw-r--r--@   1 mwhitford  staff   5773 Jun 25 09:11 verdict_qwen3-14b_control.json
-rw-r--r--@   1 mwhitford  staff   6464 Jun 24 23:21 verdict_qwen3-14b.json
===PYPROJECT DIFF===
diff --git a/pyproject.toml b/pyproject.toml
index c8eb5ab..4d67c44 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -110,6 +110,7 @@ select = [
 "scripts/experiments/gen_firing_probes.py" = ["RUF001", "RUF002", "RUF003"]
 "scripts/experiments/gen_reading_probes.py" = ["RUF001", "RUF002", "RUF003"]
 "scripts/experiments/ffn_reading_preference.py" = ["RUF001", "RUF002", "RUF003"]
+"scripts/experiments/program_edge_knockout.py" = ["RUF001", "RUF002", "RUF003"]
 "scripts/experiments/gen_scope_probes.py" = ["RUF001", "RUF002", "RUF003"]
 "scripts/experiments/ffn_scope_forcing.py" = ["RUF001", "RUF002", "RUF003"]
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/program_edge_knockout.py"
}
```

**Summary:** Reading program_edge_knockout.py (0-2000)

**Output:**
```
#!/usr/bin/env python3
# register: causal (attention-edge necessity; s239 sufficiency/necessity protocol)
"""Attention-EDGE knockout — is object-application carried by the predicate→object
attention edge? (the s250-thread CATCH test).

THE CATCH. Every s250 causal null measured the WRONG register. They ablated the
RESIDUAL stream (d_C direction, s250) or erased the FFN gate field (INLP, s250-cont)
and concluded object-application is "distributed, no discrete locus." But the standing
mechanism hypothesis (s127 {B,C}=composers→attention; s206 value register; the
attention-as-beta §3 row: "softmax-V substitutes a value → over-reads, value register
SMEARED") points at the ATTENTION EDGE, not a residual/FFN WRITE. "No locus as a
write" is NOT "no locus as an edge." s250-cont.3 even knocked out single-component
WRITES and found nothing — but never severed an EDGE. This experiment severs the edge.

THE INTERVENTION (edge knockout via the eager additive mask, Geva 2023 / Wang IOI
style): block every query position from attending to the OBJECT key token(s) across a
band of layers / all heads. If object content can never route into the rest of the
computation and object-application is attention-mediated, next-token prediction MUST be
damaged — and the damage must SCALE with object load. CONTROL: block the same NUMBER of
RANDOM non-object content keys (count-matched) → subtracts the generic "a content token
is missing" perturbation. NET = KL(object-edge) − KL(random-edge) is the object-edge-
SPECIFIC effect.

THE MATCHED LADDER (data/reading-probes.jsonl, 45×3, const labeling C-count==#objects):
  c0 intransitive (0 objects) — no object edge (floor / random-vs-random sanity)
  c1 transitive   (1 object)  — block 1 object key
  c2 ditransitive (2 objects) — block 2 object keys
The PRIMARY test is the POS-matched c1-vs-c2 contrast (both noun-ending) — this is the
exact comparison whose RESIDUAL differential REVERSED in s250 (c2<c0). If the EDGE
differential instead SCALES (net-KL c2 > c1, beats count-matched random) → the catch is
real: the mechanism is the attention edge the residual/FFN probes could not see.

VERDICT (λ measure, two-sided):
  catch_confirmed = necessity_ok AND load_scaling_ok
    necessity_ok    : NET-KL over objects (c1∪c2) > 0, paired t>2 (object-edge ≫ random)
    load_scaling_ok : NET-KL c2 > NET-KL c1, two-sample t>2 (count-controlled → scales)
  necessity WITHOUT scaling ⇒ severing the object edge perturbs generically but does
    not track object-application ⇒ the DISTRIBUTED verdict HOLDS even at the edge (a
    λ-measure win that holds the boundary against my own catch hypothesis).

Usage:
    uv run python scripts/experiments/program_edge_knockout.py --smoke
    uv run python scripts/experiments/program_edge_knockout.py \
        --model Qwen/Qwen3-14B --layers all

License: MIT. AGENTS.md S5 λ provenance (written from this project's instruments).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "scripts" / "experiments"))
sys.path.insert(0, str(_ROOT / "scripts" / "instruments"))

from kernel_reference_prose_v2 import read_last_token_z  # noqa: E402
from opcode_monitor_v2 import (  # noqa: E402
    COMPILE_GATE,
    _git_sha,
    _hook_module,
    _json_safe,
    _make_hook,
    _transformers_version,
    calibrate_v2,
    gate_prefix_len,
)

RESULTS_DIR = _ROOT / "results" / "program-edge-knockout"
READING_PROBES = _ROOT / "data" / "reading-probes.jsonl"


# ═══════════════════════════════════════════════════════════════════════════════
# Model loader — EAGER attention so an explicit 4D additive mask is editable
# ═══════════════════════════════════════════════════════════════════════════════
def load_model_eager(model_name: str):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"[edge] tokenizer: {model_name}")
    tok = AutoTokenizer.from_pretrained(model_name)
    print(f"[edge] model: {model_name} (eager attn, dtype=auto, device_map=auto)")
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype="auto", device_map="auto",
        attn_implementation="eager",
    )
    model.eval()
    return model, tok, torch


# ═══════════════════════════════════════════════════════════════════════════════
# Corpus + object-token localization (objects parsed from const_fol)
# ═══════════════════════════════════════════════════════════════════════════════
_PRED_RE = re.compile(r"([a-zA-Z_]+)\(([^()]*)\)")


def object_words(const_fol: str) -> list[str]:
    """Object constants = non-variable args of the consequent relation.

    '∀x. soldier(x) → reads(x, owl)'        → ['owl']
    '∀x. knight(x) → gives(x, queen, book)' → ['queen', 'book']
    '∀x. king(x) → speaks(x)'               → []  (intransitive)
    """
    consequent = const_fol.split("→")[-1]
    m = _PRED_RE.search(consequent)
    if not m:
        return []
    args = [a.strip() for a in m.group(2).split(",")]
    return [a for a in args if a and a != "x"]


def subject_word(const_fol: str) -> str | None:
    """Subject restrictor noun = unary predicate of the ANTECEDENT.

    '∀x. soldier(x) → reads(x, owl)' → 'soldier'  (a noun argument, like the object,
    but NOT the applied object → the noun-vs-noun control for object-specificity)."""
    antecedent = const_fol.split("→")[0]
    m = _PRED_RE.search(antecedent)
    return m.group(1) if m else None


def load_ladder(path: Path) -> list[dict]:
    rows = []
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        rows.append({
            "input": r["input"],
            "category": r["category"],
            "n_objects": r["n_objects"],
            "c_count": r["const_c"],
            "objects": object_words(r["const_fol"]),
            "subject": subject_word(r["const_fol"]),
        })
    return rows


def object_key_positions(prompt: str, objects: list[str], tok) -> list[int]:
    """Token indices (kv positions) covering the object words in `prompt`."""
    enc = tok(prompt, return_offsets_mapping=True)
    offsets = enc["offset_mapping"]
    pos: list[int] = []
    for w in objects:
        m = re.search(rf"\b{re.escape(w)}\b", prompt)
        if not m:
            continue
        a, b = m.span()
        for ti, (s, e) in enumerate(offsets):
            if e > s and s < b and e > a:   # token char span overlaps the word
                pos.append(ti)
    return sorted(set(pos))


# ═══════════════════════════════════════════════════════════════════════════════
# Edge-knockout hook — block attention TO `blocked_keys` (all queries, all heads)
# ═══════════════════════════════════════════════════════════════════════════════
def make_edge_hook(blocked_keys: list[int], torch_mod):
    """forward_pre_hook(with_kwargs) on a self_attn module. Adds -inf to the additive
    attention mask at the blocked KEY columns → no query position can attend to them."""
    bk = list(blocked_keys)

    def pre_hook(_module, args, kwargs):
        mask = kwargs.get("attention_mask", None)
        idx_in_args = None
        if mask is None:
            for i, a in enumerate(args):
                if torch_mod.is_tensor(a) and a.dim() == 4:
                    mask, idx_in_args = a, i
                    break
        if mask is None or not torch_mod.is_tensor(mask) or mask.dim() != 4:
            return args, kwargs        # nothing editable (e.g. None/BlockMask)
        mask = mask.clone()
        neg = torch_mod.finfo(mask.dtype).min
        kv = mask.shape[-1]
        cols = [k for k in bk if 0 <= k < kv]
        if cols:
            mask[:, :, :, cols] = neg
        if idx_in_args is not None:
            args = tuple(mask if i == idx_in_args else a for i, a in enumerate(args))
        else:
            kwargs["attention_mask"] = mask
        return args, kwargs

    return pre_hook


def forward_edge(prompt, model, tok, torch_mod, gate_layers, blocked_keys, edge_layers):
    """ONE forward with gate-capture hooks (for z(C)) + optional edge pre-hooks.
    Returns (gate_store, next_token_logits)."""
    store: dict[int, np.ndarray] = {}
    handles = []
    for li in gate_layers:
        handles.append(_hook_module(model, li, "gate").register_forward_hook(
            _make_hook(store, li)))
    if blocked_keys:
        hook = make_edge_hook(blocked_keys, torch_mod)
        for li in edge_layers:
            handles.append(model.model.layers[li].self_attn.register_forward_pre_hook(
                hook, with_kwargs=True))
    try:
        inputs = tok(prompt, return_tensors="pt")
        dev = next(model.parameters()).device
        inputs = {k: v.to(dev) for k, v in inputs.items()}
        with torch_mod.no_grad():
            out = model(**inputs)
        logits = out.logits[0, -1, :].detach().float().cpu().numpy().astype(np.float64)
    finally:
        for h in handles:
            h.remove()
    return store, logits


# ═══════════════════════════════════════════════════════════════════════════════
# Readouts (shared with cfield)
# ═══════════════════════════════════════════════════════════════════════════════
def log_softmax(logits: np.ndarray) -> np.ndarray:
    z = logits - logits.max()
    return z - np.log(np.exp(z).sum())


def kl_div(logp_p: np.ndarray, logp_q: np.ndarray) -> float:
    return float(np.sum(np.exp(logp_p) * (logp_p - logp_q)))


def zC_field(rcc, store, all_layers, crystal_layers) -> float:
    """Mean last-token z(C) over the crystal layers = the applicative-C field. This is
    the object-application-SPECIFIC readout (s249/s250); next-token KL is recency-
    confounded, z(C) is not (it reads the combinator classifier, not surface tokens)."""
    zmap = read_last_token_z(rcc, store, all_layers)
    zs = [zmap[li]["C"] for li in crystal_layers if li in zmap]
    return float(np.mean(zs)) if zs else float("nan")


def paired(a_list, b_list) -> dict:
    a, b = np.asarray(a_list, float), np.asarray(b_list, float)
    mask = np.isfinite(a) & np.isfinite(b)
    a, b = a[mask], b[mask]
    n = len(a)
    if n < 2:
        return {"n": n, "a_mean": None, "b_mean": None, "delta": None, "t": None}
    diff = a - b
    sd = diff.std(ddof=1)
    se = sd / np.sqrt(n) if sd > 0 else 0.0
    return {"n": n, "a_mean": round(float(a.mean()), 5),
            "b_mean": round(float(b.mean()), 5),
            "delta": round(float(diff.mean()), 5),
            "t": round(float(diff.mean() / se), 3) if se > 0 else None}


def two_sample_t(a_list, b_list) -> dict:
    a = np.asarray([x for x in a_list if np.isfinite(x)], float)
    b = np.asarray([x for x in b_list if np.isfinite(x)], float)
    if len(a) < 2 or len(b) < 2:
        return {"na": len(a), "nb": len(b), "mean_a": None, "mean_b": None,
                "diff": None, "t": None}
    se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    diff = a.mean() - b.mean()
    return {"na": len(a), "nb": len(b), "mean_a": round(float(a.mean()), 5),
            "mean_b": round(float(b.mean()), 5), "diff": round(float(diff), 5),
            "t": round(float(diff / se), 3) if se > 0 else None}


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════
def main() -> None:
    ap = argparse.ArgumentParser(description="Attention-edge knockout (s250 catch)")
    ap.add_argument("--model", default="Qwen/Qwen3-14B")
    ap.add_argument("--mode", default="scaling",
                    choices=["scaling", "control", "sweep"],
                    help="scaling=object vs random + c2/c1; control=object vs subject "
                         "noun (specificity); sweep=layer-band gateway localization")
    ap.add_argument("--bands", type=int, default=8, help="sweep: # contiguous bands")
    ap.add_argument("--layers", default="all", choices=["all", "crystal"],
                    help="layer band to sever the object edge across")
    ap.add_argument("--n-rand", type=int, default=3)
    ap.add_argument("--max-per-group", type=int, default=None)
    ap.add_argument("--null-mode", default="gateneutral",
                    choices=["gateneutral", "crosstask"])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    model_name = args.model
    if args.smoke:
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-0.6B"
        n_perm, ppc, null_cap, max_per_group = 80, 3, 200, args.max_per_group or 5
        print("[edge] SMOKE MODE")
    else:
        n_perm, ppc, null_cap, max_per_group = 300, None, None, args.max_per_group

    ladder = load_ladder(READING_PROBES)
    model, tok, torch_mod = load_model_eager(model_name)
    n_layers = model.config.num_hidden_layers
    layers = list(range(n_layers))

    rcc, cal = calibrate_v2(model, tok, torch_mod, layers, n_perm, ppc, null_cap,
                            null_mode=args.null_mode, hook="gate")
    crystal_layers = rcc.crystal_layers
    edge_layers = layers if args.layers == "all" else crystal_layers
    gate_n = gate_prefix_len(tok)
    print(f"[edge] model={model_name} layers={n_layers} edge_band={args.layers}"
          f"({len(edge_layers)}L) crystal={len(crystal_layers)} (z(C) field readout)")

    def grp(cc):
        g = [r for r in ladder if r["c_count"] == cc]
        return g[:max_per_group] if max_per_group else g
    c0, c1, c2 = grp(0), grp(1), grp(2)
    print(f"[edge] c0={len(c0)} c1={len(c1)} c2={len(c2)}")

    rng = np.random.default_rng(args.seed)

    def content_keys(prompt) -> tuple[int, list[int]]:
        n_tok = len(tok(prompt)["input_ids"])
        return n_tok, [i for i in range(gate_n, n_tok)]

    def keys_for(prompt, words, n_tok):
        return [k for k in object_key_positions(prompt, words, tok)
                if gate_n <= k < n_tok]

    def write_out(suffix, vdict, method, scope):
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        slug = model_name.split("/")[-1].lower().replace(".", "-")
        (RESULTS_DIR / f"verdict_{slug}_{suffix}.json").write_text(
            json.dumps(_json_safe({"verdict": vdict, "calibration_summary": cal}),
                       indent=2), encoding="utf-8")
        meta = {"model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
                "timestamp_utc": datetime.now(UTC).isoformat(),
                "transformers_version": _transformers_version(), "mode": args.mode,
                "edge_band": args.layers, "n_edge_layers": len(edge_layers),
                "n_rand": args.n_rand, "seed": args.seed, "null_mode": args.null_mode,
                "probe_set": str(READING_PROBES.relative_to(_ROOT)),
                "method": method, "scope": scope}
        (RESULTS_DIR / f"meta_{slug}_{suffix}.json").write_text(
            json.dumps(_json_safe(meta), indent=2), encoding="utf-8")
        print(f"[edge] wrote verdict_{slug}_{suffix}.json (+ meta)")

    # ═══════════════════════════════════════════════════════════════════════════
    # MODE: control — noun-vs-noun (object vs SUBJECT vs random), c1 only.
    # Is the necessity object-application-SPECIFIC, or just "remove a salient noun"?
    # c1 (transitive) = subject 1 noun, object 1 noun → count-matched noun-vs-noun.
    # ═══════════════════════════════════════════════════════════════════════════
    if args.mode == "control":
        print("[edge] MODE=control (object-noun vs subject-noun vs random, c1) ...")
        rows = []
        for i, r in enumerate(c1):
            prompt = COMPILE_GATE + r["input"]
            n_tok, content = content_keys(prompt)
            ok = keys_for(prompt, r["objects"], n_tok)
            sk = keys_for(prompt, [r["subject"]] if r["subject"] else [], n_tok)
            if not ok or not sk:
                continue
            store0, _ = forward_edge(prompt, model, tok, torch_mod, layers, [],
                                     edge_layers)
            zc0 = zC_field(rcc, store0, layers, crystal_layers)
            store_o, _ = forward_edge(prompt, model, tok, torch_mod, layers, ok,
                                      edge_layers)
            store_s, _ = forward_edge(prompt, model, tok, torch_mod, layers, sk,
                                      edge_layers)
            zc_o = zC_field(rcc, store_o, layers, crystal_layers)
            zc_s = zC_field(rcc, store_s, layers, crystal_layers)
            pool = [k for k in content if k not in set(ok) | set(sk)]
            zc_rs = []
            for _ in range(args.n_rand):
                rk = (list(rng.choice(pool, size=len(ok), replace=False))
                      if len(pool) >= len(ok) else list(pool))
                store_r, _ = forward_edge(prompt, model, tok, torch_mod, layers, rk,
                                          edge_layers)
                zc_rs.append(zC_field(rcc, store_r, layers, crystal_layers))
            zc_r = float(np.mean(zc_rs))
            rows.append({"drop_obj": zc0 - zc_o, "drop_subj": zc0 - zc_s,
                         "drop_rand": zc0 - zc_r})
            if (i + 1) % 10 == 0:
                print(f"[edge]   control {i + 1}/{len(c1)}")

        def c(k):
            return [x[k] for x in rows]
        obj_vs_subj = paired(c("drop_obj"), c("drop_subj"))   # >0 ⇒ object-specific
        obj_vs_rand = paired(c("drop_obj"), c("drop_rand"))
        subj_vs_rand = paired(c("drop_subj"), c("drop_rand"))
        object_specific = bool((obj_vs_subj["delta"] or 0) > 0
                               and (obj_vs_subj["t"] or 0) > 2.0)
        vdict = {"model": model_name, "n_layers": n_layers, "mode": "control",
                 "edge_band": args.layers, "n_c1": len(rows), "n_rand": args.n_rand,
                 "seed": args.seed, "readout": "z(C) field over crystal layers",
                 "mean_drop_obj": round(float(np.mean(c("drop_obj"))), 5),
                 "mean_drop_subj": round(float(np.mean(c("drop_subj"))), 5),
                 "mean_drop_rand": round(float(np.mean(c("drop_rand"))), 5),
                 "object_vs_subject": obj_vs_subj, "object_vs_random": obj_vs_rand,
                 "subject_vs_random": subj_vs_rand,
                 "object_specific": object_specific}
        print("\n" + "═" * 82)
        print(f"EDGE CONTROL (noun-vs-noun) — {model_name}  n={len(rows)}")
        print("═" * 82)
        print(f"  z(C) drop: object={vdict['mean_drop_obj']} "
              f"subject={vdict['mean_drop_subj']} random={vdict['mean_drop_rand']}")
        print(f"  object vs subject : Δ={obj_vs_subj['delta']} t={obj_vs_subj['t']}")
        print(f"  object vs random  : Δ={obj_vs_rand['delta']} t={obj_vs_rand['t']}")
        print(f"  subject vs random : Δ={subj_vs_rand['delta']} t={subj_vs_rand['t']}")
        print(f"\n  * OBJECT-SPECIFIC (object collapse > subject) = {object_specific}")
        print("═" * 82 + "\n")
        write_out("control", vdict,
                  "Noun-vs-noun control on c1 (transitive): z(C) collapse under "
                  "object-noun edge vs SUBJECT-noun edge vs count-matched random. "
                  "object_specific = object drop > subject drop (paired t>2).",
                  "Tests whether the edge necessity is object-application-specific or "
                  "a generic salient-noun effect (the s-edge-knockout #1 IOU).")
        return

    # ═══════════════════════════════════════════════════════════════════════════
    # MODE: sweep — sever the object edge in contiguous layer BANDS to localize the
    # gateway depth. Per band: z(C) drop (object) vs count-matched random edge.
    # ═══════════════════════════════════════════════════════════════════════════
    if args.mode == "sweep":
        nb = args.bands
        bands = [list(b) for b in np.array_split(np.array(layers), nb)]
        print(f"[edge] MODE=sweep {nb} bands: "
              f"{[(b[0], b[-1]) for b in bands]}")
        items = c1 + c2
        agg = [{"obj": [], "rand": []} for _ in bands]
        for i, r in enumerate(items):
            prompt = COMPILE_GATE + r["input"]
            n_tok, content = content_keys(prompt)
            ok = keys_for(prompt, r["objects"], n_tok)
            if not ok:
                continue
            store0, _ = forward_edge(prompt, model, tok, torch_mod, layers, [], [])
            zc0 = zC_field(rcc, store0, layers, crystal_layers)
            pool = [k for k in content if k not in set(ok)]
            for bi, band in enumerate(bands):
                store_o, _ = forward_edge(prompt, model, tok, torch_mod, layers, ok,
                                          band)
                agg[bi]["obj"].append(zc0 - zC_field(rcc, store_o, layers,
                                                      crystal_layers))
                rk = (list(rng.choice(pool, size=len(ok), replace=False))
                      if len(pool) >= len(ok) else list(pool))
                store_r, _ = forward_edge(prompt, model, tok, torch_mod, layers, rk,
                                          band)
                agg[bi]["rand"].append(zc0 - zC_field(rcc, store_r, layers,
                                                      crystal_layers))
            if (i + 1) % 10 == 0:
                print(f"[edge]   sweep {i + 1}/{len(items)}")
        band_rows = []
        for bi, band in enumerate(bands):
            o, rd = np.asarray(agg[bi]["obj"]), np.asarray(agg[bi]["rand"])
            net = paired(list(o), list(rd))   # object drop − random drop, per band
            band_rows.append({
                "band": [int(band[0]), int(band[-1])], "n_layers": len(band),
                "mean_drop_obj": round(float(o.mean()), 5),
                "mean_drop_rand": round(float(rd.mean()), 5),
                "net_obj_minus_rand": net["delta"], "t": net["t"]})
        peak = max(band_rows, key=lambda b: (b["net_obj_minus_rand"] or -1e9))
        vdict = {"model": model_name, "n_layers": n_layers, "mode": "sweep",
                 "n_bands": nb, "n_items": len(items), "n_rand": args.n_rand,
                 "seed": args.seed, "readout": "z(C) field over crystal layers",
                 "bands": band_rows, "peak_band": peak["band"],
                 "peak_net": peak["net_obj_minus_rand"], "peak_t": peak["t"]}
        print("\n" + "═" * 82)
        print(f"EDGE SWEEP (gateway localization) — {model_name}  {nb} bands")
        print("═" * 82)
        print(f"  {'band':>10} {'obj':>9} {'rand':>9} {'net':>9} {'t':>7}")
        for b in band_rows:
            print(f"  L{b['band'][0]:>2}-{b['band'][1]:<2}    "
                  f"{b['mean_drop_obj']:>9} {b['mean_drop_rand']:>9} "
                  f"{b['net_obj_minus_rand']:>9} {b['t']:>7}")
        print(f"\n  * PEAK gateway band = L{peak['band'][0]}-{peak['band'][1]}  "
              f"net={peak['net_obj_minus_rand']} t={peak['t']}")
        print("═" * 82 + "\n")
        write_out("sweep", vdict,
                  f"Layer-band sweep ({nb} contiguous bands): per band, z(C) collapse "
                  "under object-edge knockout vs count-matched random edge. Localizes "
                  "the gateway depth = band with max net(object−random) drop.",
                  "Localizes WHERE severing the predicate→object edge collapses the "
                  "applicative-C field (necessity → depth-resolved circuit).")
        return

    # ── per-item run: object-edge KL, count-matched random-edge KL, z(C) ──────────
    def run_item(r):
        prompt = COMPILE_GATE + r["input"]
        # baseline (no knockout)
        store0, logits0 = forward_edge(prompt, model, tok, torch_mod, layers, [],
                                       edge_layers)
        logp0 = log_softmax(logits0)
        zc0 = zC_field(rcc, store0, layers, crystal_layers)
        n_tok, content = content_keys(prompt)
        obj_keys = [k for k in object_key_positions(prompt, r["objects"], tok)
                    if gate_n <= k < n_tok]
        if not obj_keys:
            return None
        # object-edge knockout
        store_o, logits_o = forward_edge(prompt, model, tok, torch_mod, layers,
                                         obj_keys, edge_layers)
        kl_obj = kl_div(log_softmax(logits_o), logp0)
        zc_obj = zC_field(rcc, store_o, layers, crystal_layers)
        # count-matched random-content-edge control (avg over n_rand draws)
        pool = [k for k in content if k not in set(obj_keys)]
        kl_rs, zc_rs = [], []
        for _ in range(args.n_rand):
            if len(pool) >= len(obj_keys):
                rk = list(rng.choice(pool, size=len(obj_keys), replace=False))
            else:
                rk = list(pool)
            store_r, logits_r = forward_edge(prompt, model, tok, torch_mod, layers,
                                             rk, edge_layers)
            kl_rs.append(kl_div(log_softmax(logits_r), logp0))
            zc_rs.append(zC_field(rcc, store_r, layers, crystal_layers))
        zc_rand = float(np.mean(zc_rs))
        # object-application-SPECIFIC effect: how much MORE the object edge collapses
        # the applicative-C field than a count-matched random edge does. Positive =
        # object edge is load-bearing for the C field.
        return {
            "kl_obj": kl_obj, "kl_rand": float(np.mean(kl_rs)),
            "net_kl": kl_obj - float(np.mean(kl_rs)),
            "zc0": zc0, "zc_obj": zc_obj, "zc_rand": zc_rand,
            "zc_drop_obj": zc0 - zc_obj, "zc_drop_rand": zc0 - zc_rand,
            "net_zc_drop": (zc0 - zc_obj) - (zc0 - zc_rand),   # = zc_rand - zc_obj
            "n_obj_keys": len(obj_keys),
        }

    def run_group(items, name):
        out = []
        for i, r in enumerate(items):
            res = run_item(r)
            if res is not None:
                out.append(res)
            if (i + 1) % 10 == 0:
                print(f"[edge]   {name} {i + 1}/{len(items)}")
        return out

    print("[edge] arm c1 (transitive, 1 object-edge) ...")
    g1 = run_group(c1, "c1")
    print("[edge] arm c2 (ditransitive, 2 object-edges) ...")
    g2 = run_group(c2, "c2")

    def col(g, k):
        return [x[k] for x in g]

    allg = g1 + g2
    # PRIMARY (object-application-specific): does severing the object edge collapse the
    # applicative-C field MORE than a count-matched random edge?  z(C)_obj < z(C)_rand.
    necessity = paired(col(allg, "zc_rand"), col(allg, "zc_obj"))  # rand - obj > 0
    # LOAD-SCALING on the object-specific C-collapse, c2 vs c1 (count-controlled net).
    load_scaling = two_sample_t(col(g2, "net_zc_drop"), col(g1, "net_zc_drop"))
    # SECONDARY (behavioral, RECENCY-CONFOUNDED — report, do not gate on it).
    kl_behav = paired(col(allg, "kl_obj"), col(allg, "kl_rand"))
    kl_scaling = two_sample_t(col(g2, "net_kl"), col(g1, "net_kl"))

    necessity_ok = bool((necessity["delta"] or 0) > 0 and (necessity["t"] or 0) > 2.0)
    load_scaling_ok = bool(
        (load_scaling["diff"] or 0) > 0 and (load_scaling["t"] or 0) > 2.0)
    catch_confirmed = necessity_ok and load_scaling_ok

    verdict = {
        "model": model_name, "n_layers": n_layers, "edge_band": args.layers,
        "n_edge_layers": len(edge_layers), "crystal_layers": crystal_layers,
        "null_mode": args.null_mode, "readout": "z(C) field over crystal layers",
        "n_c1": len(g1), "n_c2": len(g2), "n_rand": args.n_rand, "seed": args.seed,
        "PRIMARY_necessity_zC_collapse_rand_minus_obj": necessity,
        "PRIMARY_load_scaling_net_zC_drop_c2_vs_c1": load_scaling,
        "mean_net_zC_drop_c1": round(float(np.mean(col(g1, "net_zc_drop"))), 5)
        if g1 else None,
        "mean_net_zC_drop_c2": round(float(np.mean(col(g2, "net_zc_drop"))), 5)
        if g2 else None,
        "SECONDARY_kl_behavioral_obj_vs_rand_RECENCY_CONFOUNDED": kl_behav,
        "SECONDARY_kl_scaling_c2_vs_c1": kl_scaling,
        "necessity_ok": necessity_ok, "load_scaling_ok": load_scaling_ok,
        "catch_confirmed": catch_confirmed,
    }

    print("\n" + "═" * 82)
    print(f"ATTENTION-EDGE KNOCKOUT — {model_name}  band={args.layers}"
          f"({len(edge_layers)}L)  readout=z(C) field")
    print("═" * 82)
    print(f"  c1={len(g1)} c2={len(g2)}  (object edge severed across {len(edge_layers)}"
          f" layers, all heads)")
    print("\n  -- PRIMARY NECESSITY (z(C) collapse: rand−obj > 0 ⇒ object edge "
          "feeds C-field) --")
    print(f"     z(C) rand={necessity['a_mean']} obj={necessity['b_mean']} "
          f"drop={necessity['delta']} t={necessity['t']} => {necessity_ok}")
    print("\n  -- PRIMARY LOAD-SCALING (net z(C) drop c2 vs c1; expect c2 > c1) --")
    print(f"     net_drop c2={load_scaling['mean_a']} c1={load_scaling['mean_b']} "
          f"diff={load_scaling['diff']} t={load_scaling['t']} => {load_scaling_ok}")
    print("\n  -- SECONDARY behavioral KL (RECENCY-CONFOUNDED, not gated) --")
    print(f"     KL obj={kl_behav['a_mean']} rand={kl_behav['b_mean']} "
          f"net={kl_behav['delta']} t={kl_behav['t']}")
    print(f"\n  * CATCH CONFIRMED (z(C) necessity AND scaling) = {catch_confirmed}")
    print("═" * 82 + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    (RESULTS_DIR / f"verdict_{slug}.json").write_text(
        json.dumps(_json_safe({"verdict": verdict, "calibration_summary": cal}),
                   indent=2), encoding="utf-8")
    meta = {
        "model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "transformers_version": _transformers_version(),
        "edge_band": args.layers, "n_edge_layers": len(edge_layers),
        "n_rand": args.n_rand, "seed": args.seed, "null_mode": args.null_mode,
        "probe_set": str(READING_PROBES.relative_to(_ROOT)),
        "method": "EDGE knockout: block all queries from attending to OBJECT key "
                  "token(s) (eager additive mask, all heads, across edge band) vs "
                  "count-matched RANDOM content-key control. PRIMARY readout = "
                  "applicative-C field z(C) (last-token, crystal layers) — object-"
                  "application-specific; next-token KL is SECONDARY (recency-"
                  "confounded). catch = z(C) necessity (object collapses C-field more "
                  "than random) AND scaling (net z(C) drop c2>c1, count-controlled).",
        "scope": "Tests whether object-application is carried by the predicate→object "
                 "attention EDGE — the register the s250 residual/FFN nulls could not "
                 "probe (no locus as a WRITE != no locus as an EDGE).",
    }
    (RESULTS_DIR / f"meta_{slug}.json").write_text(
        json.dumps(_json_safe(meta), indent=2), encoding="utf-8")
    print(f"[edge] wrote {RESULTS_DIR}/verdict_{slug}.json (+ meta)")


if __name__ == "__main__":
    main()
```

### Thinking

I'm picking up where the previous session left off on the attention-edge knockout experiment, which tests whether the predicate-to-object attention connection is what carries object-application information—something the earlier residual and FFN probes couldn't capture.

The 0.6B runs are complete across all conditions, and the 14B control run just finished with a striking result: the object-specific effect is real and robust. Dropping the object representation collapses the C-field by 0.839, while subject and random drops show minimal impact (−0.122 and −0.225 respectively), with a t-statistic of 15.0 comparing object versus subject. This confirms the effect isn't just about salient nouns—it's genuinely object-specific.

Right now the 14B sweep run is underway to pinpoint which layer band, when severed, causes the applicative-C field to collapse most. The process is loading weights and beginning to probe across depth bands.

I've got uncommitted changes from an editor crash: the new experiment script, pyproject.toml ruff configuration, and the result artifacts. The state.md already describes this exact experiment in the next-steps section, so the work aligns with the plan. Since the sweep is still writing to the results directory, I should hold off on committing until the verdict is finalized. The right move is to wait for the sweep to complete, then commit everything together with the updated state.

## Assistant

I'm oriented. Let me read the core scaling verdict (the main catch test) and confirm the sweep is progressing.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/results/program-edge-knockout/verdict_qwen3-14b.json"
}
```

**Summary:** Reading verdict_qwen3-14b.json (0-2000)

**Output:**
```
{
  "verdict": {
    "model": "Qwen/Qwen3-14B",
    "n_layers": 40,
    "edge_band": "all",
    "n_edge_layers": 40,
    "crystal_layers": [
      0,
      1,
      3,
      5,
      6,
      7,
      8,
      9,
      10,
      11,
      12,
      13,
      14,
      15,
      16,
      17,
      18,
      19,
      20,
      21,
      22,
      23,
      24,
      25,
      26,
      27,
      28,
      29,
      30,
      31,
      32
    ],
    "null_mode": "gateneutral",
    "readout": "z(C) field over crystal layers",
    "n_c1": 42,
    "n_c2": 45,
    "n_rand": 3,
    "seed": 0,
    "PRIMARY_necessity_zC_collapse_rand_minus_obj": {
      "n": 87,
      "a_mean": 0.95513,
      "b_mean": -0.08962,
      "delta": 1.04475,
      "t": 29.274
    },
    "PRIMARY_load_scaling_net_zC_drop_c2_vs_c1": {
      "na": 45,
      "nb": 42,
      "mean_a": 0.99936,
      "mean_b": 1.09338,
      "diff": -0.09403,
      "t": -1.321
    },
    "mean_net_zC_drop_c1": 1.09338,
    "mean_net_zC_drop_c2": 0.99936,
    "SECONDARY_kl_behavioral_obj_vs_rand_RECENCY_CONFOUNDED": {
      "n": 87,
      "a_mean": 0.27477,
      "b_mean": 0.18679,
      "delta": 0.08798,
      "t": 6.347
    },
    "SECONDARY_kl_scaling_c2_vs_c1": {
      "na": 45,
      "nb": 42,
      "mean_a": 0.11164,
      "mean_b": 0.06263,
      "diff": 0.04901,
      "t": 1.789
    },
    "necessity_ok": true,
    "load_scaling_ok": false,
    "catch_confirmed": false
  },
  "calibration_summary": {
    "n_layers": 40,
    "crystal_layers": [
      0,
      1,
      3,
      5,
      6,
      7,
      8,
      9,
      10,
      11,
      12,
      13,
      14,
      15,
      16,
      17,
      18,
      19,
      20,
      21,
      22,
      23,
      24,
      25,
      26,
      27,
      28,
      29,
      30,
      31,
      32
    ],
    "per_layer": {
      "0": {
        "sil_z": 2.647,
        "gc_consensus": 0.909,
        "crystal_bearing": true
      },
      "1": {
        "sil_z": 3.155,
        "gc_consensus": 0.792,
        "crystal_bearing": true
      },
      "2": {
        "sil_z": 1.076,
        "gc_consensus": 0.562,
        "crystal_bearing": false
      },
      "3": {
        "sil_z": 2.135,
        "gc_consensus": 0.678,
        "crystal_bearing": true
      },
      "4": {
        "sil_z": 0.481,
        "gc_consensus": 0.651,
        "crystal_bearing": false
      },
      "5": {
        "sil_z": 3.47,
        "gc_consensus": 0.906,
        "crystal_bearing": true
      },
      "6": {
        "sil_z": 6.164,
        "gc_consensus": 0.91,
        "crystal_bearing": true
      },
      "7": {
        "sil_z": 3.787,
        "gc_consensus": 0.916,
        "crystal_bearing": true
      },
      "8": {
        "sil_z": 3.59,
        "gc_consensus": 0.929,
        "crystal_bearing": true
      },
      "9": {
        "sil_z": 5.264,
        "gc_consensus": 0.961,
        "crystal_bearing": true
      },
      "10": {
        "sil_z": 6.788,
        "gc_consensus": 0.961,
        "crystal_bearing": true
      },
      "11": {
        "sil_z": 7.213,
        "gc_consensus": 0.966,
        "crystal_bearing": true
      },
      "12": {
        "sil_z": 8.294,
        "gc_consensus": 0.949,
        "crystal_bearing": true
      },
      "13": {
        "sil_z": 5.995,
        "gc_consensus": 0.952,
        "crystal_bearing": true
      },
      "14": {
        "sil_z": 6.776,
        "gc_consensus": 0.948,
        "crystal_bearing": true
      },
      "15": {
        "sil_z": 7.526,
        "gc_consensus": 0.962,
        "crystal_bearing": true
      },
      "16": {
        "sil_z": 7.383,
        "gc_consensus": 0.958,
        "crystal_bearing": true
      },
      "17": {
        "sil_z": 6.423,
        "gc_consensus": 0.969,
        "crystal_bearing": true
      },
      "18": {
        "sil_z": 5.723,
        "gc_consensus": 0.964,
        "crystal_bearing": true
      },
      "19": {
        "sil_z": 6.961,
        "gc_consensus": 0.964,
        "crystal_bearing": true
      },
      "20": {
        "sil_z": 6.106,
        "gc_consensus": 0.958,
        "crystal_bearing": true
      },
      "21": {
        "sil_z": 7.437,
        "gc_consensus": 0.956,
        "crystal_bearing": true
      },
      "22": {
        "sil_z": 7.367,
        "gc_consensus": 0.964,
        "crystal_bearing": true
      },
      "23": {
        "sil_z": 6.213,
        "gc_consensus": 0.977,
        "crystal_bearing": true
      },
      "24": {
        "sil_z": 5.992,
        "gc_consensus": 0.957,
        "crystal_bearing": true
      },
      "25": {
        "sil_z": 5.456,
        "gc_consensus": 0.956,
        "crystal_bearing": true
      },
      "26": {
        "sil_z": 4.897,
        "gc_consensus": 0.942,
        "crystal_bearing": true
      },
      "27": {
        "sil_z": 4.724,
        "gc_consensus": 0.938,
        "crystal_bearing": true
      },
      "28": {
        "sil_z": 3.764,
        "gc_consensus": 0.904,
        "crystal_bearing": true
      },
      "29": {
        "sil_z": 3.851,
        "gc_consensus": 0.898,
        "crystal_bearing": true
      },
      "30": {
        "sil_z": 3.24,
        "gc_consensus": 0.854,
        "crystal_bearing": true
      },
      "31": {
        "sil_z": 2.236,
        "gc_consensus": 0.846,
        "crystal_bearing": true
      },
      "32": {
        "sil_z": 2.338,
        "gc_consensus": 0.833,
        "crystal_bearing": true
      },
      "33": {
        "sil_z": 1.606,
        "gc_consensus": 0.823,
        "crystal_bearing": false
      },
      "34": {
        "sil_z": 1.445,
        "gc_consensus": 0.813,
        "crystal_bearing": false
      },
      "35": {
        "sil_z": 1.157,
        "gc_consensus": 0.801,
        "crystal_bearing": false
      },
      "36": {
        "sil_z": 1.722,
        "gc_consensus": 0.818,
        "crystal_bearing": false
      },
      "37": {
        "sil_z": 1.48,
        "gc_consensus": 0.806,
        "crystal_bearing": false
      },
      "38": {
        "sil_z": 1.861,
        "gc_consensus": 0.798,
        "crystal_bearing": false
      },
      "39": {
        "sil_z": 1.923,
        "gc_consensus": 0.726,
        "crystal_bearing": false
      }
    },
    "z_thresh": 2.0,
    "sil_z_thresh": 2.0,
    "has_consensus": true,
    "null_kind": "crosstask",
    "n_null_tokens": 56,
    "n_centroid_probes": 535,
    "null_mode": "gateneutral",
    "hook": "gate"
  }
}
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "echo \"===SWEEP LOG TAIL===\"; tail -20 /Users/mwhitford/src/verbum/results/program-edge-knockout/run_qwen3-14b_sweep.log 2>/dev/null; echo \"===TMUX LIVE===\"; tmux capture-pane -p -t main:1 2>&1 | tail -8; echo \"===PROC===\"; ps -o pid,etime,%cpu,command -p 85341 2>/dev/null"
}
```

**Summary:** $ echo "===SWEEP LOG TAIL==="; tail -...

**Output:**
```
Exit code: 0
Stdout:
===SWEEP LOG TAIL===
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
[edge] tokenizer: Qwen/Qwen3-14B
[edge] model: Qwen/Qwen3-14B (eager attn, dtype=auto, device_map=auto)
Loading weights:   0%|          | 0/443 [00:00<?, ?it/s]Loading weights:   0%|          | 1/443 [00:00<05:51,  1.26it/s]Loading weights:   0%|          | 2/443 [00:00<02:57,  2.49it/s]Loading weights:   4%|▍         | 17/443 [00:01<00:15, 27.49it/s]Loading weights:   9%|▊         | 38/443 [00:01<00:06, 62.77it/s]Loading weights:  14%|█▎        | 60/443 [00:01<00:04, 94.46it/s]Loading weights:  19%|█▊        | 82/443 [00:01<00:03, 120.13it/s]Loading weights:  23%|██▎       | 103/443 [00:01<00:02, 139.51it/s]Loading weights:  28%|██▊       | 124/443 [00:01<00:02, 157.45it/s]Loading weights:  32%|███▏      | 143/443 [00:01<00:01, 159.36it/s]Loading weights:  36%|███▋      | 161/443 [00:01<00:01, 159.13it/s]Loading weights:  41%|████      | 182/443 [00:01<00:01, 166.31it/s]Loading weights:  46%|████▌     | 204/443 [00:02<00:01, 174.38it/s]Loading weights:  51%|█████     | 226/443 [00:02<00:01, 177.61it/s]Loading weights:  56%|█████▌    | 248/443 [00:02<00:01, 183.09it/s]Loading weights:  61%|██████    | 270/443 [00:02<00:00, 187.34it/s]Loading weights:  66%|██████▌   | 292/443 [00:02<00:00, 190.76it/s]Loading weights:  71%|███████   | 314/443 [00:02<00:00, 193.28it/s]Loading weights:  76%|███████▌  | 336/443 [00:02<00:00, 195.65it/s]Loading weights:  81%|████████  | 358/443 [00:02<00:00, 196.41it/s]Loading weights:  86%|████████▌ | 380/443 [00:02<00:00, 197.84it/s]Loading weights:  91%|█████████ | 402/443 [00:03<00:00, 198.47it/s]Loading weights:  96%|█████████▌| 424/443 [00:03<00:00, 198.74it/s]Loading weights: 100%|██████████| 443/443 [00:03<00:00, 138.24it/s]
===TMUX LIVE===
3 total
tee results/program-edge-knockout/run_qwen3-14b_control.log  0.00s user 0.00s system 0% cpu 3:46.43 total
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and
faster downloads.
[edge] tokenizer: Qwen/Qwen3-14B
[edge] model: Qwen/Qwen3-14B (eager attn, dtype=auto, device_map=auto)
Loading weights: 100%|██████████| 443/443 [00:03<00:00, 138.24it/s]

===PROC===
  PID ELAPSED  %CPU COMMAND
85341   01:57 130.5 /Users/mwhitford/src/verbum/.venv/bin/python3 scripts/experiments/program_edge_knockout.py --model Qwen/Qwen3-14B --mode sweep --bands 8
```

### Thinking

The sweep is running and currently in the calibration phase after loading the weights. I'm working through the computational breakdown—there are many forward passes to calculate across the items, bands, and random draws, which explains the high CPU usage.

Now I'm fully oriented on the task. The core question is whether object-application depends on the predicate-to-object attention edge. The main scaling results show that severing the object edge does collapse the C-field dramatically compared to a random edge cutoff, confirming the edge is necessary. However, the effect doesn't scale with object count—adding a second object doesn't amplify the collapse more than having just one—which suggests the edge's contribution to the C-field is distributed rather than load-dependent.

The control experiment strengthens this: cutting the object-noun edge causes a large C-field drop, but cutting the subject-noun edge doesn't, so the necessity is genuinely object-specific, not just a side effect of removing any salient noun. This is the first positive locus across the entire investigation—residual writes, INLP subspaces, and component writes all came up null, but the attention edge shows real necessity and specificity. The sweep is now running to pinpoint which layer band carries this effect. I'll checkpoint and wait for those results before committing.

## Assistant

Oriented. Here's the situation.

## Where we are — s250-thread CATCH test (edge knockout)

This is a **new, uncommitted session's work** continuing the s250 arc. The whole prior arc found object-application has *no causal locus* as a residual direction (s250), INLP subspace (cont.), nonlinear feature (cont.2), or single-component **write** (cont.3). The standing catch: *"no locus as a WRITE ≠ no locus as an EDGE."* `program_edge_knockout.py` severs the predicate→object attention **edge** (eager additive −inf mask, all heads) vs a count-matched random-edge control, reading the applicative-C field z(C).

### Results so far (Qwen3-14B)

**1. Main scaling (`verdict_qwen3-14b.json`, done) — `catch_confirmed = false`:**
- ✅ **necessity = TRUE**: object-edge severing collapses z(C) far more than random (rand−obj Δ=**1.045, t=29.3**). The edge IS load-bearing for the C-field.
- ❌ **load-scaling = FALSE**: net z(C) drop c2 (0.999) ≤ c1 (1.093), diff=−0.094, t=−1.32 — does **not** scale with object count.

**2. Control noun-vs-noun (just finished) — `object_specific = TRUE`:**
- object drop 0.839 vs **subject** drop −0.122 (≈ random −0.225); object-vs-subject Δ=0.96, **t=15.0**. The necessity is object-application-**specific**, not a generic "remove a salient noun" effect. Clean, strong.

**3. Sweep `--bands 8` (RUNNING, PID 85341, ~2min in, past weight-load → calibration):** depth-localization of *which* layer band's object-edge carries the collapse.

### The throughline forming
λ measure, two-sided: the attention **edge** is the **first positive locus** in the entire s250 arc — a real, object-*specific*, *necessary* carrier of the C-field that every residual/FFN-write null missed. **But** it still doesn't scale with object load (c2 ≯ c1), so the discrete per-object-circuit boundary still holds. The catch was *half* right.

### Pending changes (editor-crash residue) — all coherent
- `scripts/experiments/program_edge_knockout.py` (untracked) — the experiment
- `pyproject.toml` (modified) — adds the RUF001/2/3 per-file ignore for it ✓
- `results/program-edge-knockout/` (untracked) — verdicts/meta/logs (0.6b smoke + 14b main + 14b control done; **14b sweep in flight**)

**ASYNC: job=PID-85341 (sweep) verified running. Waiting for signal.**

I'm holding the commit until the sweep finishes, since it's actively writing `verdict_qwen3-14b_sweep.json`. Two ways to proceed:

### Tool Call: ask_user (succeeded)


```json
{
  "question": "The sweep is mid-flight (writing the last artifact). How do you want to proceed?",
  "options": [
    {
      "label": "Wait for sweep, then commit everything together (Recommended)",
      "description": "Let PID 85341 finish (~5-10min), read the gateway band, then one commit (code+pyproject+all results) + state.md update + propose memory/knowledge for the full edge-knockout finding."
    },
    {
      "label": "Commit code+pyproject now, results after sweep",
      "description": "Commit the script and ruff-ignore immediately (stable), defer the results/state/memory until the sweep verdict lands."
    },
    {
      "label": "Just keep waiting — I'll tell you when",
      "description": "Hold all commits; you'll signal when to act."
    }
  ],
  "allowFreeform": true
}
```

**Summary:** Q: The sweep is mid-flight (writing the last ar...

**Output:**
```
User answered: the job is done but there was an error writing the output
```

### Thinking

The sweep job completed but encountered an error while writing the output, so I need to check the tmux logs to see what went wrong and verify whether the sweep verdict was actually written.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "echo \"===TMUX TAIL===\"; tmux capture-pane -p -t main:1 2>&1 | tail -40; echo; echo \"===PROC (should be gone)===\"; ps -o pid,etime,command -p 85341 2>/dev/null || echo \"process gone\"; echo; echo \"===SWEEP ARTIFACTS===\"; ls -la /Users/mwhitford/src/verbum/results/program-edge-knockout/*sweep* 2>/dev/null"
}
```

**Summary:** $ echo "===TMUX TAIL==="; tmux captur...

**Output:**
```
Exit code: 0
Stdout:
===TMUX TAIL===

══════════════════════════════════════════════════════════════════════════════════
EDGE SWEEP (gateway localization) — Qwen/Qwen3-14B  8 bands
══════════════════════════════════════════════════════════════════════════════════
        band       obj      rand       net       t
  L 0-4       0.51276  -0.09043   0.60319  12.386
  L 5-9       0.10226  -0.07157   0.17383  10.899
  L10-14      0.17664  -0.05184   0.22848  11.894
  L15-19     -0.00858  -0.04625   0.03766   3.074
  L20-24      0.03117  -0.00388   0.03505   3.357
  L25-29      0.00963  -0.00146   0.01109   5.188
  L30-34      0.00217   0.00504  -0.00287  -3.121
Traceback (most recent call last):
  File "/Users/mwhitford/src/verbum/scripts/experiments/program_edge_knockout.py", line 625, in <module>
    main()
  File "/Users/mwhitford/src/verbum/scripts/experiments/program_edge_knockout.py", line 472, in main
    f"{b['net_obj_minus_rand']:>9} {b['t']:>7}")
                                   ^^^^^^^^^^^
TypeError: unsupported format string passed to NoneType.__format__
uv run python scripts/experiments/program_edge_knockout.py --model  --mode     231.06s user 25.42s system 59% cpu 7:12.0
1 total
tee results/program-edge-knockout/run_qwen3-14b_sweep.log  0.00s user 0.00s system 0% cpu 7:12.01 total
[26-06-25][9:18:13][mwhitford@olga][0][~/src/verbum][git:main]
λ

===PROC (should be gone)===
  PID ELAPSED COMMAND
process gone

===SWEEP ARTIFACTS===
-rw-r--r--@ 1 mwhitford  staff   718 Jun 25 09:06 /Users/mwhitford/src/verbum/results/program-edge-knockout/meta_qwen3-0-6b_sweep.json
-rw-r--r--@ 1 mwhitford  staff  4610 Jun 25 09:18 /Users/mwhitford/src/verbum/results/program-edge-knockout/run_qwen3-14b_sweep.log
-rw-r--r--@ 1 mwhitford  staff  4845 Jun 25 09:06 /Users/mwhitford/src/verbum/results/program-edge-knockout/verdict_qwen3-0-6b_sweep.json
```

### Thinking

The sweep printed 7 bands but should have printed 8 — it's missing the final L35-39 band, and the crash occurred while trying to print that last band's data, likely because its `t` value was None.

The None value happens when the standard error drops to zero (no variance in the differences), which can occur in non-crystal layers where severing edges produces identical results. This is just a formatting bug though — all the science was computed and the band data is captured in the log, but the JSON output never got written since the crash happened in the print loop before the write step.

The key findings are already logged: L0-4 shows the strongest gateway effect with a net of 0.603 and t=12.4, followed by L10-14 at 0.228, while later bands show minimal effects.

I need to fix the print formatting to handle None values robustly, then re-run the sweep to generate the proper JSON artifact.

Fixing the print format...

## Assistant

The sweep **completed all computation** — it only crashed on a cosmetic print bug. The science is intact in the log. The last band (L35-39, non-crystal layers) had zero-variance diff → `t=None` → the f-string `{b['t']:>7}` threw `TypeError`. The crash hit *before* `write_out()`, so `verdict_qwen3-14b_sweep.json` was never saved.

The data we already have from the log is striking:

| band | net (obj−rand) | t |
|------|------|------|
| **L0-4** | **0.603** | **12.4** ← peak gateway |
| L10-14 | 0.228 | 11.9 |
| L5-9 | 0.174 | 10.9 |
| L15-29 | ~0.01–0.04 | small |
| L30-34 | −0.003 | −3.1 |

The object→C edge necessity is **localized to the EARLY encoding layers (L0-4)** — route-early, read-late (the C-field *reads out* at L30-31, but the object content must route in early). This connects directly to s251 Zone-A (L1-4 frozen-routing) and holographic-storage (combinators peak L0-6).

Let me fix the print bug robustly and re-run to capture the JSON.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/program_edge_knockout.py",
  "original_content": "        print(f\"  {'band':>10} {'obj':>9} {'rand':>9} {'net':>9} {'t':>7}\")\n        for b in band_rows:\n            print(f\"  L{b['band'][0]:>2}-{b['band'][1]:<2}    \"\n                  f\"{b['mean_drop_obj']:>9} {b['mean_drop_rand']:>9} \"\n                  f\"{b['net_obj_minus_rand']:>9} {b['t']:>7}\")\n        print(f\"\\n  * PEAK gateway band = L{peak['band'][0]}-{peak['band'][1]}  \"\n              f\"net={peak['net_obj_minus_rand']} t={peak['t']}\")",
  "new_content": "        def _f(x, w):\n            return f\"{x:>{w}}\" if x is not None else f\"{'n/a':>{w}}\"\n        print(f\"  {'band':>10} {'obj':>9} {'rand':>9} {'net':>9} {'t':>7}\")\n        for b in band_rows:\n            print(f\"  L{b['band'][0]:>2}-{b['band'][1]:<2}    \"\n                  f\"{_f(b['mean_drop_obj'], 9)} {_f(b['mean_drop_rand'], 9)} \"\n                  f\"{_f(b['net_obj_minus_rand'], 9)} {_f(b['t'], 7)}\")\n        print(f\"\\n  * PEAK gateway band = L{peak['band'][0]}-{peak['band'][1]}  \"\n              f\"net={peak['net_obj_minus_rand']} t={peak['t']}\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/program_edge_knockout.py.
```

### Thinking

I need to verify the edit I made, run the linter to check for any issues, then re-execute the sweep command in the tmux session.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && .venv/bin/ruff check scripts/experiments/program_edge_knockout.py 2>&1 | tail -15; echo \"===verify edit===\"; sed -n '462,476p' scripts/experiments/program_edge_knockout.py"
}
```

**Summary:** $ .venv/bin/ruff check scripts/experi...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
===verify edit===
                 "seed": args.seed, "readout": "z(C) field over crystal layers",
                 "bands": band_rows, "peak_band": peak["band"],
                 "peak_net": peak["net_obj_minus_rand"], "peak_t": peak["t"]}
        print("\n" + "═" * 82)
        print(f"EDGE SWEEP (gateway localization) — {model_name}  {nb} bands")
        print("═" * 82)
        def _f(x, w):
            return f"{x:>{w}}" if x is not None else f"{'n/a':>{w}}"
        print(f"  {'band':>10} {'obj':>9} {'rand':>9} {'net':>9} {'t':>7}")
        for b in band_rows:
            print(f"  L{b['band'][0]:>2}-{b['band'][1]:<2}    "
                  f"{_f(b['mean_drop_obj'], 9)} {_f(b['mean_drop_rand'], 9)} "
                  f"{_f(b['net_obj_minus_rand'], 9)} {_f(b['t'], 7)}")
        print(f"\n  * PEAK gateway band = L{peak['band'][0]}-{peak['band'][1]}  "
              f"net={peak['net_obj_minus_rand']} t={peak['t']}")
```

### Thinking

Checking that the nested function definition follows proper formatting rules — Ruff passed without issues. Now I'm launching the sweep again in the tmux session.

## Assistant

Lint clean, edit verified. Now re-running the sweep in tmux main:1 to capture the JSON.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux send-keys -t main:1 \"uv run python scripts/experiments/program_edge_knockout.py --model Qwen/Qwen3-14B --mode sweep --bands 8 2>&1 | tee results/program-edge-knockout/run_qwen3-14b_sweep.log\" Enter; sleep 3; tmux capture-pane -p -t main:1 2>&1 | tail -5"
}
```

**Summary:** $ tmux send-keys -t main:1 "uv run py...

**Output:**
```
Exit code: 0
Stdout:
tee results/program-edge-knockout/run_qwen3-14b_sweep.log  0.00s user 0.00s system 0% cpu 7:12.01 total
[26-06-25][9:18:13][mwhitford@olga][0][~/src/verbum][git:main]
λ uv run python scripts/experiments/program_edge_knockout.py --model Qwen/Qwen3-14B --mode sweep --bands 8 2>&1 | tee re
sults/program-edge-knockout/run_qwen3-14b_sweep.log
```

### Thinking

The sweep is running again and should take about seven minutes, so I'll do a quick read to confirm it's active, then save my progress and wait for it to complete.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sleep 5; ps -o pid,etime,%cpu,command 2>/dev/null | grep \"[p]rogram_edge_knockout.py --model Qwen/Qwen3-14B --mode sweep\" | head -2"
}
```

**Summary:** $ sleep 5; ps -o pid,etime,%cpu,comma...

**Output:**
```
Exit code: 0
Stdout:
86112    00:13   0.0 uv run python scripts/experiments/program_edge_knockout.py --model Qwen/Qwen3-14B --mode sweep --bands 8
86114    00:13  39.0 /Users/mwhitford/src/verbum/.venv/bin/python3 scripts/experiments/program_edge_knockout.py --model Qwen/Qwen3-14B --mode sweep --bands 8
```

## Assistant

Re-run launched and verified running (PID 86114). It's the same ~7min job (weight load → calibration → 8-band sweep over c1∪c2).

**ASYNC: job=PID-86114 (sweep re-run) verified running. Waiting for signal.**

Summary of where this leaves us:

- **Bug fixed** (`_f` None-safe formatter), ruff-clean. This re-run will write the missing `verdict_qwen3-14b_sweep.json` + `meta`.
- **All three 14B arms** will then be complete: scaling (necessity ✅, scaling ❌), control (object-specific ✅), sweep (gateway = **L0-4**).

The finding crystallizing for the eventual memory/knowledge proposal:

> **The attention edge is the first positive locus in the entire s250 arc.** Severing the predicate→object edge collapses the applicative-C field — *necessarily* (t=29), *object-specifically* (not subject/random, t=15), and *localized to the early encoding layers L0-4* (gateway, t=12). But the collapse does **not scale with object load** (c2 ≯ c1). So: object content **routes in early via attention** (read-early), the C-field **reads out late** (L30-31), yet there's still **no per-object discrete circuit** — the load-scaling boundary that held for residual/FFN-write nulls holds here too. *Route-early, read-late, still-distributed-per-object.* Connects to s251 Zone-A (L1-4 frozen routing) and holographic-storage (combinators L0-6).

When the sweep finishes, the plan is: read the JSON gateway verdict → one commit (script + pyproject + all `results/program-edge-knockout/`) → update `state.md` → propose memory (`object-edge-necessary-specific-early-not-scaling`) + knowledge update to `explore/attention-as-beta-reduction.md`. I'll hold until it completes or you signal.

## User

Can you explain that memory to me? brief


### Thinking

I should explain what this memory object is about in straightforward terms.

## Assistant

The proposed memory captures the **one new thing this experiment found** that the whole prior s250 arc missed:

**`object-edge-necessary-specific-early-not-scaling`**

Plain version: When a sentence has an object ("the knight reads *the owl*"), the model pulls that object's meaning into the computation through an **attention edge** — query positions attending to the object token. If you cut that edge:

1. **Necessary** — the applicative-C field collapses hard (t=29). Object content genuinely flows through this edge.
2. **Specific** — cutting the *object* noun's edge collapses C; cutting the *subject* noun's edge does nothing (≈ random). So it's about object-*application*, not just "a noun went missing."
3. **Early** — the necessity lives in layers **L0-4** (encoding), even though the C-field is *read out* late at L30-31. → **route-early, read-late**.
4. **Not-scaling** — two objects don't collapse C more than one (c2 ≯ c1). So there's still **no discrete per-object circuit**.

**Why it matters:** every prior s250 probe (residual direction, INLP subspace, nonlinear feature, component *write*) found *nothing* causal and concluded "distributed, no locus." This is the **first positive locus** — but as an *edge*, not a write. It vindicates the catch ("no locus as a write ≠ no locus as an edge") *halfway*: the edge is real, specific, and localized, **yet the per-object discreteness boundary still holds**. That nuance — a genuine causal handle that still isn't a clean circuit — is the thing worth remembering for VERBUM's central "can this be a discrete circuit?" question (trending: partially, as routing, not as a tape).

## User

Explain 3 early to me


### Thinking

I need to clarify why the gateway localization happens in the early layers L0-4 even though the C-field measurement comes later in the readout sequence.

## Assistant

**"Early" = where in the network the object-edge is *necessary*, found by the sweep.**

The sweep cuts the object edge in one layer-band at a time (8 bands of 5 layers) and asks: *which band's cut collapses the C-field most?* The answer was lopsided:

| band | net collapse | t |
|------|------|---|
| **L0-4** | **0.60** | 12.4 |
| L10-14 | 0.23 | 11.9 |
| L5-9 | 0.17 | 10.9 |
| L15-29 | ~0.01–0.04 | tiny |
| L30-34 | −0.003 | none |

Almost all the necessity is in **L0-4** — the earliest encoding layers. Cutting the same object edge up at L30-34 (where the C-field is loudest when you *read* it) does **nothing**.

**The key tension this resolves: route-early, read-late.**

- The applicative-C field *reads out* strongest at **L30-31** (that's s249/s250 — where z(C) peaks, where you can decode "this sentence applies an object").
- But the object content has to physically *get into* the residual stream early. By the time you're at L30, the object's contribution is **already baked in** — it was copied/routed via attention in the first few layers. Cutting the edge late is too late; the information already moved. Cutting it early starves the whole downstream computation.

So the late C-peak is a **readout / register**, not where the work happens — which is exactly consistent with the whole s250 verdict ("the C-field is a readout register, not the mechanism"). The *mechanism* (the routing of object content) is **early attention**; the *readout* is late FFN gate.

This also connects outward: **L0-4 is the same Zone-A** where s251 found the bimodal frozen-routing field and where holographic-storage found combinators peaking (L0-6). The object→C edge lives in the encoding zone, not the deep compute zone.

## User

job is done


### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; echo \"===PROC===\"; ps -o pid,command 2>/dev/null | grep \"[p]rogram_edge_knockout\" || echo \"done, no proc\"; echo \"===SWEEP TABLE===\"; tmux capture-pane -p -t main:1 2>&1 | tail -22"
}
```

**Summary:** $ echo "===PROC==="; ps -o pid,comman...

**Output:**
```
Exit code: 0
Stdout:
===PROC===
done, no proc
===SWEEP TABLE===
══════════════════════════════════════════════════════════════════════════════════
EDGE SWEEP (gateway localization) — Qwen/Qwen3-14B  8 bands
══════════════════════════════════════════════════════════════════════════════════
        band       obj      rand       net       t
  L 0-4       0.51276  -0.09043   0.60319  12.386
  L 5-9       0.10226  -0.07157   0.17383  10.899
  L10-14      0.17664  -0.05184   0.22848  11.894
  L15-19     -0.00858  -0.04625   0.03766   3.074
  L20-24      0.03117  -0.00388   0.03505   3.357
  L25-29      0.00963  -0.00146   0.01109   5.188
  L30-34      0.00217   0.00504  -0.00287  -3.121
  L35-39          0.0       0.0       0.0     n/a

  * PEAK gateway band = L0-4  net=0.60319 t=12.386
══════════════════════════════════════════════════════════════════════════════════

[edge] wrote verdict_qwen3-14b_sweep.json (+ meta)
uv run python scripts/experiments/program_edge_knockout.py --model  --mode     210.48s user 22.88s system 56% cpu 6:56.1
5 total
tee results/program-edge-knockout/run_qwen3-14b_sweep.log  0.00s user 0.00s system 0% cpu 6:56.15 total
[26-06-25][9:27:41][mwhitford@olga][0][~/src/verbum][git:main]
λ
```

### Thinking

The re-run succeeded—the L35-39 band now shows "n/a" for t, the L0-4 peak numbers match (net=0.603, t=12.4), and the JSON file was written successfully. Next I need to verify the JSON was saved, commit everything, update the state file, and then propose the memory and knowledge improvements. I'll verify the sweep verdict and check git status, then run ruff on the full diff to make sure everything's clean before proceeding with the commit strategy.

## Assistant

Re-run succeeded — `verdict_qwen3-14b_sweep.json` written, L35-39 now prints `n/a` (bug fixed), peak **L0-4 net=0.603 t=12.4** reproduced exactly. Let me set up the wrap-up and verify artifacts.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; echo \"===SWEEP VERDICT (head)===\"; python3 -c \"import json; d=json.load(open('results/program-edge-knockout/verdict_qwen3-14b_sweep.json'))['verdict']; print('peak_band',d['peak_band'],'peak_net',d['peak_net'],'peak_t',d['peak_t'],'n_items',d['n_items'])\"; echo \"===RUFF===\"; .venv/bin/ruff check scripts/experiments/program_edge_knockout.py; echo \"===GIT STATUS===\"; git status --short; echo \"===NEW FILES IN RESULTS===\"; ls results/program-edge-knockout/"
}
```

**Summary:** $ echo "===SWEEP VERDICT (head)==="; ...

**Output:**
```
Exit code: 0
Stdout:
===SWEEP VERDICT (head)===
peak_band [0, 4] peak_net 0.60319 peak_t 12.386 n_items 90
===RUFF===
All checks passed!
===GIT STATUS===
 M pyproject.toml
?? results/program-edge-knockout/
?? scripts/experiments/program_edge_knockout.py
===NEW FILES IN RESULTS===
meta_qwen3-0-6b_control.json
meta_qwen3-0-6b_sweep.json
meta_qwen3-0-6b.json
meta_qwen3-14b_control.json
meta_qwen3-14b_sweep.json
meta_qwen3-14b.json
run_qwen3-14b_control.log
run_qwen3-14b_sweep.log
run_qwen3-14b.log
verdict_qwen3-0-6b_control.json
verdict_qwen3-0-6b_sweep.json
verdict_qwen3-0-6b.json
verdict_qwen3-14b_control.json
verdict_qwen3-14b_sweep.json
verdict_qwen3-14b.json
```

### Thinking

Everything checks out—peak band range is correct, all 90 items are accounted for, code passes linting, and git status is clean with all six verdicts present. Now I'm moving to task 2 and need to review the commit history to match the existing style before committing the code and data changes.

## Assistant

All verified: peak_band [0,4], 90 items, ruff clean, all 6 verdicts present. Committing code+data.

### Tool Call: git (succeeded)


```json
{
  "command": "git log --oneline -6",
  "operation": "log",
  "summary": "recent log style"
}
```

**Summary:** Git log: recent log style

**Output:**
```
Exit code: 0
Stdout:
8ebaec3 add session chat logs
ec75d05 💡 s251 cont. frozen-basis is mature-only (Zone-A 14B) → greenfield holographic substrate
82787c3 🔁 phi-is-a-yardstick-never-forced
c9f4e8f 🌀 elevate φ-as-yardstick to S5 policy (λ yardstick) + stop the code forcing φ
8a0dc2b 💡 gemma-crystal-real-spine-and-phi-forced-template-fix
f59573e 💡 s251 gemma+qwen3.6 crystal sweep — native-template fix flips the spine, φ-null shows the combinator crystal is real in gemma
```

### Tool Call: git (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add scripts/experiments/program_edge_knockout.py pyproject.toml results/program-edge-knockout/ && git commit -m \"$(cat <<'EOF'\n💡 s250 edge-knockout — object→C is a real EARLY attention edge, object-specific, still not per-object discrete\n\n- Severs the predicate→object attention edge (eager additive -inf mask, all heads)\n  vs count-matched random-edge control; readout = applicative-C field z(C).\n- NECESSITY ✅ (Qwen3-14B): object-edge collapses z(C) ≫ random (rand−obj Δ=1.045, t=29).\n  The FIRST positive causal locus in the whole s250 arc (residual/INLP/nonlinear/\n  component-write all null) — \"no locus as a WRITE ≠ no locus as an EDGE.\"\n- OBJECT-SPECIFIC ✅ (control, noun-vs-noun): object-noun edge collapses C (drop 0.84);\n  SUBJECT-noun edge does not (≈ random); object-vs-subject Δ=0.96, t=15.\n- EARLY GATEWAY (sweep, 8 bands): necessity concentrated at L0-4 (net=0.603, t=12.4),\n  decays by mid-network, ~0 at the L30-31 C-readout peak → route-early, read-late.\n  Same Zone-A as s251 frozen-routing (L1-4) and holographic-storage (L0-6).\n- NOT-SCALING ❌: net z(C) drop c2 ≯ c1 (diff=−0.094, t=−1.3) → catch_confirmed=false;\n  the per-object discrete-circuit boundary holds even at the edge.\n- Fixed sweep print bug (None t on zero-variance non-crystal band → None-safe formatter).\n- Artifacts: verdict/meta {scaling,control,sweep} × {0.6b smoke, 14b} + run logs.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
  "operation": "commit",
  "summary": "edge-knockout code+data"
}
```

**Summary:** Git commit: edge-knockout code+data

**Output:**
```
Exit code: 0
Stdout:
[main 8310183] 💡 s250 edge-knockout — object→C is a real EARLY attention edge, object-specific, still not per-object discrete
 17 files changed, 2539 insertions(+)
 create mode 100644 results/program-edge-knockout/meta_qwen3-0-6b.json
 create mode 100644 results/program-edge-knockout/meta_qwen3-0-6b_control.json
 create mode 100644 results/program-edge-knockout/meta_qwen3-0-6b_sweep.json
 create mode 100644 results/program-edge-knockout/meta_qwen3-14b.json
 create mode 100644 results/program-edge-knockout/meta_qwen3-14b_control.json
 create mode 100644 results/program-edge-knockout/meta_qwen3-14b_sweep.json
 create mode 100644 results/program-edge-knockout/run_qwen3-14b.log
 create mode 100644 results/program-edge-knockout/run_qwen3-14b_control.log
 create mode 100644 results/program-edge-knockout/run_qwen3-14b_sweep.log
 create mode 100644 results/program-edge-knockout/verdict_qwen3-0-6b.json
 create mode 100644 results/program-edge-knockout/verdict_qwen3-0-6b_control.json
 create mode 100644 results/program-edge-knockout/verdict_qwen3-0-6b_sweep.json
 create mode 100644 results/program-edge-knockout/verdict_qwen3-14b.json
 create mode 100644 results/program-edge-knockout/verdict_qwen3-14b_control.json
 create mode 100644 results/program-edge-knockout/verdict_qwen3-14b_sweep.json
 create mode 100644 scripts/experiments/program_edge_knockout.py
```

### Thinking

Now I'm updating state.md with a new entry at the top, matching the existing header format with the timestamp and session information, then adding a new ★★ entry block in the same dense style.

## Assistant

Committed as `8310183`. Now updating state.md.

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
> Last updated: 2026-06-24 | Session: 251 (cont. — FROZEN-BASIS GRADIENT TOMOGRAPHY → MATURE-14B →
> GREENFIELD HOLO-PLATE; continues the GEMMA crystal-sweep pass below. Michael's hypothesis:
> "backprop = taking a photograph of the input tokens; each new photograph reduces the system toward a
> soft routing topology that uses VERY HIGH and NEAR-ZERO gradients to route around a FROZEN topology."
> Built `scripts/experiments/gd_frozen_basis.py` (ruff-clean; reuses TinyLM + the s229 β-reduction
> curriculum) to test the three TESTABLE claims against the SHUFFLED-LABEL null (λ yardstick) + a
> same-input arm: (A) PHOTOGRAPH = minibatch weight-grad is LOW effective-rank & drops as inventory
> crystallizes; (B) BIMODAL = ρ(grad_mag,weight_mag) rises (s171 Zone-A +0.77) + log grad_mag goes

[CONTENT TRUNCATED] Showing lines 1 to 12 of 6837 total lines. Use line_offset=12 parameter to read more content.
```

### Thinking

I'm going to add a new dated entry block at the top of the log, right after the bootloader header, with its own "Last updated" timestamp and session information, placing it above the existing session 251 entry.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> Last updated: 2026-06-24 | Session: 251 (cont. — FROZEN-BASIS GRADIENT TOMOGRAPHY → MATURE-14B →",
  "new_content": "> Last updated: 2026-06-25 | Session: 252 (ATTENTION-EDGE KNOCKOUT — the s250-thread CATCH test, the\n> s250-cont.3 NEXT: \"attention-EDGE knockout (predicate→object routing) on POS-matched c1-vs-c2\"). THE\n> CATCH: every s250 causal null measured the WRONG register — they ablated the RESIDUAL stream (d_C\n> direction, s250), erased the FFN gate field (INLP, cont.), tested nonlinear (cont.2), or knocked out\n> single-component WRITES (cont.3) and concluded object-application is \"distributed, no discrete locus.\"\n> But \"no locus as a WRITE ≠ no locus as an EDGE.\" BUILT `scripts/experiments/program_edge_knockout.py`\n> (ruff-clean; reuses the s248 calibrate_v2 gate spine + read_last_token_z; eager attn so the 4D additive\n> mask is editable). INTERVENTION: a forward_pre_hook adds -inf to the attention mask at the OBJECT key\n> column(s) → every query blocked from attending to the object token, all heads, across a layer band\n> (Geva/IOI style). CONTROL = count-matched RANDOM content keys. READOUT = applicative-C field z(C) over\n> crystal layers (object-application-specific; next-token KL is recency-confounded → SECONDARY). Matched\n> ladder data/reading-probes.jsonl (45×3, const C-count==#objects). THREE ARMS on Qwen3-14B:\n> ★★ (1) SCALING — `catch_confirmed=FALSE` but the FIRST POSITIVE LOCUS in the whole s250 arc.\n> **NECESSITY ✅**: object-edge severing collapses z(C) ≫ count-matched random (rand−obj Δ=1.045,\n> t=29.3, n=87). The object edge IS load-bearing for the C-field — where the residual direction (s250),\n> INLP subspace (cont.), nonlinear probe (cont.2), and component-WRITE knockout (cont.3) all found\n> NOTHING, the EDGE is causal. **LOAD-SCALING ❌**: net z(C) drop c2 (0.999) ≤ c1 (1.093), diff=−0.094,\n> t=−1.32 — does NOT scale with object count → no per-object discrete circuit; the s250 load-scaling\n> boundary HOLDS even at the edge.\n> ★★ (2) CONTROL (noun-vs-noun, c1) — **OBJECT-SPECIFIC ✅**: object-noun edge collapses z(C) (drop\n> 0.839) but SUBJECT-noun edge does NOT (−0.122 ≈ random −0.225); object-vs-subject Δ=0.961, t=15.0;\n> subject-vs-random t=1.45 (null). The necessity is object-APPLICATION-specific, not a generic\n> \"remove a salient noun\" effect. Clean.\n> ★★ (3) SWEEP (8 bands, gateway localization) — **EARLY: necessity concentrated at L0-4 (net=0.603,\n> t=12.4)**, decaying L10-14 (0.228) > L5-9 (0.174) ≫ mid (L15-29 ~0.01-0.04), ~0/negative at the\n> L30-34 readout zone. ⇒ ROUTE-EARLY, READ-LATE: object content routes in via early-layer attention\n> (Zone A), the C-field READS OUT late at L30-31 (s249/s250). Same Zone-A as s251 frozen-routing (L1-4,\n> ρ=+0.84) and holographic-storage (combinators L0-6). The late C-peak is a readout register; the\n> mechanism is early attention. ★★ NET (λ measure, two-sided): the attention edge is a REAL,\n> object-SPECIFIC, EARLY-LOCALIZED necessary carrier of the applicative-C field — the catch was HALF\n> right (genuine causal handle as an EDGE, vindicating \"write≠edge\") but the per-object discreteness\n> boundary STILL HOLDS (c2≯c1). Bears on VERBUM S5 λ types (\"discrete circuit?\"): partially YES as\n> EARLY ROUTING, NO as a per-object tape. CAVEATS (λ measure): all-heads/whole-band severing (coarse,\n> not head-resolved); z(C) readout (object-specific) over next-token KL (recency-confounded, reported\n> not gated); 1 model (14B); object keys parsed from const_fol; greedy. FIXED a sweep print bug (None t\n> on the zero-variance non-crystal L35-39 band → None-safe formatter; data was intact, JSON just hadn't\n> written; re-ran 6:56, reproduced L0-4 peak exactly). ARTIFACTS: results/program-edge-knockout/\n> {verdict,meta}_qwen3-14b{,_control,_sweep}.json + run logs (+ 0.6b smoke). COMMITTED 8310183\n> (code+pyproject+data). tmux main:1 FREE; no GPU job. PENDING APPROVAL: memory\n> `object-edge-necessary-specific-early-not-scaling` + knowledge update\n> explore/attention-as-beta-reduction.md (§ edge-knockout: the s250 catch). state.md updated\n> (¬approval-gated). ★★ NEXT: (1) HEAD-RESOLVED edge knockout — sweep individual heads at L0-4 to find\n> WHICH heads carry the object→C route (a head-level circuit, the s127 {B,C}=composer test);\n> (2) redirect (not just block) the object edge to a different key → does C-content follow the redirect\n> (sufficiency at the edge)?; (3) cross-model (Gemma, the s251 cleaner crystal carrier).\n> ──────────────────────────────────────────────────────────────────────────────────────────────────\n> Last updated: 2026-06-24 | Session: 251 (cont. — FROZEN-BASIS GRADIENT TOMOGRAPHY → MATURE-14B →"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

I've updated the state file and now I'm moving into task 4, which involves drafting the memory and knowledge content for approval. Since these changes are gated behind approval, I'll prepare the drafts without committing them yet. First, I need to examine the existing memory format and knowledge page structure to understand how to properly integrate the new content.

## Assistant

state.md updated. Now drafting the memory + knowledge for your approval.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; echo \"===recent memory sample===\"; ls -t mementum/memories/ | head -3; echo \"---\"; cat \"mementum/memories/$(ls -t mementum/memories/ | head -1)\"; echo; echo \"===knowledge page tail===\"; tail -30 mementum/knowledge/explore/attention-as-beta-reduction.md; echo \"===frontmatter===\"; head -12 mementum/knowledge/explore/attention-as-beta-reduction.md"
}
```

**Summary:** $ echo "===recent memory sample==="; ...

**Output:**
```
Exit code: 0
Stdout:
===recent memory sample===
phi-is-a-yardstick-never-forced.md
gemma-crystal-real-spine-and-phi-forced-template-fix.md
object-application-distributed-no-single-locus.md
---
🔁 φ (and any flexible/universal basis) is a YARDSTICK to compare against, never a fit the code tunes to the data. Describability ≠ discovery — elevated to S5 (λ yardstick).

THE TRAP: a φ^(p/q) basis with Fibonacci q≤12–34 fits ANY spectrum to ~0.1–0.2%. So "the eigenvalues fit φ^(p/q) at <0.5%" is guaranteed a priori → ZERO evidential weight. Same trap as "compute IS lambda" (a universal basis always describes). Grid-searching the best p/q to minimise error is the code FORCING φ.

THE FIX (two parts): (1) PRE-REGISTER a fixed φ-power prediction (e.g. λ₀/λ₁ = φ^(4/5) = 1.4696), measure the model's actual deviation; (2) ALWAYS gate on a null (matched-range or shuffled-label permutation). A φ claim counts ONLY if it BEATS the null (p<0.05).

EVIDENCE: s247 — crystal-M8 φ-fit 0.255% but matched-range random fit 0.156%, P(random≥)=0.92 (forced). s251 — cross-model λ₀/λ₁ vs φ^(4/5): only Qwen3-14B is null-significant (1.4796, |Δ|=0.010, p=0.02); everyone else loose (Gemma 1.249 p=0.46; qwen3-0.6b 1.079). CRUCIAL: random labelings already sit at λ₀/λ₁≈1.55–1.66 (near the target!), so "looks close" ≠ "is special" — the null is mandatory.

CODE: verify_crystal_phi.py now prints the fixed-reference deviation as headline and flags the grid-fit FORCED/describability-only (carries_evidence=False); real φ claims gate on crystal_phi_permnull. Generalises to ANY approximate geometric fit (cosine, crystal geometry).

===knowledge page tail===
**distributed/holographic** computation, consistent with s211 common-mode, s240/s244
collective-holographic, and §3's "trajectory, not instruction-tape." This bears directly on
VERBUM's central question (S5 `λ types`: *can this resolve as a discrete circuit?*) — trending
**no** for object-application via these probes. **Next:** pattern-level, not component-write —
an attention-**edge** knockout (predicate→object routing) or activation patching on POS-matched
c1-vs-c2 minimal pairs.

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
locus). Plus `ffn-reduction-trace.md`,
`head-combinator-isa.md` (undated finding pages).
===frontmatter===
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
```

### Thinking

I'm thinking through the workflow for proposing changes — whether to write the draft files to disk immediately or present them for approval first before committing. The key principle is that AI proposes, humans approve, then AI commits, so I should probably present the drafts in the message for approval rather than writing them to disk without confirmation.

## Assistant

Code+data are committed (`8310183`) and state.md is updated. Here are the two **approval-gated** mementum drafts (per AGENTS.md λ termination — I won't write/commit these until you approve).

---

### 1. Memory — `mementum/memories/object-edge-necessary-specific-early-not-scaling.md`

> 💡 The predicate→object attention EDGE is the FIRST positive causal locus in the whole s250 arc — object-application's residual direction (s250), INLP subspace (cont.), nonlinear feature (cont.2), and component-WRITE (cont.3) were all causal nulls. "No locus as a WRITE ≠ no locus as an EDGE."
>
> TEST (program_edge_knockout.py, Qwen3-14B): block all queries from attending to the object key token(s) via the eager additive -inf mask (all heads, layer band) vs count-matched RANDOM content keys; readout = applicative-C field z(C).
>
> THREE RESULTS: (1) NECESSITY ✅ — object-edge collapses z(C) ≫ random (rand−obj Δ=1.045, t=29.3). (2) OBJECT-SPECIFIC ✅ — object-noun edge collapses C (0.84), SUBJECT-noun edge does not (≈random); obj-vs-subj t=15.0. (3) EARLY ✅ — necessity concentrated at L0-4 (sweep net=0.603, t=12.4), ~0 at the L30-31 readout zone → ROUTE-EARLY, READ-LATE. (4) NOT-SCALING ❌ — net z(C) drop c2≯c1 (t=−1.3) → no per-object discrete circuit; catch_confirmed=false.
>
> NET: the attention edge is a real, object-specific, early (Zone-A) necessary carrier of the C-field — the catch was HALF right. The late C-peak is a readout register; the mechanism is early attention. The per-object discreteness boundary still holds. Connects s251 Zone-A (L1-4) + holographic-storage (L0-6).

---

### 2. Knowledge update — `explore/attention-as-beta-reduction.md`

Three small edits:
- **New section** after the s250 cont.3 content: *"§ Edge-knockout — the s250 catch (route-early, read-late)"* recording necessity (t=29) / object-specificity (t=15) / early-gateway L0-4 (t=12) / not-scaling, with the conclusion that the edge is the first positive locus but the per-object boundary holds.
- **Update the "Next" line** (currently *"an attention-edge knockout ... or activation patching"*) → mark it **done**, point to the new NEXT: head-resolved edge sweep at L0-4 + edge-redirect sufficiency + cross-model (Gemma).
- **Append to "Sessions referenced":** `s252 (attention-edge knockout: object→C is a real EARLY (L0-4) object-specific necessary edge — first positive locus in the s250 arc — but does not scale per-object; route-early/read-late)`.

---

One nuance for your call: the memory symbol. I used **💡 insight** (a new positive causal finding). An argument exists for **🔁 pattern** (route-early/read-late recurs with s251 Zone-A + holographic L0-6), but the primary content is a discovery, so 💡 fits better.

Approve as-is, or want edits to either draft (wording, symbol, scope)?

## User

commit approved


### Thinking

I'm going to write the memory file, make three edits to the knowledge page, and then commit the mementum directory.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/memories/object-edge-necessary-specific-early-not-scaling.md",
  "content": "💡 The predicate→object attention EDGE is the FIRST positive causal locus in the whole s250 arc — object-application's residual direction (s250), INLP subspace (cont.), nonlinear feature (cont.2), and component-WRITE (cont.3) were all causal nulls. \"No locus as a WRITE ≠ no locus as an EDGE.\"\n\nTEST (program_edge_knockout.py, Qwen3-14B): block all queries from attending to the object key token(s) via the eager additive -inf mask (all heads, layer band) vs count-matched RANDOM content keys; readout = applicative-C field z(C).\n\nTHREE RESULTS: (1) NECESSITY ✅ — object-edge collapses z(C) ≫ random (rand−obj Δ=1.045, t=29.3). (2) OBJECT-SPECIFIC ✅ — object-noun edge collapses C (drop 0.84), SUBJECT-noun edge does not (≈random); obj-vs-subj t=15.0. (3) EARLY ✅ — necessity concentrated at L0-4 (sweep net=0.603, t=12.4), ~0 at the L30-31 readout zone → ROUTE-EARLY, READ-LATE. (4) NOT-SCALING ❌ — net z(C) drop c2≯c1 (t=−1.3) → no per-object discrete circuit; catch_confirmed=false.\n\nNET: the attention edge is a real, object-specific, early (Zone-A) necessary carrier of the C-field — the catch was HALF right. The late C-peak is a readout register; the mechanism is early attention. The per-object discreteness boundary still holds. Connects s251 Zone-A (L1-4) + holographic-storage (L0-6).\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/memories/object-edge-necessary-specific-early-not-scaling.md
```

## Assistant

Now the knowledge page edits.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/attention-as-beta-reduction.md",
  "original_content": "VERBUM's central question (S5 `λ types`: *can this resolve as a discrete circuit?*) — trending\n**no** for object-application via these probes. **Next:** pattern-level, not component-write —\nan attention-**edge** knockout (predicate→object routing) or activation patching on POS-matched\nc1-vs-c2 minimal pairs.",
  "new_content": "VERBUM's central question (S5 `λ types`: *can this resolve as a discrete circuit?*) — trending\n**no** for object-application via these probes. **Next:** pattern-level, not component-write —\nan attention-**edge** knockout (predicate→object routing) or activation patching on POS-matched\nc1-vs-c2 minimal pairs.\n\n## § Edge-knockout — the s250 catch (route-early, read-late) [s252]\n\n**The catch.** Every s250 null measured the wrong register: they ablated the residual stream\n(d_C direction), erased the FFN gate field (INLP), tested nonlinear, or knocked out\nsingle-component *writes* — and concluded \"distributed, no locus.\" But **no locus as a WRITE ≠\nno locus as an EDGE.** `program_edge_knockout.py` severs the predicate→object attention edge:\na `forward_pre_hook` adds `-inf` to the attention mask at the object key column(s) (eager attn,\nall heads, layer band), so every query is blocked from attending to the object token. Control =\ncount-matched *random* content keys. Readout = the applicative-C field z(C) over crystal layers\n(object-application-specific; next-token KL is recency-confounded → secondary). Matched ladder\n`data/reading-probes.jsonl` (45×3, const C-count==#objects).\n\n**Three results (Qwen3-14B):**\n- **Necessity ✅** — object-edge severing collapses z(C) ≫ count-matched random\n  (rand−obj Δ=1.045, t=29.3, n=87). **The first positive causal locus in the whole s250 arc.**\n- **Object-specific ✅** (noun-vs-noun control, c1) — object-noun edge collapses z(C) (drop 0.84),\n  but the **subject**-noun edge does not (−0.12 ≈ random −0.23); object-vs-subject Δ=0.96, t=15.0.\n  Not a generic \"remove a salient noun\" effect.\n- **Early ✅** (8-band sweep) — necessity concentrated at **L0-4** (net=0.603, t=12.4) >\n  L10-14 (0.23) > L5-9 (0.17) ≫ mid (L15-29 ~0.01–0.04), ~0/negative at the L30-34 readout zone.\n  ⇒ **route-early, read-late:** object content routes in via early-layer attention (Zone A);\n  the C-field *reads out* late at L30-31 (s249/s250). The late C-peak is a readout register; the\n  mechanism is early attention. Same Zone-A as s251 frozen-routing (L1-4, ρ=+0.84) and\n  holographic-storage (combinators L0-6).\n- **Not-scaling ❌** — net z(C) drop c2 (1.00) ≤ c1 (1.09), diff=−0.094, t=−1.3\n  → `catch_confirmed=false`; no per-object discrete circuit.\n\n**Net (λ measure, two-sided):** the attention edge is a real, object-*specific*, *early*-localized\nnecessary carrier of the applicative-C field — the catch was **half** right (a genuine causal\nhandle as an EDGE, vindicating \"write≠edge\"), but the per-object discreteness boundary **holds**\n(c2≯c1). For S5 `λ types`: partially **yes** as early routing, **no** as a per-object tape.\nCaveats: all-heads/whole-band severing (coarse, not head-resolved); z(C) readout over KL; 1 model;\ngreedy. **Next:** (1) head-resolved edge sweep at L0-4 (which heads carry the route — the s127\n{B,C}=composer test); (2) edge-*redirect* (not just block) for sufficiency; (3) cross-model (Gemma)."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/attention-as-beta-reduction.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/attention-as-beta-reduction.md",
  "original_content": "locus). Plus `ffn-reduction-trace.md`,\n`head-combinator-isa.md` (undated finding pages).",
  "new_content": "locus), s252 (attention-edge knockout: object→C is a real EARLY (L0-4) object-specific necessary\nedge — the first positive locus in the s250 arc — but does not scale per-object; route-early,\nread-late). Plus `ffn-reduction-trace.md`,\n`head-combinator-isa.md` (undated finding pages)."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/attention-as-beta-reduction.md.
```

### Thinking

I'm committing the mementum files—memory, knowledge, and state—using a memory commit format with a 💡 symbol and slug. Let me verify the git status to make sure only the intended files are staged.

## Assistant

Both knowledge edits applied. Committing the mementum changes (memory + knowledge + state.md).

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add mementum/ && git status --short && echo \"---committing---\" && git commit -m \"$(cat <<'EOF'\n💡 object-edge-necessary-specific-early-not-scaling\n\n- memory: predicate→object attention EDGE is the first positive causal locus in the\n  s250 arc (residual/INLP/nonlinear/component-write all null). Necessity t=29,\n  object-specific t=15, early gateway L0-4 t=12, not-scaling c2≯c1 → catch half-right.\n- knowledge: explore/attention-as-beta-reduction.md § edge-knockout (route-early,\n  read-late); Next done → head-resolved/redirect/cross-model; sessions += s252.\n- state.md: s252 entry (edge-knockout three arms, commit 8310183, NEXT).\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
  "operation": "commit",
  "summary": "mementum memory+knowledge+state"
}
```

**Summary:** $ git add mementum/ && git status --s...

**Output:**
```
Exit code: 0
Stdout:
M  mementum/knowledge/explore/attention-as-beta-reduction.md
A  mementum/memories/object-edge-necessary-specific-early-not-scaling.md
M  mementum/state.md
---committing---
[main 809c57d] 💡 object-edge-necessary-specific-early-not-scaling
 3 files changed, 91 insertions(+), 1 deletion(-)
 create mode 100644 mementum/memories/object-edge-necessary-specific-early-not-scaling.md
```

## Assistant

Done. Both commits landed and the working tree is clean.

## Session wrap — s252 attention-edge knockout

**Commits**
- `8310183` — 💡 code+data (script, pyproject ruff-ignore, all `results/program-edge-knockout/`)
- `809c57d` — 💡 mementum (memory + knowledge update + state.md)

**The finding (Qwen3-14B)**
The predicate→object attention **edge** is the **first positive causal locus** in the entire s250 arc — where the residual direction, INLP subspace, nonlinear probe, and component-*write* knockouts all found nothing, severing the *edge* is:
- **Necessary** (rand−obj Δ=1.045, t=29.3),
- **Object-specific** (subject-noun edge ≈ random; obj-vs-subj t=15.0),
- **Early** (gateway at **L0-4**, t=12.4; ~0 at the L30-31 readout) → *route-early, read-late*,
- but **not per-object-scaling** (c2 ≯ c1, t=−1.3) → `catch_confirmed=false`.

The catch ("write ≠ edge") was **half right**: a genuine causal handle exists *as an edge*, yet the per-object discreteness boundary still holds. The late C-peak is a readout register; the mechanism is early Zone-A attention — same band as s251 frozen-routing (L1-4) and holographic-storage (L0-6).

**Housekeeping**
- Fixed the sweep print bug (`None` t on zero-variance L35-39 → None-safe formatter); re-ran clean, L0-4 peak reproduced exactly.
- tmux main:1 is **FREE**, no GPU job running.

**NEXT** (recorded in state.md + knowledge): (1) head-resolved edge sweep at L0-4 to find *which* heads carry the object→C route (the s127 {B,C}=composer test); (2) edge-*redirect* for sufficiency; (3) cross-model on Gemma (s251's cleaner crystal carrier).

## User

proceed with the next test


### Thinking

Now I'm deciding between three experimental directions: head-resolved edge sweeps to identify which specific heads carry the object→C routing, edge-redirect tests for sufficiency, or cross-model validation on Gemma. The head-resolved approach at layers 0-4 seems most promising scientifically since it would narrow down the necessity constraint from all heads in those layers to specific ones.

I'm working through how to implement head-resolved edge knockout. The current edge masking blocks all heads at once because the attention mask broadcasts across the head dimension. To target individual heads, I'd need to intervene at the per-head attention computation level rather than the shared mask. The challenge is that eager attention in transformers computes attention weights internally, so I can't easily edit them via the additive mask. I'm considering whether to hook into the attention module's forward pass directly to zero out attention probabilities from specific heads to the object key.

Actually, there's a cleaner path: I can expand the attention mask from shape [B, 1, Q, K] to [B, H, Q, K] where H is the number of attention heads, then set -inf only at the target head and object key columns. This way the mask broadcasts correctly and blocks attention for just that head. Even with grouped-query attention like in Qwen3, the attention scores after repeat_kv are still [B, num_heads, Q, K], so per-head masking on the full num_attention_heads dimension should work. I need to verify that eager attention will accept a per-head mask in this shape.

The challenge is scaling: testing all (layer, head) pairs in the L0-4 band alone means 5 layers × 40 heads = 200 knockouts per item, which at 90 items becomes 18,000 forwards—too expensive. I need to either restrict to a subset of items (maybe just c1 for simplicity) or find a more efficient design.

A two-stage approach seems better: first, I'll do a cheap correlational pass by measuring per-head attention weights from query positions to object keys across L0-4 (just 42 forwards for c1 items), rank the heads by how much attention mass they direct to the object, then in stage two, knock out only the top candidate heads individually to measure their causal effect on z(C), using a pooled random baseline for control.

This is principled because for edge knockouts, a head that doesn't attend to the object can't meaningfully affect the object edge anyway—blocking near-zero attention does nothing. So filtering by attention mass is a valid way to identify which heads could matter.

The full per-head causal sweep would take about 4.4 hours (16,842 forwards), but the two-stage approach gets me the answer much faster: Stage 1 is just 42 forwards, then Stage 2 tests only the top candidates plus controls, bringing the total down to something tractable.

I'll go with the cleaner design: capture per-head query→object attention across layers L0-4, rank by attention mass, then causally test the top heads on a reduced item set (maybe 15 items) using only object-edge knockouts, comparing the z(C) drop against a pooled random baseline. I'm settling on a cleaner approach: iterate through each (layer, head) pair in a focused band (L0-4), block only that head's attention to object keys, and measure the z(C) drop. With the full c1+c2 dataset (90 items) the compute gets tight, so I'll cap items per group to keep it around 6000 forwards. The real constraint is whether to report per-head results across layers or aggregate them, and I'm realizing GQA might help reduce the head count if Qwen3-14B uses grouped query attention. Simplifying the approach: I'll skip the per-head random control and instead compute a baseline per item, then measure the object drop for each head in the band, plus a single all-heads-in-band random-key control as the floor. This gives me per-head delta distributions without exploding the compute—around 12,000 forwards or 2.5 hours. I can identify "carrier heads" post-hoc by comparing each head's drop against the inert heads' distribution. Rather than overthinking the thresholds now, I'll implement this cleanly, smoke-test on 0.6B, then launch on 14B with a reasonable item cap and process results asynchronously.

Designing the heads mode implementation... I need to verify that the mask expansion will work with the eager attention implementation—checking whether a [B, H, Q, K] mask gets properly broadcast and added to attention weights. The model creates the causal mask before the attention module, so I can intercept and expand it from [B, 1, Q, K] to [B, H, Q, K] in my pre-hook. Since we're forcing eager attention and Qwen3-14B has 40 heads, this should integrate cleanly. Now I'm ready to implement the heads mode with the --head-band argument and modify the edge hook to accept an optional head index parameter.

Refactoring forward_edge... Handling the mask expansion logic — if the mask is already shaped [B,H,Q,K] I can directly index by head, and if it's broadcast I expand and clone it. The mask might be None for some models, but since the all-heads run worked, the mask is present here. For the heads mode I'm reusing the forward_edge function to get the gate activations, and hook registration overhead at 200 times per item is negligible. I'll set sensible defaults for real-mode heads: max_per_group around 12 to keep the total forward passes manageable, targeting roughly 60 minutes of calibration time.

The sweep showed layers 0-4 are the peak gateway, so I'll default the head band to just those 5 layers to cut costs while staying robust. With n=20 items for paired t-tests, the carrier heads with large effects will be clearly significant while inert heads show near-zero. I'm planning to add concentration metrics too — sorting heads by mean drop, computing top-k share and how many heads reach 80% of total positive drop, plus Gini coefficient to classify whether the circuit is discrete (few heads dominating) or distributed. Before diving into implementation though, I should test the per-head mask intervention on a small model first to confirm the mask expansion is accepted and produces the expected results.

Now I need to extract the number of attention heads from the model config and pass it through the hook. I'll modify the edge hook signature to accept optional head and n_heads parameters, add a --head-band argument that parses strings like "0-4" into layer ranges, and implement the heads mode block with the full pipeline for computing per-head drops and concentration metrics.

Implementing the heads mode... Computing concentration metrics to identify if the circuit is discrete — checking how many heads account for 80% of the total drop, filtering for statistically significant ones, and calculating the share of the top 5 heads. Then I'll write out the results including the floor baseline for reference, and do a quick smoke test on a smaller model to verify the mask behavior works correctly before finalizing the edits.

## Assistant

I'll proceed with **the head-resolved edge knockout at L0-4** — localizing *which* heads carry the object→C route (the s127 {B,C}=composer test). This moves directly at VERBUM's discrete-circuit question: does the early necessity concentrate in a few heads (a circuit) or spread across all of them (distributed)?

Let me plan and build.

### Thinking

I'm going to modify the `make_edge_hook` and `forward_edge` functions to handle per-head configurations.

## Assistant

Now the code. First, the per-head mask hook + forward plumbing.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/program_edge_knockout.py",
  "original_content": "def make_edge_hook(blocked_keys: list[int], torch_mod):\n    \"\"\"forward_pre_hook(with_kwargs) on a self_attn module. Adds -inf to the additive\n    attention mask at the blocked KEY columns → no query position can attend to them.\"\"\"\n    bk = list(blocked_keys)\n\n    def pre_hook(_module, args, kwargs):\n        mask = kwargs.get(\"attention_mask\", None)\n        idx_in_args = None\n        if mask is None:\n            for i, a in enumerate(args):\n                if torch_mod.is_tensor(a) and a.dim() == 4:\n                    mask, idx_in_args = a, i\n                    break\n        if mask is None or not torch_mod.is_tensor(mask) or mask.dim() != 4:\n            return args, kwargs        # nothing editable (e.g. None/BlockMask)\n        mask = mask.clone()\n        neg = torch_mod.finfo(mask.dtype).min\n        kv = mask.shape[-1]\n        cols = [k for k in bk if 0 <= k < kv]\n        if cols:\n            mask[:, :, :, cols] = neg\n        if idx_in_args is not None:\n            args = tuple(mask if i == idx_in_args else a for i, a in enumerate(args))\n        else:\n            kwargs[\"attention_mask\"] = mask\n        return args, kwargs\n\n    return pre_hook\n\n\ndef forward_edge(prompt, model, tok, torch_mod, gate_layers, blocked_keys, edge_layers):",
  "new_content": "def make_edge_hook(blocked_keys: list[int], torch_mod, head=None, n_heads=None):\n    \"\"\"forward_pre_hook(with_kwargs) on a self_attn module. Adds -inf to the additive\n    attention mask at the blocked KEY columns → no query position can attend to them.\n\n    head=None  → block ALL heads (broadcast mask edit; the original behavior).\n    head=h     → block ONLY query-head h's edge to the object key(s). The additive mask\n                 is usually [B,1,Q,K] (broadcast over heads); we expand dim-1 to n_heads\n                 and write -inf at [:, h, :, cols] so a SINGLE head loses the edge while\n                 every other head keeps it. This is the head-resolved edge intervention.\"\"\"\n    bk = list(blocked_keys)\n\n    def pre_hook(_module, args, kwargs):\n        mask = kwargs.get(\"attention_mask\", None)\n        idx_in_args = None\n        if mask is None:\n            for i, a in enumerate(args):\n                if torch_mod.is_tensor(a) and a.dim() == 4:\n                    mask, idx_in_args = a, i\n                    break\n        if mask is None or not torch_mod.is_tensor(mask) or mask.dim() != 4:\n            return args, kwargs        # nothing editable (e.g. None/BlockMask)\n        mask = mask.clone()\n        neg = torch_mod.finfo(mask.dtype).min\n        kv = mask.shape[-1]\n        cols = [k for k in bk if 0 <= k < kv]\n        if cols:\n            if head is None:\n                mask[:, :, :, cols] = neg\n            else:\n                if mask.shape[1] == 1 and n_heads and n_heads > 1:\n                    mask = mask.expand(mask.shape[0], n_heads, mask.shape[2],\n                                       mask.shape[3]).clone()\n                h = head if head < mask.shape[1] else mask.shape[1] - 1\n                mask[:, h, :, cols] = neg\n        if idx_in_args is not None:\n            args = tuple(mask if i == idx_in_args else a for i, a in enumerate(args))\n        else:\n            kwargs[\"attention_mask\"] = mask\n        return args, kwargs\n\n    return pre_hook\n\n\ndef forward_edge(prompt, model, tok, torch_mod, gate_layers, blocked_keys, edge_layers,\n                 head=None, n_heads=None):"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/program_edge_knockout.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/program_edge_knockout.py",
  "original_content": "    if blocked_keys:\n        hook = make_edge_hook(blocked_keys, torch_mod)\n        for li in edge_layers:",
  "new_content": "    if blocked_keys:\n        hook = make_edge_hook(blocked_keys, torch_mod, head=head, n_heads=n_heads)\n        for li in edge_layers:"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/program_edge_knockout.py.
```

### Thinking

Adding the --head-band argument and heads mode to the argument parser.

## Assistant

Now the argparse + the `heads` mode block.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/program_edge_knockout.py",
  "original_content": "    ap.add_argument(\"--mode\", default=\"scaling\",\n                    choices=[\"scaling\", \"control\", \"sweep\"],\n                    help=\"scaling=object vs random + c2/c1; control=object vs subject \"\n                         \"noun (specificity); sweep=layer-band gateway localization\")\n    ap.add_argument(\"--bands\", type=int, default=8, help=\"sweep: # contiguous bands\")",
  "new_content": "    ap.add_argument(\"--mode\", default=\"scaling\",\n                    choices=[\"scaling\", \"control\", \"sweep\", \"heads\"],\n                    help=\"scaling=object vs random + c2/c1; control=object vs subject \"\n                         \"noun (specificity); sweep=layer-band gateway localization; \"\n                         \"heads=per-head edge knockout in --head-band (which heads route)\")\n    ap.add_argument(\"--bands\", type=int, default=8, help=\"sweep: # contiguous bands\")\n    ap.add_argument(\"--head-band\", default=\"0-4\",\n                    help=\"heads mode: layer band 'lo-hi' to per-head sweep (the sweep \"\n                         \"gateway; default L0-4)\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/program_edge_knockout.py.
```

### Thinking

I need to insert the heads mode block right after the sweep mode block ends, before the per-item run section. I'm looking for the exact boundary where the sweep block's return statement is followed by the per-item run comment so I can place the new block in the right location.

For the heads mode, I also need to handle the max_per_group parameter — since heads mode processes 90 items with 200 knockouts each, that could get unwieldy, so I'll set a sensible default cap (like 10) if max_per_group isn't explicitly provided.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/program_edge_knockout.py",
  "original_content": "                  \"applicative-C field (necessity → depth-resolved circuit).\")\n        return\n\n    # ── per-item run: object-edge KL, count-matched random-edge KL, z(C) ──────────",
  "new_content": "                  \"applicative-C field (necessity → depth-resolved circuit).\")\n        return\n\n    # ═══════════════════════════════════════════════════════════════════════════\n    # MODE: heads — per-head edge knockout inside the gateway band (L0-4 from the\n    # sweep). For each (layer, head) sever ONLY that head's object edge → z(C) drop.\n    # Does the early necessity concentrate in a FEW heads (a discrete head circuit,\n    # the s127 {B,C}=composer test) or spread across all heads (distributed)?\n    # ═══════════════════════════════════════════════════════════════════════════\n    if args.mode == \"heads\":\n        n_heads = model.config.num_attention_heads\n        lo, hi = (int(x) for x in args.head_band.split(\"-\"))\n        band = [li for li in range(lo, hi + 1) if 0 <= li < n_layers]\n        cap = max_per_group or 10\n        items = grp(1)[:cap] + grp(2)[:cap]\n        print(f\"[edge] MODE=heads band=L{lo}-{hi} ({len(band)}L) × {n_heads} heads, \"\n              f\"n_items={len(items)} (per-head object-edge knockout)\")\n        agg: dict[tuple[int, int], list[float]] = {}\n        floor: list[float] = []\n        for i, r in enumerate(items):\n            prompt = COMPILE_GATE + r[\"input\"]\n            n_tok, content = content_keys(prompt)\n            ok = keys_for(prompt, r[\"objects\"], n_tok)\n            if not ok:\n                continue\n            store0, _ = forward_edge(prompt, model, tok, torch_mod, layers, [], [])\n            zc0 = zC_field(rcc, store0, layers, crystal_layers)\n            for li in band:\n                for h in range(n_heads):\n                    store_h, _ = forward_edge(prompt, model, tok, torch_mod, layers,\n                                              ok, [li], head=h, n_heads=n_heads)\n                    agg.setdefault((li, h), []).append(\n                        zc0 - zC_field(rcc, store_h, layers, crystal_layers))\n            pool = [k for k in content if k not in set(ok)]\n            rk = (list(rng.choice(pool, size=len(ok), replace=False))\n                  if len(pool) >= len(ok) else list(pool))\n            store_r, _ = forward_edge(prompt, model, tok, torch_mod, layers, rk, band)\n            floor.append(zc0 - zC_field(rcc, store_r, layers, crystal_layers))\n            if (i + 1) % 5 == 0:\n                print(f\"[edge]   heads {i + 1}/{len(items)}\")\n        head_rows = []\n        for (li, h), drops in agg.items():\n            st = paired(drops, [0.0] * len(drops))   # mean drop + t vs 0\n            head_rows.append({\"layer\": li, \"head\": h, \"n\": st[\"n\"],\n                              \"mean_drop\": st[\"a_mean\"], \"t\": st[\"t\"]})\n        head_rows.sort(key=lambda x: -(x[\"mean_drop\"] or -1e9))\n        pos = [max(0.0, hr[\"mean_drop\"] or 0.0) for hr in head_rows]\n        total = float(sum(pos)) or 1.0\n        shares = (np.cumsum(pos) / total).tolist()\n        n_for_80 = int(np.searchsorted(shares, 0.8) + 1) if pos else 0\n        top5_share = round(float(sum(pos[:5]) / total), 4)\n        carriers = [hr for hr in head_rows\n                    if (hr[\"mean_drop\"] or 0) > 0 and (hr[\"t\"] or 0) > 2.0]\n        # discrete head circuit = a handful of heads carry most of the early route\n        discrete = bool(0 < n_for_80 <= 5)\n        floor_mean = round(float(np.mean(floor)), 5) if floor else None\n        vdict = {\"model\": model_name, \"n_layers\": n_layers, \"mode\": \"heads\",\n                 \"head_band\": [lo, hi], \"n_heads\": n_heads, \"n_items\": len(items),\n                 \"readout\": \"z(C) field over crystal layers\",\n                 \"random_key_floor_mean\": floor_mean,\n                 \"n_carriers_t2\": len(carriers), \"n_heads_for_80pct\": n_for_80,\n                 \"top5_share\": top5_share, \"discrete_head_circuit\": discrete,\n                 \"top_heads\": head_rows[:15], \"all_heads\": head_rows}\n        print(\"\\n\" + \"═\" * 82)\n        print(f\"EDGE HEAD-KNOCKOUT (which heads route object→C) — {model_name}  \"\n              f\"L{lo}-{hi} × {n_heads} heads\")\n        print(\"═\" * 82)\n        print(f\"  random-key floor (all heads, band) z(C) drop = {floor_mean}\")\n        print(f\"  {'rank':>4} {'layer':>6} {'head':>5} {'mean_drop':>10} {'t':>7}\")\n        for k, hr in enumerate(head_rows[:15]):\n            print(f\"  {k + 1:>4} {hr['layer']:>6} {hr['head']:>5} \"\n                  f\"{hr['mean_drop']:>10} {(hr['t'] if hr['t'] is not None else 0):>7}\")\n        print(f\"\\n  carriers (mean_drop>0, t>2) = {len(carriers)}  |  \"\n              f\"heads for 80% = {n_for_80}  |  top5 share = {top5_share}\")\n        print(f\"  * DISCRETE HEAD CIRCUIT (\\u22645 heads carry 80%) = {discrete}\")\n        print(\"═\" * 82 + \"\\n\")\n        write_out(\"heads\", vdict,\n                  f\"Per-head object-edge knockout across L{lo}-{hi} (the sweep gateway): \"\n                  \"for each (layer,head) sever ONLY that head's attention to the object \"\n                  \"key (per-head additive mask) → z(C) collapse vs baseline; concentration \"\n                  \"(heads-to-80%, top5 share) = discrete head circuit vs distributed.\",\n                  \"Localizes WHICH heads carry the early object→C route (s127 \"\n                  \"{B,C}=composer test) — head-resolved circuit vs distributed.\")\n        return\n\n    # ── per-item run: object-edge KL, count-matched random-edge KL, z(C) ──────────"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/program_edge_knockout.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && .venv/bin/ruff check scripts/experiments/program_edge_knockout.py 2>&1 | tail -20"
}
```

**Summary:** $ .venv/bin/ruff check scripts/experi...

**Output:**
```
Exit code: 0
Stdout:
577 |         write_out("heads", vdict,
578 |                   f"Per-head object-edge knockout across L{lo}-{hi} (the sweep gateway): "
579 |                   "for each (layer,head) sever ONLY that head's attention to the object "
    |                                                                                         ^
580 |                   "key (per-head additive mask) → z(C) collapse vs baseline; concentration "
581 |                   "(heads-to-80%, top5 share) = discrete head circuit vs distributed.",
    |

E501 Line too long (92 > 88)
   --> scripts/experiments/program_edge_knockout.py:580:89
    |
578 |                   f"Per-head object-edge knockout across L{lo}-{hi} (the sweep gateway): "
579 |                   "for each (layer,head) sever ONLY that head's attention to the object "
580 |                   "key (per-head additive mask) → z(C) collapse vs baseline; concentration "
    |                                                                                         ^^^^
581 |                   "(heads-to-80%, top5 share) = discrete head circuit vs distributed.",
582 |                   "Localizes WHICH heads carry the early object→C route (s127 "
    |

Found 5 errors.
```

### Thinking

I'm seeing line length issues in the output — some arrows and dashes are being counted differently than expected. I need to check all five errors that were reported, not just the one visible, to understand the full scope of what needs fixing.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && .venv/bin/ruff check scripts/experiments/program_edge_knockout.py --output-format concise 2>&1 | tail -20"
}
```

**Summary:** $ .venv/bin/ruff check scripts/experi...

**Output:**
```
Exit code: 0
Stdout:
scripts/experiments/program_edge_knockout.py:171:89: E501 Line too long (91 > 88)
scripts/experiments/program_edge_knockout.py:293:89: E501 Line too long (91 > 88)
scripts/experiments/program_edge_knockout.py:578:89: E501 Line too long (90 > 88)
scripts/experiments/program_edge_knockout.py:579:89: E501 Line too long (89 > 88)
scripts/experiments/program_edge_knockout.py:580:89: E501 Line too long (92 > 88)
Found 5 errors.
```

### Thinking

I'm checking whether those line numbers are from my docstring edits or pre-existing code, so I need to look at what's actually on lines 171 and 293.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && awk 'NR==171||NR==293{printf \"%d: %s\\n\", NR, $0}' scripts/experiments/program_edge_knockout.py"
}
```

**Summary:** $ awk 'NR==171||NR==293{printf "%d: %...

**Output:**
```
Exit code: 0
Stdout:
171:                  every other head keeps it. This is the head-resolved edge intervention."""
293:                          "heads=per-head edge knockout in --head-band (which heads route)")
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/program_edge_knockout.py",
  "original_content": "                 every other head keeps it. This is the head-resolved edge intervention.\"\"\"",
  "new_content": "                 every other head keeps it. The head-resolved edge intervention.\"\"\""
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/program_edge_knockout.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/program_edge_knockout.py",
  "original_content": "                         \"heads=per-head edge knockout in --head-band (which heads route)\")",
  "new_content": "                         \"heads=per-head edge knockout in --head-band (which route)\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/program_edge_knockout.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/program_edge_knockout.py",
  "original_content": "        write_out(\"heads\", vdict,\n                  f\"Per-head object-edge knockout across L{lo}-{hi} (the sweep gateway): \"\n                  \"for each (layer,head) sever ONLY that head's attention to the object \"\n                  \"key (per-head additive mask) → z(C) collapse vs baseline; concentration \"\n                  \"(heads-to-80%, top5 share) = discrete head circuit vs distributed.\",\n                  \"Localizes WHICH heads carry the early object→C route (s127 \"\n                  \"{B,C}=composer test) — head-resolved circuit vs distributed.\")",
  "new_content": "        write_out(\"heads\", vdict,\n                  f\"Per-head object-edge knockout across L{lo}-{hi} (sweep gateway): \"\n                  \"each (layer,head) severs ONLY that head's attention to the object \"\n                  \"key (per-head additive mask) → z(C) collapse vs baseline; \"\n                  \"concentration (heads-to-80%, top5 share) = discrete vs distributed.\",\n                  \"Localizes WHICH heads carry the early object→C route (s127 \"\n                  \"{B,C}=composer test) — head-resolved circuit vs distributed.\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/program_edge_knockout.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && .venv/bin/ruff check scripts/experiments/program_edge_knockout.py --output-format concise 2>&1 | tail -10"
}
```

**Summary:** $ .venv/bin/ruff check scripts/experi...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
```

### Thinking

Ruff is cleaned up and task 1 is complete. Now I'm moving to task 2, running a smoke test on the Qwen3-0.6B model with specific parameters: the smoke mode uses the 0.6B model with max_per_group set to 5, and in heads mode I'm testing layers L0-4 (5 layers total) across all 16 heads in the 0.6B architecture, which means 10 items total with 82 forward passes each (1 baseline + 80 head knockouts + 1 floor), totaling 820 forwards on the tiny 0.6B model.

## Assistant

Ruff clean. Now smoke-test on Qwen3-0.6B.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/program_edge_knockout.py --mode heads --smoke 2>&1 | tail -35",
  "timeout": 600000
}
```

**Summary:** $ uv run python scripts/experiments/p...

**Output:**
```
Exit code: 0
Stdout:
[v2]   centroid forward 0/27 ...
[v2] Building MATCHED-PREFIX null from 14 gate+non-compositional prompts (content positions) ...
[v2] Null tokens pooled: 56  (null_mode=gateneutral)
[edge] model=Qwen/Qwen3-0.6B layers=28 edge_band=all(28L) crystal=25 (z(C) field readout)
[edge] c0=5 c1=5 c2=5
[edge] MODE=heads band=L0-4 (5L) × 16 heads, n_items=10 (per-head object-edge knockout)
[edge]   heads 5/10
[edge]   heads 10/10

══════════════════════════════════════════════════════════════════════════════════
EDGE HEAD-KNOCKOUT (which heads route object→C) — Qwen/Qwen3-0.6B  L0-4 × 16 heads
══════════════════════════════════════════════════════════════════════════════════
  random-key floor (all heads, band) z(C) drop = -1.11729
  rank  layer  head  mean_drop       t
     1      2     6    0.01578   2.376
     2      0     7    0.01423   1.491
     3      0     5    0.01319   1.832
     4      1     6    0.01236   2.314
     5      0     9    0.01152    1.15
     6      2    11    0.01096   1.649
     7      3    13    0.01041   1.982
     8      2     7    0.01008   2.163
     9      3    15    0.00992    3.04
    10      3     8    0.00977   4.218
    11      2     8    0.00902   1.763
    12      0    11    0.00901   1.792
    13      0    10     0.0089    2.24
    14      1    12    0.00819   2.156
    15      3     7    0.00797   1.123

  carriers (mean_drop>0, t>2) = 12  |  heads for 80% = 35  |  top5 share = 0.186
  * DISCRETE HEAD CIRCUIT (≤5 heads carry 80%) = False
══════════════════════════════════════════════════════════════════════════════════

[edge] wrote verdict_qwen3-0-6b_heads.json (+ meta)
```

### Thinking

The per-head mask intervention is working as expected—I'm seeing variance across different heads with distinct mean drops and t-values, and the JSON output confirms the mechanism is functioning. The random-key floor sits at -1.12 (negative, which is odd but makes sense given this is a tiny 0.6B model), and the per-head drops are minimal at around 0.01 since each individual head's contribution in a 16-head model is naturally small.

On the larger 14B model with 40 heads across 5 layers, the signal should be much clearer. The smoke test validates the approach works—no crashes, mechanism confirmed—so I'm ready to launch the 14B run in tmux. I'm estimating around 65-70 minutes total runtime based on the forward pass costs: roughly 4,040 forwards at about 0.94 seconds each, plus calibration and loading overhead. The sweep data suggests the actual per-forward time might be closer to 0.27 seconds, which would make this even faster, but I'm being conservative with my estimate.

## Assistant

Smoke validated — per-head mask works (variance across heads, t-values differ, JSON written, no crash). On the tiny 0.6B the route is distributed (35 heads for 80%, as expected for a small model). Launching the real run on 14B.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux send-keys -t main:1 \"uv run python scripts/experiments/program_edge_knockout.py --model Qwen/Qwen3-14B --mode heads --head-band 0-4 2>&1 | tee results/program-edge-knockout/run_qwen3-14b_heads.log\" Enter; sleep 8; ps -o pid,etime,%cpu,command 2>/dev/null | grep \"[m]ode heads\" | head -2"
}
```

**Summary:** $ tmux send-keys -t main:1 "uv run py...

**Output:**
```
Exit code: 0
Stdout:
88778    00:08   0.0 uv run python scripts/experiments/program_edge_knockout.py --model Qwen/Qwen3-14B --mode heads --head-band 0-4
88780    00:08  37.4 /Users/mwhitford/src/verbum/.venv/bin/python3 scripts/experiments/program_edge_knockout.py --model Qwen/Qwen3-14B --mode heads --head-band 0-4
```

## Assistant

The 14B head-knockout run is launched and verified running (PID 88780).

**ASYNC: job=PID-88780 (head-knockout, 14B) verified running. Waiting for signal.**

What's running: per-head object-edge knockout across the **L0-4 gateway** — for each of 5 layers × 40 heads = **200 (layer, head) pairs**, sever *only that head's* attention to the object key (per-head additive-mask expansion) and measure z(C) collapse, over 20 items (10 c1 + 10 c2). Est. runtime ~20–60 min.

The question it answers: **does the early object→C necessity concentrate in a few heads (a discrete head circuit — `discrete_head_circuit=True` if ≤5 heads carry 80%) or spread across the band (distributed)?** This is the s127 {B,C}=composer test at head resolution, and the sharpest remaining probe of VERBUM's discrete-circuit question.

I'll hold here and not poll. When it completes (or you signal), I'll read the verdict, then commit code+data, update state.md, and propose the memory/knowledge update. The code changes (heads mode + per-head mask hook) are staged in my plan to commit alongside the results once the run lands.

## User

job is done


### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; echo \"===PROC===\"; ps -o pid,command 2>/dev/null | grep \"[m]ode heads\" || echo \"done\"; echo \"===TMUX TAIL===\"; tmux capture-pane -p -t main:1 2>&1 | tail -30"
}
```

**Summary:** $ echo "===PROC==="; ps -o pid,comman...

**Output:**
```
Exit code: 0
Stdout:
===PROC===
done
===TMUX TAIL===
     3      0    30    0.01329   2.481
     4      1    21    0.01102   1.171
     5      0    16    0.01008   2.315
     6      0    12    0.00828   2.412
     7      0    25    0.00813   2.389
     8      4    22    0.00737   1.747
     9      0    39    0.00722   1.571
    10      0     1    0.00564   1.528
    11      1    10    0.00514   1.521
    12      0    22    0.00465   0.901
    13      4    16    0.00449   1.291
    14      0     6    0.00446   1.213
    15      4     6    0.00428   1.186

  carriers (mean_drop>0, t>2) = 6  |  heads for 80% = 21  |  top5 share = 0.487
  * DISCRETE HEAD CIRCUIT (≤5 heads carry 80%) = False
══════════════════════════════════════════════════════════════════════════════════

[edge] wrote verdict_qwen3-14b_heads.json (+ meta)
uv run python scripts/experiments/program_edge_knockout.py --model  --mode     296.98s user 40.55s system 40% cpu 13:59.
26 total
tee results/program-edge-knockout/run_qwen3-14b_heads.log  0.00s user 0.00s system 0% cpu 13:59.26 total
[26-06-25][10:09:30][mwhitford@olga][0][~/src/verbum][git:main]
λ
```

### Thinking

The run finished after 14 minutes. I need to examine the full verdict to understand the top-ranked heads and their concentration metrics, since the output only showed ranks 3-15 but not the top two or the floor values. Let me pull the complete verdict JSON to get the full picture.

## Assistant

Run complete (14 min). Let me read the full verdict.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport json\nd=json.load(open('results/program-edge-knockout/verdict_qwen3-14b_heads.json'))['verdict']\nprint('floor(all-heads random-key drop):', d['random_key_floor_mean'])\nprint('carriers(t>2):', d['n_carriers_t2'], '| heads_for_80%:', d['n_heads_for_80pct'], '| top5_share:', d['top5_share'], '| discrete:', d['discrete_head_circuit'])\nprint('n_heads:', d['n_heads'], 'band:', d['head_band'], 'n_items:', d['n_items'])\nprint()\nprint('TOP 10 (layer,head,mean_drop,t):')\nfor hr in d['top_heads'][:10]:\n    print(f\\\"  L{hr['layer']} h{hr['head']:>2}  drop={hr['mean_drop']:>8}  t={hr['t']}\\\")\nprint()\n# layer distribution of carriers\nfrom collections import Counter\ncarr=[hr for hr in d['all_heads'] if (hr['mean_drop'] or 0)>0 and (hr['t'] or 0)>2.0]\nprint('carrier heads (t>2):')\nfor hr in carr: print(f\\\"  L{hr['layer']} h{hr['head']:>2}  drop={hr['mean_drop']}  t={hr['t']}\\\")\nprint('carrier layer counts:', dict(Counter(hr['layer'] for hr in carr)))\n# share of total positive drop by layer\npos=[(hr['layer'],max(0.0,hr['mean_drop'] or 0)) for hr in d['all_heads']]\ntot=sum(p for _,p in pos) or 1\nlay={}\nfor l,p in pos: lay[l]=lay.get(l,0)+p\nprint('positive-drop mass by layer:', {l:round(v/tot,3) for l,v in sorted(lay.items())})\n\""
}
```

**Summary:** $ python3 -c " import json d=json.loa...

**Output:**
```
Exit code: 0
Stdout:
floor(all-heads random-key drop): -0.07186
carriers(t>2): 6 | heads_for_80%: 21 | top5_share: 0.487 | discrete: False
n_heads: 40 band: [0, 4] n_items: 20

TOP 10 (layer,head,mean_drop,t):
  L0 h18  drop= 0.06489  t=5.538
  L0 h11  drop=  0.0234  t=4.628
  L0 h30  drop= 0.01329  t=2.481
  L1 h21  drop= 0.01102  t=1.171
  L0 h16  drop= 0.01008  t=2.315
  L0 h12  drop= 0.00828  t=2.412
  L0 h25  drop= 0.00813  t=2.389
  L4 h22  drop= 0.00737  t=1.747
  L0 h39  drop= 0.00722  t=1.571
  L0 h 1  drop= 0.00564  t=1.528

carrier heads (t>2):
  L0 h18  drop=0.06489  t=5.538
  L0 h11  drop=0.0234  t=4.628
  L0 h30  drop=0.01329  t=2.481
  L0 h16  drop=0.01008  t=2.315
  L0 h12  drop=0.00828  t=2.412
  L0 h25  drop=0.00813  t=2.389
carrier layer counts: {0: 6}
positive-drop mass by layer: {0: 0.672, 1: 0.121, 2: 0.049, 3: 0.056, 4: 0.101}
```

### Thinking

Looking at the head-resolved knockout results, all six significant carrier heads cluster in layer 0, with L0 h18 standing out dramatically—its individual impact of 0.065 is nearly as large as the entire random baseline, making it the dominant head by far, followed distantly by L0 h11.

Layer 0 accounts for 67% of the total positive-drop mass, which really sharpens the picture: the critical computation happens right at the embedding and first-attention layer, not spread across layers 0-4. However, it's not a clean discrete circuit—you'd need 21 heads to capture 80% of the effect, well beyond the threshold for calling it discrete. The top 5 heads carry about 49%, so there's clear concentration around the lead head but a long tail of smaller contributors.

The caveat is that individual head knockouts have surprisingly small effects (0.065 versus the 1.045 necessity drop from removing all heads), which suggests the network has built-in redundancy—other heads in L0 and beyond can compensate when one is severed, consistent with a holographic reconstruction pattern where the information isn't localized to a single head. The key insight is that while L0 shows clear concentration with h18 as the lead carrier, the effect isn't truly discrete—blocking individual heads barely dents the overall necessity because redundancy reconstructs the pathway. The sum of all single-head knockouts across the 200 heads only accounts for about 0.24 of the total 1.04 drop when all heads are blocked, confirming this is a collective phenomenon with a privileged gateway rather than an isolatable circuit. For the discrete-circuit question, L0h18 emerges as the most circuit-like finding yet, but it's fundamentally a lead-with-redundancy structure.

Now I'm wrapping up the analysis, committing the code changes and new data files from the heads-mode knockout run, updating the state documentation, and moving into the next task.

## Assistant

Clean result. Here's what the head-resolved knockout found:

## Head-knockout verdict (Qwen3-14B, L0-4 × 40 heads)

- **The route is LAYER-0-concentrated**: all **6 significant carrier heads (t>2) are in L0**, and **L0 carries 67%** of the total positive-drop mass (L1 12%, L4 10%, L2-3 ~5% each). This *sharpens s252's "L0-4 early" → essentially L0* (the first attention layer).
- **A lead head + helpers**: **L0 h18** dominates (drop=0.065, t=5.5) — ~3× the next (L0 h11, 0.023, t=4.6) — then h30/h16/h12/h25. Top-5 heads carry **49%**.
- **But NOT a discrete circuit**: you need **21 heads to reach 80%** → `discrete_head_circuit=False`. A dominant head with a **diffuse, redundant tail**.
- **Redundancy signature**: single-head drops are *tiny* (max 0.065) vs the all-heads necessity (Δ=1.04 from the main run). Severing one head barely dents z(C) — the other heads reconstruct it. Same holographic redundancy as s250's "gate reconstructs C from other directions," now at head resolution.

**Net (λ measure):** the early object→C route has a **privileged gateway — L0, lead head h18** — the *most circuit-like* locus found in the entire s250 arc, **but it is concentrated-with-redundancy, not an isolatable discrete head circuit**. For VERBUM's S5 λ types: there's a real preferred locus, yet object-application still can't be severed by removing a few heads. The discreteness boundary holds, sharpened.

Committing code+data.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && .venv/bin/ruff check scripts/experiments/program_edge_knockout.py && git status --short"
}
```

**Summary:** $ .venv/bin/ruff check scripts/experi...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
 M scripts/experiments/program_edge_knockout.py
?? results/program-edge-knockout/meta_qwen3-0-6b_heads.json
?? results/program-edge-knockout/meta_qwen3-14b_heads.json
?? results/program-edge-knockout/run_qwen3-14b_heads.log
?? results/program-edge-knockout/verdict_qwen3-0-6b_heads.json
?? results/program-edge-knockout/verdict_qwen3-14b_heads.json
```

### Tool Call: git (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add scripts/experiments/program_edge_knockout.py results/program-edge-knockout/ && git commit -m \"$(cat <<'EOF'\n💡 s252 head-resolved edge-knockout — object→C route is LAYER-0-concentrated (lead head L0h18) but redundant, not a discrete head circuit\n\n- New mode=heads: per-head edge knockout via per-head additive-mask expansion\n  ([B,1,Q,K]→[B,H,Q,K], -inf at one head's object-key cols) → sever ONLY that\n  head's attention to the object, measure z(C) collapse. 200 (layer,head) pairs\n  across the L0-4 gateway, 20 items.\n- LAYER-0-CONCENTRATED (Qwen3-14B): all 6 significant carriers (t>2) are in L0;\n  L0 holds 67% of positive-drop mass (L1 12%, L4 10%). Sharpens s252 L0-4 → ~L0.\n- LEAD HEAD L0h18 (drop=0.065, t=5.5), ~3× next (L0h11 0.023, t=4.6); top5=49%.\n  The most circuit-like locus in the whole s250 arc.\n- NOT DISCRETE: 21 heads to reach 80% → discrete_head_circuit=false. Dominant\n  head + diffuse redundant tail; single-head drops tiny (0.065) vs all-heads\n  necessity (1.04) → holographic redundancy reconstructs C (s250 echo).\n- NET: a privileged early gateway (L0, h18) exists, but object-application can't\n  be severed by removing a few heads — concentrated-with-redundancy, not a circuit.\n- Artifacts: verdict/meta/run *_heads (0.6b smoke + 14b).\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
  "operation": "commit",
  "summary": "head-knockout code+data"
}
```

**Summary:** Git commit: head-knockout code+data

**Output:**
```
Exit code: 2
Stderr:
bash: -c: line 14: unexpected EOF while looking for matching `''
bash: -c: line 23: syntax error: unexpected end of file
```

### Thinking

Ah, I see the issue now — the apostrophe in "can't" within the commit message is breaking the heredoc syntax. The single-quoted heredoc delimiter expects no quotes inside, so that apostrophe is causing the "unexpected EOF" error.

The safest fix is to remove all apostrophes from the message entirely. I need to rewrite "can't" as "cannot" and replace "head's" with "head" or rephrase those parts to avoid the possessive form. Let me revise the commit message without any apostrophes and try again.

## Assistant

The apostrophes (`head's`, `can't`) broke the heredoc parsing. Retrying without apostrophes.

### Tool Call: git (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add scripts/experiments/program_edge_knockout.py results/program-edge-knockout/ && git commit -m \"$(cat <<'EOF'\n💡 s252 head-resolved edge-knockout — object→C route is LAYER-0-concentrated (lead head L0h18) but redundant, not a discrete head circuit\n\n- New mode=heads: per-head edge knockout via per-head additive-mask expansion\n  ([B,1,Q,K]->[B,H,Q,K], -inf at a single head object-key cols) -> sever ONLY one\n  head attention to the object, measure z(C) collapse. 200 (layer,head) pairs\n  across the L0-4 gateway, 20 items.\n- LAYER-0-CONCENTRATED (Qwen3-14B): all 6 significant carriers (t>2) are in L0;\n  L0 holds 67% of positive-drop mass (L1 12%, L4 10%). Sharpens s252 L0-4 -> ~L0.\n- LEAD HEAD L0h18 (drop=0.065, t=5.5), ~3x next (L0h11 0.023, t=4.6); top5=49%.\n  The most circuit-like locus in the whole s250 arc.\n- NOT DISCRETE: 21 heads to reach 80% -> discrete_head_circuit=false. Dominant\n  head + diffuse redundant tail; single-head drops tiny (0.065) vs all-heads\n  necessity (1.04) -> holographic redundancy reconstructs C (s250 echo).\n- NET: a privileged early gateway (L0, h18) exists, but object-application cannot\n  be severed by removing a few heads — concentrated-with-redundancy, not a circuit.\n- Artifacts: verdict/meta/run *_heads (0.6b smoke + 14b).\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
  "operation": "commit",
  "summary": "head-knockout code+data"
}
```

**Summary:** Git commit: head-knockout code+data

**Output:**
```
Exit code: 0
Stdout:
[main e7d1c09] 💡 s252 head-resolved edge-knockout — object→C route is LAYER-0-concentrated (lead head L0h18) but redundant, not a discrete head circuit
 6 files changed, 2833 insertions(+), 7 deletions(-)
 create mode 100644 results/program-edge-knockout/meta_qwen3-0-6b_heads.json
 create mode 100644 results/program-edge-knockout/meta_qwen3-14b_heads.json
 create mode 100644 results/program-edge-knockout/run_qwen3-14b_heads.log
 create mode 100644 results/program-edge-knockout/verdict_qwen3-0-6b_heads.json
 create mode 100644 results/program-edge-knockout/verdict_qwen3-14b_heads.json
```

### Thinking

I've committed the changes and now I'm updating state.md to record the head-resolved finding. I'll modify the s252 entry to mark the previous task as done and add the new result.

## Assistant

Committed `e7d1c09`. Now updating state.md with the head-resolved continuation.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> (2) redirect (not just block) the object edge to a different key → does C-content follow the redirect\n> (sufficiency at the edge)?; (3) cross-model (Gemma, the s251 cleaner crystal carrier).\n> ──────────────────────────────────────────────────────────────────────────────────────────────────",
  "new_content": "> (2) redirect (not just block) the object edge to a different key → does C-content follow the redirect\n> (sufficiency at the edge)?; (3) cross-model (Gemma, the s251 cleaner crystal carrier).\n>\n> ★★ s252 cont. — HEAD-RESOLVED EDGE KNOCKOUT (the NEXT-(1) above): per-head edge knockout localizes the\n> early object→C route to LAYER 0 with a lead head, but it is CONCENTRATED-WITH-REDUNDANCY, not a discrete\n> head circuit. BUILT mode=heads in program_edge_knockout.py: per-head additive-mask expansion\n> ([B,1,Q,K]→[B,H,Q,K], -inf at ONE head's object-key cols) severs only that head's attention to the\n> object; swept 200 (layer,head) pairs across the L0-4 gateway × 20 items, readout z(C) collapse vs\n> baseline. ★ RESULT (Qwen3-14B): (1) LAYER-0-CONCENTRATED — all 6 significant carrier heads (t>2) are in\n> L0; L0 holds 67% of positive-drop mass (L1 12%, L4 10%, L2-3 ~5%) → sharpens s252 \"L0-4 early\" down to\n> essentially L0 (first attention layer). (2) LEAD HEAD L0h18 (drop=0.065, t=5.5), ~3× the next (L0h11\n> 0.023, t=4.6), then h30/h16/h12/h25; top5 share=0.487. The MOST circuit-like locus in the whole s250\n> arc. (3) NOT DISCRETE — 21 heads to reach 80% → discrete_head_circuit=FALSE; a dominant head + diffuse\n> redundant tail. (4) REDUNDANCY — single-head drops are tiny (max 0.065) vs the all-heads necessity\n> (Δ=1.04, s252 main); severing one head barely dents z(C), the rest reconstruct it (holographic, echoes\n> s250 \"gate reconstructs C from other directions\"), now at head resolution. ★★ NET (λ measure): there IS\n> a privileged early gateway (L0, lead head h18) — a real preferred locus, the closest to a circuit yet —\n> BUT object-application cannot be severed by removing a few heads (redundancy holds). For VERBUM S5 λ\n> types: a preferred locus exists, the discreteness boundary still holds (concentrated, not discrete).\n> CAVEATS: single-head severing is a small perturbation (relative localizer); 20 items (n=20 paired per\n> head); per-head mask expansion (eager); L0-4 band; 1 model; greedy. ARTIFACTS:\n> results/program-edge-knockout/{verdict,meta,run}_qwen3-14b_heads.* (+ 0.6b smoke). COMMITTED e7d1c09\n> (code+data). tmux main:1 FREE; no GPU job. PENDING APPROVAL: memory\n> `object-c-route-layer0-lead-head-redundant-not-discrete` + knowledge update\n> explore/attention-as-beta-reduction.md (§ edge-knockout: head-resolved → L0 lead head + redundancy).\n> state.md updated (¬approval-gated). ★★ NEXT: (2) edge-REDIRECT sufficiency (does C follow the object\n> edge to a new key?); (3) cross-model (Gemma); (4) ablate L0h18 + its OV to test if the lead head is a\n> {B,C}-composer (s127) or a positional/copy head.\n> ──────────────────────────────────────────────────────────────────────────────────────────────────"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

I'm ready to draft the memory and knowledge components for your review before making any commits.

## Assistant

state.md updated. Here are the **approval-gated** mementum drafts for the head-resolved finding (I'll write + commit only on your approval):

---

### 1. Memory — `mementum/memories/object-c-route-layer0-lead-head-redundant-not-discrete.md`

> 💡 The early object→C attention route (s252) localizes to LAYER 0 with a lead head, but is concentrated-with-redundancy — NOT a discrete head circuit.
>
> TEST (program_edge_knockout.py mode=heads, Qwen3-14B): per-head additive-mask expansion ([B,1,Q,K]→[B,H,Q,K], -inf at one head's object-key cols) severs ONLY that head's attention to the object; 200 (layer,head) pairs across the L0-4 gateway × 20 items; readout z(C) collapse.
>
> RESULTS: (1) LAYER-0-CONCENTRATED — all 6 significant carriers (t>2) in L0; L0 holds 67% of positive-drop mass (L1 12%, L4 10%). Sharpens s252 "L0-4 early" → ~L0 (first attention layer). (2) LEAD HEAD L0h18 (drop=0.065, t=5.5), ~3× next (L0h11 0.023, t=4.6); top5=49%. The most circuit-like locus in the whole s250 arc. (3) NOT DISCRETE — 21 heads to reach 80% → discrete_head_circuit=false; dominant head + diffuse redundant tail. (4) REDUNDANCY — single-head drops tiny (0.065) vs all-heads necessity (1.04); severing one head barely dents z(C), the rest reconstruct it (holographic, echoes s250).
>
> NET: a privileged early gateway (L0, h18) exists — a real preferred locus — but object-application cannot be severed by a few heads. For VERBUM λ types: preferred locus yes, discreteness no. Connects s127 ({B,C}=composer heads — L0h18 is the candidate), s250 holographic reconstruction.

Symbol: **💡** (new positive localization).

---

### 2. Knowledge update — `explore/attention-as-beta-reduction.md`

Append a subsection to the existing **§ Edge-knockout** section:
- **"Head-resolved (s252 cont.)"** — records: per-head knockout → L0-concentrated (67% mass, all 6 carriers in L0), lead head **L0h18** (t=5.5), but 21 heads for 80% → concentrated-with-redundancy, not discrete; single-head drops tiny vs all-heads necessity (holographic). Conclusion: the most circuit-like locus found, yet the discreteness boundary holds, sharpened from L0-4 to L0.
- Update that section's **Next** → mark head-resolved done; new next = edge-redirect sufficiency, cross-model (Gemma), and an L0h18 OV-ablation to classify it as a {B,C}-composer (s127) vs a positional/copy head.
- Append `s252 cont.` to **Sessions referenced**.

---

Approve both as-is, or want changes (symbol, wording, scope)?

## User

commit approved


### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/memories/object-c-route-layer0-lead-head-redundant-not-discrete.md",
  "content": "💡 The early object→C attention route (s252) localizes to LAYER 0 with a lead head, but is concentrated-with-redundancy — NOT a discrete head circuit.\n\nTEST (program_edge_knockout.py mode=heads, Qwen3-14B): per-head additive-mask expansion ([B,1,Q,K]→[B,H,Q,K], -inf at one head's object-key cols) severs ONLY that head's attention to the object; 200 (layer,head) pairs across the L0-4 gateway × 20 items; readout z(C) collapse.\n\nRESULTS: (1) LAYER-0-CONCENTRATED — all 6 significant carriers (t>2) in L0; L0 holds 67% of positive-drop mass (L1 12%, L4 10%). Sharpens s252 \"L0-4 early\" → ~L0 (first attention layer). (2) LEAD HEAD L0h18 (drop=0.065, t=5.5), ~3× next (L0h11 0.023, t=4.6); top5=49%. The most circuit-like locus in the whole s250 arc. (3) NOT DISCRETE — 21 heads to reach 80% → discrete_head_circuit=false; dominant head + diffuse redundant tail. (4) REDUNDANCY — single-head drops tiny (0.065) vs all-heads necessity (1.04); severing one head barely dents z(C), the rest reconstruct it (holographic, echoes s250).\n\nNET: a privileged early gateway (L0, h18) exists — a real preferred locus — but object-application cannot be severed by a few heads. For VERBUM λ types: preferred locus yes, discreteness no. Connects s127 ({B,C}=composer heads — L0h18 is the candidate), s250 holographic reconstruction.\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/memories/object-c-route-layer0-lead-head-redundant-not-discrete.md
```

## Assistant

Now the knowledge update — let me read the current end of the edge-knockout section to append precisely.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"head-resolved\\|head-resolved edge sweep at L0-4\\|read-late; the\\|cross-model (Gemma)\\|s252 (attention-edge\" mementum/knowledge/explore/attention-as-beta-reduction.md | head"
}
```

**Summary:** $ grep -n "head-resolved\|head-resolv...

**Output:**
```
Exit code: 0
Stdout:
578:Caveats: all-heads/whole-band severing (coarse, not head-resolved); z(C) readout over KL; 1 model;
579:greedy. **Next:** (1) head-resolved edge sweep at L0-4 (which heads carry the route — the s127
580:{B,C}=composer test); (2) edge-*redirect* (not just block) for sufficiency; (3) cross-model (Gemma).
603:locus), s252 (attention-edge knockout: object→C is a real EARLY (L0-4) object-specific necessary
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/attention-as-beta-reduction.md",
  "original_content": "Caveats: all-heads/whole-band severing (coarse, not head-resolved); z(C) readout over KL; 1 model;\ngreedy. **Next:** (1) head-resolved edge sweep at L0-4 (which heads carry the route — the s127\n{B,C}=composer test); (2) edge-*redirect* (not just block) for sufficiency; (3) cross-model (Gemma).",
  "new_content": "Caveats: all-heads/whole-band severing (coarse, not head-resolved); z(C) readout over KL; 1 model;\ngreedy.\n\n### Head-resolved (s252 cont.) — L0 lead head + redundancy\n\nPer-head edge knockout (`mode=heads`): per-head additive-mask expansion\n([B,1,Q,K]→[B,H,Q,K], -inf at *one* head's object-key columns) severs only that head's\nattention to the object; 200 (layer,head) pairs across the L0-4 gateway × 20 items, readout\nz(C) collapse. **Qwen3-14B:**\n- **Layer-0-concentrated** — all 6 significant carrier heads (t>2) are in **L0**; L0 holds\n  **67%** of positive-drop mass (L1 12%, L4 10%, L2-3 ~5%). Sharpens the \"L0-4 early\" gateway\n  down to essentially **L0** (the first attention layer).\n- **Lead head L0h18** (drop=0.065, t=5.5), ~3× the next (L0h11 0.023, t=4.6), then h30/h16/\n  h12/h25; top-5 share = 0.49. The most circuit-like locus in the whole s250 arc.\n- **Not discrete** — 21 heads to reach 80% → `discrete_head_circuit=false`. A dominant head\n  + a diffuse redundant tail.\n- **Redundancy** — single-head drops are tiny (max 0.065) vs the all-heads necessity (Δ=1.04);\n  severing one head barely dents z(C), the rest reconstruct it — holographic, echoing s250\n  (\"the gate reconstructs C from other directions\"), now at head resolution.\n\n**Conclusion:** a privileged early gateway (L0, lead head h18) exists — a real preferred locus,\nthe closest to a circuit yet — **but object-application cannot be severed by removing a few heads**\n(redundancy holds). For S5 `λ types`: a preferred locus *yes*, the per-object discreteness\nboundary still *holds*, sharpened from L0-4 to L0.\n\n**Next:** (1) edge-*redirect* (not just block) for sufficiency (does C follow the object edge to\na new key?); (2) cross-model (Gemma, the s251 cleaner crystal carrier); (3) ablate **L0h18** + its\nOV to classify it as a {B,C}-composer (s127) vs a positional/copy head."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/attention-as-beta-reduction.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/attention-as-beta-reduction.md",
  "original_content": "read-late). Plus `ffn-reduction-trace.md`,",
  "new_content": "read-late), s252 cont. (head-resolved edge knockout: the early object→C route is L0-concentrated\nwith a lead head L0h18, but concentrated-with-redundancy — 21 heads for 80% — not a discrete head\ncircuit; the most circuit-like locus yet, boundary still holds). Plus `ffn-reduction-trace.md`,"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/attention-as-beta-reduction.md.
```

## Assistant

Both knowledge edits applied. Committing the mementum changes.

### Tool Call: git (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add mementum/ && git status --short && echo \"---\" && git commit -m \"$(cat <<'EOF'\n💡 object-c-route-layer0-lead-head-redundant-not-discrete\n\n- memory: per-head edge knockout localizes the early object→C route to LAYER 0\n  with a lead head (L0h18, t=5.5), but concentrated-with-redundancy (21 heads for\n  80%) — not a discrete head circuit. Most circuit-like locus in the s250 arc;\n  single-head drops tiny (0.065) vs all-heads necessity (1.04) = holographic.\n- knowledge: explore/attention-as-beta-reduction.md § Head-resolved (s252 cont.):\n  L0 lead head + redundancy; Next → redirect/cross-model/L0h18-OV; sessions += s252 cont.\n- state.md: s252 cont. entry (head-resolved, commit e7d1c09, NEXT).\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
  "operation": "commit",
  "summary": "mementum head-resolved finding"
}
```

**Summary:** Git commit: mementum head-resolved finding

**Output:**
```
Exit code: 0
Stdout:
M  mementum/knowledge/explore/attention-as-beta-reduction.md
A  mementum/memories/object-c-route-layer0-lead-head-redundant-not-discrete.md
M  mementum/state.md
---
[main a7877a8] 💡 object-c-route-layer0-lead-head-redundant-not-discrete
 3 files changed, 63 insertions(+), 3 deletions(-)
 create mode 100644 mementum/memories/object-c-route-layer0-lead-head-redundant-not-discrete.md
```

### Thinking

Both commits are in, so I'll wrap up the task list and provide a final summary.

## Assistant

Done. Both commits landed, working tree clean.

## Session wrap — s252 cont. head-resolved edge knockout

**Commits**
- `e7d1c09` — 💡 code+data (new `mode=heads` + per-head mask hook, results)
- `a7877a8` — 💡 mementum (memory + knowledge + state.md)

**The finding (Qwen3-14B)**
Per-head object-edge knockout across the L0-4 gateway (200 layer×head pairs) localizes the early object→C route:
- **Layer-0-concentrated** — all 6 significant carriers (t>2) in **L0**; L0 holds **67%** of drop mass. The "L0-4 early" gateway sharpens to **~L0**.
- **Lead head L0h18** (t=5.5), ~3× the next — the **most circuit-like locus** in the whole s250 arc.
- **But not discrete** — 21 heads to reach 80% (`discrete_head_circuit=false`); dominant head + redundant tail.
- **Holographic redundancy** — single-head drops (0.065) ≪ all-heads necessity (1.04); the rest reconstruct z(C) when one head is cut. Echoes s250 at head resolution.

**The throughline across the whole edge arc**
A genuine causal handle exists where every prior s250 *write*-probe found nothing — the **edge**, object-specific, early (L0), with a lead head (L0h18). Yet at every resolution (direction → subspace → nonlinear → write → edge → head) the **per-object discreteness boundary holds**: object-application is a *preferred-locus-with-redundancy*, not an isolatable circuit. For VERBUM's S5 λ types: **preferred locus yes, discrete circuit no** — sharpened, not overturned.

**State**
tmux main:1 FREE, no GPU job. NEXT recorded: (1) edge-*redirect* sufficiency, (2) cross-model (Gemma), (3) ablate L0h18 + OV to classify it as a {B,C}-composer (s127) vs positional/copy head.

One small note for future sessions: heredoc commits with apostrophes (`head's`, `can't`) break the shell parse — I switched to apostrophe-free messages. Worth remembering.

## User

There is supposed to be a heredoc format template in AGENTS.md that would get around the issue you keep having with apostrophes, can you evaluate AGENTS.md?


### Thinking

Looking at the AGENTS.md file and the system prompt to understand how the heredoc format handles the apostrophe issue. The git tool uses a quoted heredoc delimiter with `<<'EOF'`, which treats the body as literal text without any variable expansion or special character interpretation.

But I'm realizing the real problem: the tool runner itself wraps the entire command in single quotes when passing it to `bash -c`, so any apostrophe anywhere in the command — even safely nested inside a `<<'EOF'` heredoc — will break the outer quoting layer and cause a syntax error. The heredoc format doesn't actually solve this because the issue exists at the wrapper level, not within the heredoc itself.

Let me check if AGENTS.md actually contains guidance on this heredoc pattern or if it's only in the system prompt, and then figure out what the real fix should be — whether that's documenting the limitation or suggesting an alternative like writing the commit message to a file and using `git commit -F`.

## Assistant

Good instinct — let me actually investigate rather than assume. First, check what AGENTS.md says about heredocs, and empirically determine *why* the apostrophe breaks (the heredoc template may be fine but defeated at a different layer).

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && echo \"=== grep AGENTS.md for heredoc/EOF/commit ===\"; grep -niE \"heredoc|<<|EOF|git commit|-F \" AGENTS.md || echo \"(no matches in AGENTS.md)\"; echo; echo \"=== other places that might hold the template ===\"; grep -rniE \"heredoc|<<'EOF'\" --include=\"*.md\" . 2>/dev/null | grep -vi \"node_modules\" | head -20"
}
```

**Summary:** $ echo "=== grep AGENTS.md for heredo...

**Output:**
```
Exit code: 0
Stdout:
=== grep AGENTS.md for heredoc/EOF/commit ===
(no matches in AGENTS.md)

=== other places that might hold the template ===
./mementum/knowledge/chats/session-247b.md:2479:  "command": "cd /Users/mwhitford/src/verbum && python3 - <<'EOF'\nimport json\nfor tag,path in [(\"SINGLE-SHOT\",\"results/proof-inhabitation/google_gemma-4-31B-it.json\"),\n                 (\"REPL\",\"results/proof-repl/google_gemma-4-31B-it.json\")]:\n    d=json.load(open(path))\n    print(f\"\\n=== {tag} :: keys={list(d.keys())}\")\n    for k in (\"sensitivity\",\"specificity\",\"false_proofs\",\"avg_turns\"):\n        if k in d: print(f\"  {k}: {d[k]}\")\n    # try to surface per-task records\n    for kk in (\"tasks\",\"records\",\"results\",\"theorems\",\"details\"):\n        if kk in d and isinstance(d[kk],list):\n            print(f\"  --- {kk} ---\")\n            for r in d[kk]:\n                if isinstance(r,dict):\n                    prop=r.get('prop') or r.get('proposition') or r.get('goal') or r.get('id')\n                    ok=r.get('proved', r.get('correct', r.get('solved')))\n                    term=r.get('term') or r.get('proof') or r.get('answer') or ''\n                    isthm=r.get('is_theorem', r.get('theorem'))\n                    print(f\"    thm={isthm} proved={ok} {str(prop)[:42]:42} -> {str(term)[:30]}\")\n            break\nEOF"
./mementum/knowledge/chats/session-247b.md:2483:**Summary:** $ python3 - <<'EOF' import json for t...
./mementum/knowledge/chats/session-247b.md:5427:  "command": "cd /Users/mwhitford/src/verbum && git commit -m \"$(cat <<'EOF'\n✅ proof consensus: Qwen3-14B × Gemma — continuation removes the agreed-error ceiling\n\n- proof_tasks.py grown 12→35 theorems + 8→13 non-theorems; every ref auto-solved\n  (proof_search.solve) and kernel-certified (check_proof==VALID), zero hand-derivation\n- _gen_proof_tasks.py: authoring aid (propose props → solve → reconstruct → certify)\n- proof_consensus.py: cross-lineage agreement on KERNEL-VERIFIED proofs; re-normalises\n  each term through the kernel (exact α/reduction equality, no token-Jaccard);\n  --source inhabitation|repl; s246 grid + P(both-correct|agree/disagree)\n- result (Qwen3-14B × Gemma): single-shot term-agree 0.375 / P(agree) 0.944 with one\n  real cross-lineage agreed-error (both emit ill-typed `W I` for A→A→A); REPL term-agree\n  0.812 / P(agree) 1.000, agreed-error→0 — the continuation engine's legal-move\n  constraint makes ill-typed shared misconceptions impossible to commit\n- Gemma added to the s228 matrix: strongest single-shot prover (0.75), REPL 1.00,\n  spec 1.0, zero false proofs; consistency firewall now holds across 4 lineages\n- pyproject: per-file RUF001/002/003 ignore for proof_consensus.py surface symbols\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
./mementum/knowledge/chats/session-247b.md:5445:I'm realizing the issue is with the outer command substitution in the git commit — the backticks inside the heredoc are being captured by the `$(...)` wrapper, not by bash's heredoc parsing itself.
./mementum/knowledge/chats/session-247b.md:5447:The simplest solution is to skip the heredoc pattern entirely and write the commit message to a temporary file instead, then use `git commit -F` to read from it, which avoids all the quoting and substitution complications.
./mementum/knowledge/chats/session-239.md:3402:  "command": "git commit -m \"$(cat <<'EOF'\n💡 B native-order is frame-robust at scale, fragile at 8B floor; s237 nested-flip was a depth confound\n\ns239 v5 lead 2d path 1 — kernel_reference_order_cost_v10_frame.py, a clean\nFRAME-swap of v9: --render-frame {applied_to, result_of} open slot. v9's\n\" applied to \" INFIX vs the new \"the result of <f> on <x>\" CIRCUMFIX (flat =\none prefix + leaves chained by \" on \" = pure atom-order under new lexicon).\napplied_to+flat reproduces v9 byte-for-byte (8B smoke t=-0.567).\n\n- (1) FRAME-ROBUST WHERE STRONG, FRAGILE AT FLOOR — B-vs-C atom minpair n=24:\n  14B -8.05->-9.24 ✓ (stronger), 32B -4.48->-11.7 ✓ (stronger),\n  8B -2.87->+0.70 ✗ (floor signal does NOT survive). Frame-robustness is\n  itself SCALE-GATED; order preference is a property of composition, not the\n  \"applied to\" infix.\n- (2) s237 NESTED SIGN-FLIP = pure DEPTH confound — result_of nested 14B B<C\n  atom t=-15.45 ✓ (EQUAL depth) vs s237 applied_to nested +11.9 ✗ (UNEQUAL:\n  B nested, C flat). Equalize depth -> B<C survives nesting.\n- (3) OFF-QWEN single-step sharpening is frame×model-dependent: Gemma-31B-it\n  -0.56 n.s. -> -9.35 ✓ (circumfix unlocks the sharp single-step for the\n  instruct model; OOD caveat); OLMo-13B -1.25 -> +0.73, both n.s. Gross\n  composition (B<C-multi, B<S) holds across ALL models + BOTH frames.\n\nmementum: state s239 head + memory b-native-order-frame-robust-at-scale-\nfragile-at-floor + page vsm-opcode-monitor.md §v5 lead 2d path 1.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
./mementum/knowledge/chats/session-239.md:3420:I'm tracking down a quote mismatch in the heredoc — the single-quoted delimiter is causing the parser to look for a closing quote that doesn't exist in the body, even though I thought I'd removed the problematic apostrophes. I'll simplify the commit message by removing apostrophes to avoid any quoting issues.
./mementum/knowledge/chats/session-239.md:3424:Apostrophe in "v9's" broke the heredoc. Let me retry without apostrophes.
./mementum/knowledge/chats/session-239.md:3431:  "command": "git commit -m \"$(cat <<'EOF'\n💡 B native-order is frame-robust at scale, fragile at 8B floor; s237 nested-flip was a depth confound\n\ns239 v5 lead 2d path 1 — kernel_reference_order_cost_v10_frame.py, a clean\nFRAME-swap of v9: --render-frame {applied_to, result_of} open slot. The v9\n\" applied to \" INFIX vs the new \"the result of <f> on <x>\" CIRCUMFIX (flat =\none prefix + leaves chained by \" on \" = pure atom-order under new lexicon).\napplied_to+flat reproduces v9 byte-for-byte (8B smoke t=-0.567).\n\n- (1) FRAME-ROBUST WHERE STRONG, FRAGILE AT FLOOR — B-vs-C atom minpair n=24:\n  14B -8.05->-9.24 (stronger), 32B -4.48->-11.7 (stronger),\n  8B -2.87->+0.70 (floor signal does NOT survive). Frame-robustness is\n  itself SCALE-GATED; order preference is a property of composition, not the\n  applied-to infix.\n- (2) s237 NESTED SIGN-FLIP = pure DEPTH confound — result_of nested 14B B<C\n  atom t=-15.45 (EQUAL depth) vs s237 applied_to nested +11.9 (UNEQUAL:\n  B nested, C flat). Equalize depth then B<C survives nesting.\n- (3) OFF-QWEN single-step sharpening is frame x model-dependent: Gemma-31B-it\n  -0.56 n.s. -> -9.35 (circumfix unlocks the sharp single-step for the\n  instruct model; OOD caveat); OLMo-13B -1.25 -> +0.73, both n.s. Gross\n  composition (B<C-multi, B<S) holds across ALL models + BOTH frames.\n\nmementum: state s239 head + memory b-native-order-frame-robust-at-scale-\nfragile-at-floor + page vsm-opcode-monitor.md section v5 lead 2d path 1.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
./mementum/knowledge/chats/session-239.md:4046:  "command": "git commit -m \"$(cat <<'EOF'\n💡 Composition-is-native-order is universal across 4 model classes + 2 architectures; gate-independent (proven on non-gated Pythia)\n\ns240 v5 lead 2d path 1 cont. — the Pythia-proper 4th-class point.\nEleutherAI/pythia-2.8b-deduped (rev 7d977fed, flat n=24), applied_to (v9) +\nresult_of (v10). Pythia is NON-gated GPT-NeoX (cannot carry the FFN-gate\ncrystal) but the order-cost read is pure softmax-over-V surprisal (no gate\ncrystal) -> Pythia confirming it proves the signal is GATE-INDEPENDENT and\narchitecture-general, not a Qwen/SwiGLU artifact.\n\n- (1) GROSS holds (applied_to): composite B-vs-C-multi atom t=-9.11; B is the\n  cheapest op atom (1.37 << C 1.77/K 1.57/S 1.75/W 1.62); pooled preserve 1.40\n  << break 1.68; B-vs-W -7.44, D-vs-K -6.0. Composition-is-native-order now\n  Qwen x OLMo x Gemma x Pythia = 4 classes, 2 architectures.\n- (2) strict single-step n.s. (B-vs-C single t=-0.67, dir B<C) like OLMo\n  (-1.25) + Gemma (-0.56): the sharp f-a-b<->f-b-a swap stays Qwen-specific.\n  Wrinkle: B-vs-S single +3.70 (S atoms cheap).\n- (3) FRAME-ROBUSTNESS IS SCALE-GATED NOT CLASS-GATED: Pythia-2.8b (smallest\n  class) frame-fragile under result_of (composite -9.11 -> -1.96) like Qwen-8B.\n\nNo new code (reused v9+v10). mementum: state s240 head + memory\ncomposition-native-order-universal-4-classes-2-architectures + page\nvsm-opcode-monitor.md Pythia rows.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
./mementum/knowledge/chats/session-239.md:7888:  "command": "git commit -m \"$(cat <<'EOF'\n💡 Composition is TYPE-directed, not just positional — frequency-free nonce crossover proves the model uses an in-context type to direct composition\n\ns239 lead 2d (types). Michael: \"the system can't do combinator composition\nwithout some typing — what would direct it?\" Resolves the s236 order-cost\ncaveat: the native-order signal has a TYPE basis, not pure L-to-R copy.\nKernel-certified CCG types as ground truth (lambda_ast typecheck, CSlash\n'/'fwd '\\\\'bwd, _unify). Control: the autoregressive-causality trap (measure\nthe RIGHT token | left, never the pre-functor argument).\n\n- v1 (real words): robust BACKWARD type-licensing (verb cheap after subject-NP,\n  dear after determiner; 8B t=6.9, 14B t=7.1); forward leaky (noun=universal donor).\n- v2 (clean symmetric): backward consistency 1.0 (8B t=10.3, 14B t=5.2); forward\n  unmeasurable (determiners also universal donors); real words frequency-confounded.\n- v3 NONCE crossover (DECISIVE, frequency-free): teach a nonce noun-vs-verb\n  in-context, test det-frame vs name-frame. CROSSOVER=(det:v-n)-(name:v-n) paired\n  by nonce subtracts all main effects. 8B +2.18 (t=10.2), 14B +2.04 (t=9.3),\n  consistency 1.0 (all 16 nonce) both scales; type_directed=True @14B. A nonce\n  taught as VERB composes ~2 nats cheaper after a subject-name than the SAME nonce\n  taught as NOUN — zero frequency support.\n\nVERDICT: composition is TYPE-directed; the model uses an in-context-taught type\nto direct composition. Asymmetry (a finding): strong in the predicate-argument\n(subject->verb) frame, ~null in the determiner->noun frame, across all 3 exps ->\nmaps onto s151 (Montague typed application = predicate(argument) = K+I core).\nCaveats: typed APPLICATION not yet typed COMPOSITION (B); behavioural not causal\n(ablation=v4); 2 scales, 1 family, 16 nonce. Confirms s139 (decodable -> now USED).\n\nmementum: state s239 (arc 3/3) head + memory\ncomposition-is-type-directed-nonce-frequency-free + NEW page\nknowledge/explore/type-directed-composition.md.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
./mementum/knowledge/chats/session-239.md:9285:  "command": "git commit -m \"$(cat <<'EOF'\n💡 The type direction is partially causal at 14B (not 8B) — decodability ≠ full causality, causal localizability strengthens with scale\n\ns239 lead 2d v4 (type_directed_v4_ablation.py) — the causal upgrade of the v3\nnonce crossover. Decode the type direction = diff-of-means(verb-noun) of the\nfiller-position residual (token before nonce = next-token bottleneck), per\nlayer, pick max-AUC L*; ABLATE by projecting it out during the forward pass;\nre-measure the v3 crossover; control = random unit direction. Took 3 scopes\n(one-layer -> filler-stack -> all-positions): one locus too weak because the\nmodel re-reads type from the TEACHING tokens via attention.\n\n- 8B: type AUC 1.0 @hs10; ablation crossover x1.43 (AMPLIFIES, non-causal),\n  random x0.92.\n- 14B: type AUC 1.0 @hs28; ablation crossover x0.64 (-36%, PARTIALLY CAUSAL),\n  random x0.95.\n\nType perfectly DECODABLE both scales (deeper with scale, L10->L28); at 14B the\ntype direction is type-specifically causal (cuts crossover 36% vs random 5%) =\nfirst causal-register evidence the type rep DIRECTS composition; PARTIAL -> rest\ndistributed/redundant (one linear direction != whole carrier); 8B directional\nablation non-causal (amplifies). LESSON (lambda measure, the project's own\ns202/s204 over-read discipline in the type register): a perfectly decodable\nAUC-1.0 direction is only partially the causal lever; directional ablation is a\nweak tool here (8B amplification proves it perturbs not removes); the decisive\ntest is activation PATCHING = v5.\n\nmementum: state s239 head (v1-v4) + memory\ntype-direction-partially-causal-at-14b-decodable-not-fully-causal + page\ntype-directed-composition.md (v4 section).\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
./mementum/knowledge/chats/session-239.md:9303:I need to handle apostrophes in the heredoc string by removing them to avoid syntax issues.
./mementum/knowledge/chats/session-239.md:9307:Apostrophe in "project's" broke the heredoc again. Retrying without apostrophes:
./mementum/knowledge/chats/session-239.md:9314:  "command": "git commit -m \"$(cat <<'EOF'\n💡 The type direction is partially causal at 14B (not 8B) — decodability is not full causality, causal localizability strengthens with scale\n\ns239 lead 2d v4 (type_directed_v4_ablation.py) — the causal upgrade of the v3\nnonce crossover. Decode the type direction = diff-of-means(verb-noun) of the\nfiller-position residual (token before nonce = next-token bottleneck), per\nlayer, pick max-AUC L*; ABLATE by projecting it out during the forward pass;\nre-measure the v3 crossover; control = random unit direction. Took 3 scopes\n(one-layer -> filler-stack -> all-positions): one locus too weak because the\nmodel re-reads type from the TEACHING tokens via attention.\n\n- 8B: type AUC 1.0 @hs10; ablation crossover x1.43 (AMPLIFIES, non-causal),\n  random x0.92.\n- 14B: type AUC 1.0 @hs28; ablation crossover x0.64 (-36%, PARTIALLY CAUSAL),\n  random x0.95.\n\nType perfectly DECODABLE both scales (deeper with scale, L10->L28); at 14B the\ntype direction is type-specifically causal (cuts crossover 36% vs random 5%) =\nfirst causal-register evidence the type rep DIRECTS composition; PARTIAL means\nthe rest is distributed/redundant (one linear direction is not the whole\ncarrier); 8B directional ablation non-causal (amplifies). LESSON (lambda\nmeasure, the s202/s204 over-read discipline in the type register): a perfectly\ndecodable AUC-1.0 direction is only partially the causal lever; directional\nablation is a weak tool here (8B amplification proves it perturbs not removes);\nthe decisive test is activation PATCHING = v5.\n\nmementum: state s239 head (v1-v4) + memory\ntype-direction-partially-causal-at-14b-decodable-not-fully-causal + page\ntype-directed-composition.md (v4 section).\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
./mementum/knowledge/chats/session-229.md:1422:  "command": "cd /Users/mwhitford/src/verbum && git add mementum/knowledge/explore/sentence-atomic-curriculum-mixing.md && git commit -m \"$(cat <<'EOF'\n🌀 sentence-atomic-curriculum-mixing — punctuated β-reduction shards in NTP\n\n- s229 Michael's curriculum idea: 3 regimes (mechanics/prose-usage/NTP),\n  sentence-atomic β-reductions sprinkled into the NTP stream at ratio ρ\n- novel cut vs normal-form-curriculum-partition: by-pedagogy + interleaved\n  (measures transfer) not by-mechanism + isolated\n- core: sentence = 1 reduction = 1 punctuated exposure = the s222\n  punctuate-dont-churn + holographic-burn-in discipline as data structure\n- 4 catches: level-4 scratch path (not s222-unstable); dual-register readout\n  (s225); K-erasure ordering (s221); ρ is the experiment (sweep it)\n- decisive cheap exp: kernel mints data free; ρ=0 control vs sprinkle;\n  metric = held-out compositional generalization + crystallization register\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
./mementum/knowledge/chats/session-229.md:1440:I'm running into quote escaping issues with the heredoc syntax nested inside the git command. The unbalanced quote error suggests the shell wrapper is having trouble parsing the nested quotes. Writing the commit message to a file and using the `-F` flag would be a cleaner approach than trying to escape everything inline.
./mementum/knowledge/chats/session-229.md:1444:Heredoc got mangled by the shell wrapper. Using a message file instead.
./mementum/knowledge/chats/session-089.md:7744:  "command": "git commit -m \"$(cat <<'EOF'\n✅ v11 baseline probes 6K-10K — complete pre-slot trajectory\n\n- 5 new probe results with dispatch detail (6K, 7K, 8K, 9K, 10K)\n- Compute gate: 0.51→0.72 (still climbing, 87% active at 10K)\n- B dispatch flat at 2.4% but B-type integrate at 52% (paradox)\n- Alarm cascade: L0↑(0.62)→L1↑(1.38)→L2(1.71) descending wave\n- CycleContinue dead (0.018) across all 10K steps\n- Dispatch entropy bottomed at 0.17 (strong specialization)\n- Evolution: 3/200 accepted (1.5%)\n- This is the clean baseline before abstraction slot experiment\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
./mementum/knowledge/chats/session-089.md:7804:  "command": "git commit -m \"$(cat <<'EOF'\n✅ v11 baseline probes 6K-10K — complete pre-slot trajectory\n\n- 5 new probe results with dispatch detail (6K, 7K, 8K, 9K, 10K)\n- Compute gate: 0.51→0.72 (still climbing, 87% active at 10K)\n- B dispatch flat at 2.4% but B-type integrate at 52% (paradox)\n- Alarm cascade: L0↑(0.62)→L1↑(1.38)→L2(1.71) descending wave\n- CycleContinue dead (0.018) across all 10K steps\n- Dispatch entropy bottomed at 0.17 (strong specialization)\n- Evolution: 3/200 accepted (1.5%)\n- This is the clean baseline before abstraction slot experiment\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
```

### Thinking

I'm seeing that the AGENTS.md file doesn't actually contain the heredoc template—it only exists in the system prompt as part of the git tool description and nucleus commit convention. This apostrophe issue keeps surfacing across multiple sessions, suggesting it's a persistent pattern rather than an isolated incident.

Looking back at the prior diagnoses, the core problem is that the tool wraps commands in single-quoted bash, so any apostrophe in the commit message—even inside a heredoc—breaks the outer quoting. Previous sessions kept rediscovering this and working around it by either dropping apostrophes or using `git commit -F` with a file instead, but none of these workarounds ever made it into AGENTS.md. This is exactly the feed-forward failure the project warns about: knowledge gets lost at session boundaries because it's never encoded into the persistent documentation.

The robust solution is to write the commit message to a file using the file-writing tool (which bypasses shell quoting entirely), then use `git commit -F` to read from it. I have strong evidence this works from the four prior sessions, but let me run a quick empirical test to confirm the mechanism and validate the fix before proposing the AGENTS.md addition.

## Assistant

Now I have the full picture. Let me confirm the root cause empirically before prescribing a fix (λ assert: runtime ≡ truth).

### Tool Call: shell_command (succeeded)


```json
{
  "command": "printf 'mechanism probe — apostrophe inside <<'\"'\"'EOF'\"'\"' heredoc:\\n'; cat <<'EOF'\nthis line has an apostrophe: can't head's project's\nEOF\necho \"---exit: $?---\""
}
```

**Summary:** $ printf 'mechanism probe — apostroph...

**Output:**
```
Exit code: 0
Stdout:
mechanism probe — apostrophe inside <<'EOF' heredoc:
this line has an apostrophe: can't head's project's
---exit: 0---
```

### Thinking

Ah, so the heredoc with apostrophes works fine when it's a direct command, but fails inside command substitution within double quotes — that's the key difference. The git commit wraps the heredoc in `$(...)` inside a double-quoted string, which changes how the shell parses the quoting.

Let me test whether that exact structure breaks: echoing a command substitution with a heredoc containing apostrophes inside double quotes.

## Assistant

The plain heredoc handled apostrophes fine. So the break is specifically the `"$(cat <<'EOF'...)"` *command-substitution* nesting. Let me isolate that exact structure and the `-F` alternative.

### Tool Call: shell_command (failed)


```json
{
  "command": "echo \"=== TEST A: the exact commit structure with apostrophe ===\"; MSG=\"$(cat <<'EOF'\ntitle line\nbody cannot be severed; the head's route\nEOF\n)\"; echo \"captured: [$MSG]\"; echo \"exit A: $?\""
}
```

**Summary:** $ echo "=== TEST A: the exact commit ...

**Output:**
```
Exit code: 2
Stderr:
bash: -c: line 2: unexpected EOF while looking for matching `''
bash: -c: line 5: syntax error: unexpected end of file
```

### Thinking

I'm seeing that the command substitution syntax `$(cat <<'EOF' ... EOF)` is what causes the issue, whereas a bare heredoc works fine. The key difference is that when bash encounters `$(...)`, it triggers a recursive parse of the content inside, and that re-tokenization is what's breaking the heredoc handling.

The solution is to avoid the command substitution wrapper entirely. Instead of trying to pass the heredoc through `$(...)`, I can write the message directly to a file using a utility function, then pass that file to `git commit -F`. Alternatively, I could use `git commit -F -` with a bare heredoc piped to stdin, which sidesteps the problematic `$()` parsing altogether.

Testing the stdin approach...

## Assistant

Reproduced precisely. **Bare heredoc = safe; heredoc inside `"$(cat <<'EOF'…)"` command-substitution = apostrophes break it.** Now confirm the two fixes that avoid `$()`:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "echo \"=== FIX 1: heredoc piped directly to stdin (no \\$() wrapper) ===\"; cat <<'EOF' | wc -l\ntitle line\nbody cannot be severed; the head's route; project's owl\nEOF\necho \"exit: $?\"; echo; echo \"=== FIX 2: message file via -F (simulated: write file, read it) ===\"; printf '%s\\n' \"title\" \"\" \"body with can't, head's, project's — all literal\" > /tmp/_msgtest.txt; cat /tmp/_msgtest.txt; echo \"exit: $?\"; rm -f /tmp/_msgtest.txt"
}
```

**Summary:** $ echo "=== FIX 1: heredoc piped dire...

**Output:**
```
Exit code: 0
Stdout:
=== FIX 1: heredoc piped directly to stdin (no $() wrapper) ===
       2
exit: 0

=== FIX 2: message file via -F (simulated: write file, read it) ===
title

body with can't, head's, project's — all literal
exit: 0
```

### Thinking

I've confirmed both approaches work: using a bare heredoc to pass the message directly to stdin, and writing the message to a file first before committing. Now I'm looking at the AGENTS.md documentation to see how it currently handles commit and heredoc guidance—it appears there's no existing guidance on this topic.

The heredoc template that does exist is actually in the system prompt, and that template itself is the problematic pattern because it uses command substitution which breaks when apostrophes are in the commit message. This bug has surfaced multiple times across different sessions and been worked around each time without ever being properly documented—a classic case of knowledge that keeps getting lost. The fix should be encoded into AGENTS.md so it doesn't resurface again.

Since the user asked me to evaluate AGENTS.md, I should report these findings and propose adding a commit discipline section to the documentation. AGENTS.md is a top-level identity document for the project, so editing it is a significant meta-change, but the user's request essentially asks for this guidance to be added.

The best place to add this would be in the S3 Control section, right after the existing λ signal(commit) definition, since that's where commit format is already defined. I'll propose a new lambda that documents the safe mechanics for writing commit messages, including the specific pattern that avoids the apostrophe problem and references the sessions where this bug was rediscovered.

The key insight is that writing the message to a file first via a separate tool (avoiding shell quoting entirely) is the most robust approach, with the stdin heredoc as a secondary inline option. Let me present this evaluation and ask for approval to add it to AGENTS.md.

## Assistant

## Evaluation: AGENTS.md and the apostrophe bug

**There is no such template in AGENTS.md.** `grep` confirms AGENTS.md contains zero commit/heredoc/`-F` guidance — the only heredoc template is in the *system prompt* (`git commit -m "$(cat <<'EOF'…)"`), and **that template is the very thing that breaks.**

### Root cause (proven empirically just now)
- A **bare** heredoc with apostrophes → **works** (exit 0).
- The same body inside **`"$(cat <<'EOF'…)"`** → **breaks**: `unexpected EOF while looking for matching '`.

The break is the **`$()` command-substitution layer**, not the heredoc. When bash re-scans inside `$(...)` (under the tool's `bash -c` wrapper), an apostrophe in the body starts a quote-scan looking for a closing `'` that never comes. The `<<'EOF'` quoting protects the *delimiter* but not the command-substitution rescan. So `<<'EOF'` gives a false sense of safety here.

### This is a feed-forward gap, not a new bug
The chat logs show prior-session-me hit and diagnosed this **at least four times** — s229, s239, s247b (and I hit it again today, s252). Each time it was worked around ad hoc ("retry without apostrophes" / "use `-F`") and **never encoded**. That is exactly the failure S5 `λ feed_forward` warns about: *¬encoded → lost(forever)*. Notably, s247b and s229 me *both already concluded* the fix is `git commit -F`.

### The robust fixes (both verified, both avoid `$()`)
1. **`-F` message file (best default):** write the message with `eca__write_file` (no shell layer at all), then `git commit -F /path/msg.txt`. Apostrophes, backticks, `$`, all literal.
2. **stdin heredoc:** `git commit -F - <<'EOF' … EOF` — bare heredoc, no `$()` wrapper. Verified safe with apostrophes.

### Proposed AGENTS.md addition (S3 Control, next to `λ signal(commit)`)

```
λ commit_write(msg). ⊘ git commit -m "$(cat <<'EOF'…)" | apostrophe∈body → $()_rescan_breaks
                    | proved: s229 ∧ s239 ∧ s247b ∧ s252 (rediscovered ≥4× ≡ feed_forward_gap)
                    | cause: $()_command_subst rescans body | ' starts unterminated quote_scan
                    |        | <<'EOF' protects delimiter ¬body_rescan (false_safety)
                    | DEFAULT: write_file(msg→tmp) → git commit -F tmp | ¬shell_quoting(at_all)
                    | ∨ git commit -F - <<'EOF' … EOF | stdin_heredoc ¬$()_wrap
                    | both: apostrophe ∧ backtick ∧ $ ≡ literal | nucleus_tag ∧ symbol preserved
```

This closes the loop: the lesson stops being re-derived every few sessions.

Want me to apply this edit to AGENTS.md? (It's an S5 identity doc, so I'm confirming before touching it.)

## User

There is a specific format you can use in bash that looks like this:
```bash
read -r -d '' CODE << 'EoC' || true\n{{code}}\nEoC\nif [[ '{{repl}}' = 'cljs' ]]; then clj-nrepl-eval -p 9000 \"$CODE\"; else clj-nrepl-eval -p $(cat .nrepl-port) \"$CODE\"; fi
```


### Thinking

The user is showing me a bash pattern for safely reading heredocs into variables using `read -r -d ''` with a null delimiter, which avoids the subshell overhead of command substitution. The `|| true` handles the non-zero exit code that `read` returns when it hits EOF, and quoting the heredoc delimiter ensures the content stays literal without variable expansion.

Testing the pattern with apostrophes...

## Assistant

That's the clean inline pattern — `read -r -d '' VAR <<'EOF'` loads the body into a variable with **no `$()` command-substitution layer** to rescan and choke on apostrophes. Let me verify it empirically with the exact apostrophes that broke earlier.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "read -r -d '' MSG << 'EOF' || true\n💡 title line with apostrophes\nbody cannot be severed; the head's route; project's owl `backtick` $dollar\nEOF\necho \"captured ok, exit gate passed\"; echo \"---\"; printf '%s\\n' \"$MSG\"; echo \"---\"; echo \"len=${#MSG}\""
}
```

**Summary:** $ read -r -d '' MSG << 'EOF' || true ...

**Output:**
```
Exit code: 0
Stdout:
captured ok, exit gate passed
---
💡 title line with apostrophes
body cannot be severed; the head's route; project's owl `backtick` $dollar
---
len=104
```

### Thinking

The heredoc pattern with a quoted delimiter prevents variable expansion and handles special characters cleanly, making it better than using a temporary file since the message stays inline and readable. Verifying that variable expansion within double quotes doesn't trigger a rescan, and exploring alternative approaches like writing to a file or using stdin with the heredoc — then I need to locate the exact anchor point in AGENTS.md where the `λ signal(commit)` block ends so I can insert the commit_write lambda right after it.

## Assistant

Confirmed — `read -r -d '' MSG <<'EOF' || true` handles apostrophes, backticks, **and** `$dollar` all literally (quoted delimiter → no expansion, no `$()` rescan). This is the right default: inline, single invocation, reusable variable.

Let me locate the exact anchor in AGENTS.md (right after `λ signal(commit)` in S3) and encode it.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"single_symbol(leader)\\|λ signal(commit)\\|excluded: 📈\" AGENTS.md"
}
```

**Summary:** $ grep -n "single_symbol(leader)\|λ s...

**Output:**
```
Exit code: 0
Stdout:
212:λ signal(commit).   verbum_symbols ≡ {💡 🔄 🎯 🌀 ❌ ✅ 🔁} | narrow(global_set)
220:                    | excluded: 📈 📉 💰 🏦 (trading-only, ¬verbum)
223:                    | ∀commit → nucleus_tag(trailer) | ∀commit → single_symbol(leader)
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/AGENTS.md",
  "line_offset": 211,
  "limit": 16
}
```

**Summary:** Reading AGENTS.md (211-227)

**Output:**
```
λ signal(commit).   verbum_symbols ≡ {💡 🔄 🎯 🌀 ❌ ✅ 🔁} | narrow(global_set)
                    | 💡 insight   — discovered something new
                    | 🔄 shift     — changed approach or refactored
                    | 🎯 decision  — architectural or strategic choice
                    | 🌀 meta      — recursive / self-referential (AGENTS.md, state.md)
                    | ❌ mistake   — error identified and fixed
                    | ✅ win       — successful outcome, milestone reached
                    | 🔁 pattern   — recurring motif worth naming
                    | excluded: 📈 📉 💰 🏦 (trading-only, ¬verbum)
                    | extend(symbol) iff experiment_demands ∧ existing_insufficient
                    | code_commit: "{symbol} {description}" | memory_commit: "{symbol} {slug}"
                    | ∀commit → nucleus_tag(trailer) | ∀commit → single_symbol(leader)
```

### Research policy (to be developed)


[CONTENT TRUNCATED] Showing lines 212 to 227 of 501 total lines. Use line_offset=227 parameter to read more content.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/AGENTS.md",
  "original_content": "                    | code_commit: \"{symbol} {description}\" | memory_commit: \"{symbol} {slug}\"\n                    | ∀commit → nucleus_tag(trailer) | ∀commit → single_symbol(leader)\n```",
  "new_content": "                    | code_commit: \"{symbol} {description}\" | memory_commit: \"{symbol} {slug}\"\n                    | ∀commit → nucleus_tag(trailer) | ∀commit → single_symbol(leader)\n\nλ commit_write(m).  ⊘ git commit -m \"$(cat <<'EOF'…)\" | apostrophe∈body → $()_rescan_breaks\n                    | cause: $()_command_subst rescans body | ' starts unterminated quote_scan\n                    |        <<'EOF' protects delimiter ¬body_rescan ≡ false_safety\n                    | proved: s229 ∧ s239 ∧ s247b ∧ s252 (rediscovered ≥4× ≡ feed_forward_gap)\n                    | FIX(default): read -r -d '' M << 'EOF' || true … EOF ; git commit -m \"$M\"\n                    | read(¬$()) → var | \"$M\"_expansion ¬reparse | ' ∧ ` ∧ $ ≡ literal(quoted_delim)\n                    | proved_safe: s252 (apostrophe ∧ backtick ∧ dollar literal, len-verified)\n                    | alt: git commit -F file (write_file→-F) ∨ git commit -F - <<'EOF' (stdin,¬$())\n                    | ∀fix: nucleus_tag ∧ leading_symbol preserved | ¬strip_apostrophes(lossy_workaround)\n```"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/AGENTS.md.
```

### Thinking

Let me verify the edit I made and then test the full commit workflow by actually committing AGENTS.md with the new pattern—including apostrophes in the message to demonstrate it works end-to-end.

## Assistant

Let me verify the edit landed correctly, then dogfood the new pattern by committing AGENTS.md with it (with apostrophes, to prove it).

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/AGENTS.md",
  "line_offset": 222,
  "limit": 12
}
```

**Summary:** Reading AGENTS.md (222-234)

**Output:**
```
                    | ∀commit → nucleus_tag(trailer) | ∀commit → single_symbol(leader)

λ commit_write(m).  ⊘ git commit -m "$(cat <<'EOF'…)" | apostrophe∈body → $()_rescan_breaks
                    | cause: $()_command_subst rescans body | ' starts unterminated quote_scan
                    |        <<'EOF' protects delimiter ¬body_rescan ≡ false_safety
                    | proved: s229 ∧ s239 ∧ s247b ∧ s252 (rediscovered ≥4× ≡ feed_forward_gap)
                    | FIX(default): read -r -d '' M << 'EOF' || true … EOF ; git commit -m "$M"
                    | read(¬$()) → var | "$M"_expansion ¬reparse | ' ∧ ` ∧ $ ≡ literal(quoted_delim)
                    | proved_safe: s252 (apostrophe ∧ backtick ∧ dollar literal, len-verified)
                    | alt: git commit -F file (write_file→-F) ∨ git commit -F - <<'EOF' (stdin,¬$())
                    | ∀fix: nucleus_tag ∧ leading_symbol preserved | ¬strip_apostrophes(lossy_workaround)
```

[CONTENT TRUNCATED] Showing lines 223 to 234 of 511 total lines. Use line_offset=234 parameter to read more content.
```

## Assistant

The edit is clean. Now I'll dogfood the new pattern — committing AGENTS.md with apostrophes in the message (the exact thing that broke before).

### Tool Call: git (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add AGENTS.md && read -r -d '' M << 'EOF' || true\n🌀 encode λ commit_write — stop rediscovering the apostrophe-breaks-$()-heredoc bug\n\n- AGENTS.md S3 (next to λ signal): the project's commit template \"$(cat <<'EOF')\"\n  breaks whenever an apostrophe is in the body — the $() command-substitution\n  rescans the body and ' starts an unterminated quote scan; <<'EOF' only protects\n  the delimiter, not the rescan (false safety).\n- This was rediscovered ≥4× (s229, s239, s247b, s252) and never encoded = a\n  textbook feed-forward gap. Now it's a field equation.\n- FIX (default): read -r -d '' M << 'EOF' || true … EOF ; git commit -m \"$M\" —\n  no $() layer, \"$M\" doesn't reparse, so apostrophes/backticks/$ are all literal.\n- This very commit is written with that pattern (note: can't, head's, project's)\n  to prove it. Verified: apostrophe ∧ backtick ∧ dollar survive, len-checked.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\ngit commit -m \"$M\"",
  "operation": "commit",
  "summary": "encode commit_write lambda"
}
```

**Summary:** Git commit: encode commit_write lambda

**Output:**
```
Exit code: 0
Stdout:
[main a24c62f] 🌀 encode λ commit_write — stop rediscovering the apostrophe-breaks-$()-heredoc bug
 1 file changed, 10 insertions(+)
```

### Thinking

I've committed the changes with the new pattern that includes apostrophes in the message body, and it went through successfully. Now I'm double-checking that those apostrophes actually made it into the commit message correctly.

## Assistant

Committed `a24c62f` — and it worked first try, with `can't`, `head's`, `project's` all in the body. Let me confirm the apostrophes survived into the actual commit message:

### Tool Call: git (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git log -1 --format='%B' | grep -nE \"can.t|head.s|project.s|breaks whenever\"",
  "operation": "log",
  "summary": "verify apostrophes preserved"
}
```

**Summary:** Git log: verify apostrophes preserved

**Output:**
```
Exit code: 0
Stdout:
3:- AGENTS.md S3 (next to λ signal): the project's commit template "$(cat <<'EOF')"
4:  breaks whenever an apostrophe is in the body — the $() command-substitution
11:- This very commit is written with that pattern (note: can't, head's, project's)
```

## Assistant

Verified end-to-end. The apostrophes (`project's`, `can't`, `head's`), the backtick-adjacent `$()`, and the literal `<<'EOF'` all survived into the commit message intact.

## Summary

**Your evaluation question answered:** AGENTS.md had **no** such template — the only heredoc template (in the system prompt) is `git commit -m "$(cat <<'EOF'…)"`, which is the *cause* of the bug, not the cure.

**Root cause (proven, not assumed):** the break is the **`$()` command-substitution layer**, not the heredoc. `$()` rescans its body; an apostrophe opens a quote-scan with no close. `<<'EOF'` only protects the *delimiter* — false safety. A bare heredoc, or `read` into a variable, never triggers the rescan.

**The fix you provided — now encoded** as `λ commit_write(m)` in AGENTS.md S3 (next to `λ signal(commit)`):
```
read -r -d '' M << 'EOF' || true
…body with apostrophes, backticks, $ — all literal…
EOF
git commit -m "$M"
```
No `$()`; `"$M"` expands without re-parsing. Verified safe for `'`, `` ` ``, and `$`. Alternatives (`-F file`, `-F - <<'EOF'`) recorded as fallbacks.

**The deeper win:** this was a **feed-forward gap** — the same bug was rediscovered and ad-hoc-worked-around in s229, s239, s247b, and again today (s252), but never written down. It's now a field equation instead of a recurring tax. Committed `a24c62f` (🌀 meta), dogfooded with apostrophes in its own message.

Note: AGENTS.md is a non-mementum S5 identity doc, so this was a normal code-tree commit (no approval gate). tmux main:1 remains free.

## User

update state and knowledge this is session-252


### Thinking

I need to update the state and knowledge files to reflect session-252, particularly the edge-knockout entries and the AGENTS.md work we just completed. The user's request to "update state and knowledge" is approval to commit the mementum, so I can proceed with recording the λ commit_write fix. I need to add an entry to state.md documenting this AGENTS.md work as part of session 252, and decide whether the commit discipline lesson belongs in a knowledge page or memory file — given that AGENTS.md already encodes the field equation, a memory file for grep-ability seems more appropriate, though the user did say "knowledge."

## Assistant

Let me look at the knowledge structure to place the commit_write lesson correctly, and check what's already there for session-252.

### Tool Call: directory_tree (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge",
  "max_depth": 2
}
```

**Summary:** Listing tree: mementum/knowledge

**Output:**
```
/Users/mwhitford/src/verbum/mementum/knowledge
 INDEX.md
 attention-sparsity.md
 audit-meta-pattern.md
 audit-registry.md
 binding-graph-trace.md
 chats
  session-001.md
  session-002.md
  session-003.md
  session-004.md
  session-005.md
  session-006.md
  session-007.md
  session-008.md
  session-009.md
  session-010.md
  session-011.md
  session-012.md
  session-013.md
  session-014.md
  session-015.md
  session-016.md
  session-017.md
  session-018.md
  session-019.md
  session-020.md
  session-021.md
  session-022.md
  session-023.md
  session-024.md
  session-025.md
  session-026.md
  session-027.md
  session-028.md
  session-029.md
  session-030.md
  session-031.md
  session-032.md
  session-033.md
  session-034.md
  session-035.md
  session-036.md
  session-037.md
  session-038.md
  session-039.md
  session-040.md
  session-041.md
  session-042.md
  session-043.md
  session-044.md
  session-045.md
  session-046.md
  session-047.md
  session-048.md
  session-049.md
  session-050.md
  session-051.md
  session-052.md
  session-053.md
  session-054.md
  session-055.md
  session-056.md
  session-057.md
  session-058.md
  session-059.md
  session-060.md
  session-061.md
  session-062.md
  session-063.md
  session-064.md
  session-065.md
  session-066.md
  session-067.md
  session-068.md
  session-069.md
  session-070.md
  session-071.md
  session-072.md
  session-073.md
  session-074.md
  session-075.md
  session-076.md
  session-077.md
  session-078.md
  session-079.md
  session-080.md
  session-081.md
  session-088.md
  session-089.md
  session-090.md
  session-091.md
  session-092-53-codex.md
  session-093.md
  session-094.md
  session-095.md
  session-096.md
  session-097.md
  session-098.md
  session-099.md
  session-100.md
  session-101.md
  session-102.md
  session-103.md
  session-104.md
  session-105.md
  session-106.md
  session-107.md
  session-108.md
  session-109.md
  session-110.md
  session-111.md
  session-112.md
  session-113.md
  session-114.md
  session-115.md
  session-116.md
  session-117.md
  session-118.md
  session-119.md
  session-120.md
  session-121.md
  session-122.md
  session-123.md
  session-125.md
  session-126.md
  session-127.md
  session-128.md
  session-129.md
  session-130.md
  session-131.md
  session-132.md
  session-133.md
  session-134.md
  session-135.md
  session-136.md
  session-137.md
  session-138.md
  session-139.md
  session-140.md
  session-141.md
  session-142.md
  session-143.md
  session-144.md
  session-145.md
  session-146.md
  session-147.md
  session-148.md
  session-149.md
  session-150.md
  session-151.md
  session-152.md
  session-153.md
  session-154.md
  session-155.md
  session-156.md
  session-157.md
  session-158.md
  session-159.md
  session-160.md
  session-161.md
  session-162.md
  session-163.md
  session-164.md
  session-165.md
  session-166.md
  session-167.md
  session-168.md
  session-169.md
  session-170.md
  session-171.md
  session-172.md
  session-173.md
  session-174.md
  session-175.md
  session-176.md
  session-177.md
  session-178.md
  session-179.md
  session-180.md
  session-181.md
  session-182.md
  session-183.md
  session-184.md
  session-185.md
  session-186.md
  session-187.md
  session-188.md
  session-189.md
  session-190.md
  session-191.md
  session-192.md
  session-193.md
  session-194.md
  session-195.md
  session-196.md
  session-197.md
  session-198.md
  session-199.md
  session-200.md
  session-201.md
  session-202.md
  session-203.md
  session-204.md
  session-205.md
  session-206.md
  session-207.md
  session-208.md
  session-209.md
  session-210.md
  session-211.md
  session-212.md
  session-213.md
  session-214.md
  session-215.md
  session-216.md
  session-217.md
  session-218.md
  session-219.md
  session-220.md
  session-221.md
  session-222.md
  session-223.md
  session-224.md
  session-225.md
  session-226.md
  session-227.md
  session-228.md
  session-229.md
  session-230.md
  session-231.md
  session-232.md
  session-233.md
  session-234.md
  session-235.md
  session-236.md
  session-237.md
  session-238.md
  session-239.md
  session-240.md
  session-241.md
  session-242.md
  session-243.md
  session-244.md
  session-245.md
  session-246.md
  session-247.md
  session-247b.md
  session-248.md
  session-249-gpt55.md
  session-250.md
  session-251.md
 combinator-addressing.md
 compilation-pipeline.md
 computed-beam.md
 crystal-laplacian.md
 crystal-multi-tree.md
 crystal-native-architecture.md
 crystal-phi-derivation.md
 crystal-sieve-architecture.md
 crystal-trace-tooling.md
 crystal-universality.md
 crystal-validity-and-fidelity.md
 diffusion-holographic-isomorphism.md
 dimensional-analysis.md
 direct-delta-adjunction.md
 dvd-stamp-topology.md
 error-correction-theory.md
 explore
  5d-crystal-lattice.md
  VERBUM.md
  algedonic-alert.md
  architecture-vs-scale.md
  ascending-arm-training.md
  attention-as-beta-reduction.md
  attention-spiral-finding.md
  basin-projector-results.md
  beam-trace-findings.md
  beamformer-theory.md
  binding-cascade.md
  binding-probe-findings.md
  bios-flash-training.md
  categorical-geometry-probes.md
  combinator-function-shape.md
  combinator-training-beta-reduction.md
  compiler-as-loss.md
  complete-kernel-basis.md
  compression-vs-prediction.md
  compressor-architecture.md
  consensus-delta-folding.md
  consensus-etch-protocol.md
  consensus-evolution.md
  continuations-as-composed-plates.md
  cross-model-output-consensus.md
  crystal-basins.md
  crystal-irreducibility-proof.md
  crystal-native-descent.md
  crystal-seed-theory.md
  crystal-spine-sieve.md
  date-fourier-rotation.md
  delta-plate-lifecycle.md
  dispatch-gradient-death.md
  dispatch-ratio-prior.md
  etcher-vsm.md
  exact-ternary-fitting.md
  ffn-beam-discovery.md
  ffn-beta-reduction-indexing.md
  ffn-hierarchy.md
  ffn-moire-isa.md
  fixed-point-holograms.md
  forcing-vs-discovering.md
  fp-optimization-map.md
  fractal-collapse-compiler-cascade.md
  fractal-stride-bands.md
  full-etch-extraction.md
  function-extraction-system.md
  function-topology-consensus.md
  gradient-trajectory-tomography.md
  gradient-voting.md
  grating-cascade.md
  hologram-crystal-fusion.md
  hologram-extraction.md
  holographic-burn-in-learning-rule.md
  holographic-compression.md
  holographic-error-correction.md
  holographic-inversion.md
  holographic-kernel-separation.md
  holographic-landscape.md
  holographic-memory.md
  holographic-plates.md
  holographic-recording-protocol.md
  holographic-state-machine.md
  holographic-storage.md
  holographic-substrate-prototype.md
  holographic-tomography.md
  identity-as-substrate.md
  kernel-functions.md
  kernel-montague-mapping.md
  kernel-replacement-optimization.md
  kernel-splice-geometry-detector.md
  kernel-training.md
  kibc-32b-validation.md
  lambda-probe-atlas.md
  laser-etcher-design.md
  loom-structure.md
  mmap-continuous-training.md
  moire-training-shortcuts.md
  normal-form-curriculum-partition.md
  optimization-negative-results.md
  output-beamformers.md
  phi-compression-universal.md
  predictive-function-landscape.md
  procrustes-lens-and-crystal-comparison.md
  prompt-as-program.md
  proofs-as-continuations.md
  pythia-160m-combinators.md
  q-rotation-etching.md
  ratio-gradient-quantization.md
  readout-register-reduction-readability.md
  relational-loss-distillation.md
  relational-loss-phi-compression.md
  rope-attention-spiral.md
  s5-crystal-custodian.md
  safetensors-training.md
  sealable-continuation.md
  seed-crystal-design.md
  sentence-atomic-curriculum-mixing.md
  session-001-findings.md
  session-002-findings.md
  session-003-findings.md
  session-004-findings.md
  session-010-findings.md
  session-018.md
  session-019.md
  session-021.md
  session-023.md
  session-024.md
  session-062-probes.md
  session-071-dispatch-decoupling.md
  session-073-vsm-structure.md
  session-075-multi-cycle-dispatch.md
  session-115-microscope.md
  session-127.md
  session-history-049-062.md
  shannon-sieve-trinity.md
  spliced-reward-vsm-kernel.md
  stride-percolation.md
  structured-training.md
  taxonomy-extraction.md
  ternary-descent.md
  topology-magnitude-duality.md
  type-directed-composition.md
  type-probe-qwen3-32b.md
  universal-crystal-scaffold.md
  universal-crystal-transfer.md
  v11-design.md
  v11-kibc-architecture.md
  v12-holographic-capacity.md
  v12-kernel-architecture-v2.md
  v12-run6-design.md
  v12-vsm-evolution.md
  v13-architecture.md
  v13-design.md
  v13-funnel-shape.md
  v15-kernel-architecture.md
  v15-kernel-revert.md
  v4.1-training-trajectory.md
  v6-flip-accumulation.md
  v6.1-training-trajectory.md
  v7-pipeline-architecture.md
  v7.1-sieve-pipeline.md
  v9-architecture-speculation.md
  vsm-lm-architecture.md
  vsm-lm-v3-architecture.md
  vsm-lm-v4-design.md
  vsm-opcode-monitor.md
  vsm-outer-recurrence.md
  vsm-statechart-tensor.md
 extraction-methodology.md
 extraction-sign-accuracy.md
 ffn-circuit-types.md
 ffn-reduction-trace.md
 fibonacci-strides.md
 function-discovery.md
 gradient-zero-map.md
 gtsm-search-space.md
 head-combinator-isa.md
 hologram-reader-vsm.md
 holographic-computer.md
 holographic-error-correction.md
 holographic-etch.md
 holographic-sign-correction.md
 hpe-restoration.md
 l0-characterization.md
 lambda-halt-continuation.md
 lambda-machine.md
 lambda-tracer-diagnostic.md
 manifold-axis-and-topology.md
 mathematical-convergences.md
 mechanism-extraction.md
 mode-semantics.md
 moire-addressing.md
 mspace-gemcutter.md
 opcode-instrument.md
 phi-information-partition.md
 progressive-collapse.md
 project-thesis.md
 psi-evaluation-synthesis.md
 recursion-mirrors.md
 residual-covariance-rank.md
 retrieval-lattice.md
 saliency-aware-sieve.md
 score-matching-compression.md
 session-153-notes.md
 session-222.md
 sign-correction-topology.md
 standing-wave-magnitudes.md
 symbol-isolation.md
 td-oscillation-problem.md
 ternary-compounding.md
 ternary-dual-equation.md
 ternary-plate-extraction.md
 tiny-classifier-ternary.md
 topology-gradient-separation.md
 trace-guided-etching.md
 training-protocols.md
 tsp-trajectory-distillation.md
 two-registers-of-topology.md
 v14-architecture.md
 v15-attention-assessment.md

2 directories, 467 files
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && echo \"=== knowledge mentioning commit/heredoc/tooling/process ===\"; grep -rliE \"heredoc|commit_write|commit message|tooling|process\" mementum/knowledge/ 2>/dev/null | grep -v \"/chats/\" | head; echo \"=== memories mentioning commit/heredoc ===\"; grep -rliE \"heredoc|commit|apostrophe\" mementum/memories/ 2>/dev/null | head"
}
```

**Summary:** $ echo "=== knowledge mentioning comm...

**Output:**
```
Exit code: 0
Stdout:
=== knowledge mentioning commit/heredoc/tooling/process ===
mementum/knowledge/recursion-mirrors.md
mementum/knowledge/crystal-trace-tooling.md
mementum/knowledge/ffn-circuit-types.md
mementum/knowledge/opcode-instrument.md
mementum/knowledge/gtsm-search-space.md
mementum/knowledge/project-thesis.md
mementum/knowledge/dimensional-analysis.md
mementum/knowledge/symbol-isolation.md
mementum/knowledge/lambda-tracer-diagnostic.md
mementum/knowledge/session-222.md
=== memories mentioning commit/heredoc ===
mementum/memories/combinator-fingerprints-are-late-layer.md
mementum/memories/td-flip-interval-gnorm.md
mementum/memories/trace-loss-validated.md
mementum/memories/session-127-meta-analysis.md
mementum/memories/locus-agnostic-fixes-instrument-not-the-8b-confound.md
mementum/memories/universal-retrieval-lattice.md
mementum/memories/two-level-program-architecture.md
mementum/memories/continuation-is-foldability-oracle.md
```

### Thinking

The knowledge base is purely research-focused, so there's no separate process or tooling documentation—that's already captured in AGENTS.md as the canonical operating discipline. The grep results mentioning "commit" are just incidental references in research contexts. For session 252, the knowledge update is the edge-knockout work from the attention exploration, which is already in place.

The user's request to "update state and knowledge" most likely means recording this session's work into state.md, including the commit_write fix that belongs in AGENTS.md. I should add a session-252 entry to state.md documenting the λ commit_write feed-forward fix as a meta/process continuation, since that's the operational work that happened this session. The edge-knockout research knowledge is already current, and AGENTS.md is the proper home for the commit_write lesson—no separate research knowledge page needed. The user's instruction to "update state and knowledge" is explicit approval, so I'll proceed directly. I'm adding a new entry to state.md under session 252 for this meta work on the commit_write pattern, then creating a memory file that captures the apostrophe-heredoc lesson in a grep-recallable format. I'll insert the state entry right after the existing head-resolved block and before the session-251 separator.

## Assistant

The knowledge base is all research science — and the commit_write lesson is operating discipline, whose canonical home is AGENTS.md (already done). So for the mementum layer I'll: (1) add the session-252 meta entry to state.md, and (2) add a grep-recallable memory for the fix. Let me write both.

### Tool Call: edit_file (failed)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> (4) ablate L0h18 + its OV to test if the lead head is a {B,C}-composer (s127) or a positional/copy head.\n> ──────────────────────────────────────────────────────────────────────────────────────────────────",
  "new_content": "> (4) ablate L0h18 + its OV to test if the lead head is a {B,C}-composer (s127) or a positional/copy head.\n>\n> ★★ s252 cont.2 (META) — CLOSED THE COMMIT-WRITE FEED-FORWARD GAP (Michael surfaced it: \"there is\n> supposed to be a heredoc template in AGENTS.md that would get around the apostrophe issue\"). There\n> was NONE — AGENTS.md had no commit/heredoc guidance; the only template (system prompt) is\n> `git commit -m \"$(cat <<'EOF'…)\"` which is the BUG itself. ROOT CAUSE (proven empirically, λ assert,\n> not assumed): a bare heredoc with apostrophes WORKS; the same body inside `\"$(cat <<'EOF'…)\"` BREAKS\n> (`unexpected EOF looking for matching '`). The break is the $() COMMAND-SUBSTITUTION rescan — ' opens\n> an unterminated quote scan; `<<'EOF'` protects only the DELIMITER, not the rescan = false safety. This\n> exact bug was rediscovered ≥4× (s229, s239, s247b, s252) and never encoded = textbook feed-forward gap\n> (S5 λ feed_forward: ¬encoded → lost). FIX (Michael provided the pattern; verified safe for ' ∧ ` ∧ $,\n> len-checked): `read -r -d '' M << 'EOF' || true … EOF ; git commit -m \"$M\"` — read loads the body into\n> a var with NO $() layer; \"$M\" expands without reparse → all literal. Alts: `git commit -F file`\n> (write_file→-F) ∨ `git commit -F - <<'EOF'` (stdin, ¬$()). ENCODED as `λ commit_write(m)` in AGENTS.md\n> S3 (next to λ signal); committed a24c62f (🌀, dogfooded WITH apostrophes in its own message — exit 0,\n> apostrophes verified in git log). The lesson is now a field equation, not a recurring tax. CONNECTS:\n> S5 λ feed_forward (the gap this closes), S3 λ signal(commit) (sibling). No research impact; pure\n> tooling/coordination hygiene. memory `commit-write-apostrophe-heredoc-read-pattern`.\n> ──────────────────────────────────────────────────────────────────────────────────────────────────"
}
```

**Summary:** Editing

**Output:**
```
Original content not found in /Users/mwhitford/src/verbum/mementum/state.md
```

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/memories/commit-write-apostrophe-heredoc-read-pattern.md",
  "content": "🌀 Commit messages: NEVER `git commit -m \"$(cat <<'EOF'…)\"` when the body has an apostrophe. The $() command-substitution rescans the body and ' opens an unterminated quote scan → `bash: unexpected EOF while looking for matching '`. `<<'EOF'` protects only the DELIMITER, not the rescan = false safety.\n\nPROVEN (λ assert, runtime ≡ truth): a BARE heredoc with apostrophes works (exit 0); the SAME body inside `\"$(cat <<'EOF'…)\"` breaks. The break is the $() layer, not the heredoc.\n\nFIX (default, verified safe for ' ∧ ` ∧ $, length-checked):\n  read -r -d '' M << 'EOF' || true\n  {message body — apostrophes/backticks/$ all literal}\n  EOF\n  git commit -m \"$M\"\nread loads the body into a var with NO $() layer; \"$M\" expands without reparse.\n\nALTS: `git commit -F file` (eca__write_file → -F, zero shell quoting) ∨ `git commit -F - <<'EOF'` (stdin heredoc, no $()).\n\nNEVER strip apostrophes (lossy workaround — the old habit). Preserve nucleus tag + leading symbol.\n\nHISTORY: rediscovered ≥4× (s229, s239, s247b, s252) and never encoded = feed-forward gap. Now encoded as `λ commit_write(m)` in AGENTS.md S3 (commit a24c62f). If you are reading this and hit the bug, the field equation already exists — use it, do not re-derive.\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/memories/commit-write-apostrophe-heredoc-read-pattern.md
```

### Thinking

The edit anchor for state.md isn't matching up—the NEXT line wording must be different than expected. I need to search the file directly to find the actual text.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"L0h18\\|positional/copy\\|ablate L0h18\\|s252 cont\" mementum/state.md | head"
}
```

**Summary:** $ grep -n "L0h18\|positional/copy\|ab...

**Output:**
```
Exit code: 0
Stdout:
51:> ★★ s252 cont. — HEAD-RESOLVED EDGE KNOCKOUT (the NEXT-(1) above): per-head edge knockout localizes the
58:> essentially L0 (first attention layer). (2) LEAD HEAD L0h18 (drop=0.065, t=5.5), ~3× the next (L0h11
74:> edge to a new key?); (3) cross-model (Gemma); (4) ablate L0h18 + its OV to test if the lead head is a
75:> {B,C}-composer (s127) or a positional/copy head.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "line_offset": 73,
  "limit": 4
}
```

**Summary:** Reading state.md (73-77)

**Output:**
```
> edge to a new key?); (3) cross-model (Gemma); (4) ablate L0h18 + its OV to test if the lead head is a
> {B,C}-composer (s127) or a positional/copy head.
> ──────────────────────────────────────────────────────────────────────────────────────────────────
> Last updated: 2026-06-24 | Session: 251 (cont. — FROZEN-BASIS GRADIENT TOMOGRAPHY → MATURE-14B →

[CONTENT TRUNCATED] Showing lines 74 to 77 of 6909 total lines. Use line_offset=77 parameter to read more content.
```

### Thinking

I need to adjust my reference to match the actual line wrapping in the source, where that phrase about the composer and positional head spans two lines instead of one.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> {B,C}-composer (s127) or a positional/copy head.\n> ──────────────────────────────────────────────────────────────────────────────────────────────────\n> Last updated: 2026-06-24 | Session: 251 (cont. — FROZEN-BASIS GRADIENT TOMOGRAPHY → MATURE-14B →",
  "new_content": "> {B,C}-composer (s127) or a positional/copy head.\n>\n> ★★ s252 cont.2 (META) — CLOSED THE COMMIT-WRITE FEED-FORWARD GAP (Michael surfaced it: \"there is\n> supposed to be a heredoc template in AGENTS.md that would get around the apostrophe issue\"). There\n> was NONE — AGENTS.md had no commit/heredoc guidance; the only template (system prompt) is\n> `git commit -m \"$(cat <<'EOF'…)\"` which is the BUG itself. ROOT CAUSE (proven empirically, λ assert,\n> not assumed): a bare heredoc with apostrophes WORKS; the same body inside `\"$(cat <<'EOF'…)\"` BREAKS\n> (`unexpected EOF looking for matching '`). The break is the $() COMMAND-SUBSTITUTION rescan — ' opens\n> an unterminated quote scan; `<<'EOF'` protects only the DELIMITER, not the rescan = false safety. This\n> exact bug was rediscovered ≥4× (s229, s239, s247b, s252) and never encoded = textbook feed-forward gap\n> (S5 λ feed_forward: ¬encoded → lost). FIX (Michael provided the pattern; verified safe for ' ∧ ` ∧ $,\n> len-checked): `read -r -d '' M << 'EOF' || true … EOF ; git commit -m \"$M\"` — read loads the body into\n> a var with NO $() layer; \"$M\" expands without reparse → all literal. Alts: `git commit -F file`\n> (write_file→-F) ∨ `git commit -F - <<'EOF'` (stdin, ¬$()). ENCODED as `λ commit_write(m)` in AGENTS.md\n> S3 (next to λ signal); committed a24c62f (🌀, dogfooded WITH apostrophes in its own message — exit 0,\n> apostrophes verified in git log). The lesson is now a field equation, not a recurring tax. CONNECTS:\n> S5 λ feed_forward (the gap this closes), S3 λ signal(commit) (sibling). No research impact; pure\n> tooling/coordination hygiene. memory `commit-write-apostrophe-heredoc-read-pattern`.\n> ──────────────────────────────────────────────────────────────────────────────────────────────────\n> Last updated: 2026-06-24 | Session: 251 (cont. — FROZEN-BASIS GRADIENT TOMOGRAPHY → MATURE-14B →"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

I need to verify the session header is current at the top of the document, which shows "2026-06-25 | Session: 252" — that's correct. Now I'm committing the momentum changes to state and memory.

## Assistant

Now committing the mementum updates — using the `λ commit_write` pattern (dogfooding it).

### Tool Call: git (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add mementum/state.md mementum/memories/commit-write-apostrophe-heredoc-read-pattern.md && read -r -d '' M << 'EOF' || true\n🌀 commit-write-apostrophe-heredoc-read-pattern\n\n- memory: the $() command-substitution rescan breaks `git commit -m \"$(cat <<'EOF')\"`\n  on any apostrophe in the body; fix is `read -r -d '' M << 'EOF' || true … ; commit -m \"$M\"`\n  (no $() layer). Proven safe for ' ` $; rediscovered ≥4× before being encoded.\n- state.md: s252 cont.2 (META) entry — closed the commit-write feed-forward gap;\n  λ commit_write encoded in AGENTS.md (a24c62f), this session = 252.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\ngit commit -m \"$M\"",
  "operation": "commit",
  "summary": "state + commit_write memory"
}
```

**Summary:** Git commit: state + commit_write memory

**Output:**
```
Exit code: 0
Stdout:
[main b54aa59] 🌀 commit-write-apostrophe-heredoc-read-pattern
 2 files changed, 33 insertions(+)
 create mode 100644 mementum/memories/commit-write-apostrophe-heredoc-read-pattern.md
```

### Thinking

Checking the git status and recent commits to verify everything is clean and get a summary of what was just committed.

## Assistant

Committed `b54aa59`. Let me confirm the tree is clean and the session-252 record is complete.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && echo \"=== status ===\"; git status --short; echo \"=== session-252 commits ===\"; git log --oneline -7"
}
```

**Summary:** $ echo "=== status ==="; git status -...

**Output:**
```
Exit code: 0
Stdout:
=== status ===
=== session-252 commits ===
b54aa59 🌀 commit-write-apostrophe-heredoc-read-pattern
a24c62f 🌀 encode λ commit_write — stop rediscovering the apostrophe-breaks-$()-heredoc bug
a7877a8 💡 object-c-route-layer0-lead-head-redundant-not-discrete
e7d1c09 💡 s252 head-resolved edge-knockout — object→C route is LAYER-0-concentrated (lead head L0h18) but redundant, not a discrete head circuit
809c57d 💡 object-edge-necessary-specific-early-not-scaling
8310183 💡 s250 edge-knockout — object→C is a real EARLY attention edge, object-specific, still not per-object discrete
8ebaec3 add session chat logs
```

## Assistant

Done. Working tree clean. Session 252 is fully recorded.

## Session 252 — complete record

**Six commits, three threads:**

| commit | thread |
|--------|--------|
| `8310183` 💡 | edge-knockout code+data — object→C is a real early edge, object-specific, not per-object discrete |
| `809c57d` 💡 | mementum: `object-edge-necessary-specific-early-not-scaling` + knowledge |
| `e7d1c09` 💡 | head-resolved code+data — L0-concentrated, lead head L0h18, redundant |
| `a7877a8` 💡 | mementum: `object-c-route-layer0-lead-head-redundant-not-discrete` + knowledge |
| `a24c62f` 🌀 | AGENTS.md `λ commit_write` — encoded the heredoc fix |
| `b54aa59` 🌀 | mementum: `commit-write-apostrophe-heredoc-read-pattern` + state s252 cont.2 |

**What state.md now holds for s252:**
- **Main** (Session 252 header): attention-edge knockout — necessity ✅ (t=29), object-specific ✅ (t=15), early-gateway L0-4 ✅ (t=12), not-scaling ❌. *Route-early, read-late; first positive locus in the s250 arc.*
- **cont.**: head-resolved → L0-concentrated (67%), lead head L0h18 (t=5.5), but 21 heads for 80% → concentrated-with-redundancy, not a discrete circuit.
- **cont.2 (META)**: closed the commit-write feed-forward gap — `λ commit_write` encoded, the bug rediscovered ≥4× now a field equation.

**Knowledge updated:** `explore/attention-as-beta-reduction.md` — § Edge-knockout + § Head-resolved subsections, Next-lines advanced, sessions += s252 / s252 cont.

**Memories added:** the two research findings + the commit_write tooling lesson.

tmux main:1 free, no GPU job. The standing NEXT for the science: edge-redirect sufficiency, cross-model (Gemma), and the L0h18 OV-ablation to classify the lead head as a {B,C}-composer vs a positional/copy head.