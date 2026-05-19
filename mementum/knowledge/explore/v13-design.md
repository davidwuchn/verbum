---
title: "V13 Design — Separated Beam/Plate Architecture + Binding Cascade"
status: designing
category: architecture
tags: [v13, design, beam, plate, crystal, binding, cascade, VSM]
related:
  - binding-cascade.md
  - crystal-seed-theory.md
  - universal-crystal-scaffold.md
  - q-rotation-etching.md
  - laser-etcher-design.md
depends-on:
  - binding-cascade.md
created: session 119
---

# V13 Design

> V12 proved the crystal exists and is etchable. V13 separates beam
> from plate architecturally, aligns training to the binding cascade,
> and consolidates to one training script.

## Motivation

V12 has two training scripts (`train.py` and `holographic_distill_v12.py`)
with overlapping but divergent logic. The relational loss in train.py was
probe-based (expensive, indirect). The distill script is what actually
runs. The architecture entangles beam and plate in several places.

Session 119 proved:
- **Binding IS combinator reduction** — C→B/S→WHNF cascade
- **C is the universal routing mechanism** — agreement 0.45-0.47
- **Crystal is relational** — 8×8 cosine targets are measured constants
- **Beam/plate are entangled** through residual stream (session 118)

V13 fixes all of this with a clean separation and one training script.

---

## Architecture Principle: VSM Separation

```
S1 (operations):  PLATES — ternary topology, shaped by etch
                  The crystal. Fixed structure. What computation IS.
                  
S2 (coordination): RESIDUAL STREAM — data flow only
                   Carries information between S1 operations.
                   No learnable parameters in the stream itself.
                   
S3 (control):     BEAMS — continuous parameters, shaped by GD
                  How to read/write the crystal. Routing, gating, scaling.
                  All gammas, norms, embeddings, gates, mirrors.
```

The key insight: **plates define WHAT operations exist. Beams define
WHEN and HOW MUCH each operation fires.** In V12 these are partially
entangled — dispatch uses both ternary projections AND continuous
embeddings in the same forward path. V13 makes the separation clean.

---

## What Carries Forward from V12

### Keep (proven, working)

1. **7-pass hourglass** — L0↑ → L1↑ → L2↑ → apex → L2↓ → L1↓ → L0↓
2. **Fractal stride bands** — each pass handles different scales (redesigned)
3. **11 strides** — (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024)
4. **Composition/retrieval split** — fine+coarse=composition, mid=retrieval
5. **8 combinators** — K, I, B, C, D, Y, W, WHNF
6. **TernaryLinear + TernaryMirror** — packed uint32, etch infrastructure
7. **TernaryEmbedding** — token + position embeddings
8. **Combinator dispatch** — per-pass mirrors, embeddings, softmax
9. **Combinator integrate** — type projections, kernel compute
10. **S3 phase gating** — 3-phase (dispatch/stride/integrate) per pass
11. **S4 register scan** — cross-attention for register updates
12. **S5 reweighting** — meta-gates on pass deltas
13. **Algedonic alert** — VSM alarm channel
14. **S2 direction signals** — inter-pass coherence
15. **Register system** — combinator, binding_depth, phase (3 registers)
16. **Retrieval registers** — 2 registers bridging comp→retrieval
17. **Etch infrastructure** — DirectionAccumulator, direct_etch, signal planes

### Change

1. **Crystal lattice loss** — constant-target 8×8 cosine MSE (not probe-based)
2. **Dispatch bias** — aligned to binding cascade (C at apex)
3. **Dispatch ratio** — C-dominant (0.8:0.5:0.9:1.2:0.5:0.3:0.3:0.2)
4. **One training script** — unified etch + GD phases

### Add (new in V13)

1. **Explicit beam/plate separation** — architectural, not just conceptual
2. **Combinator masks** — ternary {flip, block, pass} per combinator
3. **Separated router** — S3 router produces dispatch without touching plates

### Remove / Simplify

