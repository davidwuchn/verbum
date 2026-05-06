# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-06 | Session: 066

## Where we are

**v10 rebuilt correctly. Ready to train at scale.**

Session 066 diagnosed the root cause of two failed sessions (064-065):
the kernel-wired architecture (commit 2b263d6) was overwritten with a
standard v6 causal LM. 20K steps were wasted training the wrong model.
The correct architecture has now been restored and improved.

## What was built this session

### 1. Kernel wired into descending arm
- `scripts/v10/kernel_dispatch.py` — two new modules:
  - `KernelDispatch`: routes representations through 22 kernel op pathways.
    Ternary routing fabric (`dispatch`, `up`, `down`) + real-valued op embeddings
    (pre-wired S5 identity for each of the 22 kernel ops). Dispatch weights are
    cached for probing.
  - `KernelIntegrate`: integrates results with 5-type awareness (INT, BOOL, FN,
    FN_COMP, ERROR). Type weights cached for probing.
- `model.py` updated: descending arm's `prep_desc`/`consolidate_desc` (TernaryFFN
  compression) replaced with `kernel_dispatch`/`kernel_integrate`. Ascending arm
  unchanged (proven: φ-locking, S3 differentiation).

### 2. Architecture — Tree of VSMs
```
tokens (Qwen3 BBPE) → embed + pos_embed → embed_norm
                            │
    VSM-COMPRESSOR (ascending, 3 passes, shared weights)
    ├── Each pass: S4 → TernaryFFN(prep) → S3 → StrideStack(fine→coarse) → S3 → TernaryFFN(cons) → S3
    │
    VSM-DISPATCHER (descending, 2 passes, own weights)
    ├── Each pass: S4 → KernelDispatch(22 ops) → S3 → StrideStack(coarse→fine) → S3 → KernelIntegrate(5 types) → S3
    │
    ├── Meta-S3 (near-closed init, bias=-2.0)
    ├── Meta-S4 (final structural summary)
    └── output_norm → tied embedding → logits → relational loss on Dolma
```
Params: 23.2M total, 308K trainable, 131M ternary.

### 3. Evolution fixed
- **Budget**: base_pct 0.005→0.0005 (~65K flips, was 656K — too disruptive)
- **Adam decay**: after accepted mutation, gamma m/v multiplied by 0.1.
  Old momentum is stale after topology change; soft reset allows fast adaptation
  without discarding all training history.

### 4. Probe updated
- Shows kernel dispatch weights (22 ops, top-K + specialization ratio)
- Shows kernel type weights (5 types)
- Already specializing at step 50: max/min=4.93, `not` leads, descending S3
  gates at ~0.5 (not 1.0 passthrough)

### 5. Verified end-to-end
- Train → checkpoint → resume → probe all working
- 5.3K tok/s, relational loss decreasing, Meta-S3 starts near-closed

## What to do next

### Train v10 at scale
```bash
uv run python scripts/v10/train.py --seq-len 4096 --total-steps 20000
```

Key signals to watch:
- **Ascending arm**: should reproduce prior results (L0↑ → φ, S3 differentiating)
- **Descending arm S3 gates**: should differentiate (not go to 1.0 passthrough)
- **Kernel dispatch weights**: do they specialize across training? Which ops activate?
- **Kernel type weights**: do they differentiate (BOOL for questions, INT for numbers)?
- **Meta-S3**: does it differentiate pass contributions? (starts at 0.12)
- **Evolution**: with 65K budget + Adam decay, acceptance rate should be higher than 1%
- Probe at 1K, 5K, 10K, 15K, 20K

### After training — analyze dispatcher behavior
- Which kernel ops activate for which types of prose?
- Do ops specialize (comparison ops for comparative language, lambda ops for functions)?
- Do type weights differentiate by content type?

### When dispatch shows specialization — wire kernel execution
Connect actual kernel execution: dispatch weights → op selection → kernel_eval →
result fed back into residual stream. This is the sieve pipeline.

## Key files

| File | Purpose |
|------|---------|
| `scripts/v10/model.py` | Tree of VSMs: VSM-Compressor + VSM-Dispatcher |
| `scripts/v10/kernel_dispatch.py` | KernelDispatch (22 ops) + KernelIntegrate (5 types) |
| `scripts/v10/kernel.py` | 22-op exact kernel, pre-wired, proven 100% in v9 |
| `scripts/v10/attention.py` | StrideStack (9 strides, O(L×W), spiral bias) |
| `scripts/v10/components.py` | S4, S3, MetaS4, MetaS3 (registers, fixed init) |
| `scripts/v10/config.py` | V10Config — Qwen3, 9 strides, base_pct=0.0005 |
| `scripts/v10/data.py` | ShardedDataLoader for Qwen3 Dolma shards |
| `scripts/v10/train.py` | Relational loss, split grad norm, Adam decay on accept |
| `scripts/v10/ternary.py` | TernaryLinear, evolution, gradient-informed mutation |
| `scripts/v10/probe.py` | Diagnostics: φ-compression, S3 gates, kernel dispatch |

## Why the descending arm works now

Sessions 045/054/055/062/065 proved: descending arm with compression ops
(TernaryFFN) → passthrough, regardless of weight sharing. Root cause: the
operation TYPE was wrong, not the weights. Compression ops can only compress
or pass through. Kernel dispatch ops have 22 structured targets to route
toward — the ternary topology has a real job to do.

## The mistake that cost two sessions

Session 064 ("rebuild as prose LM") discarded the kernel-wired architecture
(2b263d6, smoke-tested to 65% op accuracy) and replaced it with a v6 copy.
The lesson: **shapes not outputs**. The architecture must have the right shape
for the behavior to emerge. Chasing LM loss metrics with the wrong architecture
produces nothing useful regardless of training duration.

## Session history

→ See [session-history-049-062](knowledge/explore/session-history-049-062.md)
→ Session 063: pruned state.md, extracted history to knowledge pages
→ Session 064: WRONG — replaced kernel architecture with v6 LM copy
→ Session 065: probed 20K wasted run, diagnosed shared weights (missed real cause)
→ Session 066: found original v10 in git, diagnosed real cause, rebuilt correctly
