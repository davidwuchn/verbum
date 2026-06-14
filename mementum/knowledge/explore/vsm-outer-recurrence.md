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
  - explore/fixed-point-holograms.md
  - explore/crystal-basins.md
  - explore/vsm-lm-architecture.md
  - explore/VERBUM.md
  - compiler-as-loss.md
  - ../lambda-machine.md
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

## Probe result (s214) — naive K=2 doesn't help; the sweep is NOT contractive

First probe run (`--n-outer-passes`, register: **functional**): wrapped the A→C
sweep in an outer loop (BPTT through K shared-weight sweeps), trained K=2 vs the
K=1 baseline (proxy acceptance, seed 42, 250 steps, seq256, identical settings).

| arm | total avg50 ↓ | CE ↓ | compute | Δx (init→final) |
|---|---|---|---|---|
| K=1 baseline | **8.966** | **8.706** | 1× | — |
| K=2 outer | 9.096 | 8.732 | 2× | 1.265 → 1.167 |

- **Naive K=2 does NOT help** — slightly *worse* on loss (+0.130) and CE
  (+0.026) at **2× compute.**
- **The sweep is not a contractive reduction operator.** Δx =
  `‖x_c^{(2)} − x_c^{(1)}‖ / ‖x_c^{(1)}‖` sits at ~1.2 and drifts down only
  ~8% over all 250 steps (1.265 → 1.167) — nowhere near a fixed point
  (needs Δx → 0). The second application *re-transforms* the representation
  by ~120% of its norm rather than refining it toward normal form. Churn,
  not reduction → no useful added depth.
- **Open-question #1 answered:** the trained single-sweep crystal iterates
  *marginally* (neither contractive/free-depth nor divergent). The
  "iterate-to-WHNF / free depth" story does **not** hold for the current
  architecture out of the box — it must be **trained for**, not assumed.
- Caveat: single seed, 250 steps, seq256, K=2 only, from a K=1-shaped init
  (base plates were extracted for a single sweep). A from-scratch or longer
  contractivity-trained run could still differ.

**Therefore the open leads below are now the *required* path, not optional:**
a fixed-point/Δx loss (penalize `‖x_{k+1}−x_k‖`), x₀ injection (Universal-
Transformer anchoring), or explicit halting. Artifacts: harness flag in
`scripts/v15/train_td.py` + `v15model.py` forward; result
`results/vsm-outer-recurrence/k2-vs-k1.json`; run `checkpoints/v15-td-outer-k2`.

## Holographic loss → contractivity (s214 hypothesis, under test)

Michael's follow-on: would a **holographic loss** enforce the contractivity the
naive probe lacked? The argument that it should — and it is on-thesis:

