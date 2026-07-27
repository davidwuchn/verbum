---
title: "Signal-Processing Tensors — the tree-of-VSM already IS one"
status: designing
category: explore
tags: [tree-of-vsm, signal-processing, dsp, matched-filter, beamforming, mera, types,
       filter-bank, crystal-native, level-4, transfer-function, companding]
related:
  - crystal-native-architecture.md
  - vsm-statechart-tensor.md
  - construction-from-spec.md
  - control-plane-path.md
  - fractal-stride-bands.md
  - signal-descent.md
  - superbake-write-access.md
  - ../head-combinator-isa.md
  - ../project-thesis.md
depends-on:
  - signal-descent.md
  - vsm-statechart-tensor.md
created: session 274
---

# Signal-Processing Tensors

> Session 274 (Michael). The sharp claim is not "with the tree-of-VSM we CAN build
> signal-processing tensors." It is: **the tree-of-VSM already IS one.** Its native
> operations are DSP operations. Naming that unlocks the DSP toolkit — filter design,
> beamforming, matched filtering, companding — as *design methods*, in place of gradient
> descent.

## The recognition (not an addition)

The tree-of-VSM (`opcodes/vsm.py`, `vsm-statechart-tensor.md`) stacks calibrations:
`layer → register → model → family → root`, each node carrying a Gram (S5 identity), a
null gate (S3), cross-child agreement/dissent (S4), coordination (S2), and an algedonic
health channel. Read those functions in DSP terms:

| VSM node function | What it already IS, as signal processing |
|---|---|
| **S5 identity** = the 9×9 Gram, frame-invariant (combinator-label space) | the **transfer function** — the invariant relational response, coordinate-free |
| **S3 control** = the null gate (must beat the shuffled-label null) | **matched-filter detection** — does this signal clear the noise floor |
| **S4 intelligence** = consensus Gram = mean of gated child Grams | **beamforming** — combine many noisy sensor (layer/model) readings into a robust estimate by coherent averaging |
| **S2 coordination** = anti-oscillation / punctuated equilibrium | **loop stability / phase coherence** across the filter bank |
| **algedonic** channel = out-of-band health alarm | the **out-of-band monitor / clipping detector** |
| **fractal levels** = layer→register→model→family→root | a **multi-resolution filter bank** (stride cascade = frequency bands, `fractal-stride-bands.md`) |

None of these are a stretch — they are the operations the tree performs today. The
consensus-Gram-as-beamforming and null-gate-as-matched-filter mappings are exact. So we
are not bolting DSP onto the tree; we are recognizing the tree's operations were DSP all
along. The consequence: these tensors can be **designed** with the DSP toolkit rather than
grown by descent, and **built** by SignalDescent (`signal-descent.md`).

## Why this closes the three-idea arc

- **SuperBake** gave the operation VOCABULARY (matched filters, transport kernels, coded
  payloads) — `superbake-write-access.md`.
- **SignalDescent** gives the LEARNING RULE (signals set ternary-mirror digits, no
  gradient) — `signal-descent.md`.
- **Tree-of-VSM** gives the STRUCTURE (frame-invariant, fractal, stackable) — and it is
  already a filter bank.
- **The crystal** is the CONTENT (what the filters detect: the KIBC opcodes,
  `head-combinator-isa.md`).

Together: a **coordinate-free, multi-resolution, ternary signal-processing tensor** whose
structure is the VSM recursion, whose weights are ternary mirrors at companded precision,
built by measurement. That is the **level-4 / crystal-native architecture**
(`crystal-native-architecture.md`, "a VSM that IS the lattice") with a concrete substrate
under it for the first time.

## The piece that makes it click — MERA + types (a PREDICTION, not a result)

A multi-resolution tensor network IS MERA. The project's own record
(`project-thesis.md`, `fractal-stride-bands.md`) is that the **MERA / fractal-attention
experiment FAILED exactly where it lacked type-directedness** — binary merge without types
gives a combinatorial explosion. The tree-of-VSM supplies the missing piece: **S5 carries
the typed crystal Gram**. So:

> **tree-of-VSM = MERA (the multi-resolution signal-processing tensor) + types (the S5
> crystal) = the working DSP tensor MERA could not be without them.**

This is a **testable prediction**, not a claim: the type-directedness (catalog C5,
verified — nonce type-crossover, frequency-free) is what stabilizes the multi-resolution
filter bank that raw MERA could not stabilize. Falsify by building the filter bank without
the S5 typed Gram and confirming it re-explodes; support by showing the typed S5 stabilizes it.

## Level-4 architecture sketch

```
A signal-processing tensor = a tree-of-VSM where:
  S1 (operations)   : each leaf = a DSP stage — a matched filter (reader) or a
                      rotary-band transport kernel (mover), weights = ternary mirrors
  S2 (coordination) : phase coherence across the filter bank (punctuated-equilibrium
                      stability; mirror-stack agreement)
  S3 (control)      : SNR / null gate — which signals pass (matched-filter threshold)
  S4 (intelligence) : beamform — consensus across children (robust estimate)
  S5 (identity)     : the transfer-function Gram (typed crystal; frame-invariant)
  algedonic         : out-of-band alarm (clipping / halt / structural-violation tripwire)

  learning          : SignalDescent (measure response → set mirror digits), NOT backprop
  precision         : mirror depth, companded by signal energy
  content           : the KIBC crystal (what the readers detect)
```

This is the same object the control-plane path already reifies as a VSM on an existing
host (`control-plane-path.md`: parent=S1, our tensors=S2/S3, kernel checks=S3*) — here
generalized to a stand-alone tensor, and to `construction-from-spec.md` (the tree as a
coordinate-free BUILD PLAN: codes from Cholesky of the consensus Gram, register map =
build plan). Signal-processing tensors are what you get when the build plan is executed in
DSP + ternary-mirror + SignalDescent terms.

## Where to hold the enthusiasm (λ measure)

- The VSM-node → DSP-stage mapping is **solid for S3 / S4 / S5** — they are literally
  detection / beamforming / transfer-function operations today. It is a **design leap** to
  claim each S1 leaf is a *literal* filter that composes into a working forward pass — a
  hypothesis, not a measurement.
- Whether a fully signal-processing, ternary-mirror, SignalDescent-built tensor **runs a
  language model at quality** is the whole open frontier (same honesty scope as catalog
  C7: structure real, parity unproven).
- **MERA + types is a prediction to test**, not a result. State it as such.

## Open experiments

1. **S3/S4 audit (cheap, retro).** Formally re-express the existing null-gate and
   consensus-Gram code as matched-filter detection and beamforming; confirm the DSP form
   is numerically identical to what `vsm.py` computes today. (If it is, the "already IS"
   claim is proven for S3/S4.)
2. **MERA+types stabilization test.** Build a small multi-resolution filter bank with vs
   without the S5 typed Gram; measure whether types prevent the combinatorial explosion
   (`project-thesis` fractal-attention negative as the control).
3. **One DSP stage end-to-end.** Implement a single reader leaf as a ternary-mirror
   matched filter built by SignalDescent; compare detection ROC vs the float classifier.
4. **Companded filter bank.** Allocate mirror depth across the fractal levels by measured
   signal energy; check quality-vs-storage against uniform precision.

## One-line

**The tree-of-VSM is a coordinate-free, multi-resolution filter bank whose gates are
matched filters, whose consensus is beamforming, and whose identity is a typed transfer
function — a signal-processing tensor already; SignalDescent + ternary mirrors are how you
build one from scratch.**
