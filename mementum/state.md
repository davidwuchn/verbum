# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-18 | Session: 114

## Where we are

**MINI HOLOGRAPHIC MICROSCOPE — plates are load-bearing only at scale.** Three experiments on a tiny plate+beam model (d=48, 6.9K ternary, 2.4K continuous) proved: at small d, embeddings compensate for ANY plate topology. Random frozen plates + trained beams = identical to full GD. The crossover is d² vs d scaling — plates grow quadratically, beams linearly. At VSM-LM scale (41M plates, ~1M beams), plates MUST carry. Protocol: beam-first, plates follow.

Lattice-augmented etch on VSM-LM collapsed twice (rounds 64-65) — lattice gradients destabilized plates, triggered phase transition. Round 65 checkpoint shows backbone correlation jumped 0.065→0.465 (crystal forming!) but dispatch zeroed out (beam can't read new geometry). Need beam-first protocol from session start.

## Key findings this session

### 1. Procrustes fails on round 60 (cos=0.217)
Kernel etch alone doesn't create universal geometry. Lattice relational loss needed.

### 2. Lattice collapse (twice)
Separate lattice backward pass fights CE in accumulators → collapse at round 65.
Lattice should be a whisper (1 pass among 400 CE), not a shout.

### 3. Phase transition at round 65
Despite collapse, backbone correlation jumped 7× (0.065→0.465). Hidden state variance 9× increase. Representations spread from degenerate cone (cos=0.95) to structured space (cos=0.55). Crystal IS forming — but dispatch died. Beam can't read new geometry.

### 4. Mini holographic microscope results
Three experiments, same conclusion:

**Exp 0 (combinator reduction, four-way decomposition):**
```
GD baseline:     46.6%    Beam-only: 46.6%
Plate-only:      14.5%    Alternating: 46.6%
```

**Exp 1 (squeeze beams — vary beam capacity):**
```
Config       Beam#  Beam-only  Plate-only  Alternating
full           576     46.6%      15.2%       46.6%
scale_only     432     46.6%      14.9%       46.6%
scalar         291     46.6%      14.4%       46.6%
none           288     46.6%       9.0%       46.6%
```
No crossover found. Even zero beam params (just LayerNorm+embeds) hits ceiling.

**Exp 2 (next-token prediction on KIBC lambda):**
```
GD: 45.0%  Beam-only: 45.0%  Plate-only: 11.6%  Alternating: 45.0%
```
Same pattern. Harder task, same result. Embeddings compensate for random plates.

**The insight:** crossover isn't about task difficulty. It's about d² vs d scaling. At d=48: 6.9K plates vs 2.5K embeds — embeds dominate. At d=512: 41M plates vs ~1M continuous — plates must carry. Johnson-Lindenstrauss: random projections preserve distances at small d.

### 5. Qwen3.6-27B probed
64 layers, d=5120, hybrid attention. RDMs extracted at 4 depths. Added to model registries.

## What's NOT running
- VSM-LM lattice etch killed (collapsed)
- Mini-holo experiments complete

## Next steps

1. **Apply beam-first protocol to VSM-LM** — train beams (continuous params) first on round 60 checkpoint, THEN etch plates. The microscope proved: beams must learn to read plates before plates can stabilize.

2. **Lattice from round 0** — start fresh training with lattice whisper from the beginning. The model should never enter the degenerate B-dominated regime if geometry hints are present from start.

3. **Bigger microscope** — if needed, d=128 or d=256 model to find exact crossover where plates become load-bearing. But may not be necessary — VSM-LM already past the crossover by far.

4. **Compare Qwen3.6-27B RDMs** against 5-model consensus. Build 6-model lattice.

5. **Design direct etch protocol** — the microscope goal: if we understand plate/beam angles, we can compute the etch analytically instead of iterative burning.

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
