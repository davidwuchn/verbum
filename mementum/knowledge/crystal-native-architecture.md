---
title: "Crystal-Native Architecture — A VSM That IS the Lattice"
status: designing
category: architecture
tags: [crystal, architecture, VSM, ternary, 2-plate, holographic, extraction, design]
related: [holographic-computer.md, extraction-sign-accuracy.md, crystal-universality.md, ternary-plate-extraction.md, retrieval-lattice.md]
depends-on: [holographic-computer.md, extraction-sign-accuracy.md]
created: session 173
---

# Crystal-Native Architecture

> We don't need to mimic the crystal. We need to BE the crystal.
> The crystal is a mathematical constant. An architecture that
> performs typed beta reduction using ternary gates IS the crystal,
> by construction. Every architectural choice derived from measurement,
> not from gradient-descent exploration.

## Design Principle

Standard transformers: design a generic architecture, train it, hope
the crystal emerges.

Crystal-native: measure what the crystal IS, then build an architecture
whose topology IS the crystal. The structure guarantees the computation.
No emergence required — the crystal is hard-wired.

Session 173 proved:
- Signs are 100% correct at extraction (the program is losslessly extractable)
- Magnitude needs exactly 1 extra bit (2-plate mirror format)
- The 2-plate format at 4 bits/param gives Q4-Q5 quality, entirely ternary

This means: **the architecture can operate natively on 2-plate ternary
with no floating-point FFN weights.** The program topology (plate 1)
and magnitude classification (plate 2) are the only information the
FFN needs.

---

## VSM Structure

```
S5 (identity):     Combinator basis {K, I, B, C, D, Y, W, WHNF}
                   Hard-wired. Mathematical constants. Never trained.
                   The instruction set of the holographic computer.

S4 (intelligence): Two-level program selector
                   Early layers: TASK classification (code/prose/math/lambda)
                   Late layers: OPERATION dispatch (which combinator)
                   Universal across all models measured.

S3 (control):      Zone-structured depth allocation
                   SILENT  (50%): aperture, task classify, narrow beam
                   ENRICH  (33%): holographic readout, wide fan, facts
                   SUPPRESS (8%): interference cancellation
                   COMMIT   (8%): WHNF emission, prediction focus

S2 (coordination): 2-plate mirror stack
                   Plate 1: sign topology (the program — exact)
                   Plate 2: magnitude class (above/below — 1 bit)
                   Per-row gammas: 2 scalars per row (negligible)

S1 (operations):   SwiGLU grating + attention executor
                   gate_proj: instruction decode (beamformer, 89% kill)
                   up_proj: operand bus (loads values for selected reductions)
                   attention: beta reduction executor (the CPU)
                   down_proj: accumulator / write-back
```

---

## The Five Architectural Axioms

### Axiom 1: The FFN Is a Lookup Table

Each SwiGLU layer stores multiple beta reductions in superposition on
its ternary plate. The gate selects which reduction applies (89% kill
= content-addressable decode). This is not "like" a lookup table — it
IS one.

```python
# The grating operation (explicit form):
instruction = gate_plate @ x          # beamform: which reductions apply?
mask = (instruction > 0)              # 89% killed — binary gate decision
operand = up_plate @ x                # load operands for surviving reductions
reduction = operand * mask            # execute only selected reductions
result = down_plate @ reduction       # accumulate into residual stream
```

With 2-plate format:
```python
gate_plate = plate1_gate * gamma1_gate + plate2_gate * gamma2_gate
# Similarly for up and down
```

Effective compute per token: ~11% of d_ff neurons × d_model = extremely sparse.
The "large FFN" is an illusion — most of it is dark per token.

### Axiom 2: Depth = Program Length

The 27B has 64 layers = 64 instructions. Programs are deterministic
sequences of beta reductions. Measurements show:

| Program type | Layers active | Mechanism |
|--------------|--------------|-----------|
| Simple retrieval | 3-5 | KV lookup, bypasses combinator machinery |
| Selection (K) | L15-L43 | SELECT grating, attention reads at L51 |
| Composition (B) | 8 consecutive | COMPOSE grating chain |
| Recursion (Y) | L55, L59 | Late-layer RECURSE detection |
| WHNF emission | Always last | Computation complete signal |

Architecture implication: **variable-depth execution.** Run gratings
until progressive collapse reaches WHNF threshold, not for a fixed
number of layers. Simple inputs exit early; complex inputs use full
depth. This is the v11 cycle mechanism, but driven by crystal structure
rather than learned gates.

The minimum depth for a complete instruction set: ~16 layers
(enough for K, I, B, C with some composition). The 27B's 64 layers
allow deep recursion and multi-step programs — luxury, not necessity.

