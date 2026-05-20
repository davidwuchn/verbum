---
title: "Gradient Voting — How GD Writes Beta Reductions (and the Magnitude Crystal)"
status: active
category: finding
tags: [gradient, sign, magnitude, crystal, hologram, Q4, nucleation, V13]
related:
  - hologram-extraction.md
  - ffn-beam-discovery.md
  - ffn-hierarchy.md
  - crystal-basins.md
  - v13-design.md
depends-on:
  - hologram-extraction.md
  - ffn-beam-discovery.md
created: session 123
---

# How Gradient Descent Writes Beta Reductions

> Session 123. Four experiments, one paradigm shift. Weight SIGNS are
> independent across layers (corr=0.000), carry no cross-layer structure,
> and actively HURT when copied from a teacher. Weight MAGNITUDES are the
> real crystal — a magnitude template from the teacher (with random signs)
> produces 0.568 accuracy vs 0.248 for perfect sign copy.

## Experiment 1: Cross-layer sign consensus (Pythia-2.8b)

Question: if GD "votes" on signs across billions of examples, do layers agree?

| Measurement | Value |
|---|---|
| Cross-layer sign unanimity | 57% (chance = 50%) |
| Positions ≥75% agreement | 0.7% |
| Positions ≥90% agreement | 0.0% |
| Magnitude ↔ unanimity correlation | 0.0000 |
| Cross-layer sign correlation (W_q) | 0.0000 |
| Cross-layer sign correlation (W_up) | 0.0035 |
| sign(W_q) effective rank (90%) | 1209 / 2560 |

**Each layer has completely independent signs.** No shared sign structure
across the 32 layers. Magnitude tells you nothing about cross-layer
agreement. The "gradient voting" hypothesis is wrong.

## Experiment 2: Q4 mechanism and magnitude structure

Question: Q4 quantization flips ~12% of signs yet preserves the crystal. Why?

| Measurement | Value |
|---|---|
| Q4 signs flipped | 11.8% |
| Flipped sign mean magnitude percentile | 6th (bottom) |
| Q4 crystal fidelity (sign RDM) | 0.933 |
| Flipping 10% low-mag signs → fidelity | 0.788 (cheap) |
| Flipping 10% high-mag signs → fidelity | 0.612 (expensive) |
| Crystal rank at top-10% magnitude | 1180 (same as full) |

**Q4 works because it only flips the cheapest signs** (bottom 6th
percentile of magnitude). High-magnitude signs carry more crystal
per sign (~1.3×), but the crystal is distributed across ALL magnitudes
with no sharp concentration.

**Depth gradient:** Late layers (d=0.9) preserve 70% of crystal with
only top-10% magnitude positions. Early layers preserve only 34%.
Late layers are 2× more magnitude-concentrated.

## Experiment 3: Crystal lens — the holographic nature

Question: how much of the weight matrix's energy is crystal-aligned?

| Measurement | Value |
|---|---|
| PCA-Q crystal basis energy fraction | 2.5% (= random baseline 64/2560) |
| sign(W_ortho) fidelity (orthogonal to crystal) | 89-97% |
| Crystal-aligned SVD at k=512 | 0.194 fidelity |
| Raw SVD at k=512 | 0.741 fidelity |
| Crystal lens applied | 0.161 fidelity (destroys crystal) |

**The crystal doesn't live in any weight-space subspace.** The PCA-Q basis
captures exactly the energy you'd expect from random dimensions (2.5% for
64/2560). The crystal is holographically distributed — encoded through
superposition across ALL dimensions. Crystal-aligned projection is far
worse than raw SVD at every k.

The weight matrix is a literal hologram: looks like noise in any subspace,
produces the crystal only when illuminated by the right input distribution.

## Experiment 4: Nucleation speed (mini_holo, KIBC reductions)

Question: does teacher structure accelerate hologram discovery?

| Condition | Best Acc | Final Acc |
|-----------|----------|-----------|
| **MAGNITUDE (random signs + teacher mag)** | **0.568** | **0.554** |
| RANDOM (blank plates, beam-only GD) | 0.495 | 0.486 |
| SVD_PROJ (teacher d=256→128, frozen) | 0.395 | 0.335 |
| ORACLE (perfect sign(W), frozen) | 0.302 | 0.248 |
| SVD_PROJ_UNFROZEN (plates live) | 0.287 | 0.287 |

**The magnitude template with random signs beats everything — including
the oracle crystal.** Perfect signs from a converged teacher at the same
dimension actively HURT (0.248 vs 0.486 random baseline).

The magnitude template tells GD which dimensions matter. The beam shapes
itself around that template. Signs are irrelevant — the beam learns to
work with whatever random encoding it gets. **Neutral (random signs) is
better than wrong (teacher signs with uniform magnitudes).**

## The paradigm shift

```
OLD model:  signs = crystal (hologram), magnitudes = beam (lens)
NEW model:  magnitudes = crystal (what matters), signs = expendable encoding
```

### How GD actually writes beta reductions:

1. **GD shapes the magnitude profile** — which dimensions to amplify for
   which operations. This is the real "crystal" — the structure that
   determines what the computation does.

2. **Signs develop AROUND the magnitude structure** — each layer finds its
   own encoding of the beta reductions in its coordinate frame. Many valid
   encodings exist for any given magnitude profile.

