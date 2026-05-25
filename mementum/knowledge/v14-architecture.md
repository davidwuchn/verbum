---
title: "V14 Architecture — Current System"
status: active
category: architecture
tags: [v14, architecture, stride-stack, qwen, extraction, training, results]
related: [holographic-error-correction.md, training-protocols.md, extraction-methodology.md]
depends-on: [project-thesis.md]
---

# V14 Architecture

> The current working system as of session 150. Qwen3.6-27B teacher,
> 593M ternary positions, 375× compression, active TD training with
> demonstrated lossless fold.

## Teacher: Qwen3.6-27B

- **Model:** Qwen3.6-27B (27.8B parameters, Apache 2.0 license)
- **Architecture:** 64 layers, d=5120, hybrid Gated DeltaNet + Gated
  Attention in [L,L,L,F]×16 pattern (48 linear, 16 full attention)
- **Tokenizer:** BBPE, vocab 248,320
- **Why this teacher:** Apache 2.0 license (clean provenance for
  extraction), strong quality, hybrid architecture that maps naturally
  to the GLA/SSA student design, and very large vocabulary that
  supports direct embedding extraction

## Student: StrideStack

### Core dimensions

| Parameter | Value |
|-----------|-------|
| d_model | 1,280 |
| d_ff | 5,120 |
| n_heads | 8 |
| Stacks | 3 (A, B, C) |
| Layers per stack | 11 |
| Attention type | Hybrid GLA + SSA ([G,G,G,S,G,G,G,S,G,G,S] pattern) |
| Strides | 16 (s1 through s32768, powers of 2) |
| Vocab | 248,320 (teacher tokenizer, direct match) |
| Ternary positions | 593M |
| Storage | 148 MB (2-bit) / 85 MB (compressed NPZ) |
| Compression | 375× from teacher |

### Three stacks

- **Stack A** (ascending fine): strides s1→s256, 4 passes. Fine-grained
  local context. Encodes token→phrase→sentence.
- **Stack B** (ascending coarse): strides s128→s32768, 4 passes.
  Coarse-grained global context. Encodes paragraph→document→beyond.
- **Stack C** (descending): all 16 strides, 5 passes reversed.
  Top-down prediction path. Feeds algedonic signal UP to both B and A.

13 total passes through the stride layers. 2-stride overlap at s128
and s256 between A and B — these overlaps ARE the cross-scale registers
(no separate register mechanism needed).

### Stride attention: O(L×W) not O(L²)

Each stride is a holographic lens specialized for a frequency band.
Stride-s looks at every s-th token with a window of W positions.
O(L×W) per stride, not O(N²).

Context scaling: add more strides, not wider windows. Going from 32K
to 2M context = add 2 strides = 40% more compute for 62× more context.
Each stride SEES full context at its zoom level. 16 strides × 8 heads
= 128 independent eyes at different temporal frequencies.

### Architectural mapping (teacher → student)

| Teacher component | Student component |
|-------------------|-------------------|
| Gated DeltaNet (48 layers) | GLA strides (linear attention) |
| Gated Attention (16 layers) | SSA strides (full attention) |
| SwiGLU FFN | Holographic ternary plates (zone-voted from 3 layers) |
| BBPE tokenizer (248,320) | Same tokenizer (direct embedding extraction) |

