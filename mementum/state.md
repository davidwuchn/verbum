# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-06-03 | Session: 184

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 184: THE CRYSTAL SIEVE — Extraction Is Dead, Reproduction Lives**

The pivotal session. Started with "why can't we decode the magnitudes?" Ran 9 experiments
probing holographic structure at every level. Proved that extraction cannot work — the
zero mask (knowledge content) is genuinely random in every basis. Then discovered the
path: the crystal is a SIEVE, not an extractor. You don't decode magnitudes — you grow
them by training through the crystal sieve. Prototype proves crystal init 10.7× better
than random.

### The Arc of Session 184

**Phase 1 — The φ-Information Partition (experiments 1-4)**
1. Eigenvectors completely independent across layers — reconstruction cos = 0.000
2. Sign reconstruction gives 1/φ = 0.618 — the universal information baseline
3. γ = c · ‖w‖ where c is universal — 0.0172 (gate/up), 0.0099 (down), CV < 2%
4. Constant gamma BEATS per-row gamma — the variation is noise, not signal

**Phase 2 — The Negative Space (experiments 5-7)**
5. Zero mask carries 0.25 cosine — magnitude zeros (0.89) vs random (0.64)
6. Optimal zero rate is ~50%, not 35%
7. Nothing predicts zeros — gate, activations, cross-layer, SVD space, crystal space ALL fail
8. Zero mask is genuinely random in EVERY basis tested

**Phase 3 — The Paradigm Shift**
9. "If the system is derivable, the system is repeatable"
10. The crystal is a SIEVE, not an extractor — pour data through it, sediment forms
11. Extraction path is dead — you need per-weight magnitudes (irreducible teacher info)
12. Reproduction path is alive — train through crystal sieve, GD finds correct zeros

**Phase 4 — The Prototype**
13. Crystal sieve prototype on Pythia-160M: crystal init → PPL 537 in 250 steps
14. Random ternary init → PPL 5,739 in 250 steps — 10.7× WORSE
15. Crystal signs give 4,500× better starting point
16. The sieve works. The crystal IS a valid seed.

### The Sieve Model

```
SIEVE (fixed — derived from crystal equation):
  Signs:  T[i,j] ∈ {-1, +1}     from KIBC topology (the attractor)
  Scale:  C per matrix            from λ_k = C·φ^(-s·β_k)

SEDIMENT (trained — from data flowing through sieve):
  Mask:   M[i,j] ∈ {0, 1}        which weights are active (learned by GD)

FORWARD: W_eff = C · T ⊙ M
TRAINING: freeze signs, train masks + embeddings + LN
RESULT: binary masks = the knowledge content, native to ternary format
```

### Why Extraction Failed / Why Reproduction Works

The zero mask (which weights are zero) is the KNOWLEDGE CONTENT — what this
specific model learned about this specific corpus. It's the holographic fringe
pattern. Different object → different fringes. Cannot be derived from structure.

But the SIEVE (crystal signs + eigenvalue spectrum + statechart) is universal.
Every model converges to it. If you build the sieve and pour data through it,
the correct zeros emerge naturally. GD finds them — for THIS format, in THIS
architecture, with THIS data. No transplant compatibility issues.

Built the full end-to-end ternarization pipeline for Qwen3-8B. The complete recipe from session 182 (sign + per-row magnitude zeros + per-row gamma) was applied to ALL 36 layers. Result: **PPL 296,911 vs ~8 float16.** The model produces pure garbage (newlines, repeated characters, "fffff").

### The Compounding Problem

The per-layer weight cosine of 0.88 SEEMS fine — single-layer ternarization gives PPL 6-10 (vs ~6 float). But errors compound multiplicatively through 36 layers:

```
0.88^1  = 0.88    — one layer: fine
0.88^10 = 0.28    — ten layers: destroyed
0.88^36 = 0.009   — full model: pure noise
```

**Single-layer PPL was misleading.** It tests one ternary layer while 35 others remain float16 to absorb the error. When ALL layers are ternary, the representation collapses.

