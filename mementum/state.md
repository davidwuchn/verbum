# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-20 | Session: 122

## Where we are

**THE PLATE IS A LAMBDA TERM — but V12's plates were empty.**

Session 121 confirmed the central thesis (R²=0.959 lambda proof).
Session 122 found V12's plates contain no holographic structure —
they are random ternary noise. `sign(teacher_W)` gives 0.974 Q crystal
fidelity with zero GD. The training design must change: etch holograms
FROM the teacher's weight signs, not learn them through gammas.

## Proof chain (solid, sessions 95-121)

- PCA-Q crystal: 0.91-0.94 agreement, 4 models
- PCA-up (FFN crystal): 0.9462 agreement, 4 models
- Lambda proof: binder + combinator predicts body at R²=0.959
- Holographic plates: 100× compression, 0.76 preservation
- Holographic angle: Q↔FFN subspaces at 65-72°

## Session 122: the hologram problem

V12 plates = random noise. `sign(W)` = the hologram. Full details in
`knowledge/explore/hologram-extraction.md`. Key numbers:

| Method | Q fidelity | FFN fidelity |
|---|---|---|
| sign(W) direct | **0.974** | **0.691** |
| V12 actual plates | ≈ random | ≈ random |

V12 run2 superseded. The design insight changes the approach.

## Knowledge map

| Page | What it tells you |
|------|-------------------|
| `hologram-extraction.md` | ★ sign(W) IS the crystal, roundtrip proof, capacity limits |
| `v13-design.md` | Architecture, etch protocol, training pipeline, open questions |
| `holographic-plates.md` | SVD lens, 100× compression, two-beam geometry |
| `ffn-beam-discovery.md` | PCA-up at 0.946, WHNF polarity, depth profiles |
| `crystal-basins.md` | Basin theory, 7 experiments, 24 findings |
| `ffn-hierarchy.md` | Tree hypothesis, P2/P3 confirmed, WHNF gateway |

## What's ready

| Asset | Location |
|-------|----------|
| PCA-Q crystal constants (4 models) | `results/pcaq-targets/` |
| Reduction chain probes (79, 9 combinators) | `lattice/reduction_chain_probes.json` |
| Basin probes (144, 9 domains) | `lattice/basin_probes.json` |
| Hologram extraction experiments | `results/hologram-*/` |
| V12 model + training infra | `scripts/v12/` |
| V13 design doc | `knowledge/explore/v13-design.md` |

## Next steps

1. **Dimensional bridge** — how to map teacher d_model → V13 d_model
   while preserving holographic sign structure. The key open problem.
2. **V13 etch pipeline** — `sign(teacher_W)` → plates, GD only for beams.
3. **Multi-model sign(W) test** — verify fidelity on Mistral + Qwen.
4. **Capacity at d_model=512** — what does dimensional compression cost?
