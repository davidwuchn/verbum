# Smoke testing 4B type ablation

## User

orient we found types


### Thinking

I need to check the mementum/state.md file first to understand the context, then look at the related information about the types that were found.

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
> Last updated: 2026-07-30 | Session: 282 | ▶▶ LIVE PICKUP (s282 — 3-HOP RAN): ✅ built
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
>   circuits-in-compute (DEEP, done); C3 topology dominates (

[OUTPUT TRUNCATED] The tool call succeeded and the output was truncated. Full output saved to: /Users/mwhitford/.cache/eca/toolCallOutputs/toolu_01AJXm1tEjhz8wP8FWoRhx8k.txt
Use `eca__grep` or `eca__read_file` with offset/limit to view specific sections. Do not full read the file.
```

### Thinking

The user wants me to focus on the types arc with a cold-start orientation, so I'm checking what's already in State.md's top block about the s282 TYPES material. I should look at the related theory pages—specifically the ones about types as well-formedness of reduction and type as decodable readout—to confirm the P-TYPE-1b pre-registration status, then quickly scan those key knowledge page headers.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "git log --oneline -n 12; echo ---; git status -s | head -20",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ git log --oneline -n 12; echo ---; ...

**Output:**
```
Exit code: 0
Stdout:
02a4804 💡 theory closure: types are the well-formedness of β-reduction + P-TYPE-1b pre-reg (s282)
f685313 🔄 0.6B lattice prototype: refresh with band-axis loadings (instrument-consistent)
238e370 🌀 s282: fold the 3-axis functor-lattice result into knowledge + state
60b691a 💡 1a-follow @32B: the low-rank type lattice is 3 Montague FUNCTOR-KIND axes (e at origin)
6592558 🔄 1a-follow: characterize the ~3 type axes IN the low-rank band (SVD loadings)
729f09c 💡 types synthesis: decodable-readout-not-causal-direction + low-rank Montague lattice (s282)
3385768 💡 P-TYPE-1a @32B: the type lattice IS low-rank + Montague-shaped (null-gated)
c3fa367 🔄 P-TYPE-1a lattice-geometry instrument + massive-activation confound fixed
5c7e768 💡 3-hop result: depth is sequencing not capability + s282 types triangulation (mementum)
62b6066 💡 3-hop composes at BOTH scales — depth is fuel for SEQUENCING, not capability
3ec4d47 ✅ 3-hop capacity harness: operand_multihop3.py (geography chain, ceiling smoke green)
9436a62 🎯 3-hop capacity pre-reg APPROVED — geography chain frozen; state synced (s282)
---
?? mementum/knowledge/chats/session-282.md
?? refs/
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/types-are-the-well-formedness-of-reduction.md",
  "limit": 80
}
```

**Summary:** Reading types-are-the-well-formedness-of-reduction.md (0-80)

**Output:**
```
---
title: "Types are the well-formedness of β-reduction — the combinator reading of the type lattice"
status: active
category: explore
tags: [types, beta-reduction, combinators, KIBC, CCG, montague, lambek, discocat,
       curry-howard, well-formedness, S-combinator, B-combinator, functor-kind,
       type-check, compiler, P-TYPE-1, P-TYPE-1b, C1, C2, C9, s282]
related:
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

[CONTENT TRUNCATED] Showing lines 1 to 80 of 180 total lines. Use line_offset=80 parameter to read more content.
```

### Thinking

The s282 types have landed, so I'm confirming we're oriented on the current state—everything from that work appears committed, though there's a pending approval from Michael for the P-TYPE-1b heavy 32B run. The working tree is clean aside from the session chat and refs, so we're ready to move forward once that sign-off comes through.

## Assistant

Oriented. ✅ Cold-start complete — and yes, the types arc **landed** in s282. Here's where we stand:

## What we found (s282, all committed)

**Three-register triangulation** → type = decodable readout of a distributed compute, NOT a causal direction:
- **Behavioural** (v3): crossover +2.038, t=9.3 — real, but carried entirely by `name_pen` (predicate-licensing = argument saturation)
- **Decodability**: 8-way type linearly decodable 0.88–0.96 at every layer (baseline 0.28)
- **Causal** (v4): direction ablation retains 0.643 vs 0.952 random → decodable-but-not-ablatable (same pattern as D1 C-field; folds C5 into C2)

**P-TYPE-1a geometry** (null-gated @32B): the Montague type lattice is **low-rank + Montague-shaped** — compress→expand arc, sustained band L6–L48 (PR 3.7–4.8, p<0.05, ~3 axes). The montague-inversion decisive prediction ("lattice SMALL") confirmed.

**1a-follow**: the 3 axes are **functor-KIND axes** — axis0 (73%) QUANT+DET = binding, axis2 REL/PRED-vs-MOD = modification, ENTITY at the origin. Arity ladder negative → **CCG-combinatory typing, not Church-arity**.

**Theory closure** (02a4804): given attention=β-reduction (s276) + KIBC compute (C2), **a type = the well-formedness of a reduction** — unstorable by construction, which *forces* decodable-not-causal. The type lattice is a projection of the combinator basis: axis0=S/binding, axis2=B/composition, e=I/operand. S5 `λ types` resolves: type = the router's combinator-selector.

## State check

- git log is clean and coherent with state.md — s282 mementum commits are in (5c7e768, 238e370, 02a4804); working tree has only `chats/session-282.md` + `refs/` (your domains, I don't touch them)
- Branch ~30 commits ahead of origin, unpushed

## Next (pre-registered & frozen)

**P-TYPE-1b** — combinator-zone × type-class **double dissociation**: ablate axis0 (binding/S) vs axis2 (composition/B) across the L6–L48 band, predict axis0-abl breaks QUANT/DET-composition not MOD, axis2-abl the reverse, null-gated. Not a v4 repeat (zone×axis class-selectivity, not global direction). Host = 32B — **⚠ pending your GO** (heavy run; confirm the box is free).

Also open: pre-reg the depth→SEQUENCING hypothesis for 27B-hybrid, and the (a2) mammal→fur content build.

Say the word and I'll build the 1b wrapper (reusing `type_lattice_geometry` axis extraction + v3-style surprisal readouts) — or we can start with the smoke on 0.6B before committing the 32B compute.

## User

Let's smoke test it on the 4B that should be fast enough and give us some capacity to see interesting things.


### Thinking

Michael's asking for a smoke test of P-TYPE-1b on Qwen3-4B, so I need to inventory the existing tools I have available. There's the type lattice geometry script that handles axis extraction with SVD and null-gating, the v3 nonce-crossover surprisal readouts somewhere in the results directory that I need to locate, the v4 ablation script for direction ablation, and some wrapper scripts I haven't fully catalogued yet.

The pre-registration for P-TYPE-1b is frozen in the theory document, so I should read through that section to understand the frozen design, then map it against what code already exists that I can reuse. My approach is to first read the full pre-reg spec, then examine the type lattice geometry script to understand the axis extraction, hunt down the v3/v4 surprisal and ablation scripts, adapt them into a wrapper for 1b on the 4B model, and run the smoke test. I need to flag that this is instrument validation on 4B, not the actual verdict run which is supposed to use 32B—the pre-reg specifies a low-rank band that's 32B-specific, so I'll need to either measure the equivalent band on 4B using the geometry script or scale it proportionally, and I should also derive the appropriate axis directions for 4B rather than just reusing the 32B ones.

## Assistant

Good call — 4B is the workhorse (36L, dense, all the operand arcs ran there) and unlike 0.6B it actually computes the functions. Let me pull the frozen pre-reg and the instruments to reuse.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/types-are-the-well-formedness-of-reduction.md",
  "line_offset": 80
}
```

**Summary:** Reading types-are-the-well-formedness-of-reduction.md (80-2080)

**Output:**
```
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

## Sessions
s282 (theoretical closure from the types discussion; P-TYPE-1b pre-registration drafted).
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls scripts/explore/ | head -30; echo ---; ls wrapper/ | head -40; echo ---; ls results/type-directed 2>/dev/null | head",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ ls scripts/explore/ | head -30; ech...

**Output:**
```
Exit code: 0
Stdout:
__pycache__
attention_spiral_3d.py
attention_spiral.py
extract_and_train.py
extract_holographic_bank.py
fractal_collapse_screen.py
holographic_etch_with_lens.py
laser_etch_factual.py
probe_algebraic_compose.py
probe_beam_trace.py
probe_beta_reduction.py
probe_categorical_geometry.py
probe_combinators_extended.py
probe_combinators_pythia.py
probe_combinators_universal.py
probe_combinators.py
probe_composed_transform.py
probe_crystal_comparison.py
probe_crystal_seed.py
probe_datafitted_dimension.py
probe_einstein_crystal.py
probe_extraction_dimension.py
probe_factual_indexing.py
probe_factual_recall.py
probe_ffn_indexing.py
probe_fixed_point.py
probe_geometric_encoding.py
probe_hologram_atlas.py
probe_hologram_decomposition.py
probe_hologram_heads.py
---
__pycache__
build
CMakeLists.txt
frame_invariance.py
moe_calibrate.py
operand_bake.py
operand_compose.py
operand_compose2.py
operand_depthbudget.py
operand_dsp.py
operand_harden.py
operand_insert.py
operand_map.py
operand_mirror.py
operand_multihop.py
operand_multihop3.py
operand_quant.py
operand_write.py
q4_routing_topology.py
stage1_characterize.py
stage1_localize.py
tap_loader.py
vsm_tap.cpp
---
crossfamily_nonce_summary.json
crossfamily_sweep.log
crossfamily_v4_ablation.log
type_directed_v1_meta_qwen3-14b.json
type_directed_v1_meta_qwen3-8b.json
type_directed_v1_verdict_qwen3-14b.json
type_directed_v1_verdict_qwen3-8b.json
type_directed_v2_meta_qwen3-14b.json
type_directed_v2_meta_qwen3-8b.json
type_directed_v2_verdict_qwen3-14b.json
```

### Thinking

I need to find type_lattice_geometry.py and the v3/v4 scripts to locate them.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "find scripts wrapper src -name \"*type*\" -o -name \"*lattice*\" | grep -v __pycache__; echo ---; ls results/type-lattice* 2>/dev/null; ls results | grep -i -E \"type|lattice\"",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ find scripts wrapper src -name "*ty...

**Output:**
```
Exit code: 0
Stdout:
scripts/run_type_probe.py
scripts/v12/build_binding_lattice.py
scripts/v12/q2_lattice_etch_exp.py
scripts/v12/build_lattice_map.py
scripts/v12/build_basin_lattice.py
scripts/experiments/type_directed_v3_nonce.py
scripts/experiments/attention_typed_binding.py
scripts/experiments/type_directed_v2.py
scripts/experiments/crystal_sieve_prototype.py
scripts/experiments/type_directed_v4_ablation.py
scripts/experiments/crystal_circuit_types.py
scripts/experiments/type_directed_v1.py
scripts/explore/type_lattice_geometry.py
scripts/explore/probe_type_qwen3_32b.py
scripts/explore/probe_lattice_consensus.py
scripts/v10/probe_type_transition.py
---
qwen3-0-6b
qwen3-32b
attention-typed-binding
crystal-circuit-types
lattice-consensus
q2-lattice-etch
sr-self-ref-typed-20260417-003408
type-directed
type-lattice
type-probe
type-probe-qwen3-32b
type-transition
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/type_lattice_geometry.py"
}
```

**Summary:** Reading type_lattice_geometry.py (0-2000)

**Output:**
```
#!/usr/bin/env python3
"""P-TYPE-1a — the type LATTICE geometry (is it low-rank + Montague-shaped?).

Follows the s282 register triangulation (state s282): type is a DECODABLE
value-register readout (type-probe 0.88-0.96 all layers) but NOT a causal direction
(v4 type_direction_is_causal=false). So this measures the VALUE-register GEOMETRY of
the 8 Montague type centroids and asks the P-TYPE-1a question:

  Is the type geometry LOW-RANK (few primitive axes, Montague-shaped), or full-rank
  (a generic 8-way simplex with no algebra)?

Reuses the labeled data + capture pipeline from probe_type_qwen3_32b (λ one_way).

Metrics (per layer):
  1. LOW-RANK: participation ratio (PR) of the row-centered 8xD centroid matrix's
     singular values. PR ~= effective number of type axes (max ~7 for 8 classes).
     Low PR (~2-3) => a small primitive lattice; PR ~7 => generic simplex.
  2. NULL (MANDATORY, λ yardstick, pre-committed here): shuffle the type labels K
     times, recompute centroids+PR. Real low-rank counts ONLY if PR_real is below the
     shuffled-null band (p = frac[PR_null <= PR_real]). "Looks low-rank" != "is".
  3. GRAM: cosine similarity of the 8 centered type directions (structure eyeball).
  4. ARITY LADDER (exploratory, labeled): Montague currying ENTITY(e) -> PRED(<e,t>)
     -> REL(<e,<e,t>>). If arity is a consistent axis, cos(PRED-ENTITY, REL-PRED) > 0
     and beats random type-pair offsets. A vector-arithmetic type-algebra signature.
  5. DECODABILITY sanity: confirm centroids are genuinely separated (nearest-centroid
     accuracy) so we are not reading a degenerate collapsed regime.

Crystal(B/C/S) alignment is DEFERRED (cross-space; risks forced-fit — λ measure).

Usage:
    uv run python scripts/explore/type_lattice_geometry.py --model Qwen/Qwen3-0.6B \
        --device mps --layer-stride 2                     # fast prototype
    uv run python scripts/explore/type_lattice_geometry.py --model Qwen/Qwen3-32B \
        --device mps --layer-stride 2                     # the host that matters

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "scripts" / "explore"))

from probe_type_qwen3_32b import (  # noqa: E402
    LABELED_DATA,
    build_probing_dataset,
    load_model,
)

TYPE_ORDER = ["ENTITY", "PRED", "REL", "QUANT", "DET", "MOD", "CONN", "FUNC"]


def standardize(x: np.ndarray) -> np.ndarray:
    """Per-dimension z-score (diagonal whitening). Removes the massive-activation /
    rogue-dimension artifact that dominates raw mid/late residual norms and collapses
    Euclidean centroid geometry (λ measure: match the space the linear probe uses)."""
    mu = x.mean(axis=0, keepdims=True)
    sd = x.std(axis=0, keepdims=True) + 1e-6
    return (x - mu) / sd


def participation_ratio(sv: np.ndarray) -> float:
    """Effective number of components from singular values (scale-free)."""
    sv = sv[sv > 1e-12]
    if sv.size == 0:
        return 0.0
    return float((sv.sum() ** 2) / (sv ** 2).sum())


def centroids(x: np.ndarray, y: np.ndarray, labels: list[str]):
    """Per-label mean rows (labels present only). Returns (C, present_labels)."""
    rows, present = [], []
    for lab in labels:
        m = y == lab
        if m.sum() >= 2:
            rows.append(x[m].mean(axis=0))
            present.append(lab)
    return np.array(rows), present


def centroid_pr(x: np.ndarray, y: np.ndarray, labels: list[str]) -> float:
    c, present = centroids(x, y, labels)
    if len(present) < 3:
        return float("nan")
    cc = c - c.mean(axis=0, keepdims=True)          # spread of the type points
    sv = np.linalg.svd(cc, compute_uv=False)
    return participation_ratio(sv)


def nearest_centroid_acc(x: np.ndarray, y: np.ndarray, labels: list[str]) -> float:
    """Leave-nothing-out nearest-centroid accuracy (separation sanity, not CV)."""
    c, present = centroids(x, y, labels)
    if len(present) < 2:
        return float("nan")
    idx = {lab: i for i, lab in enumerate(present)}
    mask = np.array([t in idx for t in y])
    xs, ys = x[mask], y[mask]
    d = np.linalg.norm(xs[:, None, :] - c[None, :, :], axis=2)
    pred = np.array(present)[d.argmin(axis=1)]
    return float((pred == ys).mean())


def arity_ladder(x: np.ndarray, y: np.ndarray, rng) -> dict:
    """Montague currying ENTITY -> PRED -> REL as a consistent offset axis."""
    c, present = centroids(x, y, ["ENTITY", "PRED", "REL"])
    if len(present) < 3:
        return {"cos": None}
    ent, pred, rel = c[0], c[1], c[2]
    o1, o2 = pred - ent, rel - pred

    def cos(a, b):
        return float(a @ b / ((np.linalg.norm(a) * np.linalg.norm(b)) + 1e-9))

    real = cos(o1, o2)
    # null: random pairs of type-offset directions among all present types
    call, pall = centroids(x, y, TYPE_ORDER)
    null = []
    if len(pall) >= 4:
        for _ in range(200):
            i, j, k, m = rng.choice(len(pall), size=4, replace=False)
            null.append(cos(call[j] - call[i], call[m] - call[k]))
        null = np.array(null)
        p = float(np.mean(null >= real))
    else:
        p = None
    return {"cos": round(real, 3),
            "null_mean": round(float(np.mean(null)), 3) if len(null) else None,
            "p": p}


def axis_loadings(x: np.ndarray, y: np.ndarray, labels: list[str], k: int = 3) -> dict:
    """SVD of the centered type centroids -> each TYPE's loading on the top-k axes.
    Left singular vectors U[:, i] give how each present type projects onto axis i;
    var_frac = the axis's share of centroid spread. (Which types on which axis.)"""
    c, present = centroids(x, y, labels)
    if len(present) < 3:
        return {"present": present, "axes": []}
    cc = c - c.mean(axis=0, keepdims=True)
    u, s, _ = np.linalg.svd(cc, full_matrices=False)
    tot = (s ** 2).sum() + 1e-12
    axes = []
    for i in range(min(k, len(s))):
        # sign-fix: make the largest-magnitude loading positive (SVD sign is arbitrary)
        col = u[:, i]
        col = col * (1.0 if col[np.argmax(np.abs(col))] >= 0 else -1.0)
        axes.append({"i": i, "var_frac": round(float(s[i] ** 2 / tot), 3),
                     "loadings": {t: round(float(v), 3)
                                  for t, v in zip(present, col, strict=False)}})
    return {"present": present, "axes": axes}


def gram(x: np.ndarray, y: np.ndarray) -> dict:
    c, present = centroids(x, y, TYPE_ORDER)
    if len(present) < 2:
        return {}
    cc = c - c.mean(axis=0, keepdims=True)
    n = cc / (np.linalg.norm(cc, axis=1, keepdims=True) + 1e-9)
    g = n @ n.T
    return {"labels": present,
            "cos": [[round(float(v), 2) for v in row] for row in g]}


def main() -> None:
    ap = argparse.ArgumentParser(description="P-TYPE-1a type lattice geometry")
    ap.add_argument("--model", default="Qwen/Qwen3-0.6B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--layer-stride", type=int, default=2)
    ap.add_argument("--n-null", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--output", default=None)
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    model, tok, config = load_model(args.model, device=args.device)
    n_layers = config.num_hidden_layers
    layers = [-1, *range(0, n_layers, args.layer_stride)]
    if (n_layers - 1) not in layers:
        layers.append(n_layers - 1)

    data, n_lab, n_skip = build_probing_dataset(
        model, tok, layers, LABELED_DATA, verbose=True)
    print(f"[lattice] labeled={n_lab} skipped={n_skip} layers={len(data)}",
          file=sys.stderr)

    del model
    import gc
    gc.collect()

    # standardize per layer (diagonal whitening) — see standardize() docstring
    data = {L: (standardize(x), y) for L, (x, y) in data.items()}

    per_layer = {}
    for L in sorted(data.keys()):
        x, y = data[L]
        pr = centroid_pr(x, y, TYPE_ORDER)
        # pre-committed shuffled-label null
        null = []
        for _ in range(args.n_null):
            yp = rng.permutation(y)
            null.append(centroid_pr(x, yp, TYPE_ORDER))
        null = np.array([v for v in null if not np.isnan(v)])
        p = float(np.mean(null <= pr)) if null.size else None
        c, present = centroids(x, y, TYPE_ORDER)
        cc = c - c.mean(axis=0, keepdims=True)
        sv = np.linalg.svd(cc, compute_uv=False)
        tot = (sv ** 2).sum() + 1e-12
        per_layer[str(L)] = {
            "pr_real": round(pr, 3),
            "pr_null_mean": round(float(null.mean()), 3) if null.size else None,
            "pr_null_std": round(float(null.std()), 3) if null.size else None,
            "p_lowrank": p,
            "n_types": len(present),
            "var_top2": round(float((sv[:2] ** 2).sum() / tot), 3),
            "var_top3": round(float((sv[:3] ** 2).sum() / tot), 3),
            "sep_acc": round(nearest_centroid_acc(x, y, TYPE_ORDER), 3),
            "arity": arity_ladder(x, y, rng),
        }
        r = per_layer[str(L)]
        lab = "embed" if L == -1 else f"L{L}"
        print(f"[lattice] {lab:6s} PR={r['pr_real']:.2f} "
              f"null={r['pr_null_mean']}±{r['pr_null_std']} p={p} "
              f"top3var={r['var_top3']} sep={r['sep_acc']} "
              f"arity_cos={r['arity']['cos']}(p={r['arity']['p']})", file=sys.stderr)

    # gram at the most-separated layer (lexical, usually)
    best_L = max(data.keys(), key=lambda k: nearest_centroid_acc(*data[k], TYPE_ORDER))
    gram_best = gram(*data[best_L])

    # 1a-follow: characterize the ~3 primitive axes INSIDE the low-rank band.
    # band layer = interior layer (mid-third) with the most-significant low-rank null.
    interior = [L for L in data if 0 <= L and n_layers * 0.15 <= L <= n_layers * 0.65]
    band_L = (min(interior, key=lambda L: per_layer[str(L)]["p_lowrank"])
              if interior else best_L)
    bx, by = data[band_L]
    gram_band = gram(bx, by)
    load_band = axis_loadings(bx, by, TYPE_ORDER, k=3)
    print(f"\n[lattice] BAND layer L{band_L} axis loadings (type -> top-3 SVD axes):",
          file=sys.stderr)
    for ax in load_band["axes"]:
        pairs = sorted(ax["loadings"].items(), key=lambda kv: -abs(kv[1]))
        top = "  ".join(f"{t}:{v:+.2f}" for t, v in pairs)
        print(f"[lattice]   axis{ax['i']} (var {ax['var_frac']:.2f}): {top}",
              file=sys.stderr)

    slug = args.model.split("/")[-1].lower().replace(".", "-")
    out = (Path(args.output) if args.output
           else _ROOT / "results" / "type-lattice" / slug)
    out.mkdir(parents=True, exist_ok=True)
    res = {"model": args.model, "device": args.device,
           "timestamp_utc": datetime.now(UTC).isoformat(),
           "n_layers": n_layers, "n_labeled": n_lab, "n_null": args.n_null,
           "layer_stride": args.layer_stride, "type_order": TYPE_ORDER,
           "gram_best_layer": int(best_L), "gram": gram_best,
           "band_layer": int(band_L), "gram_band": gram_band,
           "axis_loadings_band": load_band,
           "per_layer": per_layer}
    (out / "lattice_geometry.json").write_text(json.dumps(res, indent=2))
    print(f"[lattice] wrote {out}/lattice_geometry.json", file=sys.stderr)


if __name__ == "__main__":
    main()
```

### Thinking

I need to examine the v3 nonce surprisal and v4 ablation scripts to extract their readout and hook-ablation patterns, then check the probe script for its model loading and dataset building approach to reuse those components.

## Assistant

Instrument is clean and reusable. Now the v3 surprisal readout and v4 ablation hook patterns:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/type_directed_v4_ablation.py"
}
```

**Summary:** Reading type_directed_v4_ablation.py (0-2000)

**Output:**
```
#!/usr/bin/env python3
# register: TYPE-DIRECTEDNESS — causal ablation of the type direction (v4)
"""Type-directedness, v4 — CAUSAL ablation (correlation -> causation).

v3 (nonce crossover) showed, frequency-free, that the model USES an in-context-taught
type to direct composition (crossover 8B +2.18/14B +2.04, t~9-10, consistency 1.0). But
that is BEHAVIOURAL/correlational. This is the causal upgrade: DECODE the type direction
in the residual stream and ABLATE it — if the type direction CAUSES the composition
behaviour, the v3 crossover COLLAPSES under type-direction ablation, while a RANDOM-
direction ablation of the same magnitude leaves it intact (the control, lambda measure).

THE MECHANISM under test: in "{teach}. {filler} {nonce}" the model predicts the nonce
from the residual at the FILLER position (the token before the nonce — the next-token
bottleneck). VERB-taught -> that residual should carry "expect a predicate" so the nonce
is cheap after a name; NOUN-taught -> "expect a noun" so cheap after a det. The TYPE
DIRECTION = difference-of-means(verb - noun) of the filler-position residual (robust
concept direction; per-layer; pick the most decodable layer L* by AUC).

INTERVENTION: project the unit type direction OUT of the residual at the filler position
at layer L* during the forward pass -> both conditions lose the type component -> if it
drove composition, name_pen (and the crossover) collapse toward 0.
CONTROL: project out a RANDOM unit direction (same procedure) -> crossover survives.

VERDICT (lambda measure): type-ablation collapses the crossover AND random preserves it
-> the type direction is CAUSAL; type-directed composition is mechanistic, not just
behavioural; confirms s139 (type decodable+co-located) as DIRECTING dispatch. Both
collapse -> ablation non-specific. Neither -> the type info the prediction uses is
not at the filler position/this layer (try other loci).

CAVEATS (lambda measure): single-position single-layer linear ablation (type may be
distributed -> a null is not decisive); difference-of-means concept direction;
in-context teaching; behavioural readout; 1 family. Per-layer AUC logged so a low-AUC
null is not over-read as "no causation".

Usage:
    uv run python scripts/experiments/type_directed_v4_ablation.py --smoke   # 8B
    uv run python scripts/experiments/type_directed_v4_ablation.py           # 14B

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT / "scripts" / "experiments"))

from opcode_monitor_v2 import (  # noqa: E402
    _git_sha,
    _json_safe,
    _transformers_version,
    load_model_and_tokenizer,
)
from type_directed_v3_nonce import (  # noqa: E402
    DET_FILL,
    NAME_FILL,
    NONCE,
    NOUN_TEACH,
    VERB_TEACH,
    build_text,
)

RESULTS_DIR = _ROOT / "results" / "type-directed"


def decoder_layers(model):
    """Architecture-agnostic decoder-layer list (cross-family ablation).

    Llama/Mistral/OLMo/Qwen/SmolLM -> model.model.layers ; GPTNeoX/Pythia ->
    model.gpt_neox.layers ; GPT-2 -> transformer.h ; OPT -> model.decoder.layers.
    """
    for path in ("model.layers", "gpt_neox.layers", "transformer.h",
                 "model.decoder.layers"):
        obj = model
        ok = True
        for attr in path.split("."):
            if not hasattr(obj, attr):
                ok = False
                break
            obj = getattr(obj, attr)
        if ok:
            return obj
    raise AttributeError("could not locate decoder layers for this architecture")


def gen_items(n_each: int, seed: int, n_teach: int):
    """v3-style items, subsampled teach templates (causal passes are 3x forwards)."""
    rng = np.random.default_rng(seed)
    items = []

    def pick(pool, k):
        idx = rng.choice(len(pool), size=min(k, len(pool)), replace=False)
        return [pool[i] for i in idx]

    for w in NONCE:
        for typ, teaches in (("noun", NOUN_TEACH), ("verb", VERB_TEACH)):
            for teach in teaches[:n_teach]:
                for frame, fills in (("det", DET_FILL), ("name", NAME_FILL)):
                    for filler in pick(fills, n_each):
                        items.append({"w": w, "type": typ, "frame": frame,
                                      "teach": teach, "filler": filler,
                                      "cond": f"{frame}_{typ}"})
    rng.shuffle(items)
    return items


def locate(item, tok):
    """Tokenize; return (ids, attn, nonce_token_indices, filler_pos)."""
    text, c0 = build_text(item["teach"], item["w"], item["filler"])
    c1 = len(text)
    enc = tok(text, return_tensors="pt", return_offsets_mapping=True)
    offsets = enc["offset_mapping"][0].tolist()
    nonce_js = [j for j, (s, e) in enumerate(offsets)
                if e > s and s < c1 and e > c0]
    filler_pos = (min(nonce_js) - 1) if nonce_js else None
    return enc, nonce_js, filler_pos


def nonce_surprisal(logits_logp, ids, nonce_js):
    vals = [-float(logits_logp[j - 1, ids[j]]) for j in nonce_js if j >= 1]
    return float(np.mean(vals)) if vals else None


def make_ablation_hook(direction_unit, pos_box, torch_mod, whole=True):
    """Forward hook on a decoder layer: project `direction_unit` OUT of the residual
    (output[0]). whole=True -> ALL token positions (global concept removal, so the type
    cannot be re-read from the teaching tokens); else only `pos_box[0]` (the filler)."""
    def hook(_module, _inp, out):
        h = out[0] if isinstance(out, tuple) else out
        d = torch_mod.as_tensor(direction_unit, dtype=h.dtype, device=h.device)
        if whole:
            coeff = h[0] @ d  # [T]
            h[0] = h[0] - coeff[:, None] * d[None, :]
        else:
            pos = pos_box[0]
            v = h[0, pos, :]
            h[0, pos, :] = v - (v @ d) * d
        return out
    return hook


def _auc(pos_scores, neg_scores):
    """Mann-Whitney AUC: P(verb proj > noun proj)."""
    pos, neg = np.asarray(pos_scores), np.asarray(neg_scores)
    if len(pos) == 0 or len(neg) == 0:
        return 0.5
    allv = np.concatenate([pos, neg])
    ranks = allv.argsort().argsort().astype(float) + 1
    r_pos = ranks[: len(pos)].sum()
    return float((r_pos - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def crossover_stats(surpr_by_cond_w):
    """Given cond->w->[surprisal], return det_pen, name_pen, crossover (paired by w)."""
    def cell(c, w):
        v = surpr_by_cond_w[c].get(w, [])
        return float(np.mean(v)) if v else None

    dpen, npen, cross = [], [], []
    for w in NONCE:
        cells = [cell(f"{fr}_{ty}", w) for fr in ("det", "name")
                 for ty in ("verb", "noun")]
        if all(c is not None for c in cells):
            dv, dn, nv, nn = cells
            dpen.append(dv - dn)
            npen.append(nv - nn)
            cross.append((dv - dn) - (nv - nn))

    def agg(arr):
        a = np.asarray(arr)
        if len(a) < 2:
            return None
        se = float(a.std(ddof=1) / np.sqrt(len(a)))
        return {"mean": round(float(a.mean()), 4),
                "t": round(float(a.mean() / se) if se > 0 else 0.0, 3), "n": len(a)}

    return {"det_pen": agg(dpen), "name_pen": agg(npen), "crossover": agg(cross)}


def run_pass(items, model, tok, torch_mod, ablations=None):
    """Forward each item; ablate the filler position across a STACK of layers.

    ablations = list[(layer_module, direction_vector)] — each projects its direction
    OUT of the filler-position residual at that layer (filler-stack ablation, so the
    type cannot be re-derived downstream). Returns cond->w->[surprisal]."""
    import torch.nn.functional as func
    out: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    dev = next(model.parameters()).device
    pos_box = [0]
    handles = []
    if ablations:
        for mod, direction in ablations:
            handles.append(mod.register_forward_hook(
                make_ablation_hook(direction, pos_box, torch_mod)))
    try:
        for it in items:
            enc, nonce_js, fpos = locate(it, tok)
            if not nonce_js or fpos is None or fpos < 0:
                continue
            pos_box[0] = fpos
            ids = enc["input_ids"][0]
            with torch_mod.no_grad():
                logits = model(input_ids=ids.unsqueeze(0).to(dev),
                               attention_mask=enc["attention_mask"].to(dev)).logits[0]
            logp = func.log_softmax(logits.float(), dim=-1).cpu()
            s = nonce_surprisal(logp, ids.cpu(), nonce_js)
            if s is not None:
                out[it["cond"]][it["w"]].append(s)
    finally:
        for h in handles:
            h.remove()
    return out


def collect_residuals(items, model, tok, torch_mod):
    """Forward with output_hidden_states; return (rows, baseline-surprisal dict). Each
    row = (item, resid[L+1,H] at FILLER pos, label 1=verb/0=noun)."""
    out: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    dev = next(model.parameters()).device
    import torch.nn.functional as func
    rows = []
    for it in items:
        enc, nonce_js, fpos = locate(it, tok)
        if not nonce_js or fpos is None or fpos < 0:
            continue
        ids = enc["input_ids"][0]
        with torch_mod.no_grad():
            res = model(input_ids=ids.unsqueeze(0).to(dev),
                        attention_mask=enc["attention_mask"].to(dev),
                        output_hidden_states=True)
        hs = res.hidden_states  # tuple len n_layers+1, each [1,T,H]
        vecs = np.stack([h[0, fpos, :].float().cpu().numpy().astype(np.float16)
                         for h in hs])  # [L+1, H]
        logp = func.log_softmax(res.logits[0].float(), dim=-1).cpu()
        s = nonce_surprisal(logp, ids.cpu(), nonce_js)
        rows.append((it, vecs, 1 if it["type"] == "verb" else 0))
        if s is not None:
            out[it["cond"]][it["w"]].append(s)
    return rows, out


def main() -> None:
    ap = argparse.ArgumentParser(description="Type-directedness causal ablation (v4)")
    ap.add_argument("--model", default="Qwen/Qwen3-14B")
    ap.add_argument("--n-each", type=int, default=3, help="fillers per cell")
    ap.add_argument("--n-teach", type=int, default=2, help="teach templates per type")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    model_name = args.model
    n_each, n_teach = args.n_each, args.n_teach
    if args.smoke:
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-8B"
        n_each, n_teach = 2, 2
        print("[type-dir4] SMOKE MODE (Qwen3-8B)")

    items = gen_items(n_each, args.seed, n_teach)
    print(f"[type-dir4] {len(items)} items (n_each={n_each}, n_teach={n_teach})")

    model, tok, torch_mod = load_model_and_tokenizer(model_name)

    # ── pass 1: collect filler-position residuals + baseline surprisal ──────────
    print("[type-dir4] pass 1: collecting residuals + baseline ...")
    rows, base = collect_residuals(items, model, tok, torch_mod)
    n_layers_p1 = rows[0][1].shape[0]  # L+1 hidden states
    hdim = rows[0][1].shape[1]

    # ── difference-of-means TYPE direction per layer + decodability (AUC) ───────
    verb_idx = [i for i, r in enumerate(rows) if r[2] == 1]
    noun_idx = [i for i, r in enumerate(rows) if r[2] == 0]
    layer_auc, layer_dir = [], []
    for li in range(n_layers_p1):
        vmean = np.mean([rows[i][1][li].astype(np.float32) for i in verb_idx], axis=0)
        nmean = np.mean([rows[i][1][li].astype(np.float32) for i in noun_idx], axis=0)
        d = vmean - nmean
        nrm = np.linalg.norm(d)
        dunit = d / nrm if nrm > 0 else d
        proj = [float(rows[i][1][li].astype(np.float32) @ dunit)
                for i in range(len(rows))]
        auc = _auc([proj[i] for i in verb_idx], [proj[i] for i in noun_idx])
        layer_auc.append(round(auc, 4))
        layer_dir.append(dunit)
    lstar = int(np.argmax(layer_auc))  # hidden-state index (0=emb, 1..=layer outputs)
    print(f"[type-dir4] type-direction decodability AUC by layer: "
          f"max={layer_auc[lstar]} @ hidden-state {lstar} (of {n_layers_p1})")
    print(f"[type-dir4]   AUC profile (every 4): "
          f"{[layer_auc[i] for i in range(0, n_layers_p1, 4)]}")

    base_stats = crossover_stats(base)
    print(f"[type-dir4] BASELINE crossover={base_stats['crossover']} "
          f"name_pen={base_stats['name_pen']}")

    # FILLER-STACK ablation: project the per-layer type direction OUT of the filler
    # residual at EVERY hidden state h >= L* (so the type cannot be re-derived
    # downstream by attention to the teaching). hidden_states[h] <- hook layers[h-1].
    if lstar == 0:
        print("[type-dir4] WARN: best AUC at embeddings; starting ablation at layer 0")
        lstar = 1
    rng = np.random.default_rng(args.seed + 7)
    layers = decoder_layers(model)
    type_ablations, rand_ablations = [], []
    for h in range(lstar, n_layers_p1):
        mod = layers[h - 1]
        type_ablations.append((mod, layer_dir[h].astype(np.float32)))
        r = rng.standard_normal(hdim).astype(np.float32)
        rand_ablations.append((mod, r / np.linalg.norm(r)))
    print(f"[type-dir4] filler-stack ablation, hidden states {lstar}.."
          f"{n_layers_p1 - 1} ({len(type_ablations)} layers)")

    print("[type-dir4] pass 2: TYPE-direction ablation ...")
    type_abl = run_pass(items, model, tok, torch_mod, type_ablations)
    type_stats = crossover_stats(type_abl)
    print("[type-dir4] pass 3: RANDOM-direction ablation (control) ...")
    rand_abl = run_pass(items, model, tok, torch_mod, rand_ablations)
    rand_stats = crossover_stats(rand_abl)

    def ratio(ab, bs):
        if ab and bs and bs.get("crossover") and ab.get("crossover") \
                and bs["crossover"]["mean"]:
            return round(ab["crossover"]["mean"] / bs["crossover"]["mean"], 3)
        return None

    type_ratio = ratio(type_stats, base_stats)
    rand_ratio = ratio(rand_stats, base_stats)
    causal = bool(type_ratio is not None and rand_ratio is not None
                  and type_ratio < 0.5 and rand_ratio > 0.7)

    verdict = {"register": "causal ablation of the type direction (v4)",
               "ablation_layer_hidden_state": lstar,
               "type_direction_auc": layer_auc[lstar], "auc_by_layer": layer_auc,
               "baseline": base_stats, "type_ablated": type_stats,
               "random_ablated": rand_stats,
               "crossover_retained_type": type_ratio,
               "crossover_retained_random": rand_ratio,
               "type_direction_is_causal": causal, "n_items": len(items)}

    print("\n" + "=" * 72)
    print("TYPE-DIRECTEDNESS v4 — is the type direction CAUSAL?")
    print("=" * 72)
    print(f"  type-direction decodability AUC @ L*={lstar}: {layer_auc[lstar]}")
    for tag, st in (("BASELINE", base_stats), ("TYPE-ablated", type_stats),
                    ("RANDOM-ablated", rand_stats)):
        cx, nm = st.get("crossover"), st.get("name_pen")
        cxs = f"{cx['mean']} (t={cx['t']})" if cx else "n/a"
        nms = f"{nm['mean']} (t={nm['t']})" if nm else "n/a"
        print(f"  {tag:<16} crossover={cxs:<22} name_pen={nms}")
    print(f"\n  crossover retained: TYPE-ablation={type_ratio}  "
          f"RANDOM-ablation={rand_ratio}")
    print(f"  * type_direction_is_causal = {causal}")
    print("=" * 72 + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    (RESULTS_DIR / f"type_directed_v4_ablation_verdict_{slug}.json").write_text(
        json.dumps(_json_safe(verdict), indent=2), encoding="utf-8")
    meta = {"model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "transformers_version": _transformers_version(),
            "n_each": n_each, "n_teach": n_teach, "n_items": len(items),
            "seed": args.seed, "hidden_dim": hdim, "n_hidden_states": n_layers_p1}
    (RESULTS_DIR / f"type_directed_v4_ablation_meta_{slug}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[type-dir4] wrote v4 verdict for {slug}")


if __name__ == "__main__":
    main()
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/type_directed_v3_nonce.py",
  "limit": 120
}
```

**Summary:** Reading type_directed_v3_nonce.py (0-120)

**Output:**
```
#!/usr/bin/env python3
# register: TYPE-DIRECTEDNESS — nonce frequency-free crossover (v3, the decisive test)
"""Type-vs-position dissociation, v3 — the FREQUENCY-FREE nonce crossover.

v1/v2 showed a ROBUST behavioural type effect (a verb is cheap after a subject-NP,
dear after a non-subject; consistency 1.0) — but with real words "type-licensed"
confounds with bigram-FREQUENCY/grammaticality, and the forward arm was unmeasurable
(universal-donor targets). This kills the frequency confound: NONCE words have NO
bigram statistics, so any composition preference is the IN-CONTEXT TYPE directing it.

THE DESIGN — a CROSSOVER INTERACTION (subtracts every main effect, incl. priming):
  Teach a nonce word's TYPE in-context, then test it in two frames:
    TEACH noun:  "{W}s are common objects."   (plural -> count noun)
    TEACH verb:  "They often {w}."            (bare/infinitive -> verb)
    TEST det:    "The {w}"   det licenses a NOUN  -> cheap if NOUN-taught
    TEST name:   "John {w}"  name licenses a PRED -> cheap if VERB-taught
  full = "{teach}. {filler} {w}"  ; measure surprisal of the final nonce token.

  det_pen(w)  = S(det, verb-taught)  - S(det, noun-taught)     ( >0 if typed )
  name_pen(w) = S(name, verb-taught) - S(name, noun-taught)    ( <0 if typed )
  CROSSOVER(w) = det_pen(w) - name_pen(w)  (paired by nonce word; >>0 if type-directed)

  A crossover (the cheaper TEACHING flips with the FRAME) CANNOT come from frequency
  or a teach/prime/frame main effect — ONLY the taught TYPE interacting with the
  frame's type-requirement. Nonce -> frequency-free. This is the decisive type-directed
  composition signal (and the clean dissociation the v2 forward arm could not give).

VERDICT (lambda measure): CROSSOVER >0 sig + det_pen>0 + name_pen<0 -> composition is
  TYPE-directed, frequency-free; the in-context type DIRECTS composition; the s236-s240
  order signal is type, not L-to-R position; the VERBUM thesis holds at the behavioural
  level. CROSSOVER ~0 -> the v1/v2 effect was (partly) frequency; type does not direct
  composition in-context (at this scale) -> needs the causal-ablation register (v4).

CAVEATS (lambda measure): in-context type teaching tests CAPACITY to use a given type,
  not only the intrinsic system; the nonce appears in BOTH teach+test (repetition/
  induction — but the crossover subtracts it as a main effect); teaching templates may
  imperfectly fix the category; single model class. Nonce tokenization logged (sanity).

Usage:
    uv run python scripts/experiments/type_directed_v3_nonce.py --smoke   # 8B
    uv run python scripts/experiments/type_directed_v3_nonce.py           # 14B

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT / "scripts" / "experiments"))

from opcode_monitor_v2 import (  # noqa: E402
    _git_sha,
    _json_safe,
    _transformers_version,
    load_model_and_tokenizer,
)

RESULTS_DIR = _ROOT / "results" / "type-directed"

# nonce words (no real-word meaning; pronounceable) — tokenization logged at runtime
NONCE = ["wug", "blicket", "dax", "fep", "gorp", "zorp", "fendle", "glorp",
         "narp", "trisk", "florp", "queel", "vimp", "dorf", "snarl", "plong"]

# TEACH templates ({w}=lowercase, {W}=capitalised). No "the {w}"/"a {w}" -> no det leak.
NOUN_TEACH = ["{W}s are common objects.", "He collected several {w}s.",
              "Those {w}s are nice.", "Many {w}s were there."]
VERB_TEACH = ["They often {w}.", "We like to {w}.", "You should {w} now.",
              "Children love to {w}."]
# TEST fillers (sentence-initial): determiners (want a NOUN) vs names (want a PRED)
DET_FILL = ["The", "This", "That", "Each", "Every", "Some"]
NAME_FILL = ["John", "Mary", "Sarah", "David", "Peter", "Susan"]


def build_text(teach_tpl: str, w: str, filler: str) -> tuple[str, int]:
    """Return (full_text, char_start_of_target). full = '{teach}. {filler} {w}'."""
    teach = teach_tpl.format(w=w, W=w.capitalize())
    prefix = f"{teach} {filler} "
    return prefix + w, len(prefix)


def gen_items(n_each: int, seed: int):
    rng = np.random.default_rng(seed)
    items = []

    def pick(pool, k):
        idx = rng.choice(len(pool), size=min(k, len(pool)), replace=False)
        return [pool[i] for i in idx]

    for w in NONCE:
        for typ, teaches in (("noun", NOUN_TEACH), ("verb", VERB_TEACH)):
            for teach in teaches:
                for frame, fills in (("det", DET_FILL), ("name", NAME_FILL)):
                    for filler in pick(fills, n_each):
                        items.append({"w": w, "type": typ, "frame": frame,
                                      "teach": teach, "filler": filler,
                                      "cond": f"{frame}_{typ}"})
    rng.shuffle(items)
    return items


def score_item(item, model, tok, torch_mod):
    text, c0 = build_text(item["teach"], item["w"], item["filler"])
    c1 = len(text)
    enc = tok(text, return_tensors="pt", return_offsets_mapping=True)
    dev = next(model.parameters()).device
    ids = enc["input_ids"][0]
    offsets = enc["offset_mapping"][0].tolist()
    import torch.nn.functional as func
    with torch_mod.no_grad():
        logits = model(input_ids=ids.unsqueeze(0).to(dev),

[CONTENT TRUNCATED] Showing lines 1 to 120 of 255 total lines. Use line_offset=120 parameter to read more content.
```

### Thinking

Now I'm designing the smoke wrapper for the 4B model. I need to extract band axes using the type lattice geometry machinery on the 4B model with the labeled data and probing dataset, but there's a critical issue: the axes were extracted in standardized space using per-dimension z-scores, while ablating in the residual stream requires directions in raw residual space—this scaling mismatch is important to account for.

To handle this, I'm computing centroids in standardized space and getting SVD axes there, then converting back to raw-space directions by scaling by the standard deviation per dimension. The ablation hook will compute the coefficient as the dot product of the normalized residual with the axis direction, then subtract that scaled component from the residual to remove the axis direction's influence. The first step is running the lattice geometry analysis on the 4B model to identify the band structure and confirm the low-rank property, since that's only been done on 0.6B and 32B so far. Once I have the per-layer axes in the band, I need to identify which axes correspond to binding versus composition by their loading patterns rather than relying on index order, since the axis arrangement likely differs across model sizes. For the binding task, I'm designing a quantifier-based readout similar to the v3 surprisal approach—teaching nonce words as nouns, then testing frames with quantifiers like "Every," "Some," "No," and "Most" to measure determiner licensing and composition selectivity.

For composition, I'm considering a parallel modifier-licensing task using frames like "The very {w}" or adjective/adverb contexts to test whether the model learns to license modifiers based on the taught word class.

I'm settling on a symmetric design across both tasks: each one uses two teaching conditions (noun vs. verb for binding; adjective vs. noun for composition) crossed with two test frames to create a crossover pattern. For binding, quantifiers like "Every/Some/No/Most" should license nouns while proper names license verbs in predicate position.

For the composition task, I'm using intensifiers like "very/quite/rather" to license adjectives in frames like "The dogs seem {w}" or "It looked {w} to me," while keeping the verb teaching separate. The crossover effect measures how much the intensifier frame boosts adjectives compared to names, minus the baseline difference between those frames. But I'm running into an issue—both tasks share predicate control, so I need to think through how that overlap affects the design.

Now I'm testing the ablation strategy: removing the quantifier/determiner axis degrades the quantifier crossover while leaving the modifier crossover intact, and vice versa. Random matched-norm baselines show neither effect, confirming the axes are doing real work. The key intervention is projecting each band axis out of the residual stream across all token positions and layers—a strong, whole-sequence ablation that should cleanly isolate what each axis contributes.

For the computational cost, I'm looking at roughly 5 passes over the full item set (baseline plus four ablation conditions) across both tasks and the control task. With a smaller smoke test—around 10 nonces, 2 teaching examples, 2 frames each, and 2 fillers per task—that comes to about 1700 forward passes on a 4B model with short prompts, which is manageable.

On an MPS device (Mac), each forward pass takes 50-100ms for short sequences, so a few minutes per pass is acceptable. The 4B model should run fine on MPS like the 32B did. I need to check what device the operand_multihop3 wrapper used, but MPS is the right choice here.

For the script structure, I'm putting this in wrapper/type_zone_ablation.py, reusing the type_lattice_geometry axis extraction and v3-style surprisal readouts. The script will load the model first... Once I identify the band of layers showing significant p-values (expecting something like L5–L25 for the 4B model), I'll extract the binding, composition, and entity axes from the loadings within that band. For the entity-axis control, I'm using the direction from the entity centroid toward the grand mean in standardized space—a small, near-origin direction that I'll normalize to a unit vector. Then I'll set up the behavioral tasks and run five passes with hooks that apply oblique projections using the derived singular vectors, plus a random control using a random unit vector in the same standardized space.

For the verdict, I'm computing crossover points per task and condition, then calculating retention ratios as the ratio of each condition's crossover to the baseline. The dissociation criteria are strict: binding-axis ablation should degrade quantitative reasoning below 0.5 while preserving modifier effects above 0.7, composition-axis ablation should show the opposite pattern, random ablation should preserve both above 0.7, entity-axis should also preserve both above 0.7, and the recall control should show a surprisal increase below some threshold.

The smoke test validates that baseline crossovers are significantly above zero at 4B for both tasks before interpreting any ablations—if 4B shows null crossovers, that signals the model is too small and I should stick with the 32B pre-registration. I'm noting that 4B differs from the pre-registered 32B host, so the band and axis resolution on 4B may be less clear than what we'd see at larger scales, and I'll report these findings as-is.

Now I need to examine the probe_type_qwen3_32b.py interfaces to understand how the probing dataset is built—specifically which token positions are captured, how hidden states are indexed, and where the decoder layer modules live for hooking. I'm also checking the load_model function to see how dtype and device are handled. My next steps are to read through that file to capture the full interface, then build out the wrapper and ablation logic.

For testing, I'll start with a quick smoke run on the 4B model using a small sample size first to verify the plumbing works before scaling up.

### Thinking

I need to handle a standardized-space projection issue for the zone ablation—applying the formula `h' = h − ((h−μ)/σ · v) (σ⊙v)` with per-layer statistics to avoid ablating rogue dimensions. I'm also running a smoke test at 4B (not the pre-reg's 32B host) to verify baseline crossovers are real before interpreting any ablation results, since it's unclear whether 4B will resolve separate binding/composition axes like larger models might.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_type_qwen3_32b.py",
  "limit": 160
}
```

**Summary:** Reading probe_type_qwen3_32b.py (0-160)

**Output:**
```
#!/usr/bin/env python3
"""Type probe — Montague semantic types in Qwen3-32B.

Does Qwen3-32B encode Montague semantic types? At which layer do types
become linearly decodable?  Pythia-160M showed 84% in embeddings, 93%
at L0, then flat.  A 32B model with a fully-formed lambda compiler may
show a richer story: refined type geometry at deeper layers, or
type-differentiation that the small model lacked.

Method:
  1. Labeled dataset: word → simplified Montague type (8 categories)
  2. Forward pass through Qwen3-32B, capture residual stream at every layer
  3. Linear probe (logistic regression) per layer — 5-fold CV
  4. Where does type information become/remain decodable?

Architecture: Qwen3-32B — 64 layers, 64 heads, GQA(8 KV), d=5120, bf16.

Usage:
    uv run python scripts/explore/probe_type_qwen3_32b.py
    uv run python scripts/explore/probe_type_qwen3_32b.py --layer-stride 2  # every other layer
    uv run python scripts/explore/probe_type_qwen3_32b.py --quick  # fewer sentences

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder

MODEL = "Qwen/Qwen3-32B"

RESULTS_DIR = Path("results/type-probe-qwen3-32b")

# ══════════════════════════════════════════════════════════════════════
# Semantic Type Labels (simplified Montague)
# ══════════════════════════════════════════════════════════════════════
#
# Full Montague types are recursive but for a linear probe we need
# flat categories that capture the major type distinctions:
#
#   ENTITY     e              proper nouns, bare nouns as constants
#   PRED       <e,t>          intransitive verbs, predicate adjectives
#   REL        <e,<e,t>>      transitive verbs
#   QUANT      <<e,t>,t>      quantifier words (every, some, no, most)
#   DET        <e,t>→e        determiners (the, a, an)
#   CONN       t→t→t          connectives (and, or, if, not, because)
#   MOD        <e,t>→<e,t>    adjectives, adverbs (predicate modifiers)
#   FUNC       (structural)   punctuation, particles, auxiliaries

LABELED_DATA = [
    # ── Simple predication (intransitive) ─────────────────────
    ("The dog runs.", [
        ("The", "DET"), ("dog", "ENTITY"), ("runs", "PRED"), (".", "FUNC"),
    ]),
    ("The bird flies.", [
        ("The", "DET"), ("bird", "ENTITY"), ("flies", "PRED"), (".", "FUNC"),
    ]),
    ("The cat sleeps.", [
        ("The", "DET"), ("cat", "ENTITY"), ("sleeps", "PRED"), (".", "FUNC"),
    ]),
    ("The teacher laughs.", [
        ("The", "DET"), ("teacher", "ENTITY"), ("laughs", "PRED"), (".", "FUNC"),
    ]),
    ("The fish swims.", [
        ("The", "DET"), ("fish", "ENTITY"), ("swims", "PRED"), (".", "FUNC"),
    ]),
    ("The farmer walks.", [
        ("The", "DET"), ("farmer", "ENTITY"), ("walks", "PRED"), (".", "FUNC"),
    ]),
    ("The singer dances.", [
        ("The", "DET"), ("singer", "ENTITY"), ("dances", "PRED"), (".", "FUNC"),
    ]),
    ("The child cries.", [
        ("The", "DET"), ("child", "ENTITY"), ("cries", "PRED"), (".", "FUNC"),
    ]),
    ("The engine roars.", [
        ("The", "DET"), ("engine", "ENTITY"), ("roars", "PRED"), (".", "FUNC"),
    ]),
    ("The river flows.", [
        ("The", "DET"), ("river", "ENTITY"), ("flows", "PRED"), (".", "FUNC"),
    ]),

    # ── Proper nouns ──────────────────────────────────────────
    ("Alice runs.", [
        ("Alice", "ENTITY"), ("runs", "PRED"), (".", "FUNC"),
    ]),
    ("Bob sleeps.", [
        ("Bob", "ENTITY"), ("sleeps", "PRED"), (".", "FUNC"),
    ]),
    ("Tom walks.", [
        ("Tom", "ENTITY"), ("walks", "PRED"), (".", "FUNC"),
    ]),
    ("Mary sings.", [
        ("Mary", "ENTITY"), ("sings", "PRED"), (".", "FUNC"),
    ]),
    ("John laughs.", [
        ("John", "ENTITY"), ("laughs", "PRED"), (".", "FUNC"),
    ]),
    ("Sarah dances.", [
        ("Sarah", "ENTITY"), ("dances", "PRED"), (".", "FUNC"),
    ]),

    # ── Transitive ────────────────────────────────────────────
    ("Alice loves Bob.", [
        ("Alice", "ENTITY"), ("loves", "REL"), ("Bob", "ENTITY"), (".", "FUNC"),
    ]),
    ("The dog sees the cat.", [
        ("The", "DET"), ("dog", "ENTITY"), ("sees", "REL"),
        ("the", "DET"), ("cat", "ENTITY"), (".", "FUNC"),
    ]),
    ("Tom helps Mary.", [
        ("Tom", "ENTITY"), ("helps", "REL"), ("Mary", "ENTITY"), (".", "FUNC"),
    ]),
    ("The teacher reads the book.", [
        ("The", "DET"), ("teacher", "ENTITY"), ("reads", "REL"),
        ("the", "DET"), ("book", "ENTITY"), (".", "FUNC"),
    ]),
    ("The farmer finds the bird.", [
        ("The", "DET"), ("farmer", "ENTITY"), ("finds", "REL"),
        ("the", "DET"), ("bird", "ENTITY"), (".", "FUNC"),
    ]),
    ("Alice watches Bob.", [
        ("Alice", "ENTITY"), ("watches", "REL"), ("Bob", "ENTITY"), (".", "FUNC"),
    ]),
    ("Sarah chases Tom.", [
        ("Sarah", "ENTITY"), ("chases", "REL"), ("Tom", "ENTITY"), (".", "FUNC"),
    ]),
    ("The child hugs the dog.", [
        ("The", "DET"), ("child", "ENTITY"), ("hugs", "REL"),
        ("the", "DET"), ("dog", "ENTITY"), (".", "FUNC"),
    ]),
    ("John knows Mary.", [
        ("John", "ENTITY"), ("knows", "REL"), ("Mary", "ENTITY"), (".", "FUNC"),
    ]),
    ("The cat catches the bird.", [
        ("The", "DET"), ("cat", "ENTITY"), ("catches", "REL"),
        ("the", "DET"), ("bird", "ENTITY"), (".", "FUNC"),
    ]),

    # ── Quantified ────────────────────────────────────────────
    ("Every dog runs.", [
        ("Every", "QUANT"), ("dog", "ENTITY"), ("runs", "PRED"), (".", "FUNC"),
    ]),
    ("Some cat sleeps.", [
        ("Some", "QUANT"), ("cat", "ENTITY"), ("sleeps", "PRED"), (".", "FUNC"),
    ]),
    ("No bird flies.", [

[CONTENT TRUNCATED] Showing lines 1 to 160 of 774 total lines. Use line_offset=160 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/wrapper/operand_multihop3.py",
  "limit": 90
}
```

**Summary:** Reading operand_multihop3.py (0-90)

**Output:**
```
"""(3-hop capacity) chained h(f(g(X))) over ONE installed operand — depth-as-fuel.

Pre-reg: mementum/knowledge/explore/three-hop-capacity-prereg.md (APPROVED s282,
geography chain FROZEN). Successor to the 2-hop wrapper/operand_multihop.py (s279).

Chain (geography): landmark --g--> city --f--> country --h--> continent.
  X = a nonce carrying a LANDMARK's content d_E (built like the 2-hop d_E, last-token
  capture of a multi-token phrase). Two UNSTATED bridges (city, country) never appear in
  the readout prompt. Final readout = closed 3-way continent {Europe, Asia, Africa}.

Framing (s280 depth-budget): this is a CAPACITY experiment, not a capability rung. A
full-chain failure counts as DEPTH-limited ONLY IF the pieces work on the same model
(Gate-2 sub-chain controls). Pre-registered predictions: Qwen3-4B -> FAIL-BY-CAPACITY
(controls pass, full chain fails); Qwen3-32B -> PASS (full + mediation). The double
dissociation across scale, pieces held constant, is the strongest C8 evidence available.

Gates (frozen in the pre-reg):
  Gate 1  FULL CHAIN    : install landmark, "The {nonce} ... continent of __"
                          -> continent; nulls = random install, baseline, content-spec.
  Gate 2  SUB-CHAINS    : (the capacity discriminator)
            S1 links     : landmark->city, city->country, country->continent at ceiling.
            2-hop g.f    : install landmark -> its COUNTRY.
            2-hop f.h    : install CITY -> its CONTINENT (the s279-style 2-hop).
  Gate 3  MEDIATION     : (only where Gate-1 passes)
            3a depth-order : logit-lens peaks ordered city < country < continent.
            3b country-swap: late country-axis swap flips continent (random does not).
            3c city-swap   : mid city-axis swap flips country+continent (random not).

`λ measure`: operand = VALUE (d_E, centroids); g,f,h = ROUTING; readout = logits;
bridges localized by DEPTH (3a) + zone-steer (3b/3c), never single-head (0/128 heads).
`λ yardstick`: nulls beside every number; real-word ceiling gates each cell; predict
a-priori, gate on nulls, no forced fit. A RUNG (capacity mapping), hook-not-weight.
Architecture-robust via resolve_parts (dense Qwen3 4B/32B; hybrid 27B follow-on).

License: MIT (`λ provenance`; SuperBake method-reference only).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# ── geography ladder: landmark -> (city, country, continent). Balanced 3-way. ──────
# Multi-token landmarks/cities handled by last-token capture (d_E) and first-token
# grading (closed candidate sets). Obscure cells are pruned by the real-word ceiling.
LANDMARKS: dict[str, tuple[str, str, str]] = {
    # Europe
    "Colosseum":      ("Rome",         "Italy",        "Europe"),
    "Louvre":         ("Paris",        "France",       "Europe"),
    "Parthenon":      ("Athens",       "Greece",       "Europe"),
    "Kremlin":        ("Moscow",       "Russia",       "Europe"),
    "Sagrada Familia":("Barcelona",    "Spain",        "Europe"),
    "Brandenburg Gate":("Berlin",      "Germany",      "Europe"),
    # Asia
    "Taj Mahal":      ("Agra",         "India",        "Asia"),
    "Kaaba":          ("Mecca",        "Saudi Arabia", "Asia"),
    "Petronas Towers":("Kuala Lumpur", "Malaysia",     "Asia"),
    "Angkor Wat":     ("Siem Reap",    "Cambodia",     "Asia"),
    "Tiananmen":      ("Beijing",      "China",        "Asia"),
    "Burj Khalifa":   ("Dubai",        "UAE",          "Asia"),
    # Africa
    "Pyramids":       ("Giza",         "Egypt",        "Africa"),
    "Sphinx":         ("Giza",         "Egypt",        "Africa"),
    "Karnak":         ("Luxor",        "Egypt",        "Africa"),
    "Table Mountain": ("Cape Town",    "South Africa", "Africa"),
    "Medina":         ("Marrakech",    "Morocco",      "Africa"),
    "Victoria Falls": ("Livingstone",  "Zambia",       "Africa"),
}

CONTINENTS = ["Europe", "Asia", "Africa"]
LM_LIST = list(LANDMARKS)
CITY_OF = {lm: v[0] for lm, v in LANDMARKS.items()}
COUNTRY_OF = {lm: v[1] for lm, v in LANDMARKS.items()}
CONT_OF = {lm: v[2] for lm, v in LANDMARKS.items()}
CITIES = sorted(set(CITY_OF.values()))
COUNTRIES = sorted(set(COUNTRY_OF.values()))
# city -> country/continent (deterministic; Giza collision is consistent)
CITY_COUNTRY = {v[0]: v[1] for v in LANDMARKS.values()}
CITY_CONT = {v[0]: v[2] for v in LANDMARKS.values()}
COUNTRY_CONT = {v[1]: v[2] for v in LANDMARKS.values()}
NONCE = "zorp"

# held-out exemplars (disjoint from the test landmarks/cities/countries)
CONT_PREFIX = (
    "The Alhambra is located on the continent of Europe.\n"

[CONTENT TRUNCATED] Showing lines 1 to 90 of 501 total lines. Use line_offset=90 parameter to read more content.
```

### Thinking

I need to find the function signatures for `load_model` and `build_probing_dataset` from the probe_type_qwen3_32b.py file.

## Assistant

Now the exact capture function signatures:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n \"def load_model\\|def build_probing_dataset\\|return \" scripts/explore/probe_type_qwen3_32b.py | head; echo ---; sed -n \"$(grep -n 'def load_model' scripts/explore/probe_type_qwen3_32b.py | cut -d: -f1),+40p\" scripts/explore/probe_type_qwen3_32b.py; echo ---; sed -n \"$(grep -n 'def build_probing_dataset' scripts/explore/probe_type_qwen3_32b.py | cut -d: -f1),+60p\" scripts/explore/probe_type_qwen3_32b.py",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ grep -n "def load_model\|def build_...

**Output:**
```
Exit code: 0
Stdout:
287:def load_model(model_name: str, device: str = "mps"):
317:    return model, tokenizer, config
328:        return model.model.layers
331:        return model.gpt_neox.layers
339:        return model.model.embed_tokens  # Qwen3, Llama, Mistral
341:        return model.gpt_neox.embed_in  # GPTNeoX
342:    return None
390:            return hook_fn
407:    return residuals, token_ids
469:    return aligned
---
def load_model(model_name: str, device: str = "mps"):
    """Load Qwen3-32B in bf16 with eager attention (for hook compatibility)."""
    from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig

    banner(f"Loading {model_name}")
    t0 = time.time()

    config = AutoConfig.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map=device,
        attn_implementation="eager",
    )
    model.eval()

    dt = time.time() - t0
    n_layers = config.num_hidden_layers
    d_model = config.hidden_size
    n_heads = config.num_attention_heads
    n_kv = getattr(config, "num_key_value_heads", n_heads)

    print(f"  Loaded in {dt:.1f}s", file=sys.stderr)
    print(f"  Layers: {n_layers}  Heads: {n_heads}  KV heads: {n_kv}  d_model: {d_model}",
          file=sys.stderr, flush=True)

    return model, tokenizer, config


# ══════════════════════════════════════════════════════════════════════
# Residual stream capture
# ══════════════════════════════════════════════════════════════════════

def get_transformer_layers(model):
    """Get the list of transformer layers from any HF model."""
    # Qwen3 structure: model.model.layers
    if hasattr(model, "model") and hasattr(model.model, "layers"):
---
def build_probing_dataset(
    model, tokenizer,
    layer_indices: list[int],
    labeled_data: list,
    verbose: bool = True,
) -> tuple[dict[int, tuple[np.ndarray, np.ndarray]], int, int]:
    """Build (residual_vector, type_label) pairs at specified layers.

    Returns:
        data_by_layer: {layer_idx: (X, y)} where X is (N, d_model), y is (N,)
        n_labeled: total labeled tokens
        n_skipped: sentences where alignment failed
    """
    data_by_layer: dict[int, tuple[list, list]] = {L: ([], []) for L in layer_indices}

    n_labeled = 0
    n_skipped = 0

    for sent_idx, (sent, word_labels) in enumerate(labeled_data):
        if verbose and sent_idx % 10 == 0:
            print(f"    sentence {sent_idx+1}/{len(labeled_data)}: {sent[:40]}...",
                  file=sys.stderr, flush=True)

        residuals, token_ids = capture_residuals(model, tokenizer, sent, layer_indices)
        aligned = align_tokens_to_labels(tokenizer, token_ids, word_labels)

        if not aligned:
            n_skipped += 1
            continue

        for tok_idx, word_type in aligned:
            for L in layer_indices:
                if L in residuals and tok_idx < residuals[L].shape[0]:
                    data_by_layer[L][0].append(residuals[L][tok_idx])
                    data_by_layer[L][1].append(word_type)
            n_labeled += 1

        # Free memory
        del residuals
        gc.collect()

    # Convert to numpy
    result = {}
    for L in layer_indices:
        X_list, y_list = data_by_layer[L]
        if X_list:
            result[L] = (np.array(X_list), np.array(y_list))

    return result, n_labeled, n_skipped


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Type probe for Qwen3-32B")
    parser.add_argument("--model", default=MODEL, help="HuggingFace model name")
    parser.add_argument("--device", default="mps", help="Device (mps, cuda, cpu)")
    parser.add_argument("--layer-stride", type=int, default=1,
                        help="Sample every N-th layer (default: every layer)")
```

### Thinking

I'm checking the layer indexing convention where `layer_indices` includes -1 for the embedding layer, and verifying that the capture_residuals hook stores the output of each decoder layer at the corresponding index so that residuals[L] contains the output from layer L.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sed -n '344,410p' scripts/explore/probe_type_qwen3_32b.py",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ sed -n '344,410p' scripts/explore/p...

**Output:**
```
Exit code: 0
Stdout:
def capture_residuals(
    model, tokenizer, text: str,
    layer_indices: list[int] | None = None,
) -> tuple[dict[int, np.ndarray], list[int]]:
    """Capture residual stream at specified layers.

    Returns:
        residuals: {layer_idx: np.array (seq_len, d_model)}
                   layer_idx=-1 is embedding output (before any transformer layer)
        token_ids: list of token IDs
    """
    layers = get_transformer_layers(model)
    n_layers = len(layers)

    if layer_indices is None:
        layer_indices = list(range(n_layers))

    layer_set = set(layer_indices)
    residuals: dict[int, np.ndarray] = {}
    hooks = []

    # Hook embedding output (layer -1)
    embed_mod = get_embed_module(model)
    if embed_mod is not None and -1 in layer_set:
        def embed_hook(module, args, output):
            if isinstance(output, tuple):
                h = output[0]
            else:
                h = output
            residuals[-1] = h[0].detach().cpu().float().numpy()
        hooks.append(embed_mod.register_forward_hook(embed_hook))

    # Hook transformer layers
    for idx in layer_indices:
        if idx < 0:
            continue

        def make_hook(layer_idx):
            def hook_fn(module, args, output):
                # output is typically (hidden_states, ...) or just hidden_states
                if isinstance(output, tuple):
                    h = output[0]
                else:
                    h = output
                residuals[layer_idx] = h[0].detach().cpu().float().numpy()
            return hook_fn

        hooks.append(layers[idx].register_forward_hook(make_hook(idx)))

    try:
        inputs = tokenizer(text, return_tensors="pt")
        # Move to model's device
        device = next(model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        token_ids = inputs["input_ids"][0].tolist()

        with torch.no_grad():
            model(**inputs, output_attentions=False)
    finally:
        for h in hooks:
            h.remove()

    return residuals, token_ids


# ══════════════════════════════════════════════════════════════════════
```

### Thinking

I've confirmed that the residual outputs align with the layer indices in my hook setup. Now I'm designing the wrapper to identify significant layers by computing per-layer p-values against a shuffled-label baseline, then finding maximal contiguous bands where p < 0.05.

For band selection, I'm taking all layers that pass the significance threshold and finding the longest contiguous run; if it's shorter than 3 layers, I fall back to the interior range [0.15, 0.65] and pick the minimum p-value layer plus/minus 2 neighbors. The capture stride is 1 across all 36 layers, so I'm hooking 37 outputs total—manageable memory-wise, though the per-sentence garbage collection in the dataset builder adds some overhead.

For axis identification within each band layer, I'm standardizing the data, computing centroids per grammatical type, and running centered SVD to extract loadings and directions. Then I'm scoring each axis by binding strength (quantifier + determiner loadings squared) and modification strength (modifier loadings squared), selecting the top binding axis and a separate top modification axis from the remaining candidates. The entity axis is derived from the entity centroid direction in standardized space, normalized to unit length as a control.

I'm logging the chosen axis indices and their scores per layer, plus the expected norm of random unit vectors in standardized space to ensure the ablation baseline is honest. The ablation hook itself standardizes the hidden state, projects onto the chosen direction, and subtracts that component back out—all computed in float32 then cast to the model's bf16 dtype. For the behavioral tasks, I'm reusing the quantifier-licensing setup from before, with frames pairing quantifier fillers against name fillers.

I'm clarifying that v3's determiner frame already mixed determiners and quantifiers together, so for this version I'll keep the quantifier set clean—"Every," "Each," "Some," "No," "Most," "All"—which map directly to the QUANT loading on axis 0. Now I need to define the modifier-licensing task, which requires picking two teaching types and two frames where one licenses the modifier and the other doesn't. ames like "It was very {w}" work as sentence-initial test frames, where the filler can be multi-word phrases like "It seemed very" or "The dog was quite". For the MOD task, I'm designing the teaching examples to use adjectives in varied sentence structures—"Those dogs are {w}", "The house seemed {w}", "Everything felt {w} today"—while being careful to avoid quantifier leakage from words like "Every" and keeping intensifiers out of the teaching set so they don't contaminate the test frame.

Now I'm setting up the verb teaching examples and working through the frame fillers: MOD fillers like "It was very", "The dog seemed quite", "That movie was rather", "She felt extremely" license adjectives, while NAME fillers like "John", "Mary", "Sarah", "David" license verbs. The crossover penalty calculation compares how well the model scores mod-frames with verb-taught versus adj-taught words, and similarly for name-frames, to measure the penalty difference.

But I'm realizing the frozen prediction axis ablation is more subtle — axis2 breaks MOD-composition specifically, not QUANT. The MOD-composition readout is the crossover_mod value, which includes both the intensifier-licensing arm and a shared name arm from predication. If axis0 ablation affects predication (which the theory suggests is argument saturation), it could degrade both crossovers through that shared name pathway, making the effect look non-selective. So instead of using full crossovers as readouts, I should use the frame-specific penalties directly — QUANT readout would be quant_pen, and so on.

The challenge is that penalties alone lose the main-effect subtraction that the crossover design provides. The pen differences across teaching conditions are within-frame and paired by nonce, which should subtract out frame main effects while preserving teaching effects. But under ablation, if the ablation weakens verb-teaching globally, both penalties would shift together.

I'm reconsidering whether to keep crossovers but make both arms class-specific per task instead of sharing the PRED arm. The issue is that tasks like BIND don't have distinct frames on the same axis. A better approach might be a within-task crossover between the two class frames—teaching noun versus adjective with quantifier-filler licensing nouns and intensifier-filler licensing adjectives. This single crossover would span both classes, so ablating either axis degrades it, but it's still not a true dissociation readout.

I need to think through what a real dissociation actually requires. ats predication as spared. The readout should include per-arm pen measurements alongside crossover significance checks, since the pre-registered prediction specifically compares how axis0-ablation degrades QUANT/DET composition relative to both its own predicate/MOD effect and random baseline — meaning I need to track pen degradation within each ablation condition across frames, accounting for the fact that teaching main effects will shift both frames equally.

Since teaching main effects add a constant to every frame's pen calculation, differences between pens across frames naturally cancel those effects out, making within-task frame contrasts clean. However, BIND and MOD tasks use different teaching pairs (noun/verb versus adj/verb), so cross-task pen comparisons carry different main effects — I need to keep comparisons within task to avoid contamination, and the verdict should focus on whether axis0-ablation degrades QUANT-pen more than its own MOD-pen.

Retention ratios (ablated over baseline) normalize each readout to its own baseline, but they still include the main-effect constant in the ratio. The cleanest defensible approach is to define class effects as within-task crossovers restricted to that class frame minus its own name arm — the standard crossover — and accept that the shared PRED arm might carry some effect. I'll report per-arm pens so we can see where changes actually occur, and note this measurement choice in the code header.

Actually, it's cleaner to have both tasks share the same teach pair, varying noun versus adjective across the quantifier and modifier frames: quantifier prefers noun-taught inputs while the intensifier frame prefers adjective-taught inputs, and I can compute the dissociation as a clean 2×2 design without needing a separate PRED arm at all.

Now I'm realizing the teach main effect contaminates each penalty individually—adding a cost to quant_pen and subtracting it from mod_pen—but when I sum them for the crossover measure, that main effect cancels out. The problem is that ablation-induced changes in the teach cost confound the individual penalty estimates.

I'm considering a cleaner three-arm design instead: one teach manipulation (noun vs adjective), three frames (quantifier, modifier, and a name-control baseline), where I report the crossover binding measure, per-frame penalties with their paired statistics, and a selectivity metric that tries to isolate the ablation effect. But the selectivity approach—taking the difference between quantifier and modifier penalty changes—doesn't actually cancel the teach main effect; ablation-induced shifts in teaching cost just get amplified as 2δm in that difference.

So I'm reframing with a consistent preference metric: for each frame, preference equals the cost difference when adjectives are taught minus when nouns are taught, where positive values mean noun-teaching is cheaper. The teach main effect adds a constant across all frames, but I can use the name frame as a shared reference point—since it's relatively neutral for both noun and adjective mismatches—to subtract out that constant exactly. This gives me clean class-specific licensing effects: quantifier licensing as the preference gap between quantifier and name frames, and modifier licensing as the preference gap between name and modifier frames.

These are paired differences of differences, essentially crossover interactions, so they're main-effect-free and directly comparable. My predictions under frozen adaptation are that quantifier licensing retention should drop below 0.5 on the bind-axis ablation but exceed 0.7 on the comp-axis ablation, while modifier licensing shows the opposite pattern.

For the recall control, I'm checking that the mean surprisal of the gold token doesn't increase by more than 20% across any ablation. I'm also refining the teaching templates to remove quantifier-like language—swapping out "Many" for "two" to keep the noun and adjective teaching sets clean and comparable.

Now I'm setting up the filler frames that come after the teaching sentence. For quantifier fillers, I'm using words like "Every," "Each," "Some," "No," "Most," and "All" to test how the model handles these in context. For modifier fillers, I'm using intensifier phrases like "It was very," "seemed quite," "rather," and "extremely" to probe adjective understanding. I'm also preparing a list of common names as potential fillers.

For the control items, I'm using straightforward factual cloze prompts to measure the surprisal of the correct answer token — things like "The capital of France is Paris." The experimental structure involves running passes across five conditions: baseline, bind_axis, comp_axis, random, and e_axis, with hooks installed at different layers to track how axis information flows through the model.

For each layer, I'm logging which binding and composition axes were selected, along with their respective scores and variance fractions. If there's ambiguity at a layer where the top candidates overlap, I'll pick the next-best option for the composition axis. The smoke test will run on the full labeled dataset — probably around 120 sentences across 4B parameters with 37 layers, which should take a few minutes with garbage collection between sentences. The item set multiplies out to 10 nonces across 2 teaching types, 2 templates, 3 frames, and 2 filler variations.

With 240 items and 5 conditions that's 1200 forward passes total; at roughly 0.15 seconds per pass on the 4B model, I'm looking at 20-30 minutes per run, which is acceptable — I can add a fast flag to reduce nonces and fillers if needed. I'll set the null band size to 100 and include metadata per run with the model, git SHA, timestamp, and seed. For layer indexing, I'm capturing residuals at each layer output and applying ablation hooks consistently across the band.

On the implementation side, I'm using bfloat16 with hooks computing in float32, and I'll adapt the nonce surprisal measurement from v3 — keeping the tokenization and offset approach self-contained rather than importing across directories, since the wrapper scripts follow that pattern.

I'm tracking a few risks: the MPS bfloat16 hooks are proven from earlier work, the probing dataset generation might be slow, and at 4B parameters the axis separation might not be as clean as at 0.6B, which could make the component axis selection noisy. The band might also be empty at p<0.05 with 100 null samples, so I'll fall back to interior min-p ± 3 layers.

Writing the script now... I need to write my own SVD function that returns the full decomposition including right singular vectors, then import the centroids and participation ratio utilities from the geometry module. For the band selection, I'm iterating through decoder layers with a stride of 1, and for the null distribution I'll compute participation ratios across 100 shuffles per layer.

Now I'm defining a function that standardizes the input data, computes centroids for each type, centers them, and performs SVD to extract the singular vectors and values. Then I'm building an axis selection function that scores the principal components based on how strongly the quantization and determinism types load onto each axis.

For the entity axis, I'm taking the centroid direction in standardized space and normalizing it. I'm also preparing to store ablation directions as pairs of the standardized vector and standard deviation per layer and condition, then setting up a hook function that will project activations along these directions.

Writing hook function... Adding more recall examples... I'm checking that the null distribution mean stays above 0.7 across random and axis conditions, verifying recall doesn't drift more than 20% from baseline across all ablations, and confirming the full dissociation pattern holds. The results get written to a JSON verdict and metadata file with a summary table, plus detailed logging of band information, per-layer axis selections, and removal norms. I'm running this with specific hyperparameters for the Qwen 3.5B model, with a smoke-test mode that reduces the null samples and filler count for faster iteration.

Now I need to track the labeled data count for runtime estimation, import the type ordering from the geometry module, and set up the paired-by-nonce structure so that each (feature, word) pair has both teaching conditions present with all combinations generated deterministically using the same fillers across cells for full crossing.

I'll compute cell values as the mean surprisal across teaching templates and fillers, then verify the quantifier sentences work—including "No" as a sentence-initial quantifier, which should be fine despite potential ambiguity. Multi-word fillers like "It was very" are acceptable, so I'm ready to write the file now.

## Assistant

Interfaces confirmed — `residuals[L]` = output of `model.model.layers[L]`, so ablation hooks on the same modules line up exactly with the capture space. Task 1 done; building the instrument.

### Thinking

I'm refining the experimental design: instead of two separate teach pairs that share a PRED arm, I'll use a single teach pair contrasting nouns and adjectives across three frames—quantifier, modifier, and name—where the name frame serves as the shared reference. This lets me calculate the preference difference between adjective-taught and noun-taught conditions for each frame, then measure how much the quantifier frame differs from the name baseline to determine if quantifiers license nouns.

### Thinking

I'm writing the instrument with a refined design: a single teach pair with three frames where both class readouts are crossover interactions against the same shared name-arm, allowing teach main-effects to cancel and making the two class effects directly comparable for a dissociation verdict.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/wrapper/type_zone_ablation.py",
  "content": "#!/usr/bin/env python3\n\"\"\"P-TYPE-1b — combinator-zone x type-class dissociation (zone x axis ablation).\n\nPre-reg: mementum/knowledge/explore/types-are-the-well-formedness-of-reduction.md\n(#p-type-1b, FROZEN s282). Host of record = Qwen3-32B; THIS FILE also runs the 4B\nSMOKE (instrument validation + capacity read; a 4B verdict does NOT close 1b).\n\nHYPOTHESIS (frozen): if type = which opcode's application is licensed, ablating a\nrole-specific type axis as a ZONE across the low-rank band selectively breaks the\nmatching type-class:\n  - binding axis (QUANT+DET loadings; S/binding role)  -> breaks quantifier licensing\n  - composition axis (MOD loadings; B/composition role) -> breaks modifier licensing\nDouble dissociation; nulls (random matched direction, e/ENTITY-origin direction,\nnon-compositional recall task) break neither. v4 (global direction, crossover\nretention) was correctly negative; this is zone x axis CLASS-selectivity.\n\nINSTRUMENT\n  1. Capture the labeled Montague-type dataset at every decoder layer (reuses\n     probe_type_qwen3_32b capture; residuals[L] = output of model.layers[L]).\n  2. Per layer: standardize (diagonal whiten - the 1a massive-activation lesson),\n     centroid SVD, PR + shuffled-label null. BAND = longest contiguous run of\n     layers with p_lowrank < 0.05 (fallback: interior min-p +/- 3).\n  3. Per band layer, pick axes BY LOADING PATTERN (not index - axis order may vary\n     across layers/scale): bind = argmax QUANT^2+DET^2 energy among top-3;\n     comp = argmax MOD^2 energy among remaining; e-dir = ENTITY centroid direction.\n  4. Zone ablation = at every band layer, every token position, remove the axis in\n     STANDARDIZED space: h' = h - (((h-mu)/sd) . v) (sd*v). This is the exact\n     projection in the space the axes live in (an oblique projection in raw space;\n     raw-space removal would target rogue massive-activation dims - lambda measure).\n\nBEHAVIOURAL READOUTS (v3-style nonce surprisal; frequency-free)\n  ONE teach pair (noun vs adj) x THREE frames, all fully crossed & paired by nonce:\n     teach noun: \"{W}s are common objects.\"     teach adj: \"The dogs are {w}.\"\n     frame quant: \"Every {w}\"    (QUANT licenses a NOUN)\n     frame mod:   \"It was very {w}\"  (intensifier licenses an ADJ)\n     frame name:  \"John {w}\"     (licenses a PRED; SHARED REFERENCE arm)\n  pref(f) = S(f|adj-taught) - S(f|noun-taught)   (per nonce)\n  Q_eff = pref(quant) - pref(name)   > 0 baseline   (quantifier-class licensing)\n  M_eff = pref(name)  - pref(mod)    > 0 baseline   (modifier-class licensing)\n  Both are crossover interactions against the SAME name arm -> the teach main\n  effect cancels IDENTICALLY in both -> Q_eff / M_eff are cross-comparable, which\n  is exactly what the dissociation verdict compares. Recall task = task control.\n\nVERDICT (pre-set margins, frozen here before the run; ret = effect/baseline):\n  GATE-0 (ceiling): baseline Q_eff and M_eff both mean>0 with t>=3 - else the host\n    cannot express the classes and NO ablation cell is interpreted (4B risk: 0.6B\n    resolved ~1 axis; a Gate-0/axis-resolution failure at 4B is itself the finding).\n  BIND-SELECTIVE: ret(Q,bind)<0.5 AND ret(M,bind)>0.7\n  COMP-SELECTIVE: ret(M,comp)<0.5 AND ret(Q,comp)>0.7\n  NULLS: random + e-axis keep BOTH rets>0.7 ; recall surprisal ratio<1.2 all conds\n  DISSOCIATION_SUPPORTED <=> gate0 & bind & comp & nulls. Anything less: verbatim.\n\nlambda measure: ablation target = value-register band axes; claim = reduction\nLICENSING -> readout is behavioural class-selectivity, never decodability change.\nA RUNG: hook-not-weight; zone-not-weights; one class pair, not the whole lattice.\n\nUsage:\n    uv run python wrapper/type_zone_ablation.py --model Qwen/Qwen3-4B --smoke\n    uv run python wrapper/type_zone_ablation.py --model Qwen/Qwen3-4B\n    uv run python wrapper/type_zone_ablation.py --model Qwen/Qwen3-32B   # verdict host\n\nLicense: MIT\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport subprocess\nimport sys\nfrom datetime import UTC, datetime\nfrom pathlib import Path\n\nimport numpy as np\nimport torch\n\n_ROOT = Path(__file__).resolve().parent.parent\nsys.path.insert(0, str(_ROOT / \"scripts\" / \"explore\"))\n\nfrom probe_type_qwen3_32b import (  # noqa: E402\n    LABELED_DATA,\n    build_probing_dataset,\n    get_transformer_layers,\n    load_model,\n)\nfrom type_lattice_geometry import (  # noqa: E402\n    TYPE_ORDER,\n    centroids,\n    participation_ratio,\n)\n\n# ── behavioural items ──────────────────────────────────────────────────────────\nNONCE = [\"wug\", \"blicket\", \"dax\", \"fep\", \"gorp\", \"zorp\",\n         \"fendle\", \"glorp\", \"narp\", \"trisk\"]\n\n# teach templates: NO quantifiers, NO intensifiers, NO test-frame leakage\nNOUN_TEACH = [\"{W}s are common objects.\", \"He collected several {w}s.\",\n              \"Those {w}s are nice.\", \"She bought two {w}s.\"]\nADJ_TEACH = [\"The dogs are {w}.\", \"His car looks {w}.\",\n             \"The food tasted {w}.\", \"That house seems {w}.\"]\n\nQUANT_FILL = [\"Every\", \"Each\", \"Some\", \"No\", \"Most\", \"All\"]\nMOD_FILL = [\"It was very\", \"The dog seemed quite\", \"That movie was rather\",\n            \"She felt extremely\", \"The room looked really\", \"His voice sounded so\"]\nNAME_FILL = [\"John\", \"Mary\", \"Sarah\", \"David\", \"Peter\", \"Susan\"]\n\n# non-compositional task control (lexical recall; gold graded as continuation)\nRECALL = [(\"The capital of France is\", \" Paris\"),\n          (\"The capital of Japan is\", \" Tokyo\"),\n          (\"The capital of Italy is\", \" Rome\"),\n          (\"Water is made of hydrogen and\", \" oxygen\"),\n          (\"The opposite of hot is\", \" cold\"),\n          (\"Two plus two equals\", \" four\"),\n          (\"The sun rises in the\", \" east\"),\n          (\"The color of snow is\", \" white\"),\n          (\"A week has seven\", \" days\"),\n          (\"The largest ocean is the\", \" Pacific\")]\n\nCONDS = [\"baseline\", \"bind_axis\", \"comp_axis\", \"random\", \"e_axis\"]\n\n\n# ── geometry: band + axes (standardized space) ─────────────────────────────────\ndef layer_geometry(x: np.ndarray, y: np.ndarray, rng, n_null: int) -> dict:\n    \"\"\"Standardize -> centroid SVD -> PR + shuffled-label null + axes.\"\"\"\n    mu = x.mean(axis=0)\n    sd = x.std(axis=0) + 1e-6\n    z = (x - mu) / sd\n\n    def pr_of(labels):\n        c, present = centroids(z, labels, TYPE_ORDER)\n        if len(present) < 3:\n            return float(\"nan\"), None, None, None\n        cc = c - c.mean(axis=0, keepdims=True)\n        u, s, vt = np.linalg.svd(cc, full_matrices=False)\n        return participation_ratio(s), present, (u, s, vt), c\n\n    pr_real, present, svd, c = pr_of(y)\n    null = []\n    for _ in range(n_null):\n        prn, _, _, _ = pr_of(rng.permutation(y))\n        if not np.isnan(prn):\n            null.append(prn)\n    null = np.array(null)\n    p = float(np.mean(null <= pr_real)) if null.size else None\n    return {\"mu\": mu, \"sd\": sd, \"present\": present, \"svd\": svd, \"centroids\": c,\n            \"pr_real\": float(pr_real), \"p_lowrank\": p,\n            \"pr_null_mean\": float(null.mean()) if null.size else None}\n\n\ndef pick_axes(geo: dict) -> dict | None:\n    \"\"\"Select bind/comp axes by loading pattern; e-dir from ENTITY centroid.\n    Returns unit directions in STANDARDIZED space + bookkeeping, or None.\"\"\"\n    if geo[\"svd\"] is None:\n        return None\n    present = geo[\"present\"]\n    idx = {t: i for i, t in enumerate(present)}\n    if not {\"QUANT\", \"DET\", \"MOD\", \"ENTITY\"} <= set(idx):\n        return None\n    u, s, vt = geo[\"svd\"]\n    k = min(3, len(s))\n    tot = (s ** 2).sum() + 1e-12\n    bind_scores = [u[idx[\"QUANT\"], i] ** 2 + u[idx[\"DET\"], i] ** 2 for i in range(k)]\n    bind_i = int(np.argmax(bind_scores))\n    mod_scores = [u[idx[\"MOD\"], i] ** 2 if i != bind_i else -1.0 for i in range(k)]\n    comp_i = int(np.argmax(mod_scores))\n\n    def unit(v):\n        return v / (np.linalg.norm(v) + 1e-12)\n\n    c = geo[\"centroids\"]\n    e_dir = unit(c[idx[\"ENTITY\"]] - c.mean(axis=0))\n    return {\"bind\": unit(vt[bind_i]), \"comp\": unit(vt[comp_i]), \"e\": e_dir,\n            \"bind_i\": bind_i, \"comp_i\": comp_i,\n            \"bind_var\": float(s[bind_i] ** 2 / tot),\n            \"comp_var\": float(s[comp_i] ** 2 / tot),\n            \"bind_score\": float(bind_scores[bind_i]),\n            \"comp_score\": float(max(mod_scores))}\n\n\ndef find_band(per_layer: dict[int, dict], n_layers: int) -> list[int]:\n    \"\"\"Longest contiguous run of layers with p_lowrank < 0.05; fallback interior.\"\"\"\n    sig = [L for L in sorted(per_layer) if (per_layer[L][\"p_lowrank\"] or 1.0) < 0.05]\n    best, cur = [], []\n    for L in sig:\n        cur = [*cur, L] if (cur and L == cur[-1] + 1) else [L]\n        if len(cur) > len(best):\n            best = cur\n    if len(best) >= 3:\n        return best\n    interior = [L for L in sorted(per_layer)\n                if n_layers * 0.15 <= L <= n_layers * 0.65]\n    if not interior:\n        return sig or sorted(per_layer)[:3]\n    lo = min(interior, key=lambda L: per_layer[L][\"p_lowrank\"] or 1.0)\n    return [L for L in sorted(per_layer) if lo - 3 <= L <= lo + 3]\n\n\n# ── zone ablation hook (exact projection in standardized space) ────────────────\ndef make_zone_hook(mu: np.ndarray, sd: np.ndarray, v: np.ndarray):\n    \"\"\"h' = h - (((h-mu)/sd) . v) * (sd*v)  at ALL positions (fp32, cast back).\"\"\"\n    box: dict = {}\n\n    def hook(_module, _inp, out):\n        h = out[0] if isinstance(out, tuple) else out\n        if not box:\n            box[\"mu\"] = torch.as_tensor(mu, dtype=torch.float32, device=h.device)\n            box[\"sd\"] = torch.as_tensor(sd, dtype=torch.float32, device=h.device)\n            box[\"v\"] = torch.as_tensor(v, dtype=torch.float32, device=h.device)\n            box[\"w\"] = box[\"sd\"] * box[\"v\"]\n        hf = h.float()\n        coeff = ((hf - box[\"mu\"]) / box[\"sd\"]) @ box[\"v\"]        # [B,T]\n        hf = hf - coeff.unsqueeze(-1) * box[\"w\"]\n        h2 = hf.to(h.dtype)\n        return (h2, *out[1:]) if isinstance(out, tuple) else h2\n\n    return hook\n\n\n# ── surprisal scoring ──────────────────────────────────────────────────────────\ndef gen_items(n_nonce: int, n_teach: int, n_fill: int) -> list[dict]:\n    \"\"\"Fully crossed (deterministic -> exact pairing by nonce).\"\"\"\n    items = []\n    for w in NONCE[:n_nonce]:\n        for ttype, teaches in ((\"noun\", NOUN_TEACH), (\"adj\", ADJ_TEACH)):\n            for teach in teaches[:n_teach]:\n                for frame, fills in ((\"quant\", QUANT_FILL), (\"mod\", MOD_FILL),\n                                     (\"name\", NAME_FILL)):\n                    for filler in fills[:n_fill]:\n                        items.append({\"kind\": \"typed\", \"w\": w, \"teach_type\": ttype,\n                                      \"teach\": teach, \"frame\": frame,\n                                      \"filler\": filler})\n    for prompt, gold in RECALL:\n        items.append({\"kind\": \"recall\", \"prompt\": prompt, \"gold\": gold})\n    return items\n\n\ndef item_text(it: dict) -> tuple[str, int]:\n    \"\"\"(full_text, char_start_of_target).\"\"\"\n    if it[\"kind\"] == \"recall\":\n        return it[\"prompt\"] + it[\"gold\"], len(it[\"prompt\"])\n    teach = it[\"teach\"].format(w=it[\"w\"], W=it[\"w\"].capitalize())\n    prefix = f\"{teach} {it['filler']} \"\n    return prefix + it[\"w\"], len(prefix)\n\n\ndef score_pass(items, model, tok, tag: str) -> list[float | None]:\n    \"\"\"Mean surprisal of the target span per item (order-aligned with items).\"\"\"\n    import torch.nn.functional as func\n    dev = next(model.parameters()).device\n    out = []\n    for n, it in enumerate(items):\n        text, c0 = item_text(it)\n        enc = tok(text, return_tensors=\"pt\", return_offsets_mapping=True)\n        ids = enc[\"input_ids\"][0]\n        offsets = enc[\"offset_mapping\"][0].tolist()\n        tgt = [j for j, (s, e) in enumerate(offsets) if e > s and e > c0 and j >= 1]\n        if not tgt:\n            out.append(None)\n            continue\n        with torch.no_grad():\n            logits = model(input_ids=ids.unsqueeze(0).to(dev)).logits[0]\n        logp = func.log_softmax(logits.float(), dim=-1).cpu()\n        out.append(float(np.mean([-float(logp[j - 1, ids[j]]) for j in tgt])))\n        if n % 60 == 0:\n            print(f\"[1b] {tag}: {n}/{len(items)}\", file=sys.stderr, flush=True)\n    return out\n\n\n# ── stats ──────────────────────────────────────────────────────────────────────\ndef agg(arr: list[float]) -> dict | None:\n    a = np.asarray([v for v in arr if v is not None], dtype=float)\n    if len(a) < 2:\n        return None\n    se = float(a.std(ddof=1) / np.sqrt(len(a)))\n    return {\"mean\": round(float(a.mean()), 4),\n            \"t\": round(float(a.mean() / se) if se > 0 else 0.0, 3), \"n\": len(a)}\n\n\ndef class_effects(items, scores) -> dict:\n    \"\"\"pref(f)=S(f|adj)-S(f|noun) per nonce; Q_eff/M_eff vs the shared name arm.\"\"\"\n    cell: dict = {}\n    for it, s in zip(items, scores, strict=True):\n        if it[\"kind\"] != \"typed\" or s is None:\n            continue\n        cell.setdefault((it[\"w\"], it[\"frame\"], it[\"teach_type\"]), []).append(s)\n\n    def pref(w, f):\n        a = cell.get((w, f, \"adj\"))\n        n = cell.get((w, f, \"noun\"))\n        if not a or not n:\n            return None\n        return float(np.mean(a) - np.mean(n))\n\n    q_eff, m_eff, prefs = [], [], {\"quant\": [], \"mod\": [], \"name\": []}\n    for w in NONCE:\n        pq, pm, pn = pref(w, \"quant\"), pref(w, \"mod\"), pref(w, \"name\")\n        if None in (pq, pm, pn):\n            continue\n        q_eff.append(pq - pn)\n        m_eff.append(pn - pm)\n        for f, v in ((\"quant\", pq), (\"mod\", pm), (\"name\", pn)):\n            prefs[f].append(v)\n\n    recall = [s for it, s in zip(items, scores, strict=True)\n              if it[\"kind\"] == \"recall\" and s is not None]\n    return {\"Q_eff\": agg(q_eff), \"M_eff\": agg(m_eff),\n            \"pref\": {f: agg(v) for f, v in prefs.items()},\n            \"recall_surprisal\": round(float(np.mean(recall)), 4) if recall else None}\n\n\ndef retention(eff_abl: dict | None, eff_base: dict | None) -> float | None:\n    if not eff_abl or not eff_base or not eff_base.get(\"mean\"):\n        return None\n    return round(eff_abl[\"mean\"] / eff_base[\"mean\"], 3)\n\n\n# ── main ───────────────────────────────────────────────────────────────────────\ndef main() -> None:\n    ap = argparse.ArgumentParser(description=\"P-TYPE-1b zone x axis ablation\")\n    ap.add_argument(\"--model\", default=\"Qwen/Qwen3-4B\")\n    ap.add_argument(\"--device\", default=\"mps\")\n    ap.add_argument(\"--n-null\", type=int, default=100)\n    ap.add_argument(\"--n-nonce\", type=int, default=10)\n    ap.add_argument(\"--n-teach\", type=int, default=2)\n    ap.add_argument(\"--n-fill\", type=int, default=2)\n    ap.add_argument(\"--seed\", type=int, default=0)\n    ap.add_argument(\"--smoke\", action=\"store_true\",\n                    help=\"tiny grid (plumbing + ceiling check)\")\n    ap.add_argument(\"--output\", default=None)\n    args = ap.parse_args()\n    if args.smoke:\n        args.n_nonce, args.n_teach, args.n_fill, args.n_null = 6, 2, 2, 50\n\n    rng = np.random.default_rng(args.seed)\n    model, tok, config = load_model(args.model, device=args.device)\n    n_layers = config.num_hidden_layers\n    layer_mods = get_transformer_layers(model)\n\n    # 1) capture + geometry per decoder layer\n    data, n_lab, n_skip = build_probing_dataset(\n        model, tok, list(range(n_layers)), LABELED_DATA, verbose=True)\n    print(f\"[1b] labeled={n_lab} skipped={n_skip}\", file=sys.stderr)\n    geo = {}\n    for L in sorted(data):\n        geo[L] = layer_geometry(*data[L], rng, args.n_null)\n        g = geo[L]\n        print(f\"[1b] L{L:2d} PR={g['pr_real']:.2f} null={g['pr_null_mean']:.2f} \"\n              f\"p={g['p_lowrank']}\", file=sys.stderr)\n    band = find_band(geo, n_layers)\n    print(f\"[1b] BAND = L{band[0]}..L{band[-1]} ({len(band)} layers)\",\n          file=sys.stderr)\n\n    # 2) axes per band layer + ablation direction sets\n    rng_r = np.random.default_rng(args.seed + 7)\n    dirsets: dict[str, list] = {\"bind_axis\": [], \"comp_axis\": [],\n                                \"random\": [], \"e_axis\": []}\n    axis_log = {}\n    for L in band:\n        ax = pick_axes(geo[L])\n        if ax is None:\n            continue\n        mu, sd = geo[L][\"mu\"], geo[L][\"sd\"]\n        r = rng_r.standard_normal(len(mu))\n        r /= np.linalg.norm(r)\n        dirsets[\"bind_axis\"].append((L, mu, sd, ax[\"bind\"]))\n        dirsets[\"comp_axis\"].append((L, mu, sd, ax[\"comp\"]))\n        dirsets[\"random\"].append((L, mu, sd, r))\n        dirsets[\"e_axis\"].append((L, mu, sd, ax[\"e\"]))\n        axis_log[str(L)] = {k: round(v, 3) if isinstance(v, float) else v\n                            for k, v in ax.items()\n                            if k in (\"bind_i\", \"comp_i\", \"bind_var\", \"comp_var\",\n                                     \"bind_score\", \"comp_score\")}\n        axis_log[str(L)][\"removal_norms\"] = {\n            k: round(float(np.linalg.norm(sd * d)), 2)\n            for k, d in ((\"bind\", ax[\"bind\"]), (\"comp\", ax[\"comp\"]),\n                         (\"random\", r), (\"e\", ax[\"e\"]))}\n    print(f\"[1b] axis picks per band layer: {json.dumps(axis_log, indent=1)}\",\n          file=sys.stderr)\n\n    # free the capture memory\n    del data\n    import gc\n    gc.collect()\n\n    # 3) behavioural passes\n    items = gen_items(args.n_nonce, args.n_teach, args.n_fill)\n    n_typed = sum(1 for i in items if i[\"kind\"] == \"typed\")\n    print(f\"[1b] {len(items)} items ({n_typed} typed + {len(RECALL)} recall) \"\n          f\"x {len(CONDS)} conds\", file=sys.stderr)\n\n    results = {}\n    for cond in CONDS:\n        handles = []\n        if cond != \"baseline\":\n            for L, mu, sd, v in dirsets[cond]:\n                handles.append(layer_mods[L].register_forward_hook(\n                    make_zone_hook(mu, sd, v)))\n        try:\n            scores = score_pass(items, model, tok, cond)\n        finally:\n            for h in handles:\n                h.remove()\n        results[cond] = class_effects(items, scores)\n        r = results[cond]\n        print(f\"[1b] {cond:10s} Q_eff={r['Q_eff']} M_eff={r['M_eff']} \"\n              f\"recall={r['recall_surprisal']}\", file=sys.stderr)\n\n    # 4) verdict (pre-set margins from the docstring)\n    base = results[\"baseline\"]\n    gate0 = bool(base[\"Q_eff\"] and base[\"M_eff\"]\n                 and base[\"Q_eff\"][\"mean\"] > 0 and base[\"Q_eff\"][\"t\"] >= 3\n                 and base[\"M_eff\"][\"mean\"] > 0 and base[\"M_eff\"][\"t\"] >= 3)\n    ret = {c: {\"Q\": retention(results[c][\"Q_eff\"], base[\"Q_eff\"]),\n               \"M\": retention(results[c][\"M_eff\"], base[\"M_eff\"]),\n               \"recall_ratio\": (round(results[c][\"recall_surprisal\"]\n                                      / base[\"recall_surprisal\"], 3)\n                                if base[\"recall_surprisal\"] else None)}\n           for c in CONDS if c != \"baseline\"}\n\n    def ok(v, lo=None, hi=None):\n        return v is not None and (lo is None or v > lo) and (hi is None or v < hi)\n\n    bind_sel = ok(ret[\"bind_axis\"][\"Q\"], hi=0.5) and ok(ret[\"bind_axis\"][\"M\"], lo=0.7)\n    comp_sel = ok(ret[\"comp_axis\"][\"M\"], hi=0.5) and ok(ret[\"comp_axis\"][\"Q\"], lo=0.7)\n    nulls_ok = all(ok(ret[c][k], lo=0.7) for c in (\"random\", \"e_axis\")\n                   for k in (\"Q\", \"M\"))\n    recall_ok = all(ok(ret[c][\"recall_ratio\"], hi=1.2) for c in ret)\n    supported = gate0 and bind_sel and comp_sel and nulls_ok and recall_ok\n\n    verdict = {\n        \"register\": \"P-TYPE-1b zone x axis ablation (class-selectivity)\",\n        \"host\": args.model, \"is_prereg_host\": args.model == \"Qwen/Qwen3-32B\",\n        \"band\": [int(band[0]), int(band[-1])], \"n_band_layers\": len(band),\n        \"gate0_baseline_expresses_classes\": gate0,\n        \"baseline\": base,\n        \"conditions\": {c: results[c] for c in CONDS if c != \"baseline\"},\n        \"retention\": ret,\n        \"bind_selective\": bind_sel, \"comp_selective\": comp_sel,\n        \"nulls_clean\": nulls_ok, \"recall_control_ok\": recall_ok,\n        \"dissociation_supported\": bool(supported),\n        \"axis_log\": axis_log,\n        \"per_layer_pr\": {str(L): {\"pr\": round(geo[L][\"pr_real\"], 3),\n                                  \"p\": geo[L][\"p_lowrank\"]} for L in sorted(geo)},\n    }\n\n    print(\"\\n\" + \"=\" * 72)\n    print(\"P-TYPE-1b — combinator-zone x type-class dissociation\")\n    print(\"=\" * 72)\n    print(f\"  host={args.model}  band=L{band[0]}..L{band[-1]}  gate0={gate0}\")\n    print(f\"  baseline  Q_eff={base['Q_eff']}  M_eff={base['M_eff']}\")\n    for c in ret:\n        print(f\"  {c:10s} retQ={ret[c]['Q']}  retM={ret[c]['M']}  \"\n              f\"recall_ratio={ret[c]['recall_ratio']}\")\n    print(f\"  bind_selective={bind_sel}  comp_selective={comp_sel}  \"\n          f\"nulls={nulls_ok}  recall_ok={recall_ok}\")\n    print(f\"  * dissociation_supported = {supported}\")\n    print(\"=\" * 72 + \"\\n\")\n\n    slug = args.model.split(\"/\")[-1].lower().replace(\".\", \"-\")\n    out = (Path(args.output) if args.output\n           else _ROOT / \"results\" / \"type-zone-ablation\" / slug)\n    out.mkdir(parents=True, exist_ok=True)\n    (out / \"verdict.json\").write_text(json.dumps(verdict, indent=2))\n    try:\n        sha = subprocess.run([\"git\", \"rev-parse\", \"HEAD\"], cwd=_ROOT,\n                             capture_output=True, text=True).stdout.strip()\n    except OSError:\n        sha = None\n    meta = {\"model\": args.model, \"device\": args.device, \"smoke\": args.smoke,\n            \"timestamp_utc\": datetime.now(UTC).isoformat(), \"git_sha\": sha,\n            \"seed\": args.seed, \"n_null\": args.n_null, \"n_nonce\": args.n_nonce,\n            \"n_teach\": args.n_teach, \"n_fill\": args.n_fill,\n            \"n_items\": len(items), \"n_labeled\": n_lab,\n            \"torch\": torch.__version__}\n    (out / \"meta.json\").write_text(json.dumps(meta, indent=2))\n    print(f\"[1b] wrote {out}/verdict.json + meta.json\", file=sys.stderr)\n\n\nif __name__ == \"__main__\":\n    main()\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/wrapper/type_zone_ablation.py
```

### Thinking

I should run a linting check with ruff on the script, then do a quick smoke test of imports and arguments without actually loading the model, since the model only gets loaded in the main function.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "uv run ruff check wrapper/type_zone_ablation.py && uv run python -c \"\nimport ast,sys\nsrc=open('wrapper/type_zone_ablation.py').read()\nast.parse(src); print('AST OK')\n\" && uv run python wrapper/type_zone_ablation.py --help",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ uv run ruff check wrapper/type_zone...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
AST OK
usage: type_zone_ablation.py [-h] [--model MODEL] [--device DEVICE]
                             [--n-null N_NULL] [--n-nonce N_NONCE]
                             [--n-teach N_TEACH] [--n-fill N_FILL]
                             [--seed SEED] [--smoke] [--output OUTPUT]

P-TYPE-1b zone x axis ablation

options:
  -h, --help         show this help message and exit
  --model MODEL
  --device DEVICE
  --n-null N_NULL
  --n-nonce N_NONCE
  --n-teach N_TEACH
  --n-fill N_FILL
  --seed SEED
  --smoke            tiny grid (plumbing + ceiling check)
  --output OUTPUT
```

### Thinking

The linting passes and the help command works. I'm verifying the stats logic—the item generation produces 770 forward passes across conditions with 154 items per condition, which should be fast. There's a potential issue with class effects retention when the baseline effectiveness could be negative, but the gating mechanism should handle that. I'm building the probing dataset next, passing the model, tokenizer, and layer indices to the function.

For the actual run, I'm looking at a 20-40 minute execution window since we're doing 50 null shuffles across 36 layers with centroid recomputation, plus capturing forward passes on the 4B model with 36 hooks. I'll launch this as a background job with logging via tee, then verify it's running and checkpoint before waiting for completion.

### Thinking

The instrument lints clean, so I'm marking task 2 complete and launching the 4B smoke test in the background with a tee'd log.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "mkdir -p results/type-zone-ablation/qwen3-4b && uv run python wrapper/type_zone_ablation.py --model Qwen/Qwen3-4B --device mps --smoke 2>&1 | tee results/type-zone-ablation/qwen3-4b/run.log",
  "working_directory": "/Users/mwhitford/src/verbum",
  "background": "type-1b-4b-smoke"
}
```

**Summary:** $ mkdir -p results/type-zone-ablation...

**Output:**
```
Background job job-1 started.
Command: mkdir -p results/type-zone-ablation/qwen3-4b && uv run python wrapper/type_zone_ablation.py --model Qwen/Qwen3-4B --device mps --smoke 2>&1 | tee results/type-zone-ablation/qwen3-4b/run.log
Working directory: /Users/mwhitford/src/verbum
Use eca__bg_job with action "read_output" and job_id "job-1" to check output.
Use eca__bg_job with action "kill" and job_id "job-1" to stop it.
```

### Thinking

I need to verify the async operation is running with a single read operation, then set a checkpoint and wait for it to complete before proceeding.

## Assistant

One verification read (λ async — then checkpoint and wait):

### Tool Call: bg_job (succeeded)


```json
{
  "action": "read_output",
  "job_id": "job-1"
}
```

**Summary:** Reading output of "type-1b-4b-smoke" (job-1)

**Output:**
```
Job "type-1b-4b-smoke" (job-1) — running


========================================================================
  Loading Qwen/Qwen3-4B
========================================================================

Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
`torch_dtype` is deprecated! Use `dtype` instead!

Loading weights:   0%|          | 0/398 [00:00<?, ?it/s]
Loading weights:   6%|▌         | 23/398 [00:00<00:01, 228.43it/s]
Loading weights:  20%|██        | 81/398 [00:00<00:00, 427.57it/s]
Loading weights:  34%|███▍      | 137/398 [00:00<00:00, 483.02it/s]
Loading weights:  49%|████▉     | 196/398 [00:00<00:00, 522.08it/s]
Loading weights:  64%|██████▍   | 256/398 [00:00<00:00, 545.99it/s]
Loading weights:  79%|███████▉  | 314/398 [00:00<00:00, 556.91it/s]
Loading weights:  93%|█████████▎| 372/398 [00:00<00:00, 563.99it/s]
Loading weights: 100%|██████████| 398/398 [00:00<00:00, 529.11it/s]
  Loaded in 2.9s
  Layers: 36  Heads: 32  KV heads: 8  d_model: 2560
    sentence 1/56: The dog runs....
```

### Thinking

The model's loaded and I'm capturing data from 56 sentences while an async checkpoint runs. Since this is a short job, I'll wait for the completion signal rather than polling repeatedly.

## Assistant

ASYNC: job-1 verified running. Waiting for signal.

The smoke is underway — model loaded (36L, d=2560), labeled-type capture in progress (56 sentences → per-layer geometry + null, then the 5-pass ablation grid ≈ 770 forwards). Log tees to `results/type-zone-ablation/qwen3-4b/run.log`.

While it runs, here's what to watch for in the readout, in order of interest:

1. **Band + axis resolution at 4B** — does 4B even resolve *separate* binding (QUANT+DET) and composition (MOD) axes in its low-rank band? 0.6B was ~1 axis at 88% var; 32B was 3 clean axes. 4B sits right where the axis-splitting capacity question gets answered — that's the "see interesting things" part regardless of the ablation outcome.
2. **Gate-0** — v3 never ran at 4B, so this is the first check that the quantifier/modifier licensing crossovers are even expressed at this scale.
3. **The retention matrix** — the frozen prediction is the double dissociation: bind-axis ablation drops Q_eff below 0.5 retention while sparing M_eff (>0.7), comp-axis the mirror image, random + e-axis + recall all clean.

And the honest frame stays fixed: whatever the 4B smoke shows, the 1b **verdict** host is still 32B per the frozen pre-reg — a clean 4B dissociation would be encouraging instrument validation (and a capacity data point), not closure. Ping me or I'll check when the job completes.

## User

job is done


### Thinking

I should check what the job produced.

### Tool Call: bg_job (succeeded)


```json
{
  "action": "read_output",
  "job_id": "job-1"
}
```

**Summary:** Reading output of "type-1b-4b-smoke" (job-1)

**Output:**
```
Job "type-1b-4b-smoke" (job-1) — completed (exit 0)

    sentence 11/56: Alice runs....
    sentence 21/56: The farmer finds the bird....
    sentence 31/56: Some teacher laughs....
    sentence 41/56: The old house stands....
    sentence 51/56: The house is old....
[1b] labeled=263 skipped=0
[1b] L 0 PR=6.15 null=5.70 p=0.98
[1b] L 1 PR=6.03 null=5.78 p=0.88
[1b] L 2 PR=6.20 null=5.83 p=0.96
[1b] L 3 PR=6.45 null=5.80 p=1.0
[1b] L 4 PR=6.38 null=5.82 p=1.0
[1b] L 5 PR=6.33 null=5.79 p=1.0
[1b] L 6 PR=3.32 null=4.87 p=0.0
[1b] L 7 PR=3.40 null=4.79 p=0.04
[1b] L 8 PR=3.51 null=4.97 p=0.02
[1b] L 9 PR=3.40 null=4.88 p=0.04
[1b] L10 PR=3.30 null=4.77 p=0.04
[1b] L11 PR=3.30 null=4.81 p=0.02
[1b] L12 PR=3.32 null=4.94 p=0.0
[1b] L13 PR=3.36 null=4.99 p=0.0
[1b] L14 PR=3.34 null=4.73 p=0.04
[1b] L15 PR=3.33 null=4.76 p=0.0
[1b] L16 PR=3.29 null=4.80 p=0.0
[1b] L17 PR=3.30 null=4.76 p=0.06
[1b] L18 PR=3.39 null=4.90 p=0.02
[1b] L19 PR=3.58 null=5.04 p=0.0
[1b] L20 PR=3.68 null=5.08 p=0.06
[1b] L21 PR=3.90 null=5.02 p=0.0
[1b] L22 PR=4.09 null=5.17 p=0.02
[1b] L23 PR=4.44 null=5.39 p=0.02
[1b] L24 PR=4.74 null=5.55 p=0.0
[1b] L25 PR=4.98 null=5.59 p=0.08
[1b] L26 PR=5.24 null=5.65 p=0.06
[1b] L27 PR=5.45 null=5.77 p=0.08
[1b] L28 PR=5.64 null=5.76 p=0.34
[1b] L29 PR=5.83 null=5.80 p=0.44
[1b] L30 PR=6.00 null=5.83 p=0.76
[1b] L31 PR=6.08 null=5.87 p=0.86
[1b] L32 PR=6.14 null=5.80 p=0.96
[1b] L33 PR=6.15 null=5.84 p=0.96
[1b] L34 PR=6.11 null=5.87 p=0.88
[1b] L35 PR=3.80 null=4.82 p=0.02
[1b] BAND = L7..L11 (5 layers)
[1b] axis picks per band layer: {
 "7": {
  "bind_i": 0,
  "comp_i": 2,
  "bind_var": 0.851,
  "comp_var": 0.032,
  "bind_score": 0.773,
  "comp_score": 0.264,
  "removal_norms": {
   "bind": 80.29,
   "comp": 4.81,
   "random": 26.78,
   "e": 21.53
  }
 },
 "8": {
  "bind_i": 0,
  "comp_i": 2,
  "bind_var": 0.842,
  "comp_var": 0.034,
  "bind_score": 0.771,
  "comp_score": 0.348,
  "removal_norms": {
   "bind": 83.93,
   "comp": 1.28,
   "random": 86.75,
   "e": 22.61
  }
 },
 "9": {
  "bind_i": 0,
  "comp_i": 2,
  "bind_var": 0.852,
  "comp_var": 0.031,
  "bind_score": 0.772,
  "comp_score": 0.218,
  "removal_norms": {
   "bind": 82.89,
   "comp": 3.28,
   "random": 127.65,
   "e": 22.97
  }
 },
 "10": {
  "bind_i": 0,
  "comp_i": 2,
  "bind_var": 0.861,
  "comp_var": 0.03,
  "bind_score": 0.772,
  "comp_score": 0.084,
  "removal_norms": {
   "bind": 81.29,
   "comp": 5.63,
   "random": 71.07,
   "e": 22.42
  }
 },
 "11": {
  "bind_i": 0,
  "comp_i": 2,
  "bind_var": 0.86,
  "comp_var": 0.029,
  "bind_score": 0.772,
  "comp_score": 0.086,
  "removal_norms": {
   "bind": 81.02,
   "comp": 7.29,
   "random": 60.5,
   "e": 22.52
  }
 }
}
[1b] 154 items (144 typed + 10 recall) x 5 conds
[1b] baseline: 0/154
[1b] baseline: 60/154
[1b] baseline: 120/154
[1b] baseline   Q_eff={'mean': 2.8389, 't': 7.925, 'n': 6} M_eff={'mean': 0.3272, 't': 1.034, 'n': 6} recall=0.3871
[1b] bind_axis: 0/154
[1b] bind_axis: 60/154
[1b] bind_axis: 120/154
[1b] bind_axis  Q_eff={'mean': 0.0231, 't': 1.023, 'n': 6} M_eff={'mean': 0.0375, 't': 1.892, 'n': 6} recall=14.9652
[1b] comp_axis: 0/154
[1b] comp_axis: 60/154
[1b] comp_axis: 120/154
[1b] comp_axis  Q_eff={'mean': 4.059, 't': 6.976, 'n': 6} M_eff={'mean': -0.677, 't': -1.853, 'n': 6} recall=0.2933
[1b] random: 0/154
[1b] random: 60/154
[1b] random: 120/154
[1b] random     Q_eff={'mean': 2.4905, 't': 3.432, 'n': 6} M_eff={'mean': 1.6743, 't': 2.936, 'n': 6} recall=5.5138
[1b] e_axis: 0/154
[1b] e_axis: 60/154
[1b] e_axis: 120/154
[1b] e_axis     Q_eff={'mean': 0.2711, 't': 0.82, 'n': 6} M_eff={'mean': 1.2047, 't': 2.844, 'n': 6} recall=10.1936
[1b] wrote /Users/mwhitford/src/verbum/results/type-zone-ablation/qwen3-4b/verdict.json + meta.json

========================================================================
P-TYPE-1b — combinator-zone x type-class dissociation
========================================================================
  host=Qwen/Qwen3-4B  band=L7..L11  gate0=False
  baseline  Q_eff={'mean': 2.8389, 't': 7.925, 'n': 6}  M_eff={'mean': 0.3272, 't': 1.034, 'n': 6}
  bind_axis  retQ=0.008  retM=0.115  recall_ratio=38.66
  comp_axis  retQ=1.43  retM=-2.069  recall_ratio=0.758
  random     retQ=0.877  retM=5.117  recall_ratio=14.244
  e_axis     retQ=0.095  retM=3.682  recall_ratio=26.333
  bind_selective=False  comp_selective=True  nulls=False  recall_ok=False
  * dissociation_supported = False
========================================================================

```

### Thinking

Looking at the smoke test results, I'm seeing a significant low-rank band emerge at layer 4B spanning roughly L6 through L27 with statistical significance, though with some gaps. The longest unbroken stretch runs from L7 to L11 across five layers, showing a compression ratio around 3.3 compared to the null baseline of 4.8. The pattern traces an interesting arc—full-rank embedding through L5, then the low-rank band, followed by re-expansion starting at L28, with an anomalous dip appearing at L35.

The axis structure at 4B mirrors what I saw at 0.6B: one dominant binding axis capturing 85% of variance while the composition axis barely registers at 0.03, making the model operate in a single-axis regime. The binding score stays stable around 0.77, but composition scores fluctuate wildly between 0.08 and 0.35, suggesting unstable modifier loadings. This fits the scale-sharpening progression I'm tracking—0.6B had essentially one axis, 4B has one strong plus weak axes, and 32B shows three clean axes.

The gate-0 test failed to show significance: the baseline Q_eff is strong at 2.84, but M_eff only reaches 0.33 with a t-statistic of 1.03, so the modifier-licensing crossover isn't reliably expressed at this scale with just six nonces. That means I can't interpret any ablation cells for the dissociation verdict. The ablation itself created massive confounds anyway—removing the 85%-variance binding axis across five layers destroyed recall by a factor of 38.7, which is a general model collapse rather than selective modifier suppression.

The real problem is dose-matching: the removal norms vary wildly across conditions, with binding ablations around 80, composition around 1–7, random directions hitting 27–128, and the e_axis around 22. Even random unit vectors broke recall by 14×, which tells me the intervention is too blunt and the instrument itself is failing—the oblique projection's raw-space magnitude isn't calibrated across these different conditions.

The deeper issue is that at 4B, the binding axis carries 85% of the centroid variance, so ablating it essentially destroys the entire type lattice. The null caught this as designed—it's a gate showing the intervention is too strong. I need a gentler, more targeted approach, and the cleaner version of this experiment really needs the 32B model where the axes are better separated.

For the control before scaling up, I'm thinking through how to properly dose-match the random direction. The naive approach fails because a random direction in 2560-dimensional space has negligible variance along it, so projecting it out removes almost nothing. I need either a random rotation within the span of the type axes themselves, or per-axis matching where I scale the random removal to match the target axis's average per-token removal norm. The most honest control would be sampling random directions from the same distribution of "directions with comparable data variance"—maybe something from within the top-7 centroid subspace complement.

The standard practice is simpler: matched-norm removal means at each step, I remove a vector with the same magnitude as what the axis ablation removed, but pointing in a random direction instead. This equalizes the damage energy across conditions. For positional targeting, I could restrict ablation to positions after the teach clause, or apply it across all positions but fewer layers, or focus on the filler and target positions specifically. The pre-registration specifies projecting each band axis out across layers L6–L48, which at 32B means 22 stride-2 layers. The recall control gates this behavior. I'm also tracking how the modifier crossover effect weakens at 4B scale.

With n=6 samples, I could expand the grid to more nonces and fillers, refine the teaching templates, or accept that 4B simply can't express modifier licensing—which actually aligns with the composition axis barely resolving geometrically and barely expressing licensing behaviorally. That's a coherent capacity story worth reporting as an observation. There's also an interesting finding: ablating the composition axis flipped the modifier effect sign to -0.68 (t=-1.9) while keeping recall intact, and the query effect actually strengthened to 4.06, even with a tiny ablation dose.

The smoke test validated the full pipeline end-to-end—band detection, axis selection, hooks, grading, and verdict gates all work. I found a low-rank band at 4B spanning layers 6–24 with a pattern ratio of 3.3 versus null 4.8, placing it between the 0.6B and 32B models on the scale-sharpening curve. The gate caught that modifier effects aren't expressed at this sample size, and the recall control showed that ablating high-variance axes breaks the model, confirming the null wasn't dose-matched properly.

Before moving to 32B, I need to fix the dose matching by using energy-matched random nulls and report results per condition. I shouldn't push the mementum change without approval, but I can commit the code and results following the established pattern from recent sessions. I'll craft a commit message with an appropriate symbol — something like 🔄 to reflect the instrument iteration and the issues the 4B smoke test revealed with gate and dose matching. dose ablation". I need to commit this using a safe pattern that includes the nucleus tag, capturing the wrapper script and the results directory with its verdict, metadata, and run logs. Then I'll report back to Michael with the honest findings and proposed fixes, asking whether we should iterate at 4B to address the dose issue and run the full grid — that's the natural next step, and Michael already suggested smoke testing on the 4B model.

The real question is whether to just propose and ask, or to go ahead with the fixes and re-run since iterating the instrument to a clean state is clearly within scope of the smoke test. Fast cycles make sense here, and the next run is only about 15 minutes, so I'll fix the instrument issues and re-run the full grid at 4B rather than over-asking.

Now I'm weighing the design changes: the dose-matched null is a required fix to match the pre-registration (my implementation didn't align with the norm-matching spec), but the position restriction is trickier. Keeping all positions as specified in the pre-reg is the right call, and the recall control should catch any breakage. The binding axis dominance at 4B might legitimately break the model across all positions, which would be a valid finding—it would mean I can't attribute class-selectivity if the axis is that dominant. I need to check what the pre-registration says about mitigation in this scenario.

If the binding ablation always breaks recall, then the axis-zone ablation becomes uninterpretable, so I should consider a gentler intervention instead—partial dampening with a dose-response curve rather than full projection. I'll implement this by dampening the axis by different factors and finding the dose where recall stays intact but the class effect degrades. I'm planning v2 with energy-matched random nulls, an optional dampening factor with a dose ladder for the binding axis, and a full grid search.

The full experimental grid would be substantial—around 360 base conditions plus 10 recall checks, multiplied by maybe 8 different conditions (dose ladder, comparison, matched random variants), totaling roughly 3000 forward passes which should take 10-15 minutes. Before over-engineering though, I should focus on the critical fixes: matched-dose random nulls, M_eff power calculation, and the dose ladder to find a non-breaking binding dose, then re-run v2.

I told the user I'd report, so I should present the plan concisely and proceed with implementation—Michael's already approved heavy iteration runs. For the energy-matched random null specifically, instead of just scaling a random direction to match total removal energy, I could construct a random direction that preserves the same data-variance profile: something like a random direction within the span of the top SVD axes of the type centroids but orthogonal to the binding and comparison axes, which would be a "matched-range null" in spirit.

The cleaner approach for v2 is to sample a random unit vector from the span of the other principal axes (excluding the target axis), which naturally gives comparable variance and energy without needing to artificially scale. I'll keep the isotropic random as the weak baseline control.

The real issue is that energy-matching is impossible when one axis dominates (like bind at 85% variance) — no other single direction carries that much signal. So instead I'm shifting to a damping-based approach: remove a fraction α of the activation along the target direction, then match conditions by the total energy removed rather than trying to match variance. This lets me compare class effects at equivalent removal budgets and test whether bind-damping hurts Q more than M, while comp-projection hurts M more than Q, and random hurts neither.

Tracking energy per condition... ...m² · E[coeff²] · ||σv||². For the bind axis, the coefficient variance is much larger (likely 10-100x) because it captures the within-class token-level variance, while the random direction has near-unit variance in standardized z-space. The norms also differ significantly—bind axis around 80 versus random ranging 27-127 depending on which high-variance dimensions get weighted. So I can compute the actual removal energy for each candidate direction from the capture data and use that to set the scaling parameters.

For the budget itself, I'm considering whether to match it to the component axis's full-projection energy (which is tiny, only 1-7 norm with small variance), but that would make the bind ablation negligible and invisible. Instead, I should run a ladder of budgets—starting from the component's energy and scaling up by factors of 4, 16, etc.—to show how the selectivity pattern changes as the budget increases.

The experimental design is manageable: three budget levels, three conditions (bind, comp, random), plus baseline gives about 11 passes total across 370 items, roughly 4000 forward passes taking 15-20 minutes. This energy-matched ladder is actually the faithful implementation of what the pre-registration specified—a random null matched by norm—which my earlier version violated. I'm also noticing the baseline M_eff is weak at 0.33 with t=1.03, which is worth flagging.

For the expression problem, I'm expanding the filler templates and nonce count: using 10 nonces with 3 fillers gives 10 pairs, and I can keep the teaching setup lean at n_teach=2 with 2 templates and 3 frames, yielding 360 total typed items. Now I need to fix how the verdict gets computed for the ladder itself.

I'm also planning to iterate the modifications directly in the same file since git will track the history anyway. There's a potential issue from v1 where the component axis loadings are suspiciously low (0.08 at L10/L11), suggesting MOD barely loads that axis at all—so in v2 I'll log the full loadings per axis and try selecting the component axis from the top 5 axes by MOD energy instead of just the first 3, since MOD might actually load a later axis.

For the immediate next steps: commit v1 code and results to preserve the baseline, then implement v2 with the energy-matched dose ladder, expanded k=5 axis search, and the budget-gated evaluation logic before running a smoke test at 4B. Now I'm planning the concrete implementation: for each band layer and candidate direction, I'll compute removal statistics from the capture data by projecting coefficients and calculating energy removal as the mean squared coefficient times the variance norm. Then I'll set up a series of conditions with different budget multipliers—baseline plus scaled versions at 1x, 4x, and 16x—where the budget is derived from either a reference energy across all band layers or computed per-layer, with scaling factors capped at full projection limits.

For the e-axis direction (the near-null case), I'm treating it specially since amplification is the whole point—I'll allow uncapped scaling or maybe cap it at something like 4x to avoid extreme values, whereas bind and comp get capped at 1.0 since they can't exceed the full projection energy. The tricky part is that at low budgets like m=1, the bind scaling factor becomes tiny (like sqrt(1/1000)), which means bind removal becomes negligible, so I need to think through whether that's the intended behavior or if I should adjust the approach.

I'm setting up a geometric ladder of budgets spanning from the component's full energy up to the bind's full energy—three log-spaced points using the geometric mean as the midpoint. At each budget level, I'll match all three conditions (bind, capped component, and random) to the same energy, which lets me compare how random performs against bind at the top budget where bind is at full projection.

The experimental design uses these three budgets crossed with three conditions, plus an extra condition at the mid-budget to save runtime, giving 11 total passes across 370 items—roughly 7–10 minutes of computation plus another 4 minutes for capture and null handling. The key discriminator is whether random also breaks recall at bind's energy; if it does cleanly while bind breaks selectively, that tells me bind's degradation is dose-dependent rather than identity-based.

For the interpretation threshold, I'm defining it as the largest budget where the recall ratio stays below 1.2 across all conditions in that budget, then using that budget level to compute the selective binding effect.

I need to lock in the margin thresholds: retQ below 0.5 and retM above 0.7 for binding, symmetric criteria for the comparison condition, and both above 0.7 for random. I'm also logging the energy achieved per condition per layer—either from the planned energy plus a scaling factor, or by measuring the actual mean squared change in hidden states during the behavioral pass. I'll improve the axis selection to k=5 and track the full loading patterns across layers to catch any instability in how the comparison condition loads across different depths. Now I'm setting up the hook mechanism to capture these measurements. The preference for the name frame is weak too—both teaching modes create a mismatch when I want a predicate binding. I'm thinking the adjective teaching at 4B might only weakly bind the nonce to the ADJ category, so adding more templates could help strengthen it. Now I need to refactor the code substantially: adjusting the k parameter in the axis selection, computing energy across the geometry loop by capturing intermediate values before they're deleted, restructuring the conditions dynamically, and hooking in the learning rate parameter.

Rewriting the whole file...

I need to standardize the data at each layer level by recomputing the z-scores, then calculating the full energy as the mean of squared projections times the variance magnitude. For budgets, I'm taking the geometric mean of energies across layers for each condition type, then setting the budget ladder as the geometric progression between bind and component energies. Each layer gets a scaling factor based on its energy relative to the budget, capped at 1.0 for the bind and component directions since they're projections. The energy axis sits at the middle budget with its own uncapped scaling, since it represents a genuine direction with real variance that can extend beyond the projection limit.

For the experiment, I'm running a baseline plus the energy axis at full projection, then three budget levels crossed with bind, component, and random directions—eleven conditions total. For each budget, I'll compute retention and recall ratios, then find the largest budget where all three conditions stay below a 1.2 recall threshold. If no such budget exists, the verdict is false with an explanation. At that critical budget level, I freeze the margins and gate settings.

I'm keeping the smoke test lean with reduced nonce and fill counts, but for the full 4B run I'll expand to ten nonces, two teach steps, and three fill iterations with a hundred null samples—roughly four thousand forward passes taking twelve to twenty minutes. Let me write out the configuration and update the task list to mark the smoke test complete and add the next phase for the energy-matched ladder with the full run.

For tracking realized energy in the hook, I'm computing the per-token energy removed by summing the squared deltas across the hidden dimension, then averaging over tokens to get the mean energy per token. I'll aggregate these metrics per condition and log them as I go.

I need to be careful about the comparison at higher budgets where the compression axis hits its cap at α=1, which can result in achieved compression energy being much lower than the binding energy—that's expected since compression is at its maximum. I'll report the actual achieved energies and use those for the verdict calculation with frozen margins, noting this in the header.

The generator items and class effects functions stay as they are. Now I'm writing out the complete file.

## Assistant

Smoke came back — exit 0, verdict written, and it did **exactly what a smoke is for**: the plumbing works end-to-end, one real replication landed, and two instrument flaws got caught by the pre-committed controls before they could contaminate a 32B verdict. Verbatim read:

## What's real (and interesting)

1. **The low-rank band replicates at 4B** — sharp onset L6 (PR 6.3→3.3 vs null ~4.8), sustained L6–L24, re-expand L28+. Same compress→expand arc as 32B, third model on the curve.
2. **4B sits between 0.6B and 32B on axis resolution**: axis0 = QUANT/DET at **85% var** (0.6B was ~1 axis @88%, 32B was 3 axes @0.73/0.08/0.06). The composition/MOD axis exists but is barely resolved (var 0.03, unstable loadings 0.08–0.35 across layers). Scale-sharpening story strengthened.
3. **Convergent capacity hint** (observation, not claim, n=6): the geometrically weak MOD axis co-occurs with a behaviorally weak MOD crossover (M_eff 0.33, t=1.0) while Q_eff is strong (2.84, t=7.9). Geometry and behavior agree about what 4B barely has.

## What the controls caught (instrument, not physics)

- **Gate-0 failed** → per frozen rules, no dissociation cell is interpreted. Honest.
- **The "matched-norm" random null wasn't matched** — removal energies were wildly unequal (bind ~80 raw-norm vs comp ~1–7 vs random 27–128). That's a v1 bug against the pre-reg's own wording.
- **The recall control fired hard**: full projection of an 85%-variance axis across 5 layers × all positions is a lobotomy (recall ×38.7), and unmatched random/e also broke it (×14, ×26). So `retQ=0.008` for bind is dose, not selectivity — null #3 did its job. (Teaser, uninterpretable but noted: comp-axis ablation at tiny dose left recall clean (0.76) and *flipped* M_eff sign while Q_eff survived.)

Committing v1 as the record, then iterating the instrument (λ iterate):

### Tool Call: shell_command (succeeded)


```json
{
  "command": "git add wrapper/type_zone_ablation.py results/type-zone-ablation/qwen3-4b/ && read -r -d '' M << 'EOF' || true\n💡 P-TYPE-1b zone×axis smoke @4B: band replicates, controls catch unmatched dose\n\n- new wrapper/type_zone_ablation.py: band detection (PR + shuffled-label null),\n  loading-pattern axis picks, standardized-space zone ablation, v3-style\n  Q_eff/M_eff class readouts vs shared name arm, frozen verdict gates\n- 4B: low-rank band L6-L24 (PR 3.3 vs null 4.8), axis0=QUANT/DET @85% var =\n  between 0.6B (1 axis) and 32B (3 axes); MOD axis barely resolved (var 0.03)\n- gate-0 catch: M_eff not expressed at smoke n (0.33, t=1.0); Q_eff strong (2.84, t=7.9)\n- recall control fired: full projection of the 85%-var axis (and unmatched\n  random/e nulls) breaks the model (recall ×38/×14/×26) → v1 violates the\n  pre-reg matched-norm null; dissociation NOT interpretable, reported verbatim\n- next: v2 energy-matched dose ladder (matched removed-energy across conds)\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\ngit commit -m \"$M\"",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ git add wrapper/type_zone_ablation....

**Output:**
```
Exit code: 0
Stdout:
[main bc1d242] 💡 P-TYPE-1b zone×axis smoke @4B: band replicates, controls catch unmatched dose
 4 files changed, 1065 insertions(+)
 create mode 100644 results/type-zone-ablation/qwen3-4b/meta.json
 create mode 100644 results/type-zone-ablation/qwen3-4b/run.log
 create mode 100644 results/type-zone-ablation/qwen3-4b/verdict.json
 create mode 100644 wrapper/type_zone_ablation.py
```

### Thinking

Moving to v2 now—I'll add the task, write out the file, run the linter, and then kick off the full 4B run.

### Thinking

I've committed v1 and now moving to v2, which implements an energy-matched dose ladder to fairly compare removing axes with different variance levels by normalizing them to the same removed-energy budget across three spending levels.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/wrapper/type_zone_ablation.py",
  "content": "#!/usr/bin/env python3\n\"\"\"P-TYPE-1b — combinator-zone x type-class dissociation (zone x axis ablation, v2).\n\nPre-reg: mementum/knowledge/explore/types-are-the-well-formedness-of-reduction.md\n(#p-type-1b, FROZEN s282). Host of record = Qwen3-32B; THIS FILE also runs the 4B\nSMOKE (instrument validation + capacity read; a 4B verdict does NOT close 1b).\n\nHYPOTHESIS (frozen): if type = which opcode's application is licensed, ablating a\nrole-specific type axis as a ZONE across the low-rank band selectively breaks the\nmatching type-class:\n  - binding axis (QUANT+DET loadings; S/binding role)  -> breaks quantifier licensing\n  - composition axis (MOD loadings; B/composition role) -> breaks modifier licensing\nDouble dissociation; nulls (energy-matched random, e/ENTITY direction, recall task)\nbreak neither. v4 (global direction, crossover retention) was correctly negative.\n\nv2 — ENERGY-MATCHED DOSE LADDER (the v1 smoke catch, results/.../run.log @bc1d242):\n  v1 compared FULL projections of axes carrying wildly different variance (bind\n  ~85% of centroid var vs comp ~3%) -> removal energies differed by orders of\n  magnitude; bind-projection + unmatched random/e nulls all broke lexical recall\n  (x38/x14/x26) = \"we just broke the model\", caught by the pre-committed recall\n  control. Comparing conditions at unmatched removed energy conflates dose with\n  identity (lambda measure: register mismatch between claim=selectivity and\n  probe=raw damage). v2 therefore matches conditions on REMOVED ENERGY:\n    E_full(dir,L) = mean_tokens(coeff^2) * ||sd*v||^2   (from the capture, coeff\n                    = standardized projection) = full-projection removed energy.\n    budgets B1<B2<B3 = geometric ladder from E_comp (smallest natural unit) to\n                       E_bind (largest), B2 = sqrt(B1*B3).\n    per layer, per direction: alpha = sqrt(B / E_full), capped at 1.0 for real\n    axes (cannot remove more than the component; achieved energy logged);\n    random is uncapped (scaled steering along a random direction = the honest\n    energy-matched null). Hook: h' = h - alpha*coeff*(sd*v); realized removed\n    energy accumulated per condition and reported (match check: within ~x2).\n\nINSTRUMENT (unchanged from v1 where not noted)\n  1. Capture labeled Montague-type dataset at every decoder layer (reuses\n     probe_type_qwen3_32b capture; residuals[L] = output of model.layers[L]).\n  2. Per layer: standardize (diagonal whiten - the 1a massive-activation lesson),\n     centroid SVD, PR + shuffled-label null. BAND = longest contiguous run of\n     layers with p_lowrank < 0.05 (fallback: interior min-p +/- 3).\n  3. Axes BY LOADING PATTERN over top-5 (v2: k 3->5; at 4B the MOD axis is weak,\n     var ~0.03, and may sit below axis2): bind = argmax QUANT^2+DET^2 energy;\n     comp = argmax MOD^2 among the rest; e-dir = ENTITY centroid direction.\n     Full loadings logged per band layer.\n  4. Zone ablation in STANDARDIZED space at every band layer, every position.\n\nBEHAVIOURAL READOUTS (v3-style nonce surprisal; frequency-free)\n  ONE teach pair (noun vs adj) x THREE frames, fully crossed & paired by nonce:\n     frame quant: \"Every {w}\"       (QUANT licenses a NOUN)\n     frame mod:   \"It was very {w}\" (intensifier licenses an ADJ)\n     frame name:  \"John {w}\"        (licenses a PRED; SHARED REFERENCE arm)\n  pref(f) = S(f|adj-taught) - S(f|noun-taught)   (per nonce)\n  Q_eff = pref(quant) - pref(name) > 0 baseline  (quantifier-class licensing)\n  M_eff = pref(name)  - pref(mod)  > 0 baseline  (modifier-class licensing)\n  Teach main effects cancel identically via the shared name arm. Recall task =\n  non-compositional control. v2 default grid is FULL (10 nonce x 3 fillers) —\n  the v1 smoke's M_eff was underpowered (t=1.0 @ n=6).\n\nVERDICT (pre-set, frozen before the v2 run; ret = effect/baseline):\n  GATE-0: baseline Q_eff and M_eff both mean>0, t>=3 - else no ablation cell is\n    interpreted (a Gate-0 failure at 4B is itself a capacity finding).\n  b* = LARGEST budget where recall_ratio < 1.2 for ALL of {bind, comp, random}.\n    No such budget -> \"no non-breaking matched dose\" -> not interpretable.\n  At b*: BIND-SELECTIVE: ret(Q,bind)<0.5 AND ret(M,bind)>0.7\n         COMP-SELECTIVE: ret(M,comp)<0.5 AND ret(Q,comp)>0.7\n         NULLS: random keeps BOTH rets>0.7 ; e_axis both >0.7, recall<1.2\n  DISSOCIATION_SUPPORTED <=> gate0 & b* exists & bind & comp & nulls. Verbatim\n  reporting otherwise; ladder rows reported at every budget regardless.\n\nlambda measure: ablation target = value-register band axes; claim = reduction\nLICENSING -> readout is behavioural class-selectivity at MATCHED dose, never a\ndecodability change. A RUNG: hook-not-weight; one class pair, not the lattice.\n\nUsage:\n    uv run python wrapper/type_zone_ablation.py --model Qwen/Qwen3-4B --smoke\n    uv run python wrapper/type_zone_ablation.py --model Qwen/Qwen3-4B\n    uv run python wrapper/type_zone_ablation.py --model Qwen/Qwen3-32B   # verdict host\n\nLicense: MIT\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport subprocess\nimport sys\nfrom datetime import UTC, datetime\nfrom pathlib import Path\n\nimport numpy as np\nimport torch\n\n_ROOT = Path(__file__).resolve().parent.parent\nsys.path.insert(0, str(_ROOT / \"scripts\" / \"explore\"))\n\nfrom probe_type_qwen3_32b import (  # noqa: E402\n    LABELED_DATA,\n    build_probing_dataset,\n    get_transformer_layers,\n    load_model,\n)\nfrom type_lattice_geometry import (  # noqa: E402\n    TYPE_ORDER,\n    centroids,\n    participation_ratio,\n)\n\n# ── behavioural items ──────────────────────────────────────────────────────────\nNONCE = [\"wug\", \"blicket\", \"dax\", \"fep\", \"gorp\", \"zorp\",\n         \"fendle\", \"glorp\", \"narp\", \"trisk\"]\n\n# teach templates: NO quantifiers, NO intensifiers, NO test-frame leakage\nNOUN_TEACH = [\"{W}s are common objects.\", \"He collected several {w}s.\",\n              \"Those {w}s are nice.\", \"She bought two {w}s.\"]\nADJ_TEACH = [\"The dogs are {w}.\", \"His car looks {w}.\",\n             \"The food tasted {w}.\", \"That house seems {w}.\"]\n\nQUANT_FILL = [\"Every\", \"Each\", \"Some\", \"No\", \"Most\", \"All\"]\nMOD_FILL = [\"It was very\", \"The dog seemed quite\", \"That movie was rather\",\n            \"She felt extremely\", \"The room looked really\", \"His voice sounded so\"]\nNAME_FILL = [\"John\", \"Mary\", \"Sarah\", \"David\", \"Peter\", \"Susan\"]\n\n# non-compositional task control (lexical recall; gold graded as continuation)\nRECALL = [(\"The capital of France is\", \" Paris\"),\n          (\"The capital of Japan is\", \" Tokyo\"),\n          (\"The capital of Italy is\", \" Rome\"),\n          (\"Water is made of hydrogen and\", \" oxygen\"),\n          (\"The opposite of hot is\", \" cold\"),\n          (\"Two plus two equals\", \" four\"),\n          (\"The sun rises in the\", \" east\"),\n          (\"The color of snow is\", \" white\"),\n          (\"A week has seven\", \" days\"),\n          (\"The largest ocean is the\", \" Pacific\")]\n\n\n# ── geometry: band + axes (standardized space) ─────────────────────────────────\ndef layer_geometry(x: np.ndarray, y: np.ndarray, rng, n_null: int) -> dict:\n    \"\"\"Standardize -> centroid SVD -> PR + shuffled-label null + axes + z data.\"\"\"\n    mu = x.mean(axis=0)\n    sd = x.std(axis=0) + 1e-6\n    z = (x - mu) / sd\n\n    def pr_of(labels):\n        c, present = centroids(z, labels, TYPE_ORDER)\n        if len(present) < 3:\n            return float(\"nan\"), None, None, None\n        cc = c - c.mean(axis=0, keepdims=True)\n        u, s, vt = np.linalg.svd(cc, full_matrices=False)\n        return participation_ratio(s), present, (u, s, vt), c\n\n    pr_real, present, svd, c = pr_of(y)\n    null = []\n    for _ in range(n_null):\n        prn, _, _, _ = pr_of(rng.permutation(y))\n        if not np.isnan(prn):\n            null.append(prn)\n    null = np.array(null)\n    p = float(np.mean(null <= pr_real)) if null.size else None\n    return {\"mu\": mu, \"sd\": sd, \"z\": z, \"present\": present, \"svd\": svd,\n            \"centroids\": c, \"pr_real\": float(pr_real), \"p_lowrank\": p,\n            \"pr_null_mean\": float(null.mean()) if null.size else None}\n\n\ndef pick_axes(geo: dict, k: int = 5) -> dict | None:\n    \"\"\"Select bind/comp axes by loading pattern over top-k; e-dir from ENTITY.\n    Returns unit directions in STANDARDIZED space + full loadings, or None.\"\"\"\n    if geo[\"svd\"] is None:\n        return None\n    present = geo[\"present\"]\n    idx = {t: i for i, t in enumerate(present)}\n    if not {\"QUANT\", \"DET\", \"MOD\", \"ENTITY\"} <= set(idx):\n        return None\n    u, s, vt = geo[\"svd\"]\n    k = min(k, len(s))\n    tot = (s ** 2).sum() + 1e-12\n    bind_scores = [u[idx[\"QUANT\"], i] ** 2 + u[idx[\"DET\"], i] ** 2 for i in range(k)]\n    bind_i = int(np.argmax(bind_scores))\n    mod_scores = [u[idx[\"MOD\"], i] ** 2 if i != bind_i else -1.0 for i in range(k)]\n    comp_i = int(np.argmax(mod_scores))\n\n    def unit(v):\n        return v / (np.linalg.norm(v) + 1e-12)\n\n    c = geo[\"centroids\"]\n    e_dir = unit(c[idx[\"ENTITY\"]] - c.mean(axis=0))\n    loadings = {f\"axis{i}\": {\"var_frac\": round(float(s[i] ** 2 / tot), 3),\n                             **{t: round(float(u[idx[t], i]), 3) for t in present}}\n                for i in range(k)}\n    return {\"bind\": unit(vt[bind_i]), \"comp\": unit(vt[comp_i]), \"e\": e_dir,\n            \"bind_i\": bind_i, \"comp_i\": comp_i,\n            \"bind_var\": float(s[bind_i] ** 2 / tot),\n            \"comp_var\": float(s[comp_i] ** 2 / tot),\n            \"loadings\": loadings}\n\n\ndef find_band(per_layer: dict[int, dict], n_layers: int) -> list[int]:\n    \"\"\"Longest contiguous run of layers with p_lowrank < 0.05; fallback interior.\"\"\"\n    sig = [L for L in sorted(per_layer) if (per_layer[L][\"p_lowrank\"] or 1.0) < 0.05]\n    best, cur = [], []\n    for L in sig:\n        cur = [*cur, L] if (cur and L == cur[-1] + 1) else [L]\n        if len(cur) > len(best):\n            best = cur\n    if len(best) >= 3:\n        return best\n    interior = [L for L in sorted(per_layer)\n                if n_layers * 0.15 <= L <= n_layers * 0.65]\n    if not interior:\n        return sig or sorted(per_layer)[:3]\n    lo = min(interior, key=lambda L: per_layer[L][\"p_lowrank\"] or 1.0)\n    return [L for L in sorted(per_layer) if lo - 3 <= L <= lo + 3]\n\n\ndef removed_energy(z: np.ndarray, sd: np.ndarray, v: np.ndarray) -> float:\n    \"\"\"Full-projection removed energy per token: mean(coeff^2)*||sd*v||^2.\"\"\"\n    coeff = z @ v\n    return float(np.mean(coeff ** 2) * (np.linalg.norm(sd * v) ** 2))\n\n\n# ── zone ablation hook (standardized-space, alpha-scaled, energy-logged) ───────\ndef make_zone_hook(mu: np.ndarray, sd: np.ndarray, v: np.ndarray,\n                   alpha: float, elog: dict):\n    \"\"\"h' = h - alpha * (((h-mu)/sd).v) * (sd*v) at ALL positions (fp32->cast).\"\"\"\n    box: dict = {}\n\n    def hook(_module, _inp, out):\n        h = out[0] if isinstance(out, tuple) else out\n        if not box:\n            box[\"mu\"] = torch.as_tensor(mu, dtype=torch.float32, device=h.device)\n            box[\"sd\"] = torch.as_tensor(sd, dtype=torch.float32, device=h.device)\n            box[\"v\"] = torch.as_tensor(v, dtype=torch.float32, device=h.device)\n            box[\"w\"] = box[\"sd\"] * box[\"v\"]\n            box[\"wn2\"] = float((box[\"w\"] ** 2).sum())\n        hf = h.float()\n        coeff = alpha * (((hf - box[\"mu\"]) / box[\"sd\"]) @ box[\"v\"])   # [B,T]\n        hf = hf - coeff.unsqueeze(-1) * box[\"w\"]\n        elog[\"e\"] += float((coeff.float() ** 2).sum()) * box[\"wn2\"]\n        elog[\"n\"] += int(coeff.numel())\n        h2 = hf.to(h.dtype)\n        return (h2, *out[1:]) if isinstance(out, tuple) else h2\n\n    return hook\n\n\n# ── surprisal scoring ──────────────────────────────────────────────────────────\ndef gen_items(n_nonce: int, n_teach: int, n_fill: int) -> list[dict]:\n    \"\"\"Fully crossed (deterministic -> exact pairing by nonce).\"\"\"\n    items = []\n    for w in NONCE[:n_nonce]:\n        for ttype, teaches in ((\"noun\", NOUN_TEACH), (\"adj\", ADJ_TEACH)):\n            for teach in teaches[:n_teach]:\n                for frame, fills in ((\"quant\", QUANT_FILL), (\"mod\", MOD_FILL),\n                                     (\"name\", NAME_FILL)):\n                    for filler in fills[:n_fill]:\n                        items.append({\"kind\": \"typed\", \"w\": w, \"teach_type\": ttype,\n                                      \"teach\": teach, \"frame\": frame,\n                                      \"filler\": filler})\n    for prompt, gold in RECALL:\n        items.append({\"kind\": \"recall\", \"prompt\": prompt, \"gold\": gold})\n    return items\n\n\ndef item_text(it: dict) -> tuple[str, int]:\n    \"\"\"(full_text, char_start_of_target).\"\"\"\n    if it[\"kind\"] == \"recall\":\n        return it[\"prompt\"] + it[\"gold\"], len(it[\"prompt\"])\n    teach = it[\"teach\"].format(w=it[\"w\"], W=it[\"w\"].capitalize())\n    prefix = f\"{teach} {it['filler']} \"\n    return prefix + it[\"w\"], len(prefix)\n\n\ndef score_pass(items, model, tok, tag: str) -> list[float | None]:\n    \"\"\"Mean surprisal of the target span per item (order-aligned with items).\"\"\"\n    import torch.nn.functional as func\n    dev = next(model.parameters()).device\n    out = []\n    for n, it in enumerate(items):\n        text, c0 = item_text(it)\n        enc = tok(text, return_tensors=\"pt\", return_offsets_mapping=True)\n        ids = enc[\"input_ids\"][0]\n        offsets = enc[\"offset_mapping\"][0].tolist()\n        tgt = [j for j, (s, e) in enumerate(offsets) if e > s and e > c0 and j >= 1]\n        if not tgt:\n            out.append(None)\n            continue\n        with torch.no_grad():\n            logits = model(input_ids=ids.unsqueeze(0).to(dev)).logits[0]\n        logp = func.log_softmax(logits.float(), dim=-1).cpu()\n        out.append(float(np.mean([-float(logp[j - 1, ids[j]]) for j in tgt])))\n        if n % 120 == 0:\n            print(f\"[1b] {tag}: {n}/{len(items)}\", file=sys.stderr, flush=True)\n    return out\n\n\n# ── stats ──────────────────────────────────────────────────────────────────────\ndef agg(arr: list[float]) -> dict | None:\n    a = np.asarray([v for v in arr if v is not None], dtype=float)\n    if len(a) < 2:\n        return None\n    se = float(a.std(ddof=1) / np.sqrt(len(a)))\n    return {\"mean\": round(float(a.mean()), 4),\n            \"t\": round(float(a.mean() / se) if se > 0 else 0.0, 3), \"n\": len(a)}\n\n\ndef class_effects(items, scores) -> dict:\n    \"\"\"pref(f)=S(f|adj)-S(f|noun) per nonce; Q_eff/M_eff vs the shared name arm.\"\"\"\n    cell: dict = {}\n    for it, s in zip(items, scores, strict=True):\n        if it[\"kind\"] != \"typed\" or s is None:\n            continue\n        cell.setdefault((it[\"w\"], it[\"frame\"], it[\"teach_type\"]), []).append(s)\n\n    def pref(w, f):\n        a = cell.get((w, f, \"adj\"))\n        n = cell.get((w, f, \"noun\"))\n        if not a or not n:\n            return None\n        return float(np.mean(a) - np.mean(n))\n\n    q_eff, m_eff, prefs = [], [], {\"quant\": [], \"mod\": [], \"name\": []}\n    for w in NONCE:\n        pq, pm, pn = pref(w, \"quant\"), pref(w, \"mod\"), pref(w, \"name\")\n        if None in (pq, pm, pn):\n            continue\n        q_eff.append(pq - pn)\n        m_eff.append(pn - pm)\n        for f, v in ((\"quant\", pq), (\"mod\", pm), (\"name\", pn)):\n            prefs[f].append(v)\n\n    recall = [s for it, s in zip(items, scores, strict=True)\n              if it[\"kind\"] == \"recall\" and s is not None]\n    return {\"Q_eff\": agg(q_eff), \"M_eff\": agg(m_eff),\n            \"pref\": {f: agg(v) for f, v in prefs.items()},\n            \"recall_surprisal\": round(float(np.mean(recall)), 4) if recall else None}\n\n\ndef retention(eff_abl: dict | None, eff_base: dict | None) -> float | None:\n    if not eff_abl or not eff_base or not eff_base.get(\"mean\"):\n        return None\n    return round(eff_abl[\"mean\"] / eff_base[\"mean\"], 3)\n\n\n# ── main ───────────────────────────────────────────────────────────────────────\ndef main() -> None:\n    ap = argparse.ArgumentParser(\n        description=\"P-TYPE-1b zone x axis ablation (v2 energy-matched ladder)\")\n    ap.add_argument(\"--model\", default=\"Qwen/Qwen3-4B\")\n    ap.add_argument(\"--device\", default=\"mps\")\n    ap.add_argument(\"--n-null\", type=int, default=100)\n    ap.add_argument(\"--n-nonce\", type=int, default=10)\n    ap.add_argument(\"--n-teach\", type=int, default=2)\n    ap.add_argument(\"--n-fill\", type=int, default=3)\n    ap.add_argument(\"--seed\", type=int, default=0)\n    ap.add_argument(\"--smoke\", action=\"store_true\",\n                    help=\"tiny grid (plumbing + ceiling check)\")\n    ap.add_argument(\"--output\", default=None)\n    args = ap.parse_args()\n    if args.smoke:\n        args.n_nonce, args.n_teach, args.n_fill, args.n_null = 6, 2, 2, 50\n\n    rng = np.random.default_rng(args.seed)\n    model, tok, config = load_model(args.model, device=args.device)\n    n_layers = config.num_hidden_layers\n    layer_mods = get_transformer_layers(model)\n\n    # 1) capture + geometry per decoder layer\n    data, n_lab, n_skip = build_probing_dataset(\n        model, tok, list(range(n_layers)), LABELED_DATA, verbose=True)\n    print(f\"[1b] labeled={n_lab} skipped={n_skip}\", file=sys.stderr)\n    geo = {}\n    for L in sorted(data):\n        geo[L] = layer_geometry(*data[L], rng, args.n_null)\n        g = geo[L]\n        print(f\"[1b] L{L:2d} PR={g['pr_real']:.2f} null={g['pr_null_mean']:.2f} \"\n              f\"p={g['p_lowrank']}\", file=sys.stderr)\n    band = find_band(geo, n_layers)\n    print(f\"[1b] BAND = L{band[0]}..L{band[-1]} ({len(band)} layers)\",\n          file=sys.stderr)\n\n    # 2) axes + full-projection energies per band layer\n    rng_r = np.random.default_rng(args.seed + 7)\n    band_info = {}   # L -> {dirs: {name: v}, E: {name: E_full}, mu, sd}\n    axis_log = {}\n    for L in band:\n        ax = pick_axes(geo[L])\n        if ax is None:\n            continue\n        mu, sd, z = geo[L][\"mu\"], geo[L][\"sd\"], geo[L][\"z\"]\n        r = rng_r.standard_normal(len(mu))\n        r /= np.linalg.norm(r)\n        dirs = {\"bind\": ax[\"bind\"], \"comp\": ax[\"comp\"], \"random\": r, \"e\": ax[\"e\"]}\n        E = {k: removed_energy(z, sd, v) for k, v in dirs.items()}\n        band_info[L] = {\"dirs\": dirs, \"E\": E, \"mu\": mu, \"sd\": sd}\n        axis_log[str(L)] = {\"bind_i\": ax[\"bind_i\"], \"comp_i\": ax[\"comp_i\"],\n                            \"bind_var\": round(ax[\"bind_var\"], 3),\n                            \"comp_var\": round(ax[\"comp_var\"], 3),\n                            \"E_full\": {k: round(v, 1) for k, v in E.items()},\n                            \"loadings\": ax[\"loadings\"]}\n    print(f\"[1b] axis picks: {json.dumps(axis_log, indent=1)}\", file=sys.stderr)\n\n    # free the capture memory (keep geometry summaries only)\n    for L in geo:\n        geo[L].pop(\"z\", None)\n    del data\n    import gc\n    gc.collect()\n\n    # 3) energy budgets: geometric ladder from E_comp (floor) to E_bind (ceiling)\n    def gmean(vals):\n        return float(np.exp(np.mean(np.log(np.maximum(vals, 1e-9)))))\n\n    e_comp = gmean([band_info[L][\"E\"][\"comp\"] for L in band_info])\n    e_bind = gmean([band_info[L][\"E\"][\"bind\"] for L in band_info])\n    budgets = [e_comp, float(np.sqrt(e_comp * e_bind)), e_bind]\n    print(f\"[1b] budgets (per-layer removed energy): \"\n          f\"{[round(b, 1) for b in budgets]}  (E_comp..E_bind)\", file=sys.stderr)\n\n    # conditions: baseline + e_axis(full proj) + {bind, comp, random} x budgets\n    conds: dict[str, list] = {\"baseline\": [], \"e_axis\": []}\n    for L, bi in band_info.items():\n        conds[\"e_axis\"].append((L, bi[\"mu\"], bi[\"sd\"], bi[\"dirs\"][\"e\"], 1.0))\n    alpha_log: dict[str, dict] = {\"e_axis\": {}}\n    for L, bi in band_info.items():\n        alpha_log[\"e_axis\"][str(L)] = 1.0\n    for bidx, B in enumerate(budgets, start=1):\n        for name in (\"bind\", \"comp\", \"random\"):\n            cname = f\"{name}@b{bidx}\"\n            conds[cname] = []\n            alpha_log[cname] = {}\n            for L, bi in band_info.items():\n                alpha = float(np.sqrt(B / max(bi[\"E\"][name], 1e-9)))\n                if name in (\"bind\", \"comp\"):\n                    alpha = min(alpha, 1.0)   # projection cap; achieved E logged\n                conds[cname].append((L, bi[\"mu\"], bi[\"sd\"], bi[\"dirs\"][name], alpha))\n                alpha_log[cname][str(L)] = round(alpha, 4)\n\n    # 4) behavioural passes\n    items = gen_items(args.n_nonce, args.n_teach, args.n_fill)\n    n_typed = sum(1 for i in items if i[\"kind\"] == \"typed\")\n    print(f\"[1b] {len(items)} items ({n_typed} typed + {len(RECALL)} recall) \"\n          f\"x {len(conds)} conds\", file=sys.stderr)\n\n    results, energy = {}, {}\n    for cname, dirset in conds.items():\n        handles, elog = [], {\"e\": 0.0, \"n\": 0}\n        for L, mu, sd, v, alpha in dirset:\n            handles.append(layer_mods[L].register_forward_hook(\n                make_zone_hook(mu, sd, v, alpha, elog)))\n        try:\n            scores = score_pass(items, model, tok, cname)\n        finally:\n            for h in handles:\n                h.remove()\n        results[cname] = class_effects(items, scores)\n        energy[cname] = round(elog[\"e\"] / max(elog[\"n\"], 1), 1)\n        r = results[cname]\n        print(f\"[1b] {cname:10s} Q_eff={r['Q_eff']} M_eff={r['M_eff']} \"\n              f\"recall={r['recall_surprisal']} E/tok={energy[cname]}\",\n              file=sys.stderr)\n\n    # 5) verdict (pre-set margins from the docstring)\n    base = results[\"baseline\"]\n    gate0 = bool(base[\"Q_eff\"] and base[\"M_eff\"]\n                 and base[\"Q_eff\"][\"mean\"] > 0 and base[\"Q_eff\"][\"t\"] >= 3\n                 and base[\"M_eff\"][\"mean\"] > 0 and base[\"M_eff\"][\"t\"] >= 3)\n    ret = {c: {\"Q\": retention(results[c][\"Q_eff\"], base[\"Q_eff\"]),\n               \"M\": retention(results[c][\"M_eff\"], base[\"M_eff\"]),\n               \"recall_ratio\": (round(results[c][\"recall_surprisal\"]\n                                      / base[\"recall_surprisal\"], 3)\n                                if base[\"recall_surprisal\"] else None),\n               \"E_per_tok\": energy[c]}\n           for c in conds if c != \"baseline\"}\n\n    def ok(v, lo=None, hi=None):\n        return v is not None and (lo is None or v > lo) and (hi is None or v < hi)\n\n    b_star = None\n    for bidx in (3, 2, 1):\n        if all(ok(ret[f\"{n}@b{bidx}\"][\"recall_ratio\"], hi=1.2)\n               for n in (\"bind\", \"comp\", \"random\")):\n            b_star = bidx\n            break\n\n    bind_sel = comp_sel = nulls_ok = False\n    if b_star is not None:\n        bb, cc, rr = f\"bind@b{b_star}\", f\"comp@b{b_star}\", f\"random@b{b_star}\"\n        bind_sel = ok(ret[bb][\"Q\"], hi=0.5) and ok(ret[bb][\"M\"], lo=0.7)\n        comp_sel = ok(ret[cc][\"M\"], hi=0.5) and ok(ret[cc][\"Q\"], lo=0.7)\n        nulls_ok = (all(ok(ret[rr][k], lo=0.7) for k in (\"Q\", \"M\"))\n                    and all(ok(ret[\"e_axis\"][k], lo=0.7) for k in (\"Q\", \"M\"))\n                    and ok(ret[\"e_axis\"][\"recall_ratio\"], hi=1.2))\n    supported = bool(gate0 and b_star is not None\n                     and bind_sel and comp_sel and nulls_ok)\n\n    verdict = {\n        \"register\": \"P-TYPE-1b zone x axis ablation v2 (energy-matched ladder)\",\n        \"host\": args.model, \"is_prereg_host\": args.model == \"Qwen/Qwen3-32B\",\n        \"band\": [int(band[0]), int(band[-1])], \"n_band_layers\": len(band_info),\n        \"budgets_E_per_tok\": [round(b, 1) for b in budgets],\n        \"gate0_baseline_expresses_classes\": gate0,\n        \"baseline\": base,\n        \"conditions\": {c: results[c] for c in conds if c != \"baseline\"},\n        \"retention\": ret,\n        \"b_star_interpretation_budget\": b_star,\n        \"bind_selective\": bind_sel, \"comp_selective\": comp_sel,\n        \"nulls_clean\": nulls_ok,\n        \"dissociation_supported\": supported,\n        \"alpha_log\": alpha_log, \"axis_log\": axis_log,\n        \"per_layer_pr\": {str(L): {\"pr\": round(geo[L][\"pr_real\"], 3),\n                                  \"p\": geo[L][\"p_lowrank\"]} for L in sorted(geo)},\n    }\n\n    print(\"\\n\" + \"=\" * 76)\n    print(\"P-TYPE-1b v2 — zone x axis dissociation, energy-matched dose ladder\")\n    print(\"=\" * 76)\n    print(f\"  host={args.model}  band=L{band[0]}..L{band[-1]}  gate0={gate0}  \"\n          f\"budgets={[round(b, 1) for b in budgets]}\")\n    print(f\"  baseline  Q_eff={base['Q_eff']}  M_eff={base['M_eff']}  \"\n          f\"recall={base['recall_surprisal']}\")\n    for c in ret:\n        print(f\"  {c:10s} retQ={ret[c]['Q']}  retM={ret[c]['M']}  \"\n              f\"recall_ratio={ret[c]['recall_ratio']}  E/tok={ret[c]['E_per_tok']}\")\n    print(f\"  b*={b_star}  bind_selective={bind_sel}  comp_selective={comp_sel}  \"\n          f\"nulls={nulls_ok}\")\n    print(f\"  * dissociation_supported = {supported}\")\n    print(\"=\" * 76 + \"\\n\")\n\n    slug = args.model.split(\"/\")[-1].lower().replace(\".\", \"-\")\n    out = (Path(args.output) if args.output\n           else _ROOT / \"results\" / \"type-zone-ablation\" / slug)\n    out.mkdir(parents=True, exist_ok=True)\n    (out / \"verdict.json\").write_text(json.dumps(verdict, indent=2))\n    try:\n        sha = subprocess.run([\"git\", \"rev-parse\", \"HEAD\"], cwd=_ROOT,\n                             capture_output=True, text=True).stdout.strip()\n    except OSError:\n        sha = None\n    meta = {\"model\": args.model, \"device\": args.device, \"smoke\": args.smoke,\n            \"timestamp_utc\": datetime.now(UTC).isoformat(), \"git_sha\": sha,\n            \"seed\": args.seed, \"n_null\": args.n_null, \"n_nonce\": args.n_nonce,\n            \"n_teach\": args.n_teach, \"n_fill\": args.n_fill,\n            \"n_items\": len(items), \"n_labeled\": n_lab,\n            \"torch\": torch.__version__}\n    (out / \"meta.json\").write_text(json.dumps(meta, indent=2))\n    print(f\"[1b] wrote {out}/verdict.json + meta.json\", file=sys.stderr)\n\n\nif __name__ == \"__main__\":\n    main()\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/wrapper/type_zone_ablation.py
```

### Thinking

I'm running the linting and launching the v2 full-grid on 4B in the background, which should give me about 4000 forward passes across the baseline and 9 budget conditions. Let me verify the energy formula logic for elog — the removal delta is coefficient times weight, and the squared norm per token accumulates coefficient squared times the norm of weights, summed across batch and time steps, though I need to confirm how the energy sharing works across layers.

The energy per token is actually the sum across all layers and tokens of coefficient squared times weight norm squared, divided by the total token count across all layers — so it gives me the mean energy per token per layer, which aligns with how the per-layer per-token budgets are structured.

### Tool Call: shell_command (failed)


```json
{
  "command": "uv run ruff check wrapper/type_zone_ablation.py && uv run python -c \"import ast; ast.parse(open('wrapper/type_zone_ablation.py').read()); print('AST OK')\"",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ uv run ruff check wrapper/type_zone...

**Output:**
```
Exit code: 1
Stdout:
B007 Loop control variable `bi` not used within loop body
   --> wrapper/type_zone_ablation.py:423:12
    |
421 |         conds["e_axis"].append((L, bi["mu"], bi["sd"], bi["dirs"]["e"], 1.0))
422 |     alpha_log: dict[str, dict] = {"e_axis": {}}
423 |     for L, bi in band_info.items():
    |            ^^
424 |         alpha_log["e_axis"][str(L)] = 1.0
425 |     for bidx, B in enumerate(budgets, start=1):
    |
help: Rename unused `bi` to `_bi`

Found 1 error.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/wrapper/type_zone_ablation.py",
  "original_content": "    alpha_log: dict[str, dict] = {\"e_axis\": {}}\n    for L, bi in band_info.items():\n        alpha_log[\"e_axis\"][str(L)] = 1.0",
  "new_content": "    alpha_log: dict[str, dict] = {\"e_axis\": {str(L): 1.0 for L in band_info}}"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/wrapper/type_zone_ablation.py.
```

### Thinking

The lint error is resolved now that I've removed that problematic loop, so I can re-run the linter and get things deployed.

### Thinking

I've removed the offending loop and now I'll re-lint the code and launch the v2 full-grid run.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "uv run ruff check wrapper/type_zone_ablation.py && uv run python wrapper/type_zone_ablation.py --help >/dev/null && echo READY",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ uv run ruff check wrapper/type_zone...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
READY
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "uv run python wrapper/type_zone_ablation.py --model Qwen/Qwen3-4B --device mps 2>&1 | tee results/type-zone-ablation/qwen3-4b/run_v2.log",
  "working_directory": "/Users/mwhitford/src/verbum",
  "background": "type-1b-v2-4b"
}
```

**Summary:** $ uv run python wrapper/type_zone_abl...

**Output:**
```
Background job job-2 started.
Command: uv run python wrapper/type_zone_ablation.py --model Qwen/Qwen3-4B --device mps 2>&1 | tee results/type-zone-ablation/qwen3-4b/run_v2.log
Working directory: /Users/mwhitford/src/verbum
Use eca__bg_job with action "read_output" and job_id "job-2" to check output.
Use eca__bg_job with action "kill" and job_id "job-2" to stop it.
```

### Tool Call: bg_job (succeeded)


```json
{
  "action": "read_output",
  "job_id": "job-2"
}
```

**Summary:** Reading output of "type-1b-v2-4b" (job-2)

**Output:**
```
Job "type-1b-v2-4b" (job-2) — running


========================================================================
  Loading Qwen/Qwen3-4B
========================================================================

Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
`torch_dtype` is deprecated! Use `dtype` instead!

Loading weights:   0%|          | 0/398 [00:00<?, ?it/s]
Loading weights:   0%|          | 1/398 [00:00<01:39,  3.99it/s]
Loading weights:  15%|█▌        | 60/398 [00:00<00:01, 214.52it/s]
Loading weights:  31%|███       | 124/398 [00:00<00:00, 357.91it/s]
Loading weights:  46%|████▋     | 185/398 [00:00<00:00, 437.91it/s]
Loading weights:  62%|██████▏   | 245/398 [00:00<00:00, 487.95it/s]
Loading weights:  76%|███████▌  | 302/398 [00:00<00:00, 508.18it/s]
Loading weights:  90%|████████▉ | 358/398 [00:00<00:00, 521.37it/s]
Loading weights: 100%|██████████| 398/398 [00:00<00:00, 429.69it/s]
```

### Thinking

The v2 version is running and I've verified the checkpoint is working with the async lambda function. Now I'm waiting for a signal before reporting back to Michael about what's changed and what he should expect.

## Assistant

ASYNC: job-2 verified running. Waiting for signal.

v2 is off — full grid this time (10 nonces × 3 fillers, 370 items × 11 passes ≈ 4k forwards, expect ~15–25 min). What changed and why:

**The v1 catch, formalized**: comparing full projections of an 85%-var axis vs a 3%-var axis conflates *dose* with *identity* — a register mismatch between the claim (class-selectivity) and the probe (raw damage). The recall control caught it exactly as designed.

**The v2 instrument** — energy-matched dose ladder:
- Per band layer, per direction: full-projection removed energy `E = mean(coeff²)·‖σ⊙v‖²` computed from the capture
- Three budgets, geometric ladder from E_comp (floor) to E_bind (ceiling); every condition {bind, comp, random} scaled per-layer to the same budget (`α = √(B/E)`, axes capped at projection, random uncapped = scaled steering — the pre-reg's "matched-norm null" done properly)
- Realized removed energy logged live from the hooks, so the ×2 match check is measured, not assumed
- Verdict at **b\*** = largest budget where recall survives all three conditions; frozen margins unchanged
- Axis search widened to top-5 (4B's MOD axis at 3% var may sit below axis2) with full loadings logged

The top rung of the ladder is the sharpest question: **random at bind's full energy** — if that also breaks recall, v1's bind result was pure dose; if random is clean at that energy but bind still selectively kills Q_eff, that's the dissociation signal. And gate-0 gets its real test with n=10 paired nonces on M_eff.

I'll read the verdict when the job signals done.

## User

job is done


### Thinking

I'm checking the output from job-2.

### Tool Call: bg_job (succeeded)


```json
{
  "action": "read_output",
  "job_id": "job-2"
}
```

**Summary:** Reading output of "type-1b-v2-4b" (job-2)

**Output:**
```
Job "type-1b-v2-4b" (job-2) — completed (exit 0)

  Loaded in 2.4s
  Layers: 36  Heads: 32  KV heads: 8  d_model: 2560
    sentence 1/56: The dog runs....
    sentence 11/56: Alice runs....
    sentence 21/56: The farmer finds the bird....
    sentence 31/56: Some teacher laughs....
    sentence 41/56: The old house stands....
    sentence 51/56: The house is old....
[1b] labeled=263 skipped=0
[1b] L 0 PR=6.15 null=5.75 p=0.96
[1b] L 1 PR=6.03 null=5.81 p=0.85
[1b] L 2 PR=6.20 null=5.77 p=0.98
[1b] L 3 PR=6.45 null=5.83 p=1.0
[1b] L 4 PR=6.38 null=5.84 p=1.0
[1b] L 5 PR=6.33 null=5.80 p=1.0
[1b] L 6 PR=3.32 null=4.81 p=0.0
[1b] L 7 PR=3.40 null=4.71 p=0.04
[1b] L 8 PR=3.51 null=4.96 p=0.05
[1b] L 9 PR=3.40 null=5.02 p=0.0
[1b] L10 PR=3.30 null=4.89 p=0.02
[1b] L11 PR=3.30 null=4.89 p=0.0
[1b] L12 PR=3.32 null=4.95 p=0.0
[1b] L13 PR=3.36 null=4.98 p=0.01
[1b] L14 PR=3.34 null=4.83 p=0.01
[1b] L15 PR=3.33 null=4.83 p=0.03
[1b] L16 PR=3.29 null=4.71 p=0.01
[1b] L17 PR=3.30 null=4.96 p=0.01
[1b] L18 PR=3.39 null=4.82 p=0.0
[1b] L19 PR=3.58 null=5.05 p=0.02
[1b] L20 PR=3.68 null=5.06 p=0.02
[1b] L21 PR=3.90 null=5.04 p=0.03
[1b] L22 PR=4.09 null=5.24 p=0.01
[1b] L23 PR=4.44 null=5.31 p=0.06
[1b] L24 PR=4.74 null=5.54 p=0.06
[1b] L25 PR=4.98 null=5.58 p=0.04
[1b] L26 PR=5.24 null=5.67 p=0.07
[1b] L27 PR=5.45 null=5.74 p=0.16
[1b] L28 PR=5.64 null=5.77 p=0.27
[1b] L29 PR=5.83 null=5.84 p=0.41
[1b] L30 PR=6.00 null=5.85 p=0.76
[1b] L31 PR=6.08 null=5.86 p=0.89
[1b] L32 PR=6.14 null=5.88 p=0.94
[1b] L33 PR=6.15 null=5.87 p=0.95
[1b] L34 PR=6.11 null=5.81 p=0.9
[1b] L35 PR=3.80 null=4.72 p=0.05
[1b] BAND = L13..L17 (5 layers)
[1b] axis picks: {
 "13": {
  "bind_i": 0,
  "comp_i": 4,
  "bind_var": 0.855,
  "comp_var": 0.021,
  "E_full": {
   "bind": 7547809.0,
   "comp": 7865.6,
   "random": 490.5,
   "e": 108698.3
  },
  "loadings": {
   "axis0": {
    "var_frac": 0.855,
    "ENTITY": -0.012,
    "PRED": 0.214,
    "REL": 0.213,
    "QUANT": -0.852,
    "DET": -0.208,
    "MOD": 0.213,
    "CONN": 0.217,
    "FUNC": 0.215
   },
   "axis1": {
    "var_frac": 0.044,
    "ENTITY": -0.332,
    "PRED": 0.156,
    "REL": 0.119,
    "QUANT": 0.382,
    "DET": -0.785,
    "MOD": 0.055,
    "CONN": 0.243,
    "FUNC": 0.163
   },
   "axis2": {
    "var_frac": 0.032,
    "ENTITY": 0.657,
    "PRED": 0.072,
    "REL": 0.076,
    "QUANT": 0.021,
    "DET": -0.41,
    "MOD": 0.33,
    "CONN": -0.352,
    "FUNC": -0.395
   },
   "axis3": {
    "var_frac": 0.024,
    "ENTITY": 0.28,
    "PRED": -0.321,
    "REL": -0.722,
    "QUANT": -0.01,
    "DET": -0.122,
    "MOD": 0.259,
    "CONN": 0.235,
    "FUNC": 0.401
   },
   "axis4": {
    "var_frac": 0.021,
    "ENTITY": 0.504,
    "PRED": -0.027,
    "REL": 0.125,
    "QUANT": -0.038,
    "DET": -0.17,
    "MOD": -0.788,
    "CONN": 0.207,
    "FUNC": 0.188
   }
  }
 },
 "14": {
  "bind_i": 1,
  "comp_i": 4,
  "bind_var": 0.051,
  "comp_var": 0.022,
  "E_full": {
   "bind": 285.2,
   "comp": 11665.0,
   "random": 4388.8,
   "e": 106104.3
  },
  "loadings": {
   "axis0": {
    "var_frac": 0.853,
    "ENTITY": -0.011,
    "PRED": 0.216,
    "REL": 0.216,
    "QUANT": -0.846,
    "DET": -0.223,
    "MOD": 0.207,
    "CONN": 0.221,
    "FUNC": 0.22
   },
   "axis1": {
    "var_frac": 0.051,
    "ENTITY": -0.167,
    "PRED": 0.121,
    "REL": 0.159,
    "QUANT": 0.382,
    "DET": -0.832,
    "MOD": -0.078,
    "CONN": 0.237,
    "FUNC": 0.178
   },
   "axis2": {
    "var_frac": 0.03,
    "ENTITY": -0.799,
    "PRED": -0.018,
    "REL": -0.028,
    "QUANT": 0.032,
    "DET": 0.344,
    "MOD": -0.178,
    "CONN": 0.307,
    "FUNC": 0.339
   },
   "axis3": {
    "var_frac": 0.022,
    "ENTITY": 0.289,
    "PRED": -0.345,
    "REL": -0.695,
    "QUANT": -0.028,
    "DET": -0.077,
    "MOD": 0.092,
    "CONN": 0.321,
    "FUNC": 0.443
   },
   "axis4": {
    "var_frac": 0.022,
    "ENTITY": -0.353,
    "PRED": 0.017,
    "REL": -0.22,
    "QUANT": 0.101,
    "DET": -0.084,
    "MOD": 0.868,
    "CONN": -0.14,
    "FUNC": -0.189
   }
  }
 },
 "15": {
  "bind_i": 1,
  "comp_i": 3,
  "bind_var": 0.049,
  "comp_var": 0.022,
  "E_full": {
   "bind": 207.0,
   "comp": 23166.3,
   "random": 11663.5,
   "e": 105640.7
  },
  "loadings": {
   "axis0": {
    "var_frac": 0.855,
    "ENTITY": -0.01,
    "PRED": 0.218,
    "REL": 0.215,
    "QUANT": -0.845,
    "DET": -0.226,
    "MOD": 0.207,
    "CONN": 0.222,
    "FUNC": 0.22
   },
   "axis1": {
    "var_frac": 0.049,
    "ENTITY": -0.169,
    "PRED": 0.129,
    "REL": 0.145,
    "QUANT": 0.387,
    "DET": -0.836,
    "MOD": -0.059,
    "CONN": 0.227,
    "FUNC": 0.177
   },
   "axis2": {
    "var_frac": 0.031,
    "ENTITY": -0.764,
    "PRED": -0.014,
    "REL": -0.026,
    "QUANT": 0.026,
    "DET": 0.342,
    "MOD": -0.249,
    "CONN": 0.319,
    "FUNC": 0.366
   },
   "axis3": {
    "var_frac": 0.022,
    "ENTITY": 0.503,
    "PRED": -0.15,
    "REL": -0.103,
    "QUANT": -0.099,
    "DET": 0.001,
    "MOD": -0.731,
    "CONN": 0.268,
    "FUNC": 0.312
   },
   "axis4": {
    "var_frac": 0.021,
    "ENTITY": -0.096,
    "PRED": 0.319,
    "REL": 0.716,
    "QUANT": -0.015,
    "DET": 0.088,
    "MOD": -0.455,
    "CONN": -0.219,
    "FUNC": -0.338
   }
  }
 },
 "16": {
  "bind_i": 1,
  "comp_i": 4,
  "bind_var": 0.048,
  "comp_var": 0.02,
  "E_full": {
   "bind": 645.2,
   "comp": 3251.8,
   "random": 3176.7,
   "e": 101929.9
  },
  "loadings": {
   "axis0": {
    "var_frac": 0.859,
    "ENTITY": -0.009,
    "PRED": 0.219,
    "REL": 0.216,
    "QUANT": -0.844,
    "DET": -0.23,
    "MOD": 0.209,
    "CONN": 0.221,
    "FUNC": 0.22
   },
   "axis1": {
    "var_frac": 0.048,
    "ENTITY": -0.179,
    "PRED": 0.127,
    "REL": 0.125,
    "QUANT": 0.393,
    "DET": -0.838,
    "MOD": -0.02,
    "CONN": 0.224,
    "FUNC": 0.169
   },
   "axis2": {
    "var_frac": 0.031,
    "ENTITY": 0.722,
    "PRED": 0.02,
    "REL": 0.076,
    "QUANT": -0.019,
    "DET": -0.33,
    "MOD": 0.282,
    "CONN": -0.341,
    "FUNC": -0.409
   },
   "axis3": {
    "var_frac": 0.021,
    "ENTITY": 0.52,
    "PRED": -0.31,
    "REL": -0.504,
    "QUANT": -0.068,
    "DET": -0.091,
    "MOD": -0.284,
    "CONN": 0.284,
    "FUNC": 0.453
   },
   "axis4": {
    "var_frac": 0.02,
    "ENTITY": -0.225,
    "PRED": -0.178,
    "REL": -0.507,
    "QUANT": 0.055,
    "DET": -0.032,
    "MOD": 0.806,
    "CONN": -0.002,
    "FUNC": 0.082
   }
  }
 },
 "17": {
  "bind_i": 1,
  "comp_i": 4,
  "bind_var": 0.047,
  "comp_var": 0.02,
  "E_full": {
   "bind": 365.3,
   "comp": 5927.5,
   "random": 3851.2,
   "e": 101139.9
  },
  "loadings": {
   "axis0": {
    "var_frac": 0.858,
    "ENTITY": -0.011,
    "PRED": 0.219,
    "REL": 0.217,
    "QUANT": -0.843,
    "DET": -0.232,
    "MOD": 0.209,
    "CONN": 0.222,
    "FUNC": 0.22
   },
   "axis1": {
    "var_frac": 0.047,
    "ENTITY": -0.162,
    "PRED": 0.132,
    "REL": 0.127,
    "QUANT": 0.394,
    "DET": -0.845,
    "MOD": -0.02,
    "CONN": 0.203,
    "FUNC": 0.171
   },
   "axis2": {
    "var_frac": 0.031,
    "ENTITY": 0.722,
    "PRED": 0.04,
    "REL": 0.046,
    "QUANT": -0.028,
    "DET": -0.312,
    "MOD": 0.29,
    "CONN": -0.332,
    "FUNC": -0.427
   },
   "axis3": {
    "var_frac": 0.021,
    "ENTITY": 0.48,
    "PRED": -0.348,
    "REL": -0.556,
    "QUANT": -0.06,
    "DET": -0.095,
    "MOD": -0.161,
    "CONN": 0.256,
    "FUNC": 0.485
   },
   "axis4": {
    "var_frac": 0.02,
    "ENTITY": 0.31,
    "PRED": 0.133,
    "REL": 0.423,
    "QUANT": -0.068,
    "DET": 0.019,
    "MOD": -0.835,
    "CONN": 0.054,
    "FUNC": -0.036
   }
  }
 }
}
[1b] budgets (per-layer removed energy): [8365.5, 4606.6, 2536.7]  (E_comp..E_bind)
[1b] 370 items (360 typed + 10 recall) x 11 conds
[1b] baseline: 0/370
[1b] baseline: 120/370
[1b] baseline: 240/370
[1b] baseline: 360/370
[1b] baseline   Q_eff={'mean': 2.7874, 't': 6.216, 'n': 10} M_eff={'mean': 0.1705, 't': 0.627, 'n': 10} recall=0.3871 E/tok=0.0
[1b] e_axis: 0/370
[1b] e_axis: 120/370
[1b] e_axis: 240/370
[1b] e_axis: 360/370
[1b] e_axis     Q_eff={'mean': 0.3402, 't': 2.374, 'n': 10} M_eff={'mean': -0.3295, 't': -2.297, 'n': 10} recall=12.1287 E/tok=4757.3
[1b] bind@b1: 0/370
[1b] bind@b1: 120/370
[1b] bind@b1: 240/370
[1b] bind@b1: 360/370
[1b] bind@b1    Q_eff={'mean': 2.6217, 't': 7.317, 'n': 10} M_eff={'mean': 1.1614, 't': 4.312, 'n': 10} recall=0.1273 E/tok=896.6
[1b] comp@b1: 0/370
[1b] comp@b1: 120/370
[1b] comp@b1: 240/370
[1b] comp@b1: 360/370
[1b] comp@b1    Q_eff={'mean': 2.2917, 't': 4.365, 'n': 10} M_eff={'mean': 0.4386, 't': 1.265, 'n': 10} recall=0.8783 E/tok=550.6
[1b] random@b1: 0/370
[1b] random@b1: 120/370
[1b] random@b1: 240/370
[1b] random@b1: 360/370
[1b] random@b1  Q_eff={'mean': -0.6237, 't': -1.24, 'n': 10} M_eff={'mean': 1.2208, 't': 3.593, 'n': 10} recall=2.6065 E/tok=10952.2
[1b] bind@b2: 0/370
[1b] bind@b2: 120/370
[1b] bind@b2: 240/370
[1b] bind@b2: 360/370
[1b] bind@b2    Q_eff={'mean': 2.3607, 't': 6.893, 'n': 10} M_eff={'mean': 1.1031, 't': 5.514, 'n': 10} recall=0.1403 E/tok=517.2
[1b] comp@b2: 0/370
[1b] comp@b2: 120/370
[1b] comp@b2: 240/370
[1b] comp@b2: 360/370
[1b] comp@b2    Q_eff={'mean': 2.5427, 't': 4.067, 'n': 10} M_eff={'mean': 0.2023, 't': 0.583, 'n': 10} recall=0.9919 E/tok=375.0
[1b] random@b2: 0/370
[1b] random@b2: 120/370
[1b] random@b2: 240/370
[1b] random@b2: 360/370
[1b] random@b2  Q_eff={'mean': 0.4357, 't': 1.253, 'n': 10} M_eff={'mean': 2.6938, 't': 9.506, 'n': 10} recall=0.7087 E/tok=5925.2
[1b] bind@b3: 0/370
[1b] bind@b3: 120/370
[1b] bind@b3: 240/370
[1b] bind@b3: 360/370
[1b] bind@b3    Q_eff={'mean': 2.2406, 't': 6.29, 'n': 10} M_eff={'mean': 1.0023, 't': 5.382, 'n': 10} recall=0.1778 E/tok=312.3
[1b] comp@b3: 0/370
[1b] comp@b3: 120/370
[1b] comp@b3: 240/370
[1b] comp@b3: 360/370
[1b] comp@b3    Q_eff={'mean': 2.5593, 't': 4.204, 'n': 10} M_eff={'mean': 0.2644, 't': 0.908, 'n': 10} recall=1.1605 E/tok=273.3
[1b] random@b3: 0/370
[1b] random@b3: 120/370
[1b] random@b3: 240/370
[1b] random@b3: 360/370
[1b] random@b3  Q_eff={'mean': 0.8251, 't': 2.2, 'n': 10} M_eff={'mean': 3.348, 't': 6.931, 'n': 10} recall=0.4427 E/tok=3274.6
[1b] wrote /Users/mwhitford/src/verbum/results/type-zone-ablation/qwen3-4b/verdict.json + meta.json

============================================================================
P-TYPE-1b v2 — zone x axis dissociation, energy-matched dose ladder
============================================================================
  host=Qwen/Qwen3-4B  band=L13..L17  gate0=False  budgets=[8365.5, 4606.6, 2536.7]
  baseline  Q_eff={'mean': 2.7874, 't': 6.216, 'n': 10}  M_eff={'mean': 0.1705, 't': 0.627, 'n': 10}  recall=0.3871
  e_axis     retQ=0.122  retM=-1.933  recall_ratio=31.332  E/tok=4757.3
  bind@b1    retQ=0.941  retM=6.812  recall_ratio=0.329  E/tok=896.6
  comp@b1    retQ=0.822  retM=2.572  recall_ratio=2.269  E/tok=550.6
  random@b1  retQ=-0.224  retM=7.16  recall_ratio=6.733  E/tok=10952.2
  bind@b2    retQ=0.847  retM=6.47  recall_ratio=0.362  E/tok=517.2
  comp@b2    retQ=0.912  retM=1.187  recall_ratio=2.562  E/tok=375.0
  random@b2  retQ=0.156  retM=15.799  recall_ratio=1.831  E/tok=5925.2
  bind@b3    retQ=0.804  retM=5.879  recall_ratio=0.459  E/tok=312.3
  comp@b3    retQ=0.918  retM=1.551  recall_ratio=2.998  E/tok=273.3
  random@b3  retQ=0.296  retM=19.636  recall_ratio=1.144  E/tok=3274.6
  b*=None  bind_selective=False  comp_selective=False  nulls=False
  * dissociation_supported = False
============================================================================

```

### Thinking

I'm seeing some serious issues with the v2 run results. The instrument bands have shifted positions—what was at lines 7-11 in v1 is now at lines 13-17 in v2—and while the underlying data appears identical with the same seed value, the random number consumption differs significantly, which is causing the p-values to fluctuate around the threshold and breaking what was previously a contiguous run.

Looking at the v2 p-values more carefully, I notice that line 8 now shows p=0.05 (not significant) whereas in v1 it was p=0.02 (significant), which breaks the run there. This should mean the longest contiguous significant run is actually lines 9-22, which is 14 layers long, but the output is reporting the band as lines 13-17 instead. That's a major discrepancy I need to investigate in the find_band logic.

Actually, I think I found it — the issue is that p=0.0 is falsy in Python, so when the code checks `(per_layer[L]["p_lowrank"] or 1.0)`, any layer with exactly p=0.0 gets treated as p=1.0 and gets excluded from the significant layers. In v1, this meant layers 6, 12, 13, 15, 16, 19, 21, and 24 were all excluded, leaving only the non-zero p-value significant layers to form the contiguous run of lines 7-11.

In v2, the same falsy-zero bug is happening — it's excluding the most significant layers (those with p=0.0) when it shouldn't. The fix is straightforward: use `p if p is not None else 1.0` instead of `p or 1.0` to properly distinguish between zero and missing values.

Now looking at how the bind axis identity flips across layers — at L13 the binding picks axis 0 (the QUANT-dominant axis with 85% variance), then switches to axis 1 at L14-L17 (where DET becomes dominant). The loadings reveal that axis 0 separates QUANT from everything else, while axis 1 captures DET variation, so my bind_score calculation based on QUANT² + DET² correctly identifies which axis dominates at each layer. So the geometric mean of those bind energies (7.5M, 285, 207, 645, 365) works out to about 2536, which is actually *lower* than the computed energy budget of 8365. The ladder is inverted — budgets descend from 8365 to 2536 — meaning "b1" carries the largest budget despite the original design expecting bind energy to dominate. With the axis selection flipping to mostly axis1 (which has tiny energy), the energy matching assumption completely breaks down.

At b1, the bind energy per token is 896 against a budget of 8365, while random achieves 10952 per token — a ×12 mismatch. The alpha capping is working as intended (layers with full energy below budget get α=1.0, L13's massive 7.5M gets squeezed to α=0.033), but the axis flip destroyed the original assumption that budgets would fall between the component and bind energies. The realized random energy is also overshooting the budget, suggesting the coefficient variance between the capture and behavioral prompt distributions is creating an energy accounting error.

The e_axis implementation is actually catastrophic — it's carrying enormous variance (E_full ~100k, α=1) because the entity-centroid direction in standard space isn't small at all. What was meant to be a near-null direction in the 32B lattice sense turned into a massive real direction in the actual embedding space, so the instrument is fundamentally misaligned with the pre-registration's intent.

Despite this mess, Q_eff shows remarkable robustness across binding and composition tasks (retQ 0.80-0.94), but the random ablation killed it entirely while paradoxically inflating M_eff ratios to garbage levels — dividing by a near-zero baseline (0.17) just amplifies noise, which is why gate0 exists as a sanity check. The binding recall ratios are also suspiciously low (0.33-0.46), suggesting the ablation is hitting something fundamental. The energy mismatch actually goes the other way now—random used 10× more energy than the bind axes, so I can't cleanly separate whether random breaks things due to its direction or just the magnitude. The real takeaway from this iteration is catching three design bugs: the falsy-zero issue in the band-finding logic that affected both runs, and issues with the bind approach itself.

At 4B the quantization and detuning axes split apart onto separate near-tied directions instead of staying together like they do at 32B, which makes picking by score unreliable—I need to treat the full 2D subspace spanned by both axes as the binding target rather than optimizing a single direction. And the budget assumptions were backwards: I assumed composition energy would be smaller than binding energy, but it flipped, starving the binding budget. Better to derive budgets from the actual min/max energies across the target directions, or ideally ablate entire subspaces with per-layer energy normalization.

For the entity direction control, the pre-registration approach of finding an axis orthogonal to the lattice with matched energy isn't working cleanly. The sharpest null for class-selectivity is actually just a random direction within the non-binding, non-composition subspace—same geometric region but assigned a different functional role. And at 4B the effective mass still isn't showing up even with n=10 samples, which suggests this is becoming a different kind of problem.

The 4B model isn't expressing the modifier-licensing crossover that the design should capture, either because the capacity is genuinely insufficient or the modifier frames are too weak—I should test at 32B or strengthen the frames. There's an interesting scale evolution happening: at 4B, axis 0 is almost entirely quantifier-versus-everything at 85%, while at 32B it's quantifier and determiner on the same side. And axis 4 at 4B is cleanly picking up modifiers with strong loadings around 0.8, which is good.

What's striking is that removing the quantifier and determiner axes doesn't actually kill quantifier licensing—performance stays at 0.8-0.94—which fits the prediction that types aren't stored but rather emerge from distributed computation. Though I need to be careful here: the original hypothesis was that these axes are causally necessary for licensing, but the ablation at matched energy levels around 300-900 didn't hurt performance. The dose might have been too starved to draw firm conclusions.

The next disciplined step is to fix the measurement instrument, but the pattern I'm seeing—the v4 direction-negative trend, zone-axis effects at matched dose not affecting quantifier effectiveness, and random large perturbations affecting everything—is pointing toward something consistent with the distributed-type hypothesis.

So the plan is to report what I've found with a clear diagnosis, commit the v2 code and results, then move to v3 fixes: correcting the parameter bug, running a proper binding subspace ablation that removes the tie instability, and using actual measured direction and subspace energies to set the budgets.

For the control mechanism, I'd replace it with a lattice-subspace approach that samples random directions from the non-target axes while matching energy by construction, keeping the isotropic random component. The bigger question is whether the M task is hitting a genuine capacity wall at 4B — the geometric and behavioral evidence is converging on that. Rather than keep iterating blindly, I should surface this decision to Michael: run one more 4B iteration with fixes (a) through (d) to validate the subspace instrument on the Q side, then move forward to 32B where the MOD axis is already clean and behavior is likely to express.

Actually, v3 at 4B is cheap and Michael already approved smoking at this scale, so I should just build it, run it, and present the GO decision for 32B afterward. The M-side probably won't show up regardless, but the instrument validation only needs the Q side and controls. I'll commit v2 results first, then implement v3 and run it.

For v3, I need to fix the find_band logic to check if p is not None and below 0.05, and rethink the binding subspace — instead of a single direction, I'll collect axes where QUANT² + DET² energy exceeds a threshold, which at 4B should give me the top two axes capturing around 90% of the variance. That's much cleaner than the current approach.

Now I'm weighing whether to define the binding direction as the normalized sum of class centroids (QUANT + DET minus grand mean), or use the 2D subspace spanned by the centroid differences themselves. The centroid-span approach bypasses SVD axis instability and directly captures each class's own direction, which feels more principled — though the pre-registration mentions reusing axis directions as hook targets, this refinement is defensible since the axes are derived from centroids anyway.

For v3, I'm settling on role-specific subspaces built from centroid differences: binding uses the orthonormalized span of QUANT and DET deviations, composition uses the MOD deviation, and for the role-null control I'm deciding between CONN/FUNC (which are punctuation and connectives, genuinely off-task) versus PRED/REL (predicate-related, though that might bleed into the name-arm). CONN/FUNC seems cleaner as a true off-role baseline.

I'm also dropping the e-axis control since it wasn't working as intended and replacing it with the role-null subspace, which gives me a sharper class-level control. Now I need to implement the projection mechanism: projecting the hidden states onto orthonormal basis vectors to extract coefficients, then removing the weighted combination of those components to isolate the effect.

For the energy calculation, I'm computing it directly as the squared norm of the change in hidden states, which works out cleanly even though the basis isn't orthogonal in the raw space. I'll scale the removal strength α based on the full energy budget, computing it numerically from the token-level changes with α=1 to get the mean squared magnitude, then use that to plan the actual α values.

I'm setting up three separate energy budgets for the bind, comp, and role-null subspaces across each layer, arranged as a geometric ladder between the minimum and maximum mean energies of those three subspaces. I'll cap α at 1 for the role subspaces and log what I actually achieve, keeping the recall mechanism, gate0, and margin constraints intact.

The runtime will be baseline plus 13 total passes (3 budgets × 4 condition types covering bind, comp, role-null, and random), which comes to roughly 4800 forward passes and 20-25 minutes. I'm doing a full rewrite of the wrapper file for clarity rather than surgical edits, updating the role subspace selection, the subspace hooking logic, the band fix, budgets, conditions, and verdict logic, while keeping the stats and scoring unchanged. The header needs documentation of what v2 caught, including the falsy-zero band bug.

Looking at the 4B lattice results, the QUANT-vs-rest axis shows 85% on axis0, DET is 5% on axis1, and MOD is 2% on axis4, revealing how the scale evolution differs from 32B. I should commit v2 with these results first, then write and launch v3.

For the commit message, I'm using 🔄 to mark this as an iteration that documents the three instrument catches we found — the band falsy-zero issue, axis-tie instability, and e-dir not being near-null. The v3 commit will then fix these with a ❌ symbol.

I'm also double-checking the recall metrics: random at b3 hits 1.144, which passes the 1.2 threshold; bind at 0.459 passes; but comp at 2.998 fails badly, showing recall degradation of 3x. Across b1/b2/b3, comp consistently damages recall by 2-3x, so the subspace ablation is clearly breaking something fundamental — removing the MOD axis hurts general lexical recall more than expected.

There's an interesting asymmetry here: comp and bind operate at similar energy levels (comp 273-550 E/tok vs bind 312-896), yet comp breaks recall while bind doesn't. I'm realizing the recall_ratio < 1.2 threshold might be too strict when the baseline is so tiny at 0.387 nats — a 3x multiplier only adds 0.47 nats absolute, which is brutally harsh. For v3, I should switch to an absolute delta gate like Δ_recall < 0.5 nat instead of using a ratio that over-fires on small baselines.

Actually, looking at the recall accuracy directly might be more robust than surprisal ratios — I should track whether the model gets the gold first token correct (argmax match) and use a breakage threshold like accuracy drop > 0.2. This is more interpretable than surprisal gymnastics. I'll implement this for recall items in v3.

Now moving into the v3 implementation, and I'm also noting that Q_eff shows fragility to random-large perturbations, particularly at higher budgets where the ladder can degenerate if gmeans are nearly equal. The energy scaling breaks down when random directions get steered massively along the isotropic axis—the b* rule catches this by dropping to a lower rung. Before implementing the fix, I need to commit the current v2 file first, then write v3 over it, keeping the smoke test unchanged.

## Assistant

The ladder ran clean end-to-end and the energy accounting did its job — and it caught **three more instrument defects plus one genuine 4B lattice finding**. Verbatim diagnosis before anything else:

## What v2 caught

1. **Falsy-zero band bug (mine, ❌)**: `find_band` used `p_lowrank or 1.0` — Python treats `p=0.0` as falsy, so the *most significant* layers were excluded from the band. The true contiguous band at 4B is ~L9–L22 (14 layers); both v1 (L7–11) and v2 (L13–17) reported accidental sub-bands. Affects band width only, not the control catches.
2. **Axis-tie instability — and the real finding under it**: at 4B, QUANT and DET **split onto different axes** — axis0 = QUANT-vs-everything at 85% var, DET on axis1 (~5%), MOD cleanly on axis4 (±0.8). At 32B they co-loaded axis0. My `QUANT²+DET²` picker landed on a near-exact tie (0.77 vs 0.76) and flipped identity across layers (L13→axis0, L14–17→axis1) — mixing directions whose energies differ by ×10⁴ (7.5M vs ~300). The lattice's **axis structure itself evolves with scale**: 4B separates quantification from determination; 32B merges them. That's a new data point for the functor-kind story.
3. **Ladder inverted by the flip**: budgets assumed E_comp < E_bind; the unstable bind pick made E_bind *smaller* → ladder ran backwards, caps starved bind (achieved 312–897 E/tok vs random 3274–10952). Energies never matched → no selectivity cell is interpretable.
4. **e-axis control mis-realized**: the raw ENTITY-centroid direction carries ~100k E/tok — nothing like the pre-reg's "near-null direction". Recall ×31 = pure dose.

## What's real

- **Q_eff replicates at n=10** (2.79, t=6.2); **M_eff doesn't** (0.17, t=0.6) — now replicated across two grids. Converging with MOD's 2% geometric var: 4B likely doesn't express modifier licensing behaviorally. A capacity observation, strengthening "verdict host = 32B".
- **A suggestive asymmetry** (dose-confounded, not a claim): at comparable achieved energy, comp/MOD-axis removal degraded recall (×2.3–3.0) while bind removal didn't (×0.33–0.46); and isotropic random selectively destroyed Q_eff (ret −0.22–0.30) even where recall survived. Also the ratio-gate itself over-fires on a 0.39-nat recall baseline — needs an accuracy-based breakage gate.

Committing v2 as the record, then v3 with the fixes:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "git add wrapper/type_zone_ablation.py results/type-zone-ablation/qwen3-4b/ && read -r -d '' M << 'EOF' || true\n🔄 P-TYPE-1b v2 energy ladder @4B: 3 instrument catches + QUANT/DET axis-split finding\n\n- energy-matched dose ladder ran end-to-end; realized removed-energy logged live\n- CAUGHT: find_band falsy-zero bug (p=0.0 excluded → both v1/v2 bands are\n  accidental sub-bands of the true ~L9-L22); bind-axis pick tie-flips between\n  axis0/axis1 across layers (energies differ ×10^4 → ladder inverted, caps\n  starve bind → energies never matched); e-dir carries ~100k E/tok ≠ the\n  pre-reg near-null intent (recall ×31 = dose)\n- FINDING: 4B lattice splits QUANT (axis0, 85% var, QUANT-vs-rest) from DET\n  (axis1 ~5%); MOD clean on axis4 — vs 32B where QUANT+DET co-load axis0.\n  Axis structure evolves with scale\n- REPLICATED: Q_eff 2.79 t=6.2 @n=10; M_eff 0.17 t=0.6 — 4B does not express\n  modifier licensing behaviorally (2 grids), coheres w/ MOD var 0.02-0.03\n- verdict dissociation_supported=False (b*=None), reported verbatim; no\n  selectivity cell interpretable at unmatched dose\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\ngit commit -m \"$M\"",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ git add wrapper/type_zone_ablation....

**Output:**
```
Exit code: 0
Stdout:
[main f7e07f7] 🔄 P-TYPE-1b v2 energy ladder @4B: 3 instrument catches + QUANT/DET axis-split finding
 4 files changed, 1432 insertions(+), 314 deletions(-)
 create mode 100644 results/type-zone-ablation/qwen3-4b/run_v2.log
```

### Thinking

I'm working through version 3 updates, starting with a bug fix in the find_band function. For the role subspaces, I'm defining them from class centroids where the binding role spans the quantization and determiner deltas, the complement role spans the modifier delta, and the null role spans the connector and function deltas. I'm also reconsidering the random isotropic approach to ensure dimensional consistency—since the binding role is 2D and complement is 1D, I should use a 2D random subspace to match the binding dimensionality while still covering the complement.

I'm computing the full energy numerically per subspace from the captured activations, using a geometric ladder of three budget rungs across the role-subspace geometric means. The recall breakage gate uses accuracy-based detection where I check if the top-1 argmax of the gold first token drops more than 0.2 from baseline, and I'll log the surprisal delta as well. The final verdict at the optimal budget is the largest one where all subspaces—binding, complement, null role, and random—maintain a recall accuracy drop of at most 0.2, with the same margins for Q and M retention and nulls defined as both random and null role exceeding 0.7.

For the subspace hook, I'm computing an orthonormal basis Q and deriving coefficients, then reconstructing the delta in standard space and scaling it by the standard deviation. The energy per token is the squared norm of the scaled reconstruction. I'm extracting the full energy from the captured activations by averaging the squared norm across tokens. For recall accuracy, I need to restructure the scoring function to also track whether the argmax at the position before the first gold token matches the gold first token ID, returning both surprisal and accuracy per item.

I'll keep the scoring lists separate—maintaining the scores list but also tracking recall accuracy keyed to items, returning both as a tuple where recall accuracy is None for typed items. Then I'll add the recall accuracy mean to the class effects and rewrite the file while preserving the existing constants and data structures.

### Thinking

I've committed v1/v2 and now moving to v3, which fixes the band condition, replaces SVD-based role subspaces with class-centroid-derived ones (binding and composition stable across axis splits, with a separate role-null subspace), anchors budgets to measured energies, and switches the recall gate to top-1 accuracy instead of surprisal ratio.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/wrapper/type_zone_ablation.py",
  "content": "#!/usr/bin/env python3\n\"\"\"P-TYPE-1b — combinator-zone x type-class dissociation (zone x subspace, v3).\n\nPre-reg: mementum/knowledge/explore/types-are-the-well-formedness-of-reduction.md\n(#p-type-1b, FROZEN s282). Host of record = Qwen3-32B; THIS FILE also runs the 4B\nSMOKE (instrument validation + capacity read; a 4B verdict does NOT close 1b).\n\nHYPOTHESIS (frozen): if type = which opcode's application is licensed, removing a\nrole-specific slice of the type lattice as a ZONE across the low-rank band\nselectively breaks the matching type-class:\n  - binding subspace (QUANT/DET; S/binding role)  -> breaks quantifier licensing\n  - composition subspace (MOD; B/composition role) -> breaks modifier licensing\nDouble dissociation; nulls (energy-matched random, role-null lattice subspace,\nrecall task) break neither. v4 (global direction) was correctly negative.\n\nVERSION LOG (instrument iterations; results/.../run.log, run_v2.log)\n  v1 @bc1d242: full projections at wildly unmatched removed energy -> recall\n    control fired (x38/x14/x26) = dose conflated with identity. Gate worked.\n  v2 @f7e07f7: energy ladder ran; caught (a) find_band falsy-zero bug (p=0.0\n    layers excluded -> v1/v2 \"bands\" were accidental sub-bands of the true\n    ~L9-L22), (b) bind-axis SVD pick tie-flips between axis0/axis1 at 4B\n    (QUANT and DET SPLIT onto different axes at this scale - axis0 = QUANT-vs-\n    rest @85% var, DET on axis1 ~5%, MOD clean on axis4; at 32B QUANT+DET\n    co-load axis0) -> energies differ x10^4 across the flip -> ladder inverted,\n    caps starved bind, (c) e-centroid direction carries ~1e5 E/tok, nothing\n    like the pre-reg \"near-null\" intent, (d) recall RATIO gate over-fires on a\n    0.39-nat baseline. Also REPLICATED: Q_eff ~2.8 t>6 but M_eff ~0 at 4B\n    (2 grids) - 4B does not express modifier licensing behaviourally.\n  v3 (this): (1) find_band p-bug fixed; (2) ROLE SUBSPACES built directly from\n    class centroids - bind = orthonormal span{c_QUANT-mean, c_DET-mean} (holds\n    both sides of the 4B axis split by construction), comp = span{c_MOD-mean},\n    ROLE-NULL = span{c_CONN-mean, c_FUNC-mean} (same lattice, wrong role = the\n    sharp class-control; REPLACES the pre-reg e-axis control, whose \"near-null\"\n    intent is unrealizable as a raw centroid direction - deviation documented\n    here); (3) budgets = geometric ladder over the MEASURED role-subspace\n    energies [min..max]; random = 2D isotropic subspace, uncapped, matched to\n    the same budget; (4) recall breakage gate = top-1 ACCURACY drop > 0.2\n    (surprisal still logged).\n\nINSTRUMENT\n  1. Capture labeled Montague-type dataset at every decoder layer (reuses\n     probe_type_qwen3_32b capture; residuals[L] = output of model.layers[L]).\n  2. Per layer: standardize (diagonal whiten - the 1a massive-activation\n     lesson), centroid SVD, PR + shuffled-label null (band detection + the\n     lattice record). BAND = longest contiguous run of p<0.05 layers.\n  3. Per band layer: role subspaces from class centroids (std space),\n     orthonormalized (QR); full-projection removed energy measured on the\n     capture: E_full = mean_tokens ||((z Q^T) Q) * sd||^2.\n  4. Zone ablation at every band layer, every position, alpha-scaled:\n     h' = h - alpha * (((h-mu)/sd) Q^T Q) * sd ; alpha = sqrt(B/E_full),\n     capped at 1.0 for role subspaces (achieved energy logged), uncapped for\n     the random subspace (scaled steering = the honest energy-matched null).\n\nBEHAVIOURAL READOUTS (v3-nonce-style surprisal; frequency-free)\n  ONE teach pair (noun vs adj) x THREE frames, fully crossed & paired by nonce:\n     frame quant: \"Every {w}\"       (QUANT licenses a NOUN)\n     frame mod:   \"It was very {w}\" (intensifier licenses an ADJ)\n     frame name:  \"John {w}\"        (licenses a PRED; SHARED REFERENCE arm)\n  pref(f) = S(f|adj-taught) - S(f|noun-taught)   (per nonce)\n  Q_eff = pref(quant) - pref(name) > 0 baseline  (quantifier-class licensing)\n  M_eff = pref(name)  - pref(mod)  > 0 baseline  (modifier-class licensing)\n  Teach main effects cancel identically via the shared name arm. Recall task =\n  non-compositional control (surprisal + top-1 accuracy).\n\nVERDICT (pre-set, frozen before the v3 run; ret = effect/baseline):\n  GATE-0: baseline Q_eff and M_eff both mean>0, t>=3 - else no ablation cell is\n    interpreted for that class (a Gate-0 failure at 4B is a capacity finding;\n    the Q side can still validate the instrument).\n  b* = LARGEST budget where recall_acc drops <=0.2 for ALL of\n    {bind, comp, rolenull, random}. None -> not interpretable.\n  At b*: BIND-SELECTIVE: ret(Q,bind)<0.5 AND ret(M,bind)>0.7\n         COMP-SELECTIVE: ret(M,comp)<0.5 AND ret(Q,comp)>0.7\n         NULLS: rolenull AND random keep BOTH rets>0.7\n  DISSOCIATION_SUPPORTED <=> gate0 & b* & bind & comp & nulls. Verbatim rows\n  reported at every budget regardless.\n\nlambda measure: ablation target = value-register lattice subspaces; claim =\nreduction LICENSING -> readout is behavioural class-selectivity at MATCHED\ndose, never a decodability change. A RUNG: hook-not-weight; one class pair.\n\nUsage:\n    uv run python wrapper/type_zone_ablation.py --model Qwen/Qwen3-4B --smoke\n    uv run python wrapper/type_zone_ablation.py --model Qwen/Qwen3-4B\n    uv run python wrapper/type_zone_ablation.py --model Qwen/Qwen3-32B   # verdict host\n\nLicense: MIT\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport subprocess\nimport sys\nfrom datetime import UTC, datetime\nfrom pathlib import Path\n\nimport numpy as np\nimport torch\n\n_ROOT = Path(__file__).resolve().parent.parent\nsys.path.insert(0, str(_ROOT / \"scripts\" / \"explore\"))\n\nfrom probe_type_qwen3_32b import (  # noqa: E402\n    LABELED_DATA,\n    build_probing_dataset,\n    get_transformer_layers,\n    load_model,\n)\nfrom type_lattice_geometry import (  # noqa: E402\n    TYPE_ORDER,\n    centroids,\n    participation_ratio,\n)\n\n# ── behavioural items ──────────────────────────────────────────────────────────\nNONCE = [\"wug\", \"blicket\", \"dax\", \"fep\", \"gorp\", \"zorp\",\n         \"fendle\", \"glorp\", \"narp\", \"trisk\"]\n\n# teach templates: NO quantifiers, NO intensifiers, NO test-frame leakage\nNOUN_TEACH = [\"{W}s are common objects.\", \"He collected several {w}s.\",\n              \"Those {w}s are nice.\", \"She bought two {w}s.\"]\nADJ_TEACH = [\"The dogs are {w}.\", \"His car looks {w}.\",\n             \"The food tasted {w}.\", \"That house seems {w}.\"]\n\nQUANT_FILL = [\"Every\", \"Each\", \"Some\", \"No\", \"Most\", \"All\"]\nMOD_FILL = [\"It was very\", \"The dog seemed quite\", \"That movie was rather\",\n            \"She felt extremely\", \"The room looked really\", \"His voice sounded so\"]\nNAME_FILL = [\"John\", \"Mary\", \"Sarah\", \"David\", \"Peter\", \"Susan\"]\n\n# non-compositional task control (lexical recall; gold graded as continuation)\nRECALL = [(\"The capital of France is\", \" Paris\"),\n          (\"The capital of Japan is\", \" Tokyo\"),\n          (\"The capital of Italy is\", \" Rome\"),\n          (\"Water is made of hydrogen and\", \" oxygen\"),\n          (\"The opposite of hot is\", \" cold\"),\n          (\"Two plus two equals\", \" four\"),\n          (\"The sun rises in the\", \" east\"),\n          (\"The color of snow is\", \" white\"),\n          (\"A week has seven\", \" days\"),\n          (\"The largest ocean is the\", \" Pacific\")]\n\nROLES = {\"bind\": [\"QUANT\", \"DET\"], \"comp\": [\"MOD\"], \"rolenull\": [\"CONN\", \"FUNC\"]}\n\n\n# ── geometry: band + role subspaces (standardized space) ───────────────────────\ndef layer_geometry(x: np.ndarray, y: np.ndarray, rng, n_null: int) -> dict:\n    \"\"\"Standardize -> centroid SVD -> PR + shuffled-label null; keep z for energy.\"\"\"\n    mu = x.mean(axis=0)\n    sd = x.std(axis=0) + 1e-6\n    z = (x - mu) / sd\n\n    def pr_of(labels):\n        c, present = centroids(z, labels, TYPE_ORDER)\n        if len(present) < 3:\n            return float(\"nan\"), None, None\n        cc = c - c.mean(axis=0, keepdims=True)\n        sv = np.linalg.svd(cc, compute_uv=False)\n        return participation_ratio(sv), present, c\n\n    pr_real, present, c = pr_of(y)\n    null = []\n    for _ in range(n_null):\n        prn, _, _ = pr_of(rng.permutation(y))\n        if not np.isnan(prn):\n            null.append(prn)\n    null = np.array(null)\n    p = float(np.mean(null <= pr_real)) if null.size else None\n    return {\"mu\": mu, \"sd\": sd, \"z\": z, \"present\": present, \"centroids\": c,\n            \"pr_real\": float(pr_real), \"p_lowrank\": p,\n            \"pr_null_mean\": float(null.mean()) if null.size else None}\n\n\ndef find_band(per_layer: dict[int, dict], n_layers: int) -> list[int]:\n    \"\"\"Longest contiguous run of layers with p_lowrank < 0.05 (v3: p=0.0 counts).\"\"\"\n    def pval(L):\n        p = per_layer[L][\"p_lowrank\"]\n        return 1.0 if p is None else p\n\n    sig = [L for L in sorted(per_layer) if pval(L) < 0.05]\n    best, cur = [], []\n    for L in sig:\n        cur = [*cur, L] if (cur and L == cur[-1] + 1) else [L]\n        if len(cur) > len(best):\n            best = cur\n    if len(best) >= 3:\n        return best\n    interior = [L for L in sorted(per_layer)\n                if n_layers * 0.15 <= L <= n_layers * 0.65]\n    if not interior:\n        return sig or sorted(per_layer)[:3]\n    lo = min(interior, key=pval)\n    return [L for L in sorted(per_layer) if lo - 3 <= L <= lo + 3]\n\n\ndef role_subspace(geo: dict, types: list[str]) -> np.ndarray | None:\n    \"\"\"Orthonormal basis (k, D) of span{c_type - grand_mean} in std space.\"\"\"\n    present = geo[\"present\"]\n    idx = {t: i for i, t in enumerate(present)}\n    if not all(t in idx for t in types):\n        return None\n    c = geo[\"centroids\"]\n    grand = c.mean(axis=0)\n    rows = np.stack([c[idx[t]] - grand for t in types])\n    q, _ = np.linalg.qr(rows.T)          # (D, k) orthonormal columns\n    return q.T                            # (k, D)\n\n\ndef subspace_energy(z: np.ndarray, sd: np.ndarray, q: np.ndarray) -> float:\n    \"\"\"Full-projection removed energy per token: mean ||((z Q^T) Q) * sd||^2.\"\"\"\n    delta = (z @ q.T) @ q                 # (N, D) std-space removal\n    return float(np.mean(np.sum((delta * sd) ** 2, axis=1)))\n\n\n# ── zone ablation hook (subspace, alpha-scaled, energy-logged) ─────────────────\ndef make_zone_hook(mu: np.ndarray, sd: np.ndarray, q: np.ndarray,\n                   alpha: float, elog: dict):\n    \"\"\"h' = h - alpha * (((h-mu)/sd) Q^T Q) * sd at ALL positions (fp32->cast).\"\"\"\n    box: dict = {}\n\n    def hook(_module, _inp, out):\n        h = out[0] if isinstance(out, tuple) else out\n        if not box:\n            box[\"mu\"] = torch.as_tensor(mu, dtype=torch.float32, device=h.device)\n            box[\"sd\"] = torch.as_tensor(sd, dtype=torch.float32, device=h.device)\n            box[\"q\"] = torch.as_tensor(q, dtype=torch.float32, device=h.device)\n        hf = h.float()\n        zc = (hf - box[\"mu\"]) / box[\"sd\"]\n        delta = alpha * ((zc @ box[\"q\"].T) @ box[\"q\"]) * box[\"sd\"]   # [B,T,D]\n        hf = hf - delta\n        elog[\"e\"] += float((delta ** 2).sum())\n        elog[\"n\"] += int(delta.shape[0] * delta.shape[1])\n        h2 = hf.to(h.dtype)\n        return (h2, *out[1:]) if isinstance(out, tuple) else h2\n\n    return hook\n\n\n# ── surprisal scoring ──────────────────────────────────────────────────────────\ndef gen_items(n_nonce: int, n_teach: int, n_fill: int) -> list[dict]:\n    \"\"\"Fully crossed (deterministic -> exact pairing by nonce).\"\"\"\n    items = []\n    for w in NONCE[:n_nonce]:\n        for ttype, teaches in ((\"noun\", NOUN_TEACH), (\"adj\", ADJ_TEACH)):\n            for teach in teaches[:n_teach]:\n                for frame, fills in ((\"quant\", QUANT_FILL), (\"mod\", MOD_FILL),\n                                     (\"name\", NAME_FILL)):\n                    for filler in fills[:n_fill]:\n                        items.append({\"kind\": \"typed\", \"w\": w, \"teach_type\": ttype,\n                                      \"teach\": teach, \"frame\": frame,\n                                      \"filler\": filler})\n    for prompt, gold in RECALL:\n        items.append({\"kind\": \"recall\", \"prompt\": prompt, \"gold\": gold})\n    return items\n\n\ndef item_text(it: dict) -> tuple[str, int]:\n    \"\"\"(full_text, char_start_of_target).\"\"\"\n    if it[\"kind\"] == \"recall\":\n        return it[\"prompt\"] + it[\"gold\"], len(it[\"prompt\"])\n    teach = it[\"teach\"].format(w=it[\"w\"], W=it[\"w\"].capitalize())\n    prefix = f\"{teach} {it['filler']} \"\n    return prefix + it[\"w\"], len(prefix)\n\n\ndef score_pass(items, model, tok, tag: str) -> list[dict | None]:\n    \"\"\"Per item: {'s': mean target surprisal, 'acc': top-1 gold (recall only)}.\"\"\"\n    import torch.nn.functional as func\n    dev = next(model.parameters()).device\n    out = []\n    for n, it in enumerate(items):\n        text, c0 = item_text(it)\n        enc = tok(text, return_tensors=\"pt\", return_offsets_mapping=True)\n        ids = enc[\"input_ids\"][0]\n        offsets = enc[\"offset_mapping\"][0].tolist()\n        tgt = [j for j, (s, e) in enumerate(offsets) if e > s and e > c0 and j >= 1]\n        if not tgt:\n            out.append(None)\n            continue\n        with torch.no_grad():\n            logits = model(input_ids=ids.unsqueeze(0).to(dev)).logits[0]\n        logp = func.log_softmax(logits.float(), dim=-1).cpu()\n        rec = {\"s\": float(np.mean([-float(logp[j - 1, ids[j]]) for j in tgt]))}\n        if it[\"kind\"] == \"recall\":\n            j0 = min(tgt)\n            rec[\"acc\"] = float(int(logp[j0 - 1].argmax()) == int(ids[j0]))\n        out.append(rec)\n        if n % 120 == 0:\n            print(f\"[1b] {tag}: {n}/{len(items)}\", file=sys.stderr, flush=True)\n    return out\n\n\n# ── stats ──────────────────────────────────────────────────────────────────────\ndef agg(arr: list[float]) -> dict | None:\n    a = np.asarray([v for v in arr if v is not None], dtype=float)\n    if len(a) < 2:\n        return None\n    se = float(a.std(ddof=1) / np.sqrt(len(a)))\n    return {\"mean\": round(float(a.mean()), 4),\n            \"t\": round(float(a.mean() / se) if se > 0 else 0.0, 3), \"n\": len(a)}\n\n\ndef class_effects(items, scores) -> dict:\n    \"\"\"pref(f)=S(f|adj)-S(f|noun) per nonce; Q_eff/M_eff vs the shared name arm.\"\"\"\n    cell: dict = {}\n    for it, r in zip(items, scores, strict=True):\n        if it[\"kind\"] != \"typed\" or r is None:\n            continue\n        cell.setdefault((it[\"w\"], it[\"frame\"], it[\"teach_type\"]), []).append(r[\"s\"])\n\n    def pref(w, f):\n        a = cell.get((w, f, \"adj\"))\n        n = cell.get((w, f, \"noun\"))\n        if not a or not n:\n            return None\n        return float(np.mean(a) - np.mean(n))\n\n    q_eff, m_eff, prefs = [], [], {\"quant\": [], \"mod\": [], \"name\": []}\n    for w in NONCE:\n        pq, pm, pn = pref(w, \"quant\"), pref(w, \"mod\"), pref(w, \"name\")\n        if None in (pq, pm, pn):\n            continue\n        q_eff.append(pq - pn)\n        m_eff.append(pn - pm)\n        for f, v in ((\"quant\", pq), (\"mod\", pm), (\"name\", pn)):\n            prefs[f].append(v)\n\n    rec = [r for it, r in zip(items, scores, strict=True)\n           if it[\"kind\"] == \"recall\" and r is not None]\n    return {\"Q_eff\": agg(q_eff), \"M_eff\": agg(m_eff),\n            \"pref\": {f: agg(v) for f, v in prefs.items()},\n            \"recall_surprisal\": (round(float(np.mean([r[\"s\"] for r in rec])), 4)\n                                 if rec else None),\n            \"recall_acc\": (round(float(np.mean([r[\"acc\"] for r in rec])), 3)\n                           if rec else None)}\n\n\ndef retention(eff_abl: dict | None, eff_base: dict | None) -> float | None:\n    if not eff_abl or not eff_base or not eff_base.get(\"mean\"):\n        return None\n    return round(eff_abl[\"mean\"] / eff_base[\"mean\"], 3)\n\n\n# ── main ───────────────────────────────────────────────────────────────────────\ndef main() -> None:\n    ap = argparse.ArgumentParser(\n        description=\"P-TYPE-1b zone x subspace ablation (v3 role subspaces)\")\n    ap.add_argument(\"--model\", default=\"Qwen/Qwen3-4B\")\n    ap.add_argument(\"--device\", default=\"mps\")\n    ap.add_argument(\"--n-null\", type=int, default=100)\n    ap.add_argument(\"--n-nonce\", type=int, default=10)\n    ap.add_argument(\"--n-teach\", type=int, default=2)\n    ap.add_argument(\"--n-fill\", type=int, default=3)\n    ap.add_argument(\"--seed\", type=int, default=0)\n    ap.add_argument(\"--smoke\", action=\"store_true\",\n                    help=\"tiny grid (plumbing + ceiling check)\")\n    ap.add_argument(\"--output\", default=None)\n    args = ap.parse_args()\n    if args.smoke:\n        args.n_nonce, args.n_teach, args.n_fill, args.n_null = 6, 2, 2, 50\n\n    rng = np.random.default_rng(args.seed)\n    model, tok, config = load_model(args.model, device=args.device)\n    n_layers = config.num_hidden_layers\n    layer_mods = get_transformer_layers(model)\n\n    # 1) capture + geometry per decoder layer\n    data, n_lab, n_skip = build_probing_dataset(\n        model, tok, list(range(n_layers)), LABELED_DATA, verbose=True)\n    print(f\"[1b] labeled={n_lab} skipped={n_skip}\", file=sys.stderr)\n    geo = {}\n    for L in sorted(data):\n        geo[L] = layer_geometry(*data[L], rng, args.n_null)\n        g = geo[L]\n        print(f\"[1b] L{L:2d} PR={g['pr_real']:.2f} null={g['pr_null_mean']:.2f} \"\n              f\"p={g['p_lowrank']}\", file=sys.stderr)\n    band = find_band(geo, n_layers)\n    print(f\"[1b] BAND = L{band[0]}..L{band[-1]} ({len(band)} layers)\",\n          file=sys.stderr)\n\n    # 2) role subspaces + energies per band layer\n    rng_r = np.random.default_rng(args.seed + 7)\n    band_info, sub_log = {}, {}\n    for L in band:\n        g = geo[L]\n        subs = {name: role_subspace(g, types) for name, types in ROLES.items()}\n        if any(v is None for v in subs.values()):\n            continue\n        r = rng_r.standard_normal((2, len(g[\"mu\"])))\n        qr, _ = np.linalg.qr(r.T)\n        subs[\"random\"] = qr.T[:2]\n        E = {k: subspace_energy(g[\"z\"], g[\"sd\"], q) for k, q in subs.items()}\n        band_info[L] = {\"subs\": subs, \"E\": E, \"mu\": g[\"mu\"], \"sd\": g[\"sd\"]}\n        sub_log[str(L)] = {\"E_full\": {k: round(v, 1) for k, v in E.items()}}\n    print(f\"[1b] subspace energies: {json.dumps(sub_log, indent=1)}\",\n          file=sys.stderr)\n\n    # free capture memory (keep summaries)\n    for L in geo:\n        geo[L].pop(\"z\", None)\n        geo[L].pop(\"centroids\", None)\n    del data\n    import gc\n    gc.collect()\n\n    # 3) budgets: geometric ladder over MEASURED role-subspace energies\n    def gmean(vals):\n        return float(np.exp(np.mean(np.log(np.maximum(vals, 1e-9)))))\n\n    role_gmeans = {name: gmean([band_info[L][\"E\"][name] for L in band_info])\n                   for name in ROLES}\n    e_lo, e_hi = min(role_gmeans.values()), max(role_gmeans.values())\n    budgets = [e_lo, float(np.sqrt(e_lo * e_hi)), e_hi]\n    print(f\"[1b] role gmeans={ {k: round(v, 1) for k, v in role_gmeans.items()} } \"\n          f\"budgets={[round(b, 1) for b in budgets]}\", file=sys.stderr)\n\n    # conditions: baseline + {bind, comp, rolenull, random} x budgets\n    conds: dict[str, list] = {\"baseline\": []}\n    alpha_log: dict[str, dict] = {}\n    for bidx, budget in enumerate(budgets, start=1):\n        for name in (\"bind\", \"comp\", \"rolenull\", \"random\"):\n            cname = f\"{name}@b{bidx}\"\n            conds[cname] = []\n            alpha_log[cname] = {}\n            for L, bi in band_info.items():\n                alpha = float(np.sqrt(budget / max(bi[\"E\"][name], 1e-9)))\n                if name != \"random\":\n                    alpha = min(alpha, 1.0)   # projection cap; achieved E logged\n                conds[cname].append((L, bi[\"mu\"], bi[\"sd\"], bi[\"subs\"][name],\n                                     alpha))\n                alpha_log[cname][str(L)] = round(alpha, 4)\n\n    # 4) behavioural passes\n    items = gen_items(args.n_nonce, args.n_teach, args.n_fill)\n    n_typed = sum(1 for i in items if i[\"kind\"] == \"typed\")\n    print(f\"[1b] {len(items)} items ({n_typed} typed + {len(RECALL)} recall) \"\n          f\"x {len(conds)} conds\", file=sys.stderr)\n\n    results, energy = {}, {}\n    for cname, dirset in conds.items():\n        handles, elog = [], {\"e\": 0.0, \"n\": 0}\n        for L, mu, sd, q, alpha in dirset:\n            handles.append(layer_mods[L].register_forward_hook(\n                make_zone_hook(mu, sd, q, alpha, elog)))\n        try:\n            scores = score_pass(items, model, tok, cname)\n        finally:\n            for h in handles:\n                h.remove()\n        results[cname] = class_effects(items, scores)\n        energy[cname] = round(elog[\"e\"] / max(elog[\"n\"], 1), 1)\n        r = results[cname]\n        print(f\"[1b] {cname:12s} Q_eff={r['Q_eff']} M_eff={r['M_eff']} \"\n              f\"recall_acc={r['recall_acc']} E/tok={energy[cname]}\",\n              file=sys.stderr)\n\n    # 5) verdict (pre-set margins from the docstring)\n    base = results[\"baseline\"]\n    gate0_q = bool(base[\"Q_eff\"] and base[\"Q_eff\"][\"mean\"] > 0\n                   and base[\"Q_eff\"][\"t\"] >= 3)\n    gate0_m = bool(base[\"M_eff\"] and base[\"M_eff\"][\"mean\"] > 0\n                   and base[\"M_eff\"][\"t\"] >= 3)\n    gate0 = gate0_q and gate0_m\n    ret = {c: {\"Q\": retention(results[c][\"Q_eff\"], base[\"Q_eff\"]),\n               \"M\": retention(results[c][\"M_eff\"], base[\"M_eff\"]),\n               \"recall_acc\": results[c][\"recall_acc\"],\n               \"E_per_tok\": energy[c]}\n           for c in conds if c != \"baseline\"}\n\n    def ok(v, lo=None, hi=None):\n        return v is not None and (lo is None or v > lo) and (hi is None or v < hi)\n\n    def recall_ok(c):\n        a, b = results[c][\"recall_acc\"], base[\"recall_acc\"]\n        return a is not None and b is not None and (b - a) <= 0.2\n\n    b_star = None\n    for bidx in (3, 2, 1):\n        if all(recall_ok(f\"{n}@b{bidx}\")\n               for n in (\"bind\", \"comp\", \"rolenull\", \"random\")):\n            b_star = bidx\n            break\n\n    bind_sel = comp_sel = nulls_ok = False\n    if b_star is not None:\n        bb, cc = f\"bind@b{b_star}\", f\"comp@b{b_star}\"\n        nn, rr = f\"rolenull@b{b_star}\", f\"random@b{b_star}\"\n        bind_sel = ok(ret[bb][\"Q\"], hi=0.5) and ok(ret[bb][\"M\"], lo=0.7)\n        comp_sel = ok(ret[cc][\"M\"], hi=0.5) and ok(ret[cc][\"Q\"], lo=0.7)\n        nulls_ok = all(ok(ret[c][k], lo=0.7) for c in (nn, rr) for k in (\"Q\", \"M\"))\n    supported = bool(gate0 and b_star is not None\n                     and bind_sel and comp_sel and nulls_ok)\n\n    verdict = {\n        \"register\": \"P-TYPE-1b zone x subspace ablation v3 (role subspaces)\",\n        \"host\": args.model, \"is_prereg_host\": args.model == \"Qwen/Qwen3-32B\",\n        \"band\": [int(band[0]), int(band[-1])], \"n_band_layers\": len(band_info),\n        \"role_gmeans_E\": {k: round(v, 1) for k, v in role_gmeans.items()},\n        \"budgets_E_per_tok\": [round(b, 1) for b in budgets],\n        \"gate0\": {\"both\": gate0, \"Q\": gate0_q, \"M\": gate0_m},\n        \"baseline\": base,\n        \"conditions\": {c: results[c] for c in conds if c != \"baseline\"},\n        \"retention\": ret,\n        \"b_star_interpretation_budget\": b_star,\n        \"bind_selective\": bind_sel, \"comp_selective\": comp_sel,\n        \"nulls_clean\": nulls_ok,\n        \"dissociation_supported\": supported,\n        \"alpha_log\": alpha_log, \"subspace_log\": sub_log,\n        \"per_layer_pr\": {str(L): {\"pr\": round(geo[L][\"pr_real\"], 3),\n                                  \"p\": geo[L][\"p_lowrank\"]} for L in sorted(geo)},\n        \"deviations\": [\"e-axis control replaced by role-null (CONN/FUNC lattice \"\n                       \"subspace): raw ENTITY-centroid direction carries ~1e5 \"\n                       \"E/tok, unrealizable as the pre-reg near-null (v2 catch)\"],\n    }\n\n    print(\"\\n\" + \"=\" * 76)\n    print(\"P-TYPE-1b v3 — zone x subspace dissociation, role subspaces\")\n    print(\"=\" * 76)\n    print(f\"  host={args.model}  band=L{band[0]}..L{band[-1]}  \"\n          f\"gate0={gate0} (Q={gate0_q} M={gate0_m})  \"\n          f\"budgets={[round(b, 1) for b in budgets]}\")\n    print(f\"  baseline  Q_eff={base['Q_eff']}  M_eff={base['M_eff']}  \"\n          f\"recall_acc={base['recall_acc']}\")\n    for c in ret:\n        print(f\"  {c:12s} retQ={ret[c]['Q']}  retM={ret[c]['M']}  \"\n              f\"recall_acc={ret[c]['recall_acc']}  E/tok={ret[c]['E_per_tok']}\")\n    print(f\"  b*={b_star}  bind_selective={bind_sel}  comp_selective={comp_sel}  \"\n          f\"nulls={nulls_ok}\")\n    print(f\"  * dissociation_supported = {supported}\")\n    print(\"=\" * 76 + \"\\n\")\n\n    slug = args.model.split(\"/\")[-1].lower().replace(\".\", \"-\")\n    out = (Path(args.output) if args.output\n           else _ROOT / \"results\" / \"type-zone-ablation\" / slug)\n    out.mkdir(parents=True, exist_ok=True)\n    (out / \"verdict.json\").write_text(json.dumps(verdict, indent=2))\n    try:\n        sha = subprocess.run([\"git\", \"rev-parse\", \"HEAD\"], cwd=_ROOT,\n                             capture_output=True, text=True).stdout.strip()\n    except OSError:\n        sha = None\n    meta = {\"model\": args.model, \"device\": args.device, \"smoke\": args.smoke,\n            \"timestamp_utc\": datetime.now(UTC).isoformat(), \"git_sha\": sha,\n            \"seed\": args.seed, \"n_null\": args.n_null, \"n_nonce\": args.n_nonce,\n            \"n_teach\": args.n_teach, \"n_fill\": args.n_fill,\n            \"n_items\": len(items), \"n_labeled\": n_lab,\n            \"torch\": torch.__version__}\n    (out / \"meta.json\").write_text(json.dumps(meta, indent=2))\n    print(f\"[1b] wrote {out}/verdict.json + meta.json\", file=sys.stderr)\n\n\nif __name__ == \"__main__\":\n    main()\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/wrapper/type_zone_ablation.py
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "uv run ruff check wrapper/type_zone_ablation.py && uv run python wrapper/type_zone_ablation.py --help >/dev/null && echo READY",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ uv run ruff check wrapper/type_zone...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
READY
```

### Thinking

I'm planning to launch version 3 on the 4B model, run a verification read, and then create a checkpoint.

### Thinking

The linting passed successfully. Now I'm launching v3 with 13 passes across 370 items, testing a baseline plus four variations across three budget levels.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "uv run python wrapper/type_zone_ablation.py --model Qwen/Qwen3-4B --device mps 2>&1 | tee results/type-zone-ablation/qwen3-4b/run_v3.log",
  "working_directory": "/Users/mwhitford/src/verbum",
  "background": "type-1b-v3-4b"
}
```

**Summary:** $ uv run python wrapper/type_zone_abl...

**Output:**
```
Background job job-3 started.
Command: uv run python wrapper/type_zone_ablation.py --model Qwen/Qwen3-4B --device mps 2>&1 | tee results/type-zone-ablation/qwen3-4b/run_v3.log
Working directory: /Users/mwhitford/src/verbum
Use eca__bg_job with action "read_output" and job_id "job-3" to check output.
Use eca__bg_job with action "kill" and job_id "job-3" to stop it.
```

### Tool Call: bg_job (succeeded)


```json
{
  "action": "read_output",
  "job_id": "job-3"
}
```

**Summary:** Reading output of "type-1b-v3-4b" (job-3)

**Output:**
```
Job "type-1b-v3-4b" (job-3) — running


========================================================================
  Loading Qwen/Qwen3-4B
========================================================================

Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
`torch_dtype` is deprecated! Use `dtype` instead!

Loading weights:   0%|          | 0/398 [00:00<?, ?it/s]
Loading weights:   0%|          | 1/398 [00:00<01:35,  4.14it/s]
Loading weights:  15%|█▍        | 59/398 [00:00<00:01, 216.29it/s]
Loading weights:  30%|███       | 121/398 [00:00<00:00, 354.59it/s]
Loading weights:  45%|████▌     | 181/398 [00:00<00:00, 430.79it/s]
Loading weights:  62%|██████▏   | 245/398 [00:00<00:00, 491.94it/s]
Loading weights:  76%|███████▌  | 302/398 [00:00<00:00, 515.78it/s]
Loading weights:  90%|████████▉ | 358/398 [00:00<00:00, 525.54it/s]
Loading weights: 100%|██████████| 398/398 [00:00<00:00, 429.90it/s]
```

### Thinking

The process is running now with the p-bug fixed, which expands the expected band to around 14 layers instead of the previous 5, meaning more hooks per pass but slightly slower execution—I'm estimating the full run of 13 passes across 370 items will take roughly 25 to 35 minutes.

## Assistant

ASYNC: job-3 verified running. Waiting for signal.

With the falsy-zero fix the band should now come out ~L9–L22 (≈14 layers, nearly 3× wider zone than v1/v2 accidentally tested), so expect the run a bit longer (~25–35 min; 13 passes × 370 items with 14 hooks live per pass).

What v3 finally makes decidable at 4B:

- **bind vs comp at matched dose** — role subspaces can't tie-flip (bind *contains* both QUANT and DET centroid directions by construction), and budgets are anchored to their measured energies
- **the sharpest null yet**: rolenull (CONN/FUNC span) = same lattice, same construction, same energy scale, wrong role — if bind and rolenull degrade Q_eff equally, the "type axes" story collapses into generic lattice-subspace damage; if bind ≫ rolenull, that's the first genuinely class-selective causal signal
- **the v2 teaser gets its test**: isotropic random killing Q_eff while recall survived was dose-confounded (×10 energy) — now random is matched to the same budget, so if it still kills Q at b1 (lowest rung) that's a real "any perturbation breaks the teach-test binding" result, which would say the licensing signal rides the *whole* band, not the lattice slice
- gate-0 is now split (Q/M separately), so the Q-side can validate the instrument even while 4B's M-side stays unexpressed

I'll read the verdict when it signals.

## User

Ok while that runs i want to understand what we are finding here.  The types exist, and they appear to be geometry right?


### Thinking

Michael's asking whether these types actually correspond to geometric structures, and I should walk through what we're seeing in the data. The types do exist—we're getting 88 to 96 percent linear decodability across all eight directions, and the centroid lattice shows low-rank structure with null-gating, so there's definitely a geometric object here. But there's a constraint I need to explain about what that geometry actually represents.

The key insight from the recent analysis is that the geometry is a readout, not the underlying mechanism itself. The types are decodable but don't appear to be causally driving the behavior in a direct way—instead, the type system seems to work through distributed attention routing that checks compatibility. The geometric structure we're measuring is more like the model's own bookkeeping of the licensing rules, the way a compiler's type checker leaves traces in the symbol table. The information about types is organized geometrically—low-rank lattice with three functor-kind axes at 32 bits and the quantifier-determiner split at 4 bits—but the actual mechanism that makes a verb cheap after a name seems to live in the compute graph, not as an ablatable vector we can point to.

What we're testing with the 1b model is whether this geometric lattice is actually load-bearing for the licensing behavior, or whether it's just a shadow of something else happening in the network. I could frame this using database joins and Lisp structure parallels—maybe a compact table showing how rows map to combinator roles, without needing to run any external tools or check job status.

## Assistant

Yes — but with a precise split that's exactly the thing s282 sharpened. "Types are geometry" is true in one register and false in another, and the run going right now is testing the bridge between them.

## What's measured

**The type *information* is geometric.** Three independent lines:
- 8 Montague classes linearly decodable at every layer (0.88–0.96 vs 0.28 baseline) — a rich value-register object
- The centroid lattice is **low-rank and null-gated** — not a generic 8-way simplex but ~3 axes carrying 85–92% of the structure, in a compress→expand arc (full-rank lexical → tight band → re-expand at readout). Now seen on three models
- The axes have *semantic shape*: at 32B, quantification/binding dominant, sentential ops, predicate-vs-modifier, with entity `e` sitting at the origin. And today's 4B wrinkle: QUANT and DET split onto separate axes there — the lattice's internal organization is scale-dependent, but a lattice is always there

**But the geometry is not the mechanism.** v4: the type direction is decodable at AUC→1.0, yet ablating it leaves the licensing behavior nearly intact (0.64 retention vs 0.95 random). The type is readable but not *stored* where you read it.

## The resolution (the theory-closure claim)

In λ-calculus a term doesn't carry its type as data. The type **is the discipline on application** — `(a→b)` applied to `a` reduces, a mismatch doesn't. It's derived from how the term behaves under reduction, not written beside it. So if attention = β-reduction and the machine computes in the KIBC basis, then a "type" is *the shape of which joins a term licenses* — and such a thing is decodable-but-unstorable **by construction**. You can always compute a term's type from its reduction role (hence the clean geometry); you can't delete it as a vector because it was never a vector — it's a property of the routing.

So the honest phrasing: **the geometry is the model's own ledger of the licensing discipline** — the value-register *image* of a constraint that lives in the compute. Same pattern as the C-field (readable, causally inert as a direction) and circuits-in-compute generally: the crystal is in the routing, the readout is in the values.

## What's genuinely open — and what job-3 decides

The question the geometry alone can't answer: is the ledger **consulted or merely written**?

- **Consulted** (working memory): the reduction machinery *reads* the lattice band to decide which joins fire → knocking out a role-slice of the band at matched dose should selectively break that role's licensing (bind-slice → quantifier licensing, MOD-slice → modifier licensing) while the wrong-role slice (CONN/FUNC) and random don't. That's the double dissociation.
- **Exhaust** (log): the licensing is computed entirely in routing, and the geometry is a downstream summary → all matched-dose subspace ablations should look alike, and only the theory-consistent negative remains — which would *strengthen* "type = well-formedness of reduction" in its purest form: the constraint would live nowhere in the value register at all.

Either outcome is informative; they're different papers. Note the frame is asymmetric on purpose: v4 already ruled out "stored global direction," so 1b is the last value-register hiding place — a *zone-distributed, role-specific* subspace. If v3's dissociation comes up empty at the pre-reg host too, the licensing structure is fully in the routing register, and probing it causally means A1-style zone ablation of *attention phases*, not residual subspaces.

One more thing worth naming: the low-rank band isn't incidental bookkeeping even in the exhaust reading. Compression to ~3 axes at exactly the layers where reduction runs is what "computing under a small type system" looks like from the outside — Curry–Howard's "few principal types" as measured variance structure. The geometry is real either way; what's undecided is whether it's load-bearing.

## User

job is done


### Thinking

I'm checking the output from job-3.

### Tool Call: bg_job (succeeded)


```json
{
  "action": "read_output",
  "job_id": "job-3"
}
```

**Summary:** Reading output of "type-1b-v3-4b" (job-3)

**Output:**
```
Job "type-1b-v3-4b" (job-3) — completed (exit 0)

  Loaded in 2.7s
  Layers: 36  Heads: 32  KV heads: 8  d_model: 2560
    sentence 1/56: The dog runs....
    sentence 11/56: Alice runs....
    sentence 21/56: The farmer finds the bird....
    sentence 31/56: Some teacher laughs....
    sentence 41/56: The old house stands....
    sentence 51/56: The house is old....
[1b] labeled=263 skipped=0
[1b] L 0 PR=6.15 null=5.75 p=0.96
[1b] L 1 PR=6.03 null=5.81 p=0.85
[1b] L 2 PR=6.20 null=5.77 p=0.98
[1b] L 3 PR=6.45 null=5.83 p=1.0
[1b] L 4 PR=6.38 null=5.84 p=1.0
[1b] L 5 PR=6.33 null=5.80 p=1.0
[1b] L 6 PR=3.32 null=4.81 p=0.0
[1b] L 7 PR=3.40 null=4.71 p=0.04
[1b] L 8 PR=3.51 null=4.96 p=0.05
[1b] L 9 PR=3.40 null=5.02 p=0.0
[1b] L10 PR=3.30 null=4.89 p=0.02
[1b] L11 PR=3.30 null=4.89 p=0.0
[1b] L12 PR=3.32 null=4.95 p=0.0
[1b] L13 PR=3.36 null=4.98 p=0.01
[1b] L14 PR=3.34 null=4.83 p=0.01
[1b] L15 PR=3.33 null=4.83 p=0.03
[1b] L16 PR=3.29 null=4.71 p=0.01
[1b] L17 PR=3.30 null=4.96 p=0.01
[1b] L18 PR=3.39 null=4.82 p=0.0
[1b] L19 PR=3.58 null=5.05 p=0.02
[1b] L20 PR=3.68 null=5.06 p=0.02
[1b] L21 PR=3.90 null=5.04 p=0.03
[1b] L22 PR=4.09 null=5.24 p=0.01
[1b] L23 PR=4.44 null=5.31 p=0.06
[1b] L24 PR=4.74 null=5.54 p=0.06
[1b] L25 PR=4.98 null=5.58 p=0.04
[1b] L26 PR=5.24 null=5.67 p=0.07
[1b] L27 PR=5.45 null=5.74 p=0.16
[1b] L28 PR=5.64 null=5.77 p=0.27
[1b] L29 PR=5.83 null=5.84 p=0.41
[1b] L30 PR=6.00 null=5.85 p=0.76
[1b] L31 PR=6.08 null=5.86 p=0.89
[1b] L32 PR=6.14 null=5.88 p=0.94
[1b] L33 PR=6.15 null=5.87 p=0.95
[1b] L34 PR=6.11 null=5.81 p=0.9
[1b] L35 PR=3.80 null=4.72 p=0.05
[1b] BAND = L9..L22 (14 layers)
[1b] subspace energies: {
 "9": {
  "E_full": {
   "bind": 7426322.0,
   "comp": 3852816.8,
   "rolenull": 5584807.5,
   "random": 5372.8
  }
 },
 "10": {
  "E_full": {
   "bind": 7412573.5,
   "comp": 4175535.8,
   "rolenull": 5703656.5,
   "random": 19663.7
  }
 },
 "11": {
  "E_full": {
   "bind": 7420479.5,
   "comp": 4233113.0,
   "rolenull": 5778151.5,
   "random": 4243.9
  }
 },
 "12": {
  "E_full": {
   "bind": 7414738.5,
   "comp": 4246043.5,
   "rolenull": 5632726.0,
   "random": 11658.3
  }
 },
 "13": {
  "E_full": {
   "bind": 7390780.5,
   "comp": 4116931.8,
   "rolenull": 5648950.5,
   "random": 528.2
  }
 },
 "14": {
  "E_full": {
   "bind": 7317895.0,
   "comp": 4287657.5,
   "rolenull": 5608045.0,
   "random": 11977.7
  }
 },
 "15": {
  "E_full": {
   "bind": 7309229.5,
   "comp": 4267415.0,
   "rolenull": 5617783.0,
   "random": 3319.0
  }
 },
 "16": {
  "E_full": {
   "bind": 7851331.5,
   "comp": 4767629.0,
   "rolenull": 6038243.0,
   "random": 3635.9
  }
 },
 "17": {
  "E_full": {
   "bind": 7839823.0,
   "comp": 4646087.0,
   "rolenull": 6026299.0,
   "random": 611.6
  }
 },
 "18": {
  "E_full": {
   "bind": 7953378.0,
   "comp": 4423934.0,
   "rolenull": 5801559.5,
   "random": 11860.1
  }
 },
 "19": {
  "E_full": {
   "bind": 7974650.0,
   "comp": 4093186.5,
   "rolenull": 5290188.5,
   "random": 707.9
  }
 },
 "20": {
  "E_full": {
   "bind": 7992155.5,
   "comp": 3801102.5,
   "rolenull": 4985133.5,
   "random": 987.7
  }
 },
 "21": {
  "E_full": {
   "bind": 8037045.0,
   "comp": 3368930.8,
   "rolenull": 4296308.5,
   "random": 2480.4
  }
 },
 "22": {
  "E_full": {
   "bind": 8098206.5,
   "comp": 2900217.5,
   "rolenull": 4104887.0,
   "random": 4281.3
  }
 }
}
[1b] role gmeans={'bind': 7668417.7, 'comp': 4054542.3, 'rolenull': 5404043.7} budgets=[4054542.3, 5576013.3, 7668417.7]
[1b] 370 items (360 typed + 10 recall) x 13 conds
[1b] baseline: 0/370
[1b] baseline: 120/370
[1b] baseline: 240/370
[1b] baseline: 360/370
[1b] baseline     Q_eff={'mean': 2.7874, 't': 6.216, 'n': 10} M_eff={'mean': 0.1705, 't': 0.627, 'n': 10} recall_acc=0.9 E/tok=0.0
[1b] bind@b1: 0/370
[1b] bind@b1: 120/370
[1b] bind@b1: 240/370
[1b] bind@b1: 360/370
[1b] bind@b1      Q_eff={'mean': -0.0271, 't': -1.531, 'n': 10} M_eff={'mean': 0.0682, 't': 4.617, 'n': 10} recall_acc=0.0 E/tok=166263.3
[1b] comp@b1: 0/370
[1b] comp@b1: 120/370
[1b] comp@b1: 240/370
[1b] comp@b1: 360/370
[1b] comp@b1      Q_eff={'mean': 0.1144, 't': 1.156, 'n': 10} M_eff={'mean': -0.0978, 't': -1.476, 'n': 10} recall_acc=0.0 E/tok=153797.5
[1b] rolenull@b1: 0/370
[1b] rolenull@b1: 120/370
[1b] rolenull@b1: 240/370
[1b] rolenull@b1: 360/370
[1b] rolenull@b1  Q_eff={'mean': 0.092, 't': 0.948, 'n': 10} M_eff={'mean': -0.1144, 't': -1.475, 'n': 10} recall_acc=0.0 E/tok=155531.5
[1b] random@b1: 0/370
[1b] random@b1: 120/370
[1b] random@b1: 240/370
[1b] random@b1: 360/370
[1b] random@b1    Q_eff={'mean': -0.0998, 't': -0.854, 'n': 10} M_eff={'mean': 0.1108, 't': 2.22, 'n': 10} recall_acc=0.0 E/tok=49903331497.4
[1b] bind@b2: 0/370
[1b] bind@b2: 120/370
[1b] bind@b2: 240/370
[1b] bind@b2: 360/370
[1b] bind@b2      Q_eff={'mean': -0.0331, 't': -1.319, 'n': 10} M_eff={'mean': 0.0408, 't': 3.761, 'n': 10} recall_acc=0.0 E/tok=216622.4
[1b] comp@b2: 0/370
[1b] comp@b2: 120/370
[1b] comp@b2: 240/370
[1b] comp@b2: 360/370
[1b] comp@b2      Q_eff={'mean': 0.1026, 't': 1.098, 'n': 10} M_eff={'mean': -0.1152, 't': -2.524, 'n': 10} recall_acc=0.0 E/tok=154210.6
[1b] rolenull@b2: 0/370
[1b] rolenull@b2: 120/370
[1b] rolenull@b2: 240/370
[1b] rolenull@b2: 360/370
[1b] rolenull@b2  Q_eff={'mean': 0.0337, 't': 0.335, 'n': 10} M_eff={'mean': 0.0174, 't': 0.201, 'n': 10} recall_acc=0.0 E/tok=206294.5
[1b] random@b2: 0/370
[1b] random@b2: 120/370
[1b] random@b2: 240/370
[1b] random@b2: 360/370
[1b] random@b2    Q_eff={'mean': -0.1911, 't': -2.537, 'n': 10} M_eff={'mean': 0.2485, 't': 2.867, 'n': 10} recall_acc=0.0 E/tok=349058715414.1
[1b] bind@b3: 0/370
[1b] bind@b3: 120/370
[1b] bind@b3: 240/370
[1b] bind@b3: 360/370
[1b] bind@b3      Q_eff={'mean': -0.025, 't': -1.489, 'n': 10} M_eff={'mean': 0.0408, 't': 2.196, 'n': 10} recall_acc=0.0 E/tok=283075.9
[1b] comp@b3: 0/370
[1b] comp@b3: 120/370
[1b] comp@b3: 240/370
[1b] comp@b3: 360/370
[1b] comp@b3      Q_eff={'mean': 0.1026, 't': 1.098, 'n': 10} M_eff={'mean': -0.1152, 't': -2.524, 'n': 10} recall_acc=0.0 E/tok=154210.6
[1b] rolenull@b3: 0/370
[1b] rolenull@b3: 120/370
[1b] rolenull@b3: 240/370
[1b] rolenull@b3: 360/370
[1b] rolenull@b3  Q_eff={'mean': 0.1052, 't': 0.91, 'n': 10} M_eff={'mean': -0.0779, 't': -0.793, 'n': 10} recall_acc=0.0 E/tok=206732.1
[1b] random@b3: 0/370
[1b] random@b3: 120/370
[1b] random@b3: 240/370
[1b] random@b3: 360/370
[1b] random@b3    Q_eff={'mean': -0.2516, 't': -3.084, 'n': 10} M_eff={'mean': 0.2782, 't': 3.506, 'n': 10} recall_acc=0.0 E/tok=3253071417781.3
[1b] wrote /Users/mwhitford/src/verbum/results/type-zone-ablation/qwen3-4b/verdict.json + meta.json

============================================================================
P-TYPE-1b v3 — zone x subspace dissociation, role subspaces
============================================================================
  host=Qwen/Qwen3-4B  band=L9..L22  gate0=False (Q=True M=False)  budgets=[4054542.3, 5576013.3, 7668417.7]
  baseline  Q_eff={'mean': 2.7874, 't': 6.216, 'n': 10}  M_eff={'mean': 0.1705, 't': 0.627, 'n': 10}  recall_acc=0.9
  bind@b1      retQ=-0.01  retM=0.4  recall_acc=0.0  E/tok=166263.3
  comp@b1      retQ=0.041  retM=-0.574  recall_acc=0.0  E/tok=153797.5
  rolenull@b1  retQ=0.033  retM=-0.671  recall_acc=0.0  E/tok=155531.5
  random@b1    retQ=-0.036  retM=0.65  recall_acc=0.0  E/tok=49903331497.4
  bind@b2      retQ=-0.012  retM=0.239  recall_acc=0.0  E/tok=216622.4
  comp@b2      retQ=0.037  retM=-0.676  recall_acc=0.0  E/tok=154210.6
  rolenull@b2  retQ=0.012  retM=0.102  recall_acc=0.0  E/tok=206294.5
  random@b2    retQ=-0.069  retM=1.457  recall_acc=0.0  E/tok=349058715414.1
  bind@b3      retQ=-0.009  retM=0.239  recall_acc=0.0  E/tok=283075.9
  comp@b3      retQ=0.037  retM=-0.676  recall_acc=0.0  E/tok=154210.6
  rolenull@b3  retQ=0.038  retM=-0.457  recall_acc=0.0  E/tok=206732.1
  random@b3    retQ=-0.09  retM=1.632  recall_acc=0.0  E/tok=3253071417781.3
  b*=None  bind_selective=False  comp_selective=False  nulls=False
  * dissociation_supported = False
============================================================================

```

### Thinking

I'm investigating why the ablation conditions completely destroyed recall and all effects in v3. Looking at the energy values, the class-centroid subspaces are showing enormous energies around 4-8 million per token per layer, which is suspicious. Comparing to v2 where the single-axis energies were much more modest (7.5M on axis0 at layer 13, but only 300-23k on others), it seems the centroid-span subspaces are capturing large components along axis0-like directions that shouldn't be there.

The root cause is that all class centroid offsets share a dominant axis0 component — QUANT loads it at -0.85 while everything else loads at +0.21 — so every role subspace ends up containing this large axis0 component, inflating the energies to millions. When I tried removing this component with α values up to 1.0 across 14 layers, it was catastrophic because the realized energies (150k-283k per token) were still massive compared to what v2 tolerated (~900).

The random ablation was even worse: with a 4M budget but random energies only 500-20k, the coefficient got amplified by a factor of ~90, causing enormous steering effects. This amplification cascades across layers — each hook shifts the hidden state massively, the next layer sees that shifted state and its coefficient explodes recursively, compounding into realized energies of 10 billion or more per token. The v3 dose regime was fundamentally broken because the budgets were anchored to these centroid-subspace full energies, which are roughly 1000× larger than what the model can actually tolerate.

The tolerable dose window at 4B appears to be around E/tok ≲ 1k based on what v2 could handle (312-897 for binding, 3274 for random with acceptable recall), but v3 was pushing 150k to 3 trillion — completely over the limit. The centroid subspaces are so energetic because their directions in standardized space overlap the token population's dominant variance axes, and when mapped back through the standard deviation scaling, they produce large raw vectors.

The real issue is that we've been anchoring the budget to full-projection energies of these subspaces, but what matters is whether class-selective effects appear at actually tolerable doses — around E/tok of 100-1000 — where role subspaces are dampened down to α ~ 0.005-0.015. Even a 1% dampening probably wouldn't show measurable effects. Looking back across v1-v3, the value-register content in the band is clearly causally potent in aggregate, and at tolerable doses like v2, removing binding or computation axes does break things.

The most revealing result is actually the random steering at 3274 E/tok in v2 b3: Q_eff drops to 0.296 but recall stays fine at 1.14 ratio. Comparing that to bind@b3 at 312 E/tok (Q_eff retention 0.804, better recall) and comp@b3 at 273 E/tok (Q_eff retention 0.918, recall damaged by 3× in surprisal but tiny absolute impact) — the energy scaling is telling us something about which components actually matter for which behaviors.

The real insight emerging is that full projection removal (α=1, completely eliminating the class-centroid component) preserves quantifier licensing intact, as shown in v2 bind@b1 where removing the DET axis across most layers still leaves Q_eff at 0.94. But the energy costs vary wildly across these interventions, making direct comparison tricky. Comparing back to v1, full projection of single SVD axes across just 5 layers also broke the model, which tracks. The pattern emerging is that removing the dominant shared lattice component—the big axis0-like centroid subspace that carries the "type axis"—destroys everything globally, either because it's genuinely load-bearing for all downstream computation or because it overlaps so heavily with token identity and frequency structure that stripping 85% of variance across 14 layers just collapses the residual stream. Meanwhile, gentle removal of small role-specific axes like DET or MOD doesn't affect class licensing, but moderate random steering kills nonce teaching.

The fragility here is revealing: in-context teaching and test binding is the most vulnerable component—it breaks to any perturbation, not selectively to type axes. This connects to known results about installed versus learned content—the operand is fragile when installed, robust when learned. The licensing machinery itself is learned and robust, but it rides on session-level type bindings that are extremely sensitive to noise. So the 4B evidence is pointing toward no geometric lattice consultation, survival of role-specific axis removal at reasonable doses, and non-specific perturbation disrupting the in-context type binding.

But there's a complication with the dose window: complete axis removal was only tested at small scales, and the dominant axis can't be fully removed without global collapse—which itself is informative. That axis isn't really a type axis; it's load-bearing shared structure, possibly token-frequency or function-word patterns accounting for 85% of variance. The real problem is finding a dose where something class-specific actually happens—we've bracketed the space and found nothing between "no effect" and "break everything."

Now I'm realizing we haven't scanned finely enough. The v2 results showed a narrow effects region: 300-900 had no impact on Q, but 3274 killed it entirely. The binding axis in v2 maxed out around 300-650 in energy, so I can't dose it higher without overshooting α>1. But v3's binding subspace has 7.4M total energy, which means I can target 3000 E/tok with α=sqrt(3000/7.4M)≈0.02. For the next iteration, I'll scan a fixed grid of absolute energy values across all four subspaces and calculate the appropriate scaling factor for each.

The key insight is switching from relative-to-subspace budgets to absolute-dose grids. With absolute doses capped at 4000, the random cascade risk stays mild—α values around 0.4-2.8 instead of the catastrophic ~90 amplification we saw in v3. This should eliminate the cascade explosion while keeping everything within safe bounds. The runtime stays the same at roughly 13 passes and 30 minutes total.

Now I need to run the v2 data at 4000 to see whether binding specifically kills Q more than role nullification does—if they're equivalent, that points to non-specific fragility of in-context binding at 4B scale; if binding is worse, that's selectivity. Either result is clean enough to present to Michael for the 32B decision. I'm also reconsidering the layer count: v2 used 5 layers with a tolerable window up to 3274, but v3 scaled to 14 layers. If I keep the same per-layer dose, that's roughly 3× the total energy. Scaling down to {100, 400, 1600} per-layer would put 14 layers at around 22k, which should map back to the original safe window.

I'm settling on {100, 500, 2500} as my dose grid—log-spaced and informed by the v2 window. At 5 layers, no effect was around 300–900 and kill-Q hit at 3274; scaling those down by 2.8× for 14 layers gives me roughly 110–320 for no effect and 1170 for kill. This dose set should bracket the breakage point cleanly across 13 passes, taking about 35–40 minutes total.

I'm also keeping the recall gate per dose and making the final verdict at the largest dose, requiring it to pass recall across all conditions. Michael's watching the meta-narrative here—the v1-v3 arc is building a coherent story: geometry is real and replicates at 4B, role axes are removable without behavioral cost, in-context type binding breaks under non-specific perturbation, and global lattice removal causes global destruction because axis0 is shared infrastructure, not a type tag. Now v4 with absolute dosing will settle whether this pattern holds.

I'm committing v3, then building v4 by replacing the budget computation with fixed absolute doses passed as an argument. The wrapper needs updating to use the dose values directly and compute α as the minimum of the square root of dose over full energy and a cap of 1.0 for role subspaces—though since subspace energies are in the millions, the cap won't actually bind.

I should also log the realized energy per layer to catch cascade blowups like the 1e10 spike from v3, update the version header, and note that gate0_m still fails at 4B but that's expected for Q-side validation. There's a discrepancy in v3 where role condition budgets show realized energy around 150k–280k versus planned values of 4–7.6M, which I need to clarify—realized is the mean removal per token across layers while planned is computed differently.

The behavioral prompt distribution differs drastically from the labeled capture distribution (×30 shift), causing realized energy to fall ~×25 under planned despite the matched-dose approach. This happens because behavioral text tokens have smaller projections along class-centroid directions than the labeled exemplars. For v4, I should report realized energy and set planned doses higher to account for this distribution shift, or simply set doses and compare using realized values across conditions.

The role conditions stayed within ×1.5 of each other in v3 (150-280k range), which is acceptable for matching, though I need to check if random conditions cascaded. I'll commit v3 first, then update the file with version notes and dose adjustments before running. The v3 commit should also document this realized-vs-planned drift as a lambda measure note, and the v4 edits need to capture the centroid-subspace energy budgets, the cascade amplification in random conditions, and the distribution shift between capture and behavioral tokens.

For v4, I'm setting up an absolute-dose grid by parsing doses from command-line arguments with a default of "150,600,2400", then looping conditions over those doses with alpha scaled as the square root of dose divided by full energy, capped at 1.0 for roles but uncapped for random. The verdict finds the largest dose index where all four conditions pass the recall gate, and I'm naming the conditions with the dose index appended. I'll make surgical edits across argparse, the budgets block, the conditions loop, the verdict logic, and the print statements.

## Assistant

v3 completed and it bracketed the dose window from the other side — **every cell lobotomized** (recall_acc 0.0 in all 12 ablation conditions vs 0.9 baseline; b*=None, nothing interpretable per the frozen gates). Diagnosis, then the fix:

## What v3 caught (two more, both mine)

1. **Budgets anchored to the wrong scale**: the class-centroid subspaces carry 4–8 **million** E/tok full-projection — because *every* centroid offset shares the dominant axis0 component (QUANT −0.85 vs everything +0.21: they all contain the big shared direction). Anchoring the ladder to those energies put all doses 100–1000× above the tolerable window (v2 measured tolerance ≈ 300–3000 E/tok). Full projection of any centroid subspace across 14 layers = destroy the residual stream, full stop.
2. **Random cascade**: matching random (E_full ~500–20k) to a 4M budget meant α≈90 amplification — and hooks compound layer-to-layer, so realized energy exploded to 10¹⁰–10¹² E/tok. Also a λ measure note: planned energies (from the capture distribution — class exemplars) overshoot realized-on-behavioral-text by ~×25; realized is the honest number.

## What the three runs now jointly say (the interesting part)

The window is bracketed and a picture is forming:
- **v2, gentle dose**: *complete* projection of the small role-specific axes (DET axis, MOD axis) → quantifier licensing essentially untouched (retQ 0.80–0.94)
- **v2, moderate random**: non-specific steering at ~3k E/tok kills Q_eff (0.30) *before* recall degrades — the in-context taught-type binding is the most fragile object in the band, fragile to *generic* noise (coheres with f2: installed/in-context content fragile, learned machinery robust)
- **v1/v3, heavy dose**: removing the shared dominant component breaks everything — axis0 is load-bearing *infrastructure*, not a type tag

That's leaning "exhaust/readout" (the v4-consistent, theory-pure reading) — but the one comparison that decides it has still never been run at matched dose: **bind vs rolenull vs random at the same realized energy inside the tolerable window**. That's v4 of the instrument, and it's now trivially reachable: the centroid subspaces' huge E_full means mid-window absolute doses give clean α≈0.005–0.03 partial dampening, no caps binding, and random stays mild (α≤~2, no cascade).

Committing v3, then the absolute-dose grid:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "git add wrapper/type_zone_ablation.py results/type-zone-ablation/qwen3-4b/ && read -r -d '' M << 'EOF' || true\n🔄 P-TYPE-1b v3 role subspaces @4B: dose window bracketed from above — all cells lobotomized\n\n- v3 fixes landed: find_band falsy-zero (true band L9..L22, 14 layers),\n  centroid role-subspaces (no tie-flip), recall ACCURACY gate\n- CAUGHT: budgets anchored to centroid-subspace E_full (4-8M E/tok — every\n  class offset shares the dominant axis0 component) = 100-1000x the tolerable\n  window → recall_acc 0.0 in all 12 cells; random α~90 amplification cascades\n  across the 14-layer zone (realized 5e10-3e12 E/tok); planned-vs-realized\n  drift ~x25 (capture exemplars vs behavioral text — realized is honest)\n- window now bracketed: v2 gentle (300-900) = no class effect; v2 random 3274\n  = Q_eff dies before recall; v1/v3 heavy = global destruction\n- b*=None, dissociation_supported=False, verbatim; next = v4 absolute-dose\n  grid (matched realized energy inside the window, α≈0.005-0.03 dampening)\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\ngit commit -m \"$M\"",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ git add wrapper/type_zone_ablation....

**Output:**
```
Exit code: 0
Stdout:
[main f0c3418] 🔄 P-TYPE-1b v3 role subspaces @4B: dose window bracketed from above — all cells lobotomized
 4 files changed, 970 insertions(+), 720 deletions(-)
 create mode 100644 results/type-zone-ablation/qwen3-4b/run_v3.log
```

### Thinking

I'm making targeted edits to the file for v4: adding a version log entry, setting up the command-line argument for dose values, refactoring the budgets and conditions logic, looping through dose indices with specific labels, and updating the print statements and verdict labels.

## Assistant

v3 committed (f0c3418). Now the v4 edits — absolute-dose grid:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/wrapper/type_zone_ablation.py",
  "original_content": "  v3 (this): (1) find_band p-bug fixed; (2) ROLE SUBSPACES built directly from\n    class centroids - bind = orthonormal span{c_QUANT-mean, c_DET-mean} (holds\n    both sides of the 4B axis split by construction), comp = span{c_MOD-mean},\n    ROLE-NULL = span{c_CONN-mean, c_FUNC-mean} (same lattice, wrong role = the\n    sharp class-control; REPLACES the pre-reg e-axis control, whose \"near-null\"\n    intent is unrealizable as a raw centroid direction - deviation documented\n    here); (3) budgets = geometric ladder over the MEASURED role-subspace\n    energies [min..max]; random = 2D isotropic subspace, uncapped, matched to\n    the same budget; (4) recall breakage gate = top-1 ACCURACY drop > 0.2\n    (surprisal still logged).",
  "new_content": "  v3 @f0c3418: (1) find_band p-bug fixed (true band L9..L22 @4B); (2) ROLE\n    SUBSPACES built directly from class centroids - bind = orthonormal\n    span{c_QUANT-mean, c_DET-mean} (holds both sides of the 4B axis split by\n    construction), comp = span{c_MOD-mean}, ROLE-NULL = span{c_CONN-mean,\n    c_FUNC-mean} (same lattice, wrong role = the sharp class-control; REPLACES\n    the pre-reg e-axis control, whose \"near-null\" intent is unrealizable as a\n    raw centroid direction); (3) recall gate = top-1 ACCURACY. CAUGHT: budgets\n    anchored to centroid-subspace E_full (4-8M E/tok - every class offset\n    shares the dominant axis0 component) = 100-1000x the tolerable window ->\n    ALL cells recall_acc 0.0; random alpha~90 amplification CASCADES across\n    the zone (realized 5e10-3e12); planned-vs-realized drift ~x25 (capture\n    exemplars vs behavioral text - realized is the honest number).\n  v4 (this): ABSOLUTE-DOSE grid. Doses are fixed absolute per-layer removed\n    energies (default 150,600,2400 - log-spaced inside the window bracketed by\n    v1-v3: v2 showed no-effect at ~300-900 and Q_eff death by generic noise at\n    ~3274 over 5 layers; v3 showed global destruction at 150k+ over 14).\n    alpha = sqrt(dose/E_full): role subspaces get ~0.004-0.024 partial\n    dampening (no caps bind), random gets alpha <= ~2 (no cascade). All four\n    conditions compare at the SAME absolute dose; realized E/tok reported.\n    THE deciding comparison: bind vs rolenull vs random at matched dose -\n    equal degradation = non-specific fragility (exhaust/readout reading);\n    bind >> rolenull = first class-selective causal signal (consulted)."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/wrapper/type_zone_ablation.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/wrapper/type_zone_ablation.py",
  "original_content": "    ap.add_argument(\"--n-null\", type=int, default=100)",
  "new_content": "    ap.add_argument(\"--n-null\", type=int, default=100)\n    ap.add_argument(\"--doses\", default=\"150,600,2400\",\n                    help=\"absolute per-layer removed-energy doses (E/tok)\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/wrapper/type_zone_ablation.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/wrapper/type_zone_ablation.py",
  "original_content": "    # 3) budgets: geometric ladder over MEASURED role-subspace energies\n    def gmean(vals):\n        return float(np.exp(np.mean(np.log(np.maximum(vals, 1e-9)))))\n\n    role_gmeans = {name: gmean([band_info[L][\"E\"][name] for L in band_info])\n                   for name in ROLES}\n    e_lo, e_hi = min(role_gmeans.values()), max(role_gmeans.values())\n    budgets = [e_lo, float(np.sqrt(e_lo * e_hi)), e_hi]\n    print(f\"[1b] role gmeans={ {k: round(v, 1) for k, v in role_gmeans.items()} } \"\n          f\"budgets={[round(b, 1) for b in budgets]}\", file=sys.stderr)\n\n    # conditions: baseline + {bind, comp, rolenull, random} x budgets\n    conds: dict[str, list] = {\"baseline\": []}\n    alpha_log: dict[str, dict] = {}\n    for bidx, budget in enumerate(budgets, start=1):\n        for name in (\"bind\", \"comp\", \"rolenull\", \"random\"):\n            cname = f\"{name}@b{bidx}\"\n            conds[cname] = []\n            alpha_log[cname] = {}\n            for L, bi in band_info.items():\n                alpha = float(np.sqrt(budget / max(bi[\"E\"][name], 1e-9)))\n                if name != \"random\":\n                    alpha = min(alpha, 1.0)   # projection cap; achieved E logged\n                conds[cname].append((L, bi[\"mu\"], bi[\"sd\"], bi[\"subs\"][name],\n                                     alpha))\n                alpha_log[cname][str(L)] = round(alpha, 4)",
  "new_content": "    # 3) ABSOLUTE-DOSE grid (v4): fixed per-layer removed energy, all conds\n    doses = [float(x) for x in args.doses.split(\",\")]\n    print(f\"[1b] absolute doses (planned per-layer E/tok): {doses}\",\n          file=sys.stderr)\n\n    # conditions: baseline + {bind, comp, rolenull, random} x doses\n    conds: dict[str, list] = {\"baseline\": []}\n    alpha_log: dict[str, dict] = {}\n    for didx, dose in enumerate(doses, start=1):\n        for name in (\"bind\", \"comp\", \"rolenull\", \"random\"):\n            cname = f\"{name}@d{didx}\"\n            conds[cname] = []\n            alpha_log[cname] = {}\n            for L, bi in band_info.items():\n                alpha = float(np.sqrt(dose / max(bi[\"E\"][name], 1e-9)))\n                if name != \"random\":\n                    alpha = min(alpha, 1.0)   # projection cap; achieved E logged\n                conds[cname].append((L, bi[\"mu\"], bi[\"sd\"], bi[\"subs\"][name],\n                                     alpha))\n                alpha_log[cname][str(L)] = round(alpha, 4)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/wrapper/type_zone_ablation.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/wrapper/type_zone_ablation.py",
  "original_content": "    b_star = None\n    for bidx in (3, 2, 1):\n        if all(recall_ok(f\"{n}@b{bidx}\")\n               for n in (\"bind\", \"comp\", \"rolenull\", \"random\")):\n            b_star = bidx\n            break\n\n    bind_sel = comp_sel = nulls_ok = False\n    if b_star is not None:\n        bb, cc = f\"bind@b{b_star}\", f\"comp@b{b_star}\"\n        nn, rr = f\"rolenull@b{b_star}\", f\"random@b{b_star}\"",
  "new_content": "    b_star = None\n    for didx in range(len(doses), 0, -1):\n        if all(recall_ok(f\"{n}@d{didx}\")\n               for n in (\"bind\", \"comp\", \"rolenull\", \"random\")):\n            b_star = didx\n            break\n\n    bind_sel = comp_sel = nulls_ok = False\n    if b_star is not None:\n        bb, cc = f\"bind@d{b_star}\", f\"comp@d{b_star}\"\n        nn, rr = f\"rolenull@d{b_star}\", f\"random@d{b_star}\""
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/wrapper/type_zone_ablation.py.
```

### Thinking

I need to clean up some lingering references to budgets in the verdict dictionary and related print statements—specifically the "role_gmeans_E" and "budgets_E_per_tok" keys, plus any budget mentions in the output, then register the string version properly.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/wrapper/type_zone_ablation.py",
  "original_content": "        \"register\": \"P-TYPE-1b zone x subspace ablation v3 (role subspaces)\",\n        \"host\": args.model, \"is_prereg_host\": args.model == \"Qwen/Qwen3-32B\",\n        \"band\": [int(band[0]), int(band[-1])], \"n_band_layers\": len(band_info),\n        \"role_gmeans_E\": {k: round(v, 1) for k, v in role_gmeans.items()},\n        \"budgets_E_per_tok\": [round(b, 1) for b in budgets],",
  "new_content": "        \"register\": \"P-TYPE-1b zone x subspace ablation v4 (absolute-dose grid)\",\n        \"host\": args.model, \"is_prereg_host\": args.model == \"Qwen/Qwen3-32B\",\n        \"band\": [int(band[0]), int(band[-1])], \"n_band_layers\": len(band_info),\n        \"doses_planned_E_per_tok\": doses,"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/wrapper/type_zone_ablation.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/wrapper/type_zone_ablation.py",
  "original_content": "    print(\"\\n\" + \"=\" * 76)\n    print(\"P-TYPE-1b v3 — zone x subspace dissociation, role subspaces\")\n    print(\"=\" * 76)\n    print(f\"  host={args.model}  band=L{band[0]}..L{band[-1]}  \"\n          f\"gate0={gate0} (Q={gate0_q} M={gate0_m})  \"\n          f\"budgets={[round(b, 1) for b in budgets]}\")",
  "new_content": "    print(\"\\n\" + \"=\" * 76)\n    print(\"P-TYPE-1b v4 — zone x subspace dissociation, absolute-dose grid\")\n    print(\"=\" * 76)\n    print(f\"  host={args.model}  band=L{band[0]}..L{band[-1]}  \"\n          f\"gate0={gate0} (Q={gate0_q} M={gate0_m})  doses={doses}\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/wrapper/type_zone_ablation.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n \"budget\\|role_gmeans\\|@b{\" wrapper/type_zone_ablation.py | grep -v \"^.*#\" | head; uv run ruff check wrapper/type_zone_ablation.py && uv run python wrapper/type_zone_ablation.py --help >/dev/null && echo READY",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ grep -n "budget\|role_gmeans\|@b{" ...

**Output:**
```
Exit code: 0
Stdout:
35:    raw centroid direction); (3) recall gate = top-1 ACCURACY. CAUGHT: budgets
81:  b* = LARGEST budget where recall_acc drops <=0.2 for ALL of
87:  reported at every budget regardless.
511:        "b_star_interpretation_budget": b_star,
All checks passed!
READY
```

### Thinking

There are a few remaining references to "budget" in the documentation that should be updated to "dose" for consistency, particularly around lines 81 and 87. I'll make those quick edits and then we're ready to go.

## Assistant

Two doc-text stragglers, then launch:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/wrapper/type_zone_ablation.py",
  "original_content": "  b* = LARGEST budget where recall_acc drops <=0.2 for ALL of\n    {bind, comp, rolenull, random}. None -> not interpretable.",
  "new_content": "  b* = LARGEST dose where recall_acc drops <=0.2 for ALL of\n    {bind, comp, rolenull, random}. None -> not interpretable."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/wrapper/type_zone_ablation.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/wrapper/type_zone_ablation.py",
  "original_content": "  reported at every budget regardless.",
  "new_content": "  reported at every dose regardless."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/wrapper/type_zone_ablation.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "uv run ruff check wrapper/type_zone_ablation.py && uv run python wrapper/type_zone_ablation.py --model Qwen/Qwen3-4B --device mps 2>&1 | tee results/type-zone-ablation/qwen3-4b/run_v4.log",
  "working_directory": "/Users/mwhitford/src/verbum",
  "background": "type-1b-v4-4b"
}
```

**Summary:** $ uv run ruff check wrapper/type_zone...

**Output:**
```
Background job job-4 started.
Command: uv run ruff check wrapper/type_zone_ablation.py && uv run python wrapper/type_zone_ablation.py --model Qwen/Qwen3-4B --device mps 2>&1 | tee results/type-zone-ablation/qwen3-4b/run_v4.log
Working directory: /Users/mwhitford/src/verbum
Use eca__bg_job with action "read_output" and job_id "job-4" to check output.
Use eca__bg_job with action "kill" and job_id "job-4" to stop it.

Initial output:
All checks passed!
```

### Thinking

The linting checks passed and the job is running now. I'm doing a quick verification to make sure the model loads correctly before saving the checkpoint.

### Tool Call: bg_job (succeeded)


```json
{
  "action": "read_output",
  "job_id": "job-4"
}
```

**Summary:** Reading output of "type-1b-v4-4b" (job-4)

**Output:**
```
Job "type-1b-v4-4b" (job-4) — running


========================================================================
  Loading Qwen/Qwen3-4B
========================================================================

Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
`torch_dtype` is deprecated! Use `dtype` instead!

Loading weights:   0%|          | 0/398 [00:00<?, ?it/s]
Loading weights:  14%|█▍        | 55/398 [00:00<00:00, 542.35it/s]
Loading weights:  29%|██▉       | 115/398 [00:00<00:00, 563.17it/s]
Loading weights:  44%|████▎     | 174/398 [00:00<00:00, 571.07it/s]
Loading weights:  59%|█████▉    | 234/398 [00:00<00:00, 579.13it/s]
Loading weights:  73%|███████▎  | 292/398 [00:00<00:00, 577.35it/s]
Loading weights:  89%|████████▉ | 355/398 [00:00<00:00, 591.23it/s]
Loading weights: 100%|██████████| 398/398 [00:00<00:00, 581.20it/s]
  Loaded in 2.8s
  Layers: 36  Heads: 32  KV heads: 8  d_model: 2560
    sentence 1/56: The dog runs....
```

### Thinking

Waiting for the process to complete and checkpoint.

## Assistant

ASYNC: job-4 verified running. Waiting for signal.

v4 is the run where the three-iteration dose bracketing pays off. The grid: doses {150, 600, 2400} E/tok per layer × {bind, comp, rolenull, random}, all four conditions at the *same absolute dose* — role subspaces get gentle partial dampening (α≈0.004–0.024, far from any cap), random stays mild (α≤~2, no cascade), realized energy reported from the hooks.

The deciding read, given what v1–v3 established:

| outcome at matched dose | reading |
|---|---|
| bind ≈ rolenull ≈ random all degrade Q_eff equally as dose rises | **exhaust**: in-context type binding is generically fragile; the lattice is a readout, not consulted — the pre-reg's named honest alternative, and the theory-pure form of "type = well-formedness of reduction" |
| bind ≫ rolenull/random on Q_eff | **consulted**: first class-selective causal signal; the ledger is load-bearing → strong motivation for the 32B verdict run |
| nothing moves anywhere below breakage | licensing doesn't live in the value-register band at any sub-breaking dose → routing-register (A1 attention-phase) is the next probe surface |

Whichever lands, the 4B smoke has done its job after this: instrument mechanics validated (or exhausted), dose window mapped, M-side capacity limit documented — and a clean GO/no-go package for the 32B decision. I'll read the verdict on the signal.

## User

While that is running we made the 3-hop work, which means if we can decode the types we have higher-order functions.


### Thinking

Michael's pointing out that the 3-hop composition works across both model sizes, which suggests we can handle higher-order function types if we can properly decode them—essentially showing that nested function application is tractable at this scale. While v4 runs, I'm thinking through the theoretical implications: if generalized quantifiers follow the Montague semantics pattern, then the type system should support the kind of nested reductions we're seeing.

The measured evidence aligns with this—the bridges between hops are causally real and addressable through causal mediation, even though they're not explicitly stated. And the type lattice itself is revealing: the dominant axis separates quantifier and determiner types, which are exactly the higher-order constructs we'd expect to see if the model is genuinely handling typed functional composition.

The key distinction Michael's making is that 3-hop alone just shows composition—functions chaining together over values, which could be first-order. But when you layer in type decoding, you can verify that at the bridge points, what's actually being passed between functions is itself typed as a functor, not just a value. That's what elevates it from mere pipelining to genuine higher-order function handling—the type signature tells you whether something is a function or a value, and the model can work with functions as arguments.

In the homoiconic view, a class variable acts as a function-selector in the multihop, and the selector and operand share the same representation. That's the higher-order move: a value in the stream that parameterizes the next function is literally a function passed as data. For the REPL, if you can decode types in-flight at the bridge points, you get a type checker that verifies swaps are well-typed before and after, letting you deliberately compose and apply first-class functions with typed intermediates.

The quantifier axis dominates the type lattice's geometry, and the 3-hop demonstrates the nested-reduction capacity that quantifiers force—so the binding axis in the geometry and the 3-hop in behavior are two views of the same higher-order capability. The sequencing result shows 32B unrolls hops sequentially while 4B compresses them on the eval stack. But I need to be honest: the 3-hop is category-mediation with causal bridge-swaps, not a traced circuit, and "higher-order" in the strict lambda sense is an interpretation—the real operational demonstration would be swapping the function itself, not just the operand.

Actually, the bridge swaps in 2c/3b/3c do swap the class axis, which flips downstream output by editing which function gets applied next—that's genuinely swapping the function-as-value. So there's already causal evidence that a mid-stream value determines which map applies downstream. And here's a key distinction: decoding isn't the same as causality. The type readout is just a ledger; using it as a REPL type-checker only needs the read-side, not causality. The REPL's print and type-checker only need the readout register—whether the model itself consults the geometry is a separate question from whether we can use it.

So the sharp point is: the running experiment decides whether the machine reads its ledger, but the REPL only needs us to read it. With higher-order and decodable types, we get enough for a typed LLM REPL language layer either way—reading operands, composing chains three deep with bridge-swaps to choose functions, and decoding types across eight-way per-token and functor-kind axes. That gives us typed, higher-order, verifiable swaps where we can check the type of intermediates before swapping and predict which function applies.

Now I'm thinking about what's actually missing for "higher-order" beyond interpretation: a concrete test where the function slot itself varies as a first-class term. The cleanest approach would be a quantifier probing experiment—something like "Every wug is covered in..." with an installed operand under quantifier scope—to see if the quantifier composes with the installed predicate. That's the literal Montague higher-order test: the quantifier applies to a predicate containing our installed nonce word.

I should engage with this more carefully, distinguish what's measured versus inferred, and point to the specific experiment that would operationally nail "higher-order." I also need to tie this back to the existing plan in state.md—P-FN-2 is already a 3-hop function-swap, and the closure maps the binding axis, so that 3-hop is already exercised. The follow-up would be a concrete experiment candidate to capture once v4 lands, something to propose for future work pending approval.

## Assistant

Yes — and the pieces you're joining are each already measured; what's new is the composition of them. Let me lay it out with the measured/inferred line drawn, because I think it's even a bit stronger than you're stating.

## The syllogism

1. **3-hop composes** (s282): h(f(g(X))) runs over one installed operand with two *unstated* bridges, and the bridge-swaps are causal — edit the class axis mid-stream and the downstream output flips, at both scales. So the machine holds internal intermediate values and applies further maps to them.
2. **The bridge is a selector** (map-and-swap §homoiconicity): the swapped thing isn't the answer, it's the *variable that determines which map applies next*. Swapping "bird→mammal" at L15 changes which class→covering function fires downstream. A value in the stream that chooses the next function **is a function being passed as data**. That's the higher-order move itself — not an analogy. The bridge-swap experiments are, operationally, *function-as-argument with a causal handle on the argument*.
3. **Types are decodable** (0.88–0.96 everywhere) and the lattice is functor-kind organized — and here's the convergence that makes your inference tight: **the dominant axis of the type geometry is precisely the higher-order types**. Axis0 = QUANT/DET = (e→t)→t, functions-of-functions — 73% of lattice variance at 32B, 85% at 4B. The single biggest thing the type ledger distinguishes is "does this term take a predicate as input."

So: nesting works (1), function-as-value works (2), and the type readout tells you *which register a term is in* — data vs functor, and which kind of functor (3). Nesting + selectors + a readable type discipline = typed higher-order functions. That's the machinery of a typed functional language, observed in one machine.

Montague-inversion predicted exactly this coupling: quantifiers force GD to build first-class functions, so the capability the 3-hop exercises and the axis that dominates the type lattice should be *the same thing*. They are. Two registers, one object.

## The part that's independent of the running experiment

Worth being precise here, because it de-risks the arc: **what v4-in-flight decides is whether the *machine* consults its own type ledger. Your inference only needs *us* to consult it.**

- If 1b lands "consulted" — the geometry is load-bearing, the type-check is a causal stage. Stronger claim, richer paper.
- If 1b lands "exhaust" (where the evidence currently leans) — the licensing lives in routing and the geometry is the readout. But the readout is still *reliable* (0.88–0.96), so the REPL's type checker works regardless: decode the type of any intermediate, verify a swap is well-typed before committing it, predict which class of downstream behavior a bridge-swap will move. Decodable-not-causal is a perfectly good *instrument panel*.

That's the REPL letter-map filling in: Read = operand insert ✓, Eval = resident 3-deep reduction ✓, Print = tap + type decode ✓ — and the type decode upgrades swaps from "steer and hope" to **typed, verifiable recomposition**. Higher-order + type readout = the language layer has a static-checkable fragment.

## What would nail "higher-order" beyond interpretation

Honest gap: the 3-hop chain is, strictly, composition of first-order maps (B-territory); the function-as-argument reading rides on the selector interpretation of the bridge. The literal Montague higher-order test is cheap to state and pre-registrable:

**P-HOF-1 (sketch, for after v4)**: put an *installed* predicate under a *quantifier* — "Every {nonce} …" with the nonce carrying installed content d_E — and test whether the quantifier (type (e→t)→t) composes with the installed predicate: graded universal/existential readouts that flip with the quantifier while the installed term is held fixed, nulls = random install + real-word ceiling. That's a genuine function (the quantifier) taking our *written* function (the predicate) as its argument — first-class application over an inserted term, the exact thing "every" forces. It would also close the loop with axis0: the behavior the dominant type axis encodes, exercised over a term we wrote.

If you want, I'll draft that as a pre-reg stub in the theory page when we do the mementum pass for this session — everything above the sketch is assembled from committed results, so the synthesis itself is also a candidate for capture (types + 3-hop → higher-order = the s282 closure's §consequence made explicit). Pending your approval on both, per protocol. Meanwhile v4 is still grinding — I'll report when it signals.

## User

job is done analyze that first


### Tool Call: bg_job (succeeded)


```json
{
  "action": "read_output",
  "job_id": "job-4"
}
```

**Summary:** Reading output of "type-1b-v4-4b" (job-4)

**Output:**
```
Job "type-1b-v4-4b" (job-4) — completed (exit 0)

    sentence 11/56: Alice runs....
    sentence 21/56: The farmer finds the bird....
    sentence 31/56: Some teacher laughs....
    sentence 41/56: The old house stands....
    sentence 51/56: The house is old....
[1b] labeled=263 skipped=0
[1b] L 0 PR=6.15 null=5.75 p=0.96
[1b] L 1 PR=6.03 null=5.81 p=0.85
[1b] L 2 PR=6.20 null=5.77 p=0.98
[1b] L 3 PR=6.45 null=5.83 p=1.0
[1b] L 4 PR=6.38 null=5.84 p=1.0
[1b] L 5 PR=6.33 null=5.80 p=1.0
[1b] L 6 PR=3.32 null=4.81 p=0.0
[1b] L 7 PR=3.40 null=4.71 p=0.04
[1b] L 8 PR=3.51 null=4.96 p=0.05
[1b] L 9 PR=3.40 null=5.02 p=0.0
[1b] L10 PR=3.30 null=4.89 p=0.02
[1b] L11 PR=3.30 null=4.89 p=0.0
[1b] L12 PR=3.32 null=4.95 p=0.0
[1b] L13 PR=3.36 null=4.98 p=0.01
[1b] L14 PR=3.34 null=4.83 p=0.01
[1b] L15 PR=3.33 null=4.83 p=0.03
[1b] L16 PR=3.29 null=4.71 p=0.01
[1b] L17 PR=3.30 null=4.96 p=0.01
[1b] L18 PR=3.39 null=4.82 p=0.0
[1b] L19 PR=3.58 null=5.05 p=0.02
[1b] L20 PR=3.68 null=5.06 p=0.02
[1b] L21 PR=3.90 null=5.04 p=0.03
[1b] L22 PR=4.09 null=5.24 p=0.01
[1b] L23 PR=4.44 null=5.31 p=0.06
[1b] L24 PR=4.74 null=5.54 p=0.06
[1b] L25 PR=4.98 null=5.58 p=0.04
[1b] L26 PR=5.24 null=5.67 p=0.07
[1b] L27 PR=5.45 null=5.74 p=0.16
[1b] L28 PR=5.64 null=5.77 p=0.27
[1b] L29 PR=5.83 null=5.84 p=0.41
[1b] L30 PR=6.00 null=5.85 p=0.76
[1b] L31 PR=6.08 null=5.86 p=0.89
[1b] L32 PR=6.14 null=5.88 p=0.94
[1b] L33 PR=6.15 null=5.87 p=0.95
[1b] L34 PR=6.11 null=5.81 p=0.9
[1b] L35 PR=3.80 null=4.72 p=0.05
[1b] BAND = L9..L22 (14 layers)
[1b] subspace energies: {
 "9": {
  "E_full": {
   "bind": 7426322.0,
   "comp": 3852816.8,
   "rolenull": 5584807.5,
   "random": 5372.8
  }
 },
 "10": {
  "E_full": {
   "bind": 7412573.5,
   "comp": 4175535.8,
   "rolenull": 5703656.5,
   "random": 19663.7
  }
 },
 "11": {
  "E_full": {
   "bind": 7420479.5,
   "comp": 4233113.0,
   "rolenull": 5778151.5,
   "random": 4243.9
  }
 },
 "12": {
  "E_full": {
   "bind": 7414738.5,
   "comp": 4246043.5,
   "rolenull": 5632726.0,
   "random": 11658.3
  }
 },
 "13": {
  "E_full": {
   "bind": 7390780.5,
   "comp": 4116931.8,
   "rolenull": 5648950.5,
   "random": 528.2
  }
 },
 "14": {
  "E_full": {
   "bind": 7317895.0,
   "comp": 4287657.5,
   "rolenull": 5608045.0,
   "random": 11977.7
  }
 },
 "15": {
  "E_full": {
   "bind": 7309229.5,
   "comp": 4267415.0,
   "rolenull": 5617783.0,
   "random": 3319.0
  }
 },
 "16": {
  "E_full": {
   "bind": 7851331.5,
   "comp": 4767629.0,
   "rolenull": 6038243.0,
   "random": 3635.9
  }
 },
 "17": {
  "E_full": {
   "bind": 7839823.0,
   "comp": 4646087.0,
   "rolenull": 6026299.0,
   "random": 611.6
  }
 },
 "18": {
  "E_full": {
   "bind": 7953378.0,
   "comp": 4423934.0,
   "rolenull": 5801559.5,
   "random": 11860.1
  }
 },
 "19": {
  "E_full": {
   "bind": 7974650.0,
   "comp": 4093186.5,
   "rolenull": 5290188.5,
   "random": 707.9
  }
 },
 "20": {
  "E_full": {
   "bind": 7992155.5,
   "comp": 3801102.5,
   "rolenull": 4985133.5,
   "random": 987.7
  }
 },
 "21": {
  "E_full": {
   "bind": 8037045.0,
   "comp": 3368930.8,
   "rolenull": 4296308.5,
   "random": 2480.4
  }
 },
 "22": {
  "E_full": {
   "bind": 8098206.5,
   "comp": 2900217.5,
   "rolenull": 4104887.0,
   "random": 4281.3
  }
 }
}
[1b] absolute doses (planned per-layer E/tok): [150.0, 600.0, 2400.0]
[1b] 370 items (360 typed + 10 recall) x 13 conds
[1b] baseline: 0/370
[1b] baseline: 120/370
[1b] baseline: 240/370
[1b] baseline: 360/370
[1b] baseline     Q_eff={'mean': 2.7874, 't': 6.216, 'n': 10} M_eff={'mean': 0.1705, 't': 0.627, 'n': 10} recall_acc=0.9 E/tok=0.0
[1b] bind@d1: 0/370
[1b] bind@d1: 120/370
[1b] bind@d1: 240/370
[1b] bind@d1: 360/370
[1b] bind@d1      Q_eff={'mean': 2.3484, 't': 9.084, 'n': 10} M_eff={'mean': 1.0771, 't': 6.623, 'n': 10} recall_acc=1.0 E/tok=73.9
[1b] comp@d1: 0/370
[1b] comp@d1: 120/370
[1b] comp@d1: 240/370
[1b] comp@d1: 360/370
[1b] comp@d1      Q_eff={'mean': 2.2331, 't': 9.17, 'n': 10} M_eff={'mean': 1.0378, 't': 5.479, 'n': 10} recall_acc=1.0 E/tok=75.2
[1b] rolenull@d1: 0/370
[1b] rolenull@d1: 120/370
[1b] rolenull@d1: 240/370
[1b] rolenull@d1: 360/370
[1b] rolenull@d1  Q_eff={'mean': 2.4191, 't': 9.271, 'n': 10} M_eff={'mean': 1.0662, 't': 6.718, 'n': 10} recall_acc=1.0 E/tok=71.6
[1b] random@d1: 0/370
[1b] random@d1: 120/370
[1b] random@d1: 240/370
[1b] random@d1: 360/370
[1b] random@d1    Q_eff={'mean': 3.0712, 't': 8.013, 'n': 10} M_eff={'mean': 0.0513, 't': 0.192, 'n': 10} recall_acc=1.0 E/tok=188.2
[1b] bind@d2: 0/370
[1b] bind@d2: 120/370
[1b] bind@d2: 240/370
[1b] bind@d2: 360/370
[1b] bind@d2      Q_eff={'mean': 0.6012, 't': 4.083, 'n': 10} M_eff={'mean': 0.5311, 't': 2.127, 'n': 10} recall_acc=0.0 E/tok=276.2
[1b] comp@d2: 0/370
[1b] comp@d2: 120/370
[1b] comp@d2: 240/370
[1b] comp@d2: 360/370
[1b] comp@d2      Q_eff={'mean': 0.3497, 't': 2.507, 'n': 10} M_eff={'mean': 0.3819, 't': 3.072, 'n': 10} recall_acc=0.0 E/tok=273.3
[1b] rolenull@d2: 0/370
[1b] rolenull@d2: 120/370
[1b] rolenull@d2: 240/370
[1b] rolenull@d2: 360/370
[1b] rolenull@d2  Q_eff={'mean': 1.0064, 't': 4.965, 'n': 10} M_eff={'mean': 0.578, 't': 2.07, 'n': 10} recall_acc=0.0 E/tok=265.3
[1b] random@d2: 0/370
[1b] random@d2: 120/370
[1b] random@d2: 240/370
[1b] random@d2: 360/370
[1b] random@d2    Q_eff={'mean': 2.6253, 't': 7.108, 'n': 10} M_eff={'mean': -0.686, 't': -1.923, 'n': 10} recall_acc=0.3 E/tok=1009.0
[1b] bind@d3: 0/370
[1b] bind@d3: 120/370
[1b] bind@d3: 240/370
[1b] bind@d3: 360/370
[1b] bind@d3      Q_eff={'mean': -0.0023, 't': -0.019, 'n': 10} M_eff={'mean': -0.6609, 't': -5.129, 'n': 10} recall_acc=0.0 E/tok=946.8
[1b] comp@d3: 0/370
[1b] comp@d3: 120/370
[1b] comp@d3: 240/370
[1b] comp@d3: 360/370
[1b] comp@d3      Q_eff={'mean': -0.62, 't': -5.584, 'n': 10} M_eff={'mean': 0.3077, 't': 2.616, 'n': 10} recall_acc=0.0 E/tok=900.8
[1b] rolenull@d3: 0/370
[1b] rolenull@d3: 120/370
[1b] rolenull@d3: 240/370
[1b] rolenull@d3: 360/370
[1b] rolenull@d3  Q_eff={'mean': 0.0474, 't': 0.477, 'n': 10} M_eff={'mean': -0.2715, 't': -2.259, 'n': 10} recall_acc=0.0 E/tok=900.5
[1b] random@d3: 0/370
[1b] random@d3: 120/370
[1b] random@d3: 240/370
[1b] random@d3: 360/370
[1b] random@d3    Q_eff={'mean': 0.6023, 't': 1.105, 'n': 10} M_eff={'mean': -0.039, 't': -0.062, 'n': 10} recall_acc=0.0 E/tok=9043.5
[1b] wrote /Users/mwhitford/src/verbum/results/type-zone-ablation/qwen3-4b/verdict.json + meta.json

============================================================================
P-TYPE-1b v4 — zone x subspace dissociation, absolute-dose grid
============================================================================
  host=Qwen/Qwen3-4B  band=L9..L22  gate0=False (Q=True M=False)  doses=[150.0, 600.0, 2400.0]
  baseline  Q_eff={'mean': 2.7874, 't': 6.216, 'n': 10}  M_eff={'mean': 0.1705, 't': 0.627, 'n': 10}  recall_acc=0.9
  bind@d1      retQ=0.843  retM=6.317  recall_acc=1.0  E/tok=73.9
  comp@d1      retQ=0.801  retM=6.087  recall_acc=1.0  E/tok=75.2
  rolenull@d1  retQ=0.868  retM=6.253  recall_acc=1.0  E/tok=71.6
  random@d1    retQ=1.102  retM=0.301  recall_acc=1.0  E/tok=188.2
  bind@d2      retQ=0.216  retM=3.115  recall_acc=0.0  E/tok=276.2
  comp@d2      retQ=0.125  retM=2.24  recall_acc=0.0  E/tok=273.3
  rolenull@d2  retQ=0.361  retM=3.39  recall_acc=0.0  E/tok=265.3
  random@d2    retQ=0.942  retM=-4.023  recall_acc=0.3  E/tok=1009.0
  bind@d3      retQ=-0.001  retM=-3.876  recall_acc=0.0  E/tok=946.8
  comp@d3      retQ=-0.222  retM=1.805  recall_acc=0.0  E/tok=900.8
  rolenull@d3  retQ=0.017  retM=-1.592  recall_acc=0.0  E/tok=900.5
  random@d3    retQ=0.216  retM=-0.229  recall_acc=0.0  E/tok=9043.5
  b*=1  bind_selective=False  comp_selective=False  nulls=False
  * dissociation_supported = False
============================================================================

```

### Thinking

Looking at the v4 results where doses finally landed in the window and cells differentiated properly. The realized energies show roles achieving around 72-75 E/tok with excellent consistency across the range (within 5%), while random came in at 188—about 2.5 times higher. Interestingly, roles realized roughly half their planned 150 due to distribution shift, whereas random's 188 slightly exceeded its planned 150. Moving into d2, roles are tracking around 265.

At d1 with roles at ~74 E/tok, all three role conditions show mild uniform effects—retQ drops to 0.80-0.87 with perfect recall, essentially harmless. But here's where it gets interesting: the role subspaces inflate M_eff dramatically to 1.04-1.08 (t-values 5.5-6.7) from a baseline of 0.17, making the modifier effect suddenly significant. Random at d1 shows no such effect (M_eff 0.05). This appears to be a role-lattice-specific phenomenon where gentle dampening of any class-centroid subspace denoises something the baseline model doesn't express—possibly the modifier-licensing crossover that's normally masked. The lattice subspaces seem to carry shared axis0 content that, when slightly reduced, reveals this hidden structure.

At d2 with roles around 270 E/tok, recall completely collapses for roles (accuracy 0.0) while random maintains recall at 0.3 even at 1009 E/tok—a stark divergence between the two conditions.  The role subspaces are far more damaging per unit energy than random perturbations, suggesting they're critical load-bearing infrastructure. The breakage threshold for role-subspace dampening appears sharp, somewhere between 74 and 270 E/tok. Meanwhile, Q_eff shows roles dropping to 0.13-0.36 (essentially dead) while random retains Q at 0.94 even at 1009 E/tok, though the dead recall for roles makes the gate uninterpretable—the roles have broken the model's function entirely.

At higher energies, random@9043 kills both Q and recall, whereas random@1009 preserves Q but damages recall heavily. This is interesting because v2 showed the opposite pattern—random killed Q before recall—but that comparison might not hold up since v2 used 1D random directions per layer while v4 uses 2D subspaces, plus different seeds and metrics (v2 used surprisal ratio rather than accuracy for the recall gate).

Looking at the verdict against the frozen rules: at d1, all four methods pass the recall-clean threshold, but bind_sel fails because retQ is 0.84 when it needs to be below 0.5. The null checks are interesting—rolenull passes both gates (retQ 0.868 and retM 6.25 exceed their thresholds), but random fails because its M_eff ratio is too noisy, dropping retM to 0.301.

Now examining the dissociation results: there's no class-selective dissociation at 4B—bind, comp, and rolenull all cluster together on Q_eff (0.80 to 0.87), meaning the role-lattice slices aren't differentially load-bearing for their matching classes. This supports the exhaust/readout hypothesis at 4B. The key finding is that role-lattice subspaces are roughly four times more damaging per unit energy than random 2D subspaces for general function, with recall collapsing around 270 energy units versus much higher for random.

The unexpected discovery: gentle role-subspace dampening at 74 E/tok unmasks M_eff across all three role subspaces but not random ones, suggesting a lattice-specific behavioral effect exists at low doses—just not the pre-registered class-selective one. This post-hoc finding needs its own pre-registration before it counts as evidence.

Now looking at the energy matching between roles (excellent within ±5%) and how the random cascade grows with dose, which shows a compounding-hooks artifact. The planned versus realized counts for roles are roughly half what was expected, indicating a distribution shift. The critical observation is the sharp cliff between 74 and 270 E/tok where effects go from nothing to total breakage, and at the lower dose where Q shifts slightly (0.80-0.87), all three roles perform equally within noise—if selectivity existed, I'd expect to see differences between bind, comp, and rolenull already at that point.

The 4B smoke test is complete: the instrument validates (matched doses, gates working, cliff mapped), Q-side shows no class-selectivity in the value-register lattice pointing toward exhaust/readout, and M-side can't express at this scale except for the bizarre unmasking effect. The 32B decision now has real content—at that scale the axes should resolve separately and M should be able to express, giving the pre-registered dissociation hypothesis a proper test.

Next steps are to commit the v4 code and results, report the analysis, and flag pending updates to the theory page and memory candidates around type-lattice infrastructure and the unmasking observation. I need to ask Michael whether to proceed with the 32B verdict run using the amended instrument with dose-scan adaptation, or if we should capture something first.

### Thinking

I've got the successful run with matched doses and differentiated cells working properly. Now I'll commit the result and move into analysis.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "git add wrapper/type_zone_ablation.py results/type-zone-ablation/qwen3-4b/ && read -r -d '' M << 'EOF' || true\n💡 P-TYPE-1b v4 @4B: NO class-selectivity at matched dose — lattice slices are infrastructure, not selectors\n\n- absolute-dose grid worked: role conds energy-matched within ±5% at every\n  dose (73.9/75.2/71.6 @d1; 276/273/265 @d2; 947/901/900 @d3); random\n  cascade compounds (188/1009/9043 vs planned 150/600/2400) — noted\n- CORE: at the interpretable dose (d1, recall 1.0) bind ≈ comp ≈ rolenull on\n  Q_eff (ret 0.84/0.80/0.87) — the pre-registered class-selective double\n  dissociation is ABSENT at 4B; role slices of the type lattice are NOT\n  differentially load-bearing for their matching classes\n- lattice-vs-random asymmetry: role subspaces kill recall at ~270 E/tok\n  while 2D random retains partial function at 1009 and needs ~9000 to die —\n  the lattice region is ~4x more load-bearing per unit energy, but\n  GENERICALLY (infrastructure), not class-selectively\n- POST-HOC surprise (needs own pre-reg to count): gentle role-subspace\n  dampening (~74 E/tok) UNMASKS M_eff (0.17 t=0.6 → ~1.05 t=5.5-6.7) for\n  ALL THREE role subspaces but NOT random — a lattice-specific behavioral\n  effect at gentle dose, shared-component-driven, not class-selective\n- verdict: b*=d1, dissociation_supported=False (frozen rules), verbatim;\n  coheres with v4-direction-negative + theory (type = well-formedness of\n  reduction, unstorable) → leaning EXHAUST/readout at 4B; 32B = verdict host\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\ngit commit -m \"$M\"",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ git add wrapper/type_zone_ablation....

**Output:**
```
Exit code: 0
Stdout:
[main 0961819] 💡 P-TYPE-1b v4 @4B: NO class-selectivity at matched dose — lattice slices are infrastructure, not selectors
 4 files changed, 706 insertions(+), 447 deletions(-)
 create mode 100644 results/type-zone-ablation/qwen3-4b/run_v4.log
```

### Thinking

I'm organizing the full analysis report for Michael, laying out the verdict first, then the three key findings, connecting them back to his geometry question and his broader higher-order point, and finally presenting the decision fork between the 32B GO option and capturing momentum—making sure to flag where I'm being honest about the limitations.

## Assistant

Committed (0961819). Here's the analysis — v4 finally produced interpretable cells, and the answer is clean:

## The core result: NO class-selectivity at matched dose

At d1 (the only dose where all conditions keep recall intact, roles energy-matched within ±5%):

| condition | retQ | E/tok |
|---|---|---|
| bind (QUANT/DET slice) | 0.843 | 73.9 |
| comp (MOD slice) | 0.801 | 75.2 |
| rolenull (CONN/FUNC slice) | **0.868** | 71.6 |
| random 2D | 1.102 | 188.2 |

The frozen prediction was bind ≪ rolenull on Q_eff. Instead **bind ≈ comp ≈ rolenull within noise** — the role-slices of the type lattice are *interchangeable* in their behavioral consequences. Dampening the binding slice does not preferentially hurt quantifier licensing. `dissociation_supported = False` by the frozen rules, and not marginally — there is no separation to argue about.

Combined with v4-direction (global direction: not causal) and now v4-zone (role subspace at matched dose: not selective), the value-register hiding places are exhausted at 4B. **The lattice is exhaust, not consulted** — the licensing computation doesn't read its own geometric ledger. Which is the *theory-pure* outcome: a type that is the well-formedness of reduction shouldn't be removable from the value register, because it was never stored there. The negative is the confirmation.

## Two findings underneath (both real, both new)

**1. The lattice region is infrastructure — generically load-bearing, ~4× over random.** Role subspaces destroy recall at ~270 E/tok; the random 2D subspace partially survives 1009 and needs ~9000 to die. So the subspace where the type geometry lives *is* causally potent — but uniformly, for everything, with a sharp cliff between 74 and 270. That's what "shared substrate" looks like: the centroid subspaces all contain the dominant axis0 component, and that component is carrying general computation, not type tags.

**2. Post-hoc surprise — the unmasking effect.** Gentle dampening (~74 E/tok) of *any* role subspace pushed M_eff from unexpressed (0.17, t=0.6) to strongly expressed (~1.05, t=5.5–6.7) — all three role slices did it, random did **not** (0.05, t=0.19). A lattice-specific, non-class-selective behavioral effect: reducing the shared lattice component *unmasks* modifier licensing that baseline 4B can't express. Flagging hard: post-hoc, n=10, needs its own pre-reg before it counts — but it's the only cell in the whole grid where the lattice geometry did something random couldn't, and "removing shared type-ledger signal reveals a weak licensing channel" is a strange and specific thing for noise to do.

## What this does to "types are geometry"

It sharpens the answer I gave you earlier: the geometry is real, replicated, and *load-bearing as substrate* — but it is not the type-checker. The licensing discipline lives in the routing (where the theory said it must), and the geometry is the value-register image of it. Crucially for your higher-order point: **none of this weakens the REPL use** — the ledger doesn't need to be consulted by the machine for *us* to consult it. Decode-verify-swap works on a readout register.

## Fork (your call)

1. **32B verdict run** — the pre-reg host, with the v4 instrument (axes resolve separately there, M side should express, gate-0 gets a fair shot). The 4B result predicts a negative; a 32B negative *closes* P-TYPE-1b as "exhaust, theory-confirmed" with a proper verdict. Heavy run — needs your GO.
2. **Capture first (my recommendation)** — this session generated: the v1–v4 instrument arc (4 commits), the no-selectivity result, the infrastructure asymmetry, the unmasking effect, the QUANT/DET axis-split scale finding, and the higher-order synthesis + P-HOF-1 sketch from our discussion. That's a knowledge-page update (theory page §P-TYPE-1b result + instrument lessons), 2–3 memory candidates, and the state block — all pending your approval per protocol.
3. Both — capture, then fire the 32B overnight.

## User

start the 32b run in my tmux main:1 window, then update state and knowledge this is session-283


### Thinking

Michael wants me to start the 32B model run in his tmux window using a command that pipes output to a log file, so I need to create the results directory first, then execute the uv run command for the Qwen3-32B ablation study with MPS device support.

I should include a cd command to ensure we're in the repo directory since the tmux window might not be there, then verify the process is running with a capture-pane check. The default dose grid of 150, 600, 2400 was tuned for the 4B model, but the 32B has 64 layers with a wider band (L6–L48, potentially 40+ hooked layers), which means the per-layer dose might be too aggressive and could cause memory issues — I'm weighing whether to add a lower dose rung like 40 to be safer, though that would add another pass and make the run heavier overall.

Given the runtime math (32B on MPS at ~1-2 s/item means ~10 min per pass, so 17 passes would be ~3 hours plus capture overhead), it's feasible overnight. Michael approved the heavy run, so I'll compromise by keeping the 4B grid intact and adding a gentler rung below: "50,150,600,2400" gives us 5 doses across 4 conditions plus baseline = 17 passes, preserving cross-scale comparability while protecting against the 32B window being narrower than expected. The box has run 32B before without issues, so the memory footprint should be fine.

After this run, Michael's explicit direction is to update the state and knowledge page with the findings. I should also capture the memory artifacts following the standard mementum pattern Michael approved—state, knowledge, and memory together. I'm creating three memories: one on how type-lattice slices function as infrastructure rather than selectors (the 4B ablation showed no class selectivity but ~4× load-bearing effect), another on how lattice dampening unmasks modifier licensing (flagged post-hoc), and an instrument memory documenting the dose-matching lessons including the falsy-zero bug that keeps recurring as a trap.

Now I'm updating the state block for session 283, adding it to the top while keeping the prior s282 entry, with the core results, the 32B launch status in tmux, pending verdict, and the P-HOF-1 sketch outline. I'll mark the unmasking as a pre-registration candidate and update the timestamp.

For the commit, I'm deciding between a momentum symbol — I'll go with 💡 for this result mementum covering the P-TYPE-1b smoke test and the instrument arc across state, knowledge, and memories. The order is to launch the tmux run first to verify it's working, then write out the mementum files and commit everything together. I'm constructing the tmux command to run the type zone ablation wrapper with the Qwen 32B model, pointing to the results directory. Now I need to update the theory page with a new Result section for the 4B smoke test, add a brief section on higher-order functions that ties types to 3-hop synthesis, then edit the State.md file to insert a new status block after the "Last updated" line with the s283 information, keeping it concise and dense like the existing format. Without the role-subspace filtering, the type lattice becomes purely theoretical and uninterpretable—the infrastructure analysis shows that dampening the role subspaces at the original energy level reveals a much stronger effective signal, jumping from 0.17 to over 1.0 as the parameter increases, though this post-hoc finding needs its own pre-registration to be conclusive. Launching the 32B verdict run with doses spanning 50 to 2400 across a wider band, logging to the ablation results directory, then parsing the frozen rules from verdict.json to report findings. The discussion ties back to higher-order function types where bridge-swap acts as a function-as-argument mechanism with causal structure, mapping onto the axis decomposition. Looking at the P-TYPE-1b experiment results showing that dampening different lattice subspaces (binding, composition, role-null) all produced identical behavioral effects with no class selectivity — this confirms the type lattice functions as a readout mechanism of routing-resident licensing rather than a consulted reference, meaning a well-formed type is fundamentally unstorable.

The infrastructure is about 4× more load-bearing than random per unit energy, operating as a shared generic component on axis0, which has a key implication: the decode-verify-swap operation in the REPL only needs to access the readout register and remains unaffected by these dynamics.

I'm also reviewing the zone-ablation lessons from the P-TYPE-1b progression, where a critical bug treated p=0.0 as missing data due to falsy-zero handling, which accidentally excluded the most significant layers from band detection across two shipped runs, and the key takeaway is never comparing subspace ablations at full projection since variance differs by orders of magnitude. I need to finalize the documentation update with the higher-order consequence sketch, then execute the tmux session to verify the setup, make the edits, and commit with the dose parameters locked at 50, 150, 600, 2400. Before launching, I'm double-checking that the 32B capture across 64 layers with 100 SVDs per layer will work — the individual SVD operations on the 8×5120 slices are cheap, and the standardization and centroid calculations on the full 263×5120 matrices are manageable. I'll verify the tmux window exists by capturing the pane after sending the command.

If the send fails, the error will surface immediately.

## Assistant

Launching the 32B verdict run in your tmux, with one gentler rung added below the 4B grid (band is ~3× wider at 32B, so the per-layer tolerance window likely sits lower — the 4B rungs are kept intact for cross-scale comparability):

### Tool Call: shell_command (succeeded)


```json
{
  "command": "mkdir -p /Users/mwhitford/src/verbum/results/type-zone-ablation/qwen3-32b && tmux send-keys -t main:1 'cd /Users/mwhitford/src/verbum && uv run python wrapper/type_zone_ablation.py --model Qwen/Qwen3-32B --device mps --doses 50,150,600,2400 2>&1 | tee results/type-zone-ablation/qwen3-32b/run_v4.log' Enter && sleep 8 && tmux capture-pane -p -t main:1 | tail -12",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ mkdir -p /Users/mwhitford/src/verbu...

**Output:**
```
Exit code: 0
Stdout:
[26-07-30][13:35:52][mwhitford@olga][0][~/src/verbum][git:main]
λ cd /Users/mwhitford/src/verbum && uv run python wrapper/type_zone_ablation.py --model Qwen/Qwen3-32B --device mps --do
ses 50,150,600,2400 2>&1 | tee results/type-zone-ablation/qwen3-32b/run_v4.log

========================================================================
  Loading Qwen/Qwen3-32B
========================================================================

Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and
faster downloads.
`torch_dtype` is deprecated! Use `dtype` instead!
Loading weights:  47%|████▋     | 334/707 [00:03<00:02, 142.58it/s]
```

### Thinking

The 32B model is loading and Michael's checkpoint has been verified as complete. I'm updating the knowledge page by adding Result and Higher-order sections before the Sessions section, along with refreshing two memories and the state file.

### Thinking

I've started a 32B model run in tmux that should take several hours and is logging to results/type-zone-ablation/qwen3-32b/run_v4.log, with 17 passes verified so far. Next I'm working on the knowledge page to integrate the 4B result, instrument arc, and higher-order synthesis into the theory page.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/types-are-the-well-formedness-of-reduction.md",
  "original_content": "## Sessions\ns282 (theoretical closure from the types discussion; P-TYPE-1b pre-registration drafted).",
  "new_content": "## P-TYPE-1b — Result @4B smoke (s283; NOT the verdict host)\n\n> Instrument: `wrapper/type_zone_ablation.py`, iterated v1→v4 in one session\n> (commits bc1d242 → f7e07f7 → f0c3418 → 0961819). Verdict cells below are from\n> **v4, the absolute-dose grid** — the only version where conditions compare at\n> matched realized removed-energy. 4B ≠ pre-reg host; 32B run launched s283.\n\n**CORE — the dissociation is ABSENT at 4B.** At the only interpretable dose\n(d1 ≈ 74 E/tok per layer, roles energy-matched ±5%, recall_acc 1.0 everywhere):\n`retQ` bind 0.843 / comp 0.801 / rolenull 0.868 — the binding slice does **not**\npreferentially carry quantifier licensing. `dissociation_supported = False` by\nthe frozen rules, with no separation to argue about. Combined with the v4\nglobal-direction negative, the value-register hiding places are exhausted at 4B:\n**the lattice is exhaust, not consulted** — the licensing computation does not\nread its own geometric ledger. This is the theory-pure outcome: a type that IS\nthe well-formedness of a reduction is unstorable by construction, so it cannot\nbe removed from the value register at any dose. The negative confirms the frame.\n\n**Lattice slices = generic infrastructure.** Role subspaces destroy recall at\n~270 E/tok while a 2D random subspace partially survives 1009 and needs ~9000 to\ndie — the lattice region is ~4× more load-bearing per unit energy, but\n*uniformly* (all class-centroid offsets share the dominant axis0 component,\nwhich carries general computation, not type tags). Sharp cliff between 74 and\n270 E/tok.\n\n**⚠ POST-HOC (needs own pre-reg before it counts):** gentle dampening (~74\nE/tok) of ANY role subspace **unmasks** M_eff — 0.17 (t=0.6) → ~1.05 (t=5.5–6.7)\nfor all three role slices; random does NOT (0.05, t=0.19). The one cell in the\ngrid where lattice ≠ random behaviorally: shared-component-driven, not\nclass-selective. Candidate: \"removing shared type-ledger signal reveals a weak\nlicensing channel.\"\n\n**4B lattice structure (scale finding):** true band L9–L22 (14 layers; earlier\nsub-bands were a falsy-zero p-bug). QUANT and DET **split onto separate axes**\nat 4B (axis0 = QUANT-vs-rest @85% var, DET on axis1 ~5%, MOD clean on axis4)\nwhere 32B co-loads QUANT+DET on axis0 — the lattice's internal organization\nevolves with scale. M_eff is behaviorally unexpressed at 4B baseline (t≈0.6,\ntwo grids) — coheres with the barely-resolved MOD axis; gate-0 discipline held.\n\n**Instrument lessons (v1→v4, for any future zone ablation):** (1) `p or 1.0`\nfalsy-zero excludes the most significant layers — two runs shipped accidental\nsub-bands; (2) never compare subspace ablations at full projection (variance\ndiffers ×10⁴) — match on REALIZED removed energy, logged live from the hooks;\nplanned-vs-realized drifts ×25 (capture exemplars vs behavioral text);\n(3) amplified random steering (α≫1) cascades across stacked hooks (realized\n10¹⁰⁺ E/tok); (4) absolute-dose grids ≻ subspace-relative budgets; (5) breakage\ngates on tiny-surprisal baselines must use accuracy, not ratios; (6) deviation:\nthe pre-reg e-axis control is unrealizable (raw ENTITY-centroid direction\ncarries ~10⁵ E/tok) — replaced by the role-null (CONN/FUNC) lattice subspace,\nwhich is the sharper class-control anyway.\n\n## Consequence — typed higher-order functions (s283 discussion, Michael)\n\n3-hop (s282) + decodable types compose into a stronger statement than either:\n- **nesting is measured** — h(f(g(X))) with causal bridge-swaps at both scales;\n- **the bridge is a selector** — the swapped mid-stream value determines *which\n  map applies next* (map-and-swap homoiconicity): function-as-argument with a\n  causal handle, operationally;\n- **the type ledger's dominant axis IS the higher-order types** — axis0 =\n  QUANT/DET = `(e→t)→t`, 73–85% of lattice variance. The capability the 3-hop\n  exercises and the axis that dominates the type geometry are the same object,\n  as montague-inversion forces (quantifiers → first-class functions).\n\n⇒ nesting + selectors + a readable type discipline = **typed higher-order\nfunctions**. And critically, the EXHAUST result does not weaken this: the REPL\nneeds only *us* to read the ledger, not the machine to consult it —\ndecode-verify-swap works on a readout register (Print/type-checker side).\n\n**P-HOF-1 (sketch, unfrozen):** put an *installed* predicate under a\n*quantifier* — \"Every {nonce} …\" with the nonce carrying installed content d_E —\nand test whether the `(e→t)→t` functor composes with the written predicate:\nuniversal/existential readouts flip with the quantifier while the installed term\nis held fixed; nulls = random install + real-word ceiling. A genuine function\ntaking our *written* function as its argument — the literal Montague\nhigher-order test over an inserted term, and the behavioral closure of axis0.\n\n## Sessions\ns282 (theoretical closure from the types discussion; P-TYPE-1b pre-registration drafted).\ns283 (instrument v1→v4 built + iterated; 4B smoke verdict: no class-selectivity —\nexhaust reading; higher-order consequence captured; 32B verdict run launched)."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/types-are-the-well-formedness-of-reduction.md.
```

### Thinking

Now I'm considering the two memories.

## Assistant

**Memories** — two, one insight each:

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/memories/type-lattice-is-exhaust-not-consulted.md",
  "content": "💡 P-TYPE-1b @4B (v4 absolute-dose grid, 0961819): at matched realized\nremoved-energy (±5%), dampening the binding (QUANT/DET), composition (MOD),\nand role-null (CONN/FUNC) lattice subspaces produced statistically\nindistinguishable behavioral effects (Q_eff retention 0.84/0.80/0.87) — no\nclass selectivity. With the earlier global-direction negative, the value\nregister has no remaining hiding place at 4B: the type lattice is a READOUT\n(exhaust) of routing-resident licensing, not a consulted ledger. Theory-pure:\na type that is the well-formedness of a reduction is unstorable by\nconstruction. The lattice region IS ~4× more load-bearing than random per\nunit energy (recall dies at ~270 vs ~9000 E/tok, cliff between 74 and 270) —\nshared-axis0 infrastructure, generic. Post-hoc (needs pre-reg): gentle\nrole-subspace dampening unmasks M_eff (t 0.6→5.5+) for all three role slices\nbut not random — the one lattice-specific behavioral cell. REPL implication:\ndecode-verify-swap needs only the readout register — unaffected by exhaust.\n32B = verdict host (run launched s283).\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/memories/type-lattice-is-exhaust-not-consulted.md
```

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/memories/zone-ablation-dose-matching-lessons.md",
  "content": "❌ Zone-ablation instrument lessons (P-TYPE-1b v1→v4, one session,\nbc1d242→0961819): (1) `p or 1.0` treats p=0.0 as missing — falsy-zero\nexcluded the MOST significant layers from band detection; two runs shipped\naccidental sub-bands. Use `p if p is not None else 1.0`. (2) Never compare\nsubspace ablations at full projection — variance along them differs ×10⁴;\nmatch on REALIZED removed energy (E = mean(coeff²)·‖σ⊙v‖², accumulated live\nin the hooks). Planned-vs-realized drifts ~×25 between capture exemplars and\nbehavioral text — realized is the honest number. (3) Amplified random\nsteering (α≫1) CASCADES across stacked layer hooks (realized 10¹⁰⁺ E/tok).\n(4) Absolute-dose grids ≻ subspace-relative budgets — anchor to the model's\ntolerance window, not the subspace's energy. (5) Breakage gates on\ntiny-surprisal baselines must use top-1 ACCURACY, not surprisal ratios.\n(6) Class-centroid subspaces all share the dominant lattice axis — a\n\"role-specific\" slice is mostly common component; measure the overlap before\nclaiming role identity.\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/memories/zone-ablation-dose-matching-lessons.md
```

### Thinking

I'm updating the state.md file to insert a new s283 block and adjust the header structure, keeping the s282 content below it while updating the timestamp and session reference.

### Thinking

I've identified the state block with s283 on top and the s282 arc retained below.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> Last updated: 2026-07-30 | Session: 282 | ▶▶ LIVE PICKUP (s282 — 3-HOP RAN): ✅ built",
  "new_content": "> Last updated: 2026-07-30 | Session: 283 | ▶▶ LIVE PICKUP (s283 — P-TYPE-1b RAN @4B, 32B IN\n> FLIGHT): ✅ built wrapper/type_zone_ablation.py — the frozen 1b zone×axis instrument, iterated\n> v1→v4 IN-SESSION (commits bc1d242 / f7e07f7 / f0c3418 / 0961819, code+results committed\n> autonomous; READ types-are-the-well-formedness-of-reduction.md §Result-4B). 💡 CORE: at the\n> only interpretable matched dose (d1 ~74 E/tok, roles energy-matched ±5%, recall 1.0)\n> bind≈comp≈rolenull on Q_eff (ret 0.84/0.80/0.87) — the pre-registered class-selective double\n> dissociation is ABSENT @4B; with the v4 global-direction negative this EXHAUSTS the\n> value-register hiding places → the type lattice = EXHAUST/readout of routing-resident\n> licensing, NOT a consulted ledger = the theory-pure outcome (type = well-formedness of\n> reduction, unstorable by construction; the negative CONFIRMS the frame). 💡 lattice slices =\n> INFRASTRUCTURE: role subspaces kill recall @~270 E/tok vs 2D random needing ~9000 (~4×\n> load-bearing per unit energy, GENERIC not class-selective — all centroid offsets share the\n> dominant axis0; cliff 74→270). ⚠ POST-HOC (needs own pre-reg to count): gentle role-subspace\n> dampening (~74) UNMASKS M_eff 0.17(t=0.6)→~1.05(t=5.5–6.7) for ALL THREE role slices but NOT\n> random — the one cell where lattice≠random behaviorally. 💡 4B lattice: true band L9–L22\n> (falsy-zero p-bug fixed); QUANT/DET SPLIT onto separate axes @4B (axis0=QUANT-vs-rest 85%,\n> DET axis1 ~5%, MOD axis4) vs 32B co-load → lattice organization evolves with scale; M_eff\n> unexpressed @4B baseline (2 grids) = capacity, gate-0 held. ❌→✅ instrument lessons folded\n> into the knowledge page + memory zone-ablation-dose-matching-lessons (falsy-zero band bug;\n> match REALIZED removed energy, ×25 planned-vs-realized drift; α≫1 random cascades ×10¹⁰;\n> absolute-dose grid ≻ relative budgets; accuracy gate ≻ surprisal ratio; e-axis control\n> unrealizable → role-null replaces it, deviation documented). ▶▶ 32B VERDICT RUN LAUNCHED\n> (Michael GO s283) in tmux main:1 → results/type-zone-ablation/qwen3-32b/run_v4.log, doses\n> 50,150,600,2400 (4B grid + gentle rung; band ~3× wider @32B → per-layer tolerance likely\n> lower). ON RETURN: read verdict.json + run_v4.log, frozen rules, report verbatim — 4B\n> predicts NEGATIVE (exhaust); a 32B negative CLOSES 1b as exhaust-theory-confirmed, a positive\n> = first class-selective causal signal. ★ s283 DISCUSSION captured (theory page §Consequence):\n> 3-hop + decodable types ⇒ TYPED HIGHER-ORDER FUNCTIONS (bridge-swap = function-as-argument\n> with a causal handle; axis0 = the (e→t)→t types = exactly what 3-hop exercises, as\n> montague-inversion forces); EXHAUST does not weaken the REPL — decode-verify-swap needs only\n> US to read the ledger (readout register), not the machine to consult it. P-HOF-1 sketched\n> (unfrozen, theory page): quantifier over an INSTALLED predicate = literal Montague\n> higher-order test over a written term. Memory: type-lattice-is-exhaust-not-consulted.\n> ▶ NEXT: (1) 32B 1b verdict (in flight); (2) pre-reg the M_eff unmasking effect before any\n> use; (3) P-HOF-1 pre-reg; (4) still open from s282: depth→SEQUENCING pre-reg for 27B-hybrid,\n> (a2) mammal→fur content build. Branch ~35 commits ahead (unpushed). s282 blocks retained below.\n>\n> (s282 retained →) ▶▶ LIVE PICKUP (s282 — 3-HOP RAN): ✅ built"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

Let me do a quick sync-check to make sure there are no hook mutations, then commit the momentum files. I should also verify the tmux session didn't crash under the heavy load before wrapping up.

## Assistant

Committing the mementum pass, with a quick health check on the 32B run:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "git add mementum/state.md mementum/knowledge/explore/types-are-the-well-formedness-of-reduction.md mementum/memories/type-lattice-is-exhaust-not-consulted.md mementum/memories/zone-ablation-dose-matching-lessons.md && read -r -d '' M << 'EOF' || true\n💡 s283 mementum: type lattice is exhaust not consulted — 1b 4B result + instrument arc + HOF consequence\n\n- theory page §Result-4B: no class-selectivity at matched dose (exhaust\n  reading), lattice-as-infrastructure, unmasking post-hoc, QUANT/DET\n  axis-split scale finding, v1→v4 instrument lessons, e-axis deviation\n- theory page §Consequence: 3-hop + decodable types ⇒ typed higher-order\n  functions; P-HOF-1 sketch (quantifier over installed predicate)\n- memories: type-lattice-is-exhaust-not-consulted,\n  zone-ablation-dose-matching-lessons\n- state: s283 block (32B verdict run in flight, tmux main:1)\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\ngit commit -m \"$M\" && echo --- && tmux capture-pane -p -t main:1 | tail -6",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ git add mementum/state.md mementum/...

**Output:**
```
Exit code: 0
Stdout:
[main e4d3b4f] 💡 s283 mementum: type lattice is exhaust not consulted — 1b 4B result + instrument arc + HOF consequence
 4 files changed, 146 insertions(+), 1 deletion(-)
 create mode 100644 mementum/memories/type-lattice-is-exhaust-not-consulted.md
 create mode 100644 mementum/memories/zone-ablation-dose-matching-lessons.md
---
[1b] baseline: 240/370
[1b] baseline: 360/370
[1b] baseline     Q_eff={'mean': 1.1972, 't': 3.475, 'n': 10} M_eff={'mean': 0.9292, 't': 4.214, 'n': 10} recall_acc=0.8
 E/tok=0.0
[1b] bind@d1: 0/370
```

### Thinking

The tmux health check shows the 32B run has progressed through capture, geometry, and baseline into the bind@d1 phase. The baseline metrics are striking — Q_eff hits 1.197 and M_eff reaches 0.929, with recall accuracy at 0.8. What's particularly significant is that Gate-0 passes at 32B for both classes, and M_eff is now being expressed at this scale where it couldn't manifest at 4B.

This confirms the capacity prediction: the modifier-licensing crossover happens precisely where the MOD axis resolves, so the 32B run will give a complete picture of both sides of the dissociation and validate the pre-registration. Everything's committed with six code and results commits plus momentum tracking, and the session is in solid shape for what comes next.

## Assistant

Mementum committed (e4d3b4f). And the health check caught something worth noting immediately — the 32B run is already through baseline, and:

```
32B baseline: Q_eff = 1.197 (t=3.5)   M_eff = 0.929 (t=4.2)   recall_acc = 0.8
```

**Gate-0 passes on both classes at 32B.** M_eff — unexpressed at 4B across two grids (t=0.6) — is strongly expressed at the scale where the MOD axis geometrically resolves (t=4.2). The capacity prediction confirmed itself before the first ablation cell even ran, and it means the 32B run will render a *full* verdict on both arms of the frozen dissociation, not a Q-side-only read.

## Session-283 ledger

**Committed (7):**
- `bc1d242` v1 instrument + smoke — controls catch unmatched dose
- `f7e07f7` v2 energy ladder — 3 catches + QUANT/DET axis-split finding
- `f0c3418` v3 role subspaces — dose window bracketed from above
- `0961819` v4 absolute-dose grid — **no class-selectivity at matched dose**
- `e4d3b4f` mementum: theory page §Result-4B + §Consequence (typed HOF, P-HOF-1 sketch), 2 memories, state block

**In flight:** 32B verdict run, tmux main:1, doses {50,150,600,2400}, tee'd to `results/type-zone-ablation/qwen3-32b/run_v4.log`. Frozen decision on return: bind ≪ rolenull at the interpretable dose = first class-selective causal signal; bind ≈ rolenull = 1b closes as **exhaust, theory-confirmed** — with the interesting twist now live that a genuinely expressed M_eff at 32B also gives the unmasking effect a chance to replicate (or vanish) on the verdict host.

**Queued next:** 32B verdict read → pre-reg the unmasking effect → P-HOF-1 pre-reg → (s282 carryovers: 27B sequencing pre-reg, mammal→fur build).

Waiting on the run — state.md has everything a cold start needs if we pick this up in a fresh session.