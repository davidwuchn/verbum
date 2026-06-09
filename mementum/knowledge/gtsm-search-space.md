---
title: "GTSM and the Search Space — Why Trajectory Matching Beats Endpoint Matching"
status: active
category: synthesis
tags: [gtsm, cgtsm, score-matching, girsanov, path-measure, loss-function, search-space, compression, diffusion]
related:
  - score-matching-compression.md
  - diffusion-holographic-isomorphism.md
  - tsp-trajectory-distillation.md
depends-on:
  - score-matching-compression.md
created: session 205
---

# GTSM and the Search Space

> Session 205. Full paper read (68pp incl. appendices E/F/G, pulled from
> arXiv:2605.00414). Michael first supplied the verbatim Def 3.1 / Thm 3.2;
> the full read added the two-solver framing (diffusion AND gradient
> boosting), the residual=score bridge, and the finite-budget weighting
> correction. This page captures the *mechanism* — how Global Trajectory
> Score Matching narrows the training search space — previously scattered
> across two pages with a conflated CGTSM/GTSM name and without the Girsanov
> argument that makes it rigorous.

## Source (verified verbatim)

**Paper:** *"Trees to Flows and Back: Unifying Decision Trees and Diffusion
Models"* (Ramachandran & Sra 2026, arXiv:2605.00414).

**Naming correction:** the "C" in CGTSM is **Continuous**. GTSM is the
general principle; **CGTSM is its continuous-time SDE instantiation**. Our
older pages (`score-matching-compression.md`, `diffusion-holographic-
isomorphism.md`) conflate the two. The paper's headline unification is
**decision trees ↔ diffusion** (gradient boosting builds trees, so our
"gradient boosting ≡ diffusion" gloss is downstream-correct, not the title).

### Definition 3.1 (Continuous Global Trajectory Score Matching)

For an ideal SDE with law P\* and scores s\*_t(x), and a model s_θ(x,t):

```
L_CGTSM(θ) = ½ ∫₀ᵀ w(t) · E_{p*_t} ‖ s_θ(x,t) − s*_t(x) ‖²_{D(t)} dt

w(t) > 0                    strictly positive weighting function
‖v‖_D = √(vᵀ D v)           diffusion-induced (semi-)norm
D = σσᵀ                     diffusion tensor of dX_t = b(x,t)dt + σ(x,t)dw_t
                            (positive definite once rank-deficient σ disallowed)
```

### Theorem 3.2 (CGTSM Optimality Implies Path Matching)

Achieving **zero** CGTSM loss for **any** strictly positive weighting
w(t) > 0 is **necessary and sufficient** for matching the full path-space
measures, i.e. **Pθ = P\***.

**Proof sketch (Girsanov).** The KL divergence between path-space measures
D_KL(P\* ‖ Pθ) is an integral of the squared difference between the process
drifts. The reverse-time drift is a function of the score, so that difference
reduces to the CGTSM integrand. The loss is zero iff the KL divergence is
zero. (Full proof: paper §F, Corollary F.3.)

## The mechanism — how it narrows the search space

Girsanov turns the codimension intuition ("each layer adds a constraint")
into an exact statement:

```
D_KL(P* ‖ Pθ) = ½ ∫₀ᵀ E‖ b*(x,t) − bθ(x,t) ‖²_D dt     KL between path measures
              = ½ ∫₀ᵀ E‖ s*_t(x) − sθ(x,t) ‖²_D dt       reverse drift = fn(score)
```

The CGTSM integrand **is** the KL integrand. Three consequences:

### 1. Marginal vs joint — the actual reason the space shrinks

- **Endpoint loss** (cross-entropy / next-token) matches only the
  **terminal marginal** P\*₀ — a single time-slice of the trajectory.
  Infinitely many path measures share one marginal.
- **GTSM** forces D_KL between the **full path-space measures** to zero
  ⟹ **Pθ = P\***. The feasible set collapses from *"all processes with the
  right terminal slice"* to *"the single process P\*."*

You pin the whole **joint law over trajectories**, not one slice of it.
This is the search-space narrowing stated exactly.

### 2. Why "any w(t) > 0" works → density matters, weighting does not

