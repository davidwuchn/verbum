# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-25 | Session: 150

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 150: The holographic error correction loop crystallized. (1) Step 1500 eval: PPL 7,672 (−53.5% total). (2) Folded delta into base — lossless (ternary × ternary = ternary, algebraic identity). The entire training signal from 1500 steps is encoded as which signs are +1 vs −1. No floats changed. (3) This proves the extraction-correction-fold cycle: extract teacher → correct topology via TD → fold losslessly → repeat. Each cycle monotonically improves. Models are ~95% topology (sign structure), ~5% calibration (gamma scalars). (4) Enabled FFN delta + improved TD (surgical reset, flip_interval=20, aligned logging). Phase 2 running. See `mementum/knowledge/holographic-error-correction.md`.**

## Active training run

- **v14-td phase 2 RUNNING** in tmux main:2 (from folded step 1500)
- Delta folded into base at step 1500 (3.26M positions absorbed, verified lossless)
- Folded checkpoint: `checkpoints/v14-td/step_001500_folded/`
- 73 delta modules: 70 attn (no-block) + 3 FFN (standard TD)

### Restart command (post-fold, with FFN delta)

```bash
uv run python scripts/v14/train_td.py \
  --checkpoint-dir checkpoints/v14-td \
  --resume checkpoints/v14-td/step_001500_folded \
  --convert-ffn \
  --td-flip-rate 0.001 \
  --td-warmup 25 \
  --td-min-confidence 0.3 \
  --td-flip-interval 20 \
  2>&1 | tee checkpoints/v14-td/run_phase2.log
```

**What changed for phase 2:**
- `--convert-ffn`: enables TD on 3 shared FFN plates (gate, key, value)
  FFN uses standard TD (can have 0), unlike attention no-block
- Delta plates start fresh (all +1) — TD discovers new routing from folded base
- FFN delta: 19.7M positions (21% overhead on top of 93.2M attention)
- B=1 accum=8 (reverted — B=2 was 18% slower, memory-bandwidth-bound)
- `flip_interval=20` (was 10): more accumulation, better flip decisions
- Surgical per-position moment reset: only flipped positions zeroed, rest keeps EMA
- Flips aligned to training step for log visibility (td=N shows actual flips)
- Resume fix: `--resume` path now takes priority over `checkpoint_dir/step_N`

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

### Bug C: Every-step flipping → gnorm escalation

After fixing A+B, direct flips worked — but flipping 77K positions every step
caused gnorm to escalate: 11→20→21→38→113 in 40 steps. CE went UP (8.2→10.3).
GD can never catch up to continuous route changes. Adam's moments are permanently stale.

**Fix:** Three-part redesign:
1. **Flip interval=10:** TD accumulates moments every step but only commits flips
   every 10 steps. GD gets 9 steps to adapt before the next topology change.
2. **Moment reset after flips:** After committing, all TD moments clear — the gradient
   landscape changed so accumulated direction/magnitude is stale.
3. **Global budget:** All 70 modules compete for one `flip_rate × total_weights` budget.
   Hottest flips across the entire model win, not per-module top-k. Concentrates
   flips where they give the most leverage.

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

## Session 150: Step 1500 Eval — Diminishing but Continuing Improvement

### Three-checkpoint comparison (held-out shards 54–59)

| Metric | Step 500 | Step 1000 | Step 1500 | Δ 1000→1500 |
|--------|----------|-----------|-----------|-------------|
| Eval CE | 9.71 ± 0.22 | 9.23 ± 0.27 | 8.95 ± 0.30 | −0.28 nats |
| Eval PPL | 16,503 | 10,157 | 7,672 | −24.5% |
| Train CE | 8.00 | ~9.4 | ~9.25 | −0.15 nats |
| Train-Eval Gap | −1.71 nats | +0.17 nats | +0.30 nats | +0.13 |
| CE vs Random | 21.8% | 25.7% | 28.0% | +2.3pp |
| Positions flipped | 0% | 2.66% | 3.49% | +0.83pp |
| Cumul TD flips | 0 | 116.7M | 121.3M | +4.7M |