### Diagnosis Results (Experiment 1: Cumulative divergence)

| After layer | Activation cosine vs float | Norm ratio | Status |
|---|---|---|---|
| 0 | 0.854 | 0.77× | Damaged |
| 1 | 0.324 | 4.6× | Catastrophic — norm explodes |
| 2 | 0.147 | 4.7× | Signal lost |
| 5 | 0.059 | 5.1× | Pure noise |
| 10 | 0.005 | 0.15× | Dead (norm collapses) |
| 20 | 0.010 | 0.16× | Stays dead |
| 35 | 0.285 | 0.73× | Slight recovery (wrong signal) |

### Diagnosis Results (Experiment 2: Single-layer ablation)

| Layer | PPL (one layer ternary) | WCos min | Root cause |
|---|---|---|---|
| 0 | 7.88 | 0.873 | OK |
| **1** | **402,822** | **0.698** | **down_proj pathological** |
| **2** | **10,819** | **0.692** | **down_proj pathological** |
| **3** | **6,770** | **0.778** | **down_proj outliers** |
| 4 | 277 | 0.886 | Moderate |
| 5 | 5.42 | 0.882 | Fine |
| 7-35 | 6-10 | 0.87+ | Fine individually |

### Diagnosis Results (Experiment 3: FFN vs Attention)

| Configuration | PPL | Verdict |
|---|---|---|
| All float16 | ~8 | Baseline |
| FFN-only ternary | 485M | Catastrophic |
| Attn-only ternary | 3,274 | Bad but 100,000× better than FFN |
| All ternary | 297K | Catastrophic |
| Skip first 6, ternary rest | 318K | Still catastrophic |
| Skip first 4, ternary rest | 217K | Still catastrophic |

### Root Cause: Early down_proj Anomaly

Layers 1-3 have pathological FFN weight distributions:

| Layer | down_proj Near0% | CV | Kurtosis | Cond# | Ternary cos |
|---|---|---|---|---|---|
| 1 | 25.8% | 1.42 | 15.76 | 123.5 | 0.698 |
| 2 | 27.4% | 1.48 | 13.30 | 142.5 | 0.692 |
| 3 | 23.9% | 1.24 | 4.78 | 29.6 | 0.778 |
| 17 (normal) | 3.2% | 0.79 | 1.09 | 18.6 | 0.873 |

Early layers already have 25-47% near-zero weights, extreme outliers (kurtosis 13-16 vs 1 normal), and condition numbers 7× higher than mid-layers. The per-row γ gets dominated by outlier weights, leaving most positions poorly reconstructed.

### The Fundamental Insight

**Extraction without adaptation fails.** The crystal equation tells us the computational structure. The sign IS the computation (84% per layer). But "84% per layer" compounds to 0.84^36 = 0.001 across the full model. You need >99% per layer to survive 36 sequential applications: 0.99^36 = 0.70 — barely usable.

**To reach 0.99 per-layer cosine, you need either:**
1. **More bits per weight** — Two-mirror ternary (4 bits) gives ~0.97, three-mirror (6 bits) gives ~0.99
2. **Calibration-based optimization** — GPTQ-style: optimize ternary weights against activation error, not weight error
3. **Training-based adaptation** — The etch protocol from sessions 176-180: GD compensates for ternary errors
4. **Scratch reproduction** — Level 4: train a ternary model from scratch with the crystal as initialization

### Ternarization Stats (all 36 layers, 35% zero rate)

| Weight type | Mean cosine | Min cosine |
|---|---|---|
| gate_proj | 0.892 | 0.884 |
| up_proj | 0.894 | 0.875 |
| down_proj | 0.875 | **0.692** |
| q_proj | 0.888 | 0.885 |
| k_proj | 0.883 | 0.872 |
| v_proj | 0.881 | 0.865 |
| o_proj | 0.882 | 0.872 |

Total params: 6.95B ternarized in 38s. 34.9% zeros. Theoretical compression 10.1× (1.38 GB ternary + 5.6 MB gamma). In-memory int8: 9.44 GB.

