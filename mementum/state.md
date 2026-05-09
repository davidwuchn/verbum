# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-09 | Session: 071

## Where we are

**Dispatch analysis reveals type-dispatch decoupling. Kernel computation pathway added.**

Session 071 analyzed the v10-topk run (12 checkpoints, 1K-12K steps, saved to
checkpoints/v10-consensus) and discovered three major findings:

1. **Dispatch is not dispatch** — the 22 "kernel ops" are just embedding vectors
   that bias a single shared FFN. There's no actual computation happening. LE, DIV,
   PARTIAL etc. are names for learned modulation directions, not operations.

2. **Type and dispatch are completely decoupled** — 163K-position probe showed FN
   type dominates at 56% regardless of which op is active. LE dispatches 59% but
   BOOL type is only 2.4%. Only 5/20 ops match their expected output type.

3. **The model DOES differentiate structured from prose** — dispatch divergence
   L1=0.905, type divergence L1=1.146. Structured data gets FN_COMP=65% type
   (vs FN=57% for prose). Different token categories get different dispatch.
   But dispatch doesn't match the right ops (arithmetic tokens → GE, not ADD).

## What was done this session

### 1. v10-topk checkpoint analysis (12 checkpoints)
- Loss trajectory: 8.06 → 7.56 over 12K steps (best: 7.561 at step 11K)
- Dispatch regime change at step 7K: NOT(41%) → LE(59%)
- Evolution dead: 2/240 accepted (0.8%), consensus threshold too strict
- Named ops mapped: LE=comparison, DIV=arithmetic, PARTIAL=lambda, etc.

### 2. Per-position dispatch probe (probe_dispatch.py)
- LE is top-1 at 84% of positions with avg weight 0.706
- The real routing decision is the runner-up slot (which 2nd op pairs with LE)
- Top pair: DIV × LE (32%), then LE × PARTIAL (19%), LE × NOT (9%)
- Co-occurrence matrix shows structured family pairing

### 3. Structured vs prose probe (probe_kernel_use.py)
- Structured data dispatches very differently from prose (L1=0.905)
- Per-category: arithmetic tokens → GE+LT (not ADD/MUL)
- Lambda tokens → GE+LE+DIV (not PARTIAL/APPLY)
- The kernel functions from kernel.py were never wired in

### 4. Descending arm phase reorder: dispatch→stride→integrate
- Changed from dispatch→integrate→stride
- Rationale: integrate (typing) needs spatial context from stride to see
  how neighbors were dispatched, preventing type-dispatch decoupling
- Both forward paths updated, validated with 100-step test run

### 5. KernelIntegrate: dual pathway with exact computation (NEW)
- Added kernel computation pathway alongside existing FFN
- Operand extraction: two TernaryLinear projections → argmax → (arg1, arg2)
- Op selection: reads dispatch_weights from KernelDispatch (argmax → op code)
- Exact kernel: computes all 22 ops vectorized, selects by op code
- Result encoding: integer result → d_model via learned embedding (1024 buckets)
- Compute gate: learned sigmoid gate per position, initialized at ~0
  - gate=0: pure FFN (backward-compatible, all prose)
  - gate=1: pure kernel (exact computation for structured data)
- Gradient: flows through result embedding + gate (kernel is non-differentiable)
- Params: 435K → 960K trainable. Throughput unchanged.

## What to do next

### Priority 1: Launch v10-topk 20K run with new architecture
```bash
uv run python scripts/v10/train.py \
    --total-steps 20000 --mix-ratio 0.1 \
    --checkpoint-dir checkpoints/v10-topk --seq-len 4096
```
Key signals to watch:
- Compute gate: does it open? mean, max, active(>0.5) fraction
- Does type distribution start tracking dispatch (BOOL should grow if LE dominates)
- Phase order effect: does the new dispatch→stride→integrate improve type coherence
- Loss trajectory vs v10-consensus baseline

### Priority 2: Monitor compute gate activation
The gate starts at ~0 (sigmoid(-5)). For the kernel pathway to matter:
- The operand extraction projections must learn to extract meaningful values
- The result embedding must learn to encode results in useful directions
- The gate must learn to open when exact computation would improve loss
This will only happen on the 10% structured data where computation matters.
If gate stays at 0 after 5K steps, may need auxiliary loss.

### Priority 3: Re-run dispatch probe after training
After the new architecture trains, re-run probe_dispatch.py and
probe_kernel_use.py to see if:
- Type-dispatch coupling improved (phase reorder effect)
- Kernel pathway is active on structured data
- Dispatch correlates better with actual operations

### Priority 4: Auxiliary loss for kernel pathway (if gate doesn't open)
If the compute gate stays near 0, consider:
- Supervised kernel loss on structured data (force op extraction)
- Warm-start the gate higher on structured data positions
- Increase structured mix ratio temporarily

## Key files

| File | Purpose |
|------|---------|
| `scripts/v10/kernel_dispatch.py` | KernelDispatch (top-k routing) + KernelIntegrate (dual pathway) |
| `scripts/v10/kernel.py` | Ground-truth kernel evaluator (22 ops, 5 types, tree eval) |
| `scripts/v10/model.py` | Tree of VSMs, phase order: dispatch→stride→integrate |
| `scripts/v10/train.py` | Training loop with compute gate monitoring |
| `scripts/v10/probe_dispatch.py` | Per-position top-2 co-occurrence analysis |
| `scripts/v10/probe_kernel_use.py` | Structured vs prose dispatch comparison |
| `scripts/v10/ternary.py` | Ternary substrate + consensus mutation pipeline |

## Key insights (session 071)

**The ops were never ops**: KernelDispatch doesn't dispatch to different computations,
it just adds different embedding vectors to a shared FFN. KernelIntegrate didn't
integrate or type, it added type embedding vectors to another shared FFN. Both were
just soft modulation — the model reinterpreted the structured initialization into
22 useful bias directions, but couldn't use them for computation.

**But the model knows the difference**: structured data gets completely different
dispatch and type patterns than prose (L1 > 0.9). The signal is there, the
computational pathway wasn't.

**The kernel was always available**: kernel.py has exact evaluation for all 22 ops,
proven in v9. The gap was wiring it into the model's forward pass with proper
gradient flow (straight-through via result embedding and compute gate).

## Session history

→ See [session-history-049-062](knowledge/explore/session-history-049-062.md)
→ Session 063: pruned state.md, extracted history to knowledge pages
→ Session 064: WRONG — replaced kernel architecture with v6 LM copy
→ Session 065: probed 20K wasted run, diagnosed shared weights (missed real cause)
→ Session 066: found original v10 in git, diagnosed real cause, rebuilt correctly
→ Session 067: analyzed 20K run, phase reorder + mixed data, 5K test launched
→ Session 068: attention spiral discovery, descending arm fine→coarse, evolution fix
→ Session 069: probed v10-spiral, diagnosed dispatch gradient death, top-k MoE routing fix
→ Session 070: consensus evolution, surgical Adam decay, mini-dispatch lab bench
→ Session 071: dispatch analysis, type-dispatch decoupling, kernel computation pathway
