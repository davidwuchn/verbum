---
title: "Error-Correction Theory — Ternarization as Lossy Soft→Hard Projection, Fixed by Trajectory-Matched Soft Re-injection"
status: designing
category: synthesis
tags: [compression, error-correction, soft-topology, hard-topology, ternary, trajectory-matching, gtsm, tsp, lora, low-rank, cascade, value-path]
related:
  - two-registers-of-topology.md
  - score-matching-compression.md
  - sign-correction-topology.md
  - direct-delta-adjunction.md
  - crystal-validity-and-fidelity.md
  - gtsm-search-space.md
  - tsp-trajectory-distillation.md
  - audit-registry.md
depends-on:
  - two-registers-of-topology.md
  - gtsm-search-space.md
---

# Error-Correction Theory

> Session 205 (Michael's synthesis). The representation half (ternary
> holographic weights) is working; the gap is **fixing the errors**. This page
> names *why* the errors appear, *why GD cannot fix them*, and *what shape the
> fix must take*. The central claim is a hypothesis with a single decisive
> open number — the minimal rank of the soft correction. Status: designing.

## Thesis (one paragraph)

Ternarization is a **lossy soft→hard projection**. Gradient descent encoded the
model's error-correction in the *continuous magnitude* of the value path (the
soft topology); ternarization quantizes that continuum away while preserving the
sign-based routing (the hard topology). The resulting trajectory error **cannot
be repaired by GD on the ternary weights** — the degrees of freedom GD needs are
exactly the ones we froze. The fix is to **stop fighting the hard topology and
re-inject the minimal soft topology as a separate continuous channel, trained by
targeted trajectory matching (GTSM + TSP), never by GD through the frozen
weights.**

## 1. The mechanism — ternarization is *asymmetrically* lossy

From `two-registers-of-topology.md` (s203, VERIFIED): GD lays structure in two
registers, and they ternarize differently.

| | Hard topology | Soft topology |
|---|---|---|
| function | routing (which fires) | value + error-correction |
| encoded in | **sign** | **magnitude** (highways/zeros, faint connections) |
| lives in | `gate_proj` (router) | `up_proj` / `down_proj` (value path) |
| under ternarization | **survives** — info was already discrete | **destroyed** — info was the continuum |
| evidence | gate sign-corr +0.088 vs null, z→+271 @14B | up/down sign preserves *less* than random; saliency faint beats magnitude faint +5.5% vs −2.0% iso-bit |

