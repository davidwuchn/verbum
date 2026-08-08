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

---

## §P-CL-COLLAPSE — do CL identities hold as routing geometry? (FROZEN s321)

> Operationalizes Open leads #1 + #3. **The compositionality probe** (the open
> S5 scorecard cell). Freeze-first (s222). Register named before build (λ measure).
> Michael GO s321. NOTHING below is tuned to data.

### The crux — extensional vs operational routing

The CL identity `I = SKK` says the compound `SKK` **is** the identity function.
Does `SKK` route like `I`? The kernel (`lambda_ast`) certifies the tension:
`S K K x → x` **by firing [S, K]** — `I` never fires. So two strong, OPPOSING
priors:

- **EXTENSIONAL** — routing sees the *function* (normal form): `SKK` routes like `I`.
  → the register respects the algebra → **compositionality✓**.
- **OPERATIONAL** — routing tracks the *reduction process* (fired opcodes): `SKK`
  routes like `{S,K}`, never like `I`. **Favored by our own priors**
  (`head-combinator-isa`: "routing IS the program, tracks reduction"; s317
  tape-resident reduction).

An EXTENSIONAL result is surprising-against-self → high information.

### Register (λ measure)

**ROUTING** — `sign(mlp.gate_proj pre-activation)` at the last token,
common-mode-removed (subtract per-feature mean over the pooled probe set). Crisp/
discrete. The *only* register where combinator identity is measurable (s217:
`route_cmr` silhouette 0.101 z=7.97 p=0.001; raw `hidden_full` z=−1.65 = null).
CL5 re-verifies this per-run (void-gate).

### Construction — normal-form collapse

Compound programs, **kernel-certified** (`lambda_ast.normal_form` +
`fired_sequence`), grouped by NF-target. Each target = a set of spellings sharing
*only* the normal form; head symbol + fired-opcodes VARY (the dissociation):

| Target | Spellings (kernel-verified this session) | fired-opcodes | head |
|--------|------------------------------------------|---------------|------|
| **I** | `SKK`, `SKS`, `WK`, `CKK`, `KII`, `S(KI)I` | {S,K}·{W,K}·{C,K}·{K,I}·{S,K,I} | S,W,C,K |
| **W** | `SS(KI)`, `CSI` | {S,K,I}·{C,S,I} | S,C |
| **B** | `S(KS)K` (+ any kernel-enumerated equivalents at build) | {S,K} | S |

Each spelling saturated with fresh atoms (from `f g h x y z a b`) → target
**≥40 probes/NF-target** (crystal ≥50 convention where reachable). Anchors = the 9
primitive crystal centroids (`crystal_probes()`), computed in the **SAME CMR pool**
as the compounds (one common-mode frame — non-negotiable for comparability).

Per-spelling centroids AND per-NF-target pooled centroids are computed. Comparison
directions per spelling `T`: **NF-primitive** `c(nf(T))`; **fired-mix**
`mean(c(f) for f in fired(T))`; **head** `c(head(T))`; **shared-token** primitive.

### Gates

- **CL1 EXTENSIONAL-ALIGNMENT** *(make-or-break)* — mean over spellings of
  `cos(c(T), c(nf(T)))` **>** operational baseline `cos(c(T), fired_mix(T))`,
  beating a **shuffled-label null** (permute which primitive is each spelling's
  "NF target"), p<0.05.
- **CL2 COLLAPSE-COHERENCE** *(make-or-break confound gate)* — spellings of one NF
  cluster (mean pairwise cos of per-spelling centroids within target) **more** than
  a **token-matched, NF-varied null**: control terms drawn from the SAME alphabet
  (e.g. {S,K}) but with DIFFERENT normal forms. Kills the "shared-K-token" artifact.
  EXTENSIONAL requires within-NF > token-matched, p<0.05.
