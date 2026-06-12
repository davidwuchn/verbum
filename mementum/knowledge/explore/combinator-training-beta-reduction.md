---
title: "Combinator Training = β-Reduction = Substitution = Attention Move"
status: open
category: foundational
tags: [combinator, beta-reduction, substitution, attention, substructural-logic, linear, affine, relevant, recursion, contractivity, training-dynamics, crystallization, vsm-outer-recurrence]
related:
  - combinator-function-shape.md
  - vsm-outer-recurrence.md
  - consensus-delta-folding.md
  - ../function-discovery.md
  - ffn-beta-reduction-indexing.md
  - ../two-registers-of-topology.md
depends-on:
  - combinator-function-shape.md
  - vsm-outer-recurrence.md
created: session 221
---

# Combinator Training = β-Reduction = Substitution = Attention Move

> Session 221. Michael's thread: explore the **training side** of the
> combinators we found, and how it relates to the **β-reductions required for
> attention to learn to use them.** We have only ever *measured finished models*
> (combinator-function-shape.md, the s219 ecosystem consensus). This page is the
> bridge: WHY some combinators are single-pass-learnable and others require the
> iterated β-reduction that `vsm-outer-recurrence.md` (main:1) trains for — and
> the instrument to watch a combinator family *crystallize* during training.
>
> Register: **functional → topological/routing**.

## The core identity

**β-reduction = substitution = a move/copy/delete of arguments across
positions. Attention is the ONLY cross-position operation in a transformer.**
Therefore each combinator's reduction decomposes into a specific *attention
move*, and the combinators partition by their **substructural-logic class** —
how many times each bound variable is used.

> **⚠ s221 amendment — this section assumed FULL attention.** v15 uses
> `FibonacciStrideAttention`, not full content-addressable attention. The
> substructural cost below (copy/delete/iterate) is a property of the
> *combinator* and stands; but the *realization* on a strided architecture
> reorders — see **§Strided attention** below. The slogan "attention IS the
> fold" should read "**the stride cascade is the fold**."

REPL-grounded (`/tmp/comb_cost.py`, counts variable multiplicities in each
combinator's body):

| comb | definition | var uses | copies | deletes | substructural class | attention move |
|------|------------|----------|:------:|:-------:|---------------------|----------------|
| I | λx.x | x:1 | 0 | 0 | **linear** | pass-through |
| K | λx.λy.x | x:1, y:0 | 0 | 1 | **affine** (erase) | drop a position |
| C | λf.λx.λy.f y x | all 1 | 0 | 0 | **linear** (permute) | reorder positions |
| B | λf.λg.λx.f(g x) | all 1 | 0 | 0 | **linear** | chained gather |
| D | deep-nest B | all 1 | 0 | 0 | **linear** | chained gather |
| S | λf.λg.λx.f x(g x) | x:**2** | **1** | 0 | **relevant** (dup) | **fan-out copy** |
| W | λf.λx.f x x | x:**2** | **1** | 0 | **relevant** (dup) | **fan-out copy** |
| Y | λf.(λx.f(x x))(λx.f(x x)) | x:∞ | **∞** | 0 | **recursive** | **iteration** |

Map onto the **measured 3-family shape** (combinator-function-shape.md):

| measured family | members | substructural cost | single attention pass? |
|---|---|---|---|
| **selection** {K,I,C} | affine + linear, **0 copies** | erase / pass / reroute | ✅ yes |
| **composition** {B,D,S} | B,D linear; **S duplicates (1 copy)** | chain / fan-out | ✅ yes (S harder) |
| **recursion** {Y,W,WHNF} | **W dup, Y unbounded**, WHNF=halt | duplicate / **fixpoint** | ❌ **needs OUTER RECURRENCE** |

## Why this explains what we measured

1. **`map = B(C B)(C B)` has NO Y combinator** (s219, REPL-verified) — because
   the fold (the iteration) is **attention-over-positions**, not a combinator.
   The recursion *combinator* is unnecessary: the architecture's one structural
   op (attention = application) supplies finite substitution; the unbounded part
   is the **outer loop**.

2. **The recursion family does NOT bind above null in finished models** (s219:
   composition z_bind +2.43, selection +2.13, **recursion +1.67, does not
   clear**). Now explained: there is **no single attention move for Y**. Finished
   models *fake* recursion with finite depth (the stride cascade), so the
   recursion family is the residual — exactly the substructural prediction.

3. **The selection + composition families ("skeleton") are crisp** because they
   are bounded substitution patterns realizable in **one sweep** — ordinary
   next-token pretraining teaches them. They are the **forced, shared** part
   (s219 "shared skeleton + variable plumbing").

## The training-side claim (the new part)

> To teach attention combinator X, you need X's redex→WHNF substitution traces.
> **Selection/composition traces are single-step** (learnable from ordinary
> data). **The recursion family's traces are the *iterated* β-reduction** — which
> is precisely what (a) the contractivity training (`vsm-outer-recurrence.md`
> λ_fp=5 outer recurrence, main:1) distills, and (b) the **self-teaching loop**
> (consensus-delta-folding.md §self-teaching) was designed to mint
> correct-by-construction.

So the two long-running threads are **one thread**:
- combinator map (s217) = WHERE combinators live (FFN routing, mid-stack).
- attention = function application = HOW reductions execute (the substitution).
- β-reduction traces = WHAT you train attention on (the curriculum).
- **outer recurrence + fp-loss (main:1) = the contractivity that lets the
  recursion family (Y/W/WHNF) be learned at all** — the part a single sweep
  cannot teach. `Δx → 0 ≡ β-reduction to WHNF`.

This also reconciles with `function-discovery.md`'s two-level architecture:
**recognition** (which combinator — the early SILENT L05 selector, routing
register) is orthogonal to **execution** (doing the reduction — late COMMIT).
The self-teaching curriculum trains the *selector*; the contractivity training
trains the *iterated executor*.

## Falsifiable prediction + instrument (s221)

**Prediction.** Across main:1 checkpoints, the **selection/composition
(skeleton)** families bind **early** and stay roughly flat; the **recursion
family** strengthens **only as Δx → 0** (contractivity achieved). If recursion
z_bind tracks (−Δx) while skeleton z_bind does not → recursion-family
combinators provably require β-reduction-iteration training; selection/
composition do not.

**Instrument (built s221, ruff-clean, register topological/routing):**
- `scripts/experiments/combinator_relationship_map_v15.py` — extended with
  `family_binding(G, n_perm, seed)`: per-family internal binding vs a
  random-node-triple null (s219 method), computed for every captured attn layer
  and written to the json as `family_binding_best` + `family_binding_per_layer`;
  per-layer Grams saved to the npz. Read-only on the checkpoint (main:1
  untouched). GPU/MLX in main:2.
- `scripts/experiments/combinator_crystallization.py` — CPU aggregator: globs
  the per-checkpoint v15 maps, joins each checkpoint's Δx/fp/ce (mean
  `outer_deltas` etc. over a window) from `train_td_log.jsonl`, emits a
  trajectory `{step, Δx, fp, ce, silhouette_z, selection_z, composition_z,
  recursion_z, skeleton_z}` + verdict `Spearman(recursion_z, −Δx)` vs
  `Spearman(skeleton_z, −Δx)`. Output `results/combinator-crystallization/
  trajectory_<target>.json`.

