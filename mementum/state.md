# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-11 | Session: 079

## Where we are

**RoPE × attention spiral investigation complete. RoPE provides the geometric substrate (64 dim pairs, wavelengths 6→5M tokens); learned Q·K alignment creates the actual spiral (~1.018/layer expansion). Three new scripts, 36 visualization outputs.**

Session 079 tested whether the attention distance spiral discovered in
session 068 is tied to RoPE's cos-sin frequency structure. Built a probe
that hooks Q/K projections to measure per-dim-pair energy distribution
across all 36 layers. Key finding: RoPE energy is BROAD at every layer
(no progressive frequency shift), and RoPE alone predicts a FLAT attention
centroid (~35 tokens, no expansion). The spiral emerges from learned W_Q/W_K
projections that choose where on RoPE's frequency ruler to align Q·K —
early layers align on high-freq dims (local attention), deeper layers on
low-freq dims (global attention). RoPE is the coordinate system; the model
learns where to stand on it at each depth.

v11 KIBC architecture remains ready for first training run (session 078).

## What was done this session

### 1. RoPE frequency analysis (mathematical)

Computed the full RoPE frequency spectrum for Qwen3-4B:
- θ_base = 1,000,000, head_dim = 128, 64 dimension pairs
- Wavelengths: 6.3 → 5,063,256 tokens (geometric series)
- Ratio between successive wavelengths: θ^(1/64) = **1.2409** (exact constant)
- Tested theoretical model: if layers shift energy by K dim pairs/layer,
  expansion = θ^(K/64). For observed 1.018 expansion, K ≈ 0.08 — too small
- Pure RoPE shift model predicts expansion ~1.006-1.008 (40-50% of observed)
- Simulated 36-layer expansion with Gaussian energy windows: confirmed

### 2. RoPE energy probe (`scripts/explore/rope_energy_probe.py`)

Hooks into Qwen3-4B's q_norm and k_norm (after projection, before RoPE):
- Captures per-dim-pair energy: mean(|q_2i|² + |q_{2i+1}|²) per layer × head
- Computes energy centroid in dim-pair space (weighted mean index)
- Predicts attention centroid from energy distribution via softmax model
- Ran all 7 prompts from attention_spiral.py for direct comparison

**Findings:**
- Q energy centroid **oscillates** (range 29-44) — does NOT monotonically shift
- K centroid shows **strong GQA alternation** (~27 vs ~37-48 per layer)
- Cross-prompt correlation r > 0.99 — this is a **model property**, not content-dependent
- Cross-prompt std = 0.3 on a 28-44 range
- RoPE-predicted expansion = **1.0000** (flat) — accounts for 0% of observed spiral
- RoPE per-dim-pair energy is BROAD at every layer

### 3. Combined 3D visualization (`scripts/explore/rope_spiral_combined.py`)

Renders the RoPE substrate and observed spiral in the same 3D space:
- **Dual helix**: observed spiral (colored by RoPE band) vs RoPE prediction (flat gray cylinder)
- **Spectral helix**: colored by RoPE wavelength, sized by Q-K divergence
- **Gap analysis**: anatomy of the learned contribution (obs - pred) with 3D radial lines
- **Unwound ribbon**: flattened view with RoPE wavelength scale overlay
- **Aggregate**: all 7 prompts wound together around the flat RoPE cylinder

### 4. Key insight: RoPE as coordinate system

```
RoPE (constant)     = coordinate system (the frequency ruler)
W_Q, W_K (learned)  = where to stand on that ruler per layer
attention centroid   = readout of learned position on the ruler
spiral              = progressive shift of standing-position across depth
```

The model doesn't learn "attend at distance X" — it learns "align Q and K on
dim pairs I-J" which, because of RoPE's geometric spacing, maps to a specific
distance scale. The spiral is the model sliding its Q·K alignment window down
the RoPE ruler across layers. Each layer computes a **delta** against RoPE's
flat ~35-token baseline: early layers push down (more local), late layers
push up (more global).

GQA head specialization: KV heads plant flags at different RoPE ruler positions
(~27 = local, ~47 = global). Q heads choose which flag to align with per layer.

### 5. Literature connection

"Round and Round We Go!" (ICLR 2025) found the same pattern in Gemma 7B:
- High-freq RoPE dims → positional attention (local patterns)
- Low-freq RoPE dims → semantic attention (long-range meaning)
- First and last layers use high frequencies most
- Our layer 5-6 spike maps to their positional→semantic transition

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
- Does the algedonic alarm differentiate? Watch alarm_factors in
  metrics_log.jsonl — early runs should show factors > 1.0 (pleasure)

### Priority 2: QK alignment decomposition probe
The RoPE energy probe showed WHERE energy sits, but the spiral comes from
Q·K ALIGNMENT per dim pair (which bands correlate, not just which have energy).
Next probe: decompose actual attention logits by RoPE dim pair to measure
per-dim-pair QK correlation at each layer. This should reveal the progressive
alignment shift that creates the spiral.

### Priority 3: Compare v11 vs v10 at matched steps
At 1K, 5K, 10K, 20K compare loss, dispatch, cycles, emphasis.

### Priority 4: Structured combinator training data
Generate KIBC reduction examples once v11 shows combinator differentiation.

### Carried
- S5 reweight investigation (activated at 15K in v10-vsm)
- v10-multicycle 8K checkpoint for comparison
- Alarm metrics threshold analysis after first v11 run

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
| `scripts/explore/rope_energy_probe.py` | RoPE dim-pair energy probe (Q/K hooks) |
| `scripts/explore/rope_spiral_combined.py` | Combined 3D: RoPE × attention spiral |
| `outputs/rope_energy/` | 19 files: energy heatmaps, centroid analysis, JSON |
| `outputs/rope_spiral/` | 17 files: dual helices, gap analysis, unwound ribbon |
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
→ Session 079: RoPE × attention spiral — energy probe shows RoPE=substrate not driver, spiral=learned Q·K alignment
