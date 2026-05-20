---
title: "V13 Design — Separated Beam/Plate Architecture + Crystal Scanner"
status: designing
category: architecture
tags: [v13, design, beam, plate, crystal, binding, cascade, VSM, PCA-Q, WHNF, FFN]
related:
  - binding-cascade.md
  - crystal-seed-theory.md
  - crystal-basins.md
  - ffn-hierarchy.md
  - v13-funnel-shape.md
depends-on:
  - binding-cascade.md
  - crystal-basins.md
created: session 119
updated: session 120
---

# V13 Design

> V12 proved the crystal exists and is etchable. V13 separates beam
> from plate architecturally, aligns training to the binding cascade,
> and consolidates to one training script.
>
> **Session 120 update:** PCA-Q decodes the universal crystal (3-4×
> sharper than hidden states). WHNF is the FFN lookup gateway. The
> combinator dispatch IS the FFN addressing function. Etch protocol
> simplified to reference beam + delta. Crystal scanner discovers
> domain-specific crystals. FFN hierarchy confirmed.

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

Session 120 proved:
- **PCA-Q decodes the crystal** — 3-4× sharper than hidden states (0.91-0.94 agreement)
- **WHNF is the FFN lookup combinator** — stop computing = start retrieving
- **Combinator dispatch IS FFN addressing** — 8 numbers predict 40-54% of FFN
- **FFN hierarchy** — magnitude encodes generality (trunk vs leaves)
- **Crystal and FFN are connected through residual stream** (different subspaces, same state)
- **Two FFN modes** — representation (crystal geometry) vs execution (active computing)
- **WHNF bridges both modes** — the only combinator that means the same in both

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

## Crystal Cosine Targets — PCA-Q (session 120, replaces hidden-state targets)

```python
# From 4-model PCA-Q consensus (Qwen3-14B, Mistral-7B, OLMo-2-13B, Pythia-2.8B)
# 118 binding probes, PCA dim=64. Order: K I B C D Y W WHNF
# Agreement: 0.91-0.94 across all zones (3-4× sharper than hidden-state targets)
# WHNF is the anti-pole: negative with everything (hidden states MASKED this)

# Zone A (0-20%): encode. Two orthogonal groups.
# {K,I} pair = 0.92. {B,C,D,Y,W} cluster = 0.57-0.98. K↔B = 0.08 (near orthogonal).
pcaq_zone_a_targets = (
    (+1.0000, +0.9210, +0.0771, +0.0906, +0.1280, +0.0363, +0.2031, -0.1694),  # K
    (+0.9210, +1.0000, +0.1177, +0.1228, +0.1553, +0.0921, +0.1837, -0.1994),  # I
    (+0.0771, +0.1177, +1.0000, +0.7963, +0.9778, +0.8370, +0.7426, -0.0094),  # B
    (+0.0906, +0.1228, +0.7963, +1.0000, +0.7680, +0.6651, +0.9219, -0.0246),  # C
    (+0.1280, +0.1553, +0.9778, +0.7680, +1.0000, +0.8057, +0.7676, -0.0246),  # D
    (+0.0363, +0.0921, +0.8370, +0.6651, +0.8057, +1.0000, +0.5693, -0.0235),  # Y
    (+0.2031, +0.1837, +0.7426, +0.9219, +0.7676, +0.5693, +1.0000, -0.0213),  # W
    (-0.1694, -0.1994, -0.0094, -0.0246, -0.0246, -0.0235, -0.0213, +1.0000),  # WHNF
)

# Zone B (30-60%): compute. Groups begin to merge. K↔I = 0.79.
pcaq_zone_b_targets = (
    (+1.0000, +0.7865, +0.1948, +0.2265, +0.3232, +0.1768, +0.5360, -0.1862),  # K
    (+0.7865, +1.0000, +0.2479, +0.2511, +0.3463, +0.1739, +0.3781, -0.2448),  # I
    (+0.1948, +0.2479, +1.0000, +0.8878, +0.8937, +0.6623, +0.6851, -0.1227),  # B
    (+0.2265, +0.2511, +0.8878, +1.0000, +0.8316, +0.7200, +0.7318, -0.1027),  # C
    (+0.3232, +0.3463, +0.8937, +0.8316, +1.0000, +0.6798, +0.8064, -0.1729),  # D
    (+0.1768, +0.1739, +0.6623, +0.7200, +0.6798, +1.0000, +0.5653, -0.0840),  # Y
    (+0.5360, +0.3781, +0.6851, +0.7318, +0.8064, +0.5653, +1.0000, -0.1379),  # W
    (-0.1862, -0.2448, -0.1227, -0.1027, -0.1729, -0.0840, -0.1379, +1.0000),  # WHNF
)

# Zone C (70-90%): converge. Everything converges. WHNF strongly anti-correlated.
pcaq_zone_c_targets = (
    (+1.0000, +0.8614, +0.5238, +0.5429, +0.5910, +0.4920, +0.7262, -0.2736),  # K
    (+0.8614, +1.0000, +0.5118, +0.5256, +0.5939, +0.4862, +0.5886, -0.2750),  # I
    (+0.5238, +0.5118, +1.0000, +0.9465, +0.9510, +0.8911, +0.8192, -0.2835),  # B
    (+0.5429, +0.5256, +0.9465, +1.0000, +0.9445, +0.9115, +0.8522, -0.2888),  # C
    (+0.5910, +0.5939, +0.9510, +0.9445, +1.0000, +0.8983, +0.8613, -0.3000),  # D
    (+0.4920, +0.4862, +0.8911, +0.9115, +0.8983, +1.0000, +0.7707, -0.2701),  # Y
    (+0.7262, +0.5886, +0.8192, +0.8522, +0.8613, +0.7707, +1.0000, -0.2838),  # W
    (-0.2736, -0.2750, -0.2835, -0.2888, -0.3000, -0.2701, -0.2838, +1.0000),  # WHNF
)
# Source: results/pcaq-targets/pcaq_targets.json
```