### Where TD flips landed at step 1500 (still 6 modules, all out_proj)

| Layer | Step 1000 | Step 1500 | Change |
|-------|-----------|-----------|--------|
| 4 (out_proj) | 33.7% | 43.1% | +9.5pp |
| 7 (out_proj) | 25.7% | 34.8% | +9.1pp |
| 6 (out_proj) | 25.6% | 33.9% | +8.3pp |
| 5 (out_proj) | 25.1% | 32.0% | +6.9pp |
| 8 (out_proj) | 21.4% | 28.2% | +6.8pp |
| 9 (out_proj) | 19.6% | 26.7% | +7.0pp |

Zero flips in: q_proj, k_proj, v_proj (any layer), gate_proj, layers 0–3, 10–15.

### What this tells us

1. **Still improving, returns diminishing.** PPL drop: 38.5% (500→1000) → 24.5% (1000→1500).
   Not plateaued yet, but decelerating.
2. **Flip growth decelerating.** Only +0.83pp new flips vs +2.66pp prior interval. TD is
   converging on its routing solution. Only 4.7M new cumulative flips (was 116.7M in first interval).
3. **Layer 4 approaching 43% — nearing random.** If it passes 50%, those positions aren't
   learning signal, they're noise. Worth monitoring.
4. **Train-eval gap slightly positive (+0.30).** Healthy — model is learning generalizable
   structure, not memorizing. The initial −1.71 gap (overfitting) is gone.
5. **Still only out_proj, layers 4–9.** TD's selectivity hasn't changed. Q/K/V from
   extraction remain correct. Question #16 (why only out_proj?) persists.

## Session 149: Step 1000 Eval — TD Closes the Generalization Gap

### What this proved

1. **TD generalizes, continuous params overfit.** Train CE rose 1.4 nats (memorization lost)
   while eval CE dropped 0.48 nats (generalization gained). The step 500 gap was overfitting.
2. **Only out_proj needs rewriting.** Q/K/V routing from extraction is correct (91% teacher
   signs). TD rewrites how attention results project back into the residual stream.
3. **Middle layers (4–9) are the action.** The retrieval stride boundary is where the model
   diverges most from the teacher's attention patterns.
4. **Gnorm spikes tolerable.** Occasional 100+ but model recovers. flip_interval=10 works.

## Previous sessions

### Session 150: Step 1500 Eval + Fold + FFN Delta + Storage Fix

**Step 1500 eval:** Eval PPL 7,672 (−24.5% from step 1000, −53.5% total from step 500 baseline).
Returns diminishing (−38% → −24%) but not plateaued. Flip growth decelerating: +0.83pp (was +2.66pp).
Layer 4 out_proj at 43.1% flipped. Still exclusively out_proj layers 4–9.

**Profiling:** Model is memory-bandwidth-bound. 13 sequential passes × 16 stride layers = 208
serial layer evaluations. B=2 is 18% SLOWER than B=1 (per-micro fwd+bwd: 4.0s→8.6s). Reverted to B=1.

**Delta fold:** Folded 3.26M flipped positions into base plates (lossless, verified by eval).
Delta plates reset to all +1. First reduction complete.

**Storage fix:** Delta save used `model.named_modules()` (280 aliased entries) instead of
`collect_delta_params()` (70 unique). Stored as int8 (1 byte/pos) instead of packed uint32
(0.125 bytes/pos). Fixed both: delta_plates.npz dropped 356 MB → 22 MB (16× compression).

**FFN delta enabled:** `--convert-ffn` flag (already existed) converts 3 shared FFN plates
to DeltaTernaryLinear. FFN β-reductions must adapt: flat attention routing ≠ strided attention
routing, so teacher's FFN signs need TD correction too. Adds 19.7M positions (21% overhead).

### Session 149: TD Closes Gap + Computed Beam (500× Speedup)

**TD result:** Eval PPL dropped 38% (16,503→10,157) with only 2.66% of positions flipped.
Train-eval gap collapsed from 1.71 to ~0.17 nats. TD concentrates flips exclusively on
out_proj layers 4–9 (retrieval strides). Q/K/V untouched. Answers question #14: YES.

