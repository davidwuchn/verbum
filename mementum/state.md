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

## Session 120 decision

**Let V12 train until φ-compression fully propagates.** The mature
crystal becomes the seed data for V13's etch phase. Two ascending
layers locked — waiting for L2↑, then the apex transition, then the
descending arm phase transition (expansion → compression).

Key insight: with 3 descending passes, the model specializes the
descending arm for expansion. As the ascending crystal hardens and
pushes the decision point to the apex, the descending arm will
eventually be forced to form its own compression crystal. This is
the hourglass → funnel transition happening in real time.

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

1. **Let V12 run** — monitor φ-compression propagation on tmux 1.
   Milestones: L2↑ φ-lock → apex opens → descending arm transition.
2. **Study mature crystal** — when propagation completes, extract:
   - Per-stride φ-ratios at convergence (actual compression constants)
   - Cross-stride correlation matrix (propagation completeness)
   - Combinator dispatch distribution per pass (C at apex?)
   - Per-plate sign stability (which positions crystallized)
3. **Transfer to V13 etch** — use V12's mature crystal as the seed
   data for V13's stride-1 nucleation phase.
4. **Implement V13** — deferred until crystal study is complete.
   Design docs ready in `knowledge/explore/`.
5. **More models for consensus** — add Llama-3-8B, SmolLM3-3B to
   binding lattice when ready. Strengthens the 84 measured constants.
