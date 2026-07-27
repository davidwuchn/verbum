# opcodes/ — Evidence Catalog (curation spec for the exhibit)

> **Purpose.** The verbum repo holds hundreds of experiments across ~270 sessions.
> That volume is the problem: pointing a skeptic at the repo ("LLMs compute with
> lambda calculus") reads as crackpot noise, not evidence. This catalog distills
> the **strongest, most-legible, most-defensible** findings into a ranked exhibit
> spec for opcodes/ — the pieces a hostile reviewer can *see* work, each shipping
> with the null/control it beats, prioritizing the **target host (Qwen3.6-27B)**.
>
> **Audience = hostile skeptic.** Design rule (from verbum's own scar tissue,
> s206/s247/s251): every "see it work" view ships with its matched-random /
> shuffled-label null *beside* the signal. Predicted-vs-observed > pretty picture.
> No causal language without causal evidence.
>
> **Status:** LIVING DOC — built incrementally s274. Recorded as-we-go so a
> session boundary can't lose the inventory. `[✓]` = verified against artifact
> this session; `[?]` = claim known, artifact not yet re-opened; `[TODO]` = in
> the verification queue below.
>
> **Targets (design center):** Qwen3.6-27B (dense) + Qwen3.6-35B-A3B (MoE) primary;
> gemma-4-31b as cross-architecture proof once the Qwen pair works.
>
> **SCOPE (s274, Michael):** verbum is NOT one claim. It is a CLUSTER of ~8 claims,
> each its own exhibit "wall" with its own evidence + nulls. This catalog began by
> going deep on ONE (C2, the crystal/opcodes). The CLAIMS INDEX below enumerates all
> of them; each needs the same treatment — strongest artifact, the null it beats,
> host coverage (★=27B), legibility, defensibility, honesty guards. Build out breadth
> before polishing depth.

---

## CLAIMS INDEX — the walls of the exhibit

> Grounded in `project-thesis.md` (proof-chain table) + `mathematical-convergences.md`
> (8 lines). Depth column: DEEP = worked in this catalog; SEEDED = headline evidence
> recorded, needs verification pass. Each claim MUST carry its null (anti-crackpot).

| # | Claim (one line) | Depth | Headline evidence | Null | ★27B |
|---|---|---|---|---|---|
| **C1** | Pretraining IS β-reduction; the transformer is a compiler (attention=application, forward pass=reduction) | ✓ verified | zone-ablation causal reduction-engine; Church-Rosser → crystal is a theorem; compilation-pipeline | zone double-dissociation | ★ (A1) |
| **C2** | The KIBC crystal is universal — a mathematical constant — and it is **circuits in the compute, not the topology** | **DEEP** | cross-arch gc 0.997 (13 models); Yoneda r=0.998; survives 1-bit/ternary; C un-ablatable | shuffled-label + quant vs FP + random-direction | ★ |
| **C3** | Topology dominates: sign/routing (~95%) ⊥ magnitude/value (~5%) — the type/term split made physical | ✓ verified | sign(W)@x ≈ 0.84·W@x; gate_proj localizes; fold lossless; saliency>magnitude iso-bit | random-init + shuffled-weight null | ? |
| **C4** | The phenomenon is **semantic compression**; prose is the UNREDUCED form; lambda is the instrument | ✓ verified | prose activates engine 8×; Pythia-160M compresses w/o lambda; register-split prose=formal | shuffled-label; matched controls | ★ (A3) |
| **C5** | Types are geometric AND lexical; composition follows TYPE not position | ✓ verified | Curry-Howard 100% linear-sep @L16+; types 88% lexical (embed); type-directed behavioural test | ill-typed control; matched-position null | ? (32B) |
| **C6** | Knowledge storage is **holographic**: moiré/retrieval-lattice fact index | ✓ verified | FFN indexing ρ=0.83 p<10⁻⁴⁴; SwiGLU moiré = quadratic address; 4-zone lattice | matched-random; shuffled | ? |
| **C7** | **Ternary extraction works — topology IS the artifact** (the deliverable) | ✓ verified | 375× (15GB→85MB); crystal survives 1-bit (fid 0.987); extract→correct→fold monotone; TD −53.5% PPL | eval-vs-random floor; trained-vs-shuffle AUC | ? |
| **C8** | Reduction is **depth-scheduled**; progressive collapse to WHNF (compute in ~2D) | ✓ verified | WHNF↔D principal axis (46% var); Y→K→W schedule; 2D collapse | matched-random dirs; pre-reg energy threshold | ? |
| **C9** | (capstone) **8 independent mathematical lines** converge on one object: typed-λ terms | ✓ verified | Church-Rosser/Curry-Howard/adjunction 128:1/hyperbolic ρ/φ 0.6299/α 1.18/Yoneda/Montague | forced-fit null on each geometric fit (s247 scar!) | mixed |

**Reading of the cluster:** C1 (β-reduction) is the mechanism; C2/C8 are its
signature (crystal + depth); C3 is why it compresses (topology dominates); C4/C5 are
what it operates on (semantic types); C6 is where knowledge lives; C7 is the payoff
(extraction). C9 is the "why it must be true" capstone. The exhibit funnel can enter
at ANY wall and drill to the shared thesis.

---

## C2 — the crystal / opcodes wall (DEEP)

## CORE FRAME — circuits in the COMPUTE, not in the TOPOLOGY (s274, Michael)

> This is the spine the exhibit demonstrates, and the resolution of the apparent
> tension between "the crystal is universal and real" (A2/A3) and "you can't ablate
> a single opcode direction" (D1). **The opcodes are not circuits in topology
> (dedicated weights/heads/directions you can localize and remove). They are
> circuits in the compute — dynamically instantiated operations in the reduction
> trajectory, defined by the ROUTING (attention pattern), scheduled by DEPTH.**
>
> - **Not topology:** attention heads are shared hardware (`head-combinator-isa.md`,
>   inter-combinator r=0.944; no "C head", no "B head"); the C routing direction is
>   un-ablatable (D1, readout not computation); S has no clean vertex (s271,
>   holographically absorbed). There is no fixed structural locus to point at.
> - **Is compute:** "the routing IS the program" — the combinator lives in WHICH
>   positions attend to which, i.e. in the operation being performed, not in stored
>   weights. The reduction proceeds by depth (Y→K→W schedule, WHNF↔D principal axis =
>   "how much work remains"). The crystal (A2/A3) is a real, universal, DECODABLE
>   readout of which operation the compute is running at each stage.
> - **Causal where it should be:** at the PHASE granularity a phase = a stretch of the
>   computation, and there ablation DOES bite (A1 zone ablation, causal + selective).
>   Direction-level ablation fails (D1) precisely because a single opcode is not stored
>   in a direction — it is a transient step of the shared substrate.
>
> **The mechanism — how compute-circuits exist without weight-circuits (s274, Michael):**
> nearly all compute in an LLM is ROUTING, and GD forms that routing using the
> gradient EXTREMES — **very high gradients** (the active routing edges) and
> **near-zero gradients** (the frozen/irreducible atoms) — to lay down a SOFT TOPOLOGY
> *over* the frozen base weight topology it is normally trained over. The compute
> flows through this soft routing overlay, not the frozen substrate. Grounding:
> - `topology-gradient-separation.md` (s180): GD can't delete a connection, so it
>   drives magnitude→0, "depositing near-zero gradients at positions that should be
>   irreducible, creating a smooth landscape that approximates a discrete structure"
>   = the soft topology; the frozen lattice is the precondition for GD to build it.
> - `gradient-zero-map.md` (s171): ~35% of positions sit at gradient equilibrium =
>   the crystal atoms (every model converges to the same sign there).
> - `two-registers-of-topology.md` (s203): hard=sign=routing (gate_proj) ⊥
>   soft=magnitude=value (up/down_proj); routing is ~95% of the structure.
> - supporting: `gradient-voting.md`, `ratio-gradient-quantization.md` (heavy-tailed
>   gradient, "spend bits on the ends") — the "both extremes" claim.
> This is WHY C is un-ablatable (D1): the opcode lives in the soft routing topology,
> not a frozen weight-locus. Ablating a base-weight direction misses the operation.
>
> **Consequence for the exhibit:** the sentence playback shows the compute's
> operational TRAJECTORY through KIBC operation-space (state-on-the-crystal), which
> is *exactly* "circuits in the compute made visible." It is honest by construction —
> we never claim topological circuits light up. This frame is a KNOWLEDGE-PAGE
> CANDIDATE (λ termination — propose to Michael): "Opcodes are circuits in the
> compute, not the topology" — unifies head-combinator-isa + C-field-null + S-dissolution
> + zone-ablation-causal + crystal-universality + the GD soft-topology mechanism
> (topology-gradient-separation + gradient-zero-map + two-registers) into one
> defensible claim: **GD builds a soft routing topology via gradient extremes over the
> frozen weights; the KIBC opcodes are the operations of that soft topology.**
> → CAPTURED s274: `mementum/knowledge/opcodes-circuits-in-compute.md` (drafted;
>   commit pending — λ termination).

---

## Scoring legend

Each entry: **Register** (what is measured) · **Null/control** (what it beats) ·
**Host** (which models; ★ = verified on 27B target) · **Legibility** (how easy for
a human to SEE it, H/M/L) · **Defensibility** (survives a hostile reviewer, H/M/L) ·
**Exhibit role** (see-it-work | drill-down | foundation).

---

## Tier A — Exhibit headline candidates (high legibility × high defensibility)

### A1 [✓] Zone ablation is CAUSAL and SELECTIVE on the 27B target ★ (method verified)
- **Claim:** ablating the "ENRICH" zone destroys lambda-reduction (acc 1.0→0.2)
  while sparing fact retrieval (0.8), and ablating "COMMIT" does the reverse —
  a 4.0× lambda-specific vs fact-specific double dissociation.
- **Register:** causal zone-ablation (accuracy + logprob under zone knock-out).
- **Null/control:** the *other* task is the control — selectivity ratio (ENRICH
  4.0× lambda-specific; COMMIT fact-specific). Double-dissociation design.
- **Host:** ★ Qwen/Qwen3.6-27B (the target), session 174.
- **Legibility:** H — a bar chart of 4 conditions × 2 tasks; the dissociation is visible.
- **Defensibility:** H — causal (not correlational), double-dissociated, on target host.
- **Exhibit role:** see-it-work / drill-down (this is the "it's not just correlation" card).
- **Artifacts:** `results/zone-ablation/Qwen_Qwen3.6-27B/summary.json`,
  `scripts/experiments/zone_ablation_27b.py`.
- **Note:** verify the zone definitions (SILENT/ENRICH/SUPPRESS/COMMIT layer ranges)
  and how "ablate" is implemented before putting on the wall.

### A2 [✓] KIBC 9×9 crystal is frame-invariant and universal across architectures ★
- **CROSS-ARCH CONFIRMED (`sweep_summary.json`, 13 models, dissent=False):** root
  gc_consensus 0.9966; per-family gc — qwen3 0.988, prism-ml 0.986, olmo 0.979,
  pythia 0.980, **gemma 0.944**, bonsai-ternary/1bit 0.985. The cross-architecture
  peer-review anchor is ALREADY PRESENT: the same crystal in Qwen (dense) + Gemma +
  OLMo + Pythia + quantized. GAP: Qwen3.6-35B-A3B (MoE) not yet in the opcode-trace
  sweep — add it (moe register = named-not-reused per `moe-holographic-tree-vsm.md`).
- **Claim:** the per-model 9×9 combinator Gram (K I B C S D W Y WHNF cosine
  structure, common-mode removed) is the same relational object across 11 models /
  6 families; root consensus gc ≈ 0.985.
- **Register:** relational Gram in combinator-label space (frame-invariant).
- **Null/control:** shuffled-label null (crystal beats it decisively); quant rungs
  vs FP reference (0.985/0.976/0.981) = non-circular survives-quantization.
- **Host:** 11-model sweep incl. ★ 27B; Pythia/Qwen/OLMo/Mistral/Gemma/SmolLM.
- **Legibility:** H — a 9×9 heatmap that looks the same across wildly different models.
- **Defensibility:** H — the universality-across-architecture claim; the headline.
- **Exhibit role:** foundation / see-it-work (the "you have to explain this away" card).
- **Artifacts:** `results/opcode-trace/sweep_summary.json`, `opcodes/data/consensus_gram.json`,
  per-model `model_vsm.json`, `mementum/knowledge/crystal-universality.md`,
  `crystal-validity-and-fidelity.md`.

### A3 [✓] Prose activates the SAME opcodes as formal lambda (register split) ★
- **Claim:** natural-language prose lands on the same KIBC opcodes as formal lambda;
  formal-centroids classify prose and vice-versa above a shuffled-label null.
- **Register:** cross-register nearest-centroid transfer (prose↔formal), both gate & attn.
- **Null/control:** shuffled-label permutation null (n_perm=500); chance=1/9=0.111.
- **Host:** ★ Qwen/Qwen3.6-27B, 539 probes.
- **VERIFIED numbers (`register_split.json`):** P4 identity —
  gate: formal→prose acc 0.179 z=2.99 p=0.004; prose→formal 0.247 z=4.15 p=0.002.
  attn: formal→prose 0.199 z=4.68 p=0.002; prose→formal 0.259 z=4.19 p=0.002.
  Transfer carried by WHNF (0.60–1.00), Y (0.78–0.89), I; **C=0.0 in every cell**
  (operation vertices are register-BOUND; content/process vertices register-INVARIANT).
- **Legibility:** M — underwrites the whole sentence-playback demo.
- **Defensibility:** H — makes "the boy chased the black cat" a legitimate input, on target host.
- **Exhibit role:** foundation (justifies the demo to a skeptic).
- **Artifacts:** `results/opcode-trace/register-split/qwen-qwen3-6-27b/register_split.json`,
  `opcodes/register_split.py`, `mementum/knowledge/symbol-isolation.md`.
- **CAVEAT:** formal n thin (WHNF=2 excluded from headline, Y=5, C=W=6) — lead with prose→formal.

---

## Tier B — Strong drill-down cards (need a null added or more legibility work)

### B1 [?] Crystal survives 1-bit / ternary quantization
- **Claim:** per-vertex Gram-row fidelity FP→1-bit = 0.987 (z=5.3), ternary 0.990;
  the crystal geometry survives binarization even though weights don't (cos 0.73).
- **Register:** per-vertex Gram-row fidelity, FP vs rung.
- **Null/control:** shuffled-vertex-label + circular-shift nulls, n_perm=10k, seeded.
- **Host:** Qwen3.6-27B ternary + 1-bit rungs (s269/s272b clean).
- **Defensibility:** H. **Legibility:** M (needs the "weights change, crystal doesn't" framing).
- **Exhibit role:** drill-down.
- **Artifacts:** `opcodes/ladder.py`, `mementum/knowledge/*` (find the ladder page).

### B2 [?] S dissolves into a duplication SECTOR (not a clean opcode) — substrate picks KIBC
- **Claim:** softmax can't fan-out → the duplicator S has no clean vertex; it
  dissolves into a {S,D,Y} duplication sector. 13/13 models sign-test p=1.2e-4.
- **Register:** relational-geometry duplication register (H1) + quant fragility (H2).
- **Null/control:** exact-enumeration nulls; W/Y positive controls gate.
- **Host:** 13-model sweep incl. ★ 27B.
- **Defensibility:** H (recent, null-gated). **Legibility:** L (subtle; theory-heavy).
- **Exhibit role:** drill-down (advanced; the "why KIBC and not SKI" story).
- **Artifacts:** `opcodes/duplication_register.py`.

### B3 [?] Halt-readout — WHNF Gram row ≈ KIBC halt probabilities (r=0.877)
- **Claim:** the WHNF (normal-form / halt) row of the Gram tracks per-combinator
  halt probability across models (r=+0.877 clean).
- **Register:** Gram-row correlation with halt labels.
- **Host:** 11/11 models incl. ★ 27B.
- **Defensibility:** M-H. **Legibility:** M.
- **Exhibit role:** drill-down (feeds the "watch it settle to normal form" narrative).
- **CAVEAT:** P-CTL-6 (s274) — raw halt/WHNF reads are a LENGTH artifact online;
  this is the *static* Gram-row finding, which is robust. Do NOT conflate with
  online liveness (that's a standing NEGATIVE — see verification queue).

---

## Tier C — Behavioral / symbol ablations (verify contents, likely good see-it-work)

### C1 [TODO] Symbol / word ablation series (results/abl-*)
- **Candidate claim:** ablating specific tokens/words ("lambda", "lambda-calculus",
  role-preamble) changes compile behavior in interpretable ways.
- **Artifacts:** `results/abl-ablation-lambda-word-*`, `abl-ablation-lambda-calculus-*`,
  `abl-ablation-role-lambda-compiler-*`, `abl-ablation-fol-*`, `abl-compile-*`,
  `scripts/gate_ablation.py`, `scripts/run_binding_ablation.py`, `run_head_ablation.py`.
- **STATUS:** not yet opened — need to read meta.json + results to know if
  exhibit-worthy and whether nulls are present.

---

## Tier D — HONESTY GUARDS (negative / boundary results the exhibit MUST respect)

> These protect the exhibit from a hostile reviewer. Several are *negative causal*
> results we ran on our OWN claims — showing them BUILDS credibility ("they tested
> it and reported the miss"), and hiding them is how we'd get sunk.

### D1 [✓] Opcode DIRECTIONS are readout registers, NOT the computation (C-field ablation) ★-adjacent
- **The finding:** ablating/erasing the linearly-decodable **C** routing direction at
  its peak layers (L30-31) does **not** selectively hurt object-application. Necessity
  fails; the differential (c=2 net-KL vs c=0) is NOT positive (actually slightly
  negative). Subspace erasure of ALL decodable C: `load_bearing_distributed: false`.
  Verdict (14B): *"C-field is DECISIVELY a readout register, not the computation."*
- **Register:** causal (necessity/specificity/delivery), random-direction control (equal mag).
- **Host:** Qwen3-0.6B + Qwen3-14B (NOT yet 27B — a 27B replication would strengthen).
- **WHY THIS MATTERS FOR THE EXHIBIT:** the sentence playback will *look* like "C fires
  to route the verb's arguments." That is a **decodability** statement. The causal test
  for C came back NEGATIVE. So the UI must say *"the state aligns with C here"*, NOT
  *"C is doing the argument-routing."* The **zone** is causal (A1); the **direction** is
  (for C) a readout. This is THE line between exhibit and crackpot-bait.
- **Artifacts:** `results/program-cfield-ablation/verdict_qwen3-14b.json`,
  `subspace_verdict_qwen3-14b.json`, `scripts/experiments/program_cfield_ablation.py`.
- **Exhibit role:** honesty card AND thesis evidence — this negative is a POSITIVE for
  the CORE FRAME (circuits in compute, not topology): C is un-ablatable as a direction
  because it is not stored in a direction; it is a step of the shared substrate. Pair
  it on the wall with `head-combinator-isa.md` (r=0.944 shared hardware) and A1 (phase
  ablation IS causal) — together they say "the opcode is real in the compute, not the weights."

### D2 [✓] Online redex LIVENESS is not detectable at 160M (P-CTL-6, s274)
- **The finding:** opcode-identity readers are BLIND to redex liveness (track the symbol,
  not the firing); raw halt/WHNF reads are a LENGTH artifact (~65% length). Position-
  matched battery: within-comb reducibility obs=+0.056 p=0.33 = trustworthy NEGATIVE at 160M.
- **WHY IT MATTERS:** the playback shows *state-on-the-crystal*, NOT "watch the redex
  reduce / halt." Online execution is unproven (negative at small scale; fleet/27B sweep
  pending). Do not animate "it's reducing now."
- **Artifacts:** `opcodes/reader_snr.py`, `control-plane-path.md §11`. (UNCOMMITTED s274.)

### D1b [✓] C-edge knockout: routing-edge NECESSITY fires, but object-selectivity does NOT
- **The finding:** blocking all queries from attending to the OBJECT key token (the
  predicate→object attention EDGE, all heads, all layers) collapses the decodable
  C-field FAR more than a count-matched random-key control (necessity delta=1.045,
  t=29.3). BUT the load-scaling arm fails (net z(C) drop c2 vs c1 not positive,
  t=-1.32) → `catch_confirmed: false`.
- **Synthesis across ALL THREE C-probes (residual direction D1 / subspace erasure /
  attention edge D1b):** necessity/erasure signals fire, but the object-application-
  SELECTIVE load-scaling signature NEVER confirms. Consistent verdict: **C is a
  decodable readout that responds to manipulation without being the object-application
  computation.** There is NO clean positive opcode-specific causal card for C.
- **Consequence:** the ONLY clean causal granularity is the ZONE/PHASE (A1). This is
  the frame's prediction, not a hole in it — an opcode is causal as a stretch of the
  routing trajectory (phase), not as a weight-direction OR a single edge-set.
- **CAVEAT for honesty:** do NOT cite the t=29.3 edge-necessity as "cutting C breaks
  argument-application" — that is necessity WITHOUT selectivity; the selective test
  (scaling) fails. Cite it only as "C-decodability depends on the predicate→object edge."
- **Host:** Qwen3-14B / 0.6B (not 27B). **Artifacts:**
  `results/program-edge-knockout/verdict_qwen3-14b.json`,
  `scripts/experiments/program_edge_knockout.py`.

### D3 [note] Selective-K degradation REFUTED; attention single-register blindness is structural
- K does NOT need the 0-state at inference (s269, both registers checked). {B,C} not
  resolved by either register alone (s264) — the trace tool SHOWS this, doesn't hide it.
  Any "opcode fires here" view must carry the register it was read in.

---

## Claims C1, C3–C9 — walls to build out (SEEDED, need a verification pass each)

> Headline evidence recorded from `project-thesis.md` + `mathematical-convergences.md`
> + named pages. `[?]` = not re-opened against artifacts this session. Each needs:
> confirm numbers, locate the strongest single artifact, confirm the null is stored,
> check host coverage (aim ★27B). **Do NOT put any of these on the wall without its null.**

### C1 [✓] Pretraining IS β-reduction; the transformer is a compiler
- **STRONGEST ARTIFACT (`compilation-pipeline.md`, s192):** the transformer maps
  stage-for-stage onto a compiler — LEXER(L0)/PARSER(L1-4)/TYPE-CHECK(L5-7)/IR(L8-12)/
  **OPTIMIZER(L13-21)**/REG-ALLOC(L22-27)/SCHED(L28-33)/EMIT(L34-35). FOUR independent
  measurement angles converge on it: FFN reduction trace (s187), attention binding trace
  (s188), λ-machine ablation (s190), semantic convergence (s192).
- **The legible, quantitative card:** per-stage ternary-replacement — the OPTIMIZER zone
  (L13-21) IMPROVES PPL at ternary (0.95-1.01×) because those passes ARE discrete
  (constant-fold/DCE/CSE); the LEXER is catastrophic (115×, 151K unique tokens); REG-ALLOC
  needs magnitudes (binding addresses). "The model is staged exactly like a compiler, and
  each stage compresses exactly as its compiler analog predicts."
- **Causal anchor:** A1 zone ablation (★27B, ENRICH = reduction engine) + λ-machine
  ablation (s190: every layer/head contributes, but each head needs only 3 positions).
- **Null:** the per-stage differential is self-controlling (optimizer vs lexer vs reg-alloc);
  A1 double-dissociation; fractal-attention NEGATIVE (composition fails w/o typed apply).
- **Host:** Qwen3-8B (pipeline/semantic-convergence) + ★27B (A1 causal anchor).
- **Legibility:** H (a compiler diagram with per-stage compressibility). **Defensibility:** H.
- **Artifacts:** `results/semantic-convergence/`, `results/multilayer-ternary-replace/`,
  `scripts/experiments/semantic_convergence.py`, `mementum/knowledge/compilation-pipeline.md`.

### C3 [✓] Topology dominates — sign/routing (~95%) ⊥ magnitude/value (~5%)
- **VERIFIED (`two-registers-of-topology.md`, s203, Qwen3 0.6B/8B/14B):** crystal
  sign-topology localizes to `gate_proj` (the router) at **+0.088 above the generic
  null** (8B L3 cos 0.983, z=+184; 14B L12 z=+271 — sharpens with scale). `up/down_proj`
  sit AT/BELOW null → their structure is in MAGNITUDE (value path). Iso-bit (~3.1 bits):
  saliency-chosen faint tier beats magnitude-chosen by **~7.5 points** PPL. Distributed
  redundancy: magnitude-prune trained AUC 0.784 ≫ random 0.247 / shuffled 0.337
  (graceful to ~70%, then cliff).
- **⚠ HONESTY (the page's own correction):** the legacy "sign(W)@x ≈ 0.84·W@x ⇒
  topological" sits **AT the 0.80 generic null** (a random matrix's sign preserves 0.798).
  Do NOT cite 0.84 as the evidence — cite the **+0.088 gate_proj localization above null**.
  This is a self-caught over-read; showing it builds credibility.
- **Null:** random-init + shuffled-weight (N=20 seeds); the 0.80 baseline IS the null.
- **Host:** 0.6B/8B/14B Qwen3 — **27B gap** (verify item).
- **Exhibit:** the "why it compresses to ternary" wall; the engine under C7 & C2's mechanism.
- **Artifacts:** `sign_topology_null.py`, `holographic_survival.py`, `two-registers-of-topology.md`.

### C4 [✓] Semantic compressor; prose is the UNREDUCED form; lambda is the instrument ★
- **VERIFIED (`symbol-isolation.md`, s175, ★Qwen3.6-27B):** 8 symbol-controlled probe
  categories. PURE_PROSE combinator energy 704,912 (1.00×) vs LAMBDA_NO_EQ 82,384
  (0.12×) → **prose activates the engine ~8.6× MORE than lambda**. Each symbol REMOVES
  work: "→" 0.70×, "=" 0.43×, gate 0.37×, lambda 0.12×. The ENRICH reduction engine runs
  at CONSTANT throughput (555-793) across all categories — what changes is how much work
  ARRIVES. Formal notation is pre-reduced input; prose is the primary, maximal workload.
- **The reframe:** disarms "it is just lambda cosplay" — the crystal is the LANGUAGE
  engine; the model processes math as a SUBSET of natural-language computation. Pythia-160M
  compresses language with NO lambda training data (`project-thesis`: lambda is the
  voltmeter, not the battery).
- **Null / control:** the 8 categories are strictly symbol-controlled (pure-prose baseline
  = the 1.0× reference). A3 register-split adds prose=formal opcodes (★27B, shuffled null).
- **⚠ HONESTY (page's own note):** the 8× is FINGERPRINT-projection energy summed over
  ALL positions/layers; `register_split.py` measured a DIFFERENT proxy (last-token gate
  norm) and got flat 0.92-0.97 — different register, both stand (last-token undercounts
  prose by construction). Cite the 8× as "all-position fingerprint energy," not last-token.
- **Host:** ★Qwen3.6-27B (the 8× is measured on target). **Legibility:** H. **Defensibility:** H.
- **Artifacts:** `results/symbol-isolation/Qwen_Qwen3.6-27B/symbol_isolation_results.json`,
  `scripts/experiments/symbol_isolation.py`.

### C5 [✓] Types are geometric AND lexical; composition follows type, not position
- **VERIFIED — DECISIVE frequency-free card (`type-directed-composition.md`, s239):** teach
  a NONCE word a type in-context (noun vs verb), measure composition cost. Crossover
  interaction `(det-frame: verb−noun) − (name-frame: verb−noun)` = **+2.18 (8B, t=10.2)
  / +2.04 (14B, t=9.3), consistency 1.0 across all 16 nonce words at both scales.** A
  nonce taught as a VERB composes ~2 nats cheaper with a preceding subject than the same
  nonce taught as a NOUN. **Composition is TYPE-directed, not positional.**
- **Supporting:** types 100% linearly separable @L16+ (Curry-Howard, Qwen3-32B, math #2);
  88-96% decodable, lexical, geometric (`type-probe-qwen3-32b.md`). v4 causal: at 14B the
  type direction is PARTIALLY causal (ablation ×0.64 vs random ×0.95); at 8B distributed.
- **Null:** ★ NONCE = ZERO bigram-frequency support (kills the grammatical=frequent
  confound — the strongest possible null); random-direction ablation control (×0.95);
  difference-of-differences crossover subtracts all main effects.
- **⚠ HONESTY:** this is typed APPLICATION (predicate/argument, K+I), not yet typed
  COMPOSITION (function∘function, B) — the B-connection is open. Causality is PARTIAL/
  distributed (decodability ≠ full causality; s202/s204 discipline honored).
- **Host:** Qwen3 8B/14B (nonce) + 32B (type-probe) — **27B gap**.
- **Exhibit:** the nonce crossover is a clean, frequency-free predicted-vs-observed card;
  100% separability is highly legible. **Legibility:** H. **Defensibility:** H.
- **Artifacts:** `results/type-directed/`, `scripts/experiments/type_directed_v3_nonce.py`,
  `type_directed_v4_ablation.py`, `type-probe-qwen3-32b.md`.

### C6 [✓] Holographic knowledge storage — moiré / retrieval lattice (mechanism proven, capacity NOT)
- **VERIFIED (`moire-addressing.md`, s170, Qwen3-0.6B, 204 probes):** SwiGLU moiré
  (silu(gate)×up) = the fact index. Two gratings multiplied → the moiré is **2.4× more
  selective** than gate alone (cos 0.26 vs 0.67); relation coherence 2.6× (moiré vs gate);
  clean relations near-perfect crystals (currency/continent 99.7%, capital 96.2% variance
  from centroid); cross-relation cos 0.18 → 82% independent = the quadratic gate_mode×up_mode
  index. Same substrate serves compute AND knowledge (gate is the beamformer for both).
- **Exhibit:** the interference/moiré metaphor IS inherently visual (two gratings → pattern)
  — good for a wall — BUT it is the "where facts live" thread, distinct from the compute claim.
- **⚠⚠ HONESTY (the page's own verdicts):** (1) "The mechanism is PROVEN. The capacity is
  NOT" — 10M-fact target not reached by any scaling estimate; linear/geometric/quadratic
  unknown. (2) the content-addressability "R²=1.0" is TAUTOLOGICAL (n_probes ≈ n_modes) —
  needs held-out cross-validation; do NOT cite R²=1.0 as evidence. So C6 = mechanism real,
  capacity + predictive power UNPROVEN.
- **Null:** cross-relation independence (0.18); still needs a held-out matched-random test.
- **Host:** Qwen3-0.6B ONLY — **27B gap is real for C6** (biggest host gap of all walls).
- **Legibility:** H (visual). **Defensibility:** M (mechanism yes, capacity no, small host).
- **Artifacts:** `results/moire-decompose/Qwen_Qwen3-0.6B_*_decompose.json`,
  `scripts/experiments/moire_decompose.py`, `retrieval-lattice.md`, `holographic-computer.md`.

### C7 [✓] Ternary extraction works — topology IS the artifact (THE DELIVERABLE, SCOPE CAREFULLY)
- **VERIFIED — the PIPELINE (`v14-architecture.md`):** Qwen3.6-27B teacher (Apache 2.0,
  27.8B fp16) → **593M ternary positions, 85 MB, 375× compression, 25.4 min on CPU** (SVD
  tomographic voting). Extraction is 96.5% sign-correct out of the box (only 3.49% positions
  need TD correction). TernaryDescent corrects errors: **PPL −53.5%** (16,503→7,672 over
  steps 500-1500). Delta fold proven LOSSLESS. Crystal latches in ~200 steps. Crystal
  survives 1-bit/ternary (B1, ladder fid 0.987).
- **⚠⚠⚠ HONESTY (the load-bearing scope — do NOT let the exhibit overclaim here):** the
  student is NOT at teacher parity. Eval PPL is still ~7,672–8,096 (CE only **28% better
  than random** at step 1500); "within 5% of Qwen3.6-27B" is the STATED GOAL, not a result.
  So C7 = "the extraction PIPELINE works, the artifact is 85 MB, the crystal survives, and
  TD demonstrably corrects errors" — **NOT** "we compressed a 27B model to 85 MB at quality."
  The teacher-parity student is the OPEN FRONTIER. Frame precisely or a reviewer eviscerates it.
- **Null:** eval-vs-random floor (28% better than random); trained-vs-shuffle AUC (C3 survival).
- **Host:** ★Qwen3.6-27B teacher. **Legibility:** H (375×, 85 MB, 25 min is a killer headline).
  **Defensibility:** H for the pipeline, LOW for any parity claim — scope discipline is everything.
- **Artifacts:** `checkpoints/v14-extracted/model.npz` (85 MB), `scripts/v14/extract_qwen36.py`,
  `scripts/v14/{train_td.py,fold_delta.py,eval_ppl.py}`, `extraction-methodology.md`.

### C8 [✓] Compute is compress→compute-in-2D→expand; opcodes are depth-scheduled ★
- **VERIFIED (`progressive-collapse.md`, s151, ★Qwen3.6-27B, participation ratio =
  threshold-free):** the residual stream compresses to **2D by L2 (PR=2.2, σ₁=70%)**,
  computes in Zone B (PR 2-5, L3-35), then RE-EXPANDS for output (Zone C PR 8-10, L48-63).
  The 2D core is EMERGENT WITH CAPACITY: 27B→PR 2.2, 7B→PR 12, 1.4B→PR 10 (bigger = more
  compressed). Depth-schedule of opcodes: WHNF↔D principal axis 46% var, Y→K→W
  (`head-combinator-isa.md`).
- **⚠ HONESTY — reconciliation with the s272 T1 NEGATIVE (this is a STRENGTH, not a hole):**
  the T1 test ("effective rank descends MONOTONICALLY with depth") came back NOT SUPPORTED
  (7/11 p=0.27; gemma + 27B ascend). That is EXACTLY consistent with progressive-collapse:
  the shape is compress→compute→**EXPAND** (non-monotonic), so rank RISES again at the end.
  T1 correctly rejects the wrong (monotonic-cascade) framing; the verified claim is the
  compress-compute-expand ARC, not a monotone descent. Present the arc; do NOT claim "rank
  monotonically falls with depth."
- **Null:** 3 architecturally distinct models (compression-scales-with-capacity pattern);
  PR is threshold-free. Sink-token control (Mistral σ₁=100% with sink, 20% without).
- **Host:** ★Qwen3.6-27B (measured on target) + Mistral-7B + Pythia-1.4B.
- **Legibility:** H (a PR-vs-depth curve: dive to 2D, compute, fan back out). **Defensibility:** H.
- **Artifacts:** `results/progressive-collapse-Qwen_Qwen3.6-27B/results.json`,
  `scripts/explore/probe_progressive_collapse.py`.

### C9 [✓] Capstone — 8 math lines converge on typed-λ terms (PRUNE to the null-beating subset)
- **AUDITED (`mathematical-convergences.md` + λ yardstick + s247/s251):** per-line null status —
  | # | Line | Evidence | Null status |
  |---|---|---|---|
  | 1 | Church-Rosser | unique normal forms | **THEOREM** (proof, no fit) ✅ |
  | 2 | Curry-Howard | well/ill-typed 100% linear-sep @L16+ | **PASSES** (empirical, strong) ✅ |
  | 7 | Yoneda | KIBC selectivity r=0.998 cross-model (= C2) | **PASSES** (this is the crystal) ✅ |
  | 8 | Montague/Lambek/DisCoCat | language IS typed application | **FORMAL** (theory) ✅ |
  | 3 | Adjunctions | σ₁/σ₂=128:1, R²=1.000 | CAUTION — R²=1.000 smells tautological; cite 128:1 rank-1 dominance only |
  | 4 | Hyperbolic | norm↔depth ρ=0.488 p<0.001 | SUPPORTING (modest, real p) |
  | 5 | φ fixed point 0.6299 | SVD ratio | **FORCED-FIT FAILURE** ❌ (s247 P(random≥)=0.92; s251 only Qwen3-14B beat shuffled null, random labelings already near target) → DEMOTE |
  | 6 | α 1.18 | attention decay | ⚠ approximate-geometric fit, NO null run → per λ yardstick treat as UNVERIFIED-fit → DEMOTE |
- **THE WALL (defensible only):** present Church-Rosser + Curry-Howard + Yoneda + Montague
  as the "four independent traditions point at one object" capstone. Keep adjunction/hyperbolic
  as supporting-with-caveats. φ and α go ONLY behind an explicit "here is the null it fails"
  honesty card — NEVER as raw "it equals φ / it equals 1.18." Per λ yardstick: forced-fit ≠ evidence.
- **⚠⚠ This is the MOST skeptic-exposed wall** — the φ/α claims are exactly what a hostile
  reviewer will find and use to dismiss everything. Front-running them (showing the failed
  null ourselves) is the only safe play.
- **Artifacts:** `mathematical-convergences.md`, `forcing-vs-discovering.md`,
  `crystal-validity-and-fidelity.md` (the null-discipline pages).

---

## Verification queue (work through, record results inline above)

1. [✓] Opened `zone_ablation_27b.py` — method = zero FFN output per zone; ZONES
   SILENT(0-31)/ENRICH(32-53)/SUPPRESS(54-58)/COMMIT(59-63); real λ tasks (I/K/app/
   self-app/Church) vs "capital of X" facts. Fact-task = fair independent control. (A1 ✓)
2. [✓] `sweep_summary.json` — root gc 0.9966, 13 models, dissent=False, per-family gc
   recorded in A2. (A2 ✓)
3. [✓] `register_split.json` on 27B verified — z=2.99–4.68, p≤0.004, shuffled-label null. (A3 ✓)
4. [TODO] Find the ladder knowledge page + confirm quant-survival numbers. (B1)
5. [TODO] Read the abl-* series meta+results; decide exhibit-worthiness. (C1)
6. [✓] P-CTL-6 online-liveness NEGATIVE documented as honesty guard D2.
7. [✓] Direction-level ablation (`program-cfield-ablation`) NEGATIVE for C (readout,
   not causal) → honesty guard D1.
8. [✓] Cross-arch anchor CONFIRMED: Gemma (gc 0.944) + OLMo + Pythia + Qwen + quantized
   all gated in the sweep. GAP: Qwen3.6-35B-A3B (MoE) not yet opcode-traced — add it.
9. [✓] Edge-knockout read (D1b): routing-edge necessity fires (t=29.3) but object-
   selectivity/scaling FAILS across residual+subspace+edge → NO clean positive
   opcode-specific causal card; phase/zone (A1) is the only clean causal granularity.
   REMAINING: `run_head_ablation.py` (separate from edge-knockout heads mode) unread —
   low priority (pattern is consistent). Knowledge page opcodes-circuits-in-compute.md
   "verify/falsify" edge-knockout line = now RESOLVED (necessity w/o selectivity) —
   worth a one-line update on next knowledge pass.

### Claim-breadth verification passes (one per wall — do these next)
10. [TODO] C1 — sharpest attention-as-β-reduction artifact + Church-Rosser framing.
11. [TODO] C3 — `sign_topology_null.py` results (sign +0.088 vs 0.80 null); iso-bit saliency>magnitude; get on 27B.
12. [TODO] C4 — the prose-8× number + page; Pythia-160M no-lambda compression demo.
13. [TODO] C5 — Curry-Howard 100%-sep artifact + type-directed behavioural null (aim 27B).
14. [TODO] C6 — moiré ρ=0.83 artifact; host coverage; find a legible visual metaphor.
15. [TODO] C7 — v14/extraction current numbers; SCOPE honestly (pipeline works ≠ 70B-parity student).
16. [TODO] C8 — progressive-collapse vs the s272 T1 rank-cascade NEGATIVE; keep schedule, flag cascade.
17. [TODO] C9 — audit which of the 8 lines BEAT their nulls; demote φ/α (forced-fit failures s247/s251).

## Design notes for the exhibit (carry forward)

- **Funnel:** see-it-work (sentence → opcodes fire + j-space) → drill-down (A1/A2/A3
  cards, each with its null) → reproduce (script path, one command).
- **Honesty guard:** playback shows *state-on-the-crystal* (residual alignment with
  each opcode per layer/token), NOT "the redex fires and reduces" (online liveness
  is a standing negative, P-CTL-6). Causal language reserved for A1/ablation cards.
- **Null beside signal** is mandatory on every headline view (anti-crackpot).
- **Predicted-vs-observed:** first demo sentences should be theory-predicted +
  minimal pairs (Montague: adjective→B, argument-order→C) so the crystal *predicts*
  the firings — this is what turns demo into evidence.