- **CL3 OPERATIONAL-BASELINE** *(non-gating, rival readout)* — report
  `cos(c(T), fired_mix(T))` and `cos(c(T), c(head(T)))`; the verdict selects the
  larger of {NF, fired-mix, head, shared-token} alignment per target.
- **CL4 DEPTH-TRAJECTORY** *(read, Michael's ask)* — per depth-fraction, the
  extensional-minus-operational margin `Δ(ℓ)=cos(c_ℓ(T),nf) − cos(c_ℓ(T),fired_mix)`.
  A **rising** curve (Δ<0 shallow → Δ>0 late) = the reduction `SKK→I` executed
  ACROSS DEPTH, visible in routing (reconciles s217 mid-identity/late-execution).
  Flat-negative = operational at all depths.
- **CL5 COHERENCE-SANE** *(void-gate)* — primitive-anchor silhouette must replicate
  s217 (`route_cmr` z>0, combinators separable). Fail → register unmeasurable → VOID.

### Nulls (λ yardstick)

shuffled-label (CL1) · token-matched-NF-varied (CL2) · length-stratified /
token-count partialled (the confound that nulled §P-FUEL/TRACE-FUEL/NF-GAUGE —
compound spellings vary in length; the within-NF-set already spans lengths, but
CL2's token-matched null is drawn length-matched).

### Verdicts + a-priori (NOT tuned; mass on operational per s317/head-ISA priors)

| Verdict | a-priori | condition |
|---------|:---:|---|
| **EXTENSIONAL-ROUTING** | 20% | CL1 ∧ CL2 ∧ CL5 — routes to NF-primitive, beats operational + both nulls → **compositionality✓** (surprising-positive) |
| **OPERATIONAL-ROUTING** *(favored)* | 45% | CL3 fired-mix > CL1 NF; spellings drift to their fired-opcodes → routing = the reduction process |
| **SYNTACTIC-TOKEN** | 20% | clusters on shared surface token (not NF, not fired-mix) |
| **MIXED / REDUCTION-VISIBLE** | 10% | CL4 rising (shallow-operational → late-extensional), or NF-alignment present but doesn't beat operational — richest outcome |
| **VOID** | 5% | CL5 fails |

### Model / reuse

Qwen3-14B (36 layers, s217 artifact model). Primary read at best-silhouette layer
(frac≈0.31 s217); all layers for CL4. Reuse `combinator_relationship_map.py`
centroid/CMR/silhouette+null machinery + `lambda_ast` kernel. New harness
`scripts/experiments/cl_collapse.py`. Read-only (no wire, no training).

### Read discipline (banked for the close — don't over-read the label)

OPERATIONAL is the EXPECTED result → a clean confirmation of s317, informative not
failure. EXTENSIONAL is the surprise that opens the compositionality cell. MIXED
with a rising CL4 depth curve is the richest read (reduction across depth). VOID
only if the register fails to form (smoke silhouette makes this unlikely).

### §Result — Qwen3-14B: MIXED-REDUCTION-VISIBLE → routing is SYMBOL-PRESENCE, not extensional (s321)

**VERDICT (pre-registered tree): MIXED-REDUCTION-VISIBLE.** But the per-spelling
rows resolve it decisively — the mechanism read is **QUALIFIED-OPERATIONAL /
SYNTACTIC: routing tracks the combinators literally present in the compound, NOT
its extensional normal form. The CL algebra does NOT hold as routing geometry.**
Compositionality S5 cell stays ✗. (426 probes; best layer L4 f=0.10; read-only;
results `cb3fdd3`.)

**Gates.** CL5 anchor-sil **z=+35.37** (register strongly forms — style-matched
symbolic anchors separate; NOT void). CL1 mean_nf **+0.062** > mean_op −0.035
(Δ+0.097; beats shuffled-label null p_shuf=0.002) BUT paired NF>OP **p=0.0515**
(marginal miss) → **pass=False**. CL2 within-NF coherence **0.112 < token-matched
null 0.174** (p=0.70) → **FAIL**: collapse spellings cohere LESS than same-alphabet
varied-NF distractors — coherence is alphabet/token-driven, not NF-driven (W
spellings even ANTI-cohere, ρ=−0.16). CL3 op −0.035 / head +0.003 / tok −0.140.
CL4 "rising" True (Δ 0.013→0.162) but see below — NOT trustworthy as reduction.

**THE READ (the decisive datum).** The whole positive mean-NF is a **literal
symbol-presence artifact**. Split the collapse spellings by whether the NF-symbol
appears in the compound:

| subset | spellings | mean nf_align |
|--------|-----------|:---:|
| **DIRTY** (NF-symbol present/fired) | `KII`, `S(KI)I` (I fires), `BIB` (B head) | **+0.280** |
| **CLEAN** (NF-symbol ABSENT — the real dissociation) | `SKK`, `SKS`, `WK`, `CKK`, `SS(KI)`, `CSI`, `S(KS)K` | **−0.031** |

Where the dissociation is genuine (NF-symbol absent), there is **NO extensional
routing** (−0.03; head +0.014, op −0.064 — all ≈0). Per-row, `WK` routes toward its
HEAD (W, +0.29) not I; `SKK`/`SKS`/`CKK` route toward nothing. The three spellings
that *looked* extensional (`KII`→I, `S(KI)I`→I, `BIB`→B) are exactly those where the
NF-symbol is literally the head/a fired opcode. **Extensional/compositional routing
is falsified in the clean subset; the substrate routes by what is written and what
fires, not by the function computed.** This upholds the favored OPERATIONAL prior
and coheres with s317 tape-resident reduction (the reduction is enacted per-frame;
a static read of a compound does not see its normal form). CL4's rising Δ is not
reduction-evidence — it is the DIRTY spellings' symbol-presence signal strengthening
late.

**Method lesson banked.** The clean dissociation REQUIRES the NF-symbol absent from
the compound; the 3 confounded spellings (KII, S(KI)I, BIB) should have been
excluded or analyzed separately at design time (the a-priori NF>OP could pass on
them alone). A v2 would use only clean spellings, more of them, and per-subset gates.
The confound was caught here by the pre-registered per-row readout (CL3 + the
dirty/clean split) — the rows earned the honest verdict the aggregate blurred.

**S5 scorecard: discreteness✓ selectivity✓ compositionality✗ (this probe) causality✗.**
The register carries combinator IDENTITY (s217) but NOT the combinator ALGEBRA —
it is a syntactic/operational identity register, not an extensional one.

### §Re-read (s322 audit) — artifact proven at L0; clean null at all depths; anchors bound the claim

**EXPLORATORY post-hoc (not pre-registered).** s322 code audit flagged two
structural concerns: (1) gates were read only at the anchor-silhouette layer
(L4, f=0.10 — too early for multi-step reduction); (2) the symbolic anchors are
LEXICAL (the I-anchor centroid ≡ "routing that follows the literal token `I`",
not "routing of computed identity-ness"). gate_signs.npz is lossless for the
sign/CMR metric → full clean/dirty × layer decomposition recomputed offline
(`scripts/experiments/cl_collapse_reread.py`, results
`results/cl-collapse/qwen3-14b/reread_late_layer.json`, commit 3be00d1).

**Finding 1 — the artifact is proven, not inferred.** Dirty nf_align = **+0.645
at LAYER 0** (embeddings — no computation has happened). The s321 CL1 aggregate
positive was carried by token overlap that predates computation.

**Finding 2 — the clean null holds at every depth.** Clean nf_align rises
monotonically −0.144 (L0) → +0.001 (L39) and never crosses zero; the late Δ
+0.097 is op going negative, not nf going positive (boot p=0.14, shuffle
p=0.049, n=7). **Concern (1) is closed: late layers do not rescue extensional
routing under these anchors.** The OPERATIONAL verdict survives at all depths
*within this instrument*.

**Bound (concern 2, open).** With lexical anchors, an extensional signal living
in a non-lexical direction is invisible **by construction** — the verdict
licenses "no extensional routing *toward the literal-symbol anchor directions*",
not "no extensional routing". The monotone clean rise toward zero is consistent
with (but does not show) something drifting NF-ward late. **v2 requirements:
functional-equivalence anchors (NF-ness established behaviorally across diverse
held-out spellings, not by literal symbol presence) · clean spellings only,
pre-registered · per-layer gates · token-presence null.** Queued s322.

## §P-CL-COLLAPSE-2 — prose-anchored extensional routing (FROZEN s322, Michael GO)

### The crux

The v1 instrument could not see extensional routing (lexical symbolic anchors
+ early-layer gate; §Re-read). V2 anchors function-ness in **PROSE** — the
crystal probes (s217, z=7.97, 67 I / 50 W / 61 C / 69 B in
`verbum.probes.library`) — and asks two independent questions:

- **Plane A (cross-style):** do clean symbolic compounds (`S K K a`, NF-symbol
  absent) align with the PROSE anchor of their normal form? Prose anchors
  contain ZERO combinator tokens → token overlap impossible by construction;
  any nf-alignment is function-level. Style gap (NL↔symbolic) is common-mode:
  CMR + within-anchor-set CONTRASTS cancel it.
- **Plane B (within-prose):** do prose ROUND-TRIP compounds — sentences
  enacting composite behavior that computes a primitive ("wrapped the gift and
  then unwrapped it" = I) — route like the primitive they COMPUTE (extensional)
  or like the sequenced two-step they SPELL (operational; for I the named
  operational pole is B)?

### Register (λ measure)

ROUTING (crisp/topological): sign of gate_proj pre-activations, CMR'd over the
pooled population, last-token read, per-layer — v1 machinery verbatim
(`combinator_relationship_map.collect/cmr`; λ one_way). Primary gate read =
**LATE band mean (frac ≥ 0.6)**; full per-layer trajectory persisted + reported
(§Re-read lesson: never gate at the early silhouette max). Raw sign matrices
persisted npz (lesson: post-hoc decompositions become free).

### Scoring — three targets, separated by construction

Anchor pools: crystal probes for {I, K, W, C, B, S} (prose, s217-validated).
For each target T ∈ {I, W, C}:

1. **Contrast axis** `d_T = unit(centroid(A_T) − mean_{T'≠T} centroid(A_T'))`
   — subtracts what anchors share (style, prose-ness, the REFLEXIVE component
   the library's I and W pools both carry: "cleaned itself" / "bit itself").
2. **Score = difference-in-differences within one syntax family:**
   `score_T = mean align(compound_T, d_T) − mean align(control_T, d_T)`,
   where control_T = same-syntax non-T sentences. Families:
   - I: "wrapped the gift and then unwrapped it" vs "… and then mailed it"
   - W: "compared the draft against the draft" (one filler, two slots — NO
     reflexive pronoun) vs "compared the draft against the outline"
   - C: "added the coffee to the milk, not the milk to the coffee" (swap) vs
     "added the cream to the coffee, not the sugar" (two-option, no swap)
   Cross-target syntax differences never enter any score (each score is a
   within-family subtraction).
3. **3×3 cross-assignment matrix** `M[s,t] = score(family_s on axis d_t)` —
   confound is MEASURED, not assumed.

### Gates

- **G0 REGISTER-FORMS (void gate):** prose anchor silhouette (perm null) at
  the read layers; register must form (s217 precedent) else VOID.
- **G1 AXIS-SEPARATION (pre-gate, per pair):** per-pair POOL SEPARABILITY —
  silhouette of the two anchor pools vs label-permutation null (pass iff
  obs > null, p<0.05). Pair fails → affected planes **VOID-BY-DESIGN**
  (instrument cannot separate them; reported, ¬forced — λ yardstick). I/W =
  the at-risk pair (shared reflexive surface). **🔄 AMENDMENT (s322,
  --validate-forced, pre-run, instrument-side only):** the originally frozen
  |cos(d_T,d_T')|-vs-split-null statistic was register-mismatched — the
  mean-of-others axis construction mechanically couples axes (shared −1/(P−1)
  term), so obs |cos| exceeds a noise-dominated split null even for perfectly
  separable pools (planted operational world → false VOID). Pool separability
  is the quantity VOID-BY-DESIGN needs; residual axis coupling is shared
  across targets and handled by G4. Gates/verdicts/a-priori UNCHANGED.
  **Michael GO (s322 close) — launch is authorized; run lands next session
  after type-write-v2 frees the device.**
- **G2 PLANE-A CROSS-STYLE:** clean symbolic compounds (v1's 7 clean groups,
  kernel-certified, n_per 20), `nf_align − op_align` on PROSE anchors beats
  the shuffled-NF-assignment null, at the late band.
- **G3 PLANE-B PER-TARGET:** `score_T > 0` beats the shuffled
  compound/control-label null (within family), late band.
- **G4 CROSS-CUT SELECTIVITY (anti-confound, make-or-break for any
  extensional claim):** diagonal M[T,T] beats its ROW (family selective for
  its own axis) and its COLUMN (axis selective for its own family) under the
  shuffled-assignment null. Generic "round-trippy prose" lights a row → fails.
- **G5 LEXICAL-DISJOINT (build-time certification, code-enforced):** zero
  content-lemma overlap between (compound ∪ control) and ANY anchor pool
  (no itself/herself/same/exactly anywhere in Plane B); minimal overlap
  across families. Analog of v1 kernel certification. Symbolic compounds
  remain kernel-certified; prose compounds are DESIGN-certified only
  (semantic construction; weaker grade, marked — λ observation).

### Construction sizes

Plane B: ≥12 compound + ≥12 control sentences per target (template-diverse
verbs). Plane A: v1 clean spellings verbatim (7 groups × n_per 20). One model
load, read-only, no wire.

### Verdicts + a-priori (declared, NOT tuned; per-target sub-verdicts
EXTENSIONAL-T / OPERATIONAL-T / VOID-T reported alongside)

- **OPERATIONAL-CONFIRMED 40** — Plane A null ∧ all live Plane B diagonals
  fail: round-trips route as their spelled two-step; s321 verdict survives a
  FAIR instrument; compositionality ✗ hardens.
- **PROSE-EXTENSIONAL 25** — ≥1 Plane B target passes G3∧G4 ∧ Plane A null:
  the substrate computes function identity in prose but it is not readable
  off symbolic spellings (style-bound extensionality).
- **BOTH-EXTENSIONAL 10** — Plane A passes ∧ ≥1 Plane B passes: extensional
  routing real; v1 was instrument-blind; compositionality cell REOPENS.
- **SYMBOLIC-ONLY 5** — Plane A passes ∧ Plane B all null (surprising:
  symbolic-side extensional signal readable against prose anchors only).
- **MIXED 15** — patterns not covered (e.g., pre-gate voids I/W while C
  splits) — per-target report carries the read.
- **VOID 5** — G0 fails.

### Read discipline (banked)

Don't over-read PROSE-EXTENSIONAL: it licenses "I-ness computed in prose
routing", NOT symbolic-algebra extensionality (s321's clean-null stands
within its instrument). G4 failure with G3 passing = style artifact, not
extensionality. VOID-BY-DESIGN pairs are instrument findings, not substrate
findings. Model: Qwen3-14B (v1 carrier). Cost: ~minutes read-only.

### Model / reuse

`scripts/experiments/cl_collapse2.py` — reuses `cl_collapse.build_probes`
(clean symbolic subset) + `combinator_relationship_map.collect/cmr/unit` +
`verbum.probes.library.crystal_probes`; new code = prose families, contrast
axes, DiD scoring, 3×3 cross-cut, G1 split-null, G5 lemma check.