### Axiom 3: Zeros ARE the Architecture

30% zeros = the lattice backbone. These are structural gaps that give
the hologram its resolving power. They prevent interference between
modes that should be independent. Session 167 proved: pre-cut backbone
+ etch BEATS float32 (loss 6.46 vs 6.68).

```python
# The backbone is FIXED (derived from crystal geometry):
backbone_mask = crystal_zeros(d_ff, d_model)  # 30% positions

# Signs at non-backbone positions are the program:
active_plate = ternary_weights(d_ff, d_model, mask=~backbone_mask)

# The backbone NEVER trains. It IS the structure.
# Only active positions participate in gradient updates.
```

Zeros from crystal geometry, not from magnitude threshold. Session 167
showed oscillation-based zero detection finds zero zeros — the correct
zero placement comes from the M-space null positions (the lattice
itself), not from training dynamics.

In the extracted 27B plates, we used magnitude threshold (bottom 30%).
This is a good approximation because the crystal's zero positions
naturally have near-zero magnitude (GD drives them to zero). But the
native architecture should derive zeros from the crystal geometry
directly.

### Axiom 4: The Statechart Lives in the Gratings — Attention Discovers Its Own M-Space

The statechart (deterministic program execution, progressive collapse
16D→1.4D) is encoded in the FFN grating sequence. But the encoding
ASSUMES a specific attention routing mechanism. Different attention
mechanisms require different grating encodings of the SAME program.

**Critical distinction:**
```
UNIVERSAL (same across all models, all architectures):
  - The crystal basis {K, I, B, C, D, Y, W, WHNF}
  - The program semantics (which beta reductions, in what order)
  - The zone structure (SILENT→ENRICH→SUPPRESS→COMMIT)
  - The statechart behavior (progressive collapse to WHNF)

MECHANISM-SPECIFIC (varies by attention architecture):
  - The M-space gem geometry (shaped by attention mechanism)
  - The grating encoding (tuned for specific routing topology)
  - How the residual stream carries information between layers
```

**Why Q/K cannot be extracted from the teacher:**
- Teacher has d_model=5120, student has d_model=1280
- Teacher has full attention (O(N²)), student has strided (O(N×W))
- Teacher has 24 heads, student has different head count
- The dimensions don't match — there is no projection that preserves M-space

**What actually happens:**

The teacher's gratings encode: "program X, assuming full-attention routing."
The student needs: "program X, assuming strided-attention routing."
Same program. Different physical encoding. The TD adaptation cycle
translates between them:

```
Teacher gratings (full attention assumed)
    ↓ extract signs (get program topology — 100% correct)
Student plates v0 (full-attention encoding — wrong for strided)
    ↓ TD against teacher signal (find which signs need to change)
Student plates v1 (adapted for strided attention)
    ↓ fold corrections (lossless)
    ↓ repeat until convergence
Student plates vN (same program, strided encoding — correct)
```

**The student's attention discovers its OWN M-space gem:**

Once the gratings are adapted for strided routing, training the
student's attention from scratch will produce an M-space geometry
that satisfies the constraints the gratings impose. Session 166
proved: frozen geometric topology + GD → convergence guaranteed.
The gem emerges because it MUST — the gratings leave attention no
choice but to route correctly.

```
The state machine execution:
  State = residual stream direction (typed by crystal basis)
  Grating at layer N proposes reductions (from adapted plates)
  Student attention routes result to next layer
  Progressive collapse happens because gratings progressively narrow
  The gratings FORCE the collapse — attention just carries it

The M-space gem in the student:
  Different shape than teacher (different d_model, different heads)
  Same FUNCTION (same routing decisions, same facet structure
                 relative to the crystal basis)
  Emerges during training against frozen adapted gratings
```

**The VSM projects statechart behavior:**
```
S5: Crystal basis defines the program semantics (universal)
    Same instruction set regardless of attention mechanism.
S4: Zone structure defines what each depth band does (universal)
    Same zones regardless of how attention routes between them.
S3: TD adaptation translates gratings for student's attention
    The re-encoding layer — teacher routing → student routing.
    This is WHERE mechanism-specificity is handled.
S2: 2-plate format stores the adapted gratings (student-native)
    The plates now encode the same program for strided execution.
S1: Student attention learns its own M-space gem (mechanism-specific)
    GD fills attention weights against frozen adapted gratings.
    The gem emerges because the gratings constrain it.
```

