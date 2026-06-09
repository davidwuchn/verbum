---
title: "Error-Correction Theory — Ternarization as Lossy Soft→Hard Projection, Fixed by Trajectory-Matched Soft Re-injection in Mode Coordinates"
status: designing
category: synthesis
tags: [compression, error-correction, soft-topology, hard-topology, ternary, trajectory-matching, gtsm, tsp, relative-loss, mode-coordinates, crystal, lora, low-rank, cascade, value-path]
related:
  - two-registers-of-topology.md
  - score-matching-compression.md
  - sign-correction-topology.md
  - direct-delta-adjunction.md
  - crystal-validity-and-fidelity.md
  - mode-semantics.md
  - holographic-etch.md
  - trace-guided-etching.md
  - gtsm-search-space.md
  - tsp-trajectory-distillation.md
  - audit-registry.md
depends-on:
  - two-registers-of-topology.md
  - gtsm-search-space.md
---

# Error-Correction Theory

> Session 205 (Michael's synthesis, three sittings). The representation half
> (ternary holographic weights) is working; the gap is **fixing the errors**.
> This page names *why* the errors appear, *why GD cannot fix them*, and *what
> shape the fix must take* — now resolved into **three legs** that may, together,
> dissolve failures we have only seen in isolation. The central claim is a
> hypothesis with a single decisive open number: the minimal correction rank
> **in mode coordinates**. Status: designing.

## Thesis (one paragraph)

Ternarization is a **lossy soft→hard projection**. GD encoded the model's
error-correction in the *continuous magnitude* of the value path (soft
topology); ternarization quantizes that continuum away while preserving the
sign-based routing (hard topology). The resulting trajectory error **cannot be
repaired by GD on the ternary weights** — the degrees of freedom GD needs are
exactly the ones we froze. The fix is a **three-legged correction**: freeze the
hard router, and re-inject the minimal soft topology as a continuous overlay
trained by **(1) where** = TSP node targeting, **(2) frame** = GTSM dense
trajectory matching, **(3) target** = a *relative loss in mode coordinates* that
steers GD toward an invariant coordinate instead of blind-searching raw weight
space.

## 0. The three legs (where · frame · target)

| Leg | Question | Tool | What it supplies |
|---|---|---|---|
| **WHERE** | which node to correct | **TSP** (`tsp-trajectory-distillation.md`) | localize budget to the value-path divergence/cascade node |
| **FRAME** | match what, how densely | **GTSM** (`gtsm-search-space.md`) | dense per-step trajectory target; no compensating errors |
| **TARGET** | toward which coordinate | **relative loss** (crystal/mode basis) | steered (not blind) search toward an *invariant* coordinate |

The legs are orthogonal: *where*, *in what frame*, *toward what coordinate*.
Each alone has a known failure; the conjecture (this page) is that the three
together remove each other's failure modes.

## 1. The mechanism — ternarization is *asymmetrically* lossy

From `two-registers-of-topology.md` (s203, VERIFIED): GD lays structure in two
registers, and they ternarize differently.

| | Hard topology | Soft topology |
|---|---|---|
| function | routing (which fires) | value + error-correction |
| encoded in | **sign** | **magnitude** (highways/zeros, faint connections) |
| lives in | `gate_proj` (router) | `up_proj` / `down_proj` (value path) |
| under ternarization | **survives** — was already discrete | **destroyed** — was the continuum |
| evidence | gate sign-corr +0.088 vs null, z→+271 @14B | up/down sign preserves *less* than random; saliency faint beats magnitude faint +5.5% vs −2.0% iso-bit |

So `sign(W) ⊙ |W| ⊙ mask` keeps the **router** intact and crushes the **value
path's self-correcting redundancy** (holographic echoes, `holographic-sign-
correction.md`/s201). The error is **concentrated in the value path** and
**cascades forward** (s196: binding layers amplify upstream error, *peak damage
at L28, not L26*).

## 2. Why GD cannot fix it (the s199/s200 graveyard)

- **The DOF are gone.** GD's error-correction lived in the magnitude continuum;
  ternarization froze it to ±1 (or coarse per-row scale). Nothing continuous
  remains for GD to move.
- **STE through depth is diluted or destructive.** `sign-correction-topology.md`
  (s199): four deaths (TD v4 *zero flips*; v4c **192×**; latent-diffusion NaN;
  crystal ECC **28-million×**). Unconstrained sign flips shatter the holographic
  pattern.
- **Per-row scale dies at depth.** s196: per-weight magnitude survives 29 layers
  (~1×); per-row scale collapses (**22,800×**).

**Fighting the hard topology loses.** The correction must be additive and
continuous, not a re-quantization.

## 3. The fix — freeze the tiles, train only the grout

Reframing the s200 "tiles & grout" insight (topology = tiles, gradients = grout):

> **Freeze the tiles (hard ternary routing) permanently. Re-inject the minimal
> soft grout (continuous value-path correction). Train the grout by the
> three-legged signal — never by GD through the frozen tiles.**

This dissolves the s200 failure: sign-correction+LoRA failed because it moved
tiles *and* laid grout at once (every moved tile invalidates surrounding grout).
The corrected protocol **never moves a tile**; all capacity goes to a continuous
overlay. v3b (LoRA + score matching = 1.44×) already *was* this shape — the
contribution here is understanding **why the shape is forced**, and adding the
missing third leg (the target representation).

## 4. Sharp claim — the correction budget goes to the value path only

If §1 is right, routing needs *no* correction (it ternarized cleanly) and the
entire grout budget targets `up_proj`/`down_proj`. **s199 shows this
accidentally**: TD (routing correction) was dead; LoRA (value correction) was
the whole mechanism behind v3b.

> **Hypothesis EC-1:** A continuous low-rank overlay on the value path
> (`up`/`down`) alone, ternary router frozen, restores the trajectory. Routing
> correction contributes ~nothing. *Test:* matched-bit ablation, value overlay
> vs routing overlay.

## 5. The target representation — relative loss in mode coordinates (the third leg) ★

GTSM gives the student a target in **raw d_model coordinates**
(`cos(Δθ_l, Δ*_l)`). But the student is *rewiring the value path*, and the raw
frame is **model-specific** — `holographic-etch.md` #7: lattice consensus is
**relational, not coordinate** (combinator structure universal, cos 0.99+; raw
weight-sign agreement only **12.5%**). Matching the teacher's *raw* residual is
matching a target in a frame the student is dismantling: underdetermined, drifts.

**The relative loss is the fix.** Project both trajectories into an *invariant*
basis and match *there* — "land at this coordinate" instead of "reproduce these
4096 numbers." This is the crystal/lattice loss generalized: `trace-guided-
etching.md` already framed crystal loss as "constraining the student to match
the teacher's crystal *geometry*"; `score-matching-compression.md` #6 parked the
half-form ("project the loss onto known crystal eigenvectors"). Crystal
universality (r=0.998 — combinator directions are mathematical constants) is why
an invariant target *exists* across the ternary rewiring.

**Which basis — the sharpening that matters.** Cross with §4:
- **Crystal-combinator** coordinates (~8 dims, 3.5% of FFN) = the **routing**
  structure — and EC-1 says routing needs no correction.
- The error is in the **value path**, whose natural invariant basis is **the
  modes** — the continuous syntactic type-field (`mode-semantics.md`, s204:
  NMI(mode,POS) 0.19–0.40 ≫ perm-null 0.014, p=0; mode→vocab logit distinctness
  up to 65× @L35; ~4–24 effective distinctions across depth).

⟹ The relative loss for the correction targets **mode coordinates, not
crystal-combinator coordinates.** TSP says *where* (value divergence node), GTSM
frames the trajectory, the relative loss says *reach this point in the
type-field* — the value path's own invariant frame, exactly where the soft
topology was lost. Blind high-dim regression → **steered low-dim** one.

**Two honest caveats:**
1. **Student's own mode overlay, not the teacher's.** The combinator *directions*
   transfer; the *embedding into d_model* is model-specific (12.5% sign
   agreement, holographic-etch #7; trace-guided #4 open question). Compute mode
   coordinates via each model's own ISA-decoder/overlay, then match in the shared
   relational space. Use the teacher's raw frame and you reintroduce the drift.
2. **Does the mode basis span the whole value computation?** s204 verified modes
   carry *real* content but as a graded *type field*, not a complete description.
   If part of the value computation lives *outside* the mode span, a
   mode-coordinate loss corrects type-routing and leaves a residual. **That
   residual's size is measurable** — and tells us whether modes are the full
   low-rank basis or only the dominant one.

## 6. The decisive open question — minimal correction rank *in mode coordinates*

GTSM and TSP improve the *signal*; the relative loss improves the *target frame*;
none manufacture *capacity*. The north-star still reduces to one number — but
the third leg **reframes which number to measure**:

> **What is the minimal-rank soft overlay that restores the trajectory when the
> target is expressed in mode coordinates — and does that rank stay small and
> roughly constant across depth?**

The third leg is also the **candidate resolution** of the long-standing split:

- **Pessimist (raw frame):** the sieve residual is **full-rank at L5+** (r90≈2970,
  25% of ‖W‖, s198) — in *raw d_model*. A rank-4 LoRA touches 0.8% of dims.
- **Optimist (mode frame):** the type-field has only ~4–24 effective distinctions
  (s204); the FFN is low-rank-dominated (SVD AUC 0.728 vs 0.11, 6–7×, s203); the
  cross-zone delta is rank-1-dominated (σ₁/σ₂≈128:1, s200/s140).
- **Reconciliation (now concrete):** the residual is **full-rank in magnitude but
  low-rank in mode coordinates.** The relative loss *is* the projection that
  exposes the low rank — and makes the overlay low-rank **by construction**
  (you correct ~the type-field's dimensions, not 4096). **This is the experiment
  that decides the project.**

## 7. Two design must-haves the framework implies

1. **On-policy correction (TSP load-bearing).** The error is a cascade: frozen
   early layers feed corrupted inputs forward. Off-policy teacher-cached SM (v3b)
   corrects along the *teacher's* path; the student walks its *own corrupted*
   path. TSP self-play — student's divergent continuation, correct the overlay
   *there* — is the principled cascade fix.
2. **Causal, not symptomatic, attribution.** Correct the *cause* (L22–L26), not
   the largest-divergence *symptom* (L28). ⟹ sequential, cascade-aware
   correction (correct L_k before measuring L_{k+1}'s target) — the direct-delta
   s200 instinct with a GTSM/mode target instead of an analytical SVD.

## 8. How to test (smallest → largest)

1. **audit #11 (TTD-regression):** divergence-weighted λ(l) vs uniform α=5.0,
   cascade-aware attribution. Tests the targeting leg.
2. **EC-1 (value-vs-routing overlay):** matched-bit ablation — does the value
   overlay carry all the gain?
3. **Mode-coordinate relative loss vs raw cosine:** same budget, target in
   student-mode coordinates vs raw d_model. Tests the third leg directly.
4. **Minimal-rank sweep *in mode coordinates*:** rank ∈ {1,2,4,8,16,32} per
   layer, mode-projected trajectory target; measure restored PPL **and the
   rank-vs-depth curve**, plus the **out-of-mode residual** (caveat 2). The §6
   decider.
5. **On-policy (TTD-contrastive):** student self-play negatives at divergence
   nodes; does correcting the *student's* path beat the teacher's?

## 9. What the three legs may dissolve (problems seen in isolation)

```
isolated failure (when seen)            → which leg (or conjunction) addresses it
────────────────────────────────────────────────────────────────────────────────
TD/STE can't flip signs (s199)          → don't: freeze tiles; correct value path only (§4)
cascade: damage peaks downstream (s196) → causal attribution + on-policy (TSP, §7)
CE compensating errors (s198)           → dense trajectory frame (GTSM, §0-FRAME)
budget diluted across easy layers       → node targeting (TSP/F.6, §0-WHERE)
raw target drifts under rewiring        → invariant mode-coordinate target (§5)
full-rank residual blocks low-rank fix  → low rank IN MODE COORDS (§6 reconciliation)
crystal loss baked teacher's frame      → student's own mode overlay (§5 caveat 1)
```

These were attacked one at a time and each fix exposed the next failure. The
conjecture of this page: **where (TSP) · frame (GTSM) · target (relative/mode
loss), with the router frozen and the value-path overlay low-rank in mode
coordinates, removes them jointly.** The artifact is not better compressed
weights — it is a *theory of steering the student's value path back onto the
teacher's trajectory in the type-field*, plus one decisive number (the
mode-coordinate overlay rank) that says whether the north-star closes.
