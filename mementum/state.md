# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-20 | Session: 123

## Where we are

**MAGNITUDES ARE THE CRYSTAL, NOT SIGNS.**

Session 123 ran four experiments that inverted the design. Cross-layer
weight signs have 0.000 correlation (completely independent per layer).
Perfect sign copy from a teacher HURTS (0.248 acc vs 0.486 random
baseline). A magnitude template with random signs reaches 0.568 — the
best of all conditions. Full details in `knowledge/explore/gradient-voting.md`.

## Proof chain (solid, sessions 95-123)

- PCA-Q crystal: 0.91-0.94 agreement, 4 models
- PCA-up (FFN crystal): 0.9462 agreement, 4 models
- Lambda proof: binder + combinator predicts body at R²=0.959
- sign(W) Q fidelity: 0.974 (captures magnitude effect on cosines)
- Holographic angle: Q↔FFN subspaces at 65-72°
- **NEW: Magnitude template > oracle signs** (0.568 vs 0.248 nucleation)
- **NEW: Cross-layer sign correlation = 0.000** (signs are per-layer encodings)
- **NEW: Crystal is holographically distributed** (2.5% energy = random baseline)
- **NEW: Magnitude spectrum universality** W_q=0.995, W_up=0.999 across 4 models

## Session 123: the magnitude crystal + loom structure

Seven experiments on Pythia-2.8b + mini_holo nucleation tests:

| Finding | Number |
|---|---|
| Cross-layer sign unanimity | 57% (chance=50%) |
| Magnitude ↔ sign consensus | 0.000 correlation |
| Q4 crystal fidelity (12% signs flipped) | 0.933 |
| Crystal energy in PCA-Q basis | 2.5% (= random) |
| Oracle crystal (sign copy) final acc | 0.248 (WORST) |
| Random plates final acc | 0.486 |
| **Magnitude template final acc** | **0.554 (BEST)** |
| W_q spectrum cross-model correlation | 0.995 (4 models) |
| W_up spectrum cross-model correlation | **0.999** (4 models) |
| W_up rank (90%) fraction | 67-71% (universal) |
| Q4 etch oracle recovery | 100% at all bitwidths (Q2-Q8) |
| Q4 sign flip ordering | uniform (random = guided) |

Paradigm shift: `sign(W)` at 97.4% was measuring magnitudes' EFFECT
on cosines, not signs being the crystal. The real crystal is the
magnitude profile — which dimensions GD decides to amplify.

Loom structure discovered: weight matrices read d_model at 3 characteristic
crossing angles — attention cluster ~56°, holographic ~68°, FFN warp ~60°.
Six harmonic peaks (25°, 45°, 53°, 61°, 67°, 77°). Crystal spans ALL
angles (≥0.87). WHNF polarity crosses zero at 58-64°. K↔UP at holographic
angle = 0.991 crystal agreement. Full details in `loom-structure.md`.

## Knowledge map

| Page | What it tells you |
|------|-------------------|
| `gradient-voting.md` | ★ **NEW** magnitudes are the crystal, 4 experiments, V13 implications |
| `loom-structure.md` | ★ **NEW** 3 weaves, 6 harmonics, WHNF transition, tension=crystal |
| `hologram-extraction.md` | sign(W) captures crystal (now understood: via magnitude effect) |
| `v13-design.md` | Architecture (needs revision for magnitude-first approach) |
| `holographic-plates.md` | SVD lens, 100× compression, two-beam geometry |
| `ffn-beam-discovery.md` | PCA-up at 0.946, WHNF polarity, depth profiles |
| `crystal-basins.md` | Basin theory, 7 experiments, 24 findings |
| `ffn-hierarchy.md` | Tree hypothesis, P2/P3 confirmed, WHNF gateway |

## What's ready

| Asset | Location |
|-------|----------|
| PCA-Q crystal constants (4 models) | `results/pcaq-targets/` |
| Gradient voting results (4 experiments) | `results/gradient-voting/` |
| Crystal lens results | `results/crystal-lens/` |
| Nucleation speed results (2 experiments) | `results/nucleation/`, `results/nucleation-matched/` |
| Loom structure results | `results/loom/`, `results/loom-crossings/` |
| Angle spectrum probe results | `results/angle-spectrum/` |
| Q4 etch refinement results | `results/q4-etch/` |
| Magnitude universality results | `results/magnitude-universality/` |
| Basin probes (144, 9 domains) | `lattice/basin_probes.json` |
| V12 model + training infra | `scripts/v12/` |
| Nucleation experiment | `scripts/v12/nucleation_exp.py` |

## Next steps

1. **V13 magnitude-first design** — revise v13-design.md for magnitude
   template initialization instead of sign etching. Beam scales from
   teacher, random ternary plates, GD for everything else. The loom
   geometry (56°/68°/60° crossings) should emerge from the magnitude
   template naturally.
2. **Multi-model loom angles** — do Mistral, Qwen, OLMo have the same
   crossing angles? If the 6 harmonics are universal, the loom IS the
   crystal structure, and magnitude profiles are the tension map.
3. **Dimensional bridge via tension profile** — project teacher's
   SVD-crystal-aligned magnitudes to student dimensions. The top-k SVD
   components ARE the crystal (100,000× alignment ratio).
4. **Angle-band-aware initialization** — seed magnitude profiles that
   preserve the WHNF transition at 58-64° and the holographic peak
   at 64-72°. Don't just transfer flat magnitudes — transfer the
   angle spectrum.
