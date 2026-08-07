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
