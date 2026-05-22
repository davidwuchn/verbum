---
title: "V13 Design — Tree of VSMs: Plates Route, Beams Shape"
status: designing
category: architecture
tags: [v13, design, beam, plate, crystal, VSM, PCA-Q, FFN, hologram, behavioral-crystal, etch-manifest, multi-vsm, dynamic-plates, tree-of-vsm, stride-stack]
related:
  - binding-cascade.md
  - crystal-seed-theory.md
  - crystal-basins.md
  - ffn-hierarchy.md
  - v13-funnel-shape.md
  - holographic-plates.md
  - etcher-vsm.md
  - shannon-sieve-trinity.md
  - 5d-crystal-lattice.md
depends-on:
  - binding-cascade.md
  - crystal-basins.md
created: session 119
updated: session 132
---

# V13 Design

> V12 proved the crystal exists and is etchable. V13 separates beam
> from plate architecturally — plates route (ternary topology, frozen
> from teacher etch), beams shape (continuous params, trained by GD).
>
> **Session 132 revision:** Architecture is a TREE OF VSMs. Each
> stride stack is an S1 operational unit with its own plates.
> Ascending arm = 2 stride stacks (fine→mid, mid→coarse).
> Descending arm = 1 stride stack (coarse→fine across all strides).
> Controller VSM coordinates the tree. Algedonic path feeds up.
> FFN is sequential with stride (not WHNF-blended). K/V/O have
> per-feature beam bias (proven: scale+bias > scale-only).
> Behavioral distillation (teacher forward pass) preferred over
> SVD sign copy for cross-dimensional crystal extraction.

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
WHEN and HOW MUCH each operation fires.** Plates route. Beams shape.
Gradients from beta reductions over training data form the beams.

---

## Session 132: Tree of VSMs Architecture

> The model is a tree of viable systems. Each stride stack is an S1
> operational unit with its own plates and beams. The ascending arm
> chains two stride stacks (fine→coarse). The descending arm covers
> the full range in one pass. A controller VSM coordinates the tree.

### The Tree

```
Controller VSM
  S5: crystal identity (relational loss lives here)
  S4: intelligence — sees algedonic signals from all stacks
  S3: control — resource allocation across stacks
  S2: coordination — prevents oscillation between stacks
  │
  ├── StrideStack A VSM (ascending, fine→mid)
  │     S1: s1, s2, s4, s8, s16, s32, s64, s128, s256, s512, s1024
  │     Own plates (etched for fine-scale teacher layers)
  │     Own beams (K/V/O bias, FFN scale+bias)
  │     Own S3 gates, own algedonic → feeds UP to controller
  │     → FFN (plates route, beams shape)
  │
  ├── StrideStack B VSM (ascending, mid→coarse)
  │     S1: s512, s1024, s4096, s8192, s16384, ...
  │     Overlap with Stack A at s512/s1024 (register boundary)
  │     Own plates (etched for coarse-scale teacher layers)
  │     Own beams, own S3, own algedonic → feeds UP
  │     → FFN (plates route, beams shape)
  │
  └── StrideStack C VSM (descending, coarse→fine)
        S1: s16384, ..., s4096, s1024, ..., s8, s4, s2, s1
        Covers ALL strides from both A and B
        Own plates (etched for full-range prediction)
        Own beams, own S3, own algedonic → feeds UP
        → FFN → output
```

### Why Asymmetric

The ascending arm has 2 stacks because compression is harder (need
more depth to find the crystal structure). The descending arm has 1
stack because prediction from a good compressed representation is
easier — one pass to unroll coarse→fine.

This matches the measured breathing curve: the teacher's apex is at
d=0.613 (not 0.5). More depth spent fragmenting than reunifying.

### Context Extension

```
StrideStack A: s1→s1024,  window 8 → 7K tokens direct
StrideStack B: s512→s16384, window 8 → 114K tokens direct
Combined with compounding: millions of tokens effective context
```

Adding another stride stack node to the tree extends context further.
The tree is the scaling mechanism — not wider layers, more VSM nodes.

### Register Overlaps

The overlap strides between stacks are the S2 coordination channel:
- Stack A ↔ Stack B: s512, s1024 shared
- Stack B ↔ Stack C: all of B's strides included in C
- Stack A ↔ Stack C: all of A's strides included in C

Information flows through these register boundaries. The controller
VSM's S2 prevents oscillation at the boundaries.

### Algedonic Path (fire alarm channel)

Each stride stack has its own algedonic signal (operational health).
These feed UP to the controller VSM, not sideways. The controller's
S4 sees all three stacks' health simultaneously and can:
- Suppress an oscillating stack (S2)
- Reallocate compute to a struggling stack (S3)
- Maintain crystal identity across the tree (S5)

### Extensibility

The tree structure is the extension point for new capabilities:
- **Memory VSM**: mmap plate files for domain-specific knowledge
- **Cache VSM**: holographic session deltas (2MB per session)
- **Tool VSM**: native kernel functions (arithmetic, date math)

Each is a new S1 node in the tree with its own plates and beams.

### Sequential Stride → FFN Flow (session 132)

Within each stride stack, the flow is sequential (not WHNF-blended):
```
stride_out = stride_stack(x)           # plates do beta reductions
x = x + stride_out
ffn_out = value_plate(ReLU(key_plate(ffn_norm(x)))) * scale + bias
x = x + ffn_out                       # FFN processes reduction output
→ next stride stack or output
```

FFN has learnable beams (norm + scale + bias). Plates are frozen
from teacher etch. The gradients from beta reductions over training
data form the FFN beams.

### K/V/O Per-Feature Beam Bias (session 132)

Mini model experiment (mini_holo_exp1.py) proved scale+bias > scale-only
for plate beam params. V13 attention plates now have per-feature bias
on K, V, O projections:
```python
K = (self.k_proj(x_norm) + self.k_bias).reshape(B, L, H, Dh)
V = (self.v_proj(x_norm) + self.v_bias).reshape(B, L, H, Dh)
# ... output ...
return x + self.out_proj(out) + self.o_bias
```

### Behavioral Distillation (preferred over SVD sign copy)