A non-negative integral ∫ w(t) g(t) dt with w > 0 and
g(t) = E‖score diff‖²_D ≥ 0 is zero **iff g(t) = 0 almost everywhere**,
independent of the shape of w. Weighting cannot *hide* a nonzero-error
region — it can only **fail to cover** one. If w(t) = 0 on a set, that
interval is unconstrained → a hole in the narrowing.

This is the formal backing for the state.md line
**"density of measurement matters, weighting does not"** — but with a
**critical scope correction** (s205, full-paper read): this holds **only for
the zero-loss fixed point**. For **finite-budget optimization** the weighting
*does* matter. Prop F.6: λ(t) injects a deliberate bias to **counter-balance a
learner's intrinsic coarse-first tendency**, forcing attention onto harder
fine-grained detail. Since we always train at finite budget, **our α=5.0 cosine
weighting is exactly such a bias choice — load-bearing, not arbitrary.**

### 3. The correct metric is set by the noise geometry

Corrections are measured in **‖v‖_D = √(vᵀDv), D = σσᵀ** — the local
diffusion tensor, not flat L2. Depth-dependent standing-wave amplitude
(0.1× @L3 → 10× @L35) is our analog of σ(t); **cosine is our scale-
invariant proxy for ‖·‖_D**. Confirmed as the literal object, not a guess.

## Why endpoint losses are ill-posed (the degeneracy GTSM removes)

The endpoint-feasible set contains a large **degenerate manifold**: configs
where one layer's error E_l is cancelled downstream by −E_l ("compensating
errors"). These look correct on the terminal marginal but diverge internally
and fail out-of-distribution. GTSM lifts that floor — each step must match
*independently*, so cancellation is not representable. An **ill-posed inverse
problem becomes well-posed.**

## One objective, two solvers — diffusion AND gradient boosting

The paper's headline (s205 full read): GTSM is a **single master objective**
(integrated score error over the whole trajectory) solved by **two algorithm
families**. The GTSM integral is **decomposable into per-chunk consistency
checks** — that decomposability is what lets disparate algorithms solve one
problem.

| | How it solves GTSM | Paper anchor |
|---|---|---|
| **Diffusion / score nets** | minimize the **entire integral at once** (one parametric score net) | Def 3.1, Thm 3.2 |
| **Gradient boosting** | **greedily** reduce the largest remaining error, chunk by chunk (add weak learners) | Def 3.3, Thm 3.4 |

**⚠ "GD" = functional gradient descent = gradient boosting over weak learners
(decision trees) — NOT parameter-space SGD on a neural net.** The duality is
"diffusion score-net ↔ gradient-boosted tree ensemble," both as GTSM solvers.

### The bridge (three load-bearing results)

1. **Residual = score (Thm E.22).** For squared-error loss the boosting
   residual `y − F_m(x)` is proportional to the optimal meta-score
   `∇_F log p(y|F_m(x))`. **Fitting residuals (boosting) IS denoising score
   matching (diffusion).** The keystone.
2. **Greedy = globally optimal (Thm 3.4 / E.30).** The discrete GTSM objective
   is **additively separable** with deterministic transitions ⟹ by **Bellman's
   principle** the myopic per-step choice is the global optimum. Boosting is the
   *optimal* solver, not a heuristic.
3. **Girsanov closes the diffusion side (F.3).** Reverse-drift difference =
   score difference ⟹ path-space KL = ∫ squared score error ⟹ zero loss ⟺
   Pθ = P\*.

### Standard diffusion losses are CGTSM special cases

- **Simple/unweighted loss** (Ho et al. 2020) = CGTSM with w(t)=1 (Prop F.5).
- **Weighted loss** λ(t) (Karras, Kingma) = CGTSM with w(t)=λ(t) (Prop F.6).
- **Consistency distillation** = bootstrapped CGTSM approximation that biases
  *coupling between adjacent timesteps* for fast sampling (Prop F.7).

### Two limits the paper states plainly

- **Idealized / asymptotic.** "Gradient boosting (in an idealized version) is
  *asymptotically* optimal." Exact equivalence (Cor E.25) needs **infinite data,
  realizability, convergence**; Thm 3.4 needs **continuous limit + rich-enough
  weak learners**.
