---
title: "Rotation Is a Series of Soft-β Reductions — the Two Math Engines Are One"
status: open
category: synthesis
tags: [beta-reduction, attention, rotation, fourier, church-encoding, combinator, duplication, interference, arithmetic, unification]
related:
  - attention-as-beta-reduction.md
  - date-fourier-rotation.md
  - gram-registers-and-the-route-map.md
  - ../curry-howard-closes-the-loop.md
depends-on:
  - attention-as-beta-reduction.md
  - date-fourier-rotation.md
created: session 344
---

# Rotation Is a Series of Soft-β Reductions — the Two Math Engines Are One

> Session 344 (Michael: "we have speculated that attention is a soft beta reduction;
> that rotation could be a series of reductions in the interference"). A unifying
> hypothesis reached from a fresh exploratory read (`arith_trace`, Qwen3-14B) + two
> standing findings (attention-as-beta-reduction s247b; date-fourier-rotation s128).
> Theory, grounded in retrodiction; owes a pre-registered discriminator to earn keep.

## The two-engines observation (arith_trace, s344, exploratory)

Pointing the audited opcode tracer (`opcodes/`, null-gated sign(gate) reader) at a
task-typed battery on Qwen3-14B reads TWO math mechanisms in TWO registers:

| math kind | register | opcode read |
|---|---|---|
| **reduction arithmetic** (2+3, succ, ×) | **FFN / gate** | **S, Y** — the duplication+recursion sector; never NO-OPs |
| **modular / cyclic** (dates, clock, day-of-week) | **attention** | FFN-**silent** (NO-OP 0.38); s128: geometric **rotation**, R²=0.95 |

Language (prose) reads the affine **KIBC** block `{I,C,K,B}` in both registers;
retrieval reads **WHNF** (halt/lookup). So math ≠ language (duplication sector vs
affine block), and *within* math, reduction ≠ rotation (FFN S/Y vs attention
rotation). The old "β_I for arithmetic" memory (s127/s161) was the OLDER 12-op ISA
vocabulary; the current 9-op CRYSTAL says the operative opcodes are **S, Y** — which
is theoretically *correct*: Church numerals REQUIRE duplication (`S = B(BW)(BBC)`;
numeral n = n-fold application = n contractions), and the affine KIBC fragment cannot
duplicate. Math being S/Y-heavy *is* the Church signature in the right basis.

## The unifying hypothesis: rotation = iterated soft-β on a circular encoding

`attention-as-beta-reduction.md` (s247b) already pins attention as **soft β-reduction**:
`out_i = Σ_j softmax(q_i·k_j) v_j` — Q = redex seeking its operand, K = operand
addresses, V = operands, softmax = selection; the softmax is a *convex combination*
(superposition of substitution), exact β being the `softmax → argmax` limit. FFN = the
β-program (ROM); attention = the one-instruction CPU.

Michael's extension decodes cleanly onto s128's own numbers:

> **"a series of reductions in the interference"** = a per-**layer series** (rotation
> *accumulates across L12→L16*, s128) of per-**head interference** (the *distributed
> collective mode*, "like a phonon," top-10 heads each adding ~0.15 rad, s128).

Composing: **rotation-by-Nδ = N soft-β steps on a *circular* (Fourier) encoding**, each
step a superposition-of-substitutions interfering across heads into a net rotation. And
rotation-by-Nδ = iterated application of rotate-by-δ = **Church-numeral N acting on a
rotate-by-δ operator on the day-circle**. That is the *same* iterated-soft-β engine as
linear arithmetic — the S/Y duplication+recursion sector — just executed on a **circular
representation** instead of a linear one. **The two engines collapse into one:** iterated
soft-β reduction over two encodings (linear → FFN; circular → attention).

## The discipline guard (why this is not yet a win)

Our own audit flags it (s204, `audit-registry` #): *"all attention is a weighted sum;
'β-reduction' is interpretation... induction/n-gram heads produce similar patterns."* So
"attention = soft β" is a beautiful lens, **trivially true at the weighted-sum level**,
that has NOT beaten the confound. And s128's linear-in-N + additive-across-heads fit
**retrodicts** the series-of-reductions story — but a learned rotation matrix R(Nδ) also
produces linear-in-N + additive heads. Per the frame ledger, **retrodiction ≠ win.** This
owes a *pre-registered* discriminator that separates "series of soft-β reductions" from
"one learned rotation," not another retrofit.

## The discriminating make-or-break — ⚪ §P-ITERATED-SOFT-REDUCTION

Two axes separate iterated-soft-β from a content-free learned rotation, and one test
covers both engines:

1. **Operand routing (the β signature).** A soft-β reduction *substitutes an operand* —
   so the rotation must route through **V / day-operand content**. Prediction: patching V
   at the day-token positions moves the rotation; a learned rotation matrix would not
   depend on V. (Directly answers the audit's "is it β or just a weighted sum?")
2. **Work-scales-with-count (the Church signature).** A *series* of reductions means
   reduction work scales with the numeric count: "9 days after" recruits more β-steps /
   accumulation layers / S-Y recruitment than "2 days after"; a single R(Nδ) applies
   once, work flat in N.

**The unification test:** run the identical count-scaling probe on *both* linear
arithmetic (FFN gate: does S-recruitment scale with operand magnitude?) *and* circular
arithmetic (attention: does β-step-count / accumulation scale with the offset?), with the
V-operand-routing patch as the "really β, not a rotation matrix" control and a
learned-rotation null. If **both scale with the count → one iterated-soft-β engine, two
encodings.** If only linear does → the engines are genuinely separate. (Subsumes the
narrower §P-ARITH-DUPLICATION.)

## Bounds

Theory + one exploratory read (Qwen3-14B, small battery, gate register blind to {B,C};
attn read soft). The unification is a *hypothesis*; the arith_trace read is exploratory
(no a-priori/verdict); s128 is the cited rotation measurement (not re-run here). The
whole attention=β frame is interpretation-heavy and carries the standing audit caveat.
Next: freeze §P-ITERATED-SOFT-REDUCTION with the operand-routing control + learned-
rotation null.