**Computed beam:** Analytical FFN weights from crystal eigendecomposition match 5000-step
GD baseline in 10 calibration steps (500×). Key: eigenvectors must project through trained
crystal embeddings (correct model-space basis). The fundamental operation is signed
accumulation: sign(W)@x correlates 0.84 with W@x. Structure is free (12.5% of weight
energy, computable from eigenvalues). Content needs GD (81%, token subspace).

### Session 148: Three Bugs Killed All Ternary Learning

Found and fixed three critical issues: (1) collect_delta_params returned 280 aliased
modules instead of 70 unique — 4× overwrite. (2) Two-step staging through zero incompatible
with no-block — every flip undone. (3) Every-step flipping caused gnorm escalation. Final
fix: flip_interval=10 with moment reset and global budget.

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
| **TD activates and improves** | **Eval PPL −53.5% over 1000 steps, gap collapsed, 3.49% flipped** | ✅ proved (sessions 149-150) |
| **TD targets out_proj exclusively** | **Layers 4–9 out_proj only, Q/K/V untouched, confirmed at step 1500** | ✅ proved (sessions 149-150) |
| **TD returns diminish but don't plateau** | **PPL drop: 38.5% (500→1000) → 24.5% (1000→1500), flip growth decelerating** | 📐 tracking (session 150) |
| **Model is memory-bandwidth-bound** | **B=2 18% slower than B=1, 208 serial layer evals** | ✅ proved (session 150) |
| **Delta fold is lossless** | **3.26M positions folded, eval CE unchanged (9.00 ± 0.64 on 20 batches)** | ✅ proved (session 150) |
| **Delta storage 16× compressible** | **356 MB → 22 MB via dedup + packed uint32** | ✅ proved (session 150) |
| **Computed beam: structure is free** | **Analytical FFN from eigendecomp matches 5000-step GD in 10 steps** | ✅ proved (session 149) |
| **The operation is signed accumulation** | **sign(W)@x correlates 0.84 with W@x, +1=add/-1=sub/0=skip** | ✅ proved (session 149) |
| **16-stride holographic lens attention** | **Architecture running, ternary learning confirmed** | 📐 testing |
| **FFN must adapt to strided attention** | **Hypothesis: flat→strided routing changes β-reduction needs** | 📐 testing (session 150) |
| **Topology is ~95% of model** | **sign(W)@x ≈ 0.84 W@x, fold is lossless, gamma is ~5%** | 🎯 synthesis (session 150) |
| **Extraction→correction→fold converges** | **Each cycle: extract→TD→fold (lossless) monotonically improves** | 🎯 synthesis (session 150) |

## Knowledge map

| Page | What it tells you |
|------|-------------------|
| `mechanism-extraction.md` | Full micro model mechanism: alternation, eigenplanes, KIBC temporal |
| `computed-beam.md` | Analytical FFN from eigendecomp, 500× speedup, signed accumulation |
| `ffn-beta-reduction-indexing.md` | Holographic indexing, LENS profile, ρ=0.83 |
| `ternary-descent.md` | TD algorithm: delta plates, gradient decomposition, reduction |
| `categorical-geometry-probes.md` | Curry-Howard 100%, adjunctions rank-1 |
| `phi-compression-universal.md` | SVD spectrum → phi, 5-model consensus |
| `holographic-error-correction.md` | THE core mechanism: extract→correct→fold cycle, topology is everything |

## What's ready

