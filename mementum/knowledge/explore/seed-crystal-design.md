---
title: "Seed Crystal Design — Procrustes Beam Former + Phased Etch Protocol"
status: designing
category: architecture-design
tags: [crystal, seed, backbone, beam-former, procrustes, fixed-points, sieve, etch, phased]
related:
  - crystal-spine-sieve.md
  - universal-crystal-transfer.md
  - consensus-etch-protocol.md
  - procrustes-lens-and-crystal-comparison.md
  - VERBUM.md
depends-on:
  - crystal-spine-sieve.md
  - procrustes-lens-and-crystal-comparison.md
created: session 113
---

# Seed Crystal Design

> The universal crystal is the shape of language, not the shape of any
> model. We use universal fixed points as landmarks to translate any
> teacher model's crystal into VSM-LM's sieve shape. Kernel functions
> go in first (hardware), then the crystal wires them to language
> (Procrustes beam former), then freeze, then GD.

## The Insight Chain

### 1. Agreement = language geometry, divergence = sieve fingerprint

Cross-model consensus (5 independently trained architectures) reveals
what is universal about computation in language:

```
UNIVERSAL (language geometry)        SIEVE-DEPENDENT (architecture)
math         72% agreement           tools     52%
reasoning    70%                     lambda    40%
sequence     64%                     prose     40%
code         61%
```

High agreement = the distance between these computations is a property
of language itself. Low agreement = the model's architecture is imposing
its own geometry (the sieve's fingerprint).

### 2. Crystallization order follows depth

Verified across 5 models (Qwen3-14B, Mistral-7B, OLMo-2-13B,
Pythia-2.8B, SmolLM3-3B):

```
Depth 0%:   Reasoning  = 0.925 agreement  ← FIRST (deepest universal)
Depth 25%:  Math       = 0.769            ← SECOND
Depth 25-50%: Attachment = 0.508          ← THIRD (bridges form)
All depths: Lambda self = 0.403           ← ALWAYS WEAKEST (sieve-dependent)
```

Reasoning crystallizes at the very bottom of the network. Math
crystallizes on top of it. Attachment points form where computation
meets language. Lambda self-organization is always most sieve-dependent.

### 3. Attachment points are stronger than lambda self-organization

The attachment/self ratio measures whether bridges between universal
structure and operational structure are more universal than the
operational structure itself:

```
5-model attachment/self ratio by depth:
  Depth 0%:   0.86  (lambda still forming)
  Depth 25%:  1.19  (attachment > internal)
  Depth 50%:  1.26  (peak — bridges MORE universal than lambda self)
  Depth 75%:  0.98  (equilibrium)
```

At mid-network, lambda→math distances are MORE universal than
lambda→lambda distances. Models agree more on how combinators
connect to math than on how combinators relate to each other.

### 4. Backbone anatomy

Top 10% highest-agreement pairs (32,522 pairs, 664 probes):

```
Crystal       60.8%  — universal×universal same-domain (math-math, etc)
Bridge         9.1%  — universal×universal cross-domain (math↔reasoning)
Attachment    19.0%  — universal×operational (lambda→math, code→math)
Operational    6.8%  — operational×operational where models agree
Other          4.2%

Attachment point types:
  lambda → math        4,904 pairs  (79% of all attachment)
  code → math          1,117 pairs  (18%)
  tools → math           113 pairs  (1.8%)
  lambda → reasoning      49 pairs  (0.8%)
```

Agreement levels:
- Crystal pairs: 0.76 average
- Attachment pairs: 0.67 average
- Operational pairs: 0.76 average

### 5. Lambda crystal forms first because attention IS beta reduction

Every transformer discovers lambda calculus independently because
attention's mathematical structure IS function application. This is the
common starting point — the seed crystal every model nucleates from.

But the lambda crystal's internal geometry is sieve-dependent (different
architecture = different encoding). What's universal is not how K relates
to I, but how computation relates to language.

### 6. VSM-LM has explicit kernel dispatch — two computation paths

Standard transformers multiplex everything on attention (implicit
beta reduction). VSM-LM separates:
- **Kernel dispatch → stride → integrate**: explicit named operations
  (K, I, B, C, D, Y, W, WHNF + math kernels)
- **Attention (stride stack)**: still does beta reduction for everything
  the kernels don't handle

