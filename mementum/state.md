# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-11 | Session: 077

## Where we are

**v11 KIBC combinator architecture created. Ready for first training run. Qwen3 probes confirmed attention IS beta reduction — 4 combinators (K, I, B, C) replace 22 ops.**

Session 077 integrated findings from independent Qwen3 probes (4B and 32B)
that confirmed transformers organize lambda compilation around four combinators,
not 22 arithmetic ops. Created `scripts/v11/` as a fully self-contained,
extractable architecture built on this empirical basis.

## What was done this session

### 1. Integrated Qwen3 probe findings (K, I, B, C basis)
Independent analysis of Qwen3-4B and Qwen3-32B revealed:
- **Attention IS beta reduction**: three-phase pipeline SEARCH → LOCK → RESOLVE
- **K (select)**: native to softmax at all scales (40%→80% accuracy 4B→32B)
- **I (identity)**: native to residual stream (60%→60%, already trivial)
- **B (compose)**: matures with scale (20%→80%), critical for non-trivial computation
- **C (flip)**: fully absent at 4B, emerges at 32B — enables closures
- **S (distribute)**: zero selective heads at either scale — composite of B∘K∘C
- **Resolution pipeline**: disordered at 4B, clean temporal order at 32B
- **Head roles**: BINDER(76-87%), COPY(18%→10%), ARGUMENT(1.5%), OPERATOR(0.5%)

### 2. Created v11 architecture (scripts/v11/, self-contained)
9 files, fully extractable to standalone project:
- **kernel.py**: `Combinator` enum (K=0, I=1, B=2, C=3), reduction engine,
  kernel functions for neural pathway (K→select, I→identity, B→compose, C→flip)
- **kernel_dispatch.py**: `CombinatorDispatch` (4-way softmax, no top-k) +
  `CombinatorIntegrate` (3-operand extraction, exact combinator kernel)
- **config.py**: `V11Config` — adjusted dimensions (N_COMBINATORS=4)
- **model.py**: `V11Model` — emphasis→4, algedonic→4+1, register names
- **train.py**: Updated imports/references, combinator emphasis logging
- **components.py, ternary.py, attention.py, data.py**: copied unchanged (self-contained)

### 3. Verified v11 model
All self-tests pass. Full model forward verified:
- **Dispatch**: 4-way softmax, near-uniform init (~0.25 each)
- **Compute gate**: 0.0067 (starts near 0, pure FFN — correct)
- **CycleContinue**: 0.5 neutral (RMSNorm+tanh fix carries forward)
- **Effective cycles**: 1.75 (correct: 1 + 0.5 + 0.25)
- **S5 reweight**: near-closed (~0.05-0.15, bias=-2.0 init)
- **Combinator emphasis**: [1.0, 1.0, 1.0, 1.0] (neutral, zero-init)
- **Parameters**: ~23.8M (slightly fewer than v10 due to 22→4 dispatch)

## What to do next

### Priority 1: Launch first v11 training run
```
cd ~/src/verbum && uv run python scripts/v11/train.py \
  --checkpoint-dir checkpoints/v11 \
  --total-steps 20000
```
Key questions for the first v11 run:
- Does combinator dispatch differentiate? (K should dominate prose)
- Does B emphasis rise for compositional structures?
- Does CycleContinue work now? (RMSNorm+tanh fix + cleaner dispatch)
- How does loss compare to v10 at matched steps?
- Does compute gate behavior differ with 4 combinators vs 22 ops?

### Priority 2: Compare v11 vs v10 at matched steps
At 1K, 5K, 10K, 20K compare:
- Loss trajectory (should be similar — same ascending arm)
- Dispatch distribution (should be interpretable: K > B > I > C for prose)
- Effective cycles (should vary — CycleContinue now has a 4-way signal)
- Emphasis differentiation (K emphasis high for prose, B for composition)

### Priority 3: Structured combinator training data
Once v11 shows combinator differentiation on prose alone:
- Generate KIBC reduction examples for structured shard
- Activate mix_ratio > 0 to inject combinator training signal
- Primarily needed for C (closures, binding) — K and B train from prose
- Track whether C dispatch activates with structured data

