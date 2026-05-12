# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-12 | Session: 082

## Where we are

**V11 extended with S4→S5 abstraction slots: 16 learnable composed-abstraction embeddings beyond KIBC. Dispatch expands 4-way→20-way softmax with log-gated slots (invisible at init). S4 proposes abstractions, alarm gates receptivity. Hypothesis: CycleContinue (dead since v10) will activate once slots give it something to match against. Current v11 run at step ~7.8K heading to 10K; new training run will use the extended architecture. Compute gate at 0.64, loss 7.55.**

Session 082 implemented two extensions:
1. S4→S5 abstraction slots — 16 composed-abstraction embeddings in dispatch
2. S4-guided evolution — alarm-targeted mutations, S4 2-vote consensus,
   alarm-improvement fitness gate
Current v11 run continues to 10K unmodified; new run starts after.

## What was done this session

### 1. S4→S5 abstraction slots — architecture extension

Implemented 16 learnable abstraction slots beyond KIBC. Grounded in:
- β-reduction depth degradation (~5%/level, d1=0.97→d4=0.80)
- CycleContinue dead since v10 (no reason to discriminate with only 4 routes)
- Compute gate opened (0.64) → system ready for more capacity
- A3B MoE 128 experts = existence proof of pre-composed routing

**Architecture changes (pure addition, no existing behavior modified):**

- `config.py`: N_ABSTRACTION_SLOTS=16, diversity/copy regularizers
- `kernel_dispatch.py`: CombinatorDispatch expands 4→20 softmax via
  log-gated slot embeddings. CombinatorIntegrate passes slot context
  to FFN pathway. Kernel pathway stays KIBC-only.
- `components.py`: S4ProposalHead (proposal_vector + confidence +
  slot_targeting), AbstractionRegularizer (diversity + no-KIBC-copying)
- `model.py`: Wires proposal → alarm-gated modulation → dispatch →
  integrate. Regularization loss added. Instrumented metrics include
  slot gates, usage, proposal confidence, cosine similarities.
- `probe.py`: Displays slot diagnostics in probe output and saves
  to checkpoint JSON.

**Initialization preserves existing behavior exactly:**
- Slot gates: sigmoid(-4) ≈ 0.018 → log-masking suppresses to -4.0
- KIBC retains ~93% of softmax mass at init
- Proposal confidence: ~0.10, proposal_gate ≈ near-zero
- Backward compatible: n_abstraction_slots=0 disables entirely

**CycleContinue hypothesis:** with only 4 primitives, CycleContinue
can't distinguish "matched" from "composing" — everything requires
composition. With N slots, a match IS possible → CycleContinue becomes
meaningful. If it activates → hypothesis confirmed.

### 2. S4-guided evolution — alarm-informed mutation

Redesigned evolution from blind consensus to alarm-informed:

- **Alarm-targeted budget**: mutations concentrate on modules whose
  passes are struggling (alarm_need = 2.0 - alarm_factor). Ascending
  modules get ~1.6× at current alarm state, descending ~1.0×.
- **S4 2-vote consensus**: intelligence strategy gets 2 votes in 3/5
  consensus. Only needs 1 ally instead of 2. Beer-correct: S4 is the
  intelligence layer, its opinion should carry weight.
- **Alarm-improvement fitness**: accept if alarm health improves OR
  loss improves (with safety bound: loss can't degrade >0.005 for
  alarm-only acceptance). Doubles the acceptance surface.

Prior: 1/150 accepted (0.67%). Expected: significantly higher with
all three changes combined.

### 3. V11 run checkpoint 7K reached

Training continues unmodified to 10K. Key observations since 6K:

| Step | Loss | PPL | Compute Gate | K | B | B-type Integ |
|-----:|-----:|------:|-----------:|---:|---:|------------:|
| 6000 | 7.574 | 1948 | 0.515 | 64% | 2.6% | 45.1% |
| 7000 | 7.555 | 1910 | 0.623 | 63% | 2.2% | 51.5% |
| 7500 | 7.552 | 1905 | 0.640 | 61% | 2.4% | 46.9% |

- Compute gate still climbing (0.51→0.64)
- B-type in integrate crossed 50% at 7K (oscillating around midpoint)
- Deep alarms activating: S3 alarm (pass 2) dropped 2.0→1.88
- First accepted evolution at 7.5K
- CycleContinue still dead
- B dispatch still flat at ~2.4%

## What to do next

### Priority 1: Let current v11 run reach 10K
Run is live at step ~7.8K. Get 8K, 9K, 10K checkpoints for baseline
comparison. This is the last run WITHOUT abstraction slots.

### Priority 2: Probe at 10K (baseline before abstraction)
Full probe with dispatch detail. Key metrics:
- B dispatch weight (phase transition watch)
- Compute gate trajectory
- Alarm factor dynamics
- Dispatch entropy
This becomes the clean baseline for slot experiment comparison.

