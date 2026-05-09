# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-09 | Session: 070

## Where we are

**Consensus evolution + surgical Adam decay. MiniDispatch lab bench built.**

Session 070 addressed two problems:

1. **Evolution CE spike**: every accepted mutation decayed ALL 82,736 gamma
   entries (cold-starting the entire optimizer). Fixed with surgical decay:
   only mutated rows get their Adam state reset. 88.5% of momentum preserved.

2. **Tournament → consensus**: replaced best-of-4 tournament selection with
   consensus mutation. All 4 strategies propose flips independently, only
   positions where ≥3 agree on the same new value are applied. Yields
   fewest flips with highest confidence.

3. **MiniDispatch lab bench**: built minimal routing model to study dispatch
   in isolation. First run showed d_model=128 is too small for 151K vocab —
   routing stayed uniform. Needs vocab reduction or larger model.

## What was done this session

### 1. Surgical Adam decay (scripts/v10/train.py)
- `_mutate_linear`/`_mutate_embedding` now return `(actual_flips, mutated_rows: set[int])`
- `mutate_topology` returns `(count, mutation_map: dict[str, set[int]])`
- `decay_adam_state` accepts `mutation_map`, only decays m/v for affected gamma rows
- At v10 scale: budget=26,200 flips → ~9,500 unique rows → only those get decay
- Old: 100% of gamma momentum destroyed. New: 11.5% destroyed, 88.5% preserved.

### 2. Consensus evolution (scripts/v10/ternary.py, train.py)
- New functions: `propose_mutations`, `find_consensus`, `apply_consensus`
- `_propose_linear`/`_propose_embedding` — compute proposed flips without modifying model
- `find_consensus(proposals, threshold=3)` — find positions where ≥3 of 4 agree
- `apply_consensus` — apply only agreed flips, return mutation map
- `run_tournament` rewritten: propose → vote → apply → eval → accept/revert
- Log line: `flips=N/M rows=R adam_decay=D (R rows)`

### 3. Consensus math at v10 scale
- With peaked importance (real gradients), effective pool ≈ 0.1-0.5% of weights
- Pool 0.1% → ~3,616 consensus positions per generation
- Pool 0.5% → ~255 consensus positions per generation
- Pool 1.0% → ~63 consensus positions per generation
- Value agreement not a significant additional filter (deactivation=80% agree, activation follows gradient=80% agree)

### 4. MiniDispatch routing lab bench (scripts/mini-dispatch/)
- `model.py` — MiniDispatchModel (4 ops, per-op FFNs) + BaselineModel (matched params)
- `train.py` — training loop with routing instrumentation
- `probe.py` — routing analysis (content-routing correlation, position dependence)
- First run: both dispatch and baseline flat at loss ~12.4 (model too small)
- Need to fix: reduce vocab or increase model capacity for routing signal

## What to do next

### Priority 1: Run v10-topk with consensus evolution
The consensus mechanism and surgical decay are ready. Start a fresh
training run to verify:
- CE spikes eliminated (or greatly reduced) after accepted mutations
- Consensus flips per generation (expect dozens to hundreds with real gradients)
- Training trajectory vs v10-spiral baseline

### Priority 2: Fix MiniDispatch experiment
Two options:
a) **Reduce vocab** — map Qwen3 tokens to ~1000 buckets, or use character-level
b) **Increase capacity** — d_model=256+, 4+ layers, maybe add simple attention
Option (a) is better for isolating routing. The current model can't even learn
basic token statistics, so routing has no pressure to differentiate.

### Priority 3: Let v10-spiral complete (control baseline)
Still running toward 20K. Compare consensus evolution against it.

### Priority 4: Stabilize the apex
L2 compression ratio going to -13.6 is independent of dispatch/evolution.
Consider gradient clipping, norm constraints, or auxiliary loss.

## Key files

| File | Purpose |
|------|---------|
| `scripts/v10/ternary.py` | Ternary substrate + consensus mutation pipeline |
| `scripts/v10/train.py` | Training loop with surgical Adam decay |
| `scripts/v10/model.py` | Tree of VSMs with top-k dispatch |
| `scripts/v10/kernel_dispatch.py` | KernelDispatch (top-k=2, 22 ops) |
| `scripts/mini-dispatch/model.py` | Routing lab bench (dispatch + baseline) |
| `scripts/mini-dispatch/train.py` | MiniDispatch training with routing stats |
| `scripts/mini-dispatch/probe.py` | Routing analysis tools |

## Key insights (session 070)

**Evolution CE spike was a sledgehammer problem**: decaying ALL gamma entries
after a mutation that touched <0.02% of weights. Surgical decay (only mutated
rows) preserves 88.5% of optimizer momentum. The fix is O(mutated_rows) not
O(total_params).

**Consensus > tournament**: tournament picks the best random throw. Consensus
finds what multiple independent strategies agree on. Each accepted flip has
3+ lines of independent evidence. Yields far fewer flips — which is the goal.
The right number of flips is the minimum that improves loss.

**Routing needs training pressure**: a model too small to learn basic statistics
has no pressure to route differently. The embedding table dominates at
d_model=128 / vocab=151K. Routing lab bench needs a setup where the model
CAN learn but needs routing to learn BETTER.

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