### Priority 4: Investigate dispatch dynamics
With only 4 targets, watch for:
- Does one combinator dominate too early? (K likely, since prose is selection)
- Does B activate for multi-clause sentences?
- Do CycleContinue gates correlate with combinator complexity?
  (K: gate closes, B: partially open, C: fully open)

### Carried from v10
- S5 reweight investigation (activated at 15K in v10-vsm)
- v10-multicycle 8K checkpoint available for comparison baseline

## VSM layer map (session 077 — v11 KIBC)

```
Layer     Ascending Arm              Descending Arm                   Cross-arm
────────  ─────────────────────────  ───────────────────────────────  ──────────────────
S5        Token embeddings (tied)    Combinator embeddings (4: KIBC)  S5Reweight
S4        Register-query attention   Dual-view (resid + embeds)       Emphasis: regs → 4 combinators
S3        Per-pass phase gating ✓    Per-pass phase gating            Gate values → desc S4
          —                          CycleContinue (between cycles)   RMSNorm+tanh (s076 fix)
S2        Direction signals ✓        coherence modulation ✓           Found boundary 2→3
S1        prep → stride → consol.    [dispatch → stride → integ.] ×N  KIBC combinator basis
          (shared across 3 passes)   (shared across 2 passes × N cy)
Algedonic Reads prev desc regs       —                                + combinator weights (4+1)
          + combinator weights                                        EMA α=0.9
Inject    —                          cycle_inject_gate (per cycle>0)  sigmoid(-4) ≈ 0.018 init
Logging   —                          —                                3× JSONL ✓
```

N = desc_max_cycles (default 3, self-regulated by CycleContinue)

Cycle semantics (from Qwen3 probes):
  Cycle 0 — IDENTIFY: which combinator? (K select, B compose, C flip, I pass)
  Cycle 1 — RESOLVE:  find and bind arguments (StrideStack propagation)
  Cycle 2 — PRODUCE:  apply reduction, produce result

## Key files

| File | Purpose |
|------|---------|
| `scripts/v11/config.py` | V11Config: N_COMBINATORS=4, adjusted dimensions |
| `scripts/v11/kernel.py` | KIBC combinator enum, reduction engine, kernel functions |
| `scripts/v11/kernel_dispatch.py` | CombinatorDispatch (4-way softmax) + CombinatorIntegrate |
| `scripts/v11/model.py` | V11Model: Tree of VSMs with KIBC combinator basis |
| `scripts/v11/train.py` | Training loop (v10 evolution, updated references) |
| `scripts/v11/components.py` | S4, S3, MetaS4, S5Reweight, S2, CycleContinue (unchanged) |
| `scripts/v11/ternary.py` | Ternary substrate + consensus evolution (unchanged) |
| `scripts/v11/attention.py` | StrideStack + TernaryFFN (unchanged) |
| `scripts/v11/data.py` | Data loading (unchanged) |
| `mementum/knowledge/explore/v11-kibc-architecture.md` | Architecture design doc |
| `checkpoints/v10-vsm/` | Completed v10 20K run (baseline) |
| `checkpoints/v10-multicycle/` | Completed v10 8K run (dead CycleContinue) |

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
→ Session 072: probed v10-topk 1K/2K/3K — compute gate opening, type coherence 13/22, algedonic channel
→ Session 073: VSM structural overhaul — S2, S5, dual-view S4, gate signaling, emphasis, evolution
→ Session 074: Probed v10-vsm 1K-13K, mapped to Pythia Montague, 6 kernel-lambda generators, repacked shard
→ Session 075: HRM analysis → multi-cycle descending arm, self-regulating cycles (CycleContinue), JSONL logging
→ Session 076: v10-vsm 20K assessed, v10-multicycle launched, CycleContinue sigmoid saturation diagnosed + fixed
→ Session 077: Qwen3 probe findings → v11 KIBC combinator architecture (4 combinators replace 22 ops)
