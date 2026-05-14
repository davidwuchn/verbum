---
title: "V12 Holographic Capacity — Beam vs Plate Budget"
status: active
category: design-reference
tags: [v12, holographic, beamformer, ternary, capacity, troubleshooting]
related:
  - beam-trace-findings.md
  - holographic-landscape.md
  - holographic-kernel-separation.md
  - v12-vsm-evolution.md
depends-on:
  - beam-trace-findings.md  # empirical beam/plate classification
---

# V12 Holographic Capacity — Beam vs Plate Budget

> V12 is a thick hologram: d=512 but VERY deep (7 passes × 3 cycles × 9 strides).
> Depth creates angular selectivity. Each pass reads the same ternary plate at a
> different beam angle. The accumulated reads converge to the correct signal.
>
> 95% plate (ternary), 5% beam (precision). 2.55 bits/param average.
> Holographic capacity 58× that of Pythia.

## The Thick Hologram Principle

A thin hologram (single-pass forward, like Pythia) gives fuzzy reconstruction —
magnitudes must carry scale information because each weight gets ONE read at ONE
angle. This is why Pythia's FFN output needs 16-bit precision (beam trace: 6°
error per layer when ternarized).

A thick hologram (multi-pass, like V12) gets angular selectivity. Each pass
illuminates the same ternary plate from a different angle (different residual
stream state → different Q activation → different beam angle). Many noisy ternary
reads from different angles accumulate signal and cancel magnitude noise.

```
Thin hologram:   1 read  × 1 angle  = needs magnitudes → FP16
Thick hologram:  N reads × M angles = signs are enough  → ternary
```

## V12 Parameter Budget: Plate vs Beam

### Summary

```
Component                          Params         Role
──────────────────────────────── ──────────────  ──────
PLATE (ternary, 1.85 bits)      116,141,056     95.0%
BEAM (precision, 16 bits)         6,074,915      5.0%
                                ──────────────
TOTAL                           122,215,971    100.0%
```

Average: **2.55 bits/param**. Memory: 39 MB (vs 244 MB FP16, 489 MB FP32).

### Plate (95% — ternary-safe, holographic sign patterns)

These weights store interference patterns. Their information lives in sign
topology. Multiple reads from different angles extract the signal.

```
Component                                    Params      Notes
────────────────────────────────────────── ──────────  ──────────────────
Embeddings (token + position)              79,888,384  TernaryEmbedding
S3 gate alignment/update projs (7 passes)   7,340,032  TernaryLinear
Desc stride K,V,O (9 strides)              7,077,888  Read 9× per token
Asc composition K,V,O (6 strides)          4,718,592  Read 4× per token
Asc retrieval K,V,O (3 strides)            2,359,296  Read 4× per token
S4 attention projs (asc + desc)            2,359,296  TernaryLinear
Consolidate FFN (512→2048→512)             2,097,664  Read 4×
Integrate FFN (512→2048→512)               2,097,152  Read 9× (3p × 3c)
Prep FFN (512→1536→512)                    1,573,376  Read 4×
Dispatch FFN (512→1536→512)                1,572,864  Read 9× (3p × 3c)
S2 direction projs (6 transitions)         1,572,864  TernaryLinear
Modulation projs (3 asc + 3 desc)          1,572,864  TernaryLinear
MetaS4 projs (q,k,v,out)                  1,048,576  TernaryLinear
Retrieval conditioning, S5 delta, etc.       862,208  Various ternary
```

**Why these are plate:**
- K, V, O projections are confirmed ternary-safe by beam trace
  (attn_dense: 2.6° avg error per layer when ternarized)
- FFN weights store sign patterns — holographic score 0.98 across
  9 models (sessions 093-096). In V12, depth means each FFN is read
  multiple times from different angles, compensating for magnitude loss
- S4/S3/S2/modulation projs are structural routing — sign patterns
  determine which information flows where, not how much

### Beam (5% — precision-critical, controls readout angle)

These weights control WHERE to look in the plate and HOW to gate
information flow. They determine the beam angle, not the plate content.

```
Component                                    Params      Notes
────────────────────────────────────────── ──────────  ──────────────────
Desc stride Q (9 strides)                  2,359,296  Beam angle (biggest!)
Asc composition Q (6 strides)              1,572,864  Beam angle
Proposal head (nn.Linear)                  1,218,816  S4→S5 control
Asc retrieval Q (3 strides)                  786,432  Beam angle
CombDispatch register conditioning            86,032  Dispatch modulation
GLA write gates (3 strides, nn.Linear)        12,312  Memory gating
S3 write gates (7 passes, nn.Linear)          10,773  Register gating
RMSNorm weights                               10,240  Amplitude calibration
Emphasis/budget projs (nn.Linear)             11,525  S4→S3 control
S5 gate/alarm/CycleCont (nn.Linear)            6,625  Various gates
```

