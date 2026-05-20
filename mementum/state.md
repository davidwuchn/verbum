# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-20 | Session: 124

## Where we are

**THE LOOM HAS 7 SUBCRYSTALS. ETCH MUST BE WEAVE-SEPARATED.**

Session 123 proved magnitudes are the crystal (beamformers). Session
124 proved the etch protocol must change: the loom has multiple
independent subcrystals at each depth, and consensus etching across
them creates destructive interference. Different computation types
(lambda, coding, retrieval, analogy, etc.) illuminate genuinely
different sign patterns at the same weight positions.

## Proof chain (solid, sessions 95-124)

- PCA-Q crystal: 0.91-0.94 agreement, 4 models
- PCA-up (FFN crystal): 0.9462 agreement, 4 models
- Lambda proof: binder + combinator predicts body at R²=0.959
- sign(W) Q fidelity: 0.974 (captures magnitude effect on cosines)
- Holographic angle: Q↔FFN subspaces at 65-72°
- Magnitude template > oracle signs: 0.568 vs 0.248 nucleation
- Cross-layer sign correlation = 0.000 (signs are per-layer encodings)
- Magnitude spectrum universality: W_q=0.995, W_up=0.999 across 4 models
- **NEW: Holographic band sign overlap = 0.495 (random) between compose↔retrieve**
- **NEW: 7 independent subcrystals at d=0.3 in mid_low band**
- **NEW: Loom breathes — fragments early, unifies mid, re-fragments late**
- **NEW: Within-group splits: retrieval↔analogy=0.496, coding↔reasoning=0.502**

## Session 124: loom-read experiments

Three experiments probing subcrystal structure:

### Experiment 1: Single-depth loom read (layer 16)
4 probe groups × 7 angle bands. Key findings:
- Holographic band (64-72°): compose↔retrieve = 0.495, retrieve↔route = 0.500
- Shared band (0-35°): all groups agree 100% — universal backbone
- route↔neutral magnitude correlation = 0.9997 (same beamformer)

### Experiment 2: Multi-depth loom read (5 depths)
Loom breathes with depth:
- d=0.1: 2-3 crystals everywhere, beamformers maximally divergent
- d=0.3: holographic hits 3 independent subcrystals
- d=0.5: maximum unity, shared band universal
- d=0.7: re-fragmentation, shared band shatters to 3, transition hits 3
- d=0.9: partial convergence, shared band still fractured (overlap=0.33)

### Experiment 3: Fine-grained loom read (10 domains × 5 depths)
Peak fragmentation: **7 subcrystals** at d=0.3, mid_low band:
  pure | lambda | arithmetic | coding | analogy | reasoning | text-gen cluster

Within-group splits at holographic d=0.5:
  retrieval↔analogy = 0.496 (★ random)
  coding↔reasoning = 0.502 (★ random)

Unexpected groupings at d=0.7 shared band (4 crystals):
  pure+retrieval | arithmetic+lambda | coding+instruction+narrative | analogy+reasoning+tool

## Knowledge map

| Page | What it tells you |
|------|-------------------|
| `gradient-voting.md` | Magnitudes are the crystal, 4 experiments, V13 implications |
| `loom-structure.md` | 3 weaves, 6 harmonics, WHNF transition, tension=crystal |
| `hologram-extraction.md` | sign(W) captures crystal (via magnitude effect) |
| `v13-design.md` | Architecture (needs revision for loom-read etch) |
| `holographic-plates.md` | SVD lens, 100× compression, two-beam geometry |
| `ffn-beam-discovery.md` | PCA-up at 0.946, WHNF polarity, depth profiles |
| `crystal-basins.md` | Basin theory, 7 experiments, 24 findings |
| `ffn-hierarchy.md` | Tree hypothesis, P2/P3 confirmed, WHNF gateway |

## What's ready

| Asset | Location |
|-------|----------|
| Loom read results (single depth) | `results/loom-read/` |
| Loom read results (5 depths) | `results/loom-read-depth/` |
| Loom read results (10 domains × 5 depths) | `results/loom-read-fine/` |
| PCA-Q crystal constants (4 models) | `results/pcaq-targets/` |
| Gradient voting results (4 experiments) | `results/gradient-voting/` |
| Crystal lens results | `results/crystal-lens/` |
| Loom structure results | `results/loom/`, `results/loom-crossings/` |
| Angle spectrum probe results | `results/angle-spectrum/` |
| Magnitude universality results | `results/magnitude-universality/` |
| Basin probes (144, 9 domains) | `lattice/basin_probes.json` |
| V12 model + training infra | `scripts/v12/` |

### Experiment 4: Breathing curve (11 depths)
Fine-resolution depth profile of subcrystal count:
- Apex at layer 19 (d=0.613) — asymmetric, more depth for fragmenting
- Two peaks: layer 7 (4 crystals ascending) and layer 22 (3 descending)
- WHNF polarity: crosses zero at L13-L16, maximally positive (+1.00) at apex
- Maps cleanly to V13 hourglass: ascending=fragmentation, apex=unity, descending=re-fragmentation

### Etcher VSM prototype
Concrete S4+S1+S3 implementation, verified:
- S4 (crystal counter) and S1 (reference beam extractor) produce same clusters ✓
- At d=0.226 with 8 families: 6 subcrystals in mid_low band
  pure | lambda+reasoning | arithmetic | coding | analogy | text_gen+retrieval
- Total beams needed at peak fragmentation: 13 (across all bands)

## Next steps

1. **Multi-model loom-read** — verify subcrystal count is universal
   across Mistral, Qwen, OLMo. If 6-7 subcrystals are universal, the
   loom structure IS the crystal structure.

2. **V13 architecture revision** — revise v13-design.md for:
   - Asymmetric hourglass (apex at d=0.6, not d=0.5)
   - Per-pass plate sets etched from teacher's corresponding depth regime
   - Etcher VSM as the extraction pipeline (S4→S3→S1)

3. **Nucleus reference beam prompts** — design 7 lambda prompts that
   maximally activate each subcrystal family. Basin probes as starting
   point, optimize for activation energy concentration at target bands.

4. **Dimensional bridge via loom-read** — does the subcrystal structure
   survive projection from d_model=2560 to d_model=512? The magnitude
   template should be projectable, but sign patterns may need re-derivation
   at the target dimensionality.

5. **Full etcher VSM** — extend prototype to run across all depths,
   write subcrystals into V13 plates per-pass. The etcher IS a hourglass
   over the teacher's layers.