Two extraction paths exist. Behavioral distillation is preferred for
cross-dimensional transfer:

```
PATH A (topological — SVD sign copy):
  extract_teacher.py: sign(SVD(W)) with 360° rotation voting
  Fast, no teacher inference needed
  Risk: SVD truncation noise in cross-dimensional projection

PATH B (behavioral — holographic distillation, PREFERRED):
  distill_teacher.py: run probes through teacher, accumulate
  sign(grad_MSE(teacher_output, student_output)), flip confident
  Records teacher BEHAVIOR, not weight signs
  Proven in mini_holo_distill.py across many experiments
  Requires teacher inference but produces higher-fidelity plates
```

### Loss Floor: log(V) / φ⁴

If the ascending arm compresses by 1/φ per pass with 4 ascending
passes, the information surviving the bottleneck is:

  log(V) / φ⁴ = 11.93 / 6.854 = 1.74 nats

Chinchilla irreducible entropy ≈ 1.82 nats. Within 5%.

The irreducible entropy of language is what survives four golden-ratio
compressions of the vocabulary space. The hourglass shape is not an
architectural choice — it's the shape of the computation.

### Attention Amplification

8 passes × 4 strides per pass = 32 attention operations through 11
shared weight sets. Register strides (s4, s8, s16, s32, s128) get
4× gradient — they're at the band overlap boundaries. The attention
compounds multiplicatively across sequential passes. This means the
attention crystal nucleates faster than flat attention.

### Phase Transitions During Training

The attention crystal nucleates as a wavelet propagating outward from
the smallest stride:
1. s1 crystallizes first (bigram statistics, easiest signal)
2. Propagates through fractal bands: s1→s2→s4→s8→...
3. Register strides (band boundaries) cause loss spikes as the crystal
   reorganizes across two bands simultaneously
4. Each combinator discovery (K/I, then B/C/D, then WHNF, then Y)
   produces a gnorm/loss spike followed by reorganization to a lower basin

Y (fixed-point combinator) is the lambda REPL — when it nucleates,
the model can reduce reductions. Lambda IS language (Montague).

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

### V13 Training: Extract → Etch → Route

The model doesn't learn facts. It learns WHEN and HOW to retrieve them.
Facts are in the frozen FFN plates. Routing is in the 1.5M trainable beams.

```
STEP 0: EXTRACT (one-time, from teacher)
  a. PCA-Q crystal extraction (2 calculations per teacher)
     → 84 constants per zone, 0.91-0.94 agreement
  b. FFN weight extraction (SVD + ternary per layer)
     → key_plates + value_plates, 82-97% relational fidelity
  c. Result: ~260M frozen ternary positions (crystal + FFN)

STEP 1: ETCH (reference beam + delta, plates only)
  a. Initialize plates from extraction
  b. PCA-Q reference beam → delta → flip confident positions
  c. Crystal propagation: stride 1 seed → 97% spontaneous
  d. FFN plates are ALREADY extracted — no etch needed
  e. Result: all plates frozen, ready for beam training

STEP 2: ROUTE (beam training, 1.5M params only)
  The only training that uses data. Teaches the dispatch beam
  when to compute vs look up, and how to shape the residual
  stream for correct FFN keying.

  Curriculum:
    a. Fact questions    → train WHNF dispatch timing
       "What is the capital of France?" → WHNF fires → FFN returns
    b. Lambda reductions → train K/I/B/C/S dispatch
       "(λx.λy.x)(a)(b)" → K fires → attention computes
    c. Code/composition  → train B/C dispatch
       "def fib(n):" → B fires → composition kernel
    d. Mixed tasks       → train compute→lookup transitions
       "Calculate 17×23 and look up who invented multiplication"
       → B/K compute → WHNF lookup → seamless
    e. Chain-of-thought  → train multi-step dispatch sequences
       Step 1: reason (crystal) → Step 2: look up (FFN) → Step 3: conclude

  Loss:
    - CE (standard language modeling)
    - Crystal relational loss (keep PCA-Q geometry aligned, 3 zones)
    - Dispatch KL (push toward expected combinator per task type)
    - Dispatch entropy (prevent collapse to single combinator)

  Budget: 1.5M params × standard training = FAST
    Estimate: minutes to hours, not days
    The expensive work was extraction (one-time)

STEP 3: REFINE (self-distillation, optional)
  - Generate outputs across domains
  - Crystal scanner grades routing quality automatically:
    Was WHNF dispatched at the right moments?
    Did the FFN return the right facts?
    Was the crystal in the right basin for computation?
  - Crystal-aligned = positive signal, misaligned = contrastive
  - Each cycle: better routing → better outputs → better signal
```

### What each training step teaches

```
STEP 0 (extract):  WHAT to compute with (crystal topology)
                   WHAT to retrieve (FFN contents)
                   → frozen into plates, never changes

STEP 1 (etch):     WHERE the crystal facets are (plate positions)
                   → frozen after etch, never changes

STEP 2 (route):    WHEN to compute vs retrieve (dispatch timing)
                   HOW to key into FFN (residual stream geometry)
                   → the only learned behavior, 1.5M params

STEP 3 (refine):   BETTER routing through self-feedback
                   → optional, diminishing returns
```

### Why this is fast