### What This Means for the Research Program

The session 182 recipe (sign + magnitude zeros + gate-predicted scale) is CORRECT for individual layers. The crystal equation accurately characterizes what each layer computes. But end-to-end inference requires either multi-mirror quantization (more bits) or training-based adaptation (GD compensates for quantization error). **Naive sign extraction is necessary but not sufficient.**

This is actually predicted by the Q4 connection in EQUATIONS.md: sign = 84% (1 bit), magnitude = 11% (2nd bit). You need 2-3 bits of magnitude precision to keep the model functional across 36 layers. The crystal tells you which 84% is the SIGN and which 11% is CALIBRATION — but you need both.

### Multi-Mirror Also Fails (3-mirror, 6 bits/param)

Decomposed each weight into 3 ternary mirrors: W ≈ γ₁·T₁ + γ₂·T₂ + γ₃·T₃.

| Strategy | Weight cos | Energy/layer | PPL |
|---|---|---|---|
| 1-mirror + zeros (1.58 bits) | 0.88 | 0.63 | 297K |
| 3-mirror greedy (6 bits) | 0.97 | 0.81 | 17.9M |
| 3-mirror joint (6 bits) | 0.97 | 0.94 | 1.69M |
| Q4 reference (4.5 bits) | ~0.9999 | ~1.00 | ~8.5 |

**Greedy gamma bug discovered:** Independent per-mirror gamma optimization systematically loses energy (0.81 per layer). Joint least-squares solve fixes to 0.94. But 0.94^36 = 0.10 — still not enough.

**The real lesson:** Q4 works not because of 4 bits but because it uses per-group-of-32 scales (128-384× more scale parameters than our per-row approach). The bottleneck is **scale granularity**, not bit count.

See: `mementum/knowledge/ternary-compounding.md`, `scripts/experiments/full_ternarize.py`, `scripts/experiments/diagnose_ternary.py`, `scripts/experiments/mirror_ternarize.py`

### Session 182: THE TERNARY DUAL EQUATION (recap)

The dual equation was correct — gate zeros (ρ=0.75 with gradient) + crystal signs (ρ=0.05) — but the recipe only achieves 0.88 per-layer cosine, insufficient for multi-layer compounding.

### Session 181: THE CRYSTAL EQUATION (recap)

```
λ_k = C · φ^(−(n/(n+1)) · β_k)
```

All derivations confirmed. 0.99999996 correlation with consensus crystal. The equation is correct — the question is how to USE it for extraction.

## Next steps

### IMMEDIATE (session 185) — SCALE THE CRYSTAL SIEVE

The sieve prototype works. Crystal init is 10.7× better than random. Now scale it.

1. **Longer training with pruning** — Run crystal sieve on Pythia-160M for 2000+ steps.
   Add proper pruning schedule: start dense, anneal to ~50% active. Use stronger weight
   decay or explicit L1 on importance scores. Target: reach float-baseline PPL (40.5).

2. **Pruning schedule design** — The current prototype doesn't prune (100% active after 250
   steps). Need: warmup (all active) → gradual pruning → target sparsity → fine-tune.
   The φ-partition suggests 50% active is optimal.

3. **Scale to Qwen3-8B** — Once Pythia prototype converges, apply same recipe to Qwen3-8B.
   Crystal signs from trained weights. Train masks only. Measure PPL on WikiText-2.
   This is the real test: can we reach Q4-competitive PPL with 2-bit ternary?

### NEXT — Build Crystal Trace Tooling

4. **Build `src/verbum/crystal/` module** — The VSM tensor instrument:
   - Model reader → crystal basis projection
   - Forward-pass tracer → statechart state classification
   - Head classification → KIBC purity per attention head
   - Design doc: `mementum/knowledge/crystal-trace-tooling.md`

### RESEARCH DIRECTIONS

- **Shared sieve across layers** — The crystal is self-similar (r=0.998). Can layers
  share ONE sieve template with different masks? This would be the fractal compression.
