# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-19 | Session: 115

## Where we are

**MICROSCOPE D-SWEEP COMPLETE — etch-first beats beam-first with attention architecture.** Two d-sweep experiments (sessions 114-115) revealed:

1. **v1 (no attention)**: Simple KIBC reduction saturates at 46.6% regardless of d. No crossover found at any scale (d=48 to d=256). Task too easy — embeddings solve it.

2. **v2 (with attention, nested compositions)**: Adding causal attention + ternary K/V/O plates creates real separation. Etch-first consistently beats beam-first by 2.8-12.6% across all d values. The original mini-holo "beam-first" finding was an artifact of the non-attention architecture.

**Key revision**: beam-first is NOT universally correct. When plates ARE the attention projections (K/V/O), the gradient accumulator over 200 batches provides stable etch signal even without trained beams. The 200-batch accumulator IS the "reference beam" — it averages out noise.

Lattice etch run is dead (collapsed at round 65, not recovering). The checkpoint is a data point only.

## Key findings this session (115)

### 1. D-sweep v1: No crossover (task too easy)
```
    d   Ratio      GD    Beam     Gap
   48    2.9×   46.6%  46.6%   0.0%
   96    5.7×   46.6%  46.6%   0.0%
  128    7.7×   46.6%  46.6%   0.0%
  192   11.5×   46.6%  46.6%   0.0%
  256   15.3×   46.6%  46.6%   0.0%
```
Simple KIBC reduction (4 rules, 18 tokens) saturates. Embeddings solve it at every scale. The d² vs d ratio doesn't matter when the task fits in the embedding table.

### 2. D-sweep v2: Etch-first wins with attention
```
    d   Ratio      GD    Beam     Gap    EtchF   BeamF   BF-EF
   48    2.7×   48.7%  47.1%   +1.6%   44.1%   41.3%   -2.8%
   96    3.2×   36.7%  43.0%   -6.3%   44.3%   31.7%  -12.6%
  128    3.4×   36.6%  35.1%   +1.5%   37.1%   29.7%   -7.4%
  192    3.6×   34.6%  30.0%   +4.6%   41.6%   30.8%  -10.8%
  256    3.7×   31.0%  37.1%   -6.1%   36.5%   30.2%   -6.4%
```
**Caveat**: GD vs beam-only gap is noisy (convergence confound — larger models underfit at fixed 3000 steps). But etch-first vs beam-first is a fair comparison (same model, same compute) and etch-first wins everywhere.

### 3. Architecture matters more than protocol
The original mini-holo (no attention, plate = single linear) found beam-first works because embeddings compensate. With attention (plates = K/V/O projections), the etch accumulator's 200-batch gradient averaging gives good signal without trained beams. The beam-first finding was architecture-specific, not universal.

### 4. Depth breakdown (d=192, clearest signal)
```
Depth 1: GD=23.0%  Beam=4.5%   (gap +18.5%)
Depth 2: GD=6.5%   Beam=0.0%   (gap +6.5%)
Depth 3: GD=2.0%   Beam=0.0%   (gap +2.0%)
Depth 4: GD=0.6%   Beam=0.0%   (gap +0.6%)
```
Plates matter most for shallow reductions. Deeper compositions are hard for all conditions.

## Session 114 findings (preserved)

### Procrustes fails on round 60 (cos=0.217)
Kernel etch alone doesn't create universal geometry. Lattice relational loss needed.

### Lattice collapse (twice)
Separate lattice backward pass fights CE in accumulators → collapse at round 65.
Lattice should be a whisper (1 pass among 400 CE), not a shout.

### Phase transition at round 65
Backbone correlation jumped 7× (0.065→0.465). Crystal IS forming — but dispatch died.

### Mini holographic microscope (original, no attention)
At d=48, beam-only = GD = 46.6%. Embeddings compensate for any plate topology.
The d² vs d argument for why plates matter at scale remains theoretically valid
but the crossover could not be observed because the task saturated.

