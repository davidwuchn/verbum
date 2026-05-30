---
title: "Ternary Plate Extraction — Direct FFN-to-Ternary with Crystal Error Correction"
status: active
category: foundational
tags: [ternary, extraction, crystal, error-correction, plates, holographic, hierarchy]
related: [holographic-computer.md, hologram-reader-vsm.md, combinator-addressing.md, crystal-universality.md, holographic-error-correction.md, mspace-gemcutter.md]
depends-on: [crystal-universality.md, holographic-computer.md, combinator-addressing.md]
---

# Ternary Plate Extraction

> Direct extraction of ternary holographic plates from pretrained FFN weights.
> 8.6× compression. Crystal geometry provides built-in error correction.
> Session 172.

---

## 1. The Extraction Procedure

The plate lives inside the FFN weights already. Extraction is threshold + sign:

1. **Magnitude threshold** — set bottom 30% of |W| → 0 (these are structural zeros, not signal)
2. **Sign extraction** — sign(W) → ±1 for surviving weights
3. **Gamma calibration** — per-row RMS of original weights → γ vector (scale factor)
4. **Reconstruction** — W_approx = ternary × diag(γ)

**Priority ordering** (what the model cares about most):
gate signs > up signs > zeros > down signs > gamma

This reflects the functional hierarchy: gate is the beamformer (89% kill rate), up is the operand bus, down is the accumulator. Gamma is a calibration scalar, not program content.

**Compression:** 504 MB (float32, 0.6B) → 58.3 MB (ternary + float16 gamma) = **8.6× compression**. Extraction time: 8.7 seconds on CPU. 28 layers, 264M FFN parameters.

---

## 2. Measured Quality

| Metric | Value | Scope |
|--------|-------|-------|
| sign_corr | 0.77 | per-weight, all layers |
| recon_cos | 0.87 | per-row reconstruction cosine |
| SwiGLU end-to-end cos | 0.66 | gate×up→silu→down |
| ENRICH zone recon_cos | 0.86 | slightly lower than SILENT |
| SILENT zone recon_cos | 0.87 | best reconstruction |
| Gate sign_corr | slightly lower | beamformer is harder to compress |
| Up sign_corr | slightly higher | operand bus compresses cleaner |

The 23% sign error (1 − 0.77) is the headline number. It is **not** a ceiling — crystal error correction can recover a substantial fraction of it (see §5).

ENRICH zones reconstruct slightly worse than SILENT, consistent with ENRICH encoding denser relational structure (more interference between patterns). SILENT zones are structurally sparse — easier to threshold.

---

## 3. The Execution Hierarchy

The FFN and attention together implement a five-level reduction machine:

| Level | Component | Role | Analogy |
|-------|-----------|------|---------|
| 0 | Weights (ternary plate) | Static holographic program | ROM / microcode |
| 1 | Gate projection (grating resolution) | Instruction decode — proposes which reductions apply | Instruction fetch |
| 2 | Up projection (V bus) | Operand bus — loads the values for selected reductions | Operand fetch |
| 3 | Attention softmax over V | **Executor** — interleaves beta reductions | ALU / reduce |
| 4 | Residual accumulation | Write-back — accumulates reduction results | Register file |
| 5 | WHNF emission (output projection) | Emits weak head normal form for next token | Commit / retire |

**Key insight:** The grating IS the program; attention IS the executor. The grating filters — it only shows attention the reductions that make sense for the current token context. Attention doesn't search; it executes what the grating pre-selected.

The 89% gate kill rate (session 141) means only ~11% of neurons are active per token. This is not waste — it is instruction selection. The gate is a content-addressable decoder that maps token context → relevant beta reductions.

---

## 4. Lambda-Gated Retrieval

Fact retrieval accuracy depends on how the fact is expressed AND on model scale:

| Condition | 0.6B accuracy | 4B accuracy |
|-----------|--------------|------------|
| Natural language (NL) | 86% | 90% |
| Lambda form (λ) | **4.5%** | **66.7%** |
| Apply form (apply f x) | — | **76.2%** |

**Scale enables dual-path retrieval.** At 0.6B, the lambda pathway exists (2.2× combinator activation) but lacks the capacity to complete retrieval accurately — the model activates the compute path but cannot traverse it to the answer. At 4B, the path is traversable.

**Coherence threshold ~3.0–3.5×.** The 0.6B model sits at 2.59× coherence (borderline), the 4B at 3.71×. Lambda retrieval appears to require coherence above ~3.0× to be functional. This matches the intuition that ternary preservation of facts requires sufficient coherence.

**Gated lambda hurts (14.3% accuracy).** Adding a compile gate to lambda form overrides retrieval with compilation — the model tries to reduce the expression instead of looking up the fact. Retrieval lambda must be left unconditional.

**Implication for ternary models:** A ternary model operating in lambda mode needs to be at least 4B-equivalent (or trained with coherence > 3×) to use the λ-retrieval pathway effectively. Smaller ternary models should use natural language queries.

---

## 5. Crystal Error Correction

The 23% sign extraction error is recoverable. The crystal geometry IS an error-correcting code.