---

## Etch Protocol: Reference Beam + Delta (session 120 simplification)

Session 120 replaced the multi-rotation tomographic etch with a much
simpler protocol: the PCA-Q crystal IS the reference beam. Etch =
measure delta from reference → flip plates toward alignment.

```
OLD (session 119): Multi-rotation tomographic etch
  - ≥8 Q rotations, sign voting, many rounds, confidence thresholds
  - Complex scheduling, hard to tune

NEW (session 120): Reference beam + delta
  - The crystal IS KNOWN (84 PCA-Q constants per zone, 0.91-0.94 agreement)
  - One measurement: PCA-project Q → 8×8 cosine → delta from target
  - Plates: accumulate delta signals → flip when confident
  - Beams: GD minimizes the same delta (continuous version)
  - Both share the SAME reference beam — the measured crystal
```

### Teacher extraction (2 calculations)

Any model can be a teacher. Architecture adaptation = one hook point:
```python
# Separate Q/K/V (Mistral, Llama, Qwen, OLMo):
hook → layer.self_attn.q_proj

# Fused QKV (Pythia, GPT-NeoX):
hook → layer.attention.query_key_value → slice [:d_model]

# Then:
q_pca = PCA(q_vectors, k=64)        # Calculation 1: strip model noise
rdm = cosine(q_pca @ q_pca.T)       # Calculation 2: relational geometry
# → the crystal. Universal. Etchable.
```

### Three-phase training

```
Phase 1: ETCH (reference beam + delta)
  Every step:
    a. PCA-project model's Q at zone boundaries
    b. Compute 8×8 cosine matrix of combinator embeddings
    c. Delta = model cosine - PCA-Q target (the reference beam)
    d. Accumulate delta into direction accumulators
    e. Flip confident positions (ternary etch)
    f. Beam GD on continuous params (same delta, continuous gradient)
  Crystal propagation is automatic:
    - Etch stride 1 first (strongest signal)
    - Self-similarity (0.72 corr) propagates to stride 2, 4, 8...
    - 97% crystallizes spontaneously from 3% seed

Phase 2: GD (beam calibration, plates frozen)
  - CE loss on training data
  - Crystal lattice loss (PCA-Q targets, all 3 zones)
  - Dispatch KL + entropy loss
  - Plates frozen, beams train
  - WHNF kernel learns the retrieval rotation

Phase 3: REFINE (self-distillation, crystal-graded)
  - Generate outputs across domains
  - Crystal scanner grades: was the model in the right basin?
  - Crystal-aligned outputs = positive training signal
  - Misaligned outputs + corrections = contrastive signal
  - Each cycle sharpens basins → better routing → better outputs
```

