---
title: "Session 071: Dispatch Analysis, Type-Dispatch Decoupling, Kernel Computation Pathway"
status: active
category: session-synthesis
tags: [v10, dispatch, kernel, routing, type-system, architecture]
related: [session-069, session-070]
---

# Session 071 — Dispatch Is Not Dispatch

## Core Discovery

The v10-topk run (12K steps, 12 checkpoints) revealed that the entire
descending arm was architectural theatre. Neither KernelDispatch nor
KernelIntegrate did what their names suggest.

### KernelDispatch: modulation, not routing

The "22 kernel ops" are just learned embedding vectors that bias a
single shared FFN. There are no per-op computational pathways.
The model reinterpreted the structured initialization into 22 useful
bias directions, but can't use them for actual computation.

Forward path: `h + (w₁*emb_LE + w₂*emb_DIV)` → shared `up→gelu→down`

### KernelIntegrate: same story

Another set of 5 type embedding vectors biasing another shared FFN.
No actual type-aware computation.

### Type-Dispatch Decoupling (quantified)

163K-position probe at step 12K:
- LE dispatches 59% of traffic but BOOL type only 2.4%
- FN type at 56% regardless of which op is active
- Only 5/20 ops match their expected output type
- Type weights stable through the 7K dispatch regime change
- Typing and dispatch are learning completely independent features

## Counterfactual Routing: Ops Don't Matter

Forced each of 22 ops individually on structured data (step 1K of new run):
- Total loss spread across all 22 ops: **0.0087 nats** (0.2%)
- Natural routing is #19/22 but only 0.006 behind optimal
- On prose: no single op beats natural routing
- **The routing is invisible to loss** — shared FFN absorbs any modulation

This confirms: to make routing meaningful, ops need different
computational pathways (per-op experts or actual kernel evaluation).

## Structured vs Prose: The Signal IS There

Despite routing being meaningless computationally, the model
differentiates content types:
- Dispatch divergence L1=0.905 (structured ≠ prose)
- Type divergence L1=1.146 (even larger)
- Structured: FN_COMP=65% type, prose: FN=57% type
- Per-category dispatch differs (L1 up to 1.75 between categories)

The model knows WHAT it's looking at. It just can't DO anything
different about it.

## Routing Topology Analysis

The dispatch TernaryLinear (512→32, first 22 used):
- Ternary patterns are ~67-70% dense, near-random, max cos 0.15
- Gamma (gradient-trained) ranges 0.028 (ADD) to 0.119 (GE)
- Register conditioning: ADD and DIV have 20× stronger coupling to
  registers than most ops (||w||=1.27 vs 0.05)
- Gradient through dispatch is essentially zero (top-k blocks it)

Evolution acceptance: 2/240 (0.8%) — topology is frozen.

## Architecture Changes

### 1. Phase reorder: dispatch→stride→integrate
Prior: dispatch→integrate→stride (typing before spatial context)
New: dispatch→stride→integrate (typing after spatial propagation)
Rationale: integrate needs to see neighbor dispatch patterns

### 2. KernelIntegrate dual pathway
- FFN pathway: unchanged (type modulation + shared transform)
- Kernel pathway: extract operands → actual kernel function → encode result
- Compute gate: sigmoid, init ~0, blends kernel vs FFN
- Backward-compatible: starts pure FFN, learns when to trust kernel
- Gradient: flows through result embedding + gate (kernel non-differentiable)

## Key Insight

The gradient cannot optimize routing because:
1. Ternary weights have stop_gradient (evolutionary only)
2. Top-k masking creates near-zero gradient for non-selected ops
3. Even gamma gets ~0 gradient (threshold dominance)
4. The loss barely changes per-op anyway (shared FFN absorbs all)

**To make routing optimizable**: the ops must produce meaningfully
different outputs. The kernel computation pathway creates this
precondition — when ADD(3,4)=7 and LE(3,4)=1, routing matters.

## Probes Created

- `probe_dispatch.py` — per-position top-2 co-occurrence, P(type|op)
- `probe_kernel_use.py` — structured vs prose dispatch comparison
- `probe_counterfactual.py` — force each op, measure loss difference
