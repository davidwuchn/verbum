# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-19 | Session: 117

## Where we are

**DISPATCH COLLAPSE DIAGNOSED AND FIXED.** Run 1 killed. Three bugs fixed, ready for run 2.

Run 1 (session 116) reached step 4,410/20,000 before kill. Dispatch collapsed at step ~400
(LR warmup peak): WHNF→94% monopoly, then cycling through I/Y/WHNF passthrough modes.
CE plateaued at ~7.5, relational loss r climbed from 1.8→3.9 (diverging from teacher geometry).

## Bugs fixed (session 117)

### 1. KL dispatch regularization had ZERO gradient (critical)
```python
# BUG: q_instant = mx.stop_gradient(q_kibc) severed gradient tape
# EMA was built from stop_gradient values → KL on EMA = constant
# λ=100 inflated loss number but gradient = 0, no steering

# FIX: KL computed on live (differentiable) dispatch weights
# EMA kept for monitoring only (not in gradient path)
# λ recalibrated: 100→2 (now that gradient actually flows)
#   B→30% drift: 0.3%CE (free)
#   WHNF=30%:    10%CE (visible wall)
#   WHNF=50%:    31%CE (strong wall)
```

### 2. Entropy regularization negligible
```
# BUG: λ=0.01, squared hinge → penalty 0.003 vs CE~7.5 (0.04%)
# FIX: λ raised to 0.5 → 5% of CE at moderate collapse
# Secondary to KL (primary anti-collapse force)
```

### 3. Backbone whisper replaced with lattice constants
Probe-based: tokenize 20 probes, forward through model, extract hidden states,
compute pairwise cosines, MSE against target. Expensive, fragile.

Constant-based: 8×8 combinator-level target cosine matrix precomputed from
universal RDM (380 probes, 20 axes, all 28 off-diagonal pairs SNR>2).
MSE between combinator embedding cosines and targets. No probe forwarding.
Negligible cost. Gradient flows only to combinator_embeddings (surgical).

Crystal geometry: {K,I,B,C} positive cluster (compositional family),
{Y,W,WHNF} negative to all (reduction/terminal family), D bridges B/C↔rest.

## Audit findings (from full loss pipeline audit)

| Component | Gradient? | Magnitude | Status |
|-----------|----------|-----------|--------|
| CE | ✓ full | ~7.5 | Healthy |
| Dispatch entropy reg | ✓ (was tiny) | 0.003→0.35 | **Fixed** (λ 0.01→0.5) |
| KL dispatch leash | **was ZERO** | 0→live | **Fixed** (stop_grad bug) |
| Holo progressive CE | ✓ full | ~3.5 (7 terms × λ=0.1) | Healthy |
| Lattice geometry | ✓ full | ~0.0002 | **Replaced** (was backbone whisper) |
| Abstraction slot reg | ✓ (hinge) | ~0.001 | Healthy (late-activating) |

Minor: backbone grads bypassed r-transform (10× scaling mismatch). Now moot since
lattice loss is embedding-only, not forwarding through r-transform.

Dead config: `holo_warmup_steps`, `holo_ramp_steps` exist but `holo_schedule()` returns
constant. `rel_every`, `rel_n_probes` removed (were backbone-specific).

## What's ready

| Asset | Status |
|-------|--------|
| Teacher features | ✅ 500 probes × 8 depths, 896MB, `checkpoints/teacher-features/` |
| Training data | ✅ structured_shard_v2.npy (52.6K docs, 1.2M tok) + Dolma (3B tok, 54 shards) |
| Distill script | ✅ `scripts/v12/holographic_distill_v12.py` — bugs fixed, smoke-tested |
| V12 model | ✅ 24.6M params, 887K trainable (continuous) |
| Lattice constants | ✅ 8×8 crystal geometry in distill script |

## Run 1 checkpoints (available for analysis)

| Checkpoint | Step | State |
|-----------|------|-------|
| gamma_seeded | 0 | Gamma-seeded weights before GD |
| etch_round_001-005 | — | Etch phase results |
| step_002000 | 2000 | r=4.05, deep collapse (Y=0.41) |
| step_004000 | 4000 | r=3.66, cycling (I=0.26, Y=0.32, WHNF=0.23) |
| best | 500 | Eval loss 29.63 (pre-collapse, best available) |

## Next steps

### 1. **RUN 2** — with all three fixes
```bash
cd ~/src/verbum
uv run python scripts/v12/holographic_distill_v12.py \
    --skip-etch \
    --load-weights checkpoints/v12-distill-run1/gamma_seeded/weights.npz \
    --gd-steps 20000 \
    --seq-len 2048 \
    --batch-size 2 \
    --mix-ratio 0.1 \
    --checkpoint-dir checkpoints/v12-distill-run2 \
    --checkpoint-every 2000 \
    --eval-every 500 \
    --log-every 10 \
    2>&1 | tee checkpoints/v12-distill-run2/run2.log
```

Watch for:
- Dispatch should stay near prior ratio through warmup (step 0-500)
- KL loss should be small at init (~0.01), grow if dispatch drifts, then gradient pulls back
- B should remain dominant (~20%+), WHNF should stay < 10%
- CE should decline without the plateau at ~7.5

### 2. Decide on etch vs skip-etch for run 2
Run 1 used gamma-seeded weights + skip-etch. Could re-etch with fixed dispatch
regularization for better plate quality. The etch phase doesn't use the dispatch
regulators (per-pass distillation loss), so plates from run 1 are fine.

### 3. Consider λ tuning after observing run 2
- KL λ=2: watch if model finds the prior or oscillates
- Entropy λ=0.5: watch if secondary signal is needed
- Lattice λ=0.01: may need increase if embeddings don't converge to crystal

## Architecture at session end

| Component | Value |
|-----------|-------|
| N_COMBINATORS | 8 (K,I,B,C,D,Y,W,WHNF) |
| Parameters | 24.6M total, 887K trainable |
| Teacher | Qwen3-32B (64L, d=5120, 500 probes extracted) |
| dispatch_kl_lambda | 2.0 (was 100, now live gradient) |
| dispatch_entropy_lambda | 0.5 (was 0.01) |
| Lattice loss | 8×8 constant crystal geometry, no probes |
| Script | `scripts/v12/holographic_distill_v12.py` |