---

## WHNF Kernel: The FFN Retrieval Gateway (session 120)

WHNF is not "do nothing" — it's the mode switch from computing to
retrieving. The WHNF kernel rotates the hidden state to align with
the WHNF anti-pole, triggering FFN retrieval neurons.

```python
# The 8 combinator kernels and their FFN modes:
#   K:    SELECT    — project out, pick operands       → FFN selection neurons
#   I:    CARRY     — identity, pass through            → FFN pass-through neurons
#   B:    COMPOSE   — chain two operations              → FFN composition neurons
#   C:    ROUTE     — rearrange arguments               → FFN routing neurons
#   S:    DISTRIBUTE — fork one input to two uses       → FFN distribution neurons
#   D:    DOUBLE    — apply twice                       → FFN iteration neurons
#   W:    DUPLICATE  — copy one argument                → FFN duplication neurons
#   Y:    FIXPOINT  — self-reference loop               → FFN recursion neurons
#   WHNF: RETRIEVE  — mode switch to lookup ★           → FFN retrieval neurons

def whnf_kernel(h, whnf_rotation):
    """Rotate hidden state into WHNF anti-pole alignment.
    
    The crystal defines WHERE the anti-pole IS (ternary plate topology).
    The beam learns the rotation TO that anti-pole (continuous params).
    When dispatch routes to WHNF, this rotation fires:
      hidden state → anti-pole alignment → FFN retrieval neurons activate
    
    Args:
        h: hidden state (d_model,)
        whnf_rotation: learned beam parameter, continuous
    Returns:
        h_rotated: aligned with WHNF anti-pole
    """
    return h @ whnf_rotation
```

### Evidence (session 120)

- WHNF is the ONLY combinator where chain probes align with pure anchor
  in FFN space (+0.24 to +0.60, both models, all depths)
- B/C chains ANTI-correlate with their pure anchors (-0.11 to -0.29)
- The FFN has two modes: representation (crystal) and execution (computing)
- WHNF bridges both: "stop" means the same in both modes
- 8 combinator numbers predict 40-54% of FFN activation patterns
- Retrieval and analogy domains route through WHNF (lookup mode)
- Instruction routes ANTI-WHNF ("keep computing, don't stop")

### FFN Addressing (free from crystal dispatch)

The combinator dispatch IS the FFN addressing function. No separate
FFN index needed. When the crystal routes to a combinator:

```
Crystal → dispatch weights → combinator kernel → hidden state transformation
                                                        ↓
                                              Residual stream modified
                                                        ↓
                                              FFN reads modified residual
                                              (different subspace, same state)
                                                        ↓
                                              Appropriate neurons fire
                                              (predicted by combinator profile)
```

The relational structure is universal (0.83-0.87 cross-model on lambda
probes). The specific neuron assignments are model-specific. V13 etches
the crystal (universal) and trains the FFN content (model-specific).

### What to etch vs what to train

```
ETCH (from teachers, 2 calcs each):     TRAIN (via GD):
  Attention crystal (PCA-Q)               Beam (Q rotation per basin)
  FFN key crystal (PCA-FFN)               High-rank dept values (instruction, coding)
  Combinator dispatch profiles            Gammas, norms, scales
  Pareto dept values (reasoning, tool)    WHNF rotation matrix
  Attention plate topology                FFN neuron fine-tuning
  WHNF anti-pole position                 Sub-VSM router weights
```

## Mechanical FFN: WHNF Kernel as Ternary Reduction (session 120)

### The radical simplification

The FFN sub-VSM collapses to a MECHANICAL KERNEL. If the plates ARE the
extracted teacher FFN weights (SVD-projected + ternary quantized), the
lookup is just two ternary matmuls. No learned routing. No beams.
Zero continuous FFN parameters.

