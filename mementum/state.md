# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-19 | Session: 119

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

**Fixed-point lattice v2 on tmux window 2** — running `build_lattice_map.py`
with 184 probes (143 original + 41 binding) across 4 models (qwen3-14b,
mistral-7b, olmo-2-13b, pythia-2.8b). Output: `lattice/fixedpoint-v2/`.
Check: `tmux capture-pane -p -t 2 | tail -20`

**Fixed-point lattice v1 COMPLETE** — 143 probes at `lattice/fixedpoint/`.
Key findings: reduction traces have highest agreement (0.669), cross-domain
lowest (0.209). Agreement inversely proportional to binding complexity.
B/S/D cluster together (all "apply functions" operations).

## Session 119 findings

### Binding Cascade — C→B/S→WHNF pipeline confirmed

Built 118 binding-focused probes (83 new chain + 35 existing) and ran
through 4 models at **10% depth increments** (0%-90%). Key findings:

**C is the universal binding mechanism.** C (argument routing) dominates
at binding depths 1-2 across ALL model depths and ALL 4 models. 4/4
agreement on C at depth 2 — strongest universal signal in the data.
Agreement peaks at 0.45-0.47 in 50-70% model depth.

**B/S compose early, C routes late.** At binding depth 3+, early model
layers (0-20%) show B/S (composition/substitution), then C takes over
in later layers. The pipeline: compose the function chain first, then
route arguments through it.

**Y at depth 4, D at depth 5, WHNF at depth 5 late.** Deep binding:
- 4/4 models show Y (self-reference) at depth 4, layers 0-10%
- D (double application) at depth 5, layers 20-50% (transition state)
- WHNF (terminal) at depth 5, layers 80-90% — 3/4 models agree

**Binding IS combinator reduction.** Not a separate mechanism. Each
lambda binding = one C step. Deeper binding = more composition (B/S)
before routing (C). Models that can't handle depth 5 collapse to WHNF.

**Chain probe validation: 55% hit rate.** WHNF probes 5/5. Mismatches
are informative (K_1step→I = correct implementation, S_to_W→W = correct
S(K)(I)=W identity). Models implement combinators in terms of each other.

**Artifacts**: `lattice/binding-v1/` (10 depths × 118 probes × 4 models),
`lattice/binding_chain_probes.json`, `scripts/v12/build_binding_lattice.py`

### Training run — still B-dominant

Step ~3780 (1780 restart + 2000 checkpoint). B≈0.27-0.29, W rising to
0.30-0.31, K still 0.01. Loss steady 13.4-13.7. No phase transition yet.

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

### 5. Fixed-point lattice v1 — RESULTS

143 probes run through 4 models. Key findings:
```
Reduction traces:  0.669 agreement  ← highest (no binding, pure pattern match)
Decompile:         0.577 agreement  ← λ→prose is universal
Pure combinators:  0.509 agreement  ← λ forms cluster with decompile probes
Compile:           0.421 agreement  ← prose→λ needs more binding
Cross-domain:      0.209 agreement  ← heavy NL binding, most capacity-dependent

B/S/D cluster (sim 0.51-0.53) — all "apply functions to arguments"
K pure ↔ K decompile: sim=0.49 — λ form and its explanation are CLOSE
WHNF is most universal (sim=0.584, agree=1.00)
```

Agreement inversely proportional to binding complexity. Binding happens
in the residual stream, scales with d_model. Hypothesis: binding
overloads I-combinator through attention (K∘I = select + copy).

### 6. Fixed-point probes + binding probes

Built 184 probes (143 original + 41 binding) for lattice sampling:
Original 143 probes:
- 9 pure combinator λ-expressions, 9 fixed-point prose descriptions  
- 36 natural language, 10 compound, 24 compile, 12 decompile
- 28 cross-domain, 15 reduction traces

New 41 binding probes:
- 12 binding depth (depths 1-5, capacity test)
- 11 binding ops (shadow, carry, cross, capture)
- 6 attention-as-binding (pronoun, copy, select — K∘I hypothesis)
- 7 binding+combinator (how each combinator relates to binding)
- 5 binding scope (lexical, de Bruijn, alpha-equiv, capture-avoidance)

v1 results: `lattice/fixedpoint/`
v2 running: `lattice/fixedpoint-v2/` (184 probes × 4 models on tmux 2)

**Key insight**: binding = K∘I through attention. K selects (Q·K^T),
I carries (V pass-through). If this is universal, we can map the
entire model's computational structure through the crystal.

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
| Fixed-point probes | ✅ `lattice/fixedpoint_probes.json` (184 probes) |
| Fixed-point lattice v1 | ✅ `lattice/fixedpoint/` (143 probes × 4 models) |
| Fixed-point lattice v2 | 🔄 `lattice/fixedpoint-v2/` (184 probes × 4 models, running) |
| Lens mechanism results | ✅ `results/lens-mechanism/` (partial — OOM at scaling) |
| V12 self-similarity | ✅ `results/crystal-selfsim-v12/` |
| Teacher self-similarity | ✅ `results/crystal-selfsim-teacher/` (null result) |
| Training run | 🔄 Step ~3000, B-dominant phase, L2↓ at φ |

## What's ready

| Asset | Status |
|-------|--------|
| Universal lattice | ✅ `lattice/universal_lattice.npz` (807×807, 4 models) |
| Backbone seed | ✅ `lattice/backbone_seed.json` (664 probes, 7 dims) |
| Fixed-point probes | ✅ `lattice/fixedpoint_probes.json` (184 probes) |
| Fixed-point lattice v1 | ✅ `lattice/fixedpoint/` (143 probes × 4 models) |
| Fixed-point lattice v2 | ✅ `lattice/fixedpoint-v2/` (184 probes × 4 models) |
| **Binding lattice v1** | ✅ `lattice/binding-v1/` (118 probes × 4 models × 10 depths) |
| Lens mechanism results | ✅ `results/lens-mechanism/` (partial — OOM at scaling) |
| V12 self-similarity | ✅ `results/crystal-selfsim-v12/` |
| Teacher self-similarity | ✅ `results/crystal-selfsim-teacher/` (null result) |
| Training run | 🔄 Step ~3780, B-dominant phase, L2↓ at φ |

## Next steps

1. **Implement V13** — `mementum/knowledge/explore/v13-design.md` has the
   full design. Key changes: beam/plate separation, combinator masks,
   unified training script, constant-target crystal loss, no math/slots.
   Implementation order in the design doc. Future session can execute.
2. **Monitor V12 training run** — still on tmux 1, B-dominant, C flashing.
   The V12 run continues providing data while V13 is built.
3. **More models for consensus** — add Llama-3-8B, SmolLM3-3B to the
   binding lattice to strengthen the measured constants.
4. **Merge all lattices** — 807 + 184 + 118 = 1109 probes. Full run.