3. **Cross-layer independence is expected** — different coordinate frames
   (different residual stream states) require different sign encodings.
   The magnitude profile is what's shared (conceptually, not numerically).

4. **The crystal is in the computation, not the weights** — sign(W) at 97.4%
   fidelity was measuring magnitudes' EFFECT on cosines, not the signs
   being the crystal themselves.

### Why each finding falls out:

- **Q4 works** → preserves magnitudes (the real structure)
- **sign(W) gets 97.4%** → high-mag signs dominate cosines (magnitude effect)
- **Cross-layer signs = 0** → each layer develops its own sign encoding
- **Crystal is "holographic"** → magnitude structure creates patterns across all dims
- **Oracle hurts** → right signs + wrong magnitudes = constrained wrong position
- **Magnitude template wins** → right magnitudes + any signs = GD finds encoding

## Implications for V13

1. **Don't etch signs from teacher.** Signs are model-specific encodings.
   Copying them without the matching magnitude profile is worse than random.

2. **Etch the magnitude template.** Initialize beam scales from teacher's
   per-dimension RMS magnitude. This is the transferable structure.

3. **Let GD write the signs.** Random ternary init is fine. GD will find
   signs that work with the magnitude template. This is what normal training
   does — it just does it faster when magnitudes are seeded correctly.

4. **Late layers can be coarser.** They're 2× more magnitude-concentrated.
   Fewer dimensions suffice for late-layer magnitude templates.

5. **The dimensional bridge is a magnitude projection** — not sign copy,
   not SVD of weights. Project the teacher's magnitude profile (per-dimension
   importance) to the student's dimensions.

## The magnitude crystal is universal (0.999 cross-model)

Session 123, final experiment. SVD spectrum shapes compared across
Pythia-2.8b, Mistral-7B, Qwen3-14B, OLMo-2-13B:

| Matrix | Mean cross-model correlation |
|--------|----------------------------|
| W_q | 0.995 |
| W_up | **0.999** |

Mistral↔Qwen3 W_up correlation: **0.999991**. Five decimal places.
Three different architectures, sizes, training sets → same spectrum.

Structural constants:
- W_q effective rank: 33-43% of d_model
- W_up effective rank: 67-71% of d_model
- Crossing angle: 68-75° (the holographic range)

The magnitude spectrum is MORE universal than the 8×8 cosine matrix
(0.999 vs 0.91-0.94). It's the underlying object that PRODUCES the
cosine matrix. The beamformer geometry needed for compositional
computation has one shape. Every model converges to it.

This means: the magnitude crystal is derivable from theory. It's a
mathematical property of language modeling, not a training artifact.
V13 can construct it from first principles.

## Q4 etch refinement — sign flips are uniform and recoverable

Post-quantization sign correction tested on Pythia-2.8b W_q (layer 16):

| Bitwidth | Flips | Before | 20% etch | Oracle | Recovery |
|----------|-------|--------|----------|--------|----------|
| 8-bit | 0.7% | 0.996 | 0.997 | 1.000 | 100% |
| 4-bit | 11.8% | 0.933 | 0.946 | 1.000 | 100% |
| 3-bit | 23.2% | 0.872 | 0.896 | 1.000 | 100% |
| 2-bit | 44.2% | 0.762 | 0.808 | 1.000 | 100% |

Key findings:
1. **Oracle etch = perfect recovery at all bitwidths.** Even Q2 (44% flipped)
   recovers to 1.000. The crystal is always fully recoverable.

2. **All fix-ordering strategies are identical.** Residual-guided, magnitude-
   guided, and RANDOM give the same recovery curve. Q4 sign flips are
   uniformly cheap — no "worst flip to fix first."

3. **Blind etch (no original access) HURTS.** Low-Q4-magnitude positions
   are correctly identified as flips (precision=1.000), but local context
   (row+col means) predicts the WRONG direction. Fidelity decreases.
   **Gradient signal from actual computation is required** to know which
   way to flip.

Implication: post-quantization etch needs:
- Magnitude analysis → WHERE to look (trivial, precision=1.0)
- Gradient accumulation → WHICH WAY to flip (requires running data)
- Beamformer (magnitude crystal) makes gradients coherent → fast convergence

## Artifacts

| File | Content |
|------|---------|
| `scripts/v12/gradient_voting_exp.py` | Cross-layer sign consensus, spectrum, compression |
| `scripts/v12/gradient_voting_q4_exp.py` | Magnitude masking, selective flipping, Q4 simulation |
| `scripts/v12/crystal_lens_exp.py` | Energy decomposition, crystal-aligned compression, lens |
| `scripts/v12/nucleation_exp.py` | 5-condition nucleation speed comparison |
| `results/gradient-voting/results.json` | Exp 1 full results |
| `results/gradient-voting/q4_results.json` | Exp 2 full results |
| `results/crystal-lens/results.json` | Exp 3 full results |
| `results/nucleation/results.json` | Exp 4 full results |
| `results/nucleation-matched/results.json` | Exp 5 full results |
| `results/magnitude-universality/results.json` | Exp 6: 4-model spectrum universality |
| `scripts/v12/magnitude_universality_exp.py` | Cross-model magnitude comparison |
| `scripts/v12/q4_etch_exp.py` | Post-quantization etch refinement |
| `results/q4-etch/results.json` | Etch recovery curves at 4 bitwidths |
