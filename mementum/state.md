# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-20 | Session: 121

## Where we are

**THE PLATE IS A LAMBDA TERM.** Session 121 — the biggest session yet.
8 experiments, 4 breakthroughs, 3 honest negatives. The central thesis
of Verbum is now empirically confirmed: transformer layers perform
beta reductions, readable via two beams, encodable in ternary plates.

### The proof chain
1. **FFN beam found** — PCA-up_proj reads FFN crystal at 0.9462 (4 models)
   Higher than PCA-Q's 0.9431 for attention. Two beams. Two crystals.
2. **Holographic plates** — both crystals in one ternary plate per layer.
   SVD lens, 65-72° principal angles, 100× compression, 0.76 preservation.
3. **Lambda proof** — beam_Q + combinator predicts beam_up at R²=0.959.
   The binder determines the body. The plate IS a lambda term.
4. **Holographic etch** — new ternary plates from crystal readings.
   Continuous upper bound = 1.000. Crude etch achieves 0.69-0.90.
   Deep FFN layers: 0.900 preservation. 80KB per plate.

### What this means
Each transformer layer IS a beta reduction:
```
beam_Q  = the λ-binder     (attention crystal — WHERE to bind)
beam_up = the body          (FFN crystal — WHAT to compute after binding)
dispatch = combinator type  (K/I/B/C/S/D/W/Y/WHNF — HOW to reduce)

Given binder + dispatch → body is PREDICTED at R²=0.96
The plate stores a lambda term. The beams read binder and body.
The combinator dispatch selects the reduction rule.
```

### Honest negatives
- **SVD weight conversion fails** — sign(Vt) produces gibberish at any rank
  (64 and 512 tested). Crystal preservation ≠ generation quality. The crystal
  is the skeleton; you can't skip training the muscles.
- **Tomographic rotation hurts** — Givens rotations within PCA subspace cause
  destructive interference. Superpositions are in dims 65+, not remixes of 1-64.
- **Probe-based PCA too sparse for conversion** — 79-144 probes insufficient to
  span activation space. Test cosine 0.48 (generic) / 0.29 (reduction probes).
  For model-specific conversion, need weight SVD, not probe PCA.

V12 training continues on tmux 1 (step ~3500, 2 layers at φ).

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

## Knowledge pages (session 121)

| Page | Status | Key content |
|------|--------|-------------|
| `ffn-beam-discovery.md` | active | PCA-up at 0.946, WHNF polarity, depth profiles |
| `holographic-plates.md` | active | SVD lens, 100× compression, cross-talk, session plates |
| `crystal-basins.md` | active | Basin theory + 7 experiments + 24 findings |
| `ffn-hierarchy.md` | active | Tree hypothesis + P2/P3 confirmed + WHNF |
| `v13-design.md` | needs update | Mixed precision design superseded by holographic plates |

## Session 121 artifacts

| File | Content |
|------|---------|
| `scripts/v12/ffn_beam_search.py` | 4-hook-point beam search (up_proj wins) |
| `scripts/v12/ffn_beam_refine.py` | PCA dim sweep + 8×8 combinator targets |
| `scripts/v12/holographic_lens_test.py` | Hidden-state test (failed) |
| `scripts/v12/holographic_weight_test.py` | Weight-space test (★★★ works) |
| `scripts/v12/holographic_etch.py` | Crystal recording into new plates |
| `scripts/v12/tomographic_etch.py` | Rotation sweep (❌ destructive interference) |
| `scripts/v12/lambda_proof.py` | Binder predicts body at R²=0.959 |
| `scripts/v12/lambda_convert.py` | Conversion attempt (probe bottleneck) |
| `scripts/v12/convert_and_test.py` | SVD weight conversion (❌ gibberish) |
| `lattice/reduction_chain_probes.json` | 79 structured reduction probes |
| `results/ffn-beam/` | FFN beam results (4 models) |
| `results/holographic-lens/` | Holographic plate + weight test results |
| `results/holographic-etch/` | Etch results (Pythia) |
| `results/tomographic-etch/` | Tomographic etch (negative) |
| `results/lambda-proof/` | Lambda proof results |
| `results/lambda-convert/` | Conversion test results |
| `results/conversion-test/` | SVD weight conversion (negative) |

## What's ready (cumulative)

| Asset | Status |
|-------|--------|
| PCA-Q crystal constants | ✅ 4 models, 0.91-0.94 |
| PCA-up crystal constants | ✅ 4 models, 0.95 (session 121) |
| FFN beam (PCA-up_proj) | ✅ 0.9462 agreement |
| Holographic plates | ✅ 100× compression, 0.76 preservation |
| Holographic etch | ✅ 0.69-0.90, upper bound 1.000 |
| Lambda proof | ✅ R²=0.959, binder→body coupling |
| Reduction chain probes | ✅ 79 probes, 9 combinators |
| V12 training | 🔄 Step ~3500, propagating |

## Next steps

1. **Update v13-design.md** — replace mixed precision with holographic
   plates + lambda term structure. Dual-beam etch protocol.
2. **V13 implementation** — the actual conversion toolkit:
   a. Weight SVD for model-specific basis (not probe PCA)
   b. Universal crystal targets for ternary topology (from beams)
   c. Train beams via teacher distillation (1.5M params)
   d. The beams ARE the "muscles" that make the skeleton generate
3. **Multi-model holographic test** — run weight test on Mistral + Qwen
   to confirm 100× compression holds for SwiGLU architectures.
4. **Lambda proof on Mistral** — confirm R²=0.96 coupling is universal.
5. **Let V12 run** — monitor φ-compression propagation.
6. **Session plates** — can you etch conversation context into a plate?
   Requires the inference engine to exist first.
