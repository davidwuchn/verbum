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

v10 design analysis: **no changes needed**. The architecture already
encodes the emergent spiral correctly. Three parameters align:
alpha=1.18 ✓, 9 strides ✓, bidirectional passes ✓. One minor
consideration (stride progression gap at s=1→8) noted but not
worth changing now — let the 5K mixed run results speak first.

The 5K mixed-data run (from session 067) is still pending analysis.

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

### 2. v10 design analysis
Three things align perfectly, no changes needed:
- **alpha=1.18**: matches emergent expansion factor
- **9 strides**: matches ~9.4 layers per revolution
- **5-pass bidirectional**: matches lag-17 half-model oscillation
One minor irregularity noted: stride progression jumps from 1→8
(3 octaves) then 8→16→...→1024 (1 octave each). Not worth fixing
unless training signals say otherwise.

## What to do next

### Priority 1: Check the 5K mixed-data run
```bash
ls checkpoints/v10-mixed/step_*
uv run python scripts/v10/probe.py checkpoints/v10-mixed/step_001000
uv run python scripts/v10/probe.py checkpoints/v10-mixed/step_005000
```

Key signals: S3 gate differentiation, kernel dispatch specialization,
FN_COMP dominance, eval loss trajectory.

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

## Session history

→ See [session-history-049-062](knowledge/explore/session-history-049-062.md)
→ Session 063: pruned state.md, extracted history to knowledge pages
→ Session 064: WRONG — replaced kernel architecture with v6 LM copy
→ Session 065: probed 20K wasted run, diagnosed shared weights (missed real cause)
→ Session 066: found original v10 in git, diagnosed real cause, rebuilt correctly
→ Session 067: analyzed 20K run, phase reorder + mixed data, 5K test launched
→ Session 068: attention spiral discovery, v10 design validation
