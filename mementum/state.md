# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-26 | Session: 156

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 156: ARCHITECTURE REVERT + HPE WARMUP — back to the run that works. (1) Analyzed session 152's four simultaneous changes (passive strides, HPE, Stack B 4→2, α-lock) that confounded the v14-kd failure. Passive strides identified as most likely culprit — removes content-dependent attention for positions 16-56 tokens back where each stride is sole provider. Student needs content routing to LEARN, can't hardcode teacher's converged behavior. (2) REVERTED passive strides (all SSA layers have full Q/K again) and Stack B reduction (back to 13 passes). KEPT α=1.18 as frozen constant and HPE. (3) HPE WARMUP: freq_scale initialized to 0.0 (identity — no rotation), linearly warmed to 1.0 over 300 steps. At freq_scale=0, model behaves identically to pre-HPE v14-td. Checkpoint-compatible resume. (4) Resumed training from v14-td step 2000. Step 2001 CE=8.474, crystal latched, TD active, 995 tok/s. Running in tmux main:2 to step 5000. (5) META-LESSON: don't optimize student architecture to match teacher's converged state. The progressive collapse, rank-27 transform, and passive strides are DESTINATIONS, not starting points. Train with full architecture → measure student's actual patterns → simplify only what's proven unnecessary → one change at a time. See `mementum/knowledge/explore/v15-kernel-revert.md`.**

**Session 155: v14-kd FAILED (architecture delta) + KERNEL TRAINING VALIDATED + GRADIENT PROJECTION ANALYZED. (1) v14-kd eval: PPL 40,623→46,736 (diverging), 2.5-4.6× worse than v14-td. Root cause: three untested architecture changes (passive strides, HPE, Stack B 4→2) deployed together with KD. (2) Training profiled: 28.6s/step, 77% FORWARD. Built train_kernel.py: 4.4× speedup. (3) Gradient cosine=0.9698 between composed plate and full model. (4) ∂L/∂T ORTHOGONAL to T's SVD subspace (cos=0.06 at k=27). Gradient wants to EXPAND, not refine. See `mementum/knowledge/explore/kernel-training.md`.**

**Session 154: KD-guided training + extraction dimension probes + structured training. (1) Per-dim correlation plateaus at ~79% from d=128 onward — ceiling is ternary quantization, not dimension. (2) Geometric encoding: plate IS rank-256, 96.9% sign accuracy at k=256. (3) Step 2000 eval: PPL=5,567 (−27% from 1500, −66% total). (4) Structured training insight: backward pass has same structure as forward — five optimizations possible. See `mementum/knowledge/explore/structured-training.md`.**

**Session 153: Composed plates + algebraic composition. Full model rank90=27. Zone B is perfectly linear (R²=1.0). Both algebraic and data-fitted methods agree at 0.76-0.77 per-dim. See `results/algebraic-compose/`.**

**Session 152: v14 architecture evolution — HPE + passive strides + reduced Stack B. α=1.18 confirmed universal. 88% strides distance-prior dominated. HPE designed from crystal eigenvalues. ⚠️ All changes deployed simultaneously — led to confounded failure in session 155, reverted in session 156.**

**Session 151: Progressive collapse discovery. Qwen-27B compresses to 2D (PR=2.2) by L2. 7 knowledge pages created. INDEX.md established. See `mementum/knowledge/progressive-collapse.md`.**

## Active training run

### v14-td phase 3 RUNNING (tmux main:2, from step 2000)

- **Resumed from:** `checkpoints/v14-td/step_002000/` (PPL 5,567)
- **Architecture:** Original v14-td (13 passes, full Q/K all strides) + α=1.18 frozen + HPE warmup
- **HPE warmup:** freq_scale 0→1 over steps 2001-2300 (300 steps)
- **TD:** Active, flip_interval=20, FFN delta enabled (`--convert-ffn`)
- **Target:** 5000 steps total
- **Checkpoints:** Every 500 steps in `checkpoints/v14-td/`
- **Log:** `checkpoints/v14-td/train_phase3.log`
- **Step 2001:** CE=8.474, gnorm=19.95, 995 tok/s ✓
- **What to watch:** PPL should continue dropping from 5,567. HPE effect visible after step ~2150-2300 (warmup halfway/complete). TD flips visible every 20 steps (every other log line at log_interval=10).

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