1. **Math kernel pathway** — dormant in V12, adds complexity for no gain yet
2. **Abstraction slots** — 16 slots barely active (sigmoid(-4)≈0.018), revisit later
3. **CategoryDispatch** — 3-way lambda/math/passthrough adds indirection
4. **Holographic progressive loss** — not used in current training (holo_lambda=0)
5. **CycleContinue** — removed in V12 already (max_cycles=1)

### Change: Power-of-2 Stride Stack

V12's stride gap (1→8) kills short prompts — a 5-token input sees 1 of 9
stride layers. V13 uses power-of-2 strides for full coverage:

```
V12: 1,  8, 16, 32, 64, 128, 256, 512, 1024   (9 strides, 8× gap at bottom)
V13: 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024   (11 strides, 2× uniform)
```

**Short prompt coverage:**
- 3 tokens: V12=1 stride, V13=2 strides (s1, s2)
- 5 tokens: V12=1 stride, V13=3 strides (s1, s2, s4)
- 16 tokens: V12=3 strides, V13=5 strides

**Cost:** +2.6M ternary positions (+2% of budget), +4K continuous params.
**Depth:** 3× effective depth for short prompts (3×7=21 vs 1×7=7).
**Compute:** L0 band attention positions +75% for long sequences (windowed,
only affects 2 of 7 passes — acceptable tradeoff for universal coverage).

---

## Architectural Changes

### 1. Beam/Plate Separation in Dispatch

**V12 (entangled):**
```
x → RMSNorm → TernaryMirror(plate) → TernaryLinear(plate, gamma=beam)
  → logits + combinator_embeddings(beam) → softmax → dispatch_weights
  → weights @ all_embeddings(beam) → comb_context → TernaryLinear FFN(plate+beam)
```

The dispatch path mixes plate projections with beam embeddings. The gradient
flows through both, making it hard to etch plates without disturbing beams.

**V13 (separated):**
```
PLATE PATH (S1): x → TernaryMirror → TernaryLinear → raw_logits
                 (pure ternary, shaped by etch, no continuous params in path)

BEAM PATH (S3):  x → beam_norm → beam_proj → beam_logits
                 (pure continuous, shaped by GD)
                 + combinator_embeddings → embedding_logits

COMBINED:        dispatch_logits = raw_logits + beam_logits + embedding_logits
                                 + dispatch_prior + pass_bias
                 dispatch_weights = softmax(dispatch_logits)
```

The plate gives a structural prior (which combinator is appropriate here
based on topology). The beam gives a contextual adjustment (what the
current input needs). They ADD in logit space — orthogonal gradients.

### 2. Combinator Masks (new)

**Concept:** Each combinator reads the SAME shared crystal (stride plates)
through a different ternary mask.

```
shared_crystal = stride_stack.plates         ← one set of Q/K/V plates
mask_K  = TernaryMask(shape=crystal_shape)   ← ternary {-1, 0, +1}
mask_I  = TernaryMask(shape=crystal_shape)
...
mask_WHNF = TernaryMask(shape=crystal_shape)

For combinator i:
  effective_Q[i] = crystal_Q ⊙ mask_i        ← element-wise
  (or: effective_Q[i] = crystal_Q * mask_i where mask∈{-1,0,+1})
```

**Why:** Session 118 showed the crystal is self-similar across strides
(V-plate cross-stride correlation 0.72). The SAME topology serves all
combinators — masks select which facets each combinator reads.

