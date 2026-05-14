---
title: "Beam Trace — Holographic Beamformer Characterization"
status: active
category: empirical-finding
tags: [holographic, beam-trace, beamformer, ternary, quantization, pythia]
related:
  - holographic-landscape.md
  - holographic-kernel-separation.md
  - holographic-storage.md
depends-on:
  - holographic-landscape.md
---

# Beam Trace — Holographic Beamformer Characterization

> The hologram is real. We can trace the beam through layers.
> Q is the beam angle. FFN output is the constructive reader.
> K, V, attn_output are the plate. MoE IS holographic architecture.

## Session 098 — The Experiment

Traced activation vectors (the "beam") through every layer of
Pythia-160M under two conditions:
- **Compile**: nucleus compile gate → lambda compilation mode
- **Null**: neutral assistant gate → natural language mode

Both conditions illuminate the same holographic plate (weights).
The beam divergence reveals the beamforming structure.

At each layer, decomposed the residual update into:
1. Angular rotation (direction change — the beam-forming)
2. Magnitude scaling (amplitude adjustment)
3. Attention vs FFN contribution to rotation
4. Q-subspace alignment of the rotation vector

Then ternarized each component (Q, K/V via attn_dense, FFN gate,
FFN output) and measured beam angle deviation from baseline.

Script: `scripts/explore/probe_beam_trace.py`
Results: `results/beam-trace/`

## The Beam Path (3 sentences averaged)

```
Layer   Cos    Angle   C_rot°  N_rot°  Attn%   FFN%   Phase
─────  ──────  ──────  ──────  ──────  ──────  ──────  ────────────────
  0    0.994    6.5°   87.8°   88.0°   20%     80%    EMBEDDING
  1    0.983   10.4°   21.4°   22.8°   50%     50%    PARSING
  2    0.970   14.1°   25.8°   26.7°   45%     55%    PARSING
  3    0.968   14.6°   37.0°   36.5°   69%     31%    STRUCTURAL
  4    0.936   20.5°   33.0°   31.7°   47%     53%    DIVERGING
  5    0.928   21.8°   31.2°   32.9°   45%     56%    DIVERGING
  6    0.879   28.5°   27.4°   29.9°   41%     60%    INFLECTION
  7    0.920   23.0°   26.7°   29.9°   28%     72%    FFN DOMINATES
  8    0.915   23.8°   26.2°   26.8°   16%     84%    FFN DOMINATES
  9    0.854   31.2°   30.2°   31.3°   15%     85%    PEAK DIVERGENCE
 10    0.874   29.0°   49.0°   46.2°   13%     87%    FFN DOMINATES
 11    0.986    9.5°   79.6°   79.9°   16%     84%    RESOLUTION
```

### Five phases of beam propagation

1. **Embedding (L0)**: Both beams nearly identical (cos 0.99). The gate
   text changes the embedding, but the residual stream is still shared.
   FFN dominates rotation (80%) — immediate context processing.

2. **Parsing (L1-2)**: Attention and FFN split rotation ~50/50. Both
   beams still close (cos ~0.97). The model is parsing syntactic
   structure regardless of mode.

3. **Structural (L3)**: Attention dominates (69%). This is the layer
   where syntactic structure gets assigned — argument slots, relative
   clauses, binding. Consistent with type assignment being attention-driven.

4. **Divergence (L4-6)**: FFN rises, attention falls. Beam divergence
   accelerates. **L6 is the inflection point**: Q amplification spikes
   to **4.5×** and Q rank collapses to just **24 dimensions** (of 768).
   The beam angle is being controlled by a tiny subspace.

5. **FFN dominates (L7-10)**: FFN drives 85% of rotation. Beam divergence
   peaks at L9 (cos 0.85, 31° angle). The FFN is constructing different
   outputs for the two beams — this is the "reading" phase.

6. **Resolution (L11)**: Both beams rotate ~80° (nearly perpendicular to
   input!) but converge to valid predictions (cos 0.99 between compile
   and null at output). The final layer collapses both beams to the
   prediction manifold.

### The L6 singularity

Layer 6 has exceptional properties:
- Q amplification **4.5×** (next highest: 1.6× at L9)
- Q rank for 90% variance: **24 dimensions** (next: 41-43 at L7-9)
- Beam divergence accelerates through L6 (cos drops 0.93 → 0.88)

