# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-20 | Session: 124

## Where we are

**CRYSTAL GATES THE HOLOGRAM. NEVER FLIP SIGNS THAT BREAK THE CRYSTAL.**

Session 124 explored the loom structure, built an etcher VSM prototype,
and discovered that unconstrained sign-flipping destroys the crystal
while improving accuracy. The crystal (relational geometry) must
constrain all hologram (sign pattern) modifications.

## Proof chain (solid, sessions 95-124)

- PCA-Q crystal: 0.91-0.94 agreement, 4 models
- PCA-up (FFN crystal): 0.9462 agreement, 4 models
- Lambda proof: binder + combinator predicts body at R²=0.959
- sign(W) Q fidelity: 0.974 (captures magnitude effect on cosines)
- Holographic angle: Q↔FFN subspaces at 65-72°
- Magnitude template > oracle signs: 0.568 vs 0.248 nucleation
- Cross-layer sign correlation = 0.000 (signs are per-layer encodings)
- Magnitude spectrum universality: W_q=0.995, W_up=0.999 across 4 models
- **NEW: 7 independent subcrystals at d=0.3 in mid_low band**
- **NEW: Loom breathes — fragments early, unifies mid, re-fragments late**
- **NEW: Breathing apex at d=0.613 (asymmetric hourglass)**
- **NEW: LOOM_MAG beats MAGNITUDE in nucleation (0.543 vs 0.511)**
- **NEW: Delta sign-flip converges (flips decline 12.6K→6.8K per round)**
- **NEW: Crystal diverges from hologram under unconstrained sign-flip**
- **NEW: Crystal must gate sign corrections (S5 invariant of etcher VSM)**

## Session 124: eight experiments

| # | Experiment | Key Finding |
|---|-----------|-------------|
| 1 | Loom read (d=0.5) | Holographic sign overlap=0.495 between compose↔retrieve |
| 2 | Loom read (5 depths) | Loom breathes: 7→1→4 subcrystals across depth |
| 3 | Fine-grained (10×5) | 7 subcrystals; retrieval↔analogy and coding↔reasoning independent |
| 4 | Breathing curve (11 depths) | Apex at d=0.613; WHNF crosses zero at L13-16 |
| 5 | Nucleation (6 conditions) | LOOM_MAG=0.543 beats MAGNITUDE=0.511; 5× faster nucleation |
| 6 | Delta refinement | Magnitude refocus works (R0→R2 climbs); 0% sign change |
| 7 | Delta sign-flip | Signs converge (flips decline); 10% flip fraction is sweet spot |
| 8 | Crystal measurement | **Crystal diverges from hologram**; accuracy↑ crystal↓; S5 invariant |

### The critical finding (experiment 8)

```
R4: accuracy=0.510 (BEST), crystal=-0.375 (INVERTED)
R3: accuracy=0.494,        crystal=+0.478 (only round both ↑)
MAG: accuracy=0.471,       crystal=+0.470 (best crystal overall)
```

Unconstrained sign optimization finds routing shortcuts that destroy
the relational geometry. Crystal must gate hologram modifications.

## Knowledge map

| Page | What it tells you |
|------|-------------------|
| `etcher-vsm.md` | ★ **NEW** Etcher VSM architecture + S5 crystal-gated constraint |
| `gradient-voting.md` | Magnitudes are the crystal, signs are expendable |
| `loom-structure.md` | 3 weaves, 6 harmonics, WHNF transition |
| `v13-design.md` | Architecture (needs revision for crystal-gated etch) |
| `hologram-extraction.md` | sign(W) captures crystal via magnitude effect |
| `crystal-basins.md` | Basin theory, 7 experiments, 24 findings |

## What's ready

| Asset | Location |
|-------|----------|
| Loom read results (3 experiments) | `results/loom-read*/` |
| Breathing curve (11 depths) | `results/loom-breathing/` |
| Nucleation results (6 conditions) | `results/loom-etch-nucleation/` |
| Delta refinement (magnitude) | `results/loom-delta-refine/` |
| Delta sign-flip (converging) | `results/loom-delta-signflip/` |
| Crystal sharpening (divergence) | `results/loom-crystal-sharpen/` |
| Etcher VSM prototype | `scripts/v12/etcher_vsm_proto.py` |
| All 8 experiment scripts | `scripts/v12/loom_*.py` |

## Next steps

1. **Crystal-gated sign-flip** — implement the S5 constraint: measure
   crystal before/after each flip, reject flips that degrade crystal.
   This should let accuracy AND crystal improve together.

2. **Crystal lattice loss in training** — add the 28-constant cosine
   target loss to beam training. This enforces crystal geometry
   continuously during GD, not just at flip time.

3. **Multi-model loom-read** — verify subcrystal count is universal
   across Mistral, Qwen, OLMo.

4. **V13 architecture revision** — asymmetric hourglass (apex at d=0.6),
   crystal-gated etch pipeline, per-pass plate sets.

5. **Scale test** — run crystal-gated LOOM_MAG on Pythia-2.8b extraction
   to d=512 V13 model. The 220× compression target.
