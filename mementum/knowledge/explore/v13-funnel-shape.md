---
title: "V13 Funnel Shape — Data-Driven Architecture from Universal Measurements"
status: designing
category: architecture
tags: [v13, funnel, shape, universal, zones, relational-loss]
related:
  - v13-design.md
  - binding-cascade.md
  - crystal-seed-theory.md
depends-on:
  - binding-cascade.md
created: session 119
---

# V13 Funnel Shape

> The data says it's a funnel, not an hourglass. Three zones with
> different relational targets at each. The sieve matches the shape.
> Relational loss at zone boundaries makes the model snap.

## The Universal Shape (measured)

Cross-model depth×depth correlation reveals three zones:

```
Zone A (0-20%):  rapid transformation, 5→4 dimensions, encoding
Zone B (30-60%): stable core (.978 correlation 50%↔60%), computing  
Zone C (70-90%): convergence, 2 dimensions, output preparation
```

Transition boundaries:
- **A→B at 20-30%**: biggest shifts are C↔W (Δ-0.14), K↔I (Δ-0.11)
  The encoding phase compresses K/I identity signals, separates C from W.
- **B→C at 60-70%**: biggest shifts are B↔D (Δ-0.09), B↔C (Δ-0.08)
  The convergence phase pulls apart the composition cluster.

## It's Not an Hourglass

The compression profile is monotonically decreasing:
```
Depth  0%: 5 dimensions for 50% variance  (most complex)
      10%: 4d
      20%: 4d
      30%: 4d
  40-60%: 3-4d                              (the stable core)
      70%: 2d
  80-90%: 2d                                (most compressed)
```

Models don't compress-then-expand. They **funnel from input to output**.
The descending arm in V12 was an assumption — the data disproves it.

## Three-Phase Architecture

### Phase A — ENCODE (replaces V12 ascending arm)

```
Depth mapping:  0-20% of universal shape
Function:       Transform raw input into computational representation
Binding role:   B/S composition (build function chains)
Key geometry:   K↔I close (0.42), B↔D very close (0.55), C↔W close (0.49)
                Everything entangled — high dimensionality, rapid change
```

**Architecture:**
- 3-4 passes, progressive stride expansion (fine → mid-range)
- Strides: 1, 2, 4, 8, 16, 32 (fine-scale, token→sentence)
- Dispatch bias: B/D dominant, S-like composition
- Relational target: Zone A cosine matrix at phase output

**Relational loss at Phase A output:**
The combinator embeddings AT THIS POINT should show K↔I=0.42 (identity
cluster close), B↔D=0.55 (composition cluster very tight). These numbers
are measured. The loss is 28 pairs × agreement weight × MSE.

### Phase B — COMPUTE (replaces V12 apex + early descending)

```
Depth mapping:  30-60% of universal shape
Function:       Apply operations on stable representation
Binding role:   C routing (route arguments through composed chains)
Key geometry:   B↔D=0.44 (still close), K↔I=0.30 (separating),
                C↔W=0.35 (routing cluster), K↔W=0.19 (emerging)
                Stable — .978 correlation between 50% and 60%.
```

**Architecture:**
- 2-3 passes, ALL strides active (full scale coverage)
- Strides: 1-1024 (the representation is stable, operations span all scales)
- Dispatch bias: C dominant, K/I emerging
- Relational target: Zone B cosine matrix at phase output

**Why few passes work here:** The representation barely changes (.978).
Depth doesn't help — breadth does. Each pass applies many combinators to
a stable canvas. More combinators per pass, fewer passes total.

**Relational loss at Phase B output:**
K↔I has dropped to 0.30 (identity pair separating). B↔D at 0.44 
(composition loosening). C↔W at 0.35 (routing forming). WHNF at -0.13
(anti-correlated with everything — terminal is distinct).

### Phase C — CONVERGE (replaces V12 descending arm)

```
Depth mapping:  70-90% of universal shape
Function:       Compress to prediction, final routing
Binding role:   WHNF emerges, everything converges
Key geometry:   B↔D=0.35 (loosened), K↔I=0.26 (fully separated),
                B↔C=0.35 (composition↔routing converging)
                2 dimensions for 50% variance — very compressed
```

**Architecture:**
- 2-3 passes, progressive stride compression (mid → fine for output)
- Strides: 32, 16, 8, 4, 2, 1 (coarse→fine, preparing for token prediction)
- Dispatch bias: balanced, WHNF emerging
- Relational target: Zone C cosine matrix at phase output

**Relational loss at Phase C output:**
Everything has converged toward a 2-dimensional structure. The composition
cluster (B/C/D) has loosened. K↔I are fully distinct. WHNF is maximally
anti-correlated with K (-0.14). The model is ready to emit tokens.