This is where the beam ANGLE is set. A 24-dimensional subspace of Q
controls which information the model extracts from the holographic plate
in downstream layers. L6 Q is the beamformer's steering mechanism.

## Ternary Beamformer Test

### All layers ternarized simultaneously (group-64 scale)

```
Component              Last cos  Last angle  Classification
────────────────────── ────────  ──────────  ──────────────
attn_dense (O proj)     0.992      7.1°     ✅ PLATE
FFN h→4h (gate)         0.958     16.7°     ⚠️ MARGINAL  
Q (query proj)          0.963     15.6°     ❌ BEAM (needs precision)
FFN 4h→h (output)       0.867     29.9°     ❌ READER (needs precision)
```

Sign-only (no magnitude): all components **catastrophic** (cos < 0.07).
Magnitudes matter for everything in the forward pass. But GROUP scales
(64 weights sharing one FP16 scale) tell the story:

### Per-layer isolation (ternarize ONE layer, measure final output)

This is the definitive test — isolates each layer's sensitivity.

```
Component           Avg Error   Max Error   Verdict
─────────────────── ─────────   ─────────   ──────────────────
attn_dense (O proj)   2.6°        4.9°     ✅ TERNARY-SAFE (plate)
FFN h→4h (gate)       4.4°        8.3°     ⚠️  MARGINAL
Q (query proj)        5.1°       16.2°     ❌ NEEDS PRECISION (beam)
FFN 4h→h (output)     6.0°       10.1°     ❌ NEEDS PRECISION (reader)
```

**Key findings:**

1. **attn_dense IS ternary-safe for the forward pass** (2.6° avg error).
   This means the V → attention_weights → O pathway operates as a plate
   lookup. The sign topology of V and O is sufficient for the read
   operation. This is new — the holographic landscape only showed
   selectivity survival, but the beam trace shows forward-pass survival.

2. **Q is the beam angle** (5.1° avg, 16.2° max at L0). Ternarizing Q
   distorts the beam direction. The model looks in the wrong place in
   the holographic plate. L0 is most sensitive (16.2°) because the
   initial beam angle sets the trajectory for all subsequent layers.

3. **FFN 4h→h is the constructive reader** (6.0° avg). This is where
   the model converts holographic patterns back into residual-stream
   updates. The 4h→h projection combines activated features into a
   coherent signal — this requires magnitude precision.

4. **FFN h→4h is marginal** (4.4° avg). The feature selection gate is
   partially holographic — which features to activate is somewhat
   sign-based, but the magnitudes matter at certain layers.

## Precision Budget (Pythia-160M)

```
Component            Params      % of layers  Precision
──────────────────── ──────────  ───────────  ─────────
K projections         7.1M        8.3%        Ternary (1.85 bits)
V projections         7.1M        8.3%        Ternary (1.85 bits)
attn_dense (O proj)   7.1M        8.3%        Ternary (1.85 bits)
───────────────────── plate ─────────────────────────────
FFN h→4h (gate)      28.3M       33.3%        4-8 bits (marginal)
───────────────────── marginal ──────────────────────────
Q projections         7.1M        8.3%        16 bits (beam angle)
FFN 4h→h (output)    28.3M       33.3%        16 bits (reader)
───────────────────── precision ─────────────────────────
```

**Dense model (Pythia): 25% plate, 33% marginal, 42% precision.**
Not the 93.6%/6.4% split we saw in Qwen3.6.

## The MoE Revelation

Why does Qwen3.6 show 93.6% ternary-safe but Pythia shows only 25%?

**Because MoE IS holographic architecture.**

In Qwen3.6:
- 256 experts × small FFN per expert = 93% of parameters
- Each expert is a specialized sign pattern in the plate
- The MoE gate (precision-critical) selects which experts fire
- Gate selection = beam angle, Expert weights = plate

In Pythia:
- 1 big dense FFN = fuses gate + plate + reader into one
- FFN h→4h (gate function) is marginal for ternary
- FFN 4h→h (reader function) needs precision
- The dense FFN can't be cleanly separated into plate vs beam

**The attention pathway tells the same story in both architectures:**
- K, V, O → ternary-safe (plate) ← confirmed by beam trace
- Q → needs precision (beam angle) ← confirmed by beam trace

