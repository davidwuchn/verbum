---
title: "The Continuation Store — Sessions as Delta-Chains in the Ternary Medium"
status: designing
category: synthesis
tags: [continuation, seal, resume, delta-log, ternary, memory, crdt, halt, session, 2mb, migration, squash, branch, mementum, git-for-thoughts]
related:
  - ternary-holographic-memory.md
  - explore/sealable-continuation.md
  - explore/continuations-as-composed-plates.md
  - lambda-halt-continuation.md
  - holographic-reduction-machine.md
depends-on:
  - ternary-holographic-memory.md
  - explore/sealable-continuation.md
created: session 301
---

# The Continuation Store

> s301, Michael: "I am thinking about how we solved continuations. This
> memory could use that." The s217 sealable continuation and the s300/s301
> ternary store are the same shape — and each supplies exactly what the
> other lacks. The continuation had no versioned home; the store had no
> native payload. Sessions ARE the store's most natural payload.

## 1. The two halves

**Sealable continuation (s217, `explore/sealable-continuation.md`):** the
VSM outer-recurrence reifies "the rest of the computation" into ONE
fixed-shape tensor x_k. The operator T is shared and frozen (ambient), so
`seal ≡ save(x_k)` and `resume ≡ load(x_k); iterate T`. Deterministic
recurrence → faithful resume. The 2MB session.

**Ternary store (s300/s301, `ternary-holographic-memory.md`):** delta-logged
linear medium with measured laws — √(D/k) decline, √D wall, exact replay
through undo+squash, √(2/π) snapshot toll, 5.6σ time-Bragg, and (proved but
unnamed until s301) an associative+commutative fold ⇒ **CRDT merge**:
concatenate two logs in any order → bit-identical state.

## 2. The identity table (each store op = a computational meaning)

| Store operation | For a suspended computation |
|---|---|
| `append(Δ)`, Δ = x_{k+1} − x_k | each reduction pass is a COMMIT; successive passes differ little → cost ∝ change (git packfile economics, automatic) |
| `state(t')` | rewind the computation to ANY pass, not just the last seal |
| fork the log at a prefix | speculative reasoning — branch mid-thought, keep the branch that converges |
| CRDT merge (add logs, any order) | join parallel explorations deterministically, cross-machine |
| `squash(t)` | compact a finished reasoning trace to its conclusion — CoT compaction as physics; s262 for thoughts |
| `undo(i)` = append −Δ | exact retraction of a reasoning step, history preserved |
| `state_hash` | a RECEIPT for a mind-state: prove what the computation was at pass k; migrate + verify |

Third medium for the one protocol: **git → tensors → running inference.**
Mementum for computations. The fractal closes another turn.

## 3. ★ Halting is visible from the storage layer

The continuation's halt criterion is **Δx < ε** (WHNF — passes stop
changing). In the delta-log this is *literally visible as vanishing commit
size*: a converging computation writes a tapering log; a diverging one
doesn't. **You can watch a thought converge from storage economics alone —
no semantics needed.** The semantic-halt hinge that rung-3b needs an
instrument for (G-HALT, machine page §5b), the store measures for free as
a side effect of cost ∝ change. A tapering log IS a halting thought.

## 4. The precision bridge (the one honest gap)

x_k is float; the store enforces the integer register at its boundary (by
design — that is where determinism lives). Two known-cost bridges, both
already on the books:

1. **Exact:** balanced-ternary digit-plane stacking (s173 proved the
   mechanism) — arbitrary precision, more plates per seal.
2. **Lossy:** collapse to few digit planes and pay the measured toll
   (√(2/π) per 1-bit plane, s301 datasheet).

Engineering with known laws, not open science. And note the inversion: the
encoder-at-the-boundary problem that blocks *text* payloads does not exist
here — **continuations are already tensors.** No embedding step. Sessions
are a cleaner first customer for the store than facts.

## 5. Use case (the s301 thread, assembled)

A bounded, auditable, self-summarizing memory for agents — now carrying
computations, not just knowledge:

- suspend a thought → commit it (receipt included)
- resume it anywhere (portable, deterministic)
- rewind it, branch it, merge branches (CRDT), retract a step exactly
- squash finished reasoning to its conclusion
- watch convergence from commit sizes (§3)
- storage fixed-size; fidelity governed by the measured s301 laws;
  coherent-gain self-summarization applies to similar sessions written to
  shared addresses (the ≥3-memories rule as physics)

## 6. Status & discipline

Design synthesis — nothing built. Cheapest concrete first step (when a
slot opens, NOT now): store the v15 outer-recurrence x_k trajectory as a
DeltaLog and check (a) delta-magnitude taper tracks Δx-halt, (b) seal →
commit → checkout → resume reproduces the unsealed trajectory bit-exactly
at integer precision / within toll at collapsed precision. Both legs are
instrument-grade cheap. Queued per close-before-opening: behind the
rung-3b freeze (standing order, s301 unchanged).