```
OLD: Complex FFN sub-VSM with learned rotation, gates, routers, blend
NEW: WHNF kernel = input @ key_plate → sign() → @ value_plate → output
     Two ternary matmuls. The combinator mask selects the department view.
     The activation function is sign() — ternary throughout.
```

### Why this works

1. **Keys are etched** — teacher's W_up, SVD-projected to d_model=512,
   ternary quantized. The plate IS the key matching matrix.
2. **Values are etched** — teacher's W_down, same projection + ternary.
   The plate IS the value retrieval matrix.
3. **Department routing is already done** — combinator dispatch selected
   which mirror to use. The mirror IS the department selector.
4. **No learned routing needed** — the crystal handles routing (attention
   path), the plates handle storage (FFN path). Beams only needed for
   the routing decision, not for the storage access.

### Two paths, one dispatch

```
V13 MODEL:
  Combinator dispatch (8-way softmax, continuous beam)
       │
       ├── K/I/B/C/S/D/W/Y → COMPUTE PATH (attention)
       │     Crystal plates + beams (gammas, norms, Q rotation)
       │     Has continuous params — the beam steers attention
       │
       └── WHNF → LOOKUP PATH (mechanical FFN)
             key_plate @ input → sign → value_plate → output
             ZERO continuous params — purely ternary
             Combinator mask selects department view
```

### The WHNF kernel (final, tested)

```python
def whnf_kernel(h, key_plate, value_plate):
    """Mechanical FFN lookup. No learned params. No masks.
    
    TESTED (session 120): unmasked beats masked 100% of the time.
    Department masking HURTS (-0.19 to -0.60 RDM). The neurons
    work as an ensemble — all of them contribute to the relational
    pattern. The lambda compiler handles routing in ATTENTION.
    The FFN just runs mechanically on whatever arrives.
    
    h:           hidden state from residual stream (d_model,)
    key_plate:   TernaryLinear — extracted W_up (d_model → d_ffn)
    value_plate: TernaryLinear — extracted W_down (d_ffn → d_model)
    """
    # Key match: which neurons fire? (full ensemble, no mask)
    keys = key_plate(h)                    # ternary matmul
    active = (keys > 0).float()            # binary activation
    
    # Value retrieval: all active neurons contribute
    return value_plate(active * keys)      # ternary matmul
```

**Evidence:** Masking to combinator departments degrades RDM by 0.19-0.60.
WHNF-only masking loses only 0.03 (Mistral) but still worse than full.
Exception: Pythia depth 30% where WHNF-only BEATS unmasked (+0.07) —
the WHNF neurons carry the relational pattern better than noisy full set.

**Architecture implication:** No masks needed in FFN path. No department
router. No combinator selection in FFN. The dispatch decides WHEN to
enter the FFN (WHNF dispatch). The FFN itself is a blind mechanical
pass through ALL ternary plates. The intelligence is ALL in the crystal.

### Two crystals, purely ternary

```
CRYSTAL 1 — ATTENTION (PCA-Q, etched):
  What: computation routing, combinator geometry
  Source: PCA-Q, 4-model consensus, 0.91-0.94 agreement
  Plates: TernaryLinear + TernaryMirror (attention Q/K/V/O)
  Beams: dispatch weights, gammas, norms (continuous, learned)
  
CRYSTAL 2 — FFN (SVD + ternary, extracted):
  What: key-value storage from teacher model
  Source: SVD project teacher W_up/W_down to d_model=512, ternary quantize
  Plates: TernaryLinear key_plate + value_plate (mechanical)
  Beams: NONE — zero continuous FFN params
  Fidelity: 82-97% relational structure preserved
```

### Capacity and budget

```
Attention crystal:  130M ternary positions (routing, computation)
FFN storage:        130M ternary positions (extracted teacher FFN)
  → 254K ternary vectors at d_model=512
  → covers Mistral-7B (458K neurons) via SVD compression
Total:              260M ternary = ~52MB model file

Continuous params:  ~1.5M (dispatch, gammas, norms, embeddings)
  → FFN has ZERO continuous params

Scaling:
  260M plates → covers 7B teacher
  390M plates → covers 14B teacher  
  630M plates → covers 70B (partial)
  1.13B plates → covers 70B (full) — 224MB model file

Compression vs teacher:
  Mistral-7B:  14GB → 52MB (269×)
  Qwen3-14B:   28GB → 77MB (363×)
  Llama-70B:  140GB → 224MB (625×)
```