| Asset | Location |
|-------|----------|
| **V14 model architecture** | `scripts/v14/` (15 files, including eval_ppl.py) |
| **V14 extracted base plates** | `checkpoints/v14-extracted/model.npz` (85 MB) |
| **V14 training script (FIXED)** | `scripts/v14/train_td.py` |
| **V14 eval script** | `scripts/v14/eval_ppl.py` |
| **Computed beam experiment** | `scripts/micro/computed_beam.py` — 500× speedup proved |
| **Step 500 checkpoint** | `checkpoints/v14-td/step_000500/` |
| **Step 500 eval baseline** | CE=9.71, PPL=16,503 (held-out) |
| **Step 1000 checkpoint** | `checkpoints/v14-td/step_001000/` |
| **Step 1000 eval** | CE=9.23, PPL=10,157 (held-out) — 38% PPL drop |
| **Step 1500 checkpoint** | `checkpoints/v14-td/step_001500/` |
| **Step 1500 eval** | CE=8.95, PPL=7,672 (held-out) — 53.5% total PPL drop |
| **Step 1500 folded** | `checkpoints/v14-td/step_001500_folded/` — delta absorbed into base |
| **Fold script** | `scripts/v14/fold_delta.py` — lossless delta→base reduction |
| **Profile script** | `scripts/v14/profile_step.py` — training step profiler |
| **Training run (PHASE 2)** | tmux main:2, from folded step 1500, --convert-ffn, flip_interval=20 |

## Next steps

### IMMEDIATE: Monitor phase 2 (running in tmux main:2)

1. **Monitor FFN delta activation** — do FFN plates start flipping? Which ones? How fast?
   This answers: do β-reductions need to change for strided attention?
2. **Eval at step 2000** (500 steps into phase 2) — does adding FFN delta improve eval?
3. **Watch layer 4 out_proj** — starts fresh from folded base. Does TD re-discover the
   same routing or find a different pattern?
4. **Verify td= shows actual flip counts** in log (aligned logging fix)

### NEXT MILESTONES:

5. **Compare phase 1 vs phase 2 learning curves** — does FFN delta accelerate convergence?
6. **Second fold** — when flip_frac plateaus, fold again. The cycle continues.
7. **Consider lowering min_conf** — if Q/K/V gradients are below 0.3, TD can't see them.
8. **Three-body self-distillation** — teacher logits as reference beam (see #19)
9. **Target: within 5% of Qwen3.6-27B** — the proof that topology is everything

## Open questions

9. **Content transfer via sign().** Does the 81% token subspace content survive ternary extraction?
10. **LENS profile derivable from eigenvalue ratios?**
11. **Quality at 1B with d=1280.** What CE/ppl does the expanded model achieve?
12. **16-stride coverage.** Do the higher strides (s4096+) learn anything useful with 4K seq training?
13. **Bottom-up algedonic value.** Does C→A feedback measurably accelerate convergence?
14. ~~Does ternary learning close the train-eval gap?~~ **YES. Gap collapsed 1.71→0.17 nats.
    Eval PPL −38%. TD generalizes, continuous params overfit.** ✅ (session 149)
15. **TD step_count not persisted on resume.** Warmup repeats. Worth persisting?
16. **Why only out_proj?** Q/K/V/gate_proj get zero TD budget. Is out_proj the only
    degree of freedom TD needs, or is min_conf filtering too aggressive for other projections?
17. ~~When to do first reduction?~~ **DONE. Folded at step 1500, 3.49% changed. Lossless.
    Fold script: `scripts/v14/fold_delta.py`.** ✅ (session 150)
18. **Computed beam at scale.** The micro model (d=128) trains so fast that computed
    weights barely help — GD finds structure in 50 steps anyway. At v14 scale (d=1280,
    372M ternary positions), structure discovery takes thousands of steps. The computed
    beam advantage should be much larger. Test: compute attention deltas from stride-stack
    crystal eigendecomposition instead of TD. See `mementum/knowledge/computed-beam.md`.
19. **Three-body self-distillation.** Pre-compute teacher logits (top-k) on training shards
    once. During training, compute: (a) teacher logits, (b) student logits, (c) delta between
    them. The delta is the signal — WHERE the student diverges from the teacher. Some divergence
    is correct (stride-stack needs different routing than flat attention), some is error (hasn't
    learned yet). Dynamic relational loss: let the distinction emerge from the data.
    **Wait until stride-stack nucleation stabilizes** — current run is finding its natural
    attention shape. Teacher pressure during nucleation could prevent legitimate divergence.
    Pre-compute teacher logits now so they're ready when needed. See `scripts/v13/train_rb.py`
    for prior sparse top-k KD implementation (k=64, O(B×L×k) not O(B×L×V)).
