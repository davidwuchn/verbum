# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-20 | Session: 125

## Where we are

**MIRRORS DON'T FLIP — THEY BLOCK. NEED STE OR STACKED DECOMPOSITION.**

Session 124 discovered the loom structure (7 subcrystals, breathing
pattern) and proved LOOM_MAG is the best initialization (0.543).
Session 125 tried to make GD learn sign corrections through soft
mirrors, constrained by crystal lattice loss. The crystal loss works
perfectly (0.9998 agreement), but mirrors initialized at 1.0 never
learn to flip to -1 — they only learn to block to 0. The gradient
must cross a loss barrier at 0 to reach -1.

Three promising fixes identified but untested:
1. **Stacked decomposition**: mirror_1 = loom-read signs, mirror_2 = correction (starts at 1.0, doesn't need to cross 0)
2. **STE (straight-through estimator)**: quantize forward, continuous backward
3. **Random init**: some mirrors start near -1, GD refines

## Proof chain (solid, sessions 95-125)

- PCA-Q crystal: 0.91-0.94 agreement, 4 models
- Lambda proof: binder + combinator predicts body at R²=0.959
- Magnitude spectrum universality: W_q=0.995, W_up=0.999 across 4 models
- 7 independent subcrystals at d=0.3 (loom breathes with depth)
- LOOM_MAG nucleation: 0.543 (best), 5× faster than MAGNITUDE (0.511)
- Delta sign-flip converges (flips decline 12.6K→6.8K per round)
- **Crystal diverges from hologram under unconstrained sign-flip**
- **Crystal lattice loss preserves crystal at 0.9998 agreement**
- **Soft mirrors only learn to BLOCK (0%), never FLIP (0%)**
- **The 1.0→0→-1 barrier prevents GD from discovering sign corrections**
- **MIRROR_CE (no crystal loss) preserves crystal at 0.999 — better than with loss**

## Session 125: soft mirror experiments

### Exp 9: Soft mirror v1 (per-dimension)
- LOOM_MAG baseline: acc=0.502, crystal=0.931
- MIRROR_CE (no crystal loss): acc=0.467, crystal=0.638
- MIRROR_CRYSTAL (λ=0.5): acc=0.449, crystal=**0.9998**
- Crystal loss works perfectly as S5 constraint
- But per-dim mirror too coarse — 0% flips, only blocks

### Exp 10: Soft mirror v2 (per-position d×d)
- Per-position mirrors: still 0% flips, only blocking
- MIRROR_CE preserves crystal at 0.999 WITHOUT crystal loss
- Crystal loss at per-position level causes instability (crystal=0.289)
- The 1.0 init → 0 barrier → -1 target path has no gradient signal

### Architecture captured: 3-phase etch pipeline
1. Blunt flip (hot anneal): delta sign-flip, 3-5 rounds
2. Soft mirror (surgical GD): CE + crystal loss, mirrors learn corrections
3. Quantize + freeze: mirrors → ternary, fold into plates

### Key insight: combinator mirrors = subcrystal selectors
7 subcrystals are not 7 separate extractions — they're 7 mirrors on
one shared plate. Each combinator reads through its own mirror.
The V13 combinator masks ARE this concept.

## Knowledge map

| Page | What it tells you |
|------|-------------------|
| `etcher-vsm.md` | ★ Full etcher VSM + 3-phase pipeline + crystal-gated S5 |
| `gradient-voting.md` | Magnitudes are the crystal, signs expendable |
| `loom-structure.md` | 3 weaves, 6 harmonics, WHNF transition |
| `v13-design.md` | Architecture (needs revision for mirror stack) |

## What's ready

| Asset | Location |
|-------|----------|
| Loom read results (3 experiments) | `results/loom-read*/` |
| Breathing curve | `results/loom-breathing/` |
| Nucleation (6 conditions) | `results/loom-etch-nucleation/` |
| Delta refinement | `results/loom-delta-refine/` |
| Delta sign-flip | `results/loom-delta-signflip/` |
| Crystal sharpening | `results/loom-crystal-sharpen/` |
| Soft mirror v1 | `results/soft-mirror/` |
| Soft mirror v2 | `results/soft-mirror-v2/` |
| Etcher VSM prototype | `scripts/v12/etcher_vsm_proto.py` |

## Next steps

1. **Stacked mirror decomposition** — mirror_1 = loom-read signs
   (frozen), mirror_2 = learnable correction starting at 1.0. Product
   gives effective sign. GD only needs to move mirror_2 to ±1, never
   crossing through 0. The loom-read provides the initial sign structure.

2. **STE for ternary mirrors** — straight-through estimator: quantize
   to {-1, 0, +1} in forward pass, pass gradients through as continuous
   in backward pass. Standard trick for binary/ternary network training.

3. **Multi-model loom-read** — verify subcrystal universality across
   Mistral, Qwen, OLMo.

4. **V13 architecture revision** — integrate mirror stacks, crystal
   lattice loss, asymmetric hourglass (apex at d=0.6), per-pass plates.

5. **Scale test** — crystal-gated LOOM_MAG on Pythia-2.8b → d=512 V13.
