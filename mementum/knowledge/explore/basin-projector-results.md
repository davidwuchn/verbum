---
title: Basin Projector Results (v1-v3)
status: done
category: experiment-results
tags: [basin, proxy-metric, MERA, ternary, evolution, PCA]
related: [session-062-probes, ascending-arm-training, compressor-architecture]
depends-on: []
---

# Basin Projector Results (Sessions 056-062)

> Six sessions building proxy-metric models. Concluded: cosine
> similarity to oracle hidden states does not translate to functional
> capability. The approach was abandoned in favor of end-to-end
> training on the actual task (v10).

## The proxy metric hypothesis

Train a small ternary model (MERA ascending arm) to reproduce Qwen3-32B's
L28 hidden states via cosine similarity. If it works, the model learns
the 32B's "typing zone" geometry and can be used as a compressor for
downstream computation.

## Results

| Version | Config | Peak | Step | Ceiling | % Ceiling |
|---------|--------|------|------|---------|-----------|
| v1 | d=64, gamma+evo | **0.743** | 16K | 0.845 | **88%** |
| v2 | d=512, gamma-only | 0.657 | 12K | 0.952 | 69% |
| v3 | d=512, gamma+evo | 0.669 | 17K | 0.952 | 70% |

### v1 (d=64, gamma + evolution) — best overall

| Step | Overall | S-expr | Math | Prose | Behav | Complex | Mixed | Loss |
|------|---------|--------|------|-------|-------|---------|-------|------|
| 1K   | 0.613   | 0.719  | 0.605| 0.651 | 0.623 | 0.534   | 0.515 | 0.390 |
| 5K   | 0.688   | 0.792  | 0.741| 0.702 | 0.684 | 0.635   | 0.634 | 0.299 |
| 10K  | 0.730   | 0.808  | 0.781| 0.753 | 0.714 | 0.692   | 0.681 | 0.269 |
| **16K** | **0.743** | **0.820** | **0.800** | **0.745** | **0.735** | **0.694** | **0.703** | **0.260** |
| 20K  | 0.685   | 0.775  | 0.753| 0.696 | 0.678 | 0.626   | 0.658 | 0.313 |

Late degradation (16K→20K): loss rose, likely evolution interference +
LR too high in well-trained model.

### v2 (d=512, gamma-only) — control experiment

Higher ceiling (0.952) but worse overall (0.657). Removing evolution was
based on a wrong inference: v1's 33/33/33 topology distribution ≠
"evolution contributed nothing." Distribution ≠ assignment — evolution
made targeted swaps improving routing while maintaining balanced macro
distribution. 22.7% acceptance rate (182/800) meant real signal.

v2's results ARE the control: without evolution, plateau 4K steps earlier
and 8.6pp lower. Gamma can scale channels but can't route signals.

### v3 (d=512, gamma + evolution) — evolution restored

Restored evolution to d=512. Peak 0.669 — slightly better than v2 but
still well below v1. The d=512 model couldn't leverage the extra capacity.

## The pivot (session 062)

The question that triggered the pivot: *"We found the compressor. We
found that we could route to kernel functions. We did not build on
either. What is this design supposed to accomplish?"*

All three basin projectors optimized a proxy metric (cosine similarity
to 32B hidden states) instead of the actual task (correct computation).
Meanwhile, two proven components — the v7 compressor and the VSM tree
kernel — sat unused.

**Decision: abandon proxy metric optimization. Train end-to-end on the
actual task. → v10.**

## Key findings

- **Proxy metric ≠ functional capability.** High cosine sim to oracle
  doesn't mean the model can compute correctly.
- **Evolution matters for ternary.** 33/33/33 distribution is maintained
  but individual weight assignments change meaningfully.
- **Width alone doesn't help.** d=512 had 13× more capacity than d=64
  but performed worse. The problem was the objective, not the model.
- **AdamW corrupts ternary weights.** Weight decay on packed ternary
  params causes silent corruption. Fix: `freeze_ternary_weights()`.

## Data artifacts

- Checkpoints: `checkpoints/basin/`, `checkpoints/basin-v2-d512/`,
  `checkpoints/basin-v3-d512/`
- Analysis: `results/basin-analysis/`
- Training logs: `results/basin-v2-d512/`, `results/basin-v3-d512/`
- Oracle data: `results/oracle-data/` (160 shards, 442K words, 3.9 GB)
- Scripts: `scripts/v9/train_basin*.py`, `scripts/v9/deep_analyze_checkpoint*.py`
