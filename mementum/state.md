# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-25 | Session: 148

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 148: Found and fixed two critical bugs that blocked all ternary learning in v14. Delta plates showed 158M TD flips but ZERO actual changes — a complete Sisyphus loop. Fixed: (1) collect_delta_params returned 280 aliased modules instead of 70 unique (shared weight 4× traversal), (2) two-step transition through zero incompatible with no-block constraint (every +1→0 staging step immediately undone by _enforce_no_block). Training restarted from step 500 checkpoint with direct +1↔-1 flips for attention deltas. First eval: CE=9.71, PPL=16,503 on held-out data (vs train CE=8.0). Waiting for TD warmup (25 steps) to see first real delta plate changes.**

## Active training run

- **v14-td resumed from step 500** in tmux main:2
- Command: `uv run python scripts/v14/train_td.py --extracted-model-path checkpoints/v14-extracted/model.npz --resume checkpoints/v14-td/step_000500`
- TD warmup resets on resume (step_count not persisted) — first flips expected ~step 526
- **Watch for:** `Δ > 0.000` in logs = ternary learning is working
- Log: `checkpoints/v14-td/run.log`

## Session 148: Two bugs killed all ternary learning

### Bug A: Delta module aliasing (collect_delta_params)

`shared_stride_stack` is shared across stack_a, stack_b, stack_c via Python reference.
MLX's `named_modules()` traverses all paths including aliases. `collect_delta_params`
returned 280 modules (70 unique × 4 paths). TD processed each physical module 4 times
with conflicting gradients — last write wins, wasting 3/4 of gradient computation.

**Fix:** Deduplication by `id(mod)` in `collect_delta_params`, keeping shortest path.
Now returns exactly 70 modules, all canonical `shared_stride_stack.*` paths.

### Bug B: Two-step transition + no-block invariant

TD's staging protocol: `+1 → 0 → ±1` (two steps, through zero).
v14 no-block invariant: attention deltas must NEVER contain 0.
`_enforce_no_block` runs after every TD step and resets zeros to +1.
Result: every staging step immediately undone. 77K fixes/step = the evidence.

**Fix:** Attention delta modules (no_block=True) use direct flips: `+1 ↔ -1`.
FFN deltas (if enabled) still use two-step staging through zero.
`_enforce_no_block` now finds 0 violations after TD step.

### First eval baseline (step 500)

| Metric | Train | Eval (held-out) | Random |
|--------|-------|-----------------|--------|
| CE | 8.00 | 9.71 ± 0.22 | 12.42 |
| PPL | 2,981 | 16,503 | 248,320 |

- 22% CE reduction over random on eval — base extraction + continuous learning works
- 1.7 nat train-eval gap — gamma/norms overfit on ~16M tokens
- ALL learning was continuous params (delta plates unchanged)
- This is the baseline before ternary learning activates

### New tooling

- `scripts/v14/eval_ppl.py` — perplexity evaluation on held-out shards (54-59)

## Session 146: v14 Architecture Build

### Design Decisions

1. **16 strides** (2⁰ through 2¹⁵ = s1..s32768). Power of 2. Max context 262K tokens.
   Each stride is a holographic lens specialized for a frequency band.
   O(L×W) per stride, not O(N²). 16 eyes vs flat attention's 1.

2. **Balanced 9/9 split** with 2-stride overlap at s128, s256:
   - Stack A (ascending fine): s1→s256, 4 passes
   - Stack B (ascending coarse): s128→s32768, 4 passes
   - Stack C (descending): all 16 strides, 5 passes reversed
   - 13 total passes, 692M ternary positions (165 MB)

3. **Bottom-up algedonic**: C feeds algedonic UP to BOTH B and A (not just a chain).
   AlgedonicCombiner merges B+C signals for A. Bottom tells top what it needs.

4. **No-block constraint on attention delta**: can only flip ±1, NEVER zero.
   Prevents the dispersal collapse that killed v13-td-r10.

5. **Vocab = 248,320** (Qwen3.6-27B tokenizer) — matches teacher for FFN alignment.

### Crystal Loss System (Einstein tensor-aware)

- **Crystal lattice MSE**: 3 zones (A=encode, B=compute, C=converge), linear average
- **Geodesic parity**: uses Riemannian mean of Zone A+C as target (NOT raw Zone B).
  Ratio geodesic/linear = 0.867 — manifold IS curved. One target prevents gradient cancellation.
- **Cross-zone lens rotation**: joint eigenbasis, enforces ~11° depth rotation
- **Spectral φ loss**: target ratio 0.6299±0.019 (5-model consensus)
- **Holographic progressive**: monotonic CE decrease through depth (12 passes)
- **Hyperbolic norm growth**: embed < A < B < C

### Training Phases (from state.json notes)

Phase 1: Base plates frozen (from Qwen3.6-27B extraction). Delta plates train.
  Crystal latches first. Then TD activates (Schmitt trigger at 3%/7%).
  GD finds calibration, TD finds routing differences for stride-stack.

Phase 2: Fold delta into base (base ⊙ delta = new base). Freeze. Reset delta to +1.

Phase 3: Normal GD + TD on the clean combined model.

## Previous sessions

### Session 145 (continued): V13-TD-R10 Collapse → V14 Extraction

v13-td-r10 collapsed at step 5878. Delta plate block accumulation killed attention.
Forensics: stride-stack needs ~80% of teacher positions, teacher signs 91% correct.
Extracted stride-attention mask (132 modules). Built v14 extraction from Qwen3.6-27B
→ 593M ternary positions (148 MB), 375× compression. Pure ±1 base plates.

### Session 145: Micro Model Mechanism Extraction

