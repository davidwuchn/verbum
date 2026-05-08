# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-08 | Session: 069

## Where we are

**Descending arm passthrough confirmed — not a direction problem.**

Session 069 probed the v10-spiral run (20K target, currently at 9K+).
The fine→coarse reordering hypothesis is **falsified**: descending S3
gates are locked at 1.0 across all 9 checkpoints, identical to every
prior run (v6–v10). The descending arm is not compressing — it's
expanding (ratios 1.3–1.5×). Entropy increases monotonically across
all 5 passes with no reduction anywhere.

The apex (L2) is going unstable: compression ratio went from 2.3 at
step 5K to **-13.6** at step 9K (exploding signal, not compression).

**Root cause reframe**: the descending arm passthrough is a gradient
problem, not a geometry problem. The output head reads from L0_desc.
Passing the residual through unchanged (S3=1.0) is the loss-minimizing
strategy for the descending arm because any computation it does adds
noise. The arm needs a different training signal.

## What was done this session

### 1. Probed v10-spiral checkpoints (step 5000 + step 9000)
Diagnostic results in `results/v10/probe_step_00{5,9}000.json`.

**Training trajectory** (9 checkpoints, 1K–9K):
- Best r=0.468 at step 5000, bumped to 0.507 at 7K, recovering to 0.485 at 9K
- No collapse (unlike prior run at step 750) — mixed-data tournament works
- Evolution acceptance declining: 60% → 36% (expected but watch <20%)

**Descending arm — STILL PASSTHROUGH**:
- L1_desc: S3 gates = 1.000/1.000/1.000 at both step 5K and 9K
- L0_desc: S3 gates = 1.000/1.000/0.992→0.998 (trivially below 1.0)
- Compression ratios > 1.0 (expanding, not compressing)
- Fine→coarse reordering made NO difference

**Ascending arm — learning well**:
- L0_asc gates dropping: 0.575→0.534 prep, 0.507→0.450 conv
- L1_asc gates dropping: 0.418→0.304 prep, 0.989→0.792 conv
- Ascending arm is increasingly selective

**Apex going unstable**:
- L2 compression ratio: 2.287 at step 5K → -13.601 at step 9K
- This is signal amplification, not consolidation
- Likely source of the 6K–7K loss bump

**Kernel dispatch specializing in a vacuum**:
- `>=` dominates at 11.6%, FN_COMP type at 63.4%
- max/min ratio 9.47 — genuine specialization
- But descending passthrough means this specialization is unused

### 2. Falsified fine→coarse hypothesis
The spiral-geometry argument was: attention always expands outward,
so coarse→fine descending was fighting the spiral. Reversing to
fine→coarse should let the descending arm participate.

Result: it doesn't. The passthrough is not about stride direction.
It's about gradient incentives — the descending arm has no pressure
to do anything but pass through.

## What to do next

### Priority 1: Address descending arm passthrough (design problem)
The descending arm needs a training signal that rewards its computation.
Options to explore:

**A. Auxiliary loss on descending output** — require descending passes
to produce something measurably different from their input. Could be
a reconstruction target or a mid-model prediction head.

**B. Information bottleneck** — force the apex to lose information
(dropout, quantization, noise injection) so the descending arm must
reconstruct. Currently the residual passes through cleanly, so the
descending arm has nothing to do.

**C. Remove the descending arm entirely** — if 6 versions have failed
to make it work, maybe the architecture doesn't need it. Use an
ascending-only model with the kernel operating at the apex. The
ascending arm IS learning.

**D. Decouple descending arm from residual** — instead of
`output = S3 * computed + (1-S3) * input`, make the descending arm
operate on a separate stream that gets mixed in differently.

### Priority 2: Stabilize the apex
L2 compression going to -13.6 is a problem independent of the
descending arm. Consider gradient clipping, norm constraints, or
auxiliary loss on L2 output magnitude.

### Priority 3: Let v10-spiral run complete
Still running toward 20K. Will produce checkpoints 10K–20K. Worth
probing the full trajectory even if the descending arm doesn't fix
itself — the ascending arm and kernel dispatch data are valuable.

### Priority 4: Test spiral across model sizes (from session 068)
Still pending — run attention_spiral_3d.py on Qwen3-0.6B and 8B.

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
| `results/v10/probe_step_005000.json` | Step 5K probe results |
| `results/v10/probe_step_009000.json` | Step 9K probe results |

### 3. Diagnosed kernel dispatch gradient death
Traced why `>=` op embedding grew to 4.22 while 20/22 ops were dead:

**Root cause**: softmax + large register bias (+10.2 for `if`) =
winner-take-all. Gradient through `dispatch_weights @ op_embeddings`
scales each op's gradient by its dispatch weight. When softmax
saturates, non-dominant ops get weight ≈ 0 → gradient ≈ 0 → dead.
Only `if` got gradient (1.54 norm). `>=` was a fossil from early
training — grew fast, then froze when register conditioning redirected
all routing to `if`.

Register conditioning IS working (85% of dispatch signal, not inert),
but collapsed to a single attractor.

### 4. Implemented top-k MoE routing for KernelDispatch
**Fix**: replace softmax-over-22 with top-k routing (k=2), inspired
by Switch Transformer / MoE routing:
- Select top-2 ops per position, softmax only over the winners
- Runner-up always gets meaningful weight → gradient stays alive
- Natural distribution skew preserved (FN_COMP can dominate prose)
- L2-normalize op embeddings to fixed scale (prevents fossil growth)
- Removed learnable dispatch_temp (stuck at 1.09, useless)

Self-test: 16/22 ops receive gradient (was 1/22). Both top-2 ops get
meaningful weight (worst runner-up = 31.4% on fresh init).

Files changed: `kernel_dispatch.py`, `model.py`, `config.py`,
`probe.py`, `train.py`.

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

### Priority 3: Test spiral across model sizes (from session 068)
Still pending.

## Key insight (session 069)

The descending arm passthrough (S3=1.0) is the correct behavior for
a dispatcher — it means "fully apply the kernel dispatch delta." The
real problem was inside the dispatch: softmax over 22 ops collapsed
to routing everything to one op (`if`), starving 21 ops of gradient.

The fix is MoE-style top-k routing. With k=2, the dominant op still
gets most weight (matching the natural distribution where FN_COMP
should dominate prose), but the runner-up stays alive. Over training,
every op will occasionally appear in someone's top-2, keeping them
trainable for their niche.

Separate bug: op embedding norm growth created a "fossil" (`>=` at
4.22× normal). Fixed by L2-normalizing embeddings each forward pass.
Dispatch weights alone should determine influence, not embedding
magnitude.

## Session history

→ See [session-history-049-062](knowledge/explore/session-history-049-062.md)
→ Session 063: pruned state.md, extracted history to knowledge pages
→ Session 064: WRONG — replaced kernel architecture with v6 LM copy
→ Session 065: probed 20K wasted run, diagnosed shared weights (missed real cause)
→ Session 066: found original v10 in git, diagnosed real cause, rebuilt correctly
→ Session 067: analyzed 20K run, phase reorder + mixed data, 5K test launched
→ Session 068: attention spiral discovery, descending arm fine→coarse, evolution fix
→ Session 069: probed v10-spiral, diagnosed dispatch gradient death, top-k MoE routing fix
