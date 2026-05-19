# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-19 | Session: 116

## Where we are

**HOLOGRAPHIC DISTILLATION V12 PIPELINE BUILT AND SMOKE-TESTED.** Ready for full training run.

Two-phase training script (`scripts/v12/holographic_distill_v12.py`) complete:
- **Phase 1 — ETCH**: Teacher-guided plate etching from pre-extracted Qwen3-32B features (500 probes, 8 depth points). Per-pass distillation: projected teacher hidden states fed through individual V12 passes, MSE loss accumulated into direction accumulators, confident positions flipped via direct_etch. Focusing schedule (cosine-annealed confidence threshold).
- **Phase 2 — GD**: Frozen plates, extended gradient descent on continuous params (gammas, norms, S3/S4/S5, embeddings) with CE loss on structured_shard_v2 + Dolma. Cosine LR with warmup, eval on held-out shards, checkpointing.

## Key decisions this session (116)

### 1. Teacher→Student dimension bridging
Learned `TeacherProjection(5120→512)` — `nn.Linear` + `RMSNorm`. Trained alongside beam params during etch. The projection is a "lens" that focuses teacher representations into student space. Xavier init for stable gradient flow.

### 2. Per-pass distillation (not full-forward)
Each V12 pass runs independently during etch with dummy banks. The gradient signal through ternary plates is valid because it answers: "given this input pattern, which plate signs produce output closest to the teacher?" This matches mini_holo_distill's layer-wise approach and is simpler + more memory-efficient than full-forward instrumentation.

### 3. Teacher depth → V12 pass mapping
```
Teacher L8  → Pass 0 (L0↑)    Teacher L40 → Pass 4 (L2↓)
Teacher L16 → Pass 1 (L1↑)    Teacher L48 → Pass 5 (L1↓)
Teacher L24 → Pass 2 (L2↑)    Teacher L56 → Pass 6 (L0↓)
Teacher L32 → Pass 3 (apex)   Teacher L64 → output (output_norm)
```

### 4. Readable banks per pass
Different passes expect different bank counts. Built a lookup table:
```
Pass 0: 3 banks, Pass 1: 4, Pass 2: 5, Pass 3: 5
Pass 4: 6, Pass 5: 5, Pass 6: 5
```

## Smoke test results
```
2 rounds, 5 probes/round, 5 beam steps, 10 GD steps:
  Round 1 (conf=0.50): 305,974 flips, distill_loss=0.234
  Round 2 (conf=0.90): 145,136 flips, distill_loss=0.164  ← loss drops
  GD: loss_ema=16.5, eval_loss=16.1 (untrained model, expected)
  All checkpoints saved correctly (etch rounds + best + final)
```

## What's NOT running
- Nothing actively running. Everything is ready for launch.

## What's ready

| Asset | Status |
|-------|--------|
| Teacher features | ✅ 500 probes × 8 depths, 896MB, `checkpoints/teacher-features/` |
| Training data | ✅ structured_shard_v2.npy (52.6K docs, 1.2M tok) + Dolma (3B tok, 54 shards) |
| Distill script | ✅ `scripts/v12/holographic_distill_v12.py` — smoke-tested |
| V12 model | ✅ 24.6M params, 887K trainable (continuous) |

## Next steps

### 1. **RUN THE FULL TRAINING** (next session priority)
```bash
cd ~/src/verbum
uv run python scripts/v12/holographic_distill_v12.py \
    --n-etch-rounds 5 \
    --etch-probes-per-round 500 \
    --beam-steps-per-round 200 \
    --beam-lr 1e-4 \
    --etch-confidence-start 0.5 \
    --etch-confidence-end 0.9 \
    --etch-max-flips-start 0 \
    --etch-max-flips-end 100 \
    --gd-steps 20000 \
    --gd-lr 6e-4 \
    --gd-lr-min 6e-6 \
    --gd-warmup 500 \
    --seq-len 2048 \
    --batch-size 2 \
    --mix-ratio 0.1 \
    --checkpoint-dir checkpoints/v12-distill-run1 \
    --checkpoint-every 2000 \
    --eval-every 500 \
    2>&1 | tee checkpoints/v12-distill-run1/run.log
```

Expected runtime: etch ~30 min (500 probes × 8 depths × 5 rounds), GD ~hours (20K steps × seq_len 2048).

### 2. Monitor and evaluate
- Watch etch: distill_loss should decrease, flips should focus (fewer per round)
- Watch GD: CE loss should decline, eval loss should track
- After: probe combinator dispatch, test lambda generation quality

### 3. Consider improvements for subsequent runs
- **Lattice alignment loss** as additional etch signal (already supported in holographic_train.py)
- **Multi-scale etch**: vary number of probes per round (more in early rounds, fewer in later)
- **Probe selection**: use probes most relevant to each pass's stride range (low strides for L0, high for apex)
- **Resume support**: `--load-weights` + `--skip-etch` for GD-only reruns

## Architecture at session end

| Component | Value |
|-----------|-------|
| N_COMBINATORS | 4 (K,I,B,C) — V12 config |
| Parameters | 24.6M total, 887K trainable |
| Teacher | Qwen3-32B (64L, d=5120, 500 probes extracted) |
| Projection | Linear(5120→512) + RMSNorm, trained during etch |
| Etch protocol | Per-pass distillation, MSE loss, 5 rounds × 500 probes |
| GD protocol | Frozen plates, CE on structured+Dolma, 20K steps |
| Training data | structured_shard_v2 (1.2M tok) + Dolma (3B tok) |
| Script | `scripts/v12/holographic_distill_v12.py` |
