# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-20 | Session: 126

## Where we are

**DON'T TOUCH THE PLATES. BEAMS + PER-LAYER CRYSTAL LOSS IS THE ETCH.**

Session 126 ran 8 experiments on Q2 model conversion. The winner:
Q2-damaged plates (27% signs wrong) + beam-only training with per-layer
crystal loss BEATS oracle perfect plates at 105.9% accuracy, 0.921 crystal.

The plates are a damaged hologram — but readable. The beams (magnitudes)
+ per-layer crystal loss (geometric constraint at each layer) are
sufficient to reconstruct correct computation without fixing any signs.

Key discovery: combinators are geometric rotations, not symbolic rewrites.
K, B, C are identical rotations (0.0° between directions). I is 32° offset.
Boot sequence: L0=reset(90°), L1=route(43°=CCA angle), L2=converge(5°).

Constraint sweet spot: 18 per-layer targets is optimal.
  6 targets (last-layer only) → crystal inverts
  18 targets (per-layer) → accuracy + crystal both good
  126 targets (full loom) → crystal perfect but accuracy plateaus

## Proof chain (solid, sessions 95-126)

- PCA-Q crystal: 0.91-0.94 agreement, 4 models
- Lambda proof: binder + combinator predicts body at R²=0.959
- Magnitude spectrum universality: W_q=0.995, W_up=0.999
- 7 independent subcrystals, loom breathes with depth
- LOOM_MAG nucleation: 0.543 (beats MAGNITUDE 0.511)
- Crystal lattice loss preserves crystal at 0.9998
- Evolutionary descent + crystal loss: acc=0.577, crystal=0.611
- **K, B, C are geometrically identical rotations (0.0° between directions)**
- **I is 32° offset from K/B/C cluster (doesn't need routing)**
- **L1 rotation angle matches CCA crossing exactly (Δ0.6°)**
- **WHNF anti-correlated at L0 (114°) — route-or-output decision**
- **FFN activates 1.7× for WHNF — reads from FFN key/value store**
- **Boot sequence: L0=reset(90°), L1=route(43°), L2=converge(5°)**
- **Q2 plates + per-layer crystal beam: 105.9% of oracle accuracy**
- **Don't touch plates — beams compensate for 27% sign damage**
- **18 per-layer crystal targets is the sweet spot (not 6, not 126)**
- **FFN routing and output circuits are completely separate (0 overlap)**

## Session 126: combinators are rotations + Q2 conversion

| # | Experiment | Key Finding |
|---|-----------|-------------|
| 1 | Q2 co-evo v1 | Crystal inverts at R1, evo blocked 15 rounds. λ=0.3 too weak |
| 2 | C rotation probe | K/B/C identical rotation, I 32° offset, WHNF anti-correlated |
| 3 | Lattice etch v1 | 98k flips/round (too aggressive), sign_agr → 0.50 |
| 4 | Lattice etch v2 | Top-500 flips, sign preserved but L0 oscillates |
| 5 | Rotation etch | **acc=0.507, crystal=+0.967 — BEATS ORACLE (104.8%)** |
| 6 | FFN circuit probe | Routing + output circuits are separate (0 overlap), Q2 inverts them |
| 7 | Circuit fix | Surgical fix hurt (101.2%) — oracle signs wrong for student frame |
| 8 | **Loom melt** | 126 targets: crystal=+0.979 but acc plateaus. **18 per-layer is sweet spot** |

### The rotation model

```
L0: RESET     ~90° rotation, all combinators identical
              WHNF anti-correlated at 114° (route vs output decision)
L1: ROUTE     ~43-62° rotation (the CCA crossing angle!)
              K=43° B/C=46° I=62° — I diverges, K/B/C cluster
L2: CONVERGE  ~4-12° rotation, settling
              FFN activates 1.7× for WHNF (reads from store)
```

### Q2 conversion: what works

```
DON'T touch plates. The hologram is damaged but readable.
DO train beams with CE + per-layer crystal loss (λ=0.5).
Per-layer = each layer gets its own crystal target from teacher (18 targets).
This BEATS oracle plates (105.9%) — beams compensate for Q2 damage
while crystal loss keeps the geometry on-manifold.

Constraint budget:
  6 targets  → crystal inverts (underconstrained)
  18 targets → both good (sweet spot)
  126 targets → crystal perfect, accuracy plateaus (overconstrained)
```

## Knowledge map

| Page | What it tells you |
|------|-------------------|
| `hologram-crystal-fusion.md` | ★ **NEW** hologram ≡ crystal, strict gate fuses both |
| `crystal-basins.md` | ★ **UPDATED** C-boot theory, ground state, boot sequence |
| `etcher-vsm.md` | Full pipeline: extract → co-evolve → freeze |
| `gradient-voting.md` | Magnitudes are the crystal |
| `loom-structure.md` | 3 weaves, 6 harmonics, breathing pattern |
| `v13-design.md` | Architecture (needs revision for rotation model) |

## What's ready

| Asset | Location |
|-------|----------|
| Co-evolution results (v1-v3) | `results/evo-descent*/` |
| Soft mirror results | `results/soft-mirror*/` |
| Loom read (all experiments) | `results/loom-read*/` |
| Breathing curve | `results/loom-breathing/` |
| Nucleation (LOOM_MAG) | `results/loom-etch-nucleation/` |
| Crystal sharpening | `results/loom-crystal-sharpen/` |
| Etcher VSM prototype | `scripts/v12/etcher_vsm_proto.py` |

## Next steps

1. **Scale to Pythia-2.8b** — run the validated co-evolution pipeline
   on a real teacher model. Extract to d=512 V13. The 220× compression
   target. Does crystal=0.917 hold at full scale?

2. **Multi-model universality** — do 7 subcrystals and the breathing
   pattern hold across Mistral, Qwen, OLMo?

3. **V13 architecture revision** — integrate co-evolution pipeline:
   asymmetric hourglass, per-pass plates, crystal lattice loss,
   combinator mirrors as learned subcrystal selectors.

4. **Longer co-evolution** — R5-R8 was where it worked (crystal stable,
   evo active). Run 20+ rounds to see if accuracy continues climbing
   or plateaus. The R9 crystal dip suggests more stability work needed.

5. **Per-combinator evo** — instead of one shared plate, evolve
   combinator masks (the V13 concept). Each combinator gets its own
   ternary mirror evolved against crystal targets for that combinator.