### Extraction pipeline (fully mechanical)

```
Step 1: Load teacher model
Step 2: For each layer:
  a. Extract W_up (d_ffn × d_teacher)
  b. SVD → top-d_model right singular vectors
  c. Project: W_up_proj = W_up @ V[:, :d_model]  (d_ffn × d_model)
  d. Ternary quantize: sign(W_up_proj) → key_plate
  e. Same for W_down → value_plate
Step 3: Etch plates into V13 (one set per stride, self-similar)
Step 4: Combinator masks from attention crystal etch (already done)
Step 5: Train beams (dispatch, gammas) via GD on training data
        FFN plates stay FROZEN — they're the teacher's knowledge
```

### Holographic FFN — Mirrors Expand Capacity

The FFN sub-VSM uses TernaryMirror to read the same plate differently
per combinator department. This is holographic storage:

```
plate ⊙ mirror_K    = K-department FFN projection
plate ⊙ mirror_WHNF = WHNF-department FFN projection (retrieval)
...same plate, 8 different reconstructions
```

Capacity with mirrors:
```
130M FFN plates + 8 mirrors = 507K ternary neurons
≈ Mistral's 458K total FFN neurons (same count, lower precision)
But: 704 effective reads per neuron (8 passes × 88 views)
The sieve trades PRECISION for DEPTH.
```

### Full extraction pipeline

```
Step 1: Extract teacher W_up (d_ffn × d_teacher)
Step 2: SVD → top-d_model right singular vectors → project to d_model
Step 3: Ternary quantize projected weights → TernaryLinear plates
Step 4: Extract teacher W_down similarly → ternary value plates
Step 5: Combinator masks become the mirrors (per-department views)
Step 6: Hook FFN activations → PCA → cosine → FFN relational crystal
Step 7: Etch plates + mirrors from teacher structure
Step 8: GD trains beam params (gammas, rotations, blend gates)
```

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

## Open Questions (updated session 120)

### Answered by session 120

1. ~~**Teacher projection**~~: **ANSWERED.** PCA replaces the learned 5120→512
   projection. PCA IS the projection — computed, not trained. No teacher
   projection layer needed.

2. ~~**Mask etch schedule**~~: **SIMPLIFIED.** Reference beam + delta replaces
   multi-rotation tomographic etch. No schedule — just accumulate deltas.

3. ~~**How to extract seed from teachers**~~: **ANSWERED.** PCA-Q: 2 calculations,
   any model, one hook point per architecture.

### Still open

4. **Mask granularity**: per-combinator per stride (72 masks) or shared (8)?
   Session 120 showed the crystal is self-similar (including FFN at 0.77).
   Shared masks + per-zone dispatch bias may suffice.

5. **WHNF rotation dimensionality**: the WHNF kernel needs a rotation matrix.
   How large? Full d_model × d_model (expensive) or low-rank approximation
   (the anti-pole is ~1-2 dimensional in PCA-Q space)?

6. **FFN etch targets**: attention and FFN need separate etch targets (different
   subspaces). Can we extract FFN targets with PCA of FFN activations using
   the same probe set? Cross-model FFN agreement is 0.75-0.87 — high enough?

7. **Basin-specific dispatch**: the dispatch bias table is currently for the
   lambda basin. If there are ~6-10 crystals (reasoning, tool, lambda,
   arithmetic, coding, analogy), should each have its own dispatch profile?
   Or does the beam (S3) learn to adapt the universal crystal per-basin?

8. **Self-distillation quality threshold**: at what crystal alignment score
   does an output count as "good" for self-distillation training? Need to
   measure the crystal alignment distribution for known-good outputs.

9. **Optimal PCA k**: k=64 works. What's the minimum? k sweep needed
   (8, 16, 32, 64, 128, 256) to find the crystal's effective rank.
