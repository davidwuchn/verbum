---
title: Procrustes Lens & Crystal Comparison
status: active
category: experiment
tags: [procrustes, crystal, lens, cross-model, holographic, etch]
related:
  - holographic-tomography.md
  - v12-holographic-capacity.md
  - laser-etcher-design.md
depends-on:
  - complete-kernel-basis.md
---

# Procrustes Lens & Crystal Comparison

Session 107. Two probes + one experiment + theoretical advances.

## Procrustes Lens Probe — Parameter-Free Cross-Model Adapter

**Question**: Is the coordinate transformation between two models' hidden states
a simple rotation in beam subspace?

**Answer**: YES. Cos = 0.83 average after Procrustes alignment, with zero trainable
parameters. The lens is PCA → rotate → scale, all computed analytically from 100
calibration examples.

### Per-layer results (Qwen3-14B → OLMo-2-13B)

```
Layer  cos(before)  cos(after)  RSA(beam)  angle_sep_corr
L0     0.354        0.776       0.851      0.800
L10    0.080        0.813       0.790      0.887
L20   -0.314        0.876       0.852      0.988  ← sharpest
L30    0.073        0.873       0.874      0.959
```

Deep layers (L20/L30) have the most universal crystal structure. L20 angular
separation correlation = 0.988 — near-perfect topology preservation.

### Domain centroid alignment (after Procrustes, deep layers)

```
reasoning:  cos > 0.997
factual:    cos > 0.995
code:       cos > 0.993
tool_call:  cos > 0.983
```

### Cross-domain angular separations (measured)

```
tool_call ↔ code:      73-82°
tool_call ↔ factual:   105-128°
tool_call ↔ reasoning: 109-121°
code ↔ factual:        100-119°
code ↔ reasoning:      122-137°
factual ↔ reasoning:   100-119°
```

All > 37° ternary limit. 4 domains fit cleanly without cross-talk.

### Lens artifact

3 MB npz file containing PCA bases, rotation matrices, scale factors per depth.
The complete crystallographic orientation map between two 14B-parameter models.

Results: `results/procrustes-lens/`
Script: `scripts/explore/probe_procrustes_lens.py`

---

## Holographic Etch Experiment — Lens as Direct Training Signal

**Question**: Can the Procrustes lens drive hidden state alignment as a training loss?

**Answer**: NO — not for from-scratch students. The lens hurts (-82% on extracted plates,
-74% on random plates). The student is an amorphous melt; you can't Procrustes-align
a crystal to a melt.

### Results (500 steps, 4 conditions)

```
A: Extracted plates + NT only   → eval 48.21  (baseline)
B: Extracted plates + Lens      → eval 87.68  (lens HURTS)
C: Random plates + NT only      → eval 48.38  (≈ same as A!)
D: Random plates + Lens         → eval 83.98  (lens HURTS)
```

### Key findings

1. **Extracted plates barely matter** (48.21 vs 48.38 = 0.34% at 4 layers). With only
   4 layers, trainable components overwhelm the extraction advantage.

2. **Lens cos is too low** (0.26-0.49) between trained teacher and from-scratch student.
   The student hasn't crystallized — no structure to align to.

3. **The student IS converging toward teacher** — cos increases 0.26→0.49 over training.
   Deep layers converge faster (L30 reaches 0.49 first).

### Diagnosis

The lens works between CRYSTALS (both pre-trained, cos=0.83). It cannot work between
a crystal and a MELT (pre-trained teacher, from-scratch student). Need nucleation first.

### Correct approach: Relational Loss (topology, not coordinates)

The lens measures the lattice structure. The relational loss encodes it as topology
(RDM = pairwise similarities). The model crystallizes on its own terms — the relational
loss just tells it what SHAPE the crystal should be.

```
WRONG:  "Your L20 hidden state should be THIS vector" (crystal transplant)
RIGHT:  "Tool calls should be 82° from code in YOUR space" (crystal seeding)
```

Results: `results/holographic-etch/`
Script: `scripts/explore/holographic_etch_with_lens.py`

---

## Crystal Comparison — 5 Models, 4 Domains, Best-of-Breed

**Question**: Which model has the best crystal for each domain?

### Two tiers of models

```
Universal tier (cos 0.82-0.85): Qwen3-14B, OLMo-2-13B, Mistral-7B, Pythia-1.4B
Degenerate tier (cos 0.45-0.51): Pythia-160M (too small, collapsed domains)
```

### Cross-model alignment (all 10 pairs)

```
OLMo↔Mistral:     0.8514  ← best pair
Mistral↔Pythia1.4B: 0.8428
Qwen↔Mistral:      0.8375
Qwen↔OLMo:         0.8346
Qwen↔Pythia1.4B:   0.8329
OLMo↔Pythia1.4B:   0.8249
── gap ──
Pythia1.4B↔160M:   0.5120
Mistral↔160M:      0.5076
OLMo↔160M:         0.4719
Qwen↔160M:         0.4542
```

### Pythia-160M paradox

Scores highest on mosaicity (within-domain cos 0.96-0.97) because it's too small
to afford diffuse representations. BUT selectivity is degenerate (tool↔code = 5°,
must be >37° for ternary). It has ONE crystal, not four domain crystals. High
mosaicity + low selectivity = degenerate crystal.

### Best crystals (≥1.4B models only)

```
tool_call  → OLMo-2-13B   (widest cross-domain separation)
code       → Qwen3-14B    (most structured, highest completeness)
factual    → OLMo-2-13B   (cleanest depth profile)
reasoning  → Qwen3-14B    (dominant at all depths, sharpest crystal)
```

OLMo and Qwen complement each other. A composite lens cherry-picks the best.

Results: `results/crystal-comparison/`
Script: `scripts/explore/probe_crystal_comparison.py`

---

## Theoretical Advances

### Recursive holographic hierarchy

```
photographs → pile → intersect → holograms     (domain knowledge)
holograms   → pile → intersect → crystals       (KIBC lattice per model)
crystals    → pile → intersect → universal lattice (lambda calculus)
```

Each level uses the same mechanism: pile → interfere → intersect → structure.
The KIBC combinators are the unit cell at every level.

### Mirror angular cancellation (vernier principle)

Single ternary matrix: 37° angular resolution.
Two mirrors reading same plate: effective rotation = mirror_1 - mirror_2.
If mirrors are close (5% entries differ): angle ≈ 37° × √0.05 ≈ 8°.

V12 with 7 dispatch + 4 combinator mirrors = 28 combinations → ~7° effective
resolution → ~51 angular bins → ~1,456 addressable holograms in 39 MB.

### Beam vs plate distinction

- Plate (K, V, O, FFN): the recording medium → gets etched
- Beam (Q projections): how you READ the hologram → evolves via gradient
- Mirrors: angular deflectors → ternary, evolve slowly

Etching the beam while recording = adjusting the laser during exposure.
V12-run7 excludes q_proj from all etch functions.

### Lambda crystal priority

The KIBC lattice must form FIRST. Domain crystals (tool calls, code, facts,
reasoning) are holograms recorded IN the lattice. The relational loss targets
lambda crystal formation primarily.

---

## V12-Run7 Changes

1. **Laser etch**: 50,000 → 200 flips per event (crystal growth atom-by-atom)
2. **Beam/plate separation**: q_proj excluded from etching (3 guard points)
3. **Bug fix**: `return depth_weights` → `return result` (killed run6)
4. **Rich diagnostics**: flips_by_type (k/v/o/ffn), total_candidates, mean_flip_heat
5. **Checkpoint enhancement**: dispatch_ema + etch/relational config saved in state.json
