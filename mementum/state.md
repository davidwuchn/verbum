# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-04 | Session: 065

## Where we are

**v10 rebuilt: split ascending/descending weights. Ready to train.**

Session 065 found that the prior v10 training (20K steps) was wasted —
it trained the wrong architecture. The 5-pass bidirectional VSM used
shared weights between ascending and descending arms, but prior sessions
(045, 054, 055, 062) had already established that compression in the
descending direction doesn't work. The descending arm should have had
its own weights from the start.

### What was wrong (prior v10)
- **Shared weights** forced the descending arm to compress — same ops as ascending
- **Descending arm learned passthrough** — S3 gates went to ~1.0 (all open)
- **Meta-S3 dead** — flat 1.0 across all passes, never differentiated
- **Training destabilized at 15K→20K** — 2 late evolution acceptances disrupted equilibrium
- **Ascending arm worked fine** — L0↑ locked on φ (dev 0.04), L1↑ converging (dev 0.10)
- The architecture was a copy of v6 wholesale, ignoring the design decisions from sessions 054-062

### What changed (this session)
1. **Split shared weights** — ascending arm (L0↑, L1↑, L2_apex) has its own
   prep/stride_stack/consolidate/mod_projs/s4. Descending arm (L1↓, L0↓) has
   its OWN set: prep_desc/stride_stack_desc/consolidate_desc/mod_projs_desc/s4_desc.
   Same op types, but free to learn different behavior.
2. **Fixed Meta-S3 init** — added temperature + learned_bias initialized to -2.0
   (sigmoid ≈ 0.12). Gates now start near-closed and must earn their way open.
   Previously started at 1.0 and had no gradient to differentiate.
3. **Updated gradient normalization** — ascending components normalize by 3 (3 passes),
   descending components normalize by 2 (2 passes). Previously all normalized by 5.
4. **Cleared wasted artifacts** — checkpoints/v10/ and results/v10/ removed.

### Architecture (v10 split)

```
tokens (Qwen3 BBPE) → embed + pos_embed → embed_norm
                            │
    ASCENDING ARM (shared weights, 3 passes)
    ├── L0↑: S4 → prep → S3 gate → StrideStack(fwd) → S3 → consolidate → S3
    ├── L1↑: S4 → prep → S3 gate → StrideStack(fwd) → S3 → consolidate → S3
    ├── L2_apex: S4 → prep → S3 → StrideStack(fwd) → S3 → consolidate → S3
    │
    DESCENDING ARM (own weights, 2 passes)
    ├── L1↓: S4_desc → prep_desc → S3 → StrideStack_desc(rev) → S3 → consolidate_desc → S3
    ├── L0↓: S4_desc → prep_desc → S3 → StrideStack_desc(rev) → S3 → consolidate_desc → S3
    │
    ├── Meta-S3 (temperature + bias, near-closed init)
    ├── Meta-S4 (final structural summary)
    └── output_norm → tied embedding → logits → CE loss
```

Params: 23.1M total, 293K trainable, 131M ternary (up from 22.5M/265K/115M).

### Why this matters

The ascending arm compresses and types — this is proven from v6 and confirmed
by the (wasted) training run where L0↑ locked on φ. The descending arm needs
to learn something DIFFERENT: reading the typed representation and routing
toward kernel functions. With shared weights, it was forced to compress.
With its own weights, it's free to learn dispatch.

The kernel (22 ops, 5 types, proven in v9) is not wired in yet — that comes
after the LM baseline shows the descending arm learning differentiated behavior.

## What to do next

### 1. Train v10-split at scale
```bash
uv run python scripts/v10/train.py --seq-len 4096 --total-steps 20000
```
Watch for:
- **Ascending arm**: should reproduce prior results (L0↑ → φ, S3 differentiating)
- **Descending arm**: with own weights, does it learn different behavior?
  Do its S3 gates differ from ascending? Does it compress or do something else?
- **Meta-S3**: with bias init, does it differentiate passes? Key signal.
- **Content spread**: should converge toward independence as before
- Probe at 1K, 5K, 10K, 15K, 20K checkpoints

### 2. Analyze descending arm behavior
After training, the key question: what did the descending arm learn?
If it learns something different from compression, that's the signal
to wire in the kernel as a gravitational attractor.

### 3. Wire kernel integration (when descending arm shows differentiation)
The sieve pipeline between ascending output and logits. Reads the typed
representation, routes through ternary topology to kernel function families.

## Key files

| File | Purpose |
|------|---------|
| `scripts/v10/model.py` | V6Compressor with split asc/desc weights |
| `scripts/v10/attention.py` | StrideStack + SingleStrideAttention |
| `scripts/v10/components.py` | S4, S3, MetaS4, MetaS3 (fixed init) |
| `scripts/v10/config.py` | V10Config (Qwen3, 9 strides, v6 params) |
| `scripts/v10/data.py` | ShardedDataLoader for Qwen3 Dolma shards |
| `scripts/v10/train.py` | Training loop (split grad norm: 3 asc, 2 desc) |
| `scripts/v10/ternary.py` | TernaryLinear, TernaryEmbedding, evolution |
| `scripts/v10/kernel.py` | 22-op exact kernel (future sieve target) |
| `scripts/v10/probe.py` | Checkpoint diagnostics (shows asc/desc separately) |

## Session history

→ See [session-history-049-062](knowledge/explore/session-history-049-062.md)
→ Session 063: pruned state.md, extracted history to knowledge pages
→ Session 064: rebuilt v10 as prose LM with v6 compressor + Qwen3 (WRONG: shared weights)
→ Session 065: probed 20K training (ascending worked, descending broken), diagnosed shared-weight
  error, split ascending/descending weights, fixed Meta-S3 init, cleared wasted artifacts