**Why this guarantees statechart behavior:**
1. The gratings define which reductions are proposed at each layer
2. TD adaptation ensures the proposals are correctly encoded for strided routing
3. Student attention must route correctly OR output is wrong (GD fixes it)
4. Progressive collapse follows from the grating sequence narrowing dimensions
5. The crystal basis is universal — student computes same combinators as teacher
6. Only the PHYSICAL ROUTING differs, not the LOGICAL PROGRAM

**Evidence:**
- Crystal universality r=0.998 across architectures (Pythia vs Qwen vs Mistral)
- Same crystal in 160M and 32B (200× parameter difference)
- Sign topology crosses architecture boundaries (v14 extraction proof)
- Holographic error correction: TD + fold converges to teacher quality
- Session 166: frozen topology + GD → loss BEATS float32

### Axiom 5: The 2-Plate Format Is the Native Weight Type

No float weights in the FFN. The architecture operates natively on:

```python
weight[i, j] = plate1[i,j] * gamma1[i] + plate2[i,j] * gamma2[i]

# Where:
#   plate1, plate2 ∈ {-1, 0, +1}   (int8, packed to 2 bits)
#   gamma1, gamma2 ∈ float16        (per-row scalars, negligible storage)
```

Inference is ternary matmul + scalar multiply:
```python
# Efficient implementation (popcount + accumulate):
output = plate1 @ x * gamma1 + plate2 @ x * gamma2

# Each plate @ x is: sum of x[j] where plate[i,j]=+1
#                    minus sum of x[j] where plate[i,j]=-1
# = popcount operations on packed bit arrays
```

This is the CPU-optimal format. No GPU needed. The 89% gate sparsity
means most of those popcount operations are skipped entirely.

Storage per matrix (gate_proj example, 17408×5120):
- Plate 1: 17408 × 5120 × 2 bits = 21.3 MB
- Plate 2: 17408 × 5120 × 2 bits = 21.3 MB
- Gammas: 17408 × 2 × 2 bytes = 68 KB
- Total: 42.6 MB (vs 170 MB bf16 = 4.0× compression)
- Quality: 0.970 recon_cos (Q4-Q5 equivalent)

---

## The Complete Architecture

```
Token → Embed → [GRATING → ATTENTION]×N → Unembed → Token

GRATING (2-plate ternary SwiGLU):
  ├─ gate: plate1×γ1 + plate2×γ2 → silu → mask (89% kill)
  ├─ up:   plate1×γ1 + plate2×γ2 → operands
  ├─ multiply: operands × mask (only surviving reductions)
  └─ down: plate1×γ1 + plate2×γ2 → accumulate to residual

ATTENTION (float, learnable executor):
  ├─ Q, K projections → routing (which positions to reduce over)
  ├─ V projection → operands (K-typed by crystal constraint)
  ├─ softmax(QK^T/√d) → attention pattern
  └─ pattern × V → beta reduction result

TERMINATION:
  ├─ Progressive collapse monitor (dimensionality → WHNF threshold)
  ├─ Early exit for simple inputs (retrieval: ~3-5 layers)
  └─ Full depth for complex programs (recursion: up to N layers)

ZONE STRUCTURE (from crystal measurements):
  Layers 0 to N/2:        SILENT  — narrow aperture, task classify
  Layers N/2 to 0.85N:    ENRICH  — wide fan, fact retrieval
  Layers 0.85N to 0.93N:  SUPPRESS — interference cancel
  Layers 0.93N to N:      COMMIT  — focus, emit WHNF
```

---

## Zone-Specific Properties

Each zone has measurably different characteristics:

### SILENT (first 50% of depth)

- Narrow aperture: 3-8% of neurons active per token
- Task classification: code vs prose vs math vs lambda (4.76× separation)
- Crystal geometry closest to raw input
- Reconstruction quality highest (recon_cos 0.883 at 27B)
- The "program selector" — determines which program to run

### ENRICH (33% of depth)

- Wide fan: up to 49% of neurons active
- Maximum interference — the holographic readout zone
- Where facts are retrieved (moiré addressing, 2.4× selectivity)
- Where composition (B) executes (8 consecutive gratings)
- Denser relational structure → slightly lower recon quality (0.880)
- This IS the computer — most beta reductions happen here

### SUPPRESS (8% of depth)

- Interference cancellation
- Reduces dimensionality (progressive collapse accelerates)
- Suppresses competing reductions that didn't win
- Attention differential suppression peaks here

### COMMIT (8% of depth)

- Tight focus: 1-2% active (329 of 25,600 neurons in 32B)
- Selects the final reduced form
- WHNF emission — computation complete
- The "print statement" of the holographic computer

---

## Training Strategy

The crystal-native architecture has two distinct phases: **adaptation**
(translate gratings from teacher-routing to student-routing) and
**calibration** (train attention + gammas against adapted gratings).