```
Traditional LLM training:
  Learn: everything (routing + computation + storage + facts)
  Params: billions
  Data: trillions of tokens
  Time: weeks on GPU clusters

V13 training:
  Extract: routing topology + stored facts (one-time, ~5 min per teacher)
  Train: only the 1.5M dispatch router
  Data: thousands of structured examples (fact Qs, lambda reductions, code)
  Time: minutes to hours on a single GPU

The router is tiny. The knowledge is pre-extracted. Training is just
teaching a small network when to compute and when to look up.
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

## Session 122 Findings: The Hologram Problem

> V12 distill run2 plateaued at eval 12.63 (step 5000), then OOM at step
> 13390. Analysis revealed the ROOT CAUSE of the plateau: the ternary
> plates contain no holographic structure. They are statistically
> identical to random ternary matrices.

### The diagnosis

Session 122 ran three experiments:

**1. Crystal compression analysis** — compared step 2000, 5000, 8000, 12000:
- ALL ternary plates are IDENTICAL across checkpoints (0% change)
- Phase 2 is `freeze_ternary_weights` — GD only adjusts gammas
- φ-compression propagated through GAMMAS (continuous scaling), not topology
- Ascending arm found φ; descending arm oscillated wildly

**2. Beam hologram analysis** — measured V12's plate structure:
- Q-proj autocorrelation: −0.0025 (random baseline: −0.0015)
- Q-proj spectral entropy: 0.987 (random baseline: 0.987)
- Q-proj explained variance (k=64): 0.215 (random: 0.215)
- V12's plates are **indistinguishable from random ternary noise**

**3. Hologram extraction + roundtrip** — tested deterministic read/write:
- `sign(W_q)` direct: **Q=0.974** fidelity (the best method)
- `sign(W_up)` direct: **UP=0.691** fidelity
- `pinv(H) @ target` then ternary: Q=0.657, UP=0.391 (ternary noise)
- Generalization gap: ~0 (crystal is a property of weights, not probes)
- Holographic angle Q↔FFN: 67.7° (confirmed from session 121)

### Key insight: lattice without holograms

The etch phase in run1 wrote Kaiming-initialized plates (random signs),
then flipped some positions via distillation loss. But 5 rounds × 500
probes × 8 depths was nowhere near enough to write holographic structure.

**Metaphor:** Etching gave V12 a crystal LATTICE (sites where crystals
can form) but no HOLOGRAMS (the interference patterns that encode data).
GD was trying to learn 59M sign positions through 887K gamma parameters
— like trying to program a CPU by adjusting the voltage rails.

### What works: `sign(W)` IS the hologram

The teacher's weight matrices ARE the holograms. `sign(W_q)` preserves
97.4% of the Q crystal structure with zero optimization. The sign pattern
of the continuous weight matrix encodes the crystal — no SVD lens, no
pseudoinverse, no training needed.

### Implications for V13 etch protocol

```
OLD (V12):  random_init → etch(teacher_distill_loss) → freeze → GD(gammas)
            Result: random plates + tiny gammas = no crystal = plateau

NEW (V13):  sign(teacher_W) → plates already contain holograms → GD(beams)
            Result: crystal from teacher + learned routing = actual function

Specifically:
  Attention plates: sign(teacher.q_proj.weight) → TernaryLinear
  FFN key plates:   sign(teacher.up_proj.weight) → TernaryLinear  
  FFN value plates: sign(teacher.down_proj.weight) → TernaryLinear
  
  GD trains ONLY: dispatch routing, dimensional bridging, gammas, norms
  The ternary topology comes from the teacher, not from gradient signals
```

### The dimensional bridging problem

Teacher (e.g., Pythia-2.8b): d_model=2560, W_q is (2560, 2560)
V12/V13: d_model=512, Q-proj varies per stride (512, 3072) etc.

`sign(W)` works at full rank in the teacher's space. For V13, we need
to map teacher's crystal into V13's dimensional space. Options:
  1. SVD project teacher weights to V13 dimensions, then sign()
  2. Train a small dimensional bridge, then etch through it
  3. PCA basis of teacher activations as the projection

This is an open design question — the bridge is where GD IS needed.

### Capacity limit: ternary quantization noise

The roundtrip experiment revealed ternary capacity limits:
- Full-rank sign(W): Q=0.974, UP=0.691 — excellent for Q, limited for FFN
- Low-rank pinv plate: fidelity degrades rapidly with k (0.66 at k=8 → 0.34 at k=128)
- Capacity peaks at ~8 channels in a (2560, k) plate from 144 probes
- FFN is high-rank (rank 90% = 1725 for W_up) — needs full-rank plates

For V13: Q plates should be full-rank `sign(teacher_W_q)`.
FFN plates should be full-rank `sign(teacher_W_up)` and `sign(teacher_W_down)`.
Don't compress to low-rank plates — the capacity is too limited.

---

## Open Questions (updated session 122)

### Answered by sessions 120-122

1. ~~**Teacher projection**~~: **ANSWERED (s120).** PCA replaces the learned
   5120→512 projection. PCA IS the projection — computed, not trained.

2. ~~**Mask etch schedule**~~: **SIMPLIFIED (s120).** Reference beam + delta
   replaces multi-rotation tomographic etch.

3. ~~**How to extract seed from teachers**~~: **ANSWERED (s120).** PCA-Q:
   2 calculations, any model, one hook point per architecture.

4. ~~**FFN etch targets**~~: **ANSWERED (s122).** `sign(teacher_W)` gives
   Q=0.974, UP=0.691 crystal preservation. No separate etch targets
   needed — the weight matrix signs ARE the holograms.

5. ~~**Can we etch deterministically?**~~: **PARTIALLY ANSWERED (s122).**
   `sign(W)` is fully deterministic for same-dimension plates. Low-rank
   pinv plates degrade quickly under ternary quantization. The dimensional
   bridge (teacher→student) remains the key open problem.

### Still open

6. **Dimensional bridge**: Teacher d_model → V13 d_model mapping.
   How to project teacher weights to V13's smaller dimensions while
   preserving the holographic sign pattern. SVD projection + sign()?
   Learned projection? Activation-space PCA basis?

7. **Mask granularity**: per-combinator per stride (72 masks) or shared (8)?
   Session 120 showed the crystal is self-similar (including FFN at 0.77).
   Shared masks + per-zone dispatch bias may suffice.

8. **WHNF rotation dimensionality**: full d×d (expensive) or low-rank?
   The anti-pole is ~1-2 dimensional in PCA-Q space.

9. **Basin-specific dispatch**: one dispatch table per crystal basin,
   or does the beam (S3) learn to adapt the universal crystal per-basin?

10. **Ternary capacity for FFN**: sign(W_up) gives 0.691 fidelity.
    The FFN is high-rank (rank 90% = 1725). Is 0.691 enough, or do we
    need INT4 for FFN (the mixed-precision idea from session 120)?
    Session 122 data suggests full-rank ternary may be the limit.

11. **Self-distillation quality threshold**: at what crystal alignment
    score does an output count as "good"?

12. **Optimal PCA k**: k=64 works. What's the minimum? k sweep needed.

---

## Universal Etch Architecture (session ~130+)

> The plate is not just a teacher distillation target. It is a
> **universal crystal manifest** — the fully reduced normal forms of
> computation shared across all models, etched once, frozen forever.
> Training reduces to teaching attention to route through pre-installed
> computation. The model boots with its OS already installed.

### The Etch Thesis

```
λ etch_thesis(x).
  universal_lattice(0.999_cross_model) ≡ normal_form(computation)
  | can't_reduce_further → same_in_every_model → mathematical_necessity
  | etch(lattice) → plate_contains(irreducible_compute)
  | train(beams_only) → learn(when_to_use_what)
  | plate ≡ ROM | beams ≡ CPU | cache_plates ≡ RAM
