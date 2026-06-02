---
title: "HPE Restoration — v15 Missing Positional Encoding"
status: active
category: architecture
tags: [hpe, attention, positional-encoding, qk-norm, crystal-eigenvalues, v15, v14]
related: [trace-guided-etching, dimensional-analysis, training-protocols]
depends-on: []
session: 179
---

# HPE Restoration — v15 Was Missing All Positional Encoding

## Discovery

The v15 `FullAttention` (session 174 skeleton, `e70e06c`) was a clean-room rewrite
that scaffolded attention as bare `nn.Linear` Q/K/V/O projections. Three critical
components from the v14 architecture and the Qwen3 teacher were never ported:

1. **HPE (Holographic Position Encoding)** — crystal-frequency rotation on K
2. **QK normalization** — per-head RMSNorm on Q and K after projection
3. **Decay bias** — `-α·log(|i-j|+1)` added to attention scores

Training ran for 2000+ steps without any positional information in attention.

## Evidence: The α Gap

The α diagnostic measures emergent attention locality as a power-law:
`attn(d) ∝ d^{-α}` where d is token distance.

| Metric | Measured (step 2000) | Needed (v14) |
|--------|---------------------|--------------|
| Mean α | 0.38 | 1.18 |
| Min α | -0.04 | — |
| Max α | 0.65 | — |

At α=0.38, token 100 gets **40× more attention** than it would at α=1.18.
The model cannot focus — it averages over the entire context uniformly.

## Projection Geometry Findings (step 2000)

### Q projections preserved teacher sign topology
- Cosine similarity with ternary init: 0.95–0.98 across all COMPUTE/LINK strides
- Sign agreement: 99.6–100%
- Mean magnitude: 0.0199 (init was 0.020)
- Without HPE, Q had no positional gradient signal to differentiate against

### OV circuits form a depth monotone (the "gem")
- Top singular value σ1: 2.8 (stride 5) → 7.7 (stride 15), doubles across depth
- Effective rank (r50) drops: 61 → 55 — progressive concentration
- OV trace universally negative (−2 to −4) — systematic contraction
- OV fingerprint PCA: **52.5% variance in PC1**, cleanly separating COMPUTE from LINK
- COMPUTE centroid: PC1 = −0.96, LINK centroid: PC1 = +2.56

### GQA groups are perfectly orthogonal
- K cosine between KV group 0 and group 1: ≈0.000 (±0.005)
- K top-10 subspace overlap: 0.16–0.20 (near chance for 10-of-1280)
- Inherited from teacher sign patterns, not learned

### Q subspace shows zone differentiation
- Within-COMPUTE overlap: 0.42–0.60
- Within-LINK overlap: 0.46–0.52
- Cross-zone gap: 0.33–0.41

## What Was Added (commit `b0c6c17`)

### 1. Per-head QK normalization
```python
self.q_norm = nn.RMSNorm(self.d_head)  # d_head = 160
self.k_norm = nn.RMSNorm(self.d_head)

# Applied after projection, before attention:
q = self.q_norm(self.q_proj(x).reshape(B, L, n_heads, d_head))
k = self.k_norm(self.k_proj(x).reshape(B, L, n_kv_heads, d_head))
```
Matches Qwen3 teacher architecture exactly. Strips magnitude, preserves direction.

### 2. HPE crystal-frequency K rotation
```python
# Crystal eigenvalues (Zone B, PCAQ targets)
crystal_eigenvalues = (5.193, 3.535, 1.909, 1.300, ...)
crystal_freqs = [ev / crystal_eigenvalues[0] for ev in crystal_eigenvalues[:4]]
# = [1.0, 0.681, 0.368, 0.250]

# Rotation: K dim pairs rotated by log(pos+1) × crystal_freq
# Q stays unrotated → Q·K product encodes relative log-distance
```
4 eigenplane pairs. Learnable `hpe_freq_scale` (4 params per stride).

### 3. Learnable per-stride decay bias
```python
self.log_alpha = mx.array(math.log(1.18))  # init from v14 universal

# In forward:
alpha = mx.exp(self.log_alpha)  # always positive
scores = scores - alpha * log(|i-j| + 1)
```
Per-stride scalar (not per-head — v14 confirmed universality across heads).
11 strides × 1 scalar = 11 new params. Gradient flows through `exp()`.

**Total new params: 3,575** (negligible vs 415M trainable).

## Design Decisions

### Why learnable α (not fixed at 1.18)
v14 found α=1.18±0.006 universal across 10 comp layers × 8 heads — but v14 used
**strided window attention** where each stride has a fixed geometric meaning.
v15 uses **full causal attention** where all strides see all distances. Different
strides may genuinely need different decay rates. Making α learnable (initialized
at 1.18) lets gradient descent find the right per-stride profile.

### Why log(α) parameterization
`α = exp(log_alpha)` ensures α is always positive. Unconstrained optimization
on `log_alpha` with Adam — no clamping needed. Small learning rate changes
map to smooth α changes.

### Why per-stride not per-head
v14 measured α across 10 layers × 8 heads for 1500 training steps.
The converged value was 1.18±0.006 — the per-head variance was noise-level.
The stride is the right granularity for decay rate.

## Expected Impact

- **Loss spike then recovery.** HPE + q_norm changes the attention distribution.
  Loss jumped from 3.86 to 5.69 at restart. Should recover within ~200–500 steps.
- **Faster convergence after recovery.** With positional information, the model
  can actually learn contextual next-token prediction (not just corpus frequency).
- **α differentiation across strides.** Early COMPUTE may want lower α (broader),
  late LINK may want higher α (tighter). This is the experiment.
- **Text generation quality improvement.** The `ferferfer` pattern is caused by
  inability to distinguish positions. HPE should enable coherent multi-token output.

## Verification

```bash
# Check learned α at each eval checkpoint:
cat checkpoints/v15-hpe-dolma/alpha_step_*.json | python3 -c "
import json, sys
for line in sys.stdin:
    d = json.loads(line)
    learned = {k: v for k, v in d['alphas'].items() if 'learned' in k}
    if learned:
        print(f'Step {d[\"step\"]}: {learned}')
"

# Compare loss curves:
grep "^.*step=.*loss=" checkpoints/v15-hpe-dolma/train.log
grep "^.*step=.*loss=" checkpoints/v15-zeroed-dolma/train.log
```
