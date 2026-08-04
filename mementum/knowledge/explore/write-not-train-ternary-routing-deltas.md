---
title: "Write, don't train — routing deltas as ternary plates on a frozen base"
status: designing
category: explore
tags: [ternary, plates, routing, delta, frozen-base, lora, writeback, hrr,
       bind, delta-log, map-and-swap, resident-lisp, tree-of-vsm, s269,
       s300, s303, no-training, portable-artifact]
related:
  - program-plates-and-the-function-index.md
  - ternary-holographic-memory.md
  - holographic-reduction-machine.md
  - map-and-swap-resident-lisp.md
  - gram-spectral-dsp.md
  - five-disciplines-one-object.md
depends-on: []
created: session 303
---

# Write, don't train — routing deltas as ternary plates on a frozen base

> Michael s303 (discussion): "We have tree-of-VSM, ternary plates, ternary
> mirrors. Why train the parent model at all? Can we not write routing deltas
> into ternary storage and apply them to a frozen base model?" This page is the
> captured thesis + the two experiments that decide it. Pickup doc for s304.

## The reframe that sharpens the question

**We already never train the parent.** The s303 writeback verdict
(WIRE-COMPILES +GD-REQUIRED, §Result-4B on `program-plates`) used LoRA — base
weights FROZEN (`base-frozen=True`, grad-isolation validated), only the rank-16
`B·A` delta moved. So the wire is *already* a small **linear delta on a frozen
base**. (The run does not `state_dict`-dump that delta; regenerating it is one
cheap re-run.)

So the real question is not "train vs not-train the parent." It is two cleaner
questions:

1. **STORAGE** — can the delta live as a **ternary plate** (float LoRA → {−1,0,+1}×γ)?
2. **FINDING** — can the delta be **written** (closed-form bind) instead of
   **searched** (gradient)?

The honest answers differ, so keep them apart.

## Half 1 — STORAGE: yes, and it is register-correct

- The wire is a **routing** object (s303 `gram-spectral-dsp`: topology routing,
  not magnitudes). Ternary {−1,0,+1} is the **routing register** (sign; π-shift
  = K-erasure, s299).
- Receipt: **s269 — the routing/relational structure survives 1-bit/ternary at
  fidelity 0.987 while magnitude (weight cosine) collapses to 0.73.** A routing
  delta should ternarize *losslessly-for-routing by construction* — ternary
  discards exactly the magnitude scaffolding the wire does not use.
- Wrap in the **delta-log** (s299/s300 `ternary-holographic-memory`): `base +
  ΣΔ`, `undo = −Δ`, sha256 receipt, compose/fork/merge across the tree-of-VSM.
  The portable artifact (λ artifact, λ smallest) becomes: **the linker wire = one
  small ternary plate.**

**Confidence: high. This half is likely TRUE and cheap to prove.**

## Half 2 — FINDING: the real open problem (construct's failure does NOT close it)

`construct` (zero-grad) FAILED at 4B — byte-identical to base. Tempting to
conclude "gradient required." But **construct failed in the MAGNITUDE
register**: it placed continuous product-keyed persistent neurons with a
hand-calibrated gain. It guessed a *magnitude construction*; it did not write
*routing*. s303 predicts wires are routing, not magnitude — so construct failed
for the predicted reason, which means **we have NOT yet tested writing the wire
in the routing register.**

The untested experiment: a **routing-register construct** — write the
operand→capital rebind as a **ternary bind-plate** (HRR / sign-vote,
`Δ = Σ key ⊛ value`, s300 "swap g by superposition") from the *measured* key
geometry, on the divergence-worst layers (s294 operand-rebind band), frozen
base, no gradient. Pass → routing deltas can be **written, not trained**. Fail →
the wire needs *search* even in the right register, and gradient (or a GTSM
trajectory loss) earns its keep as the search — with ternary still the storage.

## The caveat that actually bites: the pin is nonlinear