- **Rests on Tree-to-Flow dyadic refinement (Thm 2.5).** Trees-as-jumps would
  break it; refinement smooths splits into continuous paths so the **Novikov
  condition** for Girsanov holds (Remark F.4). Irreducible jumps ⟹ Lévy
  machinery, out of scope.

## Mapping to our compression (VERIFIED at runtime, s198)

| CGTSM object | Our transformer analog | Status |
|---|---|---|
| trajectory P over time t | residual-stream path h₀→h_L over depth | analogy |
| score s\*_t(x) | teacher residual update Δ\*_l = h\*_{l+1}−h\*_l | analogy |
| terminal marginal P₀ | output token distribution (what CE matches) | exact |
| diffusion norm ‖·‖_D | per-layer cosine (scale-invariant proxy) | proxy |
| dense coverage ∀t | per-layer SM at all ~36 layers | applied |

The narrowing principle **transferred and was measured**:
- CE-only (v3a): train loss ↓1.08 while eval PPL ↑14.06→16.83 — optimizer
  found a degenerate compensating-error solution (L35 layer-cosine 0.57).
- GTSM-style dense per-layer cosine (v3b, α=5.0): **36.6% sieve reduction
  vs 27.1%**; L35 cosine **0.57→0.94**. The degenerate basin was removed.

Empirical signature of a narrowed search space: **lower training loss is no
longer reachable by cheating; the only way down is the true trajectory.**

## The precondition most people miss

GTSM narrows the space **only when a target trajectory exists**:
- **distillation / our compression** — the teacher *is* the trajectory;
- **diffusion** — the forward noising process *manufactures* a trajectory
  with an analytically known score target.

Standard LLM **pretraining is endpoint-only** (data gives the next token,
not the intermediate residual stream) — so GTSM's leverage does **not**
apply directly there. Diffusion's deep trick is to *invent* a path to match,
converting an underdetermined endpoint problem into an overdetermined
trajectory one. CGTSM says trees and diffusion are doing the same move.

## Caveat (epistemic — keep before any published claim)

Theorem 3.2's exactness is for **SDEs with a shared diffusion tensor σ**.
"Depth = time, residual update = score" is an **idealization** of that SDE;
a discrete-depth transformer is not literally an SDE with known σσᵀ.

- The **narrowing principle transfers** (measured: compensating-error
  degeneracy removed, 27%→37%).
- The **literal Pθ = P\* guarantee does NOT transfer for free** — it is
  contingent on the SDE idealization and on cosine being a faithful enough
  stand-in for ‖·‖_D. **IOU**: this contingency is unverified for our setting.

## Related work — TSP (Tree-like Self-Play)

TSP (arXiv:2606.03489v1) is an **applied, empirical instance of the GTSM
principle on the discrete/LLM side** (full treatment: `tsp-trajectory-
distillation.md`). Same problem (endpoint/sequence-level signal too coarse for
localized errors), same fix (dense per-node signal along the generation
**tree**), same structure (TSP's generation tree = GTSM's discrete-tree side).

Two points matter here:

- **TSP corroborates the finite-budget weighting corollary (Prop F.6).** It
  deliberately *sparsifies* — concentrating its contrastive signal on a few
  critical "risk nodes" rather than matching everywhere — and wins (75.8 vs
  57.0 SFT, CodeLlama-7B). Per Thm 3.2 the zero-loss *fixed point* is
  weighting-independent; TSP's success is squarely a **finite-budget**
  phenomenon: spike `w(t)` where the learner is weak. Independent evidence for
  **audit #11**.
- **But it's contrastive, not regression.** TSP's loss is DPO-style ranking;
  GTSM is L2 score regression. The keystone bridge "residual = score" (Thm
  E.22) does **not** literally apply — the connection is structural, not a
  theorem.

The combined method (GTSM dense backbone + TSP targeted/iterative overlay, with
the teacher as the golden-path oracle) is **Targeted Trajectory Distillation**,
developed in `tsp-trajectory-distillation.md` — aimed directly at the
student-from-teacher compression north-star.

## One-sentence takeaway

GTSM replaces a single weak terminal-marginal constraint with a dense stack
of per-step score constraints whose intersection (by Girsanov, the full
path-space KL) excludes the compensating-error solutions that make endpoint
losses ill-posed — and zero-of-a-positive-integral guarantees this narrowing
for *any* weighting, provided you measure *everywhere*.
