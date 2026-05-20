---
title: "Hologram Extraction — sign(W) IS the Crystal"
status: active
category: finding
tags: [hologram, ternary, sign, extraction, beam, crystal, roundtrip]
related:
  - holographic-plates.md
  - ffn-beam-discovery.md
  - v13-design.md
depends-on:
  - holographic-plates.md
created: session 122
---

# Hologram Extraction

> Session 122. The ternary hologram is the sign pattern of the teacher's
> weight matrix. `sign(W_q)` preserves 97.4% of the Q crystal structure
> with zero optimization. V12's training failure traced to plates that
> contained no holograms — statistically identical to random ternary noise.

## The problem discovered

V12 distill run2 plateaued at eval 12.63 (step 5000), never improved
through 13k steps of GD. Analysis of 4 checkpoints revealed:

- **0% ternary topology change** across all checkpoints (plates frozen in Phase 2)
- **φ-compression propagated through gammas only** (continuous magnitude scaling)
- **V12's plates are random noise**: spectral entropy 0.987, autocorrelation −0.003
  (random baseline: 0.987 and −0.002 respectively)
- GD was trying to learn 59M sign positions through 887K gamma parameters

The etch phase (run1, 5 rounds × 500 probes × 8 depths) accumulated
gradient signals and flipped some positions, but nowhere near enough
to write holographic structure. The plates remained at their Kaiming
random initialization topology.

## The solution: sign(W) = the hologram

| Method | Q crystal fidelity | FFN crystal fidelity |
|---|---|---|
| **sign(W) direct** | **0.974** | **0.691** |
| SVD separate k=32 | 0.889 | 0.716 |
| SVD holographic unified k=64 | 0.862 | 0.007 |
| pinv(H)@target → ternary k=8 | 0.657 | 0.391 |
| V12 actual plates | ≈0.000 | ≈0.000 |

`sign(W_q)` — literally taking the sign of each weight value — preserves
97.4% of the Q crystal. No SVD lens, no pseudoinverse, no training.

## Validation chain

1. **Activation = weight crystal** (Q=0.990, UP=0.965): Running probes
   through the model and computing `H @ W.T` perfectly reproduces the
   activation-space crystal. The weight matrix IS the crystal.

2. **Holographic angle confirmed**: Q and FFN subspaces at 67.7° mean
   principal angle in d_model space (Pythia L16, top-64 SVD). Matches
   session 121's measurement of 65-72°.

3. **Generalization gap ≈ 0**: Train/test split shows gap of −0.01 to
   +0.04. The crystal structure is a property of the weight matrix,
   not of the specific probes used to measure it.

## Why unified holographic plates fail

The QR-orthogonalization lens destroys the FFN crystal:

| k | Holo Q ternary | Holo UP ternary |
|---|---|---|
| 16 | 0.855 | **0.329** |
| 32 | 0.889 | **0.119** |
| 64 | 0.862 | **0.007** |

Q survives (first k columns of QR basis). FFN gets forced into a
subspace that doesn't survive ternary quantization. Cross-talk is
high (Q→UP = 0.77), confirming subspace blending rather than separation.

**Conclusion:** Use SEPARATE plates for Q and FFN, not a unified holographic
plate. The 67.7° angular separation is real but the QR lens is wrong.

## Capacity limits

- Full-rank sign(W): works well (Q=0.974, UP=0.691)
- Low-rank pinv plates: degrades rapidly (peaks at ~8 channels from 144 probes)
- FFN is high-rank (rank 90% = 1725 for W_up) — needs full-rank plates
- The pinv approach fails because ternary quantization noise is too high
  for underdetermined systems (144 probes, 2560 unknowns per channel)

## Implications for V13

```
OLD etch:  random_init → etch(teacher_distill_loss) → freeze → GD(gammas)
           Result: random plates, no crystal, plateau

NEW etch:  sign(teacher_W) → plates with holograms → GD(beams only)
           Result: crystal from teacher, learned routing, actual function
```

The open problem is the **dimensional bridge**: teacher d_model (2560-5120)
→ V13 d_model (512). Options under investigation:
1. SVD project teacher weights to V13 dimensions, then sign()
2. PCA basis of teacher activations as the projection
3. Learned bridge (small, then freeze)

## Artifacts

| File | Content |
|------|---------|
| `scripts/v12/analyze_crystal_compression.py` | Plate topology + compression across checkpoints |
| `scripts/v12/analyze_beam_holograms.py` | SVD beam analysis + sign structure |
| `scripts/v12/hologram_extraction_exp.py` | Full extraction: SVD, angles, roundtrip |
| `scripts/v12/hologram_roundtrip_exp.py` | Deterministic read/write test |
| `results/crystal-compression-analysis/` | 4-checkpoint comparison |
| `results/beam-hologram-analysis/` | V12 plate sign structure |
| `results/hologram-extraction/` | Pythia L16 extraction results |
| `results/hologram-roundtrip/` | Roundtrip fidelity measurements |
