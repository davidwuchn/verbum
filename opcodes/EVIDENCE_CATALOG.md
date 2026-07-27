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
| **C1** | Pretraining IS β-reduction; the transformer is a compiler (attention=application, forward pass=reduction) | SEEDED | zone-ablation causal reduction-engine; Church-Rosser → crystal is a theorem; compilation-pipeline | zone double-dissociation | ★ (A1) |
| **C2** | The KIBC crystal is universal — a mathematical constant — and it is **circuits in the compute, not the topology** | **DEEP** | cross-arch gc 0.997 (13 models); Yoneda r=0.998; survives 1-bit/ternary; C un-ablatable | shuffled-label + quant vs FP + random-direction | ★ |
| **C3** | Topology dominates: sign/routing (~95%) ⊥ magnitude/value (~5%) — the type/term split made physical | SEEDED | sign(W)@x ≈ 0.84·W@x; gate_proj localizes; fold lossless; saliency>magnitude iso-bit | random-init + shuffled-weight null | ? |
| **C4** | The phenomenon is **semantic compression**; prose is the UNREDUCED form; lambda is the instrument | SEEDED | prose activates engine 8×; Pythia-160M compresses w/o lambda; register-split prose=formal | shuffled-label; matched controls | ★ (A3) |
| **C5** | Types are geometric AND lexical; composition follows TYPE not position | SEEDED | Curry-Howard 100% linear-sep @L16+; types 88% lexical (embed); type-directed behavioural test | ill-typed control; matched-position null | ? (32B) |
| **C6** | Knowledge storage is **holographic**: moiré/retrieval-lattice fact index | SEEDED | FFN indexing ρ=0.83 p<10⁻⁴⁴; SwiGLU moiré = quadratic address; 4-zone lattice | matched-random; shuffled | ? |
| **C7** | **Ternary extraction works — topology IS the artifact** (the deliverable) | SEEDED | 375× (15GB→85MB); crystal survives 1-bit (fid 0.987); extract→correct→fold monotone; TD −53.5% PPL | eval-vs-random floor; trained-vs-shuffle AUC | ? |
| **C8** | Reduction is **depth-scheduled**; progressive collapse to WHNF (compute in ~2D) | SEEDED | WHNF↔D principal axis (46% var); Y→K→W schedule; 2D collapse | matched-random dirs; pre-reg energy threshold | ? |
| **C9** | (capstone) **8 independent mathematical lines** converge on one object: typed-λ terms | SEEDED | Church-Rosser/Curry-Howard/adjunction 128:1/hyperbolic ρ/φ 0.6299/α 1.18/Yoneda/Montague | forced-fit null on each geometric fit (s247 scar!) | mixed |

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