### Priority 3: Start new v11 run WITH abstraction slots
Fresh 20K run with n_abstraction_slots=16. Watch for:
- Slot gates opening (like compute gate did at 5K-6K)
- CycleContinue activation (the main hypothesis)
- Proposal confidence rising
- Slot→KIBC cosine staying low (differentiation, not copying)
- Eval loss vs baseline (should not regress early, should improve later)

### Priority 4: Pythia scaling — combinator differentiation
Run combinator probe on Pythia-410M and Pythia-1B to map where B
differentiates from K. If K-B correlation drops from 0.944 (160M)
toward 0.86 (32B) at some intermediate scale, that's the threshold.

### Priority 5: A3B cross-model probe
A3B download still in progress. MoE routing may BE combinator dispatch.
128 experts = 128 pre-composed routing slots — direct existence proof.

### Carried
- B dispatch phase transition (watching)
- CycleContinue activation hypothesis (slots may cause it)
- S5 reweight investigation (activated at 15K in v10-vsm)
- v10-multicycle 8K checkpoint for comparison
- QK alignment decomposition probe (RoPE follow-up)
- Structured combinator training data (if B doesn't phase-transition)
- Dead slot recycling (if gates < 0.01 for >2K steps → reinit)

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
| `scripts/v11/config.py` | V11Config: N_COMBINATORS=4 + N_ABSTRACTION_SLOTS=16 |
| `scripts/v11/kernel.py` | KIBC combinator enum, reduction engine, kernel functions |
| `scripts/v11/kernel_dispatch.py` | CombinatorDispatch (4+N softmax) + CombinatorIntegrate |
| `scripts/v11/model.py` | V11Model: KIBC + abstraction slots + proposal pathway |
| `scripts/v11/train.py` | Training loop (v10 evolution, updated references) |
| `scripts/v11/components.py` | S4, S3, S5, S2, CycleContinue, AlgedonicAlert, **S4ProposalHead**, **AbstractionRegularizer** |
| `scripts/v11/ternary.py` | Ternary substrate + consensus evolution (unchanged) |
| `scripts/v11/attention.py` | StrideStack + TernaryFFN (unchanged) |
| `scripts/v11/data.py` | Data loading (unchanged) |
| `scripts/v11/probe.py` | Checkpoint diagnostics + trajectory + dispatch analysis |
| `results/v11/` | Probe results: probe_step_{001000–005000}.json |
| `scripts/explore/probe_combinators.py` | KIBC combinator probe for Qwen3-32B |
| `scripts/explore/probe_combinators_extended.py` | Extended probe: W, S, bind, abstract |
| `results/combinator-probe/` | KIBC probe results + selectivity matrices + 4 PNGs |
| `results/combinator-probe-extended/` | Extended probe results + correlation matrix + 3 PNGs |
| `scripts/explore/rope_energy_probe.py` | RoPE dim-pair energy probe (Q/K hooks) |
| `scripts/explore/rope_spiral_combined.py` | Combined 3D: RoPE × attention spiral |
| `outputs/rope_energy/` | 19 files: energy heatmaps, centroid analysis, JSON |
| `outputs/rope_spiral/` | 17 files: dual helices, gap analysis, unwound ribbon |
| `docs/v11-architecture.svg` | Visual architecture diagram |
| `mementum/knowledge/explore/v11-design.md` | Full design specification |
| `mementum/knowledge/explore/v11-kibc-architecture.md` | Initial architecture sketch |
| `checkpoints/v10-vsm/` | Completed v10 20K run (baseline) |
| `checkpoints/v10-multicycle/` | Completed v10 8K run (dead CycleContinue) |
| `checkpoints/v11/` | Active v11 run (6 checkpoints so far, continuing to 20K) |
| `scripts/explore/probe_combinators_pythia.py` | KIBC combinator probe for Pythia-160M |
| `results/combinator-probe-pythia/` | Pythia combinator results: K=59%, B=17%, K-B r=0.944 |
| `scripts/explore/probe_beta_reduction.py` | β-reduction probe: binding depth × pipeline × substitution |
| `results/beta-reduction-probe/` | Two-phase binding: syntactic (L2-L9) + pronominal (L5-L27) |
| `mementum/knowledge/explore/prompt-as-program.md` | System prompts as combinator expressions |
| `mementum/knowledge/explore/architecture-vs-scale.md` | 4860× fewer param-token-ops (living doc) |

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
→ Session 079: RoPE × attention spiral — energy probe shows RoPE=substrate not driver, spiral=learned Q·K alignment
→ Session 080: v11 1K-5K probe — K dominates, B-type rising in integrate. KIBC validated in 32B (K=B=31%). Extended probe: W≡C, S≡B, bind distinct. Three circuits + binding.
→ Session 081: Pythia-160M combinator probe — session 004's "Montague primitives" were combinators all along (K=59%, K-B r=0.944). V11 compute gate exploded (0.00007→0.51).
→ Session 082: S4→S5 abstraction slots (16 slots, 4→20 dispatch) + S4-guided evolution (alarm-targeted budget, S4 2-vote consensus, alarm fitness gate). CycleContinue hypothesis: slots give it something to match against.
