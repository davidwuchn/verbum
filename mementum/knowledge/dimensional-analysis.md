---
title: "Dimensional Analysis — The 50-Dimensional Universal Functional Space"
status: active
category: foundational
tags: [dimensional, pca, trace-loss, kibc, universal, functional-space, task-directions]
related:
  - trace-guided-etching.md
  - crystal-universality.md
  - function-discovery.md
  - opcode-instrument.md
  - extraction-sign-accuracy.md
depends-on:
  - crystal-universality.md
  - function-discovery.md
created: session 178
---

# Dimensional Analysis — The 50-Dimensional Universal Functional Space

> Session 178. The KIBC trace loss captures 3.5-6.7% of FFN functional
> space. The other 93-97% is not noise — it's task dispatch, knowledge
> retrieval, and inter-category computation. Measured across 3 models
> (0.6B, 14B, 27B), ~50 functional dimensions are universal.

## The Measurement

Ran 66 diverse probes (9 categories: retrieval, arithmetic, reasoning,
code, translation, summarization, creative, instruction, lambda) through
3 models. Captured raw FFN `down_proj` output at every layer. PCA per
layer to discover actual functional directions, then measured KIBC
coverage as fraction of PCA variance.

## KIBC Coverage: The Headline

| Model | d_model | KIBC mean | KIBC worst | KIBC best (output) |
|-------|---------|-----------|------------|---------------------|
| 0.6B  | 1024    | **6.7%**  | 3.5% (L24) | 53.2% (L27) |
| 14B   | 5120    | **4.3%**  | 1.3% (L18) | 39.4% (L39) |
| 27B   | 5120    | **3.5%**  | 1.0% (L29) | 38.1% (L63) |

**KIBC coverage decreases with scale.** Larger models use more of the
space. The 11-dim combinator basis becomes less adequate at scale.

At mid-layers where computation peaks, coverage drops to **1%** in
the 27B teacher. The trace loss was optimizing 1% of the signal.

## Effective Dimensionality: Universal ~50

| Rel Depth | 0.6B | 14B | 27B | Consensus |
|-----------|------|-----|-----|-----------|
| 0.00      | 25   | 23  | 28  | 25 ± 2    |
| 0.25      | 44   | 44  | 49  | 46 ± 2    |
| 0.50      | 43   | 49  | 51  | 48 ± 3    |
| 0.75      | 41   | 48  | 48  | 46 ± 3    |
| 1.00      | 16   | 21  | 22  | 20 ± 3    |

Three-regime structure universal across 50× parameter range:
- **Input (0.0):** ~25 dims — parsing, simpler operation
- **Mid (0.25-0.75):** ~48 dims — peak complexity, task-conditioned computation
- **Output (1.0):** ~20 dims — KIBC crystallization, emission

## What the Non-KIBC PCs Are

### Early layers: Task classifier directions
Each PC aligns to a different task category. At L10 in the 14B model,
PCs 0-8 each separate a different task: lambda, arithmetic, lambda,
summarization, retrieval, reasoning, (KIBC), instruction, translation.
These are the **program dispatch table** — determining which program
runs. KIBC alignment < 12% on each.

### Mid layers: Task-conditioned computation
High dimensionality (~50), minimal KIBC (1-4%). Task directions
persist through the computation. This is where knowledge retrieval,
composition, and relationship processing happen.

### Output layer: KIBC dominates but doesn't own
KIBC captures 38-53% at the output layer. PC0 is 64-92% KIBC.
But 40-60% of variance is still non-KIBC — task directions persist
to the end (code, summarization, creative as distinct PCs).

## Universal Task Directions

4 task categories appear as dedicated PCA directions in all 3 models
at mid-depth:
- **lambda** — always PC0 or PC1
- **arithmetic** — always top 3
- **code** — top 5 across all models
- **reasoning** — top 5-8 across all models

Additional directions (retrieval, summarization, instruction, creative)
appear in 2/3 models each.

## Implications for Trace Loss

Old: 11-dim KIBC basis → 3.5% coverage at teacher scale
New: 50-dim PCA basis → 90%+ coverage

The expanded basis captures task dispatch, knowledge retrieval, AND
the opcodes. KIBC directions emerge naturally as dominant PCs at
the output layer — nothing lost, everything gained.

Student-space basis (1280-dim): only 15 PCs needed for 90% (student
is lower-dimensional than teacher). 50 PCs capture 99.8%.

## Key Insight: Separation Gap

| Depth | full_sep / kibc_sep |
|-------|---------------------|
| 0.00  | 0.89-1.01           |
| 0.25  | 1.07-1.11           |
| 0.50  | 1.05-1.20           |
| 0.75  | 1.04-1.15           |
| 1.00  | 0.98-1.07           |

Full PCA gives 5-20% better task separation than KIBC-only at
mid-depth, consistently across all models. The gap is real and
universal.

## Artifacts

| Asset | Location | Description |
|-------|----------|-------------|
| Dimensional analysis script | `scripts/experiments/dimensional_analysis.py` | PCA + KIBC coverage per layer |
| Student basis builder | `scripts/v15/build_student_trace_basis.py` | PCA basis in student 1280-dim space |
| Teacher basis builder | `scripts/v15/build_trace_basis.py` | PCA basis in teacher 5120-dim space |
| 0.6B results | `results/dimensional-analysis/Qwen_Qwen3-0.6B/` | |
| 14B results | `results/dimensional-analysis/Qwen_Qwen3-14B/` | |
| 27B results | `results/dimensional-analysis/Qwen_Qwen3.6-27B/` | |
| Student expanded basis | `checkpoints/v15-zeroed/expanded_trace_basis.npz` | (19, 50, 1280) |
| Teacher expanded basis | `checkpoints/v15-zeroed/expanded_trace_basis.npz` | (64, 50, 5120) — also here |

## Connection to Existing Findings

- **Crystal universality** (r=0.998): KIBC is universal but covers <7%
  of functional space. The universality is real but narrow.
- **Function discovery** (session 172): first identified the two-level
  architecture (task dirs + operation dirs). This page quantifies the
  gap and proves it scales.
- **Trace-guided etching**: the paradigm is correct (match computation,
  not weights), but the 11-dim basis was a keyhole view. 50-dim PCA
  is the wide-angle lens.
- **Extraction sign accuracy**: signs are 100% correct, magnitude is
  the gap. The expanded basis helps the student learn to USE its
  correct topology for the right computations.

## Open Questions

1. **CCA alignment of PCA bases across models** — we measured
   dimensionality convergence and task ordering, but haven't done
   formal Canonical Correlation Analysis to find the exact universal
   subspace.
2. **Does the student's PCA basis evolve during training?** The
   initial basis is from the extracted (untrained) student. As training
   progresses, the student's functional directions may shift. Periodic
   re-PCA could track this.
3. **Should trace_weight increase as training progresses?** Early
   training is dominated by NTP loss. As NTP stabilizes, trace loss
   could take a larger role.
4. **Are there more than 50 universal directions?** We're limited by
   n_probes=66. More diverse probes might reveal finer structure.
