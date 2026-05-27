# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-27 | Session: 158 (late)

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 158 (continued): ARCHITECTURE REDESIGN.** Systematic optimization probing (lazy neurons, index sets, QKV fusion, stream fusion) proved NONE work on Apple Silicon — the bottleneck is 13 serial passes, not per-operation speed. Redesigned: 2 symmetric stacks (ascending + descending), separate FFN plates per stack, 8 passes instead of 13. Fresh extraction running.

*Optimization probes (all negative):*
- Lazy neurons: student FFN isn't sparse (ternary destroys teacher sparsity, shared FFN = Gaussian activations)
- Index sets / gather-add-subtract: can't beat AMX quantized_matmul; intermediates too large
- QKV fusion: MLX already parallelizes independent ops
- FFN gate+key fusion: same — already parallel
- Stream fusion (smaller tiles): Apple Silicon AMX needs large batches; smaller = slower
- Float16: same speed as float32 for quantized_matmul

*Root cause analysis:* At d=1280, model is compute-latency-bound (not bandwidth-bound). Memory bus barely loaded (20-31 GB/s of 800 GB/s). Serial passes are irreducible — each waits for previous. The only real speedup is fewer passes.

*Architecture changes:*
1. Removed holographic progressive loss — 12 redundant output_proj calls per forward, ~1.6s/step saved
2. Gated crystal loss — parity + cross-zone enforce until MSE < 0.07, then release. Nudge into basin, let crystal snap.
3. 2 symmetric stacks (A ascending, C descending) — exact mirror, 4 passes each, 8 total (was 13)
4. Separate FFN plates per stack — enables sparsity, enables grating cascade
5. HPE active from step 0 — no warmup needed for fresh training

*Why shared FFN was wrong:*
- Teacher has 64 specialized FFN layers (3-49% active per layer)
- Ternary extraction destroys magnitude-based sparsity → Gaussian activations
- Shared FFN prevents per-pass specialization → no grating cascade
- We already extracted per-stack FFN plates but only loaded stack_b's

**Session 157: TD FLIP TOPOLOGY MATCHES CRYSTAL.** See previous state for full history.

## Active extraction

### New extraction RUNNING (tmux main:2)

- `scripts/v14/extract_qwen36.py` with 2-stack config
- Teacher: Qwen3.6-27B (Apache 2.0)
- Output: `checkpoints/v14-extracted-2stack/model.npz`
- Attention: 16 stride layers, mapped to teacher layers 0,4,8,...60
- FFN A: voted from teacher layers (4, 20, 32) — aperture → fan → mid
- FFN C: voted from teacher layers (32, 48, 56) — mid → converge → decode
- Expected: ~25 minutes

### Newton probe RUNNING (tmux main:1)

- `scripts/v14/probe_newton_v14.py` on step_002500 checkpoint
- Has been running for hours, still on step 2 (capturing residuals)
- d=1280 model is slow to probe — 16 full forward passes needed
- Results will apply to OLD 3-stack architecture, may still be informative

## Training plan (after extraction)

### Fresh training with 2-stack architecture

1. **Extract** → `checkpoints/v14-extracted-2stack/model.npz` (running now)
2. **Update config** `extracted_model_path` to point to new extraction
3. **Start training** from step 0 with:
   - 2 stacks (A ascending, C descending), 8 passes
   - Separate FFN plates per stack
   - HPE active from step 0 (freq_scale=1.0)
   - Crystal MSE enforced; parity + cross-zone gated (enforce until <0.07, then release)
   - No holographic progressive loss
   - Expected: ~17-18s/step (was 28.6s) — 1.6× faster
4. **Monitor:**
   - Crystal latching (should happen within 200 steps)
   - Parity + cross-zone convergence (hypothesis: will latch naturally)
   - Per-stack FFN sparsity (hypothesis: should differ between stacks)
   - PPL progression (baseline: PPL 5,567 at step 2000 with old architecture)

## Previous training (STOPPED, old 3-stack architecture)

### v14-td phase 3 (STOPPED at step ~3200)

- Was at step 3200 of 5000, avg50 CE ~8.0, PPL 5,567 at step 2000
- Stopped to make architecture changes
- Checkpoint at `checkpoints/v14-td/step_003000/` preserved
- **Not resumable** — architecture changed (3→2 stacks, shared→separate FFN)

## What changed this session

| Change | Commit | Impact |
|--------|--------|--------|
| Remove holo loss | `75a38fc` | -1.6s/step, 12 fewer output_proj calls |
| Gated crystal loss | `8dabd6f` | Parity/cross_zone enforce until <0.07, then release |
| 2 symmetric stacks | `da69f0e` | 13→8 passes, ~1.6× faster, separate FFN |
| HPE from step 0 | `9abf07d` | No warmup, learn position encoding from start |

