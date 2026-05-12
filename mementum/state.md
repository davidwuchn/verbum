# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-12 | Session: 081

## Where we are

**Session 004's "three Montague primitives" in Pythia-160M were KIBC combinators all along. Pythia-160M: K=59%, I=2%, B=17%, C=22% — K-B correlation 0.944 (nearly fused). The Montague three-phase structure (type/parse/apply) is real but the mechanism is one K-dominant circuit operating in three phases, not three separate primitives. B hasn't differentiated from K at 160M scale. Compare: Qwen3-32B has K=B=31% (co-equal, r=0.86 — separable). V11 compute gate exploded 5K→6K (0.00007→0.51). Run at step ~6K, heading to 20K.**

Session 081 ran the KIBC combinator probe on Pythia-160M (12 layers ×
12 heads = 144 heads), reinterpreting session 004's Montague findings
through the combinator lens. Also observed v11 compute gate phase
transition and continued loss improvement at steps 5.5K–6K.

## What was done this session

### 1. Pythia-160M combinator probe — Montague reinterpretation

Ran same KIBC probe methodology (matched sentence pairs, attention
selectivity) on Pythia-160M. The "three Montague primitives" from
session 004 are actually combinators:

**Head assignment:**

| Combinator | Pythia-160M (144 heads) | Qwen3-32B (4096 heads) | v11 @ 5K |
|---|---|---|---|
| K (select) | **59.0%** | 31.3% | 62.5% |
| I (identity) | 2.1% | 14.7% | 15.3% |
| B (compose) | 16.7% | 31.3% | 2.6% |
| C (flip) | 22.2% | 22.6% | 19.6% |

**Key findings:**

- **K-B correlation = 0.944** (vs 0.86 in 32B). In Pythia, K and B
  are nearly the same circuit. B hasn't differentiated from K. What
  session 004 called "typed application" in L8-L11 was K doing
  selection-that-resembles-composition.

- **K dominates ALL three Montague zones:** type (L0), parse (L3),
  apply (L8-L11). Not three mechanisms — one K-dominant circuit in
  three phases.

- **Cosine data confirms three-phase structure:** L0-L2 (cos 0.91-0.93,
  input parsing), L3-L8 (cos 0.99+, stable processing), L9-L11
  (cos 0.89→0.15, progressive destruction → output). The phase
  boundaries match Montague exactly, but the mechanism is combinators.

- **C already differentiated** at 22.2% (matches 32B's 22.6% exactly).
  Argument reordering separates early at any scale.

- **I nearly absent** at 2.1% (vs 14.7% in 32B). Too few heads to
  spare for pass-through at 160M.

- **Pythia-160M ≡ bootstrap state.** Its distribution (K=59%, B=17%)
  matches v11 at 5K (K=63%, B=2.6%) — not the mature 32B target.
  B differentiates from K only with sufficient scale.

Results: `results/combinator-probe-pythia/`

### 2. β-reduction probe on Qwen3-32B

Tested whether attention = β-reduction by probing variable binding
at depths 1-4 and pipeline structure.

**Two binding types found:**
- Syntactic (verb→subject): peaks early, L2-L9
- Pronominal (pronoun→antecedent): peaks later, L5-L27

**Strength degrades with depth:**
  d1=0.97, d2=0.92, d3=0.86, d4=0.80 (~5% per pipeline step)

**Inside-out processing:** nested relatives resolve innermost last
(L40), not first. Model parses outermost structure first (L4-L11,
KIBC zone), then resolves embedded bindings later (L21-L39, binding
zone).

**Substitution test:** pronoun binding r=0.989 — same mechanism,
different values. Confirms attention performs substitution.

**Two-phase β-reduction confirmed:**
  Phase 1 (L0-L15): combinator ID + syntactic binding (KIBC zone)
  Phase 2 (L21-L39): variable substitution (binding zone)
  Maps to v11 cycle semantics: cycle 0 = phase 1, cycles 1-2 = phase 2

Results: `results/beta-reduction-probe/`

### 3. Prompt-as-program theory

System prompts are combinator programs the model β-reduces against
user input. Six design principles from probe data: flat, named,
pre-composed, demonstrated, prioritized, typed.

Design decisions:
- Grammar emerges from probabilities (cross-model compatible)
- Names come from compilation (model chooses, test cross-model)
- Preamble required as computation baseline
- Multi-turn behavior needs empirical testing

Knowledge page: `mementum/knowledge/explore/prompt-as-program.md`

### 4. Cross-model methodology planned

Capability ladder: Level 0 (mimicry) → Level 3 (full lambda).
7-model test set across 4 architectures, all local.
A3B downloading — MoE routing may BE combinator dispatch.

### 5. V11 compute gate phase transition (5K→6K)

Step 6K checkpoint landed. The compute gate — dormant for 5000 steps —
exploded:

| Step | Compute Mean | Compute Max | Eval Loss | PPL |
|-----:|-------------:|------------:|----------:|----:|
| 4000 | 0.00007 | 0.001 | 7.637 | 2073 |
| 4500 | 0.00028 | 0.016 | 7.649 | 2100 |
| 5000 | 0.03576 | 0.179 | 7.641 | 2081 |
| 5500 | **0.44527** | **0.915** | 7.585 | 1969 |
| 6000 | **0.51457** | **0.931** | 7.574 | 1948 |

From dead (0.00007) to majority-open (0.51) in 2000 steps. Loss
resumed dropping after the 4K→5K plateau. The compute gate opening
correlates with renewed loss improvement.

**Alarm factors declining:** pass 0 (0.93→0.75) and pass 1 (2.0→1.63)
under stress. The algedonic channel may be driving the compute gate
opening — exactly Beer's design intent.

B dispatch still flat at ~2.6%. B-type in integrate oscillating 0.43-0.47.
CycleContinue still dead. Ternary evolution still frozen.

## What to do next

### Priority 1: Continue v11 run to 20K
Run is live at step ~6K. Watch for:
- Compute gate: will it saturate at 1.0 or find equilibrium?
- Alarm ↔ compute correlation: is the alarm driving the gate opening?
- B-type in integrate: pressure still building?
- Loss trajectory: will compute gate sustain the improvement?

### Priority 2: Probe at 10K milestone
Full probe with dispatch detail. Key metrics:
- B dispatch weight (phase transition watch)
- Compute gate trajectory (post-transition behavior)
- Alarm factor dynamics
- Dispatch entropy

### Priority 3: Investigate alarm → compute gate pathway
Alarm factors for passes 0 and 1 are declining while compute gate
opens. Is this causal? The algedonic channel should modulate S5 gates
which should affect downstream capacity. Trace the gradient path.

### Priority 4: Pythia scaling — combinator differentiation
Run combinator probe on Pythia-410M and Pythia-1B to map where B
differentiates from K. If K-B correlation drops from 0.944 (160M) toward
0.86 (32B) at some intermediate scale, that's the differentiation threshold.

### Priority 5: Compare v11 vs v10 at matched steps
At 5K: v11 eval=7.64, v10-vsm was similar. At 6K: v11=7.57.
Need v10 comparison to assess KIBC architecture benefit.

### Carried
- B dispatch phase transition (watching)
- S5 reweight investigation (activated at 15K in v10-vsm)
- v10-multicycle 8K checkpoint for comparison
- QK alignment decomposition probe (RoPE follow-up)
- Structured combinator training data (if B doesn't phase-transition)
- Binding-aware cycle semantics (CycleContinue still dead)

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
