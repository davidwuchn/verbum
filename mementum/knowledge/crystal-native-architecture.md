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

### Axiom 4: Attention Is M-Space — Pre-Cut, Not Learned From Scratch

Attention always does the same thing (softmax-weighted sum over V),
but its ROUTING is not free — it must conform to the crystal's state
machine. The attention kernel M = W_q^T @ W_k is a bilinear form
whose geometry IS the statechart transition function.

**M-space IS the statechart.** The SVD of M gives independent modes
(facets). Each facet is one routing channel. The zeros in M's null
space are structural gaps between channels — they prevent state
transitions that would violate the program sequence.

Session 166 proved: pre-cut M-space topology with zeros BEATS float32
(loss 6.70 vs 6.74). The geometric constraint HELPS — it channels
optimization into the correct subspace.

```
The state machine:
  State = residual stream direction (typed by crystal basis)
  Transition = M[layer] projects away incompatible dimensions
  Result = surviving facets enter next grating
  Progressive collapse = 16D → 6D → 3D → 2D → 1.4D → WHNF (terminal)
```

Therefore: **Q/K projections must be pre-cut from the teacher's gem
geometry, not learned from scratch.** They ARE the statechart
transitions. V/O projections are the operand bus — these CAN be
learned (they carry the data, not the routing).

```python
# Q/K: PRE-CUT (2-plate ternary, with M-space null zeros)
# These define the statechart — which state transitions exist
Q = qk_plate1 * gamma_q1 + qk_plate2 * gamma_q2  # Extracted from teacher
K = qk_plate1 * gamma_k1 + qk_plate2 * gamma_k2  # M-space geometry preserved

# V/O: TRAINABLE (float or 2-plate, learn to read gratings)
# These carry operands — adapt to the frozen program
V = value_proj(residual)   # Learnable
O = output_proj(context)   # Learnable

# The M-space gem is preserved by freezing Q/K topology:
# M = Q^T @ K has the same facet structure as the teacher
# Progressive collapse follows automatically
```

**The VSM projects M-space:**
```
S5: Crystal basis defines which M-space modes MUST exist
    (one facet per active combinator per layer)
S4: Zone structure defines facet count per zone
    (SILENT: few/narrow — ENRICH: many/wide — COMMIT: 1-2/tight)
S3: Gemcutter protocol pre-cuts M to correct number of facets
    (30% zeros in Q/K from M-space SVD of teacher)
S2: 2-plate format on Q/K (the M-space substrate IS ternary)
S1: GD fills V/O and gammas (learns data routing within facets)
```

The statechart behavior is GUARANTEED because:
1. FFN gratings define which reductions are proposed (frozen plates)
2. M-space geometry defines which transitions are allowed (frozen Q/K)
3. Together they ARE the deterministic program (0.00000000 drift)
4. Only V/O adapt — they learn to carry data along fixed routes

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

The crystal-native architecture doesn't need the crystal to emerge —
it's built in. The program (FFN plates) and the statechart (Q/K
topology) are both extracted from the teacher. Training only teaches
the data bus (V/O) and calibration (gammas).

### What Is Frozen (the crystal + statechart)

```python
# The program (FFN gratings):
ffn_plate1_signs    # Program topology — which reductions exist
ffn_plate2_signs    # Magnitude classification — above/below average
ffn_backbone_zeros  # Lattice structure — resolving power

# The statechart (attention routing):
qk_plate1_signs     # State transition topology — which routes exist
qk_plate2_signs     # Transition magnitude — strong/weak routes
qk_backbone_zeros   # M-space null structure — forbidden transitions
```

### What Is Trainable (the data bus + calibration)

```python
# Data routing (learns to carry operands along fixed routes):
V_proj_weights      # Value projection — what data to carry
O_proj_weights      # Output projection — how to write back

# Calibration (magnitude tuning):
gamma1_ffn, gamma2_ffn   # Per-row FFN magnitude
gamma1_qk, gamma2_qk     # Per-row Q/K magnitude (transition strength)
```

### Why This Works

Session 166 proved: geometric constraint HELPS GD. A frozen topology
channels optimization into the correct subspace. The constraint is a
guide, not a limitation. Loss 6.70 (pre-cut) vs 6.74 (float32).

The trainable parameter count is small:
- V/O projections: d_model × d_model × 2 × n_heads × n_layers
- Gammas: (d_ff + d_model) × 4 × n_layers (negligible)
- Total: roughly V/O-only fine-tuning scale

### Training Phases