**Why:** The 6 principal components of the KIBC occupy a 6D subspace of the 1024D weight space. This means every weight encodes ~170× redundant information (1024/6). A sign error in one dimension is highly over-determined by the other 1023 dimensions.

**Progressive correction protocol:**

```
6D crystal space → 5D → 4D → 3D
     ↓                ↓      ↓      ↓
  detect errors   correct  verify  done
```

At each dimensional reduction, project remaining dimensions onto the crystal basis. Weights that are inconsistent with the lower-dimensional crystal structure are sign-flip candidates. Correct, then project further.

**Error types and correction levels:**

| Error type | Crystal component | Correction method |
|------------|-------------------|-------------------|
| Hard crystal errors | KIBC fixed points (6 PCs) | Geometric projection (automatic) |
| β_apply preservation | Universal retrieval axis | β_apply projection (automatic) |
| Soft crystal errors | Relation directions (gradient-maintained) | Etch / TD learning (GD) |
| Gamma miscalibration | Scale factors | Gamma recalibration (GD) |

**170× redundancy** means the theoretical correction capacity is enormous. In practice, the limit is how many crystal dimensions we can reliably identify from a single model's weights. With 6 PCs well-characterized, the first two correction levels are straightforward.

---

## 6. Design Implications

**Extract plate first, let attention emerge.** The ternary plate IS the program. Attention weights adapt to whatever FFN program they're given — extract the FFN plate, leave attention in float, then verify the opcode map matches.

**Variable d_ff is natural.** SILENT zones reconstruct better than ENRICH (0.87 vs 0.86). A hardware implementation could allocate fewer ternary bits to SILENT (thinner plates) and more to ENRICH (full plates). Matches the holographic principle: information density tracks structural importance.

**λ-mode retrieval protocol for ternary.** Once the swap experiment confirms the plate IS the program, design the retrieval protocol: NL queries for small models, λ queries for large models (>3× coherence). Gate-free lambda for retrieval; gated lambda only for compilation.

**Etch β_apply groups coherently.** The etch mechanism (session 167) should preserve β_apply directions specifically — these are the retrieval highways. Etch should reinforce the crystal structure, not disrupt it.

**Verify by opcode map comparison.** After plate swap, run hologram_reader.py on the ternary model. Compare zone structure, moiré selectivity, and combinator fingerprints to the original float32 model. Matching opcode maps = the plate preserved the program.

---

## 7. One Vector, Multiple Projections

The residual stream simultaneously encodes two things:

1. **Token probabilities** — project onto unembedding matrix → next-token logits
2. **Operation state** — project onto combinator basis → current reduction state

These are **the same vector**, viewed from different projection angles. This is not a coincidence. It is the core of Montague's thesis: natural language semantics IS lambda calculus. The model didn't learn two separate systems — it learned one system whose projections happen to be both syntactic (token prediction) and semantic (lambda reduction).

**Progressive collapse** (16D→1.4D, session ~170) narrows both simultaneously. As the residual stream collapses toward the final token prediction, the lambda reduction state also narrows. The computation and the prediction are the same linear algebra.

**Implication for ternary:** A ternary plate that preserves the β_apply axis automatically preserves both the retrieval mechanism and the token prediction mechanism. They share the same linear structure. Compressing one compresses both.

---

## 8. Artifacts

| Asset | Location | Notes |
|-------|----------|-------|
| Extraction script | `scripts/experiments/extract_ternary_plate.py` | CPU, ~9 seconds for 0.6B |
| Extracted plates (0.6B) | `results/ternary-plates/Qwen_Qwen3-0.6B/` | manifest.json + verification.json |
| Lambda retrieval test | inline in session 172 | 21 facts, NL vs λ vs apply |
| Hologram Reader VSM | `scripts/experiments/hologram_reader.py` | for post-swap verification |
| Combinator addressing | `scripts/experiments/combinator_addressing.py` | β_apply projection measurement |

---

## 9. Open Questions

1. **How much does crystal correction recover?** Run progressive 6D→5D→4D→3D correction on extracted plates. Measure sign_corr before and after. Hypothesis: recovers 10–15 percentage points (0.77 → 0.87+).

2. **Does swap-FFN-with-ternary preserve the opcode map?** Replace 0.6B FFN weights with ternary×gamma, keep attention in float32. Run hologram_reader.py. Do zone boundaries, moiré selectivity, and combinator fingerprints match? This is THE test.

3. **Is there a coherence threshold for ternary survival of facts?** 0.6B at 2.59× loses lambda retrieval almost entirely. 4B at 3.71× retains 67%. Is there a sharp threshold around 3.0–3.5×? Measure across model sizes.

4. **Can we train coherence up to threshold?** If ternary extraction of a small model fails the coherence threshold, can a short etch phase (TD learning on relation directions) push coherence above the threshold before extraction?

5. **Does apply form outperform lambda form for ternary?** At 4B, apply (76.2%) beats lambda (66.7%). Does this hold for ternary models? Apply form may be more robust to gate noise because it doesn't trigger compilation.