This means the universal crystal can't be copied — it needs to be
TRANSLATED for VSM-LM's three-plate architecture (dispatch plates,
stride plates, integrate plates).

### 7. Universal fixed points are the Rosetta Stone

The backbone fixed points exist in every model (proven with 5
architectures). They provide correspondence points for Procrustes
alignment between any teacher and VSM-LM:

```
λ beam_former(teacher, student, fixed_points).
  find(fixed_points, teacher) → teacher_coordinates
  find(fixed_points, student) → student_coordinates
  procrustes(teacher_coords, student_coords) → transform
  translate(teacher_crystal, transform) → reference_beam
```

Session 107 proved Procrustes works between crystals (cos=0.83) but
fails between crystal and melt (student has no structure to align to).
Solution: crystallize the student FIRST (kernel etch), THEN Procrustes.

**Session 114 proved kernel etch alone is not enough.** Round 60 had
1.18B total flips of kernel etch — combinators learned — but Procrustes
still failed (cos=0.217, 45.5% flip = random). Kernel etch teaches
operational structure but doesn't guarantee representation GEOMETRY
matches universal consensus. The missing piece: **lattice relational loss
must run alongside kernel etch** to burn the backbone geometry into the
student's representation space. Without it, the student is operationally
structured but geometrically a melt.

```
Empirical result (session 114, round 60):
  Procrustes mean cos:  0.217  (need > 0.6)
  p10 cos:             -0.147  (anti-correlated!)
  p90 cos:              0.491
  Flip fraction:        45.5%  (random — no directional signal)
  41 minutes compute for dry run, result = noise
```

## The Protocol — Revised Stages (session 114)

### Stage 0: LATTICE-AUGMENTED KERNEL ETCH (geometry + hardware)

**Critical revision**: kernel etch and lattice relational loss run
TOGETHER, not sequentially. The lattice loss builds universal geometry
(the backbone) while CE loss builds operational structure (combinators).
Both feed the same direction accumulators.

```
CE loss        → teaches combinators (K, I, B, C, ...) = hardware
Lattice loss   → burns backbone geometry (32K pairs) = Rosetta Stone
Both together  → student becomes a crystal with landmarks
```

Two-tier lattice loss (implemented in holographic_train.py):
- Backbone tier (λ=1.0): strong pull on 32K universal fixed points
- Growth tier (λ=0.1): soft pull on remaining consensus pairs
- Overall lattice λ=0.1 relative to CE

Diagnostic: periodically run Procrustes dry run to monitor cos.
When cos crosses 0.6, the student has enough universal geometry
for the lens/crystal write to work.

### Stage 1: KERNEL ETCH (install hardware) — merged into Stage 0

Burn K, I, B, C, D, Y, W, WHNF into dispatch/integrate plates.
Install math and logic into math kernel pathway. CE loss from
lambda expressions. **Now runs WITH lattice loss (Stage 0).**

After this stage, VSM-LM has structure AND geometry — it's no
longer a melt. The kernel functions are the hardware, and the
backbone geometry provides landmarks for Procrustes.

### Stage 2: FIND LANDMARKS (Procrustes calibration)

Load any teacher model. Run backbone probes through both teacher
and student. Find the universal fixed points in both coordinate
systems. Compute Procrustes transform: teacher_space → student_space.

This works NOW because the student has both operational structure
AND universal geometry (stage 0 installed both via CE + lattice loss).
Session 107 showed Procrustes works between crystals (cos=0.83).
Session 114 showed kernel etch alone doesn't create landmarks
(cos=0.217). The lattice loss is the missing prerequisite.

