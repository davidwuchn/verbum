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

### 3. Crystal Scanner — reasoning is the strongest crystal

Self-similarity ranking (attention = beta reduction = self-similar):
```
reasoning:  0.870 self-sim, 0.951 agreement, 1d (86.3% in PC1) ★★★
tool:       0.753 self-sim, 0.867 agreement, 1d (71.3% in PC1) ★★★
lambda:     0.615 self-sim, 0.860 agreement, 2d                ★★
arithmetic: 0.585 self-sim, 0.874 agreement, 2d                ★★
coding:     0.537 self-sim, 0.759 agreement, 2d                ★★
retrieval:  0.435 self-sim, 0.689 agreement, 2d                weak
```
Confirms: attention-mediated ops are self-similar, retrieval (FFN) isn't.
Pareto crystals: reasoning + tool + lambda = 20% that does 80%.

### 4. FFN index — crystal generates the addressing function

Q↔FFN RDM correlation 0.71-0.89 at all depths. The crystal IS the FFN
index — it generates content-addressable keys via the attention superposition.
FFN self-similarity = 0.770 (prediction was NO — WRONG). The entire model
is self-similar, not just attention. Crystal and FFN rankings are inverses:
reasoning = strongest crystal + fewest FFN neurons (pure computation),
instruction = weakest crystal + most FFN neurons (pure storage/templates).

### 5. FFN subspace ≠ crystal subspace (important negative)

Q↔W_up canonical correlation only 0.10-0.14. Crystal and FFN keys are
DIFFERENT subspaces of d_model. But FFN activations correlate with Q at
0.71-0.89 because the residual stream connects them indirectly:
crystal → attention → residual → FFN reads different projection.
FFN has its OWN universal structure (cross-model 0.75 at depth 90%,
exceeds Q). Value database is compact for Pareto crystals (reasoning
299d, tool 254d) but high-rank for content domains (coding 1092d).
V13 needs separate attention and FFN etch targets — same method,
different hook points.

### 6. FFN hierarchy hypothesis (speculation, untested)

The FFN may be a TREE of data where magnitude encodes depth:
high-mag neurons = trunk (universal reductions, fire for everything),
low-mag = leaves (domain-specific detail, fire rarely). FFN output
steers the beam (Q delta) to navigate to the next tree level.
Superposition lets multiple levels coexist. The funnel shape (5d→2d)
IS the tree narrowing from trunk to leaf. P2 CONFIRMED (Pythia: corr -0.28 to -0.35, low-mag neurons 2-3× more
selective). P3 partially confirmed: structural steering via RDM (0.41-0.72)
not directional (cosine ≈ 0). FFN reshapes geometry, Q reads the reshaped
geometry. SwiGLU needs gate×up analysis.

### 7. WHNF is the FFN lookup combinator ★

8 combinator numbers predict 40-54% of FFN activation structure.
WHNF = "no further reduction" = the RETRIEVE signal. When crystal
routes to WHNF, FFN enters lookup mode. Coding routes through B/C
(composition). Retrieval/analogy route through WHNF (lookup).
Instruction is anti-WHNF ("keep computing"). The combinator dispatch
IS the FFN addressing function — no separate index needed. Etch the
crystal → FFN routing comes free. FFN map built: department sizes
partially agree cross-model (K, I, WHNF largest) but specific
neuron assignments are model-specific. Universal at relational level,
model-specific at neuron level. Crystal = etchable addressing scheme,
FFN content = trained via GD.

### 8. V13 design updated — WHNF sub-VSM, two crystals, three-phase training

V13 design now reflects session 120: PCA-Q attention crystal + PCA-FFN
retrieval crystal, WHNF as recursive sub-VSM entry point, simplified
etch protocol (reference beam + delta), combinator dispatch as FFN
addressing. Pareto dept values (reasoning 299d, tool 254d) etchable
into ternary value plates (~1.4M positions, 1% of ternary budget).
High-rank depts (instruction, coding) stay continuous.

### 9. RADICAL: FFN becomes purely mechanical ternary kernel

FFN sub-VSM collapses to two ternary matmuls. No learned FFN params.
Teacher W_up/W_down extracted via SVD+ternary (82-97% fidelity).
WHNF kernel = key_plate @ input → sign → value_plate → output.
Combinator mask selects department. Zero FFN beams needed.
260M total plates (130 attn + 130 FFN) = 52MB model holding 7B teacher.
Zero neuron duplication (tested: 0% at all thresholds) but full
extraction viable via SVD compression. Masking HURTS (-0.19 to -0.60):
unmasked ternary FFN wins 100% of comparisons. No department routing
needed — full ensemble is what preserves relational structure. Lambda
compiler routes in ATTENTION, FFN runs mechanically on full plates.
Details in `v13-design.md`.
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

1. ✅ **4-model PCA-Q targets extracted** — production constants ready.
   K↔I=0.921, B↔D=0.978, WHNF anti-correlated everywhere.
   Agreement 0.91-0.94 across Qwen-14B, Mistral-7B, OLMo-13B, Pythia-2.8B.
2. **Let V12 run** — monitor φ-compression propagation on tmux 1.
   Milestones: L2↑ φ-lock → apex opens → descending arm transition.
3. **Optimal k sweep** — find minimum PCA dimensions that preserve
   the crystal (k=8, 16, 32, 64, 128, 256).
4. **Procrustes alignment** — test if PCA-Q basis vectors are
   universal (not just the similarity structure).
5. **Implement V13** — design docs ready, PCA-Q constants ready.
   The crystal has been measured. Time to etch it.