**Why these are beam:**
- Q projections confirmed precision-critical by beam trace
  (5.1° avg error per layer when ternarized). Q determines
  the attention pattern — which positions to read from
- Write gates (nn.Linear with sigmoid) are precision-critical —
  they control binary on/off decisions about information flow
- RMSNorm weights calibrate activation amplitude — the one
  place where absolute magnitude matters
- Alarm/emphasis/budget projs control system-level behavior —
  small but consequential

### Boundary cases

The **dispatch projection** (CombinatorDispatch.dispatch) is TernaryLinear.
This is V12's beam-angle equivalent for combinator selection. The beam
trace says Q needs precision, so this deserves watching:
- It's (512 → 16), very small — 8,192 params
- Dispatch entropy regularization provides gradient signal
- S4 emphasis bias and alarm dispatch bias (both nn.Linear) provide
  additive corrections in logit space
- The ternary dispatch projection sets the BASE angle; the precision
  biases STEER it. This is a viable architecture.

If dispatch collapse recurs despite the v12 variety fixes, converting
CombinatorDispatch.dispatch to nn.Linear (precision) would add only
8K params to the beam budget (negligible).

## Holographic Capacity: V12 vs Competition

### Depth × angular diversity

```
                              Depth  Angles  Capacity  Plate%  Bits/param
Architecture                  ─────  ──────  ────────  ──────  ──────────
Pythia-160M (dense, 1 pass)     1      1        1      25.0%    16.0
Qwen3.6-35B (MoE, 1 pass)      1      8        8      93.6%     2.8
V12 (ternary, 7p×3c)          6.5      9       58      95.0%     2.6
```

**V12 has 58× the holographic capacity of Pythia** at 6× fewer bits per
parameter. The depth compensates for the magnitude loss in ternary weights.

### How depth compensates

In a single-pass model (Pythia), each FFN weight contributes to ONE
matrix multiplication at ONE residual-stream state. If the weight is
ternary, the magnitude error propagates directly to the output.

In V12, the same ternary FFN weight (e.g., in the prep FFN) is read
by 4 different ascending passes, each with a different residual stream:
- Pass 0 (L0↑): fresh embeddings, fine-scale features
- Pass 1 (L1↑): L0↑ output, medium-scale features
- Pass 2 (L2↑): L1↑ output, coarse-scale features
- Pass 3 (apex): L2↑ output, global features

Each read extracts a different "facet" of the sign pattern. The ternary
error at each read is ~2-6° (from beam trace), but the errors are
UNCORRELATED across passes (different residual states). Accumulated
over 4 reads: effective error reduces by √4 = 2×.

For descending arm weights (dispatch/integrate FFN), 9 reads across
3 passes × 3 cycles: effective error reduces by √9 = 3×.

### Why this is exactly like a physical thick hologram

A physical hologram's angular selectivity scales with plate thickness:
```
Δθ ∝ λ / T
```
where λ is wavelength and T is plate thickness. A thicker plate means
each beam angle activates a narrower slice of the interference pattern —
higher angular selectivity, less cross-talk between stored patterns.

In V12:
- "Plate thickness" = number of passes × cycles = depth
- "Wavelength" ∝ 1/d_model = resolution of each read
- "Angular selectivity" = how precisely each pass extracts its facet
- More passes = thicker plate = cleaner reads from ternary signs

### Why MoE is holographic too (and V12 is better)

MoE gets angular diversity from WIDTH: 256 experts, each a separate
sign pattern. Each token activates ~8 experts — 8 angles of reading.
But 256 experts × big FFN = massive parameter redundancy.

V12 gets angular diversity from DEPTH: shared weights, 7 passes ×
3 cycles. Each pass reads the SAME signs at a different angle.
No redundant copies. Same information, more extraction.

```
MoE:  256 experts × E params = 256E stored, 8E read → 8 angles
V12:  1 set × P params = P stored, 6.5P read → 9+ angles
      Information density: V12 >> MoE
```

## Troubleshooting Guide

### If dispatch collapses (B declining, entropy dropping)

**Beam-side check:**
1. Is `emphasis_bias` active? Should see non-zero values after ~1K steps.
   The emphasis proj is nn.Linear (precision) — it should learn.