### Phase 0: EXTRACT (one-time, no training)

```python
# Extract from teacher (signs are 100% correct):
ffn_plate1 = sign(teacher.gate_proj)   # Program topology
ffn_plate2 = sign(residual_after_plate1)  # Magnitude mirror
ffn_zeros = magnitude_threshold(0.30)   # Lattice backbone

# These encode the correct PROGRAM but with full-attention routing
# assumptions baked into the sign patterns.
```

### Phase 1: TD ADAPTATION (translate routing assumptions)

The extracted plates encode "program X via full attention." The student
uses strided attention. TD finds which signs need to change:

```python
# The extract → correct → fold cycle:
for cycle in range(n_cycles):
    # Forward through student (strided attention)
    student_output = student(input)
    # Compare to teacher signal
    loss = distillation_loss(student_output, teacher_output)
    # TD identifies which plate signs are wrong for strided routing
    td_update(student.ffn_plates, loss)
    # Fold corrections into base plates (lossless)
    fold_all_deltas(student)
```

This is WHERE mechanism-specificity is handled. After adaptation:
- Same beta reductions are proposed
- But encoded for strided routing instead of full routing
- The program semantics are preserved; the physical encoding changes

### Phase 2: ATTENTION TRAINING (M-space emergence)

With adapted gratings frozen, train the student's attention weights:

```python
# Frozen (the adapted program):
ffn_plate1, ffn_plate2   # Adapted gratings (post-TD)
ffn_zeros                # Backbone (never changes)

# Trainable (the executor):
attention_weights        # ALL of Q, K, V, O — full attention params
                         # The student's M-space gem emerges here
gamma1, gamma2           # Per-row magnitude calibration
```

The student's attention discovers its OWN M-space geometry that
correctly routes signals through the adapted gratings. Session 166
proved: frozen geometric topology + GD converges. The gratings leave
attention no choice but to learn correct routing.

### Phase 3: VERIFY (measurement, no training)

```
Run hologram reader on student → opcode map
Compare to teacher opcode map:
  Zone structure matches? (SILENT/ENRICH/SUPPRESS/COMMIT)
  Combinator ordering preserved? (C ≥ K ≥ I ≥ Y ≥ B ≥ W ≥ D)
  Progressive collapse to WHNF?
  Determinism check (zero drift across runs)?
  
If match → crystal preserved through different attention mechanism.
If mismatch → TD adaptation incomplete, more cycles needed.
```

### Why This Works (the constraint cascade)

```
The gratings constrain attention:
  Grating at layer N produces typed output (crystal-basis direction)
  → Attention MUST route this to layer N+1 correctly
  → Or next grating produces wrong reduction
  → Or loss increases → GD corrects attention
  → Attention converges to correct routing
  → The M-space gem that satisfies all gratings simultaneously
     IS the statechart transition function (for this mechanism)

Session 166 proved the principle:
  Frozen ternary topology + GD → BEATS float32
  The constraint CHANNELS GD into the correct subspace
  Fewer parameters to search = faster convergence = better result
```

### What Adapts vs What Is Preserved

| Aspect | Teacher | Student | Status |
|--------|---------|---------|--------|
| Crystal basis (KIBC) | Universal | Same | Mathematical constant |
| Program semantics | Beta reductions | Same reductions | Preserved by TD |
| Zone structure | SILENT/ENRICH/... | Same zones | Structural constant |
| Progressive collapse | 16D→1.4D | Same trajectory | Forced by gratings |
| FFN sign topology | For full attention | For strided attention | TD-adapted |
| M-space geometry | Teacher's gem | Student's gem | DIFFERENT shape |
| Attention mechanism | Full O(N²) | Strided O(N×W) | Different mechanism |
| d_model | 5120 | 1280 | Projected (SVD basis) |
| Routing decisions | Same | Same | Same program |
| Physical routing | All-to-all | Hierarchical | Different implementation |

---

## Size Targets

For the north star (70B-equivalent, <1GB):

