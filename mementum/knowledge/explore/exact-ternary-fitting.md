---
title: "Exact Ternary Fitting — 3-way ΔL Acceptance Beats the Gradient Proxy"
status: active
category: algorithm
tags: [ternary-descent, td, exact-fitting, curvature, oscillation, gptq, obq, coordinate-descent, monotone, structural-zeros, exploration-target]
related:
  - ternary-descent.md
  - td-oscillation-problem.md
  - trace-guided-etching.md
  - training-protocols.md
  - score-matching-compression.md
  - two-registers-of-topology.md
depends-on:
  - ternary-descent.md
  - td-oscillation-problem.md
created: session 213
---

# Exact Ternary Fitting — 3-way ΔL Acceptance

> Session 213. New exploration target. Michael's idea: instead of using a
> **gradient proxy** to decide which signs TernaryDescent flips, directly
> evaluate the loss for all three ternary values `{−1, 0, +1}` at each
> position and take the one that improves loss most. Tested on the micro
> model — it works, the curvature term is the whole story, and it dissolves
> the s191 oscillation wall by construction (when done coordinate-wise).
>
> Register: **functional** (layer-local reconstruction loss under intervention).

## The idea

TernaryDescent (`ternary-descent.md`) decides flips from a gradient EMA: it
accumulates `direction = EMA(grad)`, `magnitude = EMA(grad²)`, and flips where
the signal-to-noise ratio is high and the descent direction opposes the current
sign. This is a **proxy** — the gradient is a *linear* (first-order) estimate of
how the loss changes, evaluated at the current point.

For a **ternary** weight the step is large (`v − a` can be 2), so the linear
estimate systematically overshoots: the gradient says "flip helps" because it
only sees the slope, but the actual discrete step lands somewhere the slope did
not predict. **This is the root cause of the s191 oscillation** (TD flips → GD
pushes back → TD flips again), and the entire S2 anti-oscillation stack
(cooldown, backoff, thermometer, conviction) exists to *suppress* it.

The idea: don't proxy. For each candidate position evaluate the **actual loss**
at `v ∈ {−1, 0, +1}` and take `argmin`. Accept only if it improves → monotone.

## The feasibility insight — no forward pass per position

The naive reading ("a forward pass per sign per position") is infeasible
(~10⁸ positions × 3). It is also unnecessary. For a **layer-local quadratic
reconstruction target** the exact loss-delta has a closed form computable for
*all* positions at once.

One linear layer, effective ternary weight `S` (per-row scale `γ`), real
calibration input `X` (n × d_in), teacher target `T = X @ W_floatᵀ` (n × d_out).
The rows are independent. Per row `i`, with residual `r_i = γ_i·(X@S[i,:]) − T[:,i]`,
changing `S[i,j]` from `a` to `v`:

```
ΔL_ij(v) = 2·γ_i·(v−a)·⟨r_i, X[:,j]⟩  +  γ_i²·(v−a)²·‖X[:,j]‖²
            └────── linear (= gradient) ──┘   └──── curvature ────┘
```

- `⟨r_i, X[:,j]⟩` for the whole `(d_out × d_in)` grid is **one matmul `Rᵀ@X`**.
- `‖X[:,j]‖²` is a precomputed `d_in`-vector; `γ_i` a `d_out`-vector.
- Evaluate the three `v`, take `argmin`. Done.

**The linear term IS the gradient TD already uses. The curvature term is exactly
what the proxy throws away** — and for ternary's large step it is not negligible;
it is the missing piece. (Verified in the harness: the closed form matches a
brute-force per-position loss recompute to ~1e-11.)