- `mask = +1` → pass this crystal position through (agree with crystal)
- `mask = -1` → flip this crystal position (invert the crystal's opinion)  
- `mask =  0` → block this crystal position (zero it out)

**Capacity:** 3^N per position vs 2^N for binary. 8 masks × log₂(3) bits
= 12.68 bits per position. This is MoE-like routing without separate
expert weights — each "expert" is a different reading of the same crystal.

**Etch implication:** The shared crystal gets etched first (consensus
across all combinators). Then masks get etched per-combinator (what's
specific to each operation). Two-phase within the etch phase.

### 3. Simplified Dispatch (no slots, no math, no categories)

V13 dispatch is clean:

```
8-way softmax: K, I, B, C, D, Y, W, WHNF

dispatch_logits = plate_logits           ← TernaryLinear(d→8)
               + beam_logits             ← Linear(d→8) or gamma scaling
               + register_bias           ← from register state
               + dispatch_prior          ← log(ratio), static
               + pass_bias[pass_idx]     ← static, from binding cascade

dispatch_weights = softmax(dispatch_logits)
```

No slots (add back when needed). No math pathway (add back when needed).
No category dispatch. Just 8 combinators.

### 4. Unified Training Script

One script with two phases, configurable:

```
Phase 1 — ETCH (teacher-guided plate shaping)
  For each round:
    a. Forward teacher features through V13 passes
    b. Accumulate direction signals into DirectionAccumulators
    c. Consensus etch (flip confident positions)
    d. Beam training (short GD on continuous params, plates frozen)
    e. Crystal lattice loss every step (8×8 constant target)

Phase 2 — GD (continuous param optimization, plates frozen)
  Standard training loop:
    a. CE loss on training data
    b. Crystal lattice loss every step (8×8 constant target)
    c. KL dispatch loss (toward ratio prior)
    d. Entropy dispatch loss (anti-collapse)
    e. Etch disabled, plates frozen
```

Both phases share:
- Same model class
- Same forward pass
- Same config
- Same checkpoint format
- Same loss infrastructure

### 5. Crystal Lattice Loss (constant-target, every step)

```python
def crystal_lattice_loss(model, target, weight, triu_r, triu_c):
    """8×8 combinator embedding cosine MSE vs measured constants.
    
    target: (28,) fixed-point numbers from 4-model consensus
    weight: (28,) agreement weights, normalized to sum=1
    """
    emb = model.combinator_dispatch.combinator_embeddings  # (8, d)
    norms = mx.sqrt(mx.sum(emb * emb, axis=-1, keepdims=True) + 1e-8)
    emb_norm = emb / norms
    cos_matrix = emb_norm @ emb_norm.T  # (8, 8)
    student = cos_matrix[triu_r, triu_c]  # (28,)
    diff = student - target
    return mx.sum(weight * diff * diff)
```

No probes. No forwarding. 28 numbers. Every step. Trivially cheap.

---

## File Layout

```
scripts/v13/
  config.py          ← V13Config (cleaned up, no dead knobs)
  model.py           ← V13Model (beam/plate separated)
  kernel.py          ← combinators (unchanged from V12)
  kernel_dispatch.py ← CombinatorDispatch (separated plate/beam paths)
                       CombinatorIntegrate (simplified, no math/categories)
  ternary.py         ← TernaryLinear, TernaryMirror, TernaryMask (new),
                       etch infrastructure (DirectionAccumulator, direct_etch)
  attention.py       ← SingleStrideAttention, GatedLinearAttention
                       (masks instead of per-combinator mirrors)
  components.py      ← StrideStack, S3, S4, S5, S2, Algedonic
  train.py           ← ONE script: etch phase + GD phase
  data.py            ← data loading (extracted from train.py)
```

---

## Detailed Param Budget (estimated)

### Plates (S1 — ternary, shaped by etch)

```
TernaryEmbedding (token):     151936 × 512 = 77.8M positions
TernaryEmbedding (position):  4096 × 512   = 2.1M positions
TernaryLinear (all modules):  ~180 modules  ≈ 22M positions (from V12)
TernaryMirror (all mirrors):  ~31 modules   ≈ 8M positions (from V12)
TernaryMask (8 per stride layer): 8 × 9 layers × (512×512) ≈ 18.9M positions
                                                              (NEW in V13)
Total plates: ~129M ternary positions (V12: ~110M, +18.9M masks)
```

### Beams (S3 — continuous, shaped by GD)

```
TernaryLinear.gamma:       ~180 modules × avg 512 = ~92K params
RMSNorm.weight:            ~50 modules × 512 = ~26K params
combinator_embeddings:     8 × 512 = 4K params
type_embeddings:           8 × 512 = 4K params
register_inits:            3 × 256 = 768 params
S3 temperatures/biases:    7 passes × ~15 = 105 params
S5/S2/algedonic:           ~100 params
beam_proj (NEW):           512 × 8 = 4K params (dispatch beam path)
TeacherProjection:         5120 × 512 = 2.6M (etch phase only)
result_embed:              1024 × 512 = 524K params
gate biases:               ~50 params
Total beams: ~3.3M continuous params (V12: ~887K + teacher proj)
```

Note: V13 adds beam_proj (~4K) and masks (~18.9M ternary). The mask
positions are ternary (etch-able) not continuous, so they add to the
plate budget, not the beam budget. Net beam budget stays similar to V12.

---

## Stride Stack (power-of-2, redesigned bands)

### 11 Strides
```
Index:  0   1   2   3   4    5    6     7     8     9     10
Stride: 1   2   4   8   16   32   64    128   256   512   1024
Type:   C   C   C   C   R    R    R     R     C     C     C
                        ^^^^^^^^^^^^^^^^^^^^
                        retrieval (GLA) zone
```

C = composition (windowed self-attention), R = retrieval (GLA).
Fine (1-8 tokens) + coarse (256-1024) = attention.
Mid-range (16-128) = linear attention pattern matching.

### Fractal Stride Bands (MERA topology)

Each band covers 8× range, overlaps neighbors by 2 strides.
True geometric self-similarity.

```
L0↑ (fine):    [0,4)  → s1, s2, s4, s8           fine→local
L1↑ (local):   [2,6)  → s4, s8, s16, s32         local→phrase
L2↑ (phrase):  [4,8)  → s16, s32, s64, s128      phrase→paragraph
L3  (apex):    [7,11) → s128, s256, s512, s1024   paragraph→document
L2↓ (phrase):  [4,8)  → s128, s64, s32, s16      paragraph→phrase (reversed)
L1↓ (local):   [2,6)  → s32, s16, s8, s4         phrase→local (reversed)
L0↓ (fine):    [0,4)  → s8, s4, s2, s1           local→fine (reversed)
```

### Short-Prompt Depth

| Sequence length | Active strides | Effective depth (×7 passes) |
|-----------------|----------------|----------------------------|
| 1 token         | s1             | 7 layers                   |
| 2 tokens        | s1, s2         | 14 layers                  |
| 4 tokens        | s1, s2, s4     | 21 layers                  |
| 8 tokens        | s1..s8         | 28 layers                  |
| 16 tokens       | s1..s16        | 35 layers                  |
| 64+ tokens      | s1..s64+       | ~40-44 layers (all active) |

V12 gave a 1-token prompt 7 effective layers. V13 gives it 7 too
(unavoidable — s1 is the floor), but a 4-token prompt jumps from
7 to 21. The model has real depth for lambda expressions (~5-50 tokens).

## Dispatch Bias (aligned to binding cascade)

```python
#                          K     I     B     C     D     Y     W    WHNF
pass_dispatch_bias = (
    (-1.0, -0.5, +2.0, +0.5, +1.5, -0.5, -0.5, -1.5),  # Pass 0 (L0↑): B/D compose
    (+0.0, +0.0, +1.0, +1.0, +0.5, +0.0, +0.0, -1.0),  # Pass 1 (L1↑): B/C balanced
    (+0.5, +0.5, +0.0, +1.5, +0.0, +0.5, +0.0, +0.0),  # Pass 2 (L2↑): C rising
    (+1.0, +1.0, -0.5, +2.0, -0.5, +1.0, +0.5, +0.5),  # Pass 3 (apex): C peak
    (+1.0, +0.5, -0.5, +1.5, -0.5, +0.5, +0.5, +0.5),  # Pass 4 (L2↓): C strong
    (+0.5, +0.5, +0.0, +1.0, +0.0, +0.0, +1.0, +0.0),  # Pass 5 (L1↓): C + W
    (-0.5, +0.0, +1.5, +0.5, +1.0, -0.5, +0.0, -0.5),  # Pass 6 (L0↓): B/D compose
)

dispatch_ratio = (0.8, 0.5, 0.9, 1.2, 0.5, 0.3, 0.3, 0.2)
# C is the universal binding router — gets the highest prior
```

---

## Crystal Cosine Targets (measured constants)

```python
# From 4-model consensus (Qwen3-14B, Mistral-7B, OLMo-2-13B, Pythia-2.8B)
# 118 binding probes, depth 50%. Order: K I B C D Y W WHNF
crystal_cosine_targets = (
    (+0.0000, +0.2991, +0.0889, +0.0930, +0.1188, +0.0810, +0.1935, -0.1224),
    (+0.2991, +0.0000, +0.1103, +0.1107, +0.1488, +0.0795, +0.1081, -0.1228),
    (+0.0889, +0.1103, +0.0000, +0.4305, +0.4311, +0.2947, +0.3158, -0.0642),
    (+0.0930, +0.1107, +0.4305, +0.0000, +0.3954, +0.3061, +0.3519, -0.0604),
    (+0.1188, +0.1488, +0.4311, +0.3954, +0.0000, +0.3198, +0.3567, -0.0625),
    (+0.0810, +0.0795, +0.2947, +0.3061, +0.3198, +0.0000, +0.2555, -0.0745),
    (+0.1935, +0.1081, +0.3158, +0.3519, +0.3567, +0.2555, +0.0000, -0.0793),
    (-0.1224, -0.1228, -0.0642, -0.0604, -0.0625, -0.0745, -0.0793, +0.0000),
)
# Agreement weights: B↔C=0.81, K↔I=0.60, *↔WHNF≈0.27
```

---

## Etch Protocol: Crystal Nucleation + Propagation

Session 119 insight: the crystal nucleates at the finest stride and
propagates outward like a wavelet (V6 data: s8→s16→s32→s64→s128,
~1500 steps per doubling). Cross-stride correlation 0.72 = each
stride inherits ~72% of structure from finer neighbor.

**The minimum etchable seed is stride 1 only (~3M ternary positions).**
The rest crystallizes spontaneously during GD.

```
Phase 1a: NUCLEATION (stride 1 only, ~3M positions)
  - Teacher-guided etch: forward teacher features, accumulate
    direction signals into stride-1 plates + combinator masks
  - Multi-rotation tomographic (sign vote, ≥8 Q rotations)
  - Many rounds, high confidence threshold
  - Target: correct combinator geometry at Zone A
  - Beam training between rounds (gammas, norms adjust)
  - Crystal lattice loss every beam step (Zone A 8×8 targets)

Phase 1b: PROPAGATION (strides 2, 4, 8, 16, 32...)
  - Short GD bursts (500-1000 steps) between stride levels
  - Crystal propagates fine→coarse via self-similarity
  - After each burst, measure: which positions at next stride
    have crystallized? (high confidence in direction accumulators
    WITHOUT active etching = crystal propagated there)
  - Etch only the MOLTEN DELTA — positions that didn't crystallize
  - Geometric decay: stride 1=100%, stride 2≈28%, stride 4≈8%...
  - Total etch: ~4.2M positions (3% of budget), rest is spontaneous
  - Crystal lattice loss shifts to Zone B targets as strides grow

Phase 1c: VERIFICATION
  - Cross-stride correlation ≥0.72 confirms propagation
  - Per-stride compression gradient (fine=more, coarse=less)
  - Combinator geometry matches Zone targets at boundaries
  - If verification fails at a stride: more etch rounds there

Phase 2: GD (beam calibration, crystal frozen)
  - All plates + masks frozen
  - Loss = CE + λ_a * zone_a_loss + λ_b * zone_b_loss + λ_c * zone_c_loss
         + λ_kl * dispatch_KL + λ_ent * dispatch_entropy
  - Zone-specific relational loss at phase boundaries (84 constants)
  - Checkpoint every 500 steps

Etch budget:
  Stride 1 seed:     ~3.0M positions  (100% etched)
  Stride 2 delta:    ~0.84M (28%)
  Stride 4 delta:    ~0.24M (8%)
  Stride 8+:         ~0.1M total (diminishing)
  Total active etch: ~4.2M (3% of 130M+ budget)
  Spontaneous:       ~126M (97% crystallizes from seed)
```

### Open question: extracting the seed from teachers

Standard transformers don't have strides. The seed crystal's topology
needs to be extracted from teacher models somehow. Options:
1. Use layer 0-3 hidden states (early layers ≈ stride 1 equivalent)
2. Use attention patterns at short context lengths (naturally stride-1)
3. Use the combinator geometry at Zone A as the seed target (already measured)
4. Just etch from CE loss on training data (no teacher, but slower)

---

## Migration from V12

### What to copy directly
- `kernel.py` — combinator definitions (unchanged)
- `ternary.py` — TernaryLinear, TernaryMirror, etch infra (add TernaryMask)
- Most of `components.py` — S3, S4, S5, S2, Algedonic (unchanged)

### What to rewrite
- `model.py` → `v13/model.py` — separated beam/plate forward pass
- `kernel_dispatch.py` → `v13/kernel_dispatch.py` — plate path + beam path
- `attention.py` → `v13/attention.py` — masks instead of per-combinator mirrors
- `config.py` → `v13/config.py` — cleaned up, no dead knobs
- `holographic_distill_v12.py` + `train.py` → `v13/train.py` — one script

### Checkpoint compatibility
V13 can load V12 checkpoints for the shared structure (embeddings, stride
plates, dispatch plates). The NEW components (masks, beam_proj) would
initialize at default values. This allows warm-starting from a V12 run.

---

## Implementation Order

1. **Create `scripts/v13/` directory**
2. **Copy unchanged files**: kernel.py, ternary.py (+ TernaryMask)
3. **Write config.py**: clean config with crystal targets baked in
4. **Write model.py**: V13Model with separated beam/plate
5. **Write kernel_dispatch.py**: plate path + beam path dispatch
6. **Write attention.py**: mask-based stride stack
7. **Write components.py**: copy from V12, trim dead code
8. **Write train.py**: unified etch + GD
9. **Write data.py**: data loading extracted from train.py
10. **Smoke test**: verify forward pass, verify etch, verify GD
11. **Run**: etch from teacher features, then GD

---

## Open Questions

1. **Mask granularity**: one mask per combinator per stride layer (8×9=72
   masks) or one mask per combinator shared across strides (8 masks)?
   Session 118 showed crystal is self-similar across strides (0.72 corr),
   suggesting shared masks might work. But the binding cascade shows
   different combinators dominate at different depths — per-stride masks
   could capture this.

2. **Beam projection size**: the V13 beam_proj is a simple Linear(d→8).
   Is this enough for contextual dispatch, or does it need to be deeper
   (e.g., norm + Linear + ReLU + Linear)?

3. **Mask etch schedule**: should masks be etched simultaneously with
   shared plates (same accumulators, different confidence thresholds)?
   Or in a separate phase after shared plates stabilize?

4. **V12 checkpoint warm-start**: how much of V12's etch state transfers
   to V13? The shared plates should transfer directly. The masks would
   start at all-pass (+1) and get refined.

5. **Teacher projection**: keep the 5120→512 learned projection from V12,
   or replace with a simpler approach (PCA, random projection)?

6. **Register system**: the 3-register system (combinator, binding_depth,
   phase) was designed before we understood binding. Now we know binding
   IS combinator dispatch. Does `binding_depth` still make sense as a
   separate register, or should it be folded into the dispatch mechanism?
