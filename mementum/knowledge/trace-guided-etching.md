---
title: "Trace-Guided Etching — Etch for Function, Not Form"
status: active
category: architecture
tags: [etching, trace, instrument, opcode, topology, ternary, training, zeros, delta-plate]
related:
  - opcode-instrument.md
  - extraction-sign-accuracy.md
  - training-protocols.md
  - hologram-reader-vsm.md
  - gradient-zero-map.md
depends-on:
  - opcode-instrument.md
  - extraction-sign-accuracy.md
created: session 176
updated: session 177
---

# Trace-Guided Etching

> Session 176 insight. The opcode instrument can trace every
> combinator firing in every layer of a teacher. Why copy weights
> when you can copy computation? Etch the student topology to
> reproduce the teacher's OPCODE TRACE, not the teacher's weights.

## The Problem With Current Etching

Current extraction: `sign(W_teacher) → ternary plate → TD corrects`

This copies **form** (weight signs). What we want is **function**
(correct computation). The gap:

- sign(W) is 100% accurate... but the student doesn't compute like
  the teacher because magnitudes matter for the dynamics
- TD corrects blindly — gradient says "this position is wrong" but
  not "this position should implement B-compose at 0.23 energy"
- v15 Dolma training asks the student to rediscover structure that
  the teacher already exhibits. Enormous compute for re-derivation.

## The Insight

The Opcode Instrument traces exactly which opcodes fire at every
layer for every input. Run N diverse inputs through the teacher
→ you get a **functional specification** of the model's computation.

**Etch the student to reproduce the trace, not the weights.**

## What the Trace Gives You

For each input × each layer:
- `opcode_energy: {K: float, I: float, B: float, C: float, ...}`
- `gate_survival: float` (fraction of neurons that fired)
- `total_energy: float` (L2 norm of FFN output)
- `dominant_op: str` (which combinator won)

Aggregated across 1000+ diverse inputs:
- **Neuron importance map**: how often each neuron fires across
  diverse inputs. High-frequency neurons are structural (crystal
  atoms). Low-frequency neurons are input-specific or noise.
