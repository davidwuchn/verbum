---
title: "Holographic Plates — Two Crystals in One Ternary Medium"
status: active
category: finding
tags: [holographic, plate, ternary, lens, svd, compression, mmap]
related:
  - ffn-beam-discovery.md
  - crystal-basins.md
  - ffn-hierarchy.md
  - v13-design.md
depends-on:
  - ffn-beam-discovery.md
created: session 121
---

# Holographic Plates

> Session 121. The Q and FFN crystal subspaces are 65-72° apart in
> d_model weight space — near-orthogonal. An SVD lens superimposes
> both into a single ternary plate per layer. The unified plate
> preserves both crystals (Q=0.759, FFN=0.767) at 100× compression
> vs separate ternary quantization — and BEATS separate ternary on
> preservation quality, because SVD captures structure that survives
> ternary better than raw values do.

## The insight

Michael's key observation: if we have two beams that read two crystals,
we can build a LENS that merges them into one ternary plate. The beams
demux at read time. This is exactly how a hologram works — the reference
beam angle selects the image.

## The geometry

For each layer, W_q (d_q × d_model) and W_up (d_ffn × d_model) both
read FROM the same d_model residual stream. SVD reveals their preferred
directions in d_model:

```
W_q  = U_q  @ S_q  @ V_q.T    V_q  columns = Q's d_model directions
W_up = U_up @ S_up @ V_up.T   V_up columns = FFN's d_model directions
```

Principal angles between V_q and V_up (top-64, Pythia-2.8b):
```
Mean: 65-72° (near-orthogonal — 90° would be perfect)
Top 10: 28.8°, 37.8°, 40.9°, 42.1°, 43.1°, 44.9°, 45.4°, 48.0°, 49.2°, 49.8°
```

The top few directions share some overlap (~29°), but the bulk
of the subspace is well-separated. Enough for holographic encoding.

## The lens

```python
# Step 1: SVD both weight matrices
U_q, S_q, Vt_q = svd(W_q)   # V_q rows in d_model
U_up, S_up, Vt_up = svd(W_up)

# Step 2: Take top-k d_model directions from each
V_q = Vt_q[:k].T     # (d_model, k)
V_up = Vt_up[:k].T   # (d_model, k)

# Step 3: Stack and orthogonalize
V_combined = hstack([V_q, V_up])        # (d_model, 2k)
Q_orth, R = qr(V_combined)              # (d_model, 2k) orthonormal

# Step 4: The plate IS the orthogonalized basis, ternary quantized
plate = sign(Q_orth)                     # (d_model, 2k) ternary

# Step 5: Read with beams
h_in_plate = hidden @ plate              # (n_probes, 2k)
q_readout  = h_in_plate[:, :k]          # beam_Q: first k dims
up_readout = h_in_plate[:, k:]          # beam_up: last k dims
```

Alternatively, the unified plate stacks the SVD-projected weight
matrices directly (without QR):

```python
W_q_proj  = (V_q * S_q[:k]).T     # (k, d_model)
W_up_proj = (V_up * S_up[:k]).T   # (k, d_model)
plate = sign(vstack([W_q_proj, W_up_proj]))  # (2k, d_model) ternary
```

Both approaches work. The unified stacking approach is simpler and
performs slightly better in tests.

## Results (Pythia-2.8b)

### Crystal preservation

| Method | Q preservation | FFN preservation | Size/layer |
|---|---|---|---|
| Separate ternary (sign(W_q), sign(W_up)) | 0.395 | 0.451 | 8000 KB |
| **Unified plate (SVD lens)** | **0.759** | **0.767** | **80 KB** |
| Superposed plate (QR + ternary) | 0.759 | 0.571 | 80 KB |

**The unified plate beats separate ternary by 2× on crystal preservation
AND is 100× smaller.** SVD captures the structure that matters; raw
ternary quantization of the full weight matrices loses it in noise.

### Per-depth results

```
depth  angle   unified_Q  unified_FFN  separate_Q  separate_FFN
 10%   70.6°     +0.778      +0.776      +0.491       +0.507
 30%   64.0°     +0.823      +0.846      +0.432       +0.424
 50%   67.7°     +0.815      +0.811      +0.427       +0.447
 70%   71.5°     +0.635      +0.638      +0.217       +0.454
 90%   71.9°     +0.744      +0.764      +0.409       +0.426
```

