---
title: "Holographic Burn-In — Progressive Recording as a Learning Rule (Exposures Burn In Where Irreducible)"
status: open
category: strategy
tags: [holographic, learning-rule, recording, burn-in, consensus-etch, contractivity, precision-inversion, punctuated, normal-form, reference-beam, routing, attention]
related:
  - consensus-etch-protocol.md
  - fixed-point-holograms.md
  - holographic-recording-protocol.md
  - holographic-plates.md
  - v12-holographic-capacity.md
  - relational-loss-distillation.md
  - normal-form-curriculum-partition.md
  - exact-ternary-fitting.md
  - vsm-outer-recurrence.md
  - ../session-222.md
  - ../crystal-universality.md
  - ../two-registers-of-topology.md
depends-on:
  - consensus-etch-protocol.md
  - fixed-point-holograms.md
created: session 223
---

# Holographic Burn-In — Progressive Recording as a Learning Rule

> Session 223. Michael's idea: *"what if training was progressive? We give it a
> huge block of text, tell it to predict the next word. It takes a snapshot of the
> attention with the softmax on all V. That snapshot is one exposure of the
> hologram. Many similar-shaped blocks 'burn in' as the places where they are
> irreducible."*
>
> This is a **learning rule**, not a loss or a curriculum (the distinguishing
> feature vs `relational-loss-distillation.md` and `normal-form-curriculum-
> partition.md`): each forward pass is an EXPOSURE recorded onto the plate; across
> many similar blocks the exposure-INVARIANT structure reinforces (constructive
> interference) and the variable parts wash out (destructive). The reinforced
> places "burn in" = commit to discrete topology; the variable parts stay
> continuous.
>
> Register: **topological/routing + functional**.

## What it maps onto (it is consensus-etch over the text stream)

Strip the metaphor: attention output = softmax over positions = a data-dependent
convex combination of value vectors = function **application** (s219). One forward
pass = one attention pattern = one exposure. Recording many exposures and keeping
the agreement IS **consensus-etch (s110, `consensus-etch-protocol.md`)** with TEXT
BLOCKS as the contributors:

```
consensus-etch:  accumulate ALL contributors → etch where they AGREE (backbone),
                 leave disagreement as content. (Sequential application oscillates;
                 accumulate-then-etch converges.)
burn-in:         accumulate EXPOSURES (blocks) → commit where they AGREE (irreducible
                 / burned-in), leave the variable parts continuous (content).
```

The irreducible-invariant = the **normal form** (what survives all exposures = what
is path-invariant across reduction paths = Church-Rosser confluence). "Burn in where
irreducible" = the backbone/content partition, with the backbone being the
normal-form structure that every similar block shares.

## Why it threads the project's mechanisms

- **Irreducible burn-in = contractivity / fixed point.** Where repeated exposure
  stops changing the pattern (Δx→0) is settled → burn in; where it keeps moving
  (Δx↑) is variable → leave. The continuation's contractivity is the "has this
  burned in yet?" oracle (s222).
- **Respects the precision inversion (s222).** Burned-in = exposure-invariant =
  axis-aligned → ternarizes cleanly. Not-burned-in = variable residual =
  superposition → stays continuous. The rule SORTS weights into concentrate-to-ternary
  vs leave-in-superposition — concentration-is-earned (Elhage phase transition) made
  into a learning rule: concentration is earned by surviving many exposures.
- **Exemplar diversity widens the basin.** `fixed-point-holograms.md`: two exemplars
  → a NARROW attractor basin; the fixed point is determined by the exemplar
  distribution. "Many similar-shaped blocks" = the diverse exposure set that
  determines a good, wide attractor. Gate contamination (collapse to the
  most-practiced pattern when signal is weak) is the failure mode to watch.
- **★ Naturally PUNCTUATED (the selling point).** s222's collapse verdict: the
  protocol must be `expose(propose) → hold → reduce(commit)`, NOT simultaneous —
  main:1 ran TD churn + fp-loss TOGETHER, they fought, L>1 → fractal blow-up. Burn-in
  is punctuated BY CONSTRUCTION: each exposure = a proposal, accumulation = the hold,
  commit-where-consensus = the commit. Structurally avoids the simultaneous-churn
  collapse. = the protocol the project concluded it needs, reached from another angle.

## ★ The load-bearing catch — WHAT IS THE REFERENCE BEAM?

