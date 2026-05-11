# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-11 | Session: 076

## Where we are

**v10-vsm completed 20K. v10-multicycle running (8K checkpoint imminent). CycleContinue sigmoid saturation diagnosed and fixed — next run will have working self-regulating cycles.**

Session 076 assessed the completed v10-vsm 20K run, launched the first
multi-cycle training run (v10-multicycle), and diagnosed a critical bug:
CycleContinue's sigmoid gate saturated to 1.0 within the first ~200 steps
and could never learn to close. Fixed with RMSNorm + tanh clamp. The
v10-multicycle run continues to 8K for a final checkpoint before restarting
with the fix.

## What was done this session

### 1. Assessed v10-vsm 20K run (complete)
Full trajectory analysis across all 20 checkpoints:
- **Loss**: 8.04 → 7.37 (best at 15K), slight regression to 7.42 at 20K
- **S5 Reweight activated** for the first time ever: pass 1 dropped from 1.0 → 0.693
  at 20K. The model learned to de-emphasize pass 1. Coincided with loss regression.
- **Compute gate**: opened and saturated by 10K (0.89 at 20K)
- **S3 gates**: beautiful differentiation — pass 0 gating down to [0.33, 0.24, 0.19]
- **Op dispatch** converged: compose(37%), sub(23%), pred(16%), min_max(10%)
- **Partial/apply (ops 18/19)**: flat at <0.3% despite kernel-lambda data enrichment
- **Evolution**: 7/400 accepted (1.75%)

### 2. Launched v10-multicycle training run
First training with multi-cycle descending arm (desc_max_cycles=3):
```
checkpoints/v10-multicycle/   ← running, step 7.5K+ at time of writing
```
JSONL logging confirmed working — all three log files accumulating correctly.
New multi-cycle instrumentation fields verified: `cycle_continue_gates`,
`effective_cycles`, `cycle_inject_gate`, per-cycle S3 gates (9 per desc pass).

### 3. Diagnosed CycleContinue sigmoid saturation
**The bug**: CycleContinue's gate_proj (Linear 768→1 + sigmoid) receives
register input with ||x|| ≈ 27.7. After even small weight updates, logit ≈ 30,
sigmoid(30) gradient ≈ 0. The gate locked at 1.0000 by step ~200 and never
moved — all 15 evals showed effective_cycles = 3.000 for both desc passes.

**Evidence**: gate_proj weight norm = 1.08, input norm ≈ 27.7, max |logit| ≈ 30.

**The fix** (committed, not yet trained):
1. **RMSNorm** on concatenated register input → ||x|| ≈ 1.0
2. **tanh(·) × 4.0** logit clamp → gate ∈ [0.018, 0.982], min gradient 0.018
3. Belt and suspenders: normalization prevents saturation, clamp guarantees it

### 4. v10-multicycle observations at 7.5K
Despite dead CycleContinue, useful signals:
- **Loss tracking identical** to v10-vsm at same steps (7.593 vs 7.598 at 7K)
- **Dispatch collapsed** to 3 ops: sub(61%), min_max(26%), and_or(11%) = 98.3%
  Much more concentrated than v10-vsm's 4-5 op spread
- **Compute gate opening slower**: 0.24 at 7.5K vs 0.80 at 7K in v10-vsm
- **S3 per-cycle gates differentiating**: L1↓ c0 disp=0.62 → c1=0.73 → c2=0.80
  (later cycles open wider) — S3 learned something about cycle structure
- **cycle_inject_gate frozen** at 0.018 (init value) — never moved

## What to do next

### Priority 1: Start fresh v10-multicycle run with CycleContinue fix
After v10-multicycle reaches 8K checkpoint, start a new run:
```
cd ~/src/verbum && uv run python scripts/v10/train.py \
  --checkpoint-dir checkpoints/v10-multicycle2 \
  --total-steps 20000 \
  --mix-ratio 0.1
```
Key questions for the new run:
- Do continuation gates differentiate? (Simple prose → close, structured → open)
- Does effective_cycles vary across eval batches?
- Does the model learn to use fewer cycles for simple content?
- Does dispatch diversity improve with working self-regulation?

