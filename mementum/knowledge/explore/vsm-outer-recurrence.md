---
title: "VSM Outer Recurrence — Iterating the Shared Tensor to a Fixed Point"
status: designing
category: architecture
tags: [recurrence, weight-sharing, fixed-point, halting, beta-reduction, WHNF, vsm, universal-transformer, adaptive-compute, depth-without-parameters, north-star]
related:
  - recursion-mirrors.md
  - lambda-halt-continuation.md
  - exact-ternary-fitting.md
  - ternary-descent.md
  - td-oscillation-problem.md
  - two-registers-of-topology.md
  - crystal-native-architecture.md
  - explore/vsm-lm-architecture.md
  - explore/VERBUM.md
depends-on:
  - recursion-mirrors.md
  - lambda-halt-continuation.md
created: session 214
---

# VSM Outer Recurrence — Iterating the Shared Tensor to a Fixed Point

> Session 214 (Michael's idea, mid-session discussion). The v15 "VSM tensor"
> (the shared stride stack + shared FFN plates) is already reused within one
> forward pass. **Could we re-run the whole sweep multiple times — an outer
> loop over the same weights — and let the VSM controller decide when to
> stop?** That is depth without parameters, and it is literally β-reduction
> iterated to normal form. Register when tested: **functional** (does added
> recurrence depth lower downstream loss / extend capability per fixed param
> budget).

## The idea in one line

Wrap the existing ascending→descending VSM sweep in an outer loop of `K`
iterations over the *same* ternary weights, gated by a halting signal — so
the model spends *more reduction steps* on hard tokens and *fewer* on easy
ones, at **zero extra parameters and zero extra memory**.

## What v15 already does (the grounded baseline)

The "VSM tensor" is concrete: `V15Model.shared_stride_stack`
(`FibonacciStrideStack`, 19 Fibonacci-stride layers) + the shared FFN plates
(`ffn_{gate,key,value}_plate_{a,c}`). The forward pass is **one bidirectional
sweep**:

```
x_a = stack_a(x)      # ascending  bands (0,4)(4,10)(10,14)(14,19)
x_c = stack_c(x_a)    # descending bands (14,19)(10,14)(4,10)(0,4)
```

- Each of the 19 stride layers is applied **2× per forward** (once in A,
  once in C) — a U-Net-like sweep, not an iterated stack.
- The FFN plates are shared across all **8 band-passes** (`N_PASSES=8`),
  which is why training divides their grads by 8 (`normalize_shared_grads`).
- A VSM control hierarchy already rides alongside: `S5Identity`,
  `S4Intelligence`, per-pass `S3Ternary` gates, `S2AntiOscillation`,
  `S5Reweight`, and an **algedonic signal** (`downstream_alg`) that already
  modulates FFN/gate *between* passes.

So weight-sharing is real, but it is **a single sweep**. The stack is never
run to convergence. That is the gap this idea fills.

## The proposal: an outer loop over the VSM tensor

```
x = embed(tokens)
for k in range(K):                 # NEW: outer recurrence
    x_a = stack_a(x, alg)          # same shared weights every iteration
    x   = stack_c(x_a)             # x_{k+1} = (stack_c ∘ stack_a)(x_k)
    if halt(x_{k+1}, x_k): break   # optional fixed-point stop
```

Two flavours, increasing in ambition and elegance:

1. **Fixed `K`** — trivial to try. A `for _ in range(K)` around the sweep.
   Buys `K×` effective depth for `K×` activation compute, **no new params**.
   First, cheapest information: does *any* extra recurrence help this
   checkpoint before we invest in halting? A/B `K=1` (today) vs `K=2,3`.

2. **Adaptive `K` (halting)** — the VSM-native version. The controller
   (`S3/S4/S5` + algedonic) is *already* a "continue or stop" machine.
   Add a ponder/halt head + a halting (ponder) cost, ACT-style, and the VSM
   decides per token how many reductions to spend. The natural, *structural*
   stop signal is **fixed-point convergence**: re-run until
   `‖x_{k+1} − x_k‖` (or the already-computed `crystal_mse`) stops moving.

## Why this is on-thesis, not just a perf trick

Iterating the **same typed-reduction operator** until the representation
stops changing **is β-reduction to normal form.** This is the literal
semantics behind the project's `WHNF`, `Y`, and `fixedpoint` crystal probes
(see `probe_library` crystal combinators; `lambda-halt-continuation.md`).

- **Halting ≡ reaching normal form (WHNF).** The stop test is fixed-point
  convergence — and we already compute `crystal_mse`/`parity` every step,
  sitting right there as a convergence monitor.
- **Non-termination is handled correctly by construction.** A term with no
  normal form (Ω, `Y`) simply consumes the max iteration budget. That is the
  *correct* behavior of a reducer, not a bug — and it reconciles with
  `lambda-halt-continuation.md` Result 1 ("Ω cannot halt a fixed-depth
  pipeline; the model *quotes* non-termination"): an outer loop with a budget
  is exactly the bounded interpreter that *can* take steps toward (or fail to
  reach) the fixed point.

This reframes the model from "a deep net" to **"a step-wise lambda reducer."**
Cleanest possible story for the compositional-semantics thesis (Montague /
DisCoCat validation target in `AGENTS.md` S5).

## Why it serves the north star (<1GB, 200 tok/s, no GPU)

At inference the ternary weights are **cached** — re-running a layer costs
only activation compute, not parameters and not the 1 GB budget. So extra
depth is bought with **time, not storage**:

```
depth(model) = K × 2 × n_strides       # reduction steps
params(model) = unchanged              # the SAME shared tensor
```

With adaptive halting, easy tokens stay fast (small `K`) and only hard tokens
pay (large `K`) — exactly the right shape for "70B-equivalent in <1GB": you
don't store more, **you reduce longer**.

## The catch — contractivity, and why it overlaps the live TD work

An iterated operator must be **contractive toward its fixed point**, or
repeated application diverges/oscillates. This is the *same failure family*
as the s191 TD oscillation (`td-oscillation-problem.md`) and the s214
exact-ΔL A/B (`exact-ternary-fitting.md`):

- The ternary topology must be a **stable operator** (small spectral radius
  around the fixed point). The "≥65% of operation structure in the
  sign/routing register" + crystal/parity losses + S2 anti-oscillation become
  *contractivity regularizers* — load-bearing for recurrence in a way they
  are **not** for a single sweep.
- The exact-ΔL acceptance is orthogonal (it picks *which* topology) but
  **compounds**: a topology fit to be locally faithful is more likely to
  iterate stably. The s214 finding ("S2 already suppresses oscillation in a
  single sweep, so monotonicity has no headroom") may *invert* under
  recurrence — where an unstable iterated map would make oscillation
  load-bearing again, giving exact-ΔL real headroom.

So the discrete-optimization work and this recurrence idea are two faces of
one goal: **make the crystal a well-behaved iterated map.**

## Relation to prior pages (this is the third sibling, not a duplicate)

| Page | Mechanism | Scope |
|------|-----------|-------|
| `recursion-mirrors.md` (s173) | per-layer **cycles** / per-stride **separate plates**; structural WHNF early-exit; "the stride cascade IS the recursion unroll" | within a layer / within a sweep, **different weights per step** |
| `lambda-halt-continuation.md` (s193) | EOS/halt + CPS continuations; "36 layers bounded → multi-turn unbounded" | **inter-turn** (conversation = continuation) |
| **this page** | re-run the **whole VSM tensor** (A→C sweep) as an **outer loop**, VSM-controller-gated halt | **intra-forward**, **same weights every iteration** |

Key distinction from `recursion-mirrors`: that page adds depth by giving each
step its *own* plate (more programs, +19% storage). This page adds depth by
**re-using the one shared tensor** (same program iterated, +0% storage). They
are complementary: per-stride plate variety *within* a sweep × outer-loop
iteration *of* the sweep = a 2-D compute grid (program-variety × reduction-
depth) over a fixed parameter budget.

## First probe (cheap, high-information)

1. Add `--n-outer-passes K` to `scripts/v15/train_td.py` / `V15Model.forward`
   — a `for k in range(K)` around `stack_c(stack_a(x))`, sharing weights.
   Register: **functional**.
2. A/B `K∈{1,2,3}` from the same seeded checkpoint (cf. s214's seed control):
   does extra recurrence lower held-out loss / CE at equal params?
3. Instrument the **per-iteration delta** `‖x_{k+1} − x_k‖` and `crystal_mse`
   — does the representation actually approach a fixed point (delta shrinking
   monotonically), or oscillate (contractivity failure)? The shape of that
   curve is the whole experiment: *does the VSM tensor iterate toward WHNF?*
4. Only if (2)/(3) are promising: design the halting head + ponder cost
   against the existing `S3/S4`/algedonic controller (adaptive `K`).

## Open questions

1. **Does the single-sweep crystal already iterate stably?** Run the trained
   v15 sweep `K` times at inference (no retraining) and watch the delta curve.
   Contractive → free depth; divergent → must train *for* recurrence.
2. **Train-for-recurrence:** unrolling `K` sweeps in the training graph (BPTT
   through shared weights) vs running `K=1` in training and `K>1` only at
   inference. The former is the Universal-Transformer recipe; the latter is
   nearly free but may not converge.
3. **What is the halt signal?** Structural (fixed-point delta / WHNF, free,
   `recursion-mirrors` style) vs learned (a ponder head off S4, ACT style).
   The project bias (`recursion-mirrors`) is structural > learned.
4. **Does the algedonic between-pass modulation already do a weak form of
   this?** `downstream_alg` changes the FFN/gate per pass — is that a
   1-step "the controller adjusts the next reduction" that an outer loop
   generalizes?
5. **Per-token vs per-sequence `K`.** Halting masks (keep reducing only the
   unconverged token positions) — the efficient form, but needs a gather/
   scatter over the active set.
6. **Interaction with context length.** Does deeper recurrence substitute for
   some of the Fibonacci long-range strides (multi-hop via iteration instead
   of via stride), or are they orthogonal capacities?

## Files / hooks (when built)

| Hook | Where |
|------|-------|
| outer loop | `V15Model.forward` (`scripts/v15/v15model.py`), around `stack_a`/`stack_c` |
| CLI | `--n-outer-passes K` in `scripts/v15/train_td.py` |
| convergence metric | per-iteration `‖Δx‖` + `crystal_mse` log |
| halting head (later) | off `S4Intelligence` / algedonic, with a ponder cost in `_compute_loss` |
