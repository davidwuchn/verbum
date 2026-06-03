---
title: FFN Circuit Types — LARQL Decomposition Applied to Verbum
status: active
category: methodology
tags: [ffn, circuit-types, larql, depth-profile, instrument]
related: [phi-information-partition, residual-covariance-rank, standing-wave-magnitudes]
depends-on: []
---

# FFN Circuit Types

> cos(W_up[j], W_down[:, j]) is a zero-cost instrument (pure weight geometry,
> no forward passes) that reveals the same depth-phase structure our activation-
> level measurements found. Discovered by applying LARQL's methodology to
> Pythia-160M in session 186.

## Source

[LARQL](https://github.com/chrishayuk/larql) treats each FFN neuron as a
key-value pair: the up-projection row is the *key* (what triggers it), the
down-projection column is the *value* (what it outputs). The cosine between
them classifies the neuron's **circuit type**.

## Circuit Type Classification

| Type | cos range | Behavior |
|------|-----------|----------|
| Identity | > 0.5 | Reads X, writes X back (self-reinforcement) |
| Transform | 0.2 – 0.5 | Reads X, writes related form (rotation) |
| Projector | -0.2 – 0.2 | Reads X, writes something orthogonal (factual bridge) |
| Suppressor | -0.5 – -0.2 | Weak direction flip |
| Inverter | < -0.5 | Strong direction flip (cancellation) |

## Key Finding: Depth Profile Confirms Phase Structure

Pythia-160M (12 layers, non-gated FFN) shows clear phase structure from
pure weight geometry, matching our activation-derived phases:

```
Layer  Proj%   Supp+Inv%  Trans%  Dark%   Verbum Phase
─────  ──────  ─────────  ──────  ──────  ──────────────
L0     99.7%      0.0%     0.3%   99.2%   EXPAND
L1-2   33-63%    59-65%    1-2%   99.0%   EXPAND→ORTHO
L3-7   23-30%    60-74%    3-10%  97-99%  ORTHO ← inverters dominate
L8     39.0%     46.1%    14.3%   94.7%   Transition
L9-10  50-62%    35-43%    3-7%   92-93%  ALIGN
L11    61.6%     35.7%     2.6%   56.9%   COLLAPSE ← dark drops
```

### Phase Mapping

| Verbum Phase | LARQL Circuit Signature | What It Means |
|---|---|---|
| **EXPAND (L0)** | 99.7% projector | Features scatter input into orthogonal directions |
| **ORTHO (L3-7)** | 60-74% suppressor+inverter | Features *flip directions* — invisible computation in null space |
| **ALIGN (L9-10)** | 50-62% projector, rising | Features become factual bridges |
| **COLLAPSE (L11)** | 62% projector, dark drops to 57% | Features resolve into vocabulary-aligned token directions |

### Cross-Model Comparison

LARQL found a related but different profile on Gemma 3 4B (34 layers,
gated FFN with SiLU):

```
L0-L6:   97% projector (passive)
L7-L18:  60% projector, 40% transform+suppress (active)
L19-L29: 85-95% projector (knowledge)
L30-L33: 89% projector + 11% identity+inverter (format gate)
```

Key differences:
- Gemma's middle layers are **transform-dominated** (partial rotation)
- Pythia's middle layers are **inverter-dominated** (direction flip)
- This may reflect gated vs non-gated FFN architecture: gated FFNs
  can do partial rotation via SiLU gating; non-gated FFNs must do
  direction flipping via GELU to achieve similar computation

## KIBC Opcodes Are Orthogonal to Circuit Types

Cross-tabulation at every layer shows uniform distribution: K, I, B, C
neurons have the **same** circuit type distribution. ρ ≈ 0 within layers.

```
Layer 3 example (all opcodes ~same distribution):
  K → 22.5% proj, 40.2% supp, 33.4% inv
  I → 21.0% proj, 43.3% supp, 33.3% inv
  B → 26.2% proj, 40.4% supp, 29.4% inv
  C → 22.8% proj, 40.4% supp, 34.1% inv
```

This means:
- **KIBC**: measures *what input patterns* activate the neuron (lambda probes)
- **Circuit type**: measures *how the neuron geometrically transforms* input→output
- These are **independent axes** of FFN neuron characterization
- Both are useful; neither subsumes the other

## Correlation Sign Flip Across Depth

ρ(cos(up,down), KIBC_profile_magnitude) changes sign:

| Layer | ρ | Interpretation |
|-------|---|---|
| L0 | +0.07 | Near zero — both random at this depth |
| L3 | -0.11 | Inverters respond MORE to KIBC |
| L8 | **-0.26** | Strongest: inverters are the KIBC-responsive neurons |
| L11 | **+0.27** | Reverses: projectors are now the KIBC-responsive neurons |

Middle layers use direction-flipping neurons to do lambda computation.
Final layer uses factual-bridge neurons for lambda output.

## Dark Space Gradient

"Dark" features (max cosine with any embedding < 0.15) don't point at
any specific token — they operate in computation space, not vocabulary
space.

```
L0-L10: 93-99% dark (computation space)
L11:    57% dark ← 43% of features point at actual tokens
```

The 40-point drop at the final layer means Pythia concentrates its
vocabulary-aligned knowledge in L11. Earlier layers operate in directions
that don't correspond to individual tokens.

This IS the standing-wave picture: middle layers are ORTHO phase where
computation happens in the null space. L11 is where it projects back
into vocabulary-aligned directions (antinodes of the standing wave).

## Instrument Value

cos(W_up[j], W_down[:, j]) should be added to crystal trace tooling:

```python
# Zero-cost depth phase detector — no forward passes needed
W_up = model.layers[l].mlp.up_proj.weight      # (intermediate, hidden)
W_down = model.layers[l].mlp.down_proj.weight   # (hidden, intermediate)
up_norm = F.normalize(W_up, dim=1)
down_norm = F.normalize(W_down.T, dim=1)
cos_up_down = (up_norm * down_norm).sum(dim=1)  # (intermediate,)
# Distribution of cos_up_down reveals the layer's computational phase
```

For **feature labeling** (what each neuron "means"):
```python
# Project down columns against output embedding
W_lm = model.lm_head.weight                    # (vocab, hidden)
logits = W_lm @ W_down[:, j]                   # (vocab,)
top_token = tokenizer.decode([logits.argmax()])
```

## Experiments

- `scripts/experiments/ffn_decomposition.py` — circuit type + token label analysis
- `scripts/experiments/ffn_kibc_crossref.py` — KIBC × circuit type cross-reference
- Results: `results/ffn-decomposition/summary.json`, `cos_values.npz`, `kibc_crossref.json`

## Crystal Signs Predict Circuit Types (session 186, experiment 2)

**ρ(sign_profile, full_profile) = 1.000 across depth.** The ternary sign
structure alone predicts the same depth phase curve as the full weights.

### Sign Agreement Depth Profile

```
sign_agree = fraction of dims where sign(W_up[j,k]) == sign(W_down[k,j])
0.5 = random (independent signs), >0.5 = correlated, <0.5 = anti-correlated

L0:  0.530  CORRELATED   → projectors   → EXPAND
L3:  0.384  ANTI-CORR    → inverters    → ORTHO peak
L4:  0.380  ANTI-CORR    → deepest      → ORTHO peak
L8:  0.451  recovering   → transitional → ALIGN onset
L11: 0.443  ANTI-CORR    → still flipped→ COLLAPSE
```

Random signs would give exactly 50%. GD creates anti-correlation between
up and down signs — the crystal *learns* to make middle-layer neurons be
inverters.

### Per-Neuron Correlation

At every layer, ρ(cos_sign, cos_full) > 0.90. At ORTHO layers (L2-L8),
ρ > 0.985. The signs predict which individual neurons are projectors vs
inverters with 98%+ fidelity.

### Implication for the Crystal Equation

`W_eff = C · T ⊙ M` — the sign tensor T between up and down projections
determines the layer's computational role:
- Correlated T_up, T_down → projector features → lookup/knowledge
- Anti-correlated T_up, T_down → inverter features → computation
- The depth gradient of anti-correlation IS the phase structure
- Magnitudes add precision; topology is already in the signs

### Experiments

- `scripts/experiments/crystal_circuit_types.py`
- Results: `results/crystal-circuit-types/summary.json`

## Open Questions

1. **Does the gated vs non-gated architecture explain the transform vs inverter
   difference?** Gemma (gated, SiLU) shows transforms; Pythia (non-gated, GELU)
   shows inverters. The gating mechanism may allow partial rotation that non-gated
   FFNs must achieve through direction flipping.

2. **Does the circuit type distribution predict the zero mask?** Inverters might
   preferentially occupy zero positions (they cancel, so zeroing them is less
   destructive). Projectors might be the knowledge neurons that must be preserved.

3. **Is the sign anti-correlation universal across models?** The sign agreement
   depth profile (0.53 → 0.38 → 0.45) should be measurable on any transformer.
   If Qwen/Llama/Gemma show the same U-shape, it's architecture-independent.

4. **ANSWERED: Cross-matrix anti-correlation is load-bearing (session 186, exp 3).**
   Decorrelating T_down (shuffling columns to destroy anti-correlation while
   preserving per-matrix statistics) degrades PPL from 511.6 to 1817.4 — a 3.6×
   worse result. Decorrelated ≈ random (1817 vs 1952), confirming: the per-matrix
   signs WITHOUT cross-matrix correlation are nearly worthless. The phase structure
   is the dominant signal. See `scripts/experiments/paired_crystal_sieve.py`.

   | Condition | Init PPL | Final PPL (250 steps) | vs Crystal |
   |-----------|----------|----------------------|------------|
   | Crystal (natural anti-corr) | 107K | **511.6** | 1.0× |
   | Decorrelated (shuffled T_down) | 485M | 1817.4 | 3.6× worse |
   | Random (both random) | 485M | 1952.5 | 3.8× worse |

   The 3.6× vs 3.8× comparison (decorrelated vs random) shows that per-matrix
   sign statistics contribute almost nothing once cross-matrix correlation is
   destroyed. **The anti-correlation IS the signal.**
