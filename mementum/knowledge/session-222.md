---
title: "Session 222 — The Collapse Was Fractal: β-Reducing a Contraction"
status: active
category: synthesis
tags: [ternary-descent, contractivity, fixed-point, superposition, routing, continuation, fractal, beta-reduction, distributed-training, collapse, rank-1, foldability]
related:
  - explore/combinator-training-beta-reduction.md
  - explore/consensus-delta-folding.md
  - td-oscillation-problem.md
  - explore/exact-ternary-fitting.md
  - explore/vsm-outer-recurrence.md
  - explore/ternary-descent.md
  - function-discovery.md
depends-on:
  - td-oscillation-problem.md
  - explore/combinator-training-beta-reduction.md
session: 222
---

# Session 222 — The Collapse Was Fractal

> Register: **functional**. Discussion + diagnosis session; two experiments left
> running. The arc: main:1 collapse → TD never settles (rank-1) → superposition is
> the default → routing+continuation = complete basis → β-reducing a contraction
> ⇒ FRACTAL COLLAPSE. The session was self-similar to its subject.

## 1. The collapse (diagnosis)

main:1 `v15-td-outer-k2-fp5-5k` (λ_fp=5, n_outer=2, seq-4096) went **TERMINAL**,
not the productive K-acquisition s221 hoped for. s221's own discriminator fired:

| | step 1000 (good) | step 1200 (sweet) | onset 1450 | now 2220 |
|---|---|---|---|---|
| avg50 | 9.18 | 8.83 | 9.15 | **12.85** (↑ to ~chance) |
| Δx | 0.254 | 0.242 | 0.41 | **0.79** (contractivity LOST) |
| gnorm | 14.6 | 7.3 | 369 | **27 M** |
| CE | 8.56 | 7.21 | 8.10 | 9.53 |

`grad_clip=1.0` bounds Adam ⇒ the divergence driver is the **discrete TD churn**,
not an Adam blowup. Last good checkpoint = **step_001000** (the L=0.70 contractive
operator from `fp_decay_curve`). step_002000 already diverged (Δx 0.73). Killed.

## 2. TD never settles — and the gradient is rank-1