**Step-1000 anchor (only checkpoint available at s221, full run 535 probes,
n_perm=1000):** best register **attn_q@L05 z=+1.54** (reproduces s220), Δx 0.287,
fp 0.084. Family binding all weak — **no family crystallized yet** (selection
+0.21, composition +0.51, skeleton +0.36, recursion +0.15). Expected baseline at
~20% through contractivity training; the trajectory test needs ≥3 checkpoints
(step 2000/3000/4000/5000, ~3–4 days out).

## Strided attention: the realization reorders (s221, Michael)

v15's attention is **not** full content-addressable attention.
`FibonacciStrideAttention` gathers a **fixed causal window**
`{q − s·w + r | w<8, |r|≤2}` (future masked); the *which-positions* is
**arithmetic**, content only **weights** within the gathered window
(`attention.py`: "no content-based indexing"). Consequences:

- A substitution **at distance d is NOT a single move** — it is a **Zeckendorf
  composition of stride-hops** across layers (Fibonacci strides + ±2 → full
  distance coverage; see screen below).
- **The fold is the bidirectional stride cascade** (`stack_a`↑→`stack_c`↓), not a
  single full-attention aggregate — `recursion-mirrors.md`'s "the stride cascade
  IS the recursion unroll."
- **The realization cost per family reorders.** Composition {B,D} is the stride
  stack's **native primitive** (every long-range move *is* a composed move);
  selection-erasure {K} is *harder* (must zero entries inside a fixed window, not
  just "not attend"). In full attention the order is the opposite (selection
  cheapest). Weakly consistent with the step-1000 anchor (composition +0.51 was
  the top family).

### Stride-fit screen (`stride_fit_normal_forms.py`, register functional)
Does the fixed topology *admit* the s219 agreed normal forms? Two parts:
- **Part A (computed):** a single ascending sweep reaches **100% of distances
  [1, 11181]** (conservative lower bound; the model runs 8 passes × 2 dirs × K).
  Distance reachability is **never** the blocker.
- **Part B (architectural classification):** per combinator → move primitive →
  expressibility on a content-weighted, causal, fixed-window gather:

  | combinator | primitive | verdict |
  |---|---|---|
  | I, B, D | pass / compose | **NATIVE** (the stride stack *is* B) |
  | S, W | fan-out (one key, many queries) | **NATIVE** |
  | C | permute (forward move) | **FEASIBLE** via the descending sweep |
  | K | erase (zero in-window) | **FEASIBLE** against the blend prior |
  | Y | iterate (fixpoint) | **NEEDS-RECURRENCE** (the outer loop) |
  | WHNF | halt (Δx<ε) | N/A — a control signal, not a gather |