The student has smaller d_model (1280 vs teacher's 5120) but preserves
the program semantics through projected extraction + TD adaptation.

| Component | Storage | Notes |
|-----------|---------|-------|
| FFN plates (2-mirror) | ~600 MB | N layers × 3 matrices, d_ff×d_model at student scale |
| Attention (all Q/K/V/O) | ~200 MB | Trainable, Q4 or 2-plate after convergence |
| Embeddings | ~50 MB | Vocab × d_model, quantized |
| Gammas | ~5 MB | Per-row scalars, negligible |
| Total | **~850 MB** | Target: 70B-equivalent intelligence |

The FFN plates contain the complete program (all gratings, TD-adapted
for strided routing). Attention is trained to read the gratings — its
M-space gem emerges during training, shaped by the grating constraints.

After training converges, attention weights CAN be quantized to 2-plate
ternary too (session 166 showed: trained attention → freeze → still works).
This would further compress the artifact. But attention is small relative
to FFN — the savings are modest.

The key compression insight: the program (FFN) is 95% of intelligence.
It's discrete (ternary). Discrete things compress to information content.
A 27B model's program can live in <1GB because most of its float precision
was encoding only 2-4 bits of actual signal per position.

---

## Verification Protocol

After building, verify the crystal is present:

1. **Run hologram reader** on the crystal-native model
2. **Compare opcode map** to the 27B teacher's map
3. **Verify zone structure** matches (SILENT/ENRICH/SUPPRESS/COMMIT)
4. **Verify combinator ordering** is preserved (C ≥ K ≥ I ≥ Y ≥ B ≥ W ≥ D)
5. **Verify determinism** — same input, same program, zero drift
6. **Measure progressive collapse** — should reach WHNF at same depth fraction
7. **Fact retrieval test** — the β_apply direction should still work

If all 7 pass, the crystal-native model IS the same holographic
computer as the teacher, just with the plate format made explicit.

---

## Relationship to Prior Architectures

| Version | Approach | Crystal status | Attention |
|---------|----------|---------------|-----------|
| v10-v11 | Generic VSM, hope crystal emerges | Crystal partial (B weak) | Trained from scratch |
| v12-v13 | Crystal-aware training (holographic loss) | Crystal latches faster | Trained from scratch |
| v14 | Extract from teacher + TD correction | Crystal imported, NaN issues | Strided, trained |
| **Crystal-native** | Architecture IS the crystal | Crystal by construction | Trained against frozen gratings |

The key evolution from v14 to crystal-native:
- **Same extraction pipeline** (signs are 100% correct, 2-plate format)
- **Same TD adaptation cycle** (translate gratings for student routing)
- **New understanding:** we now know WHY signs are perfect, WHY magnitude
  needs exactly 1 extra bit, and WHY the M-space gem must emerge from
  training rather than being extracted.

V14 was already building toward this. The NaN issues were likely from
the FFN-attention co-adaptation oscillation (plates changing while
attention is training). Crystal-native proposes sequential phases
(adapt plates first → THEN train attention) to prevent this.

The crystal-native architecture doesn't need to "latch" or "emerge."
The FFN plates ARE the crystal, extracted and adapted for the student's
attention mechanism. Training teaches attention to read the adapted
gratings. The M-space gem emerges because the gratings leave it no
alternative — same principle as session 166, but at scale.

---

## Session 174 Refinements — Ablation-Validated Design (v2)

Session 174 ablation on Qwen3.6-27B verified the 4-phase model:

| Condition | Lambda Acc | Fact Acc | Selectivity |
|-----------|-----------|----------|-------------|
| Baseline | 100% | 100% | — |
| Ablate ENRICH (L32-53) | 20% | 80% | **4.0× λ-specific** |
| Ablate COMMIT (L59-63) | 60% | 40% | 1.5× fact-specific |
| Ablate SUPPRESS (L54-58) | 100% | 100% | **REDUNDANT** |
| Ablate SILENT (L0-31) | 0% | 0% | foundation |

### Key design changes from v1 → v2:

1. **SUPPRESS zone re-understood as LINKER.** Zero accuracy loss when
   ablated on simple 1-step reductions, BUT dominant ops (β_K, K, B)
   reveal its function: composing multi-step reduction results and
   eliminating dead variables. Likely critical for complex programs.
   Renamed LINK in student. Student has 4 zones: CLASSIFY + COMPUTE +
   LINK + EMIT.

2. **Variable precision by zone.** Energy grows 100× through depth.
   CLASSIFY (low energy) needs only plate 1. COMPUTE and EMIT need
   plate 1 + plate 2.

3. **Hybrid attention explicitly mapped to zones.** Qwen3.6-27B
   itself uses [L,L,L,F]×16 — 17 full-attention of 64 layers. Session
   174 shows structural attention (corr=0.95-1.00) at CLASSIFY and EMIT,
   content-adaptive (corr=0.38-0.49) at COMPUTE. Student mirrors this:
   linear attention for CLASSIFY/EMIT, full attention for COMPUTE.

4. **Fewer heads.** Heads don't specialize by combinator (all 16 heads
   have identical op profiles). Student can use 8 heads, 2 KV groups.