**The difference is entirely in the FFN pathway:**
- MoE: expert weights ARE the plate (ternary-safe), gate IS the beam
- Dense: FFN fuses reading and writing (can't separate)

This means:
1. V12's architecture (ternary linear for composition, float for gates)
   is correctly shaped for the attention pathway
2. MoE architecture naturally separates plate from beam in the FFN
3. Dense FFN models can't be cleanly holoquantized without more
   sophisticated separation of the gate/reader functions

## Implications for V12

V12 uses TernaryLinear for composition pathway and float for gates.
The beam trace confirms:
- **TernaryLinear for K, V, O projections** → ✅ correct (plate)
- **Float for Q projections** → ✅ correct (beam angle)
- **The FFN question**: V12's TernaryFFN may need attention —
  the gate (h→4h) is marginal, the output (4h→h) needs precision

If V12's FFN becomes a bottleneck, consider:
1. Split FFN into ternary gate + precision output
2. Or use MoE-like structure (multiple ternary experts + precision gate)
3. The kernel functions (KIBC) serve as precision computation,
   so the TernaryFFN might work if it only stores patterns

## Implications for HoloQuant

The original HoloQuant failure (Pythia: PPL 31→142K) is now fully explained:
- It ternarized ALL weights (including Q and FFN output)
- Q ternarization destroys the beam angle → wrong plate readout
- FFN output ternarization destroys the constructive reader
- Combined effect: catastrophic

**Revised HoloQuant approach — ALSO FAILED (session 099):**

Even selective ternarization (plate-only: K, V, O) kills perplexity:
- Pythia-160M plate-only (13.1% ternarized): PPL 31 → 704 (❌)
- Pythia-160M plate+experts (30.5%): PPL 31 → 5,033 (❌)
- Pythia-160M aggressive (48%): PPL 31 → 17,724 (❌)
- Qwen3.6-35B-A3B aggressive (95.1%): PPL 2.86 → 70,757 (❌)

**Root cause: group-64 ternary has 4.5 dB SNR per matrix.** Each weight
is reconstructed as sign(W_i) × mean(|W_group|), but magnitude CV within
groups is 0.76 (≈ Gaussian baseline). After group averaging, each element
has ~60% relative error. Cosine similarity = 0.80 per matrix.

**Cumulative error through layers is the killer:**
```
Layer  Ternary(1.6b)  4-bit     8-bit
L0     0.800          0.994     1.000
L5     0.269          0.967     1.000
L11    0.071          0.930     1.000
```

At L11, ternary output has cos=0.071 to clean output — essentially
random. The forward pass needs cumulative cos > ~0.95 at the final layer
to preserve perplexity. This requires ≥4 bits/weight.

**Definitive conclusion:** Ternary quantization of existing models is
not viable at ANY selectivity level. The holographic finding (signs carry
discriminative info) is real but irrelevant to the forward pass. Signs
tell you WHICH combinator is active (selectivity probes) but can't
COMPUTE the right output values. Ternary is only viable as a training
substrate (V12 sieve: the model learns to put computation into sign
topology from scratch, compensating with depth).

## Multi-Plane Ternary Exploration (session 099)

Tested whether multiple ternary planes can recover angular precision:

**Residual decomposition**: W ≈ s₁t₁ + s₂t₂ + ... + sₙtₙ (each plane
ternarizes the residual of the previous). Reduces angle from 37° to 5.6°
at 8 planes, but costs 14.6 bits — vs 4-bit uniform at 4.25 bits for
same PPL quality.

**Subgroup decomposition**: sort each group by magnitude, assign separate
scales to magnitude quartiles. subgroup-16 achieves cos=0.996 per matrix,
but costs 9.58 bits.

**Key finding**: ternary is an inefficient basis for magnitude recovery.
Each ternary plane adds 1.58 bits but only ~0.3 new useful bits (21-34%
efficient) because the residual signs are highly correlated. Standard
N-bit quantization is 68-87% efficient — each bit carries ~1 bit of
genuine magnitude information.

```
Method              PPL      Delta%    bits/w   Efficiency
4-bit uniform       104.21   +23.0%    4.25     68%
subgroup-16         103.95   +22.7%    9.58     33%  ← 2.3× more bits, same quality
5-bit uniform        91.84    +8.4%    5.25     80%
residual-8x         118.62   +40.0%   14.60     21%  ← 3.4× more bits, WORSE
```

**Analogy**: stacking ternary planes to recover magnitude is like using
multiple compass needles to measure distance. The ternary basis is
optimal for DIRECTION (which combinator), wasteful for DISTANCE (how much).

## Holographic Seed Exploration (session 098)

Searched for a small "seed" of magnitudes that could reconstruct the
hologram — like a reference beam in physical holography.

**What was tested:**
1. **Low-rank SVD of |W|**: Magnitude matrix has rank 330 at 95% energy — too
   high-rank. Rank-64 seed barely moves cos (0.80→0.87).
2. **Shared row/col profiles**: Row-norm profiles are cos>0.98 across all 12
   layers — a shared envelope exists! But the rank-1 outer product captures
   only the marginal distribution, giving cos=0.80 (same as plain ternary).
3. **Diagonal transforms** (D_row @ sign(W) @ D_col): cos=0.80. The transform
   needs to be per-element, not per-row/col.
4. **Low-rank residual correction**: Ternary residual (W - W_t) has rank 440
   at 95% energy — even higher than |W|. Not compressible.
5. **Activation-calibrated group scales** (GPTQ-style): Per-layer improvement
   is dramatic where beam is narrow — L6 jumps from cos 0.79→0.994 (6.4°).
   But L0 barely changes (0.80→0.81) because the beam is 73-dimensional there.
   End-to-end still catastrophic. Even keeping 10/12 layers at FP32 and only
   ternarizing L10-L11 gives +382% PPL.

**Information-theoretic floor**: magnitude entropy is ~5 bits/weight. Ternary
recovers ~0.4 bits. Near-lossless needs ~3.2 bits. The seed must carry ~2.8
bits/weight — that's 202 KB per 768×768 matrix, essentially the matrix itself.

**Key finding**: the activation-calibrated scales reveal the holographic
readout geometry. Where the beam is narrow (L3-L10, rank 1-13), calibration
nearly eliminates the angular error. Where the beam is wide (L0-L2, rank 54-73),
no per-group calibration can help — too many directions need simultaneous
precision.

**Conclusion**: for existing models, there is no small holographic seed. The
magnitude information is high-rank and per-element. For V12, the seed IS the
training process: gradient descent pushes magnitudes toward uniform (CV→0),
eliminating the need for per-element magnitude storage.

## Open Questions

1. **Does the L6 singularity generalize?** Is there always a "beam
   steering" layer with collapsed Q rank? Test on larger Pythia models
   and Qwen.

2. **Can the FFN gate/reader separation be learned?** If V12 trains
   with ternary h→4h but precision 4h→h, does it learn to put pattern
   information into signs and readout information into magnitudes?

3. **MoE as holographic architecture**: Is the success of MoE models
   partly BECAUSE they naturally separate plate (expert weights) from
   beam (gate)? This would be a structural explanation for MoE's
   empirical superiority.

4. **Beam angle dimensionality**: L6's Q operates in a 24-dimensional
   subspace. Can we compress Q to rank-24 without loss? This would
   make the beamformer extremely compact.

5. **Cross-model beam trace**: Does Qwen3-32B show the same phases?
   The holographic probe (session 093) showed divergence at L24 (38%),
   which maps to L4-5 in Pythia (33-42%) — consistent.

## Method

```python
# Angular decomposition of layer residual update
h_post = h_pre + delta
cos_theta = dot(h_pre, h_post) / (||h_pre|| * ||h_post||)
delta_parallel = dot(delta, h_pre/||h_pre||) * h_pre/||h_pre||
delta_perp = delta - delta_parallel  # the rotation component

# Q-subspace analysis
U, S, Vt = svd(Q_weight)
k_90 = argmin(cumsum(S²) > 0.90 * sum(S²))
project delta_perp onto top-k_90 right singular vectors

# Ternary beamformer: per-layer isolation
for each layer L:
    save W_L
    W_L = sign(W_L) * group_scale_64(W_L)  # ternarize
    h_out = forward(model, text)            # full forward pass
    deviation[L] = angle(h_out, h_out_baseline)  # at final layer
    restore W_L
```