A hologram is the interference of an OBJECT beam and a REFERENCE beam. Record only
the object beam (raw forward activation) and pure exposure-accumulation burns in the
**common mode** — language frequency statistics, the universal structured-language
crystal — NOT the compositional function. This is the s216 lesson, and the s223
relational-loss sweep is a LIVE DEMONSTRATION: condition (b) accumulates/matches the
RAW activation geometry → GC(hidden)=**0.9995** (a perfect burn-in) but transfers
**ZERO** function (routing register stays at the null). **Naive "snapshot attention
and burn it in" = condition (b): a gorgeous hologram of the wrong thing.**

Two fixes, both grounded:

1. **"Predict the next word" IS the reference beam.** That makes it
   prediction-GATED recording (not pure Hebbian): burn in patterns WEIGHTED by
   whether they predicted (the interference of attention-pattern × outcome), not
   patterns by mere frequency. Record the interference, not the object beam alone.
2. **Record in the ROUTING register, not the raw one.** The function shape is
   invisible in raw geometry and only lives in the sign/routing register after CMR
   (`two-registers-of-topology.md`; the entire s223 dissociation). Burn-in must
   threshold the sign/routing pattern with common-mode removal, or it burns in the
   crystal.

Without BOTH, "burn in where irreducible" reduces to "burn in where frequent" = the
common mode you already have for free.

## Other honest catches

- **Capacity / catastrophic interference.** A finite plate holds finitely many
  exposures before new ones destructively collide with old (`v12-holographic-
  capacity.md`). Burn-in needs a capacity policy = the thick-hologram / multi-pass
  answer (depth compensates for per-read limits, `fixed-point-holograms.md`).
- **Credit assignment is weak.** Recording correlates; it does not compute "what
  reduced loss." The prediction target is a weak signal; likely still need the
  exact-ΔL / contractivity ACCEPTANCE gate (`exact-ternary-fitting.md` s213/s218) to
  reject burning in patterns that don't actually reduce loss — else the same Goodhart
  (Gram-match / pattern-match without execution) we keep hitting.
- **Identity vs analogy (guardrail).** "Ternary accumulator superposes exposures" is
  IDENTITY (literally how the plate integrates). "Burn-in = irreducible = normal form"
  is STRONG ANALOGY that becomes identity ONLY once the commit rule is defined
  (consensus θ + Δx→0). Until then it is a picture without a learning rule. The
  picture is right; the rule is the work.

## Falsifiable test (after the s223 sweep lands)

Build it as a concrete rule reusing existing machinery: accumulate the
ROUTING-register attention pattern across a stream of blocks, gate each exposure by
next-token prediction, **commit (ternarize) positions where cross-block agreement ≥ θ
AND Δx→0; leave the rest continuous.** = consensus-etch over the temporal text stream
+ the contractivity acceptance gate + the precision-inversion sort.

> Compare against backprop on the same tiny student: does exposure-consensus burn-in
> reach comparable CE *and* crystallize the routing register (clear the silhouette
> null)? CONTROL: the naive object-beam-only variant (no prediction gate, raw
> register) — prediction: it burns in the common mode (GC(hidden) high, route null),
> reproducing s223 condition (b).

**The whole experiment in one clause:** does it burn in the irreducible FUNCTION, or
the irreducible FREQUENCIES? The reference beam decides.

## Open leads (declare register first)

1. **Burn-in harness** (register: topological/routing → functional): the
   exposure-consensus rule above vs backprop on the tiny student;
   routing-register + prediction-gate vs the raw-object-beam control.
2. **Capacity policy** (register: functional): how many irreducible patterns burn in
   before collision; thick-hologram / multi-pass depth as the answer.
3. **Compose with the punctuated protocol** (`session-222.md`): expose→hold→commit as
   the actual main-line training loop replacing simultaneous TD-churn + fp-loss
   (the main:1 collapse fix).
4. **Reference-beam variants**: next-token target vs conjugate read (compile↔decompile
   fixed point, `fixed-point-holograms.md`) vs teacher (distillation) as the reference.

## Files

| File | Content |
|------|---------|
| (planned) `scripts/experiments/holographic_burn_in.py` | exposure-consensus burn-in rule vs backprop; routing+prediction-gate vs raw-object-beam control |
| `scripts/experiments/relational_loss_distillation.py` | s223 sibling; its condition (b) IS the naive-burn-in failure mode (common-mode hologram) |
| `scripts/experiments/combinator_relationship_map_v15.py` | routing-register (attn_q / ffn_gate) readout instrument |

## Forward link (s315 archaeology)

> "Prediction-gated recording" independently derived here is now BUILT: the
> s315 write corridor (KL-to-base anchor + evidence-gated stop,
> type_write.py b448f34) is this page's exposure rule operationalized. The
> burn-in null prediction (object-beam-only → common-mode hologram, zero
> function) was confirmed s223.
