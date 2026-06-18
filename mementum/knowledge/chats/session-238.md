# Let me read the verdict.

## User

orient, this is session-238


### Thinking

I'll start by checking the state.md file to understand the current context.

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
> Last updated: 2026-06-16 | Session: 237 — ▶ OPCODE v5 lead 2d PRONG 2b — the PROSE BRIDGE
> (kills the s236 bare-symbol caveat). Re-ran the order-cost read on the SAME certified
> reduction traces RENDERED AS PROSE, to test whether B's native-order win survives in the
> SEMANTIC register the model actually uses (s233 lesson: the register reads PROSE SEMANTICS
> not CL SYNTAX; bare-symbol surprisal may reflect a generic copy/induction preference for
> source-order atoms rather than composition per se). Built `kernel_reference_order_cost_v9_
> prose.py` — reuses the v8 spine (certified `step_fired` trace → teacher-force "t0 -> ... ->
> tn" → per-step softmax-over-V surprisal → ATOM-only de-confound) but renders each term via a
> DETERMINISTIC, order-faithful renderer (`App(f,x)` → "`<f> applied to <x>`", atoms → fixed
> content words). KEY DESIGN: deterministic render NOT the model decompile gate — the model
> must not choose word order (= the variable under test). **★ THE NESTING CONFOUND (found +
> controlled):** B's normal form NESTS (`f (a b)`) while C's is FLAT (`f b a`); the atom-only
> de-confound strips parens from MEASUREMENT but the bracketing stays in the CONTEXT predicting
> the atoms → B pays a clause-boundary cost unrelated to order. FIX = `--render-mode flat`
> (linearise leaves, NO parens → B and C identical structure, differ ONLY in atom ORDER = the
> pure order test) vs `nested` (faithful, CONFOUNDED). **★★ DECISIVE (the cross-table, λ
> measure two-sided) — B-vs-C atom minpair:** **14B flat t=−8.05 (B<C ✓)** ≈ symbolic v8 −7.02
> (`b_is_native_order=True`; B atom-surprisal 0.23 ≪ C 1.22/K 0.73/W 1.18/S 1.64; all 6
> contrasts B<marked sig −8…−38; pooled preserve 0.24 ≪ break 1.12); **14B NESTED t=+11.9 (B>C,
> REVERSED)** — SAME model + SAME 216 programs, flip the render → FLIP the sign = a DIRECT proof
> nesting confounds the contrast; **8B flat −0.57 n.s.** (dir B<C) ≈ symbolic 8B −0.55 (multi-
> step already sig: B<C-multi −10.6 / B<K −7.5 / B<W −7.6); **8B nested +3.17** (reversed). ✅
> flat prose REPLICATES the symbolic pattern at BOTH scales (14B decisive, 8B directional-n.s.)
> = CONVERGENCE across input modality (symbols ⊗ prose). **★ THE s236 CAVEAT IS KILLED:**
> composition-order preference is real in the SEMANTIC register, NOT a bare-symbol copy artifact.
> **★ REFINED FINDING:** B's normal form carries TWO separable real quantities — atom ORDER
> (preserved → cheap; the native-order result) and structural NESTING (deeper → atoms predicted
> inside fresh clauses cost more, dominates when nesting varies). The order claim REQUIRES
> isolating order from nesting (flat). CAVEATS (λ measure): 1 model class (Qwen);
> deterministic "applied to" frame; flat deliberately discards faithful structure to isolate
> order (nested = its complement). **★ CROSS-MODEL FLAT — DONE (s237 cont., path 1): B-NATIVE-
> ORDER IS UNIVERSAL ACROSS THE Qwen3 SCALE LADDER (8B/14B/32B, all flat n=24).** B-vs-C atom
> minpair: **8B t=−2.87 ✓** (CROSSES at full power — was −0.57 n.s. at n=8 smoke, confirming
> "power-limited not absent"), **14B t=−8.05 ✓** (strongest), **32B t=−4.48 ✓**. ALL three:
> b_is_native_order=True, every one of the 6 contrasts B<marked sig, pooled preserve ≪ break
> (8B atoms B 0.39≪C 1.61; 32B B 0.36≪C 1.23). ★ Unlike the C-locus (s232: shifts with scale),
> the ORDER-COST signal is SCALE-ROBUST — composition rides the native autoregressive order at
> every scale. Not strictly monotone (14B strongest) but all positive+significant.
> **★ CROSS-CLASS FLAT — DONE (s237 cont., path 3): the ORDER PREFERENCE replicates across 3
> MODEL CLASSES, but the STRICT single-step headline is Qwen-SPECIFIC.** OLMo-2-13B + Gemma-4-
> 31B-it (instruct), flat n=24, BOTH b_is_native_order=False on the strict single-step B-vs-C
> atom minpair (OLMo t=−1.25 d=−0.07; Gemma t=−0.56 d=−0.52, n.s.) — the cleanest f-a-b ↔ f-b-a
> swap is near-SYMMETRIC off-Qwen. BUT both STRONGLY confirm B<marked on the COMPOSITE +
> aggregate: B-vs-C-multi OLMo t=−24.4 / Gemma −11.6 (both sig); 4-5/6 contrasts sig B-cheaper;
> pooled-atoms preserve ≪ break in BOTH (OLMo 0.62≪1.08; Gemma 10.2≪14.0, cheaper=True). ⇒ the
> GROSS "composition is the native order" signal is UNIVERSAL (Qwen ⊗ OLMo ⊗ Gemma); its
> SHARPEST single-step expression is family-dependent (Qwen-sharp). CAVEAT: Gemma is INSTRUCT-
> tuned, the synthetic prose is far OOD → huge absolute surprisals (B atoms 9.9 vs Qwen ~0.3),
> noisier read (within-model contrasts still valid). gpt-neox-20b ABANDONED (slow ~48min
> download); pythia-2.8b-deduped cached if a Pythia-proper point is wanted. **★★ FIRST ACTION
> NEXT SESSION — two paths remain:** (1) the s235 OFF-DIAGONAL / proper-Jacobian curvature path
> (literal f∘g coupling — diag-Hessian only captured g'ᵀ(diag)g'); (2) a 3rd render frame
> ("the result of f on x") to confirm flat B<C is frame-robust not "applied to"-specific —
> ALSO would test whether the single-step minpair sharpens off-Qwen under a different frame.
> CODE + RESULTS + mementum COMMITTED. tmux main:1 + main:2 FREE.
>
> (Session: 236 — ▶ OPCODE v5 lead 2d PRONG 2 — the ORDER-COST
> register (is B the NATIVE softmax-over-V order?). Michael (s235): "if B is an ordering of
> operations then maybe it defaults to the order the softmax over all V uses natively?"
> Grounded in ffn-reduction-trace.md: attention executes the FFN-compiled program via softmax
> over V = β-reduction by weighted combination ⇒ softmax-over-V IS the execution order.
> HYPOTHESIS: B has no marked amplitude in ANY register (FFN gate / attn / per-head / gradient
> flat; only faint-rising in curvature s235) because B = COMPOSITION = the model's DEFAULT
> autoregressive order — it rides the native left-to-right copy/induction order for FREE, so
> carries no marked feature. BCKW as the structural rules of logic: B=associativity/COMPOSITION
> (preserves order), C=exchange/PERMUTATION (swaps), K=weakening/DELETION (drops), W=contraction
> (copies); the detectable {C,I,K,Y} BREAK the native order, B RESPECTS it ⇒ B is invisible-as-
> amplitude because it IS the substrate the others deviate from. THE TEST (`kernel_reference_
> order_cost_v8.py`, NO amplitude classifier — pure softmax over V): take a composite CL program,
> get its CERTIFIED reduction trace (`step_fired` → contractum + opcode/step), teacher-force
> "t0 -> t1 -> ... -> tn", read per-step SURPRISAL (mean −log p under LM softmax over V) of each
> contractum. Minimal pairs ("B f a b → f (a b)" order-kept vs "C f a b → f b a" SWAPPED, paired
> by atom-set) + multi-step composites; ATOM-ONLY de-confound (drop parens/length, keep order-
> bearing leaves) = the headline. **★ VERDICT (λ measure, TWO-SIDED — and the FIRST CRISP
> POSITIVE for B in the whole saga):** **(1) ✅✅ DECISIVE at 14B (n_each=24, 216 programs):
> b_is_native_order=True — the clean atom B-vs-C single-step minimal pair d=−1.26, t=−7.02; B
> atom-surprisal 0.81 ≪ C 2.14 / S 2.66 / W 2.71; B cheaper than EVERY permute/copy combinator
> (B<S t=−11.3, B<C-multi t=−11.7, B<W t=−14.5); pooled order-preserving<breaking BOTH metrics
> (atoms Δ=−1.06, full Δ=−0.52).** **(2) ⚠️ POWER-LIMITED at 8B smoke (n=8): same DIRECTION but
> the headline B<C atom minpair n.s. (t=−0.55); the multi-step/aggregate contrasts already sig
> (B<C-multi t=−4.22, B<S −5.31, B<W −11.1).** Crisp only at full power on 14B — the entire
> B-saga pattern (real-but-faint, n-limited) resolving once n is raised. (3) D≈K once deletion-
> length de-confounded (atom D−K t=−1.22 n.s.); K=deletion stays cheapest (short predictable
> contractum — taxonomy wrinkle, not order). **★ THE RESOLUTION OF THE B GAP:** B's amplitude-
> absence everywhere (s234: FFN gate flat, attn flat, per-head faintest, gradient faint) is NOT
> diffuseness/weakness — composition is the FREE autoregressive default, so it carries no marked
> amplitude feature; the instrument was looking for a marked signal where B is the UNMARKED
> baseline. **★ UNIFIES with s235:** composition has TWO faces — token-side it's the native
> order (cheap surprisal HERE, t=−7.02) and gradient-side it's the product/2nd-order (curvature
> climb t=1.90). B = the chain rule (gradient) AND the native order (forward). Both confirmed.
> CAVEATS (λ measure, load-bearing): (a) BARE SYMBOLIC CL input — cf s233 lead 2, the ROUTING
> register reads prose-semantics not CL syntax; this is a DIFFERENT read (surprisal/teacher-
> forcing not routing), but bare-symbol surprisal may partly reflect a generic copy/induction-
> head preference for source-order atoms rather than "composition" per se (which IS the proposed
> mechanism — B rides copy/induction order); (b) 14B decisive at full power, 8B directional only,
> 0.6B too small — 1 model class (Qwen), cross-scale only 2 points; (c) K-deletion length
> wrinkle in the pooled metric; (d) single-combinator + within-program contrasts. **★★ FIRST
> ACTION NEXT SESSION — three paths (B is now POSITIVE in TWO registers: order + curvature):**
> (1) CROSS-MODEL — replicate the 14B order-cost win on 8B at full n (does the headline cross
> when 8B gets n=24 too?) + 32B → is B-native-order universal or 14B-specific (cf s232 C-locus
> shifts with scale); (2) PROSE bridge for order-cost — render the certified traces as PROSE
> (lambda_gen decompile) and re-read surprisal, killing the bare-symbol caveat (the s233 lesson:
> feed prose not symbols); (3) the s235 OFF-DIAGONAL/proper-Jacobian curvature path (the literal
> f∘g coupling) — close BOTH faces of composition at fidelity. CODE COMMITTED (`5d6bdeb` code+
> smoke, `1e448e4` 14B decisive); mementum (state + memory `b-is-native-softmax-order` + page
> §v5 lead 2d prong 2) committed `ebaccde`. tmux main:1 FREE.)
>
> (Session: 235 — ▶ OPCODE v5 lead 2d PRONG 1c-ii — the
> SECOND-ORDER / CURVATURE register (the PROPER test of B=chain-rule; Michael s235: "proceed
> with 1"). Prong 1c read the FIRST-ORDER gradient (faint +1.07 n.s.) but the first-order
> gradient is a SINGLE factor / sum-over-paths — it washes out the PRODUCT structure that IS
> the chain rule. B=composition=chain-rule = product of derivatives = a SECOND-ORDER quantity
> (d²L/dz² carries g'ᵀ[f''·]g' — a quadratic form in g', the literal product-of-derivatives).
> Clean register-swap of v6 (`kernel_reference_jacobian_v7.py`, Qwen3-14B, ~9min main:1):
> same RelationalCrystalClassifier (sign-CMR, crosstask null, raw-z Welch), feature = the
> DIAGONAL HESSIAN of the probe LM-CE w.r.t. gate_proj, Hutchinson est (diag(H)_a=E_v[v_a(Hv)_a],
> v~Rademacher; double-backward of g·v, g=grad(CE,gates,create_graph=True)), pooled over
> supervised positions, n_hutch=4. **★ VERDICT (λ measure, THREE-sided):**
> **(1) ❌ STRICT: B does NOT reach significance in curvature either (discr_z +0.118, t=1.90
> < 2.0) — chain-rule NOT confirmed at the bar; the B gap survives into the second order.**
> **(2) ✅ DIRECTIONAL — the MONOTONIC CLIMB WITH DERIVATIVE ORDER, exactly as chain-rule
> predicts:** B activation(v2) t=−0.05 → first-order gradient(v6) t=+1.07 → second-order
> curvature(v7) **t=+1.90** (on +0.045 > off −0.073). B is at its strongest EVER, in the
> PREDICTED register, sitting right on the 2.0 threshold — power-limited (n=20/comb), not
> absent. **(3) ✅✅ INTERNAL-CONSISTENCY (the structural win — the curvature register
> reweights combinators EXACTLY as the math demands):** **I (identity = LINEAR, Ix=x → zero
> curvature) COLLAPSES** to t=0.68 (was activation 3.83 / gradient 1.02 / curvature 0.68 —
> monotone DOWN, the mirror image of B); **Y (recursion = self-application = inherently
> higher-order) DOMINATES** t=4.527; composers {B,C} hold/rise (C t=2.52 ✓, B 1.90↑),
> selectors {K,I} fade (K 1.94 borderline, I 0.68). The second-order register preferentially
> carries COMPOSITION/RECURSION structure (s127 {B,C}=composers) and SHEDS the linear
> combinator. Instrument WORKS (C ✓, Y ✓). Curvature set {C,Y} (K/B at the bar). **★ The two
> opposite monotones (B↑ with order, I↓ with order) are the signature: derivative order is a
> real axis the combinators sort along, and B sorts UP it.** CAVEATS (λ measure): 1 model
> (14B), n=20/comb (B sits ON the bar — power-limited), n_hutch=4 (diag-Hessian Hutchinson
> noise), DIAGONAL Hessian only (off-diagonal/interlayer-Jacobian cross-coupling — the literal
> f∘g coupling — UNTESTED), single-combinator labels, pooled-supervised locus. **★★ FIRST
> ACTION NEXT SESSION — three live paths (B is ON the threshold in the right register):**
> (1) POWER — raise n (more held-out prose/comb) and/or n_hutch (sharper diag) — does B's
> t=1.90 cross 2.0? cheapest decisive test, trend+theory strongly motivate; (2) OFF-DIAGONAL
> / proper Jacobian — diag-Hessian captures only g'ᵀ(diag)g'; the literal f∘g product-coupling
> lives in the OFF-DIAGONAL cross-coord Hessian / interlayer Jacobian dgate_late/dgate_early
> (Gauss-Newton or JVP probe) = next fidelity order; (3) PRONG 2 = composite trace-ORDER
> bridge (B as sequence not amplitude), design fork still pending. CODE COMMITTED; mementum
> (state + memory `b-climbs-with-derivative-order` + page §v5 lead 2d prong 1c-ii) PENDING
> APPROVAL. tmux main:1 FREE.)
>
> (Session: 234 — ▶ OPCODE v5 lead 2d PRONGS 1 → 1b → 1b-ii →
> 1b-iii → 1c (the B gap, chased across activation registers AND the gradient). PRONG 1c —
> the GRADIENT register (Michael: "could B be in the gradients instead of the topology?";
> `kernel_reference_gradient_v6.py`, Qwen3-14B, 1:57 main:1). Rationale: B=composition
> (Bfgx=f(gx)); in the BACKWARD pass composition IS the chain rule (product of derivatives),
> so B's home may be the gradient. Clean register-swap of prong 1: same classifier, feature
> = ∂(probe LM loss)/∂(gate) MEAN-POOLED over supervised positions (last-token grad=0;
> gd_gradient_shadow pattern). **★ VERDICT: ❌ B does NOT discriminate in the gradient
> (discr_z +0.13, t=1.07 n.s.) — chain-rule NOT supported (first-order); ✅ instrument WORKS
> (gradient {C,K,Y} discriminate: C t=2.27, K 2.88, Y 3.87) — C-yes/B-no PERSISTS into the
> backward pass.** ⚠️ BUT directionally B is its LEAST-absent: activation(v2) t=−0.05 →
> gradient t=+1.07 (on_z −0.03 > off −0.16), B's first POSITIVE signal, predicted direction,
> power-limited n.s. Register shifts: S flips gauge→ANTI (t=−2.01); I drops (3.83→1.02);
> gradient set {C,K,Y} (vs activation {C,I,K,Y}). **★ MEASUREMENT CAVEAT (λ measure, load-
> bearing): this measures B in the FIRST-ORDER gradient (centroid in gradient space), NOT
> the chain-rule/Jacobian composition structure (= product of derivatives = SECOND-order).**
> **★★ FIRST ACTION NEXT SESSION — two live paths for B (pick one):** (1) PRONG 1c-ii =
> the JACOBIAN / second-order probe — the PROPER test of B=chain-rule (the faint +trend +
> theory motivate it; first-order gradient centroid is the wrong order); (2) PRONG 2 =
> composite trace-ORDER bridge (B as sequence not amplitude) — DESIGN FORK still pending
> (Path A β-reduction-order via lambda_gen decompiled prose vs Path B concatenated validated
> crystal-prose, span-recall + Kendall-tau order vs shuffle null). WHERE B STANDS: FFN gate
> flat, attn-summed flat, per-head faintest, first-order gradient faint-positive-n.s. CAVEATS
> (λ measure): 1 model (14B), n=20/comb, pooled-supervised locus, single-combinator labels,
> first-order only. CODE COMMITTED; mementum (page §v5 lead 2d prong 1c + memory
> `b-not-clearly-in-first-order-gradient` + this state) PENDING APPROVAL. tmux main:1 FREE.)
>
> (Session: 234 — ▶ OPCODE v5 lead 2d PRONGS 1 → 1b → 1b-ii →
> 1b-iii (the B/D/W gap, fully chased across registers). PRONG 1b-iii — the PER-HEAD OV
> scan (`kernel_reference_perhead_v5.py`, Qwen3-14B, 0:57 main:1): o_proj OUTPUT sums heads,
> so a single B-composer head could be averaged away → hook o_proj INPUT, split per
> (layer,head) cell, calibrate the crystal per cell (treat each cell as a "layer"), scan B's
> raw-z Welch contrast across all 1600 cells (40L×40H), Bonferroni-ish t>4. **★ VERDICT:
> ⚠️ HEAD-DILUTION ONLY MARGINAL — B is the WEAKEST combinator at every granularity.** The
> per-head scan DOES recover a FAINT B signal the summed read missed (B max_t 5.31 @ cell
> (L17,H23), 7/1600 cells; vs o_proj-summed max t=0.49 n.s.), so summing washes out a weak
> per-head B signal. BUT B is DEAD LAST on all 3 metrics — n_sig(t>4): Y 526, C 155, K 56,
> W 24, S 22, I 19, D 8, **B 7** (below D, an anti combinator); max_t **5.31** (lowest);
> best discr_z **0.82** (lowest). No clean B-composer head; C has 155 STRONG heads (best
> L21H36 t=7.52). ⇒ B's attention representation is genuinely FAINT/DIFFUSE, NOT merely
> diluted. **B has now been tested at EVERY granularity — FFN gate (flat), attn-summed
> (flat), per-head OV (faintest of all) — the REGISTER hypothesis is FULLY EXHAUSTED.**
> **★★ FIRST ACTION NEXT SESSION — lead 2d PRONG 2 (composite trace-order bridge, the sole
> remaining path):** B's near-absence is now most likely a NO-SINGLE-TOKEN-SIGNATURE
> property — B (deep composition Bfgx=f(gx)) may live in the SEQUENCE/ORDER of operations,
> not a localized amplitude. DESIGN FORK (raised, pending): Path A (β-reduction order via
> lambda_gen LLM-decompiled prose → align to certified `fired_sequence`; faithful but heavy/
> ill-posed surface↔reduction alignment) vs Path B (composite-sequence order: concatenate
> VALIDATED single-combinator crystal prose in known order, test span-recall + order-
> preservation Kendall-tau vs shuffle null + B-in-context; robust, well-posed, weaker claim).
> Serves {C,I,K,Y} AND tests whether B appears as ORDER not amplitude. CAVEATS (λ measure):
> 1 model (14B), n_sig 7(B)/8(D) maybe partly MC noise/heavy-tailed z, ppc=20 capped calib,
> single-combinator labels, last-token. CODE COMMITTED; mementum (page §v5 lead 2d prong
> 1b-iii + memory `b-faint-at-every-granularity-not-diluted` + this state) PENDING APPROVAL.
> tmux main:1 FREE.
>
> (Session: 234 — ▶ OPCODE v5 lead 2d PRONGS 1 + 1b + 1b-ii
> (the B/D/W gap, fully chased). PRONG 1b-ii — the VALUE-REGISTER read
> (`kernel_reference_prose_v4.py`, Qwen3-14B, 1:35 main:1): parametrized the reader with an
> open-slot `hook` param (opcode_monitor_v2) — `hook='gate'` (mlp.gate_proj, FFN, default)
> vs `hook='attn'` (self_attn.o_proj = attention's residual write) — and re-ran the
> per-token raw-z contrast in the ATTENTION/value register, where s127 ({B,C}=composers→
> attention) predicts B lives. **★ VERDICT: ❌ s127 "B→attention" NOT confirmed — B is FLAT
> in attention TOO** (attn max t=0.49 n.s. vs gate max t=0.68 n.s.; attn profile delta ~0
> all bins). Having tested the TWO main registers, the "wrong register" explanation for B is
> RULED OUT. **★ THE FINDING: discriminability is a COMBINATOR property, NOT a register
> split** — {C,I,K,Y} are REGISTER-ROBUST (discriminable in BOTH gate AND attn: C gate
> t=5.6/attn 6.5; I 4.5/4.1; K 3.3/3.3; Y 8.4/9.4), B/D/W absent-or-anti in BOTH (D gate
> −2.7/attn −1.8; W −3.4/−4.8). The s127 two-group register separation is NOT reflected in
> this single-combinator last-token readout. **B's absence is now register-exhausted; two
> live explanations:** (1) HEAD DILUTION — o_proj SUMS heads, a single B-composer head
> could average away → per-HEAD OV read (prong 1b-iii); (2) NO SINGLE-TOKEN SIGNATURE — B
> (deep composition Bfgx=f(gx)) may exist only as multi-combinator ORDER across tokens →
> the composite trace-order bridge (prong 2). **★★ FIRST ACTION NEXT SESSION — lead 2d
> PRONG 2 (composite trace-order bridge, the MAIN PATH; per-head OV = optional 1b-iii):**
> CL program → certified trace (`fired_sequence`, DONE) → render PROSE (`lambda_gen`
> decompile) → align routing to the certified multi-combinator ORDER, raw-z contrast as the
> read; this serves {C,I,K,Y} AND tests whether B appears as ORDER not amplitude. CAVEATS
> (λ measure): 1 model (14B), n=20/comb, o_proj head-SUMMED (per-head untested), single-
> combinator labels, D/W anti unexplained. CODE COMMITTED; mementum (page §v5 lead 2d prong
> 1b-ii + memory `discriminability-is-combinator-not-register` + this state) PENDING
> APPROVAL. tmux main:1 FREE.
>
> (Session: 234 — ▶ OPCODE v5 lead 2d PRONGS 1 + 1b (the B/D/W
> gap). PRONG 1b (per-token B LOCUS test, `kernel_reference_prose_v3.py`, Qwen3-14B, 2:24
> main:1): reads ALL token positions (free — forward_all_positions already returns [T,d]),
> contrasts last/max/mean over tokens (Welch t) + relative-position profile, to decide
> between (i) TOKEN-LOCUS (B fires mid-sentence) vs (ii) REGISTER (B in attention/value per
> s127, invisible to the FFN gate). **★ VERDICT: ❌ TOKEN-LOCUS FALSIFIED — B does NOT
> recover at ANY position** (last t=−0.05, max t=0.68 n.s. [most lenient], mean t=−0.08);
> position profile B on−off delta ~0 across all 10 bins (max +0.33), never the clean C
> separation; D/W anti everywhere (D max t=−2.66, W max t=−3.40). ⇒ **B/D/W absence is a
> REGISTER property of the FFN gate, not token-locus.** ✅ {C,I,K,Y} ROBUST to the read
> (last/max/mean all sig) with characteristic position signatures (peak_rel: I early 0.30,
> K mid 0.48, C mid-late 0.57, Y late 0.79); C's on−off delta +0.8…+2.0 across the whole
> back half. ⚠️ S "discriminates" ONLY under mean-over-tokens (gauge integrated over the
> sentence). **★★ FIRST ACTION NEXT SESSION — lead 2d prong 1b-ii (the value-register read,
> the decisive C-yes/B-no resolver):** B is absent from the FFN gate at every token, so per
> s127 ({B,C}=composers→attention) hook `o_proj` / attention output, build per-layer crystal
> centroids in THAT register, run the raw-z contrast — does B appear in attention where the
> FFN gate cannot see it? THEN prong 2 (composite trace-order bridge for {C,I,K,Y}) +
> prong 3 (8B/32B sweep). CAVEATS (λ measure): 1 model (14B), n=20/comb, last/max/mean over
> tokens (register untested), single-combinator labels, D/W anti unexplained. CODE COMMITTED;
> mementum (page §v5 lead 2d prong 1b + memory `bdw-absence-is-register-not-token-locus` +
> this state) PENDING APPROVAL. tmux main:1 FREE.
>
> (Session: 234 — ▶ OPCODE v5 lead 2d PRONG 1 (the B/D/W gap).
> Pushed lead-2c's discriminability ONE LEVEL DEEPER: it still embedded a per-layer ARGMAX
> (route_frac = fraction of layers an op WINS) before the contrast, starving B/D/W of power.
> FIX = contrast the RAW per-op z per layer, NO argmax, Welch t-test, n=20/comb held-out +
> per-layer profile (`kernel_reference_prose_v2.py`, Qwen3-14B, 2:17 in main:1).
> **★ TWO-SIDED VERDICT:** (1) ✅ the argmax bottleneck WAS real — raw-z RESCUES **K**
> (discr_z +1.01, t=2.12; was sub-threshold) + sharpens **C/I** hugely (C +1.73 t=5.71,
> I +1.89 t=3.83); AND it's MORE CONSERVATIVE — kills a B FALSE-POSITIVE that argmax-discr
> manufactures at n=20 (B argmax +0.079>0.05 "specific", but raw-z B FLAT on 0.217≈off 0.236
> t=−0.05). ⇒ raw-z Welch > argmax route-frac: more power AND fewer false positives (same
> argmax-manufactures-false-* theme, deeper). (2) ❌ **B/D/W do NOT recover — the gap is
> GENUINE at the last-token locus:** B flat; **D,W significantly ANTI-correlated** (D −0.67
> t=−4.6, W −0.63 t=−2.3 — their own prose routes them LESS than baseline). Discriminable
> set = **{C, I, K, Y}**. **★ GAUGE REFINED:** S = pure gauge (on 2.70≈off 2.97, discr
> −0.27, zero selectivity); **Y = genuinely selective** (on 2.97 vs off 0.96, +2.01 t=6.86).
> **★ WHERE:** discriminable ops peak in the **mid-stack readable zone** L12-14 — C@L13
> Δ3.70, I@L13, Y@L14, K@L12; **B has NO readable-zone signal** (only an early L1 wash that
> vanishes on averaging; D@L3, W@L0 = noise-floor). **★ THEORY (s127 ffn-two-groups:
> {K,I}=selectors→FFN, {B,C}=composers→attention):** we read the FFN GATE → K,I,C
> discriminable but **B not** ⇒ C leaks into the FFN gate, B does NOT; **B likely lives in
> ATTENTION** (s206 OV/value register), which a last-token FFN-gate read structurally cannot
> see → B's absence is plausibly a **LOCUS artifact**, not "B isn't computed."
> **★★ FIRST ACTION NEXT SESSION — lead 2d prong 1b (the B locus test, the clean C-yes/B-no
> resolver):** re-read **B in the attention/value register** (s206 OV/logit-lens, NOT attn
> weights) and/or **per-token** (not last-token) — does B recover where s127 says it lives?
> THEN **prong 2** (composite trace-order bridge, now justified for {C,I,K,Y}: CL program →
> certified `fired_sequence` → render PROSE via `lambda_gen` → align routing to the certified
> multi-combinator ORDER, using the raw-z contrast) and **prong 3** (per-model sweep 8B/32B
> with `kernel_reference_prose_v2.py`). CAVEATS (λ measure): 1 model (14B), n=20/comb,
> last-token locus (load-bearing for B), single-combinator labels, D/W anti-signal
> unexplained. CODE COMMITTED; mementum (page §v5 lead 2d prong 1 + memory
> `bdw-gap-genuine-not-argmax-artifact` + this state) PENDING APPROVAL. tmux main:1 FREE.
>
> (Session: 233 — ▶ OPCODE v5 (leads 1→2c) — the compositional
> opcode signal is REAL but FAINT-against-common-mode and LOCUS-SHIFTS-with-scale; every
> "negative" this session was an INSTRUMENT flaw (wrong place → wrong input language →
> wrong metric), each diagnosed + fixed. ALL COMMITTED (`1754424` `1532e4e` `53ed331`
> `dd6c511` + mementum); working tree clean. Full per-lead detail in
> `knowledge/explore/vsm-opcode-monitor.md` §v5 lead 1/2/2b/2c (+ below) and 4 memories.
> **THE ARC:**
> • **lead 1 — locus-agnostic C detector** (`1754424`, re-analysis no GPU): the fixed
>   depth≥0.6 zone was the WRONG cross-model instrument; `detect_c_profile` +
>   `locus_agnostic_specificity` (count C-dominant crystal layers ANYWHERE + per-model
>   locus). Surfaces the 32B lambda-EXCLUSIVE C-EARLY signal (L5,10,11) the zone read as 0.
>   But strict frac-specificity still only 14B; 8B's `gate_neutral` C-late confound CONFIRMED
>   REAL (control routes C 0.192 > lambda 0.107). C-locus shifts with scale.
> • **lead 2 — kernel-as-reference** (`1532e4e`): built the model-invariant —
>   `lambda_ast.step_fired`/`fired_sequence` (certified per-step opcode trace, +6 pytest),
>   `probes/kernel_reference.py` (symbolic programs, SAT⊗INERT + composites),
>   `kernel_reference_audit.py`. ❌ DECISIVE NEGATIVE: bare symbolic CL routes ONLY S-gauge
>   (target_recall 1/7; reducibility not tracked) ⇒ the register reads PROSE SEMANTICS, not
>   CL SYNTAX. Instrument sound, bridge must be compiled prose.
> • **lead 2b — prose bridge** (`53ed331`): `calibrate_v2(centroid_probes=)` held-out split;
>   `kernel_reference_prose.py`. ✅ held-out PROSE recall 0.575 ≫ bare-symbol 0.14 ⇒ register
>   IS prose-semantic. ⚠️ but argmax-winner specificity gauge-dominated (S/Y win).
> • **lead 2c — gauge-subtracted discriminability** (`dd6c511`): discr(c)=route_frac(c|c-prose)
>   − route_frac(c|other-prose) replaces argmax-winner. ✅ RESCUE: C discriminable (on/off
>   0.062/0.009 ~6.6×, argmax_spec was 0.0) + I. ⚠️ PARTIAL: B/K/D/W NOT discriminable
>   (compose family SPLITS — C yes, B no, cf s127 {B,C}); S/Y stay discriminable = large
>   common-mode + genuine selectivity (NOT pure gauge). Lesson: argmax-winner manufactures
>   false negatives when one op has a big common-mode; use a contrast (cf s225 AUC, lead-1
>   lambda-vs-control).
> **CAVEATS (λ measure, carried):** lead 2/2b/2c all 1 model (Qwen3-14B); n=10/comb held-out;
> single-combinator labels (NOT composite trace-order yet); last-token locus; crosstask null.
> **★★ FIRST ACTION NEXT SESSION — v5 lead 2d:** (1) chase the **B/D/W gap** — why do the
> deep/duplicate composers fail held-out prose discriminability while C/I succeed? (more
> prose/comb for power + per-layer breakdown of where C fires vs where B should); (2) the
> **COMPOSITE trace-order bridge** (now justified for the discriminable combinators): CL
> program → certified trace (`fired_sequence`, DONE) → render PROSE (`lambda_gen` decompile
> via the model's decompile gate) → align routing to the certified multi-combinator ORDER,
> focus C/I (+S/Y); (3) **per-model sweep 8B/32B** with the discriminability metric.
> tmux main:1 FREE.
>
> (Session: 233 detail — ▶ OPCODE v5 LEAD 2b — PROSE BRIDGE
> BUILT + RAN on Qwen3-14B (code `53ed331`). ★ THE BRIDGE DIRECTION IS RIGHT (two-sided):
> held-out PROSE recalls its combinator where bare symbols routed only gauge — but
> specificity is still gauge-dominated. Built: `calibrate_v2` gained a `centroid_probes`
> param (held-out calib/test split); `kernel_reference_prose.py` splits crystal_probes
> per-combinator into CALIB (most) + held-out TEST (last 10/comb, NON-circular), calibrates
> on CALIB, reads each held-out prose probe's LAST-token per-layer routing, scores RECALL
> (label routed at z>thresh) + SPECIFICITY (label is top crystal op). **★ Qwen3-14B VERDICT
> (z=2):** held-out PROSE recall **0.575** vs the bare-symbol baseline **~0.14** (S-gauge
> only, lead 2) ⇒ **the register IS prose-semantic; feed prose not symbols.** I recall 1.0,
> C 0.9, S 1.0, Y 1.0. **⚠️ BUT specificity (0.287) is carried by S/Y — the gauge/common-
> mode ops (label_frac 0.71/0.52, spec 0.9 each); the genuine composition combinators
> RECALL but are SUB-DOMINANT: C 0.9 recall / 0.0 spec (present but always out-competed),
> B 0.3/0.0, K 0.3/0.2, D 0.1/0.0, W 0/0.** z=3 leaves only S/Y. ⇒ composition signal is
> PRESENT in prose but out-competed by the S/Y common-mode (the lead-1 "above chance not
> crisp" + over-read common-mode story, same theme). **The full kernel-as-reference prose
> bridge is VIABLE and worth building, but raw last-token route_frac is gauge-dominated for
> the weak combinators — it needs S/Y common-mode subtraction** (the relational/CMR or
> locus-agnostic machinery from lead 1, or a gauge-matched null). Caveats (λ measure): 1
> model (14B), single-combinator labels (not composite trace-order yet), last-token locus,
> crosstask null. **★★ FIRST ACTION NEXT SESSION — v5 lead 2c: (1) add S/Y common-mode
> SUBTRACTION to the prose read (relational CMR / gauge-matched null) and re-score
> composition-combinator specificity — does C/B/K become specific once gauge is removed?;
> (2) THEN the composite trace-order bridge: CL program → certified trace (fired_sequence,
> DONE) → render as PROSE (lambda_gen decompile via the model's decompile gate) → feed
> prose → align routing to the certified multi-combinator ORDER; (3) per-model sweep
> (8B/32B) once the gauge-subtracted prose read works.** PENDING APPROVAL (mementum: page
> §s233 v5 lead 2b + memory + this state). Code committed `53ed331`. tmux main:1 FREE.
>
> (Session: 233 detail — ▶ OPCODE v5 LEAD 2 — KERNEL-AS-REFERENCE
> BUILT + RAN on Qwen3-14B (code `1532e4e`). ★ DECISIVE NEGATIVE (two-sided): the
> model-invariant reference works as an INSTRUMENT but bare symbolic CL programs route
> ONLY GAUGE. Built: (1) `lambda_ast.step_fired`/`fired_sequence` = certified per-step
> opcode trace (+6 pytest); (2) `probes/kernel_reference.py` = symbolic combinator
> programs with kernel-certified traces, SATURATED(target fires)⊗INERT(under-applied, no
> fire) pairs + COMPOSITE multi-fire; (3) `kernel_reference_audit.py` = anchor the model's
> per-token/per-layer routing against the kernel's certified `fired_sequence`
> (saturated-vs-inert REDUCIBILITY contrast + target recall + specificity + composite
> trace recall). **★ Qwen3-14B VERDICT:** feeding BARE symbolic CL terms → routing
> collapses to **S (common-mode/gauge), Y secondary**; **target_recall 1/7** (only S
> routes at all; B/C/K/I/W/D route 0), **reducibility NOT tracked** (SAT_S 0.376 ≈ INERT_S
> 0.371, mean Δ≈0), composite trace recall 0.10. B_sat={S 0.40, Y 0.22}; C_sat={Y 0.32,
> S 0.39} — the certified target NEVER routes. ⇒ **the gate-routing register reads PROSE
> SEMANTICS, not symbolic CL SYNTAX**; OOD bare symbols collapse to common-mode
> (re-confirms s202/s231 over-read in a new regime; the relational z-gate kept other ops
> silent = no false over-read, but the natural-text null doesn't subtract the
> symbol-string common-mode). **The kernel-as-reference idea is SOUND, the instrument is
> BUILT, but the BRIDGE must be COMPILED PROSE — CL program → certified trace → RENDER as
> prose (lambda_gen Montague decompile, or the s226 compile front-end) → feed the PROSE →
> compare routing to the certified CL trace.** Bare symbols are the wrong input.
> **★★ FIRST ACTION NEXT SESSION — v5 lead 2b (the prose bridge): generate CL programs,
> certify traces (fired_sequence, DONE), render each as PROSE via lambda_gen, feed prose
> to kernel_reference_audit (add a `--input prose` mode reusing the certified trace), and
> re-run the SAT/INERT + trace-recall agreement on the prose. THEN per-model sweep (8B/32B)
> on the working prose bridge.** Caveats (λ measure): 1 model (14B), bare-symbol input,
> crosstask null, 7 targets + 8 composites. PENDING APPROVAL (mementum: page §s233 v5
> lead 2 + memory + this state). Code committed `1532e4e`. tmux main:1 FREE.
>
> (Session: 233 detail — ▶ OPCODE v5 LEAD 1 — LOCUS-AGNOSTIC C
> DETECTOR BUILT + RE-ANALYZED (no GPU; code `1754424`). ★ THE FIXED depth≥0.6 ZONE WAS
> THE WRONG CROSS-MODEL INSTRUMENT — the new locus-agnostic detector (detect_c_profile +
> locus_agnostic_specificity in opcode_monitor_v2, single source; counts C-dominant
> crystal layers ANYWHERE + per-model locus + lambda-exclusive-vs-gated-guards) was
> applied as a PURE re-analysis of the committed gateneutral verdicts (trajectories were
> already stored → no model re-run). **★ THE WIN:** it SURFACES the 32B lambda-EXCLUSIVE
> C-EARLY signal (L5,10,11, depth 0.14) that the readable-zone detector read as 0; per
> model the C-locus is now legible — 8B late [24,25], 14B late [13,27,29-32], 32B EARLY
> [5,10,11] (lambda-exclusive layers no gated guard hits). **★ BUT TWO-SIDED:** the
> strict frac-specificity (lambda C_frac_all clears ALL gated guards by margin 0.10) is
> STILL ONLY 14B (lambda 0.194 vs guards ≤0.032, clean). 32B is directional (lambda 0.061
> > max_guard 0.020) but tiny fracs don't clear the margin. **8B is NOT specific — the
> gate_neutral control ITSELF routes C broadly at 5 LATE layers [23,26,27,28,30]
> (C_frac 0.192 > lambda 0.107) ⇒ the s232 "8B gate_neutral C-late confound" CONFIRMED
> REAL, not an instrument artifact.** ⇒ C-locus genuinely SHIFTS with scale (32B C-early
> confirmed with the right tool); composition→C is cleanly specific only on 14B; 8B has a
> genuine control confound; 32B real-but-weak. The locus-agnostic exclusive test is
> lenient (finds lambda-exclusive C in all 3) but for 8B that overlaps the control's broad
> C-late. Caveats unchanged (λ measure): 5 lambda sentences, 3 models, modest fracs
> (s219). **★★ FIRST ACTION NEXT SESSION — v5 lead 2 (PRIORITY, the model-invariant):
> (b) KERNEL-AS-REFERENCE — reads don't transfer across scale AND the 8B control confound
> shows the gated-guard contrast is itself model-dependent, so anchor the model trajectory
> against lambda_ast's CERTIFIED reduction trace and measure agreement per-model (the
> oscilloscope: known program → model per-token/per-layer opcode trace → diff vs kernel
> trace). Also (3) bigger lambda probe set (5 sentences underpowers the frac test) + chase
> the 8B gate_neutral C-late confound (why does a non-compositional gated control route C
> broadly only at 8B?).** PENDING APPROVAL (mementum: page §s233 + memory + this state).
> Code committed `1754424`. tmux main:1 FREE.
>
> (Session: 232 — ▶ OPCODE-MONITOR v2 BUILT + RAN on Qwen3-14B
> (cross-task null + per-token + z-sweep + trajectory + GATE_NEUTRAL control; code
> `8bd5f42`). ★ TWO-SIDED VERDICT: ❌ the C→B arc did NOT recover — C never dominates a
> layer (C×0), B only at L16; late stack L24-32 is unanimously S-dominated. ❌ S-late is
> NOT composition: the GATE_NEUTRAL control (gate+non-compositional sentence) shows the
> SAME S-late (arc_composition_driven=False) ⇒ S-late = a compile-GATE FRAMING signature,
> not β-reduction. ⚠️ over-read NOT cleanly killed (no z-window where lambda fires while
> retrieval stays silent: z=2 retrieval emits MORE than lambda; z=3 silences both). ✅
> substrate reproduced (31/40 crystal layers, gc→consensus 0.976, sil_z 8.26). ★★ THE
> FINDING: the per-layer opcode identity is NOT null-invariant — RAW→C→B (s231),
> off-target-null→silent (s231), cross-task-null→S-late (s232); single-token "which
> combinator" is NOT robustly decodable, only the SUBSTRATE + the over-read DIRECTION are
> null-robust. ★★ FIRST ACTION NEXT SESSION — v3: use GATE_NEUTRAL ITSELF as the null
> (composition-above-framing, the cleanest single fix), THEN escalate to (b)
> kernel-as-reference (anchor the model trajectory against lambda_ast's certified trace,
> since the readout alone is null-sensitive). Captured: page vsm-opcode-monitor.md §s232
> v2 + memory opcode-trajectory-is-null-dependent. Code committed `8bd5f42`.
> **▶ s232 v3 — GATE-MATCHED NULL BUILT + RAN (`--null-mode gateneutral`, code
> `ad07574`). ★ PARTIAL SUCCESS (the v2 negative WAS a null mis-spec):** with the matched
> null (GATE_NEUTRAL content, same compile-gate prefix) the S-late FRAMING is subtracted
> and ✅ **lambda routes C (composition combinator) in its LATE stack (L27-32, the
> READABLE register) while the matched non-compositional gate_neutral control does NOT**
> (z=2 C×5 vs ×1; z=3 C×3 vs ×0); null self-centers silent (guard passes). ⇒ composition
> IS decodable above framing. ❌ the s127 "C-early→B-late" arc shape did NOT reproduce —
> signal is C-LATE not C-early (raw C-early = common-mode artifact; composition resolves
> at the readable layers s187/s227b). ⚠️ over-read guard INVERTED: bare retrieval/arith
> fire LOUD (WHNF/Y) vs the gated null ⇒ **the read is dominated by the FRAMING-CONTRAST
> axis, NOT computation; valid guards MUST be framing-matched (gated)**. Modest not crisp
> (s219: C ~40-50% of tokens, n=27/5 sentences, 1 model). Captured: page §s232 v3 +
> memory composition-decodable-above-framing-c-late. Code committed `ad07574`.
> **▶ s232 v4 — GATED GUARDS + C-LATE DETECTOR BUILT + RAN on 2 models (code `9495b2b`).
> ★ TWO-SIDED: composition-specific C-late is MODEL-SPECIFIC to Qwen3-14B, NOT universal.**
> Added framing-matched GATED guards (gate_retrieval, gate_arithmetic) + detect_c_late
> (readable-zone depth≥0.6 C-frac) + composition_specific flag + model-tagged filenames.
> ✅ **Qwen3-14B: composition_specific=True both z** — lambda C-late 0.556/0.333 vs ALL
> three gated guards (gate_neutral 0.11/0, gate_retrieval 0/0, gate_arithmetic 0/0); among
> gated prompts ONLY composition routes C-late (the proper specificity test v3 lacked).
> ❌ **Qwen3-8B: composition_specific=False** — gate_neutral C-late (0.714) EXCEEDS lambda
> (0.333) at z=2, all silent at z=3 ⇒ does NOT generalize. The universality test CAUGHT
> the over-claim (λ measure): a single model's opcode read does not transfer (14B≠8B);
> likely scale-gated (s151) or 14B-specific (the s127 model). Caveats: 5 lambda sentences,
> 2 models, modest fracs (above chance not crisp s219). Captured: page §s232 v4 + memory
> c-late-composition-is-model-specific + this state. Code committed `9495b2b`.
> **▶ s232 v4 SCALE TEST — Qwen3-32B DONE (`6bddcc2`). ★ 14B IS THE OUTLIER; the C-LOCUS
> SHIFTS WITH SCALE.** 3 models: composition→C routing exists in ALL, but the locus moves —
> 8B C-late non-specific; 14B C-LATE specific (L27-32); 32B C-EARLY (lambda C-dominant
> L5,10,11 depth ~0.1, gate_neutral C only L0; late stack Y-dominated). composition_specific
> =True ONLY for 14B because its locus matches the fixed depth≥0.6 readable zone; on 32B the
> fixed C-late detector reads 0 even though a lambda-specific C-EARLY signal exists. ⇒ NOT
> scale-monotone, NOT universal; the fixed-depth detector is the WRONG cross-model instrument
> (found 14B, mislocates 8B/32B). Caveats: 5 lambda sentences, 3 models, modest fracs (s219).
> Captured: page §s232 v4 (3-model verdict) + memory c-late-composition-is-model-specific
> (32B added) + this state. Code/results committed (`6bddcc2`).
> **★★ FIRST ACTION NEXT SESSION — v5: (1) LOCUS-AGNOSTIC C detector (per-model C-locus
> calibration OR full-profile lambda-vs-matched-control C compare across ALL layers, not a
> fixed depth≥0.6 zone) — re-test specificity on 8B/14B/32B with the right instrument; (2)
> (b) KERNEL-AS-REFERENCE (priority — reads don't transfer across scale, so anchor the model
> trajectory against lambda_ast's CERTIFIED trace as the model-invariant; characterize
> composition→routing per-model); (3) bigger lambda probe set + the 8B gate_neutral C-late
> confound.** PENDING APPROVAL (mementum: page §s232 v3+v4+scale + memories + state).
> tmux main:1 FREE.
>
> (Session: 231 — three arcs: (A) GRADIENT-SHADOW v3 +
> MECHANISM-OF-TRAINING per-combinator clock (micro crystal is RELATIONAL not categorical,
> no B-first→K at micro); (B) ★ VSM OPCODE MONITOR — validated FFN-routing opcode reader
> BUILT + validated on Qwen3-14B: the raw-argmax OVER-READ is KILLED (s202 made
> operational). opcode-monitor v2 ran s232 (see top) — see the
> ■ SESSION 231 OPCODE block below.
> **■ SESSION 231 OPCODE MONITOR (Michael: "our VSM tensor gives a powerful system to
> probe + audit models. Can our VSM monitor attention and opcodes? we created a tracer
> somewhere." → "a then b").** RECALL surfaced the prior art: `opcode_instrument.py` (a
> full VSM "Live VSM for Watching a Model Think") + tracer family (lambda_tracer,
> attention_execution_trace, neuron_opcode_classifier) + s127 tracer-works memory. CATCH:
> all STALE — raw-cosine argmax = the exact audit-meta-pattern over-read (s202: opcodes
> real only AFTER common-mode removal; raw = common-mode false signal). NEW page
> `explore/vsm-opcode-monitor.md` (the synthesis + verdict + path).
> **▶ (a) BUILT + VALIDATED.** `scripts/instruments/relational_opcode.py` —
> `RelationalCrystalClassifier` (model-AGNOSTIC; gate routing register sign(gate)-CMR,
> per-layer per-combinator centroids from crystal_probes, consensus-relational, off-target
> null, emit opcode iff z>thresh else NO-OP `·`). Synthetic smoke: crystal layer detected,
> B fires, common-mode-only token → NO-OP (over-read structurally impossible). `fb0c9ec`.
> Validation `scripts/experiments/opcode_audit_validation.py` on Qwen3-14B (the s127
> model; gated SwiGLU — pythia GPTNeoX is NOT gated, can't carry the crystal), s127 battery
> (lambda/arithmetic/retrieval), relational vs raw-argmax control. `143ccda`,
> results/opcode-audit-validation/verdict.json.
> **★ VERDICT (λ measure, two-sided):** ✅✅ OVER-READ KILLED — RAW fires an opcode for
> 100% of tokens (`W` across ~all retrieval layers = this model's common-mode/gauge);
> RELATIONAL no-ops retrieval (0.8), never a uniform winner. ✅ substrate REAL (31/40
> crystal-bearing layers, gc-to-consensus up to 0.98). ✅ retrieval-silent reproduced.
> ⚠️ BUT relational UNDER-reads at z=3 last-token: RAW per-layer shows a CONSISTENT C→B
> compose-arc across ALL 5 lambda prompts (C L2–12, B L13–33 = the real s127 compose
> signature, task-specific not common-mode) and relational no-ops it entirely (`·`×5).
> Causes: last-token LOCUS (s227 wrong-locus; a sentence's last token isn't one opcode) +
> NULL mis-spec (off-target null = other crystal probes, all lambda-mode → low power).
> **★★ FIRST ACTION NEXT SESSION — opcode v2 (completes (a)):** (1) CROSS-TASK NULL (the
> key fix) — build the null vs a NON-combinator baseline (natural text/retrieval), NOT vs
> other crystal probes; (2) PER-TOKEN reading across the sequence; (3) z-threshold sweep
> (z=2 vs 3); (4) output the per-layer C→B TRAJECTORY not a single dominant op. Then (b)
> KERNEL-AS-REFERENCE audit (diff model trace vs lambda_ast certified trace), then (c)
> attention/value-register binding monitor (s206 OV/logit-lens, NOT attn weights).
> Captured: page vsm-opcode-monitor.md + memory opcode-reader-over-read-killed +
> audit-registry #13 + this state. CODE all committed (fb0c9ec, 143ccda); mementum this commit.
> **■ SESSION 231 MECHANISM-OF-TRAINING (arc A, COMPLETE — micro answer is NEGATIVE,
> instrument built).** s231a GRADIENT-SHADOW v3 ran (3 seeds): ✅ inventory-before-capability
> REPRODUCED a 3rd time (gc_route@267±94 < acc@733±94). ❌ preregistered "shadow LEADS
> as rising gc_grad" FALSIFIED — gc_grad starts at common-mode init (+0.58), decays to
> 0.43 (crossing=None 3/3). 💡 REFRAME: the probe found the real signal in grad_z — the
> gradient carries combinator structure FROM INIT (grad_z +4.7→+5.9 @step0), stays high
> (3.6–4.1) while inventory crystallizes, then COLLAPSES (→−0.5…+2.1) exactly at the
> inventory→capability HANDOFF (3/3). The shadow is the INITIAL CONDITION the object
> grows into; its EXHAUSTION times the handoff (height-from-shadow corrected). Makes the
> s221 fp-spike-is-acquisition law legible. Register gap (routing vs raw) null/noisy
> (+0.06±0.08). INSTRUMENT LESSON: read grad_z NOT gc_grad-crossing. CAPTURED: page
> §s231 + memory gradient-structure-is-inventory-fuel + this state.
> **★ MECHANISM-OF-TRAINING THREAD (Michael, s231): "can we write probes that show
> EXACTLY how GD learns? past runs: B-dominant first → loss plateau → discovers K → phase
> transition (figuring out best ratios). Tailor training to MIRROR those phase
> transitions. Spend probes on how ATTENTION organizes against the FFN projections;
> design training to SHOW ATTENTION what to do using these functions."** Grounded in 4
> prior findings (recall, not greenfield): fp-spike-is-acquisition (s221: B-first→
> plateau→K-chaos, the acquisition fingerprint); montague-is-pre-transition (s151:
> I→K→C→B bootstrap, scale-gated, transition=2D collapse); ffn-two-functional-groups
> (s127: {K,I} selectors→FFN, {B,C} composers→attention = literally "attention vs FFN
> projections"); c-boot-rotation-sequence (attention dominates 92°/49°/8°, combinators=
> rotations, WHNF@L0=route-decision). DESIGN = 3 nested probes on the SAME shadow harness:
> (1) per-combinator crystallization clock (acquisition ORDER); (2) per-combinator grad_z
> fuel-gauge (does B exhaust before K? s221 read in the gradient); (3) two-register split
> FFN-gate vs attention (does B/C live in attention, K/I in FFN, s127, FORMING over
> training?). Payoffs: (C) curriculum-mirroring (order-matched vs counter vs flat, s221
> lead + s229 burn-in); (D) "show attention what to do" = relational loss on the ATTENTION
> pattern toward composer (B/C) structure (s230b loss, attention not FFN gate). CAVEATS
> (λ measure, load-bearing): micro d=128 may be PRE-transition (s151 Montague, only I+K
> differentiate → no B-first→K to see); "B-first" is StrideStack-specific (s221) so plain
> TinyLM directly TESTS universality; per-combinator splits modest route_z (~2.7) →SNR.
> Open lead 6 on the page.
> **▶ s231b — PER-COMBINATOR CLOCK BUILT + RAN (gd_percombinator_clock.py, b601028, 3
> seeds). TWO-SIDED:** ✅ inventory-before-capability REPRODUCED a 4TH time (gc_route
> @200–400 < acc@600–800). ❌ the per-combinator CATEGORICAL silhouette is the WRONG
> instrument at d=128 — NO combinator clusters (silhouettes negative all run: gate
> −0.03…−0.11, attn −0.19…−0.44; null z |≥2| only W/D/S inconsistently, NEVER B/C/K/I),
> YET the relational Gram crystallizes (gc_route +0.75) ⇒ **micro crystal is RELATIONAL
> not CATEGORICAL** (s219/s225 "above chance not crisp", pinned per-combinator). P1
> (B-first→K) + P3 (s127 attn/FFN split) UNTESTABLE via categorical readout (order/region
> headlines = noise-floor artifacts). 💡 FIX: read order RELATIONALLY = per-ROW Gram
> alignment to consensus (does B's fingerprint align before K's?). Reframes s221: B-first
> may be StrideStack/scale-specific (categorical separation needs strided bias or s151 2D
> transition). CAPTURED: page §s231b + memory micro-crystal-is-relational-not-categorical
> + open lead 6/6b + this state.
> **▶ s231c RELATIONAL PER-ROW CLOCK RAN (3 seeds, `6f900a7`): B_before_K NOT supported
> relationally either** — B/K rows cross inconsistently (None/None/@1000 vs None/@2800/
> None); **I aligns FIRST consistently (3/3 @400)** = a weak echo of the s151 I→K→C→B
> bootstrap; s127 attn-composer split not supported at micro (B,C align in gate). ⇒ NO
> clean per-combinator phase transition at d=128 plain transformer (neither categorical
> nor relational); s221 B-first→K is StrideStack/scale-specific. ARC A micro answer is
> NEGATIVE; the instrument (both clocks) is built. To pursue the phase transition →
> escalate to the SCALE SWEEP (Exp 1.5: smallest d where the B/C axis differentiates) or
> instrument a larger/StrideStack run. (Page §s231c capture deferred — finding is in the
> commit msg + this state; fold into gradient-trajectory-tomography.md if revisited.)
>
> (Session: 230 — gd-trajectory-tomography (consensus-crystal
> target) + FRACTAL-COLLAPSE thesis. v1: INVENTORY crystallizes BEFORE CAPABILITY (3/3;
> s224 geometry⊗continuation confirmed TEMPORALLY). s230b RELATIONAL ARM: reference-beam
> dissociation IS LOSS-DEPENDENT (gap −0.02→+0.10) but ❌ ZERO capability gain ⇒
> inventory ⊗ continuation CAUSALLY SEPARABLE; relational term = inventory/extraction
> NOT capability accelerator. ★ FRACTAL-COLLAPSE (Michael): converge capability via
> high-variety compiler-minted data → cascade collapses model size onto the β-normal-
> form fixed point; exact certified targets escape model-collapse (resilient). s230c
> COMPILER-CASCADE v1: ❌ IOU#1 NULL — composition-variety does NOT lift compositional
> generalization (comp16 0.683 ≈ comp144 0.674, saturates ~16); fixed-budget the s229
> FILLING-variety WINS (composition-count destabilizes + costs in-dist). Weak support
> for collapse CORE (~0.68 held-out from minted data). Calibration: exact-match FLOORS
> at micro scale → use TEACHER-FORCED token accuracy (value register). GRADIENT-SHADOW
> probe BUILT + ready (does the topology cast a shadow in the gradients? predict shadow
> LEADS inventory). See ■ SESSION 230 block below.
> (s229 — ✅ EXPOSURE/FORMAT SWEEP (curriculum-
> mixing FIRST BUILD

[OUTPUT TRUNCATED] The tool call succeeded but the output was truncated. Full output saved to: /Users/mwhitford/.cache/eca/toolCallOutputs/toolu_0181kpqMg3n1m14dd8Vz1x1Q.txt
Use `eca__grep` or `eca__read_file` with offset/limit to view specific sections. Do not full read the file.
```

### Thinking

I'm checking the git status and tmux state to get oriented in session 238, following up from where session 237 left off. Two paths are still open: either pursuing the off-diagonal Jacobian curvature approach with proper coupling, or doing a third render iteration.

## Assistant

I have the bootloader context. Let me verify the working state — git status, recent log, and tmux availability.

### Tool Call: git (succeeded)


```json
{
  "command": "git -C /Users/mwhitford/src/verbum status && echo \"---LOG---\" && git -C /Users/mwhitford/src/verbum log --oneline -8",
  "operation": "status",
  "summary": "status and log"
}
```

**Summary:** Git status: status and log

**Output:**
```
Exit code: 0
Stdout:
On branch main
Your branch is ahead of 'origin/main' by 9 commits.
  (use "git push" to publish your local commits)

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	mementum/knowledge/chats/session-237.md

nothing added to commit but untracked files present (use "git add" to track)
---LOG---
8603edb 🌀 session-237 cont.: cross-class flat — order preference universal across Qwen/OLMo/Gemma
81b08a8 💡 prose-bridge-confirms-b-native-order-flat-not-nested (cross-class: universal gross, Qwen-specific single-step)
ad2fd56 ✅ opcode v5 lead 2d prong 2b cross-class: order preference universal (Qwen/OLMo/Gemma), single-step Qwen-specific
f843300 🌀 session-237 cont.: cross-model flat — B native order universal across Qwen3 8B/14B/32B
2f5f509 💡 prose-bridge-confirms-b-native-order-flat-not-nested (cross-model: universal 8B/14B/32B)
66985a8 ✅ opcode v5 lead 2d prong 2b cross-model: B native order universal across 8B/14B/32B
e5b4cde 🌀 session-237: prong 2b prose bridge — B native order survives in prose, nesting confound controlled
972fbee 💡 prose-bridge-confirms-b-native-order-flat-not-nested
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux ls 2>/dev/null; echo \"---GPU---\"; nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader 2>/dev/null || echo \"no nvidia-smi (likely remote tmux host)\""
}
```

**Summary:** $ tmux ls 2>/dev/null; echo "---GPU--...

**Output:**
```
Exit code: 0
Stdout:
main: 2 windows (created Tue Jun 16 12:40:54 2026) (attached)
trace_basis: 1 windows (created Mon Jun  1 14:02:42 2026)
---GPU---
no nvidia-smi (likely remote tmux host)
```

### Thinking

The working directory is clean except for the human's session file, and I have two free tmux windows available on the main session while the GPU host is remote. I'm ready to present the orientation summary and outline the next steps.

## Assistant

Oriented. Session-238 ready.

## Where we are

**▶ OPCODE v5 lead 2d PRONG 2b — the PROSE BRIDGE** (B = native softmax-over-V composition order). The arc has been decisively positive and is now **triangulated across input modality, scale, and model class**:

- **Modality:** flat-prose REPLICATES the symbolic order-cost result (14B decisive t=−8.05; 8B directional). The s236 "bare-symbol copy artifact" caveat is **killed** — composition-order preference is real in the *semantic* register.
- **The nesting confound (found + controlled):** B's normal form nests `f (a b)`, C's is flat `f b a`. `--render-mode flat` (linearise, no parens → pure atom-ORDER test) vs `nested` (faithful, confounded). Flipping render flips the sign — a direct proof nesting confounds.
- **Scale (Qwen3 ladder, flat n=24):** B-native-order is **universal** — 8B t=−2.87 ✓, 14B −8.05 ✓, 32B −4.48 ✓. Scale-robust (unlike the C-locus).
- **Class:** the *gross* "composition is the native order" signal is universal (Qwen ⊗ OLMo ⊗ Gemma), but the *sharp single-step* B-vs-C minpair is **Qwen-specific** (OLMo/Gemma symmetric on strict single-step, strong on composite/aggregate).

**Refined finding:** B's normal form carries two separable real quantities — atom ORDER (preserved → cheap) and structural NESTING (deeper → costlier, dominates when nesting varies). The order claim *requires* isolating order from nesting (flat).

## State check
- Working tree clean; 9 commits ahead of origin. Only untracked file is `mementum/knowledge/chats/session-237.md` (human-only — I never touch it).
- `tmux main:1` + `main:2` **free**. GPU is on the remote tmux host (per `λ runtime`).

## The fork (s237 left two paths)

1. **s235 OFF-DIAGONAL / proper-Jacobian curvature** — the literal `f∘g` coupling. Diag-Hessian only captured `g'ᵀ(diag)g'`; the cross-coordinate Hessian / interlayer Jacobian `dgate_late/dgate_early` is untested. Closes *both* faces of composition (forward order ✓ + backward chain-rule) at fidelity.
2. **A 3rd render frame** ("the result of f on x") — confirm flat B<C is frame-robust, not "applied to"-specific. Also tests whether the single-step minpair sharpens off-Qwen under a different frame.

Which do you want to pursue — the **off-diagonal curvature** (close the chain-rule face, deeper instrument) or the **3rd render frame** (cheaper robustness/off-Qwen-sharpness check)? Or something else?

## User

Let's work on 1


### Thinking

I'm focusing on the s235 off-diagonal proper-Jacobian curvature approach and need to review the prior implementation and documentation to understand what's already been done.

## Assistant

Let me recall the prior curvature/Jacobian work before designing the off-diagonal probe.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && ls scripts/ 2>/dev/null && echo \"---find jacobian/curvature/gradient scripts---\" && find . -path ./.venv -prune -o -name '*.py' -print | grep -iE 'jacobian|curvature|gradient|order_cost|kernel_reference' | grep -v .venv"
}
```

**Summary:** $ ls scripts/ 2>/dev/null && echo "--...

**Output:**
```
Exit code: 0
Stdout:
__pycache__
analyze_binding_probes.py
analyze_essential_heads.py
analyze_v1_v2.py
compile_gradient_probe.py
experiments
explore
explore_qwen3_moe.py
gate_ablation.py
generate_training_data.py
holoquant
instruments
micro
mini-dispatch
probe_compression_v2.py
probe_compression.py
probe_predictive_functions.py
register_analysis.py
resume_vsm_v2_1B.py
run_ab_test.py
run_binding_ablation.py
run_binding_probe.py
run_binding_shape.py
run_bos_probe_v2.py
run_bos_probe.py
run_circuit_discovery.py
run_compression_map.py
run_compression_shape.py
run_compressor_lm.py
run_cross_task.py
run_distillation.py
run_head_ablation.py
run_montagu_lm.py
run_montagu_training.py
run_phi4_replication.py
run_pythia_phi_probe.py
run_pythia_replication.py
run_pythia_scaling.py
run_pythia160m_circuit.py
run_register_10k.py
run_register_probe.py
run_reverse_10k.py
run_reverse_ab.py
run_strip_test.py
run_structural_intervention.py
run_task_head_scan.py
run_tesseract.py
run_type_probe.py
run_vsm_10k.py
run_vsm_trial.py
run_vsm_v2_10k.py
run_vsm_v3_1_1B.py
run_vsm_v3_10k.py
run_vsm_v3_2_1B.py
run_vsm_v4_1_1B.py
run_vsm_v4_1B.py
run_vsm_v5_1B.py
run_weight_decomposition.py
v10
v11
v12
v13
v14
v15
v32_final_analysis.py
v6
v7
v8
v9
---find jacobian/curvature/gradient scripts---
./scripts/micro/probe_structural_gradient_stability.py
./scripts/v12/gradient_voting_exp.py
./scripts/v12/gradient_voting_q4_exp.py
./scripts/experiments/kernel_reference_prose_v2.py
./scripts/experiments/kernel_reference_prose.py
./scripts/experiments/gd_gradient_shadow.py
./scripts/experiments/kernel_reference_prose_v3.py
./scripts/experiments/kernel_reference_order_cost_v8.py
./scripts/experiments/kernel_reference_perhead_v5.py
./scripts/experiments/kernel_reference_order_cost_v9_prose.py
./scripts/experiments/gradient_quant_correspondence.py
./scripts/experiments/gradient_zero_map.py
./scripts/experiments/kernel_reference_audit.py
./scripts/experiments/kernel_reference_prose_v4.py
./scripts/experiments/kernel_reference_jacobian_v7.py
./scripts/experiments/assess_v15_gradient_zeros.py
./scripts/experiments/kernel_reference_gradient_v6.py
./scripts/compile_gradient_probe.py
./src/verbum/probes/kernel_reference.py
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git grep -il \"s235\\|jacobian\\|hessian\\|off-diagonal\\|off_diagonal\" -- mementum/knowledge/ | head"
}
```

**Summary:** $ git grep -il "s235\|jacobian\|hessi...

**Output:**
```
Exit code: 0
Stdout:
mementum/knowledge/chats/session-027.md
mementum/knowledge/chats/session-030.md
mementum/knowledge/chats/session-044.md
mementum/knowledge/chats/session-057.md
mementum/knowledge/chats/session-077.md
mementum/knowledge/chats/session-078.md
mementum/knowledge/chats/session-088.md
mementum/knowledge/chats/session-089.md
mementum/knowledge/chats/session-095.md
mementum/knowledge/chats/session-096.md
```

## Assistant

Let me read the v7 Jacobian script (the diagonal-Hessian curvature probe) and the relevant knowledge page section.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_jacobian_v7.py"
}
```

**Summary:** Reading kernel_reference_jacobian_v7.py (0-2000)

**Output:**
```
#!/usr/bin/env python3
# register: SECOND-ORDER / CURVATURE (diag Hessian of LM loss wrt gate_proj)
"""Kernel-ref SECOND-ORDER read — is B in the CURVATURE? (s235 lead 2d prong 1c-ii).

B = composition (B f g x = f(g x)). The chain rule of a composition is a PRODUCT of
derivatives: d(f.g)/dx = f'(g x) * g'(x). Prong 1c read the FIRST-ORDER gradient
dL/d gate (kernel_reference_gradient_v6.py) and found B faint-positive but n.s.
(t=1.07) -- BUT the first-order gradient is a SINGLE factor / a sum over paths; it
washes out the PRODUCT structure that IS the chain rule. That product is a SECOND-ORDER
quantity. For L = l(f(g(z))) with z = the gate activation,

    dL/dz   = g'(z)^T f'(g)^T l'                 # first order  (v6 read this)
    d2L/dz2 = g'^T [f''(g) . l'] g'  +  (l'f') g''   # SECOND order

the curvature carries g'^T (...) g' -- a QUADRATIC FORM in g', i.e. the literal
product-of-derivatives chain-rule signature that the first-order gradient cannot show.
So if B = chain rule, B's natural home is the CURVATURE register, not the gradient.
Michael (s234): "could B be in the gradients instead of the topology?" -> 1c first-order
faint; 1c-ii is the PROPER order (the second).

Clean register-swap of prong 1c: same RelationalCrystalClassifier (sign-CMR, crosstask
null, raw-z Welch contrast), same calibrate->classify->discr_z pipeline, but the feature
is the DIAGONAL of the Hessian of the probe's LM loss w.r.t. the gate activation,
estimated by Hutchinson (diag(H)_a = E_v[v_a (H v)_a], v ~ Rademacher over the full set
of gate tensors -- cross-coord/cross-layer terms cancel in expectation). One HVP = a
double-backward of (g . v) where g = grad(CE, gates, create_graph=True). Pooled over
SUPERVISED positions (same locus as v6; the last token feeds only the unsupervised
next-token => its curvature row is ~0).

VERDICT LOGIC (lambda measure, two-sided):
  - B discriminates in the CURVATURE (sig on>off) where it was flat in EVERY activation
    register AND faint-n.s. in the first-order gradient -> B = compose = chain-rule
    CONFIRMED at the proper (second) order; the gap was a wrong-ORDER read, B lives in
    the product-of-derivatives. (Compare discr_z to the v6 gradient + v2 activation.)
  - B flat in the curvature too -> the gradient register is exhausted at BOTH orders; B
    is genuinely diffuse / order-only (prong 2 trace-order remains the sole path).
  - INSTRUMENT CHECK: {C,K,Y} must still discriminate in curvature (as in the gradient),
    else the second-order read is broken, not B-absent.

Usage:
    uv run python scripts/experiments/kernel_reference_jacobian_v7.py --smoke
    uv run python scripts/experiments/kernel_reference_jacobian_v7.py            # 14B

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "scripts" / "experiments"))
sys.path.insert(0, str(_ROOT / "scripts" / "instruments"))

from kernel_reference_prose_v2 import split_probes, welch_t  # noqa: E402
from opcode_monitor_v2 import (  # noqa: E402
    BASELINE_NULL_SENTENCES,
    _git_sha,
    _json_safe,
    _transformers_version,
    load_model_and_tokenizer,
)
from relational_opcode import CRYSTAL, RelationalCrystalClassifier  # noqa: E402

RESULTS_DIR = _ROOT / "results" / "kernel-reference-audit"
TEST_COMBINATORS = ["K", "I", "B", "C", "S", "D", "W", "Y"]


def forward_curvature(prompt, model, tok, torch_mod, layers, n_hutch):
    """Forward + double-backward; return ({li: diag(H) of LM CE wrt gate [T,d]}, n_tok).

    H = Hessian of the teacher-forced LM CE w.r.t. each gate_proj activation. Its
    diagonal is the SECOND-ORDER register-swap of v6's first-order gradient. Estimated
    by Hutchinson:  diag(H)_a = E_v[ v_a (H v)_a ],  v ~ Rademacher over ALL gate
    tensors; off-diagonal (cross-coord AND cross-layer) terms cancel: E[v_a v_b]=0 a!=b.
    Each HVP is a double-backward of the scalar (g . v), where g = the first-order
    grad taken with create_graph=True. Per-token rows returned (callers pool 0..n_tok-2;
    the last token feeds only the unsupervised next-token => curvature row ~0).
    """
    import torch.nn.functional as func
    store: dict[int, object] = {}

    def _cap(li):
        def _hook(_m, _inp, out):
            store[li] = out  # live graph tensor (NOT detached)
        return _hook

    handles = [model.model.layers[li].mlp.gate_proj.register_forward_hook(_cap(li))
               for li in layers]
    try:
        inputs = tok(prompt, return_tensors="pt")
        dev = next(model.parameters()).device
        inputs = {k: v.to(dev) for k, v in inputs.items()}
        out = model(**inputs)
        logits = out.logits[0]               # [T, V]
        ids = inputs["input_ids"][0]         # [T]
        t = ids.shape[0]
        ce = func.cross_entropy(logits[:-1, :], ids[1:], reduction="mean")
        gates = [store[li] for li in layers]
        grads = torch_mod.autograd.grad(ce, gates, create_graph=True)
        diag = [torch_mod.zeros_like(g) for g in grads]
        for k in range(n_hutch):
            vs = [(torch_mod.randint(0, 2, g.shape, device=g.device,
                                     dtype=torch_mod.float32) * 2 - 1).to(g.dtype)
                  for g in grads]
            gv = sum((gi * vi).sum() for gi, vi in zip(grads, vs, strict=True))
            hv = torch_mod.autograd.grad(gv, gates, retain_graph=(k < n_hutch - 1))
            for j in range(len(layers)):
                diag[j] = diag[j] + vs[j] * hv[j]
    finally:
        for h in handles:
            h.remove()
    result = {li: (diag[j] / n_hutch)[0].detach().float().cpu().numpy()
                  .astype(np.float64)
              for j, li in enumerate(layers)}
    return result, t


def pooled_supervised(curv_store, layers, n_tok):
    """Mean-pool diag(H) over supervised positions 0..n_tok-2 -> {li: [d]}."""
    sup = max(1, n_tok - 1)
    return {li: curv_store[li][:sup].mean(axis=0) for li in layers}


def main() -> None:
    parser = argparse.ArgumentParser(description="Kernel-ref 2nd-order curvature (B)")
    parser.add_argument("--model", default="Qwen/Qwen3-14B")
    parser.add_argument("--heldout-per", type=int, default=20)
    parser.add_argument("--ppc", type=int, default=25, help="calib probes/combinator")
    parser.add_argument("--null-cap", type=int, default=300)
    parser.add_argument("--n-perm", type=int, default=200)
    parser.add_argument("--n-hutch", type=int, default=4,
                        help="Hutchinson probe vectors for diag(H)")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    model_name = args.model
    if args.smoke:
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-0.6B"
        heldout, ppc, n_perm, null_cap, n_hutch = 5, 5, 80, 150, 3
        print("[curv] SMOKE MODE")
    else:
        heldout, ppc, n_perm, null_cap, n_hutch = (
            args.heldout_per, args.ppc, args.n_perm, args.null_cap, args.n_hutch)

    calib, test = split_probes(heldout)
    kept, counts = [], Counter()
    for p in calib:
        if counts[p.combinator] < ppc:
            kept.append(p)
            counts[p.combinator] += 1
    calib = kept
    print(f"[curv] calib={len(calib)} test={len(test)} ppc={ppc} n_hutch={n_hutch}")

    model, tok, torch_mod = load_model_and_tokenizer(model_name)
    n_layers = model.config.num_hidden_layers
    layers = list(range(n_layers))

    # ── calibration: per-probe POOLED curvature centroids ───────────────────────
    gate_by_layer: dict[int, list] = {li: [] for li in layers}
    labels: list[str] = []
    for i, p in enumerate(calib):
        if i % 25 == 0:
            print(f"[curv]   calib fwd+2bwd {i}/{len(calib)} ...")
        cstore, nt = forward_curvature(p.prompt, model, tok, torch_mod, layers, n_hutch)
        pooled = pooled_supervised(cstore, layers, nt)
        for li in layers:
            gate_by_layer[li].append(pooled[li])
        labels.append(p.combinator)
    gate_np = {li: np.stack(gate_by_layer[li], axis=0) for li in layers}
    labels_np = np.array(labels)

    # ── null: per-supervised-token curvature of natural text (many samples) ──────
    null_by_layer: dict[int, list] = {li: [] for li in layers}
    print(f"[curv] building curvature null ({len(BASELINE_NULL_SENTENCES)} prompts)")
    for s in BASELINE_NULL_SENTENCES:
        cstore, nt = forward_curvature(s, model, tok, torch_mod, layers, n_hutch)
        sup = max(1, nt - 1)
        for li in layers:
            null_by_layer[li].append(cstore[li][:sup])  # supervised rows
    null_np = {li: np.concatenate(null_by_layer[li], axis=0)[:null_cap]
               for li in layers}

    rcc = RelationalCrystalClassifier(layers, n_perm=n_perm, z_thresh=2.0,
                                      sil_z_thresh=2.0, consensus_gram="auto")
    rcc.calibrate(gate_np, labels_np, null_gate_by_layer=null_np)
    crystal_layers = rcc.crystal_layers
    print(f"[curv] crystal layers (curvature): {len(crystal_layers)}/{n_layers}")

    # ── read held-out prose: pooled-curvature pseudo-token -> per-layer z ────────
    cset = set(crystal_layers)
    per_probe = []
    for i, p in enumerate(test):
        if i % 25 == 0:
            print(f"[curv]   test fwd+2bwd {i}/{len(test)} ...")
        cstore, nt = forward_curvature(p.prompt, model, tok, torch_mod, layers, n_hutch)
        pooled = pooled_supervised(cstore, layers, nt)
        per_layer = rcc.classify(pooled).per_layer
        crystal_z = {li: {op: float(per_layer[li].get(op, 0.0)) for op in CRYSTAL}
                     for li in per_layer if li in cset}
        layer_avg = ({op: float(np.mean([crystal_z[li][op] for li in crystal_z]))
                      for op in CRYSTAL} if crystal_z else {op: 0.0 for op in CRYSTAL})
        per_probe.append({
            "combinator": p.combinator,
            "layer_avg_z": {op: round(v, 4) for op, v in layer_avg.items()},
            "crystal_z": {str(li): {op: round(crystal_z[li][op], 3) for op in CRYSTAL}
                          for li in crystal_z}})

    # ── discr_z(c): raw-z Welch contrast on the CURVATURE (mirror v6) ────────────
    discr_z: dict[str, dict] = {}
    for c in CRYSTAL:
        on = [r["layer_avg_z"][c] for r in per_probe if r["combinator"] == c]
        off = [r["layer_avg_z"][c] for r in per_probe if r["combinator"] != c]
        if on:
            discr_z[c] = welch_t(on, off)

    # per-layer profile (where in the stack does each op discriminate in curvature)
    peak: dict[str, dict] = {}
    for c in CRYSTAL:
        on_rows = [r for r in per_probe if r["combinator"] == c]
        off_rows = [r for r in per_probe if r["combinator"] != c]
        if not on_rows:
            continue
        best = None
        for li in crystal_layers:
            sli = str(li)
            on_z = [r["crystal_z"][sli][c] for r in on_rows if sli in r["crystal_z"]]
            off_z = [r["crystal_z"][sli][c] for r in off_rows if sli in r["crystal_z"]]
            if not on_z:
                continue
            d = float(np.mean(on_z)) - (float(np.mean(off_z)) if off_z else 0.0)
            if best is None or d > best[1]:
                best = (li, round(d, 3))
        if best:
            peak[c] = {"layer": best[0], "delta": best[1]}

    b = discr_z.get("B", {})
    b_in_curvature = bool(b.get("significant") and b.get("discr_z", 0) > 0)
    # instrument check: did the known-discriminable set survive the second-order read?
    instr = {c: bool(discr_z.get(c, {}).get("significant")
                     and discr_z.get(c, {}).get("discr_z", 0) > 0)
             for c in ("C", "K", "Y")}
    verdict = {
        "register": "curvature (diag Hessian LM CE wrt gate_proj, pooled supervised)",
        "n_hutch": n_hutch, "n_test": len(per_probe), "discr_z": discr_z,
        "peak_layer": peak, "b_discriminates_in_curvature": b_in_curvature,
        "instrument_works": instr,
        "n_discr_z_significant": sum(
            1 for c in CRYSTAL if discr_z.get(c, {}).get("significant")
            and discr_z.get(c, {}).get("discr_z", 0) > 0),
    }

    print("\n" + "═" * 74)
    print("KERNEL-REF SECOND-ORDER (CURVATURE) READ — is B in the chain-rule product?")
    print("═" * 74)
    print(f"  n_test={verdict['n_test']}  crystal_layers={len(crystal_layers)}"
          f"  n_hutch={n_hutch}")
    print(f"\n  {'op':<4}{'on_z':>9}{'off_z':>9}{'discr_z':>9}{'t':>8}{'sig':>5}"
          f"{'peakL':>7}")
    for c in CRYSTAL:
        d = discr_z.get(c)
        if d is None:
            continue
        sig = "✓" if d["significant"] and d["discr_z"] > 0 else " "
        pk = peak.get(c, {}).get("layer", "-")
        print(f"  {c:<4}{d['on_mean']:>9}{d['off_mean']:>9}{d['discr_z']:>9}"
              f"{(d['t'] or 0):>8}{sig:>5}{pk!s:>7}")
    print(f"\n  instrument check (C/K/Y discriminate in curvature): {instr}")
    print(f"  ★ B discriminates in the CURVATURE register: "
          f"{b_in_curvature}  (B discr_z={b.get('discr_z')}, t={b.get('t')})")
    print("═" * 74 + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    out = {"verdict": verdict, "per_probe": per_probe,
           "crystal_layers": crystal_layers}
    (RESULTS_DIR / f"jacobian_v7_verdict_{slug}.json").write_text(
        json.dumps(_json_safe(out), indent=2), encoding="utf-8")
    meta = {
        "model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "transformers_version": _transformers_version(),
        "n_layers": n_layers, "n_perm": n_perm, "ppc": ppc, "heldout_per": heldout,
        "n_hutch": n_hutch, "n_calib": len(calib), "n_test": len(test),
        "register": "CURVATURE diag Hessian dL2/d gate_proj2, pooled supervised, "
                    "Hutchinson",
    }
    (RESULTS_DIR / f"jacobian_v7_meta_{slug}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[curv] wrote {RESULTS_DIR}/jacobian_v7_verdict_{slug}.json")


if __name__ == "__main__":
    main()
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && ls mementum/knowledge/explore/ | grep -i opcode; echo \"---grep s235 in opcode page---\"; grep -n \"s235\\|prong 1c-ii\\|off-diagonal\\|off-diag\\|Jacobian\\|Hessian\\|curvature\" mementum/knowledge/explore/vsm-opcode-monitor.md | head -40"
}
```

**Summary:** $ ls mementum/knowledge/explore/ | gr...

**Output:**
```
Exit code: 0
Stdout:
vsm-opcode-monitor.md
---grep s235 in opcode page---
562:FIRST-ORDER gradient (a centroid in gradient space), NOT the chain-rule/Jacobian
565:"B = chain rule" is a JACOBIAN / second-order probe (prong 1c-ii), not a first-order
569:## v5 lead 2d prong 1c-ii — the SECOND-ORDER / CURVATURE register (BUILT + RAN, s235)
571:Michael (s235): "proceed with 1" — the Jacobian / second-order probe, the PROPER test of
583:the curvature carries the quadratic form `g'ᵀ(…)g'` — the literal product-of-derivatives
587:`diag(H)_a = E_v[v_a (Hv)_a]`, `v ~ Rademacher` over all gate tensors (off-diagonal cross-
592:### ★ s235 v5 lead 2d prong 1c-ii VERDICT (Qwen3-14B, curvature register, n=20/comb; λ measure, THREE-sided)
594:**(1) ❌ STRICT — B does NOT reach significance in curvature either** (discr_z +0.118,
600:second-order curvature(v7) **t=+1.90** (on +0.045 > off −0.073). B is at its strongest signal
604:**(3) ✅✅ INTERNAL CONSISTENCY (the structural win) — the curvature register reweights the
609:| **I** (identity, `Ix=x`) | LINEAR → zero curvature | 3.83 | 1.02 | **0.68** | monotone DOWN ↓ |
617:DOMINATES** the curvature register (t=4.53). The composers {B,C} hold/rise; the selectors
625:n_hutch=4 (Hutchinson diagonal estimate noise); **DIAGONAL Hessian only** — the off-diagonal /
626:interlayer-Jacobian cross-coupling (the literal f∘g coupling, `dgate_late/dgate_early`) is
643:  backward pass. Measures FIRST-ORDER gradient, NOT the chain-rule/Jacobian structure.
644:- **★ lead 2d prong 1c-ii — DONE (s235):** SECOND-ORDER / curvature register (diag Hessian,
651:  interlayer Jacobian (diag-Hessian only captures g'ᵀ(diag)g'; the literal f∘g coupling lives
652:  off-diagonal — Gauss-Newton / JVP probe); (3) prong 2 trace-order.
657:  order?** Michael (s235): "if B is an ordering of operations then maybe it defaults to the
669:  signal where B is the UNMARKED baseline). ★ **UNIFIES with prong 1c-ii:** composition has two
671:  2nd-order (curvature climb, t=1.90). B = chain rule (gradient) AND native order (forward).
675:  prose-rendered order-cost, the off-diagonal Jacobian (prong 1c-ii path).
700:  order (nested = its complement). Next: cross-model flat (8B full-n=24 / 32B), off-diagonal
701:  Jacobian (prong 1c-ii path).
710:  cross-class (OLMo/Pythia) untested. Next: off-diagonal Jacobian; 3rd render frame; cross-class.
721:  Next: off-diagonal Jacobian; 3rd render frame (also tests if the single-step minpair sharpens
773:| `results/kernel-reference-audit/gradient_v6_verdict_qwen3-14b.json` | s234 v5 lead 2d prong 1c verdict: ❌ B does NOT discriminate in the gradient (discr_z +0.13, t=1.07 n.s.) — chain-rule NOT supported (first-order); ⚠️ but B "less absent" than any activation read (act t=−0.05 → grad +1.07, faint positive); {C,K,Y} discriminate (instrument works), C-yes/B-no persists. Measures first-order gradient NOT Jacobian |
774:| `scripts/experiments/kernel_reference_jacobian_v7.py` | s235 v5 lead 2d prong 1c-ii: SECOND-ORDER / curvature register — DIAGONAL HESSIAN of LM-CE w.r.t. gate_proj (Hutchinson `diag(H)=E_v[v⊙Hv]`, double-backward of g·v with create_graph), pooled over supervised positions; clean register-swap of v6, same RelationalCrystalClassifier + raw-z Welch; `--n-hutch` |
775:| `results/kernel-reference-audit/jacobian_v7_verdict_qwen3-14b.json` | s235 v5 lead 2d prong 1c-ii verdict: ❌ B not significant in curvature (discr_z +0.118, t=1.90 < 2.0) BUT ✅ MONOTONIC CLIMB with derivative order (act −0.05 → grad +1.07 → curv +1.90, B's best ever, ON the bar) + ✅✅ internal consistency (I=linear COLLAPSES 3.83→0.68 mirror of B; Y=recursion DOMINATES 4.53; composers hold, selectors fade). Derivative ORDER = real axis; B sorts UP. Diag-Hessian only (off-diag untested), power-limited n=20/comb |
777:| `results/kernel-reference-audit/order_cost_v8_verdict_qwen3-14b.json` | s236 v5 lead 2d prong 2 verdict (DECISIVE): ✅✅ **b_is_native_order=True** — clean atom B-vs-C minimal pair t=−7.02 (n=24); B atom-surprisal 0.81 ≪ C 2.14/S 2.66/W 2.71; B cheaper than every permute/copy (B<S −11.3, B<C-multi −11.7, B<W −14.5); pooled order-preserving<breaking. RESOLVES the B gap (composition=free autoregressive default, unmarked) + UNIFIES with curvature climb (order face + gradient face) — `1e448e4` |
```

### Thinking

I'm looking at the relevant section of the knowledge page to understand the s235 verdict and how the off-diagonal path design works.

## Assistant

Let me read the full s235 verdict section and the off-diagonal path notes in the knowledge page.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/vsm-opcode-monitor.md",
  "line_offset": 555,
  "limit": 170
}
```

**Summary:** Reading vsm-opcode-monitor.md (555-725)

**Output:**
```
(on_z −0.03 > off −0.16). A faint positive trend in the predicted direction, power-limited
(n=20/comb), short of significance. Register-specific shifts: S flips gauge→ANTI (t=−2.01),
I drops out (act t=3.83 → grad 1.02); the gradient discriminable set is {C,K,Y} (vs the
activation {C,I,K,Y}).

**★ MEASUREMENT CAVEAT (λ measure, load-bearing):** this measures B's signature in the
FIRST-ORDER gradient (a centroid in gradient space), NOT the chain-rule/Jacobian
composition structure itself (composition = a PRODUCT of derivatives = a second-order
property). The faint positive trend means the idea is not dead — but the proper test of
"B = chain rule" is a JACOBIAN / second-order probe (prong 1c-ii), not a first-order
gradient centroid. Caveats: 1 model (14B), n=20/comb, pooled-supervised locus, single-
combinator labels, first-order gradient only.

## v5 lead 2d prong 1c-ii — the SECOND-ORDER / CURVATURE register (BUILT + RAN, s235)

Michael (s235): "proceed with 1" — the Jacobian / second-order probe, the PROPER test of
B=chain-rule. Prong 1c read the FIRST-ORDER gradient ∂L/∂gate (faint +1.07 n.s.), but the
first-order gradient is a SINGLE factor / a sum over paths — it washes out the PRODUCT
structure that IS the chain rule. B = `B f g x = f(g x)` = composition; its backward
signature `d(f∘g)/dx = f'(g x)·g'(x)` is a PRODUCT of derivatives = a SECOND-ORDER quantity.
For `L = ℓ(f(g(z)))` with `z` = the gate activation,

```
dL/dz   = g'(z)ᵀ f'(g)ᵀ ℓ'                         # first order (v6 read this)
d²L/dz² = g'ᵀ [f''(g)·ℓ'] g'  +  (ℓ'f') g''        # SECOND order — the product g'ᵀ(…)g'
```

the curvature carries the quadratic form `g'ᵀ(…)g'` — the literal product-of-derivatives
chain-rule signature the first-order gradient cannot show. Clean register-swap of v6: same
RelationalCrystalClassifier (sign-CMR, crosstask null, raw-z Welch), feature = the DIAGONAL
HESSIAN of the probe LM-CE w.r.t. gate_proj, Hutchinson estimator
`diag(H)_a = E_v[v_a (Hv)_a]`, `v ~ Rademacher` over all gate tensors (off-diagonal cross-
coord/cross-layer terms cancel because `E[v_a v_b]=0`, a≠b); one HVP = a double-backward of
the scalar `g·v` where `g = grad(CE, gates, create_graph=True)`; pooled over supervised
positions, `n_hutch=4`. `kernel_reference_jacobian_v7.py`.

### ★ s235 v5 lead 2d prong 1c-ii VERDICT (Qwen3-14B, curvature register, n=20/comb; λ measure, THREE-sided)

**(1) ❌ STRICT — B does NOT reach significance in curvature either** (discr_z +0.118,
**t=1.90 < 2.0**). The chain-rule hypothesis is NOT confirmed at the significance bar; B's
gap survives into the second order.

**(2) ✅ DIRECTIONAL — the MONOTONIC CLIMB WITH DERIVATIVE ORDER, exactly as chain-rule
predicts:** B activation(v2) **t=−0.05** → first-order gradient(v6) **t=+1.07** →
second-order curvature(v7) **t=+1.90** (on +0.045 > off −0.073). B is at its strongest signal
EVER, in the PREDICTED register, sitting right ON the 2.0 threshold — power-limited
(n=20/comb), **not absent**.

**(3) ✅✅ INTERNAL CONSISTENCY (the structural win) — the curvature register reweights the
combinators EXACTLY as the math demands:**

| combinator | role | act (v2) | grad (v6) | **curv (v7)** | reads as |
|---|---|---|---|---|---|
| **I** (identity, `Ix=x`) | LINEAR → zero curvature | 3.83 | 1.02 | **0.68** | monotone DOWN ↓ |
| **B** (composition, `Bfgx=f(gx)`) | composer, product-of-derivs | −0.05 | +1.07 | **+1.90** | monotone UP ↑ |
| **C** (composer) | composer | 5.7 | 2.27 | **2.52 ✓** | holds |
| **Y** (recursion, self-application) | higher-order | 8.4 | 3.87 | **4.53 ✓** | dominates |
| **K** (selector) | selector | 3.3 | 2.88 | **1.94** | fades to bar |

**I (the LINEAR combinator) COLLAPSES monotonically** down the derivative-order axis — the
exact MIRROR IMAGE of B's climb. **Y (recursion = self-application = inherently higher-order)
DOMINATES** the curvature register (t=4.53). The composers {B,C} hold/rise; the selectors
{K,I} fade. The second-order register preferentially carries COMPOSITION/RECURSION structure
(s127 {B,C}=composers) and SHEDS the linear combinator. **The two opposite monotones (B↑
with order, I↓ with order) are the signature: derivative ORDER is a real axis the combinators
sort along, and B sorts UP it while the linear combinator sorts DOWN.** Instrument WORKS
(C ✓, Y ✓). Curvature discriminable set {C,Y} (K, B at the bar).

**Caveats (λ measure):** 1 model (14B); n=20/comb (B sits ON the bar — power-limited);
n_hutch=4 (Hutchinson diagonal estimate noise); **DIAGONAL Hessian only** — the off-diagonal /
interlayer-Jacobian cross-coupling (the literal f∘g coupling, `dgate_late/dgate_early`) is
UNTESTED; single-combinator labels; pooled-supervised locus. Mac (no CUDA) → MPS/CPU
double-backward, ~9 min main:1.

### v5 — next steps

- **★ lead 2d prong 1 — DONE (s234):** raw-z contrast rescues K + sharpens C/I, kills the
  B false-positive; B/D/W gap is GENUINE at last-token. Discriminable set {C,I,K,Y}.
- **★ lead 2d prong 1b — DONE (s234):** per-token read FALSIFIES the token-locus
  explanation — B flat at ALL positions (max t=0.68 n.s.). Register property, not locus.
- **★ lead 2d prong 1b-ii — DONE (s234):** value-register read FALSIFIES the s127
  "B→attention" prediction — B flat in attention TOO (max t=0.49 n.s.). Register exhausted.
  **Discriminability is a COMBINATOR property ({C,I,K,Y} read in both registers), not a
  register split.**
- **★ lead 2d prong 1c — DONE (s234):** GRADIENT register — B does NOT discriminate
  (t=1.07 n.s.) but is "less absent" than in any activation read (act t=−0.05 → grad
  t=+1.07, faint positive trend); {C,K,Y} discriminate; C-yes/B-no persists into the
  backward pass. Measures FIRST-ORDER gradient, NOT the chain-rule/Jacobian structure.
- **★ lead 2d prong 1c-ii — DONE (s235):** SECOND-ORDER / curvature register (diag Hessian,
  Hutchinson). ❌ B not significant (t=1.90 < 2.0) BUT ✅ a clean MONOTONIC CLIMB with
  derivative order (act −0.05 → grad +1.07 → curv +1.90, B's best ever, in the predicted
  register, ON the bar) + ✅✅ internal consistency (I=linear COLLAPSES 3.83→0.68 = mirror of
  B; Y=recursion DOMINATES 4.53; composers hold, selectors fade). Derivative ORDER is a real
  axis combinators sort along; B sorts UP it. Power-limited (n=20/comb). Three live follow-ups:
  (1) POWER (raise n / n_hutch — does t=1.90 cross 2.0? cheapest decisive); (2) OFF-DIAGONAL /
  interlayer Jacobian (diag-Hessian only captures g'ᵀ(diag)g'; the literal f∘g coupling lives
  off-diagonal — Gauss-Newton / JVP probe); (3) prong 2 trace-order.
- **★ lead 2d prong 1b-iii — DONE (s234):** per-head OV scan — head-dilution only MARGINAL
  (B faint signal at L17H23, 7/1600 cells) but B is the WEAKEST combinator at every
  granularity; no clean B-composer head. Register hypothesis FULLY EXHAUSTED.
- **★ lead 2d prong 2 — DONE (s236):** ORDER-COST register — **is B the NATIVE softmax-over-V
  order?** Michael (s235): "if B is an ordering of operations then maybe it defaults to the
  order the softmax over all V uses natively?" (ffn-reduction-trace: softmax-over-V IS the
  execution order). NO amplitude classifier — pure surprisal (mean −log p under LM softmax over
  V) of the CERTIFIED reduction trace, teacher-forced "t0 -> t1 -> ... -> tn". Minimal pairs
  ("B f a b → f (a b)" kept vs "C f a b → f b a" swapped) + multi-step composites; ATOM-ONLY
  de-confound (drop parens/length) = headline. **★ DECISIVE at 14B (n_each=24): b_is_native_
  order=True — clean atom B-vs-C minimal pair t=−7.02; B atom-surprisal 0.81 ≪ C 2.14 / S 2.66
  / W 2.71; B cheaper than every permute/copy combinator (B<S −11.3, B<C-multi −11.7, B<W
  −14.5); pooled order-preserving < breaking.** ⚠️ POWER-LIMITED at 8B smoke (n=8): same
  DIRECTION, headline n.s. (t=−0.55), multi-step already sig — crisp only at full power.
  ★ **RESOLVES the B gap:** B's amplitude-absence everywhere is NOT weakness — composition =
  the FREE autoregressive default, carries no marked feature (the instrument looked for a marked
  signal where B is the UNMARKED baseline). ★ **UNIFIES with prong 1c-ii:** composition has two
  faces — token-side the native order (cheap surprisal, t=−7.02), gradient-side the product/
  2nd-order (curvature climb, t=1.90). B = chain rule (gradient) AND native order (forward).
  Caveat (load-bearing): BARE SYMBOLIC input (cf lead 2) — bare-symbol surprisal may reflect a
  generic copy/induction preference for source-order atoms (which IS the proposed mechanism);
  prose-bridge re-read kills it. Next: cross-model (8B full-n / 32B — universal or 14B-specific?),
  prose-rendered order-cost, the off-diagonal Jacobian (prong 1c-ii path).
- **★ lead 2d prong 2b — PROSE BRIDGE — DONE (s237):** re-ran the order-cost read on the SAME
  certified traces RENDERED AS PROSE (deterministic, order-faithful: `App(f,x)` →
  "`<f> applied to <x>`", atoms → fixed content words) to kill the prong-2 bare-symbol caveat
  (s233: the register reads PROSE SEMANTICS not CL SYNTAX; bare-symbol surprisal may reflect a
  generic copy/induction preference). Used a DETERMINISTIC renderer, NOT the model decompile
  gate — the model must not choose word order (= the variable under test). **★ THE NESTING
  CONFOUND (discovered + controlled):** B's normal form NESTS (`f (a b)`) while C's is FLAT
  (`f b a`); the atom-only de-confound strips parens from MEASUREMENT but the bracketing remains
  in the CONTEXT predicting the atoms. So `--render-mode` = `flat` (linearise leaves, NO parens
  → B/C identical structure, differ ONLY in atom ORDER — the pure order test) vs `nested`
  (structurally faithful, CONFOUNDED by nesting depth). **★★ DECISIVE (the cross-table):**
  B-vs-C atom minpair — 14B flat **t=−8.05 (B<C ✓)** ≈ symbolic v8 −7.02; 14B nested **t=+11.9
  (B>C, REVERSED)**; 8B flat −0.57 n.s. (dir B<C) ≈ symbolic 8B −0.55; 8B nested +3.17
  (reversed). **SAME 14B model + SAME 216 programs, flip the render → flip the sign** = a DIRECT
  demonstration that nesting was confounding; once held constant (flat), B<C decisively. ✅ flat
  prose REPLICATES the symbolic pattern at BOTH scales (14B decisive, 8B directional-n.s. with
  multi-step already sig B<C-multi t=−10.6 / B<K −7.5 / B<W −7.6) = CONVERGENCE across input
  modality (symbols ⊗ prose). **★ THE s236 CAVEAT IS KILLED:** composition-order preference is
  real in the SEMANTIC register, not a bare-symbol copy artifact. ★ REFINED FINDING: B's normal
  form carries TWO separable real quantities — atom ORDER (preserved → cheap; the native-order
  result) and structural NESTING (deeper → atoms predicted inside fresh clauses cost more,
  dominates when nesting varies). The order claim REQUIRES isolating order from nesting (flat).
  Caveats (λ measure): 1 model class (Qwen), 14B decisive / 8B power-limited (2 scale points);
  deterministic "applied to" frame; flat deliberately discards faithful structure to isolate
  order (nested = its complement). Next: cross-model flat (8B full-n=24 / 32B), off-diagonal
  Jacobian (prong 1c-ii path).
- **★ lead 2d prong 2b CROSS-MODEL — DONE (s237 cont.): B-NATIVE-ORDER IS UNIVERSAL across the
  Qwen3 scale ladder (8B/14B/32B, all flat n=24).** B-vs-C atom minpair: **8B t=−2.87 ✓**
  (CROSSES at full power — was −0.57 n.s. at the n=8 smoke, confirming "power-limited not
  absent"), **14B t=−8.05 ✓** (strongest), **32B t=−4.48 ✓**. ALL three: b_is_native_order=True,
  every one of the 6 contrasts B<marked sig, pooled preserve ≪ break (8B atoms B 0.39≪C 1.61;
  32B B 0.36≪C 1.23). ★ Unlike the C-locus (s232 shifts with scale), the ORDER-COST signal is
  SCALE-ROBUST — composition rides the native autoregressive order at every scale (not strictly
  monotone, 14B strongest, but all positive+significant). Caveat: still 1 model CLASS (Qwen) —
  cross-class (OLMo/Pythia) untested. Next: off-diagonal Jacobian; 3rd render frame; cross-class.
- **★ lead 2d prong 2b CROSS-CLASS — DONE (s237 cont., path 3): the ORDER PREFERENCE replicates
  across 3 MODEL CLASSES, but the STRICT single-step headline is Qwen-SPECIFIC.** OLMo-2-13B +
  Gemma-4-31B-it (instruct), flat n=24: BOTH b_is_native_order=False on the strict single-step
  B-vs-C atom minpair (OLMo t=−1.25 d=−0.07; Gemma t=−0.56 d=−0.52, n.s.) — the cleanest
  f-a-b ↔ f-b-a swap is near-SYMMETRIC off-Qwen. BUT both STRONGLY confirm B<marked on the
  COMPOSITE + aggregate (B-vs-C-multi OLMo t=−24.4 / Gemma −11.6, both sig; 4-5/6 contrasts sig
  B-cheaper; pooled-atoms preserve ≪ break both: OLMo 0.62≪1.08, Gemma 10.2≪14.0). ⇒ GROSS
  "composition is the native order" is UNIVERSAL (Qwen ⊗ OLMo ⊗ Gemma); its SHARPEST single-step
  expression is family-dependent (Qwen-sharp). CAVEAT: Gemma INSTRUCT-tuned, OOD synthetic prose
  → huge absolute surprisals (B atoms 9.9 vs Qwen ~0.3), noisier (within-model contrasts valid).
  Next: off-diagonal Jacobian; 3rd render frame (also tests if the single-step minpair sharpens
  off-Qwen under a different frame).
- **★ lead 2d prong 3 (per-model sweep):** run `kernel_reference_prose_v2.py` on 8B/32B
  with the raw-z contrast — does the {C,I,K,Y} discriminable set hold across scale?
- **bigger lambda probe set** — 5 sentences underpowers the lead-1 frac test (32B

[CONTENT TRUNCATED] Showing lines 556 to 725 of 786 total lines. Use line_offset=725 parameter to read more content.
```

### Thinking

Now I'm designing the off-diagonal Jacobian probe to capture the cross-coupling between layers—specifically the composition `f∘g` that the diagonal Hessian alone couldn't reveal. The key is examining how changes in early gates propagate through late gates via the interlayer Jacobian structure.

I'm considering two measurement approaches: either injecting a perturbation at an early gate and tracking how it flows to a late gate via JVP, or directly probing the off-diagonal Hessian block to capture the cross-layer coupling that the diagonal-only measurement zeroed out.

The challenge is that measuring all layer-pair couplings is expensive, so I'd need to pool them. But I'm realizing the cleanest path is to reuse the existing per-layer feature framework — instead of a single-layer feature, define each layer's feature as a cross-layer coupling vector that encodes how it depends on other layers, keeping the same RelationalCrystalClassifier instrument intact. The cleanest approach is to perturb only the early-layer gates with a Rademacher vector, compute the full Hessian-vector product, and read the response at the late layers — this directly captures the off-diagonal cross-coupling between layers without needing the diagonal component, since the perturbation is zero at those late positions. It's a single HVP computation like v7, just with structured sparsity in the perturbation vector and reading the response on a different layer block. I'm realizing the averaging trick won't work here—taking the expectation of `(Hv)` over zero-mean Rademacher draws just gives zero, which defeats the purpose. The diagonal Hutchinson estimator works because it's quadratic in `v`, so the expectation is nonzero, but for the off-diagonal cross-layer coupling I need a similar quadratic structure to get a stable per-layer feature vector.

The cleanest approach would be to use two fixed directions instead of random ones—specifically, measuring how the early-layer gradient couples through the Hessian to the late-layer gradient via `g_late ᵀ H_{late,early} g_early`. But that gives me a scalar per layer pair, not the per-layer [d]-dimensional feature the instrument needs. I'm stuck between wanting a matrix-like measurement of coupling and needing a vector-shaped feature for the crystal centroid construction.

Let me think about this differently: the real question is whether composition shows up as cross-layer coupling that the diagonal-only read would miss. The most direct way to capture that is through interlayer Jacobian coupling—how much perturbing the early gate changes the late gate. I can measure this with a Frobenius norm via Hutchinson estimation on the Jacobian, which gives me a clean scalar per probe that won't cancel out in expectation the way cross-terms do.

But this approach loses the per-layer structure and the relational crystal machinery, and it requires forward-mode differentiation which might not be tractable. Plus, the real signal might not be in the magnitude at all—B might be unmarked in amplitude, so the off-diagonal structure and alignment with the composition direction matters more than raw coupling strength. I'm overcomplicating this. I should step back and think about what I'm actually testing, what the minimal faithful probe is, and what's feasible to run, maybe check what the RelationalCrystalClassifier expects and whether I can feed it per-layer scalars instead of vectors.

Let me look at the classifier interface and trace how features flow through the gradient v6 design, so I can make v8 a clean register-swap that captures the off-diagonal interlayer cross-coupling the user identified in the s237 fork.

## Assistant

This is the off-diagonal / interlayer-Jacobian path — the literal `f∘g` cross-layer coupling that the v7 diagonal Hessian cancelled in expectation. Let me ground the design by reading the classifier interface and the v6 gradient script (the cleanest register-swap template).

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/instruments/relational_opcode.py"
}
```

**Summary:** Reading relational_opcode.py (0-2000)

**Output:**
```
#!/usr/bin/env python3
# register: topological/routing
"""Relational crystal opcode classifier — the VALIDATED upgrade (s231, audit-aware).

THE OVER-READ THIS FIXES (audit-meta-pattern.md, s202→s206):
  "combinator opcodes: prose fires opcodes AFTER common-mode removal (p=0.001) — REAL;
   raw argmax 'tracer' = common mode = false signal."
The legacy opcode_instrument projects the FFN down-proj output onto per-op fingerprints
with RAW cosine + argmax — no register discipline, no common-mode removal, no null. It
MANUFACTURES crisp opcodes (the instrument that found the structure also faked its
crispness). This classifier replaces that with the validated read:

  1. REGISTER  — classify in the GATE routing register (sign(gate)-CMR), where the
     combinator crystal actually lives (s203 sign-topology ONLY in gate_proj; s231 the
     routing register = sign(gate)-CMR). Requires a GATED MLP (SwiGLU/GeGLU).
  2. COMMON-MODE — subtract the per-layer calibration common-mode before projecting
     (the s202 fix; the gauge that inflates every raw cosine).
  3. RELATIONAL — project onto per-combinator centroids built from the crystal probes;
     report which layers are crystal-bearing by Gram alignment to the CONSENSUS crystal
     (results/combinator-map-consensus/consensus.json, the s219 universal target).
  4. NULL — every per-op energy is a z-score vs an off-target permutation null; a token
     emits an opcode ONLY if z>thresh, else NO-OP (kills "argmax always picks winner").

DESIGN: model-AGNOSTIC. calibrate() and classify() take per-layer gate FEATURE matrices
(the caller runs the model + captures gate); the numpy science is unit-testable on
synthetic data with planted structure, no model load. The instrument (which already
hooks the gate) feeds it; the validation harness feeds it from a real HF forward pass.

CRYSTAL-9 = K I B C S D W Y WHNF (aligns with the consensus Gram order).

License: MIT
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

CRYSTAL = ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONSENSUS_PATH = (_PROJECT_ROOT / "results" / "combinator-map-consensus"
                  / "consensus.json")


# --------------------------------------------------------------------------- #
# numpy crystal instruments (inlined; mirror relational_loss_distillation)      #
# --------------------------------------------------------------------------- #
def _unit_rows(X: np.ndarray) -> np.ndarray:
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-30)


def _centroids(X: np.ndarray, labels: np.ndarray) -> np.ndarray:
    C = np.zeros((len(CRYSTAL), X.shape[1]), np.float64)
    for j, c in enumerate(CRYSTAL):
        m = labels == c
        if m.any():
            C[j] = X[m].mean(axis=0)
    return C


def _gram(C: np.ndarray) -> np.ndarray:
    U = _unit_rows(C)
    return np.clip(U @ U.T, -1, 1)


def _offdiag_corr(a: np.ndarray, b: np.ndarray) -> float:
    off = ~np.eye(len(CRYSTAL), dtype=bool)
    x, y = a[off], b[off]
    if x.std() < 1e-9 or y.std() < 1e-9:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def _silhouette(X: np.ndarray, labels: np.ndarray) -> float:
    U = _unit_rows(_centroids(X, labels))
    Xu = _unit_rows(X)
    sims = Xu @ U.T
    li = np.array([CRYSTAL.index(c) for c in labels])
    rows = np.arange(len(labels))
    own = sims[rows, li]
    other = sims.copy()
    other[rows, li] = -np.inf
    return float(np.mean(own - other.max(axis=1)))


def _silhouette_z(X: np.ndarray, labels: np.ndarray, n_perm: int,
                  rng: np.random.Generator) -> float:
    obs = _silhouette(X, labels)
    null = np.array([_silhouette(X, rng.permutation(labels)) for _ in range(n_perm)])
    return float((obs - null.mean()) / (null.std() + 1e-30))


def load_consensus_gram() -> np.ndarray | None:
    if not CONSENSUS_PATH.exists():
        return None
    d = json.loads(CONSENSUS_PATH.read_text())
    if list(d.get("crystal_order", [])) != CRYSTAL:
        return None
    return np.array(d["consensus_gram"], dtype=np.float64)


# --------------------------------------------------------------------------- #
@dataclass
class LayerCalib:
    """Per-layer calibration: the common-mode, centroids, and the null."""
    common_mode: np.ndarray                 # [d] mean sign(gate) over calib probes
    centroids: np.ndarray                   # [9, d] unit per-combinator centroids (CMR)
    null_mean: np.ndarray                   # [9] null projection mean per op
    null_std: np.ndarray                    # [9] null projection std per op
    silhouette_z: float                     # crystal significance at this layer
    gc_consensus: float                     # Gram alignment to consensus (or nan)
    crystal_bearing: bool                   # sil_z>thresh (∧ gc>0 if consensus present)
    null_kind: str = "offtarget"            # "offtarget"(crystal) | "crosstask"


@dataclass
class TokenOpcodes:
    """One token's per-layer opcode read."""
    per_layer: dict = field(default_factory=dict)   # li -> {op: z}
    emitted: dict = field(default_factory=dict)      # li -> [significant ops]
    dominant: str = "·"                              # max-z op (crystal) or no-op


class RelationalCrystalClassifier:
    """Validated FFN-routing opcode reader: gate register, sign-CMR,
    consensus-relational, null-calibrated. Model-agnostic (gate feature matrices in)."""

    def __init__(self, layers: list[int], *, n_perm: int = 300, z_thresh: float = 3.0,
                 sil_z_thresh: float = 2.0, seed: int = 0,
                 consensus_gram: np.ndarray | str | None = "auto"):
        self.layers = list(layers)
        self.n_perm = n_perm
        self.z_thresh = z_thresh
        self.sil_z_thresh = sil_z_thresh
        self.seed = seed
        # "auto" -> load the project consensus; None -> disable (synthetic/no-target);
        # ndarray -> use as given.
        self.consensus_gram = (load_consensus_gram()
                               if isinstance(consensus_gram, str)
                               else consensus_gram)
        self.calib: dict[int, LayerCalib] = {}

    # -- S5 calibration: build the per-layer crystal from the probe activations -- #
    def calibrate(self, gate_by_layer: dict[int, np.ndarray],
                  labels: np.ndarray,
                  null_gate_by_layer: dict[int, np.ndarray] | None = None,
                  ) -> dict[int, LayerCalib]:
        """gate_by_layer[li] = [N, d] gate last-token features for the N crystal probes;
        labels [N] in CRYSTAL. Build per-layer common-mode, CMR centroids, the null,
        silhouette-z, and consensus Gram alignment.

        NULL (s231 v2 — the over-read-killer that no longer under-reads):
          - null_gate_by_layer=None (default, BACK-COMPAT): off-target null — per op j
            the null is the projection of NON-j crystal probes onto j's centroid. But
            every crystal probe is lambda-mode, so "looks more like B than K/I/C?" has
            LOW POWER (the s231 under-read: the C→B arc no-ops at z=3).
          - null_gate_by_layer[li] = [M, d] NON-combinator baseline gate features (e.g.
            natural-text / retrieval tokens where no β-reduction happens): CROSS-TASK
            null — per op j the null is the projection of BASELINE tokens onto j's
            centroid (through the SAME sign-CMR transform). Then z asks "does this token
            look more like op j than a typical natural-text token does?" — recovers the
            lambda compose-arc while keeping retrieval silent."""
        labels = np.asarray(labels)
        rng = np.random.default_rng(self.seed)
        null_kind = "crosstask" if null_gate_by_layer is not None else "offtarget"
        for li in self.layers:
            G = np.asarray(gate_by_layer[li], dtype=np.float64)
            S = np.sign(G)
            common = S.mean(axis=0)                       # the common-mode (gauge)
            X = S - common                                # sign-CMR routing features
            cents = _centroids(X, labels)
            ucents = _unit_rows(cents)
            Xu = _unit_rows(X)
            sims = Xu @ ucents.T                          # [N, 9] cos to each centroid
            li_idx = np.array([CRYSTAL.index(c) for c in labels])
            nmean = np.zeros(len(CRYSTAL))
            nstd = np.ones(len(CRYSTAL))
            if null_gate_by_layer is not None:
                # CROSS-TASK null: project baseline (non-combinator) tokens through the
                # SAME sign-CMR transform onto each centroid; the per-op population is
                # the natural-text baseline distribution.
                B = np.asarray(null_gate_by_layer[li], dtype=np.float64)  # [M, d]
                Vb = np.sign(B) - common                                  # CMR baseline
                Vbu = _unit_rows(Vb)
                bsims = Vbu @ ucents.T                                    # [M, 9]
                for j in range(len(CRYSTAL)):
                    col = bsims[:, j]
                    nmean[j] = col.mean()
                    nstd[j] = col.std() + 1e-9
            else:
                # off-target null per op: projection of NON-op probes onto op centroid
                for j in range(len(CRYSTAL)):
                    off = sims[li_idx != j, j]
                    if off.size:
                        nmean[j] = off.mean()
                        nstd[j] = off.std() + 1e-9
            sil_z = _silhouette_z(X, labels, self.n_perm, rng)
            gc = (_offdiag_corr(_gram(cents), self.consensus_gram)
                  if self.consensus_gram is not None else float("nan"))
            bearing = sil_z > self.sil_z_thresh and (np.isnan(gc) or gc > 0.0)
            self.calib[li] = LayerCalib(
                common_mode=common, centroids=ucents, null_mean=nmean, null_std=nstd,
                silhouette_z=round(sil_z, 3),
                gc_consensus=(round(gc, 3) if not np.isnan(gc) else float("nan")),
                crystal_bearing=bool(bearing), null_kind=null_kind)
        return self.calib

    @property
    def crystal_layers(self) -> list[int]:
        return [li for li, c in self.calib.items() if c.crystal_bearing]

    # -- S1 classify: token gate -> null-calibrated per-op z, emit if significant -- #
    def classify(self, gate_by_layer_token: dict[int, np.ndarray]) -> TokenOpcodes:
        """gate_by_layer_token[li] = [d] one token's gate at layer li. Returns per-layer
        op z-scores, the significant (z>thresh) opcodes, and the dominant op across
        crystal-bearing layers (or '·' no-op if none significant)."""
        out = TokenOpcodes()
        best_op, best_z = "·", self.z_thresh
        for li in self.layers:
            cal = self.calib.get(li)
            if cal is None:
                continue
            g = np.asarray(gate_by_layer_token[li], dtype=np.float64)
            v = np.sign(g) - cal.common_mode
            nv = np.linalg.norm(v)
            if nv < 1e-12:
                continue
            sims = cal.centroids @ (v / nv)               # [9] cos to each centroid
            z = (sims - cal.null_mean) / cal.null_std     # null-calibrated per op
            zmap = {op: round(float(zz), 3) for op, zz in zip(CRYSTAL, z, strict=True)}
            out.per_layer[li] = zmap
            sig = [op for op, zz in zmap.items() if zz > self.z_thresh]
            if sig:
                out.emitted[li] = sig
            if cal.crystal_bearing:                       # dominant: crystal only
                j = int(np.argmax(z))
                if z[j] > best_z:
                    best_op, best_z = CRYSTAL[j], float(z[j])
        out.dominant = best_op
        return out

    def calibration_summary(self) -> dict:
        null_kinds = {c.null_kind for c in self.calib.values()}
        return {
            "n_layers": len(self.calib),
            "crystal_layers": self.crystal_layers,
            "per_layer": {li: {"sil_z": c.silhouette_z, "gc_consensus": c.gc_consensus,
                               "crystal_bearing": c.crystal_bearing}
                          for li, c in self.calib.items()},
            "z_thresh": self.z_thresh, "sil_z_thresh": self.sil_z_thresh,
            "has_consensus": self.consensus_gram is not None,
            "null_kind": (next(iter(null_kinds)) if len(null_kinds) == 1
                          else sorted(null_kinds)),
        }


# --------------------------------------------------------------------------- #
# Synthetic smoke — verify the numpy science with planted per-combinator structure #
# --------------------------------------------------------------------------- #
def _smoke() -> None:
    rng = np.random.default_rng(0)
    d, per = 64, 40
    layers = [0, 1, 2]
    # layer 1 = crystal-bearing (planted combinator directions); 0,2 = noise
    dirs = rng.standard_normal((len(CRYSTAL), d))
    labels = np.array([c for c in CRYSTAL for _ in range(per)])
    common = rng.standard_normal(d) * 3.0                 # a strong common-mode (gauge)
    gate_cal = {}
    for li in layers:
        rows = []
        for c in CRYSTAL:
            base = dirs[CRYSTAL.index(c)] if li == 1 else np.zeros(d)
            sig = 2.5 if li == 1 else 0.0
            rows.append(common + sig * base + rng.standard_normal((per, d)))
        gate_cal[li] = np.concatenate(rows, axis=0)
    clf = RelationalCrystalClassifier(layers, n_perm=120, z_thresh=3.0, seed=0,
                                      consensus_gram=None)
    clf.calibrate(gate_cal, labels)
    summ = clf.calibration_summary()
    print("calibration:", json.dumps(summ, indent=2))
    assert 1 in clf.crystal_layers, "planted crystal layer 1 not detected"
    assert 0 not in clf.crystal_layers and 2 not in clf.crystal_layers, \
        "noise layers wrongly flagged crystal-bearing"
    # a 'B' token: common-mode + B direction at layer 1
    tok = {li: (common + (3.0 * dirs[CRYSTAL.index("B")] if li == 1 else 0.0)
                + rng.standard_normal(d) * 0.5) for li in layers}
    res = clf.classify(tok)
    print("B-token dominant:", res.dominant, "| emitted:", res.emitted)
    assert res.dominant == "B", f"expected B, got {res.dominant}"
    # a pure common-mode token (no combinator) -> NO-OP (the over-read killer)
    noop = {li: common + rng.standard_normal(d) * 0.5 for li in layers}
    rn = clf.classify(noop)
    print("common-mode-only token dominant:", rn.dominant, "| emitted:", rn.emitted)
    assert rn.dominant == "·", f"common-mode token should be no-op, got {rn.dominant}"
    print("\n✅ smoke (offtarget null) passed: crystal layer detected, B fires, "
          "common-mode -> no-op")

    # -- CROSS-TASK null (s231 v2): baseline = common-mode-only "natural-text" -- #
    base = {li: np.stack([common + rng.standard_normal(d) * 0.5 for _ in range(per)])
            for li in layers}
    clf2 = RelationalCrystalClassifier(layers, n_perm=120, z_thresh=3.0, seed=0,
                                       consensus_gram=None)
    clf2.calibrate(gate_cal, labels, null_gate_by_layer=base)
    summ2 = clf2.calibration_summary()
    assert summ2["null_kind"] == "crosstask", "cross-task null not recorded"
    assert 1 in clf2.crystal_layers, "planted crystal layer 1 not detected (crosstask)"
    res2 = clf2.classify(tok)
    print("cross-task B-token dominant:", res2.dominant, "| emitted:", res2.emitted)
    assert res2.dominant == "B", f"expected B (crosstask), got {res2.dominant}"
    rn2 = clf2.classify(noop)
    print("cross-task common-mode token dominant:", rn2.dominant)
    assert rn2.dominant == "·", \
        f"common-mode token should be no-op (crosstask), got {rn2.dominant}"
    print("✅ smoke (crosstask null) passed: B fires vs natural-text baseline, "
          "common-mode -> no-op")


if __name__ == "__main__":
    _smoke()
```

### Thinking

I'm grasping the full architecture now—the instrument takes per-layer feature matrices and applies a sign-gated classifier with centroid-based contrast, while the off-diagonal probes require capturing interlayer coupling as stable per-layer features that hold up under averaging. The core challenge is designing how to extract this cross-layer interaction signal at each layer in a way that remains consistent.

The key insight is using the gradient itself as the probe direction rather than random perturbations—when I apply the Hessian to the actual gradient vector, I get both diagonal and off-diagonal contributions, and subtracting out the diagonal block isolates the pure interlayer coupling. This gives me a deterministic, stable [d]-dimensional feature per layer without the noise cancellation issues of random probes. The Hessian-vector product with the gradient as the probe direction captures exactly this gradient-of-gradient-norm behavior, which is what I need to characterize how each layer's parameters couple to the loss through other layers. So the cleanest approach is to define two separate features: the diagonal component using Hutchinson estimation (which cancels off-diagonal terms), and the off-diagonal interlayer contribution computed as the difference between the full Hessian-vector product and its block-diagonal self-term. To get all the block-diagonal self-terms efficiently, I'd compute an HVP where the perturbation vector is the gradient but masked to each layer independently, though that requires multiple passes per layer.

Alternatively, I could run both the v7 diagonal Hutchinson (with Rademacher vectors) and the full deterministic Hessian-vector product with the gradient direction, then compare how much B discriminates in each. If the full version shows stronger discrimination, the difference must come from off-diagonal coupling. But that conflates two changes—the diagonal-versus-full distinction and the Rademacher-versus-gradient direction—so it's not a clean isolation.

The cleaner path is to stay within the Hutchinson Rademacher framework and construct two features: the diagonal (v7's approach) and a second feature that isolates the off-diagonal block response by perturbing only the non-self layer blocks.

For each layer, the off-diagonal coupling is exactly `(Hg)_li − H_{li,li} g_li`—the full Hessian-vector product minus the self-block term. Computing `(Hg)_li` is one HVP with the gradient as the deterministic perturbation. The self-term `H_{li,li} g_li` would require a second HVP with the graph edges between layers severed, which isn't straightforward to implement.

The practical constraint is that per-layer HVPs would require roughly 40 backward passes per probe, and with hundreds of probes across calibration, null, and test sets, that balloons to thousands of backwards passes—far too slow compared to v7's already-lengthy runtime.

Actually, I should step back: the cleanest measurement of interlayer coupling isn't the Hessian off-diagonal at all, but the **interlayer Jacobian** directly—how the late gates change with respect to the early gates, purely first-order in the forward pass. I can compute this via finite-difference JVP: run a clean forward pass to capture baseline gate activations, then run another forward pass where I perturb the early gate output by some direction (either random or the gate's own value), and measure how much the late gates shift. The ratio gives me the interlayer Jacobian without needing any loss or second-order derivatives.

The key insight is that using a random direction averages to zero, so I need a **fixed direction**—either the gate's own activation as the natural direction of computation, or the gradient direction if I want to measure loss-relevant coupling. The s235 note mentions two approaches: **Gauss-Newton** (which builds `G = JᵀHℓJ` to capture the f∘g structure through Jacobian products) or **JVP** (which directly probes how perturbations propagate). I'm leaning toward the JVP approach since it's more direct and doesn't require computing the loss Hessian.

Given how collaborative this project has been—each design choice gets discussed and confirmed—I think I should present a clean recommendation with tradeoffs rather than just executing blindly, especially since this is a genuine fork between Hessian off-diagonal blocks, interlayer Jacobian probes, and Gauss-Newton. Let me design the most tractable version and get a quick confirm before running expensive GPU experiments.

The key insight is using per-layer Rademacher signs (one shared sign across all coordinates in a layer) multiplied by the gradient, which lets me isolate the interlayer coupling in the Hessian without it canceling out in the Hutchinson estimator—the same-layer terms vanish, but cross-layer terms survive because the signs are correlated within block-pairs.

But when I work through the math, the expectation over random signs still kills the off-diagonal terms, leaving only the diagonal. So I need to abandon the randomized approach and instead use a deterministic probe: the gradient itself. I'll compute the full Hessian-vector product `Hg` in one backward pass to capture both diagonal and off-diagonal contributions along the natural loss-relevant direction, then run a separate experiment to isolate just the diagonal component for comparison.

The real question is how to make these two measurements directly comparable. I could compute the diagonal-along-gradient via a second HVP, but that's expensive. Instead, I think the cleanest approach is to design a single decisive experiment that directly measures interlayer coupling using a finite-difference JVP with the gate activations themselves as the probe direction, then split the network into early and late blocks to see how much coupling flows between them. The sign-pattern of how late gates respond to early perturbations is what the classifier actually cares about, making this a robust fingerprint for composition. I'm considering whether to use the gate's own value as the perturbation direction (simpler, forward-only) or the gradient direction (more principled for loss-relevant coupling), and leaning toward offering both as options with gradient as the default, though that requires an additional backward pass.

Now I'm weighing whether to measure the off-diagonal Hessian block directly—which would complete the curvature register progression and capture the missing cross-layer second-order coupling from the chain rule—versus using the Jacobian-vector product for interlayer coupling. The off-diagonal Hessian feels more coherent as a continuation of the monotonic climb from activation to gradient to curvature, so I'm settling on that as v8's core feature.

To isolate the off-diagonal block cleanly, I can split the perturbation vector into early and late layer components, zeroing it out on late layers so that when I compute the Hessian-vector product, only the off-diagonal terms survive. This gives me the pure interlayer Hessian coupling along the gradient direction—exactly what the chain rule product was missing.

The direction matters: in f(g(x)), g acts early and f acts late, so the coupling I'm measuring is how f's curvature depends on g's behavior, which is the early-to-late direction. I could make this configurable, but early-to-late is the natural default since it follows the forward pass order. For the block split, I'd use the midpoint of the network as the boundary between early and late layers.

The classifier only sees features from the late layers, and the null baseline is computed the same way with the same early-block perturbation. Since I'm using the deterministic gradient direction instead of random Hutchinson vectors, I don't need the Hutchinson loop at all—this is both cleaner and faster than v7. I should still check that {C,Y} discriminate and compare B's discriminability score to the v7 diagonal baseline to see if the off-diagonal coupling is significant.

For the second gradient computation, I need `create_graph=True` for the first backward pass, then compute the Hessian-vector product by taking the gradient of the squared gradient norm with respect to the late gates. The scalar is the sum of squared early gradients, and taking its gradient with respect to late gates gives exactly the off-diagonal Hessian coupling I need.

Now I'm setting up the implementation as a clean variant of v7, keeping the same structure: `forward_offdiag` returns per-token off-diagonal coupling matrices for late layers, pooled over supervised positions. I'll name it `kernel_reference_offdiag_v8.py` and follow the same calibration and classification pipeline as before.

Writing the implementation...

## Assistant

I now fully understand the instrument and the v7 curvature register. Let me design and plan.

## Design: v8 — off-diagonal interlayer curvature (prong 1c-iii)

The v7 diagonal Hessian used a Rademacher Hutchinson estimator that **cancels all cross-layer terms in expectation** (`E[v_a v_b]=0`), so it only captured `g'ᵀ(diag)g'`. The literal `f∘g` chain-rule cross term lives in the **off-diagonal block** `H_{late,early} = ∂²L/∂gate_late ∂gate_early`.

**The clean isolation** (stays in the curvature register, deterministic, cheaper than v7):
- Split layers EARLY `[0,k)` = `g`, LATE `[k,L)` = `f` (composition `f(g(x))`: g processed first/early, f applied late).
- Perturb the **gradient direction** but supported only on EARLY: `v = g_early.detach()`, zero on late.
- One double-backward: `s = Σ_{e∈EARLY} (g_e · g_e.detach()).sum()`, `hv = grad(s, gate_late)` → `(Hv)_li = 2 Σ_{e∈EARLY} H_{li,e} g_e` for li∈LATE = **pure off-diagonal** (no `H_{li,li}` term since li∉EARLY). The literal f∘g cross-coupling along the loss-relevant direction.
- Feed `(Hv)_late` as the per-layer `[d]` feature to the *same* `RelationalCrystalClassifier` (sign-CMR, crosstask null, raw-z Welch). Compare `discr_z(B)` to v7's diagonal `t=1.90`.

This is the natural completion of the v2→v6→v7 register progression. Deterministic (no Hutchinson noise), and **isolates exactly the off-diagonal**.

### Thinking

I need to verify how the forward function handles position storage and check the imports are working, then build version 8 by modifying the forward function and adjusting the layer split based on what v7 established.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py",
  "content": "#!/usr/bin/env python3\n# register: SECOND-ORDER / OFF-DIAGONAL interlayer curvature (H_{late,early} of LM CE wrt gate_proj)\n\"\"\"Kernel-ref OFF-DIAGONAL interlayer curvature — is B in the f∘g cross-coupling?\n(s238 lead 2d prong 1c-iii).\n\nB = composition (B f g x = f(g x)). Its backward signature is the chain rule, a PRODUCT\nof derivatives `d(f∘g)/dx = f'(g x)·g'(x)`. Prong 1c-ii (kernel_reference_jacobian_v7.py)\nread the DIAGONAL Hessian of the LM loss w.r.t. the gate activation via a Rademacher\nHutchinson estimator `diag(H)_a = E_v[v_a (Hv)_a]`. That estimator CANCELS every\ncross-coordinate AND cross-layer term in expectation (`E[v_a v_b]=0`, a≠b), so it only\ncaptured the WITHIN-layer quadratic form `g'ᵀ(diag)g'`. B sat right ON the bar there\n(discr_z +0.118, t=1.90 < 2.0) with a clean monotone climb act(−0.05)→grad(+1.07)→\ndiag-curv(+1.90).\n\nBut the LITERAL f∘g coupling is the OFF-DIAGONAL block. For `L = ℓ(f(g(z)))` with the\ngate activation `z` split into an EARLY block `z_e` (≈ g, processed first) and a LATE\nblock `z_l` (≈ f, applied last),\n\n    d²L/dz_l dz_e = the OFF-DIAGONAL Hessian block H_{l,e}    # the chain-rule cross term\n\nis exactly \"how the curvature of the late computation (f) couples to the early\ncomputation (g)\" — the product-of-derivatives the diagonal read threw away.\n\nISOLATION (deterministic, ONE double-backward, NO Hutchinson noise):\n  Perturb the GRADIENT direction supported ONLY on the EARLY block: v = g_e.detach() on\n  EARLY, 0 on LATE. Then for any LATE layer li (li ∉ EARLY),\n\n      (Hv)_li = Σ_{e∈EARLY} H_{li,e} g_e                      # PURE off-diagonal (no H_{li,li})\n\n  because v is zero at li so the diagonal block never enters. Computed as a single HVP:\n      s  = Σ_{e∈EARLY} (g_e · g_e.detach()).sum()             # g_e = grad(CE, gate_e, create_graph)\n      hv = grad(s, [gate_li for li∈LATE])                     # = 2·Σ_e H_{li,e} g_e   (H symmetric)\n  The factor 2 is an overall scale; sign-CMR in the classifier is scale-free.\n\n  The perturbation direction is the GRADIENT (the loss-relevant / backprop direction the\n  chain rule actually propagates), NOT random — a random v would have E[(Hv)_li]=0 and\n  give a zero-mean, unstable per-probe feature. The gradient direction makes the feature\n  deterministic and meaningful (the literal backward composition coupling).\n\nClean register-swap of v7: same RelationalCrystalClassifier (sign-CMR, crosstask null,\nraw-z Welch contrast), same calibrate→classify→discr_z pipeline; the feature is the\nPURE OFF-DIAGONAL interlayer curvature (Hv)_late, pooled over supervised positions. The\nclassifier runs on the LATE layers only (where the feature is defined / off-diagonal).\n\nVERDICT LOGIC (λ measure, two-sided):\n  - B discriminates in the OFF-DIAGONAL where it sat ON the bar in the diagonal (v7\n    t=1.90) → the f∘g chain-rule cross-coupling is B's home; the curvature climb\n    completes off the diagonal. (Compare discr_z(B) to v7's diagonal +1.90.)\n  - B flat off-diagonal too → the curvature register is exhausted at BOTH the diagonal\n    AND the off-diagonal; B's positive signal is the FORWARD order-cost face (prong 2b),\n    not a localizable second-order amplitude.\n  - INSTRUMENT CHECK: {C,Y} (the curvature-discriminable set, v7) should still\n    discriminate in the off-diagonal block, else the read is broken not B-absent.\n\nUsage:\n    uv run python scripts/experiments/kernel_reference_offdiag_v8.py --smoke\n    uv run python scripts/experiments/kernel_reference_offdiag_v8.py            # 14B\n\nLicense: MIT\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport sys\nfrom collections import Counter\nfrom datetime import UTC, datetime\nfrom pathlib import Path\n\nimport numpy as np\n\n_ROOT = Path(__file__).resolve().parent.parent.parent\nsys.path.insert(0, str(_ROOT / \"scripts\" / \"experiments\"))\nsys.path.insert(0, str(_ROOT / \"scripts\" / \"instruments\"))\n\nfrom kernel_reference_prose_v2 import split_probes, welch_t  # noqa: E402\nfrom opcode_monitor_v2 import (  # noqa: E402\n    BASELINE_NULL_SENTENCES,\n    _git_sha,\n    _json_safe,\n    _transformers_version,\n    load_model_and_tokenizer,\n)\nfrom relational_opcode import CRYSTAL, RelationalCrystalClassifier  # noqa: E402\n\nRESULTS_DIR = _ROOT / \"results\" / \"kernel-reference-audit\"\nTEST_COMBINATORS = [\"K\", \"I\", \"B\", \"C\", \"S\", \"D\", \"W\", \"Y\"]\n\n\ndef split_early_late(n_layers: int, split_frac: float) -> tuple[list[int], list[int]]:\n    \"\"\"Partition layers into EARLY (≈ g, processed first) and LATE (≈ f, applied last).\n\n    split_frac = fraction of the stack that is EARLY. LATE = the readable mid-late zone\n    (depth ≥ split_frac) where the combinator crystal lives (s187/s227). The off-diagonal\n    feature is read on the LATE layers (coupling FROM the early block TO each late layer).\n    \"\"\"\n    k = max(1, int(round(n_layers * split_frac)))\n    k = min(k, n_layers - 1)\n    early = list(range(k))\n    late = list(range(k, n_layers))\n    return early, late\n\n\ndef forward_offdiag(prompt, model, tok, torch_mod, early, late):\n    \"\"\"Forward + double-backward; return ({li∈late: off-diag (Hv)_li [T,d]}, n_tok).\n\n    v = g_e.detach() on the EARLY block, 0 on LATE.  (Hv)_li = Σ_{e∈EARLY} H_{li,e} g_e\n    for li ∈ LATE = the PURE off-diagonal interlayer curvature (the chain-rule cross term,\n    no within-layer H_{li,li} because v is zero at li). One HVP = a double-backward of the\n    scalar Σ_e ||g_e||²(detached), where g = grad(CE, gates, create_graph=True). Per-token\n    rows returned (callers pool 0..n_tok-2; the last token feeds only the unsupervised\n    next-token ⇒ its gradient/curvature row ~0).\n    \"\"\"\n    import torch.nn.functional as func\n    all_layers = early + late\n    store: dict[int, object] = {}\n\n    def _cap(li):\n        def _hook(_m, _inp, out):\n            store[li] = out  # live graph tensor (NOT detached)\n        return _hook\n\n    handles = [model.model.layers[li].mlp.gate_proj.register_forward_hook(_cap(li))\n               for li in all_layers]\n    try:\n        inputs = tok(prompt, return_tensors=\"pt\")\n        dev = next(model.parameters()).device\n        inputs = {k: v.to(dev) for k, v in inputs.items()}\n        out = model(**inputs)\n        logits = out.logits[0]               # [T, V]\n        ids = inputs[\"input_ids\"][0]         # [T]\n        t = ids.shape[0]\n        ce = func.cross_entropy(logits[:-1, :], ids[1:], reduction=\"mean\")\n        gates_all = [store[li] for li in all_layers]\n        grads_all = torch_mod.autograd.grad(ce, gates_all, create_graph=True)\n        grad_of = dict(zip(all_layers, grads_all, strict=True))\n        # scalar: Σ_{e∈EARLY} (g_e · g_e.detach()) ⇒ grad wrt LATE gates = 2 Σ_e H_{late,e} g_e\n        scalar = sum((grad_of[e] * grad_of[e].detach()).sum() for e in early)\n        late_gates = [store[li] for li in late]\n        hv_late = torch_mod.autograd.grad(scalar, late_gates, retain_graph=False)\n    finally:\n        for h in handles:\n            h.remove()\n    result = {li: hv_late[j][0].detach().float().cpu().numpy().astype(np.float64)\n              for j, li in enumerate(late)}\n    return result, t\n\n\ndef pooled_supervised(feat_store, late, n_tok):\n    \"\"\"Mean-pool the off-diagonal feature over supervised positions 0..n_tok-2 → {li:[d]}.\"\"\"\n    sup = max(1, n_tok - 1)\n    return {li: feat_store[li][:sup].mean(axis=0) for li in late}\n\n\ndef main() -> None:\n    parser = argparse.ArgumentParser(description=\"Kernel-ref off-diagonal curvature (B)\")\n    parser.add_argument(\"--model\", default=\"Qwen/Qwen3-14B\")\n    parser.add_argument(\"--heldout-per\", type=int, default=20)\n    parser.add_argument(\"--ppc\", type=int, default=25, help=\"calib probes/combinator\")\n    parser.add_argument(\"--null-cap\", type=int, default=300)\n    parser.add_argument(\"--n-perm\", type=int, default=200)\n    parser.add_argument(\"--split-frac\", type=float, default=0.5,\n                        help=\"fraction of the stack that is EARLY (g); LATE = the rest\")\n    parser.add_argument(\"--smoke\", action=\"store_true\")\n    args = parser.parse_args()\n\n    model_name = args.model\n    if args.smoke:\n        if model_name == \"Qwen/Qwen3-14B\":\n            model_name = \"Qwen/Qwen3-0.6B\"\n        heldout, ppc, n_perm, null_cap = 5, 5, 80, 150\n        print(\"[offdiag] SMOKE MODE\")\n    else:\n        heldout, ppc, n_perm, null_cap = (\n            args.heldout_per, args.ppc, args.n_perm, args.null_cap)\n\n    calib, test = split_probes(heldout)\n    kept, counts = [], Counter()\n    for p in calib:\n        if counts[p.combinator] < ppc:\n            kept.append(p)\n            counts[p.combinator] += 1\n    calib = kept\n    print(f\"[offdiag] calib={len(calib)} test={len(test)} ppc={ppc} \"\n          f\"split_frac={args.split_frac}\")\n\n    model, tok, torch_mod = load_model_and_tokenizer(model_name)\n    n_layers = model.config.num_hidden_layers\n    early, late = split_early_late(n_layers, args.split_frac)\n    print(f\"[offdiag] EARLY={early[0]}..{early[-1]} ({len(early)} layers, ≈g)  \"\n          f\"LATE={late[0]}..{late[-1]} ({len(late)} layers, ≈f) — feature read on LATE\")\n\n    # ── calibration: per-probe POOLED off-diagonal centroids (LATE layers) ───────\n    gate_by_layer: dict[int, list] = {li: [] for li in late}\n    labels: list[str] = []\n    for i, p in enumerate(calib):\n        if i % 25 == 0:\n            print(f\"[offdiag]   calib fwd+2bwd {i}/{len(calib)} ...\")\n        fstore, nt = forward_offdiag(p.prompt, model, tok, torch_mod, early, late)\n        pooled = pooled_supervised(fstore, late, nt)\n        for li in late:\n            gate_by_layer[li].append(pooled[li])\n        labels.append(p.combinator)\n    gate_np = {li: np.stack(gate_by_layer[li], axis=0) for li in late}\n    labels_np = np.array(labels)\n\n    # ── null: per-supervised-token off-diagonal feature of natural text ──────────\n    null_by_layer: dict[int, list] = {li: [] for li in late}\n    print(f\"[offdiag] building off-diagonal null ({len(BASELINE_NULL_SENTENCES)} prompts)\")\n    for s in BASELINE_NULL_SENTENCES:\n        fstore, nt = forward_offdiag(s, model, tok, torch_mod, early, late)\n        sup = max(1, nt - 1)\n        for li in late:\n            null_by_layer[li].append(fstore[li][:sup])  # supervised rows\n    null_np = {li: np.concatenate(null_by_layer[li], axis=0)[:null_cap] for li in late}\n\n    rcc = RelationalCrystalClassifier(late, n_perm=n_perm, z_thresh=2.0,\n                                      sil_z_thresh=2.0, consensus_gram=\"auto\")\n    rcc.calibrate(gate_np, labels_np, null_gate_by_layer=null_np)\n    crystal_layers = rcc.crystal_layers\n    print(f\"[offdiag] crystal layers (off-diag curvature): \"\n          f\"{len(crystal_layers)}/{len(late)} late\")\n\n    # ── read held-out prose: pooled off-diagonal pseudo-token → per-layer z ──────\n    cset = set(crystal_layers)\n    per_probe = []\n    for i, p in enumerate(test):\n        if i % 25 == 0:\n            print(f\"[offdiag]   test fwd+2bwd {i}/{len(test)} ...\")\n        fstore, nt = forward_offdiag(p.prompt, model, tok, torch_mod, early, late)\n        pooled = pooled_supervised(fstore, late, nt)\n        per_layer = rcc.classify(pooled).per_layer\n        crystal_z = {li: {op: float(per_layer[li].get(op, 0.0)) for op in CRYSTAL}\n                     for li in per_layer if li in cset}\n        layer_avg = ({op: float(np.mean([crystal_z[li][op] for li in crystal_z]))\n                      for op in CRYSTAL} if crystal_z else {op: 0.0 for op in CRYSTAL})\n        per_probe.append({\n            \"combinator\": p.combinator,\n            \"layer_avg_z\": {op: round(v, 4) for op, v in layer_avg.items()},\n            \"crystal_z\": {str(li): {op: round(crystal_z[li][op], 3) for op in CRYSTAL}\n                          for li in crystal_z}})\n\n    # ── discr_z(c): raw-z Welch contrast on the OFF-DIAGONAL (mirror v6/v7) ───────\n    discr_z: dict[str, dict] = {}\n    for c in CRYSTAL:\n        on = [r[\"layer_avg_z\"][c] for r in per_probe if r[\"combinator\"] == c]\n        off = [r[\"layer_avg_z\"][c] for r in per_probe if r[\"combinator\"] != c]\n        if on:\n            discr_z[c] = welch_t(on, off)\n\n    # per-layer profile (where in the LATE stack does each op discriminate off-diag)\n    peak: dict[str, dict] = {}\n    for c in CRYSTAL:\n        on_rows = [r for r in per_probe if r[\"combinator\"] == c]\n        off_rows = [r for r in per_probe if r[\"combinator\"] != c]\n        if not on_rows:\n            continue\n        best = None\n        for li in crystal_layers:\n            sli = str(li)\n            on_z = [r[\"crystal_z\"][sli][c] for r in on_rows if sli in r[\"crystal_z\"]]\n            off_z = [r[\"crystal_z\"][sli][c] for r in off_rows if sli in r[\"crystal_z\"]]\n            if not on_z:\n                continue\n            d = float(np.mean(on_z)) - (float(np.mean(off_z)) if off_z else 0.0)\n            if best is None or d > best[1]:\n                best = (li, round(d, 3))\n        if best:\n            peak[c] = {\"layer\": best[0], \"delta\": best[1]}\n\n    b = discr_z.get(\"B\", {})\n    b_in_offdiag = bool(b.get(\"significant\") and b.get(\"discr_z\", 0) > 0)\n    # instrument check: did the curvature-discriminable set survive the off-diagonal read?\n    instr = {c: bool(discr_z.get(c, {}).get(\"significant\")\n                     and discr_z.get(c, {}).get(\"discr_z\", 0) > 0)\n             for c in (\"C\", \"Y\", \"K\")}\n    verdict = {\n        \"register\": \"off-diagonal interlayer curvature \"\n                    \"(H_{late,early}·g_early, pooled supervised, gradient direction)\",\n        \"split_frac\": args.split_frac,\n        \"early_layers\": [early[0], early[-1]], \"late_layers\": [late[0], late[-1]],\n        \"n_test\": len(per_probe), \"discr_z\": discr_z,\n        \"peak_layer\": peak, \"b_discriminates_in_offdiag\": b_in_offdiag,\n        \"instrument_works\": instr,\n        \"n_discr_z_significant\": sum(\n            1 for c in CRYSTAL if discr_z.get(c, {}).get(\"significant\")\n            and discr_z.get(c, {}).get(\"discr_z\", 0) > 0),\n    }\n\n    print(\"\\n\" + \"═\" * 74)\n    print(\"KERNEL-REF OFF-DIAGONAL CURVATURE — is B in the f∘g chain-rule cross term?\")\n    print(\"═\" * 74)\n    print(f\"  n_test={verdict['n_test']}  crystal_layers={len(crystal_layers)}\"\n          f\"  EARLY={early[0]}..{early[-1]}  LATE={late[0]}..{late[-1]}\")\n    print(f\"\\n  {'op':<4}{'on_z':>9}{'off_z':>9}{'discr_z':>9}{'t':>8}{'sig':>5}\"\n          f\"{'peakL':>7}\")\n    for c in CRYSTAL:\n        d = discr_z.get(c)\n        if d is None:\n            continue\n        sig = \"✓\" if d[\"significant\"] and d[\"discr_z\"] > 0 else \" \"\n        pk = peak.get(c, {}).get(\"layer\", \"-\")\n        print(f\"  {c:<4}{d['on_mean']:>9}{d['off_mean']:>9}{d['discr_z']:>9}\"\n              f\"{(d['t'] or 0):>8}{sig:>5}{pk!s:>7}\")\n    print(f\"\\n  instrument check (C/Y/K discriminate off-diagonal): {instr}\")\n    print(f\"  ★ B discriminates in the OFF-DIAGONAL register: \"\n          f\"{b_in_offdiag}  (B discr_z={b.get('discr_z')}, t={b.get('t')})\")\n    print(f\"  (compare v7 DIAGONAL: B discr_z +0.118, t=1.90; the monotone climb was \"\n          f\"act −0.05 → grad +1.07 → diag-curv +1.90)\")\n    print(\"═\" * 74 + \"\\n\")\n\n    RESULTS_DIR.mkdir(parents=True, exist_ok=True)\n    slug = model_name.split(\"/\")[-1].lower().replace(\".\", \"-\")\n    out = {\"verdict\": verdict, \"per_probe\": per_probe,\n           \"crystal_layers\": crystal_layers}\n    (RESULTS_DIR / f\"offdiag_v8_verdict_{slug}.json\").write_text(\n        json.dumps(_json_safe(out), indent=2), encoding=\"utf-8\")\n    meta = {\n        \"model\": model_name, \"smoke\": args.smoke, \"git_sha\": _git_sha(),\n        \"timestamp_utc\": datetime.now(UTC).isoformat(),\n        \"transformers_version\": _transformers_version(),\n        \"n_layers\": n_layers, \"n_perm\": n_perm, \"ppc\": ppc, \"heldout_per\": heldout,\n        \"split_frac\": args.split_frac,\n        \"early_layers\": [early[0], early[-1]], \"late_layers\": [late[0], late[-1]],\n        \"n_calib\": len(calib), \"n_test\": len(test),\n        \"register\": \"OFF-DIAGONAL interlayer curvature H_{late,early}·g_early, \"\n                    \"pooled supervised, deterministic gradient direction, one HVP\",\n    }\n    (RESULTS_DIR / f\"offdiag_v8_meta_{slug}.json\").write_text(\n        json.dumps(meta, indent=2), encoding=\"utf-8\")\n    print(f\"[offdiag] wrote {RESULTS_DIR}/offdiag_v8_verdict_{slug}.json\")\n\n\nif __name__ == \"__main__\":\n    main()\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py
```

### Thinking

I need to run diagnostics on the linting and smoke tests, checking that the imports for split_probes and welch_t are available in kernel_reference_prose_v2. I'm also considering the runtime environment—the local Mac doesn't have CUDA, so running the smoke test with Qwen3-0.6B might be slow, though it could work on MPS or CPU.

Looking at the tmux setup, it seems the Mac itself might be running the models via MPS (possibly a Mac Studio with substantial unified memory), which would make running the 14B model locally plausible. The 0.6B smoke test should run quickly on MPS. I'm a bit concerned about double-backward operations on MPS since they can be finicky with certain operations, but v7 worked, so I'll proceed with linting first and then running the smoke test.

## Assistant

Let me lint and run the smoke test.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/kernel_reference_offdiag_v8.py 2>&1 | head -40"
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
E501 Line too long (100 > 88)
 --> scripts/experiments/kernel_reference_offdiag_v8.py:2:89
  |
1 | #!/usr/bin/env python3
2 | # register: SECOND-ORDER / OFF-DIAGONAL interlayer curvature (H_{late,early} of LM CE wrt gate_proj)
  |                                                                                         ^^^^^^^^^^^^
3 | """Kernel-ref OFF-DIAGONAL interlayer curvature — is B in the f∘g cross-coupling?
4 | (s238 lead 2d prong 1c-iii).
  |

E501 Line too long (89 > 88)
 --> scripts/experiments/kernel_reference_offdiag_v8.py:7:89
  |
6 | B = composition (B f g x = f(g x)). Its backward signature is the chain rule, a PRODUCT
7 | of derivatives `d(f∘g)/dx = f'(g x)·g'(x)`. Prong 1c-ii (kernel_reference_jacobian_v7.py)
  |                                                                                         ^
8 | read the DIAGONAL Hessian of the LM loss w.r.t. the gate activation via a Rademacher
9 | Hutchinson estimator `diag(H)_a = E_v[v_a (Hv)_a]`. That estimator CANCELS every
  |

RUF002 Docstring contains ambiguous `−` (MINUS SIGN). Did you mean `-` (HYPHEN-MINUS)?
  --> scripts/experiments/kernel_reference_offdiag_v8.py:12:64
   |
10 | cross-coordinate AND cross-layer term in expectation (`E[v_a v_b]=0`, a≠b), so it only
11 | captured the WITHIN-layer quadratic form `g'ᵀ(diag)g'`. B sat right ON the bar there
12 | (discr_z +0.118, t=1.90 < 2.0) with a clean monotone climb act(−0.05)→grad(+1.07)→
   |                                                                ^
13 | diag-curv(+1.90).
   |

RUF002 Docstring contains ambiguous `ℓ` (SCRIPT SMALL L). Did you mean `l` (LATIN SMALL LETTER L)?
  --> scripts/experiments/kernel_reference_offdiag_v8.py:15:66
   |
13 | diag-curv(+1.90).
14 |
15 | But the LITERAL f∘g coupling is the OFF-DIAGONAL block. For `L = ℓ(f(g(z)))` with the
   |                                                                  ^
16 | gate activation `z` split into an EARLY block `z_e` (≈ g, processed first) and a LATE
17 | block `z_l` (≈ f, applied last),
   |
```

### Thinking

I'm checking whether these docstring lint warnings (line-too-long and ambiguous unicode characters) are pre-existing in v7 or if they're new, and whether the project configuration already suppresses them for these files.

## Assistant

These are docstring-only warnings (math notation `−`, `ℓ`, `∘`). Let me check whether v7 — the template — has the same profile, to match the project's tolerance.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && echo \"=== v7 (template) ===\" && uv run ruff check scripts/experiments/kernel_reference_jacobian_v7.py 2>&1 | tail -5 && echo \"=== v8 summary ===\" && uv run ruff check scripts/experiments/kernel_reference_offdiag_v8.py 2>&1 | grep -E \"^(E|RUF|F|W)[0-9]\" | sort | uniq -c"
}
```

**Summary:** $ echo "=== v7 (template) ===" && uv ...

**Output:**
```
Exit code: 0
Stdout:
=== v7 (template) ===
All checks passed!
=== v8 summary ===
   3 E501 Line too long (100 > 88)
   4 E501 Line too long (89 > 88)
   5 E501 Line too long (90 > 88)
   1 E501 Line too long (91 > 88)
   1 E501 Line too long (93 > 88)
   1 E501 Line too long (95 > 88)
   1 E501 Line too long (96 > 88)
   2 F541 [*] f-string without any placeholders
   1 RUF001 String contains ambiguous `−` (MINUS SIGN). Did you mean `-` (HYPHEN-MINUS)?
   1 RUF002 Docstring contains ambiguous `−` (MINUS SIGN). Did you mean `-` (HYPHEN-MINUS)?
   1 RUF002 Docstring contains ambiguous `ℓ` (SCRIPT SMALL L). Did you mean `l` (LATIN SMALL LETTER L)?
   1 RUF046 Value being cast to `int` is already an integer
```

### Thinking

V7 is passing cleanly, so now I need to fix v8 to satisfy ruff's linting rules. There are several issues to address: line length violations in docstrings and code that need wrapping, f-strings without any placeholders in print statements, ambiguous Unicode characters like the minus sign appearing in both regular strings and docstrings, and a redundant int cast on a value that's already an integer.

Looking at v7, it avoided these problems by using ASCII characters and regular hyphens instead of fancy Unicode, so I should follow that pattern. My approach is to replace the problematic characters (the minus sign and script l with their ASCII equivalents), remove unnecessary f-string prefixes, eliminate the redundant int cast, and wrap the long lines. Let me locate and fix those specific F541 and RUF001 violations.

## Assistant

v7 passes cleanly, so I'll fix v8 to match (project policy: fix > suppress). Let me see the exact code-level offenders (F541, RUF001, RUF046) and long code lines.

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/kernel_reference_offdiag_v8.py 2>&1 | grep -E \"F541|RUF001|RUF046|RUF002\" -A2 | grep -E \"^\\s+[0-9]+ \\|\" "
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 1
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check --output-format=concise scripts/experiments/kernel_reference_offdiag_v8.py 2>&1 | grep -E \"F541|RUF001|RUF046\""
}
```

**Summary:** $ uv run ruff check --output-format=c...

**Output:**
```
Exit code: 0
Stdout:
scripts/experiments/kernel_reference_offdiag_v8.py:98:16: RUF046 Value being cast to `int` is already an integer
scripts/experiments/kernel_reference_offdiag_v8.py:309:11: F541 [*] f-string without any placeholders
scripts/experiments/kernel_reference_offdiag_v8.py:310:11: F541 [*] f-string without any placeholders
scripts/experiments/kernel_reference_offdiag_v8.py:310:17: RUF001 String contains ambiguous `−` (MINUS SIGN). Did you mean `-` (HYPHEN-MINUS)?
```

### Thinking

I'm identifying several linting issues to fix: removing unnecessary rounding conversions, fixing f-strings without placeholders, replacing unicode characters with ASCII equivalents, and handling long lines. I'll use ruff's autofix for the straightforward issues and then manually address the unicode problems and line wrapping.

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check --fix scripts/experiments/kernel_reference_offdiag_v8.py 2>&1 | tail -3; echo \"---remaining---\"; uv run ruff check --output-format=concise scripts/experiments/kernel_reference_offdiag_v8.py 2>&1"
}
```

**Summary:** $ uv run ruff check --fix scripts/exp...

**Output:**
```
Exit code: 1
Stdout:
Found 22 errors (2 fixed, 20 remaining).
No fixes available (1 hidden fix can be enabled with the `--unsafe-fixes` option).
---remaining---
scripts/experiments/kernel_reference_offdiag_v8.py:2:89: E501 Line too long (100 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:7:89: E501 Line too long (89 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:12:64: RUF002 Docstring contains ambiguous `−` (MINUS SIGN). Did you mean `-` (HYPHEN-MINUS)?
scripts/experiments/kernel_reference_offdiag_v8.py:15:66: RUF002 Docstring contains ambiguous `ℓ` (SCRIPT SMALL L). Did you mean `l` (LATIN SMALL LETTER L)?
scripts/experiments/kernel_reference_offdiag_v8.py:19:89: E501 Line too long (89 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:28:89: E501 Line too long (96 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:31:89: E501 Line too long (100 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:32:89: E501 Line too long (100 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:95:89: E501 Line too long (89 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:96:89: E501 Line too long (90 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:98:16: RUF046 Value being cast to `int` is already an integer
scripts/experiments/kernel_reference_offdiag_v8.py:109:89: E501 Line too long (90 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:110:89: E501 Line too long (90 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:111:89: E501 Line too long (90 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:138:89: E501 Line too long (95 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:151:89: E501 Line too long (93 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:157:89: E501 Line too long (89 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:210:89: E501 Line too long (91 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:274:89: E501 Line too long (90 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:310:16: RUF001 String contains ambiguous `−` (MINUS SIGN). Did you mean `-` (HYPHEN-MINUS)?
Found 20 errors.
No fixes available (1 hidden fix can be enabled with the `--unsafe-fixes` option).
```

### Thinking

I need to clean up the docstring by removing ambiguous unicode characters and ensuring lines stay within the 88-column limit, using ASCII-friendly math notation like the previous version did. I'll also fix the specific linting issues on those lines and rewrite the affected code sections.

## Assistant

Let me view the current code lines after autofix to do targeted edits.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py",
  "line_offset": 91,
  "limit": 25
}
```

**Summary:** Reading kernel_reference_offdiag_v8.py (91-116)

**Output:**
```
    """Partition layers into EARLY (≈ g, processed first) and LATE (≈ f, applied last).

    split_frac = fraction of the stack that is EARLY. LATE = the readable mid-late zone
    (depth ≥ split_frac) where the combinator crystal lives (s187/s227). The off-diagonal
    feature is read on the LATE layers (coupling FROM the early block TO each late layer).
    """
    k = max(1, int(round(n_layers * split_frac)))
    k = min(k, n_layers - 1)
    early = list(range(k))
    late = list(range(k, n_layers))
    return early, late


def forward_offdiag(prompt, model, tok, torch_mod, early, late):
    """Forward + double-backward; return ({li∈late: off-diag (Hv)_li [T,d]}, n_tok).

    v = g_e.detach() on the EARLY block, 0 on LATE.  (Hv)_li = Σ_{e∈EARLY} H_{li,e} g_e
    for li ∈ LATE = the PURE off-diagonal interlayer curvature (the chain-rule cross term,
    no within-layer H_{li,li} because v is zero at li). One HVP = a double-backward of the
    scalar Σ_e ||g_e||²(detached), where g = grad(CE, gates, create_graph=True). Per-token
    rows returned (callers pool 0..n_tok-2; the last token feeds only the unsupervised
    next-token ⇒ its gradient/curvature row ~0).
    """
    import torch.nn.functional as func
    all_layers = early + late

[CONTENT TRUNCATED] Showing lines 92 to 116 of 336 total lines. Use line_offset=116 parameter to read more content.
```

### Thinking

The E501 line length issues stem from the actual docstring length rather than unicode character width—ruff counts columns properly. Since the policy favors fixing over suppressing, I'll rewrite these math-heavy docstrings to match the ASCII-wrapped style from v7 instead of adding noqa directives.

Rather than tackle every line individually, I'll replace the two large docstrings wholesale and fix the few problematic code lines, starting with the module docstring at the top of the file.

## Assistant

These are math-heavy docstrings exceeding 88 cols plus ambiguous unicode (`−`,`ℓ`). I'll rewrite the docstrings in v7's clean ASCII-wrapped style. Let me read the full header to replace it.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py",
  "line_offset": 0,
  "limit": 60
}
```

**Summary:** Reading kernel_reference_offdiag_v8.py (0-60)

**Output:**
```
#!/usr/bin/env python3
# register: SECOND-ORDER / OFF-DIAGONAL interlayer curvature (H_{late,early} of LM CE wrt gate_proj)
"""Kernel-ref OFF-DIAGONAL interlayer curvature — is B in the f∘g cross-coupling?
(s238 lead 2d prong 1c-iii).

B = composition (B f g x = f(g x)). Its backward signature is the chain rule, a PRODUCT
of derivatives `d(f∘g)/dx = f'(g x)·g'(x)`. Prong 1c-ii (kernel_reference_jacobian_v7.py)
read the DIAGONAL Hessian of the LM loss w.r.t. the gate activation via a Rademacher
Hutchinson estimator `diag(H)_a = E_v[v_a (Hv)_a]`. That estimator CANCELS every
cross-coordinate AND cross-layer term in expectation (`E[v_a v_b]=0`, a≠b), so it only
captured the WITHIN-layer quadratic form `g'ᵀ(diag)g'`. B sat right ON the bar there
(discr_z +0.118, t=1.90 < 2.0) with a clean monotone climb act(−0.05)→grad(+1.07)→
diag-curv(+1.90).

But the LITERAL f∘g coupling is the OFF-DIAGONAL block. For `L = ℓ(f(g(z)))` with the
gate activation `z` split into an EARLY block `z_e` (≈ g, processed first) and a LATE
block `z_l` (≈ f, applied last),

    d²L/dz_l dz_e = the OFF-DIAGONAL Hessian block H_{l,e}    # the chain-rule cross term

is exactly "how the curvature of the late computation (f) couples to the early
computation (g)" — the product-of-derivatives the diagonal read threw away.

ISOLATION (deterministic, ONE double-backward, NO Hutchinson noise):
  Perturb the GRADIENT direction supported ONLY on the EARLY block: v = g_e.detach() on
  EARLY, 0 on LATE. Then for any LATE layer li (li ∉ EARLY),

      (Hv)_li = Σ_{e∈EARLY} H_{li,e} g_e                      # PURE off-diagonal (no H_{li,li})

  because v is zero at li so the diagonal block never enters. Computed as a single HVP:
      s  = Σ_{e∈EARLY} (g_e · g_e.detach()).sum()             # g_e = grad(CE, gate_e, create_graph)
      hv = grad(s, [gate_li for li∈LATE])                     # = 2·Σ_e H_{li,e} g_e   (H symmetric)
  The factor 2 is an overall scale; sign-CMR in the classifier is scale-free.

  The perturbation direction is the GRADIENT (the loss-relevant / backprop direction the
  chain rule actually propagates), NOT random — a random v would have E[(Hv)_li]=0 and
  give a zero-mean, unstable per-probe feature. The gradient direction makes the feature
  deterministic and meaningful (the literal backward composition coupling).

Clean register-swap of v7: same RelationalCrystalClassifier (sign-CMR, crosstask null,
raw-z Welch contrast), same calibrate→classify→discr_z pipeline; the feature is the
PURE OFF-DIAGONAL interlayer curvature (Hv)_late, pooled over supervised positions. The
classifier runs on the LATE layers only (where the feature is defined / off-diagonal).

VERDICT LOGIC (λ measure, two-sided):
  - B discriminates in the OFF-DIAGONAL where it sat ON the bar in the diagonal (v7
    t=1.90) → the f∘g chain-rule cross-coupling is B's home; the curvature climb
    completes off the diagonal. (Compare discr_z(B) to v7's diagonal +1.90.)
  - B flat off-diagonal too → the curvature register is exhausted at BOTH the diagonal
    AND the off-diagonal; B's positive signal is the FORWARD order-cost face (prong 2b),
    not a localizable second-order amplitude.
  - INSTRUMENT CHECK: {C,Y} (the curvature-discriminable set, v7) should still
    discriminate in the off-diagonal block, else the read is broken not B-absent.

Usage:
    uv run python scripts/experiments/kernel_reference_offdiag_v8.py --smoke
    uv run python scripts/experiments/kernel_reference_offdiag_v8.py            # 14B

License: MIT
"""

[CONTENT TRUNCATED] Showing lines 1 to 60 of 336 total lines. Use line_offset=60 parameter to read more content.
```

### Thinking

I'm updating the module docstring to replace mathematical symbols with ASCII equivalents—converting the minus sign, script l, and superscript characters while keeping symbols like the composition operator, summation, and arrows that aren't flagged by the linter.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py",
  "original_content": "#!/usr/bin/env python3\n# register: SECOND-ORDER / OFF-DIAGONAL interlayer curvature (H_{late,early} of LM CE wrt gate_proj)\n\"\"\"Kernel-ref OFF-DIAGONAL interlayer curvature — is B in the f∘g cross-coupling?\n(s238 lead 2d prong 1c-iii).\n\nB = composition (B f g x = f(g x)). Its backward signature is the chain rule, a PRODUCT\nof derivatives `d(f∘g)/dx = f'(g x)·g'(x)`. Prong 1c-ii (kernel_reference_jacobian_v7.py)\nread the DIAGONAL Hessian of the LM loss w.r.t. the gate activation via a Rademacher\nHutchinson estimator `diag(H)_a = E_v[v_a (Hv)_a]`. That estimator CANCELS every\ncross-coordinate AND cross-layer term in expectation (`E[v_a v_b]=0`, a≠b), so it only\ncaptured the WITHIN-layer quadratic form `g'ᵀ(diag)g'`. B sat right ON the bar there\n(discr_z +0.118, t=1.90 < 2.0) with a clean monotone climb act(−0.05)→grad(+1.07)→\ndiag-curv(+1.90).\n\nBut the LITERAL f∘g coupling is the OFF-DIAGONAL block. For `L = ℓ(f(g(z)))` with the\ngate activation `z` split into an EARLY block `z_e` (≈ g, processed first) and a LATE\nblock `z_l` (≈ f, applied last),\n\n    d²L/dz_l dz_e = the OFF-DIAGONAL Hessian block H_{l,e}    # the chain-rule cross term\n\nis exactly \"how the curvature of the late computation (f) couples to the early\ncomputation (g)\" — the product-of-derivatives the diagonal read threw away.\n\nISOLATION (deterministic, ONE double-backward, NO Hutchinson noise):\n  Perturb the GRADIENT direction supported ONLY on the EARLY block: v = g_e.detach() on\n  EARLY, 0 on LATE. Then for any LATE layer li (li ∉ EARLY),\n\n      (Hv)_li = Σ_{e∈EARLY} H_{li,e} g_e                      # PURE off-diagonal (no H_{li,li})\n\n  because v is zero at li so the diagonal block never enters. Computed as a single HVP:\n      s  = Σ_{e∈EARLY} (g_e · g_e.detach()).sum()             # g_e = grad(CE, gate_e, create_graph)\n      hv = grad(s, [gate_li for li∈LATE])                     # = 2·Σ_e H_{li,e} g_e   (H symmetric)\n  The factor 2 is an overall scale; sign-CMR in the classifier is scale-free.\n\n  The perturbation direction is the GRADIENT (the loss-relevant / backprop direction the\n  chain rule actually propagates), NOT random — a random v would have E[(Hv)_li]=0 and\n  give a zero-mean, unstable per-probe feature. The gradient direction makes the feature\n  deterministic and meaningful (the literal backward composition coupling).\n\nClean register-swap of v7: same RelationalCrystalClassifier (sign-CMR, crosstask null,\nraw-z Welch contrast), same calibrate→classify→discr_z pipeline; the feature is the\nPURE OFF-DIAGONAL interlayer curvature (Hv)_late, pooled over supervised positions. The\nclassifier runs on the LATE layers only (where the feature is defined / off-diagonal).\n\nVERDICT LOGIC (λ measure, two-sided):\n  - B discriminates in the OFF-DIAGONAL where it sat ON the bar in the diagonal (v7\n    t=1.90) → the f∘g chain-rule cross-coupling is B's home; the curvature climb\n    completes off the diagonal. (Compare discr_z(B) to v7's diagonal +1.90.)\n  - B flat off-diagonal too → the curvature register is exhausted at BOTH the diagonal\n    AND the off-diagonal; B's positive signal is the FORWARD order-cost face (prong 2b),\n    not a localizable second-order amplitude.\n  - INSTRUMENT CHECK: {C,Y} (the curvature-discriminable set, v7) should still\n    discriminate in the off-diagonal block, else the read is broken not B-absent.",
  "new_content": "#!/usr/bin/env python3\n# register: SECOND-ORDER OFF-DIAGONAL interlayer curvature (H_{late,early} of LM CE wrt gate)\n\"\"\"Kernel-ref OFF-DIAGONAL interlayer curvature -- is B in the f.g cross-coupling?\n(s238 lead 2d prong 1c-iii).\n\nB = composition (B f g x = f(g x)). Its backward signature is the chain rule, a PRODUCT\nof derivatives `d(f.g)/dx = f'(g x).g'(x)`. Prong 1c-ii (kernel_reference_jacobian_v7.py)\nread the DIAGONAL Hessian of the LM loss w.r.t. the gate activation via a Rademacher\nHutchinson estimator `diag(H)_a = E_v[v_a (Hv)_a]`. That estimator CANCELS every\ncross-coord AND cross-layer term in expectation (`E[v_a v_b]=0`, a!=b), so it captured\nonly the WITHIN-layer quadratic form `g'^T (diag) g'`. B sat right ON the bar there\n(discr_z +0.118, t=1.90 < 2.0) with a clean monotone climb act(-0.05) -> grad(+1.07) ->\ndiag-curv(+1.90).\n\nBut the LITERAL f.g coupling is the OFF-DIAGONAL block. For `L = l(f(g(z)))` with the\ngate activation `z` split into an EARLY block `z_e` (~ g, processed first) and a LATE\nblock `z_l` (~ f, applied last),\n\n    d2L/dz_l dz_e = the OFF-DIAGONAL Hessian block H_{l,e}   # the chain-rule cross term\n\nis exactly \"how the curvature of the late computation (f) couples to the early\ncomputation (g)\" -- the product-of-derivatives the diagonal read threw away.\n\nISOLATION (deterministic, ONE double-backward, NO Hutchinson noise):\n  Perturb the GRADIENT direction supported ONLY on the EARLY block: v = g_e.detach() on\n  EARLY, 0 on LATE. Then for any LATE layer li (li not in EARLY),\n\n      (Hv)_li = Sum_{e in EARLY} H_{li,e} g_e        # PURE off-diagonal (no H_{li,li})\n\n  because v is zero at li so the diagonal block never enters. Computed as a single HVP:\n      s  = Sum_{e in EARLY} (g_e . g_e.detach()).sum()    # g_e = grad(CE, gate_e, c.g.)\n      hv = grad(s, [gate_li for li in LATE])              # = 2.Sum_e H_{li,e} g_e (sym)\n  The factor 2 is an overall scale; sign-CMR in the classifier is scale-free.\n\n  The perturbation direction is the GRADIENT (the loss-relevant / backprop direction the\n  chain rule actually propagates), NOT random -- a random v would have E[(Hv)_li]=0 and\n  give a zero-mean, unstable per-probe feature. The gradient direction makes the feature\n  deterministic and meaningful (the literal backward composition coupling).\n\nClean register-swap of v7: same RelationalCrystalClassifier (sign-CMR, crosstask null,\nraw-z Welch contrast), same calibrate -> classify -> discr_z pipeline; the feature is the\nPURE OFF-DIAGONAL interlayer curvature (Hv)_late, pooled over supervised positions. The\nclassifier runs on the LATE layers only (where the feature is defined / off-diagonal).\n\nVERDICT LOGIC (lambda measure, two-sided):\n  - B discriminates in the OFF-DIAGONAL where it sat ON the bar in the diagonal (v7\n    t=1.90) -> the f.g chain-rule cross-coupling is B's home; the curvature climb\n    completes off the diagonal. (Compare discr_z(B) to v7's diagonal +1.90.)\n  - B flat off-diagonal too -> the curvature register is exhausted at BOTH the diagonal\n    AND the off-diagonal; B's positive signal is the FORWARD order-cost face (prong 2b),\n    not a localizable second-order amplitude.\n  - INSTRUMENT CHECK: {C,Y} (the curvature-discriminable set, v7) should still\n    discriminate in the off-diagonal block, else the read is broken not B-absent."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py.
```

### Thinking

I need to fix the docstrings for `split_early_late` and `forward_offdiag`, clean up the `int(round())` calls, and address some specific code lines before running ruff again to check what's left.

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check --output-format=concise scripts/experiments/kernel_reference_offdiag_v8.py 2>&1"
}
```

**Summary:** $ uv run ruff check --output-format=c...

**Output:**
```
Exit code: 1
Stdout:
scripts/experiments/kernel_reference_offdiag_v8.py:2:89: E501 Line too long (93 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:7:89: E501 Line too long (89 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:41:89: E501 Line too long (89 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:95:89: E501 Line too long (89 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:96:89: E501 Line too long (90 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:98:16: RUF046 Value being cast to `int` is already an integer
scripts/experiments/kernel_reference_offdiag_v8.py:109:89: E501 Line too long (90 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:110:89: E501 Line too long (90 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:111:89: E501 Line too long (90 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:138:89: E501 Line too long (95 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:151:89: E501 Line too long (93 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:157:89: E501 Line too long (89 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:210:89: E501 Line too long (91 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:274:89: E501 Line too long (90 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:310:16: RUF001 String contains ambiguous `−` (MINUS SIGN). Did you mean `-` (HYPHEN-MINUS)?
Found 15 errors.
No fixes available (1 hidden fix can be enabled with the `--unsafe-fixes` option).
```

### Thinking

I'm checking why the E501 line length violations persist even after shortening—the unicode characters like `≈`, `Σ`, and `∉` each count as single columns in ruff's calculation, so they're not the culprit. Looking at line 2 specifically, the comment about the interlayer curvature is still coming in at 93 characters even though I thought I'd trimmed it.

The real problem is that I only fixed the module-level docstring but left the function docstrings and code lines untouched—those still contain unicode and exceed the 88-character limit. I need to go through the remaining problem areas systematically: the `split_early_late` function docstring around lines 91-96, the `forward_offdiag` function around 108-114, and then scan through lines 205-215, 270-276, and 305-312 to catch any other violations.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py",
  "line_offset": 88,
  "limit": 75
}
```

**Summary:** Reading kernel_reference_offdiag_v8.py (88-163)

**Output:**
```


def split_early_late(n_layers: int, split_frac: float) -> tuple[list[int], list[int]]:
    """Partition layers into EARLY (≈ g, processed first) and LATE (≈ f, applied last).

    split_frac = fraction of the stack that is EARLY. LATE = the readable mid-late zone
    (depth ≥ split_frac) where the combinator crystal lives (s187/s227). The off-diagonal
    feature is read on the LATE layers (coupling FROM the early block TO each late layer).
    """
    k = max(1, int(round(n_layers * split_frac)))
    k = min(k, n_layers - 1)
    early = list(range(k))
    late = list(range(k, n_layers))
    return early, late


def forward_offdiag(prompt, model, tok, torch_mod, early, late):
    """Forward + double-backward; return ({li∈late: off-diag (Hv)_li [T,d]}, n_tok).

    v = g_e.detach() on the EARLY block, 0 on LATE.  (Hv)_li = Σ_{e∈EARLY} H_{li,e} g_e
    for li ∈ LATE = the PURE off-diagonal interlayer curvature (the chain-rule cross term,
    no within-layer H_{li,li} because v is zero at li). One HVP = a double-backward of the
    scalar Σ_e ||g_e||²(detached), where g = grad(CE, gates, create_graph=True). Per-token
    rows returned (callers pool 0..n_tok-2; the last token feeds only the unsupervised
    next-token ⇒ its gradient/curvature row ~0).
    """
    import torch.nn.functional as func
    all_layers = early + late
    store: dict[int, object] = {}

    def _cap(li):
        def _hook(_m, _inp, out):
            store[li] = out  # live graph tensor (NOT detached)
        return _hook

    handles = [model.model.layers[li].mlp.gate_proj.register_forward_hook(_cap(li))
               for li in all_layers]
    try:
        inputs = tok(prompt, return_tensors="pt")
        dev = next(model.parameters()).device
        inputs = {k: v.to(dev) for k, v in inputs.items()}
        out = model(**inputs)
        logits = out.logits[0]               # [T, V]
        ids = inputs["input_ids"][0]         # [T]
        t = ids.shape[0]
        ce = func.cross_entropy(logits[:-1, :], ids[1:], reduction="mean")
        gates_all = [store[li] for li in all_layers]
        grads_all = torch_mod.autograd.grad(ce, gates_all, create_graph=True)
        grad_of = dict(zip(all_layers, grads_all, strict=True))
        # scalar: Σ_{e∈EARLY} (g_e · g_e.detach()) ⇒ grad wrt LATE gates = 2 Σ_e H_{late,e} g_e
        scalar = sum((grad_of[e] * grad_of[e].detach()).sum() for e in early)
        late_gates = [store[li] for li in late]
        hv_late = torch_mod.autograd.grad(scalar, late_gates, retain_graph=False)
    finally:
        for h in handles:
            h.remove()
    result = {li: hv_late[j][0].detach().float().cpu().numpy().astype(np.float64)
              for j, li in enumerate(late)}
    return result, t


def pooled_supervised(feat_store, late, n_tok):
    """Mean-pool the off-diagonal feature over supervised positions 0..n_tok-2 → {li:[d]}."""
    sup = max(1, n_tok - 1)
    return {li: feat_store[li][:sup].mean(axis=0) for li in late}


def main() -> None:
    parser = argparse.ArgumentParser(description="Kernel-ref off-diagonal curvature (B)")
    parser.add_argument("--model", default="Qwen/Qwen3-14B")
    parser.add_argument("--heldout-per", type=int, default=20)
    parser.add_argument("--ppc", type=int, default=25, help="calib probes/combinator")
    parser.add_argument("--null-cap", type=int, default=300)
    parser.add_argument("--n-perm", type=int, default=200)
    parser.add_argument("--split-frac", type=float, default=0.5,

[CONTENT TRUNCATED] Showing lines 89 to 163 of 336 total lines. Use line_offset=163 parameter to read more content.
```

### Thinking

I'm fixing the docstrings and cleaning up the code formatting, starting with the `split_early_late` function and its rounding logic.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py",
  "original_content": "    \"\"\"Partition layers into EARLY (≈ g, processed first) and LATE (≈ f, applied last).\n\n    split_frac = fraction of the stack that is EARLY. LATE = the readable mid-late zone\n    (depth ≥ split_frac) where the combinator crystal lives (s187/s227). The off-diagonal\n    feature is read on the LATE layers (coupling FROM the early block TO each late layer).\n    \"\"\"\n    k = max(1, int(round(n_layers * split_frac)))",
  "new_content": "    \"\"\"Partition layers into EARLY (~ g, processed first) and LATE (~ f, applied last).\n\n    split_frac = fraction of the stack that is EARLY. LATE = the readable mid-late zone\n    (depth >= split_frac) where the combinator crystal lives (s187/s227). The off-diag\n    feature is read on the LATE layers (coupling FROM the early block TO each late layer).\n    \"\"\"\n    k = max(1, round(n_layers * split_frac))"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py",
  "original_content": "    \"\"\"Forward + double-backward; return ({li∈late: off-diag (Hv)_li [T,d]}, n_tok).\n\n    v = g_e.detach() on the EARLY block, 0 on LATE.  (Hv)_li = Σ_{e∈EARLY} H_{li,e} g_e\n    for li ∈ LATE = the PURE off-diagonal interlayer curvature (the chain-rule cross term,\n    no within-layer H_{li,li} because v is zero at li). One HVP = a double-backward of the\n    scalar Σ_e ||g_e||²(detached), where g = grad(CE, gates, create_graph=True). Per-token\n    rows returned (callers pool 0..n_tok-2; the last token feeds only the unsupervised\n    next-token ⇒ its gradient/curvature row ~0).\n    \"\"\"",
  "new_content": "    \"\"\"Forward + double-backward; return ({li in late: off-diag (Hv)_li [T,d]}, n_tok).\n\n    v = g_e.detach() on the EARLY block, 0 on LATE.  (Hv)_li = Sum_{e} H_{li,e} g_e\n    for li in LATE = the PURE off-diagonal interlayer curvature (the chain-rule cross\n    term, no within-layer H_{li,li} because v is zero at li). One HVP = a double-backward\n    of the scalar Sum_e ||g_e||^2 (detached), g = grad(CE, gates, create_graph=True).\n    Per-token rows returned (callers pool 0..n_tok-2; the last token feeds only the\n    unsupervised next-token so its gradient/curvature row is ~0).\n    \"\"\""
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py",
  "original_content": "        # scalar: Σ_{e∈EARLY} (g_e · g_e.detach()) ⇒ grad wrt LATE gates = 2 Σ_e H_{late,e} g_e\n        scalar = sum((grad_of[e] * grad_of[e].detach()).sum() for e in early)",
  "new_content": "        # scalar Sum_e (g_e . g_e.detach()) -> grad wrt LATE gates = 2 Sum_e H_{late,e} g_e\n        scalar = sum((grad_of[e] * grad_of[e].detach()).sum() for e in early)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py",
  "original_content": "    \"\"\"Mean-pool the off-diagonal feature over supervised positions 0..n_tok-2 → {li:[d]}.\"\"\"",
  "new_content": "    \"\"\"Mean-pool the off-diag feature over supervised positions 0..n_tok-2 -> {li:[d]}.\"\"\""
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py.
```

### Thinking

I'm checking specific line numbers where ruff flagged issues—looking at line 2's comment, then lines 41, 89, 210, 274, and 310 to understand what needs fixing before running ruff again.

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check --output-format=concise scripts/experiments/kernel_reference_offdiag_v8.py 2>&1"
}
```

**Summary:** $ uv run ruff check --output-format=c...

**Output:**
```
Exit code: 1
Stdout:
scripts/experiments/kernel_reference_offdiag_v8.py:2:89: E501 Line too long (93 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:7:89: E501 Line too long (89 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:41:89: E501 Line too long (89 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:96:89: E501 Line too long (90 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:110:89: E501 Line too long (89 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:138:89: E501 Line too long (91 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:151:89: E501 Line too long (90 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:157:89: E501 Line too long (89 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:210:89: E501 Line too long (91 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:274:89: E501 Line too long (90 > 88)
scripts/experiments/kernel_reference_offdiag_v8.py:310:16: RUF001 String contains ambiguous `−` (MINUS SIGN). Did you mean `-` (HYPHEN-MINUS)?
Found 11 errors.
```

### Thinking

I'm checking which lines still exceed the 88-character limit after my edits. The unicode characters like `≈` and `²` were removed but some lines are still coming in at 89-90 characters, so I need to investigate whether ruff is counting unicode width differently or if I'm just missing something. Let me pull up the specific problematic lines and manually shorten them.

## Assistant

Some lines are still 89-91. Let me view the exact offending lines and shorten each.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && for n in 2 7 41 96 110 138 151 157 210 274 310; do printf \"%s: \" \"$n\"; awk \"NR==$n{print length(\\$0)\\\" | \\\"\\$0}\" scripts/experiments/kernel_reference_offdiag_v8.py; done"
}
```

**Summary:** $ for n in 2 7 41 96 110 138 151 157 ...

**Output:**
```
Exit code: 0
Stdout:
2: 93 | # register: SECOND-ORDER OFF-DIAGONAL interlayer curvature (H_{late,early} of LM CE wrt gate)
7: 89 | of derivatives `d(f.g)/dx = f'(g x).g'(x)`. Prong 1c-ii (kernel_reference_jacobian_v7.py)
41: 89 | raw-z Welch contrast), same calibrate -> classify -> discr_z pipeline; the feature is the
96: 90 |     feature is read on the LATE layers (coupling FROM the early block TO each late layer).
110: 89 |     term, no within-layer H_{li,li} because v is zero at li). One HVP = a double-backward
138: 91 |         # scalar Sum_e (g_e . g_e.detach()) -> grad wrt LATE gates = 2 Sum_e H_{late,e} g_e
151: 90 |     """Mean-pool the off-diag feature over supervised positions 0..n_tok-2 -> {li:[d]}."""
157: 89 |     parser = argparse.ArgumentParser(description="Kernel-ref off-diagonal curvature (B)")
210: 91 |     print(f"[offdiag] building off-diagonal null ({len(BASELINE_NULL_SENTENCES)} prompts)")
274: 90 |     # instrument check: did the curvature-discriminable set survive the off-diagonal read?
310: 60 |           "act −0.05 → grad +1.07 → diag-curv +1.90)")
```

### Thinking

I'm going through the code and trimming down verbose comments and descriptions across multiple lines to make them more concise.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py",
  "original_content": "# register: SECOND-ORDER OFF-DIAGONAL interlayer curvature (H_{late,early} of LM CE wrt gate)",
  "new_content": "# register: SECOND-ORDER OFF-DIAGONAL interlayer curvature (H_{late,early} LM CE wrt gate)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py",
  "original_content": "of derivatives `d(f.g)/dx = f'(g x).g'(x)`. Prong 1c-ii (kernel_reference_jacobian_v7.py)",
  "new_content": "of derivatives `d(f.g)/dx = f'(g x).g'(x)`. Prong 1c-ii (kernel_reference_jacobian_v7)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py",
  "original_content": "raw-z Welch contrast), same calibrate -> classify -> discr_z pipeline; the feature is the",
  "new_content": "raw-z Welch contrast), same calibrate -> classify -> discr_z pipeline; the feature ="
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py",
  "original_content": "    feature is read on the LATE layers (coupling FROM the early block TO each late layer).",
  "new_content": "    feature is read on the LATE layers (coupling FROM the early block TO each late)."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py",
  "original_content": "    term, no within-layer H_{li,li} because v is zero at li). One HVP = a double-backward",
  "new_content": "    term, no within-layer H_{li,li} since v is zero at li). One HVP = a double-backward"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py",
  "original_content": "        # scalar Sum_e (g_e . g_e.detach()) -> grad wrt LATE gates = 2 Sum_e H_{late,e} g_e",
  "new_content": "        # scalar Sum_e(g_e . g_e.detach()) -> grad wrt LATE = 2 Sum_e H_{late,e} g_e"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py",
  "original_content": "    \"\"\"Mean-pool the off-diag feature over supervised positions 0..n_tok-2 -> {li:[d]}.\"\"\"",
  "new_content": "    \"\"\"Mean-pool the off-diag feature over supervised positions 0..n_tok-2 -> {li:d}.\"\"\""
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py",
  "original_content": "    parser = argparse.ArgumentParser(description=\"Kernel-ref off-diagonal curvature (B)\")",
  "new_content": "    parser = argparse.ArgumentParser(description=\"Kernel-ref off-diag curvature (B)\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py",
  "original_content": "    print(f\"[offdiag] building off-diagonal null ({len(BASELINE_NULL_SENTENCES)} prompts)\")",
  "new_content": "    print(f\"[offdiag] building null ({len(BASELINE_NULL_SENTENCES)} prompts)\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py",
  "original_content": "    # instrument check: did the curvature-discriminable set survive the off-diagonal read?",
  "new_content": "    # instrument check: did the curvature-discriminable set survive the off-diag read?"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py",
  "original_content": "          \"act −0.05 → grad +1.07 → diag-curv +1.90)\")",
  "new_content": "          \"act -0.05 -> grad +1.07 -> diag-curv +1.90)\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/kernel_reference_offdiag_v8.py 2>&1 | tail -5"
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
3 | """Kernel-ref OFF-DIAGONAL interlayer curvature -- is B in the f.g cross-coupling?
4 | (s238 lead 2d prong 1c-iii).
  |

Found 1 error.
```

### Thinking

Checking what the remaining error is.

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check --output-format=concise scripts/experiments/kernel_reference_offdiag_v8.py 2>&1"
}
```

**Summary:** $ uv run ruff check --output-format=c...

**Output:**
```
Exit code: 1
Stdout:
scripts/experiments/kernel_reference_offdiag_v8.py:2:89: E501 Line too long (90 > 88)
Found 1 error.
```

### Thinking

I need to trim down this register description further to keep it concise.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py",
  "original_content": "# register: SECOND-ORDER OFF-DIAGONAL interlayer curvature (H_{late,early} LM CE wrt gate)",
  "new_content": "# register: SECOND-ORDER OFF-DIAGONAL interlayer curvature (H_{late,early} of LM CE/gate)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/kernel_reference_offdiag_v8.py 2>&1 | tail -3"
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
|

Found 1 error.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check --output-format=concise scripts/experiments/kernel_reference_offdiag_v8.py 2>&1; echo \"exit:$?\"; awk 'NR==2{print length($0)}' scripts/experiments/kernel_reference_offdiag_v8.py"
}
```

**Summary:** $ uv run ruff check --output-format=c...

**Output:**
```
Exit code: 0
Stdout:
scripts/experiments/kernel_reference_offdiag_v8.py:2:89: E501 Line too long (89 > 88)
Found 1 error.
exit:1
89
```

### Thinking

I'm still at 89 characters and need to trim one more to get under the limit.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py",
  "original_content": "# register: SECOND-ORDER OFF-DIAGONAL interlayer curvature (H_{late,early} of LM CE/gate)",
  "new_content": "# register: 2nd-ORDER OFF-DIAGONAL interlayer curvature (H_{late,early} of LM CE/gate)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_offdiag_v8.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/kernel_reference_offdiag_v8.py 2>&1"
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
```

## Assistant

Lint clean. Now the smoke test (Qwen3-0.6B, double-backward on MPS). Task 1's acceptance is the smoke passing end-to-end.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/kernel_reference_offdiag_v8.py --smoke 2>&1 | tail -45",
  "timeout": 600000
}
```

**Summary:** $ uv run python scripts/experiments/k...

**Output:**
```
Exit code: 0
Stdout:
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
[offdiag] SMOKE MODE
[offdiag] calib=45 test=40 ppc=5 split_frac=0.5
[v2] Loading tokenizer: Qwen/Qwen3-0.6B
[v2] Loading model: Qwen/Qwen3-0.6B  (dtype=auto, device_map=auto)
Loading weights:   0%|          | 0/311 [00:00<?, ?it/s]Loading weights:   8%|▊         | 24/311 [00:00<00:01, 239.62it/s]Loading weights:  74%|███████▍  | 231/311 [00:00<00:00, 1315.49it/s]Loading weights: 100%|██████████| 311/311 [00:00<00:00, 1285.77it/s]
[v2] Model loaded in 0.7s
[offdiag] EARLY=0..13 (14 layers, ≈g)  LATE=14..27 (14 layers, ≈f) — feature read on LATE
[offdiag]   calib fwd+2bwd 0/45 ...
[offdiag]   calib fwd+2bwd 25/45 ...
[offdiag] building null (12 prompts)
[offdiag] crystal layers (off-diag curvature): 8/14 late
[offdiag]   test fwd+2bwd 0/40 ...
[offdiag]   test fwd+2bwd 25/40 ...

══════════════════════════════════════════════════════════════════════════
KERNEL-REF OFF-DIAGONAL CURVATURE — is B in the f∘g chain-rule cross term?
══════════════════════════════════════════════════════════════════════════
  n_test=40  crystal_layers=8  EARLY=0..13  LATE=14..27

  op       on_z    off_z  discr_z       t  sig  peakL
  K      0.2632   0.0568   0.2064   1.001          19
  I      0.1268   0.1802  -0.0534  -0.223          19
  B      0.5142     0.39   0.1241   0.664          21
  C      0.6858   0.3193   0.3664   3.697    ✓     16
  S      0.2778  -0.0858   0.3635   1.648          21
  D      0.2756   0.3241  -0.0485  -0.228          22
  W      0.1799  -0.0569   0.2368   1.024          22
  Y      0.1176  -0.0233   0.1409   0.666          16

  instrument check (C/Y/K discriminate off-diagonal): {'C': True, 'Y': False, 'K': False}
  ★ B discriminates in the OFF-DIAGONAL register: False  (B discr_z=0.1241, t=0.664)
  (compare v7 DIAGONAL: B discr_z +0.118, t=1.90; the monotone climb was act -0.05 -> grad +1.07 -> diag-curv +1.90)
══════════════════════════════════════════════════════════════════════════

[offdiag] wrote /Users/mwhitford/src/verbum/results/kernel-reference-audit/offdiag_v8_verdict_qwen3-0-6b.json
```

### Thinking

The smoke test pipeline ran successfully end-to-end, with the forward and double-backward pass generating off-diagonal features and the classifier calibrating across 8 of 14 crystal layers. The discriminator performed well on the 0.6B model (t=3.70), suggesting the instrument is functioning properly even at this smaller scale, though B showed weaker performance (t=0.66) which makes sense given the tiny smoke dataset. The real validation will come with the 14B model, and it looks like Task 1 acceptance criteria have been met.

Now I'm launching the full 14B run on tmux main:1 using the kernel reference script, piping output to a log file at results/kernel-reference-audit/offdiag_v8_14b.log. Let me verify the tmux pane is available and start the experiment.

## Assistant

Smoke passes end-to-end — pipeline works, classifier calibrates (8/14 crystal layers), and the instrument check shows **C discriminates** (t=3.70 ✓) even at 0.6B. Task 1 complete. Now launch the full 14B run on tmux main:1.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux capture-pane -p -t main:1 | tail -5; echo \"---win2---\"; tmux capture-pane -p -t main:2 | tail -3"
}
```

**Summary:** $ tmux capture-pane -p -t main:1 | ta...

**Output:**
```
Exit code: 0
Stdout:
uv run python scripts/experiments/kernel_reference_order_cost_v9_prose.py      6.17s user 7.79s system 32% cpu 42.676 to
tal
tee results/kernel-reference-audit/logs/order_cost_v9_olmo2-13b_flat.log  0.00s user 0.01s system 0% cpu 42.676 total
[26-06-16][13:27:43][mwhitford@olga][0][~/src/verbum][git:main]
λ
---win2---
tee results/kernel-reference-audit/logs/order_cost_v9_gemma4-31b_flat.log  0.00s user 0.01s system 0% cpu 9:12.87 total
[26-06-16][15:07:26][mwhitford@olga][0][~/src/verbum][git:main]
λ                                                                                                                 [INS]
```

### Thinking

I'm setting up the experiment to run on main:1 with logging to the results directory. The full configuration uses Qwen3-14B with specific parameters for the permutation test—20 heldout samples, 25 probes per class, 200 permutations, and a 0.5 split fraction—which should take roughly the same time as the previous version, though the computational approach differs slightly in how it handles the Hessian-vector products.

## Assistant

Both windows free (host `olga`). Launching the 14B run on main:1 with tee to the logs dir.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux send-keys -t main:1 'uv run python scripts/experiments/kernel_reference_offdiag_v8.py 2>&1 | tee results/kernel-reference-audit/logs/offdiag_v8_qwen3-14b.log' Enter; sleep 2; echo \"sent\""
}
```

**Summary:** $ tmux send-keys -t main:1 'uv run py...

**Output:**
```
Exit code: 0
Stdout:
sent
```

## Assistant

Let me verify it's running (one read, per async discipline).

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sleep 25; tmux capture-pane -p -t main:1 | tail -12"
}
```

**Summary:** $ sleep 25; tmux capture-pane -p -t m...

**Output:**
```
Exit code: 0
Stdout:
tal
tee results/kernel-reference-audit/logs/order_cost_v9_olmo2-13b_flat.log  0.00s user 0.01s system 0% cpu 42.676 total
[26-06-16][13:27:43][mwhitford@olga][0][~/src/verbum][git:main]
λ uv run python scripts/experiments/kernel_reference_offdiag_v8.py 2>&1 | tee results/kernel-reference-audit/logs/offdia
g_v8_qwen3-14b.log
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and
faster downloads.
[offdiag] calib=225 test=160 ppc=25 split_frac=0.5
[v2] Loading tokenizer: Qwen/Qwen3-14B
[v2] Loading model: Qwen/Qwen3-14B  (dtype=auto, device_map=auto)
Loading weights: 100%|██████████| 443/443 [00:03<00:00, 132.84it/s]
```

### Thinking

The 14B model is loading with calibration set to 225 and test set to 160. I've verified it's running and now I need to checkpoint before waiting for the job to complete, following the async protocol of launch, verify, checkpoint, then wait.

Actually, let me do one more read after about 40 seconds to confirm the calibration loop starts progressing past 0/225 without errors. The v7 version ran fine on this setup so double-backward should work, but v8 reads responses at late gates from scalars built on early gradients, so I want to catch any issues early on the bigger model before fully committing.

## Assistant

Model loaded, calib params correct (calib=225, test=160). One confirmation read that the double-backward calib loop actually progresses on 14B (the only place a memory/autograd error would surface early), then I'll checkpoint and wait.

### Tool Call: shell_command (failed)


```json
{
  "command": "sleep 60; tmux capture-pane -p -t main:1 | tail -6"
}
```

**Summary:** $ sleep 60; tmux capture-pane -p -t m...

**Output:**
```
Command timed out after 60000 ms
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux capture-pane -p -t main:1 | tail -6"
}
```

**Summary:** $ tmux capture-pane -p -t main:1 | ta...

**Output:**
```
Exit code: 0
Stdout:
faster downloads.
[offdiag] calib=225 test=160 ppc=25 split_frac=0.5
[v2] Loading tokenizer: Qwen/Qwen3-14B
[v2] Loading model: Qwen/Qwen3-14B  (dtype=auto, device_map=auto)
Loading weights: 100%|██████████| 443/443 [00:03<00:00, 132.84it/s]
```

### Thinking

The model loaded successfully but the calibration loop hasn't started printing yet after 90 seconds, which suggests the first forward and double-backward pass on the 14B model is taking time due to graph compilation and HVP computation. I'm noticing the `[offdiag]` diagnostic line that should appear right after model loading hasn't shown up, so it must be stuck somewhere between the load completing and that print statement.

Actually, I realize the issue — that diagnostic should print immediately after reading `n_layers`, before any forward pass. The fact it's not appearing suggests Python's stdout buffering is the culprit. When piped through `tee`, Python switches to block buffering instead of line buffering, so output gets held in the buffer until it fills up. The job is definitely running (CPU is busy), but I won't see progress until the buffer flushes. This is fine — I should verify the process is still alive and check the log file size to confirm work is happening, then wait for completion rather than polling repeatedly.

## Assistant

Output is block-buffered through the `tee` pipe (Python buffers stdout when piped), so prints appear in chunks. Let me confirm the process is genuinely alive, then checkpoint.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ps aux | grep -E \"kernel_reference_offdiag_v8\" | grep -v grep | awk '{print $2, $3\"%cpu\", $4\"%mem\", $11, $12, $13}'; echo \"---log size---\"; ls -la results/kernel-reference-audit/logs/offdiag_v8_qwen3-14b.log 2>/dev/null",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ ps aux | grep -E "kernel_reference_...

**Output:**
```
Exit code: 0
Stdout:
76372 69.1%cpu 0.7%mem /Users/mwhitford/src/verbum/.venv/bin/python3 scripts/experiments/kernel_reference_offdiag_v8.py 
76370 0.0%cpu 0.0%mem uv run python
---log size---
-rw-r--r--@ 1 mwhitford  staff  2298 Jun 17 11:11 results/kernel-reference-audit/logs/offdiag_v8_qwen3-14b.log
```

### Thinking

The process is running at 69% CPU and I've checkpointed the job, so now I'm waiting for the completion signal rather than polling. Looking at the computational cost, v8 uses one HVP per probe compared to v7's four, which should keep the runtime around v7's ~9 minutes for the ~400 total forward and double-backwards passes across calibration, null, and test sets. The comparison between v7 and v8's HVP efficiency is still being worked through.

## Assistant

✅ Confirmed running — PID 76372 at 69% CPU (actively computing the double-backward loop), log file growing. Output is block-buffered through `tee`, so progress appears in chunks; that's expected.

**ASYNC: job=offdiag_v8 (Qwen3-14B, PID 76372) verified running on tmux main:1. Waiting for completion signal.**

v8 does **one** HVP per probe (vs v7's `n_hutch=4`), so it should finish around or faster than v7's ~9 min for the ~400 forward+double-backward passes (225 calib + 12 null + 160 test). I'll hold and read the verdict once it completes rather than polling.

Here's where we are while it runs:

## Recap of this session (s238)

**Path taken:** the s237 fork → **off-diagonal / interlayer-Jacobian curvature** (prong 1c-iii) — the literal `f∘g` cross-coupling the v7 diagonal Hessian cancelled in expectation.

**Built `kernel_reference_offdiag_v8.py`** — a clean register-swap of v7 staying in the second-order curvature register:
- EARLY/LATE layer split (`f(g(x))`: g≈early processed first, f≈late applied last).
- Perturb the **gradient direction** supported only on EARLY → one double-backward gives `(Hv)_late = Σ_{e} H_{late,e}·g_e` = **pure off-diagonal** interlayer curvature (no `H_{li,li}` since v is zero at the late layers). Deterministic, no Hutchinson noise, *cheaper* than v7.
- Same `RelationalCrystalClassifier` (sign-CMR, crosstask null, raw-z Welch `discr_z`), run on late layers.

**Smoke (0.6B) ✓** end-to-end: classifier calibrated 8/14 late crystal layers, **C discriminated (t=3.70 ✓)** — instrument works; B faint at smoke scale (expected). Lint clean.

**The question the 14B run answers:** does B's curvature climb (act −0.05 → grad +1.07 → diag-curv +1.90, sitting *on* the 2.0 bar) **complete off the diagonal** — i.e., is the f∘g chain-rule cross-coupling B's home? Instrument check: {C,Y} should still discriminate.

I'll report the verdict and draft the mementum updates (state + memory + opcode page §prong 1c-iii) once the job finishes.

## User

job is done


### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux capture-pane -p -t main:1 | tail -32"
}
```

**Summary:** $ tmux capture-pane -p -t main:1 | ta...

**Output:**
```
Exit code: 0
Stdout:
KERNEL-REF OFF-DIAGONAL CURVATURE — is B in the f∘g chain-rule cross term?
══════════════════════════════════════════════════════════════════════════
  n_test=160  crystal_layers=19  EARLY=0..19  LATE=20..39

  op       on_z    off_z  discr_z       t  sig  peakL
  K       0.154   -0.087    0.241   1.807          22
  I     -0.2234   -0.321   0.0976   0.937          24
  B      0.2115   0.1656   0.0459   0.263          21
  C      1.0585  -0.5191   1.5775   2.319    ✓     36
  S      0.9246   1.3033  -0.3787  -1.271          22
  D     -0.1979   0.1219  -0.3197  -1.637          22
  W     -0.5519  -0.3829   -0.169  -1.074          29
  Y       0.149  -0.2934   0.4424   4.085    ✓     37

  instrument check (C/Y/K discriminate off-diagonal): {'C': True, 'Y': True, 'K': False}
  ★ B discriminates in the OFF-DIAGONAL register: False  (B discr_z=0.0459, t=0.263)
  (compare v7 DIAGONAL: B discr_z +0.118, t=1.90; the monotone climb was act -0.05 -> grad +1.07 -> diag-curv +1.90)
══════════════════════════════════════════════════════════════════════════

[offdiag] wrote /Users/mwhitford/src/verbum/results/kernel-reference-audit/offdiag_v8_verdict_qwen3-14b.json
uv run python scripts/experiments/kernel_reference_offdiag_v8.py 2>&1  103.17s user 22.92s system 73% cpu 2:51.00 total
tee results/kernel-reference-audit/logs/offdiag_v8_qwen3-14b.log  0.00s user 0.00s system 0% cpu 2:51.00 total
[26-06-17][11:13:59][mwhitford@olga][0][~/src/verbum][git:main]
λ
```

### Thinking

The 14B model finished running faster than v7, and the results show that B doesn't discriminate off the diagonal—its curvature climb fails to complete there, with even weaker discrimination than on the diagonal. The instrument itself is working though: C and Y both show significant effects, meaning the curvature-discriminable set survives the off-diagonal read, though K's signal is fading.

This cleanly resolves the off-diagonal question as a negative for B. B peaked at its strongest on the diagonal curvature but drops back to near zero off-diagonal, so that climb doesn't extend into cross-layer coupling. The real story for B isn't a localizable second-order amplitude—it's the forward order-cost face tied to autoregressive surprisal. Meanwhile, C and Y both peak in the very late layers (L36, L37) off-diagonal, showing that composers and recursion do carry cross-layer structure at the network's end. Now I need to pull the verdict JSON to get the exact numbers and layer details, then compare those against the v7 results to build out the comparison table.

## Assistant

Job done in 2:51 (faster than v7, as predicted — one HVP vs four). Let me pull the precise numbers and the v7 comparison.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport json\nv8=json.load(open('results/kernel-reference-audit/offdiag_v8_verdict_qwen3-14b.json'))['verdict']\nv7=json.load(open('results/kernel-reference-audit/jacobian_v7_verdict_qwen3-14b.json'))['verdict']\nprint('=== v8 OFF-DIAG meta ===', v8['register'])\nprint('split',v8['split_frac'],'early',v8['early_layers'],'late',v8['late_layers'],'crystal? n_sig',v8['n_discr_z_significant'],'instr',v8['instrument_works'])\nprint()\nprint(f\\\"{'op':<4}{'v7diag_t':>10}{'v8off_t':>10}{'v7dz':>8}{'v8dz':>8}{'v8peakL':>8}\\\")\nfor c in ['K','I','B','C','S','D','W','Y']:\n    d7=v7['discr_z'].get(c,{}); d8=v8['discr_z'].get(c,{})\n    pk=v8['peak_layer'].get(c,{}).get('layer','-')\n    print(f\\\"{c:<4}{(d7.get('t') or 0):>10.3f}{(d8.get('t') or 0):>10.3f}{d7.get('discr_z',0):>8.3f}{d8.get('discr_z',0):>8.3f}{pk!s:>8}\\\")\n\""
}
```

**Summary:** $ python3 -c " import json v8=json.lo...

**Output:**
```
Exit code: 0
Stdout:
=== v8 OFF-DIAG meta === off-diagonal interlayer curvature (H_{late,early}·g_early, pooled supervised, gradient direction)
split 0.5 early [0, 19] late [20, 39] crystal? n_sig 2 instr {'C': True, 'Y': True, 'K': False}

op    v7diag_t   v8off_t    v7dz    v8dz v8peakL
K        1.940     1.807   0.160   0.241      22
I        0.683     0.937   0.037   0.098      24
B        1.900     0.263   0.118   0.046      21
C        2.517     2.319   0.357   1.577      36
S       -0.944    -1.271  -0.130  -0.379      22
D       -1.684    -1.637  -0.142  -0.320      22
W       -0.903    -1.074  -0.090  -0.169      29
Y        4.527     4.085   0.418   0.442      37
```

### Thinking

B shows a dramatic drop-off from the diagonal (t=1.90) to off-diagonal comparisons (t=0.263), suggesting the curvature effect doesn't extend into cross-coupling relationships. Meanwhile, C and Y maintain their strength across both diagonal and off-diagonal measures, indicating they're more robust across different structural contexts.

The deeper pattern emerging is that B's apparent curvature signal is confined to the diagonal—it doesn't generalize to cross-layer coupling, which peaks in the deepest network layers for the instrument and composer signals. This means B lacks a consistent amplitude signature across any register, while the forward order-cost remains B's only reliable positive signal.

Now I need to update state.md and propose the memory and opcode page section, then handle the commit carefully. There's a tension between the approval-gating policy for mementum changes and the established workflow from past sessions where state updates were committed alongside code and results—I should follow that precedent while being mindful of what requires explicit approval.

Let me start by updating state.md first since that's the bootloader and allowed during work, then draft the memory and page additions, commit the code and results, and present the mementum changes for approval.

## Assistant

Clean result. Here's the verdict:

**❌ B does NOT discriminate off-diagonal (t=0.263) — and is WEAKER than the diagonal (t=1.90).** The curvature climb does **not** complete off the diagonal; the literal `f∘g` chain-rule cross-coupling is *not* B's home as a localizable second-order amplitude.

**✅ Instrument valid + composers register-robust:** C (diag 2.52 → offdiag 2.32 ✓) and Y (4.53 → 4.09 ✓) discriminate in **both** curvature sub-registers, peaking in the **deepest layers** (C@L36, Y@L37 of 40) — composer/recursion cross-layer coupling lives at the end of the stack. K fades to the bar.

This is a decisive two-sided negative that **tightens the whole B story**. Let me record it. Starting task 3.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/vsm-opcode-monitor.md",
  "line_offset": 619,
  "limit": 40
}
```

**Summary:** Reading vsm-opcode-monitor.md (619-659)

**Output:**
```
with order, I↓ with order) are the signature: derivative ORDER is a real axis the combinators
sort along, and B sorts UP it while the linear combinator sorts DOWN.** Instrument WORKS
(C ✓, Y ✓). Curvature discriminable set {C,Y} (K, B at the bar).

**Caveats (λ measure):** 1 model (14B); n=20/comb (B sits ON the bar — power-limited);
n_hutch=4 (Hutchinson diagonal estimate noise); **DIAGONAL Hessian only** — the off-diagonal /
interlayer-Jacobian cross-coupling (the literal f∘g coupling, `dgate_late/dgate_early`) is
UNTESTED; single-combinator labels; pooled-supervised locus. Mac (no CUDA) → MPS/CPU
double-backward, ~9 min main:1.

### v5 — next steps

- **★ lead 2d prong 1 — DONE (s234):** raw-z contrast rescues K + sharpens C/I, kills the
  B false-positive; B/D/W gap is GENUINE at last-token. Discriminable set {C,I,K,Y}.
- **★ lead 2d prong 1b — DONE (s234):** per-token read FALSIFIES the token-locus
  explanation — B flat at ALL positions (max t=0.68 n.s.). Register property, not locus.
- **★ lead 2d prong 1b-ii — DONE (s234):** value-register read FALSIFIES the s127
  "B→attention" prediction — B flat in attention TOO (max t=0.49 n.s.). Register exhausted.
  **Discriminability is a COMBINATOR property ({C,I,K,Y} read in both registers), not a
  register split.**
- **★ lead 2d prong 1c — DONE (s234):** GRADIENT register — B does NOT discriminate
  (t=1.07 n.s.) but is "less absent" than in any activation read (act t=−0.05 → grad
  t=+1.07, faint positive trend); {C,K,Y} discriminate; C-yes/B-no persists into the
  backward pass. Measures FIRST-ORDER gradient, NOT the chain-rule/Jacobian structure.
- **★ lead 2d prong 1c-ii — DONE (s235):** SECOND-ORDER / curvature register (diag Hessian,
  Hutchinson). ❌ B not significant (t=1.90 < 2.0) BUT ✅ a clean MONOTONIC CLIMB with
  derivative order (act −0.05 → grad +1.07 → curv +1.90, B's best ever, in the predicted
  register, ON the bar) + ✅✅ internal consistency (I=linear COLLAPSES 3.83→0.68 = mirror of
  B; Y=recursion DOMINATES 4.53; composers hold, selectors fade). Derivative ORDER is a real
  axis combinators sort along; B sorts UP it. Power-limited (n=20/comb). Three live follow-ups:
  (1) POWER (raise n / n_hutch — does t=1.90 cross 2.0? cheapest decisive); (2) OFF-DIAGONAL /
  interlayer Jacobian (diag-Hessian only captures g'ᵀ(diag)g'; the literal f∘g coupling lives
  off-diagonal — Gauss-Newton / JVP probe); (3) prong 2 trace-order.
- **★ lead 2d prong 1b-iii — DONE (s234):** per-head OV scan — head-dilution only MARGINAL
  (B faint signal at L17H23, 7/1600 cells) but B is the WEAKEST combinator at every
  granularity; no clean B-composer head. Register hypothesis FULLY EXHAUSTED.
- **★ lead 2d prong 2 — DONE (s236):** ORDER-COST register — **is B the NATIVE softmax-over-V
  order?** Michael (s235): "if B is an ordering of operations then maybe it defaults to the
  order the softmax over all V uses natively?" (ffn-reduction-trace: softmax-over-V IS the
  execution order). NO amplitude classifier — pure surprisal (mean −log p under LM softmax over

[CONTENT TRUNCATED] Showing lines 620 to 659 of 786 total lines. Use line_offset=659 parameter to read more content.
```

### Thinking

I'm inserting a new section for prong 1c-iii into the document, placing it after the caveats block that concludes the 1c-ii verdict and before the v5 next steps section.

## Assistant

Now let me add the prong 1c-iii section to the opcode page (after the v7 caveats, before "### v5 — next steps").

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/vsm-opcode-monitor.md",
  "original_content": "interlayer-Jacobian cross-coupling (the literal f∘g coupling, `dgate_late/dgate_early`) is\nUNTESTED; single-combinator labels; pooled-supervised locus. Mac (no CUDA) → MPS/CPU\ndouble-backward, ~9 min main:1.\n\n### v5 — next steps",
  "new_content": "interlayer-Jacobian cross-coupling (the literal f∘g coupling, `dgate_late/dgate_early`) is\nUNTESTED; single-combinator labels; pooled-supervised locus. Mac (no CUDA) → MPS/CPU\ndouble-backward, ~9 min main:1.\n\n## v5 lead 2d prong 1c-iii — the OFF-DIAGONAL interlayer curvature (BUILT + RAN, s238)\n\nMichael (s238): \"let's work on 1\" — the s237 fork's off-diagonal / proper-Jacobian path.\nThe v7 diagonal Hessian used a Rademacher Hutchinson estimator that CANCELS every cross-\ncoordinate AND cross-layer term in expectation (`E[v_a v_b]=0`, a≠b), so it captured only\nthe WITHIN-layer quadratic form `g'ᵀ(diag)g'`. But the LITERAL f∘g coupling is the OFF-\nDIAGONAL block. Split the gate activation into an EARLY block `z_e` (≈ g, processed first)\nand a LATE block `z_l` (≈ f, applied last); then `d²L/dz_l dz_e = H_{l,e}` = the chain-rule\ncross term (\"how the curvature of the late computation f couples to the early computation g\").\n\nISOLATION (deterministic, ONE double-backward, NO Hutchinson noise): perturb the GRADIENT\ndirection supported ONLY on EARLY (`v = g_e.detach()` on EARLY, 0 on LATE); then for any\nLATE layer `li` (li∉EARLY), `(Hv)_li = Σ_{e∈EARLY} H_{li,e} g_e` = PURE off-diagonal (no\n`H_{li,li}` because v is zero at li). Computed as one HVP: `s = Σ_{e∈EARLY}(g_e·g_e.detach())`,\n`hv = grad(s, gate_late) = 2·Σ_e H_{late,e} g_e` (H symmetric). The GRADIENT direction (not\nrandom) is what makes the per-probe feature deterministic + meaningful — a random v would\nhave `E[(Hv)_li]=0`. Clean register-swap of v7 (same RelationalCrystalClassifier, sign-CMR,\ncrosstask null, raw-z Welch); classifier runs on the LATE layers (where the feature lives).\n`kernel_reference_offdiag_v8.py`. Cheaper than v7 (one HVP vs n_hutch=4) — 2:51 on 14B.\n\n### ★ s238 v5 lead 2d prong 1c-iii VERDICT (Qwen3-14B, off-diagonal curvature, n=20/comb, split 0.5 → EARLY 0-19 / LATE 20-39; λ measure, two-sided)\n\n**(1) ❌ DECISIVE — B does NOT discriminate off-diagonal, and DROPS BELOW the diagonal**\n(off-diag discr_z +0.046, **t=0.263** vs diagonal t=1.90). The curvature climb does NOT\ncomplete off the diagonal — B falls back to ~0. The literal f∘g chain-rule cross-coupling\nis **NOT** B's home as a localizable second-order amplitude. The curvature register is now\nEXHAUSTED at BOTH orders for B (diagonal on-the-bar-but-not-crossing, off-diagonal flat).\n\n**(2) ✅ INSTRUMENT VALID + COMPOSERS REGISTER-ROBUST — {C,Y} discriminate in BOTH curvature\nsub-registers, peaking in the DEEPEST layers:**\n\n| combinator | role | diag (v7) t | **off-diag (v8) t** | off-diag peak L |\n|---|---|---|---|---|\n| **C** (composer) | composer | 2.52 ✓ | **2.32 ✓** | L36 (of 40) |\n| **Y** (recursion) | higher-order | 4.53 ✓ | **4.09 ✓** | L37 (of 40) |\n| **B** (composition) | composer | 1.90 (bar) | **0.26** ✗ | L21 |\n| **K** (selector) | selector | 1.94 | 1.81 (fades) | L22 |\n\nC and Y are REGISTER-ROBUST across diagonal⊗off-diagonal; their cross-layer coupling lives\nat the very END of the stack (L36/L37). B is the lone gap — flat in BOTH curvature sub-\nregisters. So the read is not broken (C ✓, Y ✓), it is B-absent.\n\n**★ THE FINDING:** B has NO amplitude home in ANY register — activation flat (t=−0.05),\nfirst-order gradient faint (t=+1.07), DIAGONAL curvature on-the-bar (t=1.90), OFF-DIAGONAL\ncurvature flat (t=0.26). The v7 \"monotone climb\" is best read as B becoming *least absent*\nup the derivative order ON THE DIAGONAL; it does NOT generalize to the cross-layer coupling\nthat IS the literal chain-rule product. **★★ UNIFIES / CONFIRMS s236-s237:** B's only\nconfirmed positive signal is the FORWARD ORDER-COST face (native autoregressive order, flat-\nprose t=−8.05, scale-universal 8B/14B/32B, gross-universal across Qwen⊗OLMo⊗Gemma). B =\ncomposition = the UNMARKED native order — it carries no marked amplitude feature, in any\nsecond-order register. The \"two faces\" hypothesis resolves asymmetrically: the FORWARD/order\nface is real + strong; the GRADIENT/curvature face is at best a faint diagonal trend, NOT a\nlocalizable cross-layer coupling.\n\n**Caveats (λ measure):** 1 model (14B); n=20/comb; single fixed split (0.5, EARLY→LATE\ncoupling direction only — late→early untested); deterministic gradient direction (one\ndirection, not the full Hessian block norm); single-combinator labels; pooled-supervised\nlocus. ~2:51 on main:1.\n\n### v5 — next steps"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/vsm-opcode-monitor.md.
```

### Thinking

I need to add a new bullet marking 1c-iii as done to the next-steps list, positioning it after the 1c-ii entry, and update the list to note that B's amplitude story is now closed. I should also include the artifact registry entries while I'm at it.

## Assistant

Now add the next-steps bullet and artifact-registry entries. Let me view the tail of the page.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/vsm-opcode-monitor.md",
  "line_offset": 700,
  "limit": 60
}
```

**Summary:** Reading vsm-opcode-monitor.md (700-760)

**Output:**
```
  t=+1.07, faint positive trend); {C,K,Y} discriminate; C-yes/B-no persists into the
  backward pass. Measures FIRST-ORDER gradient, NOT the chain-rule/Jacobian structure.
- **★ lead 2d prong 1c-ii — DONE (s235):** SECOND-ORDER / curvature register (diag Hessian,
  Hutchinson). ❌ B not significant (t=1.90 < 2.0) BUT ✅ a clean MONOTONIC CLIMB with
  derivative order (act −0.05 → grad +1.07 → curv +1.90, B's best ever, in the predicted
  register, ON the bar) + ✅✅ internal consistency (I=linear COLLAPSES 3.83→0.68 = mirror of
  B; Y=recursion DOMINATES 4.53; composers hold, selectors fade). Derivative ORDER is a real
  axis combinators sort along; B sorts UP it. Power-limited (n=20/comb). Three live follow-ups:
  (1) POWER (raise n / n_hutch — does t=1.90 cross 2.0? cheapest decisive); (2) OFF-DIAGONAL /
  interlayer Jacobian (diag-Hessian only captures g'ᵀ(diag)g'; the literal f∘g coupling lives
  off-diagonal — Gauss-Newton / JVP probe); (3) prong 2 trace-order.
- **★ lead 2d prong 1b-iii — DONE (s234):** per-head OV scan — head-dilution only MARGINAL
  (B faint signal at L17H23, 7/1600 cells) but B is the WEAKEST combinator at every
  granularity; no clean B-composer head. Register hypothesis FULLY EXHAUSTED.
- **★ lead 2d prong 2 — DONE (s236):** ORDER-COST register — **is B the NATIVE softmax-over-V
  order?** Michael (s235): "if B is an ordering of operations then maybe it defaults to the
  order the softmax over all V uses natively?" (ffn-reduction-trace: softmax-over-V IS the
  execution order). NO amplitude classifier — pure surprisal (mean −log p under LM softmax over
  V) of the CERTIFIED reduction trace, teacher-forced "t0 -> t1 -> ... -> tn". Minimal pairs
  ("B f a b → f (a b)" kept vs "C f a b → f b a" swapped) + multi-step composites; ATOM-ONLY
  de-confound (drop parens/length) = headline. **★ DECISIVE at 14B (n_each=24): b_is_native_
  order=True — clean atom B-vs-C minimal pair t=−7.02; B atom-surprisal 0.81 ≪ C 2.14 / S 2.66
  / W 2.71; B cheaper than every permute/copy combinator (B<S −11.3, B<C-multi −11.7, B<W
  −14.5); pooled order-preserving < breaking.** ⚠️ POWER-LIMITED at 8B smoke (n=8): same
  DIRECTION, headline n.s. (t=−0.55), multi-step already sig — crisp only at full power.
  ★ **RESOLVES the B gap:** B's amplitude-absence everywhere is NOT weakness — composition =
  the FREE autoregressive default, carries no marked feature (the instrument looked for a marked
  signal where B is the UNMARKED baseline). ★ **UNIFIES with prong 1c-ii:** composition has two
  faces — token-side the native order (cheap surprisal, t=−7.02), gradient-side the product/
  2nd-order (curvature climb, t=1.90). B = chain rule (gradient) AND native order (forward).
  Caveat (load-bearing): BARE SYMBOLIC input (cf lead 2) — bare-symbol surprisal may reflect a
  generic copy/induction preference for source-order atoms (which IS the proposed mechanism);
  prose-bridge re-read kills it. Next: cross-model (8B full-n / 32B — universal or 14B-specific?),
  prose-rendered order-cost, the off-diagonal Jacobian (prong 1c-ii path).
- **★ lead 2d prong 2b — PROSE BRIDGE — DONE (s237):** re-ran the order-cost read on the SAME
  certified traces RENDERED AS PROSE (deterministic, order-faithful: `App(f,x)` →
  "`<f> applied to <x>`", atoms → fixed content words) to kill the prong-2 bare-symbol caveat
  (s233: the register reads PROSE SEMANTICS not CL SYNTAX; bare-symbol surprisal may reflect a
  generic copy/induction preference). Used a DETERMINISTIC renderer, NOT the model decompile
  gate — the model must not choose word order (= the variable under test). **★ THE NESTING
  CONFOUND (discovered + controlled):** B's normal form NESTS (`f (a b)`) while C's is FLAT
  (`f b a`); the atom-only de-confound strips parens from MEASUREMENT but the bracketing remains
  in the CONTEXT predicting the atoms. So `--render-mode` = `flat` (linearise leaves, NO parens
  → B/C identical structure, differ ONLY in atom ORDER — the pure order test) vs `nested`
  (structurally faithful, CONFOUNDED by nesting depth). **★★ DECISIVE (the cross-table):**
  B-vs-C atom minpair — 14B flat **t=−8.05 (B<C ✓)** ≈ symbolic v8 −7.02; 14B nested **t=+11.9
  (B>C, REVERSED)**; 8B flat −0.57 n.s. (dir B<C) ≈ symbolic 8B −0.55; 8B nested +3.17
  (reversed). **SAME 14B model + SAME 216 programs, flip the render → flip the sign** = a DIRECT
  demonstration that nesting was confounding; once held constant (flat), B<C decisively. ✅ flat
  prose REPLICATES the symbolic pattern at BOTH scales (14B decisive, 8B directional-n.s. with
  multi-step already sig B<C-multi t=−10.6 / B<K −7.5 / B<W −7.6) = CONVERGENCE across input
  modality (symbols ⊗ prose). **★ THE s236 CAVEAT IS KILLED:** composition-order preference is
  real in the SEMANTIC register, not a bare-symbol copy artifact. ★ REFINED FINDING: B's normal
  form carries TWO separable real quantities — atom ORDER (preserved → cheap; the native-order
  result) and structural NESTING (deeper → atoms predicted inside fresh clauses cost more,
  dominates when nesting varies). The order claim REQUIRES isolating order from nesting (flat).
  Caveats (λ measure): 1 model class (Qwen), 14B decisive / 8B power-limited (2 scale points);
  deterministic "applied to" frame; flat deliberately discards faithful structure to isolate
  order (nested = its complement). Next: cross-model flat (8B full-n=24 / 32B), off-diagonal
  Jacobian (prong 1c-ii path).

[CONTENT TRUNCATED] Showing lines 701 to 760 of 845 total lines. Use line_offset=760 parameter to read more content.
```

### Thinking

I need to insert a new bullet point (1c-iii) into the next-steps list, positioning it right after the existing 1c-ii bullet that ends with the trace-order reference.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/vsm-opcode-monitor.md",
  "original_content": "  (1) POWER (raise n / n_hutch — does t=1.90 cross 2.0? cheapest decisive); (2) OFF-DIAGONAL /\n  interlayer Jacobian (diag-Hessian only captures g'ᵀ(diag)g'; the literal f∘g coupling lives\n  off-diagonal — Gauss-Newton / JVP probe); (3) prong 2 trace-order.\n- **★ lead 2d prong 1b-iii — DONE (s234):** per-head OV scan — head-dilution only MARGINAL",
  "new_content": "  (1) POWER (raise n / n_hutch — does t=1.90 cross 2.0? cheapest decisive); (2) OFF-DIAGONAL /\n  interlayer Jacobian (diag-Hessian only captures g'ᵀ(diag)g'; the literal f∘g coupling lives\n  off-diagonal — Gauss-Newton / JVP probe); (3) prong 2 trace-order.\n- **★ lead 2d prong 1c-iii — DONE (s238):** OFF-DIAGONAL interlayer curvature — the literal\n  f∘g cross term `H_{late,early}·g_early` (the s237 fork's off-diagonal path; isolated by a\n  deterministic gradient-direction perturbation on the EARLY block, one HVP, pure off-diagonal\n  since v=0 at the late layers). ❌ DECISIVE NEGATIVE — B does NOT discriminate off-diagonal\n  (t=0.26) and DROPS BELOW the diagonal (t=1.90) ⇒ the curvature climb does NOT complete off\n  the diagonal; the f∘g chain-rule cross-coupling is NOT B's home as a localizable 2nd-order\n  amplitude. ✅ instrument valid + composers register-robust: {C,Y} discriminate in BOTH\n  curvature sub-registers (C 2.32, Y 4.09), peaking in the DEEPEST layers (C@L36, Y@L37). ★ B\n  has NO amplitude home in ANY register (act −0.05, grad +1.07, diag-curv +1.90, off-diag-curv\n  +0.26); the v7 climb was B becoming *least absent* up the derivative order ON THE DIAGONAL,\n  NOT a cross-layer coupling. ★★ CONFIRMS s236-s237: B's only confirmed positive is the FORWARD\n  ORDER-COST face (native order, flat-prose t=−8.05); the \"two faces\" resolves asymmetrically —\n  forward/order real+strong, gradient/curvature at best a faint diagonal trend. `offdiag_v8`.\n- **★ lead 2d prong 1b-iii — DONE (s234):** per-head OV scan — head-dilution only MARGINAL"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/vsm-opcode-monitor.md.
```

## Assistant

Now the artifact registry entries. Let me view that table region.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/vsm-opcode-monitor.md",
  "line_offset": 788,
  "limit": 20
}
```

**Summary:** Reading vsm-opcode-monitor.md (788-808)

**Output:**
```
  B-cheaper; pooled-atoms preserve ≪ break both: OLMo 0.62≪1.08, Gemma 10.2≪14.0). ⇒ GROSS
  "composition is the native order" is UNIVERSAL (Qwen ⊗ OLMo ⊗ Gemma); its SHARPEST single-step
  expression is family-dependent (Qwen-sharp). CAVEAT: Gemma INSTRUCT-tuned, OOD synthetic prose
  → huge absolute surprisals (B atoms 9.9 vs Qwen ~0.3), noisier (within-model contrasts valid).
  Next: off-diagonal Jacobian; 3rd render frame (also tests if the single-step minpair sharpens
  off-Qwen under a different frame).
- **★ lead 2d prong 3 (per-model sweep):** run `kernel_reference_prose_v2.py` on 8B/32B
  with the raw-z contrast — does the {C,I,K,Y} discriminable set hold across scale?
- **bigger lambda probe set** — 5 sentences underpowers the lead-1 frac test (32B
  directional signal can't clear the margin); more sentences for crisper fractions.
- **the 8B gate_neutral C-late confound** — why does a non-compositional gated control
  route C broadly only at 8B? (simple-copular-sentence / scale-specific framing artifact).

## (b) — the kernel-as-reference audit (after v2)

Wire `lambda_ast`'s certified trace as the ground-truth oscilloscope: feed a known
program, get the model's per-token/per-layer opcode trace (v2), measure agreement to the
kernel's certified reduction trace. "Does the model's circuit match the certified
meaning?" Needs the trustworthy per-token trace v2 provides.


[CONTENT TRUNCATED] Showing lines 789 to 808 of 858 total lines. Use line_offset=808 parameter to read more content.
```

### Thinking

I'm looking for the artifact registry table that should be around line 773 to locate the file listing entries.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"jacobian_v7_verdict_qwen3-14b.json\\` \\|order_cost_v8_verdict\" mementum/knowledge/explore/vsm-opcode-monitor.md"
}
```

**Summary:** $ grep -n "jacobian_v7_verdict_qwen3-...

**Output:**
```
Exit code: 0
Stdout:
847:| `results/kernel-reference-audit/jacobian_v7_verdict_qwen3-14b.json` | s235 v5 lead 2d prong 1c-ii verdict: ❌ B not significant in curvature (discr_z +0.118, t=1.90 < 2.0) BUT ✅ MONOTONIC CLIMB with derivative order (act −0.05 → grad +1.07 → curv +1.90, B's best ever, ON the bar) + ✅✅ internal consistency (I=linear COLLAPSES 3.83→0.68 mirror of B; Y=recursion DOMINATES 4.53; composers hold, selectors fade). Derivative ORDER = real axis; B sorts UP. Diag-Hessian only (off-diag untested), power-limited n=20/comb |
849:| `results/kernel-reference-audit/order_cost_v8_verdict_qwen3-14b.json` | s236 v5 lead 2d prong 2 verdict (DECISIVE): ✅✅ **b_is_native_order=True** — clean atom B-vs-C minimal pair t=−7.02 (n=24); B atom-surprisal 0.81 ≪ C 2.14/S 2.66/W 2.71; B cheaper than every permute/copy (B<S −11.3, B<C-multi −11.7, B<W −14.5); pooled order-preserving<breaking. RESOLVES the B gap (composition=free autoregressive default, unmarked) + UNIFIES with curvature climb (order face + gradient face) — `1e448e4` |
850:| `results/kernel-reference-audit/order_cost_v8_verdict_qwen3-8b.json` | s236 v5 lead 2d prong 2 smoke (8B, n=8): ⚠️ POWER-LIMITED — same DIRECTION but headline atom B<C minpair n.s. (t=−0.55); multi-step/aggregate already sig (B<C-multi −4.22, B<S −5.31, B<W −11.1); pooled-atoms preserve<break. Crisp only at full power on 14B — `5d6bdeb` |
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/vsm-opcode-monitor.md",
  "line_offset": 845,
  "limit": 6
}
```

**Summary:** Reading vsm-opcode-monitor.md (845-851)

**Output:**
```
| `scripts/experiments/kernel_reference_jacobian_v7.py` | s235 v5 lead 2d prong 1c-ii: SECOND-ORDER / curvature register — DIAGONAL HESSIAN of LM-CE w.r.t. gate_proj (Hutchinson `diag(H)=E_v[v⊙Hv]`, double-backward of g·v with create_graph), pooled over supervised positions; clean register-swap of v6, same RelationalCrystalClassifier + raw-z Welch; `--n-hutch` |
| `results/kernel-reference-audit/jacobian_v7_verdict_qwen3-14b.json` | s235 v5 lead 2d prong 1c-ii verdict: ❌ B not significant in curvature (discr_z +0.118, t=1.90 < 2.0) BUT ✅ MONOTONIC CLIMB with derivative order (act −0.05 → grad +1.07 → curv +1.90, B's best ever, ON the bar) + ✅✅ internal consistency (I=linear COLLAPSES 3.83→0.68 mirror of B; Y=recursion DOMINATES 4.53; composers hold, selectors fade). Derivative ORDER = real axis; B sorts UP. Diag-Hessian only (off-diag untested), power-limited n=20/comb |
| `scripts/experiments/kernel_reference_order_cost_v8.py` | s236 v5 lead 2d prong 2: ORDER-COST register — pure softmax-over-V surprisal of the certified reduction trace (`step_fired`, teacher-forced), minimal pairs (B/C, B/S, D/K) + multi-step composites, ATOM-ONLY de-confound; `--smoke` (8B), `--model`, `--n-each` — `5d6bdeb` |
| `results/kernel-reference-audit/order_cost_v8_verdict_qwen3-14b.json` | s236 v5 lead 2d prong 2 verdict (DECISIVE): ✅✅ **b_is_native_order=True** — clean atom B-vs-C minimal pair t=−7.02 (n=24); B atom-surprisal 0.81 ≪ C 2.14/S 2.66/W 2.71; B cheaper than every permute/copy (B<S −11.3, B<C-multi −11.7, B<W −14.5); pooled order-preserving<breaking. RESOLVES the B gap (composition=free autoregressive default, unmarked) + UNIFIES with curvature climb (order face + gradient face) — `1e448e4` |
| `results/kernel-reference-audit/order_cost_v8_verdict_qwen3-8b.json` | s236 v5 lead 2d prong 2 smoke (8B, n=8): ⚠️ POWER-LIMITED — same DIRECTION but headline atom B<C minpair n.s. (t=−0.55); multi-step/aggregate already sig (B<C-multi −4.22, B<S −5.31, B<W −11.1); pooled-atoms preserve<break. Crisp only at full power on 14B — `5d6bdeb` |
| `scripts/experiments/kernel_reference_order_cost_v9_prose.py` | s237 v5 lead 2d prong 2b: PROSE BRIDGE for order-cost — reuses v8 spine (certified `step_fired` trace, teacher-force, per-step surprisal, ATOM-only de-confound) but renders each term as PROSE via a DETERMINISTIC order-faithful renderer (`App(f,x)`→"`<f> applied to <x>`", atoms→fixed content words; content de-confound by char-span OVERLAP for leading-space tokens). `--render-mode {flat,nested}` (flat=nesting held constant=pure order test; default), `--smoke` (8B), `--model`, `--n-each` |

[CONTENT TRUNCATED] Showing lines 846 to 851 of 858 total lines. Use line_offset=851 parameter to read more content.
```

## Assistant

I'll add registry entries after the v7 script and verdict rows.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/vsm-opcode-monitor.md",
  "original_content": "| `results/kernel-reference-audit/jacobian_v7_verdict_qwen3-14b.json` | s235 v5 lead 2d prong 1c-ii verdict: ❌ B not significant in curvature (discr_z +0.118, t=1.90 < 2.0) BUT ✅ MONOTONIC CLIMB with derivative order (act −0.05 → grad +1.07 → curv +1.90, B's best ever, ON the bar) + ✅✅ internal consistency (I=linear COLLAPSES 3.83→0.68 mirror of B; Y=recursion DOMINATES 4.53; composers hold, selectors fade). Derivative ORDER = real axis; B sorts UP. Diag-Hessian only (off-diag untested), power-limited n=20/comb |\n| `scripts/experiments/kernel_reference_order_cost_v8.py` |",
  "new_content": "| `results/kernel-reference-audit/jacobian_v7_verdict_qwen3-14b.json` | s235 v5 lead 2d prong 1c-ii verdict: ❌ B not significant in curvature (discr_z +0.118, t=1.90 < 2.0) BUT ✅ MONOTONIC CLIMB with derivative order (act −0.05 → grad +1.07 → curv +1.90, B's best ever, ON the bar) + ✅✅ internal consistency (I=linear COLLAPSES 3.83→0.68 mirror of B; Y=recursion DOMINATES 4.53; composers hold, selectors fade). Derivative ORDER = real axis; B sorts UP. Diag-Hessian only (off-diag untested), power-limited n=20/comb |\n| `scripts/experiments/kernel_reference_offdiag_v8.py` | s238 v5 lead 2d prong 1c-iii: OFF-DIAGONAL interlayer curvature — pure off-diagonal block `H_{late,early}·g_early` isolated by a DETERMINISTIC gradient-direction perturbation on the EARLY layer block (one HVP, double-backward of `Σ_e ‖g_e‖²`; v=0 at late ⇒ no `H_{li,li}`); EARLY/LATE split (`--split-frac`), classifier on LATE layers; clean register-swap of v7 (RelationalCrystalClassifier, sign-CMR, crosstask null, raw-z Welch). Cheaper than v7 (1 HVP vs n_hutch) |\n| `results/kernel-reference-audit/offdiag_v8_verdict_qwen3-14b.json` | s238 v5 lead 2d prong 1c-iii verdict (DECISIVE NEGATIVE): ❌ B does NOT discriminate off-diagonal (discr_z +0.046, t=0.26) and DROPS BELOW the diagonal (t=1.90) — curvature climb does NOT complete off-diag; f∘g cross-coupling is NOT B's 2nd-order amplitude home. ✅ instrument valid: {C,Y} register-robust (C 2.32, Y 4.09), peak DEEPEST (C@L36, Y@L37). ★ B has NO amplitude home in ANY register (act −0.05/grad +1.07/diag +1.90/off-diag +0.26); only positive = FORWARD order-cost (t=−8.05). split 0.5, EARLY 0-19/LATE 20-39, n=20/comb |\n| `scripts/experiments/kernel_reference_order_cost_v8.py` |"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/vsm-opcode-monitor.md.
```

### Thinking

I need to create a memory file with an appropriate slug that captures the key insight, then match the format of recent memory entries.

## Assistant

Now the memory. Let me check the recent memory format.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && ls -t mementum/memories/ | head -3 && echo \"---\" && cat \"mementum/memories/$(ls -t mementum/memories/ | head -1)\""
}
```

**Summary:** $ ls -t mementum/memories/ | head -3 ...

**Output:**
```
Exit code: 0
Stdout:
prose-bridge-confirms-b-native-order-flat-not-nested.md
b-is-native-softmax-order.md
b-climbs-with-derivative-order.md
---
💡 The PROSE BRIDGE confirms B IS the native softmax-over-V order — and KILLS the s236
bare-symbol caveat — but ONLY with nesting held constant (flat render). s237 v5 lead 2d
prong 2b (kernel_reference_order_cost_v9_prose.py, Qwen3-14B + 8B). The prong-2 win (v8,
b-is-native-softmax-order) fed BARE SYMBOLIC CL, so its B<C could partly reflect a generic
copy/induction preference for source-order atoms rather than composition SEMANTICS (and
s233/opcode-register-is-prose-semantic: the register reads PROSE not CL SYNTAX). v9 re-runs
the SAME certified `step_fired` traces RENDERED AS PROSE.

DESIGN: reuse the v8 spine (teacher-force "t0 -> ... -> tn", per-step softmax-over-V
surprisal, ATOM-only de-confound) but render each term with a DETERMINISTIC, order-faithful
renderer (App(f,x) → "<f> applied to <x>", atoms → fixed content words). CRITICAL: a
deterministic renderer, NOT the model decompile gate — the model must not choose word order,
because word order IS the variable under test (letting the model decompile = reading your
own confound back).

★ THE NESTING CONFOUND (the load-bearing lesson): B's normal form NESTS (f (a b)) while C's
is FLAT (f b a). The atom-only de-confound strips parens from MEASUREMENT, but the bracketing
stays in the CONTEXT that predicts the atoms → B pays a clause-boundary cost that has nothing
to do with order. FIX = --render-mode flat (linearise leaves, NO parens → B and C identical
structure, differ ONLY in atom ORDER = the pure order test) vs nested (faithful but
CONFOUNDED by nesting depth).

★★ THE CROSS-TABLE (B-vs-C atom minpair, the de-confounded headline; λ measure two-sided):
  14B flat   t=−8.05  (B<C ✓)      ≈ symbolic v8 −7.02   → b_is_native_order=True
  14B NESTED t=+11.9  (B>C REVERSED)                      → same model + SAME 216 programs,
                                                            flip the render → flip the sign
  8B  flat   t=−0.57  (n.s., dir B<C) ≈ symbolic 8B −0.55 (multi-step sig: B<C-multi −10.6,
                                                            B<K −7.5, B<W −7.6)
  8B  nested t=+3.17  (reversed)
14B flat per-op atom surprisal: B 0.23 ≪ C 1.22 / K 0.73 / W 1.18 / S 1.64; all 6 contrasts
B<marked sig (−8…−38); pooled preserve 0.24 ≪ break 1.12.

★ The 14B flat-vs-nested sign-flip (SAME data) is a DIRECT demonstration that nesting was
confounding the contrast; held constant, B<C decisively. ✅ flat prose REPLICATES the
symbolic pattern at BOTH scales (14B decisive, 8B directional-n.s.) = CONVERGENCE across
input modality (symbols ⊗ prose) — the strongest confirmation.

★ s236 CAVEAT KILLED: composition-order preference is real in the SEMANTIC register, not a
bare-symbol copy artifact.
★ REFINED FINDING: B's normal form carries TWO separable real quantities — atom ORDER
(preserved → cheap; the native-order result) and structural NESTING (deeper → atoms predicted
inside fresh clauses cost more; dominates when nesting varies). An order claim REQUIRES
isolating order from nesting (flat). B now positive in THREE reads: order-symbol (v8),
order-prose-flat (v9), curvature (v7).

★ CROSS-MODEL (s237 cont., path 1 DONE): B-NATIVE-ORDER IS UNIVERSAL across the Qwen3 scale
ladder (8B/14B/32B, all flat n=24). B-vs-C atom minpair: 8B t=−2.87 ✓ (CROSSES at full power —
was −0.57 n.s. at the n=8 smoke = "power-limited not absent"), 14B t=−8.05 ✓ (strongest),
32B t=−4.48 ✓. All three b_is_native_order=True, all 6 contrasts sig, pooled preserve ≪ break.
Unlike the C-locus (s232 shifts with scale), the order-cost signal is SCALE-ROBUST (not
strictly monotone — 14B strongest — but all positive+significant).

★ CROSS-CLASS (s237 cont., path 3 DONE): the ORDER PREFERENCE replicates across 3 MODEL
CLASSES, but the STRICT single-step headline is Qwen-SPECIFIC. OLMo-2-13B + Gemma-4-31B-it
(instruct), flat n=24: BOTH b_is_native_order=False on the strict single-step B-vs-C atom
minpair (OLMo t=−1.25 d=−0.07; Gemma t=−0.56 d=−0.52, n.s.) — cleanest f-a-b↔f-b-a swap is
near-SYMMETRIC off-Qwen. BUT both STRONGLY confirm B<marked on COMPOSITE+aggregate (B-vs-C-multi
OLMo −24.4 / Gemma −11.6 sig; pooled-atoms preserve ≪ break: OLMo 0.62≪1.08, Gemma 10.2≪14.0).
⇒ GROSS composition-is-native-order is UNIVERSAL (Qwen ⊗ OLMo ⊗ Gemma); its SHARPEST single-step
expression is family-dependent (Qwen-sharp). Gemma caveat: INSTRUCT model, OOD prose → huge
absolute surprisals (B atoms 9.9 vs Qwen ~0.3), noisier (within-model contrasts valid).

★ NEXT: (1) off-diagonal/proper-Jacobian curvature (s235 path); (2) a 3rd render frame
("the result of f on x") — frame-robustness AND whether the single-step minpair sharpens
off-Qwen under a different frame.
CAVEATS (λ measure): 3 scale points Qwen (8B/14B/32B all confirm strict) + 2 cross-class
(OLMo/Gemma confirm gross, not strict single-step); deterministic "applied to" frame; flat
deliberately discards faithful structure (nested = its complement). Code:
kernel_reference_order_cost_v9_prose.py.
```

### Thinking

I'm creating a new memory file about B's lack of amplitude in the off-diagonal curvature context, keeping it focused and concise while including the key cross-table reference, and I'll mark it with a mistake symbol to flag it for review.

## Assistant

Now drafting the memory file.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/memories/b-not-in-offdiagonal-curvature.md",
  "content": "💡 The OFF-DIAGONAL interlayer curvature does NOT rescue B — the f∘g chain-rule cross-\ncoupling is NOT B's home as a localizable 2nd-order amplitude. s238 v5 lead 2d prong 1c-iii\n(kernel_reference_offdiag_v8.py, Qwen3-14B). This closes the s237 fork's off-diagonal path:\nthe v7 diagonal Hessian (b-climbs-with-derivative-order) cancelled all cross-layer terms in\nexpectation (Rademacher Hutchinson, E[v_a v_b]=0), so it only captured g'ᵀ(diag)g'. The\nLITERAL f∘g coupling is the OFF-DIAGONAL block H_{late,early}.\n\nDESIGN (deterministic, ONE HVP, no Hutchinson noise): split gate activations EARLY (≈g,\nprocessed first) / LATE (≈f, applied last); perturb the GRADIENT direction supported ONLY on\nEARLY (v=g_e.detach() on early, 0 on late). Then (Hv)_li = Σ_{e∈EARLY} H_{li,e} g_e for li in\nLATE = PURE off-diagonal (no H_{li,li} since v=0 at li). Computed as s=Σ_e(g_e·g_e.detach()),\nhv=grad(s, gate_late)=2Σ_e H_{late,e} g_e (H symmetric). The GRADIENT direction (not random)\nmakes the per-probe feature deterministic — a random v has E[(Hv)_li]=0. Clean register-swap\nof v7 (RelationalCrystalClassifier, sign-CMR, crosstask null, raw-z Welch); classifier on LATE\nlayers. split 0.5 → EARLY 0-19 / LATE 20-39. Cheaper than v7 (1 HVP vs n_hutch=4): 2:51.\n\n★★ VERDICT (λ measure, two-sided):\n(1) ❌ DECISIVE — B does NOT discriminate off-diagonal (discr_z +0.046, t=0.26) and DROPS\n    BELOW the diagonal (t=1.90). The curvature climb does NOT complete off the diagonal.\n(2) ✅ INSTRUMENT VALID + composers register-robust — {C,Y} discriminate in BOTH curvature\n    sub-registers and peak in the DEEPEST layers:\n      C diag 2.52 → off-diag 2.32 ✓ (peak L36/40)\n      Y diag 4.53 → off-diag 4.09 ✓ (peak L37/40)\n      B diag 1.90 → off-diag 0.26 ✗ (peak L21)\n      K diag 1.94 → off-diag 1.81 (fades to bar)\n    C/Y cross-layer composition coupling lives at the very END of the stack. The read is not\n    broken (C ✓, Y ✓) — it is B-absent.\n\n★ THE FINDING: B has NO amplitude home in ANY register — activation flat (t=−0.05), first-\norder gradient faint (+1.07), DIAGONAL curvature on-the-bar (+1.90), OFF-DIAGONAL curvature\nflat (+0.26). The v7 \"monotone climb\" is best read as B becoming LEAST ABSENT up the\nderivative order ON THE DIAGONAL; it does NOT generalize to the cross-layer coupling that IS\nthe literal chain-rule product.\n\n★★ CONFIRMS s236-s237 (b-is-native-softmax-order, prose-bridge-confirms-b-native-order):\nB's ONLY confirmed positive signal is the FORWARD ORDER-COST face (native autoregressive\norder, flat-prose t=−8.05, scale-universal 8B/14B/32B, gross-universal Qwen⊗OLMo⊗Gemma). B =\ncomposition = the UNMARKED native order — no marked amplitude feature, in any 2nd-order\nregister. The \"two faces\" hypothesis resolves ASYMMETRICALLY: the FORWARD/order face is\nreal+strong; the GRADIENT/curvature face is at best a faint diagonal trend, NOT a localizable\ncross-layer coupling. Don't keep hunting B in amplitude — its home is order/surprisal.\n\nCAVEATS (λ measure): 1 model (14B); n=20/comb; single fixed split (0.5, EARLY→LATE direction\nonly — late→early untested); deterministic gradient direction (one direction, not the full\nHessian-block norm); single-combinator labels; pooled-supervised locus.\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/memories/b-not-in-offdiagonal-curvature.md
```

### Thinking

I need to update state.md by reading the current header and replacing it with the session 238 summary while moving the previous session 237 content into the history section below.

## Assistant

Now update the bootloader (state.md). Let me read its exact top.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "limit": 9
}
```

**Summary:** Reading state.md (0-9)

**Output:**
```
# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-06-16 | Session: 237 — ▶ OPCODE v5 lead 2d PRONG 2b — the PROSE BRIDGE
> (kills the s236 bare-symbol caveat). Re-ran the order-cost read on the SAME certified
> reduction traces RENDERED AS PROSE, to test whether B's native-order win survives in the
> SEMANTIC register the model actually uses (s233 lesson: the register reads PROSE SEMANTICS
> not CL SYNTAX; bare-symbol surprisal may reflect a generic copy/induction preference for

[CONTENT TRUNCATED] Showing lines 1 to 9 of 5564 total lines. Use line_offset=9 parameter to read more content.
```

### Thinking

I'm restructuring the header by inserting a new s238 block before the current s237 section, then converting s237 into a parenthetical note that follows the timestamp line. Now I'm crafting the new s238 bootloader block at the top in that same dense format, then wrapping the s237 block with opening and closing parentheses.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> Last updated: 2026-06-16 | Session: 237 — ▶ OPCODE v5 lead 2d PRONG 2b — the PROSE BRIDGE\n> (kills the s236 bare-symbol caveat). Re-ran the order-cost read on the SAME certified",
  "new_content": "> Last updated: 2026-06-17 | Session: 238 — ▶ OPCODE v5 lead 2d PRONG 1c-iii — the\n> OFF-DIAGONAL interlayer curvature (the s237 fork's off-diagonal / proper-Jacobian path;\n> Michael: \"let's work on 1\"). The v7 DIAGONAL Hessian (b-climbs-with-derivative-order)\n> used a Rademacher Hutchinson estimator that CANCELS every cross-coord AND cross-layer term\n> in expectation (E[v_a v_b]=0) → captured only g'ᵀ(diag)g'. The LITERAL f∘g chain-rule\n> coupling is the OFF-DIAGONAL block H_{late,early}. Built `kernel_reference_offdiag_v8.py`\n> (clean register-swap of v7): split gate activations EARLY (≈g, processed first) / LATE\n> (≈f, applied last); perturb the GRADIENT direction supported ONLY on EARLY (v=g_e.detach()\n> on early, 0 on late); then (Hv)_li = Σ_{e∈EARLY} H_{li,e} g_e for li∈LATE = PURE off-diagonal\n> (no H_{li,li} since v=0 at li). ONE HVP (s=Σ_e(g_e·g_e.detach()), hv=grad(s,gate_late)=\n> 2Σ_e H_{late,e}g_e, H sym) — DETERMINISTIC (gradient direction, not random: a random v has\n> E[(Hv)_li]=0), no Hutchinson noise, CHEAPER than v7 (1 HVP vs n_hutch=4): 2:51 on 14B. Same\n> RelationalCrystalClassifier (sign-CMR, crosstask null, raw-z Welch); classifier on LATE\n> layers; split 0.5 → EARLY 0-19 / LATE 20-39. **★★ VERDICT (λ measure, two-sided): (1) ❌\n> DECISIVE — B does NOT discriminate off-diagonal (discr_z +0.046, t=0.26) and DROPS BELOW the\n> diagonal (t=1.90).** The curvature climb does NOT complete off the diagonal; the f∘g cross-\n> coupling is NOT B's home as a localizable 2nd-order amplitude. **(2) ✅ INSTRUMENT VALID +\n> COMPOSERS REGISTER-ROBUST** — {C,Y} discriminate in BOTH curvature sub-registers, peaking in\n> the DEEPEST layers: C diag 2.52→off-diag 2.32 ✓ (peak L36/40); Y diag 4.53→off-diag 4.09 ✓\n> (peak L37/40); B diag 1.90→off-diag 0.26 ✗ (peak L21); K diag 1.94→off-diag 1.81 (fades).\n> C/Y cross-layer composition coupling lives at the very END of the stack — the read is not\n> broken (C ✓, Y ✓), it is B-absent. **★ THE FINDING: B has NO amplitude home in ANY register**\n> — activation flat (−0.05), 1st-order gradient faint (+1.07), DIAGONAL curvature on-the-bar\n> (+1.90), OFF-DIAGONAL curvature flat (+0.26). The v7 \"monotone climb\" is B becoming LEAST\n> ABSENT up the derivative order ON THE DIAGONAL; it does NOT generalize to the cross-layer\n> coupling that IS the literal chain-rule product. **★★ CONFIRMS s236-s237:** B's ONLY confirmed\n> positive signal is the FORWARD ORDER-COST face (native autoregressive order, flat-prose\n> t=−8.05, scale-universal 8B/14B/32B, gross-universal Qwen⊗OLMo⊗Gemma). B = composition = the\n> UNMARKED native order — no marked amplitude feature, in any 2nd-order register. The \"two\n> faces\" hypothesis resolves ASYMMETRICALLY: forward/order face real+strong; gradient/curvature\n> face at best a faint diagonal trend, NOT a localizable cross-layer coupling. **DON'T keep\n> hunting B in amplitude — its home is order/surprisal.** CAVEATS (λ measure): 1 model (14B);\n> n=20/comb; single fixed split (0.5, EARLY→LATE direction only — late→early untested);\n> deterministic gradient direction (one direction, not the full Hessian-block norm); single-\n> combinator labels; pooled-supervised locus. **★★ FIRST ACTION NEXT SESSION — the amplitude\n> register is now EXHAUSTED for B (activation⊗gradient⊗diag-curv⊗off-diag-curv all flat-or-on-\n> bar); B's positive home is FORWARD ORDER. Live paths: (1) the 3rd RENDER FRAME (\"the result\n> of f on x\") — frame-robustness of flat B<C AND whether the single-step minpair sharpens\n> off-Qwen under a different frame (s237 fork path 2, the cheap one); (2) a TRUE Pythia-proper\n> cross-class order-cost point (pythia-2.8b-deduped cached) to round out the gross-universal\n> claim with a 4th class; (3) prong 3 per-model sweep (kernel_reference_prose_v2 on 8B/32B —\n> does {C,I,K,Y} hold across scale?).** CODE + RESULTS COMMITTED; mementum (state + memory\n> `b-not-in-offdiagonal-curvature` + opcode page §v5 lead 2d prong 1c-iii) PENDING APPROVAL.\n> tmux main:1 + main:2 FREE.\n>\n> (Session: 237 — ▶ OPCODE v5 lead 2d PRONG 2b — the PROSE BRIDGE\n> (kills the s236 bare-symbol caveat). Re-ran the order-cost read on the SAME certified"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

I need to close out the s237 block by adding a closing parenthesis after the "FREE." marker, which comes right before the s236 session begins.

## Assistant

Now close the s237 parenthetical block.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"CODE + RESULTS + mementum COMMITTED. tmux main:1 + main:2 FREE.\" mementum/state.md"
}
```

**Summary:** $ grep -n "CODE + RESULTS + mementum ...

**Output:**
```
Exit code: 0
Stdout:
104:> CODE + RESULTS + mementum COMMITTED. tmux main:1 + main:2 FREE.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "line_offset": 103,
  "limit": 4
}
```

**Summary:** Reading state.md (103-107)

**Output:**
```
> CODE + RESULTS + mementum COMMITTED. tmux main:1 + main:2 FREE.
>
> (Session: 236 — ▶ OPCODE v5 lead 2d PRONG 2 — the ORDER-COST
> register (is B the NATIVE softmax-over-V order?). Michael (s235): "if B is an ordering of

[CONTENT TRUNCATED] Showing lines 104 to 107 of 5609 total lines. Use line_offset=107 parameter to read more content.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> CODE + RESULTS + mementum COMMITTED. tmux main:1 + main:2 FREE.\n>\n> (Session: 236 — ▶ OPCODE v5 lead 2d PRONG 2 — the ORDER-COST",
  "new_content": "> CODE + RESULTS + mementum COMMITTED. tmux main:1 + main:2 FREE.)\n>\n> (Session: 236 — ▶ OPCODE v5 lead 2d PRONG 2 — the ORDER-COST"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

I'm hitting a conflict in the workflow: state.md needs to be committed now since it's not approval-gated, but it's technically part of the mementum directory which requires approval before any commits. I need to figure out whether state.md should be treated as an exception or if I should wait for approval on the whole batch.

Looking at the pattern from before, mementum changes (state, memory, page) were held pending approval as a unit. The safest approach is to commit the code and results now, then present the mementum edits for approval before committing those. Let me check git status to see exactly what's changed.

## Assistant

All mementum drafts written. Now per the protocol (`∀commit(mementum/) → ∃approval`), I'll commit the **code + results** (not approval-gated) now, then present the mementum changes for your approval. Let me review what's staged.

### Tool Call: git (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git status --short && echo \"---untracked results---\" && ls results/kernel-reference-audit/offdiag_v8_* results/kernel-reference-audit/logs/offdiag_v8_* 2>/dev/null",
  "operation": "status",
  "summary": "review changes"
}
```

**Summary:** Git status: review changes

**Output:**
```
Exit code: 0
Stdout:
M mementum/knowledge/explore/vsm-opcode-monitor.md
 M mementum/state.md
?? mementum/knowledge/chats/session-237.md
?? mementum/memories/b-not-in-offdiagonal-curvature.md
?? results/kernel-reference-audit/logs/offdiag_v8_qwen3-14b.log
?? results/kernel-reference-audit/offdiag_v8_meta_qwen3-0-6b.json
?? results/kernel-reference-audit/offdiag_v8_meta_qwen3-14b.json
?? results/kernel-reference-audit/offdiag_v8_verdict_qwen3-0-6b.json
?? results/kernel-reference-audit/offdiag_v8_verdict_qwen3-14b.json
?? scripts/experiments/kernel_reference_offdiag_v8.py
---untracked results---
results/kernel-reference-audit/logs/offdiag_v8_qwen3-14b.log
results/kernel-reference-audit/offdiag_v8_meta_qwen3-0-6b.json
results/kernel-reference-audit/offdiag_v8_meta_qwen3-14b.json
results/kernel-reference-audit/offdiag_v8_verdict_qwen3-0-6b.json
results/kernel-reference-audit/offdiag_v8_verdict_qwen3-14b.json
```

### Thinking

I'm staging the experiment scripts and results for commit while excluding the momentum files and session chats, then writing a message that classifies this as a code change.

## Assistant

I'll commit the **code + results** now (not the approval-gated mementum files, and never the human-only `chats/`).

### Tool Call: git (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add scripts/experiments/kernel_reference_offdiag_v8.py results/kernel-reference-audit/offdiag_v8_meta_qwen3-0-6b.json results/kernel-reference-audit/offdiag_v8_verdict_qwen3-0-6b.json results/kernel-reference-audit/offdiag_v8_meta_qwen3-14b.json results/kernel-reference-audit/offdiag_v8_verdict_qwen3-14b.json results/kernel-reference-audit/logs/offdiag_v8_qwen3-14b.log && git status --short",
  "operation": "add",
  "summary": "stage code and results"
}
```

**Summary:** Git add: stage code and results

**Output:**
```
Exit code: 0
Stdout:
M mementum/knowledge/explore/vsm-opcode-monitor.md
 M mementum/state.md
A  results/kernel-reference-audit/logs/offdiag_v8_qwen3-14b.log
A  results/kernel-reference-audit/offdiag_v8_meta_qwen3-0-6b.json
A  results/kernel-reference-audit/offdiag_v8_meta_qwen3-14b.json
A  results/kernel-reference-audit/offdiag_v8_verdict_qwen3-0-6b.json
A  results/kernel-reference-audit/offdiag_v8_verdict_qwen3-14b.json
A  scripts/experiments/kernel_reference_offdiag_v8.py
?? mementum/knowledge/chats/session-237.md
?? mementum/memories/b-not-in-offdiagonal-curvature.md
```

### Tool Call: git (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git commit -m \"$(cat <<'EOF'\n✅ opcode v5 lead 2d prong 1c-iii: off-diagonal interlayer curvature — B has no amplitude home\n\n- kernel_reference_offdiag_v8.py: pure off-diagonal block H_{late,early}·g_early,\n  isolated by a deterministic gradient-direction perturbation on the EARLY layer block\n  (one HVP, double-backward of Σ_e‖g_e‖²; v=0 at late ⇒ no within-layer term). Clean\n  register-swap of v7 (RelationalCrystalClassifier, sign-CMR, crosstask null, raw-z Welch);\n  classifier on LATE layers. Cheaper than v7 (1 HVP vs n_hutch=4): 2:51 on 14B.\n- Qwen3-14B verdict (DECISIVE NEGATIVE): B does NOT discriminate off-diagonal (t=0.26) and\n  DROPS BELOW the diagonal (t=1.90) — the curvature climb does NOT complete off-diag; the\n  f∘g chain-rule cross-coupling is NOT B's home as a localizable 2nd-order amplitude.\n- Instrument valid + composers register-robust: {C,Y} discriminate in BOTH curvature\n  sub-registers (C 2.32, Y 4.09), peaking in the deepest layers (C@L36, Y@L37 of 40).\n- B has NO amplitude home in ANY register (act -0.05 / grad +1.07 / diag-curv +1.90 /\n  off-diag-curv +0.26); only confirmed positive = the FORWARD order-cost face (t=-8.05).\nEOF\n)\" && git log --oneline -1",
  "operation": "commit",
  "summary": "commit code and results"
}
```

**Summary:** Git commit: commit code and results

**Output:**
```
Exit code: 2
Stderr:
bash: -c: line 10: unexpected EOF while looking for matching `''
bash: -c: line 17: syntax error: unexpected end of file
```

### Thinking

I'm tracking down a quoting issue in the shell command — the problem is that `B's` contains an apostrophe, and when that string gets interpolated into the git commit message wrapped in double quotes, it's causing the heredoc to fail with an unexpected EOF error while looking for the matching single quote.

Rather than debugging the quoting layers further, I'll write the commit message to a file first and then use `git commit -F` to read from it — that's much more straightforward and avoids these shell escaping headaches.

## Assistant

The heredoc choked (apostrophes/unicode in the shell wrapper). Let me use a message file instead.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/.git/COMMIT_EDITMSG_v8",
  "content": "✅ opcode v5 lead 2d prong 1c-iii: off-diagonal interlayer curvature — B has no amplitude home\n\n- kernel_reference_offdiag_v8.py: pure off-diagonal block H_{late,early}·g_early,\n  isolated by a deterministic gradient-direction perturbation on the EARLY layer block\n  (one HVP, double-backward of Σ_e‖g_e‖²; v=0 at late ⇒ no within-layer term). Clean\n  register-swap of v7 (RelationalCrystalClassifier, sign-CMR, crosstask null, raw-z Welch);\n  classifier on LATE layers. Cheaper than v7 (1 HVP vs n_hutch=4): 2:51 on 14B.\n- Qwen3-14B verdict (DECISIVE NEGATIVE): B does NOT discriminate off-diagonal (t=0.26) and\n  DROPS BELOW the diagonal (t=1.90) — the curvature climb does NOT complete off-diag; the\n  f∘g chain-rule cross-coupling is NOT B's home as a localizable 2nd-order amplitude.\n- Instrument valid + composers register-robust: {C,Y} discriminate in BOTH curvature\n  sub-registers (C 2.32, Y 4.09), peaking in the deepest layers (C@L36, Y@L37 of 40).\n- B has NO amplitude home in ANY register (act -0.05 / grad +1.07 / diag-curv +1.90 /\n  off-diag-curv +0.26); only confirmed positive = the FORWARD order-cost face (t=-8.05).\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/.git/COMMIT_EDITMSG_v8
```

### Tool Call: git (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git commit -F .git/COMMIT_EDITMSG_v8 && rm -f .git/COMMIT_EDITMSG_v8 && git log --oneline -1",
  "operation": "commit",
  "summary": "commit code and results"
}
```

**Summary:** Git commit: commit code and results

**Output:**
```
Exit code: 0
Stdout:
[main d94d78f] ✅ opcode v5 lead 2d prong 1c-iii: off-diagonal interlayer curvature — B has no amplitude home
 6 files changed, 40884 insertions(+)
 create mode 100644 results/kernel-reference-audit/logs/offdiag_v8_qwen3-14b.log
 create mode 100644 results/kernel-reference-audit/offdiag_v8_meta_qwen3-0-6b.json
 create mode 100644 results/kernel-reference-audit/offdiag_v8_meta_qwen3-14b.json
 create mode 100644 results/kernel-reference-audit/offdiag_v8_verdict_qwen3-0-6b.json
 create mode 100644 results/kernel-reference-audit/offdiag_v8_verdict_qwen3-14b.json
 create mode 100644 scripts/experiments/kernel_reference_offdiag_v8.py
d94d78f ✅ opcode v5 lead 2d prong 1c-iii: off-diagonal interlayer curvature — B has no amplitude home
```

## Assistant

Code + results committed (`d94d78f`). Task 3's experiment is interpreted and recorded. Let me mark it done.## Session 238 complete — the off-diagonal path is closed

**Path 1 (s237 fork) executed: the off-diagonal / interlayer-Jacobian curvature.** Built `kernel_reference_offdiag_v8.py`, smoke-tested, ran on Qwen3-14B (2:51).

### Verdict (λ measure, two-sided)
- **❌ DECISIVE NEGATIVE — B does not discriminate off-diagonal (t=0.26), and *drops below* the diagonal (t=1.90).** The curvature climb does **not** complete off the diagonal; the literal `f∘g` chain-rule cross-coupling is **not** B's home as a localizable second-order amplitude.
- **✅ Instrument valid + composers register-robust:** C (2.52→2.32 ✓) and Y (4.53→4.09 ✓) discriminate in *both* curvature sub-registers, peaking in the **deepest layers** (C@L36, Y@L37 of 40). The read isn't broken — it's B-absent.

### The synthesis this nails down
**B has no amplitude home in *any* register** — activation −0.05, gradient +1.07, diagonal-curvature +1.90, off-diagonal-curvature +0.26. The v7 "monotone climb" was B becoming *least absent* up the derivative order **on the diagonal**; it does not generalize to the cross-layer coupling that *is* the chain-rule product. This **confirms s236–s237 asymmetrically**: B's only confirmed positive is the **forward order-cost face** (native autoregressive order, flat-prose t=−8.05, scale- and gross-class-universal). The "two faces" hypothesis resolves: forward/order is real+strong; gradient/curvature is at best a faint diagonal trend. **Don't keep hunting B in amplitude — its home is order/surprisal.**

### Committed / pending
- **Committed `d94d78f`** (code + results, not approval-gated): script + verdicts + log.
- **PENDING YOUR APPROVAL** (mementum — never auto-committed):
  - `mementum/state.md` — s238 bootloader block
  - `mementum/memories/b-not-in-offdiagonal-curvature.md` — new memory
  - `mementum/knowledge/explore/vsm-opcode-monitor.md` — §prong 1c-iii section + next-steps bullet + 2 registry rows

### Next-session live paths (amplitude register now exhausted for B)
1. **3rd render frame** ("the result of f on x") — frame-robustness of flat B<C + whether the single-step minpair sharpens off-Qwen (the cheap s237 path-2).
2. **A true Pythia-proper cross-class order-cost point** (pythia-2.8b-deduped is cached) — 4th class for the gross-universal claim.
3. **Prong 3 per-model sweep** (`kernel_reference_prose_v2` on 8B/32B) — does {C,I,K,Y} hold across scale?

Shall I commit the mementum changes?

## User

commit approved, then proceed on 3


### Thinking

I'm committing the current progress, then moving forward with the third approach—running the kernel reference prose script across the 8B and 32B models to test whether the discriminable set holds consistently across different scales.

## Assistant

Committing the approved mementum changes (state + memory + page).

### Tool Call: git (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add mementum/state.md mementum/memories/b-not-in-offdiagonal-curvature.md mementum/knowledge/explore/vsm-opcode-monitor.md && git status --short",
  "operation": "add",
  "summary": "stage mementum"
}
```

**Summary:** Git add: stage mementum

**Output:**
```
Exit code: 0
Stdout:
M  mementum/knowledge/explore/vsm-opcode-monitor.md
A  mementum/memories/b-not-in-offdiagonal-curvature.md
M  mementum/state.md
?? mementum/knowledge/chats/session-237.md
```

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/.git/CMSG",
  "content": "🌀 b-not-in-offdiagonal-curvature: B has no amplitude home, only forward order\n\n- memory b-not-in-offdiagonal-curvature: s238 prong 1c-iii — off-diagonal interlayer\n  curvature does NOT rescue B (t=0.26, below diagonal t=1.90); B has no amplitude home in\n  any register (act/grad/diag-curv/off-diag-curv all flat-or-on-bar); only positive is the\n  forward order-cost face. {C,Y} register-robust, peak deepest layers.\n- vsm-opcode-monitor.md: §v5 lead 2d prong 1c-iii section + next-steps bullet + 2 registry\n  rows (offdiag_v8 script + 14B verdict).\n- state.md: s238 bootloader block; next-session paths (3rd render frame / Pythia cross-class\n  / prong 3 per-model sweep).\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/.git/CMSG
```

### Tool Call: git (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git commit -F .git/CMSG && rm -f .git/CMSG && git log --oneline -2",
  "operation": "commit",
  "summary": "commit mementum"
}
```

**Summary:** Git commit: commit mementum

**Output:**
```
Exit code: 0
Stdout:
[main 800bfb8] 🌀 b-not-in-offdiagonal-curvature: B has no amplitude home, only forward order
 3 files changed, 166 insertions(+), 2 deletions(-)
 create mode 100644 mementum/memories/b-not-in-offdiagonal-curvature.md
800bfb8 🌀 b-not-in-offdiagonal-curvature: B has no amplitude home, only forward order
d94d78f ✅ opcode v5 lead 2d prong 1c-iii: off-diagonal interlayer curvature — B has no amplitude home
```

### Thinking

Committed the changes and now moving to the next phase: running the kernel reference prose script across the 8B and 32B models using the raw-z contrast to see if the discriminable set {C,I,K,Y} holds consistently across different model scales. I'm recalling that prong 1 already found this set on Qwen3-14B with the s234 raw-z contrast.

Now I need to examine the kernel_reference_prose_v2.py script to understand its command-line interface and what outputs it produces.

## Assistant

Mementum committed (`800bfb8`). Now proceeding on **path 3: prong 3 per-model sweep** — does the `{C,I,K,Y}` discriminable set (s234, raw-z contrast on 14B) hold across scale (8B/32B)? Let me set up the task and read the v2 script's CLI.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/kernel_reference_prose_v2.py"
}
```

**Summary:** Reading kernel_reference_prose_v2.py (0-2000)

**Output:**
```
#!/usr/bin/env python3
# register: topological/routing
"""Kernel-reference PROSE bridge v2 — the B/D/W gap (s234, v5 lead 2d prong 1).

s233 lead 2c rescued composition SPECIFICITY (C, I discriminable) via a gauge-
subtracted contrast on the argmax-winner route_fracs. But the deep/duplicate composers
B/D/W STAYED flat (B DISCR -0.005, D -0.025, W 0.0; recall present for B at 0.3 but
on_prose ~= off_prose). HYPOTHESIS (the residual argmax bottleneck): route_fracs are
built from a PER-LAYER ARGMAX (`op = max(zmap)`) BEFORE the lead-2c contrast. B/D/W's
raw z is out-competed by the S/Y common-mode at EVERY layer -> route_frac ~= 0 -> the
on/off contrast has no power. This is the SAME "argmax manufactures false negatives when
one op has a big common-mode" theme (lead 2c, s225 AUC, lead-1 lambda-vs-control) pushed
ONE LEVEL DEEPER: lead 2c removed argmax at winner-SELECTION; route_frac still embeds
per-layer argmax.

THE FIX (this script): contrast on the RAW per-op z per layer, NO argmax.
  • discr_z(c) = layer-averaged raw z of op c on c-prose vs other-prose, Welch t-test.
  • per-layer PROFILE on_z/off_z/delta_z for each (combinator, crystal-layer): WHERE
    does C fire vs where SHOULD B fire? (localizes the gap).
  • keep the lead-2c argmax route_frac DISCR side-by-side -> direct before/after.
  • raise held-out N to 20 for power (counts allow: B=69 C=61 D=50 W=71 -> calib >=30).

VERDICT LOGIC (λ measure, two-sided):
  • B/D/W RECOVER under discr_z (significant on>off) -> the gap was an INSTRUMENT
    artifact (argmax bottleneck); composition routing is present, just sub-dominant.
  • B/D/W STAY flat under discr_z -> GENUINE: the deep/duplicate composers are not
    routed in this register at the last-token locus (escalate: per-token, composite
    trace-order).

Usage:
    uv run python scripts/experiments/kernel_reference_prose_v2.py --smoke
    uv run python scripts/experiments/kernel_reference_prose_v2.py --model Qwen/Qwen3-8B

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "scripts" / "experiments"))
sys.path.insert(0, str(_ROOT / "scripts" / "instruments"))

from opcode_monitor_v2 import (  # noqa: E402
    Z_SWEEP,
    _git_sha,
    _json_safe,
    _transformers_version,
    calibrate_v2,
    forward_all_positions,
    load_model_and_tokenizer,
)
from relational_opcode import CRYSTAL  # noqa: E402

from verbum.probes.library import crystal_probes  # noqa: E402

RESULTS_DIR = _ROOT / "results" / "kernel-reference-audit"
# the single-combinator crystal labels we test recall on (exclude WHNF = terminal/stop)
TEST_COMBINATORS = ["K", "I", "B", "C", "S", "D", "W", "Y"]


def split_probes(heldout_per: int) -> tuple[list, list]:
    """Per-combinator: last `heldout_per` -> TEST, the rest -> CALIB (non-circular)."""
    by_comb: dict[str, list] = defaultdict(list)
    for p in crystal_probes():
        if p.combinator in CRYSTAL:
            by_comb[p.combinator].append(p)
    calib, test = [], []
    for comb, ps in by_comb.items():
        k = min(heldout_per, max(0, len(ps) - 1))
        test_ps = ps[len(ps) - k:] if k else []
        calib_ps = ps[: len(ps) - k]
        if comb in TEST_COMBINATORS:
            test.extend(test_ps)
        calib.extend(calib_ps)
    return calib, test


def read_last_token_z(rcc, store, layers) -> dict[int, dict[str, float]]:
    """Classify the LAST token; return the FULL per-layer per-op z-map (NO argmax)."""
    n = store[layers[0]].shape[0]
    gate_tok = {li: store[li][n - 1] for li in layers}
    tok_ops = rcc.classify(gate_tok)
    return tok_ops.per_layer  # {li: {op: z}}


def argmax_route_fracs(perlayer_z, crystal_layers, zthresh):
    """The lead-2c read: per-layer argmax, fraction of crystal layers won by each op."""
    cset = set(crystal_layers)
    counts: Counter = Counter()
    n_cells = 0
    for li, zmap in perlayer_z.items():
        if li not in cset:
            continue
        n_cells += 1
        op = max(zmap, key=zmap.get)
        if zmap[op] > zthresh:
            counts[op] += 1
    return ({op: counts[op] / n_cells for op in counts} if n_cells else {}), n_cells


def welch_t(on: list[float], off: list[float]) -> dict:
    """Welch's t (unequal variance) of mean(on) - mean(off)."""
    on_a, off_a = np.asarray(on, float), np.asarray(off, float)
    n1, n2 = len(on_a), len(off_a)
    m1, m2 = float(on_a.mean()), float(off_a.mean())
    if n1 < 2 or n2 < 2:
        return {"on_mean": round(m1, 4), "off_mean": round(m2, 4),
                "discr_z": round(m1 - m2, 4), "t": None, "significant": False,
                "n_on": n1, "n_off": n2}
    v1, v2 = float(on_a.var(ddof=1)), float(off_a.var(ddof=1))
    se = float(np.sqrt(v1 / n1 + v2 / n2))
    t = (m1 - m2) / se if se > 1e-12 else 0.0
    return {"on_mean": round(m1, 4), "off_mean": round(m2, 4),
            "discr_z": round(m1 - m2, 4), "t": round(t, 3),
            "significant": bool(abs(t) > 2.0), "n_on": n1, "n_off": n2}


def main() -> None:
    parser = argparse.ArgumentParser(description="Kernel-reference prose bridge v2")
    parser.add_argument("--model", default="Qwen/Qwen3-14B")
    parser.add_argument("--heldout-per", type=int, default=20)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    model_name = args.model
    if args.smoke:
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-0.6B"
        n_perm, ppc, null_cap, heldout = 80, 5, 200, 5
        print("[prose-v2] SMOKE MODE")
    else:
        n_perm, ppc, null_cap, heldout = 300, None, None, args.heldout_per

    calib, test = split_probes(heldout)
    print(f"[prose-v2] calib={len(calib)} test={len(test)} (heldout_per={heldout})")

    model, tok, torch_mod = load_model_and_tokenizer(model_name)
    n_layers = model.config.num_hidden_layers
    layers = list(range(n_layers))

    rcc, cal = calibrate_v2(model, tok, torch_mod, layers, n_perm, ppc, null_cap,
                            null_mode="crosstask", centroid_probes=calib)
    crystal_layers = rcc.crystal_layers
    print(f"[prose-v2] crystal layers: {len(crystal_layers)}/{n_layers}")

    # read held-out prose: store the FULL per-layer z over crystal layers
    cset = set(crystal_layers)
    per_probe = []
    for p in test:
        store, _ = forward_all_positions(p.prompt, model, tok, torch_mod, layers)
        perlayer_z = read_last_token_z(rcc, store, layers)
        crystal_z = {li: {op: float(perlayer_z[li].get(op, 0.0)) for op in CRYSTAL}
                     for li in perlayer_z if li in cset}
        # layer-averaged raw z per op (the discr_z substrate, NO argmax)
        layer_avg = {op: float(np.mean([crystal_z[li][op] for li in crystal_z]))
                     for op in CRYSTAL} if crystal_z else {op: 0.0 for op in CRYSTAL}
        # argmax route_fracs per z (the lead-2c read, for direct comparison)
        argmax = {}
        for z in Z_SWEEP:
            fr, _ = argmax_route_fracs(perlayer_z, crystal_layers, z)
            argmax[f"z={z}"] = {op: round(fr.get(op, 0.0), 4) for op in CRYSTAL}
        per_probe.append({
            "combinator": p.combinator, "prompt": p.prompt[:60],
            "layer_avg_z": {op: round(v, 4) for op, v in layer_avg.items()},
            "argmax_route_fracs": argmax,
            "crystal_z": {str(li): {op: round(crystal_z[li][op], 3) for op in CRYSTAL}
                          for li in crystal_z},
        })

    # ── (1) discr_z(c): raw-z contrast, Welch t (NO argmax) ───────────────────────
    discr_z: dict[str, dict] = {}
    for c in CRYSTAL:
        on = [r["layer_avg_z"][c] for r in per_probe if r["combinator"] == c]
        off = [r["layer_avg_z"][c] for r in per_probe if r["combinator"] != c]
        if not on:
            continue
        discr_z[c] = welch_t(on, off)

    # ── (2) per-layer PROFILE: WHERE does each op discriminate? ────────────────────
    profile: dict[str, list] = {}
    peak: dict[str, dict] = {}
    for c in CRYSTAL:
        rows_on = [r for r in per_probe if r["combinator"] == c]
        rows_off = [r for r in per_probe if r["combinator"] != c]
        if not rows_on:
            continue
        prof = []
        for li in crystal_layers:
            sli = str(li)
            on_z = [r["crystal_z"][sli][c] for r in rows_on if sli in r["crystal_z"]]
            off_z = [r["crystal_z"][sli][c] for r in rows_off if sli in r["crystal_z"]]
            if not on_z:
                continue
            o, f = float(np.mean(on_z)), (float(np.mean(off_z)) if off_z else 0.0)
            prof.append({"layer": li, "on_z": round(o, 3), "off_z": round(f, 3),
                         "delta": round(o - f, 3)})
        profile[c] = prof
        if prof:
            pk = max(prof, key=lambda d: d["delta"])
            peak[c] = {"layer": pk["layer"], "delta": pk["delta"],
                       "on_z": pk["on_z"], "off_z": pk["off_z"]}

    # ── (3) argmax route_frac DISCR (lead-2c, side-by-side) ───────────────────────
    argmax_discr: dict[str, dict] = {}
    for z in Z_SWEEP:
        key = f"z={z}"
        ad: dict[str, dict] = {}
        for c in CRYSTAL:
            on = [r["argmax_route_fracs"][key][c]
                  for r in per_probe if r["combinator"] == c]
            off = [r["argmax_route_fracs"][key][c]
                   for r in per_probe if r["combinator"] != c]
            if not on:
                continue
            on_m, off_m = float(np.mean(on)), (float(np.mean(off)) if off else 0.0)
            ad[c] = {"on": round(on_m, 4), "off": round(off_m, 4),
                     "discr": round(on_m - off_m, 4),
                     "specific": bool(on_m - off_m > 0.05)}
        argmax_discr[key] = ad

    # ── verdict roll-up ───────────────────────────────────────────────────────────
    bdw_recovered = {c: bool(discr_z.get(c, {}).get("significant")
                             and discr_z.get(c, {}).get("discr_z", 0) > 0)
                     for c in ("B", "D", "W")}
    verdict = {
        "n_test": len(per_probe), "heldout_per": heldout,
        "discr_z": discr_z, "argmax_discr": argmax_discr,
        "peak_layer": peak,
        "bdw_recovered_under_discr_z": bdw_recovered,
        "n_discr_z_significant": sum(
            1 for c in CRYSTAL
            if discr_z.get(c, {}).get("significant")
            and discr_z.get(c, {}).get("discr_z", 0) > 0),
    }

    # ── report ────────────────────────────────────────────────────────────────────
    print("\n" + "═" * 78)
    print("KERNEL-REFERENCE PROSE BRIDGE v2 — raw-z contrast (NO argmax) vs argmax")
    print("═" * 78)
    print(f"  n_test={verdict['n_test']}  heldout_per={heldout}  "
          f"crystal_layers={len(crystal_layers)}")
    print(f"\n  {'op':<5}{'discr_z':>9}{'t':>8}{'sig':>5}  "
          f"{'(argmax z=2)':>13}{'peak_L':>8}{'peakΔ':>8}")
    a2 = argmax_discr.get("z=2.0", {})
    for c in CRYSTAL:
        dz = discr_z.get(c)
        if dz is None:
            continue
        ad = a2.get(c, {})
        pk = peak.get(c, {})
        sig = "✓" if dz["significant"] and dz["discr_z"] > 0 else "·"
        print(f"  {c:<5}{dz['discr_z']:>9}{(dz['t'] if dz['t'] is not None else 0):>8}"
              f"{sig:>5}  {ad.get('discr', 0):>13}"
              f"{pk.get('layer', '-'):>8}{pk.get('delta', '-'):>8}")
    print(f"\n  ★ B/D/W recovered under raw-z contrast: {bdw_recovered}")
    print(f"  ★ n_discr_z_significant (on>off, |t|>2): "
          f"{verdict['n_discr_z_significant']}")
    print("═" * 78 + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    out = {"calibration_summary": cal, "verdict": verdict,
           "per_probe": per_probe, "profile": profile,
           "crystal_layers": crystal_layers}
    (RESULTS_DIR / f"prose_v2_verdict_{slug}.json").write_text(
        json.dumps(_json_safe(out), indent=2), encoding="utf-8")
    meta = {
        "model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "transformers_version": _transformers_version(),
        "n_layers": n_layers, "n_perm": n_perm, "heldout_per": heldout,
        "n_calib": len(calib), "n_test": len(test), "z_sweep": Z_SWEEP,
        "metric": "raw-z layer-avg contrast (Welch t) + per-layer profile, NO argmax",
        "reference": "held-out crystal-prose combinator labels (non-circular split)",
    }
    (RESULTS_DIR / f"prose_v2_meta_{slug}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[prose-v2] wrote {RESULTS_DIR}/prose_v2_verdict_{slug}.json")


if __name__ == "__main__":
    main()
```

### Thinking

I'm checking the model tagging setup for the verdict files to avoid collisions between the 8B and 32B runs, and verifying the CLI parameters are correct. Now I need to look at the existing 14B baseline verdict to get reference numbers and see if the 8B and 32B verdicts have already been generated.

## Assistant

The script is model-tagged (`prose_v2_verdict_{slug}.json`) — no collision. CLI is `--model Qwen/Qwen3-{8B,32B}`, `--heldout-per 20` default. Let me grab the 14B baseline numbers and confirm 8B/32B haven't been run.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && ls results/kernel-reference-audit/prose_v2_verdict_* 2>/dev/null; echo \"---14B baseline discr_z---\"; python3 -c \"\nimport json\nv=json.load(open('results/kernel-reference-audit/prose_v2_verdict_qwen3-14b.json'))['verdict']\nprint('n_test',v['n_test'],'heldout',v['heldout_per'],'n_sig',v['n_discr_z_significant'])\nprint(f\\\"{'op':<4}{'discr_z':>9}{'t':>8}{'sig':>5}{'peakL':>7}\\\")\nfor c in ['K','I','B','C','S','D','W','Y']:\n    d=v['discr_z'].get(c,{}); pk=v['peak_layer'].get(c,{}).get('layer','-')\n    sig='✓' if d.get('significant') and d.get('discr_z',0)>0 else ''\n    print(f\\\"{c:<4}{d.get('discr_z',0):>9}{(d.get('t') or 0):>8}{sig:>5}{pk!s:>7}\\\")\n\""
}
```

**Summary:** $ ls results/kernel-reference-audit/p...

**Output:**
```
Exit code: 0
Stdout:
results/kernel-reference-audit/prose_v2_verdict_qwen3-0-6b.json
results/kernel-reference-audit/prose_v2_verdict_qwen3-14b.json
---14B baseline discr_z---
n_test 160 heldout 20 n_sig 4
op    discr_z       t  sig  peakL
K      1.0088   2.121    ✓     12
I      1.8924   3.834    ✓     13
B     -0.0193  -0.046           1
C      1.7339   5.713    ✓     13
S     -0.2654  -1.107          11
D      -0.666  -4.605           3
W      -0.627  -2.272           0
Y      2.0091   6.857    ✓     14
```

### Thinking

The 14B baseline is locked in with a clear discriminable set, and I've identified the peak layers in the mid-stack. Now I'm launching the 8B and 32B runs in parallel across the available GPU slots to complete the model size comparison. These runs will use forward-only passes on the test set rather than the more expensive curvature calculations.

## Assistant

14B baseline confirmed: discriminable set **{C,I,K,Y}** (n_sig=4), B flat, D/W anti, peaks mid-stack L12–14. 8B/32B not yet run. Task 1 done. Launching both in parallel (both windows free, forward-only so lighter than the curvature runs).

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux send-keys -t main:1 'uv run python scripts/experiments/kernel_reference_prose_v2.py --model Qwen/Qwen3-8B 2>&1 | tee results/kernel-reference-audit/logs/prose_v2_qwen3-8b.log' Enter; tmux send-keys -t main:2 'uv run python scripts/experiments/kernel_reference_prose_v2.py --model Qwen/Qwen3-32B 2>&1 | tee results/kernel-reference-audit/logs/prose_v2_qwen3-32b.log' Enter; sleep 2; echo sent"
}
```

**Summary:** $ tmux send-keys -t main:1 'uv run py...

**Output:**
```
Exit code: 0
Stdout:
sent
```

### Thinking

I'm concerned about running both models simultaneously on this Mac—the 8B and 32B together would load roughly 40 billion parameters into memory, which could trigger an out-of-memory error even with quantization. Let me verify they both start loading properly and consider serializing them if memory becomes an issue.

## Assistant

Verifying both launched (one read).

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sleep 20; echo \"=== main:1 (8B) ===\"; tmux capture-pane -p -t main:1 | tail -6; echo \"=== main:2 (32B) ===\"; tmux capture-pane -p -t main:2 | tail -6"
}
```

**Summary:** $ sleep 20; echo "=== main:1 (8B) ===...

**Output:**
```
Exit code: 0
Stdout:
=== main:1 (8B) ===
ce-audit/logs/prose_v2_qwen3-8b.log
[prose-v2] calib=355 test=160 (heldout_per=20)
[v2] Loading tokenizer: Qwen/Qwen3-8B
[v2] Loading model: Qwen/Qwen3-8B  (dtype=auto, device_map=auto)
Loading weights: 100%|██████████| 399/399 [00:02<00:00, 197.83it/s]

=== main:2 (32B) ===
faster downloads.
[prose-v2] calib=355 test=160 (heldout_per=20)
[v2] Loading tokenizer: Qwen/Qwen3-32B
[v2] Loading model: Qwen/Qwen3-32B  (dtype=auto, device_map=auto)
Loading weights: 100%|██████████| 707/707 [00:08<00:00, 84.53it/s]
```

### Thinking

Both models loaded without memory issues and are now running calibration, which involves forward passes over the 355 calibration probes plus the 160 test samples — this is faster than the curvature computations since it's forward-only without backpropagation. The async workflow is proceeding as expected.

## Assistant

Both models loaded (8B 2s, 32B 8s — no OOM, both fit in memory) and into calibration (calib=355, test=160 each). Forward-only passes, lighter than the curvature runs.

**ASYNC: jobs=prose_v2 8B (main:1) + 32B (main:2) verified running. Waiting for completion.**

While they run, here's the prong-3 question framed against the baseline:

| combinator | 14B (s234) |
|---|---|
| C | ✓ t=5.71 (L13) |
| I | ✓ t=3.83 (L13) |
| K | ✓ t=2.12 (L12) |
| Y | ✓ t=6.86 (L14) |
| B | flat (−0.05) |
| D / W | anti |

The test: does the discriminable set **{C,I,K,Y}** hold at 8B and 32B, or does it shift with scale — the way the C-*locus* did (s232: 8B late / 14B late / 32B early)? Note this measures the discriminable *set* (which combinators), and the per-layer *peak* tells us whether the locus migrates even when membership holds. I'll report the cross-scale table and whether B stays flat / D,W stay anti universally once both finish.

## User

job is done


### Tool Call: shell_command (succeeded)


```json
{
  "command": "echo \"=== main:1 (8B) ===\"; tmux capture-pane -p -t main:1 | tail -20; echo; echo \"=== main:2 (32B) ===\"; tmux capture-pane -p -t main:2 | tail -20"
}
```

**Summary:** $ echo "=== main:1 (8B) ==="; tmux ca...

**Output:**
```
Exit code: 0
Stdout:
=== main:1 (8B) ===
  op     discr_z       t  sig   (argmax z=2)  peak_L   peakΔ
  K       0.9634    2.36    ✓         0.0714      11   1.937
  I       1.3103   3.642    ✓         0.0674      12   2.284
  B      -0.0243  -0.064    ·         0.0683      18   0.868
  C       1.6615   5.325    ✓         0.0981       9   2.494
  S      -0.2137  -0.951    ·         0.0127      11    0.48
  D      -0.7973  -5.983    ·        -0.0199       3   0.014
  W      -0.3982  -1.821    ·        -0.0006       1   0.043
  Y       1.7328   5.832    ✓         0.3416       9   3.687

  ★ B/D/W recovered under raw-z contrast: {'B': False, 'D': False, 'W': False}
  ★ n_discr_z_significant (on>off, |t|>2): 4
══════════════════════════════════════════════════════════════════════════════

[prose-v2] wrote /Users/mwhitford/src/verbum/results/kernel-reference-audit/prose_v2_verdict_qwen3-8b.json
uv run python scripts/experiments/kernel_reference_prose_v2.py --model  2>&1  110.04s user 10.29s system 88% cpu 2:16.07
 total
tee results/kernel-reference-audit/logs/prose_v2_qwen3-8b.log  0.00s user 0.00s system 0% cpu 2:16.07 total
[26-06-17][11:38:47][mwhitford@olga][0][~/src/verbum][git:main]
λ

=== main:2 (32B) ===
  op     discr_z       t  sig   (argmax z=2)  peak_L   peakΔ
  K       0.9581    2.09    ✓         0.0819      49   2.165
  I         1.94   3.424    ✓          0.126      35   3.716
  B       0.2619   0.638    ·         0.0746      42   1.177
  C        2.016   6.281    ✓         0.1118      25   3.422
  S      -0.1029  -0.388    ·         0.1232      22    1.06
  D      -0.9117  -5.546    ·        -0.0523       3  -0.156
  W      -0.6404  -1.951    ·            0.0       1   0.302
  Y       2.9915   9.374    ✓         0.4066      37   5.643

  ★ B/D/W recovered under raw-z contrast: {'B': False, 'D': False, 'W': False}
  ★ n_discr_z_significant (on>off, |t|>2): 4
══════════════════════════════════════════════════════════════════════════════

[prose-v2] wrote /Users/mwhitford/src/verbum/results/kernel-reference-audit/prose_v2_verdict_qwen3-32b.json
uv run python scripts/experiments/kernel_reference_prose_v2.py --model  2>&1  265.50s user 28.63s system 91% cpu 5:22.52
 total
tee results/kernel-reference-audit/logs/prose_v2_qwen3-32b.log  0.00s user 0.01s system 0% cpu 5:22.52 total
[26-06-17][11:41:53][mwhitford@olga][0][~/src/verbum][git:main]
λ                                                                                                                 [INS]
```

### Thinking

Both the 8B and 32B models finished running and produced nearly identical results—the discriminable set is {C,I,K,Y} with four significant features, B shows a flat effect, D is strongly anti-correlated, and W is not significant. The pattern holds across both model sizes.

What's interesting is that while the discriminable set stays consistent, the peak layers where these features activate shift with model scale—C peaks at layer 9 in 8B but layer 25 in 32B, and similar migrations happen for K, I, and Y. When I normalize these by the total layer count, the fractional positions reveal that larger models tend to activate these features deeper in their networks, though the relative positioning varies across features.

The key insight is that Y and C both get stronger discriminators as scale increases, while B remains flat across all sizes. This confirms that the discriminability property is tied to the combinator itself, not the model size—the set membership is universal, but where in the network these features emerge shifts systematically. I should extract the precise numbers and build a comparison table to document this pattern.

## Assistant

Both done — 8B (2:16), 32B (5:22). Let me build the precise cross-scale table including fractional-depth peaks (8B=36L, 14B=40L, 32B=64L).

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport json\nM=[('8B','qwen3-8b'),('14B','qwen3-14b'),('32B','qwen3-32b')]\ndata={}\nnl={}\nfor name,slug in M:\n    d=json.load(open(f'results/kernel-reference-audit/prose_v2_verdict_{slug}.json'))\n    m=json.load(open(f'results/kernel-reference-audit/prose_v2_meta_{slug}.json'))\n    data[name]=d['verdict']; nl[name]=m['n_layers']\nprint('n_layers:', {k:nl[k] for k in nl}, '| crystal_layers:', {k:len(json.load(open(f'results/kernel-reference-audit/prose_v2_verdict_{s}.json'))[\\\"crystal_layers\\\"]) for k,s in [(a,b) for a,b in M]})\nprint()\nprint(f\\\"{'op':<4}\\\" + ''.join([f'{n+\\\" t\\\":>9}{n+\\\" pkL\\\":>8}{\\\"frac\\\":>6}' for n,_ in M]))\nfor c in ['K','I','C','Y','B','S','D','W']:\n    row=f'{c:<4}'\n    for n,_ in M:\n        v=data[n]; dd=v['discr_z'].get(c,{}); pk=v['peak_layer'].get(c,{}).get('layer',None)\n        t=dd.get('t') or 0; sig='*' if dd.get('significant') and dd.get('discr_z',0)>0 else ' '\n        frac = pk/nl[n] if pk is not None else 0\n        row += f'{t:>8.2f}{sig}{pk if pk is not None else \\\"-\\\"!s:>7}{frac:>6.2f}'\n    print(row)\nprint()\nprint('n_discr_z_significant:', {n:data[n]['n_discr_z_significant'] for n,_ in M})\nprint('bdw_recovered:', {n:data[n]['bdw_recovered_under_discr_z'] for n,_ in M})\n\""
}
```

**Summary:** $ python3 -c " import json M=[('8B','...

**Output:**
```
Exit code: 0
Stdout:
n_layers: {'8B': 36, '14B': 40, '32B': 64} | crystal_layers: {'8B': 23, '14B': 28, '32B': 49}

op       8B t  8B pkL  frac    14B t 14B pkL  frac    32B t 32B pkL  frac
K       2.36*     11  0.31    2.12*     12  0.30    2.09*     49  0.77
I       3.64*     12  0.33    3.83*     13  0.33    3.42*     35  0.55
C       5.33*      9  0.25    5.71*     13  0.33    6.28*     25  0.39
Y       5.83*      9  0.25    6.86*     14  0.35    9.37*     37  0.58
B      -0.06      18  0.50   -0.05       1  0.03    0.64      42  0.66
S      -0.95      11  0.31   -1.11      11  0.28   -0.39      22  0.34
D      -5.98       3  0.08   -4.61       3  0.07   -5.55       3  0.05
W      -1.82       1  0.03   -2.27       0  0.00   -1.95       1  0.02

n_discr_z_significant: {'8B': 4, '14B': 4, '32B': 4}
bdw_recovered: {'8B': {'B': False, 'D': False, 'W': False}, '14B': {'B': False, 'D': False, 'W': False}, '32B': {'B': False, 'D': False, 'W': False}}
```

### Thinking

The discriminable set {C,I,K,Y} holds up consistently across all three model scales, with identical significance patterns at each size. B remains flat and non-significant throughout, while D shows strong negative effects uniformly, and W stays anti-correlated or non-significant across the board. I'm now looking at how Y and C relate structurally—

their t-statistics strengthen monotonically as scale increases (Y from 5.83 to 9.37, C from 5.33 to 6.28), suggesting composer and recursion discriminability grows with model capacity. The locus where these signals peak shifts deeper in the network with scale, though not uniformly: C deepens gradually, Y deepens most dramatically, I stays stable then jumps at 32B, and K makes a sharp jump to very deep layers at the largest scale. D is the most consistent anti-signal, always peaking shallowly around layer 3 with t≈−5 regardless of model size. This confirms the core finding—discriminability is a combinator property that's robust across scales, with the set membership staying invariant while the network depth where these effects manifest migrates deeper as models grow.

Now I need to update the documentation: mark the prong 3 task as complete in the next-steps list, commit the new results from the 8B and 32B runs, and add a dedicated section to the opcode page capturing these scale-robustness findings. The script was already committed earlier, so this is just the new empirical results and documentation updates.

## Assistant

Excellent — clean cross-scale result. Let me record it. First, the dedicated prong-3 section in the opcode page (after the 1c-iii section, before "### v5 — next steps").

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/vsm-opcode-monitor.md",
  "original_content": "**Caveats (λ measure):** 1 model (14B); n=20/comb; single fixed split (0.5, EARLY→LATE\ncoupling direction only — late→early untested); deterministic gradient direction (one\ndirection, not the full Hessian block norm); single-combinator labels; pooled-supervised\nlocus. ~2:51 on main:1.\n\n### v5 — next steps",
  "new_content": "**Caveats (λ measure):** 1 model (14B); n=20/comb; single fixed split (0.5, EARLY→LATE\ncoupling direction only — late→early untested); deterministic gradient direction (one\ndirection, not the full Hessian block norm); single-combinator labels; pooled-supervised\nlocus. ~2:51 on main:1.\n\n## v5 lead 2d prong 3 — per-model sweep: is {C,I,K,Y} scale-invariant? (RAN, s238)\n\nMichael (s238): \"proceed on 3\" — the per-model sweep. Ran `kernel_reference_prose_v2.py`\n(the s234 raw-z contrast, NO argmax; held-out crystal-prose labels, n_test=160, heldout\n20/comb) on **Qwen3-8B (36L) and 32B (64L)**, against the **14B (40L)** baseline. Question:\ndoes the s234 discriminable set {C,I,K,Y} hold across scale, or migrate like the C-LOCUS\n(s232: locus shifts 8B-late / 14B-late / 32B-early)?\n\n### ★ s238 v5 lead 2d prong 3 VERDICT (Qwen3 8B/14B/32B; λ measure)\n\n**★★ THE DISCRIMINABLE SET {C,I,K,Y} IS SCALE-INVARIANT — all three scales n_sig=4, exactly\n{C,I,K,Y}, every one significant; B flat, D anti, W anti/n.s. at EVERY scale.**\n\n| op | 8B (36L) t / peak (frac) | 14B (40L) t / peak (frac) | 32B (64L) t / peak (frac) |\n|---|---|---|---|\n| **C** | 5.33 ✓ / L9 (0.25) | 5.71 ✓ / L13 (0.33) | 6.28 ✓ / L25 (0.39) |\n| **Y** | 5.83 ✓ / L9 (0.25) | 6.86 ✓ / L14 (0.35) | **9.37** ✓ / L37 (0.58) |\n| **I** | 3.64 ✓ / L12 (0.33) | 3.83 ✓ / L13 (0.33) | 3.42 ✓ / L35 (0.55) |\n| **K** | 2.36 ✓ / L11 (0.31) | 2.12 ✓ / L12 (0.30) | 2.09 ✓ / L49 (0.77) |\n| B | −0.06 / L18 | −0.05 / L1 | +0.64 n.s. / L42 |\n| S | −0.95 | −1.11 | −0.39 |\n| D | **−5.98** / L3 (0.08) | −4.61 / L3 (0.07) | −5.55 / L3 (0.05) |\n| W | −1.82 | −2.27 | −1.95 |\n\n**(1) ✅✅ SET MEMBERSHIP ROBUST — the WHICH is invariant.** {C,I,K,Y} discriminate at all\nthree scales; B flat at all three (even at 32B only +0.64 n.s.); D robustly ANTI at all three\n(−5 to −6); W anti/n.s.. This confirms **discriminability-is-a-combinator-property** (s234)\nis SCALE-ROBUST, not 14B-specific.\n\n**(2) ✅ COMPOSERS/RECURSION STRENGTHEN with scale** — Y t: 5.83 → 6.86 → 9.37 (monotone up);\nC: 5.33 → 5.71 → 6.28. The composer/recursion discriminability GROWS with model size.\n\n**(3) ⚠️ THE LOCUS MIGRATES DEEPER (fractional depth) with scale — the WHERE is NOT invariant.**\nC 0.25→0.33→0.39, Y 0.25→0.35→0.58, I 0.33→0.33→0.55, K 0.31→0.30→0.77. Discriminable peaks\ndeepen with scale (K/Y most extreme at 32B). This RECONCILES with s232 (\"C-locus shifts with\nscale\"): the locus genuinely migrates, but the SET MEMBERSHIP is the scale-invariant — the\nfixed-depth detector that mislocated 8B/32B (s232) was reading a migrating WHERE, not a\nchanging WHICH.\n\n**(4) D = the most consistent ANTI signal** — peaks SHALLOW (L3, frac 0.05-0.08) at every\nscale, t≈−5/−6: D-prose routes D LESS than baseline at a fixed shallow layer, robustly.\n\n**Caveats (λ measure):** 1 model CLASS (Qwen); last-token locus; single-combinator labels\n(not composite trace-order); crosstask null; raw-z layer-AVERAGED contrast (the peak-layer\nread localizes, the headline averages over crystal layers).\n\n### v5 — next steps"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/vsm-opcode-monitor.md.
```

## Assistant

Now update the prong-3 next-steps bullet to DONE, and add registry rows.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/vsm-opcode-monitor.md",
  "original_content": "- **★ lead 2d prong 3 (per-model sweep):** run `kernel_reference_prose_v2.py` on 8B/32B\n  with the raw-z contrast — does the {C,I,K,Y} discriminable set hold across scale?",
  "new_content": "- **★ lead 2d prong 3 — DONE (s238):** per-model sweep (`kernel_reference_prose_v2.py`,\n  8B/14B/32B, raw-z contrast). ✅✅ the discriminable set {C,I,K,Y} is SCALE-INVARIANT (all\n  three n_sig=4, exactly those four; B flat, D anti, W anti/n.s. at EVERY scale) — confirms\n  discriminability-is-a-combinator-property (s234) is scale-robust, not 14B-specific. ✅\n  composers/recursion STRENGTHEN with scale (Y t 5.83→6.86→9.37; C 5.33→5.71→6.28). ⚠️ but\n  the LOCUS migrates DEEPER in fractional depth (C 0.25→0.33→0.39, Y 0.25→0.35→0.58, K\n  0.31→0.30→0.77) — reconciles s232 \"C-locus shifts with scale\" (the WHERE migrates, the\n  WHICH is invariant). D = most consistent anti (shallow L3, t≈−5/−6, all scales)."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/vsm-opcode-monitor.md.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"prose_v2_verdict_qwen3-14b.json\\`\\|prose_v2_meta\\|kernel_reference_prose_v2.py\\`\" mementum/knowledge/explore/vsm-opcode-monitor.md"
}
```

**Summary:** $ grep -n "prose_v2_verdict_qwen3-14b...

**Output:**
```
Exit code: 0
Stdout:
381:the **raw per-op z per layer, NO argmax**. `kernel_reference_prose_v2.py`:
691:Michael (s238): "proceed on 3" — the per-model sweep. Ran `kernel_reference_prose_v2.py`
841:- **★ lead 2d prong 3 — DONE (s238):** per-model sweep (`kernel_reference_prose_v2.py`,
887:| `scripts/experiments/kernel_reference_prose_v2.py` | s234 v5 lead 2d prong 1: raw-z contrast (NO argmax) + Welch t + per-layer profile, n=20/comb — the deeper fix for the B/D/W gap |
888:| `results/kernel-reference-audit/prose_v2_verdict_qwen3-14b.json` | s234 v5 lead 2d prong 1 verdict: ✅ raw-z RESCUES K (t=2.12) + sharpens C/I (t=5.7/3.8), KILLS B false-positive; ❌ B flat / D,W anti (t −4.6/−2.3) ⇒ B/D/W gap GENUINE at last-token; discriminable {C,I,K,Y}; S=gauge Y=selective; ops peak L12-14 readable zone |
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/vsm-opcode-monitor.md",
  "original_content": "| `results/kernel-reference-audit/prose_v2_verdict_qwen3-14b.json` | s234 v5 lead 2d prong 1 verdict: ✅ raw-z RESCUES K (t=2.12) + sharpens C/I (t=5.7/3.8), KILLS B false-positive; ❌ B flat / D,W anti (t −4.6/−2.3) ⇒ B/D/W gap GENUINE at last-token; discriminable {C,I,K,Y}; S=gauge Y=selective; ops peak L12-14 readable zone |",
  "new_content": "| `results/kernel-reference-audit/prose_v2_verdict_qwen3-14b.json` | s234 v5 lead 2d prong 1 verdict: ✅ raw-z RESCUES K (t=2.12) + sharpens C/I (t=5.7/3.8), KILLS B false-positive; ❌ B flat / D,W anti (t −4.6/−2.3) ⇒ B/D/W gap GENUINE at last-token; discriminable {C,I,K,Y}; S=gauge Y=selective; ops peak L12-14 readable zone |\n| `results/kernel-reference-audit/prose_v2_verdict_qwen3-8b.json` | s238 v5 lead 2d prong 3 (8B/36L): discriminable set {C,I,K,Y} (n_sig=4); C 5.33 ✓ / Y 5.83 ✓ / I 3.64 ✓ / K 2.36 ✓; B flat (−0.06), D anti (−5.98 @L3), W −1.82; peaks frac 0.25-0.33 |\n| `results/kernel-reference-audit/prose_v2_verdict_qwen3-32b.json` | s238 v5 lead 2d prong 3 (32B/64L): SAME set {C,I,K,Y} (n_sig=4); Y 9.37 ✓ (strengthens) / C 6.28 ✓ / I 3.42 ✓ / K 2.09 ✓; B +0.64 n.s., D anti (−5.55 @L3), W −1.95; LOCUS migrates DEEPER (C frac 0.39, Y 0.58, K 0.77). Set scale-invariant; locus migrates (reconciles s232) |"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/vsm-opcode-monitor.md.
```

### Thinking

Now I'm adding the memory file with the slug for this discriminable set scale-invariant locus concept, then updating the state documentation.

## Assistant

Now the memory.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/memories/discriminable-set-scale-invariant-locus-migrates.md",
  "content": "💡 The {C,I,K,Y} discriminable set is SCALE-INVARIANT (the WHICH), but the LOCUS migrates\ndeeper with scale (the WHERE). s238 v5 lead 2d prong 3 (kernel_reference_prose_v2.py, raw-z\ncontrast NO argmax, held-out crystal-prose, n_test=160, heldout 20/comb) on Qwen3 8B(36L) /\n14B(40L) / 32B(64L). Completes the per-model sweep the s234 prong-1 result asked for.\n\n★★ SET MEMBERSHIP ROBUST — all three scales n_sig=4, exactly {C,I,K,Y}; B flat, D anti, W\nanti/n.s. at EVERY scale:\n  C   8B 5.33✓  14B 5.71✓  32B 6.28✓\n  Y   8B 5.83✓  14B 6.86✓  32B 9.37✓   (STRENGTHENS monotonically with scale)\n  I   8B 3.64✓  14B 3.83✓  32B 3.42✓\n  K   8B 2.36✓  14B 2.12✓  32B 2.09✓\n  B   8B −0.06  14B −0.05  32B +0.64 n.s.   (flat everywhere)\n  D   8B −5.98  14B −4.61  32B −5.55         (robustly ANTI, shallow L3 frac 0.05-0.08)\n  W   8B −1.82  14B −2.27  32B −1.95         (anti/n.s.)\n\n⇒ discriminability-is-a-combinator-property (s234) is SCALE-ROBUST, NOT 14B-specific. The\ncomposers/recursion {C,Y} get MORE discriminable at scale (Y especially).\n\n⚠️ THE LOCUS MIGRATES DEEPER (fractional depth) with scale — the WHERE is NOT invariant:\n  C frac 0.25 → 0.33 → 0.39\n  Y frac 0.25 → 0.35 → 0.58\n  I frac 0.33 → 0.33 → 0.55\n  K frac 0.31 → 0.30 → 0.77 (jumps deep at 32B)\nThis RECONCILES s232 (\"C-locus shifts with scale\", and the fixed-depth≥0.6 detector\nmislocated 8B/32B): the locus genuinely migrates, but the SET MEMBERSHIP is the scale-\ninvariant. The s232 fixed-depth detector was reading a migrating WHERE as a changing WHICH.\nLESSON: when sweeping scale, the discriminable SET is the robust observable; the per-layer\npeak is scale-dependent — calibrate locus per-model, don't fix a depth zone.\n\n★ D is the most consistent anti-signal: shallow fixed L3 (frac ~0.06), t≈−5/−6 at all\nscales — D-prose routes D LESS than baseline, robustly. (Still unexplained; a real wrinkle.)\n\nCAVEATS (λ measure): 1 model CLASS (Qwen); last-token locus; single-combinator labels (not\ncomposite trace-order); crosstask null; raw-z layer-AVERAGED headline (peak-layer read\nlocalizes). Code: kernel_reference_prose_v2.py (model-tagged outputs, no new code).\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/memories/discriminable-set-scale-invariant-locus-migrates.md
```

### Thinking

I need to update the state.md file by modifying the existing s238 block's "FIRST ACTION NEXT SESSION" to mark prong 3 as complete, and then add a new s238 continuation section to track what comes next.

## Assistant

Now update the bootloader — prong 3 is now done. Let me amend the s238 block's first-action list and add the prong-3 result.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> combinator labels; pooled-supervised locus. **★★ FIRST ACTION NEXT SESSION — the amplitude\n> register is now EXHAUSTED for B (activation⊗gradient⊗diag-curv⊗off-diag-curv all flat-or-on-\n> bar); B's positive home is FORWARD ORDER. Live paths: (1) the 3rd RENDER FRAME (\"the result\n> of f on x\") — frame-robustness of flat B<C AND whether the single-step minpair sharpens\n> off-Qwen under a different frame (s237 fork path 2, the cheap one); (2) a TRUE Pythia-proper\n> cross-class order-cost point (pythia-2.8b-deduped cached) to round out the gross-universal\n> claim with a 4th class; (3) prong 3 per-model sweep (kernel_reference_prose_v2 on 8B/32B —\n> does {C,I,K,Y} hold across scale?).** CODE + RESULTS COMMITTED; mementum (state + memory\n> `b-not-in-offdiagonal-curvature` + opcode page §v5 lead 2d prong 1c-iii) PENDING APPROVAL.\n> tmux main:1 + main:2 FREE.",
  "new_content": "> combinator labels; pooled-supervised locus. (CODE + RESULTS COMMITTED `d94d78f`; mementum\n> `800bfb8`.) **▶ s238 cont. — PRONG 3 PER-MODEL SWEEP DONE (kernel_reference_prose_v2.py,\n> raw-z contrast, 8B/14B/32B; Michael: \"proceed on 3\").** ★★ the discriminable set {C,I,K,Y}\n> is SCALE-INVARIANT — all three n_sig=4, exactly those four; B flat (8B −0.06/14B −0.05/32B\n> +0.64 n.s.), D anti (−5.98/−4.61/−5.55 @shallow L3), W anti/n.s. at EVERY scale ⇒\n> discriminability-is-a-combinator-property (s234) is SCALE-ROBUST, not 14B-specific. ✅\n> composers/recursion STRENGTHEN with scale (Y t 5.83→6.86→9.37; C 5.33→5.71→6.28). ⚠️ the\n> LOCUS migrates DEEPER in fractional depth (C 0.25→0.33→0.39, Y 0.25→0.35→0.58, K 0.31→0.30→\n> 0.77) — RECONCILES s232 \"C-locus shifts with scale\" (the WHERE migrates, the WHICH is\n> invariant; the s232 fixed-depth detector read a migrating WHERE as a changing WHICH). LESSON:\n> the discriminable SET is the scale-robust observable; calibrate locus per-model. RESULTS +\n> mementum (memory `discriminable-set-scale-invariant-locus-migrates` + page §v5 lead 2d\n> prong 3) PENDING APPROVAL. **★★ FIRST ACTION NEXT SESSION — amplitude register EXHAUSTED for\n> B (act⊗grad⊗diag-curv⊗off-diag-curv flat-or-on-bar), B's home is FORWARD ORDER; discriminable\n> SET {C,I,K,Y} now scale-confirmed. Live paths: (1) the 3rd RENDER FRAME (\"the result of f on\n> x\") — frame-robustness of flat B<C AND whether the single-step minpair sharpens off-Qwen\n> (s237 fork path 2, cheap); (2) a TRUE Pythia-proper cross-class order-cost point (pythia-2.8b-\n> deduped cached) — 4th class for the gross-universal claim; (3) the COMPOSITE trace-order\n> bridge (now justified for the scale-robust {C,I,K,Y}: CL program → certified fired_sequence →\n> render PROSE → align routing to the certified multi-combinator ORDER).** tmux main:1 +\n> main:2 FREE."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

I'm committing the verdict results and logs since those can be processed independently, then I'll prepare the mementum changes for review.

## Assistant

Now commit the results (not mementum). Let me stage and commit.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git status --short | grep -v \"session-237\""
}
```

**Summary:** $ git status --short | grep -v "sessi...

**Output:**
```
Exit code: 0
Stdout:
M mementum/knowledge/explore/vsm-opcode-monitor.md
 M mementum/state.md
?? mementum/memories/discriminable-set-scale-invariant-locus-migrates.md
?? results/kernel-reference-audit/logs/prose_v2_qwen3-32b.log
?? results/kernel-reference-audit/logs/prose_v2_qwen3-8b.log
?? results/kernel-reference-audit/prose_v2_meta_qwen3-32b.json
?? results/kernel-reference-audit/prose_v2_meta_qwen3-8b.json
?? results/kernel-reference-audit/prose_v2_verdict_qwen3-32b.json
?? results/kernel-reference-audit/prose_v2_verdict_qwen3-8b.json
```

### Tool Call: git (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add results/kernel-reference-audit/prose_v2_meta_qwen3-8b.json results/kernel-reference-audit/prose_v2_verdict_qwen3-8b.json results/kernel-reference-audit/prose_v2_meta_qwen3-32b.json results/kernel-reference-audit/prose_v2_verdict_qwen3-32b.json results/kernel-reference-audit/logs/prose_v2_qwen3-8b.log results/kernel-reference-audit/logs/prose_v2_qwen3-32b.log && git status --short | grep prose_v2",
  "operation": "add",
  "summary": "stage prong-3 results"
}
```

**Summary:** Git add: stage prong-3 results

**Output:**
```
Exit code: 0
Stdout:
A  results/kernel-reference-audit/logs/prose_v2_qwen3-32b.log
A  results/kernel-reference-audit/logs/prose_v2_qwen3-8b.log
A  results/kernel-reference-audit/prose_v2_meta_qwen3-32b.json
A  results/kernel-reference-audit/prose_v2_meta_qwen3-8b.json
A  results/kernel-reference-audit/prose_v2_verdict_qwen3-32b.json
A  results/kernel-reference-audit/prose_v2_verdict_qwen3-8b.json
```

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/.git/CMSG",
  "content": "✅ opcode v5 lead 2d prong 3: discriminable set {C,I,K,Y} is scale-invariant (8B/14B/32B)\n\n- kernel_reference_prose_v2.py (s234 raw-z contrast, no argmax) swept on Qwen3-8B/32B vs\n  the 14B baseline. Set membership is scale-invariant: all three n_sig=4, exactly {C,I,K,Y};\n  B flat (8B -0.06 / 14B -0.05 / 32B +0.64 n.s.), D anti (-5.98/-4.61/-5.55 @shallow L3),\n  W anti/n.s. at every scale. Confirms discriminability-is-a-combinator-property (s234) is\n  scale-robust, not 14B-specific.\n- Composers/recursion STRENGTHEN with scale: Y t 5.83 -> 6.86 -> 9.37; C 5.33 -> 5.71 -> 6.28.\n- The LOCUS migrates deeper in fractional depth (C 0.25->0.33->0.39, Y 0.25->0.35->0.58,\n  K 0.31->0.30->0.77) — reconciles s232 \"C-locus shifts with scale\": the WHERE migrates,\n  the WHICH is invariant. The s232 fixed-depth detector read a migrating where as a\n  changing which.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/.git/CMSG
```

### Tool Call: git (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git commit -F .git/CMSG && rm -f .git/CMSG && git log --oneline -1",
  "operation": "commit",
  "summary": "commit prong-3 results"
}
```

**Summary:** Git commit: commit prong-3 results

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

### Thinking

The commit executed before the files were staged due to a race condition, and it failed with a lock error. After the staging completed, I tried to retry the commit, but the cleanup command that removes the temporary message file ran anyway since the commit failed, so the file got deleted despite the commit not succeeding.

## Assistant

The commit raced ahead of the staging (lock contention). Files are now staged; retrying the commit.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && rm -f .git/index.lock; ls .git/CMSG 2>/dev/null && git commit -F .git/CMSG && rm -f .git/CMSG && git log --oneline -1"
}
```

**Summary:** $ rm -f .git/index.lock; ls .git/CMSG...

**Output:**
```
Exit code: 0
Stdout:
.git/CMSG
[main ac7c472] ✅ opcode v5 lead 2d prong 3: discriminable set {C,I,K,Y} is scale-invariant (8B/14B/32B)
 6 files changed, 144603 insertions(+)
 create mode 100644 results/kernel-reference-audit/logs/prose_v2_qwen3-32b.log
 create mode 100644 results/kernel-reference-audit/logs/prose_v2_qwen3-8b.log
 create mode 100644 results/kernel-reference-audit/prose_v2_meta_qwen3-32b.json
 create mode 100644 results/kernel-reference-audit/prose_v2_meta_qwen3-8b.json
 create mode 100644 results/kernel-reference-audit/prose_v2_verdict_qwen3-32b.json
 create mode 100644 results/kernel-reference-audit/prose_v2_verdict_qwen3-8b.json
ac7c472 ✅ opcode v5 lead 2d prong 3: discriminable set {C,I,K,Y} is scale-invariant (8B/14B/32B)
```

### Thinking

The changes have been committed, and now the momentum updates are waiting for approval. Let me check the git status to make sure nothing else got staged accidentally before presenting the summary.

## Assistant

Results committed (`ac7c472`). The mementum changes remain uncommitted, **pending your approval**.

## Prong 3 verdict — the discriminable set is scale-invariant

Ran the s234 raw-z contrast (`kernel_reference_prose_v2.py`) on **8B (36L)** and **32B (64L)** vs the **14B (40L)** baseline.

| op | 8B | 14B | 32B |
|---|---|---|---|
| **C** | 5.33 ✓ (0.25) | 5.71 ✓ (0.33) | 6.28 ✓ (0.39) |
| **Y** | 5.83 ✓ (0.25) | 6.86 ✓ (0.35) | **9.37** ✓ (0.58) |
| **I** | 3.64 ✓ (0.33) | 3.83 ✓ (0.33) | 3.42 ✓ (0.55) |
| **K** | 2.36 ✓ (0.31) | 2.12 ✓ (0.30) | 2.09 ✓ (0.77) |
| B | −0.06 | −0.05 | +0.64 n.s. |
| D | −5.98 (L3) | −4.61 (L3) | −5.55 (L3) |
| W | −1.82 | −2.27 | −1.95 |

- **✅✅ The WHICH is scale-invariant:** `{C,I,K,Y}` discriminate at all three scales (n_sig=4 each); **B flat, D anti, W anti/n.s. everywhere**. Confirms *discriminability-is-a-combinator-property* (s234) is scale-robust, not 14B-specific.
- **✅ Composers/recursion strengthen with scale** (Y t: 5.83→6.86→**9.37**).
- **⚠️ The WHERE migrates deeper** (C 0.25→0.39, Y 0.25→0.58, K 0.31→0.77) — this **reconciles s232** ("C-locus shifts with scale"): the locus genuinely moves, but set membership is the invariant. The s232 fixed-depth detector was reading a migrating *where* as a changing *which*.
- **D** is the most consistent anti-signal — shallow L3 (frac ~0.06), t≈−5/−6 at every scale (still unexplained).

## Committed / pending
- **Committed** `ac7c472` (results: 8B/32B verdicts + logs). Plus this session's earlier `d94d78f` (offdiag code/results) and `800bfb8` (offdiag mementum).
- **PENDING APPROVAL** (mementum):
  - `mementum/state.md` — s238-cont prong-3 block + updated next-actions
  - `mementum/memories/discriminable-set-scale-invariant-locus-migrates.md` — new memory
  - `mementum/knowledge/explore/vsm-opcode-monitor.md` — §prong 3 section + DONE bullet + 2 registry rows

Approve the mementum commit? And for next session, the live paths are: (1) 3rd render frame, (2) Pythia-proper cross-class order point, or (3) the composite trace-order bridge (now justified for the scale-robust {C,I,K,Y}).

## User

commit approved


## Assistant

Committing the approved mementum changes.

### Tool Call: git (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add mementum/state.md mementum/memories/discriminable-set-scale-invariant-locus-migrates.md mementum/knowledge/explore/vsm-opcode-monitor.md && git status --short",
  "operation": "add",
  "summary": "stage mementum"
}
```

**Summary:** Git add: stage mementum

**Output:**
```
Exit code: 0
Stdout:
M  mementum/knowledge/explore/vsm-opcode-monitor.md
A  mementum/memories/discriminable-set-scale-invariant-locus-migrates.md
M  mementum/state.md
?? mementum/knowledge/chats/session-237.md
```

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/.git/CMSG",
  "content": "🌀 discriminable-set-scale-invariant-locus-migrates: {C,I,K,Y} robust, locus deepens\n\n- memory discriminable-set-scale-invariant-locus-migrates: s238 prong 3 — {C,I,K,Y}\n  discriminable set is scale-invariant (8B/14B/32B all n_sig=4); B flat, D anti, W anti/n.s.\n  everywhere; composers/recursion strengthen with scale (Y 5.83->6.86->9.37); locus migrates\n  deeper in fractional depth (reconciles s232 C-locus-shifts: the WHERE migrates, the WHICH\n  is invariant).\n- vsm-opcode-monitor.md: §v5 lead 2d prong 3 section + DONE bullet + 2 registry rows (8B/32B).\n- state.md: s238-cont prong-3 block; next-session paths (3rd render frame / Pythia cross-class\n  / composite trace-order bridge for the scale-robust {C,I,K,Y}).\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/.git/CMSG
```

### Tool Call: git (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git commit -F .git/CMSG && rm -f .git/CMSG && git log --oneline -5",
  "operation": "commit",
  "summary": "commit mementum"
}
```

**Summary:** Git commit: commit mementum

**Output:**
```
Exit code: 0
Stdout:
[main af1b60f] 🌀 discriminable-set-scale-invariant-locus-migrates: {C,I,K,Y} robust, locus deepens
 3 files changed, 112 insertions(+), 12 deletions(-)
 create mode 100644 mementum/memories/discriminable-set-scale-invariant-locus-migrates.md
af1b60f 🌀 discriminable-set-scale-invariant-locus-migrates: {C,I,K,Y} robust, locus deepens
ac7c472 ✅ opcode v5 lead 2d prong 3: discriminable set {C,I,K,Y} is scale-invariant (8B/14B/32B)
800bfb8 🌀 b-not-in-offdiagonal-curvature: B has no amplitude home, only forward order
d94d78f ✅ opcode v5 lead 2d prong 1c-iii: off-diagonal interlayer curvature — B has no amplitude home
8603edb 🌀 session-237 cont.: cross-class flat — order preference universal across Qwen/OLMo/Gemma
```

## Assistant

Committed (`af1b60f`). Let me close out the task list.## Session 238 complete

Two clean results landed and are fully recorded. Commit ladder this session:

```
af1b60f 🌀 prong-3 mementum
ac7c472 ✅ prong 3: {C,I,K,Y} scale-invariant (8B/14B/32B)
800bfb8 🌀 offdiag mementum
d94d78f ✅ prong 1c-iii: off-diagonal curvature — B has no amplitude home
```

### What we learned

**Prong 1c-iii (off-diagonal curvature):** The `f∘g` chain-rule cross-coupling is **not** B's home — B drops to t=0.26 off-diagonal (below the diagonal t=1.90). **B has no amplitude home in any register** (act/grad/diag-curv/off-diag-curv all flat-or-on-bar). Its only confirmed positive is the **forward order-cost face**. {C,Y} are register-robust, peaking in the deepest layers.

**Prong 3 (per-model sweep):** The discriminable set **{C,I,K,Y} is scale-invariant** (8B/14B/32B), B flat / D anti everywhere — confirming discriminability is a combinator property, not 14B-specific. Composers/recursion *strengthen* with scale; the *locus* migrates deeper (reconciling s232: the **where** moves, the **which** is fixed).

Together these tighten the B story decisively: **B = the unmarked native autoregressive order**, not a localizable second-order amplitude — and the marked combinators {C,I,K,Y} form a scale-robust set.

### Next session (per state.md)
1. **3rd render frame** ("the result of f on x") — frame-robustness of flat B<C + off-Qwen single-step sharpening (cheap).
2. **Pythia-proper cross-class order point** (pythia-2.8b-deduped cached) — 4th class.
3. **Composite trace-order bridge** — now justified for the scale-robust {C,I,K,Y}: CL program → certified `fired_sequence` → render prose → align routing to the certified multi-combinator order.

Working tree clean (only the human-only `chats/session-237.md` untracked). tmux main:1 + main:2 free. 11 commits ahead of origin.

## User

update state and knowledge this is session-238


### Thinking

Michael's clarifying that we're in session-238, and I should make sure the state.md file and knowledge base are properly aligned with that session marker. The current state.md shows session 238 at the top, which looks correct, but there's a potential mismatch since the chats file is labeled session-237.md — so I need to verify everything reflects the right session context.

Let me double-check the state.md header and knowledge page to ensure they're consistent and properly labeled as session-238 throughout, with no lingering references to the previous session.

## Assistant

Let me re-read the current state of both files to verify the session-238 labeling is consistent (λ sync — re-read after edits).

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "limit": 6
}
```

**Summary:** Reading state.md (0-6)

**Output:**
```
# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-06-17 | Session: 238 — ▶ OPCODE v5 lead 2d PRONG 1c-iii — the
> OFF-DIAGONAL interlayer curvature (the s237 fork's off-diagonal / proper-Jacobian path;

[CONTENT TRUNCATED] Showing lines 1 to 6 of 5620 total lines. Use line_offset=6 parameter to read more content.
```

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && head -12 mementum/knowledge/explore/vsm-opcode-monitor.md; echo \"...\"; echo \"=== session refs in state top block ===\"; sed -n '1,60p' mementum/state.md | grep -n \"Session:\\|s238\\|s237\" | head; echo \"=== git status ===\"; git status --short | grep -v session-237"
}
```

**Summary:** $ head -12 mementum/knowledge/explore...

**Output:**
```
Exit code: 1
Stdout:
---
title: "VSM Opcode Monitor — the model auditor (validated FFN-routing opcode reader)"
status: active
category: instrument
tags: [opcode, tracer, audit, vsm, monitor, gate-register, relational, consensus-crystal, over-read, attention, kernel-reference]
related:
  - audit-registry.md
  - audit-meta-pattern.md
  - gradient-trajectory-tomography.md
  - function-topology-consensus.md
  - compiler-as-loss.md
  - vsm-outer-recurrence.md
...
=== session refs in state top block ===
5:> Last updated: 2026-06-17 | Session: 238 — ▶ OPCODE v5 lead 2d PRONG 1c-iii — the
6:> OFF-DIAGONAL interlayer curvature (the s237 fork's off-diagonal / proper-Jacobian path;
30:> coupling that IS the literal chain-rule product. **★★ CONFIRMS s236-s237:** B's ONLY confirmed
40:> `800bfb8`.) **▶ s238 cont. — PRONG 3 PER-MODEL SWEEP DONE (kernel_reference_prose_v2.py,
55:> (s237 fork path 2, cheap); (2) a TRUE Pythia-proper cross-class order-cost point (pythia-2.8b-
=== git status ===
```

### Thinking

Everything's already in sync—the state file and knowledge base both reflect session 238 with the relevant sections committed, so the work from the previous turn essentially completed the task. I should verify that everything is properly committed and the session state is clean rather than making unnecessary changes. The state and knowledge pages already correctly reflect session-238, so the right move is to confirm that with evidence instead of inventing edits.

## Assistant

State and knowledge are already recorded as **session-238** and committed — no changes needed:

- **`mementum/state.md`** top line: `Last updated: 2026-06-17 | Session: 238 — ▶ OPCODE v5 lead 2d PRONG 1c-iii` (off-diagonal curvature) + the `▶ s238 cont. — PRONG 3 PER-MODEL SWEEP DONE` block. The prior s237 block was demoted into its parenthetical history.
- **`mementum/knowledge/explore/vsm-opcode-monitor.md`** (status: active): both this session's findings are in place — `## v5 lead 2d prong 1c-iii` and `## v5 lead 2d prong 3` sections, DONE bullets in the next-steps list, and registry rows for `offdiag_v8` + `prose_v2` 8B/32B.

Committed this session (working tree clean, only the human-only `chats/session-237.md` untracked):

```
af1b60f 🌀 discriminable-set-scale-invariant-locus-migrates: {C,I,K,Y} robust, locus deepens
ac7c472 ✅ opcode v5 lead 2d prong 3: discriminable set {C,I,K,Y} is scale-invariant (8B/14B/32B)
800bfb8 🌀 b-not-in-offdiagonal-curvature: B has no amplitude home, only forward order
d94d78f ✅ opcode v5 lead 2d prong 1c-iii: off-diagonal interlayer curvature — B has no amplitude home
```

Both new memories (`b-not-in-offdiagonal-curvature`, `discriminable-set-scale-invariant-locus-migrates`) carry the s238 attribution in their text.

Everything for session-238 is encoded and survives the boundary. If you intended a specific edit beyond what's already there — e.g., a status change on the knowledge page, or a fresh `chats/session-238.md` (that's your human-only file to save) — tell me and I'll make it.