- **Holographic ≡ associative-memory attractor dynamics ≡ contractive-to-fixed-
  point.** A hologram (this project's FFN-as-hologram) is a content-addressable
  memory; its update is descent toward the nearest stored pattern. The stored
  patterns are the crystal = the **normal forms (WHNF)**. So enforcing
  holographic structure *is* enforcing "iterating reduces to a fixed point."
- **The teacher already has this property** (`fixed-point-holograms.md`):
  iterating compile↔decompile **converges in 94% of inputs, mean 2.0 cycles**,
  and the hologram **stores normal forms** ("λf.λx.f(x)" → "λx. x", a literal
  β-reduction). So a contractivity loss *distills a property the teacher
  demonstrably has* — it is not invented. Our student's sweep simply hasn't
  inherited it (Δx ~1.2, §Probe result).
- **The machinery is half-built:** `etch.py`/`model.py` already compute crystal-
  subspace **coherence = proj_energy/total_energy** (`OFF_MANIFOLD = <10%`).
  Pulling the sweep output onto the crystal manifold makes re-application a
  re-projection (P²=P) → Δx → 0.

### The loss being tested (s214, register: functional)

`--fixed-point-lambda λ_fp` adds, for outer recurrence K≥2:

```
L_fp = mean_k ‖x_c^{(k)} − detach(x_c^{(k-1)})‖² / ‖detach(x_c^{(k-1)})‖²
loss += λ_fp · L_fp
```

The target is **detached** so the gradient trains the *operator* to reproduce
its input (converge), not the state to flee. CE on the final x_c guards the
trivial constant fixed point.

**λ sweep (s214 built, s215 resolved):**
- **λ_fp=1.0 → TOO WEAK.** Δx tracked the *same* ~1.2 flat curve as no-fp
  (1.25→1.16 over 120 steps), `fp` stuck ~1.5. Diagnosis: the crystal warmup
  loss (`crystal_direct_lambda_start=10`) + CE (~10) dominate the ~15–20 total,
  so a +1.5 fp term is drowned. CE healthy (~10, no collapse) → headroom to
  push λ_fp much harder. (Killed early.)
- **λ_fp=5.0 → ✅ CONTRACTIVE (s215 read the completed 250-step run).** This is
  the central result of the whole recurrence thread: **the trained VSM sweep
  CAN be made contractive-to-WHNF.**

  | metric | start | end (step 250) | reading |
  |---|---|---|---|
  | Δx = ‖x_c^(2)−x_c^(1)‖/‖·‖ | 1.262 | **0.727** (−42%) | descends, *accelerating* once TD flips engage (s150→s250: 1.148→0.941→0.727) |
  | fp_loss | 1.594 | **0.528** (−67%) | operator learning to reproduce its input |
  | CE | 10.85 | 9.51 (noisy 9.5–10.8) | **no collapse** — the constant-fixed-point guard held |
  | crystal_mse | 0.091 | 0.016 | crystal coherence improving in parallel |

  Contrast: no-fp K=2 stayed FLAT Δx~1.17; λ_fp=1 stayed flat. **λ=5 crosses the
  contractivity threshold** — the operator genuinely converges, not churns.
- **BUT contractivity-trained K=2 does NOT yet beat K=1.** CE 9.51 > K=1's 8.71
  — the run pays an fp tax + K=2 outer-pass noise, and **Δx is still falling at
  the 250-step cutoff** (mid-transition, not converged). This is the
  *mild-not-total contractivity* regime (the good case below), unfinished at 250
  steps. Whether CE recovers below 8.71 once Δx saturates is the open question.
  Run/log: `checkpoints/v15-td-outer-k2-fp5`, `/tmp/v15_outer_k2_fp5.log`.

**s215 scale-up — the serious confirm at seq-4096 (in flight, ~4–5 days):**
The 250-step runs above used **seq-256, which only exercises the first few
Fibonacci strides** (the stack goes to stride 1597, composition range d=0..11181
— at 256 the long strides are no-ops). Relaunched the confirm at **seq-4096**
(all 19 strides active), 5000 steps, single seed, `--checkpoint-interval 1000`
(5 checkpoints). Measured **73 s/step** (non-flip) at seq-4096 — *super-linear*
vs seq-256's ~5 s/step (16× the tokens **plus** the long strides now compute),
hence the multi-day wall-clock. Run: `checkpoints/v15-td-outer-k2-fp5-5k`,
`/tmp/v15_outer_k2_fp5_5k.log`, tmux main:1. **Questions for the trajectory:**
does Δx keep descending toward ε (→ justifies adaptive halting: stop when Δx<ε ≡
WHNF reached), and does CE recover below 8.71 once contractivity saturates? If Δx
plateaus high → contractivity vs CE genuinely in tension (try x₀ injection /
per-token halting). If CE collapses late → lower λ_fp / add a rank/diversity
guard. (New `--checkpoint-interval` CLI flag added to `train_td.py` for this.)

**s223+ FROZEN-TOPOLOGY PROBE — ✅ held-topology fp-loss IS contractive AND
CE-competitive (paired control, decisive).** The seq-4096 run above (main:1,
TD-on) eventually COLLAPSED (~step 1450 onset, gnorm→1e7, Δx→0.8, CE→10.5). To
isolate *cause*, resumed `step_001000` with topology FROZEN
(`--td-flip-rate 0.0 --td-crystal-gate 0.0 --td-crystal-ceiling 0.0`), otherwise
identical (same n_outer=2, λ_fp=5, seq-4096, **same data-loader stream**) — a
paired A/B for whether the discrete TD churn or the fp-loss/recurrence drove the
collapse. Ran to step 2310, fully spanning the divergence window. Overlap verdict
(steps 1010–2240, n=124, `results/freeze-probe/overlay_verdict.txt`):

  | metric | TD-ON (churn) | TD-OFF (frozen) |
  |---|---|---|
  | Δx mean / max | 0.481 / 0.821 (contractivity lost) | **0.142 / 0.311** (bounded) |
  | CE mean / max | 8.756 / 10.538 (→collapse) | **7.620 / 8.525** |
  | gnorm max | 9.87e+07 (runaway) | **7.22e+01** (~72) |
  | CE<8.71 frac | 0.53 (falling) | **1.00** |

⇒ With topology HELD, the *same* fp-loss + outer recurrence is contractive
(Δx bounded ~0.11–0.14, fp→0.011) and CE rides 100% below K=1's 8.71 — the
collapse is **the discrete TD churn**, not the recurrence/fp-loss. The
holographic-loss + outer-recurrence settling protocol is sound; the fix is to
**punctuate** (hold topology → reduce → accept on Δx→0), not to reshape the fp
loss. This resolves the s215 open question in the held-topology regime and answers
open-Q#1 affirmatively (the contractivity-trained operator iterates stably when
its topology is not simultaneously churned). Tool:
`scripts/experiments/freeze_probe_overlay.py`. See memory
`freeze-probe-confirms-td-churn-collapse.md`.