- **Attention sieve** — Extend crystal sieve to attention weights (Q/K/V/O).
  Currently only FFN is sieved. Attention is ~40% of parameters.
- **VSM trace + analytical combinators** — Replace attention with KIBC combinators
  + learned routing. Requires head classification (KIBC purity measurement).

### DEFERRED

- **CLASSIFY fix** — Port GatedLinearAttention from v14 (needed for v15 etch protocol)
- **GPTQ-style mask optimization** — Simpler than full GPTQ but extraction path is now
  secondary to reproduction path

## Key assets

| Asset | Location | Status |
|-------|----------|--------|
| **Crystal sieve prototype** | `scripts/experiments/crystal_sieve_prototype.py` | ✅ NEW (session 184) |
| **Crystal space zeros** | `scripts/experiments/crystal_space_zeros.py` | ✅ NEW (session 184) |
| **φ-information partition** | `mementum/knowledge/phi-information-partition.md` | ✅ NEW (session 184) |
| **Crystal trace tooling design** | `mementum/knowledge/crystal-trace-tooling.md` | ✅ NEW (session 184) |
| **Eigenvector self-similarity** | `scripts/experiments/eigenvector_selfsimilarity.py` | ✅ NEW (session 184) |
| **Gamma φ-structure** | `scripts/experiments/gamma_phi_structure.py` | ✅ NEW (session 184) |
| **Gamma sort order** | `scripts/experiments/gamma_sort_order.py` | ✅ NEW (session 184) |
| **Row norm ↔ crystal** | `scripts/experiments/row_norm_crystal.py` | ✅ NEW (session 184) |
| **Negative space** | `scripts/experiments/negative_space.py` | ✅ NEW (session 184) |
| **Gate zero predictor** | `scripts/experiments/gate_zero_predictor.py` | ✅ NEW (session 184) |
| **Activation zero mask** | `scripts/experiments/activation_zero_mask.py` | ✅ NEW (session 184) |
| **Full ternarization pipeline** | `scripts/experiments/full_ternarize.py` | ✅ (session 183) |
| **Ternary diagnosis** | `scripts/experiments/diagnose_ternary.py` | ✅ (session 183) |
| **Compounding knowledge** | `mementum/knowledge/ternary-compounding.md` | ✅ (session 183) |
| Ternary dual equation | `mementum/knowledge/ternary-dual-equation.md` | ✅ (session 182) |
| EQUATIONS.md | `EQUATIONS.md` | ✅ (session 181) |
| Crystal derivation | `mementum/knowledge/crystal-phi-derivation.md` | ✅ (session 181) |
| Topology-gradient separation | `mementum/knowledge/topology-gradient-separation.md` | ✅ (session 180) |
| Unified probe library | `src/verbum/probes/library.py` | ✅ 903 probes, 535 crystal |
| v15 model | `scripts/v15/model.py` | ⚠️ Needs GatedLinearAttn |
| v14 GatedLinearAttn | `scripts/v14/attention.py` | ✅ Reference for port |

## What changed this session (184)

| Change | Impact |
|--------|--------|
| **Eigenvector independence** | Cross-layer reconstruction cos = 0.000 — rotations are per-layer fingerprints |
| **1/φ information partition** | Sign reconstruction from any layer gives cos ≈ 0.618 = 1/φ |
| **γ = c · ‖w‖ universal** | Per-row gamma is noise. One constant per weight type: 0.0172 (gate/up), 0.0099 (down) |
| **Constant γ beats true γ** | The φ-geometric model is smoother and reconstructs better |
| **Zero mask = holographic phase** | Carries 0.25 cosine of information. The negative space IS the signal |
| **Optimal 50% zeros** | Not 35% — we've been under-zeroing |
| **Gate zeros fail** | Gate doesn't predict up/down zeros. Per-weight ρ ≈ 0.02 |
| **Activation importance fails** | E[gate·input] ≈ random for zero mask prediction |
| **Zero mask random in ALL bases** | Weight space, SVD space, crystal space — genuinely random everywhere |
| **Paradigm shift: extraction → reproduction** | Zero mask IS the knowledge content (per-model, irreducible). Don't extract — reproduce. |
| **Crystal sieve concept** | Crystal = sieve (universal computation). Zeros = sediment (trained knowledge). |
| **Crystal sieve prototype** | Pythia-160M: crystal init PPL 537 vs random init PPL 5,739 — **10.7× better** |
| **Crystal init = 4,500× better start** | Crystal: 107K initial PPL vs random: 485M initial PPL |
| **9 experiment scripts** | eigenvector, gamma_phi, gamma_sort, row_norm, negative_space, gate_predictor, activation_mask, crystal_space_zeros, crystal_sieve_prototype |
| **2 knowledge pages** | phi-information-partition.md, crystal-trace-tooling.md |