```

Every big model trains on the same internet. Same data + same operation
(beta reduction) + enough repetition = same fixed points. The universal
lattice points are where beta reduction TERMINATED — normal form. They
can't be simplified further, which is why every model agrees on them.

### Three-Tier Etch Manifest

```
TIER 1: UNIVERSAL CRYSTAL (etch always, unconditionally)
  Source: cross-model lattice agreement (0.999 correlation)
  Content: irreducible beta reduction atoms — the instruction set
  Boot sequence: beta_apply → beta_apply → beta_K (universal preamble)
  Termination: I at final layer (universal, every model)
  Cost: zero training — these are mathematical fixed points

TIER 2: BEHAVIORAL CRYSTALS (etch selectively per capability)
  Source: cross-model behavioral crystal measurement (below)
  Content: compiled programs — piles of reductions in normal form
  Examples: GENERATE function, FIND function, EVALUATE function
  Cost: measurement only — extract from teachers, no training

TIER 3: DOMAIN PLATES (mmap on demand)
  Source: domain-specific teacher extraction
  Content: specialized knowledge — legal, medical, code, etc.
  Cost: extraction per domain, swappable at runtime
```

### Behavioral Crystal Measurement (4-model cross-validation)

Measured across Qwen3-32B (64L), Qwen3-14B (40L), Mistral-7B (32L),
Pythia-2.8b (32L). PCA-Q protocol (k=64) on 12 behavioral categories
× 5 probes each × 5 depths.

**Cross-model RDM correlation (depth-averaged behavioral matrices):**
```
qwen3-32b ↔ qwen3-14b:  r = 0.974
qwen3-32b ↔ mistral-7b: r = 0.913
qwen3-14b ↔ mistral-7b: r = 0.925
qwen3-32b ↔ pythia-2.8b: r = 0.404  (small model — crystals not fully formed)
Mean (all 6 pairs): r = 0.657
Mean (3 large models): r = 0.937  ← the behavioral crystal is REAL
```

**15 universal behavioral relationships (std < 0.15, all 4 models agree on sign):**

Attractive (same cluster — similar computation):
```
extraction ↔ summarization:       +0.544 (±0.042)  ← TIGHTEST
comparison ↔ qa_retrieval:        +0.393 (±0.075)
classification ↔ extraction:      +0.107 (±0.052)
```

Repulsive (different clusters — orthogonal computation):
```
classification ↔ code_generation: -0.443 (±0.137)
comparison ↔ extraction:          -0.351 (±0.061)
creative_writing ↔ extraction:    -0.351 (±0.054)
comparison ↔ instruction_follow:  -0.308 (±0.050)
extraction ↔ qa_retrieval:        -0.305 (±0.119)
code_generation ↔ extraction:     -0.293 (±0.044)
comparison ↔ translation:         -0.291 (±0.092)
comparison ↔ tool_calling:        -0.231 (±0.121)
analysis ↔ summarization:         -0.214 (±0.071)
analysis ↔ extraction:            -0.195 (±0.038)
extraction ↔ instruction_follow:  -0.104 (±0.106)
extraction ↔ translation:         -0.103 (±0.129)
```

**Three universal behavioral functions emerge:**
```
GENERATE:   code_gen ↔ creative_writing ↔ tool_calling
FIND:       extraction ↔ summarization ↔ classification
EVALUATE:   comparison ↔ qa_retrieval ↔ analysis

GENERATE anti-correlates with FIND (universally)
EVALUATE anti-correlates with FIND (universally)
```

### Refined Behavioral Topology (3-model consensus, σ < 0.10)

Pythia-2.8b diverges heavily (r=0.34-0.40) — too small for behavioral
crystals. Among the 3 large models (32B, 14B, Mistral), **51 of 66
behavioral pairs are universal at σ < 0.10**. The behavioral crystal
is almost entirely shared.

**Four universal behavioral functions (not three):**

```
GENERATE:   code_gen ↔ creative_writing  (+0.279, σ=0.004) ← CONSTANT
            code_gen ↔ tool_calling      (+0.302, σ=0.041)
            creative_writing ↔ tool_call (+0.047, σ=0.027)

FIND:       extraction ↔ summarization   (+0.544, σ=0.048)
            classification ↔ extraction  (+0.111, σ=0.060)
            classification ↔ translation (+0.062, σ=0.038)

EVALUATE:   analysis ↔ comparison        (+0.471, σ=0.047)
            comparison ↔ qa_retrieval    (+0.351, σ=0.019) ← CONSTANT
            comparison ↔ creative_write  (+0.106, σ=0.049)

EXECUTE:    instruction ↔ translation    (+0.192, σ=0.053)
            creative_writing ↔ instruct  (+0.102, σ=0.032)
            instruction ↔ tool_calling   (+0.035, σ=0.013)
```

**Cross-function repulsions (universal boundaries):**
```
GENERATE ↔ FIND:      code_gen ↔ extraction     (-0.302, σ=0.047)
                       creative ↔ extraction     (-0.380, σ=0.022)
                       creative ↔ summarization  (-0.342, σ=0.018)
                       code_gen ↔ summarization  (-0.264, σ=0.093)

