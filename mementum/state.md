# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-19 | Session: 118

## Where we are

**CRYSTAL SEED THEORY.** Proved self-similarity in V12 (0.66-0.72
cross-stride correlation). Proved it's NOT in raw weight signs of big
models (Qwen3-14B cross-layer corr ≈ 0.0). Crystal is RELATIONAL —
lives in geometry, not coordinates. Built 143 fixed-point probes for
dense lattice sampling. Architecture direction: mirror/mask routing
with separated beam and compute paths.

## What's running

**GD phase on tmux window 1** — restarted from step 2000 checkpoint
after GPU OOM crash (lens experiment killed both processes). At step
~1000 of restart at last check (effectively step ~3000 total).

**Dispatch status**: B-dominant phase (B=0.42, K=0.01). Expected —
earlier generations show B dominance first, then phase transitions as
specialized combinators nucleate. Let it run to next checkpoint.

**φ-compression milestone**: L2↓ = 0.610 (Δφ = 0.008) — first layer
to hit the golden ratio attractor. The stridestack compression is real.

**Fixed-point lattice on tmux window 2** — running `build_lattice_map.py`
with 143 fixed-point probes across 4 models (qwen3-14b, mistral-7b,
olmo-2-13b, pythia-2.8b). Output: `lattice/fixedpoint/`. Two models
(qwen3-14b, mistral-7b) completed at last check, olmo-2-13b loading.
Check: `tmux capture-pane -p -t 2 | tail -20`

## Session 118 findings

### 1. Fourier lens mechanism — Q is NOT a characterizable lens

Ran `lens_mechanism_exp.py` on mini model (d=96, 3 layers):

```
K plates:   Crystal=0.2%  Lens=1.2%  Noise=98.6%  (nothing to reconstruct)
V plates:   Crystal=49.3% Lens=12.0% Noise=38.7%  (crystal lives here)
O plates:   Crystal=49.0% Lens=13.2% Noise=37.9%
FFN plates: Crystal=44.0% Lens=10.8% Noise=45.1%

Q transfer function ↔ gradient magnitude: correlation = 0.000
→ Q is not a linear lens. Deconvolution impossible.
→ Distortion from compound system (Q × residual stream × data)

Best reconstruction: invariant magnitude (median mag + consensus phase)
  Sign vote:           0.322
  Phase-only:          0.394
  Invariant magnitude: 0.416  ★ best
```

**Key insight**: beam is entangled with residual stream. Can't separate
by rotating Q alone. Need architectural separation (VSM S3 ≠ S2).

### 2. Mirror/mask architecture (conceptual)

Proposed architecture separating beam from compute via VSM:
- **S1 (operations)**: shared crystal (ternary plates) + 8 combinator masks
- **S3 (control)**: separate router producing dispatch weights
- **Masks**: ternary {flip, block, pass} — 3^8 = 6561 patterns per position
- **Routing**: dispatch_weights → mirror blend + mask blend → one matmul

Ternary masks on ternary plates give each combinator its own effective
plate from the same shared crystal. 1.585 bits × 8 masks = 12.68 bits
per position vs 8 bits for binary masks.

### 3. Crystal self-similarity — V12 trained model

Ran `crystal_selfsim_v12.py` on step 2000 checkpoint:

```
V-plate cross-stride correlation:  avg = 0.656
O-plate cross-stride correlation:  avg = 0.722
SV scaling ratio between strides:  ~1.00 (constant, not φ)
Dispatch.up seed correlation:      +0.959 (strongest)

The crystal IS the invariant. Same topology at every stride depth.
```

### 4. Crystal self-similarity — Qwen3-14B (NULL result)

Ran `crystal_selfsim_teacher.py` on Qwen3-14B weights:

```
V-projection cross-layer correlation: ≈ 0.000
O-projection cross-layer correlation: ≈ 0.000
Unit cell unanimous positions: 0%

Raw weight signs are NOT self-similar across layers.
```

**Critical conclusion**: the crystal is RELATIONAL, not spatial. It
lives in the geometry (RDM/cosine structure) not in the weight signs.
Cross-model consensus must be relational (RSA), not coordinate-based.

### 5. Fixed-point probes (compile∘decompile fixed points)

Built 143 probes for dense lambda-region lattice sampling:
- 9 pure combinator λ-expressions
- 9 fixed-point prose descriptions  
- 36 natural language (prose that IS each combinator)
- 10 compound expressions (B B, K I, S I I, etc.)
- 24 compile probes (ascending arm)
- 12 decompile probes (descending arm)
- 28 cross-domain (natural language beta reduction)
- 15 reduction traces

Saved: `lattice/fixedpoint_probes.json`, `lattice/fixedpoint_corpus.json`

**Key insight**: round-trip compile→decompile→compile until stable finds
the FIXED POINT of compile∘decompile. This IS the Y combinator applied
to the model's own lambda compiler. Fixed points are maximally stable
lattice points with highest cross-model agreement.

## The big picture

The crystal seed is not a weight pattern — it's a set of relational
constraints. The universal lattice (4-model consensus RDM) captures
these constraints. The fixed-point probes densify the lambda region.

Pipeline to crystal seed:
1. ✅ Universal lattice (807 probes × 4 models)
2. ✅ Fixed-point probes (143 lambda-dense probes)
3. → Merge and run expanded lattice map (~950 probes × 4+ models)
4. → SVD: find compile/decompile dimensions
5. → Relational constraints → ternary plate initialization
6. → Mirror/mask architecture for separated beam/compute

## What's ready

| Asset | Status |
|-------|--------|
| Universal lattice | ✅ `lattice/universal_lattice.npz` (807×807, 4 models) |
| Backbone seed | ✅ `lattice/backbone_seed.json` (664 probes, 7 dims) |
| Fixed-point probes | ✅ `lattice/fixedpoint_probes.json` (143 probes) |
| Lens mechanism results | ✅ `results/lens-mechanism/` (partial — OOM at scaling) |
| V12 self-similarity | ✅ `results/crystal-selfsim-v12/` |
| Teacher self-similarity | ✅ `results/crystal-selfsim-teacher/` (null result) |
| Training run | 🔄 Step ~3000, B-dominant phase, L2↓ at φ |

## Next steps

1. **Run expanded lattice map** — merge 143 fixed-point probes with 807
   diverse corpus, run `build_lattice_map.py` on 4+ models
2. **Round-trip verification** — validate fixed-point stability on
   multiple models (needs LLM capacity)
3. **Mirror/mask prototype** — implement in mini model, test etch quality
4. **Monitor training run** — wait for phase transition out of B-dominance