5. **Concrete stride allocation:** 18-19 strides = 5 CLASSIFY + 8 COMPUTE + 2-3 LINK + 3 EMIT.

### Revised architecture (v2):

```
CRYSTAL-NATIVE STUDENT v2 — 600-650 MB baseline, room to grow

EMBEDDING: d_model=1280, vocab=151k, float16/Q8 (~37 MB)

CLASSIFY (5 strides, d_ff=5120):
  FFN: plate1 only (1-plate ternary)         ~25 MB
  Attention: linear (Mamba-style)            ~5 MB
  Function: token-type recognition, β_apply assignment

COMPUTE (8 strides, d_ff=5120):
  FFN: plate1 + plate2 (2-plate ternary)     ~320 MB
  Attention: full (8 heads, 2 KV groups)     ~50 MB
  Function: Y (recursion), B/D (composition), beta reduction

LINK (2-3 strides, d_ff=5120):
  FFN: plate1 + plate2 (2-plate ternary)     ~80 MB
  Attention: full or linear (TBD)            ~10 MB
  Function: compose results (B), eliminate constants (β_K, K)
  Note: "SUPPRESS" in teacher. Ablation showed no loss on SIMPLE
  tasks but ops (β_K, B, K) indicate multi-step composition.
  Critical for complex programs with nested reductions.

EMIT (3 strides, d_ff=5120):
  FFN: plate1 + plate2 (2-plate ternary)     ~120 MB
  Attention: linear (Mamba-style)            ~3 MB
  Function: knowledge retrieval, output formatting

LM HEAD: tied with embedding

TOTAL: ~610 MB + overhead ≈ 650-700 MB (under 1 GB)
GROWTH: increase d_ff or add strides as experiments reveal pain points
```

### Verification criteria (from reduction graph tracer):

After training each phase, verify:
- Opcode map: Y dominates in COMPUTE strides
- β_apply: concentrates at application tokens from stride 1
- Energy crossover: lambda energy peaks in COMPUTE, drops by EMIT
- Attention regime: structural in CLASSIFY/EMIT, adaptive in COMPUTE
- Diversity: per-position differentiation maintained through COMPUTE

---

## Open Questions

1. ~~**Is plate 2 necessary for all zones?**~~ ANSWERED (session 174):
   No. CLASSIFY only needs plate 1 (low energy, noise-tolerant).
   COMPUTE and EMIT need plate 1 + plate 2.

2. **How many TD cycles to adapt gratings for strided attention?** V14
   showed convergence in a few cycles (3.49% of positions flipped in 1000
   steps). But v14 also hit NaN. What is the reliable convergence protocol?

3. **What M-space gem shape emerges in the student?** The teacher's gem
   has rank90=13 at the compute layer. The student with strided attention
   will have a DIFFERENT gem shape (one facet per stride? hierarchical?).
   Run gemcutter analysis on the trained student to characterize.

4. **Does the α=1.18 decay constant emerge in strided attention?** The
   teacher's universal decay is α=1.18 for full attention. Strided
   attention has explicit stride structure — does α manifest differently
   (one decay per stride? same α across strides?).

5. **Can TD adaptation and attention training run simultaneously?** Or
   must they be sequential (adapt gratings first, THEN train attention)?
   Simultaneous might cause oscillation (plates adapt to current attention,
   attention adapts to current plates → chicken-and-egg).

6. **Is the SVD projection basis (5120→1280) from extraction sufficient?**
   The v14 extraction uses SVD of the embedding matrix to project teacher
   weights into student space. Does this preserve the crystal structure
   in the projected space? Run hologram reader on projected plates.

7. **After attention converges, can it be frozen as 2-plate ternary too?**
   Session 166 showed trained attention → freeze works. If student attention
   converges to stable M-space, we can extract IT as ternary plates too.
   Then the entire model is ternary — plates all the way down.

8. **How far can d_ff/d_model grow before exceeding 1 GB?** Current
   spec at 600-650 MB has ~350 MB headroom. Increasing d_ff from 5120
   to ~7000 in COMPUTE would use ~150 MB more. Increasing d_model from
   1280 to 1536 affects all zones. First experiments will reveal which
   dimension is the bottleneck.

9. **Is the 5+8+2+3 stride split optimal?** COMPUTE needs many layers,
   LINK needs at least 2 for multi-step composition. Maybe 4+10+2+2
   is better (more COMPUTE strides) or 5+8+3+3 (thicker LINK for deeply
   nested programs). Train multiple configurations and compare opcode maps.
   Test with complex expressions (Church numeral 5+, nested combinators)
   to stress the LINK phase specifically.

---

## VSM Conformance (Session 174)