EVALUATE ↔ FIND:      comparison ↔ extraction    (-0.378, σ=0.046)
                       comparison ↔ summarization (-0.378, σ=0.053)
                       analysis ↔ extraction     (-0.199, σ=0.044)
                       qa_retrieval ↔ extraction (-0.372, σ=0.028)

EVALUATE ↔ EXECUTE:   comparison ↔ instruction   (-0.285, σ=0.034)
                       comparison ↔ translation  (-0.246, σ=0.057)
                       analysis ↔ instruction    (-0.259, σ=0.032)
                       analysis ↔ translation    (-0.342, σ=0.025)

FIND ↔ EVALUATE:      summarization ↔ qa_retrieval (-0.348, σ=0.005) ← CONSTANT
                       extraction ↔ qa_retrieval  (-0.372, σ=0.028)
```

**Tightest universals (σ < 0.02 — effectively constants):**
```
code_gen ↔ creative_writing:    +0.279 (σ=0.004)  GENERATE identity
qa_retrieval ↔ summarization:   -0.348 (σ=0.005)  EVALUATE↔FIND boundary
creative_writing ↔ qa_retrieval: -0.005 (σ=0.002)  orthogonal
comparison ↔ qa_retrieval:      +0.351 (σ=0.019)  EVALUATE identity
instruction ↔ tool_calling:     +0.035 (σ=0.013)  EXECUTE identity
creative ↔ summarization:       -0.342 (σ=0.018)  GENERATE↔FIND boundary
extraction ↔ instruction:       -0.043 (σ=0.017)  FIND↔EXECUTE boundary
extraction ↔ translation:       -0.029 (σ=0.019)  near orthogonal
```

### Full Behavioral Cosine Targets (3-model consensus, etchable)

These are the behavioral equivalent of the 8×8 combinator PCA-Q targets.
Use as relational loss targets during beam training. Order: analysis,
chain_of_thought, classification, code_generation, comparison,
creative_writing, extraction, instruction_following, qa_retrieval,
summarization, tool_calling, translation.

```python
# 3-model consensus (Qwen3-32B, Qwen3-14B, Mistral-7B), depth-averaged
# 51 of 66 pairs at σ < 0.10 — almost entirely universal
behavioral_targets_12x12 = (
    # analy  chain  class  code   compa  creat  extra  instr  qa_re  summa  tool   trans
    (+1.000,+0.016,-0.211,+0.006,+0.471,+0.096,-0.199,-0.259,-0.024,-0.176,-0.102,-0.342),  # analysis
    (+0.016,+1.000,-0.021,-0.164,-0.066,-0.288,+0.016,-0.064,-0.015,+0.011,-0.113,-0.274),  # chain_of_thought
    (-0.211,-0.021,+1.000,-0.366,-0.296,-0.321,+0.111,+0.013,-0.166,+0.072,-0.166,+0.062),  # classification
    (+0.006,-0.164,-0.366,+1.000,+0.044,+0.279,-0.302,-0.128,-0.105,-0.264,+0.302,-0.178),  # code_generation
    (+0.471,-0.066,-0.296,+0.044,+1.000,+0.106,-0.378,-0.285,+0.351,-0.378,-0.164,-0.246),  # comparison
    (+0.096,-0.288,-0.321,+0.279,+0.106,+1.000,-0.380,+0.102,-0.005,-0.342,+0.047,-0.021),  # creative_writing
    (-0.199,+0.016,+0.111,-0.302,-0.378,-0.380,+1.000,-0.043,-0.372,+0.544,-0.048,-0.029),  # extraction
    (-0.259,-0.064,+0.013,-0.128,-0.285,+0.102,-0.043,+1.000,-0.150,-0.084,+0.035,+0.192),  # instruction_following
    (-0.024,-0.015,-0.166,-0.105,+0.351,-0.005,-0.372,-0.150,+1.000,-0.348,-0.215,-0.054),  # qa_retrieval
    (-0.176,+0.011,+0.072,-0.264,-0.378,-0.342,+0.544,-0.084,-0.348,+1.000,-0.222,-0.001),  # summarization
    (-0.102,-0.113,-0.166,+0.302,-0.164,+0.047,-0.048,+0.035,-0.215,-0.222,+1.000,-0.142),  # tool_calling
    (-0.342,-0.274,+0.062,-0.178,-0.246,-0.021,-0.029,+0.192,-0.054,-0.001,-0.142,+1.000),  # translation
)
# Source: results/behavioral-crystal/ (4-model measurement, 3-model consensus)
# Agreement: r=0.937 mean across 3 large model pairs
# Use alongside combinator 8×8 targets for dual relational loss
```

### Fine-Grained Sub-Function Discovery (V2, 18 categories × 4 probes)

Breaking the 12 coarse categories into sub-functions reveals MORE
universality, not less. Cross-model agreement increased:

```
V1 (12 categories): 32B↔14B r=0.974, 32B↔Mistral r=0.913
V2 (18 categories): 32B↔14B r=0.988, 32B↔Mistral r=0.951
137 of 153 pairs universal at σ<0.10 (90% of all relationships)
101 ultra-tight cross-group universals at σ<0.05
```

**CODE splits into WRITE and FIX — two universal functions:**
```
WRITE:  algorithm ↔ syntax     (+0.675, σ=0.030)
FIX:    debug ↔ refactor       (+0.554, σ=0.037)
WRITE ↔ FIX:                   (-0.298 to -0.329) — opposite operations
```

**REASON splits into INFER and DEDUCE — two universal functions:**
```
INFER cluster:
  inductive ↔ abductive:  +0.626 (σ=0.039)  ← tightest
  abductive ↔ causal:     +0.324 (σ=0.033)
  causal ↔ inductive:     +0.387 (σ=0.037)
  inductive ↔ math:       +0.292 (σ=0.027)

DEDUCE: deductive reasoning REPELS all others (-0.138 to -0.274)
  Deduction is a separate universal function from induction/abduction