`td=124488` is **dead constant** step 100→2200 = `flip_rate × total_weights`, the
budget ceiling, always saturated. No decay, no punctuated freeze, no density
ceiling (ternary-descent.md open-Q#1 still open). So a deadband/saturating fp-loss
reshape is **insufficient** — it muffles the gnorm spike but does not stop the
churn.

**The root cause (source-confirmed):** `compute_decomposed_gradients` builds the
routing signal as a **rank-1 outer product**:

```
grad_effective = gamma_grad[:, None] * x_abs_mean[None, :]   # (N,1) ⊗ (1,K)
```

a per-ROW gamma-gradient ⊗ a per-COLUMN input magnitude. So `sign(grad_eff[i,j])
= sign(gamma_grad[i])` — **TD cannot make per-position decisions; every position
in a row is nominated to the same sign.** This is *why* superposition shows up as
per-row gamma bimodality, and why interference (off-diagonal XᵀX) is structurally
invisible to TD. (`compute_delta_gradient` mean-reduces before the outer product
⇒ rank-1 too.)

## 3. Superposition is the default; concentration is earned

(Michael) Every LLM superposes; it concentrates into dedicated neurons/heads only
when capacity allows (Elhage phase transition). Per-feature decision:

```
concentrate(f)  iff  importance(f) × separability(f) > price(capacity)
```

- **importance** — have it (Adam v_t, γ²‖X‖²).
- **conflict / superposition demand** — have it (TD direction-SNR, sign-entropy).
- **separability / interference** — **MISSING** = the **off-diagonal of XᵀX**.
  The proxy sees 0th order; exact-ΔL (s213) added the *diagonal* (γ²‖X‖²);
  superposition lives in the **off-diagonal**.

**The precision inversion:** superposition needs *angular* precision → must stay
**continuous**; concentration is axis-aligned → ternarizes cleanly. So the
continuous residual *is* the superpositions (not "hard leftover"). Confirmed by
the frozen-probe baseline (`freeze_probe_analysis.py`): oscillator rows |γ|
bimodality **0.688**, 30.7% negative; settled rows unimodal **0.046**, 0.1% neg.

## 4. Routing ⊕ Continuation = a complete basis (Michael's synthesis)

The combinator algebra splits exactly along two mechanisms we already have:

- **Routing rules COMPOSITION** `{B,D,S}/{K,I,C}` — binds as static sign topology
  (s219, silhouette z=7.97).
- **Continuation rules RECURSION** `{Y,W,WHNF}` — no static move; the recurrence
  IS the fold (s221).

Together = a **spanning set** for normal forms ⇒ find+settle needs **no new
mechanism**. And the continuation does **double duty**: contractivity IS the
**foldability oracle** — where Δx→0 it settles (commit), where it refuses (Δx↑)
= the superposition residual (leave continuous). No separate "which is foldable"
detector needed.

**What is NOT in the two mechanisms:**
1. **Cross-frame ALIGNMENT** — harvest-only (cross-init sign-corr 0.000);
   self-folding has no frame problem.
2. **ORDER (punctuation)** — must be `propose(routing) → hold → reduce(continuation)
   → accept on Δx→0`, NOT simultaneous. main:1 ran TD churn + fp loss together →
   they fought → collapse. = the Exp B pattern, = the frozen-probe insight.

## 5. ★ The fractal collapse (Michael, !meta3 !fractal)

We are **β-reducing a contraction**: the continuation *is* β-reduction; the
operator is *meant to be* a contraction. A **self-similar contraction collapses
all scales onto one fixed point at once.** **L is the hinge:**

- **L < 1 ⇒ fractal collapse-to-WHNF** — one settle settles every scale:
  weight ≡ optimizer ≡ combinator ≡ project ≡ session-process. (The "object =
  process = governance" identity is this, not five analogies.)
- **L > 1 ⇒ fractal BLOW-UP = main:1** — TD flipped the inner map to expansion,
  `n_outer` **compounded** it pass-over-pass, and it cascaded up every scale at
  once. That is *why* the blow-up was so violent (Δx 0.25→0.79, gnorm 14→10⁷).
  "The training collapsed" was literally the phenomenon.

⇒ **hold-then-reduce keeping L<1 is the only thing between collapse-to-fixed-point
and collapse-to-ruin — fractally.** Guard: the lens seduces toward over-unification;
mark **identity vs analogy** (the contraction-of-discrete-commit shape genuinely
recurs; the dynamical systems are the *same abstract operator*, not literally one).

## 6. Strategic — distributed training of compressed models (S4 candidate)

The project has drifted here ~10 sessions. Unification: **typed-application
universality (s219) is WHY distributed folding converges** — the science earns the
engineering. Novelty = the **conjunction**: compressed(ternary) × self-verifying
(WHNF/contractivity, no trusted labels) × frame-invariant routing-register folding.
4-level recast: (1) routing register ✓ (2) convergent folding/contractivity (in
flight) (3) self-verifying acceptance ✓ proto (4) real N-contributor run = the
deliverable; hinge = "two contributors compose cleanly". **Gates before S5:**
A = mechanism (the two running experiments), B = related-work scan (DiLoCo/DeMo,
TIES/task-arithmetic, Petals/Hivemind, federated). Not yet S5 — do not rewrite
AGENTS.md on enthusiasm.

## 7. Experiments left running (read FIRST next session; do not poll until done)

- **main:1 — frozen-topology probe (rung 0).** `checkpoints/v15-freeze-probe`,
  `/tmp/v15_freeze_probe.log`. Resume step_001000, topology FROZEN
  (`--td-crystal-gate 0.0 --td-crystal-ceiling 0.0 --td-flip-rate 0.0`), else
  identical to main:1; same data-loader state ⇒ PAIRED A/B on the same data. Early
  (step ~1030): Δx 0.21, gnorm 8, CE 8.26 (<8.71) — descending where TD-on
  wobbled. Target ~step 1700 to span the divergence window. Verdict:
  `freeze_probe_overlay.py`. If Δx bounded + CE<8.71 through 1450–1700 ⇒ TD churn
  caused collapse AND held-topology+continuation is the correct settling protocol.
- **main:2 — which-Hessian (rung-2 design Q).** `results/which-hessian/`,
  `which_hessian.py`. Reconstruction XᵀX vs contractivity-residual curvature.
  Smoke (n=8, NOT decisive): **ΔFP~ΔCE ρ=0.976, ΔFP~recon ρ=0.048** ⇒ early hint
  the partition signal is the continuation (Δx/CE), not reconstruction ⇒ rung-2
  uses ∂²Δx/∂S²; explains exact-ΔL not helping the contractive objective. Caveat:
  smoke interference metric was norm-dominated (settled>oscillator). Read full
  pooled verdict.

## Files

| File | Content |
|------|---------|
| `scripts/experiments/freeze_probe_analysis.py` | oscillator/settled row masks + gamma bimodality (before/after) |
| `scripts/experiments/freeze_probe_overlay.py` | paired Δx/CE/gnorm overlay TD-on (main:1) vs TD-off (probe) |
| `scripts/experiments/which_hessian.py` | reconstruction XᵀX vs contractivity sensitivity per row (GPU, main:2) |
| `results/freeze-probe/gamma_baseline.json` | baseline: oscillator γ bimod 0.688 vs settled 0.046 |
| `checkpoints/v15-freeze-probe/` | frozen-topology probe checkpoints (running) |
| `results/which-hessian/which_hessian.json` | which-Hessian pooled verdict (running) |