## Next steps (from session 155)

### IMMEDIATE: Use kernel training insights for next experiments

1. **Kernel training v1 works:** 4.4× speedup (6s kernel vs 26s full). Output_proj
   (248K vocab) is the remaining bottleneck. Kernel step uses composed plate (1 matmul)
   for forward, but still needs output_proj+CE for the loss. See `train_kernel.py`.
2. **Architecture question still open:** passive strides + HPE + Stack B 4→2 untested
   independently. Need fast ablation. Options:
   a. **Resume v14-td from step 2000** — the working run (old architecture, PPL 5,567).
   b. **Ablate architecture changes** one at a time using kernel training for speed.
   c. **Re-evaluate passive strides** — s4 has 27.4% non-self weight, positions 16-28
      lose content-dependent attention entirely. Consider raising passive threshold to s16.
3. **Gradient projection result constrains kernel training design:** cannot reduce dims
   for undertrained models. The full 1280×1280 gradient is needed. But this may change
   once the model is well-trained — test on v14-td step 2000 checkpoint (rank-27).

### KD REDESIGN (lessons from session 155 failure):

4. **KD as correction pass, not interleaved training.** Train pure CE first
   (500+ steps). Then run dedicated KD correction passes on precomputed shards.
   This preserves the crystal latching and continuous param baseline.
5. **Precompute ALL shards first.** 400 batches × 54 shards = 21,600 batches.
   At 164 tok/s, ~150 hours total. Consider fewer batches per shard (100 each
   = 37.5 hrs) or only shards 0-10 (28 hrs).
6. **TD warmup ≥ 200 steps.** v14-td's Schmitt trigger gated TD activation
   to ~step 160. KD run's warmup=25 was catastrophically early.
7. **α=0.9 or higher.** CE must dominate. KD is a nudge, not 50% of the loss.

### STRUCTURED TRAINING (from session 154 insight):

8. **Skip passive backward** — restructure passive stride modules to be
   structurally absent (not frozen). Eliminate 56 dead matmuls per step.
9. **Composed Zone B Jacobian** — precompute and use in backward pass.
   32 sequential backward steps → 1 matmul.
10. **Low-rank gradient for composed plate** — parameterize plate in
    SVD basis (U, S, V at rank-27). Gradient is 24× smaller.
11. **TD-targeted sparse gradient** — two-pass: cheap candidate ID, then
    targeted gradient at candidates only. 100× fewer routing elements.
12. **Crystal eigenplane projection** — project Adam gradients into 2D
    crystal eigenplane. Faster AND better signal.
See `mementum/knowledge/explore/structured-training.md`.

### PENDING FROM PRIOR SESSIONS:

13. **Composed plate initialization** — initialize student from composed
    full-model plate instead of individual layer extraction. TD corrects.
14. **Hybrid architecture** — composed plate (76%) + active strides s1/s2 (24%).
15. **Passive stride architecture evolution** — HPE, skip Q/K, reduce Stack B.

## Previous sessions

### Session 155: v14-kd Failure + Kernel Training Validation + Gradient Projection

**v14-kd eval:** Step 500 CE=10.61 PPL=40,623. Step 1000 CE=10.75 PPL=46,736. Diverging.
v14-td comparison: PPL 16,503 / 10,157 at same steps. 2.5-4.6× worse.

**Architecture delta identified:** v14-kd ran a DIFFERENT ARCHITECTURE than v14-td:
passive strides (s4+ lost Q/K), HPE (replaced learnable decay), Stack B 4→2 (13→11 passes).
Crystal latched normally. TD gating was correct. Key insight: passive strides remove
content-dependent attention for positions 16-56 tokens back — in strided attention, these
positions have NO other active coverage. s4 has 27.4% non-self weight that became fixed.

