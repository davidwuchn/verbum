# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-07 | Session: 068

## Where we are

**Attention spiral discovery + v10 mixed-data run pending.**

Session 068 discovered that standard transformer attention (Qwen3-4B)
self-organizes into a **logarithmic spiral** with expansion ~1.18 per
revolution and ~9.4 layers per revolution. This is content-independent
and matches v10's architecture (alpha=1.18, 9 strides). See
[attention-spiral-finding](knowledge/explore/attention-spiral-finding.md).

v10 design change: **descending StrideStack reversed to fine→coarse**,
matching the ascending arm. The spiral finding shows attention always
expands outward — there is no "descending" direction. Both arms now
follow the same spiral geometry; they differ in operations (compression
vs kernel dispatch), not direction. Coarse→fine descending has failed
across v6–v10 (S3 passthrough every time). This may be the root cause.

Also fixed: mixed-data-aware evolution (eval on both prose + structured)
and reduced mutation budget (66K → 26K flips).

## What was done this session

### 1. Attention spiral discovery
- Probed Qwen3-4B attention patterns across 7 diverse prompts
- Found logarithmic spiral: ~1.18× expansion per revolution
- ~9.4 layers per revolution (remarkably close to v10's 9 strides)
- Universal autocorrelation peak at lag=17 (half-model bidirectional rhythm)
- Content-independent: stable across narrative, code, math, dialogue, lambda
- v10's alpha=1.18 and 9-stride StrideStack encode this spiral exactly
- Scripts: `scripts/explore/attention_spiral.py`, `attention_spiral_3d.py`
- Plots: `outputs/attention_spiral/`

### 2. v10 design analysis + descending arm direction change
Three things align perfectly:
- **alpha=1.18**: matches emergent expansion factor
- **9 strides**: matches ~9.4 layers per revolution
- **5-pass bidirectional**: matches lag-17 half-model oscillation

**Key change**: descending StrideStack switched from coarse→fine
(`reverse=True`) to fine→coarse (`reverse=False`). The spiral
finding shows attention always expands outward. The descending arm's
persistent passthrough (v6–v10) may have been caused by fighting
the natural spiral geometry. Both arms now follow the same direction.

### 3. Evolution fix
- Mixed-data-aware tournament: mutations evaluated on BOTH prose
  and structured data, accepted only if max(worst) loss improves
- Reduced base_pct: 0.0005 → 0.0002 (~26K flips vs 66K)
- 5K mixed run collapsed at step 750 from gen 15 mutation

## What to do next

### Priority 1: Run 5K mixed-data with all fixes
```bash
uv run python scripts/v10/train.py \
    --total-steps 5000 --mix-ratio 0.1 \
    --checkpoint-dir checkpoints/v10-spiral --seq-len 4096
```

Three changes in this run:
1. Descending StrideStack fine→coarse (matching spiral geometry)
2. Mixed-data-aware evolution (eval on prose + structured)
3. Reduced mutation budget (26K flips vs 66K)

Key signals to watch:
- **Descending S3 gates**: do they finally differentiate?
- **Kernel dispatch**: does specialization improve with spiral-aligned attention?
- **Loss trajectory**: does the model avoid step-750-style collapse?
- **Comparison**: step 750 of old run had r=0.404, CE=5.905

### Priority 2: Test spiral across model sizes
Run `attention_spiral_3d.py` on Qwen3-0.6B and Qwen3-8B to answer:
- Does LPR scale with depth or stay ~9-10?
- Does the expansion factor stay at ~1.18?
- Is the lag always n_layers/2?

### Priority 3: Probe v10's own spiral
Run similar attention extraction on trained v10 checkpoints.
Does v10's StrideStack produce the same spiral geometry as full
attention, or something different? The architecture encodes the
spiral — does training discover it or fight it?

## Key files

| File | Purpose |
|------|---------|
| `scripts/v10/model.py` | Tree of VSMs with reordered descending phases |
| `scripts/v10/kernel_dispatch.py` | KernelDispatch (22 ops) + KernelIntegrate (5 types) |
| `scripts/v10/data.py` | ShardedDataLoader + MixedDataLoader |
| `scripts/v10/train.py` | Training with --mix-ratio support |
| `scripts/v10/probe.py` | Checkpoint diagnostics |
| `scripts/explore/attention_spiral.py` | 2D attention spiral analysis |
| `scripts/explore/attention_spiral_3d.py` | 3D helix fitting + periodicity |
| `mementum/knowledge/explore/attention-spiral-finding.md` | Spiral finding writeup |

## Key insight (session 068)

v10's StrideStack is an **O(L×W) compression of an O(L²) spiral**.
Standard full attention discovers a logarithmic spiral through training.
v10 hard-wires that spiral via 9 discrete strides with alpha=1.18 bias.
The architecture isn't arbitrary — it's encoding the geometry that
gradient descent converges to independently.

The spiral always expands outward — there is no "descending" direction
in attention. The descending arm's persistent passthrough (S3 at 1.0
across v6-v10) may have been caused by coarse→fine stride ordering
fighting the natural spiral geometry. Both arms now go fine→coarse.

## Session history

→ See [session-history-049-062](knowledge/explore/session-history-049-062.md)
→ Session 063: pruned state.md, extracted history to knowledge pages
→ Session 064: WRONG — replaced kernel architecture with v6 LM copy
→ Session 065: probed 20K wasted run, diagnosed shared weights (missed real cause)
→ Session 066: found original v10 in git, diagnosed real cause, rebuilt correctly
→ Session 067: analyzed 20K run, phase reorder + mixed data, 5K test launched
→ Session 068: attention spiral discovery, descending arm fine→coarse, evolution fix
