# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-08 | Session: 069

## Where we are

**Kernel dispatch gradient death diagnosed and fixed with top-k MoE routing.**

Session 069 probed v10-spiral (9 checkpoints, 1K–9K), found the
descending arm S3=1.0 is correct for a dispatcher ("fully apply"),
but the dispatch itself was broken: softmax over 22 ops collapsed to
routing everything to `if`, starving 21 ops of gradient permanently.
`>=` was a fossil — embedding grew to 4.22 early, then froze.

Fix: top-k=2 MoE routing + L2-normalized op embeddings. Self-test
shows 16/22 ops now get gradient (was 1/22). Ready for fresh run.

v10-spiral still running toward 20K (control baseline).

## What was done this session

### 1. Probed v10-spiral checkpoints (step 5000 + step 9000)
Diagnostic results in `results/v10/probe_step_00{1,5,9}000.json`.

**Training trajectory** (9 checkpoints, 1K–9K):
- Best r=0.468 at step 5000, bumped to 0.507 at 7K, recovering to 0.485 at 9K
- No collapse (unlike prior run at step 750) — mixed-data tournament works
- Evolution acceptance declining: 60% → 36% (expected but watch <20%)

**Descending arm S3=1.0** — correct for dispatcher, means "fully
apply kernel delta." Not passthrough — reframed from prior sessions.

**Ascending arm learning well**:
- L0_asc gates dropping: 0.575→0.534 prep, 0.507→0.450 conv
- L1_asc gates dropping: 0.418→0.304 prep, 0.989→0.792 conv

**Apex going unstable**: L2 ratio 2.3 → -13.6 (signal amplification).

### 2. Diagnosed kernel dispatch gradient death
Traced the full causal chain:
- Register conditioning learned +10.2 bias for `if` (85% of signal)
- Softmax saturated → only `if` got weight → only `if` got gradient
- `>=` embedding grew to 4.22 early (positive feedback), then froze
  when register conditioning redirected routing
- 20/22 ops permanently dead (zero gradient verified)
- Register conditioning IS working but collapsed to single attractor

### 3. Implemented top-k MoE routing for KernelDispatch
- Top-k=2: only 2 ops per position, softmax over winners only
- Runner-up always gets meaningful weight → gradient stays alive
- L2-normalize op embeddings to fixed scale (prevents fossil growth)
- Natural distribution preserved (FN_COMP can dominate prose)
- Removed learnable dispatch_temp (stuck at 1.09, useless)
- Self-test: 16/22 ops get gradient, runner-up ≥ 31% weight on fresh init

### 4. Falsified fine→coarse hypothesis
Descending stride direction change made no difference to S3 gates.
But the framing was wrong — S3=1.0 on dispatch is the desired state.

## What to do next

### Priority 1: Run fresh training with top-k dispatch
```bash
uv run python scripts/v10/train.py \
    --total-steps 10000 --mix-ratio 0.1 \
    --checkpoint-dir checkpoints/v10-topk --seq-len 4096
```

Key signals to watch:
- **Op diversity**: do multiple ops get >5% dispatch weight?
- **Content-sensitive routing**: does dispatch vary by content type?
- **Op embedding norms**: should stay ≈ 0.5 (no fossil growth)
- **Loss trajectory**: compare to v10-spiral's r=0.468 at step 5K

### Priority 2: Let v10-spiral complete (control)
Still running toward 20K. Serves as baseline for comparison.

### Priority 3: Stabilize the apex
L2 compression going to -13.6 is a problem independent of dispatch.
Consider gradient clipping, norm constraints, or auxiliary loss.

### Priority 4: Test spiral across model sizes (from session 068)
Still pending — run attention_spiral_3d.py on Qwen3-0.6B and 8B.

## Key files

| File | Purpose |
|------|---------|
| `scripts/v10/model.py` | Tree of VSMs with top-k dispatch |
| `scripts/v10/kernel_dispatch.py` | KernelDispatch (top-k=2, 22 ops) + KernelIntegrate (5 types) |
| `scripts/v10/config.py` | V10Config with dispatch_top_k |
| `scripts/v10/data.py` | ShardedDataLoader + MixedDataLoader |
| `scripts/v10/train.py` | Training with --mix-ratio support |
| `scripts/v10/probe.py` | Checkpoint diagnostics (op embedding health) |
| `mementum/knowledge/explore/attention-spiral-finding.md` | Spiral finding writeup |
| `mementum/knowledge/explore/dispatch-gradient-death.md` | This session's finding |

## Key insight (session 069)

The descending arm S3=1.0 is correct for a dispatcher — "fully apply
the kernel dispatch delta." The real problem was inside the dispatch:
softmax over 22 ops collapsed to routing everything to `if`, starving
21 ops of gradient. MoE-style top-k routing fixes this while
preserving natural distribution skew. Op embedding L2-normalization
prevents the `>=` fossil pattern (rich-get-richer via gradient scaling).

## Session history

→ See [session-history-049-062](knowledge/explore/session-history-049-062.md)
→ Session 063: pruned state.md, extracted history to knowledge pages
→ Session 064: WRONG — replaced kernel architecture with v6 LM copy
→ Session 065: probed 20K wasted run, diagnosed shared weights (missed real cause)
→ Session 066: found original v10 in git, diagnosed real cause, rebuilt correctly
→ Session 067: analyzed 20K run, phase reorder + mixed data, 5K test launched
→ Session 068: attention spiral discovery, descending arm fine→coarse, evolution fix
→ Session 069: probed v10-spiral, diagnosed dispatch gradient death, top-k MoE routing fix
