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

---

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

### A2 [?] KIBC 9×9 crystal is frame-invariant and universal across architectures
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
- **Artifacts:** `opcodes/data/consensus_gram.json`, per-model `model_vsm.json`,
  `mementum/knowledge/crystal-universality.md`, `crystal-validity-and-fidelity.md`.
- **VERIFY:** re-open consensus_gram + a couple model_vsm to confirm gc numbers and
  that the shuffled-label null is stored/reproducible.

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

### D3 [note] Selective-K degradation REFUTED; attention single-register blindness is structural
- K does NOT need the 0-state at inference (s269, both registers checked). {B,C} not
  resolved by either register alone (s264) — the trace tool SHOWS this, doesn't hide it.
  Any "opcode fires here" view must carry the register it was read in.

---

## Verification queue (work through, record results inline above)

1. [✓] Opened `zone_ablation_27b.py` — method = zero FFN output per zone; ZONES
   SILENT(0-31)/ENRICH(32-53)/SUPPRESS(54-58)/COMMIT(59-63); real λ tasks (I/K/app/
   self-app/Church) vs "capital of X" facts. Fact-task = fair independent control. (A1 ✓)
2. [TODO] Re-open `consensus_gram.json` + 2 `model_vsm.json` — confirm gc + null. (A2)
3. [✓] `register_split.json` on 27B verified — z=2.99–4.68, p≤0.004, shuffled-label null. (A3 ✓)
4. [TODO] Find the ladder knowledge page + confirm quant-survival numbers. (B1)
5. [TODO] Read the abl-* series meta+results; decide exhibit-worthiness. (C1)
6. [✓] P-CTL-6 online-liveness NEGATIVE documented as honesty guard D2.
7. [✓] Direction-level ablation FOUND (`program-cfield-ablation`) → came back NEGATIVE
   for C (readout register, not causal) → recorded as honesty guard D1, NOT a headline.
   The strongest *positive* causal card remains the ZONE ablation (A1). OPEN: is there a
   POSITIVE direction-level causal result for any other opcode? (edge-knockout, head-
   ablation still unread — next dig.)
8. [TODO] Cross-architecture: confirm Gemma + Qwen-MoE are in the crystal sweep so
   the universality claim already spans architectures (peer-review anchor).
9. [TODO] Read `program-edge-knockout` + `run_head_ablation.py` results — any positive
   causal opcode/head card? (follows from item 7.)

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