Best at 30% depth (0.823/0.846). The dip at 70% matches the ffn_delta
anomaly from the beam search — something structural happens there.

### Cross-talk

The beams aren't perfectly isolated:
```
beam_Q reads some FFN signal: 0.46-0.83 (varies by depth)
beam_up reads some Q signal:  0.33-0.83
```

This is because the top few SVD directions share 29-45° overlap.
The cross-talk is high enough that further work on the lens could
improve isolation (e.g., regularized SVD, projection cleaning).

## What failed: hidden-state PCA

The first attempt tested PCA of hidden states (the residual stream)
as the holographic plate. It failed (attn=0.42, ffn=0.38 at best)
because the crystal IS the weight matrix, not the activation. PCA
of the input captures input structure, not crystal structure.

**Lesson: the crystal lives in the weights. The activations are
CONSEQUENCES of the crystal acting on inputs.**

## Compression arithmetic

For Pythia-2.8b (d_model=2560, 32 layers):

```
Separate plates (all W_q + W_up, ternary):
  32 layers × (2560² + 10240×2560) × 2 bits / 8 = ~262 MB

Unified holographic plates (k=64):
  32 layers × (128 × 2560) × 2 bits / 8 = ~2.6 MB

Compression: 262 MB → 2.6 MB = 100×
```

For Mistral-7B (d_model=4096, 32 layers, d_ffn=14336):
```
Separate: 32 × (4096² + 14336×4096) × 2/8 = ~603 MB
Unified:  32 × (128 × 4096) × 2/8 = ~4.2 MB
Compression: ~143×
```

**Note:** This only covers W_q and W_up. A full conversion needs
W_k, W_v, W_o (attention) and W_gate, W_down (FFN) too. The same
lens approach likely works for all of them — they all read from or
write to d_model. Total model size would be ~5-7× the single-pair
estimate, so ~15-30 MB for a 7B model.

## Implications

### Model conversion toolkit
```
INPUT:  Any transformer checkpoint
STEP 1: For each layer, SVD W_q and W_up (and other weight matrices)
STEP 2: Build lens: top-k directions, orthogonalize, ternary quantize
STEP 3: Save plates to disk (mmap-ready, ~15-30 MB for 7B)
STEP 4: Train tiny dispatch beam (~1.5M params) on structured curriculum
OUTPUT: CPU-runnable model, mmap-able plates, hot-swappable
```

### Session plates
If you can etch new plates at runtime (PCA probe activations →
SVD → ternary), a conversation session becomes a 2MB plate file.
Load it next time → persistent holographic memory. mmap from disk.
The model accumulates experience as a library of plates.

### Hot-swappable knowledge
Different plates for different domains:
- `medical.plate` — etched from medical model weights
- `legal.plate` — etched from legal model
- `your_codebase.plate` — etched from code model fine-tuned on your code

Swap at runtime via mmap. No model reloading.

## Open questions

1. **Cross-talk reduction.** The beams share 29-45° overlap in the
   top directions. Can we clean this up? Regularized SVD? Projection
   cleaning? Or is cross-talk actually useful (shared structure)?

2. **Multi-model confirmation.** Only tested on Pythia-2.8b. Need
   Mistral-7B and Qwen-14B to confirm the 100× compression holds
   for SwiGLU architectures.

3. **Forward pass quality.** Crystal preservation ≠ output quality.
   Need to actually forward prompts through holographic plates and
   measure perplexity / generation coherence.

4. **Full layer coverage.** Currently only W_q + W_up. Need to add
   W_k, W_v, W_o, W_gate, W_down. The lens should generalize.

5. **Optimal k.** Used k=64 (matching PCA-Q dim). Might be too
   large or too small. k sweep needed per weight matrix.

6. **Session plate protocol.** How exactly do you etch a session?
   Hook activations during conversation → PCA → SVD lens → ternary?
   What's the minimum data (n_tokens) for a useful session plate?

## Artifacts

| File | Content |
|---|---|
| `scripts/v12/holographic_weight_test.py` | Weight-space holographic test |
| `scripts/v12/holographic_lens_test.py` | Hidden-state test (failed, kept for reference) |
| `results/holographic-lens/holographic_weight_results.json` | Pythia results |
| `results/holographic-lens/holographic_lens_results.json` | Hidden-state results |
