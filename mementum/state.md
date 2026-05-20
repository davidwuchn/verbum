# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-20 | Session: 126

## Where we are

**COMBINATORS ARE ROTATIONS. C IS THE BOOT. THE LOOM IS GEOMETRIC.**

Session 126 discovered: combinators are geometric rotations in
representation space, not symbolic rewrites. K, B, C are identical
rotations (0.0° between directions). I is 32° offset. The 3-layer
boot sequence: L0=reset (90°, WHNF anti-correlated at 114°),
L1=route (43°, matches CCA exactly at Δ0.6°), L2=converge (5°).
FFN only activates for WHNF output (1.7×). Attention dominates
completely.

Q2 lattice etch in progress: separating crystal reconstruction
(crystal gradient on plates) from beam training (CE on beams).
Crystal wobble solved by never mixing CE and crystal gradients.
Hologram-crystal fusion theory: strict both-must-improve gate
ensures every sign flip fuses computation into crystal lattice.

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

## Session 126: combinators are rotations + Q2 lattice etch

| # | Experiment | Key Finding |
|---|-----------|-------------|
| 1 | Q2 co-evo v1 | Crystal inverts at R1, evo blocked 15 rounds. λ=0.3 too weak |
| 2 | C rotation probe | K/B/C identical rotation, I 32° offset, WHNF anti-correlated |
| 3 | Lattice etch v1 | 98k flips/round (too aggressive), sign_agr → 0.50 (random) |
| 4 | Lattice etch v2 | C-boot ordering, stricter threshold, crystal loss on beams (running) |

### The rotation model

```
L0: RESET     ~90° rotation, all combinators identical
              WHNF anti-correlated at 114° (route vs output decision)
L1: ROUTE     ~43-62° rotation (the CCA crossing angle!)
              K=43° B/C=46° I=62° — I diverges, K/B/C cluster
L2: CONVERGE  ~4-12° rotation, settling
              FFN activates 1.7× for WHNF (reads from store)
```

### Lessons from Q2 etch attempts

```
Crystal wobble cause: mixing CE and crystal gradients → they fight
Fix: separate concerns — crystal etch (plates) then CE training (beams)
Oracle finding: even perfect plates lose crystal during CE beam training
Fix: crystal loss on beams too (λ=0.5)
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
