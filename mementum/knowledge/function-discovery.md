---
title: "Function Discovery — Two-Level Program Architecture in Moiré Space"
status: active
category: foundational
tags: [function, discovery, moiré, pca, task, operation, program, classification, combinator]
related: [holographic-computer.md, combinator-addressing.md, hologram-reader-vsm.md, crystal-universality.md, ternary-plate-extraction.md]
depends-on: [holographic-computer.md, combinator-addressing.md]
---

# Function Discovery — Two-Level Program Architecture in Moiré Space

> **Core finding (session 172):** LLMs implement a two-level program architecture. Early layers (SILENT zone) classify the *type* of task. Late layers (COMMIT zone) execute *combinators*. These are orthogonal subspaces — the combinator basis is blind to the early-layer task classifier.

---

## 1. The Measurement Bias

Our 12-dim combinator fingerprints (K, I, B, C, W, Y, S, β_apply, β_K, β_I, β_compose, β_self) were constructed from explicit lambda expressions. They are tuned to capture the structure of late-layer *operation* directions — the COMMIT zone where KIBC combinators crystallize.

This created a systematic blind spot: **combinator projections cannot see early-layer task classification**, because task directions live in subspaces orthogonal to the combinator basis.

The symptom was visible in the function mapper results: running combinator projections on both 0.6B and 14B models yielded only 3 apparent programs (lambda, arithmetic, everything-else), with cross-category cosine similarity of 0.995–1.000. This appeared to say "all NL tasks are identical." It was correct but incomplete — the projection discards exactly the dimensions where task separation lives.

Full d_ff PCA reveals the complete picture.

---

## 2. Two-Level Program Architecture

### Level 1: TASK DIRECTIONS (SILENT zone, early layers)

- **Separation:** 4.76× at L05 (inter-cluster / intra-cluster distance ratio, full d_ff PCA)
- **PC0:** compute mode vs language mode
- **PC1:** recursion vs reduction
- **PC2:** structured syntax vs natural-language logic
- **Clusters (k-means, k=5):** lambda, arithmetic, code, reasoning, general NL — each distinct
- **Combinator alignment:** |projection| < 0.25 (combinators not yet crystallized at this depth)

The SILENT zone gratings classify *what kind of program is being run* before any computation begins. Tool use, summarization, code generation, lambda evaluation, and arithmetic are all detectably distinct at L05.

### Level 2: OPERATION DIRECTIONS (COMMIT zone, late layers)

- **Separation:** 1.49× (task categories converge — different tasks use the same opcodes)
- **PC0:** generative vs deterministic mode (35.2% of variance)
- **Combinator alignment strong:** PC0 = B/C/W vs K/β_K/β_I; PC1 = Y vs D/B
- **Combinator alignment:** |projection| up to 0.82

The COMMIT zone gratings execute *which combinators are applied*. Task categories converge here because lambda, arithmetic, and code all reduce via the same combinator set — the *what* has been resolved, only the *how* remains.

---

## 3. The Progressive Transformation

Gratings transform task→operation through depth. This is not a discrete switch — it is a continuous transformation visible in the separation ratio at each zone boundary:

| Depth | Zone | Separation | Interpretation |
|-------|------|-----------|----------------|
| L05 | SILENT | **4.76×** | Peak task classification |
| ~L08 | SILENT→ENRICH | 3.92× | Task signal dominant, operation emerging |
| ~L12 | ENRICH | 2.53× | Mixed — knowledge loading begins |
| ~L18 | ENRICH | 3.26× | Knowledge retrieval amplifies task signal |
| ~L22 | ENRICH→SUPPRESS | 3.33× | Task still detectable |
| ~L26 | SUPPRESS | 1.62× | Compression toward opcode basis |
| L28+ | COMMIT | **1.49×** | Operation directions dominate |

Early gratings **classify** input type. Late gratings **execute** computation. The ENRICH zone is where task-conditioned knowledge retrieval amplifies the task signal before it is compressed into opcodes.

