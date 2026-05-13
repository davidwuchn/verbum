# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-13 | Session: 091

## Where we are

**V11-holo probed 1K→9K. Phase 4 confirmed: loss plateau (7.674→7.675 at 8K-9K) while internal reorganization continues. Compute gate steadily opening (0.486→0.526→0.547), B-type oscillating (56.6%→62.8%→55.7%). Holographic intermediate CEs show reorganization wave at 9K: all passes regressed from 8K best, ratio returned to 0.99. This mirrors the 3K spike pattern — capacity exhaustion → tear apart → rebuild. 8K was a local optimum; 9K is rebuilding. Holo still ~0.12 behind baseline on eval loss but structurally richer. Baseline degrading at 10K (smoothed CE rising). Approaching 10K head-to-head.**

## What was done this session

### 1. Probed v11-holo at 8K and 9K

**Eval loss trajectory (complete):**

| Step | Holo loss | Holo PPL | Holo r | Baseline loss | Δ |
|-----:|----------:|---------:|-------:|--------------:|------:|
| 1K | 8.221 | 3,717 | 0.633 | 7.958 | +0.26 |
| 2K | 7.857 | 2,584 | 0.597 | — | — |
| 3K | 7.791 | 2,418 | 0.591 | — | — |
| 4K | 7.774 | 2,377 | 0.589 | — | — |
| 5K | 7.749 | 2,320 | 0.586 | 7.642 | +0.11 |
| 6K | 7.751 | 2,324 | 0.587 | 7.574 | +0.18 |
| 7K | 7.706 | 2,222 | 0.582 | 7.573 | +0.13 |
| **8K** | **7.674** | **2,152** | **0.579** | **7.543** | **+0.13** |
| **9K** | **7.675** | **2,154** | **0.579** | **7.560** | **+0.12** |

Gap narrowing: +0.26 → +0.12 over 9K steps.

### 2. Holographic reorganization wave at 9K

8K was a local optimum across all holographic passes. 9K regressed
everywhere — same pattern as the 3K spike during compute gate awakening.
Interpretation: the model is tearing apart representations to rebuild
with newly-available compute gate capacity (66%→74% active).

**Holographic intermediate CE trajectory:**

| Pass | 1K | 2K | 3K | 4K | 5K | 6K | 7K | **8K** | **9K** |
|------|-----:|-----:|-----:|-----:|-----:|-----:|-----:|------:|------:|
| L0↑ | 10.18 | 9.32 | 11.18 | 10.30 | 9.81 | 9.12 | 8.39 | **7.88** | **8.43** |
| L1↑ | 9.17 | 8.60 | 9.68 | 9.06 | 8.77 | 8.56 | 7.95 | **7.80** | **8.01** |
| L2 | 8.81 | 8.44 | 9.37 | 8.74 | 8.47 | 8.43 | 7.87 | **7.78** | **7.88** |
| L1↓ | 8.40 | 8.46 | 9.18 | 8.90 | 8.61 | 8.86 | 8.40 | **8.24** | **8.49** |
| L0↓ | 8.35 | 8.51 | 8.97 | 8.80 | 8.55 | 8.86 | 8.47 | **8.27** | **8.53** |
| ratio | 1.22 | 1.10 | 1.25 | 1.17 | 1.15 | 1.03 | 0.99 | **0.95** | **0.99** |

Two reorganization waves visible: 3K spike (compute gate) and 9K spike
(compute gate reaching 74% active). Each wave: regress → rebuild → better.

### 3. Structural metrics trajectory

| Step | Gate | Active% | B-type | Position K:I:C | Evo | Slots |
|-----:|-----:|--------:|-------:|:--------------:|----:|------:|
| 7K | 0.486 | 44% | 56.6% | 59:21:20 | 66% | 0/16 |
| **8K** | **0.526** | **66%** | **62.8%** | **59:21:20** | **64%** | **0/16** |
| **9K** | **0.547** | **74%** | **55.7%** | **59:21:20** | **63%** | **0/16** |

Position-level dispatch frozen at 59:21:20 for 3K steps. B-type oscillating
(56.6→62.8→55.7) — rebalancing during reorganization. Compute gate steadily
climbing. Slots still dormant, mass stable at ~0.20. S5 reweight still 1.0.
CycleContinue still frozen at 2.946.

### 4. Phase model update

Phases 1-3 confirmed (sessions 089-090). Phase 4 playing out as predicted
but with more structure than expected:

**Phase 4a (5K-8K): Ascending arm mastery.** Holographic intermediate CEs
improve monotonically. Ratio drops to 0.95 at 8K (ascending arm well ahead).
Descending arm improving slowly (8.40→8.24 at L1↓).

**Phase 4b (9K): Reorganization wave.** All passes regress. Pattern matches
3K spike — capacity exhaustion at current gate level → tear apart →
rebuild. Compute gate crossing 66%→74% appears to trigger this wave just
as 0.009→0.17 triggered the 3K wave.

**Phase 4c (predicted, 10K+): Post-reorganization gains.** If pattern
holds, 10K-11K should show holographic CEs recovering below 8K levels.
The 3K spike resolved into the best trajectory yet (3K→7K was
monotonically improving). Same expected here.

### 5. Fixed probe.py — holographic data now saved to JSON

`save_results()` was printing holographic intermediate CEs to stdout
but not persisting them. Now saves `holographic.pass_ces` and
`holographic.ratio` to probe JSON files.