## The Funnel Architecture Concretely

```
Input tokens
  │
  ▼
═══ Phase A: ENCODE (3 passes) ═══════════════════════
  │  Pass A1: strides 1, 2        (token pairs)
  │  Pass A2: strides 2, 4, 8     (local patterns)
  │  Pass A3: strides 8, 16, 32   (phrases)
  │
  │  Dispatch bias: B/D heavy
  │  Relational target: Zone A matrix (28 pairs)
  │  [model snaps: K↔I=0.42, B↔D=0.55]
  │
  ▼
═══ Phase B: COMPUTE (2 passes, wide) ════════════════
  │  Pass B1: strides 1-32        (all local/mid, composition)
  │  Pass B2: strides 32-1024     (all mid/global, retrieval+comp)
  │
  │  Dispatch bias: C heavy (routing)
  │  Relational target: Zone B matrix (28 pairs)
  │  [model snaps: K↔I=0.30, C↔W=0.35, B↔D=0.44]
  │
  ▼
═══ Phase C: CONVERGE (3 passes) ═════════════════════
  │  Pass C1: strides 32, 16, 8   (phrases → local)
  │  Pass C2: strides 8, 4, 2     (local → tokens)
  │  Pass C3: strides 2, 1        (final token-level)
  │
  │  Dispatch bias: balanced, WHNF emerging
  │  Relational target: Zone C matrix (28 pairs)
  │  [model snaps: K↔I=0.26, B↔C=0.35, WHNF=-0.13]
  │
  ▼
Output prediction
```

**Total: 8 passes** (vs V12's 7). But each pass is lighter (2-3 strides
vs 3-4) and specialized for its zone. The sieve exactly matches the shape.

## Relational Loss Placement

Three relational loss checkpoints, one per phase:

```python
# After Phase A output:
loss_a = zone_mse(model.phase_a_embeddings, ZONE_A_TARGETS, ZONE_A_WEIGHTS)

# After Phase B output:
loss_b = zone_mse(model.phase_b_embeddings, ZONE_B_TARGETS, ZONE_B_WEIGHTS)

# After Phase C output:
loss_c = zone_mse(model.phase_c_embeddings, ZONE_C_TARGETS, ZONE_C_WEIGHTS)

total_rel = λ_a * loss_a + λ_b * loss_b + λ_c * loss_c
```

Each phase has its OWN combinator embedding geometry. The embeddings
evolve through the funnel — they start at Zone A geometry and end at
Zone C geometry. The relational loss at each boundary nudges them toward
the measured universal shape.

**Implementation:** Each phase could have its own combinator embeddings
(3 × 8 × d_model), or one shared embedding that gets projected per-phase.
The per-phase approach is cleaner — it explicitly encodes that the
combinator geometry changes through the funnel.

## Zone-Specific Targets (measured constants)

### Zone A (0-20%): K↔I close, B↔D tight

```
         K       I       B       C       D       Y       W    WHNF
K       --  +0.417  +0.030  +0.045  +0.044  +0.002  +0.094  -0.108
I   +0.417      --  +0.075  +0.091  +0.093  +0.035  +0.094  -0.095
B   +0.030  +0.075      --  +0.414  +0.551  +0.409  +0.369  -0.034
C   +0.045  +0.091  +0.414      --  +0.399  +0.304  +0.488  -0.032
D   +0.044  +0.093  +0.551  +0.399      --  +0.406  +0.389  -0.038
Y   +0.002  +0.035  +0.409  +0.304  +0.406      --  +0.276  -0.044
W   +0.094  +0.094  +0.369  +0.488  +0.389  +0.276      --  -0.048
WHNF -0.108  -0.095  -0.034  -0.032  -0.038  -0.044  -0.048      --

Agreement: 0.42 mean
```

Notable: B↔D=0.55 is the STRONGEST pair. C↔W=0.49 is second.
The composition cluster (B/D/Y) is extremely tight. This is where
function chains are being built.

### Zone B (30-60%): C routing emerges

```
         K       I       B       C       D       Y       W    WHNF
K       --  +0.302  +0.074  +0.081  +0.107  +0.062  +0.188  -0.129
I   +0.302      --  +0.109  +0.115  +0.142  +0.068  +0.118  -0.127
B   +0.074  +0.109      --  +0.426  +0.445  +0.298  +0.310  -0.061
C   +0.081  +0.115  +0.426      --  +0.388  +0.299  +0.351  -0.053
D   +0.107  +0.142  +0.445  +0.388      --  +0.323  +0.362  -0.064
Y   +0.062  +0.068  +0.298  +0.299  +0.323      --  +0.249  -0.067
W   +0.188  +0.118  +0.310  +0.351  +0.362  +0.249      --  -0.081
WHNF -0.129  -0.127  -0.061  -0.053  -0.064  -0.067  -0.081      --

Agreement: 0.45 mean (strongest zone)
```