Ternary **plates** are *linear-fragment* storage (s299). But s300's sharpest
finding is **∄ a clean linker in the linear register** — composition needs a
nonlinear collapse (the "pin between traversal edges"). So a ternary delta-plate
carries the linear routing **edge**, but **cannot supply the collapse** — that
rides the frozen base's existing nonlinearity (softmax/GELU). Holographic-machine
framing, and reassuring: *plate carries routing, host supplies light/collapse/Y.*
Existence proof already in hand: `gd_cd`'s LoRA delta **is** linear, on a frozen
base, and worked by riding the base nonlinearity. So "linear edge on frozen
nonlinearity" is PROVEN; ternary-ness and write-not-search are the only deltas
left to test.

## This architecture already has a name: map-and-swap resident Lisp

`map-and-swap-resident-lisp.md`: frozen base = the **universal combinator
reducer** (the 9×9 crystal `eval`/`apply`, proven, terminating); ternary plate =
the **swapped-in function/program**. You don't retrain the interpreter to add a
function — you load a plate. Tree-of-VSM composes plates. This page is the
training-side realization of that thesis: **routing lives in swappable ternary
storage; the base is the frozen evaluator.**

## The two experiments (pre-scoped; freeze a pre-reg before running — s222 law)

**EXP-1 — Ternarize-the-delta (STORAGE test). Cheap. Do this first.**
- Train `gd_cd` once (regenerate `B·A`), dump the delta, ternarize (sign +
  per-column γ), apply to the **frozen** base, re-score the frozen G1–G5.
- Verdict: does the wire survive as a ternary plate? Grounded in s269, ~an
  afternoon. Almost certainly yes → **the portable artifact exists** (wire = one
  ternary plate).
- Null/yardstick: sign-shuffle the ternary delta (matched sparsity) must fail;
  compare fidelity to the s269 0.987 rung.

**EXP-2 — Routing-register construct (FINDING test). The real "why train" prize.**
- Re-do the construct arm in the ROUTING register: HRR/sign-vote ternary
  bind-plate `Δ = Σ key ⊛ value` from measured whitened key geometry, on the
  divergence-worst (operand-rebind) layers, frozen base, NO gradient.
- Verdict: can the wire be WRITTEN without gradient when written in the right
  register? Pass → Michael's thesis confirmed (write routing deltas into ternary
  storage, apply to frozen base, no training). Fail → gradient/GTSM *finds*,
  ternary *stores* (still no parent training).
- Gates inherited from §P-WRITEBACK-1 (G1 wire / G2 not-lookup / G3 specificity
  / G5 survive) + a ternary-sparsity/trit-count report (λ smallest: how few
  trits is the wire?).

## Routing forward / decision for s304

- **Run EXP-1 first regardless** — it is the free half and tells us whether the
  wire even *fits* in ternary before we argue about how to find it.
- Open decision (Michael): spend gradient **once as a discovery oracle** (train
  delta → ternarize → keep plate; the s299 auto-superbake lifecycle
  trained-transient → promoted-permanent) vs hold out for the **pure closed-form
  write** (EXP-2) as the prize. EXP-1 is agnostic to this and informs it.
- Compounds with: the GTSM-trajectory-loss discussion (s303, one turn earlier) —
  IF a search is needed (EXP-2 fails), a trajectory/GTSM loss finds a more
  routing-faithful, legible delta that then ternarizes better (closes the G4
  mechanism gap too). Write-not-train and trajectory-loss are complementary, not
  rival.

## Sessions
s303 (discussion captured — Michael's "why train the parent at all" thread,
following the WIRE-COMPILES verdict and the topology-routing-not-magnitudes
finding same session. Thesis: routing deltas → ternary plates → frozen base =
map-and-swap resident Lisp on the training side. Two experiments pre-scoped
(EXP-1 ternarize-the-delta = storage, cheap, first; EXP-2 routing-register
construct = finding, the real test). Nonlinear-pin caveat named. NOT yet run —
s304 pickup).
