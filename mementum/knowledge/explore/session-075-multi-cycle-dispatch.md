---
title: "Multi-Cycle Descending Arm — HRM-Inspired Self-Regulating Dispatch"
status: active
category: architecture
tags: [multi-cycle, hrm, dispatch, s3, continuation-gate, self-regulation, beer-vsm, cycle-continue]
related:
  - session-073-vsm-structure.md
  - session-071-dispatch-decoupling.md
  - kernel-montague-mapping.md
  - dispatch-gradient-death.md
  - consensus-evolution.md
depends-on:
  - session-073-vsm-structure.md
---

# Multi-Cycle Descending Arm

> Session 075. The descending arm's dispatch→stride→integrate
> now loops up to 3 times per pass, with the model itself deciding
> how many cycles contribute. Inspired by HRM's nested H/L loops,
> implemented as Beer's S3 self-regulation.

## The Insight

The Hierarchical Reasoning Model (Wang et al. 2025, arXiv:2506.21734)
uses two nested recurrent modules: a slow H_level (abstract planning)
and a fast L_level (detailed computation). The L_level loops multiple
times within each H_level step. With 27M params, it achieves near-
perfect Sudoku and maze solving.

The structural parallel to v10's VSM tree:

| HRM | v10 | Role |
|-----|-----|------|
| H_level (4 layers, slow) | S4 scan (once per pass) | Abstract planning |
| L_level (4 layers, fast) | dispatch→stride→integrate | Detailed computation |
| L_cycles = 2 | desc_max_cycles = 3 | Repetition count |
| z_L += z_H + input | cycle_inject_gate × x_anchor | Input injection |
| no_grad on N-1 steps | (deferred, viable for >3 cycles) | Memory optimization |

## The Problem Multi-Cycle Solves

Prior to this change, each descending pass got **one shot** to dispatch,
propagate, and integrate. For simple content this is fine. For
compositional operations (PARTIAL → APPLY), one cycle is insufficient:

1. Cycle 1 dispatches PARTIAL at position P. Stride propagates.
   But position P+1 (which should dispatch to APPLY) doesn't yet
   know that P dispatched to PARTIAL.
2. Integrate types the result, but with local-only context for cycle 1.

With multi-cycle:
1. Cycle 1: dispatch + stride propagates dispatch patterns spatially.
2. Cycle 2: position P+1 NOW sees P's PARTIAL dispatch through stride
   context. It can dispatch to APPLY. Integrate has both local op bias
   AND spatial context for informed type decisions.

This directly addresses the type-dispatch decoupling identified in
session 071 — typing needs spatial context that only exists after
dispatch has propagated.

## Architecture

### Multi-Cycle Flow (per descending pass)

```
S4 scan (once — slow, abstract)
│
├─ Cycle 0 [cumulative_gate = 1.0, always full]
│   ├─ Phase 0: KernelDispatch (route to 22 ops, top-k=2)
│   ├─ Phase 1: StrideStack (propagate dispatch spatially)
│   └─ Phase 2: KernelIntegrate (type + exact compute)
│   cycle_contribution = x - x_before_cycle
│   x = x_before_cycle + cumulative_gate × cycle_contribution
│   CycleContinue(registers) → continue_gate_0
│   cumulative_gate *= continue_gate_0
│
├─ Cycle 1 [cumulative_gate = continue_gate_0]
│   ├─ Input injection: x += cycle_inject_gate × x_anchor
│   ├─ Phase 0: KernelDispatch (re-routes with spatial context!)
│   ├─ Phase 1: StrideStack (re-propagates refined dispatch)
│   └─ Phase 2: KernelIntegrate (better typing with context)
│   x = x_before_cycle + cumulative_gate × cycle_contribution
│   CycleContinue(registers) → continue_gate_1
│   cumulative_gate *= continue_gate_1
│
└─ Cycle 2 [cumulative_gate = gate_0 × gate_1]
    ├─ Input injection: x += cycle_inject_gate × x_anchor
    ├─ Phase 0-2: (same shared weights, third refinement)
    └─ x = x_before_cycle + cumulative_gate × cycle_contribution
    (last cycle — no continuation gate needed)
```

### CycleContinue — S3 Between-Cycle Control

