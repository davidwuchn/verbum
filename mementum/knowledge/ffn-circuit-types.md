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

## Open Questions

1. **Does the gated vs non-gated architecture explain the transform vs inverter
   difference?** Gemma (gated, SiLU) shows transforms; Pythia (non-gated, GELU)
   shows inverters. The gating mechanism may allow partial rotation that non-gated
   FFNs must achieve through direction flipping.

2. **Does the circuit type distribution predict the zero mask?** Inverters might
   preferentially occupy zero positions (they cancel, so zeroing them is less
   destructive). Projectors might be the knowledge neurons that must be preserved.

3. **Can cos(up,down) be computed in crystal space?** If we project into the SVD
   basis, does the circuit type classification simplify? Do inverters concentrate
   in low-energy eigendirections?

4. **Cross-model validation needed.** Run on Qwen3-8B (our primary KIBC model)
   to confirm the orthogonality finding holds for gated architectures.