2. Is `alarm_dispatch_bias` moving? Check alarm factors.
3. Is dispatch entropy penalty activating? Check if entropy < 1.178 target.

**Plate-side check:**
4. Is the ternary dispatch projection (512→16) providing sufficient
   initial angles? The base dispatch logits come from ternary weights.
   If always near-zero → the plate can't distinguish combinators.
   Fix: convert dispatch proj to nn.Linear (adds only 8K precision params).

**Depth check:**
5. Are CycleContinue gates differentiating? If stuck at ~0.5, the
   cycle budget bias isn't working → fewer effective reads → thinner
   hologram for descending arm.

### If holographic loss stays high (ratio >> 1.0)

**Beam-side check:**
1. Are ascending Q projections learning? Check Q weight norms.
   Q determines what information gets extracted at each pass.

**Plate-side check:**
2. Are ascending FFN weights frozen by evolution? Check ternary
   flip acceptance rates. If zero flips accepted → plate is stuck.

**Depth check:**
3. Is the ascending arm using all 4 passes? Check per-pass S3 gates.
   If some passes are gated to ~0, effective depth is reduced →
   thinner hologram → worse intermediate decodability.

### If retrieval (M) registers stay dormant

**Beam-side check:**
1. GLA write gates are nn.Linear (precision). Check if they're learning.
   Initial sigmoid(-4) ≈ 0.018 — they should open with training.

**Plate-side check:**
2. GLA K,V,O projections are ternary. The retrieval pattern matching
   happens in sign topology. If patterns are too similar → GLA memory
   can't distinguish them. Check ternary cosine between stored patterns.

**Depth check:**
3. Retrieval registers are written at every ascending pass (4 writes).
   If ret_regs stay zero → the write projections aren't activated.

### If training loss plateaus

**The thick hologram may need time.** Each pass needs to learn its
beam angle independently. Early training: all passes read similar
angles (redundant). Late training: passes specialize into distinct
angles (high capacity). The transition looks like a plateau followed
by a drop.

Watch for:
- S3 gates differentiating between passes (not all identical)
- Per-pass intermediate CEs diverging (each pass decodes differently)
- CycleContinue gates diverging between cycles (not all 0.5)

These are signs that depth is being utilized — the thick hologram
is developing angular selectivity.

## Connection to V12 Design Decisions

### Why separate Q, K, V (not fused QKV)

Session 096 proved: fused QKV has holographic score 0.60 (Pythia)
vs separate Q/K/V at 0.92 (Qwen3, SmolLM3). The magnitudes in fused
QKV act as "lenses" steering between Q/K/V subspaces — breaks holography.

V12: every projection is separate TernaryLinear. Each weight matrix
encodes ONE function. This is the shape that lets gradient descent
find the holographic solution.

**Beam trace confirmation:** Q needs precision (beam angle), K/V/O
are ternary-safe (plate). You CAN'T get this separation with fused QKV.

### Why TernaryFFN works despite beam trace showing FFN needs precision

The beam trace tested Pythia's dense FFN — one read at one angle.
V12's FFN is read 4-9 times from different angles. At 4 reads,
ternary error (~4°) reduces to ~2° effective — within the safe range.

Additionally: V12's kernel functions (KIBC) handle constructive
computation in PRECISION (combinator_integrate.gate_proj is nn.Linear).
The TernaryFFN only needs to store patterns, not compute precisely.
The kernels read the plate; the gates control the reading.

### Why holographic loss is the depth enforcer

Holographic loss forces each intermediate pass to produce a decodable
output. Without it, the model could learn to use only the final pass
(effectively depth=1, thin hologram) and waste the other passes.

With holographic loss, each pass MUST contribute independently →
each pass develops its own beam angle → angular diversity emerges →
the hologram gets thick → ternary becomes sufficient.

The loss gradient slope (7× at pass 0, 1× at pass 6) preferentially
strengthens early passes — building the plate foundation first.

## Key numbers for reference

```
V12 Architecture          Value
────────────────────────  ─────
d_model                   512
Passes                    7 (4 asc + 3 desc)
Cycles per desc pass      3
Stride levels             9 (6 comp + 3 ret)
Total params              122.2M
Plate params              116.1M (95.0%)
Beam params                6.1M (5.0%)
Avg bits/param            2.55
Memory (holoquant)        39 MB
Memory (FP16)             244 MB
Compression               6.3×
Holographic capacity      58 (vs Pythia=1, Qwen=8)
Max depth per weight      9 reads (desc stride weights)
```