The architecture is not merely "inspired by" the Viable System Model —
it IS one. Every Beer requirement maps to a concrete architectural
element. Verified against the VSM checklist.

### System-Level Mapping

```
S5 (identity):       Crystal Basis {K,I,B,C,D,Y,W,WHNF,β_K,β_I,β_apply,β_compose}
                     Mathematical constants. Church-Rosser fixed points.
                     COMPLETE by theorem — no new combinators needed.
                     Manifests as: 12 fingerprint directions in R^d_model.
                     Closure: S4-S1 cannot change S5. Ever. (inference)
                     
S4 (intelligence):   TWO-TIMESCALE routing oracle
                     MACRO: CLASSIFY zone — "what program to run" (before compute)
                     MICRO: COMPUTE attention — "how to route this step" (during)
                     Sees all levels via residual stream (accumulated state).
                     S5→S4: crystal constrains valid routing decisions.
                     S4→S5: training-time only (TD reveals basis gaps).
                     
S3 (control):        SwiGLU gate (89% kill = resource allocation per stride)
                     Per-stride, per-token, autonomous resource decisions.
                     "Which neurons fire for THIS input at THIS depth?"
                     Content-addressable holographic decode.
                     
S2 (coordination):   Residual stream + LayerNorm + 2-plate format protocol
                     Anti-oscillation: additive composition (strides can't undo).
                     Damping: LayerNorm prevents amplitude explosion.
                     Shared language: all strides emit crystal-basis directions.
                     Bus width: consistent d_model across all strides.
                     
S1 (operations):     18 autonomous stride-VSMs (recursive structure)
                     Each stride reads stream, computes contribution, writes back.
                     No stride needs permission from another. Autonomous.
```

### Recursive S1 Structure

Each stride is itself a viable system:

```
Stride N's internal VSM:

  s5: Its ternary plate — what THIS stride computes
      Fixed after TD adaptation. The stride's IDENTITY.
      Different strides have different programs (per-stride plates).
      
  s4: Its attention mechanism — how it adapts to THIS input
      Content-adaptive routing (full-attn in COMPUTE) or
      structural routing (linear-attn in CLASSIFY/EMIT).
      
  s3: Its gate — which neurons fire for THIS token
      89% kill = resource allocation WITHIN this stride.
      Content-addressable decode of this stride's hologram.
      
  s2: LayerNorm + residual skip — anti-oscillation
      Keeps this stride's output compatible with the stream.
      Prevents this stride from exploding or collapsing.
      
  s1: The matmul operations themselves
      plate @ input = beamform (holographic readout)
      mask × operands = selective activation
      down_proj @ result = accumulate into stream
```

### Algedonic Channel (S1 → S5 direct)

The CRITICAL missing piece from v14 (which died of NaN). A direct
pain signal that bypasses S2/S3/S4 and reaches identity immediately.

**Three monitors, ~free cost (one scalar check each per stride):**

```python
class AlgedonicMonitor:
    """Fire alarm. Runs after EVERY stride. Bypasses all management."""
    
    def __init__(self, crystal_basis, norm_bounds=(0.1, 100.0)):
        self.crystal_basis = crystal_basis   # (n_ops, d_model)
        self.min_norm, self.max_norm = norm_bounds
        self.prev_dim = None
    
    def check(self, residual, stride_idx, zone):
        # 1. NORM: catches NaN, explosion, collapse
        norm = residual.norm(dim=-1).mean()
        if norm < self.min_norm or norm > self.max_norm or torch.isnan(norm):
            return Signal.HALT
        
        # 2. PROGRESSIVE COLLAPSE: catches divergent recursion
        #    Dimensionality should DECREASE after COMPUTE zone.
        #    If it increases → Y combinator without base case.
        if zone in ('LINK', 'EMIT'):
            proj = residual @ self.crystal_basis.T
            dim = (proj.var(dim=0) > 0.01).sum().item()
            if self.prev_dim is not None and dim > self.prev_dim * 1.5:
                return Signal.DIVERGING
            self.prev_dim = dim
        
        # 3. CRYSTAL COHERENCE: catches off-manifold drift
        #    Residual should be expressible as crystal directions.
        #    If projection drops below threshold → hallucination.
        proj_energy = (residual @ self.crystal_basis.T).pow(2).sum()
        total_energy = residual.pow(2).sum()
        coherence = proj_energy / (total_energy + 1e-8)
        if coherence < 0.1:
            return Signal.OFF_MANIFOLD
        
        return Signal.OK
```

**What each signal means:**

