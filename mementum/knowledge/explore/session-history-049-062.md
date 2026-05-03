---
title: Session History (049-062)
status: done
category: session-history
tags: [sessions, history, v7, v8, v9, v10, basin, probes]
related: [basin-projector-results, session-062-probes]
depends-on: []
---

# Session History: 049-062

> Breadcrumb trail from v7/v8 architecture through basin projectors
> to v10 pivot. Covering ~14 sessions of architecture evolution.

## Sessions 049-053 — v7/v8 architecture + training infrastructure

v7 pipeline LM (4-stage VSM). v8 DualMERA (compressor + pipeline), all
ternary, 559M params. Dolma re-tokenization. BIOS flash data. Evolutionary
mutation system. MLX quantized_matmul for ternary.

## Sessions 054-055 — VSM tree kernel proven

VSM tree architecture: 22 ops, 5 types, 100% accuracy, 8K ternary weights.
Identity as substrate principle discovered. A3B types prose correctly.
Extraction path identified: tokens → ascending arm → tree → VSM kernel.

## Session 056 — Typing zone + basin geometry + cross-notation convergence

Five probes on Qwen3-32B established: typing zone L28-37, 7 natural
HDBSCAN clusters, 3-level dispatch hierarchy, behavioral frames reshape
types deeply, 53/54 cross-notation pairs exceed 0.5 cosine similarity.
Reframed ascending arm target from CCG labels to geometric basins.

## Session 057 — PCA analysis + oracle pipeline

d_basin=64 confirmed (22.5× separation). d_model=256 chosen. Embedding
must be learned (PCA distillation fails). Oracle pipeline built and
pilot-validated (500 sentences, 2632 words).

## Session 058 — Oracle extraction + basin projector built

Full 80K sentence oracle extraction: 442,682 words, 160 shards, 3.9 GB.
PCA re-fit on full data. Basin projector model built (MERA ascending arm).
Training loop built with Adam + evolution + cosine loss.

## Session 059 — AdamW corruption bug + first healthy training

Found critical bug: AdamW weight decay corrupts packed ternary weights.
Fix: freeze_ternary_weights(). Fixed 6 checkpoint resume gaps. First
healthy v1 training: 0.613 overall at step 1K (73% of ceiling).

## Session 060 — Deep analysis + v2 basin projector

v1 completed (peak 0.743 at 16K). Deep per-word analysis revealed width
bottleneck: PCA at d=64 destroys context-dependent variation. Built v2
at d=512: higher ceiling (0.952) but worse overall (0.657). Removed
evolution based on wrong inference about topology distribution.

## Session 061 — v3 basin projector (d=512 + evolution restored)

Built train_basin_v3.py restoring evolution to d=512 model. Key insight:
removing evolution was wrong — 33/33/33 distribution ≠ unchanged topology.
v2 was the control experiment proving evolution's contribution. v3 training
launched (~12-14 hours).

## Session 062 — The pivot: probes + v10

Stopped chasing oracle proxy metrics. Four probes on Qwen3-32B:
- Type transition: compression IS typing
- Parse structure: no tree composition, all-at-once in last 5 layers
- Binding structure: binding gap +0.15 at L28, types = bindings
- Compressor binding: CompressorLM has 80-91% of 32B signal

Built v10: strided compressor + tree of VSMs. Smoke tested. Ready to
train at scale.

See: [basin-projector-results](basin-projector-results.md),
[session-062-probes](session-062-probes.md)