This is the OBQ / GPTQ / OBS family ("pick the quantization that minimizes layer
output error, with Hessian-aware compensation"). The micro experiment is an
independent re-derivation; the lineage is the proven, scalable form.

## The experiment

`scripts/experiments/ternary_exact_vs_proxy.py` (register: functional). Fit
ternary `S∈{−1,0,+1}` + per-row `γ` to four real weight matrices of the micro
model (`gate_proj` router + `value_proj` value-path, layers 0 & 2), against real
calibration activations (8704 token positions from `compile-train`). Start from
`S₀ = sign(W_float)`; matched flip budget (327/step); per-row optimal `γ`
recomputed each step. Three arms:

- **PROXY** — rank candidates by `|gradient|`, flip toward `−sign(grad)`. No
  curvature check (faithful full-batch analog of TD's acceptance rule).
- **EXACT-BATCH** — closed-form 3-way `argmin ΔL`, take top-B *improving* per step.
- **EXACT-SEQ** — greedy **one-at-a-time with rank-1 residual compensation**
  (GPTQ/OBS gold standard), monotone to convergence.

### Results (relative reconstruction loss `‖γ⊙(X@Sᵀ)−T‖²/‖T‖²`)

| config | baseline `sign(W)` | PROXY final | EXACT-BATCH | EXACT-SEQ |
|---|---|---|---|---|
| L0.gate  | 0.207 | **0.386** ↑ | 0.152 | **0.051** |
| L0.value | 0.116 | **0.269** ↑ | 0.137 | **0.016** |
| L2.gate  | 0.255 | 0.174 | 0.123 | **0.067** |
| L2.value | 0.174 | **0.208** ↑ | 0.176 | **0.040** |

| arm | loss-up steps / 120 | reversal frac | converged loss |
|---|---|---|---|
| PROXY | 55–76 | 0.29–0.89 | diverges past baseline in 3/4 |
| EXACT-BATCH | 51–61 | 0.21–0.94 | plateaus ~0.12–0.18 |
| EXACT-SEQ | **0** | — (monotone) | **0.016–0.067**, 14–22% sparsity |

### Three findings

1. **The curvature term is decisive.** EXACT beats PROXY at matched budget in
   every config. EXACT-SEQ reaches **3–7× below the `sign(W)` baseline**. The
   quantity the proxy discards is the quantity that matters.

2. **The proxy is non-monotone — it reproduces the oscillation wall on demand.**
   55–76 of 120 steps *increase* loss; reversal fractions up to 0.89 (chronic
   flip-flop). In 3/4 configs PROXY hits its minimum at step 0–2 then **wanders
   upward past the naive baseline** — it actively destroys the etch. EXACT-SEQ
   has **0 loss-up steps** and converges. The S2 stack is machinery to suppress
   oscillation that the gradient-proxy *acceptance rule* creates; exact ΔL
   acceptance is monotone for free.

3. **The "0" places itself.** With `{−1,0,+1}` as genuine candidates, EXACT-SEQ
   discovered **14–22% functional sparsity** by `argmin` alone — no magnitude
   threshold. Sign-decision and zero-placement unify (cf. the heuristic 30%
   structural zeros in `trace-guided-etching.md`).

## The important nuance — batching reintroduces oscillation

EXACT-BATCH (top-B improving flips per step, each ΔL computed independently)
still had 51–61 loss-up steps and high reversals. Flipping B positions at once
breaks the "everything else fixed" assumption behind each ΔL — the within-row
flip interaction. Only **EXACT-SEQ** (one flip at a time, recompute the row's
residual/γ/`Rᵀ@X` row after each — the GPTQ error-compensation move) is truly
monotone. Precise claim:

> **"Evaluate all 3 signs, take the best" dissolves the oscillation wall when
> done coordinate-wise with error compensation. Exact-but-batched is much better
> than the proxy but still interferes with itself.**

The compensation is cheap: a flip is a rank-1 update to the residual, and with
`XtXᵀ` (d_in × d_in) precomputed, each accepted flip updates one row of the
`Rᵀ@X` grid in O(d_in). Full coordinate descent to convergence is fast.

## Caveats (honest scope)

- **Layer-local reconstruction, not global next-token loss.** This is the cheap
  *exact* target by design. It aligns with `score-matching-compression.md` (v3b,
  dense per-layer score matching = 1.44× held-out) and `trace-guided-etching.md`;
  and audit #8/#7 (`audit-registry.md`) showed the global CE endpoint objective
  is degenerate (memorizes), so a layer-local surrogate is the cure, not a
  compromise. The closed form is exact only for the quadratic layer target; a
  global objective reintroduces downstream nonlinearity (forward replay).
- **The PROXY arm is an idealized full-batch analog of TD** (no EMA/SNR/cooldown).
  The claim is not "deployed TD oscillates this badly" — it is that *the
  acceptance rule at TD's core is non-monotone, and S2 is compensating for that*.
- Verified on a ~1M-param micro model; scale behavior untested.

## Where this points (open leads)

- **Wire it into TD as the acceptance rule.** Keep TD's gradient SNR as the cheap
  **proposal** (which positions are worth looking at), replace the gradient-driven
  **acceptance** with coordinate-wise exact ΔL + compensation. An OBQ/GPTQ inner
  loop wrapped in TD's proposal/budget/holographic-etch machinery. Test in an
  actual training step (`scripts/v15/train_td.py`).
- **Does monotone exact fitting remove the need for the S2 stack** (cooldown,
  backoff, thermometer)? If acceptance is monotone by construction, most of the
  anti-oscillation scaffolding may be redundant.
- **Cross-layer compensation** (full GPTQ): propagate the reconstruction error
  forward so later layers fit the *already-quantized* upstream — closes the gap
  between per-layer-local and global.
- **Scale test:** does the 3–7× gap over baseline (and over proxy) hold on a real
  teacher layer (Qwen3-0.6B/8B)?
- **Register check:** the exact loss here is reconstruction; a functional re-test
  should confirm the fitted ternary layer's *downstream PPL* improves, not just
  its local SSE.

## Files

| File | Content |
|------|---------|
| `scripts/experiments/ternary_exact_vs_proxy.py` | harness: capture layer I/O, 3 arms, ΔL self-test |
| `results/ternary-exact-vs-proxy/results.json` | per-config curves + summary metrics |
| `results/ternary-exact-vs-proxy/run.log` | run transcript |
