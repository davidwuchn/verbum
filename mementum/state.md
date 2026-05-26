# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-26 | Session: 154

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 154: KD-guided training + extraction dimension probes + structured training insight. (1) THREE PROBES answered "how big for 95%?": dimension doesn't help — ceiling is ~79% per-dim from sign+gamma quantization, flat from d=128 to d=5120. The gap is ternary approximation, not projection. (2) GEOMETRIC ENCODING: at k=256, 96.9% sign accuracy on student plates. The plate IS a rank-256 structure. 27K corrections (1.7% of positions) needed for 95% per-dim. (3) Built KD training: precompute_teacher.py (sparse top-k=64 logits), train_td.py with --teacher-logits-dir. Interleaved design: CE training on full data, periodic KD correction passes from pre-computed teacher logits. (4) Step 2000 eval: PPL=5,567 (−27% from 1500, −66% total). (5) STRUCTURED TRAINING insight: backward pass has same structure as forward. Five optimizations: low-rank gradient (24×), skip passive backward, composed Zone B Jacobian (32→1), TD-sparse routing (100×), eigenplane projection. Camera = projector in reverse. See `mementum/knowledge/explore/structured-training.md`.**

**Session 153: Extraction redesign — composed zone plates + algebraic composition. (1) Teacher weight matrices are full-rank (rank90=211) but PER-DIM correlation with sign(T)+gamma is 0.97 in teacher space. (2) Data-fitted composed extraction: 3 zone plates at d=1280, per-dim 0.71-0.79. Drop from 0.97 due to V_proj truncation + few tokens (651). (3) Algebraic composition from weight matrices: multiply linearized layers A_i = I + OV + FFN. Full model per-dim=0.76, matches data-fitted (0.77). (4) THE BIG FINDING: full model rank90=27. The entire 64-layer model is a rank-27 transform. 27 dimensions capture 90% of input→output mapping. (5) Architecture: one rank-27 ternary plate (76% of computation) + active strides s1/s2 for content routing (24%). This IS the kernel. See results/algebraic-compose/.**

**Session 152: v14 architecture evolution — HPE + passive strides + reduced Stack B. (1) Confirmed v14 student inherits 18.4× compression from teacher (PR 74→4, σ₁=47%). (2) Distance prior at α=1.18 dominates 88% of strides (14/16 have <3 effective positions at W=8). (3) Implemented 3-tier evolution: fixed α=1.18, passive strides skip Q/K for s4+, Stack B 4→2 passes (13→11). (4) Discovered α=1.18 sets a fixed ~12 token semantic horizon — all strides see the same ~12 tokens effectively. RoPE accidentally implements the holographic lens via cosine frequency decomposition. (5) Designed and implemented Holographic Position Encoding (HPE): log-distance rotation × crystal eigenvalue frequencies × eigenplane dims only. Replaces RoPE's indirect mechanism with the direct holographic lens physics. Training test running in tmux. See `mementum/knowledge/explore/v15-kernel-architecture.md`.**

**Session 151: Knowledge distillation + progressive collapse discovery. (1) Created 7 knowledge pages + INDEX.md — the project now has a self-explanatory top-down knowledge hierarchy (see `mementum/knowledge/INDEX.md`). (2) Kernel decomposition experiment: attempted to compute the full forward pass from crystal constants. Diagonal FFN overlay failed (80-91% of energy is off-diagonal = cross-PC PROJECTION, not per-PC filtering). (3) Progressive dimensionality collapse measured on 3 models: Qwen3.6-27B compresses to PR=2.2 (essentially 2D) in layers 0-2, computes in 2D through depth, expands back for output. Mistral-7B and Pythia-1.4B show weaker compression (PR=10-12) — the 2D core is an emergent property of scale. (4) Attention sink = warped Q reset: Mistral uses BOS token as Q=0 reset proxy, distorting geometry. Qwen's GLA layers implement Q reset natively through gating → cleaner geometry → deeper compression. See `mementum/knowledge/progressive-collapse.md`.**