### Priority 2: Compare v10-multicycle (dead gates) vs v10-multicycle2 (live gates)
At matched steps (e.g. 5K, 10K), compare:
- Loss trajectory
- Dispatch concentration (3-op collapse vs spread)
- Compute gate opening speed
- S3 per-cycle gate patterns

### Priority 3: Investigate dispatch collapse
v10-multicycle collapsed to 3 ops (98.3%) vs v10-vsm's broader spread.
Hypotheses:
- 3× descending compute with identical routing → model finds one good op faster
- Dead CycleContinue = wasted capacity that could have diversified dispatch
- The fix may resolve this if adaptive cycles free capacity for exploration

### Priority 4: Partial/apply ops still flat
Neither v10-vsm (20K) nor v10-multicycle (7.5K) moved ops 18/19 above noise.
10% mix_ratio may be too low. Consider:
- Higher mix_ratio (20-30%) for a targeted experiment
- Separate structured-only eval to see if partial/apply activate on that data
- Check if the op embeddings for 18/19 are even distinguishable

### Carried: S5 reweight investigation
v10-vsm showed S5 activating at 15K+ (first time). v10-multicycle S5 stable at 1.0
through 7.5K. Track whether new run with working CycleContinue affects S5 activation
timing.

## VSM layer map (session 076 update)

```
Layer     Ascending Arm              Descending Arm                   Cross-arm
────────  ─────────────────────────  ───────────────────────────────  ──────────────────
S5        Token embeddings (tied)    Op embeddings × emphasis         S5Reweight (activated in vsm!)
S4        Register-query attention   Dual-view (resid + embeds)       Emphasis: regs → per-op ✓
S3        Per-pass phase gating ✓    Per-pass phase gating            Gate values → desc S4
          —                          CycleContinue (between cycles)   ← FIXED s076: RMSNorm+tanh
S2        Direction signals ✓        coherence modulation ✓           Found boundary 2→3
S1        prep → stride → consol.    [dispatch → stride → integ.] ×N  ← MULTI-CYCLE s075
          (shared across 3 passes)   (shared across 2 passes × N cy)
Algedonic Reads prev desc regs       —                                + kernel compute
          + kernel compute                                            EMA α=0.9
Inject    —                          cycle_inject_gate (per cycle>0)  ← frozen at init s076
Logging   —                          —                                3× JSONL ✓ verified s076
```

N = desc_max_cycles (default 3, self-regulated by CycleContinue)

## Key files

| File | Purpose |
|------|---------|
| `scripts/v10/components.py` | S4, S3, MetaS4, S5Reweight, S2, **CycleContinue** (fixed s076) |
| `scripts/v10/kernel_dispatch.py` | KernelDispatch (top-k + op_emphasis), KernelIntegrate |
| `scripts/v10/model.py` | Tree of VSMs — multi-cycle descending arm, self-regulating |
| `scripts/v10/train.py` | Training loop + JSONL logging (metrics, train, evolution) |
| `scripts/v10/config.py` | Config: desc_max_cycles, cycle inject gate |
| `scripts/v10/kernel.py` | Ground-truth kernel evaluator (22 ops, 5 types) |
| `scripts/v10/ternary.py` | Ternary substrate + consensus mutation pipeline |
| `bb/us/whitford/verbum/bios.clj` | BIOS generator — 6 kernel-lambda generators |
| `scripts/v10/pack_structured.py` | Packs BIOS + compile into tokenized .npy shard |
| `checkpoints/v10-vsm/` | Completed 20K run (single-cycle) |
| `checkpoints/v10-multicycle/` | Running to 8K (dead CycleContinue) |

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