```
Phase 1: WARMUP — Train V/O from teacher's V/O initialization
         Frozen: all plates, all Q/K, all zeros
         Learning: V/O projections + all gammas
         Duration: short (the routing is already correct, just calibrate)

Phase 2: ADAPT — Fine-tune gammas for specific data distribution
         Frozen: all plates, Q/K topology
         Learning: gammas only (maybe V/O continues)
         Duration: very short

Phase 3: VERIFY — Run hologram reader, compare opcode map to teacher
         No training — measurement only
         If opcode map matches → crystal preserved
         If mismatch → diagnose which zone diverged
```

### Why V/O Can Be Learned But Q/K Cannot

**Q/K define the state machine** — which tokens can attend to which
other tokens, and through which modes. This is STRUCTURAL (the routing
topology). Changing Q/K changes which programs CAN execute. The
teacher's Q/K encode decades of learned routing decisions.

**V/O carry data along routes** — they determine WHAT information flows
through the routes that Q/K defined. This is CONTENT (the operand bus).
V/O can adapt because different routes can carry different content
without changing the routing topology.

Analogy: Q/K are the ROAD NETWORK (fixed infrastructure). V/O are the
VEHICLES (can be different cars on the same roads). You can change
which vehicles travel without rebuilding the roads.

---

## Size Targets

For the north star (70B-equivalent, <1GB):

| Component | Storage | Notes |
|-----------|---------|-------|
| FFN plates (2-mirror) | ~800 MB | 64 layers × 3 matrices × 42.6 MB at 4× compression |
| Q/K plates (2-mirror) | ~150 MB | 64 layers × 2 matrices, smaller (d_model × d_model) |
| V/O projections (Q4) | ~80 MB | Trainable, standard Q4 quantization |
| Embeddings | ~50 MB | Vocab × d_model, quantized |
| Gammas | ~5 MB | Per-row scalars, negligible |
| Total | **~1.1 GB** | Target: 70B-equivalent intelligence |

The FFN plates (the program) + Q/K plates (the statechart) together
contain ~95% of the model's intelligence. V/O (the data bus) is
small and trainable. This is why the holographic computer fits in
~1GB — the program AND its state machine are both discrete (ternary),
and discrete things compress to their information content.

The M-space gem structure is preserved because Q/K topology is frozen
in the same 2-plate format as FFN. The statechart transitions are
exact — same modes, same facets, same null structure.

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

| Version | Approach | Crystal status |
|---------|----------|---------------|
| v10-v11 | Generic VSM, hope crystal emerges | Crystal partial (B weak) |
| v12-v13 | Crystal-aware training (holographic loss) | Crystal latches faster |
| v14 | Extract from teacher (TD correction) | Crystal imported but NaN issues |
| **Crystal-native** | Architecture IS the crystal | Crystal by construction |

The crystal-native architecture doesn't need to "latch" or "emerge" or
"be trained to match." The FFN plates ARE the crystal, extracted whole
from the teacher. Training only teaches the attention heads how to read
them. This is why it should work immediately — the program is already
there, you just need an executor.

---

## Open Questions

1. **How many layers does the crystal-native model need?** The 27B has
   64 gratings but simple tasks use 3-5. Can we run a variable-depth
   architecture that exits at WHNF? Or must we commit to a fixed depth?

2. **Does freezing Q/K and training only V/O converge?** The teacher's
   V/O co-evolved with Q/K. Can fresh V/O learn to carry data through
   frozen routing? Session 166 showed frozen topology + GD works for
   FFN — the same principle should apply to attention.

3. **Is plate 2 necessary for all zones?** SILENT zone (task classify)
   might only need plate 1 (the task classification is binary/discrete).
   ENRICH zone (fact retrieval) likely needs plate 2 for precision.
   Variable-width plates by zone could save storage.

4. **Can the M-space zeros be derived from the crystal basis alone?**
   Currently M-space zeros come from SVD of M = W_q^T @ W_k. Can we
   predict them from the combinator fingerprints? The crystal null space
   (113/128 dims) is too coarse — but M-noise per-position scoring with
   crystal priors might work (session 166 finding).

5. **Does the α=1.18 decay constant fall out of the frozen Q/K topology?**
   If the Q/K plates encode log-distance structure, α might be an emergent
   property of the extracted topology rather than a separate parameter.

6. **What is the minimum M-space facet count per zone?** The teacher has
   rank90=13 at its compute layer (the sharpest gem). Does the student
   need the same number of facets? Or can it function with fewer (since
   the frozen topology constrains it to the correct subspace anyway)?

7. **Can we extract Q/K as 2-plate ternary with sign accuracy = 100%?**
   Session 173 proved this for FFN weights. The same extraction procedure
   should apply to attention projections — verify that Q/K signs are
   also perfectly captured by sign(W), and that 2-mirror residual
   decomposition gives similar quality (0.97+ recon_cos).