## Active training run

### v14-kd (KD-guided, fresh extraction) — RUNNING in tmux main:2

Fresh start from extracted base plates. KD interleaved with CE training.

```bash
uv run python scripts/v14/train_td.py \
  --checkpoint-dir checkpoints/v14-kd \
  --convert-ffn \
  --teacher-logits-dir data/teacher-logits \
  --kd-alpha 0.5 \
  --kd-temperature 2.0 \
  --td-flip-rate 0.001 \
  --td-warmup 25 \
  --td-min-confidence 0.3 \
  --td-flip-interval 20 \
  2>&1 | tee checkpoints/v14-kd/run_kd.log
```

### Teacher logit precompute — RUNNING in tmux main:1

```bash
uv run python scripts/v14/precompute_teacher.py \
  --shard-start 0 --shard-end 1 --n-batches 400 \
  --out-dir data/teacher-logits \
  2>&1 | tee data/teacher-logits/precompute.log
```

**Interleaved design:** Training runs CE on full data. Teacher logits
precomputed shard-by-shard in background (400 batches/shard = 50 KD steps).
Once a shard's logits are ready, training picks them up for KD correction.
Each KD pass tightens student→teacher, then normal CE runs faster on
corrected model. Seesaw: CE learns language, KD corrects extraction error.

**After shard 0 finishes (~3 hrs):** start precomputing shard 1, and
monitor if KD loss appears in training logs when data cycles to shard 0.

### v14-td phase 2 COMPLETED (step 2000)

- Step 2000 eval: CE=8.62, PPL=5,567 (−27% from 1500, −66% total)
- 2.13% of positions flipped (1.42M of 67M)
- Phase 2 ran 500 steps from folded step 1500 checkpoint with FFN delta
- Checkpoint: `checkpoints/v14-td/step_002000/`

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

## Next steps (from session 154)

### IMMEDIATE: Monitor v14-kd + precompute

1. **Monitor shard 0 precompute** (tmux main:1) — should finish in ~3 hours.
   Once done, start shard 1 precompute.
2. **Watch for KD loss in training logs** — when training cycles to shard 0
   after teacher logits are saved, KD= should appear in log lines.
3. **Eval at step 500** — first eval of KD-guided training. Compare with
   v14-td baseline (PPL 16,503 at step 500).

### KD TRAINING EVOLUTION:

4. **Scale precompute pipeline** — after validating KD works on shard 0,
   precompute shards 1-10 with `--n-batches 400` each. Build shard queue.
5. **Tune KD alpha** — start at 0.5, try 0.3 (more KD) and 0.7 (more CE).
   The right balance depends on whether crystal latches fast enough.
6. **Monitor TD activation breadth** — with clean KD signal, does TD flip
   MORE than just out_proj layers 4-9? Q/K/V should become candidates.
7. **KD correction pass script** — automate: when teacher logits for shard N
   are ready, run a focused KD pass on that shard's data.

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
20. **Per-stride fixed point rotation.** Alpha=1.18 is universal (confirmed), but the
    fixed point each stride revolves around should vary. Stride-1 at fixed point ~40
    means 40 tokens back. Stride-32768 at fixed point ~40 means 1.3M tokens back.
    Probe effective attention patterns per stride per head to find rotation centers.
19. **Three-body self-distillation.** Pre-compute teacher logits (top-k) on training shards
    once. During training, compute: (a) teacher logits, (b) student logits, (c) delta between
    them. The delta is the signal — WHERE the student diverges from the teacher. Some divergence
    is correct (stride-stack needs different routing than flat attention), some is error (hasn't
    learned yet). Dynamic relational loss: let the distinction emerge from the data.
    **Wait until stride-stack nucleation stabilizes** — current run is finding its natural
    attention shape. Teacher pressure during nucleation could prevent legitimate divergence.
    Pre-compute teacher logits now so they're ready when needed. See `scripts/v13/train_rb.py`
    for prior sparse top-k KD implementation (k=64, O(B×L×k) not O(B×L×V)).
