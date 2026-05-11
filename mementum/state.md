# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-11 | Session: 078

## Where we are

**v11 KIBC combinator architecture complete with Beer's algedonic alert (fire alarm). Ready for first training run. All 48 alarm metrics logged for offline threshold analysis.**

Session 078 added the algedonic alert — Beer's S1→S5 fire alarm bypass —
to the v11 architecture. The alarm monitors 48 operational health metrics
(S3 gate values, dispatch distributions, conflict scores, cycle gates, etc.)
end-to-end differentiable, producing per-pass factors [0,2] that multiply
S5Reweight gates. At init the alarm is silent (factors=1.0). After 3 test
training steps, factors already differentiated to ~1.08-1.14 (pleasure:
amplifying passes that help). 245 parameters added (negligible).

## What was done this session

### 1. Designed and implemented Beer's algedonic alert (fire alarm)

Researched Beer's original VSM algedonic channel from Brain of the Firm (1972):
- Signals between S1 and S3 continuously monitored
- Emergency condition → direct signal to S5, bypassing S4/S3/S2
- S5 "wakes up" and requests corrective action from S3 and S4
- Carries both pain (suppress) and pleasure (amplify)
- Can originate from any part of the system at any level of recursion

### 2. AlgedonicAlert implementation (components.py)

**Separate gate** (not additive bias on S5Reweight):
- Per-pass factor ∈ [0, 2] via `1 + tanh(logit)`
- Factor 1.0 = no alarm (neutral), <1.0 = pain (suppress), >1.0 = pleasure (amplify)
- `effective_gate = s5_reweight_gate × alarm_factor`
- Zero-init: alarm starts silent, learns what matters from loss signal
- 245 parameters: `nn.Linear(48, 5)` — low bandwidth, fast (Beer's design)

### 3. 48 operational health metrics (end-to-end differentiable)

| Metric | Count | Purpose |
|--------|-------|---------|
| S3 gate means per pass | 5 | Are operations being suppressed? |
| S3 gate mins per pass | 5 | Most suppressed phase per pass |
| S2 conflict cosines | 4 | Are passes fighting each other? |
| Dispatch weights (K,I,B,C) | 4 | Has dispatch collapsed to one combinator? |
| Dispatch entropy | 1 | Overall dispatch distribution health |
| Compute gate (mean, active) | 2 | Is kernel pathway opening? |
| CycleContinue gates | 4 | Are cycles self-regulating? |
| Effective cycles | 2 | Actual computational depth |
| Raw delta norms | 5 | How much each pass proposes |
| Gated delta norms | 5 | How much gets through S3 |
| Suppression ratios | 5 | gated/raw — S3 filtering intensity |
| Register bank mean norms | 6 | Are registers diverging? |

All metrics are live (no stop_gradient) — gradients flow back through
the alarm to S1/S3, teaching the whole system to avoid alarm conditions.

### 4. Live caches for end-to-end gradient flow

Added `_dispatch_weights_live` and `_compute_gate_live` to CombinatorDispatch
and CombinatorIntegrate (alongside existing stop_gradient'd probing caches).

### 5. Logging and probing

- **train.py**: Alarm factors displayed in eval (🔕 silent / 🚨 active),
  alarm_metrics + alarm_metrics_named in JSONL for threshold analysis
- **probe.py**: Alarm section in checkpoint diagnostics, trajectory table
  shows alarm when active
- **All 48 metrics logged** for later offline threshold setting from real data

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
- **NEW: Does the algedonic alarm differentiate?** Watch alarm_factors
  in metrics_log.jsonl — early runs should show factors > 1.0 (pleasure,
  amplifying useful passes). Alarm becomes interesting when factors
  diverge per pass (different alarm response for ascending vs descending).

### Priority 2: Analyze alarm metrics for threshold setting
After first training run, analyze the 48 alarm metrics timeseries:
- What are the natural ranges of S3 gate means, dispatch entropy, etc.?
- When does the alarm factor deviate most from 1.0?
- Are there correlations between specific metrics and loss improvement?
- Use this data to set meaningful alarm thresholds in a later session

### Priority 3: Compare v11 vs v10 at matched steps
At 1K, 5K, 10K, 20K compare:
- Loss trajectory (should be similar — same ascending arm)
- Dispatch distribution (should be interpretable: K > B > I > C for prose)
- Effective cycles (should vary — CycleContinue now has a 4-way signal)
- Emphasis differentiation (K emphasis high for prose, B for composition)

### Priority 4: Structured combinator training data
Once v11 shows combinator differentiation on prose alone:
- Generate KIBC reduction examples for structured shard
- Activate mix_ratio > 0 to inject combinator training signal
- Primarily needed for C (closures, binding) — K and B train from prose
- Track whether C dispatch activates with structured data

### Carried from v10
- S5 reweight investigation (activated at 15K in v10-vsm)
- v10-multicycle 8K checkpoint available for comparison baseline

## VSM layer map (session 078 — v11 KIBC + algedonic alert)

```
Layer     Ascending Arm              Descending Arm                   Cross-arm
────────  ─────────────────────────  ───────────────────────────────  ──────────────────
S5        Token embeddings (tied)    Combinator embeddings (4: KIBC)  S5Reweight × AlgedonicAlert
S4        Register-query attention   Dual-view (resid + embeds)       Emphasis: regs → 4 combinators
S3        Per-pass phase gating ✓    Per-pass phase gating            Gate values → desc S4
          —                          CycleContinue (between cycles)   RMSNorm+tanh (s076 fix)
S2        Direction signals ✓        coherence modulation ✓           Found boundary 2→3
S1        prep → stride → consol.    [dispatch → stride → integ.] ×N  KIBC combinator basis
          (shared across 3 passes)   (shared across 2 passes × N cy)
Algedonic Reads prev desc regs       —                                + combinator weights (4+1)
          + combinator weights                                        EMA α=0.9
Alert     ← 48 health metrics ──────────────────────────────────────  → S5 gate modulation
          S3 gates, S2 conflicts, dispatch, compute, cycles,          [0,2] per pass, e2e diff.
          delta norms, suppression ratios, register norms             Beer's fire alarm ✓
Inject    —                          cycle_inject_gate (per cycle>0)  sigmoid(-4) ≈ 0.018 init
Logging   —                          —                                3× JSONL + alarm ✓
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
| `scripts/v11/components.py` | S4, S3, MetaS4, S5Reweight, S2, CycleContinue, **AlgedonicAlert** |
| `scripts/v11/ternary.py` | Ternary substrate + consensus evolution (unchanged) |
| `scripts/v11/attention.py` | StrideStack + TernaryFFN (unchanged) |
| `scripts/v11/data.py` | Data loading (unchanged) |
| `scripts/v11/probe.py` | Checkpoint diagnostics + trajectory + dispatch analysis |
| `docs/v11-architecture.svg` | Visual architecture diagram |
| `mementum/knowledge/explore/v11-design.md` | Full design specification |
| `mementum/knowledge/explore/v11-kibc-architecture.md` | Initial architecture sketch |
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
→ Session 077: Qwen3 probe findings → v11 KIBC combinator architecture + probe + docs (4 combinators replace 22 ops)
→ Session 078: Beer's algedonic alert (fire alarm) — 48 health metrics, separate S5 gate, end-to-end differentiable