```python
class CycleContinue(nn.Module):
    # register_flat (n_registers × d_reg_real) → Linear(768, 1) → sigmoid
    # Zero-init weights, zero bias → gate starts at 0.5 (neutral)
    # The model learns:
    #   simple prose → gate → 0 (1 effective cycle)
    #   complex composition → gate → 1 (3 effective cycles)
```

VSM mapping: S3 already controls within-cycle (phase gating via
S3Ternary). CycleContinue extends S3 to between-cycle control.
The register state carries type/scope/role information accumulated
through the cycle's S3 phase updates — exactly the signal needed
to decide "was this cycle productive? would another help?"

### Input Injection (HRM Pattern)

```python
# At each cycle > 0:
x = x + sigmoid(self._cycle_inject_gate_raw) × x_anchor
# x_anchor = pre-cycle residual (what ascending arm produced)
# sigmoid(-4) ≈ 0.018 at init — nearly silent, model learns to open
```

HRM adds `z_H + input_embeddings` at every L_level step. This is
the v10 analog: re-ground the representation in what the ascending
arm produced, preventing drift across multiple dispatch cycles.

## Key Design Properties

### Static Graph, Dynamic Behavior
All cycles always compute (MLX requires static graphs). CycleContinue
controls behavior via gating, not short-circuiting. Cycle contributions
scale to near-zero when gates close — computed but ineffective.

### Cumulative Gate Product
Not per-cycle independent gates. The cumulative product means that
once a gate closes, ALL subsequent cycles are suppressed. This
prevents the model from learning "skip cycle 1, use cycle 2" —
cycles must be useful in order.

### At Initialization
- continue_gates = sigmoid(0) = 0.5 (neutral)
- effective_cycles = 1.0 + 0.5 + 0.25 = 1.75
- cycle_inject_gate = sigmoid(-4) ≈ 0.018
- desc_max_cycles = 3

### Backward Compatibility
- desc_max_cycles=1: no CycleContinue created, identical to pre-change
- Existing checkpoints load with desc_max_cycles=1

### Parameter Cost
- CycleContinue: 769 params (768 input + 1 bias)
- cycle_inject_gate: 1 param
- Total model: 23,896,417 (was 23,895,648)

## Observable Predictions

When training with desc_max_cycles=3, watch for:

1. **Continuation gates differentiate**: prose positions → gates close
   (effective ~1 cycle), structured/compositional → gates stay open
2. **Dispatch weights sharpen cycle-over-cycle**: cycle 2's top-1 op
   should have higher weight than cycle 1's (refinement effect)
3. **S3 phase gates differ between cycles**: cycle 2 operates on
   different register state, so alignment gates should diverge
4. **cycle_inject_gate opens**: if injection helps, the model pulls
   the raw value up from -4 toward 0 or positive
5. **effective_cycles tracks content complexity**: the JSONL metrics_log
   should show variance in effective_cycles across eval batches

## What This Does NOT Do

- **Adaptive halt** (HRM's Q-learning ACT): no per-example halt decision.
  CycleContinue is a smooth gate, not a hard stop. Future work could add
  a halt head on S5 that skips the descending arm entirely for simple tokens.
- **No-grad pre-passes** (HRM's 1-step gradient trick): all cycles get
  gradients. For desc_max_cycles > 3, the HRM trick (no_grad on N-1
  iterations, gradient only on last) would cap memory at 1-cycle cost.
  Deferred until needed.
- **Ascending arm changes**: multi-cycle is descending-only. The ascending
  arm's prep→stride→consolidate runs once per pass, unchanged.

## JSONL Instrumentation

Session 075 also added three JSONL log files to fix the data loss problem:

| File | Frequency | Key fields |
|------|-----------|------------|
| `metrics_log.jsonl` | eval_interval | cycle_continue_gates, effective_cycles, all VSM metrics |
| `train_log.jsonl` | log_interval | r, ce, lr, grad_norm, tok/s |
| `evolution_log.jsonl` | per generation | accepted/rejected, flips, consensus stats |

All append-only, survive resume. Load with `pd.read_json(..., lines=True)`.

## Files Changed

| File | Change |
|------|--------|
| `config.py` | `desc_max_cycles: int = 3` (replaces desc_cycles) |
| `components.py` | `CycleContinue` class + self-test |
| `model.py` | Multi-cycle descending branch, CycleContinue wiring, cycle_inject_gate, instrumentation |
| `train.py` | Per-cycle eval display, JSONL logging (3 files) |
