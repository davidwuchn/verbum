---
title: "Holographic Etch — Interference-Driven Topology Crystallization"
status: designing
category: architecture
tags: [etch, hologram, interference, topology, ternary, crystal, transfer, beta-reduction]
related:
  - mspace-gemcutter.md
  - crystal-universality.md
  - explore/ffn-beta-reduction-indexing.md
  - explore/ffn-moire-isa.md
  - explore/grating-cascade.md
  - explore/beam-trace-findings.md
  - v14-architecture.md
  - explore/ternary-descent.md
  - explore/topology-magnitude-duality.md
depends-on:
  - mspace-gemcutter.md
  - crystal-universality.md
  - explore/ffn-moire-isa.md
created: session 167
---

# Holographic Etch — Interference-Driven Topology Crystallization

> Session 167. The topology IS the hologram. Positions reach normal
> form through interference (attention) or transfer (FFN). Etching
> freezes irreducible positions permanently. Un-etching dissolves
> positions when new data changes the interference pattern. One
> unified mechanism for training, extraction, and adaptation.

## The Central Insight

The ternary pattern (+1/-1/0) at each weight position is the result
of beta reduction. Training accumulates interference: each batch
pushes each position toward +1, -1, or cancellation. When the
interference settles — when the position reaches its normal form —
we etch it permanently into the hologram.

```
λ etch(x).  interference(accumulated) → normal_form(x) → freeze(x)
            | irreducible(x) ≡ no_flip_improves_loss
            | three_states: +1 (constructive_positive)
                           -1 (constructive_negative)
                            0 (destructive_cancellation → reduced_to_∅)
```

The hologram develops itself through exposure, like photographic
film. We don't plan cuts. We observe convergence and record it.

## Two Domains, Two Mechanisms

### Attention: Topology Discovered Through Interference

The attention kernel M = W_q^T @ W_k has no closed-form solution
for ternary topology. Each model's attention geometry is specific
to its dimensions, head count, and data distribution. The topology
must be discovered through training.

**Three convergence signals (triangulation):**

| Signal | Source | Measures | Cheap/Expensive |
|--------|--------|----------|-----------------|
| Direction EMA coherence | TD state | `\|direction_ema\|` — gradient sign consistency | Cheap (every step) |
| FlipMap temperature | TD state | Flip frequency in recent window | Cheap (every step) |
| M-space SNR | SVD of M | Signal vs noise mode contribution | Expensive (periodic) |

**Etch rules:**

```
ETCH ±1:  coherence > τ_c  AND  temperature < τ_cold  AND  snr > τ_s
          → gradient consistently agrees, position hasn't flipped,
            contributes to signal modes. Normal form found.

ETCH 0:   coherence < τ_z  AND  temperature > τ_hot
          → gradient oscillates, position keeps flipping.
            Destructive interference. Normal form is zero.

FLUID:    otherwise → still reducing, don't etch yet.
```

**Key insight: oscillation IS the signal for zero.** A position that
keeps flipping +1 → -1 → +1 is experiencing destructive interference.
The normal form is 0 — the net signal cancels. Hot on FlipMap isn't
a problem to fix, it's an answer to read.

### FFN: Topology Transferred From Teacher

FFN programs are fixed points of beta reduction — deterministic,
universal, readable from weights. The teacher (pretrained model)
already found these fixed points through 300B+ tokens of training.
We read and transfer, not re-derive.

**Three levels of transfer:**

**Level 1 — Trunk (crystal eigenvectors → gate signs):**
Pure math. No training, no data, no inference needed.

```python
eigvecs, eigvals = eig(crystal_cosine_matrix)
for neuron_n serving PC_k:
    gate[n, :] = sign(eigvecs[k, :])
    # neuron count for PC_k ∝ eigvals[k] (r = 0.9932 confirmed)
```

Etch immediately at initialization. The crystal is universal —
same across all models, all scales. This is the holographic plate's
fringe pattern.