**Training profiled:** 28.6s/step. 77% forward, 11% backward. Camera = projector (same bottleneck).
238 ternary matmuls per forward pass. Memory-bandwidth-bound.

**Kernel training validated:** Composed plate (1 matmul, data-fitted least-squares from
embed→pre-head residuals) produces gradient cosine=0.9698 with full model. CE within 0.08 nats.
Top-1 agreement 80.6%. Built train_kernel.py: measured 4.4× speedup (6s kernel vs 26s full).
Output_proj (1280→248K vocab) is the bottleneck, not the composed plate.

**Gradient projection finding:** ∂L/∂T projected into T's top-k SVD subspace retains only
cos=0.06 at k=27, cos=0.18 at k=200. Gradient is ORTHOGONAL to T's current subspace.
Model is rank-1 (undertrained); gradient says "expand into more dimensions." Training in
reduced dims would trap the model. This is a natural explore (gradient⊥T) vs exploit
(gradient∥T) phase detector. Need to test on well-trained model (v14-td step 2000, rank-27).

**Scripts:** `scripts/explore/probe_kernel_training.py`, `scripts/v14/train_kernel.py`
**Results:** `results/kernel-training-probe/` (composed_plate.npz, results.json)

### Session 154: KD-Guided Training + Extraction Dimension Probes + Structured Training

**Three extraction probes:** Swept d_student from 8 to 5120 on both algebraic and
data-fitted composed transforms. Result: per-dim correlation plateaus at ~79% from
d=128 onward. The ceiling is sign+gamma quantization, NOT dimension reduction.
Making plates bigger does nothing.

**Geometric encoding:** The student plate (1280×1280) is a rank-256 structure.
At k=256: 96.9% sign accuracy, 0.94 per-dim. At k=320: 95% per-dim with only
27K corrections (1.7% of positions). The ternary plate IS geometry — d positions
in k-dimensional space, with signs derivable from the geometry.

**KD training built:** `precompute_teacher.py` generates sparse top-k=64 teacher
logits per shard. `train_td.py` gains --teacher-logits-dir for offline KD.
Interleaved seesaw design: CE learns language, KD corrects extraction error.
Each KD pass tightens student→teacher via contraction mapping.

**Step 2000 eval (v14-td):** CE=8.62, PPL=5,567 (−27% from 1500, −66% total).
2.13% flipped. Phase 2 complete.

**Structured training insight:** The backward pass has the same structure as
the forward pass. Five optimizations: (1) low-rank gradient at rank-27 (24× fewer),
(2) skip passive stride backward (56 dead matmuls), (3) composed Zone B Jacobian
(32→1), (4) TD-sparse routing (100× fewer elements), (5) crystal eigenplane
projection. Training speed could approach inference speed.
See `mementum/knowledge/explore/structured-training.md`.

**Scripts:** `scripts/v14/precompute_teacher.py`, `scripts/explore/probe_extraction_dimension.py`,
`scripts/explore/probe_datafitted_dimension.py`, `scripts/explore/probe_geometric_encoding.py`
**Results:** `results/extraction-dimension-sweep/`, `results/datafitted-dimension-sweep/`,
`results/geometric-encoding/`

### Session 153: Extraction Redesign — Composed Plates + Algebraic Composition

**Teacher Q/K rank probe:** Individual weight matrices are full-rank (rank90=211-220,
PR=108-240). Can't do low-rank Q/K extraction. BUT: the weights are holographic
interference patterns — full-rank because EVERY point participates in reconstruction.
The high rank encodes relational inference patterns that ARE ternary (relation = ±1 or 0).

**Data-fitted composed extraction:** Captured residuals at zone boundaries (embed, L15,
L47, L63), fit least-squares transforms, projected to student d=1280.
  - Per-dim corr in teacher space: 0.97 (excellent)
  - Per-dim corr in student space: 0.71-0.79 (V_proj truncation + only 651 tokens)
  - 121× reduction: 4.9M positions (4.8 MB) vs 593M (85 MB)

