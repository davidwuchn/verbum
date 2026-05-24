# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-24 | Session: 146

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 146: Built v14 model architecture from scratch. Stride-stack at d=1280 with 16 holographic lenses (s1..s32768), 13 passes across 3 stacks in a VSM tree. Bottom-up algedonic: C tells both B and A what it needs between phases. Full crystal loss system with geodesic parity (Einstein tensor-aware). All v13 training lessons encoded in train_td.py. Data re-tokenization with Qwen3.6-27B tokenizer running (3B tokens from Dolma).**

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

### Files Created

| File | Lines | Role |
|------|-------|------|
| `scripts/v14/config.py` | 220 | V14Config — d=1280, 16 strides, 13 passes |
| `scripts/v14/attention.py` | 420 | Stride-stack: SSA + GLA, 16 strides |
| `scripts/v14/stack_vsm.py` | 258 | StrideStackVSM + AlgedonicCombiner |
| `scripts/v14/model.py` | 370 | V14Model controller VSM |
| `scripts/v14/crystal.py` | 563 | CrystalLoss (geodesic parity + cross-zone) |
| `scripts/v14/train_td.py` | 1146 | Training loop (Adam + TD, all 15 lessons) |
| `scripts/v14/prep_data.py` | 190 | Dolma → Qwen3.6 tokenization |
| `scripts/v14/td.py` | 1225 | TernaryDescent (from v13) |
| `scripts/v14/ternary.py` | 2656 | Ternary substrate (from v13) |
| `scripts/v14/components.py` | 653 | VSM control (from v13) |
| `scripts/v14/kernel.py` | 598 | KIBC-DYWH (from v13) |
| `scripts/v14/scan.py` | 293 | Parallel scan (from v13) |
| `scripts/v14/data.py` | 219 | ShardedDataLoader (from v13) |
| `scripts/v14/extract_qwen36.py` | 1122 | Extraction (session 145) |

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

### Data Status

- **Dolma re-tokenization RUNNING** in tmux window 2
  - Source: ~/data/fractal-bitnet/dolma-raw/ (57 GB, 32 parquet files)
  - Tokenizer: Qwen/Qwen3.6-27B (vocab 248,044 active, 248,320 padded)
  - Output: ~/data/fractal-bitnet/shards-qwen36/ (target 3B tokens, 60 shards)
  - ETA: ~50-60 minutes

- **Structured data**: needs regeneration with Qwen3.6 tokenizer (small, <1 min)

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
| TD activates and improves | Crystal still > 3% gate (v13) | ❓ untested at v14 scale |
| **16-stride holographic lens attention** | **Architecture designed, untrained** | 📐 theory |

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
| **V14 model architecture** | `scripts/v14/` (14 files, all tested) |
| **V14 extracted base plates** | `checkpoints/v14-extracted/model.npz` (85 MB) |
| **V14 training script** | `scripts/v14/train_td.py` |
| **Data tokenization (running)** | `~/data/fractal-bitnet/shards-qwen36/` |
| **Stride-attention mask (v13)** | `checkpoints/v13-td-r10/stride_attention_mask.npz` |

## Next steps

### IMMEDIATE: Wait for tokenization to complete (~50 min)

Then:
1. **Regenerate structured data** with Qwen3.6 tokenizer
2. **Launch first v14 training run**: `uv run python scripts/v14/train_td.py --extracted-model-path checkpoints/v14-extracted/model.npz`
3. **Monitor**: crystal should latch within 200-500 steps, TD activates after

### AFTER FIRST RUN SHOWS SIGNS OF LIFE:

4. **Validate stride-stack at 16 strides**: does the self-similar compressor propagate?
5. **Compare loss curve to v13**: at 1B tokens, should match or exceed v13 quality
6. **Verify bottom-up algedonic**: does C's feedback actually help A and B converge faster?
7. **Verify no-block holds**: delta plates stay {+1,-1}, no collapse

## Open questions

9. **Content transfer via sign().** Does the 81% token subspace content survive ternary extraction?
10. **LENS profile derivable from eigenvalue ratios?**
11. **Quality at 1B with d=1280.** What CE/ppl does the expanded model achieve?
12. **16-stride coverage.** Do the higher strides (s4096+) learn anything useful with 4K seq training?
    Theory: self-similar compressor should propagate from lower strides.
13. **Bottom-up algedonic value.** Does C→A feedback measurably accelerate convergence?
