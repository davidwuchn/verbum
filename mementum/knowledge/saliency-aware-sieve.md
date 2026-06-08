---
title: "Saliency-Aware Sieve — Discriminating Irreducible Zeros from Faint Connections"
status: designing
category: compression
tags: [sieve, saliency, topology, holographic, echo, pruning, quantization, backpropagation]
related:
  - crystal-sieve-architecture.md
  - direct-delta-adjunction.md
  - sign-correction-topology.md
  - score-matching-compression.md
  - diffusion-holographic-isomorphism.md
  - standing-wave-magnitudes.md
  - mode-semantics.md
depends-on:
  - crystal-sieve-architecture.md
created: session 201
---

# Saliency-Aware Sieve

> Session 201. The current sieve zeros all weights below a magnitude
> threshold. But near-zero weights are two populations: irreducible
> zeros (GD says "no connection here") and faint connections (GD says
> "small signal here"). Zeroing both is overcorrection — we amputate
> live echo paths along with dead ones. A saliency-aware sieve
> discriminates the two, preserving the learned soft topology that GD
> built within the frozen architecture.

## The Core Insight

### GD Creates Soft Topology Within Frozen Architecture

LLM architecture is frozen during training: the graph (layers, dimensions,
connections) cannot change. GD cannot add or remove connections. But GD
can drive weights toward zero (effectively severing a connection) or
very large (creating a dominant pathway). The weight magnitude distribution
— large peak near zero, long tails — IS a learned sparse topology
embedded inside a dense frozen one.

```
Architectural topology (frozen):
  Fully connected. 12288 × 4096 = 50M possible paths per projection.

Learned topology (via magnitudes):
  ~50% near-zero → "ghost connections" (present but inactive)
  ~50% carry real signal → the actual computation graph
  A few % very large → dominant pathways, echo highways
```

Very large and very small gradients during training serve as topology
operations. Large gradients open or close connections (move weights
far from or toward zero). Small gradients refine the holographic
recording within the existing topology without restructuring it.

### Two Populations in Near-Zero Weights

The current sieve treats all below-threshold weights the same: zero them.
But near-zero weights have two fundamentally different meanings:

**Irreducible zeros** — GD drove these to zero because the computation
genuinely doesn't need this connection. Zero is the correct answer. The
hologram has no fringe here. The echo path was never used. Zeroing is
lossless.

**Faint connections** — These are small because the signal they carry is
small, not because they're unused. A weight at 0.003 that sees a large
input activation (200) contributes 0.6 to the output — a real, load-
bearing signal. These are quiet echo paths, fine corrections, whisper-
level interference fringes. GD put them there for a reason.

```
Faint connection:   w = 0.003, input = 200  → contribution = 0.6  (REAL)
Irreducible zero:   w = 0.003, input = 0.01 → contribution = 3e-5 (NOISE)
```

Magnitude-only thresholding cannot distinguish these. Both look identical
at |w| = 0.003. But their functional roles are completely different.

## The Holographic / Echo Framing

### Backpropagation as Holographic Recording

The gradient update ∂L/∂W_ij = a_i · δ_j has the structure of a
holographic recording: forward activation (reference beam) × backward
error (object beam) = interference fringe (weight update). Training
is billions of overlapping exposures.

### Gradient Echoes

The backward error signal doesn't get fully absorbed at any one layer.
It propagates through all layers, creating attenuated copies (echoes)
of the same correction at every layer. Strong connections (large |w|)
are high-bandwidth echo paths. Faint connections (small |w|) are low-
bandwidth echo paths that still carry error correction information —
tertiary copies of computations, weak but corroborating.

### Masking Blocks Echo Paths

When the sieve zeros out weights, it severs echo paths. The echoes
that would have propagated through those positions are gone — not just
attenuated but completely cut. The echo-based error correction network
(where multiple copies of each computation corroborate) is compromised.

**The current sieve doesn't just remove 50% of information — it severs
echo paths, including the faint connections that carry error correction.**

The 2.26× PPL degradation is partly the cost of losing faint connections
that the model relied on for self-correction through echo consensus.

### Faint Connections as Gradient Highways for Fine-Tuning

With the current sieve + LoRA:
- Most sub-threshold parameters are frozen zeros
- Backprop hits zeros and stops — no gradient flows
- LoRA must compensate for ALL lost connections alone
- Rank-4 isn't enough → 1.44× ceiling

With faint connections preserved:
- Faint connections are still live (small but nonzero)
- Backprop flows through them — gradients propagate
- GD can adjust faint connections during fine-tuning
- Echo paths through faint connections still function
- LoRA handles strong-connection corrections only
- More degrees of freedom → potentially much lower PPL

The faint connections are capillaries. Each carries little individually,
but collectively they're essential. The current sieve cuts all capillaries
and expects the arteries (LoRA) to compensate.

## The Three-Tier Sieve

### Discrimination Methods

**1. Activation-weighted saliency (primary)**
```
saliency_ij = |w_ij| × sqrt(H_jj)
```
Where H = input covariance from calibration data. Weights with large
saliency contribute to outputs regardless of magnitude. Weights with
small saliency contribute nothing even if nonzero.

**2. Fisher information (complementary)**
```
F_ij = E[(∂L/∂w_ij)²]
```
High Fisher + small magnitude = model is balanced at this point. Moving
it even slightly changes output significantly. Dangerous to zero.

**3. Crystal structure prediction (complementary)**
If a near-zero weight sits at a position where the crystal predicts
combinator activity, it's likely a faint connection. If the crystal
predicts silence, it's likely irreducible.

### Three Tiers