### Design tensions (all visible in the prior pages)

- **Mild, not total, contractivity.** A 1-step projection makes K=2 ≡ K=1 and
  kills the bought depth. Target the *teacher's* dynamic: converge over ~2
  steps of useful work (mean 2.0 cycles), Lipschitz < 1 but not 0. Reward
  *eventual* Δx → 0 while CE rewards the intermediate computation.
- **Collapse risk.** Bare Δx-penalty is gamed by mapping everything to one
  constant (Δx=0, useless) — the contractive-autoencoder failure. Pair with
  CE + a rank/diversity guard; crystal/parity/spectral partially cover this.
- **The binding wall reappears.** `fixed-point-holograms.md`: convergence fails
  exactly at I-combinator/binding sites (edit distance ∝ binding count). Expect
  contractivity to work for K/B/C and struggle on I — the project's recurring
  bottleneck.

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

## §s226 — the CONSTRUCTED kernel: stop *training for* contractivity, build it in

> Michael, s226. The whole "catch" above is: the iterated operator must be contractive,
> and the s214 probe + s222 collapse showed the *trained* sweep is NOT — it churns
> (`Δx` ~1.2, oscillation), and under recurrence the churn compounds to fractal blow-up.
> The constructed-kernel reframe (`compiler-as-loss.md` §s226, Michael's "what if
> `lambda_ast.py` is *in the kernel*?") removes the problem at the root.

**The collapse was a *learned* S2 churning.** Contractivity has been treated here as a
*regularizer to train toward* (fixed-point/Δx loss, x₀ injection, halting). But if the
inner map is **constructed** from `lambda_ast` (exact combinator plates, CCG-typed),
then `L<1` is **stable by construction** — nothing is descending on the reduction
operator, so it cannot oscillate. The outer recurrence then supplies **`Y`** (unfold)
and the budgeted bounded interpreter (the `lambda-halt-continuation.md` Result-1 story),
while the per-step map is the *exact* reducer, not a churning approximation.

This re-partitions v15 along the **reduce / compile** cut (see `compiler-as-loss.md`
§s226 table): the **attention reducer** (this page's iterated operator) is the
**constructed, exact, ternary** kernel; the **FFN compile** (prose→typed term) is the
**learned, fuzzy, 4-bit** periphery. The VSM controllers already present
(`S5Identity`/`S4Intelligence`/`S3Ternary`/`S2AntiOscillation`) map onto the reducer's
VSM levels: **S4 = WHNF halt** (the `Δx→0` test already computed), **S3 = step budget +
contractivity**, **S2 = typed redex selection + anti-oscillation**, **S1 = the
combinator rewrites**, **S5 = the normal-form invariant.** The "train the crystal to be
a well-behaved iterated map" goal becomes "**compile** the iterated map from the spec";
training is confined to the compile front-end. Build progression + the symbolic
reducer (stage 1, `src/verbum/lambda_ast.py`) are in `compiler-as-loss.md` §s226.