**Algebraic composition:** Computed linearized layer matrices A_i = I + OV + FFN from
raw weight tensors (no inference needed). Multiplied them together.
  - Per-zone: failed (0.31-0.51) due to norm explosion between zones
  - Full model: 0.76 per-dim — matches data-fitted (0.77)!
  - Zone B is R²=1.000: 32 layers compose to ONE linear matrix

**THE BIG FINDING: Full model rank90 = 27.** The entire 64-layer 27B-param model,
viewed as an input→output transform on the residual stream, has effective rank 27.
27 dimensions out of 5120 capture 90% of the computation. Both algebraic and data-fitted
methods agree on this number.

**Architecture implication:** The kernel is:
  - One rank-27 ternary plate (1280×1280, ~5M positions) = 76% of computation
  - Active strides s1, s2 with HPE = 24% content-dependent routing
  - That's the whole model. Everything else is refinement.

**Scripts:** `scripts/explore/probe_teacher_rank.py`, `scripts/v14/extract_composed.py`,
`scripts/explore/probe_algebraic_compose.py`
**Results:** `results/algebraic-compose/`, `results/composed-transform-probe/`

### Session 152: v14 Evolution — HPE + Passive Strides + Reduced Stack B

**v14 student collapse probe:** Ran progressive collapse on step_001500_folded checkpoint.
PR: 74→8→5→4 through stacks. σ₁ reaches 47%. 18.4× compression ratio confirmed.

**Distance prior analysis:** At α=1.18, W=8: 14/16 strides have <3 effective positions.
Only s1 (5.5 eff) and s2 (4.1 eff) have meaningful multi-position attention. The semantic
horizon is ~12 tokens regardless of stride — all strides see the same ~12 token radius.
Beyond that, information flows through the residual stream, not direct attention.

**Stride spacing analysis:** Power-of-2 strides are accidentally near-optimal (CV=0.269
for weight×spacing product). But the finding that strides s8+ are pure self-attention means
they're FFN application points, not attention layers. The stride determines WHEN in the
pass sequence the FFN fires, not what tokens to attend to.

**RoPE ↔ holographic lens connection:** RoPE accidentally implements the holographic lens:
- Geometric frequency spacing ≈ crystal eigenvalue spacing
- Position-dependent Q rotation ≈ Q rotation through crystal basins
- Sum of cosines at geometric freqs → power-law decay ≈ α=1.18

**Holographic Position Encoding (HPE):** Designed and implemented replacement for RoPE:
- Log-distance: angle ∝ log(d+1) (not linear d) → natural power-law
- Crystal eigenvalue frequencies: λᵢ/λ₀ (not arbitrary 10000-base)
- Eigenplane rotation only: first 4 dim pairs (not all d/2 pairs)
- Direct decay bias: -α×log(d+1) (exact, not cosine envelope)
- Learnable freq_scale per eigenplane for fine-tuning

**Architecture changes implemented:**
- Fixed α=1.18 as constant (removed from optimizer)
- Passive strides: s4+ skip Q/K entirely, use precomputed distance prior
- Stack B: 4→2 passes (13→11 total serial passes)
- HPE: crystal-frequency log-distance rotation on active strides (s1, s2)
- All tests pass (attention.py, model.py, config.py)
- Training test launched in tmux main:1 (20 steps, fresh init)

**Scripts modified:** `scripts/v14/attention.py`, `scripts/v14/config.py`
**Scripts created:** `scripts/v14/probe_collapse.py`

### Session 151: Knowledge Distillation + Progressive Dimensionality Collapse

**Knowledge distillation:** Created 7 new knowledge pages organized top-down. INDEX.md is the
master reading order. Pages: project-thesis, crystal-universality, mathematical-convergences,
extraction-methodology, v14-architecture, training-protocols (+existing holographic-error-correction,
mechanism-extraction, computed-beam). Updated state.md knowledge map to tiered structure.