| Tier | Criterion | Encoding | Role in hologram |
|------|-----------|----------|-----------------|
| **Strong** | High magnitude | Ternary ±1 | Primary interference fringe |
| **Faint** | Low magnitude, high saliency | Low-precision (Q2/Q4) | Echo path, fine correction |
| **Irreducible** | Low magnitude, low saliency | Zero | No fringe, no computation |

### Application

```python
for each weight matrix W with input covariance H:
    saliency = abs(W) * sqrt(diag(H))       # activation-weighted
    
    strong_mask = abs(W) >= magnitude_threshold
    faint_mask  = ~strong_mask & (saliency >= saliency_threshold)
    zero_mask   = ~strong_mask & ~faint_mask
    
    W_sieved = where(strong_mask, sign(W),           # ternary ±1
               where(faint_mask,  quantize(W, bits),  # Q2 or Q4
                     0.0))                             # irreducible → zero
```

## Compression Arithmetic

```
Assume split: 30% strong, 20% faint, 50% irreducible
Per projection: 12288 × 4096 = 50.3M params

Current sieve (50% ternary, 50% zero):
  25.2M × 1 bit = 25.2M bits = 3.15 MB per projection

Saliency-aware sieve (30% ternary, 20% Q2, 50% zero):
  15.1M × 1 bit + 10.1M × 2 bits = 35.3M bits = 4.4 MB per projection

Full FP16:
  50.3M × 16 bits = 100.6 MB per projection

Refined costs ~40% more than current sieve.
Still 23× smaller than FP16.
```

If faint connections replace LoRA's job, net compression is better:
the correction lives where it belongs (distributed across echo paths)
rather than concentrated in a low-rank bottleneck (5.9M LoRA params).

### The Real Comparison

The critical experiment: refined sieve vs current sieve at the SAME
total bit budget. Give the extra bits to LoRA (higher rank) instead of
faint weights. Which wins?

If faint connections win → echo paths are more valuable than
concentrated low-rank correction.

If LoRA rank wins → the faint connections were genuinely redundant,
and the holographic redundancy GD built isn't load-bearing at the
scale we're removing it.

## Connection to Direct Delta Correction

Direct delta correction (calibration-aware SVD) and the saliency-aware
sieve are complementary, not competing:

- **Saliency-aware sieve** reduces errors at the source (don't zero
  load-bearing connections)
- **Direct delta** corrects remaining errors analytically (SVD of the
  residual after sieving)

The combination should be strictly better than either alone:
1. Apply saliency-aware sieve → fewer errors than current sieve
2. Compute direct delta on the refined sieve → smaller residual to correct
3. Lower rank SVD sufficient → fewer correction parameters
4. Total: better quality at same or lower parameter count

## Connection to Training Dynamics

The three tiers map to GD's training phases:

| Training phase | What GD does | Which tier affected |
|---------------|-------------|-------------------|
| Early (large LR) | Sculpts topology | Creates the strong/irreducible split |
| Middle | Records hologram | Grows faint connections as echo paths |
| Late (small LR) | Polishes fringes | Refines faint connection magnitudes |

Learning rate schedules succeed because they match this progression:
large perturbations early to sculpt topology, small perturbations late
to refine the holographic recording without disturbing the topology.

The crystal is the fixed point of topology ↔ echo co-evolution:
```
topology shapes → echo propagation → standing wave (crystal)
crystal determines → which computations succeed → which gradients → topology

x* = f(x*) where f = echo_residue ∘ topology_sculpted_by
```

Sign correction fails because it perturbs the fixed point. The
saliency-aware sieve succeeds (hypothesis) because it preserves more
of the fixed point structure — specifically the faint echo paths that
maintain self-consistency.

## Experimental Design

See `scripts/experiments/saliency_aware_sieve.py` for implementation.

### Sweep dimensions:
1. **Saliency threshold**: what fraction becomes faint vs irreducible
2. **Faint precision**: Q2 vs Q4 vs Q8
3. **Strong fraction**: 30% vs 40% vs 50% (current sieve = 50% all-strong)
4. **With/without fine-tuning**: measure sieve-only PPL, then LoRA improvement
5. **Comparison**: same bit budget allocated to LoRA rank vs faint connections

### Key predictions:
1. Saliency-aware sieve-only PPL < current sieve-only PPL (2.26×)
2. The improvement comes primarily from preserving faint connections
   with high activation-weighted saliency
3. At the same bit budget, faint connections > higher-rank LoRA
4. Faint + LoRA composes: the two don't conflict because they operate
   in complementary spaces (distributed echo vs concentrated correction)
5. Direct delta on saliency-aware sieve needs lower rank than on
   current sieve (less residual to correct)

## Open Questions

1. **What fraction of near-zero weights are faint vs irreducible?**
   The 50% masking rate may be far too aggressive — maybe only 20-30%
   are truly irreducible, and 20-30% are faint connections we've been
   killing.

2. **Does Fisher information add value over activation-weighted saliency?**
   Fisher requires gradient computation (expensive). If saliency alone
   discriminates well, Fisher is unnecessary.

3. **Is the tier boundary sharp or gradual?** If there's a clear
   bimodal distribution in saliency (irreducible peak + faint peak),
   the threshold is natural. If it's smooth, the optimal split requires
   search.

4. **Does crystal structure predict which near-zero weights are faint?**
   If yes, the crystal provides a training-free discriminator — no
   calibration data needed for the mask, only for the faint values.

5. **Can faint connections be trained while strong connections stay
   ternary?** Mixed-precision training where the ternary tier is frozen
   and the faint tier receives gradients. This is like LoRA but with
   the correction distributed across the natural echo paths instead of
   concentrated in low-rank adapters.