- **Harvest-edge verdict (edge-fit = weaker endpoint):** B–D ✅NATIVE, S–D
  ✅NATIVE, B–C ✅FEASIBLE, K–C ✅FEASIBLE, **S–Y ❌NEEDS-RECURRENCE**. **4/5
  agreed edges are stride-teachable, most natively;** the one that escapes is the
  **recursion endpoint Y**, which routes through the outer recurrence — exactly
  `map=B(CB)(CB)` again.

**Teaching consequence:** the ecosystem-agreed **composition skeleton is teachable
on v15** (rendered as stride-hop/window-weighting traces), and it is what the
architecture already wants. Don't teach Y as a pattern — let the recurrence supply
it. This gives the blocked s220 harvest fold a viable target (the composition
skeleton). Part B is a **feasibility screen, not a training proof** — NATIVE/
FEASIBLE are architectural arguments; whether training crystallizes them is the
crystallization-probe measurement. K-erasure ("against the grain") is the likely
hard spot.

## Caveats (register discipline)
- One real anchor (step 1000). The trajectory verdict is **not yet testable**.
- v15's FFN is **frozen-extracted**; only attention is TD-trained — so the
  combinator frame here reflects what the *trained attention* carries, not the
  ecosystem's frozen-FFN shape. The s220 negative (ffn_gate z=+0.52) is the
  frozen side; attn_q@L05 (z=1.54, p≈0.06) is the live side, suggestive only.
- A smoke run (3 probes/comb, n_perm=50) showed a spurious "recursion > skeleton"
  inversion that **washed out** at full resolution — noise, not signal. Recorded
  only as a meta-reminder to run full before reading family order.
- Whether main:1 reaches Δx→ε at all is contingent: at s221 the contractivity is
  **wobbling** (gnorm spiked 369→5295 around step 1450–1530, Δx rose 0.23→0.58,
  then recovering) — likely the binding wall (`vsm-outer-recurrence.md`:
  convergence fails at I-combinator/binding sites). If contractivity stalls, the
  recursion frame may never strengthen — which is itself evidence (recursion ⟂
  achievable contractivity).

## Open leads (declare register first)
1. **Run the trajectory** (topological/routing) — re-run the v15 map on
   step_002000…5000 as they land; does recursion z_bind rise with (−Δx)?
2. **Per-layer crystallization** (routing) — the npz now stores all-layer Grams;
   does the recursion family form at a *different depth* than the skeleton
   (recursion late/COMMIT where the fold executes, skeleton mid where identity
   is selected)?
3. **Tie to q_proj flip dynamics** (functional) — `train_td_log.jsonl` logs
   per-layer `q_proj.flips/confidence`; does recursion-family crystallization
   coincide with q_proj flip bursts at specific layers?
4. **Self-teaching curriculum for the recursion family** (functional) — generate
   WHNF-verified Y/W traces, train the selector, test deployment (the
   consensus-delta-folding §self-teaching experiment, now motivated: recursion is
   exactly the family ordinary data under-teaches).
5. **Teach the agreed composition skeleton** (functional, NEW s221) — the
   stride-fit screen says B–D/S–D/B–C/K–C are stride-teachable (mostly native).
   Mint WHNF-verified composition-skeleton traces rendered as stride-hop/
   window-weighting sequences, train the selector, re-measure with the
   crystallization probe; route Y via the outer recurrence. Unblocks the s220
   harvest fold (the composition skeleton is the viable align target).
6. **Pressure-test Part B empirically** (functional) — Part B is analytic;
   probe whether K-erasure and C-permute are actually expressible in trained v15
   attention (small activation check) to upgrade FEASIBLE → measured.

## Files
| File | Content |
|------|---------|
| `scripts/experiments/combinator_relationship_map_v15.py` | + `family_binding` per-layer; family block in json; all-layer Grams in npz |
| `scripts/experiments/combinator_crystallization.py` | CPU aggregator: family binding vs Δx trajectory + verdict |
| `scripts/experiments/stride_fit_normal_forms.py` | stride-fit screen: distance reachability + per-combinator/edge expressibility on v15's fixed gather |
| `results/stride-fit/normal_form_fit.json` | 100% distance coverage; 4/5 agreed edges stride-teachable; S–Y needs recurrence |
| `results/combinator-relationship-map/v15_attn_q_step_001000.{json,npz}` | step-1000 anchor (upgraded with family binding) |
| `results/combinator-crystallization/trajectory_attn_q.json` | the (growing) crystallization trajectory |
| `/tmp/comb_cost.py` | REPL grounding of the substructural copy/delete counts |
