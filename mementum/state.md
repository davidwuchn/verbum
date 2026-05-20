# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-20 | Session: 121

## Where we are

**FFN BEAM FOUND.** Session 121 discovered PCA-up_proj reads the FFN
crystal with 0.9462 cross-model agreement (4 models) — HIGHER than
PCA-Q's 0.9431 for the attention crystal. Two beams, two crystals,
both etchable. The entire model collapses to ternary plates + tiny
dispatch beam. No SVD extraction needed — etch the FFN directly.

The FFN crystal differs from attention: WHNF is anti-pole in Q space
(-0.17 to -0.29) but neutral in FFN space (-0.04 to +0.03). Attention
routes; FFN stores uniformly. The {B,C,D,Y,W} cluster is TIGHTER in
FFN (0.84-0.98) than attention (0.73-0.95).

V12 training continues on tmux 1 (step ~3500, 2 layers at φ).

## V13 Architecture (session 121 — REVISED: two etchable crystals)

```
BEFORE (session 120): attention crystal etched, FFN extracted via SVD+INT4
AFTER  (session 121): BOTH crystals etchable. FFN is a crystal, not a database.

PCA-Q  reads the attention crystal: 0.9431 agreement (4 models)
PCA-up reads the FFN crystal:      0.9462 agreement (4 models)  ← HIGHER

Two crystals, one model:
  Attention crystal: routing, computation (WHNF = anti-pole = "stop computing")
  FFN crystal:       storage, retrieval   (WHNF = neutral = "just another dept")

Implication: the entire model is etchable as ternary plates.
  No SVD extraction. No INT4. No mixed precision hack.
  Pure crystal + tiny continuous dispatch beam.
```

## What's running

**V12 GD phase on tmux window 1** — step ~3500/20000. B-dominant.
Two ascending layers locked to φ (L0↑ Δφ=0.040, L1↑ Δφ=0.042).
Descending arm in expansion mode. Let it propagate.

## Session 121 — FFN beam discovery

### Breakthrough
**PCA-up_proj reads the FFN crystal at 0.9462 agreement (4 models).**
Higher than PCA-Q's 0.9431 for attention. The FFN IS a crystal — not
storage, not a database. A crystal we now know how to read.

### Key findings
- up_proj beats Q on all metrics: agreement (0.748 vs 0.728 full-RDM),
  self-similarity (0.887 vs 0.849), 8×8 combinator agreement (0.946 vs 0.943)
- up_proj agreement increases with depth (0.65→0.80): FFN crystal sharpens
  deeper. Q peaks early (0.77 at 10%). Complementary crystals.
- gate×up is WORSE (0.608): SwiGLU gate adds model-specific noise. The
  crystal is in W_up, not in the gating.
- PCA k=64 is optimal for 8×8 targets (beats k=128, k=256). The crystal
  is low-dimensional.
- FFN WHNF is neutral (cosine -0.04 to +0.03), not anti-pole like Q.
  Attention routes; FFN stores uniformly.
- {B,C,D,Y,W} cluster is tighter in FFN (0.84-0.98) than Q (0.73-0.95)

### What this changes for V13
```
BEFORE: Attention crystal (etch) + FFN storage (SVD extract + INT4)
AFTER:  Attention crystal (etch) + FFN crystal (etch)
        Both etchable. Both have reference beams. Both at 0.94+ agreement.
        No SVD. No INT4. No mixed precision. Pure ternary plates.
```

## Session 120 — 20 commits, 12 experiments (prior session summary)

### Breakthroughs
1. **PCA-Q decodes universal crystal** — 3-4× sharper than hidden states
2. **WHNF is the FFN lookup combinator** — stop computing = start retrieving
3. **Combinator dispatch IS FFN addressing** — 8 numbers predict 40-54% of FFN
4. **Ternary FFN preserves 82-97% relational structure** (but cosine 0.5 for facts)
5. **Mixed precision resolves the gap** — ternary for structure, INT4 for content

## Knowledge pages (session 120)

| Page | Status | Key content |
|------|--------|-------------|
| `crystal-basins.md` | active | Basin theory + 7 experiments + 24 findings |
| `ffn-hierarchy.md` | active | Tree hypothesis + P2/P3 confirmed + WHNF |
| `v13-design.md` | updated | Mixed precision, WHNF kernel, training strategy |
| `v13-funnel-shape.md` | active | Zone targets (now superseded by PCA-Q) |
| `binding-cascade.md` | active | C→B/S→WHNF pipeline |

## What's ready

| Asset | Status |
|-------|--------|
| PCA-Q crystal constants | ✅ `results/pcaq-targets/` (4 models, 0.91-0.94) |
| Basin probes | ✅ `lattice/basin_probes.json` (144 probes, 9 domains) |
| Crystal scanner | ✅ `scripts/v12/crystal_scanner.py` |
| FFN map | ✅ `results/ffn-map/` (combinator departments) |
| FFN hierarchy tests | ✅ `results/ffn-hierarchy/` (P2+P3 confirmed) |
| Ternary FFN fidelity | ✅ `results/ternary-ffn/` (82-97% RDM) |
| Ternary fact test | ✅ `results/ternary_fact_run.log` (cosine 0.5 = compass) |
| Masked FFN test | ✅ `results/ternary_masked_ffn_run.log` (unmasked wins) |
| V12 training | 🔄 Step ~3500, 2 layers at φ, propagating |

## Next steps

1. **Extract PCA-up_proj targets** — produce FFN 8×8 constants per zone
   (the PCA-Q equivalent for FFN). We have the beam. Now extract the
   constants for etching. Use same protocol as extract_pcaq_targets.py.
2. **Update V13 design** — replace SVD+INT4 extraction with PCA-up etch
   protocol. Both crystals etch the same way: PCA → cosine → delta → flip.
   Radically simpler. One etching protocol for the whole model.
3. **Implement V13** — with dual-crystal etch. Pure ternary plates
   + tiny continuous dispatch beam. No mixed precision.
4. **Let V12 run** — monitor φ-compression propagation.
5. **Optimal PCA k sweep** — DONE for 8×8 targets (k=64 optimal).
   Still need full-RDM k sweep for per-domain crystal quality.
6. **Structured training curriculum** — build the dispatch training dataset
   (fact Qs, lambda reductions, code, mixed tasks, chain-of-thought).