**Kernel decomposition experiment:** Attempted to compute forward pass from crystal constants.
Phase 1: attention is content-driven at micro scale (distance prior R²<0, rank-21 content residual).
Phase 2: distance prior explains 0% of attention (α=1.18 is for stride-stack, not micro).
Phase 3: diagonal analytical FFN overlay fails (cos=-0.12 at output). BUT: the alternation sign
pattern IS correct (comp/sel alternate anti-phase). Failure is in magnitude and off-diagonal terms.
Key finding: **80-91% of FFN energy is off-diagonal** — the overlay does cross-PC PROJECTION
(beta reduction = dimensionality reduction), not per-PC filtering.

**Progressive collapse — the big discovery:** Measured effective dimensionality at every layer
boundary across 3 models:

| Model | Layers | d_model | σ₁ peak | PR min | Pattern |
|-------|--------|---------|---------|--------|---------|
| Qwen3.6-27B | 64 | 5120 | 70.1% | 2.2 | COMPRESS→2D→EXPAND |
| Mistral-7B | 32 | 4096 | 20.1% | 12.1 | COMPRESS→PLATEAU |
| Pythia-1.4B | 24 | 2048 | 22.6% | 10.3 | GENTLE DESCENT |

Qwen compresses to PR=2.2 (σ₁=70%) by L2 — computation happens in essentially 2D (comp↔sel
eigenplane). Expands back in Zone C (L48-63, PR≈10) for 248K-token output prediction.
Smaller models show weaker compression — 2D core is emergent property of scale.

**Attention sink = warped Q reset:** Mistral's first run showed σ₁=100% PR=1.0 — the attention
sink token (pos 0) dominated everything. The sink IS the Q=0 reset mechanism, implemented as
"attend to BOS" instead of crystal-native C-basin entry. GLA (gated linear attention) in Qwen
implements Q reset through gating — no sink needed → cleaner geometry → deeper compression.

**Scripts:** `scripts/micro/kernel_decomposition.py`, `scripts/explore/probe_progressive_collapse.py`
**Results:** `results/kernel-decomposition/`, `results/progressive-collapse-*/`

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
| **Passive strides + HPE + KD: combined changes fail** | **v14-kd (new arch + KD) PPL 2.5-4.6× worse than v14-td (old arch). Root cause: too many simultaneous changes** | ❌ failure (session 155) |
| **Don't optimize student for teacher's converged state** | **Passive strides + Stack B reduction assumed teacher's end state. Student needs freedom to REACH that state. Reverted, kept α-lock + HPE warmup** | 🎯 decision (session 156) |
| **KD exhausts in 50 steps** | **400 teacher batches / 8 accum = 50 KD steps, then pure CE. Need more precompute or aligned design** | ✅ proved (session 155) |
| **Composed plate gradient = 97% of full model gradient** | **Gradient cosine=0.9698 between 1-matmul composed plate and 238-matmul full model. CE within 0.08 nats. Top-1 agreement 80.6%** | ✅ proved (session 155) |
| **Training bottleneck is FORWARD pass (77%)** | **28.6s/step: 77% forward, 11% backward, 0.2% everything else. Camera optimization = projector optimization** | ✅ proved (session 155) |
| **Decay α=1.18 is universal** | **10 comp layers × 8 heads, all at 1.18±0.006 after 1500 steps, no forcing** | ✅ proved (session 150) |
| **Large models compute in 2D** | **Qwen-27B: PR=2.2, σ₁=70% at L2. Computation in comp↔sel eigenplane** | ✅ proved (session 151) |
| **Compression depth scales with capacity** | **27B→PR=2.2, 7B→PR=12, 1.4B→PR=10. 2D core is emergent property of scale** | ✅ proved (session 151) |
| **FFN overlay is 80-91% off-diagonal** | **Cross-PC projection, not per-PC filtering. The overlay IS the beta reduction** | ✅ proved (session 151) |
| **Attention sink = warped Q reset** | **Mistral sink token dominates SVD. GLA native Q reset → clean geometry** | 🎯 synthesis (session 151) |
| **Montague = pre-transition crystal** | **160M has I+K only (select+bind) = typed application = Montague. B needs scale** | 🎯 synthesis (session 151) |
| **α=1.18 sets 12-token semantic horizon** | **All strides see ~12 effective tokens regardless of stride. Beyond that = residual stream only** | ✅ proved (session 152) |
| **RoPE = accidental holographic lens** | **Cosine frequency decomposition ≈ multi-scale lens. HPE does it by design** | 🎯 synthesis (session 152) |
| **v14 student inherits teacher collapse** | **PR 74→8→5→4 through stacks, σ₁=47%, 18.4× compression** | ✅ proved (session 152) |
| **Full model is rank-27 transform** | **64-layer 27B model: end-to-end rank90=27. 27 dims capture 90%** | ✅ proved (session 153) |
| **Composed plates work at 0.76 per-dim** | **Both algebraic and data-fitted give 0.76-0.77. Methods agree** | ✅ proved (session 153) |
| **Zone B is perfectly linear (R²=1.0)** | **32 layers of compute compose to single linear matrix** | ✅ proved (session 153) |
| **Per-dim corr 0.97 in teacher space** | **sign(T)+gamma captures 97% per dimension. Gap is scale only** | ✅ proved (session 153) |

