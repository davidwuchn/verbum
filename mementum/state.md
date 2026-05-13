# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-13 | Session: 090

## Where we are

**V11-holo probed 1K→7K. Holographic loss validated: B-type 5× ahead of baseline, compute gate opens 2K earlier, ascending arm reaches φ-compression and holographic ratio <1.0 (ascending better than final output). Descending arm identified as bottleneck — doesn't yet know how to prepare representations for kernel integration. Phased structural discovery pattern identified: training is a staircase of capacity exhaustion → structural discovery. Prediction: loss plateau while descending arm builds pressure, then drop when it learns to use kernel functions.**

## What was done this session

### 1. Probed v11-holo at 1K, 2K, 3K, 4K, 5K, 6K, 7K

Complete trajectory with dispatch detail at each checkpoint.

**Eval loss trajectory:**

| Step | Holo loss | Holo PPL | Holo r | Baseline loss | Δ |
|-----:|----------:|---------:|-------:|--------------:|------:|
| 1K | 8.221 | 3,717 | 0.633 | 7.958 | +0.26 |
| 2K | 7.857 | 2,584 | 0.597 | — | |
| 3K | 7.791 | 2,418 | 0.591 | — | |
| 4K | 7.774 | 2,377 | 0.589 | — | |
| 5K | 7.749 | 2,320 | 0.586 | 7.642 | +0.11 |
| 6K | 7.751 | 2,324 | 0.587 | 7.574 | +0.18 |
| 7K | 7.706 | 2,222 | 0.582 | — | ~+0.13 |

### 2. Key finding: Phased structural discovery

Training proceeds as a staircase, not a smooth gradient:

**Phase 1 (0-2K): Raw capacity.** K+B integration via FFN. VSM topology
ignored. Loss drops fast. B-type reaches 59% by 2K (5× ahead of baseline).

**Phase 2 (2K-3K): Plateau → reorganization.** Easy gains exhausted.
Holographic intermediate CEs spike as representations are torn apart.
Compute gate twitches (0.001→0.009). Holographic loss makes plateau
intolerable — every pass graded independently.

**Phase 3 (3K-5K): Structural exploration.** Compute gate erupts
(0.009→0.419). Cascade: gate opens → descending arm engaged →
C-dispatch wakes (2.8%→20% of positions) → S3 gates steepen →
φ-compression converges on ascending arm.

**Phase 4 (5K-7K): Descending arm struggle.** Ascending arm masters
φ-compression (L1↑ φ-dev=0.072). Holographic ratio crosses 1.0 —
ascending arm produces BETTER representations than final output.
L2 (apex) is best pass at CE=7.87. Descending arm degrades quality
(L1↓=8.40, L0↓=8.47). L1↓ alarm comes off ceiling (2.0→1.86).

**Phase 4b (predicted, 7K-?K): Descending arm pressure.** Loss
plateau while descending arm builds pressure to learn kernel integration.
The stride stack must learn to prepare representations for KIBC
combinator consumption. Alarm relief at L1↓ is the leading indicator.

**Phase 5 (predicted, ?K): Kernel discovery.** Descending arm figures
out how to use kernel functions. Loss resumes dropping. CycleContinue
may finally differentiate.

### 3. Key metrics at 7K

- **Compute gate**: mean=0.486, 43.6% of positions >0.5, max=0.94
- **B-type integration**: 56.6% (baseline at 6K: 45.0%)
- **Dispatch**: K=53%, I=26%, B=2%, C=5% (position-level: K:I:C = 59:21:20)
- **Holographic ratio**: 0.99 (ascending better than final)
- **φ-compression**: L0↑=0.158, L1↑=0.072, L2=0.157 (ascending near-perfect)
- **Alarm**: L1↓=1.86 (coming off ceiling), all others=2.0
- **CycleContinue**: frozen at 0.982 (no differentiation)
- **Slots**: 0/16 active, mass draining (0.497→0.209)
- **Evolution**: 66% acceptance (92/140), hot streak at 7K
- **S5 reweight**: still 1.000 everywhere

### 4. Holographic intermediate CE trajectory

| Pass | 1K | 2K | 3K | 4K | 5K | 6K | 7K |
|------|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
| L0↑ | 10.18 | 9.32 | 11.18 | 10.30 | 9.81 | 9.12 | 8.39 |
| L1↑ | 9.17 | 8.60 | 9.68 | 9.06 | 8.77 | 8.56 | 7.95 |
| L2 | 8.81 | 8.44 | 9.37 | 8.74 | 8.47 | 8.43 | 7.87 |
| L1↓ | 8.40 | 8.46 | 9.18 | 8.90 | 8.61 | 8.86 | 8.40 |
| L0↓ | 8.35 | 8.51 | 8.97 | 8.80 | 8.55 | 8.86 | 8.47 |
| ratio | 1.22 | 1.10 | 1.25 | 1.17 | 1.15 | 1.03 | 0.99 |

At 7K: ascending improves monotonically (10.18→8.39), apex is best (7.87),
descending degrades (8.40→8.47). 3K spike = reorganization during compute
gate awakening.