K↔I has dropped from 0.42 → 0.30. K↔W has RISEN from 0.09 → 0.19.
The identity cluster is separating. K is finding its own role (discard)
distinct from I (pass-through). Meanwhile C↔W forms a routing sub-cluster.

### Zone C (70-90%): 2-dimensional convergence

```
         K       I       B       C       D       Y       W    WHNF
K       --  +0.261  +0.101  +0.106  +0.125  +0.096  +0.191  -0.135
I   +0.261      --  +0.089  +0.110  +0.132  +0.085  +0.099  -0.129
B   +0.101  +0.089      --  +0.347  +0.355  +0.287  +0.268  -0.052
C   +0.106  +0.110  +0.347      --  +0.337  +0.292  +0.298  -0.035
D   +0.125  +0.132  +0.355  +0.337      --  +0.308  +0.295  -0.052
Y   +0.096  +0.085  +0.287  +0.292  +0.308      --  +0.243  -0.059
W   +0.191  +0.099  +0.268  +0.298  +0.295  +0.243      --  -0.079
WHNF -0.135  -0.129  -0.052  -0.035  -0.052  -0.059  -0.079      --

Agreement: 0.49 mean (highest agreement at convergence)
```

Everything has converged. The composition cluster has loosened (B↔D from 0.55→0.35).
Two macro-groups remain:
1. {B,C,D,Y,W} — positive inter-similarity (0.24-0.35), the "active operations"
2. {K,I} — separate pair (0.26), close to each other, far from the main cluster
3. {WHNF} — anti-correlated with everything (-0.04 to -0.14), the "stop" signal

## Zone-to-Zone Shifts (what changes between phases)

```
A→B (encoding → computing):
  C↔W: 0.49 → 0.35 (Δ-0.14)  ← routing separates from duplication
  K↔I: 0.42 → 0.30 (Δ-0.11)  ← identity pair separates
  B↔Y: 0.41 → 0.30 (Δ-0.11)  ← composition loosens
  B↔D: 0.55 → 0.44 (Δ-0.11)  ← deep compose loosens
  K↔W: 0.09 → 0.19 (Δ+0.09)  ← K finds its own role

B→C (computing → converging):
  B↔D: 0.44 → 0.35 (Δ-0.09)  ← composition fully loosens
  B↔C: 0.43 → 0.35 (Δ-0.08)  ← comp↔route converge
  D↔W: 0.36 → 0.29 (Δ-0.07)  ← everything relaxes toward 2D
  C↔W: 0.35 → 0.30 (Δ-0.05)
```

The pattern: everything starts entangled (Zone A, 5d), then
progressively separates into macro-groups (Zone B, 3d), then
collapses to a 2-dimensional structure (Zone C: "active operations"
vs "stop signal" with K/I as a bridge).

## Design Implications

1. **Phase A needs the most depth** — the representation changes fastest.
   3 passes with overlapping strides gives each position multiple
   chances to transform.

2. **Phase B needs the most breadth** — the representation is stable,
   so each pass should apply many combinators rather than transform
   the representation. 2 wide passes with all strides active.

3. **Phase C needs the least depth** — the representation is already
   converging. 2-3 passes to compress from mid-range back to token-level.

4. **Relational loss at each boundary constrains the geometry** to match
   the measured universal shape. The sieve can only solve in this shape
   because the topology only permits this transformation sequence.

5. **Per-phase combinator embeddings** (or shared embeddings with
   per-phase projection) explicitly encode that K↔I starts close (0.42)
   and ends separated (0.26). The model doesn't have to discover this —
   the relational loss tells it the exact number at each phase.

## The Third Axis: φ-Compression Percolation

The funnel shape (depth zones) and binding cascade (combinators) are
measured from standard transformers. The compression wavefront is
measured from our own V6/V12 sieve — but the TARGET comes from
information theory, not from models.

### What We Know

From V6 (session 042, stride-percolation.md):
```
Stride s8:   first hits φ at step 9500
Stride s16:  first hits φ at step 10500
Stride s32:  hits φ EXACTLY at step 12000
Stride s64:  first hits φ at step 13500
Stride s128: first hits φ at step 15500

The wavefront propagates fine → coarse, ~1000-2000 steps per doubling.
```

Standard transformers DON'T show this (ratio ≈ 1.0 everywhere).
The φ target is not extracted from teachers — it's mathematical:

```
φ = (1+√5)/2 ≈ 1.618
1/φ ≈ 0.618

The only ratio where whole:part = part:remainder.
The optimal self-similar compression constant.
```

