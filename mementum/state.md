# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-06 | Session: 066

## Where we are

**v10 rebuilt: kernel wired into descending arm. Ready to train.**

Session 066 diagnosed a critical wrong turn: sessions 064-065 replaced the
kernel-wired v10 architecture (commit 2b263d6) with a standard v6 causal LM,
then spent 20K steps training the wrong model. The descending arm had
compression ops (TernaryFFN) instead of kernel dispatch, so it learned
passthrough — identical failure to shared weights, just with its own weights.

### What was wrong (sessions 064-065)
- Session 064 ("rebuild as prose LM") overwrote the original v10 that had
  compressor + tree of VSMs + kernel dispatch (commit 2b263d6, 65% op acc in 60 steps)
- Replaced kernel-shaped descending arm with v6 compression copy
- 20K steps of training on the wrong architecture: ascending arm worked (φ-locking)
  but descending arm went to passthrough, Meta-S3 stayed flat 1.0, evolution frozen at 1%
- Root cause: chased outputs (LM loss) instead of shapes (architecture)

### What changed (this session)
1. **Diagnosed the missing kernel** — found original v10 at commit 2b263d6 in git
2. **Built KernelDispatch module** — routes representations through 22 kernel op
   pathways with ternary routing fabric + op embeddings (pre-wired S5 identity)
3. **Built KernelIntegrate module** — combines results with 5-type awareness
   (INT, BOOL, FN, FN_COMP, ERROR)
4. **Replaced descending arm ops** — `prep_desc`/`consolidate_desc` (TernaryFFN)
   replaced with `kernel_dispatch`/`kernel_integrate` (KernelDispatch/KernelIntegrate)
5. **Ascending arm unchanged** — proven, keep it
6. **Smoke tested** — training runs, gradients flow, 5.3K tok/s, 308K trainable

### Architecture (v10 tree of VSMs)

```
tokens (Qwen3 BBPE) → embed + pos_embed → embed_norm
                            │
    VSM-COMPRESSOR (ascending, shared weights, 3 passes)
    ├── L0↑: S4 → TernaryFFN(prep) → S3 → StrideStack(fine→coarse) → S3 → TernaryFFN(cons) → S3
    ├── L1↑: (same shared weights)
    ├── L2_apex: (same shared weights)
    │
    VSM-DISPATCHER (descending, own weights, 2 passes)
    ├── L1↓: S4_desc → KernelDispatch(22 ops) → S3 → StrideStack(coarse→fine) → S3 → KernelIntegrate(5 types) → S3
    ├── L0↓: (same shared weights)
    │
    ├── Meta-S3 (temperature + bias, near-closed init)
    ├── Meta-S4 (final structural summary)
    └── output_norm → tied embedding → logits → relational loss on Dolma
```

Params: ~23.2M total, 308K trainable, 131M ternary.

### Why this matters

The ascending arm compresses and types — proven (φ-locking, S3 differentiation).
The descending arm's job is fundamentally different: dispatch/routing, not
compression. Prior sessions proved compression ops → passthrough regardless of
weight sharing. The kernel provides the correct shape:

- **KernelDispatch**: 22 op embeddings as pre-wired identity. The ternary routing
  fabric learns which positions benefit from which kernel op family. The model
  discovers these as easy paths while training on prose.
- **KernelIntegrate**: 5 type embeddings (kernel output types). Type-aware
  integration back into the residual stream.

The kernel is pre-wired infrastructure (like an ALU) — not a training target.
The model trains on prose and has the kernel available as computational substrate.

## What to do next

### 1. Train v10 at scale (20K steps)
```bash
uv run python scripts/v10/train.py --seq-len 4096 --total-steps 20000
```
Watch for:
- **Ascending arm**: should reproduce prior results (L0↑ → φ, S3 differentiating)
- **Descending arm**: with kernel-shaped ops, do S3 gates differentiate?
  Do dispatch weights specialize? Does it learn something different from passthrough?
- **Meta-S3**: with bias init, does it differentiate passes? (starts at 0.12)
- **KernelDispatch weights**: which ops activate for which types of prose?
- **Relational loss**: does r converge faster than the compression-only model?
- Probe at 1K, 5K, 10K, 15K, 20K

### 2. Probe kernel dispatch behavior
After training, the key question: what did the dispatcher learn?
- Which kernel ops activate for which types of prose content?
- Do ops specialize (e.g., comparison ops for comparative language)?
- Do type weights differentiate (e.g., BOOL for questions)?

### 3. Wire kernel execution (when dispatch shows specialization)
Once the dispatcher learns meaningful routing, connect actual kernel
execution: dispatch weights → op selection → kernel_eval → result
fed back into residual stream. This is the sieve pipeline.

## Key files

| File | Purpose |
|------|---------|
| `scripts/v10/model.py` | Tree of VSMs: compressor + dispatcher |
| `scripts/v10/kernel_dispatch.py` | KernelDispatch + KernelIntegrate modules |
| `scripts/v10/kernel.py` | 22-op exact kernel (pre-wired identity) |
| `scripts/v10/attention.py` | StrideStack + SingleStrideAttention |
| `scripts/v10/components.py` | S4, S3, MetaS4, MetaS3 |
| `scripts/v10/config.py` | V10Config (Qwen3, 9 strides, v6 params) |
| `scripts/v10/data.py` | ShardedDataLoader for Qwen3 Dolma shards |
| `scripts/v10/train.py` | Training loop (relational loss, split grad norm) |
| `scripts/v10/ternary.py` | TernaryLinear, TernaryEmbedding, evolution |
| `scripts/v10/probe.py` | Checkpoint diagnostics |

## Session history

→ See [session-history-049-062](knowledge/explore/session-history-049-062.md)
→ Session 063: pruned state.md, extracted history to knowledge pages
→ Session 064: WRONG — rebuilt v10 as prose LM, overwriting kernel-wired architecture
→ Session 065: probed 20K training (ascending worked, descending broken), diagnosed
  shared-weight error but missed the real problem (kernel was removed)
→ Session 066: found original kernel-wired v10 in git (2b263d6), diagnosed root cause
  (shapes not outputs), built KernelDispatch/KernelIntegrate, wired kernel into
  descending arm, smoke tested