## What changed session 183 (recap)

| Change | Impact |
|--------|--------|
| **full_ternarize.py** | End-to-end pipeline: ternarize + PPL + generation |
| **diagnose_ternary.py** | 3 experiments: cumulative divergence, single-layer ablation, FFN vs attn |
| **PPL 296,911** | Naive ternary produces garbage — sign extraction is necessary but not sufficient |
| **Compounding law** | 0.88^36 = 0.009 — per-layer cosine must be >0.99 for multi-layer survival |
| **Early down_proj anomaly** | Layers 1-3 have pathological weights (25-47% near-zero, kurtosis 13-16, cond# 123-142) |
| **FFN > attn damage** | FFN-only ternary: PPL 485M; attn-only: PPL 3,274. FFN is the bottleneck |
| **Skip-early doesn't help** | Skip-6: PPL 318K. The problem is compounding, not just bad layers |
| **3-mirror greedy fails** | 6 bits/param, PPL 17.9M — greedy gamma loses energy (0.81/layer) |
| **3-mirror joint** | Joint least-squares gamma: PPL 1.69M — energy 0.94 but still garbage |
| **Greedy gamma bug** | Independent gamma optimization systematically underestimates total energy |
| **Scale granularity** | Q4 uses per-32 scales (128-384× more than per-row). That's why Q4 works |
| **mirror_ternarize.py** | Multi-mirror pipeline with joint gamma optimization |
| **Group scales are flat** | CV=0.13 within rows. No fractal φ structure at group level |
| **Per-group doesn't help** | Per-row cos 0.786 → per-32 cos 0.800. Scale granularity is NOT the bottleneck |
| **Q4 works via 16 levels** | Not scale granularity — per-weight quantization levels capture per-weight variation |
| **Hierarchical mirrors fail** | Sigmoid importance modulation: PPL 300M. Architecture change without training = garbage |
| **Session conclusion** | Pure extraction cannot work. Training-based adaptation is required for ternary. |
| **Knowledge page** | `ternary-compounding.md` — compounding law + mirror + group + hierarchical analysis |

## Knowledge map

Key pages for current direction:
- **`phi-information-partition.md`** — **signs=1/φ, γ=noise, zeros=phase, extraction dead** (session 184, NEW)
- **`crystal-trace-tooling.md`** — **VSM instrument design for crystal sieve + tracing** (session 184, NEW)
- **`ternary-compounding.md`** — **WHY 0.88 cosine/layer → garbage at 36 layers** (session 183)
- **`ternary-dual-equation.md`** — TWO EQUATIONS: gate zeros + crystal signs (session 182)
- **`EQUATIONS.md`** — THE CRYSTAL EQUATION + Q4 connection (session 181)
- **`crystal-phi-derivation.md`** — Full derivation chain (session 181)
- `topology-gradient-separation.md` — WHY lattice must be frozen, the etch protocol (session 180)
- `training-protocols.md` — TD rules, fold cycle, failure modes
- `crystal-universality.md` — KIBC universal fixed points
- `extraction-sign-accuracy.md` — signs 100% accurate, magnitude is the gap
- `project-thesis.md` — the central claim
