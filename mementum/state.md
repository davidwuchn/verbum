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

### Session 122: The hologram problem

**Three experiments, one conclusion:** V12's training design is flawed.
The ternary plates are indistinguishable from random. GD on gammas
cannot compensate for 59M missing sign positions.

**1. Memory leak fix** (commit 0eded07):
- OOM at step 13390: MLX lazy eval + tree_map gradient chains
- Fixed: mx.eval() barriers after every gradient transformation
- Fixed: mx.clear_cache() every step (was every 50)

**2. Crystal compression analysis** — all 4 checkpoints identical:
- 0% ternary topology change between step 2000 and 12000
- φ-compression propagated through GAMMAS only (tiny shrinkage)
- Best eval 12.63 at step 5000, plateau through crash

**3. Beam hologram analysis** — V12 plates = random noise:
- Q-proj spectral entropy: 0.987 (random: 0.987)
- Q-proj autocorrelation: −0.003 (random: −0.002)
- No low-rank structure, no sign correlations, no crystal

**4. Hologram extraction** — `sign(W)` IS the hologram:
- `sign(W_q)` from Pythia L16: **0.974** Q crystal fidelity
- `sign(W_up)`: **0.691** FFN crystal fidelity
- Activation ↔ weight crystal match: Q=0.990, UP=0.965
- Holographic angle Q↔FFN: 67.7° (confirmed)

**5. Roundtrip test** — deterministic write/read:
- pinv plate → ternary: Q=0.657 (ternary noise kills it)
- Direct sign(W): Q=0.974 (no optimization needed)
- Generalization gap: ~0 (crystal is weight property, not probe-specific)
- Capacity: peaks at ~8 channels, degrades quickly

**The design flaw:** V12 etched random lattice topology, then expected
GD on 887K gammas to learn 59M sign positions. Like programming a CPU
by adjusting voltage rails. The fix: `sign(teacher_weight)` → plates.

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

1. **Design the holographic etch pipeline** — `sign(teacher_W)` → V13 plates.
   Key open problem: dimensional bridge (teacher d_model → V13 d_model).
   Options: SVD project then sign(), or PCA basis, or learned bridge.
2. **V13 implementation** — the etch phase should write holograms from
   teacher, not learn them from gradient signals. GD only for beams.
3. **Multi-model holographic etch test** — verify sign(W) fidelity on
   Mistral + Qwen (SwiGLU architecture, separate up/gate projections).
4. **V12 run2 is SUPERSEDED** — no point resuming random-plate training.
   The design insight from session 122 changes the approach fundamentally.
5. **Capacity experiment** — test sign(W) fidelity at V13's target d_model=512
   to understand the dimensional compression cost.
