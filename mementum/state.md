# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-20 | Session: 125

## Where we are

**CO-EVOLUTION WORKS. ACCURACY AND CRYSTAL IMPROVE TOGETHER.**

Session 125 proved the full etch pipeline: evolutionary descent for
ternary plates (discrete bit flips) + GD for beams (continuous) +
crystal lattice loss (S5 invariant). Evo v3 improves BOTH accuracy
(0.483→0.577) AND crystal agreement (0.368→0.611). Peak round hit
crystal=0.917 — the highest student crystal ever measured.

The crystal loss doesn't just protect the crystal — it ENABLES the
evolution. Stable crystal → more positions above floor → more
useful flips accepted (53 vs 20 without crystal loss).

## Proof chain (solid, sessions 95-125)

- PCA-Q crystal: 0.91-0.94 agreement, 4 models
- Lambda proof: binder + combinator predicts body at R²=0.959
- Magnitude spectrum universality: W_q=0.995, W_up=0.999
- 7 independent subcrystals, loom breathes with depth
- LOOM_MAG nucleation: 0.543 (beats MAGNITUDE 0.511)
- Crystal lattice loss preserves crystal at 0.9998
- Soft mirrors can't flip signs (0 barrier)
- **Evolutionary descent + crystal loss: acc=0.577, crystal=0.611 (BOTH UP)**
- **Peak R8: acc=0.564, crystal=0.917 (student matches teacher crystal)**
- **Crystal stability enables evo (2.6× more accepted flips)**

## Session 125: from soft mirrors to co-evolution

| # | Experiment | Key Finding |
|---|-----------|-------------|
| 9 | Soft mirror v1 | Crystal loss=0.9998, but per-dim mirrors only block, 0% flip |
| 10 | Soft mirror v2 | Per-position mirrors: still 0% flip, 1.0→0 barrier |
| 11 | Evo descent v1 | acc=0.585 (record), but crystal drifts to -0.654 |
| 12 | Evo descent v2 | Floor works (10.7% acceptance), crystal degrades in GD phase |
| 13 | **Evo descent v3** | **acc=0.577, crystal=0.611 — BOTH improve together** |

### The validated pipeline

```
GD phase:   CE + crystal_lattice_loss  → crystal stable (0.9998)
Evo phase:  delta-guided bit flips     → crystal floor rejects bad flips
            + absolute crystal floor   → only accuracy-improving flips accepted
Co-evolve:  GD trains beam → delta guides evo → beam relaxes → repeat

Two phases in convergence:
  R0-R4: crystal stabilizing (floor blocks all evo)
  R5-R8: crystal stable, evo produces useful flips (crystal=0.917)
```

## Knowledge map

| Page | What it tells you |
|------|-------------------|
| `etcher-vsm.md` | ★ Full pipeline: extract → co-evolve → freeze |
| `gradient-voting.md` | Magnitudes are the crystal |
| `loom-structure.md` | 3 weaves, 6 harmonics, breathing pattern |
| `v13-design.md` | Architecture (needs revision for co-evolution) |

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