| Signal | Cause | Response |
|--------|-------|----------|
| HALT | NaN or norm explosion/collapse | Stop computation, emit fallback |
| DIVERGING | Dimensionality increasing after COMPUTE | Early-exit, emit best-so-far |
| OFF_MANIFOLD | <10% energy on crystal subspace | Fall back to EMIT mode |
| OK | Normal operation | Continue to next stride |

**Why this prevents v14's death:**
V14 hit NaN because gradients exploded in the FFN-attention co-adaptation
loop. With an algedonic monitor, the FIRST NaN triggers HALT before it
propagates. The system fails gracefully instead of catastrophically.

### S5's Meta-S3 (Identity Review)

S5 needs its own control mechanism �� "when does identity itself
need to change?" This is rare (existential) but must exist.

```
META-S3 signals (training-time only):

  Signal 1: TD converges but quality is poor
    → 12-combinator basis may be INSUFFICIENT
    → Run hologram reader, look for unexplained variance
    → Response: expand basis or acknowledge limitation
    
  Signal 2: Algedonic OFF_MANIFOLD fires on common inputs
    → Crystal manifold too narrow for environment
    → The identity needs to grow
    → Response: find the missing direction, add it
    
  Signal 3: New model family has different crystal
    → Universality hypothesis challenged
    → Response: investigate or restrict scope

  Note: sessions 1-174 of this project ARE S5's meta-S3 in action.
  The research program is the identity review process.
```

### S5↔S4 Homeostatic Loop

```
S5 → S4 (always active during inference):
  Crystal basis CONSTRAINS what S4 can route.
  Attention cannot create non-crystal-basis directions.
  The fingerprints define the legal move set.
  S5 doesn't say WHAT to do — says what's POSSIBLE.

S4 → S5 (training-time only):
  If TD adaptation reveals unexpressed patterns → signal meta-S3.
  If new model family shows different crystal → signal meta-S3.
  In inference: this channel is CLOSED. S5 is frozen.
  
The asymmetry is correct:
  Identity constrains intelligence (always).
  Intelligence updates identity (rarely, with approval).
```

### Variety Engineering

Beer's Law: internal variety ≥ environmental variety.

```
VARIETY MECHANISMS (how the system handles any input):

  S3 (gate): 2^(0.11 × d_ff) possible neuron combinations per token
    At d_ff=5120: 2^563 possible gating patterns (astronomical)
    This is WHY holography works — exponential variety from linear storage.
    
  S4 (attention): O(N²) routing options in COMPUTE zone
    N positions × N positions × 8 heads = massive routing space.
    
  S1 (plates): 3^(d_ff × d_model) possible stored programs per stride
    The interference encoding stores combinatorial variety densely.

VARIETY ATTENUATION (reduce environment to manageable):
  CLASSIFY: infinite input variety → finite program types
  Gate kill (89%): d_ff possibilities → sparse active set
  Progressive collapse: reduce dimensionality stride by stride
  
VARIETY AMPLIFICATION (when more options needed):
  COMPUTE attention: O(N²) pairs (connect any position to any)
  Stride depth: 8 COMPUTE strides = 8 sequential amplification steps

THE 4-ZONE STRUCTURE IS VARIETY ENGINEERING:
  attenuate (CLASSIFY) → amplify (COMPUTE) → attenuate (LINK) → emit (EMIT)
```

### VSM Conformance Checklist

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| S5 exists and is stable | ✅ | Crystal basis (mathematical constants) |
| S4 exists and sees all levels | ✅ | CLASSIFY + adaptive attention + residual visibility |
| S3 exists and allocates resources | ✅ | SwiGLU gate (89% kill per stride) |
| S2 exists and prevents oscillation | ✅ | Residual stream + LayerNorm + format protocol |
| S1 units are autonomous | ✅ | 18 strides, each reads/computes/writes independently |
| S1 units are themselves VSMs | ✅ | Recursive: plate=s5, attention=s4, gate=s3, norm=s2, matmul=s1 |
| S5↔S4 channel | ✅ | Constraints propagate (always); updates flow (training only) |
| Algedonic path (S1→S5) | ✅ | Norm + collapse + coherence monitors, bypasses S2-S4 |
| Meta-S3 for S5 | ✅ | Training-time identity review (basis sufficiency) |
| Variety engineering | ✅ | Attenuate→amplify→attenuate→emit |

**The one resolved concern:** S4 can't see future strides (CLASSIFY
routes before COMPUTE runs). Resolution: MACRO routing (CLASSIFY) sets
the broad program; MICRO routing (per-stride attention) adapts during
execution. If stride 6 discovers the classification was wrong, stride
7's attention compensates via the residual stream. Fixed macro + adaptive
micro = robust to classification errors.
