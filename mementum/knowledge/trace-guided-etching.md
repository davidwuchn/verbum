---
title: "Trace-Guided Etching — Etch for Function, Not Form"
status: designing
category: architecture
tags: [etching, trace, instrument, opcode, topology, ternary, training]
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