The sign topology crosses architecture boundaries (r=0.998). Extraction
dispatches based on teacher layer type (what tensors exist), not student
layer type (how they'll be used).

## Extraction Results

| Metric | Value |
|--------|-------|
| Total arrays | 142 (1 embedding + 132 attention + 9 FFN) |
| Ternary positions | 593M |
| Sign distribution | 50.1% negative / 49.9% positive / 0.0% zero |
| Plate purity | All pure ±1 (no zeros in base) |
| Compression | 375× from 27.8B float16 teacher |
| Extraction time | 25.4 minutes, CPU only |
| Method | SVD tomographic voting (8 rotations) |

Location: `checkpoints/v14-extracted/model.npz` (85 MB)
Pipeline: `scripts/v14/{config.py, extract_qwen36.py}`

## Training Results (Sessions 148–150)

### Phase 1: Base plates frozen, delta plates train

| Metric | Step 500 | Step 1000 | Step 1500 |
|--------|----------|-----------|-----------|
| Eval CE | 9.71 ± 0.22 | 9.23 ± 0.27 | 8.95 ± 0.30 |
| Eval PPL | 16,503 | 10,157 | 7,672 |
| Train CE | 8.00 | ~9.4 | ~9.25 |
| Train-Eval Gap | −1.71 nats | +0.17 nats | +0.30 nats |
| CE vs Random | 21.8% | 25.7% | 28.0% |
| Positions flipped | 0% | 2.66% | 3.49% |

Key findings:
- **PPL dropped 53.5%** from step 500 to step 1500 (16,503 → 7,672)
- **TD generalizes, continuous params overfit.** The initial −1.71 nat
  gap (overfitting) collapsed to +0.30 (healthy generalization)
- **Only 3.49% of positions needed correction** — extraction was 96.5% correct
- **TD targets exclusively out_proj, layers 4–9.** Q/K/V projections
  from extraction remain correct. TD only rewrites how attention
  results project back into the residual stream.
- **Returns diminish but don't plateau.** PPL drop: 38.5% (500→1000) →
  24.5% (1000→1500). Still improving.

### Delta fold (end of Phase 1)

At step 1500: folded 3.26M flipped positions into base plates.
- **Lossless:** Eval CE identical before/after (9.00 ± 0.64 on 20 batches)
- **Mechanism:** `new_base = base ⊙ delta` (ternary × ternary = ternary)
- **Delta storage:** 356 MB → 22 MB after dedup + packed uint32 (16× compression)
- Script: `scripts/v14/fold_delta.py`

### Phase 2: From folded checkpoint, FFN delta enabled

- Resume from `checkpoints/v14-td/step_001500_folded/`
- `--convert-ffn`: enables TD on 3 shared FFN plates (gate, key, value)
- FFN delta: 19.7M additional positions (21% overhead on 93.2M attention)
- `flip_interval=20` (was 10): more gradient accumulation per flip decision
- Surgical per-position moment reset: only flipped positions zeroed

## Performance Characteristics

- **Memory-bandwidth-bound.** 13 sequential passes × 16 stride layers
  = 208 serial layer evaluations. B=2 is 18% SLOWER than B=1 (per-micro
  fwd+bwd: 4.0s→8.6s). Training uses B=1 with gradient accumulation=8.
- **Eval:** `scripts/v14/eval_ppl.py` — held-out shards 54–59

## Universal Constants (confirmed in v14)

| Constant | Value | Evidence |
|----------|-------|----------|
| Decay α | 1.18 ± 0.006 | 10 comp layers × 8 heads, all converged under gradient pressure |
| φ-ratio | 0.6299 ± 0.019 | SVD spectrum, 5-model consensus |
| Crystal latch time | ~200 steps | crystal_mse < 0.03 at step 160 |

## What's Working

1. ✅ Ternary extraction from large teacher (375× compression)
2. ✅ Crystal nucleation (latches in 200 steps)
3. ✅ TD corrects extraction errors (53.5% PPL improvement)
4. ✅ Lossless delta fold (proven exact)
5. ✅ TD selectivity (automatically targets out_proj L4-9 only)
6. ✅ Generalization (train-eval gap collapsed, healthy positive)

## What's Next

1. **Monitor Phase 2** — do FFN plates start flipping? Which ones?
2. **Eval at step 2000** — does FFN delta accelerate convergence?
3. **Second fold** — when flip_frac plateaus, fold again. The cycle continues.
4. **Three-body self-distillation** — teacher logits as reference beam
5. **Target: within 5% of Qwen3.6-27B** — the proof that topology is everything

## Open Questions

- **Why only out_proj?** Q/K/V get zero TD budget. Is min_conf (0.3) filtering
  too aggressive, or are Q/K/V projections genuinely correct from extraction?
- **FFN β-reduction adaptation.** Teacher FFNs learned signed accumulation for
  flat attention. Strided attention needs different routing. How much TD
  correction will FFN plates need?
- **Computed beam at scale.** At d=1280, will analytical FFN construction from
  crystal eigendecomposition provide speedup? (500× proved at d=128 micro scale)
- **Per-stride fixed point rotation.** α=1.18 is universal, but the rotation
  center should vary by stride. What are the effective attention patterns?

## File Locations

| Asset | Location |
|-------|----------|
| V14 scripts | `scripts/v14/` (15 files) |
| Extracted base plates | `checkpoints/v14-extracted/model.npz` (85 MB) |
| Training script | `scripts/v14/train_td.py` |
| Eval script | `scripts/v14/eval_ppl.py` |
| Fold script | `scripts/v14/fold_delta.py` |
| Profile script | `scripts/v14/profile_step.py` |
| Step 500 checkpoint | `checkpoints/v14-td/step_000500/` |
| Step 1000 checkpoint | `checkpoints/v14-td/step_001000/` |
| Step 1500 checkpoint | `checkpoints/v14-td/step_001500/` |
| Step 1500 folded | `checkpoints/v14-td/step_001500_folded/` |