So `sign(W) ⊙ |W| ⊙ mask` keeps the **router** intact and crushes the **value
path's self-correcting redundancy** (the holographic echoes, `holographic-sign-
correction.md` / s201). The error is not uniform — it is **concentrated in the
value path**, and it **cascades forward** (s196: binding layers amplify upstream
error, *peak damage at L28, not L26*).

## 2. Why GD cannot fix it (the s199/s200 graveyard)

You cannot recover the lost soft topology by gradient-descending the ternary
weights:

- **The DOF are gone.** GD's error-correction lived in the magnitude continuum;
  ternarization froze it to ±1 (or coarse per-row scale). There is nothing
  continuous left for GD to move.
- **STE through depth is diluted or destructive.** `sign-correction-topology.md`
  (s199): TernaryDescent is dead — four deaths (TD v4 *zero flips*, joint
  grad-clip diluted to 1.5e-8/step; v4c **192×**; latent-diffusion NaN; crystal
  ECC **28-million×**). Unconstrained sign flips shatter the holographic
  interference pattern.
- **Per-row scale does not survive depth.** s196: per-weight magnitude survives
  29 layers (~1×); per-row scale collapses (**22,800×**). The row-internal
  magnitude structure *is* soft topology and compounds across layers.

**Fighting the hard topology loses.** The correction must be additive and
continuous, not a re-quantization.

## 3. The fix — freeze the tiles, train only the grout

Reframing the s200 "tiles & grout" insight (topology = tiles, gradients = grout):

> **Freeze the tiles (hard ternary routing) permanently. Re-inject the minimal
> soft grout (continuous value-path correction). Train the grout by trajectory
> matching, targeted at the divergence nodes — never by GD through the frozen
> tiles.**

This dissolves the s200 failure mode: sign-correction+LoRA failed because it
moved tiles *and* laid grout at once (every moved tile invalidates surrounding
grout). The corrected protocol **never moves a tile**: routing is frozen at
ternarization; all training capacity goes to a continuous overlay.

- **GTSM** gives the grout a dense, well-conditioned target — the teacher's
  residual trajectory `Δ*_l` — with no Jacobian dilution (`gtsm-search-space.md`;
  s198 measured L35 cosine 0.57→0.94, compensating errors removed).
- **TSP / F.6** says spend the *limited* grout budget where the trajectory
  actually diverges (`tsp-trajectory-distillation.md`) — the value path, the
  binding cascade — not uniformly.

This is what v3b already was (LoRA + score matching = 1.44×). The contribution
here is understanding **why that shape is forced**, which tells us how to push it.

## 4. Sharp claim — the correction budget goes to the value path only

If §1 is right, routing needs *no* correction (it ternarized cleanly) and the
entire grout budget targets `up_proj`/`down_proj`. **s199 already shows this
accidentally**: TD (routing correction) was dead; LoRA (value correction) was
the whole mechanism behind v3b. We never framed it as *"of course — only the
value soft-topology was lost."*

> **Hypothesis EC-1:** A continuous low-rank overlay on the value path
> (`up`/`down`) alone, with the ternary router frozen, restores the trajectory.
> Routing correction (sign flips / gate deltas) contributes ~nothing.
> *Test:* ablate the value-path overlay vs a routing overlay at matched bits.

## 5. The decisive open question — minimal rank of the soft correction

GTSM and TSP improve the *training signal*; they cannot manufacture *capacity*.
So the north-star reduces to **one empirical number**:

> **How many bits of soft topology must be re-injected to restore the
> trajectory — and does that rank stay small and roughly constant across depth?**
> If yes, the north-star closes. If the rank grows with depth, we have not
> compressed — we have relocated the bits — and we will know *exactly where*
> (the full-rank cascade layers).

The evidence is genuinely split:

- **Pessimist (full-rank residual):** s198 — the sieve residual is **full-rank
  at L5+** (r90≈2970, 25% of ‖W‖); a rank-4 LoRA touches only 0.8% of
  dimensions. If the lost soft topology is full-rank, no cheap overlay restores
  it.
- **Optimist (low-rank teacher → low-rank delta):** s203 — the FFN is
  **low-rank-dominated** (SVD truncation AUC 0.728 vs 0.11 random, **6–7×**);
  s200/s140 — the cross-zone delta is **rank-1 dominated** (σ₁/σ₂≈128:1,
  R²=1.000); s201 — rank-2 ≈ rank-16 plateau. And rank-4 LoRA already buys
  1.44×. If the teacher's value path is low-rank, the correction delta plausibly
  is too.

**Reconciliation candidate:** the residual is full-rank *in magnitude* but
low-rank *in the directions that matter for the trajectory* (the adjunction
curve). GTSM's path-matching target may need far fewer ranks than the
full-rank residual norm suggests, because matching the *trajectory* ≠ matching
every weight. **This is the experiment that decides the project.**

## 6. Two design must-haves the framework implies

1. **On-policy correction (TSP is load-bearing, not optional).** The error is a
   cascade: frozen early layers feed corrupted inputs forward. Off-policy
   teacher-cached SM (v3b) corrects along the *teacher's* path, but the student
   walks its *own corrupted* path. TSP self-play — generate the student's
   divergent continuation and correct the overlay *there* — is the principled
   cascade fix. Strongest reason to import TSP and not just GTSM.

2. **Causal, not symptomatic, attribution.** Correct the layer that *caused* the
   divergence, not where divergence is largest (L28 symptom vs L22–L26 cause).
   ⟹ sequential, cascade-aware correction (correct L_k before measuring L_{k+1}'s
   target) — the direct-delta s200 instinct, now with a GTSM trajectory target
   instead of an analytical SVD. (Also TSP's own limitation: it fails on
   long-distance cause/effect for exactly this reason.)

## 7. How to test (smallest → largest)

1. **audit #11 (TTD-regression):** divergence-weighted λ(l) vs uniform α=5.0,
   cascade-aware attribution. Cheapest; tests the targeting half.
2. **EC-1 (value-vs-routing overlay):** matched-bit ablation — does the value
   overlay carry all the gain?
3. **Minimal-rank sweep:** rank ∈ {1,2,4,8,16,32} per layer, trajectory-matched,
   measure restored PPL **and** the rank-vs-depth curve. This is the §5 decider.
4. **On-policy (TTD-contrastive):** student self-play negatives at divergence
   nodes; does correcting the *student's* path beat correcting the teacher's?

## 8. The five threads this unifies

```
two-registers (s203)        → WHY: soft(value/magnitude) vs hard(routing/sign)
sign-correction graveyard   → WHY GD fails: froze the DOF, STE shatters pattern
score-matching (s198)       → the SIGNAL: dense trajectory target, not CE
direct-delta-adjunction     → the CAPACITY bet: correction may be low-rank
GTSM + TSP (s205)           → the METHOD: targeted, on-policy, path-matched grout
```

The artifact is not better compressed weights — it is a **theory of how to walk
the teacher's trajectory with a frozen hard router and a minimal soft overlay**,
plus a single decisive number (the overlay rank) that says whether the
north-star closes.