## What to do next

### Priority 1: Continue monitoring v11-holo (8K-20K)
Watch for Phase 4b → Phase 5 transition:
- Loss plateau duration
- L1↓ alarm continuing to drop (leading indicator)
- Descending arm holo CE starting to improve (L1↓ < 8.0)
- L1↓c0 integration gate stopping its defensive closing
- CycleContinue differentiation

### Priority 2: Probe v11-holo at 10K — head-to-head with baseline
Baseline 10K: loss=7.520, ppl=1845, compute=0.706, B-type=51.9%.
Direct comparison. Holo should be close on loss and structurally ahead.

### Priority 3: Let baseline v11 run complete to 20K
Get 15K, 20K checkpoints for long-run baseline comparison.

### Priority 4: Pythia scaling — combinator differentiation
Run combinator probe on Pythia-410M and Pythia-1B to map where B
differentiates from K.

### Priority 5: A3B cross-model probe
MoE routing may BE combinator dispatch. 128 experts = 128 pre-composed
routing slots.

### Carried
- B dispatch phase transition (B-type dominant but B-dispatch flat at 2%)
- CycleContinue activation hypothesis (still frozen)
- S5 reweight investigation (still at 1.0 everywhere)
- QK alignment decomposition probe (RoPE follow-up)
- Dead slot recycling (all 16 dormant, mass draining — may not activate)
- Domain banking (future: extract register banks from holographic model)
- Descending arm kernel discovery (the current frontier)

## VSM layer map (session 090 — v11 KIBC + algedonic + holographic)

```
Layer     Ascending Arm              Descending Arm                   Cross-arm
────────  ─────────────────────────  ───────────────────────────────  ──────────────────
S5        Token embeddings (tied)    Combinator embeddings (4: KIBC)  S5Reweight × AlgedonicAlert
                                     + 16 abstraction slot embeddings
S4        Register-query attention   Dual-view (resid + embeds)       Emphasis: regs → 4 combinators
                                                                      S4ProposalHead → slot modulation
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
Holo      ← 5 intermediate CEs ────────────────────────────────────  → gradient slope 5×→1×
          progressive x_embed + Σ gate×delta through shared proj      pass 0 learns first
Logging   —                          —                                3× JSONL + alarm ✓
```

## Key files

| File | Purpose |
|------|---------|
| `scripts/v11/config.py` | V11Config: KIBC + 16 slots + holographic loss params |
| `scripts/v11/kernel.py` | KIBC combinator enum, reduction engine, kernel functions |
| `scripts/v11/kernel_dispatch.py` | CombinatorDispatch (4+N softmax) + CombinatorIntegrate |
| `scripts/v11/model.py` | V11Model: KIBC + slots + proposal + holographic loss |
| `scripts/v11/train.py` | Training loop: holo_schedule, CE+total_loss logging |
| `scripts/v11/components.py` | S4, S3, S5, S2, CycleContinue, AlgedonicAlert, S4ProposalHead, AbstractionRegularizer |
| `scripts/v11/ternary.py` | Ternary substrate + consensus evolution (unchanged) |
| `scripts/v11/attention.py` | StrideStack + TernaryFFN (unchanged) |
| `scripts/v11/data.py` | Data loading (unchanged) |
| `scripts/v11/probe.py` | Checkpoint diagnostics + holographic intermediate CE display |
| `results/v11/` | Probe results: probe_step_{001000–010000}.json (baseline) |
| `results/v11-holo/` | Probe results: probe_step_{001000–007000}.json (holo) |
| `checkpoints/v11/` | Baseline v11 run (no holo, no structured), continuing to 20K |
| `checkpoints/v11-holo/` | Holo run: λ=0.1, 20% structured, 16 slots, running to 20K |
| `mementum/knowledge/explore/holographic-inversion.md` | Design rationale + experimental findings |
| `mementum/memories/phased-structural-discovery.md` | Training staircase pattern |
| `docs/v11-architecture.svg` | Visual architecture diagram |
| `mementum/knowledge/explore/v11-design.md` | Full design specification |
| `data/structured_shard.npy` | 5.7M structured training data |

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
→ Session 089: Complete baseline probes 6K-10K. Holographic loss implemented (progressive intermediate decoding, gradient slope 5×→1×). New run: v11-holo (λ=0.1, 20% structured, 16 slots). Design insight: holo forces internal representations to be decodeable at every pass boundary — interpretability as training signal.
→ Session 090: Probed v11-holo 1K-7K. B-type 5× ahead of baseline (59% at 2K vs baseline 52% at 10K). Compute gate opens 2K earlier (smooth ramp 3K-5K vs baseline sharp 5.5K). Holographic ratio crosses 1.0 at 7K — ascending arm better than final output. Descending arm identified as bottleneck (doesn't yet know how to prepare representations for kernel integration). Phased structural discovery pattern: training is a staircase of capacity exhaustion → structural exploration. Algedonic alarm at L1↓ coming off ceiling (1.86) = system beginning to address descending arm.