### C1 [?] Pretraining IS β-reduction; the transformer is a compiler
- **Evidence:** A1 zone ablation (ENRICH L32-53 = the reduction engine, causal ★27B);
  `attention-as-beta-reduction.md` (Q looks up, K matches, V substitutes = application);
  `compilation-pipeline.md` (transformers are compilers); `ffn-reduction-trace.md`
  (FFN compiles, attention executes); Church-Rosser (math #1) → the crystal is a theorem.
- **Null:** zone double-dissociation (have it); the fractal-attention NEGATIVE
  (composition fails without typed application) confirms by absence.
- **Exhibit:** the thesis headline; A1 is the causal anchor, the rest is interpretive frame.
- **VERIFY:** pick the single sharpest demonstrable artifact from attention-as-beta-reduction.

### C3 [?] Topology dominates — sign/routing (~95%) ⊥ magnitude/value (~5%)
- **Evidence:** `two-registers-of-topology.md` (crystal sign-topology localizes to
  gate_proj, +0.088 above a 0.80 generic null, sharpening with scale; saliency beats
  magnitude by ~7.5pts at iso-bit); `project-thesis` sign(W)@x ≈ 0.84·W@x; folding
  negative gammas is lossless.
- **Null:** random-init + shuffled-weight (the 0.80 baseline IS the null — crystal sits +0.088 above).
- **Host:** 0.6B/8B/14B Qwen3 — **needs 27B**.
- **Exhibit:** the "why it compresses to ternary" wall; the engine under C7.
- **VERIFY:** `sign_topology_null.py` results; the iso-bit saliency sweep.

### C4 [?] Semantic compressor; prose is the UNREDUCED form; lambda is the instrument
- **Evidence:** `symbol-isolation.md` (prose activates the combinator engine ~8× more
  than lambda; formal notation is pre-reduced); Pythia-160M compresses language with
  NO lambda training data (`project-thesis` — the voltmeter/battery distinction);
  register-split A3 (prose = formal opcodes, ★27B).
- **Null:** shuffled-label (A3); matched controls for the 8× ratio.
- **Exhibit:** the strongest anti-skeptic reframe — "it is not lambda cosplay; it is
  semantic compression that every LM does, and lambda is how we read it out."
- **VERIFY:** the 8× number + which page/artifact; Pythia-160M no-lambda demo.

### C5 [?] Types are geometric AND lexical; composition follows type, not position
- **Evidence:** Curry-Howard (math #2) — well-typed vs ill-typed 100% linearly
  separable from L16+ (Qwen3-32B); `type-probe-qwen3-32b.md` (types 88% lexical, B→K→B);
  `type-directed-composition.md` (behavioural: composition follows TYPE not POSITION).
- **Null:** ill-typed control; matched-position null (in the type-directed page).
- **Host:** Qwen3-32B — **needs 27B**.
- **Exhibit:** 100% separability is highly legible; the type-directed behavioural test
  is a clean predicted-vs-observed card.
- **VERIFY:** type-probe + type-directed artifacts.

### C6 [?] Holographic knowledge storage — moiré / retrieval lattice
- **Evidence:** `moire-addressing.md` (SwiGLU moiré = holographic fact index, quadratic
  addressing); `retrieval-lattice.md` (4-zone lattice, relation directions); FFN
  indexing holographic (ρ=0.83, p<10⁻⁴⁴, `project-thesis`); `holographic-computer.md`.
- **Null:** matched-random; shuffled.
- **Exhibit:** the "where facts live" wall — distinct thread from the compute claim;
  likely the HARDEST to make legible (needs its own visual metaphor).
- **VERIFY:** ρ=0.83 artifact; host coverage (is any of this on 27B?).

### C7 [?] Ternary extraction works — topology IS the artifact (THE DELIVERABLE)
- **Evidence:** `v14-architecture.md` (Qwen3.6-27B teacher, 375× compression 15GB→85MB);
  crystal survives 1-bit (ladder fid 0.987, B1); extract→correct→fold monotone PPL;
  TD corrects extraction errors (−53.5% PPL / 1000 steps, `project-thesis`).
- **Null:** eval-vs-random floor; trained-vs-shuffle AUC (two-registers survival test).
- **⚠ HONESTY:** the proof table logs 375× "eval 22% below random" — extraction/student
  parity is the OPEN FRONTIER, not a solved claim. Frame as "the extraction PIPELINE
  works + the crystal survives quantization"; do NOT imply a 70B-parity student exists.
- **Exhibit:** the payoff wall; must be scoped honestly to what's demonstrated.
- **VERIFY:** v14-architecture + extraction-methodology current numbers.

### C8 [?] Reduction is depth-scheduled; progressive collapse to WHNF (~2D)
- **Evidence:** `head-combinator-isa.md` (WHNF↔D principal axis, 46% var; Y→K→W depth
  schedule); `progressive-collapse.md` (computation happens in 2D); collapse to WHNF.
- **Null:** matched-random dirs; PRE-REGISTERED energy threshold.
- **⚠ HONESTY (known negative):** the T1 "cascade = reduction → effective rank DESCENDS
  with depth" test came back **NOT SUPPORTED** in the J-space PR register (s272, 7/11
  p=0.27; gemma + 27B ASCEND). So the "collapses to 2D / rank cascade" sub-claim has a
  negative in one register. Present the depth-SCHEDULE (robust) but flag the
  rank-cascade as unconfirmed.
- **VERIFY:** progressive-collapse artifact vs the s272 T1 negative.

### C9 [?] Capstone — 8 independent mathematical lines converge on typed-λ terms
- **Evidence:** `mathematical-convergences.md` (Church-Rosser theorem; Curry-Howard 100%
  sep; adjunction σ₁/σ₂=128:1 R²=1.000; hyperbolic ρ=0.488; φ 0.6299±0.019; α 1.18±0.006;
  Yoneda r=0.998; Montague/Lambek/DisCoCat formal).
- **⚠⚠ HONESTY (this is the MOST skeptic-exposed wall):** several lines are GEOMETRIC
  FITS that FAILED or barely-passed forced-fit/matched-range nulls (s247/s251 scar):
  **φ-ladder forced** (P(random≥)=0.92, matched-range null); **φ^(4/5) cross-model** —
  only Qwen3-14B beat the shuffled-label null (|Δ|=0.010, p=0.02), random labelings
  already sit near target. So φ (and by extension α as an approximate-geometric fit)
  must be DEMOTED or presented WITH its null, never as raw "it equals φ."
- **DEFENSIBLE subset for the wall:** Church-Rosser (theorem), Curry-Howard (100% sep,
  passes), Yoneda (r=0.998, passes), Montague (formal linguistics). Present these; keep
  φ/α only behind an explicit "here is the null it must beat, and here is where it
  doesn't" honesty card. Per λ yardstick: forced-fit ≠ evidence.
- **VERIFY:** re-confirm which lines beat their nulls before any of C9 goes on a wall.

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