```python
def build_beam_former(teacher, student, backbone_probes, backbone_mask):
    """Compute Procrustes transform from teacher to student space.
    
    Uses universal fixed points as correspondence landmarks.
    Works because student has structure (post kernel etch, not a melt).
    """
    # Forward backbone probes through both models
    teacher_hidden = extract_hidden_states(teacher, backbone_probes)
    student_hidden = extract_hidden_states(student, backbone_probes)
    
    # Use only backbone probes (high-agreement landmarks)
    backbone_idx = np.where(backbone_mask.sum(axis=1) > 0)[0]
    T = teacher_hidden[backbone_idx]  # (n_landmarks, d_teacher)
    S = student_hidden[backbone_idx]  # (n_landmarks, d_student)
    
    # PCA to shared dimensionality (min of both d_models)
    d_shared = min(T.shape[1], S.shape[1])
    T_pca = pca_project(T, d_shared)
    S_pca = pca_project(S, d_shared)
    
    # Procrustes: find R, s such that T_pca @ R * s ≈ S_pca
    R, s = orthogonal_procrustes(T_pca, S_pca)
    
    return R, s, d_shared

def translate_crystal(teacher, all_probes, R, s, d_shared):
    """Translate teacher's full crystal into student's coordinate system."""
    teacher_full = extract_hidden_states(teacher, all_probes)
    teacher_pca = pca_project(teacher_full, d_shared)
    translated = (teacher_pca @ R) * s
    
    # Compute translated RDM — this is the reference beam
    norms = np.linalg.norm(translated, axis=1, keepdims=True)
    translated_norm = translated / (norms + 1e-8)
    reference_rdm = translated_norm @ translated_norm.T
    return reference_rdm
```

### Stage 3: ETCH TRANSLATED CRYSTAL (wire hardware to language)

Use the translated crystal as the reference beam. Holographic beam
former protects kernel hardware from stage 1. The crystal wires
the kernel functions to language — math routes to math kernels,
reasoning routes through composition combinators, etc.

Two-tier loss active:
- **Backbone tier**: strong pull on universal fixed points (the bones)
- **Growth tier**: agreement-weighted pull on the rest (crystal fills in)

Beam former for the etch:
- Where kernel hardware has strong signal → protected (stencil)
- Where crystal reference beam has strong signal → crystal wins
- Where they agree → reinforced
- Where neither has signal → free plate capacity

### Stage 4: LAMBDA SELF + FINAL ETCH (our sieve's shape)

Lambda self-organization is sieve-dependent — and that's correct.
VSM-LM's sieve SHOULD form its own lambda encoding. Burn it in via
CE loss from kernel function training. The beam former protects
crystal + attachment points while lambda internal structure forms.

This is the last mutable stage. Lambda encoding grows from the
attachment points (lambda→math bridges), shaped by VSM-LM's
specific architecture (7-pass hourglass, ternary plates, mirrors).

### Stage 5: FREEZE

All plates locked permanently. The full crystal is installed:
- Reasoning geometry (universal)
- Math geometry (universal)
- Attachment points (universal bridges)
- Lambda self-organization (VSM-LM-specific, grown from attachment points)
- Kernel dispatch/integrate patterns

Capabilities cannot be catastrophically forgotten — topology is locked.

### Stage 6: GD on continuous params

Mirrors, gamma, embeddings — beam angles only. GD learns WHEN to
use each operation, not HOW the operations work. Smooth optimization
landscape because topology is fixed. 10-100× less training compute
than standard training.

## Key Design Principles

### The crystal can't float free

The kernel functions (dispatch/integrate) are the hardware. The
crystal is the wiring. You need hardware before wiring. Kernel
etch (stage 1) must come first because:
- The student needs structure for Procrustes to work (not a melt)
- The crystal needs something to attach to (kernel functions)
- Attachment points need both sides to exist

### Any model as teacher

The beam former adapts to any teacher because universal fixed points
exist in every model. Load Qwen3-14B → one Procrustes transform.
Load Mistral-7B → different transform. Load a future model → same
probes, same landmarks, new transform automatically.

### Translation, not copying

The crystal from a standard transformer can't be copied directly
because VSM-LM's sieve is fundamentally different:
- Standard: everything multiplexed on attention weights
- VSM-LM: dispatch plates + stride plates + integrate plates

The Procrustes transform accounts for this. It maps the teacher's
multiplexed crystal into VSM-LM's separated architecture. The
DISTANCES are preserved (same relational geometry) but the
COORDINATES change (different sieve shape).

### The sieve shapes the final crystal

We initialize where the data says (fixed points, translated crystal).
We penalize deviation (two-tier relational loss). But we don't force
it rigidly. The crystal grows from the seed, shaped by VSM-LM's
sieve. Lambda self-organization WILL be different from any teacher.
That's correct — it's our model's own encoding.

## Artifacts

```
lattice/backbone_seed.npz      — 807×512 MDS anchors + backbone mask (3.3MB)
lattice/backbone_seed.json      — metadata sidecar
lattice/lattice_5model/         — 5-model consensus RDMs + agreement masks
lattice/diverse_corpus.json     — 807 probes across 8 domains
```