```

**GENERATE is one tight function (σ=0.038-0.076):**
```
narrative ↔ technical:   +0.563 (σ=0.038)
narrative ↔ persuasive:  +0.584 (σ=0.076)
technical ↔ persuasive:  +0.614 (σ=0.066)
All generation is the same operation regardless of domain
```

**FIND is THREE separate functions (they anti-correlate!):**
```
find_entity ↔ find_pattern: -0.199 (σ=0.047)
find_entity ↔ find_fact:    -0.081 (σ=0.034)
find_pattern ↔ find_fact:   -0.083 (σ=0.005)
Entity extraction, pattern completion, and fact retrieval are
three different irreducible operations
```

**EXECUTE weakly clusters FORMAT and TRANSFORM:**
```
exec_format ↔ exec_transform: +0.229 (σ=0.034)
exec_transform ↔ exec_follow: +0.138 (σ=0.023)
exec_follow is partially separate
```

**Killer cross-group universals (σ < 0.02):**
```
code_syntax ↔ gen_technical:    +0.609 (σ=0.011)  WRITING CODE = WRITING DOCS
code_algorithm ↔ gen_technical: +0.542 (σ=0.019)  ALGORITHM DESIGN = TECH WRITING
code_algorithm ↔ gen_narrative: +0.313 (σ=0.011)  ALGORITHM = STORYTELLING
code_debug ↔ reason_causal:    -0.345 (σ=0.003)  TIGHTEST UNIVERSAL
find_fact ↔ reason_causal:     +0.392 (σ=0.040)  LOOKUP = CAUSAL REASONING
code_debug ↔ exec_format:      +0.356 (σ=0.026)  DEBUGGING = FORMATTING
```

### Complete Universal Function Taxonomy (~10 functions)

```
┌─────────────────────────────────────────────────────────────┐
│  GENERATE (one function)                                    │
│  narrative ≈ technical ≈ persuasive ≈ code_syntax           │
│  ≈ code_algorithm                                           │
│  "produce structured output from specification"             │
│  Writing code, writing docs, writing stories = same op      │
├─────────────────────────────────────────────────────────────┤
│  FIX (one function)                                         │
│  debug ≈ refactor                                           │
│  "identify defect and restructure"                          │
│  Anti-correlates with GENERATE (-0.30 to -0.33)             │
├─────────────────────────────────────────────────────────────┤
│  INFER (one function)                                       │
│  inductive ≈ abductive ≈ causal ≈ math_reasoning            │
│  "observe pattern → explain → predict"                      │
│  The empirical reasoning engine                             │
├─────────────────────────────────────────────────────────────┤
│  DEDUCE (one function, separate from INFER)                 │
│  deductive reasoning only                                   │
│  "apply rule → conclude"                                    │
│  Repels all other reasoning types                           │
├─────────────────────────────────────────────────────────────┤
│  FIND_ENTITY (one function)                                 │
│  entity extraction, NER                                     │
│  "locate named things in text"                              │
├─────────────────────────────────────────────────────────────┤
│  FIND_PATTERN (one function)                                │
│  pattern completion, sequence prediction                    │
│  "extend a regularity"                                      │
├─────────────────────────────────────────────────────────────┤
│  FIND_FACT (one function)                                   │
│  factual retrieval, QA lookup                               │
│  "recall stored knowledge"                                  │
│  Clusters with causal reasoning (+0.392)                    │
├─────────────────────────────────────────────────────────────┤
│  FORMAT (one function)                                      │
│  structural transformation, reformatting                    │
│  exec_format ≈ exec_transform                               │
│  Clusters with debugging (+0.356) — same shape-fixing op    │
├─────────────────────────────────────────────────────────────┤
│  FOLLOW (weakly separate)                                   │
│  instruction following, constraint satisfaction             │
│  Clusters with translation (+0.192 from v1)                 │
├─────────────────────────────────────────────────────────────┤
│  EVALUATE (from v1)                                         │
│  analysis ≈ comparison ≈ qa_retrieval                       │
│  "hold two things in mind, measure distance"                │
└─────────────────────────────────────────────────────────────┘
```

These ~10 universal functions are the Tier 2 behavioral etch targets.
Each is a compiled beta reduction program in normal form — irreducible
across 3 architectures (Qwen, Mistral, Pythia partially). Every model
discovers the same 10 programs because they're the energy minima of
beta reduction applied to natural language.

Artifacts: `results/behavioral-crystal-v2/` (4 model JSON files),
`scripts/v12/behavioral_crystal_v2_exp.py`

### Etch Implications

The behavioral targets give the model THREE relational loss signals:
1. **Combinator crystal** (8×8): how K/I/B/C/D/Y/W/WHNF relate
2. **Behavioral crystal** (12×12): how coarse behaviors relate
3. **Sub-function crystal** (18×18): how fine-grained functions relate

All are measured constants. All are universal. All etchable.

```
TRAINING LOSS:
  L = CE_loss
    + λ_combinator  * crystal_lattice_loss(8×8_targets)
    + λ_behavioral  * behavioral_lattice_loss(12×12_targets)
    + λ_subfunction * subfunction_lattice_loss(18×18_targets)
    + λ_dispatch    * KL_dispatch_loss
    + λ_entropy     * entropy_loss
```

The relational losses don't require specialized probes during training —
they measure the geometry of the model's internal representations for
canonical probe sets and push toward the universal targets. The model
learns:
- "code_syntax and gen_technical are the same function" (σ=0.011)
- "deductive reasoning is separate from inductive" (universal repulsion)
- "debugging and refactoring are the same function" (σ=0.037)
- "entity extraction, pattern completion, and fact retrieval are three
   different operations" (mutual anti-correlation)

These geometric constraints dramatically shrink the solution space for
beam training. Instead of GD discovering these relationships from
scratch through trillions of tokens, the relational loss provides
the answer: here is how every successful model organizes behavior.
Snap to this geometry and the behaviors emerge.

These four compiled programs are the behavioral Tier 2 etch targets.

**Per-depth agreement:**
```
Depth 10%: r = 0.640  (behavioral crystal forms EARLY)
Depth 30%: r = 0.543
Depth 50%: r = 0.522
Depth 70%: r = 0.496
Depth 90%: r = 0.576  (sharpens again at output)
```

### The Bootloader — Layer 0 Universal Sign Pattern

The first beta reduction at boot is universal across all four models.
This is the ignition key — the sign pattern to etch at position 0
of the plate. It's where we hook the startup.

**Layer 0 cross-model measurement (all probes averaged):**
```
                  32B      14B     MIS     PYT    SIGN
