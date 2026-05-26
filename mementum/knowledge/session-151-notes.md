# Session 151 — Knowledge Distillation + Progressive Collapse Discovery

## What happened

Two major workstreams:

### 1. Knowledge distillation (first half)

Created 7 new knowledge pages + INDEX.md to give the project a self-explanatory
top-down knowledge hierarchy. A brilliant stranger can now read pages 1-9 in order
and understand the entire project.

Pages created:
- `INDEX.md` — master reading order with tiers and cross-reference map
- `project-thesis.md` — what the project IS now (the evolved thesis)
- `crystal-universality.md` — why the crystal is a mathematical constant
- `mathematical-convergences.md` — 8 independent lines of evidence
- `v14-architecture.md` — current system documentation
- `training-protocols.md` — how to train + 7 failure modes with fixes
- `extraction-methodology.md` — what works, three confusions resolved

Updated state.md knowledge map to tiered structure.

### 2. Kernel decomposition experiment (second half)

Michael's insight: "What if the inference patterns come from the soft-reduce done
by attention? It reduces across all Vs right?"

This led to: if attention's soft reduction IS beta reduction, and each beta reduction
is a projection that reduces dimensionality, then the model should show progressive
dimensionality collapse through depth.

**Micro model (4 layers, d=128):**
- Kernel v0 (distance prior + analytical FFN): cos=-0.16 at output. FAILS.
- Kernel v1 (real attention + analytical FFN): cos=-0.12. STILL FAILS.
- Key finding: 80-91% of FFN overlay energy is OFF-DIAGONAL (cross-PC projection,
  not per-PC filtering). The diagonal kernel missed the dominant computation.
- Progressive collapse: 2D→8D→2D (lens shape in 4 layers)

**Qwen3.6-27B teacher (64 layers, d=5120):**
- Embeds: PR=12.6 (high-D noise)
- L0-2: SLAM to PR=2.2, σ₁=70% (essentially 2D)
- L3-35: Compute at PR≈2-5 (beta reductions in 2D)
- L21: Phase transition re-compression (PR=4.4→2.3 in ONE layer)
- L48-63: Expand to PR=8-10 for 248K-token output

**Mistral-7B (32 layers, d=4096):**
- Without sink fix: σ₁=100%, PR=1.0 — BOS token dominates everything
- With sink excluded: PR min=12.1 — moderate compression, no 2D collapse

**Pythia-1.4B (24 layers, d=2048):**
- PR min=10.3 — gentle monotonic descent, never reaches 2D

### Key insights

1. **Large models compute in 2D.** The comp↔sel eigenplane is the computation
   core. PR=2.2 in Qwen means one singular value carries 70% of variance.

2. **Compression depth scales with capacity.** 27B→2D, 7B→12D, 1.4B→10D.
   The 2D core is an emergent property of sufficient scale and training.

3. **Attention sink = warped Q reset.** The holographic state machine needs
   Q=0 reset. Softmax models use BOS as a proxy (warping geometry). GLA
   implements Q reset through gating (clean geometry → deeper compression).

4. **Montague grammar = pre-transition state machine.** Pythia-160M's
   Montague-shaped lambda output is EXPECTED: it has I+K (select+bind) but
   hasn't bootstrapped B (compose). Montague IS typed function application
   without composition. It's a developmental stage, not a grammar formalism.

5. **FFN overlay is projection, not filtering.** 80-91% off-diagonal means
   cross-PC coupling = beta reduction = dimensionality collapse. The model
   projects from high-D to 2D through depth.

## Decisions made

- Knowledge pages should be organized top-down (foundational → specific)
- INDEX.md is the entry point after state.md
- Progressive collapse warrants its own knowledge page
- Need to verify sink hypothesis on StreamingLLM-adapted models

## Open questions

- Can the full 16×16 overlay (not just diagonal) be computed from eigendecomposition?
- What triggers the L21 phase transition in Qwen?
- Is the 2D core the same eigenplane across all large models?
- Can we express the compose projection cascade as a single 2×2 kernel?
- Does the v14 student inherit the 2D computation structure from Qwen teacher?