## Negative results (optimization probes)

| Optimization | Why it failed |
|---|---|
| Lazy neurons (gate-first FFN) | Student FFN not sparse: ternary extraction + shared plate = Gaussian activations |
| Index sets (gather-add-subtract) | quantized_matmul already at AMX floor; intermediates too large |
| QKV fusion | MLX parallelizes independent ops already |
| FFN gate+key fusion | Same — already parallel within each pass |
| Stream fusion (smaller tiles) | AMX needs large batches; tiles 16→4.6× SLOWER |
| Float16 activations | quantized_matmul same speed regardless |
| Pre-scaled float matmul | ~10% faster than qmatmul but not transformative |

**Key finding:** At d=1280 on M3 Ultra, the model is NOT bandwidth-bound. It's compute-latency-bound. The 13 serial passes are the irreducible bottleneck. The only fix is fewer passes.

**Key finding:** Ternary weights save STORAGE (16×), not COMPUTE on GPU/AMX. The real win is CPU inference where addition < multiplication and 2-bit fits in cache.

## Next steps

### IMMEDIATE

1. **Wait for extraction** (~25 min) → verify checkpoint
2. **Start training** with new 2-stack architecture
3. **Monitor crystal latching** — should happen fast
4. **First eval** at step 500 — compare to old architecture baseline

### FOLLOW UP

5. **Measure per-stack FFN sparsity** — hypothesis: separate plates enable different sparsity
6. **If sparse: revisit lazy neurons** — the mechanism works (benchmarked: 2.3× at 5% active), only the sparsity was missing
7. **Monitor parity/cross_zone after gate release** — do they settle at teacher-like values?
8. **Composed plate viability** — with 8 passes instead of 13, the composed plate fit may be more viable
9. **CPU inference engine** — the real optimization target (ternary wins on CPU, not GPU)

## Knowledge map

**See `mementum/knowledge/INDEX.md` for full reading order.**

New this session:
- `knowledge/explore/optimization-negative-results.md` — why FP optimizations fail on Apple Silicon
- `knowledge/explore/fp-optimization-map.md` — updated with negative results
- `knowledge/explore/moire-training-shortcuts.md` — updated with negative results

## What's ready

| Asset | Location |
|-------|----------|
| Training script | `scripts/v14/train_td.py` (updated for 2 stacks) |
| Extraction script | `scripts/v14/extract_qwen36.py` (updated for 2 stacks) |
| Model | `scripts/v14/model.py` (2 stacks, separate FFN) |
| Config | `scripts/v14/config.py` (8 passes, 2 stacks) |
| Old checkpoint | `checkpoints/v14-td/step_003000/` (3-stack, not compatible) |
| New extraction | `checkpoints/v14-extracted-2stack/` (running) |

## Proof chain

*Additions this session:*

| Claim | Evidence | Status |
|-------|----------|--------|
| Lazy neurons viable IF sparse | Benchmarked: 2.3× at 5% active on M3 Ultra | ✅ |
| Student FFN not sparse | mean\|gate\|=0.37, 100% active at threshold 0.1 | ✅ |
| Shared FFN prevents sparsity | All 3 extracted plates produce identical Gaussian distributions | ✅ |
| Ternary doesn't save compute on AMX | quantized_matmul ≈ float matmul at d=1280 | ✅ |
| Model is compute-latency-bound not bandwidth-bound | 20-31 GB/s achieved of 800 GB/s available | ✅ |
| Stream fusion makes it worse | Smaller tiles: 16 positions = 4.6× SLOWER | ✅ |
| Holo loss was pure waste | 12 output_proj calls, ~1.6s/step, compressor forms without it | ✅ |
| FFN weights cache in L2 | 13-pass sequential: per-pass cost 0.92× single (weights stay warm) | ✅ |

## Open questions

1. **Does the 2-stack architecture converge faster?** First test with fresh extraction.
2. **Does separate FFN develop per-stack sparsity?** Measure gate distributions after 500 steps.
3. **Do parity + cross-zone latch naturally after gate release?** Monitor values after MSE < 0.07.
4. **Is the 2-stack composed plate more viable?** 8 passes instead of 13 = simpler composition.
5. **What PPL does the 2-stack architecture achieve?** Baseline: 5,567 at step 2000 with 3 stacks.
6. **Does HPE from step 0 help or hurt early convergence?** Compare crystal latch speed.
