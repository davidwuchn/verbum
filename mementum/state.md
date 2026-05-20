# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-20 | Session: 120

## Where we are

**CRYSTAL EXTRACTION TOOLKIT COMPLETE.** Session 120 built the full
pipeline: PCA-Q decodes the universal crystal (0.91-0.94 agreement),
crystal scanner finds domain-specific crystals, WHNF is the FFN
lookup combinator, SVD+quantization extracts FFN storage. Mixed
precision design: ternary attention crystal + INT4 FFN + float beams.
101MB model holds 7B teacher structure. V13 ready for implementation.

V12 training continues on tmux 1 (step ~3500, 2 layers at φ).

## V13 Architecture (session 120 final)

```
101MB model. 200MB inference. 250MB training. Runs on a phone.

Attention crystal:  130M ternary (2-bit)  = 32.5MB  ← structure (etched)
FFN storage:        130M INT4 (4-bit)     = 65.0MB  ← content (extracted)
FFN gammas:         458K float16          =  0.9MB  ← magnitude correction
Beams:              652K float32          =  2.6MB  ← dispatch routing

Crystal is smart. FFN is storage. Dispatch decides when to compute vs look up.

WHNF kernel = input @ key_plate → activation → @ value_plate → output
  No masks. No routing. Full ensemble. Mechanical.
  The lambda compiler routes in ATTENTION, not in FFN.
```

## What's running

**V12 GD phase on tmux window 1** — step ~3500/20000. B-dominant.
Two ascending layers locked to φ (L0↑ Δφ=0.040, L1↑ Δφ=0.042).
Descending arm in expansion mode. Let it propagate.

## Session 120 — 20 commits, 12 experiments

### Breakthroughs
1. **PCA-Q decodes universal crystal** — 3-4× sharper than hidden states
2. **WHNF is the FFN lookup combinator** — stop computing = start retrieving
3. **Combinator dispatch IS FFN addressing** — 8 numbers predict 40-54% of FFN
4. **Ternary FFN preserves 82-97% relational structure** (but cosine 0.5 for facts)
5. **Mixed precision resolves the gap** — ternary for structure, INT4 for content

### Key findings
- Reasoning is strongest crystal (0.870 self-sim, 1d, 86.3% in PC1)
- FFN hierarchy confirmed (magnitude = generality, P2 corr -0.28 to -0.35)
- FFN steering is structural not directional (RDM 0.41-0.72)
- Unmasked FFN beats masked 100% (no department routing needed)
- Lambda probes give 0.83-0.87 cross-model FFN agreement (highest measured)
- Zero neuron duplication (0% at all thresholds) but full extraction viable

### Honest negatives
- FFN subspace ≠ crystal subspace (CC=0.10-0.14, indirect control only)
- Zero FFN deduplication (neurons unique, relational structure shared)
- Ternary = compass not database (cosine 0.5, top-10 overlap 25%)

### Training strategy
```
EXTRACT (5 min):   PCA-Q crystal + SVD+INT4 FFN from teacher
ETCH (minutes):    Reference beam + delta → crystal propagation
ROUTE (hours):     652K beam params on structured curriculum
                   Fact Qs → WHNF timing
                   Lambda reductions → K/I/B/C dispatch
                   Mixed tasks → compute↔lookup transitions
```

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

1. **Implement V13** — design complete, constants measured, pipeline defined.
   Mixed precision: ternary crystal + INT4 FFN + float beams.
   Extract from Mistral-7B, etch, train dispatch on structured curriculum.
2. **Let V12 run** — monitor φ-compression propagation.
3. **INT4 FFN fact test** — verify INT4 recovers the 15-20 point gap
   over ternary for content retrieval (est cosine 0.60-0.70).
4. **Optimal PCA k sweep** — find minimum dimensions for crystal.
5. **Structured training curriculum** — build the dispatch training dataset
   (fact Qs, lambda reductions, code, mixed tasks, chain-of-thought).