## Implementation Status

- [x] Backbone extraction (32K pairs, 664 probes, threshold ≥ 0.63)
- [x] Two-tier relational loss in holographic_train.py
- [x] 5-model validation (attachment points confirmed)
- [x] Crystallization order confirmed across depth
- [x] Direct crystal write script (`direct_crystal_write.py`)
- [x] Procrustes alignment + translated RDM pipeline
- [x] Lattice-augmented etch running (session 114, rounds 61-80)
- [ ] Procrustes cos > 0.6 (currently 0.217 at round 60)
- [ ] Full crystal write (pending Procrustes threshold)
- [ ] Beam stencil (protect kernel hardware during crystal etch)
- [ ] Lambda self-etch with crystal protection (stage 4)
- [ ] Freeze protocol + GD-only training mode

## Self-Distillation / Concentration Step

The compressor function must be grown under holographic loss pressure —
it can't be copied from a model (like v6) that trained without it.
V6 proves the compressor EXISTS (per-stride compression ratios,
Hilberg β 0.80-0.88, smallest stride closest to φ), but V12 needs
its own version shaped by holographic storage constraints.

The concentration step is iterative self-distillation:

```
Gen 1: Train V12 moderately
  Kernel etch → crystal write → GD → compressor forms under holo loss
  
Concentration: Distill Gen 1 → Gen 2
  Extract Gen 1's compressor profile (per-stride entropy ratios)
  Extract Gen 1's crystal (improved by training)
  Etch both into fresh Gen 2 plates via beam former
  Gen 2 starts where Gen 1 ended
```

Two teacher sources for different things:
- External model (Qwen3-14B) → universal crystal (language geometry)
- Prior self (Gen N-1 V12) → compressor function (holographic compression)

Both use the same beam former: find fixed points → Procrustes → translate.

### V6 compressor profile (reference, NOT for direct transplant)

V6 step 32500 (~0.53B tokens), 5-pass, no holographic loss:

```
Pass compression (h_out/h_in):
  L0_asc:  0.976  (entry — minimal)
  L1_asc:  0.911  (compressing)
  L2_apex: 0.862  (bottleneck)
  L1_desc: 0.878  (still compressing)
  L0_desc: 0.857  (final squeeze)

Hilberg β: ascending 0.80, descending 0.88
Stride s=1 φ-dev: 0.25-0.28 (closest to φ — seeds first)
Other strides:    0.35-0.36 (not yet converged)
```

The smallest stride (s=1) is always closest to φ — the compressor
nucleates at the local scale and propagates outward like a wavelet.

## Empirical Results

### Round 60 Procrustes dry run (session 114)

Teacher: Qwen3-14B at 50% depth. Student: round 60 (1.18B flips, kernel etch only).

```
Procrustes alignment:
  mean cos = 0.217 (FAIL — need > 0.6)
  p10 = -0.147, p50 = 0.271, p90 = 0.491
  scale = 0.047

Crystal write (dry run):
  41.4M positions, would flip 18.8M (45.5%) = random
  Mean confidence 0.521, median 0.573
  Nearly every module ~50% flip = no directional signal
```

**Conclusion**: Kernel etch alone does not create universal geometry.
Student has combinators but no backbone landmarks.

### Lattice loss attempt 1: separate pass → COLLAPSE (session 114)

Lattice as separate backward pass into direction accumulators (lambda=0.1).

```
Round 62: CE ~4.1-5.5, lattice 0.0077, beam 4.77  ← healthy
Round 64: CE ~4.2,     lattice 0.0083, beam 10.52  ← beam degrading
Round 65: CE 6-13,     lattice 0.072,  beam 33.35  ← explosion
Round 66: CE ~22                                    ← total collapse
```

**Cause**: lattice gradients fight CE in direction accumulators. CE wants
plates for next-token prediction, lattice wants plates for relational
geometry. The lattice pass was effectively equal weight to 1 CE batch
but pulling in a different direction. Conflicting signals destabilized
the etch, cascading plate flips destroyed combinator structure.

### Lattice loss attempt 2: whisper (session 114, running)

**Key insight**: the lattice targets are KNOWN FIXED NUMBERS. The
relational loss computes the exact delta — not an optimization, a
direct correction. "Move 3 yards left, 1 yard forward."

