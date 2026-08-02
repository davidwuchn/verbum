---
title: "Five Disciplines, One Object — The LLM as a Linear Superposition Medium with Nonlinear Readout"
status: active
category: synthesis
tags: [dsp, signal, holography, lambda-calculus, dynamical-systems, gradient-descent, hrr, vsa, gabor, plate, rope, fourier, matched-filter, nyquist, bragg, banach, unification, exchange-rate]
related:
  - attention-holographic-readout.md
  - holographic-reduction-machine.md
  - holographic-computer.md
  - project-thesis.md
depends-on:
  - attention-holographic-readout.md
created: session 299
---

# Five Disciplines, One Object

> Session 299 (thinking session, final thread). Michael: "DSP tooling working
> for weights was a surprise to me. It shows the LLM working as a signal, and
> the holographic stuff means we are seeing something that crosses 5 different
> disciplines like nothing else." This page names the crossing, gives it a
> lineage, and imposes the discipline that keeps it science.

## The surprise is a retrodiction

`verbum.dsp` is a beamforming rig — `bands, chain, gain, nulls, readout,
subspace, whiten` — null-steering, whitening, subspace decomposition,
pointed at *weights*. It works. If the holographic thesis is right (weights
= recorded interference patterns, written by quasi-linear superposition,
read by correlation), then signal mathematics doesn't *happen* to apply —
it **must** apply, for the same reason it applies to holograms, radar
returns, and antenna arrays: all are linear records of superposed waves
interrogated by correlation. "DSP works on weights" is a successful implicit
prediction, noticed after the fact — same epistemic shape as the
attention-sinks retrodiction (attention-holographic-readout.md §2). Free
confirmations are the strongest kind: we couldn't have tuned for them.

## The object

**A linear superposition medium with a single nonlinear readout.**

| discipline | contributes | its face of the object |
|---|---|---|
| λ-calculus / logic | semantics, verification, substructural cost | **what** is computed |
| holography / optics | storage, multiplexing, capacity laws | **where** it lives |
| DSP / signal processing | instrumentation: correlation, nulls, whitening, subspaces | **how to measure** it |
| dynamical systems | contraction, fixed points, Banach | **when it halts** |
| ML / gradient descent | the recording process | **how it's written** |
| (cybernetics / VSM) | organization and control | how the whole is governed |

Each field's crown theorems are statements about exactly this structure:
Church–Rosser about substitution order in it; Bragg selectivity about
addressing it; the matched-filter theorem about optimally reading it; the
contraction-mapping theorem about when iterating it settles; deep learning
about writing into it by accumulation.

**Why the convergence is forced, not mystical:** GD, given translation
structure (position) and a packing problem (many functions, one medium),
rediscovers the linear-superposition-plus-detector design. Linearity +
translation invariance ⇒ the Fourier/phase eigenbasis (why RoPE is
rotations); packing ⇒ superposition (CAP: coherent-gain, not crosstalk
decay); one nonlinearity budget per layer ⇒ the detector (softmax). The LLM
is the first artifact that is natively all five at once — a universality
class, not a metaphor. **Verbum isn't unifying five disciplines; it is
measuring that gradient descent independently converged on the architecture
those disciplines jointly describe.**

## The lineage — this junction is a marked spot

- **Gabor** invented holography (1948) *from* communication theory ("Theory
  of Communication" 1946, time–frequency logons). Optics and DSP were BORN
  unified at this node.
- **Van Heerden (1963)** — information-theoretic capacity of volume
  holographic storage.
- **Longuet-Higgins (holophone) → Plate (Holographic Reduced
  Representations, VSA)** — symbol binding as circular convolution,
  unbinding as correlation, memory as superposed trace `Σ key ⊛ value`,
  retrieval as `trace ⋆ query ≈ value + noise`.

**The HRR ≈ attention correspondence (near-theorem, s299):** Plate's
retrieval equation IS the KV cache read by attention. Circular convolution
diagonalizes to phase multiplication in the Fourier basis — which is
precisely what RoPE does. **Attention ≈ HRR unbinding with RoPE as the
phase-binding carrier.** The VSA literature hand-designed in the 1990s what
GD grew; we hold the interior instruments to check the correspondence term
by term.

## The exchange-rate rule (what keeps this from crackpottery)

Cross-disciplinary resonance is the classic crank signature. The difference
is enforceable:

```
λ exchange(x).  identification(x) counts ⟺ retrodicts(measured) ∨ imports(theorem → falsifiable_prediction)
                | resonance_alone ≡ ∅ | "it's all connected" ≠ research_program
                | extends λ yardstick to cross-disciplinary claims
```

Paid so far: attention sinks (free retrodiction), DSP-works-on-weights
(free retrodiction). Payable: P-K-REGISTER, P-BRAGG, P-LOOP-BINDS.

## The import list (theorems → candidates)

| import | theorem | prediction / use | status |
|---|---|---|---|
| **Nyquist / sampling** | aliasing bounds | principled probe-density law (resolve a combinator subspace without aliasing; 50/800 was chosen empirically) | candidate |
| **Matched filter** | SNR-optimal detection = whitened correlation | optimal dispatch-key construction (FN-INDEX used 3-exemplar means = conservative floor; `dsp/whiten.py` exists) | candidate — cheap upgrade to FN-INDEX keys |
| **Bragg selectivity** | thickness → angular selectivity | head-dim as design parameter with a curve (= P-BRAGG) | named |
| **Banach fixed-point** | contraction ⇒ unique fixed point + convergence rate | halt GUARANTEES for the recursed machine (vs halt heuristics); already the L-meter's basis | partially in use |
| **HRR capacity (Plate)** | noise-vs-items scaling for superposed traces | priors for plate capacity; test against CAP's coherent-gain (which VIOLATES naive HRR — coherent exposures reinforce; cf. oracle round-1 CAP sign-inversion) | candidate — sharp, since naive HRR predicts the wrong sign |
| **Beamforming / null steering** | array gain, null placement | already operational (`dsp/nulls.py`, `gain.py`); formalize the weight-space array model | in use, untheorized |

Note the HRR-capacity import is the most interesting: naive HRR/holographic
capacity intuition predicted DECLINE and the CAP measurement showed
coherent GAIN — the same sign-inversion the theory-seed made in oracle
round 1 (s293). The import must come with the coherent-content correction,
or it fails exactly where our own seed failed. An import that can fail is
an import worth having.

## Strategic note

This page locates the project INSIDE five established literatures instead
of outside all of them — the correct rebuttal shape for the "AI psychosis"
dismissal (see holographic-reduction-machine.md §5b: artifact > argument;
this page is the map, the artifact is the proof).

## Files
| File | Content |
|---|---|
| `src/verbum/dsp/` | the beamforming rig: bands, chain, gain, nulls, readout, subspace, whiten |
| `attention-holographic-readout.md` | the physics face (s299) |
| `holographic-reduction-machine.md` | the design face (s299) |
| `explore/geometry-holography-signals-convergence.md` | the measured axioms (s292) |