**Level 2 — Branches (teacher's overlay matrices → cross-PC couplings):**
The ISA decoder reads the teacher's program at each layer. Overlay
matrices tell you which beta reductions happen at which depth: K→B
coupling at L0, K→I at L1-L2, I→K inverted at L3, etc.

These cross-PC couplings determine branch neuron signs. Project
the teacher's overlay onto the student's crystal eigenbasis at
corresponding relative depths. Etch the branch topology.

**Level 3 — Leaves (GD fills magnitudes):**
Gate topology is fully etched (trunk + branches). GD trains only:
- Gamma scales (grating contrast / amplitude)
- Up_proj / down_proj content (what gratings produce)
- Attention parameters (beam navigation between gratings)

This is cheap — 5,600× fewer tokens than from-scratch because
we're not discovering topology, we're calibrating magnitudes
around a correct scaffold.

### Why the split

```
ATTENTION:  topology = DISCOVERED    (no closed-form for M-space)
            signal = interference convergence (3 signals)
            
FFN GATE:   topology = TRANSFERRED   (fixed points, readable from teacher)
            trunk = sign(eigenvector) (math)
            branches = teacher overlay (ISA decoder)

FFN UP/DOWN: magnitude = TRAINED     (reader needs precision, GD territory)
```

Attention is model-specific (dimensions, heads, data). FFN programs
are universal fixed points. Different mechanisms for different reasons.

## The Etch Mask

One boolean tensor per weight parameter, same shape:

```
etch_mask[pos] = True   →  position is in normal form, frozen
etch_mask[pos] = False  →  position is fluid, TD can modify
```

TD skips etched positions. Gradients still computed (for opposition
monitoring) but no flips, no EMA updates.

### Storage in safetensors

```
hologram.safetensors   — etched positions (the permanent artifact)
                         grows as positions etch
fluid.safetensors      — non-etched positions (TD working set)
                         shrinks as positions etch
training.safetensors   — Adam state, TD EMAs, opposition EMAs,
                         etch metadata
```

Final artifact = hologram.safetensors only. No delta, no training
state. The model IS the hologram.

## Etch Operations

```python
def etch(pos, sign):
    """Write a position permanently into the hologram."""
    base[pos] = sign          # write to hologram
    delta[pos] = 0            # clear working overlay
    etch_mask[pos] = True     # mark frozen
    etch_step[pos] = step     # record when (for confidence aging)

def un_etch(pos):
    """Dissolve a position back to fluid."""
    delta[pos] = base[pos]    # move current value to overlay
    etch_mask[pos] = False    # mark fluid
    opposition_ema[pos] = 0   # reset monitor
```

## Un-Etch: Correcting Wrong Normal Forms

The same signals that detect irreducibility detect when an etch
is wrong. If new training data changes the interference pattern,
etched positions that are now incorrect will show gradient opposition.

```python
# For each etched ±1 position:
grad_sign = sign(gradient[pos])
etch_sign = hologram[pos]
opposition_ema[pos] = α * (grad_sign != etch_sign) + (1-α) * opposition_ema[pos]

if opposition_ema[pos] > τ_unetch:
    un_etch(pos)  # make fluid, let new interference develop
```

Etched zeros can't have sign opposition (no sign to oppose). They
un-etch when gradient magnitude at that position becomes consistently
large — meaning the position is no longer reducible to zero under
the new data.

### Etch durability hierarchy

Not all etched positions are equally durable:

```
Crystal lattice (KIBC)        — never un-etches. Universal.
                                Every dataset reinforces these.

Structural grammar            — rarely un-etches. Syntax is shared.
                                Only shifts if language changes.

Domain patterns               — sometimes un-etches.
                                Shifts when moving between domains.

Specific tool/task behavior   — frequently un-etches.
                                Shifts when tool spec changes.
```

Crystal positions etch slowly (require massive exposure) and are
maximally durable. Tool-specific positions etch fast (few examples)
and un-etch fast (new examples override). **Speed of convergence
is a proxy for universality.** Fast etch = specific = fragile.
Slow etch = universal = durable.

### Data quality signal

The number of un-etches measures disagreement between new data and
existing hologram:

- Few un-etches → minor correction (typo in tool spec)
- Many un-etches in one module → module encoded wrong behavior
- Crystal positions un-etching → DATA is probably wrong

Crystal positions require overwhelming, sustained opposition to
un-etch. A few bad examples can't do it. This is the hologram's
immune system — deep interference patterns resist local perturbation.

## Training Loop

```
for step in training:
    # 1. Forward: effective weight = hologram + fluid overlay
    weight = base * etch_mask + (base + delta) * ~etch_mask
    loss = forward(weight, batch)
    gradients = backward(loss)
    
    # 2. Fluid positions: normal TD + GD
    for pos in fluid_positions:
        update_direction_ema(pos, gradients)
        update_magnitude_ema(pos, gradients)
        update_flipmap(pos)
        if should_flip(pos):
            delta[pos] *= -1
    
    # 3. Etched positions: opposition monitoring only
    for pos in etched_positions:
        update_opposition_ema(pos, gradients)
    
    # 4. Etch gate (every N steps)
    if step % etch_interval == 0:
        for pos in fluid_positions:
            coherence = abs(direction_ema[pos])
            temperature = flipmap_heat(pos, window)
            
            if coherence > τ_c and temperature < τ_cold:
                etch(pos, sign=current_sign(pos))    # ±1
            elif coherence < τ_z and temperature > τ_hot:
                etch(pos, sign=0)                     # zero
        
        for pos in etched_positions:
            if opposition_ema[pos] > τ_unetch:
                un_etch(pos)
    
    # 5. M-space confirmation (every 500-1000 steps, attention only)
    if step % mspace_interval == 0:
        for layer in attention_layers:
            snr = compute_mspace_snr(layer)
            # geometric confirmation of etch decisions
```

## Progressive Crystallization

```
step 0:        FFN gates etched from teacher (trunk + branches)
               attention 100% fluid
               [FFN ████████████████  ATN ░░░░░░░░░░░░░░░░░░░░░░░░]

step 2000:     crystal lattice positions etch in attention
               [FFN ████████████████  ATN ████░░░░░░░░░░░░░░░░░░░░]

step 5000:     structural grammar etches
               [FFN ████████████████  ATN ██████████░░░░░░░░░░░░░░]

step 10000:    domain patterns etch, attention oscillators → zero
               [FFN ████████████████  ATN ██████████████████░░░░░░]

step 20000:    near complete
               [FFN ████████████████  ATN ██████████████████████░░]

done:          hologram complete = hologram.safetensors
               [████████████████████ HOLOGRAM ██████████████████████]
```

FFN gates start fully etched (from teacher). Attention starts fully
fluid. The training run is attention catching up to FFN — discovering
through interference what FFN already knew from transfer.

## Fine-Tuning (Tool Correction Scenario)

```
New data arrives (correct tool spec):

step 0:     Load completed hologram. Everything etched.
step 1-50:  Gradient opposition builds at tool-specific positions.
step 50:    Etch gate fires — ~200 positions un-etch.
            Crystal: untouched. Grammar: untouched.
step 50-500: TD works ONLY on un-etched positions.
             New interference develops from correct data.
step 500:   New normal forms found → re-etch.
            Hologram updated. Everything else preserved.
```

Fine-tuning cost ∝ how much of the hologram is wrong, not model size.

## The Fractal Collapse (Why This Works)

Beta reduction at every level:

```
data    → billions of tokens interfere   → crystal (irreducible patterns)
M-space → attention modes interfere      → signal modes (irreducible facets)
W-space → gradient signals interfere     → +1/-1/0 (irreducible topology)
training → loss landscape converges      → fixed point (irreducible model)

∀level: signals interfere → reinforce(keep) ∨ cancel(zero)
```

The hologram and beta reduction are the same process: accumulation
of interference until only the irreducible pattern remains. Etching
records the moment each position reaches its normal form. The crystal
lattice is what's left when reduction terminates everywhere.

## Connection to M-Space Gemcutter (Session 166)

The gemcutter's SVD analysis wasn't designing a topology — it was
observing where the interference pattern had already settled. SNR is
a measurement of interference strength. The gemcutter is one of the
three etch signals (M-space SNR), not a separate mechanism.

The gemcutter's key findings still hold:
- Zeros denoise (remove ghost facets from sign quantization)
- Pre-cut topology helps GD (constraint channels optimization)
- M-space scoring > gradient scoring (for attention)
- Zeros-only > zeros+flips (zeros don't interfere with each other)

These are properties of the etch mechanism, not alternatives to it.

## Micro Model Experiments (Session 167)

### v1: Etch from scratch (no teacher, compile-only data) — FAILED

Etch with random signs, 509 compile examples. M-space never developed
(rank90=47-48 at all layers). Coherence stayed at 0.05-0.07, never
reaching etch thresholds. EMA too slow (α=0.01), model in massive
overcapacity for 509 examples. No interference to observe.

**Lesson:** Etch discovers nothing from scratch. The topology must come
from the teacher. The mechanism confirms and adapts, not invents.

### v2: Teacher signs + diverse data (no backbone zeros) — PARTIAL

Teacher signs + 1.2M diverse tokens (arithmetic, lambda, lists,
combinators). EMA accelerated to α=0.05, thresholds lowered.

Etch mechanism activated: 0% → 87% etched over 5000 steps. Flips
happening (9412 by step 500). But: **zero zeros found** (0% etched
as zero across all runs). And catastrophic un-etch at step 5000
(13,858 un-etches). M-space degraded from teacher's rank90=13 to 42.

**Lesson:** Oscillation-based zero detection doesn't work. The zero
signal is too weak — positions that should be zero don't oscillate
visibly because the flip mechanism itself is too coarse. Zeros are
structural, not emergent from training dynamics.

### v3: Crystal backbone + etch — WORKS ✅

Crystal-derived zeros (M-space SVD of teacher, noise positions zeroed)
as permanent backbone + teacher signs for ±1 positions + etch mechanism
for sign confirmation/adaptation.

**Results on diverse data (1.2M tokens, 5000 steps):**

| Variant | Loss | L2:rank90 | L2:top1% |
|---------|------|-----------|----------|
| A. Float32 (full GD) | 6.6828 | 13 | 66.5% |
| **C. Backbone 30% + etch** | **6.4603** | 43 | 12.9% |
| B. Backbone 20% + etch | 6.7404 | 42 | 16.7% |
| D. Frozen 30% (no etch) | 7.0221 | 25 | 56.1% |

**Key findings:**

1. **Backbone 30% + etch beats float32 on loss** (6.46 vs 6.68).
   Confirms session 166 result with diverse data and etch adaptation.

2. **Etch on ±1 adds 0.56 over frozen signs** (C=6.46 vs D=7.02).
   The etch mechanism improves loss substantially by adapting the
   teacher's sign topology to the new data distribution.

3. **30% backbone > 20% backbone.** B barely matches float32. The
   backbone needs enough zeros to carve clear facet boundaries.

4. **M-space blurs when adapting to different data.** Teacher's
   rank90=13 (lambda-only gem). Etch variants reach rank90=42-43
   on diverse data. The etch mechanism finds a topology that
   optimizes loss at the expense of the lambda-specific gem —
   because diverse data wants a different attention geometry.
   This is correct behavior: the topology adapts to the actual data.

5. **Zeros are structural, not emergent.** Three experiments confirm:
   oscillation-based zero detection produces zero zeros. The backbone
   must come from M-space SVD of the teacher / crystal geometry.

6. **Un-etch storm near training end.** Learning rate minimum creates
   regime change → mass un-etch + re-etch. C recovered well (6.68→6.46
   through the storm). May need etch-freeze at low LR.

### Architecture validated

```
WHAT WORKS:
  Crystal backbone (zeros)  → from teacher M-space SVD     → permanent
  Teacher signs (±1)        → from teacher weight signs     → initial, adaptable
  Etch mechanism (±1)       → confirms/adapts signs via TD  → improves loss
  Gamma (per-row scale)     → learned by GD                 → magnitude calibration

WHAT DOESN'T WORK:
  Etch from scratch         → no topology to work with      → M-space never forms
  Oscillation → zero        → signal too weak               → zeros must be structural
  Etch without backbone     → loses gem structure            → backbone is necessary
```

## Open Questions

1. **M-space vs loss tradeoff.** Etch optimizes loss but blurs the gem.
   Is this because diverse data genuinely wants a different geometry, or
   because the etch mechanism is too aggressive? Per-layer thresholds
   might help — protect the compute layer (L2) more than others.

2. **Teacher overlay projection fidelity.** How well do 27B overlays
   project onto 1280-dim student? The crystal eigenbasis is universal
   but dimension reduction may lose branch detail.

3. **Etch interval tuning.** The step-5000 un-etch storm suggests etch
   should freeze (stop un-etching) when learning rate drops below a
   threshold. The etch mechanism needs its own schedule.

4. **Per-layer etch thresholds.** The aperture layers (L0-L2) may need
   different thresholds than the fan zone (L8-L48).

5. **Interaction between attention etch and FFN etch.** Does etching
   FFN gates change what attention needs to learn?

6. **Optimal backbone fraction at v14 scale.** 30% works at micro.
   Probably scale-dependent. Sweep needed at v14.

7. **Lattice consensus is relational, not coordinate.** Cross-model
   probe (4 Qwen3 models) showed PC allocation is universal (cos=0.99+)
   but weight-sign agreement is only 12.5%. The combinator structure is
   universal but the coordinate mapping into d_model is model-specific.
   Consensus must use overlay matrices (ISA decoder) not raw weight signs.

## Artifacts

| Component | Description | Status |
|-----------|-------------|--------|
| `scripts/micro/train_etch.py` | v1: etch from scratch (failed) | Done |
| `scripts/micro/train_etch_v2.py` | v2: teacher signs + diverse data | Done |
| `scripts/micro/train_etch_v3.py` | v3: crystal backbone + etch (works) | Done |
| `results/holographic-etch-micro/` | All experimental results | Done |
| `etch_mask` tensor + safetensors storage | Boolean mask per parameter | Design |
| Teacher transfer pipeline | ISA decoder → crystal projection → student etch | Design |
| Modified v14 training loop | Etch-aware TD + backbone zeros | Design |
