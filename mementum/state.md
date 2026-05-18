# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-18 | Session: 114

## Where we are

**LATTICE AS WHISPER — relational hint from the tensor, not a training objective.** Direct crystal write on round 60 showed Procrustes fails (cos=0.217). First lattice attempt (separate backward, lambda=0.1) collapsed the model at round 65 — lattice gradients fought CE in direction accumulators. Solution: lattice is 1 pass among 400 CE passes per round. The accumulator sees 401 gradient samples; lattice is a consistent whisper that never cancels, while CE noise partially cancels across ops. Over rounds, the universal geometry slowly emerges from the noise floor. Not forced. Found.

## What's running

**Lattice-whisper holographic etch v2** — `tmux main:1`
- Resumed from round 60, running rounds 61→80
- Checkpoint dir: `checkpoints/v12-holo-lattice-v2/`
- Lattice: 1 pass per round (50 probes) vs 400 CE passes (8 ops × 50 batches)
- Two-tier: backbone λ=1.0, growth λ=0.1, lattice λ=0.1
- Effective lattice weight: ~0.1/400 = 0.00025 of CE signal
- This is the whisper approach — should NOT collapse

## What was done this session (114)

### 1. Direct crystal write dry run — round 60
Ran `direct_crystal_write.py --dry-run` with Qwen3-14B teacher.
- Procrustes cos=0.217 (need >0.6), 45.5% flip = random noise
- Student has no universal geometry for Procrustes to lock onto

### 2. Bug fixes
- **attention.py**: stride stack crash when L < stride (probes 3-47 tokens, strides up to 1024). Zero output when L_s=0.
- **direct_crystal_write.py**: numpy indexing into MLX arrays, O(n²) triu loop → mx.triu
- **holographic_train.py**: same numpy/MLX indexing and triu fixes in lattice_alignment_loss

### 3. First lattice attempt — COLLAPSED
Lattice as separate backward pass into direction accumulators (lambda=0.1).
```
Round 62: CE ~4.1-5.5, lattice 0.0077, beam 4.77  ← healthy
Round 64: CE ~4.2,     lattice 0.0083, beam 10.52  ← beam degrading
Round 65: CE 6-13,     lattice 0.072,  beam 33.35  ← explosion
Round 66: CE ~22                                    ← total collapse
```
**Cause**: lattice gradients fight CE in the accumulators. CE wants plates for next-token prediction, lattice wants plates for relational geometry. Separate passes = conflicting signals on the same plates.

### 4. Key insight: lattice as whisper, not training objective

The lattice targets are KNOWN FIXED NUMBERS from 5-model consensus. The relational loss computes the EXACT delta — "move 3 yards left, 1 yard forward." One pass, known answer.

The fix: lattice is 1 accumulator pass among 400 CE passes. It cannot overpower CE. But it never cancels (same direction every round), while CE noise partially cancels across ops. Over many rounds, the consistent whisper accumulates into signal.

```
CE signals:     K wants X, B wants Y → partially cancel (noise)
Lattice signal: always points toward universal geometry → never cancels
Result:         universal geometry slowly emerges from noise floor
```

This is information from the tensor, not a competing objective.

### 5. Qwen3.6-27B probed
- Downloaded and cached (55.6GB)
- 64 layers, d=5120, hybrid attention (full every 4th layer, linear between)
- `model.model.layers` works (Qwen3_5DecoderLayer)
- RDMs extracted at 4 depths (0%, 25%, 50%, 75%)
- Added to MODELS registry in build_lattice_map.py and TEACHERS in direct_crystal_write.py
- Single-model extraction completed; need comparison script for consensus analysis
- Raw RDMs saved in `lattice/lattice_qwen36_27b/`

## Next steps

1. **Monitor v2 lattice-whisper etch** — watch for stability (should NOT collapse).
   Key metrics: CE loss stays ~4-5, lattice loss trends down slowly, beam loss stable.

2. **Compare Qwen3.6-27B RDMs against 5-model consensus** — write comparison script
   to measure agreement at each depth. Larger model = sharper crystal = more lattice points?

3. **Re-run Procrustes dry run at round 70-75** — check if cos is climbing:
   ```
   uv run python scripts/v12/direct_crystal_write.py \
       --teacher qwen3-14b \
       --student-weights checkpoints/v12-holo-lattice-v2/round_0070/weights.npz \
       --dry-run
   ```

4. **Build 6-model consensus** — add Qwen3.6-27B to the lattice map for richer backbone

5. **If cos > 0.6 → full crystal write** — one-shot plate programming

## Architecture at session end

| Component | Value |
|-----------|-------|
| N_COMBINATORS | 8 (K,I,B,C,D,Y,W,WHNF) |
| Parameters | 24.6M |
| Beam loss | 4.77 (round 60 baseline) |
| Crystal state | Lattice whisper active (v2), building universal backbone |
| Backbone | 32K pairs, 664 probes, threshold ≥ 0.63 |
| Models validated | 5+1 (qwen3-14b, mistral-7b, olmo-2-13b, pythia-2.8b, smollm3-3b + qwen3.6-27b probed) |
| Lattice loss | Whisper: 1 pass / 400 CE passes, effective weight ~0.00025 |
| Procrustes cos | 0.217 (round 60, need > 0.6 for crystal write) |
| Key files | `seed-crystal-design.md`, `backbone_seed.npz`, `lattice_5model/`, `lattice_qwen36_27b/` |