Alternating overlay (beta-reduction cycle), 3 rotation eigenplanes (±48.8°, ±13.9°, ±2.1°),
KIBC is temporal (B→K→C→B through depth), rotation accelerates through depth (L0:2° → L3:24°),
mechanism is input-invariant (CV<0.5), overlay converges by step 500.

### Session 144: Parity Gradient Cancellation + Einstein Tensor

Three-zone parity = gradient opposition. Zone B only: 1.167→0.039. Crystal manifold IS
curved (geodesic/linear=0.75). G_ab has even/odd block structure. Student sits on
Riemannian mean.

### Session 142: Holographic State Machine + Crystal Error Correction

THE MODEL IS A HOLOGRAPHIC STATE MACHINE. FFN plates = holographic storage, crystal
basins = states, Q rotation = readout beam, gate = beamformer. Built hierarchical
crystal parity loss + cross-zone lens rotation loss.

## Proof chain

| Claim | Evidence | Status |
|-------|----------|--------|
| Universal crystal exists | 4+ model consensus | ✅ proved |
| KIBC-DYWH basis universal | Found across all architectures | ✅ proved |
| Types are lexical (88% embed) | Qwen3-32B type probe | ✅ proved |
| SVD spectrum → phi | 5-model consensus, φ-dev=0.012 | ✅ proved |
| FFN indexing is holographic | ρ=0.83 input→FFN, p<10⁻⁴⁴ | ✅ proved |
| FFN depth = LENS | aperture 3% → fan 49% → converge 2% | ✅ proved |
| Crystal manifold is curved | Geodesic/linear=0.75, G_ab even/odd | ✅ proved |
| Parity gradient cancellation | 3-zone opposition → stuck 1.167 | ✅ proved |
| Zone-B-only parity works | 1.167→0.039 on first step | ✅ proved |
| Model is holographic state machine | FFN=storage, crystal=states, Q=beam | 🎯 synthesis |
| FFN overlay alternates comp/sel | micro model: -+-+ / +-+- across 4 layers | ✅ proved |
| KIBC is temporal (layers not heads) | B→K→C→B depth sequence in micro model | ✅ proved |
| Mechanism is input-invariant | CV<0.5 for all PCs across 8 categories | ✅ proved |
| Rotation accelerates through depth | L0: 2° → L3: 24° (12× increase) | ✅ proved |
| Stride-stack needs ~80% of teacher attention | v13-td-r10 collapse forensics | ✅ proved |
| Teacher attention signs 91% correct for stride | Cross-stack agreement where both active | ✅ proved |
| Qwen3.6-27B extractable to 593M ternary | v14 extraction: 375× compression | ✅ proved |
| Crystal latches within 200 steps | v14-td: crystal_mse < 0.03 at step 160 | ✅ proved |
| **Shared-weight aliasing breaks TD** | **280 vs 70 modules, 4× overwrite** | ✅ proved (session 148) |
| **No-block kills two-step staging** | **77K zeros/step reset, 0% delta change** | ✅ proved (session 148) |
| TD activates and improves | Fix applied, awaiting post-fix data | ❓ testing |
| **16-stride holographic lens attention** | **Architecture running, ternary learning unblocked** | 📐 testing |

## Knowledge map

| Page | What it tells you |
|------|-------------------|
| `mechanism-extraction.md` | Full micro model mechanism: alternation, eigenplanes, KIBC temporal |
| `ffn-beta-reduction-indexing.md` | Holographic indexing, LENS profile, ρ=0.83 |
| `ternary-descent.md` | TD algorithm: delta plates, gradient decomposition, reduction |
| `categorical-geometry-probes.md` | Curry-Howard 100%, adjunctions rank-1 |
| `phi-compression-universal.md` | SVD spectrum → phi, 5-model consensus |

## What's ready

| Asset | Location |
|-------|----------|
| **V14 model architecture** | `scripts/v14/` (15 files, including eval_ppl.py) |
| **V14 extracted base plates** | `checkpoints/v14-extracted/model.npz` (85 MB) |
| **V14 training script (FIXED)** | `scripts/v14/train_td.py` |
| **V14 eval script** | `scripts/v14/eval_ppl.py` |
| **Step 500 checkpoint** | `checkpoints/v14-td/step_000500/` |
| **Step 500 eval baseline** | CE=9.71, PPL=16,503 (held-out) |
| **Training run (active)** | tmux main:2, resumed from step 500 |

## Next steps

### IMMEDIATE: Monitor training for TD activation (~step 526)

1. **Watch for `Δ > 0.000`** in training logs — confirms ternary learning unblocked
2. **After 100 steps with active TD:** run `eval_ppl.py` again and compare to baseline
3. **Compare train/eval gap:** ternary routing should generalize better than gamma memorization

### AFTER TERNARY LEARNING CONFIRMED WORKING:

4. **Monitor delta_stats:** flip_frac should grow, no_block_fixed should stay 0
5. **First reduction:** when delta converges, fold into base, reset, continue
6. **Eval at each milestone:** track eval PPL curve alongside training

## Open questions

9. **Content transfer via sign().** Does the 81% token subspace content survive ternary extraction?
10. **LENS profile derivable from eigenvalue ratios?**
11. **Quality at 1B with d=1280.** What CE/ppl does the expanded model achieve?
12. **16-stride coverage.** Do the higher strides (s4096+) learn anything useful with 4K seq training?
13. **Bottom-up algedonic value.** Does C→A feedback measurably accelerate convergence?
14. **Does ternary learning close the train-eval gap?** Topology changes should generalize
    better than continuous parameter overfitting. Step 500 baseline: 1.71 nat gap.
15. **TD step_count not persisted on resume.** Warmup repeats. Worth persisting?
