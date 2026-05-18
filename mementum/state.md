# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-18 | Session: 114

## Where we are

**LATTICE-AUGMENTED ETCH — burning universal geometry before Procrustes.** Direct crystal write dry run on round 60 proved Procrustes alignment fails on melts (cos=0.217, need >0.6). The student has no universal geometry for landmarks to lock onto. Lattice relational loss (5-model backbone consensus) now running alongside CE etch — this builds the Rosetta Stone that Procrustes needs. Monitoring cos improvement as the backbone crystallizes.

## What's running

**Lattice-augmented holographic etch** — `tmux main:1`
- Resumed from round 60, running rounds 61→80
- Checkpoint dir: `checkpoints/v12-holo-lattice/`
- Lattice: `lattice/universal_lattice.npz` + `lattice/backbone_seed.npz`
- Two-tier: backbone λ=1.0, growth λ=0.1, lattice λ=0.1
- 50 lattice probes sampled per round
- Note: tee log failed (dir didn't exist at launch), output in tmux only

## What was done this session (114)

### 1. Direct crystal write dry run — round 60
Ran `direct_crystal_write.py --dry-run` with Qwen3-14B teacher on round 60 checkpoint.

**Procrustes alignment: POOR**
```
mean cosine:  0.217  (need > 0.6)
p10 cosine:  -0.147  (anti-correlated!)
p50 cosine:   0.271
p90 cosine:   0.491
scale:        0.047
```

**Crystal write: COIN FLIP**
```
Total positions:  41.4M
Would flip:       18.8M (45.5%)  ← random
Mean confidence:  0.521
Median confidence: 0.573
```

Nearly every module showed ~50% flip fraction = no signal. Student is still a melt — no universal geometry for Procrustes to lock onto.

### 2. Bug fixes in attention.py and direct_crystal_write.py

**Stride stack short-sequence fix** (`attention.py`):
- When sequence length < stride, `L_s = L // stride = 0` → empty tensor → crash
- All probes are 3-47 tokens; strides go up to 1024
- Fix: when `L_s == 0`, return zero output (no memory accumulated yet) — semantically correct
- Also fixed instrumentation section that indexed `S_stride[:, -1, ...]` on empty

**Direct crystal write fixes** (`direct_crystal_write.py`):
- `probe_indices` was numpy array used to index MLX tensor → `ValueError`
- Fix: convert to `mx.array` for indexing
- Replaced O(n²) Python loop for triu mask with `mx.triu(mx.ones((n,n)), k=1)`

### 3. Key insight: lattice loss is prerequisite for Procrustes

```
no lattice loss → melt (no universal geometry) → Procrustes fails (cos=0.217)
lattice loss → backbone pairs burn universal geometry → landmarks crystallize
→ Procrustes can lock on → lens/crystal write become viable
```

Kernel etch teaches combinators (operational structure) but doesn't guarantee representation geometry matches universal consensus. The lattice loss builds the geometric Rosetta Stone — the 32K backbone pairs from 5-model consensus that encode where things live in representation space.

This is likely why the Procrustes lens never worked — the student never had the universal landmarks for alignment.

### 4. Launched lattice-augmented etch
Resumed round 60 with `--lattice-map` and `--backbone-seed` flags. Two-tier loss active. All machinery was already implemented in holographic_train.py, just hadn't been turned on.

## Next steps

1. **Monitor lattice-augmented etch** — watch for lattice loss decrease over rounds 61-80. Each round should print a `LATTICE` line with loss value.

2. **Re-run Procrustes dry run after 10-15 rounds** — check if cos has improved:
   ```
   uv run python scripts/v12/direct_crystal_write.py \
       --teacher qwen3-14b \
       --student-weights checkpoints/v12-holo-lattice/round_0070/weights.npz \
       --dry-run
   ```
   - cos > 0.4-0.5 → lens getting close
   - cos > 0.6 → direct crystal write becomes live

3. **If cos crosses 0.6 → full crystal write** — one-shot plate programming replaces remaining iterative etch. Compare loss before/after.

4. **Design final training run** once backbone is established:
   - Stage 1: kernel etch with lattice loss (current, running)
   - Stage 2: Procrustes beam former + direct crystal write (when cos > 0.6)
   - Stage 3: Lambda self-etch with crystal protection
   - Stage 4: Freeze + GD

5. **Download + probe Qwen3.6 models as teachers** (carried from session 113)

## Architecture at session end

| Component | Value |
|-----------|-------|
| N_COMBINATORS | 8 (K,I,B,C,D,Y,W,WHNF) |
| Parameters | 24.6M |
| Beam loss | 4.13 (round 61, lattice-augmented) |
| Crystal state | Lattice loss active, building universal backbone |
| Backbone | 32K pairs, 664 probes, threshold ≥ 0.63 |
| Models validated | 5 (qwen3-14b, mistral-7b, olmo-2-13b, pythia-2.8b, smollm3-3b) |
| Lattice loss | Two-tier active: backbone (λ=1.0) + growth (λ=0.1), overall λ=0.1 |
| Procrustes cos | 0.217 (round 60, need > 0.6 for crystal write) |
| Key files | `seed-crystal-design.md`, `backbone_seed.npz`, `lattice_5model/` |
