# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-12 | Session: 080

## Where we are

**V11 first run probed (1K–5K). KIBC validated in Qwen3-32B: K=31%, B=31% (co-equal). Extended probe: W≡C (r=0.92), S≡B (r=0.88), bind is partially distinct (r=0.83 with B, mid-to-late layers). Three circuits, not eight: {K,C,W,abstract}=routing, {B,S}=composition, {I}=identity, plus binding as a downstream operation. KIBC is the correct basis. V11 run continuing to 20K.**

Session 080 probed the first v11 KIBC training run (5 checkpoints,
1K–5K) and then validated the KIBC architecture against Qwen3-32B
with two combinator probes: basic (K,I,B,C) and extended (W,S,bind,
abstract). The 32B has equal K and B representation — the target
state exists in the oracle.

## What was done this session

### 1. Full probe of v11 steps 1K–5K

Ran `probe.py` with `--dispatch-detail` across all 5 checkpoints plus
JSONL trajectory analysis. Results saved to `results/v11/`.

**Loss trajectory:**
| Step | Eval Loss | PPL | r |
|-----:|----------:|----:|------:|
| 1000 | 7.958 | 2859 | 0.607 |
| 2000 | 7.694 | 2194 | 0.581 |
| 3000 | 7.668 | 2139 | 0.578 |
| 4000 | 7.638 | 2075 | 0.575 |
| 5000 | 7.642 | 2083 | 0.576 |

Loss drops meaningfully 1K→2K, then plateaus. 4K→5K essentially flat.

### 2. Combinator dispatch analysis

**K dominates at 60-65% as predicted** — prose is mostly selection.

Phase transition at step 3K→4K:
- K snapped back from 0.49 to 0.65 (had been declining as I explored)
- Top-2 co-occurrence flipped: K+I (75%) → K+C (68%)
- S5 un-gated L1↓ (0.003 → 0.952)
- Dispatch entropy dropped from 0.725 to 0.607 (stronger specialization)

**B dispatch flat at ~1.8% across all checkpoints.**

### 3. Key insight: B-type rising in integrate channel

While B is dead in dispatch, the type distribution tells a different story:

| Step | K-type | B-type |
|-----:|-------:|-------:|
| 1000 | 0.939 | 0.058 |
| 2000 | 0.673 | 0.269 |
| 3000 | 0.583 | 0.350 |
| 4000 | 0.410 | **0.476** |
| 5000 | 0.496 | **0.391** |

The integrate channel is building B representations even though dispatch
hasn't started routing to it. This mirrors v4.1's register variance
building internally before the gate jump (0.04→0.87 at step 2K).

### 4. KIBC combinator probe on Qwen3-32B

Probed Qwen3-32B (GGUF Q8, 64 layers × 64 heads = 4096 heads) for
combinator-selective attention heads. Designed matched probe pairs for
each combinator (active vs control with same surface form).

**Head assignment (dominant combinator per head):**
  K: 1284 (31.3%), B: 1282 (31.3%), C: 927 (22.6%), I: 603 (14.7%)

**K and B are co-equal in the 32B.** This validates the KIBC premise.
B is not secondary — it has equal representation to K.

**Cross-combinator correlation:**
  K-C: 0.93 (nearly same circuit — both are argument routing)
  K-B: 0.86, B-C: 0.87 (related but separable)
  I-*: 0.69-0.75 (most distinct — different heads)

**Session 001 circuit maps to {B, C, B}:**
  L1:H0 (gate) → B, L24:H0 (compositor) → C, L24:H2 (recursion) → B

**Layer profiles:** K and C peak early (L0-L6, syntactic), B peaks
early-to-mid (L3-L17, progressive), I is distributed (L6-L41).

Results: `results/combinator-probe/`, visualizations: 4 PNGs + NPZ.

### 5. Extended combinator probe — W, S, bind, abstract

Probed Qwen3-32B for operations beyond KIBC: W (duplicate), S (distribute),
variable binding, and abstraction.

