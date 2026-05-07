# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-07 | Session: 067

## Where we are

**v10 phase reorder + mixed data training launched.**

Session 067 analyzed the completed v10 20K-step training run, diagnosed
two issues in the descending arm, and applied two architectural changes:

1. **Descending phase reorder**: dispatch → integrate → stride (was
   dispatch → stride → integrate). Typing now sees undiluted dispatch
   signal before spatial mixing.
2. **Mixed data training**: 10% structured (BIOS math + lambda + clojure),
   90% Dolma prose. Gives kernel dispatch 22 ops concrete targets.

A 5K test run is in progress at `checkpoints/v10-mixed`.

## What was done this session

### 1. v10 20K training run analyzed
- Best eval: step 17K (r=0.543, loss=7.31)
- Evolution disruption at 18K-20K: 9 mutations in 3K steps, eval regressed
- **Ascending arm works**: S3 gates differentiate (0.22-0.85), φ-dev=0.06
- **Descending arm passthrough**: S3 gates at 1.0, FN_COMP dominates at 0.62
- Kernel dispatch specializes (+=0.33, neg=0.20) but S3 lets everything through

### 2. Architecture diagram
- `docs/v10-architecture.svg` — full visual of feed-forward + feedback channels

### 3. Phase reorder (commit 103dc7d)
- Descending phases: dispatch → integrate → stride (was dispatch → stride → integrate)
- Rationale: dispatch and typing are local per-position decisions — kept adjacent
  so typing sees undiluted dispatch signal. StrideStack propagates complete
  (op + type) representations across scales.
- The prior ordering let spatial mixing wash out dispatch structure before
  typing, contributing to FN_COMP dominating and S3 → 1.0 passthrough.

### 4. Mixed data (commit 28ee23d)
- `MixedDataLoader` in data.py: per-batch random draw from prose or structured
- `pack_structured.py`: tokenizes BIOS + compile examples into .npy shard
- 60K examples → 1.5M tokens: 35% lambda, 57% s-expr, 8% raw math
- Exercises all 22 kernel ops: arithmetic, comparison, boolean, lambda
- `--mix-ratio 0.1` CLI arg for train.py (default 0.0 for backward compat)

## What to do next

### Monitor 5K mixed-data run
```bash
# Check if training is still running
ls checkpoints/v10-mixed/step_*

# Probe key checkpoints
uv run python scripts/v10/probe.py checkpoints/v10-mixed/step_001000
uv run python scripts/v10/probe.py checkpoints/v10-mixed/step_005000
```

Key signals to watch:
- **Descending S3 gates**: do they differentiate (< 1.0)?
- **Kernel dispatch**: does specialization change pattern?
- **Kernel type weights**: does FN_COMP still dominate, or do types differentiate?
- **Eval loss**: does it improve faster or slower than prose-only?

### If S3 differentiates → run at 20K
```bash
uv run python scripts/v10/train.py \
    --total-steps 20000 --mix-ratio 0.1 \
    --checkpoint-dir checkpoints/v10-mixed-20k --seq-len 4096
```

### If S3 still passthrough → investigate further
- Try higher mix_ratio (0.2, 0.3)
- Try curriculum: pure structured first, then mix
- Consider: does the S3 bias initialization need to be more aggressive?
- Consider: does the descending S4 need separate learning rate?

## Key files

| File | Purpose |
|------|---------|
| `scripts/v10/model.py` | Tree of VSMs with reordered descending phases |
| `scripts/v10/kernel_dispatch.py` | KernelDispatch (22 ops) + KernelIntegrate (5 types) |
| `scripts/v10/data.py` | ShardedDataLoader + MixedDataLoader |
| `scripts/v10/train.py` | Training with --mix-ratio support |
| `scripts/v10/pack_structured.py` | BIOS/lambda → tokenized .npy shard |
| `scripts/v10/probe.py` | Checkpoint diagnostics |
| `docs/v10-architecture.svg` | Architecture diagram |
| `data/structured_shard.npy` | 1.5M tokens of structured training data |

## Key insight

The kernel dispatch has 22 ops (arithmetic, comparison, boolean, lambda)
that map directly to lambda/math operations. With pure prose, these ops
have no clear grounding — dispatch tries to route English words through
`+`, `not`, `apply`. S3 sees uniform deltas and opens to 1.0.

With structured data, the dispatch has crisp targets: `3 + 5 = 8` routes
through `+`, `(not true) → false` routes through `not`, `(comp f g)` routes
through `comp`. S3 has something real to selectively gate.

The two changes are complementary: phase reorder ensures typing sees
undiluted dispatch signal; mixed data ensures there IS a dispatch signal
worth preserving.

## Session history

→ See [session-history-049-062](knowledge/explore/session-history-049-062.md)
→ Session 063: pruned state.md, extracted history to knowledge pages
→ Session 064: WRONG — replaced kernel architecture with v6 LM copy
→ Session 065: probed 20K wasted run, diagnosed shared weights (missed real cause)
→ Session 066: found original v10 in git, diagnosed real cause, rebuilt correctly
→ Session 067: analyzed 20K run, phase reorder + mixed data, 5K test launched
