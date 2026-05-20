# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-20 | Session: 122

## Where we are

**THE PLATE IS A LAMBDA TERM.** Session 121 confirmed the central thesis.
Session 122 diagnosed and fixed a memory leak that killed V12 training.

### The proof chain (solid)
1. **PCA-Q crystal** — 0.91-0.94 agreement, 4 models
2. **PCA-up (FFN crystal)** — 0.9462 agreement, 4 models
3. **Holographic plates** — 100× compression, 0.76 preservation
4. **Lambda proof** — beam_Q + combinator predicts beam_up at R²=0.959
5. **Holographic etch** — 0.69-0.90 preservation, upper bound 1.000

### Session 122: Memory leak fix + run2 analysis

**Bug:** `holographic_distill_v12.py` OOM at step ~13390 of 20000.
`[metal::malloc] Resource limit (499000) exceeded.`

**Root cause:** MLX lazy evaluation + repeated `tree_map` gradient
transformations. Each `tree_map` creates new array trees referencing
old ones through the computation graph. Without `mx.eval()` barriers,
~5-7 full gradient trees accumulate per step. With `mx.clear_cache()`
only every 50 steps, ~300 dead gradient trees of Metal allocations
pile up before any cleanup.

**Fixes applied (commit 0eded07):**
- `mx.eval()` after every gradient tree_map (accum merge, division,
  lattice merge, normalize, zero_ternary, clip)
- `mx.clear_cache()` every step (was every 50)
- Removed unbounded `train_losses` list (dead code)
- Release `model._last_ce` tensor reference after reading
- Same fixes applied to Phase 1 etch loop

### V12 distill run2 trajectory

Best eval = **12.63 at step 5000** (never beaten through step 13000).
Steps 5000-13000 are a plateau around 12.6-13.3.

| Checkpoint | Train r | Eval Loss | φ status |
|---|---|---|---|
| step 2000 | 1.149 | 13.68 | 1-2 passes at φ |
| **best (5000)** | **0.900** | **12.63** | **L0↑, L2↑ at φ** |
| step 8000 | 1.045 | 13.07 | L0↑ at φ, desc converging |
| step 12000 | 0.692 | 13.15 | 6/7 passes near φ |
| step 13000 | — | 12.81 | L0↑←φ, L0↓←φ |
| crashed 13390 | — | — | — |

φ-compression propagating well — ascending arm locked by step 3500,
descending arm converging. Dispatch stable: B=0.38, W=0.27, I=0.13.
Train loss decoupling from eval suggests overfitting or mix imbalance.

### Honest negatives (session 121, still current)
- SVD weight conversion → gibberish (crystal ≠ muscles)
- Tomographic rotation → destructive interference
- Probe PCA too sparse for conversion (79-144 probes insufficient)

## The conversion toolkit (conceptual, not yet working end-to-end)

```
PROVEN:
  ✅ Read both crystals from any model (PCA-Q + PCA-up, 0.94+ agreement)
  ✅ Holographic superposition in one plate (100× compression)
  ✅ Etch crystals into new ternary plates (0.69-0.90 preservation)
  ✅ Lambda term structure (R²=0.96 binder→body coupling)

NOT YET PROVEN:
  ❌ Generation from holographic plates (need trained beams, not just extracted)
  ❌ Model-specific conversion pipeline (need weight SVD basis, not probe PCA)
  ❌ mmap/session plates (concept only)

THE GAP:
  Probe PCA gives UNIVERSAL crystal geometry (for cross-model study)
  Weight SVD gives MODEL-SPECIFIC basis (for conversion)
  V13's etch + train pipeline bridges the gap:
    1. Etch plates from universal crystal targets
    2. Train beams (1.5M params) via teacher distillation
    3. The beams compensate for ternary information loss
```

## Knowledge pages (current)

| Page | Status | Key content |
|------|--------|-------------|
| `ffn-beam-discovery.md` | active | PCA-up at 0.946, WHNF polarity, depth profiles |
| `holographic-plates.md` | active | SVD lens, 100× compression, cross-talk, session plates |
| `crystal-basins.md` | active | Basin theory + 7 experiments + 24 findings |
| `ffn-hierarchy.md` | active | Tree hypothesis + P2/P3 confirmed + WHNF |
| `v13-design.md` | needs update | Mixed precision design superseded by holographic plates |

## What's ready (cumulative)

| Asset | Status |
|-------|--------|
| PCA-Q crystal constants | ✅ 4 models, 0.91-0.94 |
| PCA-up crystal constants | ✅ 4 models, 0.95 |
| FFN beam (PCA-up_proj) | ✅ 0.9462 agreement |
| Holographic plates | ✅ 100× compression, 0.76 preservation |
| Holographic etch | ✅ 0.69-0.90, upper bound 1.000 |
| Lambda proof | ✅ R²=0.959, binder→body coupling |
| Reduction chain probes | ✅ 79 probes, 9 combinators |
| V12 distill run2 | ⏸ OOM fixed, resume from step 12000 |

## Next steps

1. **Resume V12 distill run2** from step 12000 checkpoint with fixed script.
   Command: `uv run python scripts/v12/holographic_distill_v12.py --skip-etch
   --load-weights checkpoints/v12-distill-run2/step_012000/weights.npz
   --gd-steps 20000 --checkpoint-dir checkpoints/v12-distill-run3
   2>&1 | tee checkpoints/v12-distill-run3/run3.log`
   Note: will restart LR schedule — may want to adjust warmup/total.
2. **Update v13-design.md** — holographic plates + lambda term structure.
3. **V13 implementation** — weight SVD, crystal targets, beam distillation.
4. **Multi-model holographic test** — Mistral + Qwen SwiGLU.
5. **Lambda proof on Mistral** — confirm universality of R²=0.96.