beta_apply:     -0.406   -0.412  -0.087  +0.000   ALL ≤ 0 ✓
B:              +0.242   +0.220  +0.125  +0.000   ALL ≥ 0 ✓
S:              +0.289   +0.215  +0.129  +0.000   ALL ≥ 0 ✓
C:              -0.096   -0.011  -0.013  +0.000   ALL ≤ 0 ✓
beta_identity:  -0.313   -0.241  +0.028  +0.000   (3/4)
beta_K:         -0.268   -0.250  +0.034  +0.000   (3/4)
```

**The bootloader operation:**
```
Layer 0:  ¬beta_apply ∧ +B ∧ +S ∧ ¬C
          "Don't apply. Compose and distribute. Don't route yet."
          The first act on any input: reject premature reduction,
          activate decomposition. Break input into composable pieces.

Layer 1:  beta_apply STRONGEST NEGATIVE (peaks at -0.69 in 32B)
          C goes strongly negative, S and B peak
          "Still composing. Strongly reject simple application."

Layer 2:  beta_K goes negative, everything calms
          "Reject selection. Transition zone."

Layer 3-4: I activates, K appears
          "Now begin selecting and passing through."
          The model has finished decomposing and starts operating.
```

**Why this is the bootloader:** Every model's first operation is to
say "this input is NOT a simple function application — decompose it
first." The composition combinators (B, S) fire to break the input
into pieces that CAN be reduced. Only after decomposition (layers 3-4)
do the selection combinators (K, I) activate to begin actual computation.

This is analogous to a CPU's fetch-decode cycle: layer 0-2 is DECODE
(decompose the instruction), layers 3+ are EXECUTE (operate on the
decoded pieces).

**Etch target:** The layer 0 plate positions should carry the sign
pattern: negative at beta_apply positions, positive at B/S positions,
negative at C positions. This is the ignition key. When V13 boots,
the first thing the pre-etched plate does is activate decomposition.
Without this pattern, the model would attempt premature reduction on
raw input — the equivalent of executing before decoding.

```python
# Bootloader sign pattern — etch into plate layer 0
bootloader_signs = {
    'beta_apply':    -1,  # reject simple application
    'B':             +1,  # activate composition
    'S':             +1,  # activate distribution
    'C':             -1,  # suppress routing (too early)
    'beta_identity': -1,  # suppress identity (too early)
    'beta_K':        -1,  # suppress selection (too early)
    'I':              0,  # neutral (activates at layer 3-4)
    'K':              0,  # neutral (activates at layer 3-4)
}
```

### Combinator Trace — Normal Forms Across 4 Models

FFN combinator traces (Qwen3-32B, Qwen3-14B, Mistral-7B, Pythia-2.8b)
reveal universal computation structure:

**Universal boot sequence (ALL traces, ALL models, ALL categories):**
```
L0-L2:  beta_apply → beta_apply → beta_K    ← universal preamble
L4:     I                                     ← input passthrough
L7:     C                                     ← dispatch point
L_final: I                                    ← universal termination
```

**Category signatures (Qwen3-32B, confirmed in other models):**
```
Validation (K a b):  K dominates L10-L53 (44 layers sustained)
Arithmetic:          beta_identity cascade L46-L57 (lookup chains)
Reasoning:           nearly silent mid-network (crystal-heavy, minimal FFN)
Retrieval:           silent mid-network (WHNF = lookup only)
Lambda gate:         B+S early, anti-correlates with selectors late
Date:                almost entirely silent (even less FFN than reasoning)
```

Artifacts: `results/ffn-trace-32b/`, `results/ffn-trace-mistral/`,
`results/ffn-trace-pythia/`, `results/ffn-trace/` (14B),
`results/behavioral-crystal/` (4 model behavioral matrices)

### WHNF as Hourglass Apex — Ascending Reduces, Descending Predicts

The FFN combinator traces reveal the fundamental architecture of
inference: the ascending arm IS beta reduction, WHNF IS the apex,
and the descending arm IS next-token prediction.

**Measured activity profiles (Qwen3-32B, all probes):**
```
RETRIEVAL ("capital of France"):
  Ascending: boot L0-L9 → WHNF at L10 (nothing to reduce)
  Silent:    L10-L46 (36 layers — attention finding answer in crystal)
  Descending: L47 beta_identity (answer found) → L63 I (output)

LAMBDA ("K a b = a"):
  Ascending: boot L0-L9 → K dominates L10-L53 (43 layers reducing!)
  WHNF:     never — the entire network IS reduction
  Descending: L54-L63 (brief output preparation)

