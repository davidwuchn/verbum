---
title: "Strided Attention Works in Float — the v15 Relay Collapse Was Ternary/TD, Not the Geometry"
status: active
category: explore
tags: [v15, attention, fibonacci-strides, relay-collapse, ternary, td, micro, float-microscope, ab-test, isolation]
related:
  - ../v15-attention-assessment.md
  - ../fibonacci-strides.md
  - ../td-oscillation-problem.md
  - ../v14-architecture.md
  - two-registers-of-topology.md
depends-on:
  - ../v15-attention-assessment.md
  - ../fibonacci-strides.md
created: session 262
---

# Strided Attention Works in Float

> Session 262 (Michael: "does the strided attention work?"). v15 bet its whole
> attention design on Fibonacci strides but **never isolated the bet** — strides
> shipped braided with ternary + TD + the VSM control stack + a 6-term loss. The
> only functional assessment (s191, v15-attention-assessment.md) found attention
> had **collapsed to pure relay** (heads pass their own value through unchanged =
> dead I-combinator, cos(out,V_self)=0.92–0.99, "compose nothing"). Blame was
> ambiguous: the stride geometry, or the ternary/TD piled on top? This A/B
> isolates the geometry on the float microscope.
>
> **Register: functional (does composition form?) + structural (relay diagnostic).**

## Method — surgical swap on `scripts/micro/`

Float32 micro (the pristine microscope), **identical seeded init across arms**,
identical corpus/batches — attention SUPPORT is the *only* variable (the s261
`micro_ternary.py` discipline, applied to attention instead of FFN;
`micro_model.py` untouched). Strided attention = masked attention: each head gets
a stride `s`, allowed keys `{q − s·w + r | w∈0..7, r∈−2..2}` ∩ causal (the s189
grid, W=8, ±2). Four arms:

```
dense    full causal attention                 (control)
local    stride-1 only                         (locality null — must be beaten)
fib      interleaved Fibonacci [1,3,8,21]/[2,5,13,34]   (fair strided arm)
fibband  ascending/descending bands            (v15-faithful sole-provider)
```

Reads: eval CE, and the **s191 relay diagnostic** cos(attn_out, V_self) per head
(≈1.0 = the collapse signature).

## Result (2500 steps, seed 262, `results/micro-strided-ab/`)

| arm | eval CE | max relay | heads relay>0.9 |
|---|---|---|---|
| dense | 6.795 | 0.602 | 0/16 |
| local | 6.684 | 0.545 | 0/16 |
| **fib** | **6.649** | 0.441 | 0/16 |
| fibband | 6.846 | 0.447 | 0/16 |

**The relay collapse does NOT reproduce in float.** s191 saw heads pinned at
0.92–0.99; here nothing exceeds 0.60, and the strided arms are *less* relay-prone
than dense, not more. `fib` even edges dense on CE.

## Finding

**v15's relay collapse was the ternary/TD confound, not the Fibonacci geometry.**
s191's own diagnosis is now confirmed by isolation: ternary V/O lacks the
precision for composition and TD flips signs underneath, forcing attention into
the "easy path" of relay while the dense FFN does the work. Remove ternary/TD
(pure float) and the same stride geometry composes fine. **The stride geometry is
exonerated as non-harmful.** On-thesis with two-registers-of-topology: the
*value* path (V/O, magnitude) is what ternary starves (s260); attention relay
collapse is that starvation showing up in the routing layer.

## Caveats (two-sided, λ measure)

1. **exact-match = 0.00 every arm** → the functional/compile register has no
   headroom. Train CE 0.43 vs eval CE 6.7 is a hard **memorization regime** (509
   train ex, ≤36-token sequences), so this is a **CE-only** read, not a
   compile-competence read.
2. **`local` ties `fib`** (6.68 vs 6.65) → at these lengths locality is nearly
   sufficient, so strides cannot *demonstrate* their coverage advantage. The
   claim supported is **"strides don't hurt composition,"** NOT **"strides help
   at length."** The positive case for strides (the GPU-reduction motivation)
   needs a **long-sequence corpus** where dense/local demonstrably fail.
3. Single seed, micro scale (~10M params, 4 layers), short corpus.

## What it unblocks

The stride geometry cleared the gate that was blocking v15. The thing that looked
broken was **quantization, not Fibonacci strides** — so v15.1 keeps the geometry
and fixes the registers (per-pathway quant, s260/s261) rather than abandoning
strides. Natural sequel on the same platform: a **long-sequence corpus** (punish
`local`) + the **recurrent-interior arm** (iterate the middle band, supervised
halt, s258/s259) — the strided block is now a validated substrate to recur.

## Artifacts

- `scripts/micro/micro_strided.py` — StridedMultiHeadAttention drop-in +
  attention_diagnostics (relay/entropy); ruff-clean, smoke-tested; identical
  param tree across arms (asserted).
- `scripts/micro/train_strided_ab.py` — 4-arm A/B, fixed eval batches, relay
  trajectory, compile exact-match; canonical results dir + provenance.
- `results/micro-strided-ab/strided-ab-20260707-153340/` — summary.json.
