# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-10 | Session: 075

## Where we are

**v10-vsm architecture upgraded: self-regulating multi-cycle descending arm + JSONL instrumentation. Training at step 14K+ with new kernel-lambda data.**

Session 075 studied the HRM (Hierarchical Reasoning Model, Wang et al. 2025)
architecture — a 27M-param recurrent reasoner with nested H/L loops and
adaptive computation time. Mapped its key ideas onto v10's VSM structure and
implemented two changes: multi-cycle descending dispatch (HRM-inspired) and
self-regulating cycle depth (VSM-native). Also added full JSONL metrics
logging to fix the instrumentation data loss problem.

## What was done this session

### 1. Analyzed HRM architecture for v10 applicability
Studied the full HRM codebase (~/src/HRM). Key structural parallel:
- HRM's H_level (slow, abstract planning) = v10's S4 scan (once per pass)
- HRM's L_level (fast, detailed computation) = v10's dispatch→stride→integrate
- HRM's L_cycles (inner loop repeated N times) = v10's new multi-cycle descending arm
- HRM's 1-step gradient trick (no_grad on N-1 iterations) = potential future optimization

Identified 4 transferable ideas ranked by impact:
1. Multi-cycle descending arm (implemented)
2. Additive input injection (implemented as cycle_inject_gate)
3. No-grad pre-passes (deferred — viable for desc_max_cycles > 3)
4. Adaptive compute / S5 halt (implemented as CycleContinue)

### 2. Implemented multi-cycle descending arm
The descending arm's dispatch→stride→integrate now loops up to `desc_max_cycles`
(default 3) per pass, with shared weights across cycles.

Why this helps mechanistically:
- **Cycle 1**: dispatch routes from compressed reps, stride propagates, integrate types
- **Cycle 2+**: dispatch re-routes with spatial context from prior stride — each
  position sees what neighbors dispatched, enabling PARTIAL→APPLY composition
- Addresses the type-dispatch decoupling problem (integrate needed spatial context
  that only exists after dispatch has propagated)

Input injection gate (`cycle_inject_gate`, sigmoid, starts ~0.018) re-grounds each
cycle in the pre-cycle residual — HRM's `z_L += z_H + input` pattern for v10.

### 3. Implemented self-regulating cycle depth (CycleContinue)
Instead of fixed `desc_cycles`, a learned S3 continuation gate decides whether
each subsequent cycle should contribute:

- **CycleContinue** module: reads register state (type/scope/role after S3 updates)
  → Linear → sigmoid → scalar continuation gate
- Cumulative gate product: cycle 0 = full strength, cycle 1 = scaled by gate_0,
  cycle 2 = scaled by gate_0 × gate_1
- All cycles always compute (static graph for MLX), gating controls contribution
- At init: gates = 0.5 (neutral), effective_cycles ≈ 1.75
- The model learns: simple prose → gates close (1 cycle), complex composition → gates open (3 cycles)

VSM mapping: S3 controls within-cycle (phase gating) AND between-cycles (continuation).
This is Beer's S3 doing its job — the system self-regulates computational depth.

New params: 769 (CycleContinue: 768→1 linear + bias). Total: 23,896,417.

### 4. Added JSONL instrumentation logging
Fixed the data loss problem: previously, all instrumentation metrics were
print-only (lost) or single-snapshot in state.json.

Three append-only JSONL files now accumulate in checkpoint_dir:

| File | Frequency | Contents |
|------|-----------|----------|
| `metrics_log.jsonl` | Every eval_interval | Full forward_instrumented: S3 gates, S5 reweight, S2 conflict/scales, register norms, compression ratios, dispatch/type weights, op emphasis, compute gate, cycle_continue_gates, effective_cycles |
| `train_log.jsonl` | Every log_interval | step, r, ce, lr, grad_norm, tok/s |
| `evolution_log.jsonl` | Every generation | accepted/rejected, delta, flips, consensus stats |

All survive resume. NaN/Inf sanitized to null. Ready for `pd.read_json(..., lines=True)`.

## What to do next

### Priority 1: Probe step 16K+ for kernel-lambda response
(Carried from session 074 — still waiting for training to reach 16K)
- `Op 18 (partial)`: 0.66% → should climb with new structured data
- `Op 19 (apply)`: 0.06% → biggest expected change
- Eval loss should NOT spike
- NOW: JSONL logs will capture the full trajectory automatically

### Priority 2: Validate multi-cycle dispatch behavior at training time
First training run with desc_max_cycles=3 should show:
- Do continuation gates differentiate? (Simple content → close, structured → open)
- Does cycle_inject_gate learn to open? (Currently ~0.018)
- Do S3 gates differ between cycles within a pass?
- Do dispatch weight distributions sharpen in cycle 2 vs cycle 1?
- Does effective_cycles vary across eval batches?

### Priority 3: S5 reweight investigation
(Carried from session 074 — still dormant across all 13K steps)
- Fully dormant. Now with JSONL logging, its trajectory will be tracked
  automatically through the metrics_log.

### Priority 4: Let run complete to 20K, then assess
The run is configured for 20K steps. JSONL logs will capture everything.
At 20K: full assessment of both kernel-lambda enrichment AND multi-cycle
dispatch behavior.

### Future: Benchmark desc_max_cycles=1 vs 3
Once the new architecture trains, compare:
- desc_max_cycles=1 (baseline, matches prior behavior)
- desc_max_cycles=3 (self-regulating)
Metrics: eval loss, dispatch weight diversity, type coherence, effective cycles

## VSM layer map (session 075 update)

```
Layer     Ascending Arm              Descending Arm                   Cross-arm
────────  ─────────────────────────  ───────────────────────────────  ──────────────────
S5        Token embeddings (tied)    Op embeddings × emphasis         S5Reweight (DORMANT)
S4        Register-query attention   Dual-view (resid + embeds)       Emphasis: regs → per-op ✓
S3        Per-pass phase gating ✓    Per-pass phase gating            Gate values → desc S4
          —                          CycleContinue (between cycles)   ← NEW session 075
S2        Direction signals ✓        coherence modulation ✓           Found boundary 2→3
S1        prep → stride → consol.    [dispatch → stride → integ.] ×N  ← MULTI-CYCLE s075
          (shared across 3 passes)   (shared across 2 passes × N cy)
Algedonic Reads prev desc regs       —                                + kernel compute
          + kernel compute                                            EMA α=0.9
Inject    —                          cycle_inject_gate (per cycle>0)  ← NEW session 075
Logging   —                          —                                3× JSONL append logs
```

N = desc_max_cycles (default 3, self-regulated by CycleContinue)

## Key files

| File | Purpose |
|------|---------|
| `scripts/v10/components.py` | S4, S3, MetaS4, S5Reweight, S2, **CycleContinue** |
| `scripts/v10/kernel_dispatch.py` | KernelDispatch (top-k + op_emphasis), KernelIntegrate |
| `scripts/v10/model.py` | Tree of VSMs — multi-cycle descending arm, self-regulating |
| `scripts/v10/train.py` | Training loop + JSONL logging (metrics, train, evolution) |
| `scripts/v10/config.py` | Config: desc_max_cycles, cycle inject gate |
| `scripts/v10/kernel.py` | Ground-truth kernel evaluator (22 ops, 5 types) |
| `scripts/v10/ternary.py` | Ternary substrate + consensus mutation pipeline |
| `bb/us/whitford/verbum/bios.clj` | BIOS generator — 6 kernel-lambda generators |
| `scripts/v10/pack_structured.py` | Packs BIOS + compile into tokenized .npy shard |
| `checkpoints/v10-vsm/` | Active training run (step 14K+) |

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