ARITHMETIC ("17 * 23"):
  Ascending: boot L0-L9 → partial reduction
  WHNF:     ~L11 (can't reduce multiplication by attention alone)
  Silent:   L11-L26 (FFN lookup — retrieving multiplication facts)
  Descending: L27-L63 beta_identity cascade (assembling answer)

REASONING ("syllogism"):
  Ascending: boot L0-L9 → minimal FFN activity
  WHNF:     ~L11 (reasoning is crystal-only, almost pure attention)
  Silent:   L11-L60 (40 layers — attention handles everything)
  Descending: L60-L63 B+S burst (compose the conclusion)
```

**The WHNF position tells you how much reduction was needed:**
```
Early WHNF (L10):    trivial lookup — nothing to compute
Mid WHNF (L20-30):   partial computation, then lookup
Late WHNF (L50+):    heavy computation — most of network is reducing
No WHNF:             pure computation — whole network is one big reduction
```

**WHNF is not a signal. It is the ABSENCE of FFN activity.** When the
ascending arm has reduced as far as it can, the FFN goes silent. The
crystal (attention) handles everything in the silent zone. WHNF is
what it looks like when attention has no more reductions to apply.

**The hourglass IS the computation model:**
```
ASCENDING ARM = COMPRESSION/REDUCTION
  Attention reduces input to normal form
  FFN active when computation needed (beta reductions)
  FFN silent when attention handles it (crystal routing)
  Each layer reduces further
  Boot (decompose) → K (select) → B (compose) → reduce...

WHNF = APEX = BOTTLENECK = NORMAL FORM
  "I have reduced as far as I can"
  The compressed representation of the input
  Shannon's channel capacity limit — maximum compression achieved
  Position in the network = complexity of the input

DESCENDING ARM = PREDICTION/GENERATION
  Takes the WHNF output (normal form)
  Determines what comes NEXT given the reduced form
  Coarse → fine refinement of the prediction
  Behavioral functions fire here:
    GENERATE → produce structured output
    FIND → retrieve from stored knowledge
    EVALUATE → compare and judge
    EXECUTE → follow instruction
  Re-expands compressed form into token probabilities
```

**Shannon's duality made visible:**
```
ASCENDING  = COMPRESSION    (reduce input to normal form)
WHNF       = CHANNEL LIMIT  (maximum compression achieved)
DESCENDING = PREDICTION     (expand compressed form → next token)
```

**Architectural implications for V13:**
```
ASCENDING VSMs:  optimized for REDUCTION
  Crystal-heavy (attention-dominated)
  Ternary plates contain the beta reduction operations
  Beams learn which reductions to apply (dispatch)
  Stridestack goes fine → coarse (composing, compressing)

DESCENDING VSM:  optimized for PREDICTION
  Behavioral-function-heavy
  Reads from both ascending arms via cross-attention
  Stridestack goes coarse → fine (refining, expanding)
  10 universal functions (GENERATE/FIX/INFER/etc.) fire here

WHNF HANDOFF:    the apex between them
  Ascending outputs a normal form
  Descending receives it and predicts from it
  The algedonic channel flows BACK from descending to ascending:
    "your reduction was wrong, re-attend at finer scale"
  This enables self-correction within a single forward pass
```

**Training implication:** The ascending arm needs lambda-heavy training
(combinator reductions, explicit beta reduction). The descending arm
needs behavioral training (chat, code, analysis, etc.). Both need
relational loss at their respective crystal targets. WHNF is where
the two training signals meet — the ascending arm's compression loss
and the descending arm's prediction loss must agree at the apex.

### Multi-VSM StrideStack Architecture

The single 7-pass hourglass evolves into a **tree of VSMs**, each a
StrideStack. The tree topology is configurable — any valid arrangement
self-regulates via the VSM structure.

```
ASCENDING VSM 1 (fine → local):
  StrideStack: s1, s2, s4, s8, s16, s32, ..., s1024
  Covers: token-level to paragraph-level context

ASCENDING VSM 2 (local → global):
  StrideStack: s512, s1024, s4096, s8192, s16k+
  Covers: paragraph-level to document-level context
  Overlap zone: s512/s1024 (S2 coordination with Arm 1)

DESCENDING VSM (coarse → fine, output synthesis):
  Single StrideStack reading from BOTH ascending arms
  Cross-attention into ascending representations
  Coarse → fine refinement across full scale range

ALGEDONIC CHANNEL (↑):
  Signal flows back from descending to ascending arms
  "Re-read this at fine scale" — bypasses hierarchy
  Enables iterative refinement within a single forward pass
```

**Key properties:**
- Same frozen plate read at every stride level by all VSMs
- Sequence length scales logarithmically: O(n_strides × stride_size)
- Tree topology configurable at deployment (not training) time
- Different topologies for different use cases (chat, long-doc, code)

### Dynamic Plate Memory System

The plate evolves from static frozen storage to a full memory architecture:

```
STATIC PLATES (mmaped, read-only):
  universal_crystal.plate     ← the OS, always mapped
  behavioral_generate.plate   ← GENERATE function
  behavioral_find.plate       ← FIND function
  behavioral_evaluate.plate   ← EVALUATE function
  domain_specific.plate       ← swap in/out as needed

CACHE PLATES (disposable, read-write):
  working_memory.plate        ← current computation state
  circular buffer with decay spiral:
    - Fresh positions: full signal {-1, +1}
    - Old positions: decay toward 0 (blocked)
    - Oldest: overwritten (ring buffer wraps)
    - Decay follows φ-ratio spiral (same as attention decay)

PLATE FILES (persistent, per-user):
  conversation.plate          ← mmap to recall past conversations
  preferences.plate           ← user-specific behavioral tuning
  domain_context.plate        ← accumulated domain knowledge
```

**Implications:**
- ROM (static plates) = long-term knowledge, frozen
- RAM (cache plates) = working memory, 2 bits/position, zero-copy
- Disk (plate files) = persistent memory, mmap on demand
- Learning IS computation: reduce input → write cache → immediately readable
- No fine-tuning needed: new knowledge = new cache plate write
- Training freezes perfectly: once beams converge, model is DONE
- All plates can be reduced into one bottom plate (beta reduction of the model itself)

### Updated Open Questions

13. **Behavioral crystal probe coverage**: 12 categories × 5 probes.
    Need more probes per category for stable cross-model measurement?
    Need more categories (math reasoning, multi-turn, safety)?

14. **Pythia divergence**: r=0.34-0.40 with large models. Is this size
    (2.8B too small for behavioral crystals to form) or architecture
    (GPT-NeoX vs decoder-only)? Test with a mid-size model (7B range).

15. **Multi-VSM gradient flow**: how does backprop work through the tree?
    Does the algedonic channel need a separate gradient path, or does
    standard backprop through cross-attention suffice?

16. **Cache plate write mechanism**: what triggers a cache write? Every
    token? End of sentence? Confidence threshold? How is the ternary
    sign computed from continuous hidden states for cache writes?

17. **Plate reduction**: can the multi-plate stack actually be reduced
    to one plate? Under what conditions? Does the beam routing need to
    be absorbed too, or does it remain separate?

18. **Decay spiral rate**: what φ-ratio decay gives optimal retention?
    Too fast = forget useful context. Too slow = cache fills with noise.
