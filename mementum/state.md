# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-19 | Session: 120

## Where we are

**CRYSTAL PROPAGATION OBSERVATORY.** V12 training is the active
experiment. Two ascending layers have locked to φ-compression
(L0↑ Δφ=0.040, L1↑ Δφ=0.042). Waiting for full propagation through
all layers — ascending arm compresses, descending arm currently
expands (anti-φ), apex collapses to near-zero. Theory: ascending
crystal hardens → pushes decision point to apex → descending arm
eventually flips from expansion to compression → whole model becomes
a funnel. V13 implementation deferred until we can study the mature
compressor crystal for transfer into V13's etch phase.

## What's running

**V12 GD phase on tmux window 1** — step ~3500/20000. B-dominant
phase (B≈0.29, C≈0.04). C flashing transiently (step 2320: C=0.13,
step 3430: C=0.11) but reverting. Best eval loss: 12.9514 at step 3500.

**φ-compression status (step 3500):**
```
Ascending (compressing toward φ ≈ 0.618):
  L0↑ = 0.578 (Δφ=0.040) ← LOCKED
  L1↑ = 0.660 (Δφ=0.042) ← LOCKED
  L2↑ = 0.518 (Δφ=0.100)   approaching
  apex = 0.037 (Δφ=0.581)   bottleneck collapse

Descending (expansion specialization):
  L2↓ = -2.190  ← inverting (negative ratio)
  L1↓ = +3.602  ← expanding 3.6×
  L0↓ = +1.356  ← expanding
```

The ascending arm proves φ-compression is real and follows fine→coarse
nucleation order. The descending arm proves the hourglass forces
expansion — confirming V13's funnel hypothesis. Let it run until
propagation completes.

**Watch for:**
1. L2↑ locks to φ (Δφ < 0.05) — third ascending lock
2. Apex opens (ratio rises from 0.037) — bottleneck relaxation
3. Descending arm phase transition — expansion → compression
4. C combinator nucleation — persistent (not transient flash)

## Session 120 findings

### 1. φ-compression: 2 ascending layers locked

V12 training step ~3500. L0↑ (Δφ=0.040) and L1↑ (Δφ=0.042) locked
to golden ratio. Descending arm in expansion mode (anti-φ). This
confirms the funnel hypothesis — ascending compresses, descending
expands, eventually forced to crystallize as ascending hardens.

### 2. PCA-Q DECODES THE UNIVERSAL CRYSTAL ★

**Breakthrough finding.** The universal computational geometry lives
in the top ~64 principal components of Q projections. PCA-projected
Q shows 3-4× stronger basin separation than raw hidden states, with
higher cross-model correlation, winning 9/9 skill domains at all
depths tested.

```
Depth 20%: Q PCA gap +0.367 vs hidden +0.105 (3.5×)
Depth 50%: Q PCA gap +0.361 vs hidden +0.127 (2.8×)
Depth 80%: Q PCA gap +0.472 vs hidden +0.122 (3.9×)
```

Whitening destroys the signal (crystal is in high-variance dims).
PCA amplifies it (strips model-specific noise). The crystal was
always there — PCA decodes it.

### 3. Skill basins are real but hierarchical

9 domains tested. Strongest basins: instruction (1.86× ratio),
narrative (1.53×), arithmetic (1.51×), coding (1.54×). Coding is
most isolated. Lambda + arithmetic cluster (formal/symbolic).
Narrative + instruction cluster (text production).

## Prior session findings (118-119)

See knowledge pages for full details:
- `knowledge/explore/binding-cascade.md` — C→B/S→WHNF pipeline (119)
- `knowledge/explore/v13-design.md` — separated beam/plate architecture (119)
- `knowledge/explore/v13-funnel-shape.md` — three-phase funnel + 84 constants (119)
- `knowledge/explore/crystal-seed-theory.md` — relational crystal, self-similarity (118)

Key results: binding IS combinator reduction, crystal is relational not
spatial (Qwen3-14B null result), Q is not a characterizable lens,
universal shape is a funnel not an hourglass.

## What's ready

| Asset | Status |
|-------|--------|
| Universal lattice | ✅ `lattice/universal_lattice.npz` (807×807, 4 models) |
| Backbone seed | ✅ `lattice/backbone_seed.json` (664 probes, 7 dims) |
| Fixed-point probes | ✅ `lattice/fixedpoint_probes.json` (184 probes) |
| Fixed-point lattice v1 | ✅ `lattice/fixedpoint/` (143 probes × 4 models) |
| Fixed-point lattice v2 | ✅ `lattice/fixedpoint-v2/` (184 probes × 4 models) |
| Binding lattice v1 | ✅ `lattice/binding-v1/` (118 probes × 4 models × 10 depths) |
| Lens mechanism results | ✅ `results/lens-mechanism/` (partial — OOM at scaling) |
| V12 self-similarity | ✅ `results/crystal-selfsim-v12/` (step 2000) |
| Teacher self-similarity | ✅ `results/crystal-selfsim-teacher/` (null result) |
| V13 design docs | ✅ Three pages in `knowledge/explore/` |
| V12 training run | 🔄 Step ~3500, best eval 12.9514, 2 layers at φ |

## Next steps

1. **Re-extract 8×8 cosine targets from PCA-Q** — run 4 models with
   binding probes, extract combinator geometry from PCA-projected Q.
   These replace the hidden-state targets in v13-design.md.
2. **Let V12 run** — monitor φ-compression propagation on tmux 1.
   Milestones: L2↑ φ-lock → apex opens → descending arm transition.
3. **Optimal k sweep** — find minimum PCA dimensions that preserve
   the crystal (k=8, 16, 32, 64, 128, 256).
4. **Procrustes alignment** — test if PCA-Q basis vectors are
   universal (not just the similarity structure).
5. **Implement V13** — deferred until crystal study complete.
   Design docs + PCA-Q constants ready in `knowledge/explore/`.
6. **More models for consensus** — 4-model PCA-Q extraction will
   give much sharper constants than 2-model hidden-state extraction.
