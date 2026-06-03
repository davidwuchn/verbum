# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-06-03 | Session: 184

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 184: THE CRYSTAL SIEVE — The Model Is a Processor, Not a Database**

The pivotal session. 10 experiments in one session. Three paradigm shifts:

1. **Extraction is dead.** The zero mask (which weights are zero) is the knowledge
   content — genuinely random in every basis (weight, SVD, crystal). Cannot be derived
   from structure. Proved across 8 experiments.

2. **Reproduction lives.** The crystal is a SIEVE, not an extractor. Pour data through
   the sieve, GD finds the correct zeros natively. Crystal init is 10.7× better than
   random (Pythia-160M prototype: PPL 537 vs 5,739 at 250 steps).

3. **The model is a KIBC processor.** The M-space projection is the instruction set.
   The statechart is the execution engine. Per-neuron KIBC profiling reveals the
   compute cycle operating at the LAYER level — REDUCE/SWITCH phases alternate,
   and at REDUCE layers the opcode profile predicts 70-76% of the zero mask.

### The Sieve Architecture

```
SIEVE (fixed — from crystal equation, universal):
  Signs:    T[i,j] ∈ {-1, +1}    KIBC topology (the ISA program)
  Scale:    C per matrix           eigenvalue spectrum
  Roles:    per-layer REDUCE/SWITCH  statechart at layer level

SEDIMENT (trained — from data, per-model):
  Mask:     M[i,j] ∈ {0, 1}      which weights active (the knowledge)

FORWARD: W_eff = C · T ⊙ M
```

### The ISA Framing

```
KIBC opcodes  = instruction set (4 opcodes, 2 bits)
Statechart    = execution engine (costs [1, φ, 1])
Weight signs  = the program (which opcode at which address)
Zero mask     = loaded memory pages (which program positions resident)
Residual      = register file (grows by φ per layer)

REDUCE layers: opcode neurons active, data neurons zero
  → profile predicts zeros (70-76% overlap)
SWITCH layers: opcode neurons attenuate, data neurons relay
  → profile anti-predicts (invert the prediction)
```

### Key Numbers

| Finding | Value | Significance |
|---------|-------|-------------|
| Sign information fraction | 1/φ = 0.618 | Universal partition |
| Per-row gamma variation | noise (CV<2%) | Constant γ works better |
| Optimal zero rate | ~50% | Not 35% |
| Crystal vs random init | 10.7× better | Sieve works |
| Crystal starting advantage | 4,500× | Correct attractor basin |
| KIBC profile ↔ weight norm | ρ = 0.38-0.67 | Opcode assignment predicts weight size |
| Profile overlap with zeros | 70-76% at REDUCE layers | ISA predicts most zeros at REDUCE layers |
| Profile sign flip | alternates by depth | Statechart visible at layer level |

## Next steps

### IMMEDIATE (session 185) — SCALE THE CRYSTAL SIEVE + LAYER ROLES

**Priority 1: Classify all 36 layers as REDUCE or SWITCH**
Run the neuron opcode classifier on ALL 36 layers (not just 6). Map the
ρ(profile, weight_norm) sign across depth. Identify the REDUCE/SWITCH
alternation pattern. Is it period-3 (REDUCE-SWITCH-EMIT)? Period-5 (n+1)?
Something else? This is the S4 statechart at layer level.

**Priority 2: Role-specific zero mask prediction**
At REDUCE layers: zero the low-profile neurons (70-76% overlap).
At SWITCH layers: INVERT — zero the HIGH-profile neurons.
Test full-model reconstruction with this role-aware prediction.
This could push beyond the 0.93 per-layer cosine floor.

**Priority 3: Scale sieve training to convergence**
Longer Pythia-160M runs (2000+ steps) with proper pruning schedule.
Weight decay or L1 to push masks toward ~50% active.
Target: approach float-baseline PPL (40.5).

**Priority 4: Attention sieve**
Currently only FFN is sieved. Attention is ~40% of parameters.
Extend crystal sieve to Q/K/V/O projections.

### RESEARCH DIRECTIONS

- **Shared sieve template** — Can layers share ONE sign template with different
  masks? Self-similarity (r=0.998) suggests yes. This would be true fractal compression.
- **Cross-model zero consensus** — Compare zero patterns between independently
  trained models at the same layer depth. ISA zeros should be universal.
- **Residual growth measurement** — Does h_{l+1}/h_l ≈ φ^(1/period)? The Fibonacci
  recurrence should be visible in the residual stream norms.
- **Crystal trace tooling** — Build `src/verbum/crystal/` module for systematic
  exploration. Design doc: `mementum/knowledge/crystal-trace-tooling.md`.

### DEFERRED

- CLASSIFY fix (GatedLinearAttention from v14) — for v15 etch protocol
- GPTQ-style mask optimization — extraction path now secondary