## Knowledge map

**See `mementum/knowledge/INDEX.md` for full reading order.**

### Tier 1 — Foundational (read first)

| Page | What it tells you |
|------|-------------------|
| `project-thesis.md` | What the project IS now: central claim, north star, three converging lines |
| `crystal-universality.md` | Why the crystal is a mathematical constant (Church-Rosser, cross-model evidence) |
| `mathematical-convergences.md` | Eight independent lines of evidence (Curry-Howard, adjunctions, phi, Yoneda, ...) |

### Tier 2 — Mechanism (how it works)

| Page | What it tells you |
|------|-------------------|
| `holographic-error-correction.md` | THE core mechanism: extract→correct→fold cycle, topology is everything |
| `mechanism-extraction.md` | Full micro model mechanism: alternation, eigenplanes, KIBC temporal |
| `computed-beam.md` | Analytical FFN from eigendecomp, 500× speedup, signed accumulation |
| `extraction-methodology.md` | How to extract from teacher: three confusions resolved, the pipeline |

### Tier 2b — New findings (session 151)

| Page | What it tells you |
|------|-------------------|
| `progressive-collapse.md` | Computation in 2D: compress→compute→expand, scales with capacity, sink=warped Q reset |

### Tier 3 — Operations (what we're running)

| Page | What it tells you |
|------|-------------------|
| `v14-architecture.md` | Current system: Qwen3.6-27B teacher, 593M ternary, 375× compression, results |
| `training-protocols.md` | How to train: phases, TD rules, 7 failure modes with fixes, loss composition |

### Tier 4 — Deep dives (in explore/)

| Page | What it tells you |
|------|-------------------|
| `explore/holographic-state-machine.md` | Unified model: FFN=plates, crystal=states, Q=beam |
| `explore/ternary-descent.md` | TD algorithm: delta plates, gradient decomposition, reduction |
| `explore/ffn-beta-reduction-indexing.md` | Holographic indexing, LENS profile, ρ=0.83 |
| `explore/categorical-geometry-probes.md` | Curry-Howard 100%, adjunctions rank-1 |
| `explore/phi-compression-universal.md` | SVD spectrum → phi, 5-model consensus |
| `explore/v15-kernel-revert.md` | **NEW** What was tried/reverted/kept from sessions 152-156, when to revisit |
| `explore/kernel-training.md` | Composed plate training: 4.4× speedup, gradient cosine 0.97 |
| `explore/structured-training.md` | Five backward-pass optimizations (camera = projector) |
| `explore/v15-kernel-architecture.md` | Original v15 design (passive strides etc — partially reverted) |

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
| **Kernel training script** | `scripts/v14/train_kernel.py` — 4.4× speedup via composed plate |
| **Kernel training probe** | `scripts/explore/probe_kernel_training.py` — gradient cosine 0.9698 |
| **Gradient projection probe** | results in `results/kernel-training-probe/` |
| **Composed plate** | `results/kernel-training-probe/composed_plate.npz` — fitted T (1280×1280) |