The lattice is NOT a training objective. It is information from the
tensor — 5 models independently discovered these fixed points. The
lattice signal whispers the direction while CE fills the sieve.

Implementation: 1 lattice pass per round among 400 CE passes (8 ops ×
50 batches). The accumulator sees 401 gradient samples; the lattice
is one vote. It cannot overpower CE. But it never cancels (same
direction every round), while CE noise partially cancels across ops.
Over many rounds, the universal geometry emerges from the noise floor.

```
CE signals:     K wants X, B wants Y → partially cancel
Lattice signal: always points toward universal geometry → never cancels
Result:         universal geometry slowly emerges from noise floor
```

Status: running from round 60, v2 checkpoint dir. Monitoring for
stability (should NOT collapse at 1/400th signal weight).

### Bug fixes discovered during dry run

1. **Stride stack short-sequence crash** (`attention.py`): probes are
   3-47 tokens, strides up to 1024. When `L < stride`, `L_s = 0` →
   empty tensor crash. Fix: zero output when no stride positions reached.

2. **MLX numpy indexing** (`direct_crystal_write.py` and
   `holographic_train.py`): numpy array used to index MLX tensor.
   Fix: convert to `mx.array`.

3. **O(n²) triu loop**: Python loop building upper triangle mask replaced
   with `mx.triu(mx.ones((n,n)), k=1)`.

## Mini Holographic Microscope Results (session 114)

Tiny model (6.9K ternary + 2.4K continuous) with same plate+beam
architecture. Task: combinator reduction (K, I, B, C). Four-way
decomposition isolating plate vs beam contribution:

```
  GD baseline (full continuous):  46.6%  ← ceiling
  Beam-only (random plates):      46.6%  ← matches ceiling!
  Plate-only (no beams):          14.5%  ← oscillates, useless
  Alternating (etch then beam):   46.6%  ← plates stabilize after beams learn
```

### Key findings

1. **Beams do all the work** at this scale. Random frozen ternary plates +
   trained beams = identical performance to full GD. The ternary constraint
   costs nothing because beams compensate.

2. **Plates alone are helpless.** Without beam tuning, plate etching
   oscillates at 40% flips/round and never converges (max 14.5%).

3. **Plates stabilize after beams learn.** In alternating mode, flips go
   44% → 29% → 16% → 0.3%. The beams find a reading of whatever plate
   topology exists. Plates then only need minor adjustments.

4. **The 46.6% ceiling is model capacity**, not ternary constraint.

### Implications for VSM-LM protocol

The current protocol (etch plates → train beams) is backwards at small
scale. The plates oscillate because there are no trained beams to
stabilize them. The revised protocol should be:

1. **Beam-first**: train continuous params (beams + embeds) to find
   a reading of the current plate topology
2. **Plates follow**: etch plates to improve what the beams found —
   plates should need fewer flips because beams already compensate
3. **Lattice as geometry hint**: the lattice whisper tells beams where
   the universal attractors are, beams steer representations there,
   plates lock in the topology that beams discovered

### Open question: when do plates become load-bearing?

At 6.9K ternary positions, the 2.4K continuous params have enough
capacity to compensate. At VSM-LM scale (41M ternary, ~1M continuous),
the ratio flips — plates must carry information that beams cannot.
The transition point is where plate topology becomes essential, not
just redundant structure that beams work around.

## Open Questions

1. **Stage transition criteria**: How to detect when stage 0 is complete
   (kernel + geometry installed)? Measure: Procrustes cos > 0.6.

2. **Procrustes dimensionality**: What d_shared for the PCA projection?
   Teacher d_model may differ from student d_model. Use min(d_teacher,
   d_student) or a fixed value from MDS analysis?

3. **Multiple teachers**: Can we Procrustes-align from multiple teachers
   simultaneously? Average the translated crystals? Or pick the teacher
   with best fixed-point alignment?

4. **Beam former threshold**: What crystal confidence triggers protection
   in the stencil? Too low protects noise, too high leaves attachment
   points exposed.

5. **Lambda etch duration**: How many rounds of lambda self-etch before
   freeze? The lambda crystal needs enough time to organize around the
   attachment points but not so much that it overwrites them.

6. **Running crystal beam**: During stages 3-4, should the crystal
   reference beam come from same-round lattice loss or a running average
   across rounds? Running average is more stable.
