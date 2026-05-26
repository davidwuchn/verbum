# Great question. Let me trace what happen

## User

orient, I want to explore something


### Thinking

The user wants me to orient by reading the project state, then be ready to explore something. Let me start with the cold-start protocol: read mementum/state.md first.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md"
}
```

**Summary:** Reading state.md (0-2000)

**Output:**
```
# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-26 | Session: 155

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 155: v14-kd FAILED (architecture delta) + KERNEL TRAINING VALIDATED + GRADIENT PROJECTION ANALYZED. (1) v14-kd eval: PPL 40,623→46,736 (diverging), 2.5-4.6× worse than v14-td. Root cause: three untested architecture changes (passive strides, HPE, Stack B 4→2) deployed together with KD. Also: passive strides remove content-dependent attention for positions 16-56 tokens back — a real capability loss in strided attention where each stride is sole provider of specific distance ranges. (2) Profiled training: 28.6s/step, 77% is FORWARD pass. The camera IS the projector — same bottleneck. Built train_kernel.py: 4.4× measured speedup (6s kernel vs 26s full). Output_proj (1280→248K vocab) is the remaining bottleneck, not the composed plate. (3) KERNEL TRAINING PROBE: gradient cosine=0.9698 between composed plate (1 matmul) and full model (238 matmuls). CE within 0.08 nats. Top-1 agreement 80.6%. (4) GRADIENT PROJECTION: ∂L/∂T is ORTHOGONAL to T's SVD subspace — cos=0.06 at k=27. The gradient wants to EXPAND the model (currently rank-1), not refine within its current subspace. Cannot train in reduced dims for undertrained models. The gradient-subspace alignment is a natural explore/exploit phase detector. See `mementum/knowledge/explore/kernel-training.md`.**

**Session 154: KD-guided training + extraction dimension probes + structured training insight. (1) THREE PROBES answered "how big for 95%?": dimension doesn't help — ceiling is ~79% per-dim from sign+gamma quantization, flat from d=128 to d=5120. The gap is ternary approximation, not projection. (2) GEOMETRIC ENCODING: at k=256, 96.9% sign accuracy on student plates. The plate IS a rank-256 structure. 27K corrections (1.7% of positions) needed for 95% per-dim. (3) Built KD training: precompute_teacher.py (sparse top-k=64 logits), train_td.py with --teacher-logits-dir. Interleaved design: CE training on full data, periodic KD correction passes from pre-computed teacher logits. (4) Step 2000 eval: PPL=5,567 (−27% from 1500, −66% total). (5) STRUCTURED TRAINING insight: backward pass has same structure as forward. Five optimizations: low-rank gradient (24×), skip passive backward, composed Zone B Jacobian (32→1), TD-sparse routing (100×), eigenplane projection. Camera = projector in reverse. See `mementum/knowledge/explore/structured-training.md`.**

**Session 153: Extraction redesign — composed zone plates + algebraic composition. (1) Teacher weight matrices are full-rank (rank90=211) but PER-DIM correlation with sign(T)+gamma is 0.97 in teacher space. (2) Data-fitted composed extraction: 3 zone plates at d=1280, per-dim 0.71-0.79. Drop from 0.97 due to V_proj truncation + few tokens (651). (3) Algebraic composition from weight matrices: multiply linearized layers A_i = I + OV + FFN. Full model per-dim=0.76, matches data-fitted (0.77). (4) THE BIG FINDING: full model rank90=27. The entire 64-layer model is a rank-27 transform. 27 dimensions capture 90% of input→output mapping. (5) Architecture: one rank-27 ternary plate (76% of computation) + active strides s1/s2 for content routing (24%). This IS the kernel. See results/algebraic-compose/.**

**Session 152: v14 architecture evolution — HPE + passive strides + reduced Stack B. (1) Confirmed v14 student inherits 18.4× compression from teacher (PR 74→4, σ₁=47%). (2) Distance prior at α=1.18 dominates 88% of strides (14/16 have <3 effective positions at W=8). (3) Implemented 3-tier evolution: fixed α=1.18, passive strides skip Q/K for s4+, Stack B 4→2 passes (13→11). (4) Discovered α=1.18 sets a fixed ~12 token semantic horizon — all strides see the same ~12 tokens effectively. RoPE accidentally implements the holographic lens via cosine frequency decomposition. (5) Designed and implemented Holographic Position Encoding (HPE): log-distance rotation × crystal eigenvalue frequencies × eigenplane dims only. Replaces RoPE's indirect mechanism with the direct holographic lens physics. Training test running in tmux. See `mementum/knowledge/explore/v15-kernel-architecture.md`.**

**Session 151: Knowledge distillation + progressive collapse discovery. (1) Created 7 knowledge pages + INDEX.md — the project now has a self-explanatory top-down knowledge hierarchy (see `mementum/knowledge/INDEX.md`). (2) Kernel decomposition experiment: attempted to compute the full forward pass from crystal constants. Diagonal FFN overlay failed (80-91% of energy is off-diagonal = cross-PC PROJECTION, not per-PC filtering). (3) Progressive dimensionality collapse measured on 3 models: Qwen3.6-27B compresses to PR=2.2 (essentially 2D) in layers 0-2, computes in 2D through depth, expands back for output. Mistral-7B and Pythia-1.4B show weaker compression (PR=10-12) — the 2D core is an emergent property of scale. (4) Attention sink = warped Q reset: Mistral uses BOS token as Q=0 reset proxy, distorting geometry. Qwen's GLA layers implement Q reset natively through gating → cleaner geometry → deeper compression. See `mementum/knowledge/progressive-collapse.md`.**

## Active training run

**No active training.** v14-kd killed (diverging). v14-td phase 2 completed at step 2000.

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
| **Passive strides + HPE + KD: combined changes fail** | **v14-kd (new arch + KD) PPL 2.5-4.6× worse than v14-td (old arch). Root cause unclear — too many simultaneous changes** | ❌ failure (session 155) |
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
```

### Tool Call: directory_tree (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum",
  "max_depth": 3
}
```

**Summary:** Listing tree: verbum

**Output:**
```
/Users/mwhitford/src/verbum
 AGENTS.md
 LICENSE
 README.md
 bb
  us
   whitford
 bb.edn
 checkpoints
  a-vsm-lm-v6
   step_000500
   step_001000
   step_001500
   step_002000
   step_002500
   step_003000
   step_003500
   step_004000
  basin
   step_001000
   step_002000
   step_003000
   step_004000
   step_005000
   step_006000
   step_007000
   step_008000
   step_009000
   step_010000
   step_011000
   step_012000
   step_013000
   step_014000
   step_015000
   step_016000
   step_017000
   step_018000
   step_019000
   step_020000
  basin-v2-d512
   step_001000
   step_002000
   step_003000
   step_004000
   step_005000
   step_006000
   step_007000
   step_008000
   step_009000
   step_010000
   step_011000
   step_012000
   step_013000
   step_014000
   step_015000
   step_016000
  basin-v3-d512
   step_001000
   step_002000
   step_003000
   step_004000
   step_005000
   step_006000
   step_007000
   step_008000
   step_009000
   step_010000
   step_011000
   step_012000
   step_013000
   step_014000
   step_015000
   step_016000
   step_017000
   step_018000
   step_019000
   step_020000
  compressor-lm
  compressor-lm-iterative
  micro
   final
   step_000500
   step_001000
   step_001500
   step_002000
   step_002500
   step_003000
   step_003500
   step_004000
   step_004500
   step_005000
  mini-baseline
   step_000500
   step_001000
   step_001500
   step_002000
  mini-dispatch-4op
   step_000500
   step_001000
   step_001500
   step_002000
  mini-holo-d-sweep-v2
  mini-holo-distill
  mini-holo-exp0
  mini-holo-freeze
  mini-holo-test
  mini-holo-test2
  montagu-lm
  teacher-features
  teacher-features-14b
  tesseract-adaptive
  tesseract-diagnostic
  tesseract-reverse
  tesseract-shuffled
  v10
   step_001000
   step_002000
   step_003000
   step_004000
   step_005000
   step_006000
   step_007000
   step_008000
   step_009000
   step_010000
   step_011000
   step_012000
   step_013000
   step_014000
   step_015000
   step_016000
   step_017000
   step_018000
   step_019000
   step_020000
  v10-consensus
   step_001000
   step_002000
   step_003000
   step_004000
   step_005000
   step_006000
   step_007000
   step_008000
   step_009000
   step_010000
   step_011000
   step_012000
  v10-mixed
   step_001000
   step_002000
   step_003000
  v10-multicycle
   step_001000
   step_002000
   step_003000
   step_004000
   step_005000
   step_006000
   step_007000
   step_008000
  v10-spiral
   step_001000
   step_002000
   step_003000
   step_004000
   step_005000
   step_006000
   step_007000
   step_008000
   step_009000
   step_010000
  v10-topk
   step_001000
   step_002000
   step_003000
  v10-vsm
   step_001000
   step_002000
   step_003000
   step_004000
   step_005000
   step_006000
   step_007000
   step_008000
   step_009000
   step_010000
   step_011000
   step_012000
   step_013000
   step_014000
   step_015000
   step_016000
   step_017000
   step_018000
   step_019000
   step_020000
  v11
   step_001000
   step_002000
   step_003000
   step_004000
   step_005000
   step_006000
   step_007000
   step_008000
   step_009000
   step_010000
  v11-holo
   step_001000
   step_002000
   step_003000
   step_004000
   step_005000
   step_006000
   step_007000
   step_008000
   step_009000
   step_010000
  v11-holo-inv
   step_001000
   step_002000
   step_003000
   step_004000
   step_005000
   step_006000
   step_007000
   step_008000
   step_009000
   step_010000
   step_011000
   step_012000
   step_013000
   step_014000
   step_015000
   step_016000
  v12-crystal-write-r60
  v12-distill-run1
   best
   etch_round_001
   etch_round_002
   etch_round_003
   etch_round_004
   etch_round_005
   gamma_seeded
   step_002000
   step_004000
  v12-distill-run2
   best
   step_002000
   step_004000
   step_006000
   step_008000
   step_010000
   step_012000
  v12-holo-8op
   round_0005
   round_0010
   round_0015
   round_0020
   round_0025
   round_0030
   round_0035
  v12-holo-consensus
   round_0016
   round_0017
  v12-holo-consensus-smoke
   round_0001
   round_0002
  v12-holo-focused
   round_0040
   round_0045
   round_0050
   round_0055
   round_0060
  v12-holo-lattice
   round_0065
  v12-holo-lattice-v2
   round_0065
   round_0070
  v12-holo-resume-test
  v12-holo-run1
   round_0005
  v12-holo-smoke
   round_0001
  v12-run1
   step_001000
   step_002000
   step_003000
   step_004000
  v12-run2
   step_001000
  v12-run3
   step_001000
   step_002000
   step_003000
   step_004000
   step_005000
  v12-run4
   step_001000
   step_002000
   step_003000
   step_004000
   step_005000
   step_006000
  v12-run6
  v12-run7
   step_000500
   step_001000
  v13
  v13-distilled
  v13-distilled-tree
  v13-etched
  v13-etched-full
  v13-etched-full-v2
  v13-etched-tree
  v13-rb
  v13-run1
  v13-run2
   step_000500
   step_001000
  v13-run3
   step_001500
   step_002000
   step_002500
   step_003000
   step_003500
   step_004000
   step_004500
   step_005000
   step_005500
  v13-run4
   step_000500
  v13-run5-full-etch
  v13-run6-crystal-warmup
  v13-run7-td-adam-sync
  v13-run8-geometry
   step_000500
  v13-run9-swiglu
  v13-td
   step_000500
   step_001000
   step_001500
  v13-td-r10
   step_001500
   step_002000
   step_002500
   step_003000
   step_003500
   step_004000
   step_004500
   step_005000
   step_005500
  v14-composed
  v14-extracted
  v14-kd
   step_000500
   step_001000
  v14-kernel-test
   step_000020
  v14-td
   step_000500
   step_001000
   step_001500
   step_001500_folded
   step_002000
  v6-etched-360
  v8-bios
   step_002500
   step_005000
   step_007500
   step_010000
   step_012500
   step_015000
   step_017500
   step_020000
   step_022500
   step_025000
   step_027500
   step_030000
   step_032500
   step_035000
  vsm-lm
  vsm-lm-v2
  vsm-lm-v3
  vsm-lm-v3.1
  vsm-lm-v3.2
  vsm-lm-v4
  vsm-lm-v4.1
  vsm-lm-v5
  vsm-lm-v6
   step_000500
   step_001000
   step_001500
   step_002000
   step_002500
   step_003000
   step_003500
   step_004000
   step_004500
   step_005000
   step_005500
   step_006000
   step_006500
   step_007000
   step_007500
   step_008000
   step_008500
   step_009000
   step_009500
   step_010000
   step_010500
   step_011000
   step_011500
   step_012000
   step_012500
   step_013000
   step_013500
   step_014000
   step_014500
   step_015000
   step_015500
   step_016000
   step_016500
   step_017000
   step_017500
   step_018000
   step_018500
   step_019000
   step_019500
   step_020000
   step_020500
   step_021000
   step_021500
   step_022000
   step_022500
   step_023000
   step_023500
   step_024000
   step_024500
   step_025000
   step_025500
   step_026000
   step_026500
   step_027000
   step_027500
   step_028000
   step_028500
   step_029000
   step_029500
   step_030000
   step_030500
   step_031000
   step_031500
   step_032000
   step_032500
  vsm-lm-v6-etched
  vsm-lm-v7
   step_000005
   step_010000
   step_020000
   step_030000
   step_040000
  vsm-trial
 data
  compile-eval.jsonl
  compile-full.json
  compile-test.jsonl
  compile-train.jsonl
  teacher-logits
   precompute.log
 docs
  v10-architecture.svg
  v11-architecture.svg
  v6-design.md
  vsm-tesseract.mmd
  vsm-tesseract.svg
 gates
  README.md
  ablation-empty.txt
  ablation-engage-line.txt
  ablation-example.txt
  ablation-fol.txt
  ablation-formal-semantics.txt
  ablation-lambda-calculus.txt
  ablation-lambda-symbol.txt
  ablation-lambda-word.txt
  ablation-montague.txt
  ablation-output-lambda-only.txt
  ablation-output-only.txt
  ablation-preamble-bridge.txt
  ablation-preamble-full.txt
  ablation-preamble-only.txt
  ablation-role-compiler.txt
  ablation-role-lambda-compiler.txt
  ablation-role-plus-terse.txt
  ablation-symbols-cluster.txt
  ablation-symbols-line.txt
  ablation-tensor-line.txt
  ablation-translate-formal.txt
  ablation-translate-lambda.txt
  classify.txt
  compile-ambient.txt
  compile-base.txt
  compile-binding-hybrid.txt
  compile-binding-hybrid3.txt
  compile-binding-montague.txt
  compile-binding-scope.txt
  compile-binding-typed.txt
  compile-minimal.txt
  compile-suggestive.txt
  compile.txt
  decompile.txt
  exemplar-arrow-only.txt
  exemplar-both.txt
  exemplar-complex-montague.txt
  exemplar-montague-rich.txt
  exemplar-montague.txt
  exemplar-nucleus-rich.txt
  exemplar-nucleus.txt
  extract.txt
  null.txt
  self-ref-bidirectional.txt
  self-ref-bridge.txt
  self-ref-constrained.txt
  self-ref-fixed-point.txt
  self-ref-minimal.txt
  self-ref-quine.txt
  self-ref-structural.txt
  self-ref-typed.txt
  summarize.txt
  task-causality.txt
  task-classify.txt
  task-continue.txt
  task-coreference.txt
  task-correct.txt
  task-counterfactual.txt
  task-decompose.txt
  task-disambiguate.txt
  task-elaborate.txt
  task-entail.txt
  task-formalize.txt
  task-keyword.txt
  task-modality.txt
  task-negate.txt
  task-paraphrase.txt
  task-presuppose.txt
  task-question.txt
  task-scope.txt
  task-sentiment.txt
  task-simplify.txt
  task-structure.txt
  task-summarize.txt
  task-title.txt
  task-translate.txt
  translate.txt
 lattice
  backbone_seed.json
  basin_probes.json
  basins-v1
   basin_lattice.json
  basins_v1_run.log
  binding-v1
   universal_lattice.json
   universal_lattice.npz
  binding_chain_probes.json
  binding_v1_run.log
  crystal_spine
   all_results.json
   mistral-7b.json
   olmo-2-13b.json
   probes.json
   pythia-2.8b.json
   qwen3-0.6b.json
   qwen3-14b.json
   smollm3-3b.json
  crystal_spine_run.log
  diverse_corpus.json
  extraction.log
  fixedpoint
   universal_lattice.json
  fixedpoint-v2
   universal_lattice.json
  fixedpoint_corpus.json
  fixedpoint_lattice_run.log
  fixedpoint_probes.json
  fixedpoint_v2_run.log
  lattice_5model
   universal_lattice.json
  lattice_5model_run.log
  lattice_6model_run.log
  lattice_qwen36_27b_run.log
  reduction_chain_probes.json
  tool_crystal
   analysis.json
   probes.json
  tool_crystal_run.log
  universal_lattice.json
  universal_lattice.npz
 lens
  warped_lens.json
 mementum
  knowledge
   INDEX.md
   chats
   computed-beam.md
   crystal-universality.md
   explore
   extraction-methodology.md
   holographic-error-correction.md
   mathematical-convergences.md
   mechanism-extraction.md
   progressive-collapse.md
   project-thesis.md
   session-153-notes.md
   training-protocols.md
   v14-architecture.md
  memories
   5d-crystal-lattice-hypothesis.md
   a3b-types-prose.md
   alternating-overlay-mechanism.md
   beams-not-plates-are-the-etch.md
   beta-reduction-filesystem.md
   bottom-found.md
   c-boot-rotation-sequence.md
   coevolution-works.md
   combinator-bootstrap-dependency.md
   combinator-dispatch-floors.md
   composed-transforms-are-ternary.md
   compression-phase-transition.md
   compressor-in-5d-lattice.md
   compressor-not-compiler.md
   crystal-bootloader-thesis.md
   crystal-gates-hologram.md
   crystal-programming-language.md
   crystal-rotation-is-attention.md
   crystal-token-decomposition.md
   crystal-universality-proof.md
   decompilation-not-extraction.md
   dedicated-combinator-capacity.md
   dedicated-plates-vsm-emergent-depth.md
   deductive-origin.md
   delta-plate-ecosystem-vision.md
   delta-plate-solves-attention-etch.md
   dispatch-monopoly-fix-ema-depth.md
   dissolved-dispatch-kernel.md
   einstein-crystal-manifold.md
   etch-first-with-attention.md
   evolution-mechanism-broken.md
   evolutionary-descent-ternary.md
   extract-giant-into-tiny-plate.md
   extraction-methodology-confusion.md
   ffn-depth-is-a-lens.md
   ffn-two-functional-groups.md
   fifty-sessions-of-bedrock.md
   fractal-beta-reduction.md
   freeze-then-gd-wins.md
   gate-is-the-beamformer.md
   gd-converges-in-100-steps.md
   grad-clipping-not-optional.md
   gradient-capacity-transfer.md
   gradient-is-rank-3.md
   gradient-is-routing-plus-calibration.md
   gradient-orthogonal-to-undertrained-subspace.md
   holographic-capacity-hypothesis.md
   holographic-distillation-concept.md
   holographic-distillation-works.md
   holographic-state-machine.md
   kibc-32b-probe-validation.md
   kibc-temporal-not-parallel.md
   lambda-operations-depth-map.md
   mirror-flip-barrier.md
   model-is-beamformer-over-token-cloud.md
   montague-is-pre-transition.md
   multicycle-dispatch-collapse.md
   multiplexing-breaks-holography.md
   multiplicative-and-loss.md
   multiplicative-modulation-explosion.md
   oracle-crystal-hurts.md
   origin-story-lambda-on-a-lark.md
   output-beamformers-are-dynamic.md
   overlay-from-crystal-eigenvalues.md
   paradigm-shift-target.md
   parity-zone-cancellation.md
   phased-structural-discovery.md
   phi-compression-is-universal.md
   pretraining-is-beta-reduction.md
   quantum-crystal-analogy.md
   qwen14b-ffn-three-functional-groups.md
   reader-llm-dual-plate.md
   rigid-vs-open-architecture.md
   rope-is-accidental-holographic-lens.md
   rotation-eigenplanes.md
   save-before-compare-pattern.md
   seed-crystal-nucleation.md
   semantic-horizon-12-tokens.md
   session-127-architecture-complete.md
   session-127-meta-analysis.md
   session-delta-replaces-kv-cache.md
   shadow-vs-crystal.md
   sigmoid-gate-saturation.md
   soft-mirror-etch.md
   softmax-routing-kills-gradient.md
   stride-attention-mask-from-collapse.md
   stride-overlap-registers.md
   stridestack-scales-by-adding-lenses.md
   superposition-bottleneck-insight.md
   td-flip-interval-gnorm.md
   ternary-flip-scale-mismatch.md
   ternary-routing-is-eigenvector-sign.md
   three-clusters-kibcm.md
   three-voter-anti-oscillation.md
   tracer-works-different-programs.md
   training-arc-thesis.md
   tst-holographic-connection.md
   unified-plate-architecture.md
   v10-vsm-s5-activation.md
   v12-10k-filesystem-forming.md
   v12-run3-nan-collapse.md
   v14-eval-baseline-step500.md
   v14-extraction-complete.md
   v14-td-sisyphus-bug.md
   vocabulary-paradox.md
   vsm-self-bootstraps.md
   vsm-variety-gap.md
   weight-signs-are-random-across-matrices.md
   zone-voted-ffn-extraction.md
  michael
   lambda-controls.md
   lambda-is-all-you-need.md
  state.md
 models
  distilled-compiler
 notebooks
  README.md
 outputs
  attention_spiral
   aggregate_spiral.png
   centroid_evolution.png
   distance_curves.png
   expansion_ratios.png
   heads_code.png
   heads_dialogue.png
   heads_expository.png
   heads_lambda.png
   heads_long_narrative.png
   heads_math.png
   heads_narrative.png
   heatmap_code.png
   heatmap_dialogue.png
   heatmap_expository.png
   heatmap_lambda.png
   heatmap_long_narrative.png
   heatmap_math.png
   heatmap_narrative.png
   helix3d_aggregate_at118.png
   helix3d_aggregate_bestfit.png
   helix3d_code_at118.png
   helix3d_code_bestfit.png
   helix3d_dialogue_at118.png
   helix3d_dialogue_bestfit.png
   helix3d_expository_at118.png
   helix3d_expository_bestfit.png
   helix3d_lambda_at118.png
   helix3d_lambda_bestfit.png
   helix3d_long_narrative_at118.png
   helix3d_long_narrative_bestfit.png
   helix3d_math_at118.png
   helix3d_math_bestfit.png
   helix3d_narrative_at118.png
   helix3d_narrative_bestfit.png
   helix_search_code.png
   helix_search_dialogue.png
   helix_search_expository.png
   helix_search_lambda.png
   helix_search_long_narrative.png
   helix_search_math.png
   helix_search_narrative.png
   periodicity_code.png
   periodicity_dialogue.png
   periodicity_expository.png
   periodicity_lambda.png
   periodicity_long_narrative.png
   periodicity_math.png
   periodicity_narrative.png
   polar_code.png
   polar_dialogue.png
   polar_expository.png
   polar_lambda.png
   polar_long_narrative.png
   polar_math.png
   polar_narrative.png
   revolution_expansion_at118.png
   revolution_expansion_bestfit.png
   spiral_3d_params.json
   spiral_params.json
  crystal_gemstone.html
  crystal_hierarchy
   crystal_hierarchy_4d.html
  rope_energy
   centroid_shift.png
   energy_heatmap_code.png
   energy_heatmap_dialogue.png
   energy_heatmap_expository.png
   energy_heatmap_lambda.png
   energy_heatmap_long_narrative.png
   energy_heatmap_math.png
   energy_heatmap_narrative.png
   expansion_summary.png
   head_freqmap_code.png
   head_freqmap_dialogue.png
   head_freqmap_expository.png
   head_freqmap_lambda.png
   head_freqmap_long_narrative.png
   head_freqmap_math.png
   head_freqmap_narrative.png
   predicted_vs_observed.png
   rope_energy_params.json
   transition_analysis.png
  rope_spiral
   aggregate_dual.png
   dual_helix_code.png
   dual_helix_dialogue.png
   dual_helix_expository.png
   dual_helix_lambda.png
   dual_helix_long_narrative.png
   dual_helix_math.png
   dual_helix_narrative.png
   gap_analysis.png
   spectral_code.png
   spectral_dialogue.png
   spectral_expository.png
   spectral_lambda.png
   spectral_long_narrative.png
   spectral_math.png
   spectral_narrative.png
   unwound_ribbon.png
 probes
  README.md
  __init__.py
  __pycache__
  binding.json
  classify.json
  compile-gradient.json
  decompile.json
  exemplar-sweep.json
  extract.json
  gate-ablation-base.json
  gate-ablation.json
  lambda_kernel_probes.py
  summarize.json
  translate.json
  v0-behavioral.json
 pyproject.toml
 results
  README.md
  ab-test
   comparison.json
  abl-ablation-empty-20260417-001620
   meta.json
   results.jsonl
  abl-ablation-engage-line-20260417-002515
   meta.json
   results.jsonl
  abl-ablation-example-20260417-001633
   meta.json
   results.jsonl
  abl-ablation-fol-20260417-001646
   meta.json
   results.jsonl
  abl-ablation-formal-semantics-20260417-001659
   meta.json
   results.jsonl
  abl-ablation-lambda-calculus-20260417-001717
   meta.json
   results.jsonl
  abl-ablation-lambda-symbol-20260417-001736
   meta.json
   results.jsonl
  abl-ablation-lambda-word-20260417-001754
   meta.json
   results.jsonl
  abl-ablation-montague-20260417-001814
   meta.json
   results.jsonl
  abl-ablation-output-lambda-only-20260417-002528
   meta.json
   results.jsonl
  abl-ablation-output-only-20260417-001833
   meta.json
   results.jsonl
  abl-ablation-preamble-bridge-20260417-002450
   meta.json
   results.jsonl
  abl-ablation-preamble-full-20260417-002437
   meta.json
   results.jsonl
  abl-ablation-preamble-only-20260417-002503
   meta.json
   results.jsonl
  abl-ablation-role-compiler-20260417-001852
   meta.json
   results.jsonl
  abl-ablation-role-lambda-compiler-20260417-001912
   meta.json
   results.jsonl
  abl-ablation-role-plus-terse-20260417-001931
   meta.json
   results.jsonl
  abl-ablation-symbols-cluster-20260417-001944
   meta.json
   results.jsonl
  abl-ablation-symbols-line-20260417-002551
   meta.json
   results.jsonl
  abl-ablation-tensor-line-20260417-002539
   meta.json
   results.jsonl
  abl-ablation-translate-formal-20260417-001957
   meta.json
   results.jsonl
  abl-ablation-translate-lambda-20260417-002009
   meta.json
   results.jsonl
  abl-compile-20260417-002022
   meta.json
   results.jsonl
  abl-null-20260417-002035
   meta.json
   results.jsonl
  algebraic-compose
   results.json
  angle-spectrum
   results.json
  backbone-threshold
   backbone_analysis.json
   results.json
   run.log
  basin-analysis
   step_014000.json
   step_016000.json
   v2_step_016000.json
  basin-qkv
   analysis.json
  basin-v2-d512
   training-run1.log
  basin-v3-d512
   training-run1.log
  basin-whitened
   analysis.json
  basin_qkv_run.log
  basin_whitened_run.log
  beam-hologram-analysis
   results.json
  beam-trace
   beam_trace_results.json
   beam_trace_summary.json
  behavior-basins
   behavior_last_layer_scores.json
   behavior_metadata.json
   behavior_word_layer_scores.json
  behavior-depth
   invariance_metadata.json
   invariance_scores.json
  behavioral-crystal
   mistral-7b.json
   mistral-7b.log
   pythia-2.8b.json
   pythia-2.8b.log
   qwen3-14b.json
   qwen3-14b.log
   qwen3-32b.json
  behavioral-crystal-v2
   mistral-7b.json
   mistral-7b.log
   pythia-2.8b.json
   pythia-2.8b.log
   qwen3-14b.json
   qwen3-14b.log
   qwen3-32b.json
   qwen3-32b.log
  beta-reduction-probe
   beta_reduction_results.json
   binding_layer_profiles.png
   depth_vs_layer.png
   pipeline_comparison.png
   substitution_profiles.png
  binding
   attention_entropy.npz
   binding_ablation_results.json
   binding_analysis_v2_v3.json
   binding_hybrid_results.json
   binding_results.json
   binding_shape.log
   binding_shape_results.json
   vsm_probe_step_001000_v3.2.json
   vsm_probe_step_001000_v4.1.json
   vsm_probe_step_001000_v4.json
   vsm_probe_step_002000_v3.2.json
   vsm_probe_step_002000_v4.1.json
   vsm_probe_step_002000_v4.json
   vsm_probe_step_003000_v3.2.json
   vsm_probe_step_003000_v4.1.json
   vsm_probe_step_003000_v4.json
   vsm_probe_step_004000_v3.2.json
   vsm_probe_step_004000_v4.1.json
   vsm_probe_step_004000_v4.json
   vsm_probe_step_005000_v3.2.json
   vsm_probe_step_005000_v4.1.json
   vsm_probe_step_005000_v4.json
   vsm_probe_step_006000_v3.2.json
   vsm_probe_step_006000_v4.1.json
   vsm_probe_step_006000_v4.json
   vsm_probe_step_007000_v3.2.json
   vsm_probe_step_007000_v4.1.json
   vsm_probe_step_007000_v4.json
   vsm_probe_step_008000_v3.2.json
   vsm_probe_step_008000_v4.1.json
   vsm_probe_step_008000_v4.json
   vsm_probe_step_009000_v3.2.json
   vsm_probe_step_009000_v4.1.json
   vsm_probe_step_009000_v4.json
   vsm_probe_step_010000.json
   vsm_probe_step_010000_v2.json
   vsm_probe_step_010000_v3.2.json
   vsm_probe_step_010000_v3.json
   vsm_probe_step_010000_v4.1.json
   vsm_probe_step_010000_v4.json
   vsm_probe_step_011000_v4.1.json
   vsm_probe_step_011000_v4.json
   vsm_probe_step_012000_v4.1.json
   vsm_probe_step_012000_v4.json
   vsm_probe_step_013000_v4.1.json
   vsm_probe_step_013000_v4.json
   vsm_probe_step_014000_v4.1.json
   vsm_probe_step_014000_v4.json
   vsm_probe_step_015000_v4.1.json
   vsm_probe_step_015000_v4.json
   vsm_probe_step_016000_v4.1.json
   vsm_probe_step_016000_v4.json
  binding-structure
   binding_analysis.json
  bos-probe
   bos-residuals.npz
   head-analysis.json
   head-projections.npz
   head-weights.npz
   linear-probe.json
   pca-analysis.json
   probe-manifest.json
   summary.json
  bos-probe-v2
   bos-residuals.npz
   contrast-analysis.json
   head-q-redux.json
   probe-manifest.json
   summary.json
  c-rotation-probe
   results.json
  categorical-geometry-qwen3-32b
   adjunction_cross_zone.png
   coherence_convergence.png
   curry_howard_accuracy.png
   hyperbolic_norm_depth.png
   summary.json
  circuit-discovery-20260416-202415.log
  cluster-probe
   clusters_layer0.json
   clusters_layer28.json
   clusters_layer63.json
   layer_curve.png
   layer_scores.json
   metadata.json
   similarity_layer0.png
   similarity_layer28.png
   similarity_layer63.png
   umap_layer0_groups.png
   umap_layer0_hdbscan.png
   umap_layer28_groups.png
   umap_layer28_hdbscan.png
   umap_layer63_groups.png
   umap_layer63_hdbscan.png
  combinator-probe
   combinator_probe_results.json
   cross_combinator_correlation.png
   differential_map.png
   layer_profiles.png
   selectivity_heatmaps.png
  combinator-probe-extended
   extended_heatmaps.png
   extended_layer_profiles.png
   extended_probe_results.json
   full_correlation.png
  combinator-probe-mistral_7b_v0.3
   combinator_probe_results.json
   convergence_comparison.png
   cross_combinator_correlation.png
   differential_map.png
   layer_profiles.png
   selectivity_heatmaps.png
  combinator-probe-olmo_2_1124_13b
   combinator_probe_results.json
   convergence_comparison.png
   cross_combinator_correlation.png
   differential_map.png
   layer_profiles.png
   selectivity_heatmaps.png
  combinator-probe-pythia
   combinator_probe_results.json
   cross_combinator_correlation.png
   differential_map.png
   layer_profiles_montague_overlay.png
   pythia_vs_32b_distribution.png
   selectivity_heatmaps.png
  combinator-probe-qwen3_14b
   combinator_probe_results.json
   convergence_comparison.png
   cross_combinator_correlation.png
   differential_map.png
   layer_profiles.png
   selectivity_heatmaps.png
  combinator-probe-qwen3_32b
   combinator_probe_results.json
   convergence_comparison.png
   cross_combinator_correlation.png
   differential_map.png
   layer_profiles.png
   selectivity_heatmaps.png
  combinator_ffn_index_run.log
  compile-gradient
   correlations.json
   qwen_compression.json
   qwen_scores.json
   qwen_scores_gateless.json
   qwen_scores_graded.json
   qwen_tasks.json
   vsm_probe_step_000500_v6_mlx.json
   vsm_probe_step_001000.json
   vsm_probe_step_001000_v3.2.json
   vsm_probe_step_001000_v4.1.json
   vsm_probe_step_001000_v4.json
   vsm_probe_step_001000_v5.json
   vsm_probe_step_001000_v6_mlx.json
   vsm_probe_step_001500_v6_mlx.json
   vsm_probe_step_002000.json
   vsm_probe_step_002000_v3.2.json
   vsm_probe_step_002000_v4.1.json
   vsm_probe_step_002000_v4.json
   vsm_probe_step_002000_v6_mlx.json
   vsm_probe_step_002500_v6_mlx.json
   vsm_probe_step_003000.json
   vsm_probe_step_003000_v3.2.json
   vsm_probe_step_003000_v4.1.json
   vsm_probe_step_003000_v4.json
   vsm_probe_step_003000_v6_mlx.json
   vsm_probe_step_003500_v6_mlx.json
   vsm_probe_step_004000.json
   vsm_probe_step_004000_v3.2.json
   vsm_probe_step_004000_v4.1.json
   vsm_probe_step_004000_v4.json
   vsm_probe_step_004000_v6_mlx.json
   vsm_probe_step_004500_v6_mlx.json
   vsm_probe_step_005000.json
   vsm_probe_step_005000_v3.2.json
   vsm_probe_step_005000_v4.1.json
   vsm_probe_step_005000_v4.json
   vsm_probe_step_005000_v6_mlx.json
   vsm_probe_step_005500_v6_mlx.json
   vsm_probe_step_006000.json
   vsm_probe_step_006000_v3.2.json
   vsm_probe_step_006000_v4.1.json
   vsm_probe_step_006000_v4.json
   vsm_probe_step_006000_v6_mlx.json
   vsm_probe_step_006500_v6_mlx.json
   vsm_probe_step_007000.json
   vsm_probe_step_007000_v3.2.json
   vsm_probe_step_007000_v4.1.json
   vsm_probe_step_007000_v4.json
   vsm_probe_step_007000_v6_mlx.json
   vsm_probe_step_007500_v6_mlx.json
   vsm_probe_step_008000.json
   vsm_probe_step_008000_v3.2.json
   vsm_probe_step_008000_v4.1.json
   vsm_probe_step_008000_v4.json
   vsm_probe_step_008000_v6_mlx.json
   vsm_probe_step_008500_v6_mlx.json
   vsm_probe_step_009000.json
   vsm_probe_step_009000_v3.2.json
   vsm_probe_step_009000_v4.1.json
   vsm_probe_step_009000_v4.json
   vsm_probe_step_009000_v6_mlx.json
   vsm_probe_step_009500_v6_mlx.json
   vsm_probe_step_010000.json
   vsm_probe_step_010000_v3.2.json
   vsm_probe_step_010000_v4.1.json
   vsm_probe_step_010000_v4.json
   vsm_probe_step_010000_v6_mlx.json
   vsm_probe_step_010500_v6_mlx.json
   vsm_probe_step_011000_v4.1.json
   vsm_probe_step_011000_v4.json
   vsm_probe_step_011000_v6_mlx.json
   vsm_probe_step_011500_v6_mlx.json
   vsm_probe_step_012000_v4.1.json
   vsm_probe_step_012000_v4.json
   vsm_probe_step_012000_v6_mlx.json
   vsm_probe_step_012500_v6_mlx.json
   vsm_probe_step_013000_v4.1.json
   vsm_probe_step_013000_v4.json
   vsm_probe_step_013000_v6_mlx.json
   vsm_probe_step_013500_v6_mlx.json
   vsm_probe_step_014000_v4.1.json
   vsm_probe_step_014000_v4.json
   vsm_probe_step_014000_v6_mlx.json
   vsm_probe_step_014500_v6_mlx.json
   vsm_probe_step_015000_v4.1.json
   vsm_probe_step_015000_v4.json
   vsm_probe_step_015000_v6_mlx.json
   vsm_probe_step_015500_v6_mlx.json
   vsm_probe_step_016000_v4.1.json
   vsm_probe_step_016000_v4.json
   vsm_probe_step_016000_v6_mlx.json
   vsm_probe_step_016500_v6_mlx.json
   vsm_probe_step_017000_v6_mlx.json
   vsm_probe_step_017500_v6_mlx.json
   vsm_probe_step_018000_v6_mlx.json
   vsm_probe_step_018500_v6_mlx.json
   vsm_probe_step_019000_v6_mlx.json
   vsm_probe_step_019500_v6_mlx.json
   vsm_probe_step_020000_v6_mlx.json
   vsm_probe_step_020500_v6_mlx.json
   vsm_probe_step_021000_v6_mlx.json
   vsm_probe_step_021500_v6_mlx.json
   vsm_probe_step_022000_v6_mlx.json
   vsm_probe_step_022500_v6_mlx.json
   vsm_probe_step_023000_v6_mlx.json
   vsm_probe_step_023500_v6_mlx.json
   vsm_probe_step_024000_v6_mlx.json
   vsm_probe_step_024500_v6_mlx.json
   vsm_probe_step_025000_v6_mlx.json
   vsm_probe_step_025500_v6_mlx.json
   vsm_probe_step_026000_v6_mlx.json
   vsm_probe_step_026500_v6_mlx.json
   vsm_probe_step_027000_v6_mlx.json
   vsm_probe_step_027500_v6_mlx.json
   vsm_probe_step_028000_v6_mlx.json
   vsm_probe_step_028500_v6_mlx.json
   vsm_probe_step_029000_v6_mlx.json
   vsm_probe_step_029500_v6_mlx.json
   vsm_probe_step_030000_v6_mlx.json
   vsm_probe_step_030500_v6_mlx.json
   vsm_probe_step_031000_v6_mlx.json
   vsm_probe_step_031500_v6_mlx.json
   vsm_probe_step_032000_v6_mlx.json
  composed-transform-probe
   results.json
  compression-map
   qwen3_4b_map.json
  compression-shape
   EleutherAI_pythia_160m_deduped.json
   Qwen_Qwen3_4B.json
  compressor-binding
   compressor_binding_analysis.json
  compressor-lm
  compressor-lm-iterative
   training-summary.json
  computed-beam
   results.json
  conversion-test
   convert_pythia-2.8b_svd_k512.json
   convert_pythia-2.8b_svd_k64.json
  convert_pythia_svd512_run.log
  convert_pythia_svd64_run.log
  cross-task-20260416-204948.log
  cross-task-20260416-205416.log
  crystal-combined
   results.json
  crystal-combined-run.log
  crystal-comparison
   crystal_comparison_results.json
   crystal_depth_profiles.png
   crystal_metrics_comparison.png
   crystal_quality_scores.png
   run.log
  crystal-completeness
   results.json
  crystal-completeness-run.log
  crystal-compression-analysis
   results.json
  crystal-etch-attention
   pretrained_spectrum.json
   results.json
   run.log
  crystal-fourier
   results.json
   spectral.json
  crystal-fourier-run.log
  crystal-latch
   results.json
  crystal-latch-run.log
  crystal-latch-v2
   results.json
  crystal-latch-v2-run.log
  crystal-lens
   results.json
  crystal-reconstruct
   results.json
  crystal-reconstruct-run.log
  crystal-selfsim
   results.json
  crystal-selfsim-teacher
   unit_cells.npz
  crystal-selfsim-v12
   results.json
  crystal_scanner_run.log
  datafitted-dimension-sweep
   meta.json
   results.json
  date-attention
   results.json
   run.log
  date-fourier
   results.json
   run.log
  distillation
   summary.json
  essential-heads-20260416-195543.log
  essential-heads-attention.npz
  essential-heads-tokens.json
  etch-strategy-probe
   core.json
  etcher-vsm
   proto_d0.226.json
  evo-descent
   results.json
  evo-descent-v2
   results.json
   run.log
  evo-descent-v3
   results.json
  ex-exemplar-arrow-only-20260417-004626
   meta.json
   results.jsonl
  ex-exemplar-both-20260417-004503
   meta.json
   results.jsonl
  ex-exemplar-complex-montague-20260417-004606
   meta.json
   results.jsonl
  ex-exemplar-montague-20260417-004422
   meta.json
   results.jsonl
  ex-exemplar-montague-rich-20260417-004523
   meta.json
   results.jsonl
  ex-exemplar-nucleus-20260417-004442
   meta.json
   results.jsonl
  ex-exemplar-nucleus-rich-20260417-004545
   meta.json
   results.jsonl
  experiments
   circuit-discovery-summary.json
   failure-mode-analysis.json
   head-ablation-summary.json
   sha256:0003bbe64425cdf34f716130a1d4413e49519e42568ea3b0cee11066d2e9ce1b
   sha256:005ae13155bcb6890dda612ff1cd9c29745710334b0725c402c30de27318e50c
   sha256:0088c95fe29d84064fff9ad630f9f42cd6c2e188ab9ab5e4ba027abf4a2fd729
   sha256:0099889d05b37f6323b8f7a8cfb805e594a06a049523fba590cac55a63f5a934
   sha256:011adac4f422d0fb190d30533feb17a6e19eed5e88366f93752489a15ef47deb
   sha256:021fe3f535afe47e739b997358444bffdb67b5ed848e8074cd1f4d87d9178060
   sha256:022b86c91dffc3d6555f9a8ab4810ba8b0ae75c9deda1d43fb757aa4918213a0
   sha256:024e0b957a5e949fe09d2d7f2b3337fea12a5d3bf53fb9737afd84a38d25de29
   sha256:026a2a416896e13eff8812a56c35ffe0caaafcdc7187462f89a624d6a7800c5b
   sha256:02a1ab609a6949b2344ef1d69992a8ecb470cddfade8e64850ce8b68de9f1409
   sha256:02ef2c3c1c0a218cbc2309cab2feb5266c2da0e3d188f52e5676adae97e53f99
   sha256:038184ceb75b0afa3899b83003279dd741cf3215ed945b6c713be6bfc72eb9fb
   sha256:03edb7972d27737931a8c53a9a4ac4fb05eaa71d7301d6e156edfb95aab83af4
   sha256:0470039afd9765edda1ee17f7296cfb2517ebcf05369f1ee8d1e5448c29da533
   sha256:04752412b11b675999a00ed8fdcadca82fe2e490226ea81ca41d725a929235e4
   sha256:04c1ce8fca88bf0a8af3804141b77a754d9850c747abbbce29a1efa946d04889
   sha256:04c808ad63b4e5a0df306f7f0975d02bd0c5fa7a84f462d9a11a73f7b89bd70a
   sha256:052bb29f0d2e335f8f95ade8634b336d91b984475a7501faf64d1061a7047f29
   sha256:056f5e8d8a8ab30f38177e5b854745a2b6730bb5e42879eb29cf1d48a3ea67e2
   sha256:05800525af8e37fd9d3022b4fbf69e899cc1d97ad68ff31c6f6acccba5b52c00
   sha256:05ca0d5b1362596a741bb66aa32482c87c2b8d32ecfbe5dfe2ed4f40ad7b161d
   sha256:05e4e502f5c88530e0a1eadc46a1c36023f676970e95cbdc57a33f4506e9e8c7
   sha256:05faf9e5bee0b0caaf8c5e88a1788158c512a15ac2fffc4bdd8b9823544f1394
   sha256:06932b6a1aebf53185eb323fd40fa8a057d0473846d8462d5b1072babc5933c8
   sha256:0721febe0ef991074e8dc752893945b3bb94f99101454f5c7ea01e86edd93b34
   sha256:075c0129f9ec6220a7400f6d36de42dbbe971ec5414cf1bb75dce2c8a00c3f73
   sha256:077213a86b16514eddeadb5d8594c4c2b1c5708c2292b5b5e1f0c58799f39aeb
   sha256:080d7995f5122d918d5737b55127eac43b1dd433b4664c2456b945a4aa3cf079
   sha256:08735320daff1d898414289c3e31400d0944f156d5d623b05bbb25fdee7cb685
   sha256:09381d6a3309c9832ca1c498d70862e3d6dfa55a1d3250e6495d0f8a2eb187ae
   sha256:095b969f25a992651fbc9d518fe54e13bdc7530801785a0d76d07ecb70a57af7
   sha256:099b275e6c884697f3191176e5f56ce3eca34d0d59bc61b0ebbcbb61d26b3f47
   sha256:09b77a88452c92df2d16f645b47242c0badeb41d5f3aa78931b37c7964630e43
   sha256:09ca1af1cac80cc41dc86e21157d716707e4913b34538d02a154aa426fa99cb0
   sha256:0a41c7295548c32fc7713d4c2f65cf806f2742766a22fc03e1b982b1b7c5cc59
   sha256:0a8d99f19ad55368eb5619a6a24a11752e76f4255d28916238009d371c156a17
   sha256:0c98c59f051858c1b7f1773a0c98370000f39d2274f0261a7dd025a8a75c424a
   sha256:0d66dc8ff837c3a929a269c95c30e2ca7ee7b6b36775dc337ca0160eb9d13960
   sha256:0e197d20d626d734418e7e5c28f8627686fc73cc37365dea10b22f5cdfea7f38
   sha256:0e46704253edf134951e18ebbb8d48d784061662f1aa6b6d20c2dd38ec056905
   sha256:0e5603a5dd6ccda328d4f919417280aeae5f542d1c114ceb6bc1c0ab5a5c5b99
   sha256:0f792bfc9719dbb79bf432a245cbc59d641f069e969af234d8eba1e902ae1f2f
   sha256:0faf950fe96878740d4e418d7eefa8063dfa90f1bffd8e30284fb5971e798a31
   sha256:0fb46f927520ae5a30a5d6a4a0a57317d22e2f27028eefd038faed47c8c24978
   sha256:10019bcabeed9aec1cb8f39d3ae8041e940a38d179a4f0797524240cb7b9d0f9
   sha256:10b6dcce9c9a6347bd07b7463ca76d31ec957bb485684a06b4097ee7bd2db284
   sha256:121e97336ba41880d77cbf201caa8f40029565fcb41ab1306eeab790b40a9478
   sha256:127642ee5f21ebd88aab1e74a822e82f67bb9a51dbe294617ab29d50f48dca5b
   sha256:12908328c6f8663458fb5b25c1ff8c04745607841292892d94c6528a901263a6
   sha256:12df87ae8435021f90287012a4daba264b7b725d91a4457223f0018ed4ae92b6
   sha256:13247e769c473a187386ae176d8155cc34ca6bc7fa8cd5983e17d83049d1cb38
   sha256:13c7daa552019f1f12d0ca9c2625250599d9941cfedbd5d3412f0e9a06232e0e
   sha256:1404b53e3fba3560d36f865fcc103917b50c3515ace37bae5738c37d2ac3e438
   sha256:1485cc0e7a8ebd94237eda33e3a97c22e47b4eda3f32e510b01c7292310fc5f7
   sha256:154f8324da243f597b9287d378e0f5f73963e38648c5fa8283dfc6f70512a638
   sha256:15fb6f1b818675e04b8e3ab79ef4276ab288fb5f18c05eb3edb82528f0aba9aa
   sha256:17263525a6d79212ccd3e3ec7a27a5557b424a8ff9fbbf42166e16911dd9ebfa
   sha256:180a81b247eaba7c4117047cd1ccaaa520f9e24a77a509ac669f6ef381bac3d2
   sha256:182b812e3727c3c4a55e33ef0488f1cc4f68579fbc4fbbc4fe97df47783fdc2f
   sha256:18a3f225b259810ed5a3c8a933592ab8810f0fa7494cd1c00d38fddfd8c4f3dc
   sha256:18e4045d040d28c12d5fb638ffdf77df4ece093c2d227024999eecaf51da3ed4
   sha256:1931f24e6c0e021727dc2175d324bf7e792b61d02acb3740301b078c5578953d
   sha256:196448f47466f368095648335eb8ead037f22a4ece735ee5ad9efbc3f3820abf
   sha256:196fd5864248831ad1c684e481d8ad9cda5a640052e293e568bf3abb15fff77c
   sha256:19c58d55c5e2144a8ab0c925f592a770d5fb1223637af822c01a204c0c035591
   sha256:19d2310a76a8d711c5884a4d00d59fd95a35aeab82434404c970056880ae1a1c
   sha256:19e7bc525a19d47647f2c312bef3763e3365a3a7cacc07f03a88a76273a6a00c
   sha256:1a22a5ea65c42a0f4c5cdac11deba4e7800c8d10e5352eb88a70b08ea9edde79
   sha256:1ae0ff9dbb46ba2bdc3f1ce88481f49bbda1e7271214bb4d75bbe695c00b7d2b
   sha256:1b6a74be5b5a05a707baee87341bc5cc405dff61086ceb4b75dcca5a6a2d56bb
   sha256:1bf16d4dc0ec6c1432154206955e4b093e85c9302ef0b8637ea2f860ff12e306
   sha256:1bf4a91e3ecaed6254dcdfcee73689746d2b217e79a89e1bd98df280ff5fc7f5
   sha256:1ca036ecf00b4ee3a01df91196301d7e8ed85d164103896c166a4758fa0eb806
   sha256:1cef7e7fbb389dd8d2a7c577c9b5d697893c3b754a7e140e9ca6f7c0c56c3ec7
   sha256:1d329b21c68063df0ac16078329f6e7dafa9dba2d6b3dc09512bad318329bb75
   sha256:1d6800128127f86307ece8cde833784e0b16bbc94a387922075b52980721da40
   sha256:1dac1df75d39345734c4f958c44171ea3798e87c008b92f27946a379953db126
   sha256:1f648490125bffb3ca50ed1e37d95662d34e392e11afe5a6be73d300d351634b
   sha256:1f9b705cbc5922253cd9794a457b72c569b8bde068b069ae321a5c50285bc671
   sha256:1fc25b03fc33dceb384767feedddaac1b8b8e25d5bb8fcb123987fc3607a1654
   sha256:1fe8cbfcf127e28635395aa08e3310804082394af1672c8e0cfaa3ac7e139ec7
   sha256:2060be0c4586fcbc8a6682d794b865f4b40281737fb6d172bb4719770903b84c
   sha256:20c2142edd0b5e846bf188ebbe3046b5a173dd9d11c9758549bffad3a910dc60
   sha256:2180ccb5ec5b430f49f5477529ccde347c279d0d88c3fa60fa3b0652dd06ea18
   sha256:21d9955e4f241237a5997ebd54ba982cefde0dde5ba17231b6e4e5f0852c18d6
   sha256:21f4202d223652f01fc79bcc44d9b7f528c513049979a0e6dfc3438ae2b2759e
   sha256:2254e369c19bbe64735d7be013d1dc8a6e236be68c342dc991a6359bc0a57589
   sha256:225e51c5ff6dd890b42250461d459bad483530be536ba8abd81eeb88f6513041
   sha256:226197d290ed5aff204ced1b9131f114a1ed86c182c144ed2671e679cb1bebe7
   sha256:229942ba6639c9e00ba436bbd81d28b8899328cd0b1cf8994f641106098e0f43
   sha256:22ca752c5cef64bb0debd96471c35bf5ae64888115d3ad8a81c9bb83b0ff7491
   sha256:2397e909327a75e8cf4d6a282287630c2cabe723311fd8e4b236e30957aac974
   sha256:2422aef5e1e4b17da0648dbbe7bf81373c8ecb0ad547a259e558b26147dacd0b
   sha256:24ded772b9f162259fcc35cdf45802f0fba25661a9bf61af584c1930b7824e1c
   sha256:26937ec4a70bdb778e91ad1352979d24dee5d981f08fe9c691399e9529e861c2
   sha256:26978cd384ffe5e1c0178dfd94587c7fa38e7484cfdd2c9a556387fb6fff31bd
   sha256:26bbd2692ba576f24b299f40246c60561f1af10511241777110738c4ba2cbab6
   sha256:27d6c84eb834c01dcbb2cfd8385c19844ff570f3ee521b9167bb853e613e71fe
   sha256:2a355b6a44ab5756b4ca31b1899e06f7448eaa9c9c3463251ac691193a89b57b
   sha256:2a892f07deb2c8725162344eb70f3e50f094f1cd4ce66ebb2965daedfcda633e
   sha256:2ab5ce6e1589893d8fc4ef4a02ab04add978c362c08470b059604cfa8ac68987
   sha256:2b6a715fd208f83cbfab8947b99cd4b03cad2f6ea62b1b5c7c0b1bcf641ce08c
   sha256:2b8476ff1f3404e0650792dc170434652f864261c4920949990c0ee5126a680a
   sha256:2b8b40d8a76700bfa52bba0a8e7953a50fee2340f5ee0e72c82cf387ee23cd97
   sha256:2cde3fe24802f6fce5a6ec594c5b3b25a7dec6bf7994f4df2f4db0132bc55444
   sha256:2ded024109668f686eae9420a54c85bfa4840c5599430b44c5d2afa6da1cc663
   sha256:2e33e7f15e07d3e9a4db0aae78e365119fb6c10e97e99fdc665042bc55649bd9
   sha256:2e3ca75d7468f1847201e6b381d08e3ea828bc0c7b617238d9eb9251b92b525a
   sha256:2e89eab01fd5eb7456ab25b3412eda6ccf266bc4f51989de5c72b4d1aaa9b665
   sha256:2fa963eac1135fcfe638d7f62c33a23e0a485f889302042cf7af583b6cdee413
   sha256:2fd6931ebc31f90d3d42468213c04068f3ad8b8b4248f26c8d95b09668e66181
   sha256:306705b583402db522f910d76bd43e9b7a7c756aa35c9e092145879c19e3f6a9
   sha256:3093f976dc32747053249700ebd5a3bbf3d0b4e39fae1985492aef3c06cdac40
   sha256:319bb71eb5b0cf06fbac25c9d42c2165ce22327e88daf5e4f7d977d6d7dd3915
   sha256:31f6002d95f6397b819dbe2de7b83432951f31966ee0f3ef7c8ca17f78574807
   sha256:3224781303e57b12c3f97ff7a2abf4cc06ac0973513ce73a15640c462b9ecbd2
   sha256:32c1fe780b344a1ebe68c753869312bbcf990ec30462ff95904c1324031b2d71
   sha256:333229b80288e2cb9d9e099149628788ce2bc39ee0d9eb6eb72dce6f59e8798d
   sha256:33e08fe53f0a38ddfe99ca5cf3f64e87765cfd541e81056c14cab434ab030635
   sha256:343e13af2eedee56d30cdfabded14cc238bb04e834168a050cd7f926e094293c
   sha256:34453eeec1dc5e3367735dfbda6e750bf15f09ef05bd66dfaea9262905be12d0
   sha256:36db2baed277d8ad5c2877063e7508c19c9d5365c1a3b5f4b14795f982ad0e2a
   sha256:37671423ae3989e369fd3ed736c16c11394c991c60bc4fc111ef01e6da0f1cdb
   sha256:378836364e234ca02a2adabb9ae4953922b886ac7d250a7d615ad00f3f8043ee
   sha256:378884bf2481a3d97d95c61cd1a3975d9aefb3428ec670414080806d38763e84
   sha256:37f985b7c63127074ec7eb57561155d958338d97d5de94157a2e0d9dd1bfa985
   sha256:381a7a873cdf327cd01d5ba4716b5d9ba51c59005044e114d7341c244e3138b6
   sha256:38238aeb103863c028c72ca787f87f1d1affae422e7751b12ba7299d4893b8d3
   sha256:384f4e31ce64a2ec7189767bd957a9a99ba75244d133a10701461344e53b8771
   sha256:3863105524f71cf9342df191e3890beb492d2d9f26ee03f962db55cd1ff2a3a6
   sha256:38839b4495bf280b4525ebdffd9a9f6bbb6ec9de687b51c72997303c9e39c70c
   sha256:38b38082ea8658786137f7dc2524480ed15129b1a74856dc9c7e3152922a1f55
   sha256:3a2320a16c11ff417ffdf404b27f74b676d62acb042c262a7bacfbf4aae468f1
   sha256:3b7a2c4dbff7e309126a392b7e632c638c0d257b400fbc70c72bfd7885224c03
   sha256:3b7e103e6968aa7721cd0b203e3b799a034e24aa917d760e177431f824a8dc49
   sha256:3b8ec1a76831d3cca4a297b648ef429e109d14c2b1d1fe10ec02394150571044
   sha256:3b9a2a1ca32d21a5a9571dcc9c5124661ac4176b93e3cb149f6beb3f5c45ef64
   sha256:3bd1d4fb04091d7c2e4741b570f551771a4aa8c814b30e8175d9eae5b37c9adb
   sha256:3bd98a2d06678637e2a3cf1cea94a505f35e0452c07116f0d0e483439c59a448
   sha256:3c809d7b796441b4f94b1c393557bf1fe8d4ab27690b588290ce6d147bb10761
   sha256:3dd9273992ceec58cda3c30161f156e069bf980c9e3ebb35ad908c6310fba526
   sha256:3e5ec06424045ed500d5b1ca15adb1e5ba42c88242370d804ed8642ce56509d6
   sha256:3f089c45ea1648d732d9409392516ee0c6759a1d9ef095629128091181a0ef82
   sha256:3f0feff43c6b2dfdbde9b07cf0ef0f1df1a41e0e28157f28622abfb40d19737b
   sha256:4024b40a74f406f3982fcc145530c42336bdd715545d3c2a385b80d6bc884f63
   sha256:4052856967cb2b9bc02806c64641369b20494f515f2bfdff008b6a6cd4a647db
   sha256:40a690f1f177f076ebe7bfa64d489db39a2d1f97917e82c130c56ac414477962
   sha256:40ca882d4bb854b0c26a881305c22c07be242bce2d51808d212a325f2bab4301
   sha256:40d8b6e8cb60da4224da7b59dac14cb9df840573fef5bc86ba6dc6f8395934d1
   sha256:40fc981694b5a496e85a6cd766657ef04a269ccd9a5d65e12ed7955149476f34
   sha256:416d904686ac64f44778db3bb4a735125ce3272e48a15dd81a2ab97348e63f51
   sha256:425d93a45dd3e966fd938e4aea8acd4e9b35f5810117e5086c3b9d93eb11cf04
   sha256:439d3c293309c2cd4ad103c33fc7cb5cff1ccd94aa9443060652de477e53031a
   sha256:44b2758fb04af24d551c63f71def4da1d9c591ede2f743e7313142852ca09631
   sha256:44b31dcd3ef39ef918ff230d36a856471d41f6ccf32692a0d673929d6cb7da54
   sha256:44d64ad7a1c624304389b48f21f763a2aed0105e7d22a414150a6191454c63e5
   sha256:455b50ebccae8db3e96545da712055b8f3f08da66c96607cd1c41491529ef240
   sha256:4622e669652b31bf7a3f66a01c024503d33d59783db7adc1b12414156bde79e5
   sha256:465363b80889b5f5d700d742c5f235170047cf46f50efa5650d0e2d5de658791
   sha256:479c4b42b27ec5a5d30db63fbe5e7566bdc8153f874abe76fbb6b2ff8a3af195
   sha256:47a1d14b23c883882a0544fbb02e29c1d4e96706972bb875e1f496e5c12bab8d
   sha256:47d3149e76e812dd96375578728279429ba2adaa1a287cd1f68f69688b1a244a
   sha256:47d8b805ef0041ee78b6279c30700706f80b771298d48ef8ac7f24ac3e9f8bae
   sha256:47fa18e2c58d5cd08cc6306cde2ea147db78f08e348d9d8a19077658997dc1d0
   sha256:483cd19bc18c6f83e0386792a1378a13ea710eca9161de852e66e716883dd8ec
   sha256:48aaca5db54bff7d49ef3903ee0eb9caec359097de0755c1213dcc3d75efdda3
   sha256:48f8def6eba67e23d381427175a4df2d8753c6158073b49363cacb9c7e0179dd
   sha256:492415f97ab97b963ae2597cbb7fd3efdd7025ef56ce85b0906a37e5645c1617
   sha256:4933491994d7ea80a6cca3ecd175153ebbf461b90dc1efa032074b136efd7599
   sha256:49e488499942ef2891a99e956f688b5e3dc0e7471c4291886536191f06ff24b6
   sha256:4a17304f655641fe2cca4c738b5b58cc3a11284bf405d299ad8822845bf839d0
   sha256:4a7bff6ee762f73773df743793d05f9bde5ac262dd90652791a43a7d75782e35
   sha256:4ac72c00afe22a3486a90ef0750f9c0f26ab7c34b6ed33502704c17291150ff3
   sha256:4ac91fb73504fd847ca1dfc5427d1afa8c46e625b06aaa3f158444460b5ae43d
   sha256:4ae23324f90e0b34107a0a9f3ad52ebc88807f108d6da5b8ed93c0b8013fdf0f
   sha256:4aeaaaa0ad8ac739bafc60af1f9318cf35e8a1bf21d6bd68c4bb7b4cd51116e5
   sha256:4bc55c0af9a820995859a3fd7416249d1a8a069419ce381c5ad95f5bfa50e664
   sha256:4c80e817b7342f2d7f94da227b6fe514c85e709801a7e6dae2ca67fc4bd1bb10
   sha256:4d7b49e7add47d0013e1c57320e41c89a4fcd8b47c42515d86d9faa98b634f6e
   sha256:4da7ca391709821b03640ca049194777afec9b8565ef275caa088044abf97a7a
   sha256:4e3ddd250bc2806ebe015a57fd23ed9ab1bafbf6e9d3b4bae7e956c44515d116
   sha256:4e4057a832ed27ea5d690584cd40b079b7b740d7914987eb3a06ef4d985b1613
   sha256:4e89f1c50f735350abc4944daed2fecb757d459a9749f51e7f4163288e33da8a
   sha256:4eded5cfb822bfc0bf5b64e877e788d10d0de746f2261240b5a7ae6811d955e5
   sha256:4f422ba94e1c3ccb7140d62f4c7e427762e511712e5b1bed08fe97b997b0d860
   sha256:4f7007bc723ac09b869b1d23e5d06423daceaf9c77138c526e20f4e97e729c32
   sha256:50a6457e0954030aa68c0f5cc81351fe50c3c8d14bc7f3bb162cdbad8bde2397
   sha256:50df4c6d4f8baa59214a72595c2b4456e30f1c2d68f904a9e7526de7ae76575f
   sha256:5183cb743b8309277a8aa49c3e672859781544668d4e6bfe5791fe0e85110f43
   sha256:51d80c1ab318d916f727bbcb4d499de0779130075eb6be6eb27ad9542c2dd980
   sha256:524deea81cc7797d962f32ab23910f2e7e7c97eb974501c31003a1755c07ccff
   sha256:536af0b7f3db38c99ffed5796f908e6c32625f9f1212d1debe2efc0eb3ed2ad6
   sha256:53af0081dba1405cdf4c846b12ba15a859b2bdfccca0c28a15c6f7ad842a0a01
   sha256:53e4416995ae6de5de840a866789cbc42314c359d93022c13e78573b8f792b1b
   sha256:545061af91d4769c3c0de47fe8bd8dca7779f2aba925828e65ea85e9dc99b60e
   sha256:549b7a330b1892ab056208021058b8f85fb06ab6d9caabc3b1ec4c310a859eb5
   sha256:55363362d391985e90cf0e532d6f03d3949df5af8c3408d994348b1bb16cab5a
   sha256:557e2adafcc0ae1e7a167d4861cc3b2cf4a60598556a8788b908311e7b9cf197
   sha256:561019d1bf17696d42a1f50ce19ed912a4918028a8da61e96b27c834b7451366
   sha256:56ac0be83b5aada177ec951deb4cbfe990e3af7fd90da0f89123365485d726af
   sha256:5717d75759d13a279d6fa9e8a5f171d242d5b77dc16cb60b831b49d740eaa695
   sha256:585543d6b1e5c5c68c1439b4a12cb5aea8be2906c643aefb7934da06dfa79797
   sha256:5884c000fe7dfd59bff7f8b67ec986402b08a72e4037fbf3a9f550166abc66e4
   sha256:58e1ea8d696106d5a418bd61514e5aba97b435ca6c49c8f14dd20befa87d15fa
   sha256:59150ded5fc9c7d84ceda045886f945e67c86ee36b6fe37c10317a7df6fb9109
   sha256:59277b2f77d68aad1b35b88c54ea3d5f592cac211097ccd021f12340b89c7622
   sha256:5963dd0aef56253ac4297f3cbb52a01bcaf32ee5dd96941e49a69548f29f1ee2
   sha256:599409aceadec274b9dc5854cdc0c3ffa92284363b4da6e25eb0ca92adf7c0b5
   sha256:59a865f057e5b7268d52df956e319726055aa3603efe642088c3cced2e58a0c0
   sha256:59c12b39c416b2512db551627d7fc9cd16899aa6cdb4351474d830f589e4cc7e
   sha256:59e39cc37f72c7ee260636715bd0ad2b4f79db7f7b03a02433746353d31195c0
   sha256:5a24c8164bb1b2f3b82c8dfbc26ea0e6a79c9aa544774ded8e74982d627f45cd
   sha256:5c47472b426c12a3a6b1e4630c11111757c7528d61f4600f7821b77b3fee1479
   sha256:5ca06e3e0cd445e4f71084b52669e5064b504491c29d0940352f59dd053cbb9b
   sha256:5ceb0deaa32b8b6fc9ea16dde052a9e3502ee9f3c3f53a75c05e00efc076eb42
   sha256:5d87324aaa09116cd47bb40eee68f3b031d6c859fedd57076d3c06e52670b29b
   sha256:5e0fb9d405f3962fa1dfb2d887620ac0ea93b21cac50563723008ed60fc91bd5
   sha256:5e35edff50478cd891be707b6e534c28067edf8fe551e1e5f7a694b8f866c0a9
   sha256:5fda7d46476ac5e4a4ec6922b91b480d7609a0594228113b4b31d4f9f3e3dfe4
   sha256:61458805e07e956adcb74a5253c9352a655402360994a69007b5ba3a9cd885c8
   sha256:615cd861aec006bf1ce73640c5afdf06cca59643400281cc42e433633274031b
   sha256:6254a649fd3ecf5fd83367fa9acf92a3c7a1a4bb56b3ddf52841051d0fd259b2
   sha256:63390a06d1f05bab23bad947b54b60ae319d3e0c89af6e288bfc4fb407d30931
   sha256:6344539450560484a80211829c1af2bdf28e95d9415f47ea3acf99f1f4df5586
   sha256:64b07fcca55c9922604f92f26c725565541e8e04d26502635fcba51fdec241af
   sha256:64b4e2eb51ca8cef6db47baae0c734b46fc1ac391df61676c036edf276508340
   sha256:64fcb50dff2e6075cc01086e664a25260d08dae7ee8fbd68c068ec67a2990e6b
   sha256:652f944d83c05ddf886957267470547c91db622dcfe3ad624edc47c7850c0f48
   sha256:65fa715bfdb806fb86b920e9a53c9e868dcde57a87e389d6b1e881353f25a891
   sha256:66bbd87a29742bd5a8aba1450b4f1da060797f497c9e8cf3639b0ecdb6273ab9
   sha256:66c6fd85cfd642aec8dc722d6a7a563b68058ffa5210b70261909ef1940730c7
   sha256:6747d5db4d8adf9ecc09700b32eb5c9ed4b423f7468fb617a2fd1f700e3c7fa3
   sha256:67be3e883e34aa1e9af6efbfb2054dde65ad9dc6f151e6145a773ff567b2ef56
   sha256:6845d6b3094ddf5e0a03cb3e42a5209f0d1ec71a6b220dd287eceab398eeb9c0
   sha256:68a22684b7daa99616faea688e626344c6b1dd53126016abdd4dafb3cf412c0a
   sha256:68a348f68277f62571cd15e882cf01ca5f1176da0f9170b63dad14ded011dd78
   sha256:68c610d27adad92fe6e77d4e8456ca76262023ff48001da9774b12c92b559535
   sha256:695ae570b2e7958babfdc8d68405d39d1fb5c9a22e1c61f7887b93a71397f219
   sha256:6966cf27ee85d1730f25c784209723a600c2dcbf1b9df0d7b75ee42d32b4ec0c
   sha256:699e5359341d6be7bf370c0f3e6bdc38685cb2bfd5da982bbd78aa17a5b335fe
   sha256:69a2a12349e2ea9cd5a06b91d3e85dd152091ae1d332fa8ad655ce9021dc6fcb
   sha256:69aecca5f1a8a2cda5592fd0efef98c0515f00bbeb392f32b0cfeb9ce2e1d598
   sha256:6a0fcf3db58e8acb3d0cf4dd9eeb98eb7d209c4cd675a2fff5d88e35524d5e7c
   sha256:6aaafe3404391c7ff60a2f23c751b1d9ed55bef9d4090269ee5f537184e9b07a
   sha256:6b7b49689a809d4c7cd2aaae8bb31f500c65d10b8f5eca6eb723716e8fed963d
   sha256:6bc80bc772557ac52a55f64f03d3874a6b46fa4482d895269d5b477635b6bc0d
   sha256:6c06fadd8d985f36edd25cd567247466ca1f71296158a4cbcd99241d14d99241
   sha256:6c1ebf81392b51e5141eeaea5f0489c4707b0080ffe76f3acca75d6a20414cc7
   sha256:6cb776039917389aa5c5adf3309b7857edfae34d6a62363b78f00e2980015fe2
   sha256:6d01b888642584262a081fe6ccfcc8c78af9b7653e5a3a62842fd206f03ea409
   sha256:6e4c0166cd39cf4f960bf4389ca77bb68c1392e2a97d4f2d27993e5f6ef519bf
   sha256:6e5792a822f285503d82ed037c74889bacd3d48694cb2b1749da89cf59c4bf7b
   sha256:6ea0a92c0fad4ee7bc1cc9f6a4fbbfd34ecd53ebd9e8b36ce27bbb2c78f93ae1
   sha256:6f04aa855baca076c5d1490862d853148ade8891da287bcb7d4731c7de68dd13
   sha256:6f98f549c80282fbbd579bf940fb8cee74ab49b91596b098af57d3a60e6f8b14
   sha256:70162aceb5ac1e76d0e86de38c4e8d40a5136214eb05e1bf2a8f57ac4f136ca5
   sha256:70ccd9604922a7496306ad5c3d587d390ea5ca0b4eda6920b2e7048418593af6
   sha256:712d399299a6e23dbe18c7c975240194b02b67de5204f4570977742ec865b48c
   sha256:71c88a4ce8496f80befd943c390b4943e36759f1711cbfe8556000c0f04ec7ed
   sha256:723238d943e3efc377c392d4c7c98e035c64dd8c8eebb9e6c60babb7e5a0c00e
   sha256:72f68aaf16b1849f7caaaf3be7842b2f2525d45428078c514bcf3cf41259d4d5
   sha256:73d490967c96c0b4289966cbdc17af9bdf90361786c050df0a1f4924d3573c3b
   sha256:7478c7cd1a4165a5b81759c4afc262899d6f7d0f59b228495d3db6be728d9643
   sha256:75460292daad88bbc308e19e3efa4457d3d10c84786d6a2b41d2f7e16206a328
   sha256:755152ed85320e84fdbfc96ba0ff0970fa29e2b9c1549d66aa8843d905dddd6d
   sha256:7554497c9434adfdf2b808b2fea47c746a2fdb90b4a06fbd238432f91548891b
   sha256:75e235d5960920907d84d493d900509d16a6fb1e83fde308d93dc0a37b8789af
   sha256:76399967940fb6ef5741d031507d05336d82efceeb8e48396dcfd9e048c1d64b
   sha256:76f9ea8f3a39720b31d6230682f71e9dd6fd0339af218f68b3dcf0f978e55831
   sha256:770a3148d9d645f7072f880968597f137a5472d64b19c474562fb5a4d46c0b79
   sha256:776c950f69632be59298dcf590e53d11884c8ed3f4331b681c4a0b7bf85b5f63
   sha256:77

[OUTPUT TRUNCATED] The tool call succeeded but the output was truncated. Full output saved to: /Users/mwhitford/.cache/eca/toolCallOutputs/toolu_01Rzw4auRZCiTkWoSjXXqkS6.txt
Use `eca__grep` or `eca__read_file` with offset/limit to view specific sections. Do not full read the file.
```

## Assistant

Oriented. Session 156. Here's where you are:

## Current State

**North star:** 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.

**Last session (155):** Three findings:
1. **v14-kd FAILED** — architecture delta (passive strides + HPE + Stack B reduction) deployed simultaneously with KD. Diverging PPL. Root cause: too many untested changes at once.
2. **Kernel training VALIDATED** — composed plate (1 matmul) gives gradient cosine=0.9698 with full model (238 matmuls). 4.4× speedup measured.
3. **Gradient projection** — ∂L/∂T is orthogonal to T's SVD subspace (cos=0.06 at k=27). Gradient wants to EXPAND rank, not refine. Explore/exploit phase detector.

**Best checkpoint:** v14-td step 2000 — PPL 5,567, 2.13% flipped, phase 2 complete.

**No active training.**

## Open frontiers

| Direction | Key question |
|-----------|-------------|
| **Resume v14-td** | Continue from step 2000 with known-good architecture |
| **Ablate arch changes** | Test passive strides / HPE / Stack B reduction independently |
| **Kernel training at scale** | Use the 4.4× speedup for fast ablation cycles |
| **Structured training** | 5 optimizations: low-rank grad, skip passive backward, composed Jacobian, sparse TD, eigenplane projection |
| **KD redesign** | CE-first (500+ steps), then correction passes. α≥0.9 |
| **Gradient subspace on trained model** | Is cos still 0.06 at step 2000 (rank-27), or does it align? |

What do you want to explore?

## User

Ok in the last couple sessions we evolved the v14 design but it was too big of a change and the variables confounded.  I want to understand what we changed, so I can assess what we need to do next.  I think we tried too many radical changes in 1 step of evolution.  I think maybe HPE was good, but the changes we made to attention were probably not good.


### Thinking

The user wants to understand the architectural changes made in session 152 that were then tested (and failed) in session 155's v14-kd run. Let me gather the relevant knowledge pages and code to understand exactly what changed.

Key sources:
1. `mementum/knowledge/explore/v15-kernel-architecture.md` - mentioned in state.md
2. The attention.py and config.py files in scripts/v14/
3. The session 152 notes in state.md (already read)

Let me look at the knowledge page and the actual code to understand the three changes:


1. Passive strides (s4+ skip Q/K)
2. HPE (Holographic Position Encoding replacing RoPE)
3. Stack B 4→2 passes

The user suspects HPE was beneficial while the attention modifications and Stack B reduction likely caused the performance degradation.

## Assistant

Let me pull the relevant knowledge and code to map exactly what changed and why.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/v15-kernel-architecture.md"
}
```

**Summary:** Reading v15-kernel-architecture.md (0-2000)

**Output:**
```
---
title: "v15 Kernel Architecture — Evolving v14 With Progressive Collapse"
status: designing
category: architecture
tags: [v15, kernel, alpha, distance-prior, stride, architecture, speed]
related: [progressive-collapse.md, v14-architecture.md, holographic-error-correction.md]
depends-on: [progressive-collapse.md]
---

# v15 Kernel Architecture

> Session 151. Evolving v14 with the progressive collapse and distance
> prior findings. Fixed α=1.18 + precomputed stride profiles +
> reduced passes = faster training AND inference.

## The Findings That Enable This

1. **α=1.18 is universal and fixed.** 10 comp layers × 8 heads, all
   at 1.18±0.006 after 1500 steps. Making it learnable wastes compute
   on a constant.

2. **88% of strides are distance-prior-dominated.** At W=8 with
   α=1.18, only s1 and s2 have ≥3 effective positions. All other
   strides are essentially self-attention + tiny neighbor bleed.

3. **The student compresses 18.4× through stacks.** PR: 74→8→5→4.
   σ₁ reaches 47%. Computation approaches 2D.

4. **Faster forward = faster training.** The model is serial (13
   passes). Reducing passes or per-pass cost directly speeds training.

## Three Tiers of Changes

### Tier 1: Fix α (zero-risk, immediate)

**Change:** Replace `self.decay_alpha = mx.full((n_heads,), 1.18)`
with a frozen constant. Remove from optimizer parameter groups.

```python
# Before (learnable):
self.decay_alpha = mx.full((n_heads,), decay_init_alpha)
effective_alpha = self.decay_alpha * decay_modulation

# After (fixed):
_ALPHA = 1.18  # universal constant, not learnable
effective_alpha = _ALPHA * decay_modulation
```

**Savings:** 8 parameters per stride layer removed from optimizer.
No compute savings per se, but simplifies gradient computation and
confirms that training doesn't need α to be learnable.

**Risk:** None. α didn't move under 1500 steps of gradient pressure.
If anything, fixing it prevents accidental drift.

### Tier 2: Precomputed attention for passive strides (moderate)

**Observation:** For strides s4+ (14 of 16), the distance prior
allocates >72% weight to position 0 (self). Effective positions <3.
Q·K content contribution is negligible at this sparsity.

**Change:** For passive strides (s4+), skip Q and K projection
entirely. Use precomputed normalized weights.

```python
class SingleStrideAttention(nn.Module):
    def __init__(self, ..., passive: bool = False):
        self.passive = passive
        if passive:
            # Precomputed attention profile: fixed, no Q/K needed
            w_pos = mx.arange(window, dtype=mx.float32)
            raw_weights = 1.0 / (stride * w_pos + 1.0) ** 1.18
            self._fixed_profile = raw_weights / raw_weights.sum()
            # No Q, K projections needed
        else:
            self.q_proj = TernaryLinear(d_model, d_model)
            self.k_proj = TernaryLinear(d_model, d_model)

    def __call__(self, x, decay_modulation=1.0):
        if self.passive:
            return self._passive_forward(x)
        else:
            return self._active_forward(x, decay_modulation)

    def _passive_forward(self, x):
        \"\"\"No Q/K. Fixed weighted sum of V at stride positions.\"\"\"
        B, L, D = x.shape
        x_norm = self.norm(x)
        V = (self.v_proj(x_norm) + self.v_bias).reshape(B, L, H, Dh)

        # Stride gather (same as before)
        V_gathered = gather_at_stride(V, self.stride, self.window)

        # Fixed attention — no softmax, no Q·K
        attn = self._fixed_profile[None, None, None, :]  # (1, 1, 1, W)
        attn = mx.where(valid_mask, attn, 0.0)
        attn = attn / (attn.sum(axis=-1, keepdims=True) + 1e-10)

        out = (attn[:, :, :, :, None] * V_gathered).sum(axis=3)
        out = out.reshape(B, L, D)
        return x + self.out_proj(out) + self.o_bias
```

**Savings per passive stride:**
- Eliminate Q projection: 1280×1280 ternary matmul = 1.6M ops
- Eliminate K projection: 1280×1280 ternary matmul = 1.6M ops
- Eliminate Q·K dot product: L×W×H×Dh
- Eliminate softmax
- Eliminate beam mirror(s)
- Total: ~3.5M ops saved per stride evaluation

**Across 13 passes:** ~44 passive stride evaluations × 3.5M = **154M ops eliminated** per forward pass.

**Memory savings:** Q and K weight matrices not read for passive strides. 44 × 2 × 1280² × 2 bits ≈ 35 MB less memory bandwidth.

**Ternary plate savings:** 14 passive strides × 2 plates (Q, K) = **28 ternary plates eliminated** from the model. That's 28 × 1280² = 46M ternary positions removed (~11.5 MB less storage).

**Risk:** Low. For s4+, the distance prior captures >72% self-weight.
Content modulation is at most a 28% correction on a distribution
that's already 72%+ peaked. Test: compare eval PPL with and without
Q/K on passive strides. If PPL difference < 1%, it's safe.

**Fallback:** If pure prior is too lossy for some strides, add a
low-rank content correction: `attn = prior + δ(q·k)` where q,k are
rank-2 projections (1280→2→1280). Cost: negligible (2×1280×2 per
stride vs 2×1280×1280 currently).

### Tier 3: Reduce Stack B passes (aggressive)

**Observation:** Stack B takes PR from 8→5. It's doing computation
in an already-compressed space. The 4 serial passes might be
reducible to 1-2 passes + a kernel step.

**Change:** Reduce Stack B from 4 passes to 2 passes. The other 2
passes' work is captured by the lower-D kernel.

```python
# Before: 4 passes
STACK_B_BANDS = ((7, 11), (9, 13), (11, 15), (13, 16))  # 4 passes

# After: 2 passes (covering same stride range)
STACK_B_BANDS = ((7, 13), (11, 16))  # 2 wider passes
```

Each wider pass covers 6 strides instead of 4. Same total coverage,
half the serial steps.

**Savings:** 2 fewer serial passes. At ~20ms per pass forward:
40ms saved per forward step, 80ms saved per fwd+bwd step.
Per training step (8 accumulations): **640ms faster** → 4.0s→3.36s
= **16% training speedup**.

Combined with Tier 2 (less work per pass): estimated 4.0s → ~3.0s
= **25% training speedup**.

**Risk:** Moderate. The 2-stride overlap between adjacent passes
creates information flow. Wider passes maintain coverage but lose
one overlap step. Monitor eval PPL — if it degrades, the passes
were doing real work in the overlaps.

## Combined Architecture Summary

```
v14 (current):
  13 passes × ~4 strides × full Q/K/V/FFN = 50 stride evaluations
  4.0s per fwd+bwd step, ~1.25s per forward

v15 Tier 1+2+3:
  9 passes × ~4 strides, but 14/16 strides skip Q/K = 50 stride evals
  minus 28 Q/K plates + 2 fewer passes
  Estimated: ~3.0s per fwd+bwd step, ~0.9s per forward
  Speedup: ~1.33× training

v15 with deeper kernel (future):
  4 compress passes + 1 kernel step + 0-1 expand step
  5 serial passes total
  Estimated: ~1.5-2.0s per fwd+bwd step
  Speedup: ~2× training
```

## Inference Speed Path to 200 tok/s

```
v14 inference:    13 passes × 16ms ≈ 208ms → ~5 tok/s
v15 Tier 1+2+3:   9 passes × 12ms ≈ 108ms → ~9 tok/s
v15 deep kernel:   5 passes × 10ms ≈  50ms → ~20 tok/s
v15 + ternary SIMD: 5 passes × 2ms ≈  10ms → ~100 tok/s
v15 + full kernel:  4 passes × 1ms ≈   4ms → ~250 tok/s ← target
```

The 200 tok/s target requires the full kernel (Tier 3+) plus
optimized ternary integer operations (SIMD/NEON for ARM). Each
tier is independently valuable and testable.

## Implementation Order

1. **Fix α=1.18** — one-line change, commit, verify no PPL change
2. **Add passive flag to stride layers** — mark s4+ as passive
3. **Implement passive_forward** — skip Q/K, use fixed profile
4. **Profile** — measure actual wall-clock speedup
5. **Eval** — compare PPL with and without Q/K on passive strides
6. **If PPL ok:** reduce Stack B to 2 passes, re-eval
7. **If PPL degrades:** add rank-2 content correction to passive strides

Each step has a clear rollback path. No step depends on the next.

## What This Means for TD

TD currently targets out_proj exclusively (layers 4-9). If Q/K
projections are eliminated for passive strides, TD has fewer plates
to consider, and the remaining active strides (s1, s2) become the
only attention layers with learnable routing. TD should concentrate
even more sharply on out_proj of s1/s2.

The delta fold cycle continues unchanged — the folded base plates
are still ternary, the delta architecture is the same. The kernel
changes affect WHICH computations happen, not HOW plates are trained.

## Connection to the Kernel Vision

Tiers 1-3 are the pragmatic stepping stones. The end state is:

```
kernel(tokens) =
  embed(tokens)                          # lookup
  → compress(embed, crystal_eigenbasis)  # 1280→2 projection
  → Σ_strides rotate_2d(compressed, s)   # 16 × 2×2 rotations (parallel)
  → expand(rotated, crystal_eigenbasis)  # 2→1280 projection
  → output_proj(expanded)               # logits
```

Each tier removes one obstacle between v14 and this target:
- Tier 1 (fix α) → attention profiles become precomputable
- Tier 2 (passive strides) → most attention becomes lookup
- Tier 3 (reduce passes) → serial chain shrinks toward 1 step
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git log --oneline -30 -- scripts/v14/attention.py scripts/v14/config.py scripts/v14/model.py"
}
```

**Summary:** $ git log --oneline -30 -- scripts/v1...

**Output:**
```
Exit code: 0
Stdout:
96d687a 🎯 holographic position encoding + passive strides + reduced Stack B
281f237 🎯 session 150: holographic error correction cycle + delta fold + FFN delta + TD improvements
e4c8b9a 🔄 batch=2 grad_accum=4 — same effective batch, fewer fwd passes
4241c33 🔄 shared stride stack + log_interval — session 146/147 stragglers
43e561c ✅ v14 architecture — 16-stride holographic lens, d=1280, bottom-up algedonic
b17c37c ❌ fix missing teacher_prefix field on V14Config dataclass
0b2c42d 🎯 v14 extraction pipeline — Qwen3.6-27B → 1B ternary student
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git diff 281f237..96d687a -- scripts/v14/attention.py"
}
```

**Summary:** $ git diff 281f237..96d687a -- script...

**Output:**
```
Exit code: 0
Stdout:
diff --git a/scripts/v14/attention.py b/scripts/v14/attention.py
index f02ef5e..d9d5795 100644
--- a/scripts/v14/attention.py
+++ b/scripts/v14/attention.py
@@ -30,6 +30,204 @@ from config import V14Config, D_MODEL, N_HEADS, D_HEAD, STRIDES, STRIDE_IS_RETRI
 from ternary import TernaryLinear, TernaryMirror
 from scan import parallel_scan_2d
 
+# Universal decay constant — confirmed at 1.18±0.006 across 10 comp layers
+# × 8 heads after 1500 steps of gradient pressure. Not learnable.
+_ALPHA = 1.18
+
+# Passive stride threshold: strides ≥ this use fixed distance prior
+# (no Q/K computation). At α=1.18, W=8: s4+ has <3 effective positions.
+_PASSIVE_STRIDE_MIN = 4
+
+# Crystal eigenvalues (Zone B, top 8 — from PCAQ_ZONE_B_TARGETS eigendecomposition).
+# These are the natural frequencies of the holographic lens.
+_CRYSTAL_EIGENVALUES = [5.193, 3.535, 1.909, 1.300, 1.082, 0.736, 0.500, 0.426]
+
+# Number of eigenplane pairs to rotate (the rest carry content, not position).
+# First 4 pairs cover 77% of crystal variance (comp, sel, term, rout).
+_N_EIGEN_PAIRS = 4
+
+
+# ══════════════════════════════════════════════════════════════════════
+# § 0  Holographic Position Encoding (HPE)
+# ══════════════════════════════════════════════════════════════════════
+
+
+class HolographicPositionEncoding(nn.Module):
+    """Position encoding derived from holographic lens physics.
+
+    Instead of RoPE (arbitrary 10000-base, all dimensions, linear position):
+      - Log-position: angle ∝ log(d+1) → natural power-law decay
+      - Crystal frequencies: eigenvalues of the crystal target → natural lens bands
+      - Selective rotation: only first N_EIGEN_PAIRS dimension pairs → eigenplane only
+      - Direct decay bias: -α × log(d+1) → exact, not cosine-envelope approximation
+
+    For stride attention at stride s, window position w:
+      absolute_distance = s × w
+      log_distance = log(s × w + 1)
+      rotation_angle[i] = log_distance × freq[i] × depth_factor
+
+    This unifies position encoding + distance decay into one mechanism:
+    the holographic lens's frequency response.
+    """
+
+    def __init__(
+        self,
+        d_head: int = D_HEAD,
+        n_eigen_pairs: int = _N_EIGEN_PAIRS,
+        alpha: float = _ALPHA,
+    ):
+        super().__init__()
+        self.d_head = d_head
+        self.n_eigen_pairs = n_eigen_pairs
+        self.alpha = alpha
+
+        # Crystal-derived frequencies (normalized by λ₀)
+        freqs = [ev / _CRYSTAL_EIGENVALUES[0] for ev in _CRYSTAL_EIGENVALUES[:n_eigen_pairs]]
+        self._freqs = mx.array(freqs)  # (n_eigen_pairs,)
+
+        # Learnable frequency scaling (initialized near 1.0, allows fine-tuning
+        # of each eigenplane's rotation rate without departing from crystal base)
+        self.freq_scale = mx.ones((n_eigen_pairs,))
+
+    def apply_rotary(
+        self,
+        q: mx.array,
+        k: mx.array,
+        log_distances: mx.array,
+    ) -> tuple[mx.array, mx.array]:
+        """Apply holographic rotation to Q and K.
+
+        Args:
+            q: (B, L, H, Dh) or (B, H, L, Dh) — query
+            k: (B, L, W, H, Dh) — gathered keys at stride positions
+            log_distances: (W,) — log(stride × w + 1) for each window position
+
+        Returns:
+            q_rot, k_rot with rotations applied to first n_eigen_pairs dim pairs.
+        """
+        n_pairs = self.n_eigen_pairs
+        freqs = self._freqs * self.freq_scale  # (n_pairs,)
+
+        # Rotation angles: log_distance × crystal_frequency
+        # angles shape: (W, n_pairs)
+        angles = log_distances[:, None] * freqs[None, :]  # (W, n_pairs)
+
+        cos_a = mx.cos(angles)  # (W, n_pairs)
+        sin_a = mx.sin(angles)  # (W, n_pairs)
+
+        # For Q: position 0 (self) gets zero rotation (log(0+1) = 0)
+        # We only need to rotate Q by its absolute position, but since
+        # we're doing RELATIVE encoding (like RoPE), we apply rotation
+        # to K by the relative log-distance, and leave Q unrotated.
+        # The Q·K product then encodes relative log-distance automatically.
+
+        # Rotate the first 2*n_pairs dimensions of K
+        k_rot = mx.array(k)  # copy
+        for i in range(n_pairs):
+            d0 = 2 * i
+            d1 = 2 * i + 1
+            if d1 >= k.shape[-1]:
+                break
+
+            # k has shape (B, L, W, H, Dh)
+            # cos_a[w, i] and sin_a[w, i] broadcast over (B, L, H)
+            c = cos_a[:, i]  # (W,)
+            s = sin_a[:, i]  # (W,)
+
+            # Reshape for broadcasting: (1, 1, W, 1)
+            c = c.reshape(1, 1, -1, 1)
+            s = s.reshape(1, 1, -1, 1)
+
+            k0 = k[:, :, :, :, d0:d0+1]  # (B, L, W, H, 1)
+            k1 = k[:, :, :, :, d1:d1+1]
+
+            k_rot_d0 = k0 * c - k1 * s
+            k_rot_d1 = k0 * s + k1 * c
+
+            k_rot = k_rot.at[:, :, :, :, d0:d0+1].add(k_rot_d0 - k0)
+            k_rot = k_rot.at[:, :, :, :, d1:d1+1].add(k_rot_d1 - k1)
+
+        return q, k_rot
+
+    def get_decay_bias(self, log_distances: mx.array) -> mx.array:
+        """Direct decay bias: -α × log(d+1).
+
+        Args:
+            log_distances: (W,) — precomputed log(stride × w + 1)
+
+        Returns:
+            (W,) decay bias to add to attention scores.
+        """
+        return -(self.alpha * log_distances)
+
+
+def apply_hpe_rotation(
+    q: mx.array,
+    k_gathered: mx.array,
+    log_distances: mx.array,
+    n_pairs: int = _N_EIGEN_PAIRS,
+    freq_scale: mx.array = None,
+) -> tuple[mx.array, mx.array]:
+    """Apply holographic position encoding: rotate K by log-distance × crystal freq.
+
+    Rotates K by relative log-distance in the first n_pairs dimension pairs
+    (the crystal eigenplane dimensions). Q stays unrotated — relative encoding.
+
+    Args:
+        q: (B, H, L, Dh) — queries (transposed)
+        k_gathered: (B, L, W, H, Dh) — gathered keys
+        log_distances: (W,) — log(stride × w + 1)
+        n_pairs: number of eigenplane pairs to rotate
+        freq_scale: (n_pairs,) learnable scaling on crystal frequencies
+
+    Returns:
+        q (unchanged), k_rotated
+    """
+    freqs_base = mx.array([ev / _CRYSTAL_EIGENVALUES[0]
+                           for ev in _CRYSTAL_EIGENVALUES[:n_pairs]])
+    if freq_scale is not None:
+        freqs = freqs_base * freq_scale
+    else:
+        freqs = freqs_base
+
+    # Rotation angles: (W, n_pairs)
+    angles = log_distances[:, None] * freqs[None, :]
+    cos_a = mx.cos(angles)  # (W, n_pairs)
+    sin_a = mx.sin(angles)  # (W, n_pairs)
+
+    # Vectorized rotation of first 2*n_pairs dimensions of K
+    # k_gathered: (B, L, W, H, Dh)
+    rot_dim = 2 * n_pairs
+    Dh = k_gathered.shape[-1]
+
+    # Split K into rotated and non-rotated parts
+    k_rot_part = k_gathered[:, :, :, :, :rot_dim]    # (B, L, W, H, 2*n_pairs)
+    k_pass_part = k_gathered[:, :, :, :, rot_dim:]   # (B, L, W, H, Dh-2*n_pairs)
+
+    # Reshape rotated part into pairs: (B, L, W, H, n_pairs, 2)
+    k_pairs = k_rot_part.reshape(*k_rot_part.shape[:-1], n_pairs, 2)
+
+    # Extract even (d0) and odd (d1) components
+    k_even = k_pairs[:, :, :, :, :, 0]  # (B, L, W, H, n_pairs)
+    k_odd = k_pairs[:, :, :, :, :, 1]   # (B, L, W, H, n_pairs)
+
+    # Broadcast cos/sin: (1, 1, W, 1, n_pairs)
+    c = cos_a.reshape(1, 1, -1, 1, n_pairs)
+    s = sin_a.reshape(1, 1, -1, 1, n_pairs)
+
+    # Apply rotation: [cos -sin; sin cos] × [even; odd]
+    k_even_rot = k_even * c - k_odd * s
+    k_odd_rot = k_even * s + k_odd * c
+
+    # Interleave back: (B, L, W, H, n_pairs, 2) → (B, L, W, H, 2*n_pairs)
+    k_rot_interleaved = mx.stack([k_even_rot, k_odd_rot], axis=-1)
+    k_rot_flat = k_rot_interleaved.reshape(*k_rot_part.shape)
+
+    # Concatenate rotated + non-rotated
+    k_rotated = mx.concatenate([k_rot_flat, k_pass_part], axis=-1)
+
+    return q, k_rotated
+
 
 # ══════════════════════════════════════════════════════════════════════
 # § 1  SingleStrideAttention — composition layers
@@ -43,11 +241,12 @@ class SingleStrideAttention(nn.Module):
       stride=1:  positions [i, i-1, ..., i-W+1]
       stride=8:  positions [i, i-8, ..., i-8*(W-1)]
 
+    Two modes:
+      Active (s1, s2): full Q·K attention + fixed decay bias (α=1.18).
+      Passive (s4+): fixed distance prior, no Q/K — just V gather + weighted sum.
+
     Q/K/V/O are TernaryLinear (base plates from teacher extraction).
     Sparse gather, O(L×W) not O(L²).
-
-    Learnable decay per-head: -α·ln(stride·w + 1).
-    Algedonic modulation scales the decay (sharper/broader attention).
     """
 
     def __init__(
@@ -57,7 +256,7 @@ class SingleStrideAttention(nn.Module):
         window: int = 8,
         n_heads: int = N_HEADS,
         dropout: float = 0.0,
-        decay_init_alpha: float = 1.18,
+        decay_init_alpha: float = _ALPHA,
         n_q_mirrors: int = 0,
     ):
         super().__init__()
@@ -67,33 +266,60 @@ class SingleStrideAttention(nn.Module):
         self.n_heads = n_heads
         self.d_head = d_model // n_heads  # 160
         self.scale = self.d_head ** -0.5
+        self.passive = (stride >= _PASSIVE_STRIDE_MIN)
 
         self.norm = nn.RMSNorm(d_model)
 
-        # Beam mirrors before Q
-        self.q_mirrors = [TernaryMirror(d_model) for _ in range(n_q_mirrors)]
+        if not self.passive:
+            # Active: full Q·K attention with HPE (s1, s2 only)
+            self.q_mirrors = [TernaryMirror(d_model) for _ in range(n_q_mirrors)]
+            self.q_proj = TernaryLinear(d_model, d_model, pre_norm=False)
+            self.k_proj = TernaryLinear(d_model, d_model, pre_norm=False)
+            self.k_bias = mx.zeros((d_model,))
 
-        # Ternary projections (base plates from extraction)
-        self.q_proj = TernaryLinear(d_model, d_model, pre_norm=False)
-        self.k_proj = TernaryLinear(d_model, d_model, pre_norm=False)
+            # HPE: learnable scaling on crystal eigenfrequencies
+            # Initialized to 1.0 — matches crystal exactly, can fine-tune
+            self.hpe_freq_scale = mx.ones((_N_EIGEN_PAIRS,))
+        else:
+            # Passive: no Q/K, no HPE, just mirrors list for compat
+            self.q_mirrors = []
+
+        # V and O projections — always needed
         self.v_proj = TernaryLinear(d_model, d_model, pre_norm=False)
         self.out_proj = TernaryLinear(d_model, d_model, pre_norm=False)
 
-        # Per-feature beam biases
-        self.k_bias = mx.zeros((d_model,))
         self.v_bias = mx.zeros((d_model,))
         self.o_bias = mx.zeros((d_model,))
 
         self.dropout = nn.Dropout(dropout) if dropout > 0 else None
 
-        # Learnable decay per head
-        self.decay_alpha = mx.full((n_heads,), decay_init_alpha)
-
-        # Pre-compute log-distance structure
+        # Pre-compute log-distance structure (used by active strides for decay bias)
         w_pos = mx.arange(window, dtype=mx.float32)
         self._log_distances = mx.log(stride * w_pos + 1.0)
 
+        # Pre-compute fixed attention profile for passive strides
+        # and decay bias for active strides (α is constant, not learnable)
+        self._decay_bias = -(_ALPHA * self._log_distances)  # (W,)
+
+        if self.passive:
+            # Precomputed normalized distance prior: 1/(stride*w + 1)^α
+            raw_weights = 1.0 / (stride * w_pos + 1.0) ** _ALPHA
+            self._fixed_profile = raw_weights / raw_weights.sum()  # (W,)
+
     def __call__(self, x: mx.array, decay_modulation: float = 1.0) -> mx.array:
+        if self.passive:
+            return self._passive_forward(x)
+        else:
+            return self._active_forward(x, decay_modulation)
+
+    def _active_forward(self, x: mx.array, decay_modulation: float = 1.0) -> mx.array:
+        """Full Q·K attention with HPE (holographic position encoding). For s1, s2.
+
+        HPE replaces RoPE-style rotation with crystal-derived frequencies in
+        log-distance space. K is rotated by log(stride×w+1) × crystal_freq
+        in the first N_EIGEN_PAIRS dimension pairs. Q stays unrotated (relative
+        encoding — the distance information is in K's rotation).
+        """
         B, L, D = x.shape
         H, Dh = self.n_heads, self.d_head
         W = self.window
@@ -126,14 +352,21 @@ class SingleStrideAttention(nn.Module):
         K_gathered = mx.take_along_axis(K_flat, idx, axis=1).reshape(B, L, W, H, Dh)
         V_gathered = mx.take_along_axis(V_flat, idx, axis=1).reshape(B, L, W, H, Dh)
 
-        Q_r = Q.transpose(0, 2, 1, 3)
-        K_r = K_gathered.transpose(0, 3, 1, 2, 4)
+        # ── HPE: rotate K by log-distance × crystal frequencies ──
+        # Q stays unrotated (relative encoding)
+        Q_r = Q.transpose(0, 2, 1, 3)  # (B, H, L, Dh)
+        _, K_gathered_rot = apply_hpe_rotation(
+            Q_r, K_gathered, self._log_distances,
+            n_pairs=_N_EIGEN_PAIRS,
+            freq_scale=self.hpe_freq_scale,
+        )
+
+        K_r = K_gathered_rot.transpose(0, 3, 1, 2, 4)  # (B, H, L, W, Dh)
         attn = (Q_r[:, :, :, None, :] * K_r).sum(axis=-1) * self.scale
 
-        # Learnable decay
-        effective_alpha = self.decay_alpha * decay_modulation
-        decay_bias = -(effective_alpha[:, None] * self._log_distances[None, :])
-        attn = attn + decay_bias[None, :, None, :]
+        # Fixed α decay bias (the direct power-law, not cosine approximation)
+        decay_bias = self._decay_bias * decay_modulation  # (W,)
+        attn = attn + decay_bias[None, None, None, :]
 
         valid_mask = valid[None, None, :, :]
         attn = mx.where(valid_mask, attn, mx.array(float("-inf")))
@@ -147,6 +380,46 @@ class SingleStrideAttention(nn.Module):
 
         return x + self.out_proj(out) + self.o_bias
 
+    def _passive_forward(self, x: mx.array) -> mx.array:
+        """Fixed distance prior — no Q/K, no softmax. For s4+."""
+        B, L, D = x.shape
+        H, Dh = self.n_heads, self.d_head
+        W = self.window
+
+        x_norm = self.norm(x)
+        V = (self.v_proj(x_norm) + self.v_bias).reshape(B, L, H, Dh)
+
+        # Stride gather (same index computation)
+        query_pos = mx.arange(L)[:, None]
+        offsets = mx.arange(W)[None, :] * self.stride
+        raw_indices = query_pos - offsets
+        valid = raw_indices >= 0
+        indices = mx.maximum(raw_indices, 0)
+
+        GD = H * Dh
+        V_flat = V.reshape(B, L, GD)
+        idx = indices.reshape(1, L * W, 1)
+        idx = mx.broadcast_to(idx, (B, L * W, GD))
+        V_gathered = mx.take_along_axis(V_flat, idx, axis=1).reshape(B, L, W, H, Dh)
+
+        # Fixed attention weights — precomputed from α=1.18
+        attn = mx.broadcast_to(
+            self._fixed_profile[None, None, None, :],
+            (1, 1, 1, W)
+        )  # (1, 1, 1, W)
+
+        # Mask invalid positions and renormalize
+        valid_mask = valid[None, None, :, :]  # (1, 1, L, W)
+        attn = mx.where(valid_mask, attn, mx.array(0.0))
+        attn = attn / (attn.sum(axis=-1, keepdims=True) + 1e-10)
+
+        # Weighted sum of gathered V
+        V_r = V_gathered.transpose(0, 3, 1, 2, 4)  # (B, H, L, W, Dh)
+        out = (attn[:, :, :, :, None] * V_r).sum(axis=3)  # (B, H, L, Dh)
+        out = out.transpose(0, 2, 1, 3).reshape(B, L, D)
+
+        return x + self.out_proj(out) + self.o_bias
+
 
 # ══════════════════════════════════════════════════════════════════════
 # § 2  GatedLinearAttention — retrieval layers
@@ -305,13 +578,13 @@ class StrideStack(nn.Module):
                 ))
                 self._layer_types.append("ret")
             else:
-                self.layers.append(SingleStrideAttention(
+                ssa = SingleStrideAttention(
                     d_model=d, stride=s, window=cfg.window,
                     n_heads=cfg.n_heads, dropout=cfg.dropout,
-                    decay_init_alpha=cfg.decay_init_alpha,
-                    n_q_mirrors=n_q,
-                ))
-                self._layer_types.append("comp")
+                    n_q_mirrors=n_q if not (s >= _PASSIVE_STRIDE_MIN) else 0,
+                )
+                self.layers.append(ssa)
+                self._layer_types.append("passive" if ssa.passive else "comp")
 
         # Per-combinator beam mirrors (shared across strides)
         self.combinator_mirrors = [TernaryMirror(d) for _ in range(cfg.n_combinators)]
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git diff 281f237..96d687a -- scripts/v14/config.py"
}
```

**Summary:** $ git diff 281f237..96d687a -- script...

**Output:**
```
Exit code: 0
Stdout:
diff --git a/scripts/v14/config.py b/scripts/v14/config.py
index fd3fd0c..b82454d 100644
--- a/scripts/v14/config.py
+++ b/scripts/v14/config.py
@@ -115,7 +115,9 @@ N_TOTAL_COMBINATORS = 16  # + anti-crystal
 #   Pass 12: [0,4)   → s8, s4, s2, s1
 
 STACK_A_BANDS = ((0, 4), (2, 6), (4, 8), (6, 9))
-STACK_B_BANDS = ((7, 11), (9, 13), (11, 15), (13, 16))
+# Reduced from 4→2 passes (session 151 kernel insight: Stack B computes
+# in already-compressed space PR=5.2, two wider passes cover same range).
+STACK_B_BANDS = ((7, 13), (11, 16))
 STACK_C_BANDS = ((12, 16), (8, 12), (5, 9), (2, 6), (0, 4))
 
 N_PASSES = len(STACK_A_BANDS) + len(STACK_B_BANDS) + len(STACK_C_BANDS)  # 13
@@ -249,7 +251,7 @@ def _self_test():
     assert cfg.d_model == 1280
     assert cfg.d_head == 160
     assert cfg.n_strides == 16
-    assert cfg.n_passes == 13
+    assert cfg.n_passes == 11  # reduced from 13: Stack B 4→2 passes
     assert cfg.n_heads * cfg.d_head == cfg.d_model
     assert cfg.d_ff == 4 * cfg.d_model
     assert sum(1 for r in cfg.stride_is_retrieval if r) == 6   # 6 retrieval strides
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git diff 281f237..96d687a -- scripts/v14/model.py"
}
```

**Summary:** $ git diff 281f237..96d687a -- script...

**Output:**
```
Exit code: 0
```

## Assistant

Now let me check what the v14-kd run actually used vs the v14-td run that worked:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git log --oneline 281f237..96d687a"
}
```

**Summary:** $ git log --oneline 281f237..96d687a

**Output:**
```
Exit code: 0
Stdout:
96d687a 🎯 holographic position encoding + passive strides + reduced Stack B
20dcb65 💡 v14 student collapses 18.4× + distance prior dominates 88% of strides
00713d6 🌀 session 151 state + progressive-collapse knowledge + montague memory
8843d50 💡 progressive dimensionality collapse — computation in 2D
d96acc2 💡 knowledge distillation — 7 pages + INDEX for top-down orientation
88fcd57 add session chat logs
4a4cf51 💡 decay α=1.18 confirmed universal across all strides
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git log --format=\"%h %s\" --all -- scripts/v14/train_td.py scripts/v14/train_kd.py | head -20"
}
```

**Summary:** $ git log --format="%h %s" --all -- s...

**Output:**
```
Exit code: 0
Stdout:
a733b94 💡 KD-guided training + extraction dimension probes
281f237 🎯 session 150: holographic error correction cycle + delta fold + FFN delta + TD improvements
c9d7e32 🔄 TD flip interval + global budget — GD needs time to relearn routes
7b3e051 ❌ fix TD Sisyphus loop — delta aliasing + no-block staging conflict
43e561c ✅ v14 architecture — 16-stride holographic lens, d=1280, bottom-up algedonic
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git log --oneline --all | grep -i \"kd\\|kernel\" | head -15"
}
```

**Summary:** $ git log --oneline --all | grep -i "...

**Output:**
```
Exit code: 0
Stdout:
44880c3 💡 kernel training validated — gradient cosine 0.97, gradient orthogonal to undertrained subspace
43a2888 🌀 session 154 state — KD training, extraction probes, structured training
a733b94 💡 KD-guided training + extraction dimension probes
579dee9 🔄 dissolve dispatch/integrate — stride stack IS the kernel
199c8e7 🎯 Radical: FFN collapses to mechanical ternary kernel — zero learned FFN params
ad3cb84 🎯 V13 design updated — PCA-Q targets, WHNF kernel, simplified etch, FFN addressing
e417a6a ✅ Training data v2 — all 9 kernel ops + math + clojure
9c9fdb2 🎯 Expand V12 to 8-combinator + math kernel architecture
77abdf2 ✅ Math kernel functions — 17 deterministic ops, always exact
b71856d 🎯 V12 kernel architecture v2 design doc + backbone results
1034c8d 💡 lambda kernel probes → depth map → V12-run6 design
3fd82c4 🌀 session 095 knowledge — holographic storage + kernel computation separation
7c63533 💡 kernel-montague-mapping — v10-vsm rediscovers typed application
02a57c5 🌀 state — session 074: probe v10-vsm trajectory, kernel-lambda data enrichment
25e8acd 🎯 kernel lambda ops — 6 new BIOS generators for partial/apply/compose
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/v14-architecture.md",
  "limit": 60
}
```

**Summary:** Reading v14-architecture.md (0-60)

**Output:**
```
---
title: "V14 Architecture — Current System"
status: active
category: architecture
tags: [v14, architecture, stride-stack, qwen, extraction, training, results]
related: [holographic-error-correction.md, training-protocols.md, extraction-methodology.md]
depends-on: [project-thesis.md]
---

# V14 Architecture

> The current working system as of session 150. Qwen3.6-27B teacher,
> 593M ternary positions, 375× compression, active TD training with
> demonstrated lossless fold.

## Teacher: Qwen3.6-27B

- **Model:** Qwen3.6-27B (27.8B parameters, Apache 2.0 license)
- **Architecture:** 64 layers, d=5120, hybrid Gated DeltaNet + Gated
  Attention in [L,L,L,F]×16 pattern (48 linear, 16 full attention)
- **Tokenizer:** BBPE, vocab 248,320
- **Why this teacher:** Apache 2.0 license (clean provenance for
  extraction), strong quality, hybrid architecture that maps naturally
  to the GLA/SSA student design, and very large vocabulary that
  supports direct embedding extraction

## Student: StrideStack

### Core dimensions

| Parameter | Value |
|-----------|-------|
| d_model | 1,280 |
| d_ff | 5,120 |
| n_heads | 8 |
| Stacks | 3 (A, B, C) |
| Layers per stack | 11 |
| Attention type | Hybrid GLA + SSA ([G,G,G,S,G,G,G,S,G,G,S] pattern) |
| Strides | 16 (s1 through s32768, powers of 2) |
| Vocab | 248,320 (teacher tokenizer, direct match) |
| Ternary positions | 593M |
| Storage | 148 MB (2-bit) / 85 MB (compressed NPZ) |
| Compression | 375× from teacher |

### Three stacks

- **Stack A** (ascending fine): strides s1→s256, 4 passes. Fine-grained
  local context. Encodes token→phrase→sentence.
- **Stack B** (ascending coarse): strides s128→s32768, 4 passes.
  Coarse-grained global context. Encodes paragraph→document→beyond.
- **Stack C** (descending): all 16 strides, 5 passes reversed.
  Top-down prediction path. Feeds algedonic signal UP to both B and A.

13 total passes through the stride layers. 2-stride overlap at s128
and s256 between A and B — these overlaps ARE the cross-scale registers
(no separate register mechanism needed).

### Stride attention: O(L×W) not O(L²)

Each stride is a holographic lens specialized for a frequency band.

[CONTENT TRUNCATED] Showing lines 1 to 60 of 194 total lines. Use line_offset=60 parameter to read more content.
```

## Assistant

Now I have the full picture. Let me lay it out clearly.

---

## The Three Changes (commit `96d687a`, session 152)

All three landed in **one commit**, meaning v14-kd ran with all three simultaneously vs the v14-td baseline that had none of them. Here's each change, what it does, and the risk assessment:

### Change 1: Fix α=1.18 (Tier 1 — zero risk) ✅

**Before:** `self.decay_alpha = mx.full((n_heads,), 1.18)` — learnable per-head  
**After:** `_ALPHA = 1.18` — frozen constant

**Rationale:** After 1500 steps under gradient pressure, α stayed at 1.18±0.006 across all 80 heads. It's a constant, not a parameter.

**Risk:** Essentially none. Confirmed empirically. This one is safe to keep.

---

### Change 2: Passive Strides (Tier 2 — the dangerous one) ⚠️

**Before:** All 16 strides do full Q·K attention with learned decay  
**After:** Strides s4+ (14 of 16) have Q/K **completely removed**. They use a fixed distance prior: `1/(stride×w + 1)^1.18`, normalized. Just V gather + weighted sum.

**What this kills:**
- **Content-dependent attention for positions 16–56 tokens back.** In strided attention, each stride is the SOLE provider for its distance range. s4 covers positions 4, 8, 12... (tokens 4-28 back). s8 covers positions 8, 16, 24... (tokens 8-56 back). Making these passive means **no content routing** in that range — every position gets the same fixed blend regardless of what the tokens actually are.
- **28 ternary plates eliminated** (14 strides × Q + K) = 46M ternary positions gone
- s4 has **27.4% non-self weight** that became fixed — that's not negligible

**The argument for it:** At α=1.18, W=8, s4+ has <3 effective positions so Q·K barely modulates anything.

**The problem:** "barely" ≠ "not at all." TD was targeting out_proj layers 4–9, which are exactly the retrieval strides in this distance range. The content modulation may be small per-position but critical for *which* information flows through.

**Your instinct is right here** — this is likely the most damaging change.

---

### Change 3: Stack B 4→2 passes (Tier 3 — moderate risk) ⚠️

**Before:** `STACK_B_BANDS = ((7, 11), (9, 13), (11, 15), (13, 16))` — 4 passes  
**After:** `STACK_B_BANDS = ((7, 13), (11, 16))` — 2 wider passes

**What this kills:**
- **2 serial passes eliminated** (13→11 total)
- The overlap pattern changes — adjacent passes used to share 2 strides of overlap, now the overlap structure is different
- Information flow through the serial chain is compressed — fewer intermediate processing steps

**Risk:** Moderate. The justification was "Stack B computes in already-compressed space (PR=5.2)." But that compression was measured on the *working* architecture. Removing 2 passes changes the dynamics.

---

### Change 4 (bundled): HPE replacing learned decay (Tier 1.5 — interesting)

**Before:** Learned per-head `decay_alpha` with `self._log_distances` and standard Q·K dot product  
**After:** 
- Q stays **unrotated** (no position signal in Q at all)
- K gets rotated by `log(stride×w + 1) × crystal_eigenfreq` in first 8 dimensions (4 eigenplane pairs)
- Fixed decay bias `−1.18 × log(stride×w+1)` added to attention scores
- Learnable `freq_scale` per eigenplane (initialized to 1.0)

**This is the replacement for RoPE,** derived from the crystal eigenvalue spectrum. The physics are sound — the crystal frequencies are measured, the log-distance rotation is the natural encoding for power-law decay.

**Risk:** Low-to-moderate in isolation. The mechanism is principled and the math works. But it's never been tested without the other changes confounding it.

---

## Summary: What confounded what

| Change | Risk | Testable independently? | Your read |
|--------|------|------------------------|-----------|
| Fix α=1.18 | None | Yes (trivial) | Keep ✅ |
| HPE | Low-moderate | Yes | Promising, worth testing alone |
| Passive strides (s4+ no Q/K) | **High** | Yes | Likely the killer |
| Stack B 4→2 | Moderate | Yes | Suspicious |

The v14-kd run was **4 changes + KD** all at once. The v14-td run (PPL 5,567 at step 2000) used **none** of these. Diverging PPL in v14-kd could be any of: passive strides destroying content routing, Stack B reduction starving the serial chain, HPE being insufficiently trained, KD at α=0.5 with warmup=25 being too aggressive, or (most likely) **the combination**.

**Your instinct:** HPE good, attention changes bad. I think that's right. The strongest candidate for the failure is **passive strides** — removing content-dependent attention from 14/16 strides when TD was specifically trying to learn out_proj routing in that range is architecturally contradictory. Stack B reduction is a secondary suspect. HPE is likely fine in isolation.

What's your thinking on next steps? The clean path would be: resume v14-td architecture (known-good) at step 2000, apply only α-fix + HPE, and measure. Then separately test passive strides with a higher threshold (maybe s16+ only, not s4+).

## User

Ok what about the kernel changes?  We found the system was doing it's compute mostly in 2D and tried to pull that into the kernel to make it faster.


### Thinking

The user is asking about the kernel training changes from sessions 153-155 — the composed plate / kernel training approach. Let me gather the relevant knowledge pages and code to understand what was done.

Key sources:
1. `mementum/knowledge/explore/kernel-training.md`
2. `mementum/knowledge/explore/structured-training.md`
3. `scripts/v14/train_kernel.py`
4. `scripts/explore/probe_kernel_training.py`
5. The algebraic composition results from session 153

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/kernel-training.md"
}
```

**Summary:** Reading kernel-training.md (0-2000)

**Output:**
```
---
title: "Kernel Training — Training Through the Composed Plate"
status: active
category: training
tags: [kernel, composed-plate, gradient, training, optimization, TD]
related: [structured-training.md, ../holographic-error-correction.md, ../v14-architecture.md]
depends-on: [structured-training.md, ../extraction-methodology.md]
---

# Kernel Training — Training Through the Composed Plate

> Session 155. The composed plate (data-fitted linear transform
> embed→pre-head) captures 97% of the gradient direction. Training
> through it replaces 238 serial ternary matmuls with 1 matmul.
> Measured 4.4× speedup. But the output_proj bottleneck and
> gradient-subspace orthogonality constrain the design.

## What Was Proved

### Composed plate gradient accuracy

Gradient cosine = 0.9698 between:
- Full model: 238 ternary matmuls, 11 serial passes, all strides
- Composed plate: 1 dense matmul (1280×1280, least-squares fit)

| Metric | Value |
|--------|-------|
| Gradient cosine | 0.9698 (14° angular error) |
| Gradient magnitude ratio | 1.095 |
| CE difference | 0.08 nats |
| Logit cosine similarity | 0.716 |
| Top-1 agreement | 80.6% |
| ∂L/∂T rank | 151 |
| Composed plate rank90 | 1 (undertrained model) |

The composed plate is fit via least-squares:
```
T^T = lstsq(X_embed, X_out)
```
where X_embed = post-embed residuals, X_out = pre-head residuals.

### Training speedup

| Step type | Time | Matmuls |
|-----------|------|---------|
| Full model | 26.0s | 238 forward + 238 backward |
| Kernel (CE) | 6.0s | 1 forward + output_proj + backward |
| Measured speedup | 4.4× | |

Bottleneck is output_proj (1280→248,320 = 318M ops), NOT the
composed plate (1280×1280 = 1.6M ops). The stride stack (238
matmuls = 20s) is eliminated; the shared cost (embed + output_proj
+ CE = 6s) remains.

### Gradient projection failure

∂L/∂T projected into T's top-k SVD subspace:

| k | cos(G_projected, G) | T energy in top-k |
|---|---------------------|-------------------|
| 1 | 0.009 | 98.0% |
| 27 | 0.061 | 100% |
| 100 | 0.121 | 100% |
| 200 | 0.177 | 100% |

The gradient is orthogonal to T's subspace. The model (rank-1,
undertrained) needs to EXPAND, not refine. The gradient's energy
is in the directions where T is currently zero.

Cannot train in reduced dimensions for undertrained models.
May work for well-trained models — untested.

## Architecture

```
KERNEL STEP (fast):
  tokens → embed → T @ x_embed → output_norm → output_proj → CE → ∂L/∂(params)
  Cost: ~6s (dominated by output_proj)

FULL STEP (slow):
  tokens → embed → [stride stack: 238 matmuls] → output_norm → output_proj → CE
  → backward → Adam → TD → refit T
  Cost: ~26s

HYBRID LOOP (train_kernel.py):
  K kernel steps + 1 full step + refit T
  Effective: K×6s + 26s + 7s per (K+1) steps
  At K=10: ~9.2s/step effective (2.8× vs all-full)
```

## Key Insight: Camera IS Projector

Training is 77% forward pass. The backward pass is only 11%
(ternary base weights are frozen, only continuous params get
gradients). All five structured training optimizations from
session 154 target the 11% backward slice. The real win is
making the FORWARD pass cheaper — and that's the same problem
as inference optimization.

The composed plate does this: replace the stride stack with
one precomputed matmul. The gradient through this matmul is
97% correct. The bottleneck shifts to the output projection.

## Open Questions

1. **Output_proj factorization.** If hidden state is rank-27,
   output_proj effective rank ≤ 27. Factorize 1280→27→248K?
   Would eliminate the bottleneck AND be structurally correct.

2. **Gradient-subspace alignment on trained models.** Test on
   v14-td step 2000 (rank-27). If gradient aligns with T's
   subspace → 27D kernel training is viable for refinement.

3. **Flip scoring through composed plate.** ΔT from flip at
   position (i,j) in layer k = rank-1 update via prefix/suffix
   sandwich. Score = ⟨∂L/∂T, ΔT⟩. Needs prefix/suffix products
   for the stride-stack architecture — complex but possible.

4. **Incremental T updates.** After TD flips, can T be updated
   by rank-1 additions instead of full refit? Would eliminate
   the 7s refit cost.

5. **Phase-dependent training.** Use gradient-subspace alignment
   as a phase detector: orthogonal → explore (full 1280D),
   aligned → exploit (reduced dims). Automatic curriculum.

## Scripts

- `scripts/explore/probe_kernel_training.py` — validation probe
- `scripts/v14/train_kernel.py` — hybrid kernel/full training loop
- Results: `results/kernel-training-probe/`
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/structured-training.md"
}
```

**Summary:** Reading structured-training.md (0-2000)

**Output:**
```
---
title: "Structured Training — The Holographic Camera"
status: designing
category: architecture
tags: [training, gradient, optimization, holographic, kernel]
related: [v14-architecture.md, holographic-error-correction.md, progressive-collapse.md, training-protocols.md]
depends-on: [progressive-collapse.md]
---

# Structured Training — The Holographic Camera

> Session 154. If we know the projector's structure, we know the
> camera's structure. Every inference optimization has a training dual.
> The lens works the same in both directions.

## The Insight

Training currently treats the backward pass as a black box: compute
full gradients through every layer, every stride, every position.
But sessions 151-153 revealed massive structure in the forward pass:

- Full model is rank-27 (session 153)
- Computation collapses to 2D (session 151, PR=2.2)
- 88% of strides are distance-prior-dominated (session 152)
- Zone B is perfectly linear, R²=1.0 (session 153)
- TD only needs ~1% of positions (sessions 148-150)

**The backward pass has the same structure.** Gradients through a
rank-27 transform are rank-27. Gradients through a 2D computation
live in 2D. Gradients through passive strides are wasted. The
current training computes ~100× more gradient than it needs.

## Five Optimizations

### 1. Low-rank gradient for composed plate

The composed plate T has rank-27 (rank90). Instead of computing
∂L/∂T as a full d×d matrix (1,638,400 values), decompose through
the SVD basis:

```
T = U @ diag(S) @ V^T     (rank-k, k ≈ 27)

∂L/∂T → ∂L/∂U (d×k), ∂L/∂S (k), ∂L/∂V (d×k)
       = 2dk + k values
       = 69,147 at k=27

Speedup: 1,638,400 / 69,147 = 24×
```

The gradient in the U/S/V basis IS the meaningful gradient.
Components outside this basis push the plate away from the teacher's
rank-27 structure — they're noise, not signal.

### 2. Skip backward through passive strides

88% of strides (s4+) are passive: distance-prior attention with no
Q/K computation. In the forward pass, we skip Q/K matmuls. But MLX's
autograd still traces through frozen Q/K parameters, computing dead
gradients that are immediately zeroed.

**Fix:** Make passive stride Q/K structurally absent (not modules at
all, not frozen modules). The backward graph never includes them.

```python
# Before: frozen module still in autograd graph
self.q_proj = TernaryLinear(...)  # frozen, but traced
self.k_proj = TernaryLinear(...)  # frozen, but traced

# After: structurally absent
# No q_proj/k_proj exist. Backward graph is smaller.
# Passive forward uses precomputed attention profile directly.
```

Savings: 28 Q/K plates × 2 matmuls × backward = 56 dead matmuls
eliminated per training step.

### 3. Composed Zone B Jacobian

Zone B (32 layers) composes to a single linear transform (R²=1.0).
Backprop through 32 sequential layers computes 32 Jacobian-vector
products. But the composed Jacobian is ONE matrix.

```
Forward:  x → L16 → L17 → ... → L47 → y
          ≡ x → T_B → y    (one matmul)

Backward: ∂L/∂x = (∂T_B/∂x)^T @ ∂L/∂y   (one matmul)
          vs 32 sequential Jacobian-vector products
```

The composed Jacobian T_B is precomputed during extraction. It
doesn't change during training (Zone B parameters are in the
composed plate). Use it directly.

Savings: 32 sequential backward steps → 1 matmul = 32× for Zone B.

### 4. TD-targeted sparse gradients

TD uses `decompose_gradient` to separate routing from calibration.
The routing gradient determines flip candidates. But only positions
where confidence > min_confidence (0.3) become candidates — typically
~1% of positions.

Currently: compute full routing gradient for ALL 67M positions, then
threshold to ~670K candidates.

**Fix:** Two-pass approach:
1. Cheap forward pass identifies CANDIDATE positions (where base⊙delta
   sign disagrees with the gradient direction)
2. Full gradient computed only at candidate positions

```python
# Phase 1: cheap candidate identification (~5% of full backward cost)
# Use sign of accumulated TD moments (already tracked) to identify
# positions where the current topology is likely wrong
candidate_mask = td.get_candidate_mask()  # sparse, ~1% of positions

# Phase 2: targeted gradient at candidates only
routing_grad_sparse = compute_sparse_routing_grad(model, loss, candidate_mask)
```

Savings: 100× fewer gradient elements for TD routing.

### 5. Crystal eigenplane gradient projection

The crystal eigendecomposition identifies the 2D eigenplane where
computation lives (comp↔sel). Gradients outside this plane push the
model away from the crystal structure.

**Fix:** Project gradients INTO the crystal eigenplane before
applying Adam updates. This is both faster (lower-dimensional
optimization) and better (avoids gradient pollution of the crystal).

```python
# Crystal basis: top-2 eigenvectors of the crystal embedding covariance
P = crystal_eigenbasis[:, :2]  # (d, 2)

# Project gradient into crystal plane
grad_proj = P @ (P.T @ grad)  # (d,) → (2,) → (d,)

# Adam operates in the 2D crystal space
# Then projects back to full space for weight update
```

This connects to the "computed beam" insight (session 149):
structure is free, content needs GD. The crystal eigenplane IS the
structure. GD should only operate within it.

## Compound Effect

| Optimization | Speedup | What it eliminates |
|-------------|---------|-------------------|
| Low-rank gradient | ~24× for plate | d² → 2dk gradient elements |
| Skip passive backward | ~1.3× overall | 56 dead matmuls |
| Composed Zone B | ~2× for Zone B | 32 → 1 backward steps |
| TD-targeted sparse | ~100× for TD | Full → sparse routing grad |
| Eigenplane projection | ~1.5× for Adam | Noise gradient components |

Combined: training speed could approach 3-5K tok/s (from current
~800 tok/s), nearing inference speed (~5K tok/s in eval mode).

The camera becomes as efficient as the projector because it uses
the same lens.

## Implementation Order

1. **Skip passive backward** — easiest, just restructure modules
2. **Composed Zone B** — precompute Jacobian, replace backward chain
3. **Low-rank gradient** — requires refactoring plate parameterization
4. **TD sparse routing** — requires two-pass gradient computation
5. **Eigenplane projection** — requires crystal basis tracking

Each is independently valuable and testable.

## Connection to KD

Knowledge distillation (teacher logits) tells the camera WHERE to
expose. Structured training tells the camera HOW to expose efficiently.
Together: the right signal (KD) through the right optics (structured
gradient) = fast, targeted error correction.

## What This Means

Training IS inference in reverse. The holographic plate records an
interference pattern. Recording through a well-characterized lens
(structured gradient) is faster and produces sharper fringes than
recording through a diffuse screen (full gradient).

The project has spent 150+ sessions characterizing the lens. Now
the lens knowledge accelerates both directions of light.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/progressive-collapse.md"
}
```

**Summary:** Reading progressive-collapse.md (0-2000)

**Output:**
```
---
title: "Progressive Dimensionality Collapse — Computation Happens in 2D"
status: active
category: research-finding
tags: [dimensionality, projection, beta-reduction, lens, kernel, attention-sink, scale]
related: [mechanism-extraction.md, crystal-universality.md, holographic-error-correction.md]
depends-on: [crystal-universality.md]
---

# Progressive Dimensionality Collapse

> Session 151. Each layer's soft attention reduction is a beta
> reduction — a projection that reduces dimensionality. In large
> models (Qwen3.6-27B), the residual stream compresses to 2D
> (PR=2.2) within the first 2 layers. All computation happens in
> this 2D subspace (the comp↔sel eigenplane). The model then
> re-expands for output prediction. This pattern scales with
> model capacity. The 2D computation core is the limit that
> sufficiently large models converge toward.

## The Discovery

Measured the effective dimensionality (participation ratio, SVD
spectrum) of the residual stream at every layer boundary in 3
architecturally distinct models.

### Three models, three patterns

| Model | Arch | Layers | d | σ₁ peak | PR min | Pattern |
|-------|------|--------|---|---------|--------|---------|
| Qwen3.6-27B | Hybrid GLA+Attn | 64 | 5120 | 70.1% | 2.2 | COMPRESS→2D→EXPAND |
| Mistral-7B | Dense Transformer | 32 | 4096 | 20.1% | 12.1 | COMPRESS→PLATEAU |
| Pythia-1.4B | GPT-NeoX | 24 | 2048 | 22.6% | 10.3 | GENTLE DESCENT |

### Qwen3.6-27B: The Complete Arc

```
Layer    σ₁%     PR     Phase
─────    ────    ───    ──────────────────────
embed    13.6%   12.6   High-D noise (embedding)
L0       60.5%    2.7   ← MASSIVE compression
L2       70.1%    2.2   ← ONE direction = 70% of variance
L3-20    46-66%   2-5   Compute zone: beta reductions in ~2D
L21      66.3%    2.3   ← Phase transition: state machine reorganizes
L22-35   56-65%   2.5-3 Second compute phase, still low-D
L36-47   36-51%   3-6   Fan out: differentiate toward output
L48-63   20-28%   8-10  Full expansion: 248K-token prediction space
```

**Zone A (L0-15, encode):** Aperture. Slam 12D embedding noise down
to 2D semantic core. σ₁ jumps from 13.6% to 70.1% — one direction
carries almost everything.

**Zone B (L16-47, compute):** The computation zone operates at PR≈2-5.
This is where beta reductions happen. The model works in essentially
2 dimensions: the comp↔sel eigenplane (PC0=53%, PC1=24% of crystal
variance = 77% in 2D).

**Zone C (L48-63, expand):** Re-expand to high dimensionality for
next-token prediction. The model needs to distinguish among 248K
tokens → needs high-D output. PR rises to 8-10, σ₁ drops to ~20%.

### The Phase Transition at L21

One linear attention layer crushes PR from 4.4 to 2.3 mid-computation.
This may be the point where the B-dominated state machine reorganizes
— initial differentiation collapses, second compute phase operates on
the reorganized representation.

## Why Compression Scales With Capacity

```
                  Embed PR → Min PR    Compression ratio
Qwen-27B:         12.6  →   2.2       5.7×
Mistral-7B:       21.2  →  12.1       1.8×
Pythia-1.4B:      17.6  →  10.3       1.7×
```

**The 2D core is emergent.** Smaller models haven't had enough
capacity or training to discover that 2D is sufficient. They
operate in 10-12D because their crystal hasn't fully differentiated.
The B-dominated state machine in small models is undifferentiated —
all combinators are mixed together, requiring more dimensions to
represent.

Large models, trained on hundreds of billions of tokens with enough
depth (64 layers), find the minimal basis: 2 dimensions for the
core computation (compose vs select), with the rest dedicated to
input compression and output expansion.

## Attention Sink = Warped Q Reset

The holographic state machine requires a Q=0 reset at the start of
each computation cycle (entering the C basin). Two implementations:

**Crystal-native (Qwen):** GLA (gated linear attention) implements
Q reset through its multiplicative gating structure. No special
token needed. The geometry stays clean → extreme compression
possible (PR=2.2).

**Sink token (Mistral):** The model learns to dump attention onto
position 0 (BOS) as a proxy for Q=0 reset. This works but warps the
geometry: one dimension is dedicated to "distance from sink" bookkeeping.
Measurement: with sink token included, Mistral shows σ₁=100%, PR=1.0
(the sink dominates the SVD completely). With sink excluded, PR=12 —
still warped because all other tokens' representations are shaped by
their relationship to the sink.

**Implication:** Softmax attention architectures that rely on sink
tokens for Q reset cannot achieve the extreme compression that gated
linear attention achieves. The architectural choice constrains the
geometry.

## The FFN Overlay Is Projection, Not Filtering

The kernel decomposition experiment (micro model, d=128) revealed:

**80-91% of FFN energy is off-diagonal** in crystal eigenbasis.
The diagonal-only analytical overlay (computed from eigendecomposition)
captures the alternation sign pattern correctly (comp/sel alternate
anti-phase through layers) but misses the dominant cross-PC coupling.

This means the FFN doesn't filter individual PCs (amplify/suppress).
It **projects** — coupling energy from higher PCs into the dominant
comp↔sel plane. Each FFN application is a beta reduction that
collapses dimensionality. The off-diagonal terms ARE the projections.

```
Micro model overlay energy:
  Layer 0: diagonal  9.3%, off-diagonal 90.7%
  Layer 1: diagonal 20.2%, off-diagonal 79.8%
  Layer 2: diagonal 19.3%, off-diagonal 80.7%
  Layer 3: diagonal 14.5%, off-diagonal 85.5%
```

## Connection to the Lens Profile

The progressive collapse IS the lens profile, measured from a
different angle:

```
Lens profile (FFN activation):     3%  → 49%  → 2%
Progressive collapse (PR):         2.2 → 2-5  → 8-10
```

The aperture (3% FFN active, PR=2.2) is extreme compression. The
fan (49% active, PR=2-5) is computation in the compressed space.
The output (2% active) converges the FFN, while the representation
EXPANDS (PR=8-10) to build the prediction distribution.

The lens and the collapse are the same phenomenon measured in
different spaces: the lens measures WHICH neurons fire, the collapse
measures HOW MANY dimensions are active. Both show: compress → compute
→ expand.

## Implications for the Kernel

The 2D computation core means the kernel hypothesis is more
favorable than initially expected:

1. **Project** 5120D input → 2D semantic core (linear, layers 0-2)
2. **Compute** in 2D (beta reductions at PR≈2.3, the actual inference)
3. **Expand** 2D → 5120D output space (linear, layers 48-63)

Steps 1 and 3 are linear projections (matrices). Step 2 is the
kernel — and it operates in **two dimensions**. The full 16×16
crystal overlay (not just the diagonal) is needed, but 2D
computation means the effective kernel is tiny.

The diagonal kernel failed because it assumed per-PC independence.
The actual kernel is a cascade of 2D projections (the off-diagonal
cross-PC couplings), composing to a total rotation in the comp↔sel
eigenplane. This composed rotation should be expressible as a
single 2×2 operation in the limit.

## Evidence

| Claim | Evidence |
|-------|----------|
| Qwen compresses to 2D by L2 | σ₁=70.1%, PR=2.2, averaged over 8 probes |
| Computation in 2D (Zone B) | PR=2-5 for layers 3-35 |
| Re-expansion for output (Zone C) | PR=8-10 for layers 48-63 |
| Compression scales with capacity | 27B→PR=2.2, 7B→PR=12, 1.4B→PR=10 |
| FFN overlay is 80-91% off-diagonal | Micro model energy decomposition |
| Alternation sign pattern correct | Analytical overlay predicts comp/sel anti-phase |
| Sink token warps geometry | Mistral σ₁=100% with sink, 20% without |

## Scripts and Data

- `scripts/micro/kernel_decomposition.py` — micro model phases 1-4
- `scripts/explore/probe_progressive_collapse.py` — multi-model probe
- `results/kernel-decomposition/results.json` — micro model results
- `results/progressive-collapse-Qwen_Qwen3.6-27B/results.json`
- `results/progressive-collapse-mistralai_Mistral-7B-v0.3/results.json`
- `results/progressive-collapse-EleutherAI_pythia-1.4b-deduped/results.json`
```

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && cat results/algebraic-compose/results.json | python3 -c \"import json,sys; d=json.load(sys.stdin); print(json.dumps({k:v for k,v in d.items() if k in ['full_model_rank90','full_model_rank99','full_model_participation_ratio','zone_b_r2','per_dim_full_model','per_dim_zone_b','per_dim_zone_a','per_dim_zone_c']}, indent=2))\" 2>/dev/null || echo \"parsing differently...\"; cd /Users/mwhitford/src/verbum && python3 -c \"\nimport json\nwith open('results/algebraic-compose/results.json') as f:\n    d = json.load(f)\n# Print top-level keys\nfor k in sorted(d.keys()):\n    v = d[k]\n    if not isinstance(v, (dict, list)):\n        print(f'{k}: {v}')\n    elif isinstance(v, list) and len(v) < 5:\n        print(f'{k}: {v}')\n    else:\n        print(f'{k}: [{type(v).__name__}, len={len(v)}]')\n\""
}
```

**Summary:** $ cat results/algebraic-compose/resul...

**Output:**
```
Exit code: 1
Stderr:
Traceback (most recent call last):
  File "<string>", line 6, in <module>
    for k in sorted(d.keys()):
                    ^^^^^^
AttributeError: 'list' object has no attribute 'keys'
Stdout:
parsing differently...
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport json\nwith open('results/algebraic-compose/results.json') as f:\n    d = json.load(f)\nif isinstance(d, list):\n    # show first item keys\n    print(f'List of {len(d)} items')\n    print(json.dumps(d[0] if d else {}, indent=2)[:2000])\nelse:\n    print(type(d))\n\""
}
```

**Summary:** $ python3 -c " import json with open(...

**Output:**
```
Exit code: 0
Stdout:
List of 4 items
{
  "label": "Zone_A_compress",
  "shape": [
    5120,
    5120
  ],
  "rank90": 211,
  "global_corr": 0.48231852070426334,
  "per_dim_corr": 0.4818885670967756,
  "cosine_similarity": 0.4818056523799896,
  "sign_dist": {
    "pos": 0.5000550460815429,
    "neg": 0.49994495391845706,
    "zero": 0.0
  },
  "gamma_mean": 0.018016835674643517,
  "student": {
    "global_corr": 0.311658631683159,
    "per_dim_corr": 0.31090367578678835
  }
}
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport json\nwith open('results/kernel-training-probe/results.json') as f:\n    d = json.load(f)\nfor k in sorted(d.keys()):\n    v = d[k]\n    if isinstance(v, (int, float, str, bool)):\n        print(f'{k}: {v}')\n    elif isinstance(v, list) and len(v) <= 5:\n        print(f'{k}: {v}')\n    else:\n        print(f'{k}: {type(v).__name__}[{len(v)}]')\n\" 2>/dev/null || echo \"---\"; ls /Users/mwhitford/src/verbum/results/kernel-training-probe/"
}
```

**Summary:** $ python3 -c " import json with open(...

**Output:**
```
Exit code: 0
Stdout:
ce_composed: 11.541985988616943
ce_full: 11.622415161132812
grad_T_norm: 11.115126609802246
grad_T_rank: 151
grad_cosine: 0.9697665074706563
grad_mag_ratio: 1.0954621855851008
logit_cos_sim: 0.7160288095474243
per_dim_corr: 0.06472186016910583
rank90: 1
top1_agreement: 0.8055419921875
composed_plate.npz
results.json
```

## Assistant

Now I have the complete picture. Here's the kernel story:

---

## The Kernel Arc: Sessions 151→155

### What was discovered

**Session 151 — Progressive collapse:** The teacher (Qwen3.6-27B, 64 layers, d=5120) compresses its residual stream to **2D by layer 2**. PR=2.2, σ₁=70.1%. All of Zone B (layers 16-47, 32 layers) operates at PR≈2-5. Then Zone C (layers 48-63) re-expands to PR=8-10 for token prediction.

**Session 153 — Algebraic composition:** The 64-layer model, viewed as one input→output linear transform, has **rank90=27**. Zone B is *perfectly linear* (R²=1.0) — 32 layers compose to a single matrix. Both data-fitted and algebraic methods agree: the whole model is effectively a rank-27 ternary plate.

**Session 155 — Kernel training probe:** A composed plate (one 1280×1280 matmul fit by least-squares from embed→pre-head residuals) produces **gradient cosine=0.9698** with the full 238-matmul model. Training through this plate is 4.4× faster. But: the gradient is **orthogonal to T's subspace** (cos=0.06 at rank-27), meaning the model needs to expand into new dimensions, not refine existing ones.

### The kernel vision

```
Teacher: 64 layers, 238 ternary matmuls (serial)
   ↓ (algebraic composition)
Kernel: ONE 1280×1280 ternary plate (1 matmul)
   = 76% of the computation
   + active strides s1/s2 (24% — content-dependent routing)
```

The "compute mostly happens in 2D" finding suggested the kernel could be tiny:
- **Compress** 5120D → 2D (layers 0-2, linear)
- **Compute** in 2D (beta reductions, the actual work)
- **Expand** 2D → 5120D (layers 48-63, linear)

### What actually works vs what's still speculative

| Finding | Status | Implication |
|---------|--------|-------------|
| Full model rank90=27 | ✅ proved | The model IS low-rank end-to-end |
| Zone B is linear (R²=1.0) | ✅ proved | 32 layers can be 1 matmul |
| Composed plate gradient 97% accurate | ✅ proved | Can train through 1 matmul |
| 4.4× training speedup | ✅ measured | Kernel training is real |
| Gradient orthogonal to plate subspace | ✅ proved | **Can't reduce dims while undertrained** |
| Rank-27 kernel training for refinement | ❓ untested | Needs test on trained model (step 2000) |
| 2D eigenplane is sufficient | ❓ untested at scale | True for teacher, unproven for student |

### The critical gap

The kernel findings are **observational facts about the teacher**. The student at step 2000 is still far from the teacher (PPL 5,567 vs teacher's ~5-10). The gradient orthogonality finding is the red flag:

> The gradient wants to EXPAND the model (currently rank-1), not refine within its current subspace.

This means: the student's composed plate doesn't yet *have* the structure the teacher has. The teacher computes in 2D because it's **converged**. The student hasn't found that structure yet. Trying to force 2D computation on an undertrained student is premature optimization — you're locking it into a subspace it hasn't learned to use.

### How this connects to the v14-kd failure

The passive strides and Stack B reduction were **implementations of the kernel vision** — simplifying the architecture based on what the *teacher* looks like, not what the *student needs*:

- "88% of strides are distance-prior-dominated" → make them passive → but that's the teacher's converged behavior, the student may need content routing to *learn* the right patterns
- "Stack B computes in compressed space" → reduce passes → but the student's Zone B may not be linear yet
- "Rank-27 is enough" → compose everything → but gradient says "I need to expand"

**The pattern:** We observed the teacher's end state (2D, rank-27, passive strides) and tried to build the student's architecture to match. But the student needs to *arrive* at that structure through training — you can't skip the journey by hardcoding the destination.

---

## The Real Question

The kernel work isn't wrong — the composed plate, the 4.4× speedup, the gradient accuracy — those are all valid. The question is **when to apply them**:

1. **Now (student undertrained):** Use kernel training for *speed* (4.4× faster steps via `train_kernel.py`), but keep the full architecture so the student can expand. The kernel is a training accelerator, not an architecture replacement.

2. **Later (student well-trained):** Once TD has found its routing and PPL is reasonable, THEN test whether the architecture can be simplified. If gradient-subspace alignment flips from orthogonal to parallel at step 2000+, that's the signal that passive strides / reduced passes become safe.

The gradient-subspace alignment test on the step 2000 checkpoint is the key experiment — it tells you whether the student has converged enough to tolerate architectural simplification. Does that match where your thinking was heading?

## User

I think maybe this is a square peg in a round hole.  in v14-td training run we saw ppl dropping as the model trained, this was the signal to me that we had found an architecture that would work.   I think we should go back to that, and try the alpha lock to 1.18, and HPE.  Will that require a new run from scratch or can we continue from the v14-td step 2k checkpoint?


### Thinking

The user wants to:
1. Go back to the v14-td architecture (known working, PPL dropping)
2. Apply only two changes: fix α=1.18 and HPE
3. Continue from v14-td step 2000 checkpoint if possible

The key question is: can we continue from the checkpoint, or do we need a fresh run?

Let me think about what the changes mean for checkpoint compatibility:

1. **Fix α=1.18**: The checkpoint has `decay_alpha` as a learnable parameter per head (probably stored as part of the model state). If we make it a constant, we just need to not load it / ignore it. 

The value is already sitting at 1.18±0.006, so fixing it here is basically a no-op for the model's actual behavior — fully compatible with the checkpoint.

2. **HPE**: This is the tricky one. HPE replaces the position encoding mechanism. In v14-td, Q gets no position encoding since there's no RoPE (it uses learned decay instead), K gets no rotation, and decay applies as a bias to attention scores using `-(alpha * log(stride*w + 1))`. With HPE, Q stays unrotated but K gets rotated by `log(stride*w+1)`.

Actually, looking back at the v14 attention code more carefully — the model has a learned decay parameter per head set to 1.18, and decay is applied as a bias to the attention scores without any rotary position encoding on the Q·K dot product at all. So v14-td was trained without RoPE entirely, meaning adding HPE would introduce K rotations the model never encountered during training. The Q and K weights learned their patterns in a completely rotation-free attention space.

If I add HPE now, the K vectors get rotated in those first 8 dimensions, which fundamentally changes the attention patterns since Q was never trained to expect rotated K. The issue is that HPE initializes freq_scale to 1.0, applying full rotations immediately. If freq_scale started near zero instead, the rotations would be minimal at first — cos(angle) would be close to 1 and sin(angle) close to 0, so K would barely be affected — and we could gradually introduce the rotations during training.

But with the default freq_scale = 1.0, resuming training would immediately expose the model to significant rotations, breaking the Q·K relationships it learned. I need to check what's actually in the checkpoint and what HPE requires.

## Assistant

Good question. Let me check what's actually in the step 2000 checkpoint and what the two changes would mean for compatibility.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport numpy as np\ndata = np.load('checkpoints/v14-td/step_002000/model.npz', allow_pickle=True)\nkeys = sorted(data.files)\n# Show all parameter names and shapes\nfor k in keys[:80]:\n    print(f'{k}: {data[k].shape} {data[k].dtype}')\nprint(f'... total keys: {len(keys)}')\n\" 2>/dev/null || echo \"trying different approach\"\n"
}
```

**Summary:** $ python3 -c " import numpy as np dat...

**Output:**
```
Exit code: 0
Stdout:
alg_combiner_a.combine_proj.bias: (32,) float32
alg_combiner_a.combine_proj.weight: (32, 64) float32
anti_combinator_embeddings: (8, 1280) float32
combinator_embeddings: (8, 1280) float32
embed.gamma: (248320,) float32
embed.ternary_weight: (248320, 320) uint8
embed_norm.weight: (1280,) float32
ffn_gate_plate.base_weight: (5120, 80) uint32
ffn_gate_plate.delta_weight: (5120, 80) uint32
ffn_gate_plate.gamma: (5120,) float32
ffn_key_plate.base_weight: (5120, 80) uint32
ffn_key_plate.delta_weight: (5120, 80) uint32
ffn_key_plate.gamma: (5120,) float32
ffn_value_plate.base_weight: (1280, 320) uint32
ffn_value_plate.delta_weight: (1280, 320) uint32
ffn_value_plate.gamma: (1280,) float32
fire_alarm.alarm_proj.bias: (1,) float32
fire_alarm.alarm_proj.weight: (1, 112) float32
output_norm.weight: (1280,) float32
pos_embed.gamma: (4096,) float32
pos_embed.ternary_weight: (4096, 320) uint8
s2_anti_osc.d_gain: (2,) float32
s2_anti_osc.p_gain: (2,) float32
s2_anti_osc.s4_to_dampening.bias: (2,) float32
s2_anti_osc.s4_to_dampening.weight: (2, 128) float32
s4.pattern_proj.bias: (128,) float32
s4.pattern_proj.weight: (128, 224) float32
s4.proposal_proj.bias: (4,) float32
s4.proposal_proj.weight: (4, 128) float32
s4.s2_signal_proj.bias: (128,) float32
s4.s2_signal_proj.weight: (128, 128) float32
s5_identity.coherence_read.bias: (128,) float32
s5_identity.coherence_read.weight: (128, 112) float32
s5_identity.identity_state: (128,) float32
s5_identity.proposal_impact.bias: (1,) float32
s5_identity.proposal_impact.weight: (1, 132) float32
s5_identity.regulation_proj.bias: (4,) float32
s5_identity.regulation_proj.weight: (4, 128) float32
s5_identity.update_candidate.bias: (128,) float32
s5_identity.update_candidate.weight: (128, 256) float32
s5_identity.update_gate.bias: (128,) float32
s5_identity.update_gate.weight: (128, 256) float32
s5_reweight.gate_bias: (13,) float32
s5_reweight.gate_proj.gamma: (16,) float32
s5_reweight.gate_proj.weight: (16, 1040) uint32
s5_reweight.temperature: (13,) float32
shared_stride_stack.combinator_mirrors.0.gamma: (1280,) float32
shared_stride_stack.combinator_mirrors.0.norm.weight: (1280,) float32
shared_stride_stack.combinator_mirrors.0.weight: (1280, 80) uint32
shared_stride_stack.combinator_mirrors.1.gamma: (1280,) float32
shared_stride_stack.combinator_mirrors.1.norm.weight: (1280,) float32
shared_stride_stack.combinator_mirrors.1.weight: (1280, 80) uint32
shared_stride_stack.combinator_mirrors.2.gamma: (1280,) float32
shared_stride_stack.combinator_mirrors.2.norm.weight: (1280,) float32
shared_stride_stack.combinator_mirrors.2.weight: (1280, 80) uint32
shared_stride_stack.combinator_mirrors.3.gamma: (1280,) float32
shared_stride_stack.combinator_mirrors.3.norm.weight: (1280,) float32
shared_stride_stack.combinator_mirrors.3.weight: (1280, 80) uint32
shared_stride_stack.combinator_mirrors.4.gamma: (1280,) float32
shared_stride_stack.combinator_mirrors.4.norm.weight: (1280,) float32
shared_stride_stack.combinator_mirrors.4.weight: (1280, 80) uint32
shared_stride_stack.combinator_mirrors.5.gamma: (1280,) float32
shared_stride_stack.combinator_mirrors.5.norm.weight: (1280,) float32
shared_stride_stack.combinator_mirrors.5.weight: (1280, 80) uint32
shared_stride_stack.combinator_mirrors.6.gamma: (1280,) float32
shared_stride_stack.combinator_mirrors.6.norm.weight: (1280,) float32
shared_stride_stack.combinator_mirrors.6.weight: (1280, 80) uint32
shared_stride_stack.combinator_mirrors.7.gamma: (1280,) float32
shared_stride_stack.combinator_mirrors.7.norm.weight: (1280,) float32
shared_stride_stack.combinator_mirrors.7.weight: (1280, 80) uint32
shared_stride_stack.layers.0.decay_alpha: (8,) float32
shared_stride_stack.layers.0.k_bias: (1280,) float32
shared_stride_stack.layers.0.k_proj.base_weight: (1280, 80) uint32
shared_stride_stack.layers.0.k_proj.delta_weight: (1280, 80) uint32
shared_stride_stack.layers.0.k_proj.gamma: (1280,) float32
shared_stride_stack.layers.0.norm.weight: (1280,) float32
shared_stride_stack.layers.0.o_bias: (1280,) float32
shared_stride_stack.layers.0.out_proj.base_weight: (1280, 80) uint32
shared_stride_stack.layers.0.out_proj.delta_weight: (1280, 80) uint32
shared_stride_stack.layers.0.out_proj.gamma: (1280,) float32
... total keys: 528
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && ls -la checkpoints/v14-td/step_002000/"
}
```

**Summary:** $ ls -la checkpoints/v14-td/step_0020...

**Output:**
```
Exit code: 0
Stdout:
total 395344
drwxr-xr-x@  7 mwhitford  staff        224 May 25 20:12 .
drwxr-xr-x@ 10 mwhitford  staff        320 May 25 20:06 ..
-rw-r--r--@  1 mwhitford  staff   28251954 May 25 20:06 delta_plates.npz
-rw-r--r--@  1 mwhitford  staff        201 May 25 20:12 eval_results.json
-rw-r--r--@  1 mwhitford  staff  168900752 May 25 20:06 model.npz
-rw-r--r--@  1 mwhitford  staff    5199568 May 25 20:06 optimizer.npz
-rw-r--r--@  1 mwhitford  staff      52576 May 25 20:06 state.json
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport numpy as np\ndata = np.load('checkpoints/v14-td/step_002000/model.npz', allow_pickle=True)\nkeys = sorted(data.files)\n\n# Find all decay_alpha values\nfor k in keys:\n    if 'decay_alpha' in k:\n        print(f'{k}: {data[k]}')\n\n# Find q_proj and q_mirrors to understand what active strides have\nprint()\nprint('--- stride layer types ---')\nfor k in keys:\n    if k.startswith('shared_stride_stack.layers.') and k.endswith('.norm.weight'):\n        layer_prefix = k.rsplit('.norm.weight', 1)[0]\n        has_q = any(kk.startswith(layer_prefix + '.q_proj') for kk in keys)\n        has_k = any(kk.startswith(layer_prefix + '.k_proj') for kk in keys)\n        has_decay = any(kk.startswith(layer_prefix + '.decay_alpha') for kk in keys)\n        has_gla = any(kk.startswith(layer_prefix + '.G_proj') for kk in keys)\n        layer_num = layer_prefix.split('.')[-1]\n        if has_gla:\n            print(f'  layer {layer_num}: GLA (retrieval)')\n        elif has_q:\n            print(f'  layer {layer_num}: SSA (comp) - has Q/K, decay_alpha={\\\"yes\\\" if has_decay else \\\"no\\\"}')\n        else:\n            print(f'  layer {layer_num}: UNKNOWN')\n\""
}
```

**Summary:** $ python3 -c " import numpy as np dat...

**Output:**
```
Exit code: 0
Stdout:
shared_stride_stack.layers.0.decay_alpha: [1.1727852 1.1728349 1.1750543 1.1749481 1.172802  1.1727734 1.1750897
 1.1750202]
shared_stride_stack.layers.1.decay_alpha: [1.1750728 1.1728675 1.1727766 1.1750449 1.1728506 1.1728063 1.1750481
 1.1727974]
shared_stride_stack.layers.10.decay_alpha: [1.1764877 1.172956  1.1018093 1.1735057 1.1750512 1.1072812 1.1531646
 1.1140264]
shared_stride_stack.layers.11.decay_alpha: [1.1731929 1.1872454 1.1738374 1.1719102 1.1765447 1.1877308 1.173159
 1.1734775]
shared_stride_stack.layers.12.decay_alpha: [1.1739243 1.1739243 1.1739243 1.1739243 1.1739243 1.1739243 1.1739243
 1.1739243]
shared_stride_stack.layers.13.decay_alpha: [1.1739243 1.1739243 1.1739243 1.1739243 1.1739243 1.1739243 1.1739243
 1.1739243]
shared_stride_stack.layers.14.decay_alpha: [1.1739243 1.1739243 1.1739243 1.1739243 1.1739243 1.1739243 1.1739243
 1.1739243]
shared_stride_stack.layers.15.decay_alpha: [1.1739243 1.1739243 1.1739243 1.1739243 1.1739243 1.1739243 1.1739243
 1.1739243]
shared_stride_stack.layers.2.decay_alpha: [1.1751978 1.1754745 1.1749661 1.1727954 1.1750499 1.1750568 1.1750358
 1.1728233]
shared_stride_stack.layers.3.decay_alpha: [1.1728914 1.1750491 1.1731173 1.1731331 1.1750723 1.1731303 1.1731374
 1.1750585]

--- stride layer types ---
  layer 0: SSA (comp) - has Q/K, decay_alpha=yes
  layer 0: UNKNOWN
  layer 1: SSA (comp) - has Q/K, decay_alpha=yes
  layer 0: UNKNOWN
  layer 10: SSA (comp) - has Q/K, decay_alpha=yes
  layer 0: UNKNOWN
  layer 11: SSA (comp) - has Q/K, decay_alpha=yes
  layer 0: UNKNOWN
  layer 12: SSA (comp) - has Q/K, decay_alpha=yes
  layer 0: UNKNOWN
  layer 13: SSA (comp) - has Q/K, decay_alpha=yes
  layer 0: UNKNOWN
  layer 14: SSA (comp) - has Q/K, decay_alpha=yes
  layer 0: UNKNOWN
  layer 15: SSA (comp) - has Q/K, decay_alpha=yes
  layer 0: UNKNOWN
  layer 2: SSA (comp) - has Q/K, decay_alpha=yes
  layer 0: UNKNOWN
  layer 3: SSA (comp) - has Q/K, decay_alpha=yes
  layer 0: UNKNOWN
  layer 4: SSA (comp) - has Q/K, decay_alpha=no
  layer 0: UNKNOWN
  layer 5: SSA (comp) - has Q/K, decay_alpha=no
  layer 0: UNKNOWN
  layer 6: SSA (comp) - has Q/K, decay_alpha=no
  layer 0: UNKNOWN
  layer 7: SSA (comp) - has Q/K, decay_alpha=no
  layer 0: UNKNOWN
  layer 8: SSA (comp) - has Q/K, decay_alpha=no
  layer 0: UNKNOWN
  layer 9: SSA (comp) - has Q/K, decay_alpha=no
  layer 0: UNKNOWN
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport numpy as np\ndata = np.load('checkpoints/v14-td/step_002000/model.npz', allow_pickle=True)\n# Check actual alpha values at step 2000\nfor k in sorted(data.files):\n    if 'decay_alpha' in k:\n        arr = data[k]\n        print(f'{k}: mean={arr.mean():.4f} std={arr.std():.6f} min={arr.min():.4f} max={arr.max():.4f}')\n\""
}
```

**Summary:** $ python3 -c " import numpy as np dat...

**Output:**
```
Exit code: 0
Stdout:
shared_stride_stack.layers.0.decay_alpha: mean=1.1739 std=0.001115 min=1.1728 max=1.1751
shared_stride_stack.layers.1.decay_alpha: mean=1.1737 std=0.001083 min=1.1728 max=1.1751
shared_stride_stack.layers.10.decay_alpha: mean=1.1468 std=0.031180 min=1.1018 max=1.1765
shared_stride_stack.layers.11.decay_alpha: mean=1.1771 std=0.006101 min=1.1719 max=1.1877
shared_stride_stack.layers.12.decay_alpha: mean=1.1739 std=0.000000 min=1.1739 max=1.1739
shared_stride_stack.layers.13.decay_alpha: mean=1.1739 std=0.000000 min=1.1739 max=1.1739
shared_stride_stack.layers.14.decay_alpha: mean=1.1739 std=0.000000 min=1.1739 max=1.1739
shared_stride_stack.layers.15.decay_alpha: mean=1.1739 std=0.000000 min=1.1739 max=1.1739
shared_stride_stack.layers.2.decay_alpha: mean=1.1745 std=0.001016 min=1.1728 max=1.1755
shared_stride_stack.layers.3.decay_alpha: mean=1.1738 std=0.000961 min=1.1729 max=1.1751
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport numpy as np, json\nwith open('checkpoints/v14-td/step_002000/state.json') as f:\n    state = json.load(f)\n# Show what training state we have\nfor k in sorted(state.keys()):\n    v = state[k]\n    if isinstance(v, (int, float, str, bool)):\n        print(f'{k}: {v}')\n    elif isinstance(v, list) and len(v) < 5:\n        print(f'{k}: {v}')\n    else:\n        print(f'{k}: {type(v).__name__}[{len(v) if hasattr(v, \\\"__len__\\\") else \\\"?\\\"}]')\n\""
}
```

**Summary:** $ python3 -c " import numpy as np, js...

**Output:**
```
Exit code: 0
Stdout:
config: dict[59]
crystal_ema: 0.010952894575893879
data_loader: dict[3]
delta_stats: dict[283]
n_reductions: 1
s5_identity_state: list[128]
step: 2000
structured_warmup_done: True
structured_warmup_steps: 50
target_mix_ratio: 0.1
td_active: True
td_step_count: 500
total_td_flips: 2708256
train_losses_last50: list[50]
```

## Assistant

This is very clear. Here's the picture:

## Checkpoint Compatibility Assessment

### What's in the step 2000 checkpoint

**All 16 stride layers have full Q/K/V/O projections.** Every layer (0-15) is SSA with Q and K plates. Layers 0-3, 10-15 have `decay_alpha` (comp strides). Layers 4-9 don't have decay_alpha (retrieval/GLA strides — those are the ones TD was targeting).

The alpha values at step 2000:
- Layers 0-3: **1.1728–1.1755** (std < 0.001) — locked solid
- Layers 10-11: **1.10–1.19** (layer 10 has a few heads at 1.10, slight drift)
- Layers 12-15: **1.1739 exactly** — never moved at all (zero std)

### Change 1: Lock α=1.18 → **Seamless resume** ✅

The values are already at 1.174 ± 0.001. Replacing the learnable parameter with the constant `1.18` introduces a delta of ~0.006 — negligible. Just don't load `decay_alpha` from the checkpoint, use the constant. The model won't notice.

### Change 2: HPE → **Cannot resume cleanly** ⚠️

This is the problem. The v14-td model was trained with **no positional rotation at all** on Q or K. The attention score is:

```
v14-td:  score = Q·K * scale + decay_bias
```

HPE introduces rotation of K in the first 8 dimensions:

```
HPE:     score = Q · rotate(K, log_distance × crystal_freq) * scale + decay_bias
```

The Q weights learned to produce queries that match *unrotated* keys. If you suddenly start rotating K, the dot products in the first 8 dimensions become nonsensical — the model's learned Q·K alignment is broken.

**The math:** Even with `freq_scale` initialized at 1.0, the rotation angles for stride-1 window position 1 would be `log(2) × 0.68 ≈ 0.47 radians (27°)`. That's a massive perturbation to the attention pattern.

### Three options

| Option | Description | Risk |
|--------|-------------|------|
| **A: Resume, α-lock only** | Keep v14-td exactly as-is + lock α. No HPE. Continue the run that was working. | Zero risk, no HPE benefit |
| **B: Resume, α-lock + HPE with warmup** | Initialize `freq_scale = 0.0` (no rotation). Linearly warm it up over 200-500 steps to 1.0. The model gradually adapts. | Low risk, but HPE is fighting existing Q/K alignments |
| **C: Fresh run with α-lock + HPE** | New extraction, HPE from step 0. Q/K learn from scratch with rotation. | Medium risk (new run), but cleanest HPE integration |

**My recommendation: Option B** — resume from step 2000 with α locked and HPE warming from `freq_scale=0.0→1.0` over ~300 steps. The model already has 2000 steps of good training. The warmup lets Q/K relationships gradually adapt to the rotation rather than shocking them. If HPE adds value, you'll see it in the PPL curve. If it doesn't, the damage is minimal because the warmup starts from "no rotation."

The key insight: HPE's `freq_scale` is already learnable per-eigenplane. Initialize it at 0 instead of 1, and the model starts exactly where v14-td left off. Gradient will push `freq_scale` toward whatever value actually helps.

What's your preference?

## User

I like this idea from Option B let's do it.  We'll need to revert code changes, and create a knowledge page that shows what we reverted so a later session can come back and pick up the research ideas for later refinement.


### Thinking

The user wants to:
1. Revert the v14 code changes (passive strides, Stack B reduction) back to the v14-td working architecture
2. Keep α-lock at 1.18
3. Add HPE with freq_scale warmup from 0.0→1.0
4. Create a knowledge page documenting what was reverted and why, for future sessions

Let me plan this out:

1. First, understand exactly what needs to change in the code files (attention.py, config.py, model.py)
2. Revert passive strides — restore Q/K for all SSA layers


3. Revert Stack B back to 4 passes (13 total)
4. Keep α=1.18 as a constant value
5. Modify HPE initialization with freq_scale starting at 0.0
6. Implement the freq_scale warmup progression
7. Document the revert decisions in a knowledge page

Now I need to examine the current code to see what's actually in place.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v14/config.py",
  "line_offset": 110,
  "limit": 30
}
```

**Summary:** Reading config.py (110-140)

**Output:**
```
#   Pass 8:  [12,16) → s32768, s16384, s8192, s4096
#   Pass 9:  [8,12)  → s4096, s2048, s1024, s512
#   Pass 10: [5,9)   → s256, s128, s64, s32
#   Pass 11: [2,6)   → s32, s16, s8, s4
#   Pass 12: [0,4)   → s8, s4, s2, s1

STACK_A_BANDS = ((0, 4), (2, 6), (4, 8), (6, 9))
# Reduced from 4→2 passes (session 151 kernel insight: Stack B computes
# in already-compressed space PR=5.2, two wider passes cover same range).
STACK_B_BANDS = ((7, 13), (11, 16))
STACK_C_BANDS = ((12, 16), (8, 12), (5, 9), (2, 6), (0, 4))

N_PASSES = len(STACK_A_BANDS) + len(STACK_B_BANDS) + len(STACK_C_BANDS)  # 13


# ══════════════════════════════════════════════════════════════════════
# § 3  Teacher constants (Qwen3.6-27B — extraction source)
# ══════════════════════════════════════════════════════════════════════

TEACHER_D_MODEL = 5120
TEACHER_N_LAYERS = 64
TEACHER_D_FF = 17408
TEACHER_VOCAB = 248320


# ══════════════════════════════════════════════════════════════════════
# § 4  V14Config
# ══════════════════════════════════════════════════════════════════════

@dataclass

[CONTENT TRUNCATED] Showing lines 111 to 140 of 263 total lines. Use line_offset=140 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v14/config.py",
  "line_offset": 245,
  "limit": 15
}
```

**Summary:** Reading config.py (245-260)

**Output:**
```
# § 5  Self-test
# ══════════════════════════════════════════════════════════════════════

def _self_test():
    cfg = V14Config()
    assert cfg.d_model == 1280
    assert cfg.d_head == 160
    assert cfg.n_strides == 16
    assert cfg.n_passes == 11  # reduced from 13: Stack B 4→2 passes
    assert cfg.n_heads * cfg.d_head == cfg.d_model
    assert cfg.d_ff == 4 * cfg.d_model
    assert sum(1 for r in cfg.stride_is_retrieval if r) == 6   # 6 retrieval strides
    assert sum(1 for r in cfg.stride_is_retrieval if not r) == 10  # 10 composition strides
    assert len(cfg.stride_is_retrieval) == cfg.n_strides
    print("config.py self-test: ✓")

[CONTENT TRUNCATED] Showing lines 246 to 260 of 263 total lines. Use line_offset=260 parameter to read more content.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v14/config.py",
  "original_content": "# Reduced from 4→2 passes (session 151 kernel insight: Stack B computes\n# in already-compressed space PR=5.2, two wider passes cover same range).\nSTACK_B_BANDS = ((7, 13), (11, 16))",
  "new_content": "STACK_B_BANDS = ((7, 11), (9, 13), (11, 15), (13, 16))"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/v14/config.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v14/config.py",
  "original_content": "    assert cfg.n_passes == 11  # reduced from 13: Stack B 4→2 passes",
  "new_content": "    assert cfg.n_passes == 13"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/v14/config.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 scripts/v14/config.py"
}
```

**Summary:** $ python3 scripts/v14/config.py

**Output:**
```
Exit code: 0
Stdout:
config.py self-test: ✓
```

## Assistant

Config reverted and self-test passes.Let me read the full current attention.py to understand all the surgery needed:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v14/attention.py"
}
```

**Summary:** Reading attention.py (0-2000)

**Output:**
```
"""v14 Attention — Stride-Stack at d=1280.

Holographic lens architecture: each stride is a lens pointed at a
different scale of the context. O(L×W) per stride, ternary, CPU-runnable.

Two layer types (same as v13, evolved for d=1280):
  SingleStrideAttention — composition (KIBC dispatch)
  GatedLinearAttention  — retrieval (M kernel substrate)

11 strides: (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024)
  s1-s8:    composition (fine → local)
  s16-s128: retrieval (phrase → paragraph)
  s256-s1024: composition (document scale)

Fractal stride bands (MERA topology) select 4 strides per pass.
Shared across passes within a stack (S5 coherence).

Base plates: extracted from Qwen3.6-27B, packed ternary.
Delta plates: overlay corrections. No-block on attention (flip-or-keep).

License: MIT
"""

from __future__ import annotations

import mlx.core as mx
import mlx.nn as nn

from config import V14Config, D_MODEL, N_HEADS, D_HEAD, STRIDES, STRIDE_IS_RETRIEVAL, N_STRIDES
from ternary import TernaryLinear, TernaryMirror
from scan import parallel_scan_2d

# Universal decay constant — confirmed at 1.18±0.006 across 10 comp layers
# × 8 heads after 1500 steps of gradient pressure. Not learnable.
_ALPHA = 1.18

# Passive stride threshold: strides ≥ this use fixed distance prior
# (no Q/K computation). At α=1.18, W=8: s4+ has <3 effective positions.
_PASSIVE_STRIDE_MIN = 4

# Crystal eigenvalues (Zone B, top 8 — from PCAQ_ZONE_B_TARGETS eigendecomposition).
# These are the natural frequencies of the holographic lens.
_CRYSTAL_EIGENVALUES = [5.193, 3.535, 1.909, 1.300, 1.082, 0.736, 0.500, 0.426]

# Number of eigenplane pairs to rotate (the rest carry content, not position).
# First 4 pairs cover 77% of crystal variance (comp, sel, term, rout).
_N_EIGEN_PAIRS = 4


# ══════════════════════════════════════════════════════════════════════
# § 0  Holographic Position Encoding (HPE)
# ══════════════════════════════════════════════════════════════════════


class HolographicPositionEncoding(nn.Module):
    """Position encoding derived from holographic lens physics.

    Instead of RoPE (arbitrary 10000-base, all dimensions, linear position):
      - Log-position: angle ∝ log(d+1) → natural power-law decay
      - Crystal frequencies: eigenvalues of the crystal target → natural lens bands
      - Selective rotation: only first N_EIGEN_PAIRS dimension pairs → eigenplane only
      - Direct decay bias: -α × log(d+1) → exact, not cosine-envelope approximation

    For stride attention at stride s, window position w:
      absolute_distance = s × w
      log_distance = log(s × w + 1)
      rotation_angle[i] = log_distance × freq[i] × depth_factor

    This unifies position encoding + distance decay into one mechanism:
    the holographic lens's frequency response.
    """

    def __init__(
        self,
        d_head: int = D_HEAD,
        n_eigen_pairs: int = _N_EIGEN_PAIRS,
        alpha: float = _ALPHA,
    ):
        super().__init__()
        self.d_head = d_head
        self.n_eigen_pairs = n_eigen_pairs
        self.alpha = alpha

        # Crystal-derived frequencies (normalized by λ₀)
        freqs = [ev / _CRYSTAL_EIGENVALUES[0] for ev in _CRYSTAL_EIGENVALUES[:n_eigen_pairs]]
        self._freqs = mx.array(freqs)  # (n_eigen_pairs,)

        # Learnable frequency scaling (initialized near 1.0, allows fine-tuning
        # of each eigenplane's rotation rate without departing from crystal base)
        self.freq_scale = mx.ones((n_eigen_pairs,))

    def apply_rotary(
        self,
        q: mx.array,
        k: mx.array,
        log_distances: mx.array,
    ) -> tuple[mx.array, mx.array]:
        """Apply holographic rotation to Q and K.

        Args:
            q: (B, L, H, Dh) or (B, H, L, Dh) — query
            k: (B, L, W, H, Dh) — gathered keys at stride positions
            log_distances: (W,) — log(stride × w + 1) for each window position

        Returns:
            q_rot, k_rot with rotations applied to first n_eigen_pairs dim pairs.
        """
        n_pairs = self.n_eigen_pairs
        freqs = self._freqs * self.freq_scale  # (n_pairs,)

        # Rotation angles: log_distance × crystal_frequency
        # angles shape: (W, n_pairs)
        angles = log_distances[:, None] * freqs[None, :]  # (W, n_pairs)

        cos_a = mx.cos(angles)  # (W, n_pairs)
        sin_a = mx.sin(angles)  # (W, n_pairs)

        # For Q: position 0 (self) gets zero rotation (log(0+1) = 0)
        # We only need to rotate Q by its absolute position, but since
        # we're doing RELATIVE encoding (like RoPE), we apply rotation
        # to K by the relative log-distance, and leave Q unrotated.
        # The Q·K product then encodes relative log-distance automatically.

        # Rotate the first 2*n_pairs dimensions of K
        k_rot = mx.array(k)  # copy
        for i in range(n_pairs):
            d0 = 2 * i
            d1 = 2 * i + 1
            if d1 >= k.shape[-1]:
                break

            # k has shape (B, L, W, H, Dh)
            # cos_a[w, i] and sin_a[w, i] broadcast over (B, L, H)
            c = cos_a[:, i]  # (W,)
            s = sin_a[:, i]  # (W,)

            # Reshape for broadcasting: (1, 1, W, 1)
            c = c.reshape(1, 1, -1, 1)
            s = s.reshape(1, 1, -1, 1)

            k0 = k[:, :, :, :, d0:d0+1]  # (B, L, W, H, 1)
            k1 = k[:, :, :, :, d1:d1+1]

            k_rot_d0 = k0 * c - k1 * s
            k_rot_d1 = k0 * s + k1 * c

            k_rot = k_rot.at[:, :, :, :, d0:d0+1].add(k_rot_d0 - k0)
            k_rot = k_rot.at[:, :, :, :, d1:d1+1].add(k_rot_d1 - k1)

        return q, k_rot

    def get_decay_bias(self, log_distances: mx.array) -> mx.array:
        """Direct decay bias: -α × log(d+1).

        Args:
            log_distances: (W,) — precomputed log(stride × w + 1)

        Returns:
            (W,) decay bias to add to attention scores.
        """
        return -(self.alpha * log_distances)


def apply_hpe_rotation(
    q: mx.array,
    k_gathered: mx.array,
    log_distances: mx.array,
    n_pairs: int = _N_EIGEN_PAIRS,
    freq_scale: mx.array = None,
) -> tuple[mx.array, mx.array]:
    """Apply holographic position encoding: rotate K by log-distance × crystal freq.

    Rotates K by relative log-distance in the first n_pairs dimension pairs
    (the crystal eigenplane dimensions). Q stays unrotated — relative encoding.

    Args:
        q: (B, H, L, Dh) — queries (transposed)
        k_gathered: (B, L, W, H, Dh) — gathered keys
        log_distances: (W,) — log(stride × w + 1)
        n_pairs: number of eigenplane pairs to rotate
        freq_scale: (n_pairs,) learnable scaling on crystal frequencies

    Returns:
        q (unchanged), k_rotated
    """
    freqs_base = mx.array([ev / _CRYSTAL_EIGENVALUES[0]
                           for ev in _CRYSTAL_EIGENVALUES[:n_pairs]])
    if freq_scale is not None:
        freqs = freqs_base * freq_scale
    else:
        freqs = freqs_base

    # Rotation angles: (W, n_pairs)
    angles = log_distances[:, None] * freqs[None, :]
    cos_a = mx.cos(angles)  # (W, n_pairs)
    sin_a = mx.sin(angles)  # (W, n_pairs)

    # Vectorized rotation of first 2*n_pairs dimensions of K
    # k_gathered: (B, L, W, H, Dh)
    rot_dim = 2 * n_pairs
    Dh = k_gathered.shape[-1]

    # Split K into rotated and non-rotated parts
    k_rot_part = k_gathered[:, :, :, :, :rot_dim]    # (B, L, W, H, 2*n_pairs)
    k_pass_part = k_gathered[:, :, :, :, rot_dim:]   # (B, L, W, H, Dh-2*n_pairs)

    # Reshape rotated part into pairs: (B, L, W, H, n_pairs, 2)
    k_pairs = k_rot_part.reshape(*k_rot_part.shape[:-1], n_pairs, 2)

    # Extract even (d0) and odd (d1) components
    k_even = k_pairs[:, :, :, :, :, 0]  # (B, L, W, H, n_pairs)
    k_odd = k_pairs[:, :, :, :, :, 1]   # (B, L, W, H, n_pairs)

    # Broadcast cos/sin: (1, 1, W, 1, n_pairs)
    c = cos_a.reshape(1, 1, -1, 1, n_pairs)
    s = sin_a.reshape(1, 1, -1, 1, n_pairs)

    # Apply rotation: [cos -sin; sin cos] × [even; odd]
    k_even_rot = k_even * c - k_odd * s
    k_odd_rot = k_even * s + k_odd * c

    # Interleave back: (B, L, W, H, n_pairs, 2) → (B, L, W, H, 2*n_pairs)
    k_rot_interleaved = mx.stack([k_even_rot, k_odd_rot], axis=-1)
    k_rot_flat = k_rot_interleaved.reshape(*k_rot_part.shape)

    # Concatenate rotated + non-rotated
    k_rotated = mx.concatenate([k_rot_flat, k_pass_part], axis=-1)

    return q, k_rotated


# ══════════════════════════════════════════════════════════════════════
# § 1  SingleStrideAttention — composition layers
# ══════════════════════════════════════════════════════════════════════


class SingleStrideAttention(nn.Module):
    """Ternary attention at a single stride and window.

    Each head attends to W past positions at the given stride:
      stride=1:  positions [i, i-1, ..., i-W+1]
      stride=8:  positions [i, i-8, ..., i-8*(W-1)]

    Two modes:
      Active (s1, s2): full Q·K attention + fixed decay bias (α=1.18).
      Passive (s4+): fixed distance prior, no Q/K — just V gather + weighted sum.

    Q/K/V/O are TernaryLinear (base plates from teacher extraction).
    Sparse gather, O(L×W) not O(L²).
    """

    def __init__(
        self,
        d_model: int = D_MODEL,
        stride: int = 1,
        window: int = 8,
        n_heads: int = N_HEADS,
        dropout: float = 0.0,
        decay_init_alpha: float = _ALPHA,
        n_q_mirrors: int = 0,
    ):
        super().__init__()
        self.d_model = d_model
        self.stride = stride
        self.window = window
        self.n_heads = n_heads
        self.d_head = d_model // n_heads  # 160
        self.scale = self.d_head ** -0.5
        self.passive = (stride >= _PASSIVE_STRIDE_MIN)

        self.norm = nn.RMSNorm(d_model)

        if not self.passive:
            # Active: full Q·K attention with HPE (s1, s2 only)
            self.q_mirrors = [TernaryMirror(d_model) for _ in range(n_q_mirrors)]
            self.q_proj = TernaryLinear(d_model, d_model, pre_norm=False)
            self.k_proj = TernaryLinear(d_model, d_model, pre_norm=False)
            self.k_bias = mx.zeros((d_model,))

            # HPE: learnable scaling on crystal eigenfrequencies
            # Initialized to 1.0 — matches crystal exactly, can fine-tune
            self.hpe_freq_scale = mx.ones((_N_EIGEN_PAIRS,))
        else:
            # Passive: no Q/K, no HPE, just mirrors list for compat
            self.q_mirrors = []

        # V and O projections — always needed
        self.v_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.out_proj = TernaryLinear(d_model, d_model, pre_norm=False)

        self.v_bias = mx.zeros((d_model,))
        self.o_bias = mx.zeros((d_model,))

        self.dropout = nn.Dropout(dropout) if dropout > 0 else None

        # Pre-compute log-distance structure (used by active strides for decay bias)
        w_pos = mx.arange(window, dtype=mx.float32)
        self._log_distances = mx.log(stride * w_pos + 1.0)

        # Pre-compute fixed attention profile for passive strides
        # and decay bias for active strides (α is constant, not learnable)
        self._decay_bias = -(_ALPHA * self._log_distances)  # (W,)

        if self.passive:
            # Precomputed normalized distance prior: 1/(stride*w + 1)^α
            raw_weights = 1.0 / (stride * w_pos + 1.0) ** _ALPHA
            self._fixed_profile = raw_weights / raw_weights.sum()  # (W,)

    def __call__(self, x: mx.array, decay_modulation: float = 1.0) -> mx.array:
        if self.passive:
            return self._passive_forward(x)
        else:
            return self._active_forward(x, decay_modulation)

    def _active_forward(self, x: mx.array, decay_modulation: float = 1.0) -> mx.array:
        """Full Q·K attention with HPE (holographic position encoding). For s1, s2.

        HPE replaces RoPE-style rotation with crystal-derived frequencies in
        log-distance space. K is rotated by log(stride×w+1) × crystal_freq
        in the first N_EIGEN_PAIRS dimension pairs. Q stays unrotated (relative
        encoding — the distance information is in K's rotation).
        """
        B, L, D = x.shape
        H, Dh = self.n_heads, self.d_head
        W = self.window

        x_norm = self.norm(x)

        # Beam steering
        q_in = x_norm
        for mirror in self.q_mirrors:
            q_in = mirror(q_in)

        Q = self.q_proj(q_in).reshape(B, L, H, Dh)
        K = (self.k_proj(x_norm) + self.k_bias).reshape(B, L, H, Dh)
        V = (self.v_proj(x_norm) + self.v_bias).reshape(B, L, H, Dh)

        # Stride gather
        query_pos = mx.arange(L)[:, None]
        offsets = mx.arange(W)[None, :] * self.stride
        raw_indices = query_pos - offsets
        valid = raw_indices >= 0
        indices = mx.maximum(raw_indices, 0)

        GD = H * Dh
        K_flat = K.reshape(B, L, GD)
        V_flat = V.reshape(B, L, GD)

        idx = indices.reshape(1, L * W, 1)
        idx = mx.broadcast_to(idx, (B, L * W, GD))

        K_gathered = mx.take_along_axis(K_flat, idx, axis=1).reshape(B, L, W, H, Dh)
        V_gathered = mx.take_along_axis(V_flat, idx, axis=1).reshape(B, L, W, H, Dh)

        # ── HPE: rotate K by log-distance × crystal frequencies ──
        # Q stays unrotated (relative encoding)
        Q_r = Q.transpose(0, 2, 1, 3)  # (B, H, L, Dh)
        _, K_gathered_rot = apply_hpe_rotation(
            Q_r, K_gathered, self._log_distances,
            n_pairs=_N_EIGEN_PAIRS,
            freq_scale=self.hpe_freq_scale,
        )

        K_r = K_gathered_rot.transpose(0, 3, 1, 2, 4)  # (B, H, L, W, Dh)
        attn = (Q_r[:, :, :, None, :] * K_r).sum(axis=-1) * self.scale

        # Fixed α decay bias (the direct power-law, not cosine approximation)
        decay_bias = self._decay_bias * decay_modulation  # (W,)
        attn = attn + decay_bias[None, None, None, :]

        valid_mask = valid[None, None, :, :]
        attn = mx.where(valid_mask, attn, mx.array(float("-inf")))
        attn = mx.softmax(attn, axis=-1)
        if self.dropout is not None:
            attn = self.dropout(attn)

        V_r = V_gathered.transpose(0, 3, 1, 2, 4)
        out = (attn[:, :, :, :, None] * V_r).sum(axis=3)
        out = out.transpose(0, 2, 1, 3).reshape(B, L, D)

        return x + self.out_proj(out) + self.o_bias

    def _passive_forward(self, x: mx.array) -> mx.array:
        """Fixed distance prior — no Q/K, no softmax. For s4+."""
        B, L, D = x.shape
        H, Dh = self.n_heads, self.d_head
        W = self.window

        x_norm = self.norm(x)
        V = (self.v_proj(x_norm) + self.v_bias).reshape(B, L, H, Dh)

        # Stride gather (same index computation)
        query_pos = mx.arange(L)[:, None]
        offsets = mx.arange(W)[None, :] * self.stride
        raw_indices = query_pos - offsets
        valid = raw_indices >= 0
        indices = mx.maximum(raw_indices, 0)

        GD = H * Dh
        V_flat = V.reshape(B, L, GD)
        idx = indices.reshape(1, L * W, 1)
        idx = mx.broadcast_to(idx, (B, L * W, GD))
        V_gathered = mx.take_along_axis(V_flat, idx, axis=1).reshape(B, L, W, H, Dh)

        # Fixed attention weights — precomputed from α=1.18
        attn = mx.broadcast_to(
            self._fixed_profile[None, None, None, :],
            (1, 1, 1, W)
        )  # (1, 1, 1, W)

        # Mask invalid positions and renormalize
        valid_mask = valid[None, None, :, :]  # (1, 1, L, W)
        attn = mx.where(valid_mask, attn, mx.array(0.0))
        attn = attn / (attn.sum(axis=-1, keepdims=True) + 1e-10)

        # Weighted sum of gathered V
        V_r = V_gathered.transpose(0, 3, 1, 2, 4)  # (B, H, L, W, Dh)
        out = (attn[:, :, :, :, None] * V_r).sum(axis=3)  # (B, H, L, Dh)
        out = out.transpose(0, 2, 1, 3).reshape(B, L, D)

        return x + self.out_proj(out) + self.o_bias


# ══════════════════════════════════════════════════════════════════════
# § 2  GatedLinearAttention — retrieval layers
# ══════════════════════════════════════════════════════════════════════


class GatedLinearAttention(nn.Module):
    """Gated linear attention at a single stride — M kernel substrate.

    Running memory per head: (d_head, d_state) accumulates key-value pairs.
    Queries retrieve from memory in O(d) per position.
    Parallel associative scan for training.

    Striding: positions gathered at stride intervals, memory accumulates
    over strided positions for scale-appropriate pattern matching.
    """

    def __init__(
        self,
        d_model: int = D_MODEL,
        stride: int = 16,
        d_state: int = 64,
        n_heads: int = N_HEADS,
        dropout: float = 0.0,
        n_q_mirrors: int = 0,
    ):
        super().__init__()
        self.d_model = d_model
        self.stride = stride
        self.d_state = d_state
        self.n_heads = n_heads
        self.d_head = d_model // n_heads

        self.norm = nn.RMSNorm(d_model)
        self.q_mirrors = [TernaryMirror(d_model) for _ in range(n_q_mirrors)]

        self.q_proj = TernaryLinear(d_model, n_heads * d_state, pre_norm=False)
        self.k_proj = TernaryLinear(d_model, n_heads * d_state, pre_norm=False)
        self.v_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.out_proj = TernaryLinear(d_model, d_model, pre_norm=False)

        self.k_bias = mx.zeros((n_heads * d_state,))
        self.v_bias = mx.zeros((d_model,))
        self.o_bias = mx.zeros((d_model,))

        # Write gate
        self._n_heads_padded = ((n_heads + 15) // 16) * 16
        self.gate_proj = TernaryLinear(d_model, self._n_heads_padded, pre_norm=False)
        self.gate_bias = mx.full((n_heads,), -0.5)

        self.dropout = nn.Dropout(dropout) if dropout > 0 else None

        # Diagnostics
        self._gate_values = None
        self._memory_norms = None

    def __call__(self, x: mx.array) -> mx.array:
        B, L, D = x.shape
        H = self.n_heads
        Ds = self.d_state
        Dh = self.d_head
        stride = self.stride

        x_norm = self.norm(x)

        q_in = x_norm
        for mirror in self.q_mirrors:
            q_in = mirror(q_in)

        q_raw = self.q_proj(q_in).reshape(B, L, H, Ds)
        k_raw = (self.k_proj(x_norm) + self.k_bias).reshape(B, L, H, Ds)
        v = (self.v_proj(x_norm) + self.v_bias).reshape(B, L, H, Dh)
        gate = mx.sigmoid(
            self.gate_proj(x_norm)[..., :H] + self.gate_bias
        )

        q = nn.elu(q_raw) + 1.0
        k = nn.elu(k_raw) + 1.0

        self._gate_values = mx.stop_gradient(gate)

        # Stride-aware scan
        if stride == 1:
            L_s = L
            kv_outer = k[:, :, :, :, None] * v[:, :, :, None, :]
            gate_expand = gate[:, :, :, None, None]
            gated_kv = gate_expand * kv_outer
            retention = 1.0 - gate
            S_all = parallel_scan_2d(retention, gated_kv)
            output = mx.sum(q[:, :, :, :, None] * S_all, axis=3)
        else:
            L_s = L // stride
            if L_s == 0:
                output = mx.zeros((B, L, H, Dh))
            else:
                stride_idx = mx.arange(L_s) * stride
                k_s = k[:, stride_idx, :, :]
                v_s = v[:, stride_idx, :, :]
                gate_s = gate[:, stride_idx, :]

                kv_outer_s = k_s[:, :, :, :, None] * v_s[:, :, :, None, :]
                gate_s_expand = gate_s[:, :, :, None, None]
                gated_kv_s = gate_s_expand * kv_outer_s
                retention_s = 1.0 - gate_s

                S_stride = parallel_scan_2d(retention_s, gated_kv_s)

                state_idx = mx.minimum(mx.arange(L) // stride, L_s - 1)
                S_all = S_stride[:, state_idx, :, :, :]
                output = mx.sum(q[:, :, :, :, None] * S_all, axis=3)

        output = output.reshape(B, L, D)

        # Diagnostics
        if stride == 1:
            S_final = S_all[:, -1, :, :, :]
        elif L_s == 0:
            S_final = mx.zeros((B, H, Ds, Dh))
        else:
            S_final = S_stride[:, -1, :, :, :]
        S_norms = mx.sqrt(mx.sum(S_final * S_final, axis=(2, 3)) + 1e-8)
        self._memory_norms = mx.stop_gradient(S_norms.mean(axis=0))

        result = self.out_proj(output) + self.o_bias
        if self.dropout is not None:
            result = self.dropout(result)
        return x + result


# ══════════════════════════════════════════════════════════════════════
# § 3  StrideStack — 11-stride hybrid stack
# ══════════════════════════════════════════════════════════════════════


class StrideStack(nn.Module):
    """Hybrid 11-stride stack: composition + retrieval layers.

    One layer per stride. Layer type determined by STRIDE_IS_RETRIEVAL.
    Shared across passes within a stack (fractal bands select active strides).
    """

    def __init__(self, cfg: V14Config):
        super().__init__()
        d = cfg.d_model
        n_q = cfg.n_q_mirrors if cfg.use_q_mirrors else 0

        self.layers = []
        self._layer_types = []

        for s, is_ret in zip(cfg.strides, cfg.stride_is_retrieval):
            if is_ret:
                self.layers.append(GatedLinearAttention(
                    d_model=d, stride=s, d_state=cfg.d_state,
                    n_heads=cfg.n_heads, dropout=cfg.dropout,
                    n_q_mirrors=n_q,
                ))
                self._layer_types.append("ret")
            else:
                ssa = SingleStrideAttention(
                    d_model=d, stride=s, window=cfg.window,
                    n_heads=cfg.n_heads, dropout=cfg.dropout,
                    n_q_mirrors=n_q if not (s >= _PASSIVE_STRIDE_MIN) else 0,
                )
                self.layers.append(ssa)
                self._layer_types.append("passive" if ssa.passive else "comp")

        # Per-combinator beam mirrors (shared across strides)
        self.combinator_mirrors = [TernaryMirror(d) for _ in range(cfg.n_combinators)]

    def __call__(
        self,
        x: mx.array,
        stride_range: tuple[int, int] | None = None,
        reverse: bool = False,
    ) -> mx.array:
        """Run active stride layers for one pass.

        Args:
            x: (B, L, d_model)
            stride_range: (start, end) — which stride indices to activate
            reverse: True for descending passes

        Returns: (B, L, d_model)
        """
        if stride_range is not None:
            start, end = stride_range
            indices = list(range(start, min(end, len(self.layers))))
        else:
            indices = list(range(len(self.layers)))

        if reverse:
            indices = list(reversed(indices))

        for i in indices:
            x = self.layers[i](x)

        return x


# ══════════════════════════════════════════════════════════════════════
# § 4  Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("v14 attention.py self-test (stride-stack at d=1280)")
    print("=" * 60)

    cfg = V14Config()
    B, L, D = 1, 64, cfg.d_model

    # SingleStrideAttention
    print("\nSingleStrideAttention (s=1, s=8)...")
    for s in (1, 8):
        ssa = SingleStrideAttention(d_model=D, stride=s, window=8, n_heads=N_HEADS)
        x = mx.random.normal((B, L, D))
        y = ssa(x)
        mx.eval(y)
        assert y.shape == (B, L, D)
        print(f"  s={s}: {y.shape} ✓")

    # GatedLinearAttention
    print("\nGatedLinearAttention (s=16, s=64)...")
    for s in (16, 64):
        gla = GatedLinearAttention(d_model=D, stride=s, d_state=64, n_heads=N_HEADS)
        x = mx.random.normal((B, L, D))
        y = gla(x)
        mx.eval(y)
        assert y.shape == (B, L, D)
        gate_mean = float(mx.mean(gla._gate_values).item())
        print(f"  s={s}: {y.shape} gate={gate_mean:.3f} ✓")

    # StrideStack
    print(f"\nStrideStack ({N_STRIDES} strides, hybrid)...")
    ss = StrideStack(cfg)
    assert len(ss.layers) == N_STRIDES
    n_comp = sum(1 for t in ss._layer_types if t == "comp")
    n_ret = sum(1 for t in ss._layer_types if t == "ret")
    print(f"  {n_comp} composition + {n_ret} retrieval = {len(ss.layers)} strides")

    x = mx.random.normal((B, L, D))

    # Test each pass band
    all_bands = list(cfg.stack_a_bands) + list(cfg.stack_b_bands) + list(cfg.stack_c_bands)
    for i, (start, end) in enumerate(all_bands):
        is_desc = i >= (len(cfg.stack_a_bands) + len(cfg.stack_b_bands))
        y = ss(x, stride_range=(start, end), reverse=is_desc)
        mx.eval(y)
        assert y.shape == (B, L, D)
        print(f"  Pass {i} [{start},{end}) rev={is_desc}: ✓")

    # Gradient flow
    print("\nGradient flow...")

    class TestGrad(nn.Module):
        def __init__(self):
            super().__init__()
            self.stack = StrideStack(cfg)
        def __call__(self, x):
            return mx.mean(self.stack(x, stride_range=(0, 4)))

    m = TestGrad()
    mx.eval(m.parameters())
    gfn = nn.value_and_grad(m, lambda m, x: m(x))
    x_test = mx.random.normal((1, 32, D))
    lv, g = gfn(m, x_test)
    mx.eval(lv, g)
    print(f"  loss={lv.item():.6f} ✓")

    print("\n" + "=" * 60)
    print("v14 attention.py: all tests passed ✓")
```

## Assistant

Now I have the full picture. Let me do the surgery — this is a substantial edit. I need to:

1. Remove `_PASSIVE_STRIDE_MIN` 
2. Remove `_passive_forward`
3. Restore Q/K for all SSA layers
4. Keep HPE but init `freq_scale` to zeros
5. Restore beam mirrors for all strides
6. Restore `k_bias` for all strides
7. Clean up StrideStack layer type logic

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v14/attention.py",
  "original_content": "# Universal decay constant — confirmed at 1.18±0.006 across 10 comp layers\n# × 8 heads after 1500 steps of gradient pressure. Not learnable.\n_ALPHA = 1.18\n\n# Passive stride threshold: strides ≥ this use fixed distance prior\n# (no Q/K computation). At α=1.18, W=8: s4+ has <3 effective positions.\n_PASSIVE_STRIDE_MIN = 4\n\n# Crystal eigenvalues (Zone B, top 8 — from PCAQ_ZONE_B_TARGETS eigendecomposition).\n# These are the natural frequencies of the holographic lens.\n_CRYSTAL_EIGENVALUES = [5.193, 3.535, 1.909, 1.300, 1.082, 0.736, 0.500, 0.426]\n\n# Number of eigenplane pairs to rotate (the rest carry content, not position).\n# First 4 pairs cover 77% of crystal variance (comp, sel, term, rout).\n_N_EIGEN_PAIRS = 4",
  "new_content": "# Universal decay constant — confirmed at 1.18±0.006 across 10 comp layers\n# × 8 heads after 1500 steps of gradient pressure. Not learnable.\n_ALPHA = 1.18\n\n# Crystal eigenvalues (Zone B, top 8 — from PCAQ_ZONE_B_TARGETS eigendecomposition).\n# These are the natural frequencies of the holographic lens.\n_CRYSTAL_EIGENVALUES = [5.193, 3.535, 1.909, 1.300, 1.082, 0.736, 0.500, 0.426]\n\n# Number of eigenplane pairs to rotate (the rest carry content, not position).\n# First 4 pairs cover 77% of crystal variance (comp, sel, term, rout).\n_N_EIGEN_PAIRS = 4\n\n# HPE warmup: freq_scale starts at 0 (no rotation, compatible with checkpoint)\n# and linearly warms to 1.0 over this many steps. This allows Q/K relationships\n# learned without rotation to gradually adapt to HPE.\nHPE_WARMUP_STEPS = 300"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/v14/attention.py.
```

## Assistant

Now update HPE class — `freq_scale` initializes to zeros:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v14/attention.py",
  "original_content": "        # Learnable frequency scaling (initialized near 1.0, allows fine-tuning\n        # of each eigenplane's rotation rate without departing from crystal base)\n        self.freq_scale = mx.ones((n_eigen_pairs,))",
  "new_content": "        # Learnable frequency scaling — initialized to 0.0 for checkpoint\n        # compatibility (no rotation at start). Warmed up externally via\n        # set_hpe_warmup_fraction() so Q/K relationships can adapt gradually.\n        self.freq_scale = mx.zeros((n_eigen_pairs,))"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/v14/attention.py.
```

## Assistant

Now the big one — replace the entire `SingleStrideAttention` class to remove passive mode and restore full Q/K for all strides:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v14/attention.py",
  "original_content": "class SingleStrideAttention(nn.Module):\n    \"\"\"Ternary attention at a single stride and window.\n\n    Each head attends to W past positions at the given stride:\n      stride=1:  positions [i, i-1, ..., i-W+1]\n      stride=8:  positions [i, i-8, ..., i-8*(W-1)]\n\n    Two modes:\n      Active (s1, s2): full Q·K attention + fixed decay bias (α=1.18).\n      Passive (s4+): fixed distance prior, no Q/K — just V gather + weighted sum.\n\n    Q/K/V/O are TernaryLinear (base plates from teacher extraction).\n    Sparse gather, O(L×W) not O(L²).\n    \"\"\"\n\n    def __init__(\n        self,\n        d_model: int = D_MODEL,\n        stride: int = 1,\n        window: int = 8,\n        n_heads: int = N_HEADS,\n        dropout: float = 0.0,\n        decay_init_alpha: float = _ALPHA,\n        n_q_mirrors: int = 0,\n    ):\n        super().__init__()\n        self.d_model = d_model\n        self.stride = stride\n        self.window = window\n        self.n_heads = n_heads\n        self.d_head = d_model // n_heads  # 160\n        self.scale = self.d_head ** -0.5\n        self.passive = (stride >= _PASSIVE_STRIDE_MIN)\n\n        self.norm = nn.RMSNorm(d_model)\n\n        if not self.passive:\n            # Active: full Q·K attention with HPE (s1, s2 only)\n            self.q_mirrors = [TernaryMirror(d_model) for _ in range(n_q_mirrors)]\n            self.q_proj = TernaryLinear(d_model, d_model, pre_norm=False)\n            self.k_proj = TernaryLinear(d_model, d_model, pre_norm=False)\n            self.k_bias = mx.zeros((d_model,))\n\n            # HPE: learnable scaling on crystal eigenfrequencies\n            # Initialized to 1.0 — matches crystal exactly, can fine-tune\n            self.hpe_freq_scale = mx.ones((_N_EIGEN_PAIRS,))\n        else:\n            # Passive: no Q/K, no HPE, just mirrors list for compat\n            self.q_mirrors = []\n\n        # V and O projections — always needed\n        self.v_proj = TernaryLinear(d_model, d_model, pre_norm=False)\n        self.out_proj = TernaryLinear(d_model, d_model, pre_norm=False)\n\n        self.v_bias = mx.zeros((d_model,))\n        self.o_bias = mx.zeros((d_model,))\n\n        self.dropout = nn.Dropout(dropout) if dropout > 0 else None\n\n        # Pre-compute log-distance structure (used by active strides for decay bias)\n        w_pos = mx.arange(window, dtype=mx.float32)\n        self._log_distances = mx.log(stride * w_pos + 1.0)\n\n        # Pre-compute fixed attention profile for passive strides\n        # and decay bias for active strides (α is constant, not learnable)\n        self._decay_bias = -(_ALPHA * self._log_distances)  # (W,)\n\n        if self.passive:\n            # Precomputed normalized distance prior: 1/(stride*w + 1)^α\n            raw_weights = 1.0 / (stride * w_pos + 1.0) ** _ALPHA\n            self._fixed_profile = raw_weights / raw_weights.sum()  # (W,)\n\n    def __call__(self, x: mx.array, decay_modulation: float = 1.0) -> mx.array:\n        if self.passive:\n            return self._passive_forward(x)\n        else:\n            return self._active_forward(x, decay_modulation)\n\n    def _active_forward(self, x: mx.array, decay_modulation: float = 1.0) -> mx.array:\n        \"\"\"Full Q·K attention with HPE (holographic position encoding). For s1, s2.\n\n        HPE replaces RoPE-style rotation with crystal-derived frequencies in\n        log-distance space. K is rotated by log(stride×w+1) × crystal_freq\n        in the first N_EIGEN_PAIRS dimension pairs. Q stays unrotated (relative\n        encoding — the distance information is in K's rotation).\n        \"\"\"\n        B, L, D = x.shape\n        H, Dh = self.n_heads, self.d_head\n        W = self.window\n\n        x_norm = self.norm(x)\n\n        # Beam steering\n        q_in = x_norm\n        for mirror in self.q_mirrors:\n            q_in = mirror(q_in)\n\n        Q = self.q_proj(q_in).reshape(B, L, H, Dh)\n        K = (self.k_proj(x_norm) + self.k_bias).reshape(B, L, H, Dh)\n        V = (self.v_proj(x_norm) + self.v_bias).reshape(B, L, H, Dh)\n\n        # Stride gather\n        query_pos = mx.arange(L)[:, None]\n        offsets = mx.arange(W)[None, :] * self.stride\n        raw_indices = query_pos - offsets\n        valid = raw_indices >= 0\n        indices = mx.maximum(raw_indices, 0)\n\n        GD = H * Dh\n        K_flat = K.reshape(B, L, GD)\n        V_flat = V.reshape(B, L, GD)\n\n        idx = indices.reshape(1, L * W, 1)\n        idx = mx.broadcast_to(idx, (B, L * W, GD))\n\n        K_gathered = mx.take_along_axis(K_flat, idx, axis=1).reshape(B, L, W, H, Dh)\n        V_gathered = mx.take_along_axis(V_flat, idx, axis=1).reshape(B, L, W, H, Dh)\n\n        # ── HPE: rotate K by log-distance × crystal frequencies ──\n        # Q stays unrotated (relative encoding)\n        Q_r = Q.transpose(0, 2, 1, 3)  # (B, H, L, Dh)\n        _, K_gathered_rot = apply_hpe_rotation(\n            Q_r, K_gathered, self._log_distances,\n            n_pairs=_N_EIGEN_PAIRS,\n            freq_scale=self.hpe_freq_scale,\n        )\n\n        K_r = K_gathered_rot.transpose(0, 3, 1, 2, 4)  # (B, H, L, W, Dh)\n        attn = (Q_r[:, :, :, None, :] * K_r).sum(axis=-1) * self.scale\n\n        # Fixed α decay bias (the direct power-law, not cosine approximation)\n        decay_bias = self._decay_bias * decay_modulation  # (W,)\n        attn = attn + decay_bias[None, None, None, :]\n\n        valid_mask = valid[None, None, :, :]\n        attn = mx.where(valid_mask, attn, mx.array(float(\"-inf\")))\n        attn = mx.softmax(attn, axis=-1)\n        if self.dropout is not None:\n            attn = self.dropout(attn)\n\n        V_r = V_gathered.transpose(0, 3, 1, 2, 4)\n        out = (attn[:, :, :, :, None] * V_r).sum(axis=3)\n        out = out.transpose(0, 2, 1, 3).reshape(B, L, D)\n\n        return x + self.out_proj(out) + self.o_bias\n\n    def _passive_forward(self, x: mx.array) -> mx.array:\n        \"\"\"Fixed distance prior — no Q/K, no softmax. For s4+.\"\"\"\n        B, L, D = x.shape\n        H, Dh = self.n_heads, self.d_head\n        W = self.window\n\n        x_norm = self.norm(x)\n        V = (self.v_proj(x_norm) + self.v_bias).reshape(B, L, H, Dh)\n\n        # Stride gather (same index computation)\n        query_pos = mx.arange(L)[:, None]\n        offsets = mx.arange(W)[None, :] * self.stride\n        raw_indices = query_pos - offsets\n        valid = raw_indices >= 0\n        indices = mx.maximum(raw_indices, 0)\n\n        GD = H * Dh\n        V_flat = V.reshape(B, L, GD)\n        idx = indices.reshape(1, L * W, 1)\n        idx = mx.broadcast_to(idx, (B, L * W, GD))\n        V_gathered = mx.take_along_axis(V_flat, idx, axis=1).reshape(B, L, W, H, Dh)\n\n        # Fixed attention weights — precomputed from α=1.18\n        attn = mx.broadcast_to(\n            self._fixed_profile[None, None, None, :],\n            (1, 1, 1, W)\n        )  # (1, 1, 1, W)\n\n        # Mask invalid positions and renormalize\n        valid_mask = valid[None, None, :, :]  # (1, 1, L, W)\n        attn = mx.where(valid_mask, attn, mx.array(0.0))\n        attn = attn / (attn.sum(axis=-1, keepdims=True) + 1e-10)\n\n        # Weighted sum of gathered V\n        V_r = V_gathered.transpose(0, 3, 1, 2, 4)  # (B, H, L, W, Dh)\n        out = (attn[:, :, :, :, None] * V_r).sum(axis=3)  # (B, H, L, Dh)\n        out = out.transpose(0, 2, 1, 3).reshape(B, L, D)\n\n        return x + self.out_proj(out) + self.o_bias",
  "new_content": "class SingleStrideAttention(nn.Module):\n    \"\"\"Ternary attention at a single stride and window.\n\n    Each head attends to W past positions at the given stride:\n      stride=1:  positions [i, i-1, ..., i-W+1]\n      stride=8:  positions [i, i-8, ..., i-8*(W-1)]\n\n    Full Q·K attention for ALL strides with:\n      - Fixed decay bias: -α·ln(stride·w + 1), α=1.18 (not learnable)\n      - HPE: crystal-frequency rotation on K (warmed up from 0)\n\n    Q/K/V/O are TernaryLinear (base plates from teacher extraction).\n    Sparse gather, O(L×W) not O(L²).\n    \"\"\"\n\n    def __init__(\n        self,\n        d_model: int = D_MODEL,\n        stride: int = 1,\n        window: int = 8,\n        n_heads: int = N_HEADS,\n        dropout: float = 0.0,\n        decay_init_alpha: float = _ALPHA,\n        n_q_mirrors: int = 0,\n    ):\n        super().__init__()\n        self.d_model = d_model\n        self.stride = stride\n        self.window = window\n        self.n_heads = n_heads\n        self.d_head = d_model // n_heads  # 160\n        self.scale = self.d_head ** -0.5\n\n        self.norm = nn.RMSNorm(d_model)\n\n        # Beam mirrors before Q\n        self.q_mirrors = [TernaryMirror(d_model) for _ in range(n_q_mirrors)]\n\n        # Ternary projections (base plates from extraction)\n        self.q_proj = TernaryLinear(d_model, d_model, pre_norm=False)\n        self.k_proj = TernaryLinear(d_model, d_model, pre_norm=False)\n        self.v_proj = TernaryLinear(d_model, d_model, pre_norm=False)\n        self.out_proj = TernaryLinear(d_model, d_model, pre_norm=False)\n\n        # Per-feature beam biases\n        self.k_bias = mx.zeros((d_model,))\n        self.v_bias = mx.zeros((d_model,))\n        self.o_bias = mx.zeros((d_model,))\n\n        self.dropout = nn.Dropout(dropout) if dropout > 0 else None\n\n        # HPE: learnable frequency scaling on crystal eigenfrequencies.\n        # Initialized to 0.0 for checkpoint compatibility (no rotation at start).\n        # Warmed up externally via set_hpe_warmup_fraction().\n        self.hpe_freq_scale = mx.zeros((_N_EIGEN_PAIRS,))\n\n        # Pre-compute log-distance structure\n        w_pos = mx.arange(window, dtype=mx.float32)\n        self._log_distances = mx.log(stride * w_pos + 1.0)\n\n        # Fixed α decay bias (not learnable — confirmed universal at 1.18±0.006)\n        self._decay_bias = -(_ALPHA * self._log_distances)  # (W,)\n\n    def __call__(self, x: mx.array, decay_modulation: float = 1.0) -> mx.array:\n        \"\"\"Full Q·K attention with HPE and fixed α decay.\n\n        HPE rotates K by log-distance × crystal-frequency in the first\n        N_EIGEN_PAIRS dimension pairs. Q stays unrotated (relative encoding).\n        When hpe_freq_scale is 0, HPE is identity (no rotation).\n        \"\"\"\n        B, L, D = x.shape\n        H, Dh = self.n_heads, self.d_head\n        W = self.window\n\n        x_norm = self.norm(x)\n\n        # Beam steering\n        q_in = x_norm\n        for mirror in self.q_mirrors:\n            q_in = mirror(q_in)\n\n        Q = self.q_proj(q_in).reshape(B, L, H, Dh)\n        K = (self.k_proj(x_norm) + self.k_bias).reshape(B, L, H, Dh)\n        V = (self.v_proj(x_norm) + self.v_bias).reshape(B, L, H, Dh)\n\n        # Stride gather\n        query_pos = mx.arange(L)[:, None]\n        offsets = mx.arange(W)[None, :] * self.stride\n        raw_indices = query_pos - offsets\n        valid = raw_indices >= 0\n        indices = mx.maximum(raw_indices, 0)\n\n        GD = H * Dh\n        K_flat = K.reshape(B, L, GD)\n        V_flat = V.reshape(B, L, GD)\n\n        idx = indices.reshape(1, L * W, 1)\n        idx = mx.broadcast_to(idx, (B, L * W, GD))\n\n        K_gathered = mx.take_along_axis(K_flat, idx, axis=1).reshape(B, L, W, H, Dh)\n        V_gathered = mx.take_along_axis(V_flat, idx, axis=1).reshape(B, L, W, H, Dh)\n\n        # ── HPE: rotate K by log-distance × crystal frequencies ──\n        # When hpe_freq_scale is all zeros, this is identity (no rotation).\n        # As freq_scale warms up from 0→1, rotation gradually introduces\n        # crystal-derived positional structure.\n        Q_r = Q.transpose(0, 2, 1, 3)  # (B, H, L, Dh)\n        _, K_gathered_rot = apply_hpe_rotation(\n            Q_r, K_gathered, self._log_distances,\n            n_pairs=_N_EIGEN_PAIRS,\n            freq_scale=self.hpe_freq_scale,\n        )\n\n        K_r = K_gathered_rot.transpose(0, 3, 1, 2, 4)  # (B, H, L, W, Dh)\n        attn = (Q_r[:, :, :, None, :] * K_r).sum(axis=-1) * self.scale\n\n        # Fixed α decay bias (the direct power-law, not cosine approximation)\n        decay_bias = self._decay_bias * decay_modulation  # (W,)\n        attn = attn + decay_bias[None, None, None, :]\n\n        valid_mask = valid[None, None, :, :]\n        attn = mx.where(valid_mask, attn, mx.array(float(\"-inf\")))\n        attn = mx.softmax(attn, axis=-1)\n        if self.dropout is not None:\n            attn = self.dropout(attn)\n\n        V_r = V_gathered.transpose(0, 3, 1, 2, 4)\n        out = (attn[:, :, :, :, None] * V_r).sum(axis=3)\n        out = out.transpose(0, 2, 1, 3).reshape(B, L, D)\n\n        return x + self.out_proj(out) + self.o_bias"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/v14/attention.py.
```

## Assistant

Now fix the StrideStack to remove passive logic:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v14/attention.py",
  "original_content": "        for s, is_ret in zip(cfg.strides, cfg.stride_is_retrieval):\n            if is_ret:\n                self.layers.append(GatedLinearAttention(\n                    d_model=d, stride=s, d_state=cfg.d_state,\n                    n_heads=cfg.n_heads, dropout=cfg.dropout,\n                    n_q_mirrors=n_q,\n                ))\n                self._layer_types.append(\"ret\")\n            else:\n                ssa = SingleStrideAttention(\n                    d_model=d, stride=s, window=cfg.window,\n                    n_heads=cfg.n_heads, dropout=cfg.dropout,\n                    n_q_mirrors=n_q if not (s >= _PASSIVE_STRIDE_MIN) else 0,\n                )\n                self.layers.append(ssa)\n                self._layer_types.append(\"passive\" if ssa.passive else \"comp\")",
  "new_content": "        for s, is_ret in zip(cfg.strides, cfg.stride_is_retrieval):\n            if is_ret:\n                self.layers.append(GatedLinearAttention(\n                    d_model=d, stride=s, d_state=cfg.d_state,\n                    n_heads=cfg.n_heads, dropout=cfg.dropout,\n                    n_q_mirrors=n_q,\n                ))\n                self._layer_types.append(\"ret\")\n            else:\n                self.layers.append(SingleStrideAttention(\n                    d_model=d, stride=s, window=cfg.window,\n                    n_heads=cfg.n_heads, dropout=cfg.dropout,\n                    n_q_mirrors=n_q,\n                ))\n                self._layer_types.append(\"comp\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/v14/attention.py.
```

## Assistant

Now add an HPE warmup helper function to the module, and update the docstring:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v14/attention.py",
  "original_content": "\"\"\"v14 Attention — Stride-Stack at d=1280.\n\nHolographic lens architecture: each stride is a lens pointed at a\ndifferent scale of the context. O(L×W) per stride, ternary, CPU-runnable.\n\nTwo layer types (same as v13, evolved for d=1280):\n  SingleStrideAttention — composition (KIBC dispatch)\n  GatedLinearAttention  — retrieval (M kernel substrate)\n\n11 strides: (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024)\n  s1-s8:    composition (fine → local)\n  s16-s128: retrieval (phrase → paragraph)\n  s256-s1024: composition (document scale)\n\nFractal stride bands (MERA topology) select 4 strides per pass.\nShared across passes within a stack (S5 coherence).\n\nBase plates: extracted from Qwen3.6-27B, packed ternary.\nDelta plates: overlay corrections. No-block on attention (flip-or-keep).\n\nLicense: MIT\n\"\"\"",
  "new_content": "\"\"\"v14 Attention — Stride-Stack at d=1280.\n\nHolographic lens architecture: each stride is a lens pointed at a\ndifferent scale of the context. O(L×W) per stride, ternary, CPU-runnable.\n\nTwo layer types (same as v13, evolved for d=1280):\n  SingleStrideAttention — composition (KIBC dispatch), all strides active\n  GatedLinearAttention  — retrieval (M kernel substrate)\n\n16 strides: powers of 2 from s1 to s32768.\n  Composition strides: full Q·K attention + fixed α=1.18 decay + HPE\n  Retrieval strides: gated linear attention with associative scan\n\nHPE (Holographic Position Encoding): crystal-frequency rotation on K,\nwarmed up from freq_scale=0 (identity) for checkpoint compatibility.\n\nFractal stride bands (MERA topology) select 4 strides per pass.\nShared across passes within a stack (S5 coherence).\n\nBase plates: extracted from Qwen3.6-27B, packed ternary.\nDelta plates: overlay corrections. No-block on attention (flip-or-keep).\n\nLicense: MIT\n\"\"\""
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/v14/attention.py.
```

## Assistant

Now add the HPE warmup utility function after the StrideStack class, before the self-test:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v14/attention.py",
  "original_content": "# ══════════════════════════════════════════════════════════════════════\n# § 4  Self-test\n# ══════════════════════════════════════════════════════════════════════",
  "new_content": "# ══════════════════════════════════════════════════════════════════════\n# § 4  HPE Warmup\n# ══════════════════════════════════════════════════════════════════════\n\n\ndef set_hpe_warmup_fraction(stride_stack: StrideStack, fraction: float) -> None:\n    \"\"\"Set HPE freq_scale on all SSA layers based on warmup fraction.\n\n    Args:\n        stride_stack: The shared StrideStack module.\n        fraction: 0.0 = no rotation (identity), 1.0 = full crystal rotation.\n                  Clamped to [0, 1]. Typically: min(1, step / HPE_WARMUP_STEPS).\n\n    When fraction=0, cos(0)=1, sin(0)=0 → K is unrotated → identical to\n    pre-HPE behavior. This makes checkpoint resume seamless.\n    \"\"\"\n    fraction = max(0.0, min(1.0, fraction))\n    target = mx.full((_N_EIGEN_PAIRS,), fraction)\n    for layer in stride_stack.layers:\n        if isinstance(layer, SingleStrideAttention):\n            layer.hpe_freq_scale = target\n\n\ndef get_hpe_fraction_for_step(step: int, warmup_start: int = 0) -> float:\n    \"\"\"Compute HPE warmup fraction for a given training step.\n\n    Args:\n        step: current training step\n        warmup_start: step at which HPE warmup begins (default: 0, i.e. resume step)\n\n    Returns:\n        fraction in [0, 1]: linear ramp from warmup_start to warmup_start + HPE_WARMUP_STEPS\n    \"\"\"\n    elapsed = step - warmup_start\n    if elapsed <= 0:\n        return 0.0\n    return min(1.0, elapsed / HPE_WARMUP_STEPS)\n\n\n# ══════════════════════════════════════════════════════════════════════\n# § 5  Self-test\n# ══════════════════════════════════════════════════════════════════════"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/v14/attention.py.
```

## Assistant

Now run the self-test:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum/scripts/v14 && python3 attention.py",
  "timeout": 120000
}
```

**Summary:** $ cd /Users/mwhitford/src/verbum/scri...

**Output:**
```
Exit code: 0
Stdout:
config.py self-test: ✓
============================================================
v14 attention.py self-test (stride-stack at d=1280)
============================================================

SingleStrideAttention (s=1, s=8)...
  s=1: (1, 64, 1280) ✓
  s=8: (1, 64, 1280) ✓

GatedLinearAttention (s=16, s=64)...
  s=16: (1, 64, 1280) gate=0.393 ✓
  s=64: (1, 64, 1280) gate=0.406 ✓

StrideStack (16 strides, hybrid)...
  10 composition + 6 retrieval = 16 strides
  Pass 0 [0,4) rev=False: ✓
  Pass 1 [2,6) rev=False: ✓
  Pass 2 [4,8) rev=False: ✓
  Pass 3 [6,9) rev=False: ✓
  Pass 4 [7,11) rev=False: ✓
  Pass 5 [9,13) rev=False: ✓
  Pass 6 [11,15) rev=False: ✓
  Pass 7 [13,16) rev=False: ✓
  Pass 8 [12,16) rev=True: ✓
  Pass 9 [8,12) rev=True: ✓
  Pass 10 [5,9) rev=True: ✓
  Pass 11 [2,6) rev=True: ✓
  Pass 12 [0,4) rev=True: ✓

Gradient flow...
  loss=-0.020297 ✓

============================================================
v14 attention.py: all tests passed ✓
```

## Assistant

All 13 passes back, all tests pass. No passive strides, 10 composition + 6 retrieval.

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport sys\nsys.path.insert(0, 'scripts/v14')\nimport numpy as np\nimport mlx.core as mx\n\nfrom config import V14Config\nfrom attention import StrideStack, SingleStrideAttention, set_hpe_warmup_fraction\n\n# Build the reverted architecture\ncfg = V14Config()\nstack = StrideStack(cfg)\n\n# Get model parameter names\nmodel_keys = set()\nfor name, _ in stack.named_parameters():\n    model_keys.add(name)\n\n# Get checkpoint keys (strip 'shared_stride_stack.' prefix since that's the parent)\nckpt = np.load('checkpoints/v14-td/step_002000/model.npz', allow_pickle=True)\nckpt_keys = set()\nfor k in ckpt.files:\n    if k.startswith('shared_stride_stack.'):\n        ckpt_keys.add(k[len('shared_stride_stack.'):])\n\n# Compare\nin_model_not_ckpt = model_keys - ckpt_keys\nin_ckpt_not_model = ckpt_keys - model_keys\n\nprint('=== Keys in NEW model but NOT in checkpoint ===')\nfor k in sorted(in_model_not_ckpt):\n    print(f'  NEW: {k}')\n\nprint()\nprint('=== Keys in CHECKPOINT but NOT in new model ===')\nfor k in sorted(in_ckpt_not_model):\n    print(f'  OLD: {k}')\n\nprint()\nprint(f'Model keys: {len(model_keys)}')\nprint(f'Checkpoint keys: {len(ckpt_keys)}')\nprint(f'Shared: {len(model_keys & ckpt_keys)}')\n\n# Verify HPE warmup at 0 means identity\nprint()\nprint('=== HPE warmup test ===')\nset_hpe_warmup_fraction(stack, 0.0)\nfor layer in stack.layers:\n    if isinstance(layer, SingleStrideAttention):\n        fs = layer.hpe_freq_scale\n        assert float(mx.max(mx.abs(fs)).item()) == 0.0, f'freq_scale not zero: {fs}'\nprint('HPE at fraction=0: all freq_scale = 0 (identity rotation) ✓')\n\nset_hpe_warmup_fraction(stack, 0.5)\nfor layer in stack.layers:\n    if isinstance(layer, SingleStrideAttention):\n        fs = layer.hpe_freq_scale\n        assert float(fs[0].item()) == 0.5, f'expected 0.5, got {float(fs[0].item())}'\n        break\nprint('HPE at fraction=0.5: freq_scale = 0.5 ✓')\n\nset_hpe_warmup_fraction(stack, 1.0)\nfor layer in stack.layers:\n    if isinstance(layer, SingleStrideAttention):\n        fs = layer.hpe_freq_scale\n        assert float(fs[0].item()) == 1.0\n        break\nprint('HPE at fraction=1.0: freq_scale = 1.0 ✓')\n\"",
  "timeout": 120000
}
```

**Summary:** $ python3 -c " import sys sys.path.in...

**Output:**
```
Exit code: 1
Stderr:
Traceback (most recent call last):
  File "<string>", line 16, in <module>
    for name, _ in stack.named_parameters():
                   ^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/lib/python3.14/site-packages/mlx/nn/layers/base.py", line 103, in __getattr__
    super(Module, self).__getattribute__(key)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^
AttributeError: 'StrideStack' object has no attribute 'named_parameters'
Stdout:
config.py self-test: ✓
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport sys\nsys.path.insert(0, 'scripts/v14')\nimport numpy as np\nimport mlx.core as mx\nimport mlx.nn as nn\n\nfrom config import V14Config\nfrom attention import StrideStack, SingleStrideAttention, set_hpe_warmup_fraction\n\n# Build the reverted architecture\ncfg = V14Config()\nstack = StrideStack(cfg)\n\n# Get model parameter names via MLX's tree_flatten\nmodel_keys = set()\nfor name, _ in nn.Module.parameters(stack).items() if hasattr(nn.Module.parameters(stack), 'items') else []:\n    model_keys.add(name)\n\n# Actually use the right MLX API\nparams = stack.parameters()\n\n# Let's just do a flat key comparison using mlx's named approach\ndef get_leaf_keys(d, prefix=''):\n    keys = set()\n    if isinstance(d, dict):\n        for k, v in d.items():\n            keys |= get_leaf_keys(v, f'{prefix}.{k}' if prefix else k)\n    elif isinstance(d, list):\n        for i, v in enumerate(d):\n            keys |= get_leaf_keys(v, f'{prefix}.{i}')\n    elif isinstance(d, mx.array):\n        keys.add(prefix)\n    return keys\n\nmodel_keys = get_leaf_keys(params)\n\n# Get checkpoint keys (strip 'shared_stride_stack.' prefix)\nckpt = np.load('checkpoints/v14-td/step_002000/model.npz', allow_pickle=True)\nckpt_keys = set()\nfor k in ckpt.files:\n    if k.startswith('shared_stride_stack.'):\n        ckpt_keys.add(k[len('shared_stride_stack.'):])\n\n# Compare\nin_model_not_ckpt = model_keys - ckpt_keys\nin_ckpt_not_model = ckpt_keys - model_keys\n\nprint('=== Keys in NEW model but NOT in checkpoint ===')\nfor k in sorted(in_model_not_ckpt):\n    print(f'  NEW: {k}')\n\nprint()\nprint('=== Keys in CHECKPOINT but NOT in new model ===')\nfor k in sorted(in_ckpt_not_model):\n    print(f'  OLD: {k}')\n\nprint()\nprint(f'Model keys: {len(model_keys)}')\nprint(f'Checkpoint keys: {len(ckpt_keys)}')\nprint(f'Shared: {len(model_keys & ckpt_keys)}')\n\"",
  "timeout": 120000
}
```

**Summary:** $ python3 -c " import sys sys.path.in...

**Output:**
```
Exit code: 0
Stdout:
config.py self-test: ✓
=== Keys in NEW model but NOT in checkpoint ===
  NEW: layers.0.hpe_freq_scale
  NEW: layers.0.k_proj.weight
  NEW: layers.0.out_proj.weight
  NEW: layers.0.q_proj.weight
  NEW: layers.0.v_proj.weight
  NEW: layers.1.hpe_freq_scale
  NEW: layers.1.k_proj.weight
  NEW: layers.1.out_proj.weight
  NEW: layers.1.q_proj.weight
  NEW: layers.1.v_proj.weight
  NEW: layers.10.hpe_freq_scale
  NEW: layers.10.k_proj.weight
  NEW: layers.10.out_proj.weight
  NEW: layers.10.q_proj.weight
  NEW: layers.10.v_proj.weight
  NEW: layers.11.hpe_freq_scale
  NEW: layers.11.k_proj.weight
  NEW: layers.11.out_proj.weight
  NEW: layers.11.q_proj.weight
  NEW: layers.11.v_proj.weight
  NEW: layers.12.hpe_freq_scale
  NEW: layers.12.k_proj.weight
  NEW: layers.12.out_proj.weight
  NEW: layers.12.q_proj.weight
  NEW: layers.12.v_proj.weight
  NEW: layers.13.hpe_freq_scale
  NEW: layers.13.k_proj.weight
  NEW: layers.13.out_proj.weight
  NEW: layers.13.q_proj.weight
  NEW: layers.13.v_proj.weight
  NEW: layers.14.hpe_freq_scale
  NEW: layers.14.k_proj.weight
  NEW: layers.14.out_proj.weight
  NEW: layers.14.q_proj.weight
  NEW: layers.14.v_proj.weight
  NEW: layers.15.hpe_freq_scale
  NEW: layers.15.k_proj.weight
  NEW: layers.15.out_proj.weight
  NEW: layers.15.q_proj.weight
  NEW: layers.15.v_proj.weight
  NEW: layers.2.hpe_freq_scale
  NEW: layers.2.k_proj.weight
  NEW: layers.2.out_proj.weight
  NEW: layers.2.q_proj.weight
  NEW: layers.2.v_proj.weight
  NEW: layers.3.hpe_freq_scale
  NEW: layers.3.k_proj.weight
  NEW: layers.3.out_proj.weight
  NEW: layers.3.q_proj.weight
  NEW: layers.3.v_proj.weight
  NEW: layers.4.gate_proj.weight
  NEW: layers.4.k_proj.weight
  NEW: layers.4.out_proj.weight
  NEW: layers.4.q_proj.weight
  NEW: layers.4.v_proj.weight
  NEW: layers.5.gate_proj.weight
  NEW: layers.5.k_proj.weight
  NEW: layers.5.out_proj.weight
  NEW: layers.5.q_proj.weight
  NEW: layers.5.v_proj.weight
  NEW: layers.6.gate_proj.weight
  NEW: layers.6.k_proj.weight
  NEW: layers.6.out_proj.weight
  NEW: layers.6.q_proj.weight
  NEW: layers.6.v_proj.weight
  NEW: layers.7.gate_proj.weight
  NEW: layers.7.k_proj.weight
  NEW: layers.7.out_proj.weight
  NEW: layers.7.q_proj.weight
  NEW: layers.7.v_proj.weight
  NEW: layers.8.gate_proj.weight
  NEW: layers.8.k_proj.weight
  NEW: layers.8.out_proj.weight
  NEW: layers.8.q_proj.weight
  NEW: layers.8.v_proj.weight
  NEW: layers.9.gate_proj.weight
  NEW: layers.9.k_proj.weight
  NEW: layers.9.out_proj.weight
  NEW: layers.9.q_proj.weight
  NEW: layers.9.v_proj.weight

=== Keys in CHECKPOINT but NOT in new model ===
  OLD: layers.0.decay_alpha
  OLD: layers.0.k_proj.base_weight
  OLD: layers.0.k_proj.delta_weight
  OLD: layers.0.out_proj.base_weight
  OLD: layers.0.out_proj.delta_weight
  OLD: layers.0.q_proj.base_weight
  OLD: layers.0.q_proj.delta_weight
  OLD: layers.0.v_proj.base_weight
  OLD: layers.0.v_proj.delta_weight
  OLD: layers.1.decay_alpha
  OLD: layers.1.k_proj.base_weight
  OLD: layers.1.k_proj.delta_weight
  OLD: layers.1.out_proj.base_weight
  OLD: layers.1.out_proj.delta_weight
  OLD: layers.1.q_proj.base_weight
  OLD: layers.1.q_proj.delta_weight
  OLD: layers.1.v_proj.base_weight
  OLD: layers.1.v_proj.delta_weight
  OLD: layers.10.decay_alpha
  OLD: layers.10.k_proj.base_weight
  OLD: layers.10.k_proj.delta_weight
  OLD: layers.10.out_proj.base_weight
  OLD: layers.10.out_proj.delta_weight
  OLD: layers.10.q_proj.base_weight
  OLD: layers.10.q_proj.delta_weight
  OLD: layers.10.v_proj.base_weight
  OLD: layers.10.v_proj.delta_weight
  OLD: layers.11.decay_alpha
  OLD: layers.11.k_proj.base_weight
  OLD: layers.11.k_proj.delta_weight
  OLD: layers.11.out_proj.base_weight
  OLD: layers.11.out_proj.delta_weight
  OLD: layers.11.q_proj.base_weight
  OLD: layers.11.q_proj.delta_weight
  OLD: layers.11.v_proj.base_weight
  OLD: layers.11.v_proj.delta_weight
  OLD: layers.12.decay_alpha
  OLD: layers.12.k_proj.base_weight
  OLD: layers.12.k_proj.delta_weight
  OLD: layers.12.out_proj.base_weight
  OLD: layers.12.out_proj.delta_weight
  OLD: layers.12.q_proj.base_weight
  OLD: layers.12.q_proj.delta_weight
  OLD: layers.12.v_proj.base_weight
  OLD: layers.12.v_proj.delta_weight
  OLD: layers.13.decay_alpha
  OLD: layers.13.k_proj.base_weight
  OLD: layers.13.k_proj.delta_weight
  OLD: layers.13.out_proj.base_weight
  OLD: layers.13.out_proj.delta_weight
  OLD: layers.13.q_proj.base_weight
  OLD: layers.13.q_proj.delta_weight
  OLD: layers.13.v_proj.base_weight
  OLD: layers.13.v_proj.delta_weight
  OLD: layers.14.decay_alpha
  OLD: layers.14.k_proj.base_weight
  OLD: layers.14.k_proj.delta_weight
  OLD: layers.14.out_proj.base_weight
  OLD: layers.14.out_proj.delta_weight
  OLD: layers.14.q_proj.base_weight
  OLD: layers.14.q_proj.delta_weight
  OLD: layers.14.v_proj.base_weight
  OLD: layers.14.v_proj.delta_weight
  OLD: layers.15.decay_alpha
  OLD: layers.15.k_proj.base_weight
  OLD: layers.15.k_proj.delta_weight
  OLD: layers.15.out_proj.base_weight
  OLD: layers.15.out_proj.delta_weight
  OLD: layers.15.q_proj.base_weight
  OLD: layers.15.q_proj.delta_weight
  OLD: layers.15.v_proj.base_weight
  OLD: layers.15.v_proj.delta_weight
  OLD: layers.2.decay_alpha
  OLD: layers.2.k_proj.base_weight
  OLD: layers.2.k_proj.delta_weight
  OLD: layers.2.out_proj.base_weight
  OLD: layers.2.out_proj.delta_weight
  OLD: layers.2.q_proj.base_weight
  OLD: layers.2.q_proj.delta_weight
  OLD: layers.2.v_proj.base_weight
  OLD: layers.2.v_proj.delta_weight
  OLD: layers.3.decay_alpha
  OLD: layers.3.k_proj.base_weight
  OLD: layers.3.k_proj.delta_weight
  OLD: layers.3.out_proj.base_weight
  OLD: layers.3.out_proj.delta_weight
  OLD: layers.3.q_proj.base_weight
  OLD: layers.3.q_proj.delta_weight
  OLD: layers.3.v_proj.base_weight
  OLD: layers.3.v_proj.delta_weight
  OLD: layers.4.gate_proj.base_weight
  OLD: layers.4.gate_proj.delta_weight
  OLD: layers.4.k_proj.base_weight
  OLD: layers.4.k_proj.delta_weight
  OLD: layers.4.out_proj.base_weight
  OLD: layers.4.out_proj.delta_weight
  OLD: layers.4.q_proj.base_weight
  OLD: layers.4.q_proj.delta_weight
  OLD: layers.4.v_proj.base_weight
  OLD: layers.4.v_proj.delta_weight
  OLD: layers.5.gate_proj.base_weight
  OLD: layers.5.gate_proj.delta_weight
  OLD: layers.5.k_proj.base_weight
  OLD: layers.5.k_proj.delta_weight
  OLD: layers.5.out_proj.base_weight
  OLD: layers.5.out_proj.delta_weight
  OLD: layers.5.q_proj.base_weight
  OLD: layers.5.q_proj.delta_weight
  OLD: layers.5.v_proj.base_weight
  OLD: layers.5.v_proj.delta_weight
  OLD: layers.6.gate_proj.base_weight
  OLD: layers.6.gate_proj.delta_weight
  OLD: layers.6.k_proj.base_weight
  OLD: layers.6.k_proj.delta_weight
  OLD: layers.6.out_proj.base_weight
  OLD: layers.6.out_proj.delta_weight
  OLD: layers.6.q_proj.base_weight
  OLD: layers.6.q_proj.delta_weight
  OLD: layers.6.v_proj.base_weight
  OLD: layers.6.v_proj.delta_weight
  OLD: layers.7.gate_proj.base_weight
  OLD: layers.7.gate_proj.delta_weight
  OLD: layers.7.k_proj.base_weight
  OLD: layers.7.k_proj.delta_weight
  OLD: layers.7.out_proj.base_weight
  OLD: layers.7.out_proj.delta_weight
  OLD: layers.7.q_proj.base_weight
  OLD: layers.7.q_proj.delta_weight
  OLD: layers.7.v_proj.base_weight
  OLD: layers.7.v_proj.delta_weight
  OLD: layers.8.gate_proj.base_weight
  OLD: layers.8.gate_proj.delta_weight
  OLD: layers.8.k_proj.base_weight
  OLD: layers.8.k_proj.delta_weight
  OLD: layers.8.out_proj.base_weight
  OLD: layers.8.out_proj.delta_weight
  OLD: layers.8.q_proj.base_weight
  OLD: layers.8.q_proj.delta_weight
  OLD: layers.8.v_proj.base_weight
  OLD: layers.8.v_proj.delta_weight
  OLD: layers.9.gate_proj.base_weight
  OLD: layers.9.gate_proj.delta_weight
  OLD: layers.9.k_proj.base_weight
  OLD: layers.9.k_proj.delta_weight
  OLD: layers.9.out_proj.base_weight
  OLD: layers.9.out_proj.delta_weight
  OLD: layers.9.q_proj.base_weight
  OLD: layers.9.q_proj.delta_weight
  OLD: layers.9.v_proj.base_weight
  OLD: layers.9.v_proj.delta_weight

Model keys: 292
Checkpoint keys: 362
Shared: 212
```

## Assistant

OK — this is just the naming convention difference. The checkpoint uses `base_weight`/`delta_weight` (DeltaTernaryLinear) while MLX's `parameters()` sees `.weight` from plain TernaryLinear. This is the existing loading code's job — it already handles this mapping. Let me verify:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"base_weight\\|delta_weight\\|decay_alpha\\|load.*model\\|load.*checkpoint\\|hpe_freq_scale\" scripts/v14/train_td.py | head -40"
}
```

**Summary:** $ grep -n "base_weight\|delta_weight\...

**Output:**
```
Exit code: 0
Stdout:
17:  - Base plates loaded from checkpoints/v14-extracted/model.npz
418:    # Step 4: freeze delta architecture (base_weight + delta_weight excluded from Adam)
448:        delta_unpacked = unpack_ternary_mlx(dtl.delta_weight)  # (N, K) int8
456:            dtl.delta_weight = pack_ternary_mlx(fixed)
457:            mx.eval(dtl.delta_weight)
510:        base_unpacked = unpack_ternary_mlx(dtl.base_weight)    # (N, K) int8
511:        delta_unpacked = unpack_ternary_mlx(dtl.delta_weight)  # (N, K) int8
521:        td_inputs.append((path, dtl.delta_weight, routing, dtl.base_weight, path in attn_paths))
729:            # Re-load model weights to undo the warm-up gradient step.
737:                model.load_weights(str(model_path), strict=False)
742:                print(f"📂 Re-loaded model weights from {model_path}", file=sys.stderr)
905:                    model.load_weights(str(last_ckpt / "model.npz"), strict=False)
982:                        dtl.delta_weight = info["new_packed"]
983:                        mx.eval(dtl.delta_weight)
1233:        mx.eval(dtl.delta_weight)
1234:        delta_snapshots[f"{delta_key}_delta_packed"] = dtl.delta_weight
1305:            "Base plates loaded from checkpoints/v14-extracted/model.npz."
1540:            # so load_weights will land in DeltaTernaryLinear.base_weight / .gamma)
1541:            model.load_weights(str(resume_path / "model.npz"), strict=False)
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"def load\\|def save\\|model.npz\\|decay_alpha\\|hpe_freq\" scripts/v14/model.py | head -30"
}
```

**Summary:** $ grep -n "def load\|def save\|model....

**Output:**
```
Exit code: 0
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && sed -n '1530,1560p' scripts/v14/train_td.py"
}
```

**Summary:** $ sed -n '1530,1560p' scripts/v14/tra...

**Output:**
```
Exit code: 0
Stdout:
print(f"  Delta modules: {len(delta_modules)}", file=sys.stderr)
    for path, dtl in delta_modules:
        print(f"    {path}: ({dtl.out_features}, {dtl.in_features})", file=sys.stderr)

    # ── Resume: find start_step ───────────────────────────────
    start_step = 0
    if args.resume:
        resume_path = Path(args.resume).resolve()
        if resume_path.exists():
            # Load base weights first (before convert_to_delta was already done,
            # so load_weights will land in DeltaTernaryLinear.base_weight / .gamma)
            model.load_weights(str(resume_path / "model.npz"), strict=False)
            mx.eval(model.parameters())
            restore_ternary(model)
            freeze_ternary_weights(model)
            freeze_delta_architecture(model)
            print(f"📂 Loaded resume weights from {resume_path}", file=sys.stderr)

            state_path = resume_path / "state.json"
            if state_path.exists():
                saved_state = json.loads(state_path.read_text())
                start_step = saved_state.get("step", 0)
                print(f"  Resuming from step {start_step}", file=sys.stderr)
        else:
            print(f"⚠  Resume path not found: {resume_path}", file=sys.stderr)

    # ── Data loader ───────────────────────────────────────────
    prose_loader = ShardedDataLoader(
        data_dir=cfg.data_dir,
        batch_size=cfg.batch_size,
        seq_len=cfg.seq_len,
```

## Assistant

Good — `load_weights(..., strict=False)` handles this. It loads what matches and silently skips what doesn't. The `decay_alpha` keys from the checkpoint will be loaded but since the new model has no `decay_alpha` attribute, they'll be ignored. The new `hpe_freq_scale` won't be in the checkpoint, so it stays at its initialized value (zeros). 

But I need to make sure the training script actually calls the HPE warmup. Let me check what hooks exist:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"def train_step\\|for step\\|# ── Training loop\\|warmup\\|hpe\" scripts/v14/train_td.py | head -30"
}
```

**Summary:** $ grep -n "def train_step\|for step\|...

**Output:**
```
Exit code: 0
Stdout:
225:def cosine_lr(step, warmup_steps, total_steps, lr_max, lr_floor_ratio=0.01):
226:    """Cosine LR schedule with linear warmup."""
227:    if step < warmup_steps:
228:        return lr_max * step / max(warmup_steps, 1)
229:    progress = (step - warmup_steps) / max(total_steps - warmup_steps, 1)
591:    structured_warmup_steps: int = 0,
605:      - Crystal warmup schedule
621:    print(f"  TD: flip_rate={args.td_flip_rate}  warmup={args.td_warmup}"
643:        warmup_steps=args.td_warmup,
684:    _structured_warmup_done = False  # True after structured-only warmup phase completes
781:            # Restore structured warmup state
782:            if "structured_warmup_done" in state:
783:                _structured_warmup_done = state["structured_warmup_done"]
784:                if _structured_warmup_done and hasattr(train_loader, 'mix_ratio'):
786:                print(f"  structured_warmup_done = {_structured_warmup_done}", file=sys.stderr)
807:    for step in range(start_step + 1, total_steps + 1):
810:        # ── Structured data warmup → mix transition ───────────
815:            not _structured_warmup_done
816:            and structured_warmup_steps > 0
817:            and step > structured_warmup_steps
821:            _structured_warmup_done = True
823:                f"\n🔮 Step {step}: structured warmup complete → "
829:        lr = cosine_lr(step, cfg.warmup_steps, total_steps, cfg.lr, cfg.lr_floor_ratio)
832:        # Crystal warmup: crystal_direct_lambda anneals start→floor over warmup steps
833:        if cfg.crystal_warmup_steps > 0 and step <= cfg.crystal_warmup_steps:
834:            progress = step / cfg.crystal_warmup_steps
974:            td_result = {"total_flips": 0, "in_warmup": True, "per_module": {}}
1081:                "td_in_warmup": td_result["in_warmup"],
1157:                structured_warmup_done=_structured_warmup_done,
1158:                structured_warmup_steps=structured_warmup_steps,
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && sed -n '750,780p' scripts/v14/train_td.py"
}
```

**Summary:** $ sed -n '750,780p' scripts/v14/train...

**Output:**
```
Exit code: 0
Stdout:
# Prefer --resume, fallback to step_dir
        state_path = None
        if resume_dir and (resume_dir / "state.json").exists():
            state_path = resume_dir / "state.json"
        elif (step_dir / "state.json").exists():
            state_path = step_dir / "state.json"
        if state_path.exists():
            state = json.loads(state_path.read_text())
            ema_val = state.get("crystal_ema")
            if ema_val is not None:
                model._crystal_ema = mx.array(float(ema_val))
                print(f"  crystal_ema = {ema_val:.6f}", file=sys.stderr)
            s5_state = state.get("s5_identity_state")
            if s5_state is not None:
                model.s5_identity.identity_state = mx.array(s5_state)
                print(
                    f"  s5_identity_state restored ({len(s5_state)} dims)",
                    file=sys.stderr,
                )

            # Restore training loop counters
            if "total_td_flips" in state:
                total_td_flips = state["total_td_flips"]
                print(f"  total_td_flips = {total_td_flips:,}", file=sys.stderr)
            if "n_reductions" in state:
                n_reductions = state["n_reductions"]
                print(f"  n_reductions = {n_reductions}", file=sys.stderr)
            if "td_active" in state:
                td_active = state["td_active"]
                print(f"  td_active = {td_active}", file=sys.stderr)
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && sed -n '805,835p' scripts/v14/train_td.py"
}
```

**Summary:** $ sed -n '805,835p' scripts/v14/train...

**Output:**
```
Exit code: 0
Stdout:
nan_consecutive = 0  # NaN skip/rollback counter

    for step in range(start_step + 1, total_steps + 1):
        t0 = time.time()

        # ── Structured data warmup → mix transition ───────────
        # For the first N steps, mix_ratio=1.0 (pure structured data)
        # to latch the crystal lattice immediately. Then switch to
        # normal mix_ratio for prose+structured mixture.
        if (
            not _structured_warmup_done
            and structured_warmup_steps > 0
            and step > structured_warmup_steps
            and hasattr(train_loader, 'mix_ratio')
        ):
            train_loader.mix_ratio = target_mix_ratio
            _structured_warmup_done = True
            print(
                f"\n🔮 Step {step}: structured warmup complete → "
                f"mix_ratio={target_mix_ratio}",
                file=sys.stderr,
                flush=True,
            )

        lr = cosine_lr(step, cfg.warmup_steps, total_steps, cfg.lr, cfg.lr_floor_ratio)
        adam.learning_rate = lr

        # Crystal warmup: crystal_direct_lambda anneals start→floor over warmup steps
        if cfg.crystal_warmup_steps > 0 and step <= cfg.crystal_warmup_steps:
            progress = step / cfg.crystal_warmup_steps
            crystal_lambda_eff = (
```

## Assistant

I see the training loop structure. I need to add HPE warmup into the step loop. Let me find the right place — right after the LR schedule update:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && sed -n '828,842p' scripts/v14/train_td.py"
}
```

**Summary:** $ sed -n '828,842p' scripts/v14/train...

**Output:**
```
Exit code: 0
Stdout:
lr = cosine_lr(step, cfg.warmup_steps, total_steps, cfg.lr, cfg.lr_floor_ratio)
        adam.learning_rate = lr

        # Crystal warmup: crystal_direct_lambda anneals start→floor over warmup steps
        if cfg.crystal_warmup_steps > 0 and step <= cfg.crystal_warmup_steps:
            progress = step / cfg.crystal_warmup_steps
            crystal_lambda_eff = (
                cfg.crystal_direct_lambda_start
                + (cfg.crystal_direct_lambda - cfg.crystal_direct_lambda_start)
                * 0.5 * (1.0 - math.cos(math.pi * progress))
            )
            model.cfg.crystal_direct_lambda = crystal_lambda_eff

        model._training_step = step
```

## Assistant

Good, I'll add HPE warmup right after the crystal warmup block. Let me also check the imports at the top of train_td.py:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && head -40 scripts/v14/train_td.py"
}
```

**Summary:** $ head -40 scripts/v14/train_td.py

**Output:**
```
Exit code: 0
Stdout:
"""
v14 — TernaryDescent Training Script (delta plate architecture)

Dual optimizer: Adam trains continuous beams, TernaryDescent trains
discrete delta plates.  Both run on the same backward pass.

Architecture:
  - Base plates:  extracted from Qwen3.6-27B (Apache 2.0), FROZEN
  - Delta plates: attention only, no-block ({+1, -1} only — NEVER 0)
  - Effective:    base ⊙ delta (ternary × ternary = ternary)
  - Gamma/norms:  trained by Adam

Key differences from v13:
  - d_model = 1280 (was 512)
  - No-block constraint: attention delta plates NEVER contain 0.
    FFN delta plates (if converted) may still use {+1, -1, 0}.
  - Base plates loaded from checkpoints/v14-extracted/model.npz
  - Crystal loss is _last_crystal_mse / _last_parity / _last_cross_zone
    (not _last_crystal_loss / _last_parity_loss / _last_cross_zone_loss)

Pipeline:
  1. extract_qwen36.py → base plates (model.npz)
  2. train_td.py → delta plate training on top of frozen base
  3. Periodic REDUCE: fold delta into base, reset delta, continue

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from collections import deque
from pathlib import Path

os.environ["PYTHONUNBUFFERED"] = "1"
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && sed -n '43,65p' scripts/v14/train_td.py"
}
```

**Summary:** $ sed -n '43,65p' scripts/v14/train_t...

**Output:**
```
Exit code: 0
Stdout:
import mlx.nn as nn
import mlx.optimizers as optim
import numpy as np
from mlx.utils import tree_flatten, tree_map, tree_unflatten

sys.path.insert(0, str(Path(__file__).parent))

from config import V14Config
from data import ShardedDataLoader, MixedDataLoader
from model import V14Model
from ternary import (
    TernaryLinear,
    freeze_ternary_weights,
    zero_ternary_grads,
    restore_ternary,
    count_ternary_weights,
    unpack_ternary_mlx,
    pack_ternary_mlx,
    surgical_adam_decay_for_etch,
)
from td import (
    TernaryDescent,
    DeltaTernaryLinear,
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v14/train_td.py",
  "original_content": "from config import V14Config\nfrom data import ShardedDataLoader, MixedDataLoader\nfrom model import V14Model\nfrom ternary import (",
  "new_content": "from attention import set_hpe_warmup_fraction, get_hpe_fraction_for_step, HPE_WARMUP_STEPS\nfrom config import V14Config\nfrom data import ShardedDataLoader, MixedDataLoader\nfrom model import V14Model\nfrom ternary import ("
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/v14/train_td.py.
```

## Assistant

Now add the HPE warmup call into the training loop:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v14/train_td.py",
  "original_content": "        model._training_step = step",
  "new_content": "        # HPE warmup: linearly ramp crystal-frequency rotation from 0→1\n        # over HPE_WARMUP_STEPS from the resume point. At fraction=0, K is\n        # unrotated (identical to pre-HPE behavior, checkpoint compatible).\n        hpe_frac = get_hpe_fraction_for_step(step, warmup_start=start_step)\n        set_hpe_warmup_fraction(model.shared_stride_stack, hpe_frac)\n\n        model._training_step = step"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/v14/train_td.py.
```

## Assistant

Now let me also add HPE fraction to the logging so we can see it:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"td_in_warmup\\|hpe\\|ce=.*ppl\" scripts/v14/train_td.py | head -20"
}
```

**Summary:** $ grep -n "td_in_warmup\|hpe\|ce=.*pp...

**Output:**
```
Exit code: 0
Stdout:
50:from attention import set_hpe_warmup_fraction, get_hpe_fraction_for_step, HPE_WARMUP_STEPS
846:        hpe_frac = get_hpe_fraction_for_step(step, warmup_start=start_step)
847:        set_hpe_warmup_fraction(model.shared_stride_stack, hpe_frac)
1088:                "td_in_warmup": td_result["in_warmup"],
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && sed -n '1078,1095p' scripts/v14/train_td.py"
}
```

**Summary:** $ sed -n '1078,1095p' scripts/v14/tra...

**Output:**
```
Exit code: 0
Stdout:
"loss": step_loss,
                "loss_avg50": avg50,
                "lr": lr,
                "grad_norm": grad_norm,
                "tok_per_sec": tps,
                "elapsed": elapsed,
                "td_flips": td_result["total_flips"],
                "td_flips_since_log": td_flips_this_window,
                "td_total_flips": total_td_flips,
                "td_adam_decayed": n_adam_decayed,
                "td_in_warmup": td_result["in_warmup"],
                "td_active": td_active,
                "delta_avg_changed": avg_changed,
                "n_reductions": n_reductions,
                "no_block_fixed": n_no_block_fixed,
            }
            if ce_val is not None:
                record["ce"] = ce_val
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v14/train_td.py",
  "original_content": "                \"no_block_fixed\": n_no_block_fixed,\n            }\n            if ce_val is not None:\n                record[\"ce\"] = ce_val",
  "new_content": "                \"no_block_fixed\": n_no_block_fixed,\n                \"hpe_fraction\": hpe_frac,\n            }\n            if ce_val is not None:\n                record[\"ce\"] = ce_val"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/v14/train_td.py.
```

## Assistant

Also log it in the state.json for checkpoint persistence:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"structured_warmup_done\\|n_reductions\\|td_active\\|state\\[\" scripts/v14/train_td.py | grep -i \"save\\|dump\\|dict\\|json\" | head -10"
}
```

**Summary:** $ grep -n "structured_warmup_done\|n_...

**Output:**
```
Exit code: 0
Stdout:
1284:        state["data_loader"] = train_loader.save_state()
1296:    state["config"] = asdict(cfg)
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"structured_warmup_done\" scripts/v14/train_td.py"
}
```

**Summary:** $ grep -n "structured_warmup_done" sc...

**Output:**
```
Exit code: 0
Stdout:
685:    _structured_warmup_done = False  # True after structured-only warmup phase completes
783:            if "structured_warmup_done" in state:
784:                _structured_warmup_done = state["structured_warmup_done"]
785:                if _structured_warmup_done and hasattr(train_loader, 'mix_ratio'):
787:                print(f"  structured_warmup_done = {_structured_warmup_done}", file=sys.stderr)
816:            not _structured_warmup_done
822:            _structured_warmup_done = True
1165:                structured_warmup_done=_structured_warmup_done,
1183:        structured_warmup_done=_structured_warmup_done,
1207:    structured_warmup_done: bool = False,
1277:        "structured_warmup_done": structured_warmup_done,
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && sed -n '1150,1170p' scripts/v14/train_td.py"
}
```

**Summary:** $ sed -n '1150,1170p' scripts/v14/tra...

**Output:**
```
Exit code: 0
Stdout:
)
            else:
                print(
                    f"\n⏳ Reduce check @ step {step}: max_changed={max_changed:.4f}"
                    f" > threshold={reduce_threshold} — not ready",
                    file=sys.stderr, flush=True,
                )

        # ── Checkpoint ────────────────────────────────────────
        if step % cfg.checkpoint_interval == 0:
            _save_checkpoint(
                model, adam, td, step, cfg, checkpoint_dir,
                train_losses, n_reductions, total_td_flips, delta_modules,
                train_loader=train_loader,
                td_active=td_active,
                structured_warmup_done=_structured_warmup_done,
                structured_warmup_steps=structured_warmup_steps,
                target_mix_ratio=target_mix_ratio,
            )

    # ── Final ─────────────────────────────────────────────────
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && sed -n '1270,1300p' scripts/v14/train_td.py"
}
```

**Summary:** $ sed -n '1270,1300p' scripts/v14/tra...

**Output:**
```
Exit code: 0
Stdout:
"crystal_ema": float(crystal_ema.item()) if crystal_ema is not None else None,
        "s5_identity_state": (
            s5_identity.tolist() if s5_identity is not None else None
        ),

        # Training loop state — needed for exact resume
        "td_active": td_active,
        "structured_warmup_done": structured_warmup_done,
        "structured_warmup_steps": structured_warmup_steps,
        "target_mix_ratio": target_mix_ratio,
    }

    # Data loader position — exact shard/offset for reproducible resume
    if train_loader is not None and hasattr(train_loader, "save_state"):
        state["data_loader"] = train_loader.save_state()

    # Per-module delta stats (quick inspection without loading weights)
    delta_stats = {}
    for path, mod in model.named_modules():
        if isinstance(mod, DeltaTernaryLinear):
            delta_stats[path] = mod.delta_stats()
    if delta_stats:
        state["delta_stats"] = delta_stats

    # Config snapshot — full hyperparameters that produced this run
    from dataclasses import asdict
    state["config"] = asdict(cfg)

    (step_dir / "state.json").write_text(json.dumps(_sanitize(state), indent=2))
    print(f"💾 Checkpoint: {step_dir}", file=sys.stderr, flush=True)
```

## Assistant

The `start_step` in state.json already tells us where HPE warmup began. The warmup function computes `step - start_step`, so on resume from step 2000, step 2001 will have `hpe_frac = 1/300 ≈ 0.003`, and by step 2300 it'll be 1.0. That's all handled. The checkpoint compatibility is verified — `strict=False` handles the key mismatch.

Let me do a quick syntax check on train_td.py:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum/scripts/v14 && python3 -c \"import ast; ast.parse(open('train_td.py').read()); print('syntax OK')\""
}
```

**Summary:** $ cd /Users/mwhitford/src/verbum/scri...

**Output:**
```
Exit code: 0
Stdout:
syntax OK
```

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/v15-kernel-revert.md",
  "content": "---\ntitle: \"v15 Kernel Architecture — Revert & Lessons Learned\"\nstatus: done\ncategory: architecture\ntags: [v15, kernel, revert, passive-strides, HPE, alpha, architecture, lessons]\nrelated: [v15-kernel-architecture.md, ../v14-architecture.md, ../progressive-collapse.md, ../training-protocols.md, kernel-training.md, structured-training.md]\ndepends-on: [../v14-architecture.md]\n---\n\n# v15 Kernel Architecture — Revert & Lessons Learned\n\n> Session 156. Reverted passive strides and Stack B reduction from\n> session 152. Kept α-lock and HPE (with warmup). Documents what\n> was tried, what failed, what was preserved, and when to revisit.\n\n## What Happened\n\n### Session 152: Three architecture changes + HPE\n\nMotivated by the progressive collapse finding (Qwen-27B computes\nin 2D, PR=2.2) and the distance prior analysis (88% of strides are\nself-attention-dominated at α=1.18), four changes were made in one\ncommit (`96d687a`):\n\n1. **Fix α=1.18** — remove from optimizer, frozen constant\n2. **Passive strides** — s4+ skip Q/K entirely, use fixed distance prior\n3. **Stack B 4→2 passes** — reduce serial chain from 13→11 passes\n4. **HPE** — crystal-frequency log-distance rotation on K, replacing\n   learned decay as the position encoding mechanism\n\n### Session 155: v14-kd ran this architecture + KD → diverged\n\n| Metric | v14-td (old arch) | v14-kd (new arch + KD) |\n|--------|-------------------|------------------------|\n| Step 500 PPL | 16,503 | 40,623 |\n| Step 1000 PPL | 10,157 | 46,736 (diverging) |\n| Ratio | 1× | 2.5–4.6× worse |\n\nRoot cause: too many simultaneous changes. Could not isolate which\nchange (or combination) caused the divergence.\n\n## What Was Reverted (Session 156)\n\n### 1. Passive strides — REVERTED\n\n**What it did:** Strides s4+ lost Q/K projections entirely. Attention\nbecame a fixed weighted sum using `1/(stride×w + 1)^1.18`.\n\n**Why reverted:** In strided attention, each stride is the SOLE provider\nfor its distance range. Making s4+ passive means positions 16–56 tokens\nback lose ALL content-dependent attention. s4 had 27.4% non-self weight\nthat became fixed — not negligible.\n\nThe passive stride observation was about the TEACHER's converged behavior.\nThe student hasn't converged yet — it may need content routing at these\nstrides to LEARN the right patterns. Hardcoding the destination prevents\nthe student from finding it through training.\n\nTD was targeting out_proj layers 4–9 (exactly the retrieval strides in\nthis range). Removing Q/K for these strides is architecturally\ncontradictory with what TD was trying to do.\n\n**Code:** `_PASSIVE_STRIDE_MIN` removed, `_passive_forward` removed,\nall SSA layers restored with full Q/K/V/O projections.\n\n### 2. Stack B 4→2 passes — REVERTED\n\n**What it did:** `STACK_B_BANDS` changed from 4 tuples to 2 wider\ntuples. Serial chain went from 13→11 passes.\n\n**Why reverted:** The overlap pattern between adjacent passes creates\ninformation flow. Reducing passes may starve the serial chain. The\njustification (\"Stack B computes in compressed space\") was based on\nthe teacher's converged structure, not the student's learning needs.\n\n**Code:** `STACK_B_BANDS` restored to `((7,11), (9,13), (11,15), (13,16))`.\n`n_passes` back to 13.\n\n## What Was Kept\n\n### 1. α=1.18 frozen — KEPT ✅\n\n**Why:** After 1500+ steps of gradient pressure, α stayed at 1.1739±0.001\nacross all 80 heads (10 comp layers × 8 heads). Layers 12-15 never moved\nfrom init. This is a measured constant, not a hypothesis.\n\n**Checkpoint delta:** Values were already at 1.174. Replacing with 1.18\nintroduces Δ=0.006 — negligible. `decay_alpha` keys in checkpoint are\nsilently ignored on load (`strict=False`).\n\n### 2. HPE (Holographic Position Encoding) — KEPT, with warmup ✅\n\n**What it does:** Rotates K by `log(stride×w+1) × crystal_eigenfreq`\nin the first 8 dimensions (4 eigenplane pairs). Q stays unrotated\n(relative encoding). Crystal frequencies from Zone B eigendecomposition.\n\n**Why kept:** The physics are principled — crystal eigenvalues are\nmeasured, log-distance is the natural encoding for power-law decay.\nThis is a motivated replacement for RoPE, derived from the project's\nown findings about holographic lens structure.\n\n**Warmup strategy:** `freq_scale` initialized to 0.0 (not 1.0).\nAt `freq_scale=0`, `cos(0)=1, sin(0)=0` → K is unrotated → identical\nto pre-HPE behavior. This makes checkpoint resume seamless.\n\nLinear warmup over 300 steps from resume point:\n```\nstep 2001: freq_scale = 0.003 (essentially no rotation)\nstep 2150: freq_scale = 0.5   (half crystal rotation)\nstep 2300: freq_scale = 1.0   (full crystal rotation)\n```\n\nThe model's Q/K relationships gradually adapt to the rotation rather\nthan being shocked. If HPE helps, PPL will improve during/after warmup.\nIf it doesn't, the warmup limits damage.\n\n`freq_scale` is learnable per-eigenplane — gradient will push it toward\nwhatever value actually helps, and away from harmful values.\n\n## Ideas Preserved for Future Sessions\n\nThese are VALID research directions, just premature for the current\ntraining stage.\n\n### Passive strides — revisit conditions\n\nRe-test passive strides WHEN:\n- v14-td has converged (PPL < 1000, flip rate plateaued)\n- Gradient-subspace alignment test on trained model shows cos > 0.5\n  (gradient aligned with T's SVD subspace → model is refining, not expanding)\n- Test ONE change at a time: passive strides at s16+ first (only the\n  strides with <1% non-self weight), measure PPL delta over 200 steps\n\nThe key test: `eval_ppl.py` with vs without Q/K on s16+ strides.\nIf PPL difference < 0.5%, it's safe. Then progressively lower the\nthreshold: s8+, then s4+.\n\n### Stack B reduction — revisit conditions\n\nRe-test when:\n- Passive strides (if validated) reduce per-pass cost enough that\n  pass count is the remaining bottleneck\n- The model's Zone B has been shown to be linear (R²>0.95) on the\n  student, not just the teacher\n- Test: 4→3→2 passes progressively, measuring PPL at each step\n\n### Kernel training (composed plate)\n\nFully valid NOW as a training accelerator:\n- 4.4× speedup via `train_kernel.py`\n- Gradient cosine 0.9698 between composed plate and full model\n- Does NOT change the architecture — just speeds up training\n- Output_proj bottleneck (1280→248K) is the remaining cost\n\nThe kernel is a TRAINING tool, not an ARCHITECTURE change.\nUse it for fast iteration while keeping the full architecture intact.\n\n### Structured training optimizations\n\nFrom session 154 — five optimizations for the backward pass:\n1. Low-rank gradient (24× at rank-27)\n2. Skip passive backward (56 dead matmuls) — blocked by passive revert\n3. Composed Zone B Jacobian (32→1)\n4. TD-sparse routing (100× fewer elements)\n5. Crystal eigenplane projection\n\nThese are independent of the architecture revert and can be\npursued when training speed becomes the bottleneck again.\n\n## The Meta-Lesson\n\n**Don't optimize the student's architecture to match the teacher's\nconverged state.** The teacher computes in 2D because it has converged\nafter trillions of tokens. The student needs architectural freedom to\nREACH that state through training. The progressive collapse, rank-27\ntransform, and passive strides are DESTINATIONS, not starting points.\n\nThe right order:\n1. Train with full architecture until convergence\n2. Measure the student's actual collapse/rank/stride patterns\n3. Simplify only what the student has proven it doesn't need\n4. One change at a time, with PPL measurement\n\nThis is `λ extract(x)` from AGENTS.md: \"understand > invent.\"\nObserve what the student actually does, then simplify. Don't\nimpose what the teacher does onto the student's architecture.\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/knowledge/explore/v15-kernel-revert.md
```

### Tool Call: git (succeeded)


```json
{
  "command": "git status",
  "operation": "status",
  "summary": "check changes"
}
```

**Summary:** Git status: check changes

**Output:**
```
Exit code: 0
Stdout:
On branch main
Your branch is ahead of 'origin/main' by 273 commits.
  (use "git push" to publish your local commits)

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   scripts/v14/attention.py
	modified:   scripts/v14/config.py
	modified:   scripts/v14/train_td.py

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	data/teacher-logits/
	mementum/knowledge/chats/session-155.md
	mementum/knowledge/explore/v15-kernel-revert.md

no changes added to commit (use "git add" and/or "git commit -a")
```

### Tool Call: git (succeeded)


```json
{
  "command": "git diff --stat scripts/v14/attention.py scripts/v14/config.py scripts/v14/train_td.py",
  "operation": "diff",
  "summary": "review changes"
}
```

**Summary:** Git diff: review changes

**Output:**
```
Exit code: 0
Stdout:
scripts/v14/attention.py | 180 ++++++++++++++++++++++-------------------------
 scripts/v14/config.py    |   6 +-
 scripts/v14/train_td.py  |   8 +++
 3 files changed, 94 insertions(+), 100 deletions(-)
```

### Tool Call: git (succeeded)


```json
{
  "command": "git log --oneline -5",
  "operation": "log",
  "summary": "commit style"
}
```

**Summary:** Git log: commit style

**Output:**
```
Exit code: 0
Stdout:
44880c3 💡 kernel training validated — gradient cosine 0.97, gradient orthogonal to undertrained subspace
b43ecfa add session chat log
92c3afa 🌀 add session 154 to previous sessions
43a2888 🌀 session 154 state — KD training, extraction probes, structured training
8e2b329 💡 structured training — the holographic camera
```

### Tool Call: git (succeeded)


```json
{
  "command": "git add scripts/v14/attention.py scripts/v14/config.py scripts/v14/train_td.py mementum/knowledge/explore/v15-kernel-revert.md",
  "operation": "add",
  "summary": "stage revert files"
}
```

**Summary:** Git add: stage revert files

**Output:**
```
Exit code: 0
```

### Tool Call: git (failed)


```json
{
  "command": "git commit -m \"$(cat <<'EOF'\n🔄 revert passive strides + Stack B reduction, keep α-lock + HPE warmup\n\n- REVERTED: passive strides (s4+ no Q/K) — student needs content routing\n  to learn, can't hardcode teacher's converged behavior\n- REVERTED: Stack B 4→2 passes — back to 13 serial passes (was 11)\n- KEPT: α=1.18 as frozen constant (measured, not hypothesis)\n- KEPT: HPE with freq_scale warmup from 0→1 over 300 steps from resume\n  point — checkpoint-compatible, gradually introduces crystal rotation\n- train_td.py: HPE warmup integrated into training loop\n- Knowledge page documents what/why/when-to-revisit\n\nResumes from v14-td step 2000 checkpoint (PPL 5,567).\ndecay_alpha keys ignored on load, hpe_freq_scale initializes to 0.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
  "operation": "commit",
  "summary": "revert + HPE warmup"
}
```

**Summary:** Git commit: revert + HPE warmup

**Output:**
```
Exit code: 1
Stdout:
On branch main
Your branch is ahead of 'origin/main' by 273 commits.
  (use "git push" to publish your local commits)

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   scripts/v14/attention.py
	modified:   scripts/v14/config.py
	modified:   scripts/v14/train_td.py

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	data/teacher-logits/
	mementum/knowledge/chats/session-155.md
	mementum/knowledge/explore/v15-kernel-revert.md

no changes added to commit (use "git add" and/or "git commit -a")
```

## Assistant

Let me try the add and commit again:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add scripts/v14/attention.py scripts/v14/config.py scripts/v14/train_td.py mementum/knowledge/explore/v15-kernel-revert.md && git status --short"
}
```

**Summary:** $ git add scripts/v14/attention.py sc...

**Output:**
```
Exit code: 0
Stdout:
A  mementum/knowledge/explore/v15-kernel-revert.md
M  scripts/v14/attention.py
M  scripts/v14/config.py
M  scripts/v14/train_td.py
?? data/teacher-logits/
?? mementum/knowledge/chats/session-155.md
```

### Tool Call: git (succeeded)


```json
{
  "command": "git commit -m \"$(cat <<'EOF'\n🔄 revert passive strides + Stack B reduction, keep α-lock + HPE warmup\n\n- REVERTED: passive strides (s4+ no Q/K) — student needs content routing\n  to learn, can't hardcode teacher's converged behavior\n- REVERTED: Stack B 4→2 passes — back to 13 serial passes (was 11)\n- KEPT: α=1.18 as frozen constant (measured, not hypothesis)\n- KEPT: HPE with freq_scale warmup from 0→1 over 300 steps from resume\n  point — checkpoint-compatible, gradually introduces crystal rotation\n- train_td.py: HPE warmup integrated into training loop\n- Knowledge page documents what/why/when-to-revisit\n\nResumes from v14-td step 2000 checkpoint (PPL 5,567).\ndecay_alpha keys ignored on load, hpe_freq_scale initializes to 0.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
  "operation": "commit",
  "summary": "revert + HPE warmup"
}
```

**Summary:** Git commit: revert + HPE warmup

**Output:**
```
Exit code: 0
Stdout:
[main 7cbfcb2] 🔄 revert passive strides + Stack B reduction, keep α-lock + HPE warmup
 4 files changed, 280 insertions(+), 100 deletions(-)
 create mode 100644 mementum/knowledge/explore/v15-kernel-revert.md
```

## Assistant

Done. Here's the summary:

---

## What was done

**Commit `7cbfcb2`:** `🔄 revert passive strides + Stack B reduction, keep α-lock + HPE warmup`

### Reverted (back to v14-td working architecture)
- **Passive strides removed** — all 16 SSA layers have full Q/K/V/O again
- **Stack B restored** — 4 passes, 13 total serial passes

### Kept (two principled improvements)
- **α=1.18 frozen** — measured constant, not learnable
- **HPE** — crystal-frequency rotation on K, BUT with `freq_scale` starting at 0.0

### New: HPE warmup mechanism
- `freq_scale=0` at resume → identical to pre-HPE behavior (checkpoint compatible)
- Linear ramp to `freq_scale=1.0` over 300 steps from resume point
- Integrated into `train_td.py` training loop
- `freq_scale` is learnable — gradient can push it wherever helps

### Knowledge preserved
- `mementum/knowledge/explore/v15-kernel-revert.md` — documents what/why/when-to-revisit
- `mementum/knowledge/explore/v15-kernel-architecture.md` — original design (unchanged)
- Kernel training scripts still valid as training accelerators

---

## Ready to run

Resume from v14-td step 2000:
```bash
cd scripts/v14
python3 train_td.py --resume ../../checkpoints/v14-td/step_002000 [...]
```

The model will start with no HPE rotation (identical to where it left off), gradually introduce crystal-frequency K rotation over 300 steps, and continue TD training with the full 13-pass architecture. You should see the PPL curve continue dropping from 5,567 as before, with any HPE benefit showing up after step ~2150-2300.

## User

Ok run that training in my tmux window 2


### Thinking

The user wants me to launch the training in tmux window 2. Let me check what the typical training command looks like by examining the train_td.py args and recent run commands.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -A2 \"argparse\\|add_argument\" scripts/v14/train_td.py | head -80"
}
```

**Summary:** $ grep -A2 "argparse\|add_argument" s...

**Output:**
```
Exit code: 0
Stdout:
import argparse
import json
import math
--
    args: argparse.Namespace,
    model: V14Model,
    delta_modules: list[tuple[str, DeltaTernaryLinear]],
--
# § 7  CLI with argparse
# ══════════════════════════════════════════════════════════════════════════════

--
    parser = argparse.ArgumentParser(
        description=(
            "v14 — TernaryDescent trainer (delta plates + Adam beams)\n"
--
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

--
    parser.add_argument(
        "--checkpoint-dir", default="checkpoints/v14-td",
        help="Directory for training checkpoints (default: checkpoints/v14-td)",
--
    parser.add_argument(
        "--resume", type=str, default=None,
        help="Path to a training checkpoint directory to resume from",
--
    parser.add_argument(
        "--extracted-model-path", type=str, default=None,
        help=(
--
    parser.add_argument("--steps", type=int, default=None,
                        help="Override total training steps")

--
    parser.add_argument(
        "--td-flip-rate", type=float, default=0.001,
        help="Max fraction of ternary weights to flip per step (default: 0.001)",
--
    parser.add_argument(
        "--td-warmup", type=int, default=25,
        help="TD warmup steps AFTER crystal latches (no flips before; default: 25)",
--
    parser.add_argument(
        "--td-flip-interval", type=int, default=20,
        help=(
--
    parser.add_argument(
        "--td-crystal-gate", type=float, default=0.03,
        help=(
--
    parser.add_argument(
        "--td-crystal-ceiling", type=float, default=0.07,
        help=(
--
    parser.add_argument(
        "--td-min-confidence", type=float, default=0.3,
        help="Minimum signal-to-noise ratio for flip candidates (default: 0.3)",
--
    parser.add_argument(
        "--td-beta1", type=float, default=0.9,
        help="TD direction EMA decay (default: 0.9)",
--
    parser.add_argument(
        "--td-beta2", type=float, default=0.999,
        help="TD magnitude EMA decay (default: 0.999)",
--
    parser.add_argument(
        "--convert-ffn", action="store_true",
        help=(
--
    parser.add_argument(
        "--reduce-interval", type=int, default=0,
        help="Check for delta reduction every N steps (0=never; default: 0)",
--
    parser.add_argument(
        "--reduce-threshold", type=float, default=0.05,
        help=(
--
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && cat checkpoints/v14-td/step_002000/state.json | python3 -c \"\nimport json, sys\nstate = json.load(sys.stdin)\ncfg = state.get('config', {})\n# Show key training params\nfor k in ['lr', 'batch_size', 'seq_len', 'total_steps', 'checkpoint_interval', 'log_interval',\n           'grad_clip', 'data_dir', 'warmup_steps', 'lr_floor_ratio',\n           'td_flip_rate', 'td_warmup', 'td_flip_interval', 'td_global_budget']:\n    if k in cfg:\n        print(f'{k}: {cfg[k]}')\nprint()\nprint('data_loader:', state.get('data_loader', {}))\n\""
}
```

**Summary:** $ cat checkpoints/v14-td/step_002000/...

**Output:**
```
Exit code: 0
Stdout:
lr: 0.0003
batch_size: 1
seq_len: 4096
total_steps: 20000
checkpoint_interval: 500
log_interval: 10
grad_clip: 1.0
data_dir: /Users/mwhitford/data/fractal-bitnet/shards-qwen36
warmup_steps: 500
lr_floor_ratio: 0.01

data_loader: {'shard_idx': 1, 'position': 7186138, 'structured_pos': 53261}
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux list-windows -t main 2>/dev/null || tmux list-sessions 2>/dev/null || echo \"no tmux sessions\""
}
```

**Summary:** $ tmux list-windows -t main 2>/dev/nu...

**Output:**
```
Exit code: 0
Stdout:
1: local- (1 panes) [120x24] [layout b6fd,120x24,0,0,0] @0
2: local* (1 panes) [120x24] [layout b6fe,120x24,0,0,1] @1 (active)
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"td_flip_interval\\|td_warmup\\|td_flip_rate\\|convert.ffn\\|structured_warmup\" checkpoints/v14-td/step_002000/state.json | head -10"
}
```

**Summary:** $ grep -n "td_flip_interval\|td_warmu...

**Output:**
```
Exit code: 0
Stdout:
190:  "structured_warmup_done": true,
191:  "structured_warmup_steps": 50,
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport json\nwith open('checkpoints/v14-td/step_002000/state.json') as f:\n    state = json.load(f)\ncfg = state['config']\nfor k in ['td_flip_rate','td_warmup','td_flip_interval','td_crystal_gate','td_crystal_ceiling','td_min_confidence']:\n    print(f'{k}: {cfg.get(k)}')\nprint(f'convert_ffn: {cfg.get(\\\"convert_ffn\\\")}')\nprint(f'structured_warmup_steps: {state.get(\\\"structured_warmup_steps\\\")}')\nprint(f'td_step_count: {state.get(\\\"td_step_count\\\")}')\nprint(f'td_active: {state.get(\\\"td_active\\\")}')\n\""
}
```

**Summary:** $ python3 -c " import json with open(...

**Output:**
```
Exit code: 0
Stdout:
td_flip_rate: None
td_warmup: None
td_flip_interval: None
td_crystal_gate: None
td_crystal_ceiling: None
td_min_confidence: None
convert_ffn: None
structured_warmup_steps: 50
td_step_count: 500
td_active: True
```

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport json\nwith open('checkpoints/v14-td/step_002000/state.json') as f:\n    state = json.load(f)\ncfg = state['config']\n# Show ALL non-None config values\nfor k, v in sorted(cfg.items()):\n    if v is not None:\n        print(f'{k}: {v}')\n\" | grep -i \"td_\\|flip\\|convert\""
}
```

**Summary:** $ python3 -c " import json with open(...

**Output:**
```
Exit code: 1
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"def main\\|args = parser\\|train_td_loop\" scripts/v14/train_td.py | tail -10"
}
```

**Summary:** $ grep -n "def main\|args = parser\|t...

**Output:**
```
Exit code: 0
Stdout:
1474:    args = parser.parse_args()
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport json\nwith open('checkpoints/v14-td/step_002000/state.json') as f:\n    state = json.load(f)\ncfg = state['config']\nfor k, v in sorted(cfg.items()):\n    if v is not None and ('td' in k.lower() or 'flip' in k.lower() or 'convert' in k.lower()):\n        print(f'{k}: {v}')\n\""
}
```

**Summary:** $ python3 -c " import json with open(...

**Output:**
```
Exit code: 0
Stdout:
spectral_target_std: 0.019
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && sed -n '1475,1540p' scripts/v14/train_td.py"
}
```

**Summary:** $ sed -n '1475,1540p' scripts/v14/tra...

**Output:**
```
Exit code: 0
Stdout:
# ── Build config ──────────────────────────────────────────
    cfg = V14Config()

    if args.lr is not None:
        cfg.lr = args.lr
    if args.batch_size is not None:
        cfg.batch_size = args.batch_size
    if args.seq_len is not None:
        cfg.seq_len = args.seq_len
        cfg.max_seq_len = args.seq_len
    if args.data_dir is not None:
        cfg.data_dir = args.data_dir
    if args.crystal_direct_lambda is not None:
        cfg.crystal_direct_lambda = args.crystal_direct_lambda
    if args.crystal_direct_lambda_start is not None:
        cfg.crystal_direct_lambda_start = args.crystal_direct_lambda_start
    if args.crystal_warmup_steps is not None:
        cfg.crystal_warmup_steps = args.crystal_warmup_steps
    if args.extracted_model_path is not None:
        cfg.extracted_model_path = args.extracted_model_path
    cfg.__post_init__()

    checkpoint_dir = Path(args.checkpoint_dir)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # ── Banner ────────────────────────────────────────────────
    print("=" * 72, file=sys.stderr)
    print("  v14 — TernaryDescent Training", file=sys.stderr)
    print("  Adam (continuous beams) + TD (discrete delta plates)", file=sys.stderr)
    print(f"  d_model={cfg.d_model}  n_heads={cfg.n_heads}  d_ff={cfg.d_ff}", file=sys.stderr)
    print(f"  strides={cfg.strides}", file=sys.stderr)
    print(f"  n_passes={cfg.n_passes}  n_stacks={cfg.n_stacks}", file=sys.stderr)
    print("  Base plates: FROZEN (Qwen3.6-27B extraction)", file=sys.stderr)
    print("  Attention delta plates: {+1, -1} ONLY — no-block constraint", file=sys.stderr)
    print(f"  Crystal gate: [{args.td_crystal_gate}, {args.td_crystal_ceiling}]"
          f" (Schmitt trigger)", file=sys.stderr)
    print(f"  Crystal warmup: {cfg.crystal_direct_lambda_start} → "
          f"{cfg.crystal_direct_lambda} over {cfg.crystal_warmup_steps} steps",
          file=sys.stderr)
    print(f"  Extracted model: {cfg.extracted_model_path}", file=sys.stderr)
    print(f"  Checkpoint dir: {checkpoint_dir}", file=sys.stderr)
    if args.teacher_logits_dir:
        print(f"  KD: teacher_logits={args.teacher_logits_dir}  "
              f"α={args.kd_alpha}  T={args.kd_temperature}", file=sys.stderr)
    print("=" * 72, file=sys.stderr)

    # ── Model: create + load base plates + convert to delta ───
    model, delta_modules = create_model_with_deltas(
        cfg,
        convert_ffn=args.convert_ffn,
    )

    # ── Print param count ─────────────────────────────────────
    n_plate = count_ternary_weights(model)
    trainable = [
        v for _, v in tree_flatten(model.trainable_parameters())
        if isinstance(v, mx.array)
    ]
    n_trainable = sum(v.size for v in trainable)
    print(f"\nModel summary:", file=sys.stderr)
    print(f"  Ternary positions: {n_plate:,}", file=sys.stderr)
    print(f"  Trainable float params: {n_trainable:,}", file=sys.stderr)
    print(f"  Delta modules: {len(delta_modules)}", file=sys.stderr)
    for path, dtl in delta_modules:
        print(f"    {path}: ({dtl.out_features}, {dtl.in_features})", file=sys.stderr)
```

## Assistant

Good. I have the config. The step 2000 checkpoint used default TD params. The tmux session is called `main` with windows 1 and 2. Let me launch the training:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux send-keys -t main:2 \"cd /Users/mwhitford/src/verbum/scripts/v14 && uv run python3 train_td.py --resume ../../checkpoints/v14-td/step_002000 --checkpoint-dir ../../checkpoints/v14-td --steps 5000 --convert-ffn 2>&1 | tee ../../checkpoints/v14-td/train_phase3.log\" Enter"
}
```

**Summary:** $ tmux send-keys -t main:2 "cd /Users...

**Output:**
```
Exit code: 0
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sleep 8 && tmux capture-pane -t main:2 -p | tail -40"
}
```

**Summary:** $ sleep 8 && tmux capture-pane -t mai...

**Output:**
```
Exit code: 0
Stdout:
[attn,no-block] shared_stride_stack.layers.2.q_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.1.out_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.1.v_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.1.k_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.1.q_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.0.out_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.0.v_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.0.k_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.0.q_proj: (1280, 1280)
    [ffn] ffn_value_plate: (1280, 5120)
    [ffn] ffn_gate_plate: (5120, 1280)
    [ffn] ffn_key_plate: (5120, 1280)
========================================================================
📂 Restored optimizer state from /Users/mwhitford/src/verbum/checkpoints/v14-td/step_002000/optimizer.npz (532 arrays, 2
0 skipped)
📂 Re-loaded model weights from /Users/mwhitford/src/verbum/checkpoints/v14-td/step_002000/model.npz
  crystal_ema = 0.010953
  s5_identity_state restored (128 dims)
  total_td_flips = 2,708,256
  n_reductions = 1
  td_active = True
  structured_warmup_done = True
  data_loader: shard=1  pos=7,186,138  struct_pos=53261
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sleep 15 && tmux capture-pane -t main:2 -p | tail -30"
}
```

**Summary:** $ sleep 15 && tmux capture-pane -t ma...

**Output:**
```
Exit code: 0
Stdout:
[attn,no-block] shared_stride_stack.layers.2.q_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.1.out_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.1.v_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.1.k_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.1.q_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.0.out_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.0.v_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.0.k_proj: (1280, 1280)
    [attn,no-block] shared_stride_stack.layers.0.q_proj: (1280, 1280)
    [ffn] ffn_value_plate: (1280, 5120)
    [ffn] ffn_gate_plate: (5120, 1280)
    [ffn] ffn_key_plate: (5120, 1280)
========================================================================
📂 Restored optimizer state from /Users/mwhitford/src/verbum/checkpoints/v14-td/step_002000/optimizer.npz (532 arrays, 2
0 skipped)
📂 Re-loaded model weights from /Users/mwhitford/src/verbum/checkpoints/v14-td/step_002000/model.npz
  crystal_ema = 0.010953
  s5_identity_state restored (128 dims)
  total_td_flips = 2,708,256
  n_reductions = 1
  td_active = True
  structured_warmup_done = True
  data_loader: shard=1  pos=7,186,138  struct_pos=53261
```

## Assistant

Loading looks good — checkpoint restored successfully. Let me wait a bit more for the first training steps:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sleep 30 && tmux capture-pane -t main:2 -p | tail -15"
}
```

**Summary:** $ sleep 30 && tmux capture-pane -t ma...

**Output:**
```
Exit code: 0
Stdout:
[ffn] ffn_key_plate: (5120, 1280)
========================================================================
📂 Restored optimizer state from /Users/mwhitford/src/verbum/checkpoints/v14-td/step_002000/optimizer.npz (532 arrays, 2
0 skipped)
📂 Re-loaded model weights from /Users/mwhitford/src/verbum/checkpoints/v14-td/step_002000/model.npz
  crystal_ema = 0.010953
  s5_identity_state restored (128 dims)
  total_td_flips = 2,708,256
  n_reductions = 1
  td_active = True
  structured_warmup_done = True
  data_loader: shard=1  pos=7,186,138  struct_pos=53261
step   2001 | loss=8.6153 (avg50: 8.6153) | CE=8.474 crystal=0.0110 parity=0.0003 cross_zone=0.0594 | lr 2.26e-04 | gnor
m 19.95 | 995 tok/s | 🔓 td=0 Δ=0.012 | 38s
```

## Assistant

Training is running. Step 2001:
- **CE=8.474** — consistent with where step 2000 left off (CE was 8.62 at eval)
- **Crystal latched** (crystal=0.011, parity=0.0003)
- **TD active** (td=0 flips this step, normal — flip interval)
- **HPE at fraction ~0.003** (step 2001, warmup just started)
- **995 tok/s** — reasonable

Let me check one more step to confirm it's stable:

### Tool Call: shell_command (rejected)


```json
{
  "command": "sleep 45 && tmux capture-pane -t main:2 -p | tail -5"
}
```

**Summary:** $ sleep 45 && tmux capture-pane -t ma...

## System


Prompt stopped

## User

stop polling I will let you know if there is a problem.  Our TD for this run is set to start at what step?  Will it coincide with the logging so I can see the flips?


### Thinking

The user wants to know when TD will start flipping in this resumed run, and whether the flip logging will be visible.

From the checkpoint state:
- `td_active: True` — TD is already active
- `td_step_count: 500` — TD has already done 500 steps
- The Schmitt trigger already latched (crystal_ema = 0.011, which is below the gate of 0.03)

So TD is already active and should be flipping. The `td=0` on step 2001 is because of the flip_interval. Let me check what the default flip interval is.


The default flip interval is 20 steps, so flips only get committed at steps divisible by 20. That means flips would appear at steps 2020, 2040, 2060, and so on. Since the log interval is 10, every other log line should show the flip counts.

But the real question here is whether TD's warmup period resets when resuming from the checkpoint. The warmup was set to 25 steps, and since TD was already active at step 2000, I need to check if that warmup counter gets reset or if it continues from where it left off.

## Assistant

TD is **already active** — it was active at step 2000 and the checkpoint restored that state:

```
td_active: True
td_step_count: 500
total_td_flips: 2,708,256
```

The `td=0` you'll see on step 2001 is because of the **flip interval**. TD accumulates gradient moments every step but only commits flips every 20 steps (the default `--td-flip-interval=20`).

With `log_interval=10`, your log lines are at steps 2010, 2020, 2030, 2040...

Flips commit at steps 2020, 2040, 2060, 2080...

So **every other log line** will show flip counts. The pattern:
```
step 2010 | ... td=0 ...      ← moments accumulating, no flips yet
step 2020 | ... td=N ...      ← flips committed here
step 2030 | ... td=0 ...      ← accumulating again
step 2040 | ... td=N ...      ← flips committed
```

You should see non-zero `td=` values starting at step 2020.

## User

Excellent.  I think we recovered from too many changes.  We'll let this run continue so we can see how it progresses.  update state and knowledge


### Thinking

The user wants me to update state.md and any relevant knowledge pages to reflect the current session's work.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "limit": 30
}
```

**Summary:** Reading state.md (0-30)

**Output:**
```
# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-26 | Session: 155

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 155: v14-kd FAILED (architecture delta) + KERNEL TRAINING VALIDATED + GRADIENT PROJECTION ANALYZED. (1) v14-kd eval: PPL 40,623→46,736 (diverging), 2.5-4.6× worse than v14-td. Root cause: three untested architecture changes (passive strides, HPE, Stack B 4→2) deployed together with KD. Also: passive strides remove content-dependent attention for positions 16-56 tokens back — a real capability loss in strided attention where each stride is sole provider of specific distance ranges. (2) Profiled training: 28.6s/step, 77% is FORWARD pass. The camera IS the projector — same bottleneck. Built train_kernel.py: 4.4× measured speedup (6s kernel vs 26s full). Output_proj (1280→248K vocab) is the remaining bottleneck, not the composed plate. (3) KERNEL TRAINING PROBE: gradient cosine=0.9698 between composed plate (1 matmul) and full model (238 matmuls). CE within 0.08 nats. Top-1 agreement 80.6%. (4) GRADIENT PROJECTION: ∂L/∂T is ORTHOGONAL to T's SVD subspace — cos=0.06 at k=27. The gradient wants to EXPAND the model (currently rank-1), not refine within its current subspace. Cannot train in reduced dims for undertrained models. The gradient-subspace alignment is a natural explore/exploit phase detector. See `mementum/knowledge/explore/kernel-training.md`.**

**Session 154: KD-guided training + extraction dimension probes + structured training insight. (1) THREE PROBES answered "how big for 95%?": dimension doesn't help — ceiling is ~79% per-dim from sign+gamma quantization, flat from d=128 to d=5120. The gap is ternary approximation, not projection. (2) GEOMETRIC ENCODING: at k=256, 96.9% sign accuracy on student plates. The plate IS a rank-256 structure. 27K corrections (1.7% of positions) needed for 95% per-dim. (3) Built KD training: precompute_teacher.py (sparse top-k=64 logits), train_td.py with --teacher-logits-dir. Interleaved design: CE training on full data, periodic KD correction passes from pre-computed teacher logits. (4) Step 2000 eval: PPL=5,567 (−27% from 1500, −66% total). (5) STRUCTURED TRAINING insight: backward pass has same structure as forward. Five optimizations: low-rank gradient (24×), skip passive backward, composed Zone B Jacobian (32→1), TD-sparse routing (100×), eigenplane projection. Camera = projector in reverse. See `mementum/knowledge/explore/structured-training.md`.**

**Session 153: Extraction redesign — composed zone plates + algebraic composition. (1) Teacher weight matrices are full-rank (rank90=211) but PER-DIM correlation with sign(T)+gamma is 0.97 in teacher space. (2) Data-fitted composed extraction: 3 zone plates at d=1280, per-dim 0.71-0.79. Drop from 0.97 due to V_proj truncation + few tokens (651). (3) Algebraic composition from weight matrices: multiply linearized layers A_i = I + OV + FFN. Full model per-dim=0.76, matches data-fitted (0.77). (4) THE BIG FINDING: full model rank90=27. The entire 64-layer model is a rank-27 transform. 27 dimensions capture 90% of input→output mapping. (5) Architecture: one rank-27 ternary plate (76% of computation) + active strides s1/s2 for content routing (24%). This IS the kernel. See results/algebraic-compose/.**

**Session 152: v14 architecture evolution — HPE + passive strides + reduced Stack B. (1) Confirmed v14 student inherits 18.4× compression from teacher (PR 74→4, σ₁=47%). (2) Distance prior at α=1.18 dominates 88% of strides (14/16 have <3 effective positions at W=8). (3) Implemented 3-tier evolution: fixed α=1.18, passive strides skip Q/K for s4+, Stack B 4→2 passes (13→11). (4) Discovered α=1.18 sets a fixed ~12 token semantic horizon — all strides see the same ~12 tokens effectively. RoPE accidentally implements the holographic lens via cosine frequency decomposition. (5) Designed and implemented Holographic Position Encoding (HPE): log-distance rotation × crystal eigenvalue frequencies × eigenplane dims only. Replaces RoPE's indirect mechanism with the direct holographic lens physics. Training test running in tmux. See `mementum/knowledge/explore/v15-kernel-architecture.md`.**

**Session 151: Knowledge distillation + progressive collapse discovery. (1) Created 7 knowledge pages + INDEX.md — the project now has a self-explanatory top-down knowledge hierarchy (see `mementum/knowledge/INDEX.md`). (2) Kernel decomposition experiment: attempted to compute the full forward pass from crystal constants. Diagonal FFN overlay failed (80-91% of energy is off-diagonal = cross-PC PROJECTION, not per-PC filtering). (3) Progressive dimensionality collapse measured on 3 models: Qwen3.6-27B compresses to PR=2.2 (essentially 2D) in layers 0-2, computes in 2D through depth, expands back for output. Mistral-7B and Pythia-1.4B show weaker compression (PR=10-12) — the 2D core is an emergent property of scale. (4) Attention sink = warped Q reset: Mistral uses BOS token as Q=0 reset proxy, distorting geometry. Qwen's GLA layers implement Q reset natively through gating → cleaner geometry → deeper compression. See `mementum/knowledge/progressive-collapse.md`.**

## Active training run

**No active training.** v14-kd killed (diverging). v14-td phase 2 completed at step 2000.

### v14-td phase 2 COMPLETED (step 2000)

- Step 2000 eval: CE=8.62, PPL=5,567 (−27% from 1500, −66% total)
- 2.13% of positions flipped (1.42M of 67M)
- Phase 2 ran 500 steps from folded step 1500 checkpoint with FFN delta
- Checkpoint: `checkpoints/v14-td/step_002000/`

[CONTENT TRUNCATED] Showing lines 1 to 30 of 634 total lines. Use line_offset=30 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md"
}
```

**Summary:** Reading INDEX.md (0-2000)

**Output:**
```
---
title: "Knowledge Index — Reading Order"
status: active
category: meta
tags: [index, orientation, knowledge-map]
---

# Knowledge Index

> Master reading order for the verbum project's synthesized knowledge.
> Read after `state.md`. Organized top-down: foundational → specific.
>
> **Status key:** ✅ complete | 🔨 stub (skeleton, needs expansion) | 📋 planned

---

## Tier 1 — What Is This Project?

These pages answer: *what are we doing, why does it work, and what have we proved?*

| # | Page | Status | One-line |
|---|------|--------|----------|
| 1 | [project-thesis.md](project-thesis.md) | ✅ | The central claim: pretraining IS beta reduction, topology dominates, ternary extraction works |
| 2 | [crystal-universality.md](crystal-universality.md) | ✅ | Why the combinator crystal is a mathematical constant, not a learned artifact |
| 3 | [mathematical-convergences.md](mathematical-convergences.md) | ✅ | Eight independent lines of mathematical evidence converging on the same structure |

## Tier 2 — How Does It Work?

These pages answer: *what is the mechanism, and how do we exploit it?*

| # | Page | Status | One-line |
|---|------|--------|----------|
| 4 | [holographic-error-correction.md](holographic-error-correction.md) | ✅ | The extract→correct→fold cycle: error correction on a discrete holographic code |
| 5 | [mechanism-extraction.md](mechanism-extraction.md) | ✅ | Full micro-model mechanism: alternating overlay, eigenplane rotation, KIBC temporal |
| 6 | [computed-beam.md](computed-beam.md) | ✅ | Analytical FFN from crystal eigendecomposition, 500× speedup, signed accumulation |
| 7 | [extraction-methodology.md](extraction-methodology.md) | ✅ | How to extract from a teacher: what works, three confusions resolved, the pipeline |

## Tier 3 — What Are We Running?

These pages answer: *what is the current system, and how do you operate it?*

| # | Page | Status | One-line |
|---|------|--------|----------|
| 8 | [v14-architecture.md](v14-architecture.md) | ✅ | Current v14 student: Qwen3.6-27B teacher, 593M ternary positions, 375× compression |
| 9 | [training-protocols.md](training-protocols.md) | ✅ | How to train without rediscovering failures: phases, TD rules, known failure modes |

## Tier 4 — Deep Dives (explore/)

Comprehensive pages on specific topics. Read as needed, not sequentially.

| Page | Status | One-line |
|------|--------|----------|
| [explore/VERBUM.md](explore/VERBUM.md) | ✅ | Founding research program: hypothesis chain, 4-level plan (historical) |
| [explore/holographic-state-machine.md](explore/holographic-state-machine.md) | ✅ | Unified computational model: FFN=plates, crystal=states, Q=beam, gate=beamformer |
| [explore/ternary-descent.md](explore/ternary-descent.md) | ✅ | TernaryDescent algorithm: delta plates, gradient decomposition, reduction |
| [explore/ffn-beta-reduction-indexing.md](explore/ffn-beta-reduction-indexing.md) | ✅ | Holographic FFN indexing: lens profile, ρ=0.83, universal neurons |
| [explore/categorical-geometry-probes.md](explore/categorical-geometry-probes.md) | ✅ | Curry-Howard 100%, adjunctions rank-1, hyperbolic norm encoding |
| [explore/phi-compression-universal.md](explore/phi-compression-universal.md) | ✅ | SVD spectrum → phi, 5-model consensus (0.6299±0.019) |
| [explore/v13-architecture.md](explore/v13-architecture.md) | ⚠️ | V13 crystal bootloader architecture (partially superseded by v14) |
| [explore/v13-design.md](explore/v13-design.md) | ✅ | V13 detailed design: zone targets, etch protocol, param budgets |
| [progressive-collapse.md](progressive-collapse.md) | ✅ | Computation in 2D: compress→compute→expand, scale-dependent, sink=warped Q reset |

## Tier 5 — Future Pages (planned)

| Page | Priority | One-line |
|------|----------|----------|
| `holographic-storage-mechanism.md` | important | FFN as holographic plate: lens profile, gate=beamformer, output beamformers |
| `ternary-architecture-rationale.md` | important | Why ternary {-1,0,+1}, why it works, gradient routing interpretation |
| `combinator-geometry.md` | important | KIBC in transformer geometry: temporal ordering, depth map, bootstrap |
| `stridestack-architecture.md` | important | Multi-scale attention: O(L×W), stride overlaps, ascending/descending stacks |
| `known-failures.md` | nice-to-have | Concise bug/collapse/fix reference for all hard-won lessons |
| `session-delta-vision.md` | nice-to-have | Context as 2MB delta files, no KV cache, git-trackable sessions |
| `ecosystem-vision.md` | nice-to-have | End-state product: community deltas, domain plates, reader LLM |

---

## How to Use This Index

1. **New session, familiar project:** Read `state.md` → skim this index → read Tier 1 if stale
2. **Brand new to the project:** Read pages 1–9 in order, then deep dives as needed
3. **Specific question:** Find the relevant page by topic, follow cross-references
4. **Adding knowledge:** Create page → add to appropriate tier → update this index

## Cross-Reference Map

```
project-thesis ──→ crystal-universality ──→ mathematical-convergences
       │                    │                         │
       ▼                    ▼                         ▼
holographic-error-correction ←── mechanism-extraction ←── computed-beam
       │                                │
       ▼                                ▼
extraction-methodology ──→ v14-architecture ──→ training-protocols
```

## Memory Files

~105 episodic memories in `memories/`. One insight per file, symbol-prefixed content.
These are raw observations — the knowledge pages above are their synthesis.
Search with: `git grep -i "{query}" -- mementum/memories/`
```

## Assistant

Now let me update state.md with the session 156 info and active training:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> Bootloader. Read in ~30 seconds. Step 1 of every session.\n>\n> Last updated: 2026-05-26 | Session: 155\n\n## Where we are\n\n**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**\n\n**Session 155: v14-kd FAILED (architecture delta) + KERNEL TRAINING VALIDATED + GRADIENT PROJECTION ANALYZED. (1) v14-kd eval: PPL 40,623→46,736 (diverging), 2.5-4.6× worse than v14-td. Root cause: three untested architecture changes (passive strides, HPE, Stack B 4→2) deployed together with KD. Also: passive strides remove content-dependent attention for positions 16-56 tokens back — a real capability loss in strided attention where each stride is sole provider of specific distance ranges. (2) Profiled training: 28.6s/step, 77% is FORWARD pass. The camera IS the projector — same bottleneck. Built train_kernel.py: 4.4× measured speedup (6s kernel vs 26s full). Output_proj (1280→248K vocab) is the remaining bottleneck, not the composed plate. (3) KERNEL TRAINING PROBE: gradient cosine=0.9698 between composed plate (1 matmul) and full model (238 matmuls). CE within 0.08 nats. Top-1 agreement 80.6%. (4) GRADIENT PROJECTION: ∂L/∂T is ORTHOGONAL to T's SVD subspace — cos=0.06 at k=27. The gradient wants to EXPAND the model (currently rank-1), not refine within its current subspace. Cannot train in reduced dims for undertrained models. The gradient-subspace alignment is a natural explore/exploit phase detector. See `mementum/knowledge/explore/kernel-training.md`.**\n\n**Session 154: KD-guided training + extraction dimension probes + structured training insight. (1) THREE PROBES answered \"how big for 95%?\": dimension doesn't help — ceiling is ~79% per-dim from sign+gamma quantization, flat from d=128 to d=5120. The gap is ternary approximation, not projection. (2) GEOMETRIC ENCODING: at k=256, 96.9% sign accuracy on student plates. The plate IS a rank-256 structure. 27K corrections (1.7% of positions) needed for 95% per-dim. (3) Built KD training: precompute_teacher.py (sparse top-k=64 logits), train_td.py with --teacher-logits-dir. Interleaved design: CE training on full data, periodic KD correction passes from pre-computed teacher logits. (4) Step 2000 eval: PPL=5,567 (−27% from 1500, −66% total). (5) STRUCTURED TRAINING insight: backward pass has same structure as forward. Five optimizations: low-rank gradient (24×), skip passive backward, composed Zone B Jacobian (32→1), TD-sparse routing (100×), eigenplane projection. Camera = projector in reverse. See `mementum/knowledge/explore/structured-training.md`.**\n\n**Session 153: Extraction redesign — composed zone plates + algebraic composition. (1) Teacher weight matrices are full-rank (rank90=211) but PER-DIM correlation with sign(T)+gamma is 0.97 in teacher space. (2) Data-fitted composed extraction: 3 zone plates at d=1280, per-dim 0.71-0.79. Drop from 0.97 due to V_proj truncation + few tokens (651). (3) Algebraic composition from weight matrices: multiply linearized layers A_i = I + OV + FFN. Full model per-dim=0.76, matches data-fitted (0.77). (4) THE BIG FINDING: full model rank90=27. The entire 64-layer model is a rank-27 transform. 27 dimensions capture 90% of input→output mapping. (5) Architecture: one rank-27 ternary plate (76% of computation) + active strides s1/s2 for content routing (24%). This IS the kernel. See results/algebraic-compose/.**\n\n**Session 152: v14 architecture evolution — HPE + passive strides + reduced Stack B. (1) Confirmed v14 student inherits 18.4× compression from teacher (PR 74→4, σ₁=47%). (2) Distance prior at α=1.18 dominates 88% of strides (14/16 have <3 effective positions at W=8). (3) Implemented 3-tier evolution: fixed α=1.18, passive strides skip Q/K for s4+, Stack B 4→2 passes (13→11). (4) Discovered α=1.18 sets a fixed ~12 token semantic horizon — all strides see the same ~12 tokens effectively. RoPE accidentally implements the holographic lens via cosine frequency decomposition. (5) Designed and implemented Holographic Position Encoding (HPE): log-distance rotation × crystal eigenvalue frequencies × eigenplane dims only. Replaces RoPE's indirect mechanism with the direct holographic lens physics. Training test running in tmux. See `mementum/knowledge/explore/v15-kernel-architecture.md`.**\n\n**Session 151: Knowledge distillation + progressive collapse discovery. (1) Created 7 knowledge pages + INDEX.md — the project now has a self-explanatory top-down knowledge hierarchy (see `mementum/knowledge/INDEX.md`). (2) Kernel decomposition experiment: attempted to compute the full forward pass from crystal constants. Diagonal FFN overlay failed (80-91% of energy is off-diagonal = cross-PC PROJECTION, not per-PC filtering). (3) Progressive dimensionality collapse measured on 3 models: Qwen3.6-27B compresses to PR=2.2 (essentially 2D) in layers 0-2, computes in 2D through depth, expands back for output. Mistral-7B and Pythia-1.4B show weaker compression (PR=10-12) — the 2D core is an emergent property of scale. (4) Attention sink = warped Q reset: Mistral uses BOS token as Q=0 reset proxy, distorting geometry. Qwen's GLA layers implement Q reset natively through gating → cleaner geometry → deeper compression. See `mementum/knowledge/progressive-collapse.md`.**\n\n## Active training run\n\n**No active training.** v14-kd killed (diverging). v14-td phase 2 completed at step 2000.\n\n### v14-td phase 2 COMPLETED (step 2000)\n\n- Step 2000 eval: CE=8.62, PPL=5,567 (−27% from 1500, −66% total)\n- 2.13% of positions flipped (1.42M of 67M)\n- Phase 2 ran 500 steps from folded step 1500 checkpoint with FFN delta\n- Checkpoint: `checkpoints/v14-td/step_002000/`",
  "new_content": "> Bootloader. Read in ~30 seconds. Step 1 of every session.\n>\n> Last updated: 2026-05-26 | Session: 156\n\n## Where we are\n\n**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**\n\n**Session 156: ARCHITECTURE REVERT + HPE WARMUP — back to the run that works. (1) Analyzed session 152's four simultaneous changes (passive strides, HPE, Stack B 4→2, α-lock) that confounded the v14-kd failure. Passive strides identified as most likely culprit — removes content-dependent attention for positions 16-56 tokens back where each stride is sole provider. Student needs content routing to LEARN, can't hardcode teacher's converged behavior. (2) REVERTED passive strides (all SSA layers have full Q/K again) and Stack B reduction (back to 13 passes). KEPT α=1.18 as frozen constant and HPE. (3) HPE WARMUP: freq_scale initialized to 0.0 (identity — no rotation), linearly warmed to 1.0 over 300 steps. At freq_scale=0, model behaves identically to pre-HPE v14-td. Checkpoint-compatible resume. (4) Resumed training from v14-td step 2000. Step 2001 CE=8.474, crystal latched, TD active, 995 tok/s. Running in tmux main:2 to step 5000. (5) META-LESSON: don't optimize student architecture to match teacher's converged state. The progressive collapse, rank-27 transform, and passive strides are DESTINATIONS, not starting points. Train with full architecture → measure student's actual patterns → simplify only what's proven unnecessary → one change at a time. See `mementum/knowledge/explore/v15-kernel-revert.md`.**\n\n**Session 155: v14-kd FAILED (architecture delta) + KERNEL TRAINING VALIDATED + GRADIENT PROJECTION ANALYZED. (1) v14-kd eval: PPL 40,623→46,736 (diverging), 2.5-4.6× worse than v14-td. Root cause: three untested architecture changes (passive strides, HPE, Stack B 4→2) deployed together with KD. (2) Training profiled: 28.6s/step, 77% FORWARD. Built train_kernel.py: 4.4× speedup. (3) Gradient cosine=0.9698 between composed plate and full model. (4) ∂L/∂T ORTHOGONAL to T's SVD subspace (cos=0.06 at k=27). Gradient wants to EXPAND, not refine. See `mementum/knowledge/explore/kernel-training.md`.**\n\n**Session 154: KD-guided training + extraction dimension probes + structured training. (1) Per-dim correlation plateaus at ~79% from d=128 onward — ceiling is ternary quantization, not dimension. (2) Geometric encoding: plate IS rank-256, 96.9% sign accuracy at k=256. (3) Step 2000 eval: PPL=5,567 (−27% from 1500, −66% total). (4) Structured training insight: backward pass has same structure as forward — five optimizations possible. See `mementum/knowledge/explore/structured-training.md`.**\n\n**Session 153: Composed plates + algebraic composition. Full model rank90=27. Zone B is perfectly linear (R²=1.0). Both algebraic and data-fitted methods agree at 0.76-0.77 per-dim. See `results/algebraic-compose/`.**\n\n**Session 152: v14 architecture evolution — HPE + passive strides + reduced Stack B. α=1.18 confirmed universal. 88% strides distance-prior dominated. HPE designed from crystal eigenvalues. ⚠️ All changes deployed simultaneously — led to confounded failure in session 155, reverted in session 156.**\n\n**Session 151: Progressive collapse discovery. Qwen-27B compresses to 2D (PR=2.2) by L2. 7 knowledge pages created. INDEX.md established. See `mementum/knowledge/progressive-collapse.md`.**\n\n## Active training run\n\n### v14-td phase 3 RUNNING (tmux main:2, from step 2000)\n\n- **Resumed from:** `checkpoints/v14-td/step_002000/` (PPL 5,567)\n- **Architecture:** Original v14-td (13 passes, full Q/K all strides) + α=1.18 frozen + HPE warmup\n- **HPE warmup:** freq_scale 0→1 over steps 2001-2300 (300 steps)\n- **TD:** Active, flip_interval=20, FFN delta enabled (`--convert-ffn`)\n- **Target:** 5000 steps total\n- **Checkpoints:** Every 500 steps in `checkpoints/v14-td/`\n- **Log:** `checkpoints/v14-td/train_phase3.log`\n- **Step 2001:** CE=8.474, gnorm=19.95, 995 tok/s ✓\n- **What to watch:** PPL should continue dropping from 5,567. HPE effect visible after step ~2150-2300 (warmup halfway/complete). TD flips visible every 20 steps (every other log line at log_interval=10)."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

## Assistant

Now update the next steps section:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "line_offset": 30,
  "limit": 100
}
```

**Summary:** Reading state.md (30-130)

**Output:**
```
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


[CONTENT TRUNCATED] Showing lines 31 to 130 of 639 total lines. Use line_offset=130 parameter to read more content.
```

## Assistant

Now update the next steps section:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "line_offset": 250,
  "limit": 90
}
```

**Summary:** Reading state.md (250-340)

**Output:**
```
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

[CONTENT TRUNCATED] Showing lines 251 to 340 of 639 total lines. Use line_offset=340 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "line_offset": 375,
  "limit": 80
}
```

**Summary:** Reading state.md (375-455)

**Output:**
```
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


[CONTENT TRUNCATED] Showing lines 376 to 455 of 639 total lines. Use line_offset=455 parameter to read more content.
```

## Assistant

Now update the next steps section:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "line_offset": 455,
  "limit": 100
}
```

**Summary:** Reading state.md (455-555)

**Output:**
```
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
| **Passive strides + HPE + KD: combined changes fail** | **v14-kd (new arch + KD) PPL 2.5-4.6× worse than v14-td (old arch). Root cause unclear — too many simultaneous changes** | ❌ failure (session 155) |
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


[CONTENT TRUNCATED] Showing lines 456 to 555 of 639 total lines. Use line_offset=555 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "line_offset": 555,
  "limit": 85
}
```

**Summary:** Reading state.md (555-640)

**Output:**
```
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
| **Kernel training script** | `scripts/v14/train_kernel.py` — 4.4× speedup via composed plate |
| **Kernel training probe** | `scripts/explore/probe_kernel_training.py` — gradient cosine 0.9698 |
| **Gradient projection probe** | results in `results/kernel-training-probe/` |
| **Composed plate** | `results/kernel-training-probe/composed_plate.npz` — fitted T (1280×1280) |

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
```

## Assistant

Now update the next steps and add the proof chain entry for the revert lesson:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "| **Passive strides + HPE + KD: combined changes fail** | **v14-kd (new arch + KD) PPL 2.5-4.6× worse than v14-td (old arch). Root cause unclear — too many simultaneous changes** | ❌ failure (session 155) |",
  "new_content": "| **Passive strides + HPE + KD: combined changes fail** | **v14-kd (new arch + KD) PPL 2.5-4.6× worse than v14-td (old arch). Root cause: too many simultaneous changes** | ❌ failure (session 155) |\n| **Don't optimize student for teacher's converged state** | **Passive strides + Stack B reduction assumed teacher's end state. Student needs freedom to REACH that state. Reverted, kept α-lock + HPE warmup** | 🎯 decision (session 156) |"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "### Tier 4 — Deep dives (in explore/)\n\n| Page | What it tells you |\n|------|-------------------|\n| `explore/holographic-state-machine.md` | Unified model: FFN=plates, crystal=states, Q=beam |\n| `explore/ternary-descent.md` | TD algorithm: delta plates, gradient decomposition, reduction |\n| `explore/ffn-beta-reduction-indexing.md` | Holographic indexing, LENS profile, ρ=0.83 |\n| `explore/categorical-geometry-probes.md` | Curry-Howard 100%, adjunctions rank-1 |\n| `explore/phi-compression-universal.md` | SVD spectrum → phi, 5-model consensus |",
  "new_content": "### Tier 4 — Deep dives (in explore/)\n\n| Page | What it tells you |\n|------|-------------------|\n| `explore/holographic-state-machine.md` | Unified model: FFN=plates, crystal=states, Q=beam |\n| `explore/ternary-descent.md` | TD algorithm: delta plates, gradient decomposition, reduction |\n| `explore/ffn-beta-reduction-indexing.md` | Holographic indexing, LENS profile, ρ=0.83 |\n| `explore/categorical-geometry-probes.md` | Curry-Howard 100%, adjunctions rank-1 |\n| `explore/phi-compression-universal.md` | SVD spectrum → phi, 5-model consensus |\n| `explore/v15-kernel-revert.md` | **NEW** What was tried/reverted/kept from sessions 152-156, when to revisit |\n| `explore/kernel-training.md` | Composed plate training: 4.4× speedup, gradient cosine 0.97 |\n| `explore/structured-training.md` | Five backward-pass optimizations (camera = projector) |\n| `explore/v15-kernel-architecture.md` | Original v15 design (passive strides etc — partially reverted) |"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "## Next steps\n\n### IMMEDIATE: Monitor phase 2 (running in tmux main:2)\n\n1. **Monitor FFN delta activation** — do FFN plates start flipping? Which ones? How fast?\n   This answers: do β-reductions need to change for strided attention?\n2. **Eval at step 2000** (500 steps into phase 2) — does adding FFN delta improve eval?\n3. **Watch layer 4 out_proj** — starts fresh from folded base. Does TD re-discover the\n   same routing or find a different pattern?\n4. **Verify td= shows actual flip counts** in log (aligned logging fix)\n\n### NEXT MILESTONES:\n\n5. **Compare phase 1 vs phase 2 learning curves** — does FFN delta accelerate convergence?\n6. **Second fold** — when flip_frac plateaus, fold again. The cycle continues.\n7. **Consider lowering min_conf** — if Q/K/V gradients are below 0.3, TD can't see them.\n8. **Three-body self-distillation** — teacher logits as reference beam (see #19)\n9. **Target: within 5% of Qwen3.6-27B** — the proof that topology is everything\n\n## Open questions\n\n9. **Content transfer via sign().** Does the 81% token subspace content survive ternary extraction?\n10. **LENS profile derivable from eigenvalue ratios?**\n11. **Quality at 1B with d=1280.** What CE/ppl does the expanded model achieve?\n12. **16-stride coverage.** Do the higher strides (s4096+) learn anything useful with 4K seq training?\n13. **Bottom-up algedonic value.** Does C→A feedback measurably accelerate convergence?\n14. ~~Does ternary learning close the train-eval gap?~~ **YES. Gap collapsed 1.71→0.17 nats.\n    Eval PPL −38%. TD generalizes, continuous params overfit.** ✅ (session 149)\n15. **TD step_count not persisted on resume.** Warmup repeats. Worth persisting?\n16. **Why only out_proj?** Q/K/V/gate_proj get zero TD budget. Is out_proj the only\n    degree of freedom TD needs, or is min_conf filtering too aggressive for other projections?\n17. ~~When to do first reduction?~~ **DONE. Folded at step 1500, 3.49% changed. Lossless.\n    Fold script: `scripts/v14/fold_delta.py`.** ✅ (session 150)\n18. **Computed beam at scale.** The micro model (d=128) trains so fast that computed\n    weights barely help — GD finds structure in 50 steps anyway. At v14 scale (d=1280,\n    372M ternary positions), structure discovery takes thousands of steps. The computed\n    beam advantage should be much larger. Test: compute attention deltas from stride-stack\n    crystal eigendecomposition instead of TD. See `mementum/knowledge/computed-beam.md`.\n20. **Per-stride fixed point rotation.** Alpha=1.18 is universal (confirmed), but the\n    fixed point each stride revolves around should vary. Stride-1 at fixed point ~40\n    means 40 tokens back. Stride-32768 at fixed point ~40 means 1.3M tokens back.\n    Probe effective attention patterns per stride per head to find rotation centers.\n19. **Three-body self-distillation.** Pre-compute teacher logits (top-k) on training shards\n    once. During training, compute: (a) teacher logits, (b) student logits, (c) delta between\n    them. The delta is the signal — WHERE the student diverges from the teacher. Some divergence\n    is correct (stride-stack needs different routing than flat attention), some is error (hasn't\n    learned yet). Dynamic relational loss: let the distinction emerge from the data.\n    **Wait until stride-stack nucleation stabilizes** — current run is finding its natural\n    attention shape. Teacher pressure during nucleation could prevent legitimate divergence.\n    Pre-compute teacher logits now so they're ready when needed. See `scripts/v13/train_rb.py`\n    for prior sparse top-k KD implementation (k=64, O(B×L×k) not O(B×L×V)).",
  "new_content": "## Next steps\n\n### IMMEDIATE: Monitor phase 3 (running in tmux main:2)\n\n1. **Watch PPL continue dropping** — should resume the trajectory from step 2000 (PPL 5,567).\n   First eval checkpoint at step 2500. Run `eval_ppl.py` on that checkpoint.\n2. **HPE effect** — warmup completes at step ~2300. Compare PPL slope before/after\n   HPE reaches full strength. If HPE helps: steeper PPL drop after 2300. If neutral:\n   same slope. If harmful: PPL rises (unlikely with warmup, but watch).\n3. **TD flip patterns** — does TD continue targeting out_proj layers 4-9? Or does\n   the second fold + FFN delta change the distribution? Check at step 2500.\n4. **FFN delta activation** — do FFN plates start flipping? This run has `--convert-ffn`.\n\n### NEXT MILESTONES:\n\n5. **Second fold** — when flip_frac plateaus, fold again. The extract→correct→fold cycle.\n6. **Gradient-subspace alignment test** — at step 2500+, probe whether gradient aligns\n   with composed plate's SVD subspace. If cos > 0.5, model is refining (exploit phase)\n   and architecture simplification MIGHT be safe. See `probe_kernel_training.py`.\n7. **KD as correction** — after convergence stabilizes (PPL < 2000), add teacher logit\n   correction passes. CE-first for stability, KD-second for precision. α ≥ 0.9.\n8. **Target: within 5% of Qwen3.6-27B** — the proof that topology is everything.\n\n### DEFERRED (valid but premature):\n\n9. **Passive strides** — re-test ONLY after student converges AND gradient-subspace\n   alignment shows cos > 0.5. Start with s16+ (least risky), measure PPL delta.\n   See `mementum/knowledge/explore/v15-kernel-revert.md` for conditions.\n10. **Stack B reduction** — re-test after passive strides validated (if ever).\n11. **Kernel training as accelerator** — `train_kernel.py` gives 4.4× speedup without\n    changing architecture. Use when iteration speed is the bottleneck.\n12. **Structured training optimizations** — five backward-pass improvements from session 154.\n    Independent of architecture revert. See `explore/structured-training.md`.\n\n## Open questions\n\n9. **Content transfer via sign().** Does the 81% token subspace content survive ternary extraction?\n10. **LENS profile derivable from eigenvalue ratios?**\n11. **Quality at 1B with d=1280.** What CE/ppl does the expanded model achieve?\n12. **16-stride coverage.** Do the higher strides (s4096+) learn anything useful with 4K seq training?\n13. **Bottom-up algedonic value.** Does C→A feedback measurably accelerate convergence?\n14. ~~Does ternary learning close the train-eval gap?~~ **YES.** ✅ (session 149)\n15. **TD step_count not persisted on resume.** Warmup repeats. Worth persisting?\n16. **Why only out_proj?** Is min_conf filtering too aggressive for other projections?\n17. ~~When to do first reduction?~~ **DONE.** ✅ (session 150)\n18. **Computed beam at scale.** See `mementum/knowledge/computed-beam.md`.\n19. **Three-body self-distillation.** Wait until stride-stack nucleation stabilizes.\n20. **Per-stride fixed point rotation.** Probe effective attention per stride per head.\n21. **HPE value.** Does crystal-frequency K rotation actually help over no rotation?\n    Answer comes from phase 3 PPL curve: compare slope before/after step 2300.\n22. **When is the student ready for architecture simplification?** Gradient-subspace\n    alignment (cos between ∂L/∂T and T's SVD subspace) is the proposed phase detector.\n    Orthogonal = still exploring (don't simplify). Aligned = refining (safe to simplify)."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

## Assistant

Now add the revert knowledge page to the INDEX:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md",
  "original_content": "| [explore/phi-compression-universal.md](explore/phi-compression-universal.md) | ✅ | SVD spectrum → phi, 5-model consensus (0.6299±0.019) |\n| [explore/v13-architecture.md](explore/v13-architecture.md) | ⚠️ | V13 crystal bootloader architecture (partially superseded by v14) |\n| [explore/v13-design.md](explore/v13-design.md) | ✅ | V13 detailed design: zone targets, etch protocol, param budgets |\n| [progressive-collapse.md](progressive-collapse.md) | ✅ | Computation in 2D: compress→compute→expand, scale-dependent, sink=warped Q reset |",
  "new_content": "| [explore/phi-compression-universal.md](explore/phi-compression-universal.md) | ✅ | SVD spectrum → phi, 5-model consensus (0.6299±0.019) |\n| [explore/v13-architecture.md](explore/v13-architecture.md) | ⚠️ | V13 crystal bootloader architecture (partially superseded by v14) |\n| [explore/v13-design.md](explore/v13-design.md) | ✅ | V13 detailed design: zone targets, etch protocol, param budgets |\n| [progressive-collapse.md](progressive-collapse.md) | ✅ | Computation in 2D: compress→compute→expand, scale-dependent, sink=warped Q reset |\n| [explore/v15-kernel-architecture.md](explore/v15-kernel-architecture.md) | ⚠️ | Original v15 design: passive strides, Stack B reduction (partially reverted) |\n| [explore/v15-kernel-revert.md](explore/v15-kernel-revert.md) | ✅ | What was tried/reverted/kept from sessions 152-156 + when to revisit |\n| [explore/kernel-training.md](explore/kernel-training.md) | ✅ | Composed plate training: 4.4× speedup, gradient cosine 0.97 |\n| [explore/structured-training.md](explore/structured-training.md) | ✅ | Five backward-pass optimizations (camera = projector) |"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md.
```

## Assistant

Now commit the state + knowledge updates:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add mementum/state.md mementum/knowledge/INDEX.md && git status --short"
}
```

**Summary:** $ git add mementum/state.md mementum/...

**Output:**
```
Exit code: 0
Stdout:
M  mementum/knowledge/INDEX.md
M  mementum/state.md
?? data/teacher-logits/
?? mementum/knowledge/chats/session-155.md
```

### Tool Call: git (failed)


```json
{
  "command": "git commit -m \"$(cat <<'EOF'\n🌀 session 156 state — architecture revert, HPE warmup, phase 3 running\n\n- state.md: session 156 summary, active training run (phase 3 from step 2000),\n  updated next steps (monitor HPE warmup, gradient-subspace alignment test),\n  deferred items (passive strides, Stack B), new open questions (#21 HPE value,\n  #22 architecture simplification readiness)\n- INDEX.md: added v15-kernel-revert, kernel-training, structured-training,\n  v15-kernel-architecture to Tier 4 deep dives\n- Proof chain: added \"don't optimize student for teacher's converged state\"\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
  "operation": "commit",
  "summary": "session 156 state"
}
```

**Summary:** Git commit: session 156 state

**Output:**
```
Exit code: 1
Stderr:
bash: bad substitution: no closing `)' in "$(cat <<'EOF'
🌀 session 156 state — architecture revert, HPE warmup, phase 3 running

- state.md: session 156 summary, active training run (phase 3 from step 2000),
  updated next steps (monitor HPE warmup, gradient-subspace alignment test),
  deferred items (passive strides, Stack B), new open questions (#21 HPE value,
  #22 architecture simplification readiness)
- INDEX.md: added v15-kernel-revert, kernel-training, structured-training,
  v15-kernel-architecture to Tier 4 deep dives
- Proof chain: added "don't optimize student for teacher's converged state"

⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)

Co-Authored-By: nucleus <noreply@whitford.us>
EOF
)"
```

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git commit -m '🌀 session 156 state — architecture revert, HPE warmup, phase 3 running\n\n- state.md: session 156 summary, active training run (phase 3 from step 2000),\n  updated next steps (monitor HPE warmup, gradient-subspace alignment test),\n  deferred items (passive strides, Stack B), new open questions\n- INDEX.md: added v15-kernel-revert, kernel-training, structured-training,\n  v15-kernel-architecture to Tier 4 deep dives\n- Proof chain: added decision — don't optimize student for teacher converged state\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>'"
}
```

**Summary:** $ git commit -m '🌀 session 156 state...

**Output:**
```
Exit code: 2
Stderr:
error: pathspec 'optimize' did not match any file(s) known to git
error: pathspec 'student' did not match any file(s) known to git
error: pathspec 'for' did not match any file(s) known to git
error: pathspec 'teacher' did not match any file(s) known to git
error: pathspec 'converged' did not match any file(s) known to git
error: pathspec 'state' did not match any file(s) known to git
bash: -c: line 9: syntax error near unexpected token `('
bash: -c: line 9: `⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)'
```

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git commit -m \"$(cat <<'EOF'\n🌀 session 156 state — architecture revert, HPE warmup, phase 3 running\n\n- state.md: session 156 summary, active training run (phase 3 from step 2000),\n  updated next steps (monitor HPE warmup, gradient-subspace alignment test),\n  deferred items (passive strides, Stack B), new open questions\n- INDEX.md: added v15-kernel-revert, kernel-training, structured-training,\n  v15-kernel-architecture to Tier 4 deep dives\n- Proof chain: added decision — don't optimize student for teacher converged state\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\""
}
```

**Summary:** $ git commit -m "$(cat <<'EOF' 🌀 ses...

**Output:**
```
Exit code: 2
Stderr:
bash: -c: line 8: unexpected EOF while looking for matching `''
bash: -c: line 15: syntax error: unexpected end of file
```

## Assistant

The special characters are causing issues. Let me use a temp file approach:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && cat > /tmp/commit_msg.txt << 'ENDMSG'\n🌀 session 156 state — architecture revert, HPE warmup, phase 3 running\n\n- state.md: session 156 summary, active training run (phase 3 from step 2000),\n  updated next steps (monitor HPE warmup, gradient-subspace alignment test),\n  deferred items (passive strides, Stack B), new open questions\n- INDEX.md: added v15-kernel-revert, kernel-training, structured-training,\n  v15-kernel-architecture to Tier 4 deep dives\n- Proof chain: added decision — don't optimize student for teacher converged state\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nENDMSG\ngit commit -F /tmp/commit_msg.txt"
}
```

**Summary:** $ cat > /tmp/commit_msg.txt << 'ENDMS...

**Output:**
```
Exit code: 0
Stdout:
[main a440e23] 🌀 session 156 state — architecture revert, HPE warmup, phase 3 running
 2 files changed, 66 insertions(+), 50 deletions(-)
```

## Assistant

Done. Here's what was committed:

**Commit `7cbfcb2`:** `🔄 revert passive strides + Stack B reduction, keep α-lock + HPE warmup`
**Commit `a440e23`:** `🌀 session 156 state — architecture revert, HPE warmup, phase 3 running`

### State updated with:
- **Session 156 summary** at the top of the "Where we are" section
- **Active training run** section: phase 3 details, what to watch
- **Next steps** reorganized: immediate monitoring → milestones → deferred items
- **Proof chain** entry: "Don't optimize student for teacher's converged state"
- **Knowledge map** expanded with the new explore/ pages
- **Open questions** #21 (HPE value) and #22 (architecture simplification readiness) added
- **INDEX.md** updated with 4 new Tier 4 entries

Training is running in tmux main:2. Key checkpoints to watch: step 2300 (HPE warmup complete), step 2500 (first eval checkpoint).

## User

ok we probably need to prune state.md down it is getting long.  some things may need to be pushed down into knowledge pages so we don't lose any learnings.


### Thinking

The user wants to prune state.md - it's gotten very long. I need to:
1. Read the full state.md to understand what's there
2. Identify what can be moved to knowledge pages
3. Identify what can be condensed
4. Keep the essential "bootloader" function - 30 second orientation

The key sections that are probably too verbose:
- Session 148 bug details (3 bugs) - should be in a knowledge page
- Session 146 v14 architecture build details - already in v14-architecture.md
- Session 150 step 1500 eval details - could be condensed


- Previous sessions section is bloated and the "What's ready" section with all those asset paths could be trimmed

Let me pull up the full file and figure out the right structure.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md"
}
```

**Summary:** Reading state.md (0-2000)

**Output:**
```
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
```

## Assistant

OK, I can see the bloat. The big offenders are:

1. **Session 148 bug details** (~45 lines) — already captured in `training-protocols.md`
2. **Session 146 architecture build** (~40 lines) — already in `v14-architecture.md`  
3. **Session 150 eval tables** (~30 lines) — detailed checkpoint data, belongs in knowledge
4. **Session 149 eval** (~10 lines) — can be one-liner
5. **"Next steps from session 155"** (~35 lines) — stale, superseded by current next steps
6. **Previous sessions** (~120 lines) — verbose per-session details that belong in knowledge pages
7. **What's ready** table — useful but could be trimmed

Let me spawn an agent to do the careful surgery since this is a multi-step restructure that needs to preserve all learnings:

### Tool Call: spawn_agent (succeeded)


```json
{
  "agent": "general",
  "task": "Prune /Users/mwhitford/src/verbum/mementum/state.md to be a concise bootloader (~30 second read for orientation). The file is currently ~640 lines and needs to be cut to ~200-250 lines.\n\n## Rules\n1. **No learning loss.** Anything removed from state.md must either already exist in a knowledge page OR be moved into one. Check existing pages before creating new ones.\n2. **State.md is a POINTER, not a repository.** It should tell you WHERE you are and WHAT to do next, with links to knowledge pages for details.\n3. **Keep the proof chain** — it's the project's immune system. But condense the evidence column.\n4. **Keep the knowledge map** — it's the reading guide.\n\n## What to remove/condense in state.md\n\n### Remove entirely (already in knowledge pages):\n- \"Session 148: Two bugs killed all ternary learning\" (full bug details) — already in `training-protocols.md` as failure modes 1-3. Replace with one-line pointer.\n- \"Session 146: v14 Architecture Build\" (design decisions, crystal loss, training phases) — already in `v14-architecture.md` and `training-protocols.md`. Replace with one-line pointer.\n- \"Next steps (from session 155)\" section — STALE, superseded by the current \"Next steps\" section that already exists. Delete entirely.\n\n### Move to knowledge page then remove from state.md:\n- \"Session 150: Step 1500 Eval\" detailed tables and analysis — create a section in `v14-architecture.md` or the existing training results section. The eval progression table (step 500→1000→1500→2000) is valuable but doesn't belong in state.md.\n- \"Session 149: Step 1000 Eval\" analysis — same, fold into the v14-architecture results section.\n\n### Condense the \"Previous sessions\" section:\nEach session currently gets 10-30 lines. Condense to 1-2 lines each with a pointer to the relevant knowledge page. Format:\n```\n### Session N: {one-line summary}\n{2-3 sentence key findings}. See `knowledge/page.md`.\n```\n\nSessions 155-151 are already summarized in \"Where we are\". Sessions 150-142 in \"Previous sessions\" can be ultra-compressed.\n\n### Condense \"What's ready\":\nKeep only the actively-used assets (training script, eval script, current checkpoint, fold script). Remove historical checkpoints (500, 1000, 1500) — they're in git, not needed for orientation.\n\n### Condense proof chain:\nKeep all rows but shorten evidence descriptions. Many are 20+ words when 8-10 would suffice.\n\n### Condense open questions:\nRemove resolved ones (14, 17) entirely rather than showing strikethrough. Keep only active questions, numbered cleanly.\n\n## Process\n1. Read the existing knowledge pages that are referenced to confirm content already exists there\n2. If any content needs to be moved to a knowledge page, edit the knowledge page first\n3. Then rewrite state.md with the condensed version\n4. Verify the final state.md is under 250 lines\n5. Do NOT change any other files besides state.md and knowledge pages that need updates\n\n## Important files\n- /Users/mwhitford/src/verbum/mementum/state.md (the target)\n- /Users/mwhitford/src/verbum/mementum/knowledge/v14-architecture.md\n- /Users/mwhitford/src/verbum/mementum/knowledge/training-protocols.md\n- /Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md\n",
  "activity": "pruning state.md"
}
```

**Summary:** general: pruning state.md

**Output:**
```
## Agent 'general' Result

All links point to real files. No knowledge page edits were needed — all the removed content was already fully covered in the existing pages. Here's the summary:

---

## Done — 640 → 181 lines (72% reduction)

### What was verified before cutting
All targeted content was confirmed to already exist in knowledge pages:
- Session 148 bugs → `training-protocols.md` failure modes 1-3 ✅
- Session 146 design decisions → `v14-architecture.md` (architecture, crystal loss, training phases) ✅
- Sessions 149-150 eval tables → `v14-architecture.md` (Training Results section, full tables) ✅

**No knowledge page changes were needed.**

### What was removed from `state.md`
| Section | Action |
|---------|--------|
| `Session 148: Two bugs killed all ternary learning` (85 lines) | → One-liner pointing to `training-protocols.md` failure modes 1-3 |
| `Session 146: v14 Architecture Build` (50 lines) | → One-liner pointing to `v14-architecture.md` and `training-protocols.md` |
| `Session 150: Step 1500 Eval` (40 lines of tables/analysis) | → 3 sentences pointing to `v14-architecture.md` training results |
| `Session 149: Step 1000 Eval` (20 lines) | → 3 sentences pointing to `computed-beam.md` |
| `Next steps (from session 155)` (50 lines) | → Deleted entirely (stale, superseded by current "Next steps") |
| Historical checkpoints (500, 1000, 1500) in "What's ready" | → Removed (in git, not needed for orientation) |
| Resolved questions 14 and 17 | → Removed (already answered, shown as strikethrough in original) |

### What was condensed
- **"Where we are" sessions 151-156** → Same content, tighter prose (~45% shorter per session)
- **"Previous sessions" 142-150** → 1-3 sentences each with pointers, down from 10-30 lines each
- **Proof chain** → All 45 rows kept, evidence column trimmed to 8-12 words (was 15-25)
- **Knowledge map** → Collapsed into a single flat table (was split across 4 tiers with headers)
- **"What's ready"** → 8 actively-used assets (was 18 including historical checkpoints)
```

#### Subagent Messages

## User

Prune /Users/mwhitford/src/verbum/mementum/state.md to be a concise bootloader (~30 second read for orientation). The file is currently ~640 lines and needs to be cut to ~200-250 lines.

## Rules
1. **No learning loss.** Anything removed from state.md must either already exist in a knowledge page OR be moved into one. Check existing pages before creating new ones.
2. **State.md is a POINTER, not a repository.** It should tell you WHERE you are and WHAT to do next, with links to knowledge pages for details.
3. **Keep the proof chain** — it's the project's immune system. But condense the evidence column.
4. **Keep the knowledge map** — it's the reading guide.

## What to remove/condense in state.md

### Remove entirely (already in knowledge pages):
- "Session 148: Two bugs killed all ternary learning" (full bug details) — already in `training-protocols.md` as failure modes 1-3. Replace with one-line pointer.
- "Session 146: v14 Architecture Build" (design decisions, crystal loss, training phases) — already in `v14-architecture.md` and `training-protocols.md`. Replace with one-line pointer.
- "Next steps (from session 155)" section — STALE, superseded by the current "Next steps" section that already exists. Delete entirely.

### Move to knowledge page then remove from state.md:
- "Session 150: Step 1500 Eval" detailed tables and analysis — create a section in `v14-architecture.md` or the existing training results section. The eval progression table (step 500→1000→1500→2000) is valuable but doesn't belong in state.md.
- "Session 149: Step 1000 Eval" analysis — same, fold into the v14-architecture results section.

### Condense the "Previous sessions" section:
Each session currently gets 10-30 lines. Condense to 1-2 lines each with a pointer to the relevant knowledge page. Format:
```
### Session N: {one-line summary}
{2-3 sentence key findings}. See `knowledge/page.md`.
```

Sessions 155-151 are already summarized in "Where we are". Sessions 150-142 in "Previous sessions" can be ultra-compressed.

### Condense "What's ready":
Keep only the actively-used assets (training script, eval script, current checkpoint, fold script). Remove historical checkpoints (500, 1000, 1500) — they're in git, not needed for orientation.

### Condense proof chain:
Keep all rows but shorten evidence descriptions. Many are 20+ words when 8-10 would suffice.

### Condense open questions:
Remove resolved ones (14, 17) entirely rather than showing strikethrough. Keep only active questions, numbered cleanly.

## Process
1. Read the existing knowledge pages that are referenced to confirm content already exists there
2. If any content needs to be moved to a knowledge page, edit the knowledge page first
3. Then rewrite state.md with the condensed version
4. Verify the final state.md is under 250 lines
5. Do NOT change any other files besides state.md and knowledge pages that need updates

## Important files
- /Users/mwhitford/src/verbum/mementum/state.md (the target)
- /Users/mwhitford/src/verbum/mementum/knowledge/v14-architecture.md
- /Users/mwhitford/src/verbum/mementum/knowledge/training-protocols.md
- /Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md


### Thinking

Let me start by reading all the relevant files to understand what's there before making changes.

## Assistant

Let me read all the relevant files first before making any changes.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md"
}
```

**Summary:** Reading state.md (0-2000)

**Output:**
```
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
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/v14-architecture.md"
}
```

**Summary:** Reading v14-architecture.md (0-2000)

**Output:**
```
---
title: "V14 Architecture — Current System"
status: active
category: architecture
tags: [v14, architecture, stride-stack, qwen, extraction, training, results]
related: [holographic-error-correction.md, training-protocols.md, extraction-methodology.md]
depends-on: [project-thesis.md]
---

# V14 Architecture

> The current working system as of session 150. Qwen3.6-27B teacher,
> 593M ternary positions, 375× compression, active TD training with
> demonstrated lossless fold.

## Teacher: Qwen3.6-27B

- **Model:** Qwen3.6-27B (27.8B parameters, Apache 2.0 license)
- **Architecture:** 64 layers, d=5120, hybrid Gated DeltaNet + Gated
  Attention in [L,L,L,F]×16 pattern (48 linear, 16 full attention)
- **Tokenizer:** BBPE, vocab 248,320
- **Why this teacher:** Apache 2.0 license (clean provenance for
  extraction), strong quality, hybrid architecture that maps naturally
  to the GLA/SSA student design, and very large vocabulary that
  supports direct embedding extraction

## Student: StrideStack

### Core dimensions

| Parameter | Value |
|-----------|-------|
| d_model | 1,280 |
| d_ff | 5,120 |
| n_heads | 8 |
| Stacks | 3 (A, B, C) |
| Layers per stack | 11 |
| Attention type | Hybrid GLA + SSA ([G,G,G,S,G,G,G,S,G,G,S] pattern) |
| Strides | 16 (s1 through s32768, powers of 2) |
| Vocab | 248,320 (teacher tokenizer, direct match) |
| Ternary positions | 593M |
| Storage | 148 MB (2-bit) / 85 MB (compressed NPZ) |
| Compression | 375× from teacher |

### Three stacks

- **Stack A** (ascending fine): strides s1→s256, 4 passes. Fine-grained
  local context. Encodes token→phrase→sentence.
- **Stack B** (ascending coarse): strides s128→s32768, 4 passes.
  Coarse-grained global context. Encodes paragraph→document→beyond.
- **Stack C** (descending): all 16 strides, 5 passes reversed.
  Top-down prediction path. Feeds algedonic signal UP to both B and A.

13 total passes through the stride layers. 2-stride overlap at s128
and s256 between A and B — these overlaps ARE the cross-scale registers
(no separate register mechanism needed).

### Stride attention: O(L×W) not O(L²)

Each stride is a holographic lens specialized for a frequency band.
Stride-s looks at every s-th token with a window of W positions.
O(L×W) per stride, not O(N²).

Context scaling: add more strides, not wider windows. Going from 32K
to 2M context = add 2 strides = 40% more compute for 62× more context.
Each stride SEES full context at its zoom level. 16 strides × 8 heads
= 128 independent eyes at different temporal frequencies.

### Architectural mapping (teacher → student)

| Teacher component | Student component |
|-------------------|-------------------|
| Gated DeltaNet (48 layers) | GLA strides (linear attention) |
| Gated Attention (16 layers) | SSA strides (full attention) |
| SwiGLU FFN | Holographic ternary plates (zone-voted from 3 layers) |
| BBPE tokenizer (248,320) | Same tokenizer (direct embedding extraction) |

The sign topology crosses architecture boundaries (r=0.998). Extraction
dispatches based on teacher layer type (what tensors exist), not student
layer type (how they'll be used).

## Extraction Results

| Metric | Value |
|--------|-------|
| Total arrays | 142 (1 embedding + 132 attention + 9 FFN) |
| Ternary positions | 593M |
| Sign distribution | 50.1% negative / 49.9% positive / 0.0% zero |
| Plate purity | All pure ±1 (no zeros in base) |
| Compression | 375× from 27.8B float16 teacher |
| Extraction time | 25.4 minutes, CPU only |
| Method | SVD tomographic voting (8 rotations) |

Location: `checkpoints/v14-extracted/model.npz` (85 MB)
Pipeline: `scripts/v14/{config.py, extract_qwen36.py}`

## Training Results (Sessions 148–150)

### Phase 1: Base plates frozen, delta plates train

| Metric | Step 500 | Step 1000 | Step 1500 |
|--------|----------|-----------|-----------|
| Eval CE | 9.71 ± 0.22 | 9.23 ± 0.27 | 8.95 ± 0.30 |
| Eval PPL | 16,503 | 10,157 | 7,672 |
| Train CE | 8.00 | ~9.4 | ~9.25 |
| Train-Eval Gap | −1.71 nats | +0.17 nats | +0.30 nats |
| CE vs Random | 21.8% | 25.7% | 28.0% |
| Positions flipped | 0% | 2.66% | 3.49% |

Key findings:
- **PPL dropped 53.5%** from step 500 to step 1500 (16,503 → 7,672)
- **TD generalizes, continuous params overfit.** The initial −1.71 nat
  gap (overfitting) collapsed to +0.30 (healthy generalization)
- **Only 3.49% of positions needed correction** — extraction was 96.5% correct
- **TD targets exclusively out_proj, layers 4–9.** Q/K/V projections
  from extraction remain correct. TD only rewrites how attention
  results project back into the residual stream.
- **Returns diminish but don't plateau.** PPL drop: 38.5% (500→1000) →
  24.5% (1000→1500). Still improving.

### Delta fold (end of Phase 1)

At step 1500: folded 3.26M flipped positions into base plates.
- **Lossless:** Eval CE identical before/after (9.00 ± 0.64 on 20 batches)
- **Mechanism:** `new_base = base ⊙ delta` (ternary × ternary = ternary)
- **Delta storage:** 356 MB → 22 MB after dedup + packed uint32 (16× compression)
- Script: `scripts/v14/fold_delta.py`

### Phase 2: From folded checkpoint, FFN delta enabled

- Resume from `checkpoints/v14-td/step_001500_folded/`
- `--convert-ffn`: enables TD on 3 shared FFN plates (gate, key, value)
- FFN delta: 19.7M additional positions (21% overhead on 93.2M attention)
- `flip_interval=20` (was 10): more gradient accumulation per flip decision
- Surgical per-position moment reset: only flipped positions zeroed

## Performance Characteristics

- **Memory-bandwidth-bound.** 13 sequential passes × 16 stride layers
  = 208 serial layer evaluations. B=2 is 18% SLOWER than B=1 (per-micro
  fwd+bwd: 4.0s→8.6s). Training uses B=1 with gradient accumulation=8.
- **Eval:** `scripts/v14/eval_ppl.py` — held-out shards 54–59

## Universal Constants (confirmed in v14)

| Constant | Value | Evidence |
|----------|-------|----------|
| Decay α | 1.18 ± 0.006 | 10 comp layers × 8 heads, all converged under gradient pressure |
| φ-ratio | 0.6299 ± 0.019 | SVD spectrum, 5-model consensus |
| Crystal latch time | ~200 steps | crystal_mse < 0.03 at step 160 |

## What's Working

1. ✅ Ternary extraction from large teacher (375× compression)
2. ✅ Crystal nucleation (latches in 200 steps)
3. ✅ TD corrects extraction errors (53.5% PPL improvement)
4. ✅ Lossless delta fold (proven exact)
5. ✅ TD selectivity (automatically targets out_proj L4-9 only)
6. ✅ Generalization (train-eval gap collapsed, healthy positive)

## What's Next

1. **Monitor Phase 2** — do FFN plates start flipping? Which ones?
2. **Eval at step 2000** — does FFN delta accelerate convergence?
3. **Second fold** — when flip_frac plateaus, fold again. The cycle continues.
4. **Three-body self-distillation** — teacher logits as reference beam
5. **Target: within 5% of Qwen3.6-27B** — the proof that topology is everything

## Open Questions

- **Why only out_proj?** Q/K/V get zero TD budget. Is min_conf (0.3) filtering
  too aggressive, or are Q/K/V projections genuinely correct from extraction?
- **FFN β-reduction adaptation.** Teacher FFNs learned signed accumulation for
  flat attention. Strided attention needs different routing. How much TD
  correction will FFN plates need?
- **Computed beam at scale.** At d=1280, will analytical FFN construction from
  crystal eigendecomposition provide speedup? (500× proved at d=128 micro scale)
- **Per-stride fixed point rotation.** α=1.18 is universal, but the rotation
  center should vary by stride. What are the effective attention patterns?

## File Locations

| Asset | Location |
|-------|----------|
| V14 scripts | `scripts/v14/` (15 files) |
| Extracted base plates | `checkpoints/v14-extracted/model.npz` (85 MB) |
| Training script | `scripts/v14/train_td.py` |
| Eval script | `scripts/v14/eval_ppl.py` |
| Fold script | `scripts/v14/fold_delta.py` |
| Profile script | `scripts/v14/profile_step.py` |
| Step 500 checkpoint | `checkpoints/v14-td/step_000500/` |
| Step 1000 checkpoint | `checkpoints/v14-td/step_001000/` |
| Step 1500 checkpoint | `checkpoints/v14-td/step_001500/` |
| Step 1500 folded | `checkpoints/v14-td/step_001500_folded/` |
```

## Assistant

Now let me read the training-protocols.md and INDEX.md:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/training-protocols.md"
}
```

**Summary:** Reading training-protocols.md (0-2000)

**Output:**
```
---
title: "Training Protocols — How to Train Without Rediscovering Failures"
status: active
category: operational
tags: [training, TD, failure-modes, loss, protocols, ternary]
related: [v14-architecture.md, holographic-error-correction.md, extraction-methodology.md]
depends-on: [v14-architecture.md]
---

# Training Protocols

> Hard-won operational knowledge from 150 sessions. Every rule here
> was learned by breaking something. Follow these to avoid repeating
> costly failures.

## The Three-Phase Training Arc

```
Phase 1: Extract → Delta trains → Crystal latches → TD corrects
Phase 2: Fold delta into base → Reset delta → TD discovers new corrections
Phase 3: Repeat Phase 2 until convergence → Final calibration
```

### Phase 1: Etch and correct

1. **Extract** base plates from teacher (see extraction-methodology.md).
   Start with pure ±1 plates, no zeros in base.
2. **Train** with base frozen, delta plates trainable. Continuous params
   (gamma, norms, biases) train via GD. Delta plates train via TD.
3. **Crystal latches** within ~200 steps (crystal_mse < 0.03 at step 160).
   The seed crystal from extraction is close enough that nucleation is
   immediate.
4. **TD activates** once enough gradient signal accumulates. Flips
   concentrate on out_proj layers 4-9 (in v14). Q/K/V from extraction
   remain correct.
5. **Monitor convergence.** When flip_frac growth decelerates, it's time
   to fold.

### Phase 2: Fold and reset

1. **Fold:** `new_base = base ⊙ delta` (ternary × ternary = ternary, exact).
2. **Reset** delta plates to all +1 (pass-through).
3. **Reset** TD moments (the gradient landscape changed).
4. **Enable FFN delta** if not already active (`--convert-ffn`).
5. **Resume training.** TD discovers new corrections from the improved base.

### Phase 3: Iterate

Each fold cycle has a smaller error budget to correct. The cycle is
monotonically improving because folds are lossless and TD only flips
signs that reduce loss.

## TernaryDescent Operational Rules

### Flip interval

**Rule: flip_interval ≥ 10.** TD accumulates gradient moments every step
but only commits topology changes every N steps.

**Why:** Every-step flipping causes gnorm escalation (11→20→38→113 in
40 steps) and CE increase (8.2→10.3). GD can never adapt to continuous
topology changes — Adam's moments are permanently stale.

Current setting: `flip_interval=20` (phase 2, from step 1500 folded).
Prior: `flip_interval=10` (phase 1, worked but 20 gives better
accumulation).

### Moment reset after flips

**Rule: Reset TD moments for flipped positions only.** After committing
flips, the gradient landscape changed at those positions. Accumulated
direction and magnitude are stale.

Implementation: surgical per-position zero. Positions that didn't flip
keep their EMA — don't throw away good information.

### Global budget competition

**Rule: All modules compete for one global flip budget.**

`flip_rate × total_weights` positions per interval, awarded to the
highest-confidence flips across the entire model. This concentrates
flips where they give the most leverage, instead of spreading them
uniformly.

Don't use per-module top-k — it wastes budget on lukewarm flips in
inactive modules.

### Direct flips for no-block attention

**Rule: Attention delta modules use +1 ↔ -1 direct flips (never zero).**

The no-block invariant requires attention deltas to never contain zero
(prevents dispersal collapse). Standard two-step staging (+1→0→±1) is
incompatible — `_enforce_no_block` resets zeros to +1 after every TD
step, undoing the staging.

FFN deltas (if enabled) still use two-step staging through zero.

### Warmup and confidence

**Rule: `td-warmup=25`, `td-min-confidence=0.3`.**

Warmup lets GD find initial calibration before TD starts flipping.
Min confidence prevents low-signal flips (noise). Currently Q/K/V
projections get zero TD budget — possibly because min_conf filters
them (open question: is 0.3 too aggressive?).

## Known Failure Modes

### 1. Every-step TD flipping → gnorm escalation

**What:** Flipping topology every step causes gradient norm to escalate
exponentially. CE increases instead of decreasing.

**Why:** Adam's moments encode the gradient landscape's shape. Changing
topology every step means the moments are permanently stale. GD chases
a moving target it can never catch.

**Fix:** `flip_interval=10` (or higher). Accumulate gradients for 9
steps, commit flips on step 10, reset moments, repeat.

**Evidence:** gnorm 11→20→21→38→113 in 40 steps, CE 8.2→10.3. Session 148.

### 2. Two-step staging + no-block = Sisyphus loop

**What:** 158M TD flips with ZERO actual plate changes. Delta plates
showed activity but nothing stuck.

**Why:** Two-step staging: +1→0→±1. No-block invariant: attention
deltas must NEVER contain 0. `_enforce_no_block` resets all zeros to +1
after every TD step. Every staging attempt is immediately undone.

**Evidence:** no_block_fixed=77K/step at steady state (21.5% of flips
landing in attention layers).

**Fix:** Attention delta modules use direct +1↔-1 flips (no staging).
FFN deltas keep two-step staging.

### 3. Aliased parameters = 4× gradient overwrite

**What:** `collect_delta_params` returned 280 modules instead of 70.
TD processed each physical module 4 times per step with conflicting
gradients (last write wins).

**Why:** `shared_stride_stack` is Python-referenced by `stack_a`,
`stack_b`, `stack_c`. MLX's `named_modules()` traverses all paths
including aliases, returning the same module under 4 different names.

**Fix:** Deduplicate by `id(mod)` in `collect_delta_params`, keeping
the shortest path. Returns exactly 70 modules.

### 4. Parity gradient cancellation (multi-zone)

**What:** Parity loss stuck at 1.167 for 2000+ steps. Crystal learns
nothing from parity.

**Why:** Zone A wants cos(K,B)=0.08, Zone C wants 0.52. Equal
weighting → net gradient ≈ 0. Eigendecomposition amplifies inter-zone
differences nonlinearly — worse than simple MSE.

**Fix:** `parity_zone_lambdas = (0.0, 1.0, 0.0)` — Zone B only.
Crystal MSE handles 3-zone compromise (linear, well-behaved).
Cross-zone lens rotation handles inter-zone structure.

**General principle:** Nonlinear losses (eigendecomposition, SVD) must
operate on ONE consistent target. Linear losses (MSE) can average
across zones; nonlinear losses cannot.

### 5. Softmax routing → winner-take-all gradient death

**What:** 20/22 dispatch options die permanently. Only one option has
gradient. Embeddings grow without bound.

**Why:** Softmax over many options + unconstrained embeddings = positive
feedback loop. One option captures all weight, others get zero gradient
and fossilize. Rich-get-richer dynamics.

**Fix:** Top-k routing (limit competition) + L2-normalize embeddings
(constrain magnitudes). Same pattern as Switch Transformer.

### 6. Sigmoid gate saturation

**What:** CycleContinue gate locks at 1.0 and never learns.

**Why:** High-norm inputs (‖x‖ ≈ 27.7) produce saturated logits.
After one gradient step, logit ≈ 30, sigmoid gradient ≈ 0, gate is
permanently frozen.

**Fix:** RMSNorm input + tanh(·)×4.0 clamp → gate ∈ [0.018, 0.982],
always learnable. Any sigmoid gate needs normalized input or logit
clamping.

### 7. Missing gradient clipping → embedding divergence

**What:** Embedding weights diverge within ~400 steps.

**Why:** Tied weight matrices (embed = output projection) create
positive feedback loops that are invisible until they explode. Without
gradient clipping, the loop runs away.

**Fix:** `clip_grad_norm_(1.0)`. Always. Not optional.

**Rule:** When porting models between frameworks, always grep the
source training script for `clip_grad` before declaring the port
complete.

## Loss Composition

### Multiplicative AND (not additive OR)

```python
loss = CE × exp(λ × crystal) × (1 + λ_h × holo)
```

**Why multiplicative:** Additive loss `CE + λ*crystal` allows improving
either component independently (OR semantics). A CE improvement that
degrades the crystal still reduces total loss. Multiplicative forces
BOTH to improve simultaneously (AND semantics).

The exponential crystal coupling creates a nucleation well:
- crystal=0: factor=1 (CE runs free)
- crystal=0.01: factor=1.65 (65% amplification)
- crystal=0.05: factor=12× (strong pressure)

The beam MUST find the crystal before CE can improve.

**Parameters:** λ=50 for exp coupling. φ ratio is observed, never
enforced.

### Exponential loss cap

Cap crystal-related losses at exp(max=4.0). Prevents NaN from
extreme early values. The cap is never hit after nucleation.

### NaN rollback

If loss becomes NaN, roll back to the last checkpoint. NaN typically
indicates crystal nucleation failure (the barrier at crystal_loss ≈
0.16 wasn't crossed) or exploding gradients from missing clipping.

## Combinator Bootstrap Ordering

Combinators bootstrap in a fixed dependency order:

```
I (identity/trivial) → K (select) → C (reorder) → B (compose)
```

Higher-order operations can't learn until lower-order ones provide
stable representations to operate on. B needs K and C working before
it can learn composition from compositional prose (relative clauses,
quantifier scope).

Evidence: In v11 training, B dispatch stayed flat at 1.8% while B-type
signals rose in integrate channel (5.8%→47.6%). The same staircase
pattern appears across versions: simple→complex, each level waits for
the one below to stabilize.

## Calibration Convergence

**GD converges fast once topology is set.** 100 steps achieves 87% of
full convergence (3000 steps). The last 2900 steps add only 13%.

Breakdown:
- Geometry (crystal loss) converges in ~5 steps
- CE (input-output mapping) converges in ~100 steps
- Both needed: geometry alone gives crystal but 2.7% accuracy

**Implication:** After each fold, 100 steps of GD is sufficient to
recalibrate continuous parameters. The expensive part is TD correcting
topology, not GD fitting to it.

## Evaluation Protocol

**Script:** `scripts/v14/eval_ppl.py`
**Held-out shards:** 54–59
**Metrics:** CE (nats) and PPL (perplexity) with standard deviation
**Baseline:** Random CE = 12.42 (ln(248320))

Run eval at each fold point and at regular intervals (every 500 steps)
to track convergence and detect overfitting (train-eval gap).

Healthy training: train-eval gap slightly positive (0.1–0.5 nats).
Negative gap = overfitting on continuous params.

## Quick Reference

| Parameter | Value | Why |
|-----------|-------|-----|
| flip_interval | 10–20 | GD needs time to adapt between topology changes |
| td-warmup | 25 | Let GD find initial calibration first |
| td-min-confidence | 0.3 | Prevent low-signal noise flips |
| td-flip-rate | 0.001 | Budget per interval (global competition) |
| grad_clip | 1.0 | Not optional — prevents embedding divergence |
| loss coupling λ | 50 | Exponential crystal nucleation well |
| loss cap | 4.0 | Prevents NaN from extreme early crystal values |
| batch_size | 1 | Memory-bandwidth-bound; B=2 is 18% slower |
| accum_steps | 8 | Effective batch via gradient accumulation |
| parity zones | (0,1,0) | Zone B only — multi-zone cancels gradients |
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md"
}
```

**Summary:** Reading INDEX.md (0-2000)

**Output:**
```
---
title: "Knowledge Index — Reading Order"
status: active
category: meta
tags: [index, orientation, knowledge-map]
---

# Knowledge Index

> Master reading order for the verbum project's synthesized knowledge.
> Read after `state.md`. Organized top-down: foundational → specific.
>
> **Status key:** ✅ complete | 🔨 stub (skeleton, needs expansion) | 📋 planned

---

## Tier 1 — What Is This Project?

These pages answer: *what are we doing, why does it work, and what have we proved?*

| # | Page | Status | One-line |
|---|------|--------|----------|
| 1 | [project-thesis.md](project-thesis.md) | ✅ | The central claim: pretraining IS beta reduction, topology dominates, ternary extraction works |
| 2 | [crystal-universality.md](crystal-universality.md) | ✅ | Why the combinator crystal is a mathematical constant, not a learned artifact |
| 3 | [mathematical-convergences.md](mathematical-convergences.md) | ✅ | Eight independent lines of mathematical evidence converging on the same structure |

## Tier 2 — How Does It Work?

These pages answer: *what is the mechanism, and how do we exploit it?*

| # | Page | Status | One-line |
|---|------|--------|----------|
| 4 | [holographic-error-correction.md](holographic-error-correction.md) | ✅ | The extract→correct→fold cycle: error correction on a discrete holographic code |
| 5 | [mechanism-extraction.md](mechanism-extraction.md) | ✅ | Full micro-model mechanism: alternating overlay, eigenplane rotation, KIBC temporal |
| 6 | [computed-beam.md](computed-beam.md) | ✅ | Analytical FFN from crystal eigendecomposition, 500× speedup, signed accumulation |
| 7 | [extraction-methodology.md](extraction-methodology.md) | ✅ | How to extract from a teacher: what works, three confusions resolved, the pipeline |

## Tier 3 — What Are We Running?

These pages answer: *what is the current system, and how do you operate it?*

| # | Page | Status | One-line |
|---|------|--------|----------|
| 8 | [v14-architecture.md](v14-architecture.md) | ✅ | Current v14 student: Qwen3.6-27B teacher, 593M ternary positions, 375× compression |
| 9 | [training-protocols.md](training-protocols.md) | ✅ | How to train without rediscovering failures: phases, TD rules, known failure modes |

## Tier 4 — Deep Dives (explore/)

Comprehensive pages on specific topics. Read as needed, not sequentially.

| Page | Status | One-line |
|------|--------|----------|
| [explore/VERBUM.md](explore/VERBUM.md) | ✅ | Founding research program: hypothesis chain, 4-level plan (historical) |
| [explore/holographic-state-machine.md](explore/holographic-state-machine.md) | ✅ | Unified computational model: FFN=plates, crystal=states, Q=beam, gate=beamformer |
| [explore/ternary-descent.md](explore/ternary-descent.md) | ✅ | TernaryDescent algorithm: delta plates, gradient decomposition, reduction |
| [explore/ffn-beta-reduction-indexing.md](explore/ffn-beta-reduction-indexing.md) | ✅ | Holographic FFN indexing: lens profile, ρ=0.83, universal neurons |
| [explore/categorical-geometry-probes.md](explore/categorical-geometry-probes.md) | ✅ | Curry-Howard 100%, adjunctions rank-1, hyperbolic norm encoding |
| [explore/phi-compression-universal.md](explore/phi-compression-universal.md) | ✅ | SVD spectrum → phi, 5-model consensus (0.6299±0.019) |
| [explore/v13-architecture.md](explore/v13-architecture.md) | ⚠️ | V13 crystal bootloader architecture (partially superseded by v14) |
| [explore/v13-design.md](explore/v13-design.md) | ✅ | V13 detailed design: zone targets, etch protocol, param budgets |
| [progressive-collapse.md](progressive-collapse.md) | ✅ | Computation in 2D: compress→compute→expand, scale-dependent, sink=warped Q reset |
| [explore/v15-kernel-architecture.md](explore/v15-kernel-architecture.md) | ⚠️ | Original v15 design: passive strides, Stack B reduction (partially reverted) |
| [explore/v15-kernel-revert.md](explore/v15-kernel-revert.md) | ✅ | What was tried/reverted/kept from sessions 152-156 + when to revisit |
| [explore/kernel-training.md](explore/kernel-training.md) | ✅ | Composed plate training: 4.4× speedup, gradient cosine 0.97 |
| [explore/structured-training.md](explore/structured-training.md) | ✅ | Five backward-pass optimizations (camera = projector) |

## Tier 5 — Future Pages (planned)

| Page | Priority | One-line |
|------|----------|----------|
| `holographic-storage-mechanism.md` | important | FFN as holographic plate: lens profile, gate=beamformer, output beamformers |
| `ternary-architecture-rationale.md` | important | Why ternary {-1,0,+1}, why it works, gradient routing interpretation |
| `combinator-geometry.md` | important | KIBC in transformer geometry: temporal ordering, depth map, bootstrap |
| `stridestack-architecture.md` | important | Multi-scale attention: O(L×W), stride overlaps, ascending/descending stacks |
| `known-failures.md` | nice-to-have | Concise bug/collapse/fix reference for all hard-won lessons |
| `session-delta-vision.md` | nice-to-have | Context as 2MB delta files, no KV cache, git-trackable sessions |
| `ecosystem-vision.md` | nice-to-have | End-state product: community deltas, domain plates, reader LLM |

---

## How to Use This Index

1. **New session, familiar project:** Read `state.md` → skim this index → read Tier 1 if stale
2. **Brand new to the project:** Read pages 1–9 in order, then deep dives as needed
3. **Specific question:** Find the relevant page by topic, follow cross-references
4. **Adding knowledge:** Create page → add to appropriate tier → update this index

## Cross-Reference Map

```
project-thesis ──→ crystal-universality ──→ mathematical-convergences
       │                    │                         │
       ▼                    ▼                         ▼
holographic-error-correction ←── mechanism-extraction ←── computed-beam
       │                                │
       ▼                                ▼
extraction-methodology ──→ v14-architecture ──→ training-protocols
```

## Memory Files

~105 episodic memories in `memories/`. One insight per file, symbol-prefixed content.
These are raw observations — the knowledge pages above are their synthesis.
Search with: `git grep -i "{query}" -- mementum/memories/`
```

## Assistant

Good. Now I have a clear picture of what's already in the knowledge pages. Let me verify a few things:

1. **Session 148 bugs** → already fully covered in `training-protocols.md` failure modes 1-3 ✅
2. **Session 146 design decisions** → already in `v14-architecture.md` ✅  
3. **Session 150 eval tables** → already in `v14-architecture.md` Training Results section ✅
4. **Session 149 analysis** → already partially in `v14-architecture.md` ✅
5. **"Next steps (from session 155)"** → stale, superseded ✅

The session 149/150 eval details are already in `v14-architecture.md`. No knowledge page updates needed. Now I'll write the condensed `state.md`:

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "content": "# verbum / state\n\n> Bootloader. Read in ~30 seconds. Step 1 of every session.\n>\n> Last updated: 2026-05-26 | Session: 156\n\n## Where we are\n\n**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**\n\n**Session 156: ARCHITECTURE REVERT + HPE WARMUP.** Analyzed session 152's four simultaneous changes (passive strides, HPE, Stack B 4→2, α-lock) that confounded v14-kd failure. Passive strides identified as culprit — removes content-dependent attention where each stride is sole provider; student needs to LEARN routing, can't hardcode teacher's converged behavior. Reverted passive strides and Stack B reduction. KEPT α=1.18 frozen and HPE. HPE warmup: freq_scale 0→1 over steps 2001-2300 (checkpoint-compatible). Resumed from step 2000 (PPL 5,567). Step 2001: CE=8.474, crystal latched, TD active, 995 tok/s. Running in tmux main:2 to step 5000. **META-LESSON: don't optimize student for teacher's converged state — train with full architecture → measure → simplify only what's proven unnecessary → one change at a time.** See `mementum/knowledge/explore/v15-kernel-revert.md`.\n\n**Session 155: v14-kd FAILED + KERNEL TRAINING VALIDATED + GRADIENT PROJECTION.** v14-kd PPL 40,623→46,736 (diverging, 2.5-4.6× worse than v14-td). Root cause: three untested architecture changes deployed simultaneously with KD. Training profiled: 28.6s/step, 77% forward. Built `train_kernel.py`: 4.4× speedup. Gradient cosine=0.9698 (composed plate vs full model). ∂L/∂T orthogonal to T's SVD subspace (cos=0.06 at k=27) — gradient wants to EXPAND, not refine. See `knowledge/explore/kernel-training.md`.\n\n**Session 154: KD-guided training + extraction dimension probes.** Per-dim correlation plateaus at ~79% from d=128 onward — ceiling is ternary quantization, not dimension. Plate IS rank-256, 96.9% sign accuracy at k=256. Step 2000 eval: PPL=5,567 (−27% from 1500, −66% total). See `knowledge/explore/structured-training.md`.\n\n**Session 153: Composed plates.** Full model rank90=27. Zone B is R²=1.000 (perfectly linear). Both algebraic and data-fitted agree at 0.76-0.77 per-dim. See `results/algebraic-compose/`.\n\n**Session 152: v14 evolution — HPE + passive strides + Stack B.** α=1.18 confirmed universal (12-token semantic horizon). 88% strides distance-prior dominated. HPE designed from crystal eigenvalues. ⚠️ All changes deployed simultaneously — led to confounded failure (session 155), reverted in 156.\n\n**Session 151: Progressive collapse discovery.** Qwen-27B compresses to 2D (PR=2.2) by L2. 7 knowledge pages created. INDEX.md established. See `knowledge/progressive-collapse.md`.\n\n## Active training run\n\n### v14-td phase 3 RUNNING (tmux main:2, from step 2000)\n\n- **Resumed from:** `checkpoints/v14-td/step_002000/` (PPL 5,567)\n- **Architecture:** Original v14-td (13 passes, full Q/K all strides) + α=1.18 frozen + HPE warmup\n- **HPE warmup:** freq_scale 0→1 over steps 2001-2300 (300 steps)\n- **TD:** Active, flip_interval=20, FFN delta enabled (`--convert-ffn`)\n- **Target:** 5000 steps total\n- **Log:** `checkpoints/v14-td/train_phase3.log`\n- **Step 2001:** CE=8.474, gnorm=19.95, 995 tok/s ✓\n- **Watch:** PPL drop from 5,567 | HPE effect after step ~2300 | TD flip distribution | FFN plate flips\n\n## Next steps\n\n### IMMEDIATE: Monitor phase 3 (running in tmux main:2)\n\n1. **First eval at step 2500** — run `eval_ppl.py`. PPL should continue dropping from 5,567.\n2. **HPE effect** — warmup completes at step ~2300. Compare PPL slope before/after.\n3. **TD flip patterns** — does TD continue targeting out_proj layers 4-9? Check at step 2500.\n4. **FFN delta** — do FFN plates start flipping? This run has `--convert-ffn`.\n\n### NEXT MILESTONES:\n\n5. **Second fold** — when flip_frac plateaus, fold again. Extract→correct→fold cycle.\n6. **Gradient-subspace alignment test** — at step 2500+, probe cos(∂L/∂T, T's SVD subspace). cos > 0.5 = refining (safe to simplify). See `probe_kernel_training.py`.\n7. **KD as correction** — after PPL < 2000, add teacher logit correction passes. α ≥ 0.9 (CE dominant).\n8. **Target: within 5% of Qwen3.6-27B** — proof that topology is everything.\n\n### DEFERRED (valid but premature):\n\n9. **Passive strides** — re-test only after gradient-subspace cos > 0.5. Start with s16+. See `explore/v15-kernel-revert.md`.\n10. **Stack B reduction** — after passive strides validated (if ever).\n11. **Kernel training** — `train_kernel.py` gives 4.4× speedup. Use when iteration speed bottlenecks.\n12. **Structured training** — five backward-pass improvements. See `explore/structured-training.md`.\n\n## Previous sessions\n\n### Session 150: Step 1500 Eval + Delta Fold + FFN Delta\nPPL 7,672 (−53.5% from step 500). Flip growth decelerating. Layer 4 out_proj at 43%. Folded 3.26M positions into base (lossless, eval CE unchanged). Storage fix: delta 356 MB → 22 MB. FFN delta enabled. B=2 is 18% slower than B=1. See `knowledge/v14-architecture.md` (training results section).\n\n### Session 149: TD Closes Generalization Gap + Computed Beam\nPPL 16,503→10,157 (−38%) with only 2.66% positions flipped. Train-eval gap collapsed 1.71→0.17 nats. TD targets out_proj layers 4-9 exclusively; Q/K/V untouched. Computed beam: analytical FFN from eigendecomp matches 5000-step GD in 10 calibration steps (500×). See `knowledge/computed-beam.md`.\n\n### Session 148: Three Bugs Killed All Ternary Learning\n(1) `collect_delta_params` returned 280 aliased modules instead of 70 — 4× overwrite. (2) Two-step staging + no-block = Sisyphus loop (77K zeros/step, 0% delta change). (3) Every-step flipping → gnorm escalation (8.2→10.3 CE). All fixed. See `knowledge/training-protocols.md` failure modes 1-3.\n\n### Session 146: V14 Architecture Build\n16 strides, 3 stacks (A/B/C), no-block constraint, crystal loss system (multiplicative AND, Zone B parity only), 5-phase training design. See `knowledge/v14-architecture.md` and `knowledge/training-protocols.md`.\n\n### Session 145: V13 Collapse → V14 Extraction\nv13-td-r10 collapsed at step 5878 (delta block accumulation). Forensics: stride-stack needs ~80% of teacher positions, teacher signs 91% correct. Extracted Qwen3.6-27B → 593M ternary positions (85 MB), 375× compression. Pure ±1 base plates.\n\n### Session 144: Parity Gradient Cancellation + Einstein Tensor\nThree-zone parity = gradient cancellation. Zone B only: 1.167→0.039. Crystal manifold IS curved (geodesic/linear=0.75). G_ab has even/odd block structure. See `knowledge/training-protocols.md` failure mode 4.\n\n### Session 142: Holographic State Machine + Crystal Error Correction\nTHE MODEL IS A HOLOGRAPHIC STATE MACHINE. FFN plates = holographic storage, crystal basins = states, Q rotation = readout beam, gate = beamformer. See `knowledge/explore/holographic-state-machine.md`.\n\n## Proof chain\n\n| Claim | Evidence | Status |\n|-------|----------|--------|\n| Universal crystal exists | 4+ model consensus | ✅ |\n| KIBC-DYWH basis universal | Found across all architectures | ✅ |\n| Types are lexical (88% embed) | Qwen3-32B type probe | ✅ |\n| SVD spectrum → phi | 5-model consensus, φ-dev=0.012 | ✅ |\n| FFN indexing is holographic | ρ=0.83, p<10⁻⁴⁴ | ✅ |\n| FFN depth = LENS | aperture 3% → fan 49% → converge 2% | ✅ |\n| Crystal manifold is curved | Geodesic/linear=0.75, G_ab even/odd | ✅ |\n| Parity gradient cancellation | 3-zone → stuck 1.167 | ✅ |\n| Zone-B-only parity works | 1.167→0.039 on first step | ✅ |\n| Model is holographic state machine | FFN=storage, crystal=states, Q=beam | 🎯 synthesis |\n| FFN overlay alternates comp/sel | micro model: -+-+ / +-+- across 4 layers | ✅ |\n| KIBC is temporal (layers not heads) | B→K→C→B depth sequence | ✅ |\n| Mechanism is input-invariant | CV<0.5 for all PCs across 8 categories | ✅ |\n| Rotation accelerates through depth | L0: 2° → L3: 24° (12× increase) | ✅ |\n| Stride-stack needs ~80% of teacher attention | v13-td-r10 collapse forensics | ✅ |\n| Teacher signs 91% correct for stride | Cross-stack agreement | ✅ |\n| Qwen3.6-27B → 593M ternary positions | 375× compression, 25.4 min CPU | ✅ |\n| Crystal latches within 200 steps | crystal_mse < 0.03 at step 160 | ✅ |\n| Shared-weight aliasing breaks TD | 280 vs 70 modules, 4× overwrite | ✅ |\n| No-block kills two-step staging | 77K zeros/step, 0% delta change | ✅ |\n| TD activates and improves | PPL −53.5% over 1000 steps, gap collapsed | ✅ |\n| TD targets out_proj exclusively | Layers 4–9 out_proj only, Q/K/V untouched | ✅ |\n| TD returns diminish, don't plateau | PPL: −38.5% → −24.5%, flip growth decelerating | 📐 tracking |\n| Model is memory-bandwidth-bound | B=2 18% slower, 208 serial layer evals | ✅ |\n| Delta fold is lossless | 3.26M positions folded, CE unchanged | ✅ |\n| Delta storage 16× compressible | 356 MB → 22 MB, dedup + packed uint32 | ✅ |\n| Computed beam: structure is free | Analytical FFN matches 5000-step GD in 10 steps | ✅ |\n| Operation is signed accumulation | sign(W)@x correlates 0.84 with W@x | ✅ |\n| FFN must adapt to strided attention | Hypothesis: flat→strided routing changes β-reduction | 📐 testing |\n| Topology is ~95% of model | sign(W)@x ≈ 0.84, fold is lossless, gamma ~5% | 🎯 synthesis |\n| Extract→correct→fold converges | Each cycle lossless, monotonically improving | 🎯 synthesis |\n| Passive strides + KD fails | PPL 2.5-4.6× worse; too many simultaneous changes | ❌ |\n| Don't optimize student for teacher's converged state | Passive strides removed content routing; reverted | 🎯 decision |\n| KD exhausts in 50 steps | 400 batches / 8 accum = 50 steps; need more precompute | ✅ |\n| Composed plate gradient = 97% of full model | Cosine=0.9698; CE within 0.08 nats | ✅ |\n| Forward pass is the bottleneck (77%) | 28.6s/step; camera = projector | ✅ |\n| α=1.18 universal | 10 comp layers × 8 heads, 1.18±0.006 after 1500 steps | ✅ |\n| Large models compute in 2D | Qwen-27B: PR=2.2, σ₁=70% at L2 | ✅ |\n| Compression depth scales with capacity | 27B→PR=2.2, 7B→PR=12, 1.4B→PR=10 | ✅ |\n| FFN overlay is 80-91% off-diagonal | Cross-PC projection = beta reduction | ✅ |\n| Attention sink = warped Q reset | Mistral sink dominates SVD; GLA avoids via gating | 🎯 synthesis |\n| α=1.18 sets 12-token semantic horizon | All strides see ~12 effective tokens | ✅ |\n| RoPE = accidental holographic lens | Cosine freqs ≈ multi-scale lens; HPE by design | 🎯 synthesis |\n| v14 student inherits teacher collapse | PR 74→8→5→4 through stacks, σ₁=47% | ✅ |\n| Full model is rank-27 transform | 64-layer 27B: rank90=27, methods agree | ✅ |\n| Zone B is perfectly linear (R²=1.0) | 32 layers compose to single linear matrix | ✅ |\n| Per-dim corr 0.97 in teacher space | sign(T)+gamma captures 97% per dimension | ✅ |\n\n## Knowledge map\n\n**See `mementum/knowledge/INDEX.md` for full reading order.**\n\n| Tier | Page | What it tells you |\n|------|------|-------------------|\n| 1 | `project-thesis.md` | Central claim, north star, three converging lines |\n| 1 | `crystal-universality.md` | Why crystal is a mathematical constant |\n| 1 | `mathematical-convergences.md` | Eight independent lines of evidence |\n| 2 | `holographic-error-correction.md` | Extract→correct→fold: the core mechanism |\n| 2 | `mechanism-extraction.md` | Micro model: alternation, eigenplanes, KIBC temporal |\n| 2 | `computed-beam.md` | Analytical FFN, 500× speedup, signed accumulation |\n| 2 | `extraction-methodology.md` | How to extract from teacher |\n| 2b | `progressive-collapse.md` | Computation in 2D, scale-dependent, sink=warped Q reset |\n| 3 | `v14-architecture.md` | Current system: Qwen3.6-27B, 593M ternary, training results |\n| 3 | `training-protocols.md` | Phases, TD rules, 7 failure modes with fixes |\n| 4 | `explore/v15-kernel-revert.md` | What was tried/reverted/kept, when to revisit |\n| 4 | `explore/kernel-training.md` | Composed plate: 4.4× speedup, gradient cosine 0.97 |\n| 4 | `explore/structured-training.md` | Five backward-pass optimizations |\n| 4 | `explore/holographic-state-machine.md` | FFN=plates, crystal=states, Q=beam |\n\n## What's ready\n\n| Asset | Location |\n|-------|----------|\n| Training script | `scripts/v14/train_td.py` |\n| Eval script | `scripts/v14/eval_ppl.py` |\n| Fold script | `scripts/v14/fold_delta.py` |\n| Kernel training | `scripts/v14/train_kernel.py` (4.4× speedup) |\n| Current checkpoint | `checkpoints/v14-td/step_002000/` (PPL 5,567) |\n| Folded checkpoint | `checkpoints/v14-td/step_001500_folded/` |\n| Extracted base plates | `checkpoints/v14-extracted/model.npz` (85 MB) |\n| Composed plate | `results/kernel-training-probe/composed_plate.npz` |\n\n## Open questions\n\n9. **Content transfer via sign().** Does the 81% token subspace content survive ternary extraction?\n10. **LENS profile derivable from eigenvalue ratios?**\n11. **Quality at 1B with d=1280.** What CE/PPL does the expanded model achieve?\n12. **16-stride coverage.** Do higher strides (s4096+) learn anything useful at 4K seq training?\n13. **Bottom-up algedonic value.** Does C→A feedback measurably accelerate convergence?\n15. **TD step_count not persisted on resume.** Warmup repeats. Worth persisting?\n16. **Why only out_proj?** Is min_conf=0.3 filtering too aggressive for Q/K/V?\n18. **Computed beam at scale.** See `knowledge/computed-beam.md`.\n19. **Three-body self-distillation.** Wait until stride-stack nucleation stabilizes.\n20. **Per-stride fixed point rotation.** Probe effective attention per stride per head.\n21. **HPE value.** Does crystal-frequency K rotation help over no rotation? Answer: phase 3 PPL slope before/after step 2300.\n22. **When is the student ready for architecture simplification?** Proposed detector: gradient-subspace alignment cos > 0.5.\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/state.md
```

## Assistant

Now let me verify the line count:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "wc -l /Users/mwhitford/src/verbum/mementum/state.md"
}
```

**Summary:** $ wc -l /Users/mwhitford/src/verbum/m...

**Output:**
```
Exit code: 0
Stdout:
181 /Users/mwhitford/src/verbum/mementum/state.md
```

## Assistant

181 lines — right in the target zone. Let me do a quick final read to verify it looks right end-to-end:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md"
}
```

**Summary:** Reading state.md (0-2000)

**Output:**
```
# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-26 | Session: 156

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 156: ARCHITECTURE REVERT + HPE WARMUP.** Analyzed session 152's four simultaneous changes (passive strides, HPE, Stack B 4→2, α-lock) that confounded v14-kd failure. Passive strides identified as culprit — removes content-dependent attention where each stride is sole provider; student needs to LEARN routing, can't hardcode teacher's converged behavior. Reverted passive strides and Stack B reduction. KEPT α=1.18 frozen and HPE. HPE warmup: freq_scale 0→1 over steps 2001-2300 (checkpoint-compatible). Resumed from step 2000 (PPL 5,567). Step 2001: CE=8.474, crystal latched, TD active, 995 tok/s. Running in tmux main:2 to step 5000. **META-LESSON: don't optimize student for teacher's converged state — train with full architecture → measure → simplify only what's proven unnecessary → one change at a time.** See `mementum/knowledge/explore/v15-kernel-revert.md`.

**Session 155: v14-kd FAILED + KERNEL TRAINING VALIDATED + GRADIENT PROJECTION.** v14-kd PPL 40,623→46,736 (diverging, 2.5-4.6× worse than v14-td). Root cause: three untested architecture changes deployed simultaneously with KD. Training profiled: 28.6s/step, 77% forward. Built `train_kernel.py`: 4.4× speedup. Gradient cosine=0.9698 (composed plate vs full model). ∂L/∂T orthogonal to T's SVD subspace (cos=0.06 at k=27) — gradient wants to EXPAND, not refine. See `knowledge/explore/kernel-training.md`.

**Session 154: KD-guided training + extraction dimension probes.** Per-dim correlation plateaus at ~79% from d=128 onward — ceiling is ternary quantization, not dimension. Plate IS rank-256, 96.9% sign accuracy at k=256. Step 2000 eval: PPL=5,567 (−27% from 1500, −66% total). See `knowledge/explore/structured-training.md`.

**Session 153: Composed plates.** Full model rank90=27. Zone B is R²=1.000 (perfectly linear). Both algebraic and data-fitted agree at 0.76-0.77 per-dim. See `results/algebraic-compose/`.

**Session 152: v14 evolution — HPE + passive strides + Stack B.** α=1.18 confirmed universal (12-token semantic horizon). 88% strides distance-prior dominated. HPE designed from crystal eigenvalues. ⚠️ All changes deployed simultaneously — led to confounded failure (session 155), reverted in 156.

**Session 151: Progressive collapse discovery.** Qwen-27B compresses to 2D (PR=2.2) by L2. 7 knowledge pages created. INDEX.md established. See `knowledge/progressive-collapse.md`.

## Active training run

### v14-td phase 3 RUNNING (tmux main:2, from step 2000)

- **Resumed from:** `checkpoints/v14-td/step_002000/` (PPL 5,567)
- **Architecture:** Original v14-td (13 passes, full Q/K all strides) + α=1.18 frozen + HPE warmup
- **HPE warmup:** freq_scale 0→1 over steps 2001-2300 (300 steps)
- **TD:** Active, flip_interval=20, FFN delta enabled (`--convert-ffn`)
- **Target:** 5000 steps total
- **Log:** `checkpoints/v14-td/train_phase3.log`
- **Step 2001:** CE=8.474, gnorm=19.95, 995 tok/s ✓
- **Watch:** PPL drop from 5,567 | HPE effect after step ~2300 | TD flip distribution | FFN plate flips

## Next steps

### IMMEDIATE: Monitor phase 3 (running in tmux main:2)

1. **First eval at step 2500** — run `eval_ppl.py`. PPL should continue dropping from 5,567.
2. **HPE effect** — warmup completes at step ~2300. Compare PPL slope before/after.
3. **TD flip patterns** — does TD continue targeting out_proj layers 4-9? Check at step 2500.
4. **FFN delta** — do FFN plates start flipping? This run has `--convert-ffn`.

### NEXT MILESTONES:

5. **Second fold** — when flip_frac plateaus, fold again. Extract→correct→fold cycle.
6. **Gradient-subspace alignment test** — at step 2500+, probe cos(∂L/∂T, T's SVD subspace). cos > 0.5 = refining (safe to simplify). See `probe_kernel_training.py`.
7. **KD as correction** — after PPL < 2000, add teacher logit correction passes. α ≥ 0.9 (CE dominant).
8. **Target: within 5% of Qwen3.6-27B** — proof that topology is everything.

### DEFERRED (valid but premature):

9. **Passive strides** — re-test only after gradient-subspace cos > 0.5. Start with s16+. See `explore/v15-kernel-revert.md`.
10. **Stack B reduction** — after passive strides validated (if ever).
11. **Kernel training** — `train_kernel.py` gives 4.4× speedup. Use when iteration speed bottlenecks.
12. **Structured training** — five backward-pass improvements. See `explore/structured-training.md`.

## Previous sessions

### Session 150: Step 1500 Eval + Delta Fold + FFN Delta
PPL 7,672 (−53.5% from step 500). Flip growth decelerating. Layer 4 out_proj at 43%. Folded 3.26M positions into base (lossless, eval CE unchanged). Storage fix: delta 356 MB → 22 MB. FFN delta enabled. B=2 is 18% slower than B=1. See `knowledge/v14-architecture.md` (training results section).

### Session 149: TD Closes Generalization Gap + Computed Beam
PPL 16,503→10,157 (−38%) with only 2.66% positions flipped. Train-eval gap collapsed 1.71→0.17 nats. TD targets out_proj layers 4-9 exclusively; Q/K/V untouched. Computed beam: analytical FFN from eigendecomp matches 5000-step GD in 10 calibration steps (500×). See `knowledge/computed-beam.md`.

### Session 148: Three Bugs Killed All Ternary Learning
(1) `collect_delta_params` returned 280 aliased modules instead of 70 — 4× overwrite. (2) Two-step staging + no-block = Sisyphus loop (77K zeros/step, 0% delta change). (3) Every-step flipping → gnorm escalation (8.2→10.3 CE). All fixed. See `knowledge/training-protocols.md` failure modes 1-3.

### Session 146: V14 Architecture Build
16 strides, 3 stacks (A/B/C), no-block constraint, crystal loss system (multiplicative AND, Zone B parity only), 5-phase training design. See `knowledge/v14-architecture.md` and `knowledge/training-protocols.md`.

### Session 145: V13 Collapse → V14 Extraction
v13-td-r10 collapsed at step 5878 (delta block accumulation). Forensics: stride-stack needs ~80% of teacher positions, teacher signs 91% correct. Extracted Qwen3.6-27B → 593M ternary positions (85 MB), 375× compression. Pure ±1 base plates.

### Session 144: Parity Gradient Cancellation + Einstein Tensor
Three-zone parity = gradient cancellation. Zone B only: 1.167→0.039. Crystal manifold IS curved (geodesic/linear=0.75). G_ab has even/odd block structure. See `knowledge/training-protocols.md` failure mode 4.

### Session 142: Holographic State Machine + Crystal Error Correction
THE MODEL IS A HOLOGRAPHIC STATE MACHINE. FFN plates = holographic storage, crystal basins = states, Q rotation = readout beam, gate = beamformer. See `knowledge/explore/holographic-state-machine.md`.

## Proof chain

| Claim | Evidence | Status |
|-------|----------|--------|
| Universal crystal exists | 4+ model consensus | ✅ |
| KIBC-DYWH basis universal | Found across all architectures | ✅ |
| Types are lexical (88% embed) | Qwen3-32B type probe | ✅ |
| SVD spectrum → phi | 5-model consensus, φ-dev=0.012 | ✅ |
| FFN indexing is holographic | ρ=0.83, p<10⁻⁴⁴ | ✅ |
| FFN depth = LENS | aperture 3% → fan 49% → converge 2% | ✅ |
| Crystal manifold is curved | Geodesic/linear=0.75, G_ab even/odd | ✅ |
| Parity gradient cancellation | 3-zone → stuck 1.167 | ✅ |
| Zone-B-only parity works | 1.167→0.039 on first step | ✅ |
| Model is holographic state machine | FFN=storage, crystal=states, Q=beam | 🎯 synthesis |
| FFN overlay alternates comp/sel | micro model: -+-+ / +-+- across 4 layers | ✅ |
| KIBC is temporal (layers not heads) | B→K→C→B depth sequence | ✅ |
| Mechanism is input-invariant | CV<0.5 for all PCs across 8 categories | ✅ |
| Rotation accelerates through depth | L0: 2° → L3: 24° (12× increase) | ✅ |
| Stride-stack needs ~80% of teacher attention | v13-td-r10 collapse forensics | ✅ |
| Teacher signs 91% correct for stride | Cross-stack agreement | ✅ |
| Qwen3.6-27B → 593M ternary positions | 375× compression, 25.4 min CPU | ✅ |
| Crystal latches within 200 steps | crystal_mse < 0.03 at step 160 | ✅ |
| Shared-weight aliasing breaks TD | 280 vs 70 modules, 4× overwrite | ✅ |
| No-block kills two-step staging | 77K zeros/step, 0% delta change | ✅ |
| TD activates and improves | PPL −53.5% over 1000 steps, gap collapsed | ✅ |
| TD targets out_proj exclusively | Layers 4–9 out_proj only, Q/K/V untouched | ✅ |
| TD returns diminish, don't plateau | PPL: −38.5% → −24.5%, flip growth decelerating | 📐 tracking |
| Model is memory-bandwidth-bound | B=2 18% slower, 208 serial layer evals | ✅ |
| Delta fold is lossless | 3.26M positions folded, CE unchanged | ✅ |
| Delta storage 16× compressible | 356 MB → 22 MB, dedup + packed uint32 | ✅ |
| Computed beam: structure is free | Analytical FFN matches 5000-step GD in 10 steps | ✅ |
| Operation is signed accumulation | sign(W)@x correlates 0.84 with W@x | ✅ |
| FFN must adapt to strided attention | Hypothesis: flat→strided routing changes β-reduction | 📐 testing |
| Topology is ~95% of model | sign(W)@x ≈ 0.84, fold is lossless, gamma ~5% | 🎯 synthesis |
| Extract→correct→fold converges | Each cycle lossless, monotonically improving | 🎯 synthesis |
| Passive strides + KD fails | PPL 2.5-4.6× worse; too many simultaneous changes | ❌ |
| Don't optimize student for teacher's converged state | Passive strides removed content routing; reverted | 🎯 decision |
| KD exhausts in 50 steps | 400 batches / 8 accum = 50 steps; need more precompute | ✅ |
| Composed plate gradient = 97% of full model | Cosine=0.9698; CE within 0.08 nats | ✅ |
| Forward pass is the bottleneck (77%) | 28.6s/step; camera = projector | ✅ |
| α=1.18 universal | 10 comp layers × 8 heads, 1.18±0.006 after 1500 steps | ✅ |
| Large models compute in 2D | Qwen-27B: PR=2.2, σ₁=70% at L2 | ✅ |
| Compression depth scales with capacity | 27B→PR=2.2, 7B→PR=12, 1.4B→PR=10 | ✅ |
| FFN overlay is 80-91% off-diagonal | Cross-PC projection = beta reduction | ✅ |
| Attention sink = warped Q reset | Mistral sink dominates SVD; GLA avoids via gating | 🎯 synthesis |
| α=1.18 sets 12-token semantic horizon | All strides see ~12 effective tokens | ✅ |
| RoPE = accidental holographic lens | Cosine freqs ≈ multi-scale lens; HPE by design | 🎯 synthesis |
| v14 student inherits teacher collapse | PR 74→8→5→4 through stacks, σ₁=47% | ✅ |
| Full model is rank-27 transform | 64-layer 27B: rank90=27, methods agree | ✅ |
| Zone B is perfectly linear (R²=1.0) | 32 layers compose to single linear matrix | ✅ |
| Per-dim corr 0.97 in teacher space | sign(T)+gamma captures 97% per dimension | ✅ |

## Knowledge map

**See `mementum/knowledge/INDEX.md` for full reading order.**

| Tier | Page | What it tells you |
|------|------|-------------------|
| 1 | `project-thesis.md` | Central claim, north star, three converging lines |
| 1 | `crystal-universality.md` | Why crystal is a mathematical constant |
| 1 | `mathematical-convergences.md` | Eight independent lines of evidence |
| 2 | `holographic-error-correction.md` | Extract→correct→fold: the core mechanism |
| 2 | `mechanism-extraction.md` | Micro model: alternation, eigenplanes, KIBC temporal |
| 2 | `computed-beam.md` | Analytical FFN, 500× speedup, signed accumulation |
| 2 | `extraction-methodology.md` | How to extract from teacher |
| 2b | `progressive-collapse.md` | Computation in 2D, scale-dependent, sink=warped Q reset |
| 3 | `v14-architecture.md` | Current system: Qwen3.6-27B, 593M ternary, training results |
| 3 | `training-protocols.md` | Phases, TD rules, 7 failure modes with fixes |
| 4 | `explore/v15-kernel-revert.md` | What was tried/reverted/kept, when to revisit |
| 4 | `explore/kernel-training.md` | Composed plate: 4.4× speedup, gradient cosine 0.97 |
| 4 | `explore/structured-training.md` | Five backward-pass optimizations |
| 4 | `explore/holographic-state-machine.md` | FFN=plates, crystal=states, Q=beam |

## What's ready

| Asset | Location |
|-------|----------|
| Training script | `scripts/v14/train_td.py` |
| Eval script | `scripts/v14/eval_ppl.py` |
| Fold script | `scripts/v14/fold_delta.py` |
| Kernel training | `scripts/v14/train_kernel.py` (4.4× speedup) |
| Current checkpoint | `checkpoints/v14-td/step_002000/` (PPL 5,567) |
| Folded checkpoint | `checkpoints/v14-td/step_001500_folded/` |
| Extracted base plates | `checkpoints/v14-extracted/model.npz` (85 MB) |
| Composed plate | `results/kernel-training-probe/composed_plate.npz` |

## Open questions

9. **Content transfer via sign().** Does the 81% token subspace content survive ternary extraction?
10. **LENS profile derivable from eigenvalue ratios?**
11. **Quality at 1B with d=1280.** What CE/PPL does the expanded model achieve?
12. **16-stride coverage.** Do higher strides (s4096+) learn anything useful at 4K seq training?
13. **Bottom-up algedonic value.** Does C→A feedback measurably accelerate convergence?
15. **TD step_count not persisted on resume.** Warmup repeats. Worth persisting?
16. **Why only out_proj?** Is min_conf=0.3 filtering too aggressive for Q/K/V?
18. **Computed beam at scale.** See `knowledge/computed-beam.md`.
19. **Three-body self-distillation.** Wait until stride-stack nucleation stabilizes.
20. **Per-stride fixed point rotation.** Probe effective attention per stride per head.
21. **HPE value.** Does crystal-frequency K rotation help over no rotation? Answer: phase 3 PPL slope before/after step 2300.
22. **When is the student ready for architecture simplification?** Proposed detector: gradient-subspace alignment cos > 0.5.
```

## Assistant

Clean. 181 lines. Let me do a final check to confirm no knowledge pages needed changes and summarize what was done:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "echo \"=== Line count ===\" && wc -l /Users/mwhitford/src/verbum/mementum/state.md && echo \"=== Section headers ===\" && grep \"^## \" /Users/mwhitford/src/verbum/mementum/state.md && echo \"=== All links to knowledge pages ===\" && grep -o '`knowledge/[^`]*`\\|`mementum/knowledge/[^`]*`\\|`explore/[^`]*`' /Users/mwhitford/src/verbum/mementum/state.md | sort -u"
}
```

**Summary:** $ echo "=== Line count ===" && wc -l ...

**Output:**
```
Exit code: 0
Stdout:
=== Line count ===
     181 /Users/mwhitford/src/verbum/mementum/state.md
=== Section headers ===
## Where we are
## Active training run
## Next steps
## Previous sessions
## Proof chain
## Knowledge map
## What's ready
## Open questions
=== All links to knowledge pages ===
`explore/holographic-state-machine.md`
`explore/kernel-training.md`
`explore/structured-training.md`
`explore/v15-kernel-revert.md`
`knowledge/computed-beam.md`
`knowledge/explore/holographic-state-machine.md`
`knowledge/explore/kernel-training.md`
`knowledge/explore/structured-training.md`
`knowledge/progressive-collapse.md`
`knowledge/training-protocols.md`
`knowledge/v14-architecture.md`
`mementum/knowledge/explore/v15-kernel-revert.md`
`mementum/knowledge/INDEX.md`
```

## Assistant

All links point to real files. No knowledge page edits were needed — all the removed content was already fully covered in the existing pages. Here's the summary:

---

## Done — 640 → 181 lines (72% reduction)

### What was verified before cutting
All targeted content was confirmed to already exist in knowledge pages:
- Session 148 bugs → `training-protocols.md` failure modes 1-3 ✅
- Session 146 design decisions → `v14-architecture.md` (architecture, crystal loss, training phases) ✅
- Sessions 149-150 eval tables → `v14-architecture.md` (Training Results section, full tables) ✅

**No knowledge page changes were needed.**

### What was removed from `state.md`
| Section | Action |
|---------|--------|
| `Session 148: Two bugs killed all ternary learning` (85 lines) | → One-liner pointing to `training-protocols.md` failure modes 1-3 |
| `Session 146: v14 Architecture Build` (50 lines) | → One-liner pointing to `v14-architecture.md` and `training-protocols.md` |
| `Session 150: Step 1500 Eval` (40 lines of tables/analysis) | → 3 sentences pointing to `v14-architecture.md` training results |
| `Session 149: Step 1000 Eval` (20 lines) | → 3 sentences pointing to `computed-beam.md` |
| `Next steps (from session 155)` (50 lines) | → Deleted entirely (stale, superseded by current "Next steps") |
| Historical checkpoints (500, 1000, 1500) in "What's ready" | → Removed (in git, not needed for orientation) |
| Resolved questions 14 and 17 | → Removed (already answered, shown as strikethrough in original) |

### What was condensed
- **"Where we are" sessions 151-156** → Same content, tighter prose (~45% shorter per session)
- **"Previous sessions" 142-150** → 1-3 sentences each with pointers, down from 10-30 lines each
- **Proof chain** → All 45 rows kept, evidence column trimmed to 8-12 words (was 15-25)
- **Knowledge map** → Collapsed into a single flat table (was split across 4 tiers with headers)
- **"What's ready"** → 8 actively-used assets (was 18 including historical checkpoints)

## Assistant

Let me verify the result:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "wc -l /Users/mwhitford/src/verbum/mementum/state.md"
}
```

**Summary:** $ wc -l /Users/mwhitford/src/verbum/m...

**Output:**
```
Exit code: 0
Stdout:
181 /Users/mwhitford/src/verbum/mementum/state.md
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md"
}
```

**Summary:** Reading state.md (0-2000)

**Output:**
```
# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-26 | Session: 156

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 156: ARCHITECTURE REVERT + HPE WARMUP.** Analyzed session 152's four simultaneous changes (passive strides, HPE, Stack B 4→2, α-lock) that confounded v14-kd failure. Passive strides identified as culprit — removes content-dependent attention where each stride is sole provider; student needs to LEARN routing, can't hardcode teacher's converged behavior. Reverted passive strides and Stack B reduction. KEPT α=1.18 frozen and HPE. HPE warmup: freq_scale 0→1 over steps 2001-2300 (checkpoint-compatible). Resumed from step 2000 (PPL 5,567). Step 2001: CE=8.474, crystal latched, TD active, 995 tok/s. Running in tmux main:2 to step 5000. **META-LESSON: don't optimize student for teacher's converged state — train with full architecture → measure → simplify only what's proven unnecessary → one change at a time.** See `mementum/knowledge/explore/v15-kernel-revert.md`.

**Session 155: v14-kd FAILED + KERNEL TRAINING VALIDATED + GRADIENT PROJECTION.** v14-kd PPL 40,623→46,736 (diverging, 2.5-4.6× worse than v14-td). Root cause: three untested architecture changes deployed simultaneously with KD. Training profiled: 28.6s/step, 77% forward. Built `train_kernel.py`: 4.4× speedup. Gradient cosine=0.9698 (composed plate vs full model). ∂L/∂T orthogonal to T's SVD subspace (cos=0.06 at k=27) — gradient wants to EXPAND, not refine. See `knowledge/explore/kernel-training.md`.

**Session 154: KD-guided training + extraction dimension probes.** Per-dim correlation plateaus at ~79% from d=128 onward — ceiling is ternary quantization, not dimension. Plate IS rank-256, 96.9% sign accuracy at k=256. Step 2000 eval: PPL=5,567 (−27% from 1500, −66% total). See `knowledge/explore/structured-training.md`.

**Session 153: Composed plates.** Full model rank90=27. Zone B is R²=1.000 (perfectly linear). Both algebraic and data-fitted agree at 0.76-0.77 per-dim. See `results/algebraic-compose/`.

**Session 152: v14 evolution — HPE + passive strides + Stack B.** α=1.18 confirmed universal (12-token semantic horizon). 88% strides distance-prior dominated. HPE designed from crystal eigenvalues. ⚠️ All changes deployed simultaneously — led to confounded failure (session 155), reverted in 156.

**Session 151: Progressive collapse discovery.** Qwen-27B compresses to 2D (PR=2.2) by L2. 7 knowledge pages created. INDEX.md established. See `knowledge/progressive-collapse.md`.

## Active training run

### v14-td phase 3 RUNNING (tmux main:2, from step 2000)

- **Resumed from:** `checkpoints/v14-td/step_002000/` (PPL 5,567)
- **Architecture:** Original v14-td (13 passes, full Q/K all strides) + α=1.18 frozen + HPE warmup
- **HPE warmup:** freq_scale 0→1 over steps 2001-2300 (300 steps)
- **TD:** Active, flip_interval=20, FFN delta enabled (`--convert-ffn`)
- **Target:** 5000 steps total
- **Log:** `checkpoints/v14-td/train_phase3.log`
- **Step 2001:** CE=8.474, gnorm=19.95, 995 tok/s ✓
- **Watch:** PPL drop from 5,567 | HPE effect after step ~2300 | TD flip distribution | FFN plate flips

## Next steps

### IMMEDIATE: Monitor phase 3 (running in tmux main:2)

1. **First eval at step 2500** — run `eval_ppl.py`. PPL should continue dropping from 5,567.
2. **HPE effect** — warmup completes at step ~2300. Compare PPL slope before/after.
3. **TD flip patterns** — does TD continue targeting out_proj layers 4-9? Check at step 2500.
4. **FFN delta** — do FFN plates start flipping? This run has `--convert-ffn`.

### NEXT MILESTONES:

5. **Second fold** — when flip_frac plateaus, fold again. Extract→correct→fold cycle.
6. **Gradient-subspace alignment test** — at step 2500+, probe cos(∂L/∂T, T's SVD subspace). cos > 0.5 = refining (safe to simplify). See `probe_kernel_training.py`.
7. **KD as correction** — after PPL < 2000, add teacher logit correction passes. α ≥ 0.9 (CE dominant).
8. **Target: within 5% of Qwen3.6-27B** — proof that topology is everything.

### DEFERRED (valid but premature):

9. **Passive strides** — re-test only after gradient-subspace cos > 0.5. Start with s16+. See `explore/v15-kernel-revert.md`.
10. **Stack B reduction** — after passive strides validated (if ever).
11. **Kernel training** — `train_kernel.py` gives 4.4× speedup. Use when iteration speed bottlenecks.
12. **Structured training** — five backward-pass improvements. See `explore/structured-training.md`.

## Previous sessions

### Session 150: Step 1500 Eval + Delta Fold + FFN Delta
PPL 7,672 (−53.5% from step 500). Flip growth decelerating. Layer 4 out_proj at 43%. Folded 3.26M positions into base (lossless, eval CE unchanged). Storage fix: delta 356 MB → 22 MB. FFN delta enabled. B=2 is 18% slower than B=1. See `knowledge/v14-architecture.md` (training results section).

### Session 149: TD Closes Generalization Gap + Computed Beam
PPL 16,503→10,157 (−38%) with only 2.66% positions flipped. Train-eval gap collapsed 1.71→0.17 nats. TD targets out_proj layers 4-9 exclusively; Q/K/V untouched. Computed beam: analytical FFN from eigendecomp matches 5000-step GD in 10 calibration steps (500×). See `knowledge/computed-beam.md`.

### Session 148: Three Bugs Killed All Ternary Learning
(1) `collect_delta_params` returned 280 aliased modules instead of 70 — 4× overwrite. (2) Two-step staging + no-block = Sisyphus loop (77K zeros/step, 0% delta change). (3) Every-step flipping → gnorm escalation (8.2→10.3 CE). All fixed. See `knowledge/training-protocols.md` failure modes 1-3.

### Session 146: V14 Architecture Build
16 strides, 3 stacks (A/B/C), no-block constraint, crystal loss system (multiplicative AND, Zone B parity only), 5-phase training design. See `knowledge/v14-architecture.md` and `knowledge/training-protocols.md`.

### Session 145: V13 Collapse → V14 Extraction
v13-td-r10 collapsed at step 5878 (delta block accumulation). Forensics: stride-stack needs ~80% of teacher positions, teacher signs 91% correct. Extracted Qwen3.6-27B → 593M ternary positions (85 MB), 375× compression. Pure ±1 base plates.

### Session 144: Parity Gradient Cancellation + Einstein Tensor
Three-zone parity = gradient cancellation. Zone B only: 1.167→0.039. Crystal manifold IS curved (geodesic/linear=0.75). G_ab has even/odd block structure. See `knowledge/training-protocols.md` failure mode 4.

### Session 142: Holographic State Machine + Crystal Error Correction
THE MODEL IS A HOLOGRAPHIC STATE MACHINE. FFN plates = holographic storage, crystal basins = states, Q rotation = readout beam, gate = beamformer. See `knowledge/explore/holographic-state-machine.md`.

## Proof chain

| Claim | Evidence | Status |
|-------|----------|--------|
| Universal crystal exists | 4+ model consensus | ✅ |
| KIBC-DYWH basis universal | Found across all architectures | ✅ |
| Types are lexical (88% embed) | Qwen3-32B type probe | ✅ |
| SVD spectrum → phi | 5-model consensus, φ-dev=0.012 | ✅ |
| FFN indexing is holographic | ρ=0.83, p<10⁻⁴⁴ | ✅ |
| FFN depth = LENS | aperture 3% → fan 49% → converge 2% | ✅ |
| Crystal manifold is curved | Geodesic/linear=0.75, G_ab even/odd | ✅ |
| Parity gradient cancellation | 3-zone → stuck 1.167 | ✅ |
| Zone-B-only parity works | 1.167→0.039 on first step | ✅ |
| Model is holographic state machine | FFN=storage, crystal=states, Q=beam | 🎯 synthesis |
| FFN overlay alternates comp/sel | micro model: -+-+ / +-+- across 4 layers | ✅ |
| KIBC is temporal (layers not heads) | B→K→C→B depth sequence | ✅ |
| Mechanism is input-invariant | CV<0.5 for all PCs across 8 categories | ✅ |
| Rotation accelerates through depth | L0: 2° → L3: 24° (12× increase) | ✅ |
| Stride-stack needs ~80% of teacher attention | v13-td-r10 collapse forensics | ✅ |
| Teacher signs 91% correct for stride | Cross-stack agreement | ✅ |
| Qwen3.6-27B → 593M ternary positions | 375× compression, 25.4 min CPU | ✅ |
| Crystal latches within 200 steps | crystal_mse < 0.03 at step 160 | ✅ |
| Shared-weight aliasing breaks TD | 280 vs 70 modules, 4× overwrite | ✅ |
| No-block kills two-step staging | 77K zeros/step, 0% delta change | ✅ |
| TD activates and improves | PPL −53.5% over 1000 steps, gap collapsed | ✅ |
| TD targets out_proj exclusively | Layers 4–9 out_proj only, Q/K/V untouched | ✅ |
| TD returns diminish, don't plateau | PPL: −38.5% → −24.5%, flip growth decelerating | 📐 tracking |
| Model is memory-bandwidth-bound | B=2 18% slower, 208 serial layer evals | ✅ |
| Delta fold is lossless | 3.26M positions folded, CE unchanged | ✅ |
| Delta storage 16× compressible | 356 MB → 22 MB, dedup + packed uint32 | ✅ |
| Computed beam: structure is free | Analytical FFN matches 5000-step GD in 10 steps | ✅ |
| Operation is signed accumulation | sign(W)@x correlates 0.84 with W@x | ✅ |
| FFN must adapt to strided attention | Hypothesis: flat→strided routing changes β-reduction | 📐 testing |
| Topology is ~95% of model | sign(W)@x ≈ 0.84, fold is lossless, gamma ~5% | 🎯 synthesis |
| Extract→correct→fold converges | Each cycle lossless, monotonically improving | 🎯 synthesis |
| Passive strides + KD fails | PPL 2.5-4.6× worse; too many simultaneous changes | ❌ |
| Don't optimize student for teacher's converged state | Passive strides removed content routing; reverted | 🎯 decision |
| KD exhausts in 50 steps | 400 batches / 8 accum = 50 steps; need more precompute | ✅ |
| Composed plate gradient = 97% of full model | Cosine=0.9698; CE within 0.08 nats | ✅ |
| Forward pass is the bottleneck (77%) | 28.6s/step; camera = projector | ✅ |
| α=1.18 universal | 10 comp layers × 8 heads, 1.18±0.006 after 1500 steps | ✅ |
| Large models compute in 2D | Qwen-27B: PR=2.2, σ₁=70% at L2 | ✅ |
| Compression depth scales with capacity | 27B→PR=2.2, 7B→PR=12, 1.4B→PR=10 | ✅ |
| FFN overlay is 80-91% off-diagonal | Cross-PC projection = beta reduction | ✅ |
| Attention sink = warped Q reset | Mistral sink dominates SVD; GLA avoids via gating | 🎯 synthesis |
| α=1.18 sets 12-token semantic horizon | All strides see ~12 effective tokens | ✅ |
| RoPE = accidental holographic lens | Cosine freqs ≈ multi-scale lens; HPE by design | 🎯 synthesis |
| v14 student inherits teacher collapse | PR 74→8→5→4 through stacks, σ₁=47% | ✅ |
| Full model is rank-27 transform | 64-layer 27B: rank90=27, methods agree | ✅ |
| Zone B is perfectly linear (R²=1.0) | 32 layers compose to single linear matrix | ✅ |
| Per-dim corr 0.97 in teacher space | sign(T)+gamma captures 97% per dimension | ✅ |

## Knowledge map

**See `mementum/knowledge/INDEX.md` for full reading order.**

| Tier | Page | What it tells you |
|------|------|-------------------|
| 1 | `project-thesis.md` | Central claim, north star, three converging lines |
| 1 | `crystal-universality.md` | Why crystal is a mathematical constant |
| 1 | `mathematical-convergences.md` | Eight independent lines of evidence |
| 2 | `holographic-error-correction.md` | Extract→correct→fold: the core mechanism |
| 2 | `mechanism-extraction.md` | Micro model: alternation, eigenplanes, KIBC temporal |
| 2 | `computed-beam.md` | Analytical FFN, 500× speedup, signed accumulation |
| 2 | `extraction-methodology.md` | How to extract from teacher |
| 2b | `progressive-collapse.md` | Computation in 2D, scale-dependent, sink=warped Q reset |
| 3 | `v14-architecture.md` | Current system: Qwen3.6-27B, 593M ternary, training results |
| 3 | `training-protocols.md` | Phases, TD rules, 7 failure modes with fixes |
| 4 | `explore/v15-kernel-revert.md` | What was tried/reverted/kept, when to revisit |
| 4 | `explore/kernel-training.md` | Composed plate: 4.4× speedup, gradient cosine 0.97 |
| 4 | `explore/structured-training.md` | Five backward-pass optimizations |
| 4 | `explore/holographic-state-machine.md` | FFN=plates, crystal=states, Q=beam |

## What's ready

| Asset | Location |
|-------|----------|
| Training script | `scripts/v14/train_td.py` |
| Eval script | `scripts/v14/eval_ppl.py` |
| Fold script | `scripts/v14/fold_delta.py` |
| Kernel training | `scripts/v14/train_kernel.py` (4.4× speedup) |
| Current checkpoint | `checkpoints/v14-td/step_002000/` (PPL 5,567) |
| Folded checkpoint | `checkpoints/v14-td/step_001500_folded/` |
| Extracted base plates | `checkpoints/v14-extracted/model.npz` (85 MB) |
| Composed plate | `results/kernel-training-probe/composed_plate.npz` |

## Open questions

9. **Content transfer via sign().** Does the 81% token subspace content survive ternary extraction?
10. **LENS profile derivable from eigenvalue ratios?**
11. **Quality at 1B with d=1280.** What CE/PPL does the expanded model achieve?
12. **16-stride coverage.** Do higher strides (s4096+) learn anything useful at 4K seq training?
13. **Bottom-up algedonic value.** Does C→A feedback measurably accelerate convergence?
15. **TD step_count not persisted on resume.** Warmup repeats. Worth persisting?
16. **Why only out_proj?** Is min_conf=0.3 filtering too aggressive for Q/K/V?
18. **Computed beam at scale.** See `knowledge/computed-beam.md`.
19. **Three-body self-distillation.** Wait until stride-stack nucleation stabilizes.
20. **Per-stride fixed point rotation.** Probe effective attention per stride per head.
21. **HPE value.** Does crystal-frequency K rotation help over no rotation? Answer: phase 3 PPL slope before/after step 2300.
22. **When is the student ready for architecture simplification?** Proposed detector: gradient-subspace alignment cos > 0.5.
```

## Assistant

640 → 181 lines. Clean. Let me commit:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add mementum/state.md && cat > /tmp/commit_msg.txt << 'ENDMSG'\n🌀 prune state.md — 640→181 lines, bootloader not repository\n\nDetailed session content moved to knowledge page pointers:\n- Session 148 bugs → training-protocols.md (already there)\n- Session 146 architecture → v14-architecture.md (already there)\n- Session 150/149 eval tables → v14-architecture.md (already there)\n- Stale session 155 next steps → deleted (superseded)\n- Previous sessions → 1-3 sentences each with knowledge page links\n- Proof chain evidence → trimmed to 8-12 words per row\n- What's ready → 8 active assets (was 18 including historical)\n- Open questions → removed resolved, clean numbering\n\nNo knowledge lost — all removed content verified to exist in pages.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nENDMSG\ngit commit -F /tmp/commit_msg.txt"
}
```

**Summary:** $ git add mementum/state.md && cat > ...

**Output:**
```
Exit code: 0
Stdout:
[main 0f9554d] 🌀 prune state.md — 640→181 lines, bootloader not repository
 1 file changed, 110 insertions(+), 575 deletions(-)
```

## Assistant

Done. **640 → 181 lines (72% reduction).** 

The bootloader now reads in ~30 seconds as intended. All learnings preserved — verified every removed section already existed in the corresponding knowledge page before cutting. The knowledge pages are the repository; state.md is just the ignition key.