### 6. Implemented coarse→fine descending stride stack

Added `desc_stride_reverse` config flag (default=False, preserves existing).
When True, descending arm processes strides in reverse order (s1024→...→s1)
while ascending arm remains fine→coarse (s1→...→s1024). The change is
3 lines in model.py + config/CLI plumbing.

**Rationale**: ascending arm compresses (fine→coarse), descending arm should
expand (coarse→fine). Both arms using fine→coarse = "rowing on the same
side." With holographic loss providing per-pass training signal, the
coarse→fine direction now has the direct loss it needs to learn — the same
principle that makes TST work (Peng et al. 2026: coarse prediction with
direct loss → 2.5× training speedup). The original coarse→fine descending
arm failed because it lacked this signal; holographic loss fixes that.

**Plan**: let v11-holo reach 10K for baseline comparison, then start
v11-holo-inv with coarse→fine descending + fractal bands for A/B comparison.

### 7. Implemented fractal stride bands

Each pass now activates only strides matching its resolution level:

```
L0↑ (fine):    s1,s8,s16,s32           (4 strides, fine→coarse)
L1↑ (medium):  s16,s32,s64,s128,s256   (5 strides, fine→coarse)
L2  (apex):    s64,s128,s256,s512,s1024 (5 strides, fine→coarse)
L1↓ (medium):  s256,s128,s64,s32,s16   (5 strides, coarse→fine)
L0↓ (fine):    s32,s16,s8,s1           (4 strides, coarse→fine)
```

Symmetric hourglass: descending mirrors ascending, reversed. Adjacent passes
share 2-3 strides for inter-level communication. 23 stride-layer activations
per forward instead of 45 (~49% compute savings). Same shared weights —
only the activation pattern changes. MERA tensor network topology.

**Why this should help the hologram**: if normal LLMs are piles of photographs
that accidentally form holograms, and we're training holograms directly via
holographic loss, then fractal bands stop the model from wasting capacity
processing all 9 strides at every pass. Each pass focuses on its natural
resolution band, graded by holo CE at that band. The freed capacity can be
used to pack holograms more densely — the whole point of holographic storage.

Launch command:
```
uv run python scripts/v11/train.py \
  --checkpoint-dir checkpoints/v11-holo-inv \
  --total-steps 20000 \
  --holo-lambda 0.1 \
  --mix-ratio 0.2 \
  --fractal-stride-bands
```

Note: `--desc-stride-reverse` is now the default. `--no-desc-stride-reverse`
to opt out. Fractal bands require explicit `--fractal-stride-bands`.

## What to do next

### Priority 1: Probe v11-holo at 10K — head-to-head with baseline
Baseline 10K: loss=7.520, ppl=1845, compute=0.706, B-type=51.9%.
Will show whether the 9K reorganization wave resolves into gains.
Holo run live at ~9.5K, 10K checkpoint expected soon.

### Priority 2: Launch v11-holo-inv after 10K probe
Start new run with `--desc-stride-reverse` for direct A/B comparison.
Same config as v11-holo (λ=0.1, 20% structured) plus coarse→fine
descending arm. Hypothesis: descending arm holographic CEs improve
faster, Phase 4→5 transition happens earlier, terminal loss is lower.
See launch command in §6 above.

### Priority 3: Continue monitoring both runs (10K-20K)
Watch for:
- v11-holo: Phase 4c recovery from 9K reorganization wave
- v11-holo-inv: ascending/descending arm complementarity
- Descending arm L1↓ < 8.0 in either run
- CycleContinue differentiation
- Holographic ratio divergence between runs

### Priority 4: Baseline status
Baseline stopped at step 10,300. Declare 10K as terminal comparison
point. Focus compute on holo and holo-inv runs.

### Priority 5: Pythia scaling — combinator differentiation
Run combinator probe on Pythia-410M and Pythia-1B to map where B
differentiates from K.

### Carried
- B dispatch phase transition (B-type dominant but B-dispatch flat at 2%)
- CycleContinue activation hypothesis (still frozen at 2.946)
- S5 reweight investigation (still at 1.0 everywhere)
- QK alignment decomposition probe (RoPE follow-up)
- Dead slot recycling (all 16 dormant, mass ~0.20 — may not activate)
- Domain banking (future: extract register banks from holographic model)
- Descending arm kernel discovery (the current frontier)
- Reorganization wave pattern: 3K and 9K spikes share topology
- TST connection: Peng et al. 2026 validates coarse→fine + direct loss

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
| `results/v11-holo/` | Probe results: probe_step_{001000–009000}.json (holo) |
| `checkpoints/v11/` | Baseline v11 run (no holo, no structured), continuing to 20K |
| `checkpoints/v11-holo/` | Holo run: λ=0.1, 20% structured, 16 slots, running to 20K |
| `checkpoints/v11-holo-inv/` | (planned) Holo + coarse→fine descending arm |
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
→ Session 091: Probed v11-holo 8K-9K. 8K local optimum (ratio=0.95), 9K reorganization wave. Implemented coarse→fine descending stride stack (default=True) + fractal stride bands (each pass uses scale-appropriate strides, ~49% compute savings, MERA topology). TST paper (Peng et al. 2026) validates coarse→fine + direct loss. Holographic loss provides that signal. Plan: v11-holo-inv run with both features after 10K comparison.