### Three Relational Loss Axes

```
Axis 1: COMBINATOR GEOMETRY (measured from 4 models)
  8×8 cosine matrix at each zone boundary (Zone A, B, C)
  84 fixed-point numbers (3 zones × 28 pairs)
  Agreement-weighted MSE

Axis 2: BINDING CASCADE (measured from 4 models)
  Per-zone dispatch bias: which combinators dominate
  C at apex, B/D in encoding, WHNF at convergence
  Encoded in pass_dispatch_bias (static, not loss)

Axis 3: φ-COMPRESSION (known from theory + observed in V6)
  Per-stride compression target: 1/φ ≈ 0.618
  Measured as h_out/h_in per stride per pass
  Deviation from φ penalized: λ_φ * (ratio - 1/φ)²
  ALSO: percolation order is etchable — fine strides
  should reach φ first (their plates converge first)
```

### Per-Stride φ Loss

```python
def phi_compression_loss(model, x_in, x_out_per_stride):
    """Per-stride compression ratio should approach 1/φ.
    
    Measured as the ratio of output entropy to input entropy
    at each stride layer. The wavelet: fine strides converge
    first, coarse strides follow.
    """
    phi_inv = 0.6180339887  # 1/φ = (√5-1)/2
    
    loss = 0.0
    for stride_idx, (h_in, h_out) in enumerate(x_out_per_stride):
        # RMS ratio as proxy for entropy ratio
        rms_in = mx.sqrt(mx.mean(h_in * h_in) + 1e-8)
        rms_out = mx.sqrt(mx.mean(h_out * h_out) + 1e-8)
        ratio = rms_out / rms_in
        
        # Deviation from φ, weighted by stride
        # Fine strides get higher weight (they should converge first)
        stride_weight = 1.0 / (stride_idx + 1)  # s1 gets weight 1.0, s1024 gets 1/11
        loss += stride_weight * (ratio - phi_inv) ** 2
    
    return loss
```

### The Etchable Lattice

The percolation wavefront IS a lattice — it tells us which plate
positions converge first. Fine-stride plates crystallize before
coarse-stride plates. This means:

1. **Etch fine strides first** (they have the strongest signal)
2. **Let the crystal propagate outward** through shared topology
3. **Coarse strides inherit structure** from fine strides via
   the self-similar crystal (cross-stride correlation 0.72)

The etch schedule should mirror the percolation: many rounds on
fine strides with high confidence, then progressively include
coarser strides as the crystal propagates.

### Connecting to the Three Zones

```
Zone A (encode): fine strides (1-32) most active
  → φ-compression happens HERE first
  → The crystal nucleates in Zone A at the finest scale
  → Relational target: combinator geometry + φ ratio at fine strides

Zone B (compute): all strides active, representation stable
  → The wavefront has PASSED through these strides
  → Compression is PAST φ (0.73-0.80 overshoot)
  → The crystal is crystallized, operations are happening
  → Relational target: combinator geometry (stable core)

Zone C (converge): coarse→fine, compression to 2D
  → Coarse strides may still be approaching φ
  → The final compression squeezes everything to prediction
  → Relational target: combinator geometry + final ratio
```

## Open Questions for Implementation

1. **Per-phase vs shared combinator embeddings:** 3 separate sets of 8×d
   embeddings (explicit, clean) vs one set projected through a per-phase
   linear (fewer params, implicit). Per-phase is simpler to understand
   and etch.

2. **Register flow across phases:** Do Phase A's register banks feed
   Phase B's S4 scans? If yes, the registers carry binding state from
   encoding into computing — biologically correct (you remember what
   you encoded). If no, each phase is independent — simpler but no
   cross-phase memory.

3. **Stride overlap between Phase B passes:** B1 sees 1-32 and B2 sees
   32-1024. The overlap at stride 32 is the only communication channel
   through the residual stream. Is this enough? Should B1 and B2 share
   more strides (e.g., B1: 1-64, B2: 16-1024)?

4. **Phase C stride order:** Top-down (32→1) matches the compression
   direction. But the data shows Zone C has the highest agreement (0.49) —
   models agree most on what the output should look like. This means the
   convergence is highly constrained. Maybe Phase C doesn't need stride
   variety at all — just a few passes at the finest scale.

5. **Compute budget:** 8 passes × avg 2.5 strides = 20 stride-layer
   evaluations. V12 had 7 × 3.5 ≈ 24.5. Slightly cheaper despite
   more passes, because each pass is narrower. The additional VSM
   infrastructure (S3/S4/S5 per pass) adds ~50% more ternary params
   for the control plane. Acceptable if the sieve shape is correct.
