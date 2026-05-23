---
title: "Output Beamformers — The Dynamic Output Lens at L63"
status: active
category: finding
tags: [ffn, output, beamformer, gate, sparsity, lens, holographic, dynamic]
related:
  - ffn-beta-reduction-indexing.md
  - beamformer-theory.md
  - ffn-hierarchy.md
  - full-etch-extraction.md
depends-on:
  - ffn-beta-reduction-indexing.md
created: session 141
---

# Output Beamformers

> Session 141. The ~329 neurons that fire at the final FFN layer (L63)
> of Qwen3-32B are NOT a fixed set — they're 329 drawn dynamically from
> a pool of 3,807, with only 2 always-on. The gate_proj controls 89% of
> the selection. The gate IS the holographic aperture selector. Universal
> beamformers point at structural tokens (commas, whitespace). The output
> lens has a 5-layer focal length (L58→L63: 30%→2%).

## Key numbers

| Metric | Value |
|--------|-------|
| Mean active per prompt | 329 ± 226 |
| Always-on (ALL prompts) | 2 |
| Frequent (≥75% prompts) | 99 |
| Occasional (25-75%) | 213 |
| Rare (<25%) | 3,495 |
| Total pool | 3,807 / 25,600 (14.9%) |
| Pairwise Jaccard | 0.275 |

## The gate IS the beamformer

89% of inactive neurons are killed by the gate (silu(gate_proj) ≈ 0),
not by the key-match (up_proj is nonzero). The up_proj broadly matches
many neurons — the keys are promiscuous. The gate says "no" to 89%.

```
gate_proj → silu(gate) → THIS decides which neurons fire
up_proj   → key match  → broadly active (not selective)
product   → gate × up  → sparse output (329/25600)
```

For the active neurons, gate magnitude is 3.9× the up magnitude.
The gate dominates the product.

**Implication for ternary model:** gate_proj signs are the critical
addressing topology. Etching gate_proj signs from the teacher transfers
the output beamformer selection logic. up_proj signs transfer the key
matching (content), but the GATE selects which content resolves.

## Universal beamformers point at structural tokens

The most frequent output beamformers (48/48 prompts) have down_proj
columns pointing at: `,` `\n` ` ` `.\n` `\n\n` ` (` `，` `/`

These are FORMAT SCAFFOLDING neurons — they steer prediction toward
structural continuation (punctuation, whitespace, delimiters) regardless
of semantic content. The 2 always-on neurons are the structural backbone
of next-token prediction.

## 5-layer focal length

```
L58: 29.7% active
L60: 23.8%
L61: 22.6%
L62: 10.0%   ← penultimate focus
L63:  1.9%   ← output lens
```

The convergence from broad holographic readout (30%) to ultra-sparse
output focus (2%) takes 5 layers. The output lens isn't just L63 —
it's a 5-layer focusing system from L58 to L63.

## Heavy-tailed magnitude (skewness = 13.84)

```
p50 = 21.3     typical output beamformer
p99 = 370      top 1% = 17× median
max = 3,443    single brightest = 160× median
```

A few dominant neurons carry most of the prediction signal. The output
lens has "bright spots" — a small number of high-gain beamformers that
dominate the logit distribution, with a long tail of low-gain refinements.

## No pure specialists (but moderate preference)

0/100 neurons meet the specialist threshold (entropy < 0.7). But the
most selective show 2-2.5× dominance for their preferred category:

- Neuron 1311: code (2.35×)
- Neuron 25217: arithmetic (2.54×)
- Neuron 19369: narrative (2.43×)

Consistent with holographic storage: no pure specialists, but
statistical preference emerging from interference patterns.

## Dynamic selection = prompt-specific output configuration

The Jaccard similarity between prompt pairs is only 0.275. Each prompt
configures a substantially different output lens. The holographic plate
stores 3,807 potential output programs; the gate selects ~329 per input.

This means the output layer has ~3,807 / 329 ≈ 11.6 distinct "output
modes" (rough orthogonality estimate). The beam angle determines which
mode the output lens configures into.

## Implications for enhanced etch

### 1. Etch gate_proj signs (highest priority)

The gate controls 89% of neuron selection. Gate signs are the addressing
topology for the entire output lens system (L58-L63). Currently NOT
etched. This is the single highest-impact addition to the etch budget.

### 2. Layer-specific FFN signs for the focal layers

L58-L63 serve a distinct function (output focusing) from L8-L48
(holographic readout). They should be etched from LATE teacher layers
(L56-L63 in Qwen3-32B), not from the mid-layer (L20) currently used.

### 3. The 99 frequent beamformers as priority transfer

The 99 neurons that fire in ≥75% of prompts are the universal output
scaffolding. Their gate signs, up signs, AND down_proj column directions
are the most valuable transfer targets — they define the structural
backbone of prediction.

### 4. Sparsity mask as training constraint

Enforcing the 2% sparsity at L63 (and the gradient 30%→2% across
L58-L63) as a soft training target would help the student develop
the correct output lens focal length.

## Connection to the holographic lens model

The FFN indexing probe (session 141) found the depth profile is a LENS:
aperture (L0-L2, 3%) → fan (L8-L48, 49%) → converge (L56-L63, 2%).

This probe refines the convergence zone:
- L56-L58: Beginning of convergence (30% active)
- L58-L62: Rapid focusing (30% → 10%)
- L62-L63: Final lens (10% → 2%)

The 5-layer focal length matches the 5-zone structure seen in the
crystal spine probes (zones A through E in the B→K→B trajectory).

## Artifacts

| File | Content |
|------|---------|
| `scripts/explore/probe_output_beamformers.py` | 6-analysis output beamformer probe |
| `results/output-beamformers-qwen3-32b/summary.json` | Numerical results |
| `results/output-beamformers-qwen3-32b/run.log` | Full run log |