---

## 4. Combinator Alignment Through Depth

The KIBC basis does not exist a priori — it *emerges* through depth:

- **Early layers:** |projection onto combinator basis| < 0.25. The activation geometry is dominated by task-type directions. Combinator fingerprints capture negligible variance.
- **Transition (SUPPRESS zone):** Alignment increases as task directions are compressed and the operation basis crystallizes.
- **Late layers:** |projection| up to 0.82. Combinator directions dominate. The crystal is formed.

This means the combinator fingerprinting approach (hologram reader, combinator addressing) is correctly targeted at late-layer structure — it just does not capture the equally important early-layer task classifier.

---

## 5. What the Function Mapper Showed First

Running `function_mapper.py` (12-dim combinator projection) on 0.6B and 14B:

- Both models: only 3 apparent programs — lambda, arithmetic, everything-else
- Cross-category cosine: 0.995–1.000 (near-identical directions)
- Conclusion at the time: "NL tasks are functionally indistinguishable"

This was a **measurement artifact**, not a property of the model. The 12-dim combinator projection is a late-layer instrument applied to full-depth activations. It averages over all layers, where the dominant variance is operation-direction (late, strong) rather than task-direction (early, weaker in the combinator subspace but strong in d_ff PCA).

The function mapper result is *correct for what it measures*: at the combinator level, all NL text reduces to the same small opcode set. The function discovery result adds the missing level: at the task level, those NL tasks are 4.76× separated in early-layer moiré space.

---

## 6. Implications for Extraction

The three zones have **different functional content** that must be preserved separately:

| Zone | Functional content | Extraction priority |
|------|--------------------|-------------------|
| SILENT | Task classifier directions (early PC0–PC2) | Must preserve — determines which program runs |
| ENRICH | Knowledge store (relation directions, soft crystal) | Must preserve — provides factual content |
| COMMIT | Crystallized KIBC combinators (hard crystal) | Must preserve — executes computation |

A ternary extraction that collapses all zones equally will degrade the task classifier first (smallest signal in combinator subspace) while preserving the combinator structure (largest signal). This predicts a specific failure mode: ternary models that execute combinators correctly but route to wrong programs.

The SILENT zone gratings must be extracted with the same fidelity as the COMMIT zone, even though their combinator-projection signal is weak. Full d_ff PCA geometry must be preserved, not just combinator projections.

---

## 7. Artifacts

| Asset | Location |
|-------|----------|
| Function mapper (combinator projection) | `scripts/experiments/function_mapper.py` |
| Function discovery (unsupervised PCA) | `scripts/experiments/function_discovery.py` |
| Function map results (0.6B, 14B) | `results/function-map/` |
| Function discovery results (14B) | `results/function-discovery/Qwen_Qwen3-14B/` |
| Hologram readout (14B) | `results/hologram-reader/Qwen_Qwen3-14B/` |

---

## 8. Open Questions

1. **What are the TASK directions explicitly?** The early-layer moiré PCs (PC0=compute/language, PC1=recursion/reduction, PC2=structured/NL) — can we extract these as explicit direction vectors, analogous to combinator fingerprints? They are the "program selector" directions.

2. **Do task directions transfer across model families?** The combinator crystal is universal (session 161, crystal-universality.md). Are the task-classifier directions equally universal, or model-family-specific?

3. **How many distinct task programs exist?** k-means with k=5 shows lambda, arithmetic, code, reasoning, general NL. Is this the true number, or an artifact of the probe set? The real k is unknown.

4. **Can the task directions be exploited for controlled steering?** If PC0 separates "compute mode" from "language mode," projecting onto PC0 and shifting might route arbitrary input through the lambda execution path — a form of task-direction steering.

5. **Does the two-level architecture scale?** At 0.6B vs 14B, does the task separation ratio increase (more distinct task classifiers at scale) or decrease (universal opcode basis dominates earlier)?