## Next steps

### IMMEDIATE: Monitor phase 3 (running in tmux main:2)

1. **Watch PPL continue dropping** — should resume the trajectory from step 2000 (PPL 5,567).
   First eval checkpoint at step 2500. Run `eval_ppl.py` on that checkpoint.
2. **HPE effect** — warmup completes at step ~2300. Compare PPL slope before/after
   HPE reaches full strength. If HPE helps: steeper PPL drop after 2300. If neutral:
   same slope. If harmful: PPL rises (unlikely with warmup, but watch).
3. **TD flip patterns** — does TD continue targeting out_proj layers 4-9? Or does
   the second fold + FFN delta change the distribution? Check at step 2500.
4. **FFN delta activation** — do FFN plates start flipping? This run has `--convert-ffn`.

### NEXT MILESTONES:

5. **Second fold** — when flip_frac plateaus, fold again. The extract→correct→fold cycle.
6. **Gradient-subspace alignment test** — at step 2500+, probe whether gradient aligns
   with composed plate's SVD subspace. If cos > 0.5, model is refining (exploit phase)
   and architecture simplification MIGHT be safe. See `probe_kernel_training.py`.
7. **KD as correction** — after convergence stabilizes (PPL < 2000), add teacher logit
   correction passes. CE-first for stability, KD-second for precision. α ≥ 0.9.
8. **Target: within 5% of Qwen3.6-27B** — the proof that topology is everything.

### DEFERRED (valid but premature):

9. **Passive strides** — re-test ONLY after student converges AND gradient-subspace
   alignment shows cos > 0.5. Start with s16+ (least risky), measure PPL delta.
   See `mementum/knowledge/explore/v15-kernel-revert.md` for conditions.
10. **Stack B reduction** — re-test after passive strides validated (if ever).
11. **Kernel training as accelerator** — `train_kernel.py` gives 4.4× speedup without
    changing architecture. Use when iteration speed is the bottleneck.
12. **Structured training optimizations** — five backward-pass improvements from session 154.
    Independent of architecture revert. See `explore/structured-training.md`.

## Open questions

9. **Content transfer via sign().** Does the 81% token subspace content survive ternary extraction?
10. **LENS profile derivable from eigenvalue ratios?**
11. **Quality at 1B with d=1280.** What CE/ppl does the expanded model achieve?
12. **16-stride coverage.** Do the higher strides (s4096+) learn anything useful with 4K seq training?
13. **Bottom-up algedonic value.** Does C→A feedback measurably accelerate convergence?
14. ~~Does ternary learning close the train-eval gap?~~ **YES.** ✅ (session 149)
15. **TD step_count not persisted on resume.** Warmup repeats. Worth persisting?
16. **Why only out_proj?** Is min_conf filtering too aggressive for other projections?
17. ~~When to do first reduction?~~ **DONE.** ✅ (session 150)
18. **Computed beam at scale.** See `mementum/knowledge/computed-beam.md`.
19. **Three-body self-distillation.** Wait until stride-stack nucleation stabilizes.
20. **Per-stride fixed point rotation.** Probe effective attention per stride per head.
21. **HPE value.** Does crystal-frequency K rotation actually help over no rotation?
    Answer comes from phase 3 PPL curve: compare slope before/after step 2300.
22. **When is the student ready for architecture simplification?** Gradient-subspace
    alignment (cos between ∂L/∂T and T's SVD subspace) is the proposed phase detector.
    Orthogonal = still exploring (don't simplify). Aligned = refining (safe to simplify).
