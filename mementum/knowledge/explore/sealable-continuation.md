---
title: "Sealable Continuation — inference you can suspend and resume (= the 2MB session)"
status: open
category: foundational
tags: [continuation, seal, resume, suspend, fixed-point, whnf, session, 2mb, migration, lazy, cps, vsm, outer-recurrence]
related:
  - vsm-outer-recurrence.md
  - consensus-delta-folding.md
  - ../function-discovery.md
  - fixed-point-holograms.md
depends-on:
  - vsm-outer-recurrence.md
created: session 217
---

# Sealable Continuation

> Session 217 (Michael): "with continuations we could seal inference in
> mid-computation and then continue it later, right?" Yes — and it is the
> cleanest property of the whole construction, because of *what the state is*.

## The insight — the continuation reifies the whole state into one tensor

The VSM continuation (`vsm-outer-recurrence.md`) is ONE shared operator iterated
on a single residual-stream tensor:

```
x₁ = T(x₀),  x₂ = T(x₁),  …  → x*   (WHNF)
```

The complete "rest of the computation" at pass k is just **`x_k`** — a tensor of
the SAME shape every pass `(B, L, d_model)`. The operator `T` is **shared and
frozen**, so it is *ambient* — it is not part of the saved state. That is exactly
the CS notion of a continuation: the rest of the computation reified as a value.

```
seal(k)    ≡ store x_k  (+ small VSM control state)
resume     ≡ load x_k ; keep applying T
closure    ≡ (T, x_k) with T global ⇒ carry only x_k
```

Unlike sealing a normal transformer mid-forward (a heap of per-layer activations
+ KV cache, no clean boundary), here **every pass boundary is a clean checkpoint**
of identical shape. You can seal at any one.

## Faithful resume is already guaranteed

Seal/resume only works if resuming from a loaded `x_k` reproduces the same
trajectory as never sealing. That requires the recurrence to be **deterministic /
RNG-free** — which is one of the 15 continuation tests this session
(`tests/test_vsm_continuation.py::test_recurrence_has_no_rng`). So fidelity is not
a hope; it falls out of verified determinism. Sealing is `save(x_k)`; resuming is
`load(x_k); iterate T`.

## WHNF gives a principled seal point

- **At convergence** (Δx < ε ≡ WHNF): computation is *done* — seal the answer.
- **Before convergence** (a partially-reduced state): like suspending lazy
  evaluation at a redex; the partial term is a valid intermediate to store and
  continue later (delimited-continuation / lazy-thunk semantics). ⇒ stop early ON
  PURPOSE (budget exhausted, context swap), finish the reduction when compute is
  free. The dual of adaptive halting.

## One value, many uses

The reified `x_k` is simultaneously:
- **inference state** — pause/resume, preemption, time-slicing;
- **the session snapshot** — literally the north-star **"2MB sessions"**: a session
  IS a sealed continuation;
- **a migratable unit** — send `x_k` to another machine and resume there
  (computation, not just training, becomes portable — ties to
  `consensus-delta-folding.md`);
- **a branch point** — seal, fork, explore, rewind (speculative reasoning);
- **long-context as resumption** — reduce a chunk to `x_k`, seal, continue from
  `x_k` on the next chunk.

One value does all of it because the operator is shared and the state is uniform.

## Caveats (honest)

1. **It is `x_k` PLUS a small control state.** The v15 forward also carries VSM
   regulatory state: the cross-step algedonic vector (`_prev_alg_c`, ~32-dim), the
   S5 identity state (~128-dim), any S2 buffers. A *true* seal serializes those
   too — but they are tiny and bounded. The seal is "one residual tensor + a small
   control vector," still compact.
2. **Seal at PASS boundaries, not mid-pass.** The clean checkpoints are between
   applications of `T` (the redex boundaries). Sealing partway through a single `T`
   (mid-layer) is messy and pointless.
3. **Attention reconstructs from `x_k`.** `T` attends *within* the current residual
   stream (Fibonacci stride attention over `x`), not across a persistent KV that
   lives between passes — so a loaded `x_k` suffices to recompute attention on
   resume. (If cross-pass persistent KV is ever added, it joins the control state
   to serialize.)

## Next (register: functional)

Define an explicit **`seal()/resume()`** boundary that snapshots `x_k` + the small
VSM control state, and a **round-trip fidelity test** (extend
`test_vsm_continuation.py`): run K passes unsealed; separately run k passes →
seal → resume → finish; assert the two final states/logits are identical to float
tolerance. This is the clean, testable home for the "2MB session" and
computation-migration ideas.