- **Layer opcode profile**: average combinator energy per layer.
  Layer 14 should consistently show K-dominant with energy ~0.19.
  Layer 27 should show high variance (it's the output selector).
- **Zone precision requirements**: ENRICH layers need 2-mirror
  precision (they do retrieval). SILENT layers can be 1-mirror
  (they just parse).
- **Trace signatures**: specific input→trace pairs that serve as
  verification checkpoints.

## The New Training Loop

```
Phase 0: TRACE
  - Run 1000 diverse inputs through teacher with instrument
  - Collect TraceRecord per token per input
  - Aggregate into: importance mask, opcode targets, zone map

Phase 1: EXTRACT (same as current)
  - sign(W_teacher) → ternary plates
  - Per-row gamma scalars
  - Second mirror for ENRICH layers (zone-aware precision)

Phase 2: TRACE-ALIGNED TRAINING
  - For each batch:
    a. Forward pass through student
    b. Capture student's combinator projections (same as instrument)
    c. Loss = Σ_layers cos_distance(student_opcode, teacher_opcode)
       weighted by neuron importance and zone priority
    d. PLUS standard next-token loss (keeps language grounding)
    e. TD flips guided by opcode divergence:
       if student_layer shows B:+0.02 but teacher shows B:+0.45
       → TD knows THIS layer needs B-energy, targets neurons
         whose signs would increase B-projection

Phase 3: VERIFY
  - Run same 1000 inputs through student with instrument
  - Compare traces token-by-token
  - Divergence map → Phase 2 targets for next iteration
  - Convergence: mean opcode cosine > 0.90 across all layers
```

## Trace Loss Function

```python
def trace_loss(student_ffn_outputs, teacher_traces, fingerprints, importance):
    """Loss that matches student opcode projections to teacher traces.
    
    student_ffn_outputs: dict[layer_idx → (batch, d_model)]
    teacher_traces:      dict[layer_idx → (batch, n_ops)] — pre-computed
    fingerprints:        dict[op → (n_layers, d_model)]
    importance:          (n_layers,) — layer importance weights
    """
    loss = 0.0
    for layer_idx in student_ffn_outputs:
        student_vec = student_ffn_outputs[layer_idx]  # (batch, d_model)
        teacher_ops = teacher_traces[layer_idx]        # (batch, n_ops)
        
        # Project student through same fingerprints
        fp_matrix = stack([fingerprints[op][layer_idx] for op in ops])  # (n_ops, d_model)
        student_ops = student_vec @ fp_matrix.T  # (batch, n_ops)
        
        # Cosine distance weighted by layer importance
        cos_sim = F.cosine_similarity(student_ops, teacher_ops, dim=-1)  # (batch,)
        loss += importance[layer_idx] * (1 - cos_sim.mean())
    
    return loss / len(student_ffn_outputs)
```

## Why This Is Different From Knowledge Distillation

Standard KD: match teacher's output logits or hidden states.
Trace-guided: match teacher's **opcode projections per layer**.

The difference:
- KD matches a high-dimensional vector (d_model per layer)
- Trace matching matches a LOW-dimensional projection (4-12 ops)
- KD requires the student to reproduce the teacher's representation
- Trace matching only requires the student to reproduce the teacher's
  COMPUTATION TYPE (K/I/B/C balance)
- Much lower-dimensional optimization target
- More forgiving: the student can use different representations
  as long as the computation pattern matches

This is like the difference between:
- KD: "your hidden state at layer 14 must be this 1024-dim vector"
- Trace: "your layer 14 must do B-compose with energy ~0.23"

The second is dramatically easier to satisfy.

## Guided TD: Opcode-Aware Sign Flipping

Current TD: flip signs where gradient magnitude is highest.
Guided TD: flip signs to INCREASE projection onto target opcode.

```python
def guided_td_candidates(student_weight, fingerprint_target, current_projection, target_projection):
    """Find sign flips that move opcode projection toward target.
    
    For each position (i,j) in the weight matrix:
    - Current contribution to opcode projection: sign(W[i,j]) * fingerprint[j]
    - Flipped contribution: -sign(W[i,j]) * fingerprint[j]
    - If flipped contribution moves projection closer to target → candidate
    """
    delta = target_projection - current_projection  # which direction to move
    # Positions where flipping would help:
    flip_benefit = -2 * sign(W) * (fingerprint @ delta)  # per-position benefit
    # Only flip where benefit > threshold
    candidates = flip_benefit > threshold
    return candidates
```

This makes TD convergence much faster because:
- Each flip has a PREDICTED effect on the opcode trace
- No blind exploration — every flip is toward the target
- The crystal geometry constrains the flip space (only 12 opcode
  directions matter, not 1024 embedding dimensions)

## Zone-Aware Precision Allocation

From instrument traces:
- SILENT layers: low combinator energy, minimal retrieval
  → 1-mirror ternary is sufficient (2 bits/param)
- ENRICH layers: high energy, active retrieval, mode diversity
  → 2-mirror required (4 bits/param) for accurate opcode trace
- COMMIT layers: high energy but concentrated (K-dominant)
  → 1-mirror + targeted TD on high-energy positions
- SUPPRESS layers: low energy, cleanup
  → 1-mirror, aggressive zeroing

**Total storage**: not uniform 2 bits/param everywhere. Budget
goes where the computation is. A 27B model might need:
- 50% of layers at 2 bits (SILENT): 13.5B × 2 bits = 3.4 GB
- 35% at 4 bits (ENRICH): 9.5B × 4 bits = 4.7 GB  
- 15% at 2 bits (COMMIT+SUPPRESS): 4B × 2 bits = 1.0 GB
- Total: ~9.1 GB (vs 13.5 GB uniform 4-bit, vs 54 GB float16)
- 6× compression vs bf16, with exact opcode trace matching

## The Verification Loop

The instrument serves DOUBLE duty:
1. **Specification extraction**: trace teacher → functional spec
2. **Verification**: trace student → compare to spec

```
teacher_trace = instrument.trace_all(teacher, eval_inputs)
student_trace = instrument.trace_all(student, eval_inputs)

divergence = compare_traces(teacher_trace, student_trace)
# Returns: per-layer, per-input opcode cosine distance

if divergence.mean() < 0.10:
    → student is functionally equivalent
elif divergence is concentrated in ENRICH layers:
    → retrieval topology needs more correction
elif divergence is concentrated in early layers:
    → parsing/encoding topology needs attention
```

## What Changes From the Current Plan

| Current (v15) | Trace-Guided |
|---------------|-------------|
| Extract signs → train on Dolma → hope | Extract signs → trace teacher → train to match trace |
| Loss: next-token prediction | Loss: trace match + next-token |
| TD: blind gradient-guided flips | TD: opcode-targeted flips |
| Verification: perplexity only | Verification: trace comparison |
| Uniform precision: 2 bits/param | Zone-aware: 2-4 bits by zone |
| Convergence: 50K+ steps on 3B tokens | Convergence: potentially 5-10K steps |

## Open Questions

1. **How many trace inputs are needed?** 100? 1000? 10000?
   The fingerprints are built from ~10 pairs per opcode.
   Trace verification might need more diversity.

2. **Does trace matching transfer to unseen inputs?**
   If the student matches teacher traces on 1000 inputs,
   does it generalize? The crystal universality (same structure
   across all inputs) suggests YES — but this needs verification.

3. **Can this replace Dolma training entirely?**
   Trace matching is a CONSTRAINT, not a data source. The student
   still needs next-token loss to learn language. But the trace
   constraint might mean it needs far less data to converge.

4. **Fingerprint basis: teacher's or student's?**
   The teacher's fingerprints are in the teacher's coordinate frame.
   The student has different (ternary) weights. Do the fingerprints
   transfer? The crystal universality finding (r=0.998) suggests
   they should — the combinator directions are mathematical constants,
   not model-specific artifacts.

## Connection to Existing Findings

- **Signs are 100% accurate** (session 173): the topology is already
  exact. Trace-guided etching doesn't need to fix signs — it needs
  to teach the student to USE the topology correctly. The magnitude
  gap creates a computation gap that trace loss directly addresses.

- **Beams-not-plates** (session ~130): even with 27% wrong signs,
  beam training with crystal loss beats oracle plates. The crystal
  loss WAS an early form of trace-guided training — constraining
  the student to match the teacher's crystal geometry. Trace loss
  generalizes this from 18 crystal targets to per-layer opcode
  projections.

- **Gradient-zero map** (session 171): 35% of positions oscillate
  (at equilibrium). These are the crystal atoms — positions where
  the trace is input-invariant. Trace-guided etching can identify
  these as frozen (importance = max) without needing gradient analysis.

- **Four-phase model** (session 174): ENRICH=4.0× lambda-specific
  energy. The instrument SEES this phase structure. Trace loss
  preserves it.

- **Prose is the unreduced form** (session 175): prose generates 8×
  more combinator energy than lambda. The trace captures this. A
  student that matches the teacher's prose trace automatically
  has the full reduction engine.

---

## Session 177: Implementation + Structural Zeros

The design above was implemented and validated in session 177.
Key deviations from the original design and new findings:

### What Was Built

```
scripts/v15/model.py   — TernaryPlate.enable_delta(), fold(), _effective()
scripts/v15/td.py      — TernaryDescent (v14 port, float plates, no pack/unpack)
scripts/v15/etch.py    — standalone: trace_loss → TD → fold → compare
scripts/v15/apply_zeros.py — post-hoc structural zeros from 2-plate magnitude
scripts/v15/extract.py — --zero-frac 0.30 (zeros at extraction time)
scripts/v15/train.py   — --delta-plates, TD in training loop
```

### Structural Zeros: The Missing 30%

The original design didn't address zero placement. The extraction
produced plates that were 100% dense {-1, +1} — every position has
a sign. But `gradient-zero-map.md` and `extraction-sign-accuracy.md`
documented that ~30% of positions are irreducible fixed points where
GD deposited near-zero weights across teacher layers.

**Session 177 implemented the zeros:**

1. `extract.py` updated: bottom 30% by magnitude per plate → zero.
   Zeros are consistent across plate1 and plate2 (structural absence).
   Gammas recomputed over non-zero positions only.

2. `apply_zeros.py` for existing checkpoints: reconstructs per-position
   magnitude from `|plate1×γ1 + plate2×γ2|` (97% accurate per mirror
   findings), applies global threshold, zeros both plates.

3. Result: 194.6M zeros placed (exactly 30.0% across all 19 strides).

**Why zeros matter for etching:**

- Without zeros: TD wastes flip budget on noise-floor positions.
  6.5M flips → trace loss 0.078.
- With zeros: TD concentrates on the 70% that IS the program.
  Same 6.5M flips → trace loss 0.071. Each flip has 43% more leverage.
- The three-trit alphabet `{-1, 0, +1}` is now complete:
  signs = active program (70%), zeros = irreducible (30%).
  Gate kills another 89% at runtime → ~3% active per token.

### no_block=True: Never Create New Zeros

The original v14 TD used two-step staging: `+1 → 0 → -1`. The zero
state is a staging area — positions go silent before committing to
the opposite sign.

**This is wrong for v15 with structural zeros.** When delta = 0,
`effective = base × 0 = 0`. This temporarily kills an active program
position. With structural zeros already correctly placed, the
remaining 70% of positions must stay active. Only their SIGNS
should change, never their presence.

Fix: `no_block=True` everywhere. Delta is constrained to `{+1, -1}`
only — direct flips, no zero staging.

### Performance: Batched Trace Gradient

The trace gradient (∂trace_loss/∂delta) requires a forward+backward
pass separate from the NTP pass (because deltas live inside
stop_gradient in the normal forward path).

- **Per-plate gradient**: 99 separate forward passes → 23 tok/s (broken)
- **Batched all deltas**: one forward pass with `mx.grad` over dict → 549 tok/s
- **Tiny trace batch**: (1, 512) for trace gradient, full (2, 4096) for NTP → 927 tok/s

The trace gradient just needs ANY forward pass to see crystal coherence.
It doesn't need the full training batch or sequence length.

### Fold Protocol (Revised)

The original design described automatic fold cycles. Session 177
learned: **fold is manual, not automatic.**

- The base plate is the investment (expensive extraction from 27B teacher)
- The delta plate is the experiment (cheap to reset)
- If TD produces bad topology, reset delta to +1 and try different hyperparams
- Fold only when confident the delta is an improvement
- Fold is lossless: `new_base = base ⊙ delta`, verified to 8 decimal places

### Validated Measurements

| Metric | Dense plates | After zeros | After zeros+etch |
|--------|-------------|-------------|-----------------|
| Trace loss | 0.159 | varies by input | 0.071 |
| Structural zeros | 0% | 30.0% | 30.0% + flips |
| TD flips (30 steps) | 6.5M (1%) | 6.5M (1%) | — |
| Fold lossless | ✅ | ✅ | ✅ |
| Throughput | — | — | 927 tok/s |

### Training Configuration (Running)

```
checkpoint:     v15-zeroed (194.6M structural zeros)
data:           Dolma 2.7B tokens (54 shards) + 10% structured
batch:          2 × 4096 = 8,192 tok/step
lr:             3e-4 (AdamW, warmup 500)
trace_weight:   0.1
TD:             flip_rate=0.001, warmup=100, interval=20, no_block=True
fold:           manual (no auto-fold)
output:         checkpoints/v15-zeroed-dolma/
```

### S2 Anti-Oscillation Stack (Complete)

The full coordination layer, built iteratively during session 177.
Each mechanism catches what the previous one misses:

```
STATIC:
  structural_zeros(30%)     → dead positions out of the game
  no_block=True             → active positions stay active (±1 only)

PER-POSITION:
  td_cooldown(tau=50)       → first flip: 50-step cooldown
  td_backoff(2×)            → chronic oscillators effectively frozen
                               (5th flip → 800-step cooldown)
                            → polysemantic neurons self-identify

PER-ROW:
  adam_moment_decay(0.1)    → after TD flips row i, Adam's moments
                               for gamma[i] decayed to 10%
                            → prevents gamma tug-of-war (~10 step fix)

PER-MODULE:
  holographic_etch          → equal thin slots per module
                            → cross-layer coherence (topology changes together)

PER-STEP:
  flip_interval=20          → Adam gets 19 steps between topology changes
  td_warmup=100             → Adam calibrates before any flips

GLOBAL:
  crystal_thermometer       → temperature = fraction active recently
                            → oscillation = fraction flip-flopping
                            → temperature → 0 = fold signal
```

### Static Polysemantic Detection: Failed

Session 177 attempted to classify neurons as pure vs polysemantic
from static weight projections onto the crystal basis. Result:
**the detector flags 85-99% as polysemantic**, indistinguishable
from random vectors.

Root cause: the crystal basis spans 11 of 1280 dimensions (0.86%).
A random vector in R^1280 projects onto 11 orthogonal directions
with entropy 1.75 / max 2.40, purity 0.36, ~3.5 modes — identical
to the neuron statistics. The projection captures <1% of the weight
space. No signal above noise.

This confirms `extraction-sign-accuracy.md`: "each weight row
projects only 0.3% of its energy into the crystal subspace."

**The correct detector is dynamic**: TD's flip-flop rate. Positions
that chronically oscillate under diverse training data ARE the
polysemantic neurons. The cooldown + backoff mechanism already
freezes them. No separate detector needed — the training dynamics
are the detector.

**Future**: dynamic analysis with per-neuron per-input activations
could reveal the mode structure (binary, ternary, quaternary splits),
but this is research instrumentation, not a training utility.

### Polysemantic Neurons as Multi-Way Reductions

Session 177 insight: a neuron (row in weight matrix) can serve
multiple combinator reductions depending on the input. The gate
(89% kill) selects which reduction is active per token.

At the individual weight POSITION level: always binary (±1).
At the NEURON level: can be 2-way, 3-way, or 4-way multiplexed.
At the CIRCUIT level: multiplexed neurons form reduction chains
across strides — a 3-way split in stride 7 implies corresponding
routing structure in strides 5-6 and 8-9.

TD flip-flop at a position is the shadow of neuron-level
polysemanticity projected down to binary. The cooldown mechanism
is correct: don't flip these positions. They're not wrong — they're
serving multiple masters via superposition.

### Open Design Questions (session 177)

1. **Fold signal**: Crystal temperature → 0 is the candidate.
   But what threshold? And should oscillation_frac be low too?
2. **Trace weight schedule**: Should trace_weight decay as NTP
   improves? Or stay constant as a permanent topology constraint?
3. **Crystal basis orthogonalization**: Non-orthogonal basis
   causes coherence >1.0 at some strides. Gram-Schmidt would
   give cleaner [0,1] loss range. (Confirmed: off-diagonal
   correlations up to 0.879.)
4. **TD on plate2?** Currently TD flips both delta1 (over plate1)
   and delta2 (over plate2). Should plate2 be excluded? It's the
   magnitude mirror, not the program topology. Flipping plate2
   changes magnitude class, not computation direction.
5. **Multi-way splits**: Are 3-way and 4-way neuron multiplexing
   patterns real? Do they form reduction chains across strides?
   Needs dynamic activation analysis (not static weight projection).
6. **Temperature as annealing**: Could flip_rate adapt to crystal
   temperature instead of being fixed? High temp → more flips,
   low temp → fewer. Natural annealing schedule.