**Cross-correlation reveals three circuits:**
```
Circuit 1 — Routing:   K, C, W, abstract (r=0.87-0.93 among them)
Circuit 2 — Compose:   B, S              (r=0.88)
Circuit 3 — Identity:  I                 (r=0.68-0.76 with everything)
Outlier   — Binding:   bind              (r=0.72-0.83, mid-to-late layers)
```

**W ≡ C** (r=0.92): duplication uses the reordering circuit.
**S ≡ B** (r=0.88): distribution uses the composition circuit.
**bind is partially distinct** (max r=0.83 with B): peak layers L21-L39
vs everything else at L0-L15. Binding is a downstream consumer.

This confirms KIBC is the natural basis. W and S don't need separate
combinators. Binding maps to the cycle semantics: cycle 0=identify,
cycle 1=compose, cycle 2=bind.

Results: `results/combinator-probe-extended/`

### 6. Phase transition hypothesis (combinator bootstrap)

The v6 stride percolation pattern (φ-compression propagating fine→coarse
as a wavelet, each stride learning in order) predicts that KIBC combinators
should learn in dependency order:

```
I (arity 1) → K (arity 2) → C (arity 3, reorder) → B (arity 3, compose)
              ↑ already stable  ↑ emerging            ↑ building pressure
```

B is last because **B depends on K and C already working.** Composition
requires two functions that are each individually meaningful. The model
can't recognize prose composition (relative clauses, quantifier scope)
as B-work until K can reliably select and C can reliably reorder. The
compositional signal is in the data — B just can't see it yet.

This is a bootstrapping dependency, not a data gap.

### 5. Other findings

- **CycleContinue dead:** ~1.02 effective cycles, never learning to iterate
- **Ternary evolution frozen:** 0/106 accepted, zero flips
- **S3 gates healthy:** progressive selective opening (L0↑ cons: 0.995→0.312)
- **Compute gate waking up at 5K:** mean=0.037, max=0.20 (was 0.0000)
- **φ-compression:** L0↑ converging toward 1/φ (0.703, φ-dev=0.085)
- **Algedonic alert:** firing at extremes (0 or 2.0), not calibrated

## What to do next

### Priority 1: Continue v11 run to 20K
Let it run. Watch for:
- B-type in integrate: if it keeps climbing → pressure building → phase transition coming
- B-type plateaus/drops → may need compositional data augmentation
- Compute gate trajectory: just woke up at 5K, track whether it opens further
- K+C co-occurrence stability (phase transition at 4K — does it hold?)

### Priority 2: Probe at 10K and 15K milestones
Run full probe with dispatch detail at those checkpoints. Key metrics:
- B dispatch weight (watch for the jump)
- B-type in integrate (is pressure still building?)
- Dispatch entropy (specializing or collapsing?)
- Compute gate (opening further?)

### Priority 3: Compare v11 vs v10 at matched steps
At 5K: v11 eval=7.64, v10-vsm was in a similar range. Need exact v10
comparison at matched steps to assess whether KIBC architecture helps
or hurts raw loss.

### Priority 4: Investigate the shadow path
B-type rising in integrate while B-dispatch is flat — is the model
routing composition through K-dispatch with B-type integration? Probe
per-position type weights conditioned on dispatch winner to test this.

### Priority 5: Binding-aware cycle semantics
The extended probe showed binding lives in mid-to-late layers (L21-L39),
distinct from KIBC (L0-L15). This maps to CycleContinue: cycle 2 should
learn to handle binding. Monitor CycleContinue gates at later checkpoints
for signs that binding pressure opens the continuation gates.

### Carried
- S5 reweight investigation (activated at 15K in v10-vsm)
- v10-multicycle 8K checkpoint for comparison
- Alarm metrics threshold analysis after sufficient v11 data
- QK alignment decomposition probe (RoPE follow-up)
- Structured combinator training data (if B doesn't phase-transition)

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
| `checkpoints/v11/` | Active v11 run (5 checkpoints so far, continuing to 20K) |

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