## Key assets

| Asset | Location | Status |
|-------|----------|--------|
| **Crystal sieve prototype** | `scripts/experiments/crystal_sieve_prototype.py` | ✅ NEW (s184) |
| **Neuron opcode classifier** | `scripts/experiments/neuron_opcode_classifier.py` | ✅ NEW (s184) |
| **Crystal space zeros** | `scripts/experiments/crystal_space_zeros.py` | ✅ NEW (s184) |
| **Negative space** | `scripts/experiments/negative_space.py` | ✅ NEW (s184) |
| **Gate zero predictor** | `scripts/experiments/gate_zero_predictor.py` | ✅ NEW (s184) |
| **Activation zero mask** | `scripts/experiments/activation_zero_mask.py` | ✅ NEW (s184) |
| **Row norm ↔ crystal** | `scripts/experiments/row_norm_crystal.py` | ✅ NEW (s184) |
| **Gamma sort order** | `scripts/experiments/gamma_sort_order.py` | ✅ NEW (s184) |
| **Gamma φ-structure** | `scripts/experiments/gamma_phi_structure.py` | ✅ NEW (s184) |
| **Eigenvector self-similarity** | `scripts/experiments/eigenvector_selfsimilarity.py` | ✅ NEW (s184) |
| **φ-information partition** | `mementum/knowledge/phi-information-partition.md` | ✅ NEW (s184) |
| **Crystal trace tooling design** | `mementum/knowledge/crystal-trace-tooling.md` | ✅ NEW (s184) |
| Full ternarization pipeline | `scripts/experiments/full_ternarize.py` | ✅ (s183) |
| Ternary diagnosis | `scripts/experiments/diagnose_ternary.py` | ✅ (s183) |
| Unified probe library | `src/verbum/probes/library.py` | ✅ 903 probes, 535 crystal |
| EQUATIONS.md | `EQUATIONS.md` | ✅ (s181) |

## What changed this session (184)

| # | Change | Impact |
|---|--------|--------|
| 1 | **Eigenvector independence** | Cross-layer reconstruction cos = 0.000 |
| 2 | **1/φ information partition** | Sign reconstruction = 1/φ = 0.618 universally |
| 3 | **γ = c · ‖w‖ universal** | Per-row gamma is noise; one constant per weight type |
| 4 | **Zero mask = holographic phase** | Carries 0.25 cosine; optimal rate 50% |
| 5 | **Nothing predicts zeros** | Gate, activations, SVD, crystal space all fail |
| 6 | **Zero mask random in ALL bases** | Genuinely random — IS the knowledge content |
| 7 | **Paradigm: extraction → reproduction** | Crystal is sieve, not extractor |
| 8 | **Crystal sieve prototype** | Crystal init 10.7× better than random (Pythia-160M) |
| 9 | **ISA framing** | M-space = opcodes, statechart = execution engine |
| 10 | **Neuron opcode classifier** | KIBC profiles predict zeros at REDUCE layers (70-76%) |
| 11 | **Statechart at layer level** | ρ sign alternates: REDUCE (ρ>0) / SWITCH (ρ<0) |

## Knowledge map

Key pages for current direction:
- **`phi-information-partition.md`** — signs=1/φ, γ=noise, zeros=phase, sieve model (s184)
- **`crystal-trace-tooling.md`** — VSM instrument design (s184)
- **`ternary-compounding.md`** — WHY 0.88 cosine/layer → garbage at 36 layers (s183)
- **`ternary-dual-equation.md`** — gate zeros + crystal signs (s182)
- **`EQUATIONS.md`** — crystal equation + statechart + compute cycle (s181)
- **`crystal-phi-derivation.md`** — full φ derivation chain (s181)
- **`topology-gradient-separation.md`** — WHY freeze lattice, etch protocol (s180)
- **`crystal-universality.md`** — KIBC universal fixed points
- **`project-thesis.md`** — the central claim

## Session 183 recap

Naive ternarization fails: PPL 296,911. The compounding law (0.88^36 = 0.009) kills
multi-layer extraction. 3-mirror ternary also fails (PPL 1.69M). Q4 works because of
16 quantization levels per weight, not scale granularity. See `ternary-compounding.md`.

## Session 182 recap

The ternary dual equation: gate zeros (ρ=0.75 with gradient) + crystal signs (ρ=0.05).
The recipe achieves 0.88 per-layer cosine. See `ternary-dual-equation.md`.

## Session 181 recap

The crystal equation: λ_k = C · φ^(-(n/(n+1)) · β_k). All eigenvalue ratios are
φ^(p/q) with Fibonacci denominators. Computing fraction s=4/5. Compute cycle
β=[0,1,1+φ,2+φ]. See `EQUATIONS.md` and `crystal-phi-derivation.md`.