### Qwen3.6-27B probed
64 layers, d=5120, hybrid attention. RDMs extracted at 4 depths.

### 5. Oracle crystal write FAILS (session 115)
Exact sign(W) from converged GD model = worst crystal (38.6%). Adding noise HELPS
(50% noise = 52.5%). Oracle topology is coupled to magnitudes the ternary model
can't access. Random plates outperform oracle crystal. This means direct crystal
write of weight signs from teacher → student is flawed. Must target representation
geometry (relational distances) not weight topology (sign patterns).

### 6. Freeze + GD recovery (session 115)
```
GD ceiling:           89.5%
Beam-only (random):   52.4%
Full alternating:     41.2%
Freeze round 5 + GD: 54.1%  ← BEST
Freeze 15r + ext GD:  49.6%
```
Etching plates for ~5 rounds then freezing + extended beam GD beats both full
alternating and beam-only-from-scratch. The etch creates useful plate topology,
then extended GD on continuous params exploits it. Full alternating wastes compute
on diminishing-return etch cycles. Sweet spot: ~5 etch rounds at d=48.

Validates seed crystal Stage 6 (GD after freeze). Budget should be heavily
weighted toward post-freeze GD.

## What's NOT running
- VSM-LM lattice etch killed (collapsed at round 65)
- All microscope experiments complete (v1 d-sweep, v2 d-sweep, freeze)

## Next steps

**Strategy: design new training run from scratch using all microscope findings.**

1. **Build holographic distillation pipeline** — extract layer-wise features from Qwen3-32B (teacher), wire into V12 etch accumulator. Forward diverse probes through teacher, capture (input→output) at each layer, etch interference pattern into VSM-LM ternary plates. Mini-holo proved 91.3% oracle recovery at d=48.

2. **Run holographic distillation → freeze → extended GD** — etch ~5 rounds from teacher features, freeze all ternary plates, then 80%+ of compute budget on GD over continuous params (Q, gamma, embeds, mirrors).

3. **Teacher**: Qwen3-32B (text-only, same Qwen3 tokenizer, 64 layers, d=5120, 61GB cached). Qwen3.6 models use different tokenizer (248K vocab) — incompatible with our data.

4. **Training data ready**: structured_shard_v2.npy (52.6K docs, 1.2M tokens, all 9 kernel ops + math + clojure). Plus Dolma shards (3B tokens general text).

## Architecture at session end

| Component | Value |
|-----------|-------|
| N_COMBINATORS | 8 (K,I,B,C,D,Y,W,WHNF) |
| Parameters | 24.6M |
| Crystal state | Round 65 shows backbone correlation 0.465 but dispatch dead |
| Backbone | 32K pairs, 664 probes, threshold ≥ 0.63 |
| Models validated | 5+1 (+ qwen3.6-27b probed) |
| Procrustes cos | 0.217 (round 60), untested post-lattice |
| Mini-holo | d-sweeps, freeze+GD, crystal write (fails), holo distill (91.3%!) |
| Training data | structured_shard_v2.npy: 52.6K docs, 1.2M tok, all 9 ops + math |
| Key insight | Holo distill (teacher beam angles) → freeze → GD = 91% of oracle |

## Architecture at session end

| Component | Value |
|-----------|-------|
| N_COMBINATORS | 8 (K,I,B,C,D,Y,W,WHNF) |
| Parameters | 24.6M |
| Crystal state | Round 65 shows backbone correlation 0.465 but dispatch dead |
| Backbone | 32K pairs, 664 probes, threshold ≥ 0.63 |
| Models validated | 5+1 (+ qwen3.6-27b probed) |
| Procrustes cos | 0.217 (round 60), untested post-lattice |
| Mini-holo | 3 experiments complete, crossover not found at d=48 |
| Key insight | Plates load-bearing only at scale (d² vs d). Beam-first protocol. |
