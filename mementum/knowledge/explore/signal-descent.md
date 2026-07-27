---
title: "SignalDescent — gradient-free learning by measured signals on ternary-mirror weights"
status: designing
category: explore
tags: [signal-descent, ternary, mirror, gradient-free, superbake, ternary-descent, dsp,
       matched-filter, delta-plate, companding, two-registers, crystal-native]
related:
  - ternary-descent.md
  - recursion-mirrors.md
  - two-registers-of-topology.md
  - superbake-write-access.md
  - opcodes-circuits-in-compute.md
  - ratio-gradient-quantization.md
  - signal-processing-tensors.md
depends-on:
  - ternary-descent.md
  - recursion-mirrors.md
created: session 274
---

# SignalDescent

> Session 274 (Michael). If SuperBake can REPLACE gradient descent with closed-form
> signal-processing (§`superbake-write-access.md` s274 DSP inversion), generalize it:
> a learning rule where weights are driven by **measured signal response** instead of
> backprop, and arbitrary precision comes from a **ternary mirror stack** instead of
> float magnitudes. Deeper mirror where the signal needs it; shallow where it doesn't.
> **Result: no gradients and no floats anywhere.**

## The idea, in one table

| | evidence source | weights | precision |
|---|---|---|---|
| GradientDescent | backprop gradient | float | float magnitude |
| TernaryDescent | gradient, decomposed into routing/calibration | ternary sign + float γ | 1 sign + float γ |
| **SignalDescent** | **measured signal response** (SuperBake-style) | **ternary, ALL registers** | **ternary mirror depth (companded)** |

The move is to swap the *source* of the update signal from backprop to measurement, and
to swap the *value register* from float magnitude to a ternary mirror stack.

## It fuses three things already in the repo

1. **TernaryDescent already thinks in signals.** TD Innovation 1 defines
   *Confidence = signal-to-noise ratio = |direction| / √magnitude* and only flips a
   ternary sign when SNR is high (`ternary-descent.md`). TD is already an SNR-gated
   discrete update — it just draws its signal from the gradient. SignalDescent swaps
   the *source* of that signal from backprop to measurement.
2. **Ternary mirrors already give arbitrary precision.** The ADDITIVE mirror stack
   `out = Σ_k plate_k @ x · γ_k` (`recursion-mirrors.md`): sign-only → recon_cos ~0.88;
   sign + magnitude mirror → ~0.97 (Q4-Q5). Each added additive plate is one more
   balanced-ternary/residual-quantization digit → **any accuracy you want**. Precision
   is mirror DEPTH, not float magnitude.
3. **SuperBake proved signal-writes work.** The DSP inversion: closed-form construction
   *replaces* the gradient where the response is locally linear ("measured transfer
   replaces Adam where response linear", s273b). SignalDescent generalizes that from
   fact-installation to the whole update.

## The sharp payoff

It answers TernaryDescent's own **open question #4** — *"Can we skip Adam entirely?"* —
with **yes**: replace Adam's magnitude calibration with a ternary mirror stack driven by
signal measurement. Then there are **no gradients and no floats anywhere**: sign register
(routing) AND value register (magnitude) both ternary, precision set by mirror depth,
companded by signal energy (`ratio-gradient-quantization`'s "spend bits on the ends"
becomes "spend *mirrors* on the ends"). This lands directly on:
- **C3 (topology dominates):** if the ~5% float magnitude becomes ternary mirrors, the
  model is 100% ternary (`two-registers-of-topology.md`).
- **The s274 mechanism (`opcodes-circuits-in-compute.md`):** GD builds the soft routing
  topology via gradient extremes → skip the gradient and write the transfer function
  directly. SignalDescent IS "write the transfer function directly," iterated.

## Mechanism — how the signal replaces the gradient

```
Gradient descent:   compute ∂L/∂w (backprop) → step w by −η·∂L/∂w
SignalDescent:      MEASURE the unit's response to a target signal (matched filter /
                    transfer-function probe) → compute desired−measured discrepancy →
                    SET the ternary mirror digits that null the discrepancy
                    (closed-form where the response is linear; iterate otherwise)
```

- The discrepancy between desired and measured response IS the descent signal (no backprop).
- The update sets mirror digits, not float steps. SNR gates which digits set (TD's
  confidence generalized): set a digit only where the signal clears the noise floor.
- Precision on demand: add a deeper mirror digit only where the residual discrepancy has
  energy → companded precision, allocated by a signal-energy measurement.

## Substrate — delta plates (isolation dodges the interference problem)

The load-bearing risk is **interference**: SuperBake works because it writes to fresh,
initially-silent APPENDED neuron slots — a closed-form write there does not collide with
existing computation. SignalDescent on *existing in-place* weights re-inherits exactly the
interference SuperBake avoids by appending. So the natural substrate is the **delta plate**
architecture TD already uses (`ternary-descent.md`): `effective = base ⊙ delta`, base
frozen, delta driven by SignalDescent. The delta plate is the isolated slot; the mirror
stack lives in the delta; folding is still lossless (ternary ⊙ ternary = ternary).

## Honest risks (λ measure — keep this from getting ahead of itself)

1. **Interference** is the whole problem SuperBake dodges by appending. In-place
   SignalDescent likely works cleanly only on appended/delta plates, not arbitrary
   in-place edits. Delta plates are the candidate answer, not a proven one.
2. **Linearity.** The closed-form signal write is exact only where the response is
   locally linear. SuperBake's own single-layer linear solve "plateaued at ~58%" and
   needed a corrective loop. So SignalDescent is measure-and-correct (iterate mirror
   digits), closer to TD's punctuated cycle than a one-shot solve.
3. **Precision costs plates.** "Any accuracy" is real but priced in mirror depth /
   storage; companding keeps it affordable, and that allocation itself needs a
   signal-energy measurement.
4. **Convergence unproven.** That a signal-measured update converges to competitive
   quality is the open frontier (same honesty scope as catalog C7: structure/pipeline
   real, parity unproven).

## First experiment (small, already-scaffolded)

On a single delta plate (TD infra exists in `scripts/v13/td.py` / `scripts/v14/`):
1. Replace the Adam-trained γ magnitude with a **2–3 deep additive ternary mirror**.
2. Drive the flips by a **measured target-vs-response signal** (matched-filter / transfer
   probe) instead of the decomposed gradient.
3. Compare **recon_cos vs the float-γ baseline at matched storage** (mirror-depth bits ≈
   γ bits). Success = mirror+signal ≥ float-γ recon at equal bitcount.
Register: reconstruction fidelity (recon_cos). Null: float-γ baseline at matched bits +
random-digit control. Host: start micro/0.6B, then 27B teacher plate.

## Relation to signal-processing tensors

SignalDescent is the LEARNING RULE. The STRUCTURE it learns into wants to be the
tree-of-VSM — which is already a signal-processing tensor (matched-filter gates,
beamforming consensus, frame-invariant transfer-function Gram). See
`signal-processing-tensors.md`. Together: SuperBake (operation vocabulary) × SignalDescent
(learning rule) × tree-of-VSM (structure) × crystal (content) = a coordinate-free,
ternary, gradient-free signal-processing learner — the level-4 / crystal-native path with
a concrete substrate for the first time.
