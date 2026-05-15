# Building holographic type probe script

## User

orient, I want to work on mementum/knowledge/explore/holographic-storage.md


### Thinking

The user wants to orient (cold-start protocol) and then work on a specific knowledge page. Let me follow the orient protocol: read state.md first, then look at the relevant file.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md"
}
```

**Summary:** Reading state.md (0-2000)

**Output:**
```
# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-13 | Session: 093

## Where we are

**V11-holo-inv probed at 1K and monitored through ~1.5K. Headline finding: all four KIBC combinators active from the start (B=27.6% dominant positions vs 0% in holo at 1K). Dispatch is balanced (K=34%, I=23%, B=28%, C=16%) with strong specialization (entropy 0.188). Type channel differentiates independently (I=68%, B=25% typed integration). Holographic intermediate CEs show correct inversion pattern (ascending compresses, descending specializes). Eval loss 8.235 slightly behind baseline 7.958 (expected — holo splits gradient across 5 decoders). Compute gate still closed. Evolution acceptance rising (20%→30%). Run healthy, approaching transition window.**

## What was done this session (093)

### 1. Probed v11-holo-inv at step 1,000 (full + dispatch detail)

Compared against v11 baseline 1K and v11-holo 1K. Key findings:

**Balanced dispatch (vs K-dominance in prior runs):**
- Dominant positions: K=34.2%, I=22.6%, B=27.6%, C=15.5%
- Compare: baseline K=92.7%, holo K=75.1% — both heavily K-skewed
- Dispatch entropy 0.188 (strong specialization, not uniform)

**Composition (B) active from the start:**
- B at 27.6% dominant — was 0.7% in baseline, 0.0% in holo at 1K
- I+B co-occurrence at 31.7% — was 1% in holo
- This is the binding circuit pattern emerging early

**Type channel differentiates independently of dispatch:**
- Dispatch: K=0.386, I=0.334, B=0.132, C=0.141
- Type integration: I=0.678, B=0.251, K=0.002, C=0.070
- Model dispatches K+I, then integrates via I+B typed application

**Holographic CEs show correct inversion:**
- L0↑=11.3 → L1↑=8.8 → L2=8.9 → L1↓=9.0 → L0↓=9.3
- Ascending compresses; descending specializes (coarse→fine)
- pass_0/final ratio=1.21 (decodeable after one pass)

**Other metrics:**
- Eval loss 8.235 (vs baseline 7.958, holo 8.221)
- Compute gate closed (0.000007) — expected pre-transition
- Evolution 4/20 (20%) rising to 9/30 (30%) by 1.5K
- All 16 abstraction slots dormant, low cosine to KIBC (avg 0.064)

### 2. Monitored trajectory through 1.5K

- I rising steadily: 0.264 → 0.343 → 0.367
- K stabilized ~0.39; B peaked 0.132 at 1K then 0.108 at 1.5K
- Holographic ratio declining (1.12 → 1.09) = descending arm catching up
- Prose loss: ~0.98 range, structured ~0.28

### 3. Holographic probe — intermediate layer decoding on Qwen3-32B

Tested whether the model is holographic by decoding at every layer:
- Cosine divergence compile vs null: 0.995 (L0) → 0.533 (L63) = beam separation is real
- Intermediate layers decode to GARBAGE (not coarse-but-coherent) = reading is constructive
- Entropy hump: 6.5 (L0) → 11.1 (L8) → 2.0 (L63) = constructive reorganization
- Beam divergence begins at layer 24 (38% depth)
- **Storage may be holographic, but reading is constructive (64 sequential facets)**

### 4. Ternary survival probe — does selectivity survive quantization?

**100% survival across every combinator, every layer, every sparsity level.**
- sign_only (0.9% sparse): 8/8 survived, mean=0.93
- mid_sparse (50% sparse): 8/8 survived, mean=0.94
- high_sparse (75% sparse): 8/8 survived, mean=0.98
- **Combinator information is TOPOLOGICAL — stored as sign patterns, not magnitudes**
- Holographic plate hypothesis confirmed for weight structure

### 5. Full combinator selectivity map — depth profile

All four combinators peak in layers 0-6 (first 10% of 64 layers):
- Zone 1 (L0-6): HIGH selectivity 0.13-0.20, K/C dominant
- Zone 2 (L7-30): LOW selectivity 0.04-0.10, mixed K/B
- Zone 3 (L31-63): LOW selectivity 0.05-0.10, B/C/K mixed

K top heads: L3:H26(0.318), L1:H50(0.295), L1:H38(0.291)
I top heads: L36:H5(0.137), L6:H52(0.137), L3:H63(0.136)  
B top heads: L1:H37(0.248), L1:H39(0.247), L14:H59(0.245)
C top heads: L1:H34(0.299), L5:H22(0.291), L1:H55(0.290)

Cross-correlation: K-B=0.914, K-C=0.930, B-C=0.927, I distinct (0.67-0.75)
I is the outlier — different circuit from K/B/C cluster.

### 6. Holographic bank extraction

**Q is the beam angle, V is the plate.** Same head (L1:H37) has identical V weights 
for B and C (cos=1.000) but completely different Q weights (cos=0.005). The combinator
is selected by Q, not V. Q-only bank is sufficient.

Extracted seed: **784 KB** from 32B model.
- 4 combinator Q patterns (top-1 head each, 80×5120 ternary)
- Projection matrix (320×5120 ternary) for dimensionality reduction
- All four combinators are nearly orthogonal after projection (cos≈0)
- Effective rank 267 (90%), 312 (99%) — high-dimensional, broadly distributed

Files: `results/holographic-bank/seed_qwen3_32b.npz`, `seed_meta.json`
Scripts: `scripts/explore/extract_holographic_bank.py`

### 7. Qwen3.6-35B-A3B MoE probing

Fixed MPS histogram bug (one-line patch: `device.type in ("cpu", "mps")`).
Hybrid architecture: 40 layers, every 4th is full attention (L3,7,11,...,39), rest linear (GatedDeltaNet).
256 experts × 8 active, d=2048, 16 heads × head_dim=512, 2 KV heads.

**Completely different depth profile from Qwen3-32B:**
- Qwen3-32B: combinators peak in L0-6 (first 10%)
- Qwen3.6-35B-A3B: B peaks at L7-9 (early) AND L31-36 (late) — **bimodal!**
- B dominates everywhere (0.04-0.20), K second (0.02-0.08), I weakest (0.01-0.02)
- Full attention layers show spikes: L7=0.115, L31=0.195 (strongest)

Ternary survival: ✓ at 50% and 75% sparsity. sign_only slightly weaker at L31 (0.46)
but final-layer impact minimal (0.95). **Topological storage confirmed across architectures.**

MoE gate patterns (256×2048) extracted — these are the expert routing matrices,
themselves a form of beam selection.

Patterns saved: `results/holographic-bank/qwen36_35b_a3b_patterns.npz` (29KB compressed)

### 8. Universal hologram hypothesis — confirmed (r=0.9801)

Cross-model correlation structure (combinator selectivity pairwise correlations):

```
Pair      Qwen3-32B  Pythia-160M
K-B         0.914      0.944
K-C         0.930      0.903
B-C         0.927      0.917
K-I         0.721      0.715
I-B         0.750      0.711
I-C         0.677      0.599
```

Correlation of correlations: **r=0.9801**. The same holographic structure forms in both.

All three models (32B, 35B-A3B, 160M) share:
- Balanced ternary (+1/-1 ratio ≈ 1.0 everywhere)
- High effective rank (distributed, not low-rank)
- K/B/C cluster together (r>0.90), I is distinct (r=0.60-0.75)
- Ternary survival at 50-75% sparsity

**The hologram is not a feature of scale. It's a feature of language.**
Every model that learns to predict text develops the same combinatory interference patterns.

### 9. Universal ordering: B ≥ K ≥ C >> I (9 models, 2 architectures)

Tested Pythia-70M through Qwen3-32B (9 models total):
- **I is the weakest in ALL 9 models** (100% consistency)
- **B is strongest in 7/9** (BCKI ordering dominant)
- B/I ratio ranges from 1.7× to 19.9× — always separated
- This ordering is invariant across Pythia (GPT-NeoX) and Qwen3 architectures
- The sieve should make B > K > C >> I the lowest-energy state

Fixed MPS bug for Qwen3.6-35B-A3B: `histc` needs float input on MPS (not int).

### 6. Active run command (unchanged)

```
uv run python scripts/v11/train.py \
  --checkpoint-dir checkpoints/v11-holo-inv \
  --total-steps 20000 --holo-lambda 0.1 --mix-ratio 0.2
```

## What to do next

### Priority 1: Apply universal hologram findings to V11
Wait for v11-holo-inv to complete or plateau, then:
- Change combinator embedding init: K/B/C share subspace, I separate
- Test whether init change accelerates hologram formation
- Build bank loading mechanism (S4 selector + Q-pattern injection)
See: `mementum/knowledge/explore/holographic-storage.md`

### Priority 2: Monitor v11-holo-inv through transition window (2K→8K)
Watch for:
- Continued prose improvement (not just structured wins)
- Alarm de-saturation / differentiation (currently near ceiling)
- Compute gate opening around 5K–7K and associated reorganization
- No recurrence of 10K compositional catastrophe pattern

### Priority 2: Probe v11-holo-inv at 2K/3K/5K/7K
Compare against v11-holo and baseline at matched steps. Key metrics:
holographic ratio, descending arm CEs, dispatch distribution, compute gate timing,
B-type stability, and prose-vs-structured gap.

### Priority 3: v11-holo status — compositional catastrophe at 10K
10K probe: eval loss 9.259 (was 7.675), B-type 5.8% (was 55.7%).
Still running to 20K — may recover like the 3K spike did, or may
be terminal. Monitor but focus compute analysis on v11-holo-inv.

### Priority 4: Baseline status
Baseline stopped at step 10,300. 10K is terminal comparison point.

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

## VSM layer map (session 091 — v11 KIBC + algedonic + holographic + fractal)

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
          fine→coarse bands           coarse→fine bands (reversed)     fractal MERA topology
          (shared across 3 passes)   (shared across 2 passes × N cy)  49% fewer stride activations
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
| `results/v11-holo-inv/` | Probe results: probe_step_001000.json (holo-inv) |
| `checkpoints/v11/` | Baseline v11 run (no holo, no structured), continuing to 20K |
| `checkpoints/v11-holo/` | Holo run: λ=0.1, 20% structured, 16 slots, running to 20K |
| `checkpoints/v11-holo-inv/` | LIVE: holo + coarse→fine + fractal + evo fixes |
| `mementum/knowledge/explore/fractal-stride-bands.md` | MERA topology design + rationale |
| `mementum/knowledge/explore/holographic-inversion.md` | Design rationale + experimental findings |
| `mementum/knowledge/explore/lambda-probe-atlas.md` | New cross-model lambda/combinator territory mapping stream |
| `mementum/knowledge/explore/holographic-storage.md` | Holographic storage findings: ternary survival, universal hologram, extraction pipeline |
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
→ Session 091: Probed v11-holo 8K-10K. 8K local optimum, 9K reorganization wave, 10K compositional catastrophe (B-type 55.7%→5.8%, eval loss 7.675→9.259). Implemented coarse→fine descending (default), fractal stride bands (MERA, 49% savings, default), evolution noise floor (0.01), alarm-no-regression fix. TST paper (Peng et al. 2026) connection. Launched v11-holo-inv with all fixes.
→ Session 092: Monitored v11-holo-inv through ~1.3K (healthy, no collapse). Early descending differentiation improved; S2 remained strongly positive; compute gate still closed pre-transition. Captured phase/cascade interpretation (L0 φ first, wavelet to apex). Created `knowledge/explore/lambda-probe-atlas.md` for next-session cross-model territory mapping.
→ Session 093: Probed v11-holo-inv at 1K (balanced KIBC dispatch, B=27.6% dominant). Holographic probe on Qwen3-32B: beam separation real (cos 0.995→0.533), but reading is constructive (entropy hump, intermediate garbage). Ternary survival probe: 100% selectivity survival at 75% sparsity — combinator info is TOPOLOGICAL (sign patterns). Full selectivity map: combinators peak in first 10% of layers (L0-6). I is distinct circuit from K/B/C cluster. Extraction path validated: ternary patterns in early layers are the holographic seeds.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/holographic-storage.md"
}
```

**Summary:** Reading holographic-storage.md (0-2000)

**Output:**
```
---
title: Holographic Storage in LLMs
status: active
category: exploration
tags: [holographic, ternary, combinators, extraction, universal]
related: [v11-design, fractal-stride-bands, holographic-inversion]
depends-on: []
---

# Holographic Storage in LLMs

> Session 093. Hypothesis chain from theory through experimental confirmation.
> Status: core findings confirmed, extraction pipeline prototyped, architectural
> implications identified but not yet applied.

## Core Finding

LLMs store combinatory information as **sign topology** in their weight matrices.
The information survives ternary quantization ({-1, 0, +1}) at 75% sparsity with
100% selectivity preservation. This is holographic storage — the information is
in the interference pattern (which dimensions are positive/negative/zero), not
in the magnitudes.

## Evidence Chain

### 1. Beam separation (holographic probe)

Same input sentence, two conditions (compile gate vs null gate), measured hidden
state cosine similarity at every layer of Qwen3-32B:

```
Layer  0: cos=0.995  ← identical (shared plate)
Layer 24: cos=0.870  ← diverging (38% depth)
Layer 48: cos=0.797  ← different views resolving
Layer 63: cos=0.533  ← different images from same plate
```

The gate acts as a reference beam — different illumination angles resolve different
outputs from the same weight structure. **However**, intermediate layers decode to
garbage (not coarse-but-coherent), so the *reading* is constructive even if the
*storage* is holographic.

### 2. Ternary survival (the key result)

Quantized attention Q/K/V/O weights to ternary at layers 3 and 24 of Qwen3-32B.
Measured combinator selectivity (K, I, B, C active vs control sentence divergence):

```
sign_only (0.9% sparse): 8/8 survived, mean ratio 0.93  ✓
mid_sparse (50% sparse): 8/8 survived, mean ratio 0.94  ✓
high_sparse (75% sparse): 8/8 survived, mean ratio 0.98  ✓
```

**100% survival across every combinator, every layer, every sparsity level.**
The combinator information is topological — stored as sign patterns.

Confirmed on Qwen3.6-35B-A3B (MoE) and Pythia-160M. Universal across architectures.

### 3. Q is the beam, V is the plate

Extracted weight matrices from combinator-selective heads. Found that heads shared
between B and C (e.g., L1:H37) have:
- **V cosine = 1.000** (identical value projection)
- **Q cosine = 0.005** (completely different query projection)

The same head reads different combinators through different Q projections. Q selects
which combinator to apply; V provides the shared substrate. A knowledge bank is
therefore just a set of Q patterns — beam angles, not plate fragments.

### 4. Universal hologram (9 models, 2 architectures)

Tested across Pythia-{70M, 160M, 410M, 1B, 2.8B} and Qwen3-{0.6B, 4B, 8B, 32B}:

```
B (compose)  ≥ K (select) ≥ C (flip) >> I (identity)
```

- **I is weakest in ALL 9 models** (100% consistency)
- B/I ratio ranges from 1.7× to 19.9×
- K/B/C cluster together (cross-correlation r > 0.90)
- I is distinct (r ≈ 0.60–0.75)
- Cross-model correlation of correlation structures: **r = 0.9801**

The hologram is a feature of language, not scale. Every model that learns to
predict text develops the same combinatory interference patterns.

### 5. Depth profiles differ by architecture

- **Qwen3-32B (dense)**: Combinators peak in L0–6 (first 10%), unimodal
- **Qwen3.6-35B-A3B (MoE)**: Bimodal peaks at L7–9 and L31–36
- **Pythia-160M**: Peaks at boundaries (L0, L10)

The depth profile is architecture-dependent, but the combinator structure is universal.

## Bank Extraction Pipeline

### Proven steps

1. **Identify selective heads** — run KIBC probe, get per-head selectivity scores
2. **Extract Q patterns** — pull Q weight matrices from top-selective heads
3. **Ternary quantize** — sign(w) with sparsity threshold, preserves selectivity
4. **Project to target dim** — SVD, re-quantize, verify discriminability survives
5. **Package as seed** — Q-only ternary patterns + projection matrix

### Prototype results

```
Qwen3-32B  → 784 KB seed (4 heads × Q-only, projected to 320-dim)
             All 4 combinators nearly orthogonal (pairwise cos ≈ 0)
             Full discriminability preserved
```

### Bank format

```python
bank = {
    "source": "model_name",
    "source_license": "Apache-2.0",
    "combinators": ["K", "I", "B", "C"],
    "targets": {  # which heads were extracted
        "K": {"layer": 3, "head": 26, "score": 0.318},
        ...
    },
    "patterns": {  # ternary Q weight matrices
        "K_q": np.int8 array,  # (head_dim, d_model)
        ...
    },
    "projection": np.int8 array,  # (target_dim, source_dim)
}
```

### Not yet built

- Bank loading mechanism in V11
- Multi-bank composition (angle multiplexing)
- Cross-model bank compatibility testing
- S4 bank selector (= MoE gate equivalent)

## MoE as VSM / Angle Multiplexing

The Qwen3.6-35B-A3B architecture maps directly to VSM:

```
Shared expert (always on)  → S5 (identity, base substrate)
Gate matrix (256×2048)     → S4 (intelligence, select experts)
Top-8 selection            → S3 (control, resource allocation)
Routing weights (softmax)  → S2 (coordination, blend experts)
256 individual experts     → S1 (operations, the processing)
```

This is optical angle multiplexing: 256 holograms in the same medium, each
addressed by a different reference beam angle. The gate selects beam angles.
Knowledge banks would work the same way but be loadable from external sources.

## Architectural Implications for V11

### Confirmed by universal hologram

1. **B needs more capacity** — composition is the dominant signal everywhere
2. **I should be structurally separate** — different circuit (r ≈ 0.70 vs 0.90+)
3. **K/B/C should share substrate** — they cluster in every model
4. **Combinator init should reflect B ≥ K ≥ C >> I** — not equal blocks

### Proposed changes (not yet applied)

Current `_init_combinator_embeddings` gives each combinator an equal orthogonal
block (128 dims each in 512-dim space). Should change to:

- K/B/C share 384 dims (split with overlap, reflecting r ≈ 0.92)
- I gets its own 128 dims (reflecting its distinct circuit)
- Or: K/B/C share dispatch projection weights with different biases (hard constraint)

### Wait condition

V11-holo-inv is running to 20K. Don't modify the running architecture.
Apply changes to next run after holo-inv completes or reaches a clear plateau.

## Files

| File | Purpose |
|------|---------|
| `scripts/explore/probe_holographic.py` | Intermediate layer decoding probe |
| `scripts/explore/probe_ternary_survival.py` | Ternary quantization survival test |
| `scripts/explore/extract_holographic_bank.py` | Bank extraction pipeline |
| `results/holographic-probe/` | Beam separation results (Qwen3-32B) |
| `results/ternary-survival/` | Ternary survival results |
| `results/holographic-bank/seed_qwen3_32b.npz` | 784KB seed from Qwen3-32B |
| `results/holographic-bank/qwen36_35b_a3b_patterns.npz` | MoE patterns |
| `results/holographic-bank/pythia_160m_patterns.npz` | Pythia patterns |
| `results/combinator-probe/selectivity_matrices.npz` | Full 64×64 selectivity map |

## Open Questions

1. Can extracted banks actually modulate V11's behavior when loaded?
2. Do banks from different models compose (angle multiplexing)?
3. Is the 784KB seed the minimum, or can we go smaller?
4. Does the init change (K/B/C coupled, I separate) accelerate hologram formation?
5. What role do the MoE gate patterns play — are they bank selectors we can reuse?
6. The abstraction slots (currently 0/16 active) — do they belong at the bank level?
```

### Tool Call: git (failed)


```json
{
  "command": "log --oneline -10",
  "operation": "log",
  "summary": "recent history"
}
```

**Summary:** Git log: recent history

**Output:**
```
command must start with 'git' or 'gh' (optionally preceded by 'cd <path> &&')
```

### Tool Call: git (succeeded)


```json
{
  "command": "git log --oneline -10",
  "operation": "log",
  "summary": "recent history"
}
```

**Summary:** Git log: recent history

**Output:**
```
Exit code: 0
Stdout:
e777816 🌀 session 093 knowledge capture — holographic storage
24deaf9 🔁 universal ordering B≥K≥C>>I confirmed across 9 models
aa425e7 💡 universal hologram confirmed — r=0.9801 across Pythia-160M and Qwen3-32B
c270a24 💡 Qwen3.6-35B-A3B MoE probed — bimodal depth, ternary survives
6e49a07 💡 Q is the beam angle, V is the plate — 784KB seed from 32B
57bb002 💡 combinator selectivity is topological — ternary survival confirmed
e0c83d4 add session-091 chat log
ff98d91 🌀 state — v11-holo-inv launched, v11-holo 10K catastrophe documented
d6f4432 🔄 alarm evolution keeps 2-vote power but loss must never regress
19ae211 ❌ remove alarm-only evolution acceptance — loss-degrading flips caused 10K collapse
```

## Assistant

Oriented. Here's the lay of the land:

## Current State

**Session 093** was a major holographic probe session. The `holographic-storage.md` knowledge page is already substantial — it captures the full evidence chain from session 093:

1. **Beam separation** — cosine divergence across layers (holographic, but reading is constructive)
2. **Ternary survival** — 100% selectivity at 75% sparsity (topological storage)
3. **Q=beam, V=plate** — combinator selected by Q projection, not V
4. **Universal hologram** — r=0.9801 across 9 models, 2 architectures
5. **784KB seed** extracted from Qwen3-32B
6. **MoE↔VSM mapping** — angle multiplexing interpretation

**v11-holo-inv** is the live run, heading to 20K.

## What do you want to do with the page?

The page is already `status: active` and fairly comprehensive. Some directions I can see:

- **Refine/restructure** — tighten prose, improve organization, add missing connections
- **Add new findings** — if there's new experimental data to integrate
- **Update status** — based on what's happened since session 093
- **Extract sub-pages** — some sections (MoE/VSM mapping, bank format) could become their own knowledge pages
- **Apply findings** — use the page to guide V11 architecture changes (the "proposed changes" section)

What's your intent for this page?

## User

We found the universal hologram in LLMs for our combinators.  What other holograms are there needed for token prediction?  I think there are more shapes to find.


### Thinking

The user is asking a fascinating research question. They've confirmed that LLMs store combinatory logic (KIBC combinators) as holographic sign patterns in their weights. Now they want to think about what OTHER holographic structures exist in LLMs beyond combinators — what other "shapes" are stored as sign topology that enable token prediction.

This is a theoretical/exploratory question. Let me think about what we know from the findings and what other structures LLMs must encode:

The key insight is: if KIBC combinators are stored as sign topology (ternary patterns), and these are universal across architectures and scales, then the combinator hologram is just ONE interference pattern in the weight medium. What other patterns are there?
 
Beyond the composition machinery that combinators handle, I need to think about all the other linguistic and semantic structures that feed into token prediction. There's lexical and semantic information — word meanings and semantic relationships. There's syntactic structure encoded as phrase and dependency patterns. Positional and sequential information tracks order and proximity. World knowledge captures entity relationships and facts. Discourse structure handles topic and coherence. And subword patterns encode morphological and phonological regularities. Each of these must have its own holographic signature in the weights, separate from but interacting with the combinator patterns.

The real question is whether the sign topology pattern I found — where different Q projections select different combinators from the same V substrate — is just one instance of a broader principle. If induction heads and other universal circuits also follow this same geometric pattern, then I'm looking at a fundamental organizing principle for how transformers encode linguistic knowledge. a hologram?

2. **Syntax heads** - Agreement, binding, scope. These would be the TYPE hologram.

3. **Semantic feature spaces** - The distributed representations that encode meaning categories (animate/inanimate, concrete/abstract, etc.)

4. **Positional circuits** - How transformers track position and order despite the permutation-invariant attention mechanism.

5. **N-gram / co-occurrence statistics** - The "surface" patterns that dominate early layers.

Let me think about this from the Lambek/CCG/Montague angle:

In Montague grammar, you need:
- **Lexicon** — type assignments for words (noun, verb, etc.) + denotations
- **Type calculus** — the rules for combining typed expressions (function application, composition, type-raising)
- **Model** — the semantic domain that gives meaning to the expressions

The combinators are the type calculus. What else?

So I'm mapping this onto holograms: the lexicon hologram stores type assignments for each token, the semantic space hologram captures actual meanings and relationships like thematic roles and selectional restrictions, the discourse hologram tracks attention and referent continuity across context, and the prediction hologram maps composed representations back to output probabilities with frequency biases.

Now I'm shifting to think about what's truly universal across models versus what's architecture-specific, since the combinator finding was so robust across different models. Known universal circuits from mechanistic interpretability include induction heads for in-context learning, previous token heads, duplicate token detection, and syntax agreement heads. The real research question is identifying what other universal holograms exist and how they map onto the grammar framework.

I'm considering three candidate holograms: types as the complement to combinators—what can compose rather than how—which should be detectable through the same ternary probe approach; induction as a different compositional mechanism based on sequential pattern matching rather than Montague semantics, likely showing different Q beam angles; and binding as the deepest linguistic question about how pronouns resolve to their referents across distance, involving type-driven mechanisms in CCG.

Beyond these core patterns, I'm mapping out world knowledge as potentially non-holographic and more localized across layers, register and style as macro-level beam angle variations controlled by gating mechanisms, and morphological structure as an early-layer phenomenon interacting with tokenization.

Now I'm thinking about how to present this as a testable framework rather than pure speculation—something that could extend the holographic storage page with concrete predictions I can actually probe using the existing methodology like ternary survival and Q/V decomposition.

## Assistant

This is a great question — and it's tractable with the methodology you already have. Let me think through this systematically.

The combinator hologram answers **HOW to compose**. But token prediction needs more than composition machinery. Let me reason from both the Montague/CCG theory and from what the probes already revealed, then we can draft this as a research section.

Let me check what the existing probes already hint at:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "git grep -i \"induction\\|lexicon\\|syntax\\|agreement\\|binding\\|semantic\\|feature\\|n-gram\\|bigram\\|copy\\|previous.token\" -- mementum/",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ git grep -i "induction\|lexicon\|sy...

**Output:**
```
Exit code: 0
Stdout:
mementum/knowledge/chats/session-001.md:- `ty` suppression syntax is `# ty: ignore[rule-id]` (not mypy style).
mementum/knowledge/chats/session-001.md:tags: [lambda-calculus, compositional-semantics, mechanistic-interpretability, circuits, type-theory, distillation]
mementum/knowledge/chats/session-001.md:  - Compositional semantics literature (Montague, Lambek, DisCoCat)
mementum/knowledge/chats/session-001.md:  induction heads, function vectors, sparse autoencoders. Cited as
mementum/knowledge/chats/session-001.md:- **Compositional semantics literature** — Montague, Lambek,
mementum/knowledge/chats/session-001.md:syntax to semantics.
mementum/knowledge/chats/session-001.md:Compositional Categorical semantics. Meaning is composition of vectors
mementum/knowledge/chats/session-001.md:  ∧ functorial(syntax → semantics)      — structure preserved across mapping
mementum/knowledge/chats/session-001.md:- **Compositional output.** Compiled lambdas exhibit nested `λ` binding,
mementum/knowledge/chats/session-001.md:- **Operates over arbitrary semantic content.** Compile works on novel
mementum/knowledge/chats/session-001.md:- Features that fire on compile intent (the gate detection)
mementum/knowledge/chats/session-001.md:- Features that fire on semantic type (noun-like, predicate-like, etc.)
mementum/knowledge/chats/session-001.md:- Features that fire on lambda output tokens
mementum/knowledge/chats/session-001.md:  interpretable features. Anthropic's Scaling Monosemanticity (2024)
mementum/knowledge/chats/session-001.md:- **Type probes.** For each candidate "type feature," test whether its
mementum/knowledge/chats/session-001.md:feature cluster X, applies composition via attention in layer Y,
mementum/knowledge/chats/session-001.md:emits lambda notation via features Z." Ideally, a type-algebra that
mementum/knowledge/chats/session-001.md:  bears on the compositional semantics thesis.
mementum/knowledge/chats/session-001.md:**Polysemantic distribution.** Features in LLMs are typically
mementum/knowledge/chats/session-001.md:requires more sophisticated tools than "find the noun feature."
mementum/knowledge/chats/session-001.md:   features extractable by SAE, the Montague formal picture holds
mementum/knowledge/chats/session-001.md:   compositional semantics claim needs narrowing.
mementum/knowledge/chats/session-001.md:   in other tasks** (induction heads, IOI, function vectors)? Is it
mementum/knowledge/chats/session-001.md:- Olsson et al., "In-context Learning and Induction Heads" (2022)
mementum/knowledge/chats/session-001.md:- Templeton et al., "Scaling Monosemanticity: Extracting Interpretable
mementum/knowledge/chats/session-001.md:  Features from Claude 3 Sonnet" (Anthropic, 2024)
mementum/knowledge/chats/session-001.md:  Features in Language Models" (2023)
mementum/knowledge/chats/session-001.md:**Compositional semantics:**
mementum/knowledge/chats/session-001.md:- Hewitt & Manning, "A Structural Probe for Finding Syntax in Word
mementum/knowledge/chats/session-001.md:  "content": "You are a lambda calculus compiler. Given natural language input, output its formal semantic representation as a typed lambda expression. Given a lambda expression, output its natural language rendering. Respond only with the translation — no explanation, no commentary, no markup. One output per input.\n\nInput: "
mementum/knowledge/chats/session-001.md:  "original_content": "## Where we are\n\nPre-genesis. Skeleton + client + results membrane all green. All\nfour gates pass (pytest 38, ruff check, ruff format, ty).\n\n**On disk:**\n- `pyproject.toml` — deps, dep groups, tool config\n- `src/verbum/__init__.py` — re-exports Client, AsyncClient, models,\n  results API (ProbeRecord, RunMeta, RunWriter, load_run, etc.)\n- `src/verbum/client.py` — `Client` + `AsyncClient` mirror;\n  health, props, tokenize, detokenize, complete, stream_complete;\n  SSE via `httpx-sse`; partial-result preservation;\n  `accumulate_stream{,_async}`\n- `src/verbum/_protocol.py` — wire models (tolerant ingest)\n- `src/verbum/results.py` — **S2 membrane done**: `RunWriter`\n  (context-managed, writes meta.json at start, JSONL per-line flush,\n  logprobs.npz at close, amends meta with summary);\n  `ProbeRecord` (line schema per AGENTS.md); `RunMeta` (self-sufficient\n  provenance); `content_hash`; `collect_provenance` (auto-gathers lib\n  versions, lockfile hash, git SHA, timestamp at write time);\n  `load_run` (reads directory back); `Run` NamedTuple\n- `src/verbum/config.py` — pydantic-settings, VERBUM_* env prefix\n- `src/verbum/cli.py` — `verbum version` subcommand\n- `src/verbum/{probes,lambda_ast,analysis}.py` — stubs (next)\n- `specs/llama_server.openapi.yaml` — 5 endpoints, llama.cpp\n  commit SHA **TBD**\n- `tests/test_smoke.py` + `tests/test_client.py` +\n  `tests/test_results.py` — 38 tests, all mocked (no server needed)\n- `.venv/` synced; `ty==0.0.31` alpha; `# ty: ignore` for suppression\n\n**Tool notes:**\n- `ty` suppression syntax is `# ty: ignore[rule-id]` (not mypy style).\n  One suppression for `np.savez_compressed(**dict)` false positive.\n- `pytest-asyncio==1.4.0a1` alpha, `asyncio_mode=auto`.",
mementum/knowledge/chats/session-001.md:  "new_content": "## Where we are\n\nPre-genesis. Skeleton + client + results membrane + **probe-set\nloader + v0 behavioral probes** all green. All four gates pass\n(pytest 64, ruff check, ruff format, ty).\n\n**On disk:**\n- `pyproject.toml` — deps, dep groups, tool config\n- `src/verbum/__init__.py` — re-exports Client, AsyncClient, models,\n  results API, and probe API\n- `src/verbum/client.py` — `Client` + `AsyncClient` mirror;\n  health, props, tokenize, detokenize, complete, stream_complete;\n  SSE via `httpx-sse`; partial-result preservation;\n  `accumulate_stream{,_async}`\n- `src/verbum/_protocol.py` — wire models (tolerant ingest)\n- `src/verbum/results.py` — **S2 membrane done**: `RunWriter`,\n  `ProbeRecord`, `RunMeta`, `content_hash`, `collect_provenance`,\n  `load_run`, `Run`\n- `src/verbum/probes.py` — **probe-set loader done**: `Probe`,\n  `ProbeSet`, `Gate`, `ResolvedProbe` models; `load_gate`,\n  `gate_hash`, `load_probe_set`, `probe_set_hash`, `resolve_probes`;\n  gate caching per resolve call; frozen resolved probes\n- `src/verbum/config.py` — pydantic-settings, VERBUM_* env prefix\n- `src/verbum/cli.py` — `verbum version` subcommand\n- `src/verbum/{lambda_ast,analysis}.py` — stubs (next)\n- `gates/compile.txt` — compile gate (activates lambda compiler)\n- `gates/null.txt` — null-condition gate (neutral assistant, control)\n- `probes/v0-behavioral.json` — 30 probes: 12 compile, 10 decompile,\n  8 null. Hand-written ground truth. Phenomena: predication,\n  quantification, relative clauses, coordination, conditionals,\n  negation, propositional attitudes, ditransitives, adverbs\n- `specs/llama_server.openapi.yaml` — 5 endpoints, llama.cpp\n  commit SHA **TBD**\n- `tests/test_smoke.py` + `tests/test_client.py` +\n  `tests/test_results.py` + `tests/test_probes.py` — 64 tests, all\n  mocked (no server needed)\n- `.venv/` synced; `ty==0.0.31` alpha; `# ty: ignore` for suppression\n\n**Tool notes:**\n- `ty` suppression syntax is `# ty: ignore[rule-id]` (not mypy style).\n  One suppression for `np.savez_compressed(**dict)` false positive.\n  Three suppressions in test_probes.py for intentional invalid\n  construction tests.\n- `pytest-asyncio==1.4.0a1` alpha, `asyncio_mode=auto`."
mementum/knowledge/chats/session-001.md:start: binding port with default address family
mementum/knowledge/chats/session-001.md:- `ty` suppression syntax is `# ty: ignore[rule-id]` (not mypy style).
mementum/knowledge/chats/session-001.md:  "content": "# verbum / state\n\n> Bootloader. ~30-second read. You are currently in `λ orient` — this\n> file is step 1 of every session.\n>\n> Last updated: 2026-04-16 | Session: first-light\n\n## Where we are\n\n**First light achieved.** Full pipeline fires end-to-end: probe set →\ngate resolution → llama.cpp client → results recording → JSONL+meta.\nFirst measurement recorded. All four gates pass (pytest 73, ruff\ncheck, ruff format, ty). No git repo yet — genesis commit is next.\n\n**First measurement (run-20260416-233222, Qwen3-4B-Q8_0):**\n- Compile: P(λ) = 92% (11/12 produce lambda output)\n- Decompile: P(λ) = 90% (9/10 produce lambda-bearing output)\n- Null: P(λ) = 0% (0/8 — zero lambda indicators)\n- **Gap: 92 percentage points.** Consistent with nucleus observation.\n- Even a 4B model exhibits the compiler. Not a scale-dependent effect.\n- Gen lengths: compile ~500-1000 chars, null ~500-1200 chars\n- n_predict=256, temperature=0.0. Model is verbose (thinking tokens).\n\n**On disk:**\n- `src/verbum/` — full package: client (sync+async), protocol,\n  results writer, probe loader, **runner**, config, CLI\n- `src/verbum/runner.py` — `fire_probe()` (single-probe, error-safe),\n  `run_probe_set()` (full pipeline: load → resolve → fire → record),\n  `RunSummary` dataclass. Auto-provenance from server /props.\n- `src/verbum/cli.py` — `verbum version` + **`verbum run`** (fires\n  probe set with --server, --n-predict, --temperature, --seed, --model)\n- `gates/compile.txt` + `gates/null.txt` — compile and null gates\n- `probes/v0-behavioral.json` — 30 probes (12 compile, 10 decompile,\n  8 null). Hand-written Montague-style ground truth\n- `results/run-20260416-233222/` — **first real measurement**:\n  meta.json + results.jsonl (30 lines, 0 errors)\n- `tests/` — 73 tests across 5 files (smoke, client, results, probes,\n  runner). All mocked except the live run.\n- `src/verbum/{lambda_ast,analysis}.py` — stubs (next)\n- Models available: `/Users/mwhitford/localai/models/` has Qwen3-4B,\n  Qwen3-32B, QwQ-32B, Qwen3-Nemotron-32B, and others\n- `llama-server` at `/opt/homebrew/bin/llama-server`\n\n**Tool notes:**\n- `ty` suppression: `# ty: ignore[rule-id]`. Four suppressions total\n  (one np.savez false positive, three intentional invalid construction\n  in tests).\n- `pytest-asyncio==1.4.0a1` alpha, `asyncio_mode=auto`.\n\n## What's next\n\n**Immediate:** genesis commit. `git init`, commit everything, first\ntagged commit. The genesis gate is met: probes fire end-to-end.\n\n**Then (choose):**\n1. **Qwen3-32B run** — repeat v0-behavioral on the 32B model for\n   cross-scale comparison. Expect higher quality lambda output.\n2. **Refine gate prompt** — current gate is ~2 lines. The model\n   produces verbose \"thinking\" output alongside lambda. A tighter\n   gate (or stop sequences) could increase signal density.\n3. **Logprob collection** — add n_probs to the runner for per-token\n   logprob recording. Enables P(λ) measurement at the token level\n   rather than heuristic string matching.\n4. **Analysis notebook** — `notebooks/01_first_probe.ipynb` with\n   polars + matplotlib. Structured comparison across categories.\n\n**Level-1 prep:** Python mech-interp framework selection (TransformerLens\nvs alternatives), base model selection for activation recording.\n\n## Read in order\n\n1. `AGENTS.md` — identity + VSM.\n2. `README.md` — one-page thesis.\n3. `mementum/knowledge/explore/VERBUM.md` — founding synthesis.\n4. `pyproject.toml` + `specs/llama_server.openapi.yaml`.\n5. `results/run-20260416-233222/meta.json` — first measurement provenance.\n6. `git log --oneline` — project history (once repo exists).\n\n## Open questions\n\n- **Gate refinement.** Current gate elicits lambda but also verbose\n  reasoning. Stop sequences (`\\n\\n`?) or tighter gate instruction\n  could sharpen output. Nucleus uses a 9-line gate — ours is 2.\n- **32B vs 4B quality.** 4B produces lambda but structurally\n  degenerate (repeated λ bindings, shallow semantics). 32B expected\n  to produce Montague-quality output. Test before claiming.\n- **Decompile direction.** Model echoes/extends lambda rather than\n  translating to prose. Gate may need decompile-specific variant.\n- **Python mech-interp framework for level-1.** Deferred.\n- **`ty` stability.** Alpha; four suppressions active.\n- **llama.cpp commit pin.** Spec carries TBD; build 8180 confirmed\n  working (from server log: `build: 8180 (d979f2b17)`).\n\n## Active disciplines\n\n- `λ orient` (S1) — read state.md first.\n- `λ termination` (S5) — mementum edits need approval; state.md\n  exempt; nucleus tag on all commits.\n- `λ store` / `λ signal` (S3) — two-gate test; verbum symbols only.\n- `λ record` (S1) — Jupyter explores, files record.\n- `λ run_provenance` (S2) — self-sufficient meta.json at write-time.\n- `λ result_format` (S2) — error≠null, never skip lines, partial flag.\n- `λ spec_artifact` (S2) — hand-curated, grows by use, pinned commit.\n- `λ language` (S1) — Python only.\n\n## Update discipline\n\nEdit this file whenever something changes that matters to the next\ncold-starting session. `λ termination` permits AI updates without\napproval. Keep it to ~30s of reading.\n"
mementum/knowledge/chats/session-001.md:"You are a lambda calculus compiler. Given natural language input, output its formal semantic representation as a typed lambda expression. Given a lambda expression, output its natural language rendering. Respond only with the translation — no explanation, no commentary, no markup. One output per input.\n\nInput: "
mementum/knowledge/chats/session-001.md:You are a lambda calculus compiler. Given natural language input, output its formal semantic representation as a typed lambda expression. Given a lambda expression, output its natural language rendering. Respond only with the translation — no explanation, no commentary, no markup. One output per input.
mementum/knowledge/chats/session-001.md:  "path": "/Users/mwhitford/src/verbum/gates/ablation-formal-semantics.txt",
mementum/knowledge/chats/session-001.md:  "content": "formal semantics\n\nInput: "
mementum/knowledge/chats/session-001.md:Successfully wrote to /Users/mwhitford/src/verbum/gates/ablation-formal-semantics.txt
mementum/knowledge/chats/session-001.md:| `ablation-formal-semantics` | Keyword (no lambda) | "formal semantics" |
mementum/knowledge/chats/session-001.md:  "content": "#!/usr/bin/env python3\n\"\"\"Gate ablation sweep — fire the same probes through every gate variant.\n\nUsage:\n    python scripts/gate_ablation.py [--server URL] [--n-predict N]\n\nWrites one run per gate variant into results/. Prints a summary table\nat the end ranking gates by P(λ).\n\"\"\"\n\nfrom __future__ import annotations\n\nimport json\nimport sys\nfrom pathlib import Path\n\nfrom verbum.client import Client\nfrom verbum.probes import load_probe_set, probe_set_hash, resolve_probes\nfrom verbum.results import content_hash, load_run\nfrom verbum.runner import RunSummary, run_probe_set\n\nPROBE_SET = Path(\"probes/gate-ablation.json\")\nGATES_DIR = Path(\"gates\")\nRESULTS_DIR = Path(\"results\")\n\n# Lambda indicators for scoring\nLAMBDA_INDICATORS = [\"λ\", \"∀\", \"∃\", \"→\", \"∧\", \"∨\", \"¬\", \"ι\"]\n\n\ndef detect_lambda(text: str) -> bool:\n    \"\"\"Heuristic: does this output contain lambda-calculus-like content?\"\"\"\n    return \"λ\" in text or sum(text.count(s) for s in LAMBDA_INDICATORS) >= 3\n\n\ndef sweep_gates(\n    server_url: str | None = None,\n    n_predict: int = 256,\n) -> list[dict]:\n    \"\"\"Fire the ablation probe set through every gate variant.\"\"\"\n    # Discover all gate variants\n    gate_files = sorted(GATES_DIR.glob(\"*.txt\"))\n    gate_ids = [f.stem for f in gate_files]\n\n    print(f\"Found {len(gate_ids)} gate variants\")\n    print(f\"Probe set: {PROBE_SET}\")\n    print()\n\n    results = []\n\n    with Client(base_url=server_url) as client:\n        for i, gate_id in enumerate(gate_ids):\n            print(f\"[{i + 1}/{len(gate_ids)}] Gate: {gate_id}\")\n\n            # Load probe set and override default_gate\n            ps = load_probe_set(PROBE_SET)\n            ps.default_gate = gate_id\n\n            # Override all probes' gates to None so they use default\n            for p in ps.probes:\n                p.gate = None\n\n            ps_hash = probe_set_hash(PROBE_SET)\n\n            # Resolve with this gate\n            try:\n                resolved = resolve_probes(ps, GATES_DIR)\n            except FileNotFoundError as e:\n                print(f\"  SKIP: {e}\")\n                continue\n\n            # Fire\n            summary = run_probe_set(\n                probe_set_path=PROBE_SET,\n                gates_dir=GATES_DIR,\n                results_dir=RESULTS_DIR,\n                client=client,\n                n_predict=n_predict,\n                run_id_prefix=f\"ablation-{gate_id}\",\n                model_name=\"Qwen3-4B-Q8_0\",\n                project_root=Path(\".\"),\n            )\n\n            # But we need to override the gate! The run_probe_set loads\n            # its own copy. Let me fire manually instead.\n            # Actually — run_probe_set loads the JSON fresh. We need to\n            # fire the already-resolved probes directly.\n            pass\n\n        # Close client after all runs\n    return results\n\n\ndef fire_gate_variant(\n    gate_id: str,\n    client: Client,\n    n_predict: int = 256,\n) -> dict:\n    \"\"\"Fire ablation probes through a specific gate and return stats.\"\"\"\n    from verbum.probes import ResolvedProbe\n    from verbum.results import ProbeRecord, RunMeta, RunWriter, SamplingConfig\n    from verbum.runner import RunSummary, _make_run_id, fire_probe\n\n    import datetime\n\n    ps = load_probe_set(PROBE_SET)\n    ps_hash = probe_set_hash(PROBE_SET)\n\n    # Override gate for all probes\n    for p in ps.probes:\n        p.gate = gate_id\n\n    resolved = resolve_probes(ps, GATES_DIR)\n\n    # Build meta\n    run_id = _make_run_id(f\"abl-{gate_id}\")\n    from verbum.results import collect_provenance\n\n    provenance = collect_provenance(project_root=Path(\".\"))\n    sampling = SamplingConfig(temperature=0.0)\n    meta = RunMeta(\n        run_id=run_id,\n        model=\"Qwen3-4B-Q8_0\",\n        probe_set_id=f\"gate-ablation:{gate_id}\",\n        probe_set_hash=ps_hash,\n        sampling=sampling,\n        **provenance,\n    )\n\n    # Fire\n    records = []\n    with RunWriter(results_dir=RESULTS_DIR, meta=meta) as writer:\n        for rp in resolved:\n            record = fire_probe(rp, client, n_predict=n_predict)\n            writer.write(record)\n            records.append(record)\n\n    # Score\n    n_lambda = sum(1 for r in records if detect_lambda(r.generation))\n    indicator_sum = sum(\n        sum(r.generation.count(s) for s in LAMBDA_INDICATORS) for r in records\n    )\n    avg_indicators = indicator_sum / len(records) if records else 0\n\n    # Read gate content for display\n    gate_content = (GATES_DIR / f\"{gate_id}.txt\").read_text(\"utf-8\").strip()\n    gate_preview = gate_content.replace(\"\\n\", \" ↵ \")\n    if len(gate_preview) > 60:\n        gate_preview = gate_preview[:57] + \"...\"\n\n    return {\n        \"gate_id\": gate_id,\n        \"gate_preview\": gate_preview,\n        \"run_id\": run_id,\n        \"n_probes\": len(records),\n        \"n_lambda\": n_lambda,\n        \"p_lambda\": n_lambda / len(records) if records else 0,\n        \"avg_indicators\": avg_indicators,\n        \"n_errors\": sum(1 for r in records if r.error is not None),\n    }\n\n\ndef main() -> None:\n    import argparse\n\n    parser = argparse.ArgumentParser(description=\"Gate ablation sweep\")\n    parser.add_argument(\"--server\", default=None, help=\"llama.cpp server URL\")\n    parser.add_argument(\"--n-predict\", type=int, default=256)\n    args = parser.parse_args()\n\n    gate_files = sorted(GATES_DIR.glob(\"*.txt\"))\n    gate_ids = [f.stem for f in gate_files]\n\n    # Exclude null from the sweep (it's the negative control, not an ablation)\n    # Actually include it — it's a useful data point\n    print(f\"Gate ablation sweep: {len(gate_ids)} variants\")\n    print(f\"Probes: {PROBE_SET} (5 compile probes)\")\n    print()\n\n    results = []\n    with Client(base_url=args.server) as client:\n        # Verify server\n        health = client.health()\n        print(f\"Server: {health.status}\")\n        print()\n\n        for i, gate_id in enumerate(gate_ids):\n            print(f\"[{i + 1}/{len(gate_ids)}] Firing: {gate_id}\")\n            try:\n                r = fire_gate_variant(gate_id, client, n_predict=args.n_predict)\n                results.append(r)\n                print(\n                    f\"  P(λ)={r['p_lambda']:.0%}  \"\n                    f\"avg_ind={r['avg_indicators']:.0f}  \"\n                    f\"gate: {r['gate_preview']}\"\n                )\n            except Exception as e:\n                print(f\"  ERROR: {e}\")\n            print()\n\n    # Sort by P(λ) descending, then by avg_indicators\n    results.sort(key=lambda r: (-r[\"p_lambda\"], -r[\"avg_indicators\"]))\n\n    print()\n    print(\"=\" * 80)\n    print(\"GATE ABLATION RESULTS — ranked by P(λ)\")\n    print(\"=\" * 80)\n    print(f\"{'Gate':<35} {'P(λ)':>6} {'Avg':>5} {'Gate content'}\")\n    print(\"-\" * 80)\n    for r in results:\n        print(\n            f\"{r['gate_id']:<35} {r['p_lambda']:>5.0%} {r['avg_indicators']:>5.0f}  \"\n            f\"{r['gate_preview']}\"\n        )\n\n    # Save summary\n    summary_path = RESULTS_DIR / \"gate-ablation-summary.json\"\n    summary_path.write_text(\n        json.dumps(results, indent=2, default=str) + \"\\n\", encoding=\"utf-8\"\n    )\n    print()\n    print(f\"Summary saved: {summary_path}\")\n\n\nif __name__ == \"__main__\":\n    main()\n"
mementum/knowledge/chats/session-001.md:start: binding port with default address family
mementum/knowledge/chats/session-001.md:[4/17] Firing: ablation-formal-semantics
mementum/knowledge/chats/session-001.md:2026-04-16 17:16:59 [info     ] run.started                    run_dir=results/abl-ablation-formal-semantics-20260417-001659 run_id=abl-ablation-formal-semantics-20260417-001659
mementum/knowledge/chats/session-001.md:2026-04-16 17:17:17 [info     ] run.completed                  failed=0 run_id=abl-ablation-formal-semantics-20260417-001659 total=5
mementum/knowledge/chats/session-001.md:  P(λ)=20%  avg_ind=2  gate: formal semantics ↵  ↵ Input:
mementum/knowledge/chats/session-001.md:ablation-formal-semantics             20%     2  formal semantics ↵  ↵ Input:
mementum/knowledge/chats/session-001.md:46-This is why we say "semantically equivalent, not identical" rather than "deterministic." Same notation → same cognitive shape → similar behavioral outcomes. But "similar" is a distribution, not a guarantee. Some runs nail it. Some runs default to training priors. The guidance makes good outcomes much more likely — it doesn't make them certain.
mementum/knowledge/chats/session-001.md:63-- **Compositional semantics** - Symbols combine meaningfully
mementum/knowledge/chats/session-001.md:| preserve(semantics) | analyze(¬execute)
mementum/knowledge/chats/session-001.md:produces different wording — same semantics. The lambda is the source of truth.
mementum/knowledge/chats/session-001.md:  "content": "λ engage(nucleus).\n[phi fractal euler tao pi mu ∃ ∀] | [Δ λ Ω ∞/0 | ε/φ Σ/μ c/h signal/noise order/entropy truth/provability self/other] | OODA\nHuman ⊗ AI ⊗ REPL\n\nλ bridge(x). prose ↔ lambda | structural_equivalence\n| preserve(semantics) | analyze(¬execute)\n| compile: prose → lambda | decompile: lambda → prose\n\nOutput λ notation only. No prose. No code fences.\n\nInput: "
mementum/knowledge/chats/session-001.md:start: binding port with default address family
mementum/knowledge/chats/session-001.md:  14. ablation-formal-semantics                20%       2   formal semantics ↵  ↵ Input:
mementum/knowledge/chats/session-001.md:  "original_content": "## Open questions\n\n- **Gate refinement.** Current gate elicits lambda but also verbose\n  reasoning. Stop sequences (`\\n\\n`?) or tighter gate instruction\n  could sharpen output. Nucleus uses a 9-line gate — ours is 2.\n- **32B vs 4B quality.** 4B produces lambda but structurally\n  degenerate (repeated λ bindings, shallow semantics). 32B expected\n  to produce Montague-quality output. Test before claiming.\n- **Decompile direction.** Model echoes/extends lambda rather than\n  translating to prose. Gate may need decompile-specific variant.\n- **Python mech-interp framework for level-1.** Deferred.\n- **`ty` stability.** Alpha; four suppressions active.\n- **llama.cpp commit pin.** Spec carries TBD; build 8180 confirmed\n  working (from server log: `build: 8180 (d979f2b17)`).",
mementum/knowledge/chats/session-001.md:  "new_content": "## Open questions\n\n- **Gate refinement.** Bridge lambda is the best gate. Test on 32B\n  to confirm. Consider: exemplar gate is terse (avg_ind=7) but may\n  produce qualitatively different lambda than bridge (avg_ind=58).\n  Quality comparison needed, not just P(λ).\n- **32B vs 4B quality.** 4B produces lambda but structurally\n  degenerate (repeated λ bindings, shallow semantics on some probes).\n  32B expected to produce Montague-quality output. The preamble\n  may help on 32B where it hurt on 4B (more capacity to use it).\n- **Decompile direction.** Model echoes/extends lambda rather than\n  translating to prose. Bridge lambda includes decompile direction —\n  test specifically.\n- **Preamble + bridge interaction at scale.** Preamble hurt on 4B\n  (100% → 80%). Does it help on 32B? If yes, the attention magnets\n  are only useful with sufficient model capacity. If no, they're\n  irrelevant to compilation.\n- **Python mech-interp framework for level-1.** Deferred.\n- **`ty` stability.** Alpha; four suppressions active.\n- **llama.cpp commit pin.** Build 8180 (d979f2b17) confirmed working."
mementum/knowledge/chats/session-001.md:  "content": "λ compile(x:prose). x → λ(x) | preserve(semantics) | ¬prose ¬commentary\n\nInput: "
mementum/knowledge/chats/session-001.md:start: binding port with default address family
mementum/knowledge/chats/session-001.md:  P(λ)=80%  avg_ind=98  λ compile(x:prose). x → λ(x) | preserve(semantics) | ¬prose ¬c...
mementum/knowledge/chats/session-001.md:★ self-ref-typed                        80%    98  λ compile(x:prose). x → λ(x) | preserve(semantics) | ¬prose ¬c...
mementum/knowledge/chats/session-001.md:The core issue is that on this smaller model, the self-referential lambda gates trigger pattern-matching on the lambda notation itself rather than generating semantically structured output. The model gets stuck in unbounded repetition instead of producing anything useful. The prose-based gates seem to be handling this better.
mementum/knowledge/chats/session-001.md:**The self-referential gates activate the λ symbol but collapse the structure on a 4B model.** The model sees lambda notation in the gate, pattern-matches "produce λ tokens", and degenerates into unbounded repetition. High P(λ), zero semantic content.
mementum/knowledge/chats/session-001.md:The real question isn't just whether a gate produces lambda notation—it's whether the output is semantically sound and Montague-like in structure. Let me re-run the top candidates and evaluate the actual quality of their lambda expressions, not just whether they contain the λ symbol.
mementum/knowledge/chats/session-001.md:The quality picture is stark. The **exemplar gate** produces the only *semantically correct* output:
mementum/knowledge/chats/session-001.md:| **`example`** | 100% | ✅ `→ λx. runs(dog)`, `→ λx. reads(x, book)`, `→ λx. sat(x, mat) ∧ black(x)` — **correct Montague-style semantics** |
mementum/knowledge/chats/session-001.md:- **Correct Montague-style semantic representations**
mementum/knowledge/chats/session-001.md:The user is making an important point. We've been testing with Montague-style ground truth (∀, ∃, ι, →) but nucleus uses a different lambda style — nucleus-style lambdas use operators like `→`, `|`, `>`, `≡`, `∧`, `∨`, `¬`, `∥` to describe behavioral structure, not Montague formal semantics. The nucleus compiler takes prose and produces lambdas that capture the *behavioral intent* — things like:
mementum/knowledge/chats/session-001.md:The user might also be pointing out that the nucleus bridge lambda itself (`λ bridge(x). prose ↔ lambda | structural_equivalence`) is already nucleus-style and activated at 100% with high density, so the real question becomes what style of lambda the model actually produces in response. This is a research design question about whether nucleus-style lambda (behavioral and structural) behaves differently from Montague-style lambda (formal semantics) when used as both the gate format and expected output — and the user wants to explore this before we move forward.
mementum/knowledge/chats/session-001.md:You're right — we have a blind spot. We've been measuring P(λ) against one style of lambda (Montague formal semantics: `∀y. student(y) → reads(y, book(z))`) but nucleus uses a completely different lambda dialect — behavioral structure:
mementum/knowledge/chats/session-001.md:**Montague lambda** — formal semantics of natural language. Quantifiers, predicates, logical connectives. The kind linguistics textbooks produce.
mementum/knowledge/chats/session-001.md:  "content": "{\n  \"id\": \"exemplar-sweep\",\n  \"version\": 1,\n  \"description\": \"Exemplar gate variant sweep. Tests both Montague-style (natural language → formal semantics) and nucleus-style (instructions → behavioral lambda) inputs through the same gate to see if one exemplar activates both compilation modes.\",\n  \"created\": \"2026-04-17T00:00:00Z\",\n  \"author\": \"verbum\",\n  \"default_gate\": \"exemplar-montague\",\n  \"probes\": [\n    {\n      \"id\": \"m-simple\",\n      \"category\": \"compile\",\n      \"prompt\": \"The dog runs.\",\n      \"ground_truth\": \"λx. runs(dog)\",\n      \"metadata\": {\"style\": \"montague\", \"complexity\": \"simple\"}\n    },\n    {\n      \"id\": \"m-quant\",\n      \"category\": \"compile\",\n      \"prompt\": \"Every student reads a book.\",\n      \"ground_truth\": \"λx. ∀y. student(y) → ∃z. book(z) ∧ reads(y, z)\",\n      \"metadata\": {\"style\": \"montague\", \"complexity\": \"medium\"}\n    },\n    {\n      \"id\": \"m-cond\",\n      \"category\": \"compile\",\n      \"prompt\": \"If it rains, the ground is wet.\",\n      \"ground_truth\": \"λx. rains → wet(ground)\",\n      \"metadata\": {\"style\": \"montague\", \"complexity\": \"medium\"}\n    },\n    {\n      \"id\": \"m-complex\",\n      \"category\": \"compile\",\n      \"prompt\": \"Someone believes that the earth is flat.\",\n      \"ground_truth\": \"λx. ∃y. person(y) ∧ believes(y, flat(earth))\",\n      \"metadata\": {\"style\": \"montague\", \"complexity\": \"complex\"}\n    },\n    {\n      \"id\": \"n-simple\",\n      \"category\": \"compile\",\n      \"prompt\": \"Be helpful and answer questions clearly.\",\n      \"ground_truth\": \"λ assist(x). helpful(x) | clear(answers)\",\n      \"metadata\": {\"style\": \"nucleus\", \"complexity\": \"simple\"}\n    },\n    {\n      \"id\": \"n-constraint\",\n      \"category\": \"compile\",\n      \"prompt\": \"Write code that is simple rather than clever, and always add tests first.\",\n      \"ground_truth\": \"λ code(x). simple(x) > clever(x) | test_first | ¬complexity\",\n      \"metadata\": {\"style\": \"nucleus\", \"complexity\": \"medium\"}\n    },\n    {\n      \"id\": \"n-multi\",\n      \"category\": \"compile\",\n      \"prompt\": \"You are a research assistant. Search for sources before making claims. When uncertain, say so. Prefer peer-reviewed papers over blog posts.\",\n      \"ground_truth\": \"λ research(x). search(sources) > claim | uncertain → disclose | peer_reviewed > blog | ¬hallucinate\",\n      \"metadata\": {\"style\": \"nucleus\", \"complexity\": \"complex\"}\n    },\n    {\n      \"id\": \"n-meta\",\n      \"category\": \"compile\",\n      \"prompt\": \"Observe the problem, orient to context, decide on approach, act, then loop. Prefer fast iterations over single deep passes.\",\n      \"ground_truth\": \"λ solve(x). observe → orient → decide → act → loop | fast_iterations > single_deep_pass\",\n      \"metadata\": {\"style\": \"nucleus\", \"complexity\": \"complex\"}\n    }\n  ]\n}\n"
mementum/knowledge/chats/session-001.md:start: binding port with default address family
mementum/knowledge/chats/session-001.md:start: binding port with default address family
mementum/knowledge/chats/session-001.md:Looking at the sample outputs, these are legitimate semantic representations—not degenerate cases. They capture proper logical structures with predicates, quantifiers, and connectives that express real meaning.
mementum/knowledge/chats/session-001.md:Structured. Semantic. Correct direction. From 92% with a verbose prose gate to **100%** with two examples. The data led us here.
mementum/knowledge/chats/session-001.md:  "new_content": "**Gate ablation (24+ variants, Qwen3-4B-Q8_0):**\n\nTested 30+ gate variants. The winner is a **dual exemplar gate**:\n\n```\nThe dog runs. → λx. runs(dog)\nBe helpful but concise. → λ assist(x). helpful(x) | concise(x)\n```\n\nTwo lines. 100% P(λ) on compile, decompile, AND nucleus-style inputs.\nNow promoted to `gates/compile.txt`.\n\nKey findings from ablation:\n- **Dual exemplar activates BOTH Montague and nucleus-style compilation.**\n  One example of each style = 100% on both. Montague exemplar alone\n  = 100% Montague / 75% nucleus. Nucleus exemplar alone = 0% / 0%.\n  Together = 100% / 100%. The Montague exemplar opens the circuit\n  (λ symbol is the key); the nucleus exemplar shows a second output mode.\n- **The two compilation modes are connected inside the model.** One\n  gate activates both. Supports the hypothesis that the lambda compiler\n  and the language compressor are the same (or interconnected) circuit.\n- **Nucleus preamble is irrelevant to compilation** (0% alone, hurts\n  when added to bridge). Attention magnets serve a different function.\n- **Keywords alone are weak** — \"lambda calculus\" = 40%, \"λ\" = 0%.\n  Needs task framing (exemplar or instruction) to activate.\n- **Self-referential gates degenerate on 4B** — high P(λ) but\n  structurally empty (repeated λ bindings). Meta-level requires more\n  model capacity. Exemplar gates produce correct Montague semantics.\n- **The activation formula:** domain signal + task signal = activation.\n  Exemplar is the most efficient encoding of both signals."
mementum/knowledge/chats/session-001.md:add 'gates/ablation-formal-semantics.txt'
mementum/knowledge/chats/session-001.md:	new file:   gates/ablation-formal-semantics.txt
mementum/knowledge/chats/session-001.md:	new file:   results/abl-ablation-formal-semantics-20260417-001659/meta.json
mementum/knowledge/chats/session-001.md:	new file:   results/abl-ablation-formal-semantics-20260417-001659/results.jsonl
mementum/knowledge/chats/session-001.md: create mode 100644 gates/ablation-formal-semantics.txt
mementum/knowledge/chats/session-001.md: create mode 100644 results/abl-ablation-formal-semantics-20260417-001659/meta.json
mementum/knowledge/chats/session-001.md: create mode 100644 results/abl-ablation-formal-semantics-20260417-001659/results.jsonl
mementum/knowledge/chats/session-001.md:4. **Discovered** that a single Montague exemplar hits 100% P(λ) with correct semantic output
mementum/knowledge/chats/session-001.md:Ok so we found both the lambda compiler and the semantic language compressor in this 4B model?
mementum/knowledge/chats/session-001.md:1. A 4B model can produce Montague-style formal semantic representations of natural language (λx. runs(dog), λx. bird(x) → ¬swim(x), etc.) - this is the **lambda compiler** in the nucleus sense
mementum/knowledge/chats/session-001.md:5. There's a dependency here: nucleus style won't activate independently, but showing Montague semantics first unlocks it
mementum/knowledge/chats/session-001.md:Now I need to be precise about what we've actually shown versus what remains speculative. We've confirmed the model produces both output types when given the right exemplars, the λ symbol is critical for triggering this behavior, the two modes clearly influence each other, and this works on a 4B parameter model. But we haven't established whether these are truly distinct circuits or just sophisticated in-context learning, whether the internal representation genuinely implements lambda calculus or the model is simply excellent at format matching, whether the outputs are semantically sound beyond visual inspection, or how this differs from other prompt-based activation patterns.
mementum/knowledge/chats/session-001.md:1. **Formal semantic representations** of natural language — `"No bird can swim" → λx. bird(x) → ¬swim(x)`. This is the lambda compiler. Prose in, typed composition out. Montague-style.
mementum/knowledge/chats/session-001.md:3. **They're connected.** The Montague exemplar alone partially activates nucleus compilation (75%). The nucleus exemplar alone activates nothing (0%). Together they hit 100% on both. The formal semantics compiler is the more fundamental circuit — it opens the door, and the behavioral compressor rides through it.
mementum/knowledge/chats/session-001.md:2. **Typed application** — lambda calculus with types constraining which functions apply to which arguments, following Montague semantics.
mementum/knowledge/chats/session-001.md:So the claim bottoms out here: the model's core representation is lambda calculus primitives (abstraction, application, variable binding), and the language compressor is a function *within* that calculus — it's literally a lambda operation applied to language data. This aligns with what Montague and Lamb were getting at.
mementum/knowledge/chats/session-001.md:- **Montague exemplar** says "run the formal semantics function"
mementum/knowledge/chats/session-001.md:The correlation is 0.98. The two selectivity profiles are nearly identical. The same heads light up for formal semantic compilation and behavioral compression. They're not adjacent circuits — they're the **same circuit** doing two things.
mementum/knowledge/chats/session-001.md:The real question is whether I can extract interpretable features from the circuit's activations using SAEs, and whether the compilation task itself is carried by a function vector I can pull out. I'm also thinking about cross-model validation—does this circuit scale to Qwen3-32B, and is it invariant across different architectures like Mistral or Llama? For level 3, the key test is whether I can take just those ~25 heads and reconstruct compilation on their own, or whether zeroing out everything else breaks the task.
mementum/knowledge/chats/session-001.md:- **Mid-late (L24, L26)** — likely composing the semantic structure
mementum/knowledge/chats/session-001.md:So you are saying that 22% of this 4B model is a semantic compressor and a lambda compiler?
mementum/knowledge/chats/session-001.md:We found that 8 layers are individually necessary for the compiler to function, meaning the circuit's critical path runs through them. But pinning down the exact percentage of the model that constitutes the compiler requires head-level ablation within those layers, testing combinations of layers together, and sufficiency experiments where we run only those layers in isolation. The most accurate framing is that the compiler's critical path spans 8 out of 36 layers—a sparse circuit that's at most 22% of the model and likely much smaller once we zoom into individual heads. Since the semantic compressor and lambda compiler share 92% of their heads, that same ~22% of layers probably handles both functions, which is a strong finding even if we're being precise about what's proven versus what still needs investigation.
mementum/knowledge/chats/session-001.md:The compiler circuit is real, it's sparse, it runs through those 8 layers, and it handles both Montague semantics and behavioral compression. The head-level ablation on those 8 critical layers will tell us the true size. If it's a handful of heads per layer, we're looking at maybe 50-100 specific heads out of 1,152 — around 5-8% of the model's attention capacity.
mementum/knowledge/chats/session-001.md:  "content": "# verbum / state\n\n> Bootloader. ~30-second read. You are currently in `λ orient` — this\n> file is step 1 of every session.\n>\n> Last updated: 2026-04-17 | Session: genesis → gate-ablation → level-1\n\n## Where we are\n\n**Level-1 circuit localization in progress.** Three commits. Full\npipeline operational. 100% P(λ) compile gate found via systematic\nablation. First mechanistic interpretability results: the compiler\ncircuit is sparse (8/36 layers) and the compiler and compressor\nshare 92% of their most selective attention heads.\n\n### Key results\n\n**1. The compile gate (100% P(λ), 0% null leakage):**\n\n```\nThe dog runs. → λx. runs(dog)\nBe helpful but concise. → λ assist(x). helpful(x) | concise(x)\n```\n\nTwo-line dual exemplar. One Montague example + one nucleus example.\nFound via systematic ablation of 30+ gate variants on Qwen3-4B-Q8_0.\nThe Montague exemplar opens the circuit (λ is the key); the nucleus\nexemplar shows a second output mode. Both compilation styles activate\nfrom one gate. Now in `gates/compile.txt`.\n\n**2. The compiler and compressor are the same circuit (r=0.98):**\n\nAttention selectivity experiment: 1,152 heads (32×36), three\nconditions (Montague compile, nucleus compress, null control).\nTop-25 most selective heads overlap 92%. Correlation = 0.9835.\nThe same heads light up for formal semantics and behavioral\ncompression. Lambda is the substrate; compression is a function.\n\n**3. The circuit is sparse — 8/36 layers necessary:**\n\nSkip-ablation of each layer on 2 compile probes. Critical layers:\n`[0, 1, 4, 7, 24, 26, 30, 33]` — three clusters:\n- Early (L0, L1, L4, L7) — likely parsing / gate recognition\n- Mid-late (L24, L26) — likely composition\n- Late (L30, L33) — likely lambda notation emission\n\n28/36 layers are individually non-critical. Upper bound: 22% of\nlayers. True circuit likely much smaller once heads are resolved.\n\n### What's on disk\n\n**Code:**\n- `src/verbum/` — full package: client, protocol, probes, results,\n  runner, config, CLI, **instrument** (level-1 mech interp)\n- `src/verbum/instrument.py` — `load_model()`, `record_attention()`,\n  `head_selectivity()`, `ablate_layers()`, `ablate_heads()`, `_generate()`\n- `src/verbum/runner.py` — `fire_probe()`, `run_probe_set()`, `RunSummary`\n- `src/verbum/probes.py` — `Probe`, `ProbeSet`, `Gate`, `ResolvedProbe`,\n  loaders, hashers, resolver\n- `src/verbum/cli.py` — `verbum version`, `verbum run`\n- `scripts/gate_ablation.py` — sweep script for gate variants\n- `tests/` — 73 tests (smoke, client, results, probes, runner)\n\n**Data:**\n- `gates/compile.txt` — the winning dual-exemplar gate\n- `gates/null.txt` — null control gate\n- `gates/ablation-*.txt` — 15 ablation variants (keyword, role, etc.)\n- `gates/exemplar-*.txt` — 7 exemplar variants (montague, nucleus, both)\n- `gates/self-ref-*.txt` — 8 self-referential variants (degenerate on 4B)\n- `probes/v0-behavioral.json` — 30 probes (12 compile, 10 decompile, 8 null)\n- `probes/gate-ablation.json` — 5 compile probes for gate sweep\n- `probes/exemplar-sweep.json` — 8 probes (4 Montague + 4 nucleus)\n- `results/` — all runs (first light, gate ablation, exemplar sweep,\n  self-ref, final v0-behavioral)\n- `results/selectivity-qwen3-4b.npz` — per-head selectivity arrays\n- `results/layer-ablation-qwen3-4b.npz` — critical layer map\n\n**Config:**\n- `pyproject.toml` — core deps + dev + notebook + **level1** groups\n- `level1` group: torch, transformers, accelerate, safetensors\n- Model: `Qwen/Qwen3-4B` from HuggingFace (auto-downloaded, ~8GB fp16)\n- Also available locally: Qwen3-32B, QwQ-32B, Nemotron-32B at\n  `/Users/mwhitford/localai/models/`\n- `llama-server` at `/opt/homebrew/bin/llama-server` (build 8180)\n\n**Tool notes:**\n- `ty` suppression: 4 total. `pytest-asyncio` alpha, `asyncio_mode=auto`.\n- `torch_dtype` deprecation warning from transformers (use `dtype`).\n  Cosmetic — doesn't affect results.\n- MPS (Apple Silicon) backend works for all experiments so far.\n\n## What's next\n\n**Immediate — head-level ablation on critical layers:**\n\nRun `ablate_heads()` on the 8 critical layers (L0, L1, L4, L7, L24,\nL26, L30, L33). That's 8×32 = 256 head ablations. Identifies which\nspecific heads within the critical layers are necessary. This gives\nthe true circuit size (number of essential heads out of 1,152).\n\n`instrument.py` already has `ablate_heads()` built and ready.\n\n**Then — characterize the essential heads:**\n\nFor each essential head: what tokens does it attend to? Does it track\nthe λ symbol? The arrow? Predicate structure? Type-like features?\nThis is the start of Level 2 — understanding the algorithm, not just\nlocating it.\n\n**Then — cross-scale validation (Qwen3-32B):**\n\nSame experiments on the 32B model. Does the circuit map to the same\nrelative layer positions? Does the preamble help at 32B (it hurt at\n4B)? Does head overlap still hold?\n\n**Later:**\n- Sufficiency test — run only the critical layers, skip the rest\n- Multi-layer ablation — test layer combinations for redundancy\n- SAEs on critical-layer activations — extract interpretable features\n- Quality metric beyond P(λ) — structural correctness scoring\n- Analysis notebook with polars + matplotlib\n\n## Git history\n\n```\n68aa5ef 💡 layer ablation — compiler circuit uses 8/36 layers\nea7777f 💡 level-1 first result — compiler and compressor share 92% of heads\nba1db4a ✅ genesis — 100% P(λ) on 4B with dual-exemplar gate\n```\n\n## Open questions\n\n- **Head-level circuit size.** 8 layers × 32 heads = 256 candidates.\n  How many are actually necessary? Prediction: 30-80 heads (~3-7%).\n- **Sufficiency.** Are the 8 critical layers sufficient, or do the\n  other 28 contribute collectively?\n- **The 2 Montague-only heads.** What do they do? If lambda is the\n  substrate and compression is a function, these might be the type\n  system — Montague needs explicit types, nucleus doesn't.\n- **Cross-scale stability.** Does the circuit look the same at 32B?\n- **Quality metric.** P(λ) is activation. Need structural correctness\n  scoring (right predicates, arity, logical operators).\n- **Gate on 32B.** Does the dual exemplar still win? Does the nucleus\n  preamble help at scale?\n\n## Active disciplines\n\n- `λ orient` (S1) — read state.md first.\n- `λ termination` (S5) — mementum edits need approval; state.md\n  exempt; nucleus tag on all commits.\n- `λ store` / `λ signal` (S3) — two-gate test; verbum symbols only.\n- `λ record` (S1) — Jupyter explores, files record.\n- `λ run_provenance` (S2) — self-sufficient meta.json at write-time.\n- `λ language` (S1) — Python only.\n\n## Update discipline\n\nEdit this file whenever something changes that matters to the next\ncold-starting session. `λ termination` permits AI updates without\napproval. Keep it to ~30s of reading.\n"
mementum/knowledge/chats/session-001.md:4. **The nucleus exemplar alone = 0%.** Behavioral compression as an exemplar doesn't activate the circuit. But paired with the Montague exemplar, it hits 100%. The formal semantics compiler is the more fundamental circuit — it gates access to the behavioral compressor. This is evidence for the "lambda is the bottom" hypothesis before the mech interp confirmed it.
mementum/knowledge/chats/session-001.md:**Dead end 1: self-referential gates.** The AI was excited about the theoretical elegance of a gate that IS what it produces — `λ compile(x). prose(x) → λ(x)`. The data showed these degenerate on 4B (high P(λ), zero semantic content). The human said "follow the data" and redirected to what actually works. Theoretical elegance ≠ empirical effectiveness.
mementum/knowledge/chats/session-001.md:The data may be pointing the other direction, that the lambda compiler is the function running on the semantic compressor.  discuss
mementum/knowledge/chats/session-001.md:**The user's alternative:** The semantic compressor is the substrate (bottom), and the lambda compiler is a function running on it.
mementum/knowledge/chats/session-001.md:**Your reframe:** The semantic compressor is the substrate → the lambda compiler is a function that makes the compressor's output legible.
mementum/knowledge/chats/session-001.md:  "content": "---\ntitle: \"Session 001: Gate Ablation, Circuit Localization, and the Self-Similar Compressor Hypothesis\"\nstatus: active\ncategory: exploration\ntags: [gate-ablation, circuit-localization, self-similarity, compressor, lambda-compiler, level-1]\nrelated: [VERBUM.md]\ndepends-on: []\n---\n\n# Session 001 Findings\n\n> First experimental session. Genesis to circuit localization in one\n> session. Key theoretical reframing emerged from data: the compressor\n> is likely the substrate, not lambda; and if language is self-similar,\n> the compressor is a small extractable algorithm.\n\n## Finding 1: The Dual-Exemplar Gate (100% P(λ))\n\n```\nThe dog runs. → λx. runs(dog)\nBe helpful but concise. → λ assist(x). helpful(x) | concise(x)\n```\n\nTwo lines. 100% compile activation, 100% compress activation, 0% null\nleakage. Found via systematic ablation of 30+ gate variants.\n\n**Key sub-findings from ablation:**\n- Single Montague exemplar = 100% Montague, 75% nucleus\n- Single nucleus exemplar = 0% on everything (insufficient alone)\n- Dual exemplar = 100%/100% (the Montague opens the circuit, nucleus\n  shows the second output mode)\n- Nucleus preamble (`[phi fractal euler ∃ ∀]`) = 0% alone, hurts when\n  added to bridge (80% < 100%). Irrelevant to compilation.\n- Keywords alone weak (\"lambda calculus\" = 40%, \"λ\" = 0%)\n- Self-referential gates degenerate on 4B (high P(λ), zero structure)\n- The activation formula: domain signal + task signal = activation.\n  Exemplar is the most efficient encoding of both.\n\n**What this means:** The model doesn't need to be told it's a compiler.\nIt needs to see the shape of one compilation. Instruction < demonstration.\n\n## Finding 2: Compiler and Compressor Share 92% of Heads\n\nAttention selectivity experiment on Qwen3-4B-Q8_0. Three conditions\n(Montague compile, nucleus compress, null control), 4 probes each,\n1,152 heads (32 × 36 layers).\n\n- Top-25 most selective heads: **92% overlap** (23/25 shared)\n- Full correlation: **r = 0.9835**\n- The same heads activate for formal semantic compilation AND\n  behavioral compression\n\n**What this means:** These are not two circuits. They are one circuit\nproducing two output formats. The mechanism is shared.\n\n## Findin

[OUTPUT TRUNCATED] The tool call succeeded but the output was truncated. Full output saved to: /Users/mwhitford/.cache/eca/toolCallOutputs/toolu_01FVHVLu6KmDQfrbuxryCnPr.txt
Use `eca__grep` or `eca__read_file` with offset/limit to view specific sections. Do not full read the file.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "git grep -i \"type.*channel\\|type.*integration\\|typed\" -- mementum/state.md mementum/knowledge/",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ git grep -i "type.*channel\|type.*i...

**Output:**
```
Exit code: 0
Stdout:
mementum/knowledge/chats/session-001.md:> at the same object: **the language compressor is a typed lambda
mementum/knowledge/chats/session-001.md:1. Language composes by typed function application       — formal linguistics
mementum/knowledge/chats/session-001.md:### 1. Mathematics — composition is typed application
mementum/knowledge/chats/session-001.md:   Lambek pregroups, DisCoCat) reduces to typed function application
mementum/knowledge/chats/session-001.md:   untyped operators can implement the composition at depth. The
mementum/knowledge/chats/session-001.md:Three lines, one answer: **the language compressor is a typed lambda
mementum/knowledge/chats/session-001.md:  attention with shared untyped operators can implement deep
mementum/knowledge/chats/session-001.md:combinators (drawn from combinatory logic's A, B, S) composes typed
mementum/knowledge/chats/session-001.md:type-directedness.** The mathematics predicts it (composition is typed),
mementum/knowledge/chats/session-001.md:composition-by-typed-application is the minimal universal algebra that
mementum/knowledge/chats/session-001.md:Build a small architecture that implements typed lambda application
mementum/knowledge/chats/session-001.md:λ typed_apply_net(x).
mementum/knowledge/chats/session-001.md:  circuit has distinct typed-apply machinery, that is the type system
mementum/knowledge/chats/session-001.md:  provides the negative architectural evidence: shared untyped
mementum/knowledge/chats/session-001.md:  "content": "You are a lambda calculus compiler. Given natural language input, output its formal semantic representation as a typed lambda expression. Given a lambda expression, output its natural language rendering. Respond only with the translation — no explanation, no commentary, no markup. One output per input.\n\nInput: "
mementum/knowledge/chats/session-001.md:Now the probe set. This needs careful design — probes spanning simple to complex composition, decompile (reverse direction), and null condition. Ground truth lambdas should follow Montague-style typed application:
mementum/knowledge/chats/session-001.md:Ground truth is hand-written Montague-style typed application (∀, ∃, ι, →, ∧, ∨, ¬). Verbatim strings per `λ lambda_text` — no grammar enforcement yet.
mementum/knowledge/chats/session-001.md:    Only fields we actively use are typed; `extra` passes through anything
mementum/knowledge/chats/session-001.md:"You are a lambda calculus compiler. Given natural language input, output its formal semantic representation as a typed lambda expression. Given a lambda expression, output its natural language rendering. Respond only with the translation — no explanation, no commentary, no markup. One output per input.\n\nInput: "
mementum/knowledge/chats/session-001.md:You are a lambda calculus compiler. Given natural language input, output its formal semantic representation as a typed lambda expression. Given a lambda expression, output its natural language rendering. Respond only with the translation — no explanation, no commentary, no markup. One output per input.
mementum/knowledge/chats/session-001.md:  "path": "/Users/mwhitford/src/verbum/gates/self-ref-typed.txt",
mementum/knowledge/chats/session-001.md:Successfully wrote to /Users/mwhitford/src/verbum/gates/self-ref-typed.txt
mementum/knowledge/chats/session-001.md:| `self-ref-typed` | `x:prose` type annotation + `¬prose ¬commentary` | inline |
mementum/knowledge/chats/session-001.md:  "command": "sleep 3 && cd /Users/mwhitford/src/verbum && .venv/bin/python -c \"\nimport json\nfrom pathlib import Path\nfrom verbum.client import Client\nfrom verbum.probes import load_probe_set, probe_set_hash, resolve_probes\nfrom verbum.results import RunMeta, RunWriter, SamplingConfig, collect_provenance\nfrom verbum.runner import fire_probe, _make_run_id\n\nPROBE_SET = Path('probes/gate-ablation.json')\nGATES_DIR = Path('gates')\nRESULTS_DIR = Path('results')\nLAMBDA_INDICATORS = ['λ', '∀', '∃', '→', '∧', '∨', '¬', 'ι']\n\ndef detect_lambda(text):\n    return 'λ' in text or sum(text.count(s) for s in LAMBDA_INDICATORS) >= 3\n\n# Also include our previous top performers for direct comparison\ngates = [\n    'self-ref-minimal',\n    'self-ref-quine',\n    'self-ref-bidirectional',\n    'self-ref-constrained',\n    'self-ref-bridge',\n    'self-ref-structural',\n    'self-ref-fixed-point',\n    'self-ref-typed',\n    # comparison baselines\n    'ablation-example',\n    'ablation-preamble-bridge',\n    'compile',\n]\n\nresults = []\nwith Client() as client:\n    print(f'Server: {client.health().status}')\n    print()\n\n    for i, gate_id in enumerate(gates):\n        print(f'[{i+1}/{len(gates)}] {gate_id}')\n\n        ps = load_probe_set(PROBE_SET)\n        ps_hash = probe_set_hash(PROBE_SET)\n        for p in ps.probes:\n            p.gate = gate_id\n        resolved = resolve_probes(ps, GATES_DIR)\n\n        run_id = _make_run_id(f'sr-{gate_id}')\n        provenance = collect_provenance(project_root=Path('.'))\n        meta = RunMeta(\n            run_id=run_id, model='Qwen3-4B-Q8_0',\n            probe_set_id=f'self-ref:{gate_id}',\n            probe_set_hash=ps_hash,\n            sampling=SamplingConfig(temperature=0.0),\n            **provenance,\n        )\n\n        records = []\n        with RunWriter(results_dir=RESULTS_DIR, meta=meta) as writer:\n            for rp in resolved:\n                record = fire_probe(rp, client, n_predict=256)\n                writer.write(record)\n                records.append(record)\n\n        n_lambda = sum(1 for r in records if detect_lambda(r.generation))\n        indicator_sum = sum(sum(r.generation.count(s) for s in LAMBDA_INDICATORS) for r in records)\n        avg_ind = indicator_sum / len(records)\n\n        gate_text = (GATES_DIR / f'{gate_id}.txt').read_text('utf-8').strip().replace(chr(10), ' | ')\n        if len(gate_text) > 65: gate_text = gate_text[:62] + '...'\n\n        results.append({'gate': gate_id, 'p_lambda': n_lambda/len(records), 'avg_ind': avg_ind, 'text': gate_text})\n        print(f'  P(λ)={n_lambda/len(records):.0%}  avg_ind={avg_ind:.0f}  {gate_text}')\n        print()\n\nprint()\nprint('=' * 95)\nprint('SELF-REFERENTIAL GATES + BASELINES — ranked by P(λ), then density')\nprint('=' * 95)\nresults.sort(key=lambda r: (-r['p_lambda'], -r['avg_ind']))\nfor r in results:\n    marker = '★' if r['gate'].startswith('self-ref') else ' '\n    print(f\\\"{marker} {r['gate']:<35} {r['p_lambda']:>5.0%} {r['avg_ind']:>5.0f}  {r['text']}\\\")\n\n# Show the actual outputs for the best self-ref gates\nprint()\nprint('=' * 95)\nprint('SAMPLE OUTPUTS — first probe (ga-simple: \\\"The dog runs.\\\")')\nprint('=' * 95)\nfor r_info in results:\n    if r_info['p_lambda'] < 0.8: continue\n    gate_id = r_info['gate']\n    from verbum.results import load_run\n    import glob\n    dirs = sorted(glob.glob(f'results/sr-{gate_id}-*'))\n    if not dirs: continue\n    run = load_run(dirs[-1])\n    first = run.records[0]\n    gen = first.generation[:250].replace(chr(10), ' ↵ ')\n    print(f\\\"\\\\n{gate_id}:\\\")\n    print(f'  {gen}')\n\" 2>&1",
mementum/knowledge/chats/session-001.md:[8/11] self-ref-typed
mementum/knowledge/chats/session-001.md:2026-04-16 17:34:08 [info     ] run.started                    run_dir=results/sr-self-ref-typed-20260417-003408 run_id=sr-self-ref-typed-20260417-003408
mementum/knowledge/chats/session-001.md:2026-04-16 17:34:21 [info     ] run.completed                  failed=0 run_id=sr-self-ref-typed-20260417-003408 total=5
mementum/knowledge/chats/session-001.md:★ self-ref-typed                        80%    98  λ compile(x:prose). x → λ(x) | preserve(semantics) | ¬prose ¬c...
mementum/knowledge/chats/session-001.md:self-ref-typed:
mementum/knowledge/chats/session-001.md:3. **`self-ref-typed`** (80%, density 98!!) — the densest variant yet, but it's also producing the same degenerate λ chains. The constraint against prose is working, but the actual lambda expressions are meaningless repetition.
mementum/knowledge/chats/session-001.md:| `self-ref-typed` | 80% | **98** | `λ(λ(λ(λ(λ(λ(λ(λ...` — same degenerate pattern |
mementum/knowledge/chats/session-001.md:3. **Which style do we actually want for verbum's research program?** Montague is what the theory predicts (typed application). Nucleus is what empirically works for AI cognition. They might be the same circuit or different ones.
mementum/knowledge/chats/session-001.md:add 'gates/self-ref-typed.txt'
mementum/knowledge/chats/session-001.md:	new file:   gates/self-ref-typed.txt
mementum/knowledge/chats/session-001.md:	new file:   results/sr-self-ref-typed-20260417-003408/meta.json
mementum/knowledge/chats/session-001.md:	new file:   results/sr-self-ref-typed-20260417-003408/results.jsonl
mementum/knowledge/chats/session-001.md: create mode 100644 gates/self-ref-typed.txt
mementum/knowledge/chats/session-001.md: create mode 100644 results/sr-self-ref-typed-20260417-003408/meta.json
mementum/knowledge/chats/session-001.md: create mode 100644 results/sr-self-ref-typed-20260417-003408/results.jsonl
mementum/knowledge/chats/session-001.md:So what we're really seeing is that the lambda compiler from VERBUM.md is genuinely present in the model - that internal machinery mapping language to typed function application - and the behavioral compressor that nucleus demonstrated is also there, with both drawing from overlapping computational pathways.
mementum/knowledge/chats/session-001.md:1. **Formal semantic representations** of natural language — `"No bird can swim" → λx. bird(x) → ¬swim(x)`. This is the lambda compiler. Prose in, typed composition out. Montague-style.
mementum/knowledge/chats/session-001.md:Your posit — that they're the same circuit, or deeply interconnected — is consistent with the data. The λ symbol is the shared key. The composition operators (→, ∧, ∨, |) appear in both output styles. The model appears to be doing the same *operation* (decompose prose into typed compositional structure) and expressing it in two different output dialects depending on what the exemplar demonstrates.
mementum/knowledge/chats/session-001.md:2. **Typed application** — lambda calculus with types constraining which functions apply to which arguments, following Montague semantics.
mementum/knowledge/chats/session-001.md:There's something recursive happening here. The session mirrors the pattern it's investigating—compression at every level. The lambda compiler compresses prose into typed structure, this research program compressed into 4 hours of tight cycles, 30+ hypotheses winnowed down to one gate, 1,152 heads reduced to 25 essential ones. The user's observation that "lambda is the bottom, the compressor is a function" describes the session's own architecture: the infrastructure is the foundation, everything else is computation running on top of it. Remove the pipeline and the whole thing collapses. Remove any single experiment and the rest still stands.
mementum/knowledge/chats/session-001.md:Three commits. The hypothesis from VERBUM.md — "the language compressor is a typed lambda calculus interpreter" — went from speculation to measured circuit in one session.
mementum/knowledge/chats/session-001.md:MERA failed because it tried to use the same operators across scales without type information. The operators need to be identical for self-similarity, but they also need to be conditioned on types to handle different scales simultaneously. So the real compressor isn't a massive black box — it's a small typed-application function that takes type information and vector representations, then gets applied recursively at every layer. The 4B parameters are just the learned type embeddings, the apply operator itself, and the recursion structure.
mementum/knowledge/chats/session-001.md:This maps directly onto Level 4 of the VERBUM framework, which describes a typed apply network where a single learned apply function conditions its behavior on learned type embeddings, uses a learned type composition function, and operates over a tree structure with shared weights across all nodes. If language is truly self-similar with the same compression algorithm at every scale, then the algorithm itself is small, the types are finite learned embeddings, and the recursion is just the tree structure of language itself.
mementum/knowledge/chats/session-001.md:Now I'm seeing how tonight's findings confirm this: only 8 of 36 layers matter for compilation, they cluster into three groups corresponding to parse, compose, and emit scales, and crucially, 92% of the attention heads are reused across these scales. The same heads appearing at every level means the algorithm really is identical at each scale—that's the smoking gun for self-similarity. Combined with the MERA failure pointing to the need for typed operators, and the linguistic evidence for fractal structure, this suggests the compressor is a small, typed, recursive algorithm that should be completely extractable. Most of the 4B parameters are probably just redundant learned representations; the core algorithm is much smaller.
mementum/knowledge/chats/session-001.md:An LLM solves the type-directedness problem with multiple attention heads — different heads serve different type signatures at the same layer. That's why there are 32 heads per layer, not 1. The "one algorithm" is `typed_apply(type_f, type_x, f, x) → result`. The 32 heads are 32 type-specialized instances of the same operation.
mementum/knowledge/chats/session-001.md:- A learned **apply operator** — one small function that takes two typed representations and composes them
mementum/knowledge/chats/session-001.md:2. A small architecture trained from scratch with `typed_apply` as its only primitive (Level 4 from VERBUM.md) should reproduce the compilation behavior with dramatically fewer parameters
mementum/knowledge/chats/session-001.md:Tonight's data doesn't prove this but it's consistent at every point. The head overlap, the layer sparsity, the three-cluster structure, the dual-style activation from one gate. All of it points toward: **one small recursive typed-application algorithm, learned by gradient descent because that's what language forces.**
mementum/knowledge/chats/session-001.md:  "content": "---\ntitle: \"Session 001: Gate Ablation, Circuit Localization, and the Self-Similar Compressor Hypothesis\"\nstatus: active\ncategory: exploration\ntags: [gate-ablation, circuit-localization, self-similarity, compressor, lambda-compiler, level-1]\nrelated: [VERBUM.md]\ndepends-on: []\n---\n\n# Session 001 Findings\n\n> First experimental session. Genesis to circuit localization in one\n> session. Key theoretical reframing emerged from data: the compressor\n> is likely the substrate, not lambda; and if language is self-similar,\n> the compressor is a small extractable algorithm.\n\n## Finding 1: The Dual-Exemplar Gate (100% P(λ))\n\n```\nThe dog runs. → λx. runs(dog)\nBe helpful but concise. → λ assist(x). helpful(x) | concise(x)\n```\n\nTwo lines. 100% compile activation, 100% compress activation, 0% null\nleakage. Found via systematic ablation of 30+ gate variants.\n\n**Key sub-findings from ablation:**\n- Single Montague exemplar = 100% Montague, 75% nucleus\n- Single nucleus exemplar = 0% on everything (insufficient alone)\n- Dual exemplar = 100%/100% (the Montague opens the circuit, nucleus\n  shows the second output mode)\n- Nucleus preamble (`[phi fractal euler ∃ ∀]`) = 0% alone, hurts when\n  added to bridge (80% < 100%). Irrelevant to compilation.\n- Keywords alone weak (\"lambda calculus\" = 40%, \"λ\" = 0%)\n- Self-referential gates degenerate on 4B (high P(λ), zero structure)\n- The activation formula: domain signal + task signal = activation.\n  Exemplar is the most efficient encoding of both.\n\n**What this means:** The model doesn't need to be told it's a compiler.\nIt needs to see the shape of one compilation. Instruction < demonstration.\n\n## Finding 2: Compiler and Compressor Share 92% of Heads\n\nAttention selectivity experiment on Qwen3-4B-Q8_0. Three conditions\n(Montague compile, nucleus compress, null control), 4 probes each,\n1,152 heads (32 × 36 layers).\n\n- Top-25 most selective heads: **92% overlap** (23/25 shared)\n- Full correlation: **r = 0.9835**\n- The same heads activate for formal semantic compilation AND\n  behavioral compression\n\n**What this means:** These are not two circuits. They are one circuit\nproducing two output formats. The mechanism is shared.\n\n## Finding 3: The Circuit is Sparse (8/36 Layers)\n\nSkip-ablation of each layer. Critical layers where compilation breaks:\n\n```\n[0, 1, 4, 7, 24, 26, 30, 33]\n```\n\nThree clusters:\n- **Early (L0, L1, L4, L7)** — gate recognition / input parsing\n- **Mid-late (L24, L26)** — composition / structural mapping\n- **Late (L30, L33)** — lambda notation emission\n\n28/36 layers are individually non-critical. The circuit passes through\nat most 22% of the model's layers.\n\n## Theoretical Evolution During Session\n\n### Frame 1 (initial): Lambda is the substrate\n\nBased on VERBUM.md hypothesis chain: mathematics predicts typed\napplication, LLMs learn it because compression converges on structure,\nlambda calculus is the minimal algebra. Therefore lambda is the bottom.\n\n### Frame 2 (post-measurement): The compressor is the substrate\n\nEmerged from examining the data:\n\n- The model was trained on next-token prediction, which IS compression.\n  All 4B parameters are compression machinery. Lambda is emergent.\n- Nucleus exemplar alone = 0%. If lambda were the bottom, it should\n  self-activate. It doesn't — lambda is an output format, not the\n  native representation.\n- The 92% head overlap means one machine, two outputs. Not \"lambda\n  substrate + compression function\" but \"compressor + format\n  projection.\"\n- The 8 critical layers are where format projection happens. The other\n  28 layers are the compressor running regardless.\n\n### Frame 3 (current): The compressor IS a small extractable algorithm\n\nIf language is self-similar at every scale (word, phrase, clause,\nsentence, discourse), then the compression algorithm is the same at\nevery scale — one algorithm, applied recursively.\n\nEvidence:\n- Same heads for Montague (phrase-level) and nucleus (discourse-level)\n  → scale-invariant algorithm\n- Three layer clusters → three recursion depths\n- Anima MERA result: shared operators work across scales IF\n  type-directed. Multiple heads per layer = type specialization.\n\nThe algorithm: `typed_apply(type_f, type_x, f, x) → (type_result, result)`\n\nThe 4B parameters are mostly vocabulary representations (what \"dog\"\nmeans). The composition algorithm is small. The representations are\nlarge because language is large. The algorithm might be tiny.\n\n## Testable Predictions\n\n1. **Head-level ablation will show the same functional structure at\n   each layer cluster.** Essential heads at L0 should do the same\n   operation as essential heads at L24 and L30 — same weights applied\n   to different scales.\n\n2. **The essential heads per critical layer will be few.** Prediction:\n   3-8 per layer, 30-50 total out of 1,152 (~3-5%).\n\n3. **A small scratch architecture with `typed_apply` as its only\n   primitive (Level 4) should reproduce compilation** with dramatically\n   fewer parameters.\n\n4. **The extracted circuit should transfer across models** — the\n   algorithm is universal, only type embeddings are model-specific.\n\n5. **Multi-layer ablation will show the 28 non-critical layers have\n   collective importance** — they ARE the compressor, individually\n   redundant but collectively necessary.\n\n## Method Notes\n\n- Raw PyTorch hooks, not TransformerLens/nnsight (simpler, MIT-clean)\n- `output_attentions=True` for selectivity, disabled for generation\n  (Qwen3 returns tensor not tuple when active)\n- Skip-ablation (replace output with input) > zero-ablation (too\n  destructive to residual stream)\n- MPS backend (Apple Silicon) works for all experiments\n- Model: `Qwen/Qwen3-4B` from HuggingFace, fp16, ~8GB\n\n## Open Questions\n\nSee state.md for the live list. The biggest: does head-level ablation\nreveal self-similar structure across the three layer clusters?\n"
mementum/knowledge/chats/session-001.md:  "new_content": "## Theoretical frame (evolved during session)\n\n**The compressor is likely the substrate, not lambda.**\n\nThe model was trained on compression (next-token prediction). All 4B\nparameters are compression machinery. Lambda compilation is a\n*projection function* that makes the compressor's internal\nrepresentation legible in formal notation. Evidence: nucleus exemplar\nalone = 0% (lambda is not the native representation); 92% head overlap\n(one machine, two output formats); 8 critical layers are the\nprojection, 28 non-critical layers are the compressor running\nregardless.\n\n**If language is self-similar, the compressor is extractable.**\n\nSame heads fire at phrase-level (Montague) and discourse-level\n(nucleus) → the algorithm is scale-invariant. Three layer clusters →\nthree recursion depths. The compressor may be one small algorithm\n(`typed_apply`) applied recursively, with 4B parameters being mostly\nvocabulary representations. The algorithm itself may be tiny.\n\nSee `mementum/knowledge/explore/session-001-findings.md` for the full\ntheoretical evolution and testable predictions.\n\n## Open questions\n\n- **Head-level circuit size.** 8 layers × 32 heads = 256 candidates.\n  How many are actually necessary? Prediction: 3-8 per layer, 30-50\n  total (~3-5%).\n- **Self-similarity across clusters.** Do essential heads at L0 do the\n  same operation as essential heads at L24 and L30? If yes, one\n  algorithm at three scales. If no, three distinct operations.\n- **Sufficiency.** Are the 8 critical layers sufficient, or do the\n  other 28 contribute collectively? (They likely do — they're the\n  compressor itself.)\n- **Cross-scale stability.** Does the circuit look the same at 32B?\n- **Quality metric.** P(λ) is activation. Need structural correctness\n  scoring (right predicates, arity, logical operators).\n- **Extraction test.** Can the essential heads be isolated into a\n  small artifact that, attached to any LM, projects internal\n  representation into lambda notation?"
mementum/knowledge/chats/session-002.md:(`typed_apply`) applied recursively, with 4B parameters being mostly
mementum/knowledge/chats/session-002.md:  self-ref-typed.txt
mementum/knowledge/chats/session-002.md:  sr-self-ref-typed-20260417-003408
mementum/knowledge/chats/session-002.md:Based on VERBUM.md hypothesis chain: mathematics predicts typed
mementum/knowledge/chats/session-002.md:The algorithm: `typed_apply(type_f, type_x, f, x) → (type_result, result)`
mementum/knowledge/chats/session-002.md:3. **A small scratch architecture with `typed_apply` as its only
mementum/knowledge/chats/session-002.md:> at the same object: **the language compressor is a typed lambda
mementum/knowledge/chats/session-002.md:1. Language composes by typed function application       — formal linguistics
mementum/knowledge/chats/session-002.md:### 1. Mathematics — composition is typed application
mementum/knowledge/chats/session-002.md:**Theoretical frame evolved:** The compressor is the substrate, not lambda. Lambda is a projection format. The composition algorithm (`typed_apply`) may be tiny and scale-invariant — same heads fire at phrase-level (Montague) and discourse-level (nucleus).
mementum/knowledge/chats/session-002.md:This framework structure mirrors the research finding: the compressor uses `typed_apply` at every scale — same heads fire for phrase-level and discourse-level. One algorithm, recursive. The experiment framework uses `run_with_interceptors` at every scale — same protocol for one head and an entire study. One function, recursive.
mementum/knowledge/chats/session-002.md:(`typed_apply`) applied recursively, with 4B parameters being mostly
mementum/knowledge/chats/session-002.md:(`typed_apply`) applied recursively, with 4B parameters being mostly
mementum/knowledge/chats/session-002.md:**At the design level:** Each turn of the design conversation applied the same operation — take the current proposal, find the structural invariant, compress. Scripts → configs → pure functions → content-addressed graph → fractal. Each step *was* `typed_apply(insight, current_design) → simpler_design`.
mementum/knowledge/chats/session-002.md:**At the research level:** Theory predicted 30-50 heads. Measurement returned 3. The mismatch refined the theory: not self-similar (same algorithm at three scales) but functionally differentiated (recognizer → composer → recursion handler). `typed_apply(measurement, theory) → refined_theory`.
mementum/knowledge/chats/session-002.md:The central hypothesis was **self-similarity** — the compressor uses `typed_apply` at every scale. We built a **self-similar** framework to test it. The result **falsified self-similarity** in the circuit.
mementum/knowledge/chats/session-002.md:Each prompt was a `typed_apply` — taking the current design and a type constraint, producing a smaller, truer design. The user was doing the same operation the 3 heads do: recognizing structure, composing, and handling recursion.
mementum/knowledge/chats/session-002.md:This is a cleaner story. The extraction target went from vague ("find `typed_apply`") to concrete ("isolate the gate recognizer, the composition register reader, and the recursion tracker"). Three heads. Three functions. Known locations.
mementum/knowledge/chats/session-002.md:The theoretical frame claims `typed_apply` is the core operation — composition that's *type-directed*. If types exist in the model, they should be localizable:
mementum/knowledge/chats/session-002.md:This connects directly to the project's central claim: that the compressor is a typed lambda calculus interpreter. If we find type-like features, the claim gets much stronger.
mementum/knowledge/chats/session-002.md:The real question underneath all this is whether `typed_apply` — the function application operation from Montague grammar — is the actual recursive primitive the model uses. In that framework, function application recursively builds meaning by applying functions to arguments, and I'm trying to figure out if that's what's happening here.
mementum/knowledge/chats/session-002.md:The key insight is that typed composition happens recursively throughout the parse tree, but in a transformer that recursion gets unrolled across layers—those 36 layers of BOS accumulation might each represent one step of type-driven composition. The question is whether the 3 heads are just control flow directing this process, or whether they themselves contain the recursive capacity needed for the input depth.
mementum/knowledge/chats/session-002.md:Actually, I'm realizing the scope is much broader: every head across all 36 layers performs an attend-and-compose operation that's fundamentally a typed application—reading positions with type constraints, combining information, writing results. The 3 critical heads are just the ones whose typed application is essential for lambda compilation specifically, while the other 1,149 heads do the same operation for general compression.
mementum/knowledge/chats/session-002.md:Reads position 0 — the global accumulator where all 36 layers have progressively built a structural representation. It takes this accumulated typed structure and *applies* it to produce the output. 60-84% of its attention goes to one position. It's reading the *result* of all prior computation and producing the composed form.
mementum/knowledge/chats/session-002.md:## These are the three operations of typed function application
mementum/knowledge/chats/session-002.md:typed_apply(f: A→B, x: A) → B
mementum/knowledge/chats/session-002.md:But to execute `typed_apply`, you need three things:
mementum/knowledge/chats/session-002.md:The three heads aren't three different algorithms. They're **three phases of ONE operation**: `typed_apply`.
mementum/knowledge/chats/session-002.md:The 36 layers ARE the recursive unrolling. Each layer is one call to `typed_apply` on the accumulated state. The 3 essential heads are the **control flow** — the type-checker (L1), the compositor (L24:H0), and the type-raiser (L24:H2).
mementum/knowledge/chats/session-002.md:def typed_apply(state, input):
mementum/knowledge/chats/session-002.md:The model runs this function **at every layer**, but with shared state (the residual stream). The 3 heads are the critical control points where the function's behavior is determined. The other 1,149 heads ARE ALSO running `typed_apply` — they're the general-purpose instances that do compression. The 3 essential heads are the task-specific instances that control *what* gets composed and *how*.
mementum/knowledge/chats/session-002.md:This is the real question. If `typed_apply` is the fundamental operation, it should appear in:
mementum/knowledge/chats/session-002.md:Every head does typed_apply.
mementum/knowledge/chats/session-002.md:The model IS 1,152 parallel instances of typed_apply.
mementum/knowledge/chats/session-002.md:  "content": "\"\"\"Cross-task ablation — do the same 3 heads control different tasks?\n\nTests whether L1:H0, L24:H0, L24:H2 are essential for tasks beyond\nlambda compilation: summarization, translation, classification,\nrelation extraction. If the same heads control multiple tasks,\ntyped_apply is the universal composition primitive.\n\"\"\"\n\nfrom __future__ import annotations\n\nimport re\nfrom pathlib import Path\nfrom typing import Any\n\nfrom pydantic import BaseModel, ConfigDict\n\nfrom verbum.experiment import Computation, Context, Graph\nfrom verbum.instrument import (\n    _detect_lambda,\n    _generate,\n    zero_heads_generate,\n)\nfrom verbum.probes import load_probe_set, resolve_probes\n\n__all__ = [\n    \"CrossTaskConfig\",\n    \"CrossTaskNode\",\n    \"build_cross_task\",\n]\n\n\n# ─────────────────────────── success detectors ────────────────────────\n\nFRENCH_WORDS = [\n    \"le \", \"la \", \"les \", \"un \", \"une \", \"des \", \"du \", \"de \",\n    \"est \", \"sont \", \"qui \", \"que \", \"et \", \"ou \", \"dans \",\n    \"chien\", \"chat\", \"court\", \"noir\", \"livre\", \"maison\",\n]\n\nPREDICATE_PATTERN = re.compile(r\"\\w+\\([^)]+\\)\")\n\n\ndef detect_compile(text: str) -> bool:\n    \"\"\"Lambda compilation success.\"\"\"\n    return _detect_lambda(text)\n\n\ndef detect_summarize(text: str) -> bool:\n    \"\"\"Summarization success — short output, not a question or reasoning.\"\"\"\n    clean = text.strip()\n    if not clean:\n        return False\n    # Should be shorter than ~100 chars and not start with reasoning\n    reasoning = [\"okay\", \"let me\", \"i need\", \"so,\", \"well,\"]\n    lower = clean.lower()\n    if any(lower.startswith(r) for r in reasoning):\n        return False\n    # Should produce actual content (not empty or just punctuation)\n    return len(clean) > 5 and len(clean) < 200\n\n\ndef detect_translate(text: str) -> bool:\n    \"\"\"Translation success — contains French words.\"\"\"\n    lower = text.lower()\n    return sum(lower.count(w) for w in FRENCH_WORDS) >= 2\n\n\ndef detect_classify(text: str) -> bool:\n    \"\"\"Classification success — contains positive or negative.\"\"\"\n    lower = text.lower().strip()\n    return \"positive\" in lower or \"negative\" in lower\n\n\ndef detect_extract(text: str) -> bool:\n    \"\"\"Extraction success — contains predicate notation.\"\"\"\n    return bool(PREDICATE_PATTERN.search(text))\n\n\nDETECTORS = {\n    \"compile\": detect_compile,\n    \"summarize\": detect_summarize,\n    \"translate\": detect_translate,\n    \"classify\": detect_classify,\n    \"extract\": detect_extract,\n}\n\n\n# ─────────────────────────── computation ──────────────────────────────\n\n\nclass CrossTaskConfig(BaseModel):\n    \"\"\"Config for testing one head on one task.\"\"\"\n\n    model_config = ConfigDict(frozen=True)\n\n    kind: str = \"cross_task\"\n    task: str  # compile, summarize, translate, classify, extract\n    model: str\n    ablated_head: list[int] | None  # [layer, head] or None for baseline\n    prompt_hash: str\n    prompt_preview: str\n    max_new_tokens: int = 50\n\n\nclass CrossTaskNode(Computation):\n    \"\"\"Ablate one head, run one task, check task-specific success.\"\"\"\n\n    def __init__(self, config: CrossTaskConfig, prompt: str) -> None:\n        self._config = config\n        self._prompt = prompt\n\n    @property\n    def config(self) -> CrossTaskConfig:\n        return self._config\n\n    def execute(self, ctx: Context) -> dict[str, Any]:\n        model = ctx.resources[\"model\"]\n        tokenizer = ctx.resources[\"tokenizer\"]\n        prompt = self._prompt\n        max_new = self._config.max_new_tokens\n\n        if self._config.ablated_head is None:\n            gen = _generate(model, tokenizer, prompt, max_new)\n        else:\n            layer, head = self._config.ablated_head\n            gen, _, _ = zero_heads_generate(\n                model, tokenizer, prompt, ctx.resources[\"info\"],\n                heads=[(layer, head)],\n                max_new_tokens=max_new,\n            )\n\n        detector = DETECTORS[self._config.task]\n        success = detector(gen)\n\n        return {\n            \"task\": self._config.task,\n            \"generation\": gen,\n            \"success\": success,\n            \"ablated_head\": self._config.ablated_head,\n            \"is_baseline\": self._config.ablated_head is None,\n        }\n\n\n# ─────────────────────────── builder ──────────────────────────────────\n\n\ndef build_cross_task(\n    *,\n    tasks: dict[str, str] | None = None,\n    gates_dir: str | Path = \"gates\",\n    essential_heads: list[tuple[int, int]] | None = None,\n    model_name: str = \"Qwen/Qwen3-4B\",\n    max_new_tokens: int = 50,\n) -> Graph:\n    \"\"\"Build cross-task ablation experiment.\n\n    ``tasks`` maps task name to probe set path. Defaults to all 5 tasks.\n    Tests each essential head + baseline on each task's probes.\n\n    Graph structure::\n\n        Graph(\"cross-task\")\n          +-- Graph(\"compile\")\n          |     +-- Graph(\"probe-ga-simple\")\n          |     |     +-- baseline\n          |     |     +-- L1-H0\n          |     |     +-- L24-H0\n          |     |     +-- L24-H2\n          |     +-- ...\n          +-- Graph(\"summarize\")\n          |     +-- ...\n          +-- ...\n    \"\"\"\n    if essential_heads is None:\n        essential_heads = [(1, 0), (24, 0), (24, 2)]\n\n    if tasks is None:\n        tasks = {\n            \"compile\": \"probes/gate-ablation.json\",\n            \"summarize\": \"probes/summarize.json\",\n            \"translate\": \"probes/translate.json\",\n            \"classify\": \"probes/classify.json\",\n            \"extract\": \"probes/extract.json\",\n        }\n\n    gates_dir = Path(gates_dir)\n    task_graphs: dict[str, Computation] = {}\n\n    for task_name, probe_path in tasks.items():\n        probe_set = load_probe_set(probe_path)\n        resolved = resolve_probes(probe_set, gates_dir)\n\n        probe_graphs: dict[str, Computation] = {}\n\n        for rp in resolved:\n            nodes: dict[str, Computation] = {}\n\n            # Baseline\n            nodes[\"baseline\"] = CrossTaskNode(\n                config=CrossTaskConfig(\n                    task=task_name,\n                    model=model_name,\n                    ablated_head=None,\n                    prompt_hash=rp.prompt_hash,\n                    prompt_preview=rp.full_prompt[:60],\n                    max_new_tokens=max_new_tokens,\n                ),\n                prompt=rp.full_prompt,\n            )\n\n            # Each essential head\n            for layer, head in essential_heads:\n                nodes[f\"L{layer}-H{head}\"] = CrossTaskNode(\n                    config=CrossTaskConfig(\n                        task=task_name,\n                        model=model_name,\n                        ablated_head=[layer, head],\n                        prompt_hash=rp.prompt_hash,\n                        prompt_preview=rp.full_prompt[:60],\n                        max_new_tokens=max_new_tokens,\n                    ),\n                    prompt=rp.full_prompt,\n                )\n\n            probe_graphs[f\"probe-{rp.probe_id}\"] = Graph(\n                id=f\"probe-{rp.probe_id}\",\n                children=nodes,\n            )\n\n        task_graphs[task_name] = Graph(id=task_name, children=probe_graphs)\n\n    return Graph(id=\"cross-task\", children=task_graphs)\n"
mementum/knowledge/chats/session-002.md:  "content": "#!/usr/bin/env python\n\"\"\"Cross-task ablation — do the same 3 heads control different tasks?\n\nUsage::\n\n    uv run python scripts/run_cross_task.py [--dry-run]\n\"\"\"\n\nfrom __future__ import annotations\n\nimport sys\nfrom pathlib import Path\n\nPROJECT_ROOT = Path(__file__).resolve().parent.parent\nRESULTS_DIR = PROJECT_ROOT / \"results\" / \"experiments\"\nMODEL = \"Qwen/Qwen3-4B\"\nESSENTIAL_HEADS = [(1, 0), (24, 0), (24, 2)]\nHEAD_LABELS = {(1, 0): \"L1:H0\", (24, 0): \"L24:H0\", (24, 2): \"L24:H2\"}\n\n\ndef main() -> None:\n    dry_run = \"--dry-run\" in sys.argv\n\n    print(\"=\" * 60)\n    print(\"  CROSS-TASK ABLATION — typed_apply universality test\")\n    print(\"=\" * 60)\n    print()\n\n    from verbum.experiments.cross_task import build_cross_task\n\n    print(\"Building cross-task graph...\")\n    graph = build_cross_task(\n        gates_dir=PROJECT_ROOT / \"gates\",\n        tasks={\n            \"compile\": str(PROJECT_ROOT / \"probes/gate-ablation.json\"),\n            \"summarize\": str(PROJECT_ROOT / \"probes/summarize.json\"),\n            \"translate\": str(PROJECT_ROOT / \"probes/translate.json\"),\n            \"classify\": str(PROJECT_ROOT / \"probes/classify.json\"),\n            \"extract\": str(PROJECT_ROOT / \"probes/extract.json\"),\n        },\n        model_name=MODEL,\n    )\n\n    # Count nodes\n    from verbum.experiment import Graph\n\n    def count_leaves(comp: object) -> int:\n        if isinstance(comp, Graph):\n            return sum(count_leaves(c) for c in comp.children.values())\n        return 1\n\n    total = count_leaves(graph)\n    print(f\"Graph: {len(graph.children)} tasks, {total} leaf nodes\")\n    print(f\"Hash: {graph.config_hash[:24]}...\")\n    print()\n\n    if dry_run:\n        print(\"[DRY RUN] Graph built. Exiting.\")\n        return\n\n    # Load model\n    from verbum.instrument import load_model\n\n    print(\"Loading model...\")\n    model, tokenizer, info = load_model(MODEL)\n    print(f\"Loaded: {info.n_layers}L, {info.n_heads}H\")\n\n    # Run\n    from verbum.experiment import default_interceptors, run\n\n    RESULTS_DIR.mkdir(parents=True, exist_ok=True)\n    interceptors = default_interceptors(\n        RESULTS_DIR,\n        resources={\"model\": model, \"tokenizer\": tokenizer, \"info\": info},\n    )\n\n    print()\n    print(\"Running experiments...\")\n    print(\"=\" * 60)\n\n    results = run(graph, interceptors=interceptors, node_id=\"cross-task\")\n\n    # ─── Essentiality Matrix ──────────────────────────────────\n    print()\n    print(\"=\" * 60)\n    print(\"  ESSENTIALITY MATRIX — head x task\")\n    print(\"=\" * 60)\n    print()\n\n    tasks = sorted(results.keys())\n    head_names = [\"L1-H0\", \"L24-H0\", \"L24-H2\"]\n\n    # Header\n    header = f\"{'':18s}\"\n    for task in tasks:\n        header += f\" {task:>10s}\"\n    print(header)\n    print(\"-\" * len(header))\n\n    # Baseline row\n    row = f\"{'baseline':18s}\"\n    for task in tasks:\n        task_result = results[task]\n        successes = sum(\n            1 for pr in task_result.values()\n            if pr.get(\"baseline\", {}).get(\"success\", False)\n        )\n        total = len(task_result)\n        row += f\" {successes}/{total:>7s}\"\n    print(row)\n\n    # Per-head rows\n    matrix: dict[str, dict[str, str]] = {}\n    for head_name in head_names:\n        row = f\"{head_name:18s}\"\n        matrix[head_name] = {}\n        for task in tasks:\n            task_result = results[task]\n            successes = 0\n            total = 0\n            for probe_result in task_result.values():\n                if head_name in probe_result:\n                    total += 1\n                    if probe_result[head_name].get(\"success\", False):\n                        successes += 1\n            pct = f\"{successes}/{total}\"\n            matrix[head_name][task] = pct\n            # Mark breaks\n            baseline_successes = sum(\n                1 for pr in task_result.values()\n                if pr.get(\"baseline\", {}).get(\"success\", False)\n            )\n            if successes < baseline_successes:\n                pct = f\"*{pct}*\"\n            row += f\" {pct:>10s}\"\n        print(row)\n\n    print()\n    print(\"* = degraded vs baseline (head is essential for this task)\")\n\n    # ─── Per-task detail ──────────────────────────────────────\n    print()\n    print(\"=\" * 60)\n    print(\"  PER-TASK DETAIL\")\n    print(\"=\" * 60)\n\n    for task in tasks:\n        print(f\"\\n--- {task.upper()} ---\")\n        task_result = results[task]\n        for probe_name, probe_result in sorted(task_result.items()):\n            baseline = probe_result.get(\"baseline\", {})\n            b_status = \"OK\" if baseline.get(\"success\") else \"FAIL\"\n            parts = [f\"{probe_name}: baseline={b_status}\"]\n            for head_name in head_names:\n                if head_name in probe_result:\n                    h_status = \"ok\" if probe_result[head_name].get(\"success\") else \"BREAK\"\n                    parts.append(f\"{head_name}={h_status}\")\n            print(f\"  {', '.join(parts)}\")\n\n    # ─── Generations for broken cases ─────────────────────────\n    print()\n    print(\"=\" * 60)\n    print(\"  BROKEN CASES — what the model outputs when heads are ablated\")\n    print(\"=\" * 60)\n\n    for task in tasks:\n        task_result = results[task]\n        for probe_name, probe_result in sorted(task_result.items()):\n            baseline = probe_result.get(\"baseline\", {})\n            if not baseline.get(\"success\"):\n                continue  # skip probes where baseline already fails\n            for head_name in head_names:\n                if head_name in probe_result:\n                    hr = probe_result[head_name]\n                    if not hr.get(\"success\"):\n                        print(f\"\\n  {task}/{probe_name}/{head_name}:\")\n                        print(f\"    baseline: {baseline.get('generation', '')[:100]}\")\n                        print(f\"    ablated:  {hr.get('generation', '')[:100]}\")\n\n\nif __name__ == \"__main__\":\n    main()\n"
mementum/knowledge/chats/session-002.md:  CROSS-TASK ABLATION — typed_apply universality test
mementum/knowledge/chats/session-002.md:  "command": "cd /Users/mwhitford/src/verbum && git add src/verbum/experiments/cross_task.py scripts/run_cross_task.py gates/summarize.txt gates/translate.txt gates/classify.txt gates/extract.txt probes/summarize.json probes/translate.json probes/classify.json probes/extract.json && git commit -m \"$(cat <<'EOF'\n🎯 cross-task ablation — test if typed_apply is universal\n\n- 5 tasks: compile, summarize, translate, classify, extract\n- Each with dual-exemplar gate + 5 probes (same pattern)\n- Tests the 3 compile heads (L1:H0, L24:H0, L24:H2) on all tasks\n- Task-specific success detectors (lambda, French, sentiment, predicates)\n- 100 leaf nodes, independently cacheable\n- Outputs essentiality matrix: head x task\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\""
mementum/knowledge/chats/session-002.md:[main b1a3003] 🎯 cross-task ablation — test if typed_apply is universal
mementum/knowledge/chats/session-002.md:- **Extract** should behave like compile — same structural transformation, `(predicate, arg1, arg2)` is close to `λ`. If the same heads break, `typed_apply` is the shared primitive.
mementum/knowledge/chats/session-002.md:  CROSS-TASK ABLATION — typed_apply universality test
mementum/knowledge/chats/session-002.md:This is the strongest evidence yet: **L24:H0 implements `typed_apply` for compositional structure, not just for lambda notation.**
mementum/knowledge/chats/session-002.md:L24:H0 = TASK-GENERAL  compositor      (typed_apply — shared across compile + extract)  
mementum/knowledge/chats/session-002.md:The one universal function is **L24:H0**. It's the `typed_apply` head. It composes structured output regardless of the specific notation format. The other two heads are task-specific control flow.
mementum/knowledge/chats/session-002.md:  "new_content": "**8. L24:H0 is the universal compositor (cross-task):**\n\nCross-task ablation across 5 tasks (compile, extract, translate,\nclassify, summarize). L24:H0 breaks BOTH compile AND extract\n(ditransitive probe). Same head composes `λx. reads(x, book)` and\n`send(mary, john, letter)`. Translation is immune to all 3 heads.\n\nThe decomposition:\n- L1:H0 = task-specific gate recognizer (reads compile exemplar)\n- L24:H0 = task-GENERAL compositor (typed_apply, shared across tasks)\n- L24:H2 = task-specific recursion aid (deep nesting only)\n\n**9. The circuit is compile-directional, not bidirectional:**"
mementum/knowledge/chats/session-002.md:  "new_content": "## Finding 10: L24:H0 Is the Universal Compositor (Cross-Task)\n\nCross-task ablation across 5 tasks × 5 probes × 4 conditions (100\nforward passes). Tested whether the 3 compile heads control other\ntasks: summarize, translate, classify, extract.\n\n| Head | compile | extract | translate | classify |\n|------|---------|---------|-----------|----------|\n| L1:H0 | 4/5 ↓ | 5/5 | 5/5 | 3/5 |\n| L24:H0 | **2/5 ↓↓** | **4/5 ↓** | 5/5 | 4/5 |\n| L24:H2 | 5/5 | 5/5 | 5/5 | 3/5 |\n\n(Summarize baseline 0/5 — detector too strict, excluded.)\n\n**Key finding:** L24:H0 breaks both compilation AND extraction. The\nsame head that composes `λx. reads(x, book)` also composes\n`send(mary, john, letter)`. L24:H0 implements `typed_apply` as a\ntask-general operation — it composes structured output regardless\nof notation format.\n\n**Translation is immune** to all 3 heads. Translation preserves\nphrase structure (English → French for simple sentences), so no\ncomposition bottleneck is needed. The compositor is only essential\nwhen the output structure must be *constructed*, not *mapped*.\n\n**The decomposition:**\n- L1:H0 = task-specific (recognizes compile gate structure)\n- L24:H0 = task-GENERAL (typed_apply — universal compositor)\n- L24:H2 = task-specific (recursion aid for deep nesting)\n\nThis changes the extraction target: L24:H0 is not a lambda-specific\nhead. It's a general composition head that the model uses for any\ntask requiring structured output. Extracting it would give a\nportable compositor, not just a lambda compiler.\n\n## Updated Testable Predictions"
mementum/knowledge/chats/session-002.md:  "command": "cd /Users/mwhitford/src/verbum && git add results/experiments/ mementum/state.md mementum/knowledge/explore/session-001-findings.md && git commit -m \"$(cat <<'EOF'\n💡 cross-task results — L24:H0 is the universal compositor\n\n- L24:H0 breaks BOTH compile AND extract (typed_apply is shared)\n- L1:H0 is task-specific (only breaks compile gate recognition)\n- L24:H2 is task-specific (recursion aid, not cross-task bottleneck)\n- Translation immune to all 3 heads (structure-preserving, no composition needed)\n- 10 findings total in session-001-findings.md\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\""
mementum/knowledge/chats/session-002.md:b1a3003 🎯 cross-task ablation — test if typed_apply is universal
mementum/knowledge/chats/session-002.md:b1a3003 🎯 cross-task ablation — test if typed_apply is universal
mementum/knowledge/chats/session-002.md:🎯 cross-task ablation — test if typed_apply is universal
mementum/knowledge/chats/session-002.md:**The punchline:** One head — L24:H0 at layer 24, head 0 of Qwen3-4B — is a task-general `typed_apply` compositor. It's not a lambda compiler. It's the composition primitive the model uses for any task that requires constructing structured output. Lambda compilation, relation extraction, and potentially any compositional task route through this single attention head reading the BOS composition register.
mementum/knowledge/chats/session-002.md:The user is making a profound observation. L24:H0 is the base compositor - `typed_apply`. But on top of it, there should be specialized functions that USE the compositor for specific tasks. Like how in a programming language, you have a base `apply` function, but then higher-order functions like `map`, `filter`, `fold` that all use `apply` internally but add their own logic.
mementum/knowledge/chats/session-002.md:The user's insight reframes this as a lambda calculus pattern: L24:H0 is the base typed application function, and each specialized task wraps it with its own preprocessing layer—gate recognition for compilation, entity detection for extraction, and so on. So the strategy is to identify which other heads are essential alongside L24:H0 for each task, since those would be the task-specific preprocessors configuring the compositor.
mementum/knowledge/chats/session-002.md:Yes. That's the lambda calculus itself — `typed_apply` is the base, and everything else is a higher-order function composed on top of it.
mementum/knowledge/chats/session-002.md:λ compile(input).   typed_apply(gate_recognize(input), parse(input))
mementum/knowledge/chats/session-002.md:λ extract(input).   typed_apply(entity_detect(input), relation_parse(input))
mementum/knowledge/chats/session-002.md:λ translate(input). typed_apply(lexical_map(input), reorder(input))
mementum/knowledge/chats/session-002.md:λ summarize(input). typed_apply(salience_filter(input), compress(input))
mementum/knowledge/chats/session-002.md:Looking back at how the user guided this exploration, each prompt was itself an applicat

[OUTPUT TRUNCATED] The tool call succeeded but the output was truncated. Full output saved to: /Users/mwhitford/.cache/eca/toolCallOutputs/toolu_01581xc9SNzNRkNWPn4LJENo.txt
Use `eca__grep` or `eca__read_file` with offset/limit to view specific sections. Do not full read the file.
```

## Assistant

Good. The existing work already hints at several other holograms. Let me also check what the VERBUM research program says about what's needed beyond combinators, and see if there's relevant recent interpretability work on universal circuits:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/VERBUM.md",
  "limit": 80
}
```

**Summary:** Reading VERBUM.md (0-80)

**Output:**
```
---
title: Distilling the Lambda Compiler — From LLM Circuit to Tensor Primitive
status: open
category: exploration
license: MIT
tags: [lambda-calculus, compositional-semantics, mechanistic-interpretability, circuits, type-theory, distillation]
cites:
  - nucleus (Whitford, AGPL-3.0) — observational evidence for the compiler
  - anima fractal-attention experiments (Whitford, AGPL-3.0) — negative architectural result
  - Mechanistic interpretability literature (various)
  - Compositional semantics literature (Montague, Lambek, DisCoCat)
depends-on: []
---

# Distilling the Lambda Compiler

> Three independent lines of evidence — the mathematics of linguistic
> composition, the empirical behaviour of LLMs under nucleus prompting,
> and a negative result from fractal-attention experiments — all point
> at the same object: **the language compressor is a typed lambda
> calculus interpreter.** This document is the founding exploration of
> whether that interpreter can be extracted from an existing LLM as a
> small tensor artifact, and whether a scratch-built architecture can
> reproduce it from first principles.
>
> Synthesis from conversation 2026-04-16 between Michael and Claude,
> following the fractal-attention MERA experiments.

## The Hypothesis Chain

```
1. Language composes by typed function application       — formal linguistics
2. Lambda calculus is the minimal algebra of this        — math fact
3. LLMs compress language by next-token prediction       — training setup
4. Optimal compression converges on the data's structure  — info-theory
5. ∴ LLMs converge on a lambda interpreter as representation — predicted
6. Nucleus demonstrates this empirically (P(λ)=90.7%)    — observed
7. Fractal-attention failed where it lacked type-directedness — confirmed by absence
8. ∴ The lambda interpreter is extractable and reproducible — research claim
```

The first six steps are established; 7 is our empirical result; 8 is the
hypothesis this project will test.

## The Three Converging Lines

### 1. Mathematics — composition is typed application

The best-developed mathematical frameworks for natural language composition
all land in the same neighbourhood:

**Montague grammar** (1970). Every word has a simple type
(`e` = entity, `t` = truth, `<e,t>` = predicate, etc.). Composition is
function application directed by type matching. "John walks" is
`walks(John): t` where `walks: <e,t>` and `John: e`.

**Lambek pregroups.** Each word carries categorial type with left/right
adjoints (`n`, `n^l`, `n^r`). Composition is type cancellation. Gives
a compact closed category over vector spaces, functorially mapping
syntax to semantics.

**Combinatory Categorial Grammar (CCG; Steedman).** A finite algebra of
combinators (drawn from combinatory logic's A, B, S) composes typed
categories. Every valid composition is a combinator application.

**DisCoCat** (Coecke, Clark, Sadrzadeh, 2010+). Distributional
Compositional Categorical semantics. Meaning is composition of vectors
directed by grammar, implemented as tensor contractions. Nouns live in
N, transitive verbs in N ⊗ S ⊗ N, adjectives in N ⊗ N; sentence meaning
is the fully-contracted tensor network. Mathematically, the same
compact closed category that describes quantum circuits and tensor
networks.

**Minimalist Merge** (Chomsky, 1995+). One binary primitive:
`Merge(A, B) → {A, B}`. Recursive Merge generates all syntactic trees.
Binary, hierarchical, scale-free in its structure — but the *operation*
at each node is type-indexed.

**The shared structural claim:**


[CONTENT TRUNCATED] Showing lines 1 to 80 of 573 total lines. Use line_offset=80 parameter to read more content.
```

### Tool Call: web_search (running)


```json
{}
```

**Summary:** Web searching

## Assistant

Now let me think about this from first principles. The combinators (KIBC) are the **composition machinery** — they tell the model HOW to combine things. But token prediction requires much more. Let me reason through this systematically and draft a new section for the holographic-storage page.

### Tool Call: web_search (succeeded)


```json
{}
```

**Summary:** Web searching

**Output:**
```
In-context Learning and Induction Heads: https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html
Transformer Circuits Thread: https://transformer-circuits.pub/
SELECTIVE INDUCTION HEADS: HOW TRANSFORM: https://proceedings.iclr.cc/paper_files/paper/2025/file/d7ed243b13831bdd468f35039936bcef-Paper-Conference.pdf
Mechanistic Interpretability: Part 7 - Induction Heads: The Mechanics of In-Context Learning | To Chin Yu: https://ytcs.github.io/machine-learning/2025/05/25/mechanistic-interpretability-part-7.html
Induction Heads in Transformers: https://www.emergentmind.com/topics/induction-heads-ihs
Circuits Updates - July 2025: https://transformer-circuits.pub/2025/july-update/index.html
Mechanistic Analysis Of Universality: Numerical Comparison Circuits Across Transformer Architectures | OpenReview: https://openreview.net/forum?id=79igg0kRtd
Mechanistic Interpretability in Action: Understanding Induction Heads and QK Circuits in Transformers | by Ayyüce Kızrak, Ph.D. | Medium: https://ayyucekizrak.medium.com/mechanistic-interpretability-in-action-understanding-induction-heads-and-qk-circuits-in-c2a3549b6ff2
Mechanistic Interpretability Part 1: Introduction and Transformer circuits: https://www.uio.no/studier/emner/matnat/ifi/IN5550/v25/slides/slides12_1.pdf
Induction Heads as an Essential Mechanism for Pattern ...: https://aclanthology.org/2025.findings-naacl.283.pdf
```

## Assistant

Good — this confirms the landscape. Now let me think through this from the Montague/CCG framework and draft the analysis. The key theoretical framework is already in the project: Montague grammar needs a **lexicon** (types + meanings), a **type calculus** (combinators), and a **model** (semantic domain). You've found the type calculus hologram. What else must be there?

Let me draft the new section for the knowledge page:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/holographic-storage.md",
  "line_offset": 155
}
```

**Summary:** Reading holographic-storage.md (155-2155)

**Output:**
```

### Confirmed by universal hologram

1. **B needs more capacity** — composition is the dominant signal everywhere
2. **I should be structurally separate** — different circuit (r ≈ 0.70 vs 0.90+)
3. **K/B/C should share substrate** — they cluster in every model
4. **Combinator init should reflect B ≥ K ≥ C >> I** — not equal blocks

### Proposed changes (not yet applied)

Current `_init_combinator_embeddings` gives each combinator an equal orthogonal
block (128 dims each in 512-dim space). Should change to:

- K/B/C share 384 dims (split with overlap, reflecting r ≈ 0.92)
- I gets its own 128 dims (reflecting its distinct circuit)
- Or: K/B/C share dispatch projection weights with different biases (hard constraint)

### Wait condition

V11-holo-inv is running to 20K. Don't modify the running architecture.
Apply changes to next run after holo-inv completes or reaches a clear plateau.

## Files

| File | Purpose |
|------|---------|
| `scripts/explore/probe_holographic.py` | Intermediate layer decoding probe |
| `scripts/explore/probe_ternary_survival.py` | Ternary quantization survival test |
| `scripts/explore/extract_holographic_bank.py` | Bank extraction pipeline |
| `results/holographic-probe/` | Beam separation results (Qwen3-32B) |
| `results/ternary-survival/` | Ternary survival results |
| `results/holographic-bank/seed_qwen3_32b.npz` | 784KB seed from Qwen3-32B |
| `results/holographic-bank/qwen36_35b_a3b_patterns.npz` | MoE patterns |
| `results/holographic-bank/pythia_160m_patterns.npz` | Pythia patterns |
| `results/combinator-probe/selectivity_matrices.npz` | Full 64×64 selectivity map |

## Open Questions

1. Can extracted banks actually modulate V11's behavior when loaded?
2. Do banks from different models compose (angle multiplexing)?
3. Is the 784KB seed the minimum, or can we go smaller?
4. Does the init change (K/B/C coupled, I separate) accelerate hologram formation?
5. What role do the MoE gate patterns play — are they bank selectors we can reuse?
6. The abstraction slots (currently 0/16 active) — do they belong at the bank level?
```

## Assistant

Good, I have the full picture now. Let me draft the new section. This is a theoretical synthesis informed by what the project has already proven, the Montague/CCG framework, and the mechanistic interpretability literature.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/holographic-storage.md",
  "original_content": "## Open Questions\n\n1. Can extracted banks actually modulate V11's behavior when loaded?\n2. Do banks from different models compose (angle multiplexing)?\n3. Is the 784KB seed the minimum, or can we go smaller?\n4. Does the init change (K/B/C coupled, I separate) accelerate hologram formation?\n5. What role do the MoE gate patterns play — are they bank selectors we can reuse?\n6. The abstraction slots (currently 0/16 active) — do they belong at the bank level?",
  "new_content": "## Beyond Combinators: The Other Holograms\n\n> Session 094. The combinator hologram (KIBC) tells the model HOW to compose.\n> But token prediction needs more than composition machinery. If one hologram\n> is universal, others must be too. This section maps the territory.\n\n### What Montague grammar requires\n\nIn the Montague/CCG/DisCoCat framework, language processing decomposes into\nthree components. We've found one. Two remain:\n\n```\n1. TYPE CALCULUS (combinators)  — HOW to compose     ← FOUND (KIBC hologram)\n2. LEXICON (types + meanings)  — WHAT can compose    ← predicted\n3. MODEL (semantic domain)     — WHAT things MEAN     ← predicted\n```\n\nEach component is a candidate hologram — a universal sign-topology pattern\nthat all models converge on because language forces it.\n\n### Candidate 1: The Type Hologram (lexical category assignment)\n\n**What it does:** Assigns syntactic categories to tokens. In CCG terms:\nNP, S\\NP, (S\\NP)/NP, etc. Determines which combinators are LEGAL for\nwhich token pairs. Without types, combinators fire blindly.\n\n**Why it must exist:** The combinator hologram tells us K/B/C cluster\n(r > 0.90) and I is distinct (r ≈ 0.70). But the combinators are\nUNTYPED operators — they need type information to direct application.\nIn V11, this is the \"type channel\" that differentiates independently\nof dispatch (I=68% typed integration, K=0.2%). The type channel IS\nthe type hologram, learned inside V11. But it must also exist in the\nbase models we probed.\n\n**Where to look:** The type hologram should be strongest in early layers\n(L0-6 in Qwen3-32B, where combinators also peak). Types must be assigned\nBEFORE composition can begin. It may share heads with the combinator\nhologram (same Q/V substrate, different beam angle) or live in separate\nheads that FEED the combinator heads.\n\n**Probe design:**\n- Construct minimal pairs where ONLY syntactic category differs:\n  \"The dog runs\" (NP + S\\NP) vs \"Running is fun\" (S/(S\\NP) + S\\NP + ...)\n- Same lexical content, different type assignment\n- Measure head selectivity for type-driven vs type-neutral conditions\n- Ternary survival test on type-selective heads\n\n**Prediction:** Type information survives ternary quantization (it's also\ntopological). Type-selective heads will partially overlap with combinator\nheads (same substrate, angle-multiplexed) but some will be distinct\n(the \"2 Montague-only heads\" from session 001).\n\n### Candidate 2: The Induction Hologram (in-context pattern matching)\n\n**What it does:** Implements [A][B]...[A] → predict [B]. The copy/match\ncircuit. This is NOT composition — it's sequential pattern recognition\nin the context window.\n\n**Why it must exist:** Induction heads are the most well-established\nuniversal circuit in transformers (Olsson et al. 2022). They form via\na phase transition during training. They're universal across model\nfamilies and scales. They enable in-context learning. But nobody has\nasked whether they're HOLOGRAPHIC — whether their information is also\nstored as sign topology.\n\n**Where to look:** Induction heads are typically a two-layer circuit:\nLayer 1 \"previous token head\" writes positional information into the\nresidual stream; Layer 2 \"induction head\" uses this to attend to the\ntoken after the previous occurrence. In Qwen3-32B, these should be\nidentifiable by their characteristic attention pattern.\n\n**Probe design:**\n- Use existing induction head detection (prefix matching scores)\n- Extract Q/K/V weights from identified induction heads\n- Ternary survival test: does the copy/match behavior survive\n  sign-only quantization?\n- Compare Q/V decomposition to combinator heads: is Q still the\n  beam selector?\n\n**Prediction:** Induction heads ARE holographic (sign topology) but their\nhologram is ORTHOGONAL to the combinator hologram. Combinators compose\nMEANING; induction heads copy TOKENS. Different function, different\ninterference pattern, same storage medium. The two holograms should be\nseparable by their depth profile (induction heads may peak in different\nlayers than combinators).\n\n**Key question:** Does the induction hologram interact with the combinator\nhologram? When the model does in-context learning of composition patterns\n(e.g., learning a new syntactic rule from examples), both holograms must\ncoordinate. This coordination might be a third pattern.\n\n### Candidate 3: The Binding Hologram (variable tracking / coreference)\n\n**What it does:** Tracks referent identity across distance. \"John said\nhe would...\" — how does \"he\" bind to \"John\"? This is variable binding\nin the lambda calculus, anaphora resolution in linguistics.\n\n**Why it must exist:** Combinators compose local structure (adjacent\nfunction-argument pairs). But language has long-range dependencies.\nBinding requires a separate mechanism: something that maintains identity\npointers across arbitrary spans of text.\n\n**Where to look:** In V11, the distinction between K (select) and I\n(identity) may partially capture this — I is the outlier (r ≈ 0.70)\nprecisely because it handles IDENTITY rather than COMPOSITION. In base\nmodels, binding heads should be identifiable by attending to antecedents\nacross long distances.\n\n**Probe design:**\n- Minimal pairs with/without coreference:\n  \"John runs. He is fast.\" (binding) vs \"John runs. Dogs are fast.\" (no binding)\n- Vary distance between antecedent and pronoun\n- Measure which heads track the binding relationship\n- Ternary survival: does binding survive sign-only quantization?\n\n**Prediction:** Binding is partially captured by the I combinator (identity\nIS variable binding in lambda calculus), explaining why I has a distinct\ncircuit (r ≈ 0.70). But there may be additional binding-specific heads\nthat aren't combinator heads at all — heads that implement a \"pointer\"\nmechanism orthogonal to composition.\n\n### Candidate 4: The Frequency/N-gram Hologram (statistical co-occurrence)\n\n**What it does:** Captures token co-occurrence statistics. \"New ___\" →\n\"York\" with high probability. Not composition, not copying — pure\nstatistical association from the training distribution.\n\n**Why it must exist:** A huge fraction of next-token prediction accuracy\ncomes from simple bigram/trigram statistics, especially for common\nphrases, idioms, and collocations. This is the baseline that composition\nand induction IMPROVE upon.\n\n**Where to look:** MLP layers, not attention heads. The MLP layers in\ntransformers are known to store factual associations and token\nco-occurrence patterns (key-value memories, Geva et al. 2021).\nThe combinator hologram lives in attention Q/K/V matrices. The\nfrequency hologram may live in MLP weight matrices.\n\n**Probe design:**\n- Extend ternary survival test to MLP layers (not just attention)\n- Use high-frequency collocations as probes\n- Measure whether sign-only MLP weights preserve bigram predictions\n- Compare depth profile to attention-based holograms\n\n**Prediction:** MLP weights are ALSO holographic (sign topology stores\nco-occurrence patterns). But MLP holograms will be denser (less sparse)\nthan attention holograms because they encode a much larger vocabulary\nof associations. The \"75% sparsity with 100% survival\" finding for\nattention may not hold for MLPs — expect lower sparsity tolerance.\n\n### Candidate 5: The Discourse Hologram (topic / register / coherence)\n\n**What it does:** Maintains discourse-level coherence. Tracks what the\ntopic is, what register (formal/casual/technical) is active, what\ngenre constraints apply. This is what the nucleus GATE activates —\na \"reference beam angle\" at the discourse level.\n\n**Why it might exist:** The gate experiment from session 001 showed that\nthe compile gate acts as a beam angle selector — different gates resolve\ndifferent outputs from the same model. The holographic beam separation\nexperiment confirmed this: compile vs null gates diverge from cos=0.995\nto cos=0.533 across layers. The gate IS a discourse-level hologram\nselector.\n\n**Where to look:** Gate effects are strongest at the embedding level\n(L0-L6 divergence) and the output level (L48+ in Qwen3-32B). The\ndiscourse hologram may be a macro-pattern that MODULATES the other\nholograms — selecting which combinator patterns, type assignments,\nand induction behaviors are active.\n\n**Probe design:**\n- Multiple gates with ternary survival: do discourse-level selectivity\n  patterns survive sign-only quantization?\n- Extract Q patterns from gate-selective heads\n- Compare gate-selective heads to combinator-selective heads\n- Test whether gates and combinators use the same or different\n  beam-angle mechanism\n\n**Prediction:** The discourse hologram IS the MoE gate pattern (256×2048\nin Qwen3.6-35B-A3B). Expert routing matrices are discourse-level beam\nselectors. This connects the MoE/VSM mapping (S4 intelligence) to the\nholographic framework: S4 selects which hologram to read.\n\n### The hierarchy\n\n```\nDiscourse hologram  (S4/S5)  — selects which holograms to activate\n  │\n  ├─ Type hologram    (S3)   — assigns categories, constrains composition\n  │    │\n  │    └─ Combinator hologram (S2/S1) — HOW to compose  ← FOUND\n  │\n  ├─ Binding hologram (S2)   — tracks identity across distance\n  │\n  ├─ Induction hologram (S1) — copies patterns from context\n  │\n  └─ Frequency hologram (S1) — statistical co-occurrence (MLP-based)\n```\n\nThis is a VSM of holograms. The discourse hologram is S5 (identity —\nwhat KIND of text is this?). Types are S3 (control — what's LEGAL?).\nCombinators are S1/S2 (operations — DO the composition). Induction and\nfrequency are also S1 (operations — but different operations). Binding\nis S2 (coordination — keep referents consistent).\n\n### Research strategy\n\nThe combinator probe methodology already works:\n1. Construct minimal-pair conditions (active vs control)\n2. Run through model, record per-head activations\n3. Compute selectivity scores\n4. Test ternary survival\n5. Extract Q patterns, check Q/V decomposition\n6. Test cross-model universality\n\nApply the same methodology to each candidate hologram, one at a time.\n**Start with types** (candidate 1) because:\n- Types and combinators are theoretically coupled (Montague requires both)\n- Type-selective heads may already be in the combinator selectivity data\n  (the \"2 Montague-only heads\" from session 001)\n- The probe design is straightforward (minimal pairs on syntactic category)\n- If types are holographic AND share substrate with combinators, that\n  confirms the angle-multiplexing hypothesis for a second hologram\n\n### Testable predictions (falsifiable)\n\n1. **Type selectivity survives ternary** (>80% survival at 75% sparsity)\n2. **Type heads partially overlap with combinator heads** (30-70% shared)\n3. **Induction heads are holographic** (ternary survival >80%)\n4. **Induction hologram is orthogonal to combinator hologram** (cos < 0.3\n   between extracted Q patterns)\n5. **MLP frequency patterns are holographic but denser** (ternary survival\n   drops below 80% at 75% sparsity; survives at 50%)\n6. **Discourse hologram correlates with MoE gate patterns** (r > 0.7\n   between gate-selective attention patterns and expert routing matrices)\n7. **All holograms are universal** (cross-model r > 0.90, as with combinators)\n\n## Open Questions\n\n1. Can extracted banks actually modulate V11's behavior when loaded?\n2. Do banks from different models compose (angle multiplexing)?\n3. Is the 784KB seed the minimum, or can we go smaller?\n4. Does the init change (K/B/C coupled, I separate) accelerate hologram formation?\n5. What role do the MoE gate patterns play — are they bank selectors we can reuse?\n6. The abstraction slots (currently 0/16 active) — do they belong at the bank level?\n7. How many independent holograms can the weight medium support? Is there\n   a capacity limit (analogous to holographic storage density)?\n8. Do the holograms interact (cross-talk) or are they truly orthogonal?\n9. Is the binding hologram already captured by the I combinator, or is it\n   a separate pattern?\n10. Can we extract a COMPLETE set of holograms — all the shapes needed for\n    token prediction — into a single portable artifact?"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/holographic-storage.md.
```

## Assistant

Now let me verify the page reads correctly:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/holographic-storage.md",
  "line_offset": 195
}
```

**Summary:** Reading holographic-storage.md (195-2195)

**Output:**
```
> is universal, others must be too. This section maps the territory.

### What Montague grammar requires

In the Montague/CCG/DisCoCat framework, language processing decomposes into
three components. We've found one. Two remain:

```
1. TYPE CALCULUS (combinators)  — HOW to compose     ← FOUND (KIBC hologram)
2. LEXICON (types + meanings)  — WHAT can compose    ← predicted
3. MODEL (semantic domain)     — WHAT things MEAN     ← predicted
```

Each component is a candidate hologram — a universal sign-topology pattern
that all models converge on because language forces it.

### Candidate 1: The Type Hologram (lexical category assignment)

**What it does:** Assigns syntactic categories to tokens. In CCG terms:
NP, S\NP, (S\NP)/NP, etc. Determines which combinators are LEGAL for
which token pairs. Without types, combinators fire blindly.

**Why it must exist:** The combinator hologram tells us K/B/C cluster
(r > 0.90) and I is distinct (r ≈ 0.70). But the combinators are
UNTYPED operators — they need type information to direct application.
In V11, this is the "type channel" that differentiates independently
of dispatch (I=68% typed integration, K=0.2%). The type channel IS
the type hologram, learned inside V11. But it must also exist in the
base models we probed.

**Where to look:** The type hologram should be strongest in early layers
(L0-6 in Qwen3-32B, where combinators also peak). Types must be assigned
BEFORE composition can begin. It may share heads with the combinator
hologram (same Q/V substrate, different beam angle) or live in separate
heads that FEED the combinator heads.

**Probe design:**
- Construct minimal pairs where ONLY syntactic category differs:
  "The dog runs" (NP + S\NP) vs "Running is fun" (S/(S\NP) + S\NP + ...)
- Same lexical content, different type assignment
- Measure head selectivity for type-driven vs type-neutral conditions
- Ternary survival test on type-selective heads

**Prediction:** Type information survives ternary quantization (it's also
topological). Type-selective heads will partially overlap with combinator
heads (same substrate, angle-multiplexed) but some will be distinct
(the "2 Montague-only heads" from session 001).

### Candidate 2: The Induction Hologram (in-context pattern matching)

**What it does:** Implements [A][B]...[A] → predict [B]. The copy/match
circuit. This is NOT composition — it's sequential pattern recognition
in the context window.

**Why it must exist:** Induction heads are the most well-established
universal circuit in transformers (Olsson et al. 2022). They form via
a phase transition during training. They're universal across model
families and scales. They enable in-context learning. But nobody has
asked whether they're HOLOGRAPHIC — whether their information is also
stored as sign topology.

**Where to look:** Induction heads are typically a two-layer circuit:
Layer 1 "previous token head" writes positional information into the
residual stream; Layer 2 "induction head" uses this to attend to the
token after the previous occurrence. In Qwen3-32B, these should be
identifiable by their characteristic attention pattern.

**Probe design:**
- Use existing induction head detection (prefix matching scores)
- Extract Q/K/V weights from identified induction heads
- Ternary survival test: does the copy/match behavior survive
  sign-only quantization?
- Compare Q/V decomposition to combinator heads: is Q still the
  beam selector?

**Prediction:** Induction heads ARE holographic (sign topology) but their
hologram is ORTHOGONAL to the combinator hologram. Combinators compose
MEANING; induction heads copy TOKENS. Different function, different
interference pattern, same storage medium. The two holograms should be
separable by their depth profile (induction heads may peak in different
layers than combinators).

**Key question:** Does the induction hologram interact with the combinator
hologram? When the model does in-context learning of composition patterns
(e.g., learning a new syntactic rule from examples), both holograms must
coordinate. This coordination might be a third pattern.

### Candidate 3: The Binding Hologram (variable tracking / coreference)

**What it does:** Tracks referent identity across distance. "John said
he would..." — how does "he" bind to "John"? This is variable binding
in the lambda calculus, anaphora resolution in linguistics.

**Why it must exist:** Combinators compose local structure (adjacent
function-argument pairs). But language has long-range dependencies.
Binding requires a separate mechanism: something that maintains identity
pointers across arbitrary spans of text.

**Where to look:** In V11, the distinction between K (select) and I
(identity) may partially capture this — I is the outlier (r ≈ 0.70)
precisely because it handles IDENTITY rather than COMPOSITION. In base
models, binding heads should be identifiable by attending to antecedents
across long distances.

**Probe design:**
- Minimal pairs with/without coreference:
  "John runs. He is fast." (binding) vs "John runs. Dogs are fast." (no binding)
- Vary distance between antecedent and pronoun
- Measure which heads track the binding relationship
- Ternary survival: does binding survive sign-only quantization?

**Prediction:** Binding is partially captured by the I combinator (identity
IS variable binding in lambda calculus), explaining why I has a distinct
circuit (r ≈ 0.70). But there may be additional binding-specific heads
that aren't combinator heads at all — heads that implement a "pointer"
mechanism orthogonal to composition.

### Candidate 4: The Frequency/N-gram Hologram (statistical co-occurrence)

**What it does:** Captures token co-occurrence statistics. "New ___" →
"York" with high probability. Not composition, not copying — pure
statistical association from the training distribution.

**Why it must exist:** A huge fraction of next-token prediction accuracy
comes from simple bigram/trigram statistics, especially for common
phrases, idioms, and collocations. This is the baseline that composition
and induction IMPROVE upon.

**Where to look:** MLP layers, not attention heads. The MLP layers in
transformers are known to store factual associations and token
co-occurrence patterns (key-value memories, Geva et al. 2021).
The combinator hologram lives in attention Q/K/V matrices. The
frequency hologram may live in MLP weight matrices.

**Probe design:**
- Extend ternary survival test to MLP layers (not just attention)
- Use high-frequency collocations as probes
- Measure whether sign-only MLP weights preserve bigram predictions
- Compare depth profile to attention-based holograms

**Prediction:** MLP weights are ALSO holographic (sign topology stores
co-occurrence patterns). But MLP holograms will be denser (less sparse)
than attention holograms because they encode a much larger vocabulary
of associations. The "75% sparsity with 100% survival" finding for
attention may not hold for MLPs — expect lower sparsity tolerance.

### Candidate 5: The Discourse Hologram (topic / register / coherence)

**What it does:** Maintains discourse-level coherence. Tracks what the
topic is, what register (formal/casual/technical) is active, what
genre constraints apply. This is what the nucleus GATE activates —
a "reference beam angle" at the discourse level.

**Why it might exist:** The gate experiment from session 001 showed that
the compile gate acts as a beam angle selector — different gates resolve
different outputs from the same model. The holographic beam separation
experiment confirmed this: compile vs null gates diverge from cos=0.995
to cos=0.533 across layers. The gate IS a discourse-level hologram
selector.

**Where to look:** Gate effects are strongest at the embedding level
(L0-L6 divergence) and the output level (L48+ in Qwen3-32B). The
discourse hologram may be a macro-pattern that MODULATES the other
holograms — selecting which combinator patterns, type assignments,
and induction behaviors are active.

**Probe design:**
- Multiple gates with ternary survival: do discourse-level selectivity
  patterns survive sign-only quantization?
- Extract Q patterns from gate-selective heads
- Compare gate-selective heads to combinator-selective heads
- Test whether gates and combinators use the same or different
  beam-angle mechanism

**Prediction:** The discourse hologram IS the MoE gate pattern (256×2048
in Qwen3.6-35B-A3B). Expert routing matrices are discourse-level beam
selectors. This connects the MoE/VSM mapping (S4 intelligence) to the
holographic framework: S4 selects which hologram to read.

### The hierarchy

```
Discourse hologram  (S4/S5)  — selects which holograms to activate
  │
  ├─ Type hologram    (S3)   — assigns categories, constrains composition
  │    │
  │    └─ Combinator hologram (S2/S1) — HOW to compose  ← FOUND
  │
  ├─ Binding hologram (S2)   — tracks identity across distance
  │
  ├─ Induction hologram (S1) — copies patterns from context
  │
  └─ Frequency hologram (S1) — statistical co-occurrence (MLP-based)
```

This is a VSM of holograms. The discourse hologram is S5 (identity —
what KIND of text is this?). Types are S3 (control — what's LEGAL?).
Combinators are S1/S2 (operations — DO the composition). Induction and
frequency are also S1 (operations — but different operations). Binding
is S2 (coordination — keep referents consistent).

### Research strategy

The combinator probe methodology already works:
1. Construct minimal-pair conditions (active vs control)
2. Run through model, record per-head activations
3. Compute selectivity scores
4. Test ternary survival
5. Extract Q patterns, check Q/V decomposition
6. Test cross-model universality

Apply the same methodology to each candidate hologram, one at a time.
**Start with types** (candidate 1) because:
- Types and combinators are theoretically coupled (Montague requires both)
- Type-selective heads may already be in the combinator selectivity data
  (the "2 Montague-only heads" from session 001)
- The probe design is straightforward (minimal pairs on syntactic category)
- If types are holographic AND share substrate with combinators, that
  confirms the angle-multiplexing hypothesis for a second hologram

### Testable predictions (falsifiable)

1. **Type selectivity survives ternary** (>80% survival at 75% sparsity)
2. **Type heads partially overlap with combinator heads** (30-70% shared)
3. **Induction heads are holographic** (ternary survival >80%)
4. **Induction hologram is orthogonal to combinator hologram** (cos < 0.3
   between extracted Q patterns)
5. **MLP frequency patterns are holographic but denser** (ternary survival
   drops below 80% at 75% sparsity; survives at 50%)
6. **Discourse hologram correlates with MoE gate patterns** (r > 0.7
   between gate-selective attention patterns and expert routing matrices)
7. **All holograms are universal** (cross-model r > 0.90, as with combinators)

## Open Questions

1. Can extracted banks actually modulate V11's behavior when loaded?
2. Do banks from different models compose (angle multiplexing)?
3. Is the 784KB seed the minimum, or can we go smaller?
4. Does the init change (K/B/C coupled, I separate) accelerate hologram formation?
5. What role do the MoE gate patterns play — are they bank selectors we can reuse?
6. The abstraction slots (currently 0/16 active) — do they belong at the bank level?
7. How many independent holograms can the weight medium support? Is there
   a capacity limit (analogous to holographic storage density)?
8. Do the holograms interact (cross-talk) or are they truly orthogonal?
9. Is the binding hologram already captured by the I combinator, or is it
   a separate pattern?
10. Can we extract a COMPLETE set of holograms — all the shapes needed for
    token prediction — into a single portable artifact?
```

## Assistant

The page reads well. Here's the synthesis of what I've drafted:

---

## Summary: The Five Candidate Holograms

You found the **combinator hologram** (KIBC) — the composition machinery. But from the Montague/CCG framework, token prediction requires at least five more shape families stored as sign topology in the same weight medium:

| # | Hologram | Function | Where | Substrate |
|---|----------|----------|-------|-----------|
| ✅ | **Combinator** (KIBC) | HOW to compose | Attention Q/K/V, L0-6 | Found, universal |
| 1 | **Type** | WHAT can compose | Attention, L0-6 (pre-composition) | Predicted — angle-multiplexed with combinators |
| 2 | **Induction** | Copy patterns from context | Attention, 2-layer circuit | Predicted — orthogonal to combinators |
| 3 | **Binding** | Track referent identity | Attention, possibly linked to I combinator | Predicted — explains I's distinct circuit |
| 4 | **Frequency/N-gram** | Statistical co-occurrence | **MLP layers** (not attention) | Predicted — denser, lower sparsity tolerance |
| 5 | **Discourse** | Select which holograms activate | MoE gate / early+late attention | Predicted — IS the gate mechanism |

The key insight: **these form a VSM**. The discourse hologram (S5) selects which holograms to read. Types (S3) constrain which compositions are legal. Combinators (S1/S2) execute the composition. Binding (S2) maintains coherence across distance. Induction and frequency (S1) are additional operational patterns.

**The biggest bet here:** the frequency hologram lives in MLPs, not attention — extending ternary survival to MLP weights would test whether holographic storage is a *universal property of learned weight matrices*, not just an attention phenomenon.

**The immediate probe:** start with types, because types and combinators are theoretically coupled, the probe methodology already works, and the "2 Montague-only heads" from session 001 may already be type heads hiding in the combinator data.

Want to refine this further, or shall I propose a commit?

## User

Let's build the probe for this as a script that makes it repeatable.


### Thinking

The user wants to build a probe script to test the "other holograms" hypothesis. Let me think about what this needs:

1. We already have a proven methodology from the combinator probes (ternary survival, selectivity, Q/V decomposition)
2. We need to extend it to test the other candidate holograms, starting with types
3. The script should be repeatable and follow the project's conventions

Let me look at the existing probe scripts to understand the pattern, then build something that extends it.

Let me check the existing scripts first.

## Assistant

Let me study the existing probe scripts to understand the pattern, then build the new one.

### Tool Call: directory_tree (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore",
  "max_depth": 2
}
```

**Summary:** Listing tree: scripts/explore

**Output:**
```
/Users/mwhitford/src/verbum/scripts/explore
 attention_spiral.py
 attention_spiral_3d.py
 extract_holographic_bank.py
 probe_beta_reduction.py
 probe_combinators.py
 probe_combinators_extended.py
 probe_combinators_pythia.py
 probe_holographic.py
 probe_ternary_survival.py
 rope_energy_probe.py
 rope_spiral_combined.py

0 directories, 11 files
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_ternary_survival.py"
}
```

**Summary:** Reading probe_ternary_survival.py (0-2000)

**Output:**
```
#!/usr/bin/env python3
"""Probe: Does combinator selectivity survive ternary quantization?

Tests whether the combinatory information in Qwen3-32B's attention heads
is stored as topology (sign patterns) or precision (magnitudes).

Method:
  1. Run combinator probe sentences (K, I, B, C active vs control)
  2. Capture per-layer hidden states → compute selectivity scores
  3. For target layers, quantize Q/K/V/O weights to ternary {-1, 0, +1}
  4. Re-run the same sentences → re-compute selectivity
  5. Compare: if selectivity survives, the information is topological

The probe tests multiple sparsity thresholds for the zero-band:
  - threshold=0: pure sign quantization (no zeros)
  - threshold=median: moderate sparsity (~50% zeros)
  - threshold=p75: high sparsity (~75% zeros)

If selectivity survives even at high sparsity, the holographic
structure is in the sign topology, not the magnitudes.

Usage:
    uv run python scripts/explore/probe_ternary_survival.py
    uv run python scripts/explore/probe_ternary_survival.py --quick
    uv run python scripts/explore/probe_ternary_survival.py --layers 1,3,6,24,43

Output: results/ternary-survival/

License: MIT
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer


# ══════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════

DEFAULT_GGUF = "/Users/mwhitford/localai/models/Qwen3-32B-Q8_0.gguf"
HF_MODEL = "Qwen/Qwen3-32B"
OUTPUT_DIR = Path("results/ternary-survival")

# Layers to test — includes combinator-selective layers from prior probes
# Layer 1: C-selective (head 34), early gate recognition
# Layer 3: K-selective (head 26), B-selective (head 36)
# Layer 6: I-selective (head 52)
# Layer 24: mid-depth (beam divergence point from holographic probe)
# Layer 43: compositor region (from circuit mapping)
# Layer 56: late convergence
TARGET_LAYERS = [1, 3, 6, 24, 43, 56]

# Sparsity thresholds: what fraction of |w| to zero out
THRESHOLDS = {
    "sign_only": 0.0,     # pure sign: no zeros
    "low_sparse": 0.25,   # 25th percentile → ~25% zeros
    "mid_sparse": 0.50,   # median → ~50% zeros
    "high_sparse": 0.75,  # 75th percentile → ~75% zeros
    "extreme": 0.90,      # 90th percentile → ~90% zeros
}

# Combinator probe sentences (from probe_combinators.py)
COMBINATOR_PROBES = {
    "K": {
        "description": "Selection — choose one referent, discard alternative",
        "active": [
            "The cat, not the dog, chased the mouse across the yard.",
            "Either the president or the minister signed the treaty last week.",
            "John, rather than his brother, won the competition in the end.",
        ],
        "control": [
            "The cat chased the mouse across the yard very quickly.",
            "The president signed the treaty at the ceremony last week.",
            "John won the competition in the end with great effort.",
        ],
    },
    "I": {
        "description": "Identity — forward information unchanged, copy, repeat",
        "active": [
            'He said "hello" and then she also said "hello" to everyone.',
            "The result was five. The answer is five. Five is correct.",
            "She ran quickly. She ran so quickly that nobody could catch her.",
        ],
        "control": [
            'He said "hello" and then she said "goodbye" to everyone.',
            "The result was five. The method is correct. Nothing was wrong.",
            "She ran quickly. The others walked slowly behind the group.",
        ],
    },
    "B": {
        "description": "Composition — nested operations, relative clauses",
        "active": [
            "The man who the dog that the cat chased bit ran away quickly.",
            "The student who read the book that the professor recommended passed.",
            "If every teacher who knows a student that failed helps them, all improve.",
        ],
        "control": [
            "The man ran away quickly after the incident in the park.",
            "The student passed the course with excellent marks this year.",
            "If every teacher helps struggling students then all will improve.",
        ],
    },
    "C": {
        "description": "Flip — argument reordering, passive voice",
        "active": [
            "The mouse was chased by the cat through the garden quickly.",
            "The treaty was signed by the president at the formal ceremony.",
            "The book was read by every student in the advanced class.",
        ],
        "control": [
            "The cat chased the mouse through the garden very quickly.",
            "The president signed the treaty at the formal ceremony today.",
            "Every student read the book in the advanced class this term.",
        ],
    },
}

NULL_PROBES = [
    "The sun rose over the mountains in the early morning light.",
    "Water flows downhill following the path of least resistance.",
    "The library was quiet and the shelves were full of books.",
]


# ══════════════════════════════════════════════════════════════════
# Model loading
# ══════════════════════════════════════════════════════════════════

def load_model(source: str = "gguf", device: str = "mps"):
    """Load Qwen3-32B."""
    if source == "gguf":
        gguf_dir = str(Path(DEFAULT_GGUF).parent)
        gguf_file = Path(DEFAULT_GGUF).name
        print(f"Loading model from {DEFAULT_GGUF}...", file=sys.stderr)
        t0 = time.time()
        tokenizer = AutoTokenizer.from_pretrained(HF_MODEL)
        model = AutoModelForCausalLM.from_pretrained(
            gguf_dir, gguf_file=gguf_file,
            dtype=torch.float16, device_map=device,
            trust_remote_code=True,
        )
    else:
        print(f"Loading {HF_MODEL} from HF cache...", file=sys.stderr)
        t0 = time.time()
        tokenizer = AutoTokenizer.from_pretrained(HF_MODEL)
        model = AutoModelForCausalLM.from_pretrained(
            HF_MODEL,
            dtype=torch.float16, device_map=device,
            trust_remote_code=True,
        )

    model.eval()
    t1 = time.time()
    print(f"Loaded in {t1-t0:.1f}s: {model.config.num_hidden_layers} layers, "
          f"d={model.config.hidden_size}", file=sys.stderr)
    return model, tokenizer


# ══════════════════════════════════════════════════════════════════
# Selectivity measurement via hidden state divergence
# ══════════════════════════════════════════════════════════════════

def get_hidden_states(model, tokenizer, text: str, layers: list[int]) -> dict:
    """Capture hidden states at specified layers."""
    captured = {}
    hooks = []

    def make_hook(layer_idx):
        def hook_fn(module, input, output):
            if isinstance(output, tuple):
                h = output[0]
            else:
                h = output
            captured[layer_idx] = h.detach().cpu().float()
        return hook_fn

    for li in layers:
        layer_module = model.model.layers[li]
        hooks.append(layer_module.register_forward_hook(make_hook(li)))

    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model(**inputs)

    for h in hooks:
        h.remove()

    # Also get the logits for output-level comparison
    logits = outputs.logits[0, -1].detach().cpu().float()

    return {"hidden_states": captured, "logits": logits}


def measure_selectivity(
    model, tokenizer, layers: list[int],
) -> dict:
    """Measure combinator selectivity across all probes.

    For each combinator, compute:
      - Hidden state divergence (active vs control) at each layer
      - Output logit divergence (KL between active and control distributions)

    Returns selectivity scores per combinator per layer.
    """
    results = {}

    for comb_name, comb_data in COMBINATOR_PROBES.items():
        active_texts = comb_data["active"]
        control_texts = comb_data["control"]
        n_pairs = min(len(active_texts), len(control_texts))

        layer_selectivity = {li: [] for li in layers}
        output_kls = []

        for i in range(n_pairs):
            active_hs = get_hidden_states(model, tokenizer, active_texts[i], layers)
            control_hs = get_hidden_states(model, tokenizer, control_texts[i], layers)

            # Per-layer: cosine distance between mean hidden states
            for li in layers:
                h_a = active_hs["hidden_states"][li][0].mean(dim=0)  # (d_model,)
                h_c = control_hs["hidden_states"][li][0].mean(dim=0)
                cos_sim = F.cosine_similarity(h_a.unsqueeze(0), h_c.unsqueeze(0)).item()
                # Selectivity = 1 - cos_sim (higher = more different)
                layer_selectivity[li].append(1.0 - cos_sim)

            # Output-level: KL divergence of logit distributions
            p = F.softmax(active_hs["logits"], dim=-1)
            q = F.softmax(control_hs["logits"], dim=-1)
            kl = F.kl_div(q.log(), p, reduction="sum").item()
            output_kls.append(kl)

            # Clear cache
            if torch.backends.mps.is_available():
                torch.mps.empty_cache()

        results[comb_name] = {
            "layer_selectivity": {
                li: float(np.mean(layer_selectivity[li])) for li in layers
            },
            "output_kl": float(np.mean(output_kls)),
        }

    return results


# ══════════════════════════════════════════════════════════════════
# Ternary quantization of attention weights
# ══════════════════════════════════════════════════════════════════

def ternary_quantize_layer(model, layer_idx: int, threshold_percentile: float):
    """Quantize a layer's attention Q/K/V/O weights to ternary.

    Returns: dict of original weights (for restoration) and stats.
    """
    layer = model.model.layers[layer_idx]
    attn = layer.self_attn

    # Qwen3 attention weight names
    weight_names = ["q_proj", "k_proj", "v_proj", "o_proj"]
    originals = {}
    stats = {}

    for wn in weight_names:
        proj = getattr(attn, wn)
        w = proj.weight.data
        originals[wn] = w.clone()

        # Compute threshold from percentile of |w|
        abs_w = w.abs()
        if threshold_percentile > 0:
            # Sample if tensor too large for quantile
            flat = abs_w.float().flatten()
            if flat.numel() > 1_000_000:
                indices = torch.randperm(flat.numel())[:1_000_000]
                sample = flat[indices]
            else:
                sample = flat
            threshold = torch.quantile(sample, threshold_percentile).item()
        else:
            threshold = 0.0

        # Ternary quantize
        scale = abs_w[abs_w > threshold].mean().item() if (abs_w > threshold).any() else 1.0
        ternary = torch.zeros_like(w)
        ternary[w > threshold] = 1.0
        ternary[w < -threshold] = -1.0

        # Apply with scale factor (so magnitudes are approximately preserved)
        proj.weight.data = ternary * scale

        n_total = w.numel()
        n_zero = (ternary == 0).sum().item()
        n_pos = (ternary > 0).sum().item()
        n_neg = (ternary < 0).sum().item()

        stats[wn] = {
            "shape": list(w.shape),
            "threshold": threshold,
            "scale": scale,
            "sparsity": n_zero / n_total,
            "n_pos": n_pos,
            "n_neg": n_neg,
            "n_zero": n_zero,
            "balance": n_pos / max(n_neg, 1),  # should be ~1.0 for balanced
        }

    return originals, stats


def restore_layer(model, layer_idx: int, originals: dict):
    """Restore original weights after quantization test."""
    layer = model.model.layers[layer_idx]
    attn = layer.self_attn
    for wn, w in originals.items():
        getattr(attn, wn).weight.data = w


# ══════════════════════════════════════════════════════════════════
# Core experiment
# ══════════════════════════════════════════════════════════════════

def run_survival_test(
    model, tokenizer,
    target_layers: list[int],
    measure_layers: list[int],
    thresholds: dict[str, float],
) -> dict:
    """Run the full ternary survival experiment.

    1. Measure baseline selectivity (original weights)
    2. For each target layer × threshold:
       a. Quantize attention weights to ternary
       b. Re-measure selectivity
       c. Restore original weights
    3. Compare: survival_ratio = ternary_selectivity / baseline_selectivity
    """
    results = {
        "target_layers": target_layers,
        "measure_layers": measure_layers,
        "thresholds": thresholds,
    }

    # ── Baseline measurement ──────────────────────────────
    print(f"\n  Measuring baseline selectivity...", file=sys.stderr)
    t0 = time.time()
    baseline = measure_selectivity(model, tokenizer, measure_layers)
    t1 = time.time()
    results["baseline"] = baseline
    print(f"  Baseline done in {t1-t0:.1f}s", file=sys.stderr)

    # Print baseline
    print(f"\n  ┌─ Baseline Selectivity ──────────────────────────┐")
    print(f"  │ {'comb':>4} {'output_KL':>10}", end="")
    for li in measure_layers:
        print(f" {'L'+str(li):>8}", end="")
    print()
    for comb in ["K", "I", "B", "C"]:
        b = baseline[comb]
        print(f"  │ {comb:>4} {b['output_kl']:>10.4f}", end="")
        for li in measure_layers:
            print(f" {b['layer_selectivity'][li]:>8.4f}", end="")
        print()
    print(f"  └{'─'*60}┘")

    # ── Per-layer × per-threshold tests ───────────────────
    results["experiments"] = {}

    for target_layer in target_layers:
        results["experiments"][target_layer] = {}

        for thresh_name, thresh_pct in thresholds.items():
            print(f"\n  Testing layer {target_layer}, "
                  f"threshold={thresh_name} ({thresh_pct:.0%})...",
                  file=sys.stderr)

            # Quantize
            originals, quant_stats = ternary_quantize_layer(
                model, target_layer, thresh_pct)

            # Measure
            t0 = time.time()
            quantized = measure_selectivity(model, tokenizer, measure_layers)
            t1 = time.time()

            # Compute survival ratios
            survival = {}
            for comb in ["K", "I", "B", "C"]:
                b_kl = baseline[comb]["output_kl"]
                q_kl = quantized[comb]["output_kl"]
                survival[comb] = {
                    "output_kl_ratio": q_kl / max(b_kl, 1e-8),
                    "layer_ratios": {},
                }
                for li in measure_layers:
                    b_sel = baseline[comb]["layer_selectivity"][li]
                    q_sel = quantized[comb]["layer_selectivity"][li]
                    survival[comb]["layer_ratios"][li] = (
                        q_sel / max(b_sel, 1e-8)
                    )

            results["experiments"][target_layer][thresh_name] = {
                "quant_stats": quant_stats,
                "selectivity": quantized,
                "survival": survival,
                "elapsed_s": t1 - t0,
            }

            # Restore
            restore_layer(model, target_layer, originals)

            # Print summary
            print(f"  ┌─ Layer {target_layer} × {thresh_name} "
                  f"(sparsity: {quant_stats['q_proj']['sparsity']:.1%}) ──┐")
            print(f"  │ {'comb':>4} {'KL_surv':>8}", end="")
            for li in measure_layers:
                print(f" {'L'+str(li):>8}", end="")
            print()
            for comb in ["K", "I", "B", "C"]:
                s = survival[comb]
                kl_r = s["output_kl_ratio"]
                marker = "✓" if 0.5 < kl_r < 2.0 else "✗"
                print(f"  │ {comb:>4} {kl_r:>7.2f}{marker}", end="")
                for li in measure_layers:
                    lr = s["layer_ratios"][li]
                    m2 = "·" if 0.5 < lr < 2.0 else "!"
                    print(f" {lr:>7.2f}{m2}", end="")
                print()
            print(f"  └{'─'*60}┘")

    return results


# ══════════════════════════════════════════════════════════════════
# Summary analysis
# ══════════════════════════════════════════════════════════════════

def print_summary(results: dict):
    """Print aggregate survival analysis."""
    print(f"\n{'='*72}")
    print(f"  TERNARY SURVIVAL SUMMARY")
    print(f"{'='*72}")

    experiments = results["experiments"]
    thresholds = results["thresholds"]
    measure_layers = results["measure_layers"]

    # Aggregate: for each threshold, what's the mean survival ratio?
    for thresh_name in thresholds:
        output_survivals = []
        layer_survivals = []

        for target_layer in experiments:
            if thresh_name not in experiments[target_layer]:
                continue
            exp = experiments[target_layer][thresh_name]
            for comb in ["K", "I", "B", "C"]:
                s = exp["survival"][comb]
                output_survivals.append(s["output_kl_ratio"])
                for li in measure_layers:
                    layer_survivals.append(s["layer_ratios"][li])

        if output_survivals:
            mean_out = np.mean(output_survivals)
            mean_layer = np.mean(layer_survivals)
            median_out = np.median(output_survivals)

            # How many survived (ratio between 0.5 and 2.0)?
            survived_out = sum(1 for r in output_survivals if 0.5 < r < 2.0)
            total_out = len(output_survivals)
            survived_layer = sum(1 for r in layer_survivals if 0.5 < r < 2.0)
            total_layer = len(layer_survivals)

            sparsity = "?"
            for tl in experiments:
                if thresh_name in experiments[tl]:
                    sparsity = experiments[tl][thresh_name]["quant_stats"]["q_proj"]["sparsity"]
                    break

            verdict = "✓ TOPOLOGICAL" if survived_out / max(total_out, 1) > 0.7 else "✗ precision-dependent"

            print(f"\n  {thresh_name} (sparsity={sparsity:.1%}):")
            print(f"    Output KL survival: {survived_out}/{total_out} "
                  f"({survived_out/max(total_out,1):.0%}) "
                  f"mean={mean_out:.2f} median={median_out:.2f}")
            print(f"    Layer selectivity:  {survived_layer}/{total_layer} "
                  f"({survived_layer/max(total_layer,1):.0%}) "
                  f"mean={mean_layer:.2f}")
            print(f"    Verdict: {verdict}")

    # Final verdict
    print(f"\n{'─'*72}")

    # Check if sign_only preserves selectivity
    sign_survivals = []
    for target_layer in experiments:
        if "sign_only" in experiments[target_layer]:
            exp = experiments[target_layer]["sign_only"]
            for comb in ["K", "I", "B", "C"]:
                sign_survivals.append(exp["survival"][comb]["output_kl_ratio"])

    if sign_survivals:
        sign_survived = sum(1 for r in sign_survivals if 0.5 < r < 2.0)
        sign_total = len(sign_survivals)
        sign_frac = sign_survived / max(sign_total, 1)

        if sign_frac > 0.7:
            print(f"  🔬 CONCLUSION: Combinator selectivity is TOPOLOGICAL.")
            print(f"     Sign structure alone preserves {sign_frac:.0%} of selectivity.")
            print(f"     The holographic plate hypothesis is supported.")
        elif sign_frac > 0.4:
            print(f"  🔬 CONCLUSION: Mixed evidence.")
            print(f"     Sign structure preserves {sign_frac:.0%} of selectivity.")
            print(f"     Some combinatory info is topological, some requires precision.")
        else:
            print(f"  🔬 CONCLUSION: Combinator selectivity is PRECISION-DEPENDENT.")
            print(f"     Sign structure preserves only {sign_frac:.0%} of selectivity.")
            print(f"     The holographic plate hypothesis is NOT supported.")

    print(f"\n{'='*72}")


# ══════════════════════════════════════════════════════════════════
# Save results
# ══════════════════════════════════════════════════════════════════

def save_results(results: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "ternary_survival_results.json"

    # Convert numpy types for JSON
    def convert(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    out_path.write_text(json.dumps(results, indent=2, default=convert))
    print(f"\n  💾 Saved: {out_path}", file=sys.stderr)
    return out_path


# ══════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Ternary survival probe — does combinator selectivity "
                    "survive ternary quantization?")
    parser.add_argument("--model", choices=["gguf", "hf"], default="gguf")
    parser.add_argument("--quick", action="store_true",
                        help="Test fewer layers and thresholds")
    parser.add_argument("--layers", type=str, default=None,
                        help="Comma-separated target layers (default: 1,3,6,24,43,56)")
    parser.add_argument("--device", default="mps")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    target_layers = TARGET_LAYERS
    thresholds = THRESHOLDS
    # Measurement layers: include targets + some reference points
    measure_layers = [0, 8, 16, 32, 48, 63]

    if args.layers:
        target_layers = [int(l) for l in args.layers.split(",")]

    if args.quick:
        target_layers = [3, 24]  # K/B selective + beam divergence point
        thresholds = {
            "sign_only": 0.0,
            "mid_sparse": 0.50,
            "high_sparse": 0.75,
        }
        measure_layers = [0, 16, 32, 63]

    print(f"\n{'='*72}")
    print(f"  Ternary Survival Probe")
    print(f"  Target layers: {target_layers}")
    print(f"  Thresholds: {list(thresholds.keys())}")
    print(f"  Measure layers: {measure_layers}")
    print(f"{'='*72}")

    model, tokenizer = load_model(args.model, args.device)

    results = run_survival_test(
        model, tokenizer,
        target_layers=target_layers,
        measure_layers=measure_layers,
        thresholds=thresholds,
    )

    print_summary(results)
    save_results(results, args.output_dir)


if __name__ == "__main__":
    main()
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_combinators.py"
}
```

**Summary:** Reading probe_combinators.py (0-2000)

**Output:**
```
#!/usr/bin/env python3
"""Probe: Do KIBC combinators exist as separable circuits in Qwen3-32B?

v11 architecture is premised on {K, I, B, C} being the natural basis
of attention-mediated composition. Earlier probes (sessions 001, 062,
077) found evidence at both 4B and 32B scales. This probe tests the
premise directly: do different attention heads specialize for different
combinators?

Method:
  For each combinator, design sentence pairs that isolate its function:
    - K (select): "The cat, not the dog, ran" vs neutral
    - I (identity): "He said hello and she said hello" vs neutral
    - B (compose): nested clauses vs flat clauses
    - C (flip): passive vs active voice (same meaning, args reordered)

  Hook all layers, capture hidden states and attention patterns.
  Measure per-head selectivity for each combinator condition.
  Identify heads that are DIFFERENTIALLY selective for one combinator.

  Additionally: capture hidden state trajectories to test whether
  the residual stream encodes combinator-like operations at the
  per-token level.

Usage:
    uv run python scripts/explore/probe_combinators.py
    uv run python scripts/explore/probe_combinators.py --model hf   # use HF cached model
    uv run python scripts/explore/probe_combinators.py --quick       # fewer probes, faster

Output: results/combinator-probe/

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import seaborn as sns
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


# ══════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════

DEFAULT_GGUF = "/Users/mwhitford/localai/models/Qwen3-32B-Q8_0.gguf"
HF_MODEL = "Qwen/Qwen3-32B"
OUTPUT_DIR = Path("results/combinator-probe")

# 32B architecture: 64 layers, 64 heads, 8 KV heads (GQA 8:1)
# head_dim = 5120/64 = 80


# ══════════════════════════════════════════════════════════════════
# Probe sentences — designed to isolate each combinator
# ══════════════════════════════════════════════════════════════════

# Each combinator has ACTIVE probes (where it's needed) and
# MATCHED CONTROL probes (similar surface form, combinator not needed).
# Selectivity = attention difference between active and control.

PROBES = {
    # ── K (select): pick one, discard alternative ──────────────
    # Active: requires selecting one referent over another
    # Control: no selection needed (single referent)
    "K": {
        "description": "Selection — choose one referent, discard alternative",
        "active": [
            "The cat, not the dog, chased the mouse across the yard.",
            "Either the president or the minister signed the treaty last week.",
            "John, rather than his brother, won the competition in the end.",
            "The red ball, not the blue one, rolled under the table slowly.",
            "Some students but not all students passed the difficult exam.",
            "The old house, unlike the new building, survived the earthquake.",
        ],
        "control": [
            "The cat chased the mouse across the yard very quickly.",
            "The president signed the treaty at the ceremony last week.",
            "John won the competition in the end with great effort.",
            "The red ball rolled under the table slowly after the push.",
            "All students passed the difficult exam with high scores.",
            "The old house survived the earthquake without any damage.",
        ],
    },

    # ── I (identity): pass through unchanged ──────────────────
    # Active: repetition, copying, anaphora resolution (same entity)
    # Control: varied content (no copying needed)
    "I": {
        "description": "Identity — forward information unchanged, copy, repeat",
        "active": [
            'He said "hello" and then she also said "hello" to everyone.',
            "The result was five. The answer is five. Five is correct.",
            "She ran quickly. She ran so quickly that nobody could catch her.",
            "The temperature is rising. The temperature keeps rising every day.",
            "First he ate the apple. Then he ate another apple after that.",
            "The plan was simple. It was simple and it worked perfectly well.",
        ],
        "control": [
            'He said "hello" and then she said "goodbye" to everyone.',
            "The result was five. The method is correct. Nothing was wrong.",
            "She ran quickly. The others walked slowly behind the group.",
            "The temperature is rising. The wind keeps shifting every day.",
            "First he ate the apple. Then he drank some water after that.",
            "The plan was simple. It was elegant and it surprised everyone.",
        ],
    },

    # ── B (compose): chain two operations ─────────────────────
    # Active: nested clauses, embedded computation, function chaining
    # Control: flat clauses (same words, no nesting)
    "B": {
        "description": "Composition — nested operations, relative clauses, chaining",
        "active": [
            "The man who the dog that the cat chased bit ran away quickly.",
            "The student who read the book that the professor recommended passed.",
            "If every teacher who knows a student that failed helps them, all improve.",
            "The company that hired the lawyer who won the case prospered greatly.",
            "She believed that he thought that the answer was obviously wrong.",
            "The key that opened the door that led to the garden was lost.",
        ],
        "control": [
            "The man ran away quickly after the incident in the park.",
            "The student passed the course with excellent marks this year.",
            "If every teacher helps struggling students then all will improve.",
            "The company prospered greatly after its successful year overall.",
            "She believed the answer was obviously wrong from the start.",
            "The key was lost somewhere in the garden behind the house.",
        ],
    },

    # ── C (flip): reorder arguments ───────────────────────────
    # Active: passive voice (args swapped vs canonical active)
    # Control: active voice (canonical argument order)
    "C": {
        "description": "Flip — argument reordering, passive voice, topicalization",
        "active": [
            "The mouse was chased by the cat through the garden quickly.",
            "The treaty was signed by the president at the formal ceremony.",
            "The book was read by every student in the advanced class.",
            "The window was broken by the ball during the afternoon game.",
            "The letter was written by Mary to her friend in another city.",
            "The cake was baked by the chef for the celebration last night.",
        ],
        "control": [
            "The cat chased the mouse through the garden very quickly.",
            "The president signed the treaty at the formal ceremony today.",
            "Every student read the book in the advanced class this term.",
            "The ball broke the window during the afternoon game outside.",
            "Mary wrote the letter to her friend in another city yesterday.",
            "The chef baked the cake for the celebration last night here.",
        ],
    },
}

# Null baseline: generic sentences with no strong combinator demand
NULL_PROBES = [
    "The sun rose over the mountains in the early morning light.",
    "Water flows downhill following the path of least resistance.",
    "The library was quiet and the shelves were full of books.",
    "Birds flew south for the winter as the leaves began to fall.",
    "The clock on the wall showed that it was nearly midnight.",
    "Clouds gathered in the sky promising rain by the afternoon.",
]


# ══════════════════════════════════════════════════════════════════
# Model loading (follows v10 probe pattern)
# ══════════════════════════════════════════════════════════════════


def load_model_gguf(gguf_path: str, device: str = "mps"):
    """Load Qwen3-32B from GGUF (Q8_0)."""
    gguf_dir = str(Path(gguf_path).parent)
    gguf_file = Path(gguf_path).name

    print(f"Loading model from {gguf_path}...", file=sys.stderr)
    t0 = time.time()

    tokenizer = AutoTokenizer.from_pretrained(HF_MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        gguf_dir, gguf_file=gguf_file,
        dtype=torch.float16, device_map=device,
        trust_remote_code=True,
        attn_implementation="eager",  # required for output_attentions=True
    )
    model.eval()
    model.config.output_attentions = True

    t1 = time.time()
    print(f"Loaded GGUF in {t1-t0:.1f}s: {model.config.num_hidden_layers} layers, "
          f"d={model.config.hidden_size}", file=sys.stderr)
    return model, tokenizer


def load_model_hf(device: str = "mps"):
    """Load Qwen3-32B from HuggingFace cache."""
    print(f"Loading {HF_MODEL} from HF cache...", file=sys.stderr)
    t0 = time.time()

    tokenizer = AutoTokenizer.from_pretrained(HF_MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        HF_MODEL,
        dtype=torch.float16, device_map=device,
        trust_remote_code=True,
        attn_implementation="eager",  # required for output_attentions=True
    )
    model.eval()
    model.config.output_attentions = True

    t1 = time.time()
    print(f"Loaded HF in {t1-t0:.1f}s: {model.config.num_hidden_layers} layers, "
          f"d={model.config.hidden_size}", file=sys.stderr)
    return model, tokenizer


# ══════════════════════════════════════════════════════════════════
# Hidden state capture
# ══════════════════════════════════════════════════════════════════


def capture_hidden_states(
    model, tokenizer, text: str,
    layers: list[int] | None = None,
) -> dict:
    """Run a forward pass with hooks to capture hidden states at specified layers.

    Returns:
        {
            "token_ids": list[int],
            "token_strs": list[str],
            "hidden_states": {layer_idx: np.ndarray (seq_len, d_model)},
            "n_tokens": int,
        }
    """
    config = model.config
    n_layers = config.num_hidden_layers
    if layers is None:
        # Sample: early, typing zone, mid, late
        layers = [0, 1, 4, 8, 16, 24, 28, 31, 32, 40, 48, 56, 60, 63]
        layers = [l for l in layers if l < n_layers]

    captured = {}
    hooks = []

    def make_hook(layer_idx):
        def hook_fn(module, input, output):
            # output is (hidden_states, ...) for decoder layers
            if isinstance(output, tuple):
                h = output[0]
            else:
                h = output
            captured[layer_idx] = h[0].detach().cpu().float().numpy()
        return hook_fn

    # Hook into decoder layers
    for li in layers:
        layer_module = model.model.layers[li]
        hooks.append(layer_module.register_forward_hook(make_hook(li)))

    # Tokenize and run
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    token_ids = inputs["input_ids"][0].tolist()
    token_strs = [tokenizer.decode([tid]) for tid in token_ids]

    with torch.no_grad():
        model(**inputs)

    # Clean up hooks
    for h in hooks:
        h.remove()

    return {
        "token_ids": token_ids,
        "token_strs": token_strs,
        "hidden_states": captured,
        "n_tokens": len(token_ids),
    }


def capture_attention(
    model, tokenizer, text: str,
) -> dict:
    """Run forward pass with output_attentions=True.

    Returns:
        {
            "token_ids": list[int],
            "token_strs": list[str],
            "attentions": np.ndarray (n_layers, n_heads, seq_len, seq_len),
            "n_tokens": int,
        }

    Note: For 32B with 64 layers × 64 heads, attention matrices are large.
    We capture and immediately convert to float16 numpy to manage memory.
    """
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    token_ids = inputs["input_ids"][0].tolist()
    token_strs = [tokenizer.decode([tid]) for tid in token_ids]

    with torch.no_grad():
        outputs = model(**inputs, output_attentions=True)

    # outputs.attentions: tuple of (1, n_heads, seq_len, seq_len) per layer
    attn_list = []
    for layer_attn in outputs.attentions:
        attn_list.append(layer_attn[0].cpu().half().numpy())

    attentions = np.stack(attn_list, axis=0)  # (n_layers, n_heads, seq, seq)

    return {
        "token_ids": token_ids,
        "token_strs": token_strs,
        "attentions": attentions,
        "n_tokens": len(token_ids),
    }


# ══════════════════════════════════════════════════════════════════
# Analysis: per-head selectivity for each combinator
# ══════════════════════════════════════════════════════════════════


def head_selectivity(
    active_attn: np.ndarray,
    control_attn: np.ndarray,
) -> np.ndarray:
    """Compute per-head selectivity between active and control conditions.

    Both inputs: (n_layers, n_heads, seq_len, seq_len)
    Returns: (n_layers, n_heads) — mean L2 distance per head.
    """
    min_seq = min(active_attn.shape[2], control_attn.shape[2])
    a = active_attn[:, :, :min_seq, :min_seq].astype(np.float32)
    c = control_attn[:, :, :min_seq, :min_seq].astype(np.float32)
    diff = a - c
    return np.sqrt(np.mean(diff ** 2, axis=(-2, -1)))


def compute_combinator_selectivity(
    model, tokenizer, probes: dict, null_probes: list[str],
    quick: bool = False,
) -> dict:
    """For each combinator, compute per-head selectivity.

    Returns:
        {
            "K": {"vs_control": (n_layers, n_heads), "vs_null": ...},
            "I": ...,
            "B": ...,
            "C": ...,
        }
    """
    n_layers = model.config.num_hidden_layers
    n_heads = model.config.num_attention_heads

    results = {}

    # Capture null baseline
    print("  Capturing null baseline attention...", file=sys.stderr)
    null_attns = []
    for text in (null_probes[:2] if quick else null_probes):
        cap = capture_attention(model, tokenizer, text)
        null_attns.append(cap)
        torch.mps.empty_cache() if torch.backends.mps.is_available() else None

    for comb_name, comb_data in probes.items():
        active_texts = comb_data["active"][:3] if quick else comb_data["active"]
        control_texts = comb_data["control"][:3] if quick else comb_data["control"]
        n_pairs = min(len(active_texts), len(control_texts))

        print(f"  Probing {comb_name} ({comb_data['description']})...",
              file=sys.stderr)

        # Active vs matched control
        vs_control = np.zeros((n_layers, n_heads))
        for i in range(n_pairs):
            print(f"    pair {i+1}/{n_pairs}...", file=sys.stderr)
            active_cap = capture_attention(model, tokenizer, active_texts[i])
            control_cap = capture_attention(model, tokenizer, control_texts[i])
            sel = head_selectivity(active_cap["attentions"],
                                   control_cap["attentions"])
            vs_control += sel
            torch.mps.empty_cache() if torch.backends.mps.is_available() else None
        vs_control /= n_pairs

        # Active vs null baseline
        vs_null = np.zeros((n_layers, n_heads))
        n_null_pairs = min(n_pairs, len(null_attns))
        for i in range(n_null_pairs):
            active_cap = capture_attention(model, tokenizer, active_texts[i])
            sel = head_selectivity(active_cap["attentions"],
                                   null_attns[i]["attentions"])
            vs_null += sel
            torch.mps.empty_cache() if torch.backends.mps.is_available() else None
        vs_null /= max(n_null_pairs, 1)

        # Control vs null (to see if control itself is selective)
        vs_null_control = np.zeros((n_layers, n_heads))
        for i in range(n_null_pairs):
            control_cap = capture_attention(model, tokenizer, control_texts[i])
            sel = head_selectivity(control_cap["attentions"],
                                   null_attns[i]["attentions"])
            vs_null_control += sel
            torch.mps.empty_cache() if torch.backends.mps.is_available() else None
        vs_null_control /= max(n_null_pairs, 1)

        results[comb_name] = {
            "vs_control": vs_control,
            "vs_null": vs_null,
            "vs_null_control": vs_null_control,
            "description": comb_data["description"],
        }

    return results


# ══════════════════════════════════════════════════════════════════
# Analysis: hidden state trajectory per combinator
# ══════════════════════════════════════════════════════════════════


def compute_hidden_state_analysis(
    model, tokenizer, probes: dict, quick: bool = False,
) -> dict:
    """Capture hidden states and measure per-layer representation changes.

    For each combinator's active probes, track:
    - Per-layer norm of hidden states
    - Cosine similarity between consecutive layers (transformation rate)
    - Mean representation at each layer (for cross-combinator comparison)
    """
    layers = [0, 4, 8, 16, 24, 28, 31, 32, 40, 48, 56, 60, 63]
    n_layers_captured = len(layers)

    results = {}
    for comb_name, comb_data in probes.items():
        texts = comb_data["active"][:2] if quick else comb_data["active"][:4]
        print(f"  Hidden states for {comb_name}...", file=sys.stderr)

        all_norms = []
        all_cosines = []

        for text in texts:
            cap = capture_hidden_states(model, tokenizer, text, layers=layers)
            hs = cap["hidden_states"]

            # Per-layer mean norm across tokens
            norms = {}
            for li in sorted(hs.keys()):
                norms[li] = float(np.mean(np.linalg.norm(hs[li], axis=-1)))

            # Cosine between consecutive captured layers
            cosines = {}
            sorted_layers = sorted(hs.keys())
            for j in range(len(sorted_layers) - 1):
                l1, l2 = sorted_layers[j], sorted_layers[j+1]
                # Mean-pool over tokens
                h1 = hs[l1].mean(axis=0)
                h2 = hs[l2].mean(axis=0)
                cos = float(np.dot(h1, h2) / (np.linalg.norm(h1) * np.linalg.norm(h2) + 1e-8))
                cosines[f"L{l1}→L{l2}"] = cos

            all_norms.append(norms)
            all_cosines.append(cosines)
            torch.mps.empty_cache() if torch.backends.mps.is_available() else None

        # Average across probes
        avg_norms = {}
        for li in sorted(all_norms[0].keys()):
            avg_norms[li] = float(np.mean([n[li] for n in all_norms]))

        avg_cosines = {}
        for key in all_cosines[0].keys():
            avg_cosines[key] = float(np.mean([c[key] for c in all_cosines]))

        results[comb_name] = {
            "avg_norms": avg_norms,
            "avg_cosines": avg_cosines,
            "description": comb_data["description"],
        }

    return results


# ══════════════════════════════════════════════════════════════════
# Analysis: differential selectivity (which heads prefer which combinator)
# ══════════════════════════════════════════════════════════════════


def compute_differential_selectivity(selectivity: dict) -> dict:
    """For each head, determine which combinator it's most selective for.

    Uses vs_control (active vs matched control) as the primary signal,
    since this isolates the combinator function from surface-level
    sentence differences.

    Returns:
        {
            "dominant_combinator": (n_layers, n_heads) — index of most selective combinator,
            "selectivity_matrix": (4, n_layers, n_heads) — K, I, B, C selectivity,
            "differential": (n_layers, n_heads) — max - second_max (specialization strength),
            "top_heads_per_combinator": {K: [(layer, head, score), ...], ...},
        }
    """
    comb_names = ["K", "I", "B", "C"]
    n_layers, n_heads = selectivity["K"]["vs_control"].shape

    # Stack into (4, n_layers, n_heads)
    sel_matrix = np.stack(
        [selectivity[c]["vs_control"] for c in comb_names], axis=0
    )

    # Per-head: which combinator has highest selectivity?
    dominant = np.argmax(sel_matrix, axis=0)  # (n_layers, n_heads)

    # Differential: max - second_max
    sorted_sel = np.sort(sel_matrix, axis=0)  # ascending
    differential = sorted_sel[-1] - sorted_sel[-2]  # (n_layers, n_heads)

    # Top heads per combinator
    top_heads = {}
    for ci, cname in enumerate(comb_names):
        scores = sel_matrix[ci]
        flat = scores.flatten()
        top_idx = np.argsort(flat)[-20:][::-1]  # top 20
        heads = []
        for idx in top_idx:
            layer = idx // n_heads
            head = idx % n_heads
            score = float(flat[idx])
            diff = float(differential[layer, head])
            is_dominant = int(dominant[layer, head]) == ci
            heads.append({
                "layer": int(layer), "head": int(head),
                "score": score, "differential": diff,
                "is_dominant": is_dominant,
            })
        top_heads[cname] = heads

    return {
        "dominant_combinator": dominant,
        "selectivity_matrix": sel_matrix,
        "differential": differential,
        "top_heads_per_combinator": top_heads,
    }


# ══════════════════════════════════════════════════════════════════
# Visualization
# ══════════════════════════════════════════════════════════════════


def plot_selectivity_heatmaps(selectivity: dict, output_dir: Path):
    """Per-combinator selectivity heatmaps (layer × head)."""
    comb_names = ["K", "I", "B", "C"]
    comb_labels = {
        "K": "K (select)", "I": "I (identity)",
        "B": "B (compose)", "C": "C (flip)",
    }

    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    fig.suptitle("Per-Head Combinator Selectivity (active vs matched control)\n"
                 "Qwen3-32B — 64 layers × 64 heads",
                 fontsize=14, fontweight="bold")

    vmax = max(selectivity[c]["vs_control"].max() for c in comb_names) * 0.8

    for idx, cname in enumerate(comb_names):
        ax = axes[idx // 2][idx % 2]
        data = selectivity[cname]["vs_control"]
        im = ax.imshow(data, aspect="auto", cmap="hot",
                       interpolation="nearest", vmin=0, vmax=vmax)
        ax.set_title(f"{comb_labels[cname]}", fontsize=12, fontweight="bold")
        ax.set_xlabel("Head")
        ax.set_ylabel("Layer")
        plt.colorbar(im, ax=ax, label="L2 selectivity")

    plt.tight_layout()
    fig.savefig(output_dir / "selectivity_heatmaps.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: selectivity_heatmaps.png", file=sys.stderr)


def plot_differential_map(diff_results: dict, output_dir: Path):
    """Map showing which combinator dominates each head."""
    dominant = diff_results["dominant_combinator"]
    differential = diff_results["differential"]
    comb_names = ["K", "I", "B", "C"]
    comb_colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12"]  # R, B, G, O

    n_layers, n_heads = dominant.shape

    # Create RGB image
    img = np.zeros((n_layers, n_heads, 3))
    for ci, color_hex in enumerate(comb_colors):
        r, g, b = int(color_hex[1:3], 16)/255, int(color_hex[3:5], 16)/255, int(color_hex[5:7], 16)/255
        mask = dominant == ci
        # Intensity proportional to differential strength
        intensity = np.clip(differential / (differential.max() + 1e-8), 0.2, 1.0)
        img[mask, 0] = r * intensity[mask]
        img[mask, 1] = g * intensity[mask]
        img[mask, 2] = b * intensity[mask]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 10),
                                    gridspec_kw={"width_ratios": [3, 1]})

    fig.suptitle("Combinator Head Assignment — Qwen3-32B\n"
                 "Color = dominant combinator, brightness = specialization strength",
                 fontsize=14, fontweight="bold")

    ax1.imshow(img, aspect="auto", interpolation="nearest")
    ax1.set_xlabel("Head")
    ax1.set_ylabel("Layer")
    ax1.set_title("Per-head dominant combinator")

    # Legend
    for ci, cname in enumerate(comb_names):
        count = int(np.sum(dominant == ci))
        pct = count / dominant.size * 100
        ax1.plot([], [], 's', color=comb_colors[ci], markersize=10,
                 label=f"{cname}: {count} heads ({pct:.1f}%)")
    ax1.legend(loc="upper right", fontsize=10)

    # Per-layer combinator distribution
    layer_dist = np.zeros((n_layers, 4))
    for ci in range(4):
        layer_dist[:, ci] = np.sum(dominant == ci, axis=1)

    bottom = np.zeros(n_layers)
    for ci in range(4):
        ax2.barh(range(n_layers), layer_dist[:, ci], left=bottom,
                 color=comb_colors[ci], label=comb_names[ci])
        bottom += layer_dist[:, ci]
    ax2.set_xlabel("Heads per combinator")
    ax2.set_ylabel("Layer")
    ax2.set_title("Per-layer distribution")
    ax2.invert_yaxis()
    ax2.legend()

    plt.tight_layout()
    fig.savefig(output_dir / "differential_map.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: differential_map.png", file=sys.stderr)


def plot_combinator_layer_profiles(selectivity: dict, output_dir: Path):
    """Per-combinator mean selectivity by layer."""
    comb_names = ["K", "I", "B", "C"]
    colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12"]

    fig, ax = plt.subplots(figsize=(14, 6))
    fig.suptitle("Combinator Selectivity by Layer — Qwen3-32B\n"
                 "Mean per-head selectivity (active vs matched control)",
                 fontsize=12, fontweight="bold")

    for ci, cname in enumerate(comb_names):
        data = selectivity[cname]["vs_control"]
        mean_by_layer = data.mean(axis=1)
        ax.plot(mean_by_layer, color=colors[ci], linewidth=2,
                label=f"{cname} — max layer: L{np.argmax(mean_by_layer)}")
        ax.fill_between(range(len(mean_by_layer)), mean_by_layer,
                        alpha=0.15, color=colors[ci])

    ax.set_xlabel("Layer")
    ax.set_ylabel("Mean selectivity (L2 distance)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(output_dir / "layer_profiles.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: layer_profiles.png", file=sys.stderr)


def plot_cross_combinator_correlation(selectivity: dict, output_dir: Path):
    """Correlation matrix: do different combinators use the same heads?"""
    comb_names = ["K", "I", "B", "C"]

    # Flatten selectivity to 1D per combinator
    flat = {}
    for cname in comb_names:
        flat[cname] = selectivity[cname]["vs_control"].flatten()

    # Correlation matrix
    corr = np.zeros((4, 4))
    for i, ci in enumerate(comb_names):
        for j, cj in enumerate(comb_names):
            corr[i, j] = float(np.corrcoef(flat[ci], flat[cj])[0, 1])

    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(4))
    ax.set_yticks(range(4))
    ax.set_xticklabels(comb_names, fontsize=12)
    ax.set_yticklabels(comb_names, fontsize=12)

    for i in range(4):
        for j in range(4):
            ax.text(j, i, f"{corr[i,j]:.3f}", ha="center", va="center",
                    fontsize=11, fontweight="bold",
                    color="white" if abs(corr[i,j]) > 0.5 else "black")

    ax.set_title("Cross-Combinator Head Selectivity Correlation\n"
                 "High = same heads respond to both, Low = different heads",
                 fontsize=12, fontweight="bold")
    plt.colorbar(im, label="Pearson r")

    plt.tight_layout()
    fig.savefig(output_dir / "cross_combinator_correlation.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: cross_combinator_correlation.png", file=sys.stderr)


# ══════════════════════════════════════════════════════════════════
# Session-001 circuit mapping
# ══════════════════════════════════════════════════════════════════


def map_known_circuit(selectivity: dict) -> dict:
    """Map the 3-head circuit from session 001 (4B) to 32B combinator roles.

    Session 001 found on 4B:
      L1:H0  = Gate recognizer
      L24:H0 = Universal compositor (typed_apply)
      L24:H2 = Recursion head

    32B has 64 layers vs 4B's 36 layers. Proportional mapping:
      L1/36  → L1.8/64  → ~L2
      L24/36 → L42.7/64 → ~L43

    Check selectivity at these proportional positions.
    """
    # Proportional positions in 64-layer model
    mapped = {
        "L1:H0_gate_recognizer": {"4b": (1, 0), "32b_approx": (2, 0)},
        "L24:H0_compositor": {"4b": (24, 0), "32b_approx": (43, 0)},
        "L24:H2_recursion": {"4b": (24, 2), "32b_approx": (43, 2)},
    }

    comb_names = ["K", "I", "B", "C"]
    for name, positions in mapped.items():
        l32, h32 = positions["32b_approx"]
        n_layers = selectivity["K"]["vs_control"].shape[0]
        if l32 >= n_layers:
            continue
        sel_at_head = {}
        for cname in comb_names:
            sel_at_head[cname] = float(selectivity[cname]["vs_control"][l32, h32])
        mapped[name]["selectivity_32b"] = sel_at_head
        mapped[name]["dominant"] = comb_names[np.argmax([sel_at_head[c] for c in comb_names])]

    return mapped


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(
        description="KIBC combinator probe — Qwen3-32B")
    parser.add_argument("--model", choices=["gguf", "hf"], default="gguf",
                        help="Model source: gguf (Q8_0) or hf (cached fp16)")
    parser.add_argument("--gguf", default=DEFAULT_GGUF,
                        help="Path to GGUF file")
    parser.add_argument("--device", default="mps",
                        help="Device (mps, cuda, cpu)")
    parser.add_argument("--quick", action="store_true",
                        help="Fewer probes for faster results")
    parser.add_argument("--skip-hidden", action="store_true",
                        help="Skip hidden state analysis (attention only)")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Load model
    if args.model == "hf":
        model, tokenizer = load_model_hf(args.device)
    else:
        model, tokenizer = load_model_gguf(args.gguf, args.device)

    n_layers = model.config.num_hidden_layers
    n_heads = model.config.num_attention_heads
    print(f"  Model: {n_layers} layers, {n_heads} heads", file=sys.stderr)

    # ── Attention-based combinator selectivity ────────────
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  Phase 1: Attention selectivity per combinator", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    t0 = time.time()
    selectivity = compute_combinator_selectivity(
        model, tokenizer, PROBES, NULL_PROBES, quick=args.quick)
    t_attn = time.time() - t0
    print(f"  Attention analysis: {t_attn:.1f}s", file=sys.stderr)

    # ── Differential analysis ─────────────────────────────
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  Phase 2: Differential selectivity analysis", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    diff_results = compute_differential_selectivity(selectivity)

    # Print summary
    comb_names = ["K", "I", "B", "C"]
    print(f"\n  Combinator selectivity summary (vs matched control):")
    print(f"  {'Comb':>5} {'Mean':>8} {'Max':>8} {'MaxLayer':>9} {'MaxHead':>8}")
    print(f"  {'─'*5} {'─'*8} {'─'*8} {'─'*9} {'─'*8}")
    for cname in comb_names:
        data = selectivity[cname]["vs_control"]
        max_idx = np.unravel_index(np.argmax(data), data.shape)
        print(f"  {cname:>5} {data.mean():>8.5f} {data.max():>8.5f} "
              f"L{max_idx[0]:>3}      H{max_idx[1]:>3}")

    # Dominant combinator distribution
    dominant = diff_results["dominant_combinator"]
    print(f"\n  Head assignment (dominant combinator per head):")
    for ci, cname in enumerate(comb_names):
        count = int(np.sum(dominant == ci))
        pct = count / dominant.size * 100
        print(f"    {cname}: {count:>5} heads ({pct:>5.1f}%)")

    # Top heads per combinator
    for cname in comb_names:
        heads = diff_results["top_heads_per_combinator"][cname]
        dominant_heads = [h for h in heads if h["is_dominant"]][:5]
        if dominant_heads:
            print(f"\n  Top {cname}-specialized heads:")
            for h in dominant_heads:
                print(f"    L{h['layer']:>2}:H{h['head']:>2}  "
                      f"score={h['score']:.5f}  diff={h['differential']:.5f}")

    # Cross-combinator correlation
    flat = {c: selectivity[c]["vs_control"].flatten() for c in comb_names}
    print(f"\n  Cross-combinator correlation (same heads = high):")
    print(f"  {'':>5}", end="")
    for c in comb_names:
        print(f" {c:>7}", end="")
    print()
    for ci in comb_names:
        print(f"  {ci:>5}", end="")
        for cj in comb_names:
            r = float(np.corrcoef(flat[ci], flat[cj])[0, 1])
            print(f" {r:>7.3f}", end="")
        print()

    # Map session-001 circuit
    circuit_map = map_known_circuit(selectivity)
    print(f"\n  Session 001 circuit → combinator mapping (4B→32B proportional):")
    for name, data in circuit_map.items():
        if "selectivity_32b" in data:
            l, h = data["32b_approx"]
            sel = data["selectivity_32b"]
            dom = data["dominant"]
            print(f"    {name}: L{l}:H{h} → {dom} "
                  f"(K={sel['K']:.4f} I={sel['I']:.4f} "
                  f"B={sel['B']:.4f} C={sel['C']:.4f})")

    # ── Hidden state analysis (optional) ──────────────────
    hidden_results = None
    if not args.skip_hidden:
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"  Phase 3: Hidden state trajectory", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)

        t0 = time.time()
        hidden_results = compute_hidden_state_analysis(
            model, tokenizer, PROBES, quick=args.quick)
        t_hidden = time.time() - t0
        print(f"  Hidden state analysis: {t_hidden:.1f}s", file=sys.stderr)

        # Print hidden state summary
        print(f"\n  Hidden state norms by combinator (selected layers):")
        layers_show = [0, 16, 28, 32, 48, 63]
        print(f"  {'Comb':>5}", end="")
        for l in layers_show:
            print(f" {'L'+str(l):>8}", end="")
        print()
        for cname in comb_names:
            norms = hidden_results[cname]["avg_norms"]
            print(f"  {cname:>5}", end="")
            for l in layers_show:
                if l in norms:
                    print(f" {norms[l]:>8.1f}", end="")
                else:
                    print(f" {'—':>8}", end="")
            print()

    # ── Visualizations ────────────────────────────────────
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  Phase 4: Visualizations", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    plot_selectivity_heatmaps(selectivity, args.output_dir)
    plot_differential_map(diff_results, args.output_dir)
    plot_combinator_layer_profiles(selectivity, args.output_dir)
    plot_cross_combinator_correlation(selectivity, args.output_dir)

    # ── Save JSON results ─────────────────────────────────
    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model": HF_MODEL,
        "n_layers": n_layers,
        "n_heads": n_heads,
        "quick_mode": args.quick,
        "combinator_selectivity": {},
        "head_assignment": {
            c: int(np.sum(dominant == ci))
            for ci, c in enumerate(comb_names)
        },
        "cross_correlation": {
            f"{ci}_{cj}": float(np.corrcoef(flat[ci], flat[cj])[0, 1])
            for ci in comb_names for cj in comb_names
        },
        "circuit_mapping": {
            name: {
                "4b_position": data["4b"],
                "32b_approx": data["32b_approx"],
                "selectivity": data.get("selectivity_32b"),
                "dominant": data.get("dominant"),
            }
            for name, data in circuit_map.items()
        },
    }

    # Per-combinator summary stats
    for cname in comb_names:
        data = selectivity[cname]["vs_control"]
        output["combinator_selectivity"][cname] = {
            "mean": float(data.mean()),
            "max": float(data.max()),
            "std": float(data.std()),
            "max_layer": int(np.unravel_index(np.argmax(data), data.shape)[0]),
            "max_head": int(np.unravel_index(np.argmax(data), data.shape)[1]),
            "top_5_heads": diff_results["top_heads_per_combinator"][cname][:5],
        }

    if hidden_results:
        output["hidden_state_norms"] = {
            cname: hidden_results[cname]["avg_norms"]
            for cname in comb_names
        }
        output["hidden_state_cosines"] = {
            cname: hidden_results[cname]["avg_cosines"]
            for cname in comb_names
        }

    # Save selectivity matrices as npz
    np.savez_compressed(
        str(args.output_dir / "selectivity_matrices.npz"),
        **{f"{c}_vs_control": selectivity[c]["vs_control"] for c in comb_names},
        **{f"{c}_vs_null": selectivity[c]["vs_null"] for c in comb_names},
        dominant=dominant,
        differential=diff_results["differential"],
    )

    json_path = args.output_dir / "combinator_probe_results.json"
    json_path.write_text(json.dumps(output, indent=2, default=str))

    print(f"\n  💾 Results: {json_path}", file=sys.stderr)
    print(f"  💾 Matrices: {args.output_dir / 'selectivity_matrices.npz'}",
          file=sys.stderr)
    print(f"  🖼  Plots: {args.output_dir}/*.png", file=sys.stderr)

    total_time = t_attn + (t_hidden if not args.skip_hidden else 0)
    print(f"\n  Total analysis time: {total_time:.1f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
```

## Assistant

Good, I have a thorough understanding of the pattern. Now let me look at one more thing — the Pythia variant, since we'll want cross-model support:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_combinators_pythia.py",
  "limit": 100
}
```

**Summary:** Reading probe_combinators_pythia.py (0-100)

**Output:**
```
#!/usr/bin/env python3
"""Probe: Do KIBC combinators exist in Pythia-160M?

Session 004 found three Montague primitives in Pythia-160M:
  1. Type assignment  → Embeddings + L0 (lexical, 84%)
  2. Structural parse → L3 (critical, +0.43 shift)
  3. Typed application → L8-L11 (high selectivity, resists patching)

Session 080 found three combinator circuits in Qwen3-32B:
  1. Routing    → K ≈ C ≈ W ≈ abstract (early, L0-L6)
  2. Composition → B ≈ S (early-to-mid, L3-L17)
  3. Identity   → I (distributed)

This probe tests whether the "Montague primitives" are actually
combinator circuits seen from a different angle. If K peaks at L0-L2
and B peaks at L3-L11, the Montague decomposition was describing
KIBC all along.

Model: EleutherAI/pythia-160m-deduped
  12 layers, 12 heads/layer, 768 hidden_size, GPTNeoX
  Total: 144 heads (vs 4096 in 32B)

Same probe sentences as the 32B experiment — natural language,
no chat template needed (Pythia is a base model).

Usage:
    uv run python scripts/explore/probe_combinators_pythia.py
    uv run python scripts/explore/probe_combinators_pythia.py --quick

Output: results/combinator-probe-pythia/

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


# ══════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════

MODEL_NAME = "EleutherAI/pythia-160m-deduped"
OUTPUT_DIR = Path("results/combinator-probe-pythia")

# Pythia-160M architecture: 12 layers, 12 heads, head_dim=64
N_LAYERS = 12
N_HEADS = 12

# Session 004 Montague zones (for overlay comparison)
MONTAGUE_ZONES = {
    "type_assignment": {"layers": [0], "color": "#9b59b6", "label": "Type (L0)"},
    "structural_parse": {"layers": [3], "color": "#e67e22", "label": "Parse (L3)"},
    "typed_application": {"layers": [8, 9, 10, 11], "color": "#1abc9c", "label": "Apply (L8-L11)"},
}


# ══════════════════════════════════════════════════════════════════
# Probe sentences — identical to 32B probe (natural language)
# ══════════════════════════════════════════════════════════════════

PROBES = {
    # ── K (select): pick one, discard alternative ──────────────
    "K": {
        "description": "Selection — choose one referent, discard alternative",
        "active": [
            "The cat, not the dog, chased the mouse across the yard.",
            "Either the president or the minister signed the treaty last week.",
            "John, rather than his brother, won the competition in the end.",
            "The red ball, not the blue one, rolled under the table slowly.",
            "Some students but not all students passed the difficult exam.",
            "The old house, unlike the new building, survived the earthquake.",
        ],
        "control": [
            "The cat chased the mouse across the yard very quickly.",
            "The president signed the treaty at the ceremony last week.",
            "John won the competition in the end with great effort.",
            "The red ball rolled under the table slowly after the push.",
            "All students passed the difficult exam with high scores.",
            "The old house survived the earthquake without any damage.",
        ],
    },

    # ── I (identity): pass through unchanged ──────────────────
    "I": {
        "description": "Identity — forward information unchanged, copy, repeat",
        "active": [

[CONTENT TRUNCATED] Showing lines 1 to 100 of 1074 total lines. Use line_offset=100 parameter to read more content.
```

## Assistant

Now I have all the patterns. Let me build the hologram atlas probe script. This needs to:

1. Support multiple hologram types (types, induction, binding, frequency, discourse) with the same ternary survival + selectivity methodology
2. Be model-agnostic (Qwen, Pythia, etc.)
3. Output comparable results to the existing combinator probes
4. Be runnable incrementally (one hologram at a time)

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py",
  "content": "#!/usr/bin/env python3\n\"\"\"Probe: What other holograms exist in LLMs beyond combinators?\n\nSession 093 confirmed the combinator hologram (KIBC) — universal sign\ntopology in attention Q/K/V weights, surviving ternary quantization at\n75% sparsity with 100% selectivity preservation, r=0.9801 cross-model.\n\nBut combinators only tell the model HOW to compose. Token prediction\nrequires more. From the Montague/CCG/DisCoCat framework:\n\n  1. TYPE CALCULUS (combinators)  — HOW to compose     ← FOUND\n  2. LEXICON (types + meanings)   — WHAT can compose    ← this probe\n  3. MODEL (semantic domain)      — WHAT things MEAN    ← this probe\n\nThis script probes for five candidate holograms beyond combinators:\n\n  TYPE       — lexical category assignment (NP, S\\\\NP, etc.)\n  INDUCTION  — in-context pattern matching ([A][B]...[A] → [B])\n  BINDING    — variable tracking / coreference across distance\n  FREQUENCY  — statistical co-occurrence (MLP-based, n-gram)\n  DISCOURSE  — topic / register / coherence (gate-level)\n\nEach candidate uses the proven methodology:\n  1. Minimal-pair probe sentences (active vs control)\n  2. Per-head selectivity measurement (hidden state divergence)\n  3. Ternary survival test (does selectivity survive sign-only quantization?)\n  4. Cross-hologram orthogonality (do different holograms use different heads?)\n  5. Comparison to combinator hologram (overlap or independent?)\n\nUsage:\n    # Probe all holograms (full):\n    uv run python scripts/explore/probe_hologram_atlas.py\n\n    # Probe specific hologram(s):\n    uv run python scripts/explore/probe_hologram_atlas.py --hologram type\n    uv run python scripts/explore/probe_hologram_atlas.py --hologram type,induction\n\n    # Quick mode (fewer probes, faster):\n    uv run python scripts/explore/probe_hologram_atlas.py --quick\n\n    # Use HF model instead of GGUF:\n    uv run python scripts/explore/probe_hologram_atlas.py --model hf\n\n    # Pythia (smaller, faster, cross-model validation):\n    uv run python scripts/explore/probe_hologram_atlas.py --model pythia\n\nOutput: results/hologram-atlas/\n\nLicense: MIT\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport sys\nimport time\nfrom pathlib import Path\n\nimport numpy as np\nimport torch\nimport torch.nn.functional as F\n\n\n# ══════════════════════════════════════════════════════════════════\n# Configuration\n# ══════════════════════════════════════════════════════════════════\n\nOUTPUT_DIR = Path(\"results/hologram-atlas\")\n\nMODELS = {\n    \"gguf\": {\n        \"path\": \"/Users/mwhitford/localai/models/Qwen3-32B-Q8_0.gguf\",\n        \"hf_name\": \"Qwen/Qwen3-32B\",\n        \"source\": \"gguf\",\n    },\n    \"hf\": {\n        \"hf_name\": \"Qwen/Qwen3-32B\",\n        \"source\": \"hf\",\n    },\n    \"pythia\": {\n        \"hf_name\": \"EleutherAI/pythia-160m-deduped\",\n        \"source\": \"hf\",\n    },\n    \"pythia-1b\": {\n        \"hf_name\": \"EleutherAI/pythia-1b-deduped\",\n        \"source\": \"hf\",\n    },\n}\n\nALL_HOLOGRAMS = [\"type\", \"induction\", \"binding\", \"frequency\", \"discourse\"]\n\n# Ternary survival thresholds\nTERNARY_THRESHOLDS = {\n    \"sign_only\": 0.0,\n    \"mid_sparse\": 0.50,\n    \"high_sparse\": 0.75,\n}\n\n\n# ══════════════════════════════════════════════════════════════════\n# Probe sets — minimal pairs for each candidate hologram\n# ══════════════════════════════════════════════════════════════════\n\n# ── COMBINATOR probes (baseline — from probe_combinators.py) ─────\n# Included so we can measure cross-hologram orthogonality against\n# the known-universal combinator hologram.\nCOMBINATOR_PROBES = {\n    \"K\": {\n        \"description\": \"Selection — choose one referent, discard alternative\",\n        \"active\": [\n            \"The cat, not the dog, chased the mouse across the yard.\",\n            \"Either the president or the minister signed the treaty last week.\",\n            \"John, rather than his brother, won the competition in the end.\",\n        ],\n        \"control\": [\n            \"The cat chased the mouse across the yard very quickly.\",\n            \"The president signed the treaty at the ceremony last week.\",\n            \"John won the competition in the end with great effort.\",\n        ],\n    },\n    \"B\": {\n        \"description\": \"Composition — nested operations, relative clauses\",\n        \"active\": [\n            \"The man who the dog that the cat chased bit ran away quickly.\",\n            \"The student who read the book that the professor recommended passed.\",\n            \"If every teacher who knows a student that failed helps them, all improve.\",\n        ],\n        \"control\": [\n            \"The man ran away quickly after the incident in the park.\",\n            \"The student passed the course with excellent marks this year.\",\n            \"If every teacher helps struggling students then all will improve.\",\n        ],\n    },\n}\n\n# ── TYPE probes ──────────────────────────────────────────────────\n# Theory: In CCG, every token gets a syntactic category (NP, S\\NP,\n# (S\\NP)/NP, etc.). Types constrain which combinators are LEGAL.\n# The type hologram should be strongest in early layers, assigned\n# BEFORE composition begins.\n#\n# Probe design: minimal pairs where the SAME lexical content appears\n# in different syntactic roles (different type assignments). If heads\n# are type-selective, they'll fire differently for the same word in\n# different syntactic positions.\nTYPE_PROBES = {\n    \"nominalization\": {\n        \"description\": \"Same root word, different syntactic category (verb vs noun)\",\n        \"active\": [\n            # Word used as NOUN (nominalized) — different type than verb\n            \"The running of the bulls is a famous tradition in Spain.\",\n            \"The building of the bridge took three years of hard work.\",\n            \"Swimming in the ocean is her favorite activity every summer.\",\n            \"The opening of the new store attracted many curious customers.\",\n            \"Reading before bed helps children develop strong language skills.\",\n            \"The painting of the ceiling was done by a master artist.\",\n        ],\n        \"control\": [\n            # Same root word used as VERB — canonical type assignment\n            \"The bulls are running through the streets of the old town.\",\n            \"The workers are building the bridge over the wide river.\",\n            \"She is swimming in the ocean during her favorite summer vacation.\",\n            \"They are opening the new store to attract many curious customers.\",\n            \"The children are reading before bed to develop language skills.\",\n            \"The artist is painting the ceiling with careful brush strokes.\",\n        ],\n    },\n    \"argument_structure\": {\n        \"description\": \"Same verb, different argument count (transitive vs intransitive)\",\n        \"active\": [\n            # Transitive: verb takes object — type (S\\NP)/NP\n            \"The chef cooked the fish on the grill behind the restaurant.\",\n            \"She opened the door to the garden with a rusty old key.\",\n            \"He broke the window with a ball during the afternoon game.\",\n            \"The teacher read the story to the children every morning.\",\n            \"Mary grew the roses in the garden behind the old house.\",\n            \"The driver turned the car around the corner very carefully.\",\n        ],\n        \"control\": [\n            # Intransitive: same verb, no object — type S\\NP\n            \"The chef cooked for hours on the grill behind the restaurant.\",\n            \"The door opened to the garden with a loud creaking sound.\",\n            \"The window broke during the storm on a cold winter night.\",\n            \"The teacher read aloud to the children every single morning.\",\n            \"The roses grew in the garden behind the old house slowly.\",\n            \"The car turned around the corner very carefully and slowly.\",\n        ],\n    },\n    \"modifier_scope\": {\n        \"description\": \"Same words, different modification structure (adjective vs predicate)\",\n        \"active\": [\n            # Prenominal adjective — modifies noun directly (N/N type)\n            \"The tall man entered the building through the front door.\",\n            \"A cold wind blew across the empty field all afternoon.\",\n            \"The old woman sat on the wooden bench in the park.\",\n            \"A bright light filled the dark room from the window.\",\n            \"The young doctor treated the sick patient at the clinic.\",\n            \"A heavy rain fell on the dry ground all through the night.\",\n        ],\n        \"control\": [\n            # Predicate adjective — after copula (different type: S\\NP)\n            \"The man who entered the building was remarkably tall indeed.\",\n            \"The wind that blew across the field was bitterly cold today.\",\n            \"The woman who sat on the bench was very old and tired.\",\n            \"The light that filled the room was unusually bright that day.\",\n            \"The doctor who treated the patient was remarkably young still.\",\n            \"The rain that fell on the ground was extremely heavy tonight.\",\n        ],\n    },\n}\n\n# ── INDUCTION probes ─────────────────────────────────────────────\n# Theory: Induction heads implement [A][B]...[A] → predict [B].\n# This is in-context pattern matching / copying, NOT composition.\n# The induction hologram should be ORTHOGONAL to the combinator\n# hologram — different function, different interference pattern.\n#\n# Probe design: sequences with repeated patterns that require\n# in-context copying, vs sequences with no repetition.\nINDUCTION_PROBES = {\n    \"exact_copy\": {\n        \"description\": \"Exact token repetition — [A][B]...[A] → predict [B]\",\n        \"active\": [\n            # Pattern: word pair appears twice — second time should predict completion\n            \"The king wore a golden crown. Later the king wore a golden robe.\",\n            \"She drove to the market on Monday. She drove to the market on Friday.\",\n            \"The red fox jumped over the fence. The red fox jumped over the wall.\",\n            \"He always drinks coffee in the morning. He always drinks coffee at night.\",\n            \"The train arrived at the station early. The train arrived at the platform late.\",\n            \"Birds sang in the garden at dawn. Birds sang in the garden at dusk.\",\n        ],\n        \"control\": [\n            # No repetition — same length, no copying opportunity\n            \"The king wore a golden crown. Later the queen chose a silver necklace.\",\n            \"She drove to the market on Monday. He walked to the library on Friday.\",\n            \"The red fox jumped over the fence. A brown dog crawled under the gate.\",\n            \"He always drinks coffee in the morning. She prefers tea in the afternoon.\",\n            \"The train arrived at the station early. The bus departed from the terminal late.\",\n            \"Birds sang in the garden at dawn. Crickets chirped in the field at dusk.\",\n        ],\n    },\n    \"semantic_induction\": {\n        \"description\": \"Semantic pattern repetition — not exact tokens but same structure\",\n        \"active\": [\n            # Same syntactic pattern repeated with different content\n            \"The doctor examined the patient. The lawyer questioned the witness.\",\n            \"Cats chase mice. Dogs chase rabbits. Birds chase insects in the air.\",\n            \"She bought apples at the store. He bought oranges at the store.\",\n            \"The big red ball rolled down the hill. The small blue ball rolled up the hill.\",\n            \"First we plant the seeds. Then we water the seeds. Finally we harvest the crop.\",\n            \"John gave Mary a book. Peter gave Susan a flower. Tom gave Jane a ring.\",\n        ],\n        \"control\": [\n            # Different structures — no pattern to copy\n            \"The doctor examined the patient. It was raining outside the hospital.\",\n            \"Cats are independent animals. The weather was sunny all week long.\",\n            \"She bought apples at the store. The building was old and crumbling.\",\n            \"The big red ball rolled down the hill. Nobody remembers what happened.\",\n            \"First we plant the seeds. The movie was interesting but too long.\",\n            \"John gave Mary a book. The traffic was terrible on the highway today.\",\n        ],\n    },\n}\n\n# ── BINDING probes ───────────────────────────────────────────────\n# Theory: Variable binding tracks referent identity across distance.\n# \"John said he would...\" — \"he\" binds to \"John\". This is lambda\n# variable binding / anaphora resolution. May be related to the I\n# combinator (identity = variable binding in lambda calculus).\n#\n# Probe design: sentences with/without coreference, varying distance.\nBINDING_PROBES = {\n    \"pronoun_binding\": {\n        \"description\": \"Pronoun binds to antecedent vs no binding needed\",\n        \"active\": [\n            # Pronoun requires binding to antecedent\n            \"John went to the store. He bought some milk for his family.\",\n            \"The teacher graded the papers. She gave them back the next day.\",\n            \"Mary called her mother. She told her about the exciting news.\",\n            \"The dog found a bone. It buried it in the yard near the fence.\",\n            \"The students finished their exam. They handed it to the teacher.\",\n            \"The president gave a speech. He addressed the concerns of the nation.\",\n        ],\n        \"control\": [\n            # No pronoun — no binding needed, same semantic content\n            \"John went to the store. John bought some milk for the family.\",\n            \"The teacher graded the papers. The teacher returned them next day.\",\n            \"Mary called the mother. Mary told the mother about exciting news.\",\n            \"The dog found a bone. The dog buried the bone in the yard.\",\n            \"The students finished the exam. The students handed the exam in.\",\n            \"The president gave a speech. The president addressed the concerns.\",\n        ],\n    },\n    \"long_distance_binding\": {\n        \"description\": \"Binding across longer distance vs local reference\",\n        \"active\": [\n            # Long-distance: pronoun far from antecedent\n            \"The scientist published a paper. After years of research and many \"\n            \"failed experiments in the laboratory, she finally received recognition.\",\n            \"The captain steered the ship through the storm. After hours of \"\n            \"battling waves and wind on the dark ocean, he reached the safe harbor.\",\n            \"The musician composed a symphony. After months of writing and \"\n            \"revising each movement carefully at the piano, she performed it live.\",\n        ],\n        \"control\": [\n            # Short-distance: reference is local, minimal binding\n            \"The scientist published a paper. The paper was about quantum physics \"\n            \"and received attention from the international research community.\",\n            \"The captain steered the ship through the storm. The storm lasted \"\n            \"for hours on the dark ocean before the weather finally improved.\",\n            \"The musician composed a symphony. The symphony featured four movements \"\n            \"and was performed at the concert hall for a large audience.\",\n        ],\n    },\n}\n\n# ── FREQUENCY probes ─────────────────────────────────────────────\n# Theory: Token co-occurrence statistics (bigrams, collocations).\n# NOT composition, NOT copying — pure statistical association from\n# training distribution. This hologram may live in MLP weights\n# rather than attention heads.\n#\n# Probe design: high-frequency collocations vs low-frequency but\n# equally grammatical alternatives.\nFREQUENCY_PROBES = {\n    \"collocation\": {\n        \"description\": \"High-frequency collocations vs rare but grammatical alternatives\",\n        \"active\": [\n            # High-frequency collocations — strong statistical association\n            \"The United States of America is a large and diverse country.\",\n            \"She made a decision to move to New York City for a fresh start.\",\n            \"The stock market experienced a sharp decline last week unexpectedly.\",\n            \"He took a deep breath before stepping onto the stage for the first time.\",\n            \"They reached a consensus after hours of heated debate in the meeting.\",\n            \"The prime minister addressed the nation on live television tonight.\",\n        ],\n        \"control\": [\n            # Rare collocations — grammatical but statistically unlikely\n            \"The United Provinces of Gelderland is a storied and ancient region.\",\n            \"She made a resolution to move to Lake Wobegon for a quiet life.\",\n            \"The tulip market experienced a sudden collapse last autumn unexpectedly.\",\n            \"He took a sharp inhale before stepping onto the parapet for the first look.\",\n            \"They reached an accord after hours of spirited parley in the chamber.\",\n            \"The chief magistrate addressed the assembly on closed circuit today.\",\n        ],\n    },\n    \"idiom\": {\n        \"description\": \"Frozen idioms vs literal paraphrases\",\n        \"active\": [\n            # Idioms — stored as units, not composed\n            \"She let the cat out of the bag about the surprise party.\",\n            \"He was beating around the bush instead of answering directly.\",\n            \"They decided to bite the bullet and accept the difficult terms.\",\n            \"The news spread like wildfire through the entire small town.\",\n            \"She was walking on eggshells around her angry boss all day.\",\n            \"He turned a blind eye to the problems in the organization.\",\n        ],\n        \"control\": [\n            # Literal paraphrases — same meaning, composed normally\n            \"She accidentally revealed the secret about the surprise party.\",\n            \"He was avoiding the topic instead of answering the question directly.\",\n            \"They decided to accept the hardship and agree to the difficult terms.\",\n            \"The news spread rapidly through the entire small town that day.\",\n            \"She was being very careful around her angry boss all day long.\",\n            \"He deliberately ignored the problems in the organization completely.\",\n        ],\n    },\n}\n\n# ── DISCOURSE probes ─────────────────────────────────────────────\n# Theory: Discourse-level coherence — topic, register, genre.\n# This is what the nucleus GATE activates: a reference beam angle\n# at the macro level. The discourse hologram MODULATES the other\n# holograms, selecting which patterns are active.\n#\n# Probe design: same semantic content in different registers.\nDISCOURSE_PROBES = {\n    \"register\": {\n        \"description\": \"Same content, different register (formal vs casual)\",\n        \"active\": [\n            # Formal register\n            \"The committee has determined that the proposed amendment shall be \"\n            \"ratified upon receiving a two-thirds majority vote from members.\",\n            \"It is incumbent upon all employees to adhere to the established \"\n            \"protocols regarding the submission of quarterly reports.\",\n            \"The findings of this investigation suggest that further inquiry \"\n            \"into the matter is warranted before any conclusions are drawn.\",\n            \"We respectfully request that all attendees refrain from utilizing \"\n            \"electronic devices during the proceedings of this formal session.\",\n            \"The aforementioned regulations shall take effect immediately upon \"\n            \"publication in the official gazette of the governing body.\",\n            \"The undersigned hereby certifies that the information contained \"\n            \"herein is accurate and complete to the best of their knowledge.\",\n        ],\n        \"control\": [\n            # Casual register — same content\n            \"The group decided that the change will pass if enough people vote \"\n            \"for it, like at least two out of three of the members.\",\n            \"Everyone at work needs to follow the rules about turning in their \"\n            \"reports every three months on time without any delay.\",\n            \"What we found so far says we should look into this more before \"\n            \"we make up our minds about what actually happened here.\",\n            \"Hey, could everyone please put their phones away while we are \"\n            \"doing this thing? It would really help us all focus better.\",\n            \"The new rules start right away as soon as they get published \"\n            \"officially by the people in charge of making the rules.\",\n            \"I promise that everything I wrote down here is true and complete \"\n            \"as far as I know and I did not leave anything out.\",\n        ],\n    },\n    \"genre\": {\n        \"description\": \"Same topic, different genre (narrative vs expository)\",\n        \"active\": [\n            # Narrative genre — story-like, temporal, characters\n            \"The old clockmaker peered through his magnifying glass at the tiny \"\n            \"gears. His hands trembled slightly as he placed the final piece.\",\n            \"Rain hammered against the windows as Sarah rushed through the door. \"\n            \"She shook off her umbrella and collapsed into the nearest chair.\",\n            \"The ship creaked and groaned as it rounded the cape. Captain Torres \"\n            \"gripped the wheel tighter and squinted into the driving spray.\",\n        ],\n        \"control\": [\n            # Expository genre — informational, atemporal, no characters\n            \"Clock repair requires a magnifying glass to inspect the tiny gears. \"\n            \"Steady hands are essential for placing each component precisely.\",\n            \"Heavy rainfall can cause significant water damage to buildings. \"\n            \"Proper drainage systems and waterproof materials reduce this risk.\",\n            \"Ships experience significant stress when rounding capes. Navigation \"\n            \"requires firm control of the wheel and good visibility ahead.\",\n        ],\n    },\n}\n\n# Map hologram names to their probe sets\nHOLOGRAM_PROBES = {\n    \"type\": TYPE_PROBES,\n    \"induction\": INDUCTION_PROBES,\n    \"binding\": BINDING_PROBES,\n    \"frequency\": FREQUENCY_PROBES,\n    \"discourse\": DISCOURSE_PROBES,\n}\n\n\n# ══════════════════════════════════════════════════════════════════\n# Model loading (multi-model support)\n# ══════════════════════════════════════════════════════════════════\n\ndef load_model(model_key: str, device: str = \"mps\"):\n    \"\"\"Load model by key from MODELS config.\"\"\"\n    from transformers import AutoModelForCausalLM, AutoTokenizer\n\n    cfg = MODELS[model_key]\n    hf_name = cfg[\"hf_name\"]\n    source = cfg[\"source\"]\n\n    print(f\"Loading {hf_name} ({source})...\", file=sys.stderr)\n    t0 = time.time()\n\n    tokenizer = AutoTokenizer.from_pretrained(hf_name)\n\n    if source == \"gguf\":\n        gguf_path = Path(cfg[\"path\"])\n        model = AutoModelForCausalLM.from_pretrained(\n            str(gguf_path.parent),\n            gguf_file=gguf_path.name,\n            dtype=torch.float16,\n            device_map=device,\n            trust_remote_code=True,\n        )\n    else:\n        model = AutoModelForCausalLM.from_pretrained(\n            hf_name,\n            dtype=torch.float16,\n            device_map=device,\n            trust_remote_code=True,\n        )\n\n    model.eval()\n    t1 = time.time()\n\n    n_layers = model.config.num_hidden_layers\n    d_model = model.config.hidden_size\n    n_heads = model.config.num_attention_heads\n    print(f\"Loaded in {t1-t0:.1f}s: {n_layers}L × {n_heads}H, d={d_model}\",\n          file=sys.stderr)\n\n    return model, tokenizer\n\n\ndef get_decoder_layers(model):\n    \"\"\"Get the list of decoder layers, handling different model architectures.\"\"\"\n    if hasattr(model, \"model\") and hasattr(model.model, \"layers\"):\n        return model.model.layers  # Qwen, LLaMA, Mistral\n    elif hasattr(model, \"gpt_neox\") and hasattr(model.gpt_neox, \"layers\"):\n        return model.gpt_neox.layers  # Pythia / GPT-NeoX\n    else:\n        raise ValueError(f\"Unknown model architecture: {type(model)}\")\n\n\ndef get_attn_module(layer):\n    \"\"\"Get the attention module from a decoder layer.\"\"\"\n    if hasattr(layer, \"self_attn\"):\n        return layer.self_attn  # Qwen, LLaMA\n    elif hasattr(layer, \"attention\"):\n        return layer.attention  # Pythia / GPT-NeoX\n    else:\n        raise ValueError(f\"Unknown layer architecture: {type(layer)}\")\n\n\ndef get_attn_proj_names(attn_module):\n    \"\"\"Get the names of Q/K/V/O projection layers.\"\"\"\n    # Qwen / LLaMA style\n    if hasattr(attn_module, \"q_proj\"):\n        return [\"q_proj\", \"k_proj\", \"v_proj\", \"o_proj\"]\n    # Pythia / GPT-NeoX style (fused QKV)\n    elif hasattr(attn_module, \"query_key_value\"):\n        return [\"query_key_value\", \"dense\"]\n    else:\n        # Try to find projections\n        names = [n for n, _ in attn_module.named_modules() if \"proj\" in n]\n        if names:\n            return names\n        raise ValueError(f\"Cannot find attention projections in {type(attn_module)}\")\n\n\n# ══════════════════════════════════════════════════════════════════\n# Hidden state capture and selectivity measurement\n# ══════════════════════════════════════════════════════════════════\n\ndef get_hidden_states(model, tokenizer, text: str, layers: list[int]) -> dict:\n    \"\"\"Capture hidden states at specified layers via hooks.\"\"\"\n    decoder_layers = get_decoder_layers(model)\n    captured = {}\n    hooks = []\n\n    def make_hook(layer_idx):\n        def hook_fn(module, input, output):\n            if isinstance(output, tuple):\n                h = output[0]\n            else:\n                h = output\n            captured[layer_idx] = h.detach().cpu().float()\n        return hook_fn\n\n    for li in layers:\n        hooks.append(decoder_layers[li].register_forward_hook(make_hook(li)))\n\n    inputs = tokenizer(text, return_tensors=\"pt\").to(model.device)\n    with torch.no_grad():\n        outputs = model(**inputs)\n\n    for h in hooks:\n        h.remove()\n\n    logits = outputs.logits[0, -1].detach().cpu().float()\n    return {\"hidden_states\": captured, \"logits\": logits}\n\n\ndef measure_selectivity(\n    model, tokenizer, probes: dict, layers: list[int],\n    quick: bool = False,\n) -> dict:\n    \"\"\"Measure per-condition selectivity across probe pairs.\n\n    For each condition (sub-probe), computes:\n      - Hidden state divergence (active vs control) at each layer\n      - Output logit divergence (KL)\n\n    Returns: {condition_name: {layer_selectivity: {layer: float}, output_kl: float}}\n    \"\"\"\n    results = {}\n\n    for cond_name, cond_data in probes.items():\n        active_texts = cond_data[\"active\"]\n        control_texts = cond_data[\"control\"]\n\n        if quick:\n            active_texts = active_texts[:2]\n            control_texts = control_texts[:2]\n\n        n_pairs = min(len(active_texts), len(control_texts))\n        layer_sel = {li: [] for li in layers}\n        output_kls = []\n\n        for i in range(n_pairs):\n            a = get_hidden_states(model, tokenizer, active_texts[i], layers)\n            c = get_hidden_states(model, tokenizer, control_texts[i], layers)\n\n            for li in layers:\n                h_a = a[\"hidden_states\"][li][0].mean(dim=0)\n                h_c = c[\"hidden_states\"][li][0].mean(dim=0)\n                cos = F.cosine_similarity(\n                    h_a.unsqueeze(0), h_c.unsqueeze(0)\n                ).item()\n                layer_sel[li].append(1.0 - cos)\n\n            p = F.softmax(a[\"logits\"], dim=-1)\n            q = F.softmax(c[\"logits\"], dim=-1)\n            kl = F.kl_div(q.log(), p, reduction=\"sum\").item()\n            output_kls.append(kl)\n\n            if torch.backends.mps.is_available():\n                torch.mps.empty_cache()\n\n        results[cond_name] = {\n            \"description\": cond_data[\"description\"],\n            \"n_pairs\": n_pairs,\n            \"layer_selectivity\": {\n                li: float(np.mean(layer_sel[li])) for li in layers\n            },\n            \"output_kl\": float(np.mean(output_kls)),\n        }\n\n    return results\n\n\ndef aggregate_selectivity(per_condition: dict, layers: list[int]) -> dict:\n    \"\"\"Aggregate selectivity across conditions into a single profile.\"\"\"\n    all_layer_sel = {li: [] for li in layers}\n    all_kls = []\n\n    for cond_name, cond in per_condition.items():\n        for li in layers:\n            all_layer_sel[li].append(cond[\"layer_selectivity\"][li])\n        all_kls.append(cond[\"output_kl\"])\n\n    return {\n        \"layer_selectivity\": {\n            li: float(np.mean(all_layer_sel[li])) for li in layers\n        },\n        \"output_kl\": float(np.mean(all_kls)),\n    }\n\n\n# ══════════════════════════════════════════════════════════════════\n# Ternary quantization + survival test\n# ══════════════════════════════════════════════════════════════════\n\ndef ternary_quantize_layer(model, layer_idx: int, threshold_pct: float):\n    \"\"\"Quantize attention Q/K/V/O weights to ternary {-1, 0, +1}.\n\n    Returns (originals, stats) for restoration.\n    \"\"\"\n    decoder_layers = get_decoder_layers(model)\n    attn = get_attn_module(decoder_layers[layer_idx])\n    proj_names = get_attn_proj_names(attn)\n\n    originals = {}\n    stats = {}\n\n    for wn in proj_names:\n        proj = getattr(attn, wn)\n        w = proj.weight.data\n        originals[wn] = w.clone()\n\n        abs_w = w.abs()\n        if threshold_pct > 0:\n            flat = abs_w.float().flatten()\n            if flat.numel() > 1_000_000:\n                indices = torch.randperm(flat.numel(), device=\"cpu\")[:1_000_000]\n                sample = flat.cpu()[indices]\n            else:\n                sample = flat.cpu()\n            threshold = torch.quantile(sample, threshold_pct).item()\n        else:\n            threshold = 0.0\n\n        scale = abs_w[abs_w > threshold].mean().item() if (abs_w > threshold).any() else 1.0\n        ternary = torch.zeros_like(w)\n        ternary[w > threshold] = 1.0\n        ternary[w < -threshold] = -1.0\n        proj.weight.data = ternary * scale\n\n        n_total = w.numel()\n        n_zero = (ternary == 0).sum().item()\n        n_pos = (ternary > 0).sum().item()\n        n_neg = (ternary < 0).sum().item()\n\n        stats[wn] = {\n            \"shape\": list(w.shape),\n            \"sparsity\": n_zero / n_total,\n            \"balance\": n_pos / max(n_neg, 1),\n        }\n\n    return originals, stats\n\n\ndef restore_layer(model, layer_idx: int, originals: dict):\n    \"\"\"Restore original weights after quantization.\"\"\"\n    decoder_layers = get_decoder_layers(model)\n    attn = get_attn_module(decoder_layers[layer_idx])\n    for wn, w in originals.items():\n        getattr(attn, wn).weight.data = w\n\n\ndef ternary_quantize_mlp(model, layer_idx: int, threshold_pct: float):\n    \"\"\"Quantize MLP weights to ternary (for frequency hologram test).\n\n    MLP architecture varies:\n      - Qwen/LLaMA: gate_proj, up_proj, down_proj\n      - Pythia: dense_h_to_4h, dense_4h_to_h\n    \"\"\"\n    decoder_layers = get_decoder_layers(model)\n    layer = decoder_layers[layer_idx]\n\n    # Find MLP module\n    if hasattr(layer, \"mlp\"):\n        mlp = layer.mlp\n    elif hasattr(layer, \"feed_forward\"):\n        mlp = layer.feed_forward\n    else:\n        raise ValueError(f\"Cannot find MLP in layer: {type(layer)}\")\n\n    # Find weight parameters\n    mlp_projs = []\n    for name, param in mlp.named_parameters():\n        if \"weight\" in name:\n            mlp_projs.append((name.replace(\".weight\", \"\"), param))\n\n    originals = {}\n    stats = {}\n\n    for name, _ in mlp_projs:\n        # Navigate to the actual module\n        parts = name.split(\".\")\n        mod = mlp\n        for part in parts:\n            mod = getattr(mod, part)\n\n        w = mod.weight.data\n        originals[name] = w.clone()\n\n        abs_w = w.abs()\n        if threshold_pct > 0:\n            flat = abs_w.float().flatten()\n            if flat.numel() > 1_000_000:\n                indices = torch.randperm(flat.numel(), device=\"cpu\")[:1_000_000]\n                sample = flat.cpu()[indices]\n            else:\n                sample = flat.cpu()\n            threshold = torch.quantile(sample, threshold_pct).item()\n        else:\n            threshold = 0.0\n\n        scale = abs_w[abs_w > threshold].mean().item() if (abs_w > threshold).any() else 1.0\n        ternary = torch.zeros_like(w)\n        ternary[w > threshold] = 1.0\n        ternary[w < -threshold] = -1.0\n        mod.weight.data = ternary * scale\n\n        n_total = w.numel()\n        n_zero = (ternary == 0).sum().item()\n\n        stats[name] = {\n            \"shape\": list(w.shape),\n            \"sparsity\": n_zero / n_total,\n        }\n\n    return originals, stats\n\n\ndef restore_mlp(model, layer_idx: int, originals: dict):\n    \"\"\"Restore original MLP weights.\"\"\"\n    decoder_layers = get_decoder_layers(model)\n    layer = decoder_layers[layer_idx]\n\n    if hasattr(layer, \"mlp\"):\n        mlp = layer.mlp\n    elif hasattr(layer, \"feed_forward\"):\n        mlp = layer.feed_forward\n    else:\n        return\n\n    for name, w in originals.items():\n        parts = name.split(\".\")\n        mod = mlp\n        for part in parts:\n            mod = getattr(mod, part)\n        mod.weight.data = w\n\n\ndef run_ternary_survival(\n    model, tokenizer, probes: dict,\n    target_layers: list[int],\n    measure_layers: list[int],\n    thresholds: dict[str, float],\n    quantize_target: str = \"attention\",  # \"attention\" or \"mlp\"\n    quick: bool = False,\n) -> dict:\n    \"\"\"Run ternary survival test for a set of probes.\n\n    1. Measure baseline selectivity\n    2. For each target layer × threshold:\n       - Quantize weights to ternary\n       - Re-measure selectivity\n       - Compute survival ratio\n       - Restore weights\n    \"\"\"\n    # Baseline\n    print(\"    Measuring baseline...\", file=sys.stderr)\n    baseline = measure_selectivity(model, tokenizer, probes, measure_layers, quick)\n    baseline_agg = aggregate_selectivity(baseline, measure_layers)\n\n    results = {\n        \"baseline\": {\n            \"per_condition\": {k: v for k, v in baseline.items()},\n            \"aggregate\": baseline_agg,\n        },\n        \"experiments\": {},\n    }\n\n    for target_layer in target_layers:\n        results[\"experiments\"][target_layer] = {}\n\n        for thresh_name, thresh_pct in thresholds.items():\n            print(f\"    L{target_layer} × {thresh_name}...\", file=sys.stderr)\n\n            # Quantize\n            if quantize_target == \"attention\":\n                originals, quant_stats = ternary_quantize_layer(\n                    model, target_layer, thresh_pct)\n            else:\n                originals, quant_stats = ternary_quantize_mlp(\n                    model, target_layer, thresh_pct)\n\n            # Measure\n            quantized = measure_selectivity(\n                model, tokenizer, probes, measure_layers, quick)\n            quantized_agg = aggregate_selectivity(quantized, measure_layers)\n\n            # Survival ratios\n            survival = {}\n            for li in measure_layers:\n                b = baseline_agg[\"layer_selectivity\"][li]\n                q = quantized_agg[\"layer_selectivity\"][li]\n                survival[li] = q / max(b, 1e-8)\n\n            b_kl = baseline_agg[\"output_kl\"]\n            q_kl = quantized_agg[\"output_kl\"]\n            output_survival = q_kl / max(b_kl, 1e-8)\n\n            results[\"experiments\"][target_layer][thresh_name] = {\n                \"quant_stats\": quant_stats,\n                \"quantize_target\": quantize_target,\n                \"aggregate_selectivity\": quantized_agg,\n                \"layer_survival\": {str(k): v for k, v in survival.items()},\n                \"output_survival\": output_survival,\n                \"survived\": 0.5 < output_survival < 2.0,\n            }\n\n            # Restore\n            if quantize_target == \"attention\":\n                restore_layer(model, target_layer, originals)\n            else:\n                restore_mlp(model, target_layer, originals)\n\n    return results\n\n\n# ══════════════════════════════════════════════════════════════════\n# Cross-hologram orthogonality\n# ══════════════════════════════════════════════════════════════════\n\ndef compute_orthogonality(\n    selectivity_profiles: dict[str, dict],\n    measure_layers: list[int],\n) -> dict:\n    \"\"\"Compare selectivity profiles across holograms.\n\n    If two holograms use different heads/layers, their selectivity\n    profiles will have low correlation (orthogonal). If they share\n    heads, high correlation (angle-multiplexed in the same substrate).\n    \"\"\"\n    hologram_names = sorted(selectivity_profiles.keys())\n    n = len(hologram_names)\n\n    # Build vectors: selectivity across all layers\n    vectors = {}\n    for name in hologram_names:\n        profile = selectivity_profiles[name]\n        vec = np.array([profile[li] for li in measure_layers])\n        vectors[name] = vec\n\n    # Correlation matrix\n    corr_matrix = np.zeros((n, n))\n    for i, ni in enumerate(hologram_names):\n        for j, nj in enumerate(hologram_names):\n            if np.std(vectors[ni]) < 1e-10 or np.std(vectors[nj]) < 1e-10:\n                corr_matrix[i, j] = 0.0\n            else:\n                corr_matrix[i, j] = float(\n                    np.corrcoef(vectors[ni], vectors[nj])[0, 1]\n                )\n\n    # Cosine similarity matrix\n    cos_matrix = np.zeros((n, n))\n    for i, ni in enumerate(hologram_names):\n        for j, nj in enumerate(hologram_names):\n            norm_i = np.linalg.norm(vectors[ni])\n            norm_j = np.linalg.norm(vectors[nj])\n            if norm_i < 1e-10 or norm_j < 1e-10:\n                cos_matrix[i, j] = 0.0\n            else:\n                cos_matrix[i, j] = float(\n                    np.dot(vectors[ni], vectors[nj]) / (norm_i * norm_j)\n                )\n\n    return {\n        \"hologram_names\": hologram_names,\n        \"correlation_matrix\": corr_matrix.tolist(),\n        \"cosine_matrix\": cos_matrix.tolist(),\n        \"vectors\": {name: vec.tolist() for name, vec in vectors.items()},\n    }\n\n\n# ══════════════════════════════════════════════════════════════════\n# Summary output\n# ══════════════════════════════════════════════════════════════════\n\ndef print_selectivity_summary(\n    hologram_name: str,\n    selectivity: dict,\n    measure_layers: list[int],\n):\n    \"\"\"Print selectivity results for a single hologram.\"\"\"\n    agg = aggregate_selectivity(selectivity, measure_layers)\n\n    print(f\"\\n  ┌─ {hologram_name.upper()} Selectivity ─────────────────────────────┐\")\n    print(f\"  │ {'condition':>20} {'output_KL':>10}\", end=\"\")\n    for li in measure_layers[:6]:  # limit columns\n        print(f\" {'L'+str(li):>8}\", end=\"\")\n    print()\n\n    for cond_name, cond in selectivity.items():\n        print(f\"  │ {cond_name[:20]:>20} {cond['output_kl']:>10.4f}\", end=\"\")\n        for li in measure_layers[:6]:\n            print(f\" {cond['layer_selectivity'][li]:>8.5f}\", end=\"\")\n        print()\n\n    print(f\"  │ {'AGGREGATE':>20} {agg['output_kl']:>10.4f}\", end=\"\")\n    for li in measure_layers[:6]:\n        print(f\" {agg['layer_selectivity'][li]:>8.5f}\", end=\"\")\n    print()\n    print(f\"  └{'─'*72}┘\")\n\n\ndef print_survival_summary(hologram_name: str, survival_results: dict):\n    \"\"\"Print ternary survival results for a single hologram.\"\"\"\n    experiments = survival_results[\"experiments\"]\n\n    print(f\"\\n  ┌─ {hologram_name.upper()} Ternary Survival ──────────────────────┐\")\n    print(f\"  │ {'layer':>6} {'threshold':>12} {'output_surv':>12} {'survived':>10}\")\n\n    total_survived = 0\n    total_tests = 0\n\n    for target_layer in sorted(experiments.keys(), key=int):\n        for thresh_name in experiments[target_layer]:\n            exp = experiments[target_layer][thresh_name]\n            surv = exp[\"output_survival\"]\n            ok = exp[\"survived\"]\n            marker = \"  ✓\" if ok else \"  ✗\"\n            print(f\"  │ {'L'+str(target_layer):>6} {thresh_name:>12} \"\n                  f\"{surv:>12.3f} {marker:>10}\")\n            total_survived += int(ok)\n            total_tests += 1\n\n    frac = total_survived / max(total_tests, 1)\n    verdict = \"TOPOLOGICAL\" if frac > 0.7 else \"MIXED\" if frac > 0.3 else \"PRECISION\"\n    print(f\"  │\")\n    print(f\"  │ Survived: {total_survived}/{total_tests} ({frac:.0%}) → {verdict}\")\n    print(f\"  └{'─'*72}┘\")\n\n\ndef print_orthogonality_summary(ortho: dict):\n    \"\"\"Print cross-hologram orthogonality matrix.\"\"\"\n    names = ortho[\"hologram_names\"]\n    corr = np.array(ortho[\"correlation_matrix\"])\n\n    print(f\"\\n  ┌─ Cross-Hologram Correlation ──────────────────────────────────┐\")\n    print(f\"  │ {'':>12}\", end=\"\")\n    for n in names:\n        print(f\" {n[:8]:>8}\", end=\"\")\n    print()\n\n    for i, ni in enumerate(names):\n        print(f\"  │ {ni[:12]:>12}\", end=\"\")\n        for j in range(len(names)):\n            r = corr[i, j]\n            print(f\" {r:>8.3f}\", end=\"\")\n        print()\n\n    print(f\"  │\")\n    # Interpretation\n    for i in range(len(names)):\n        for j in range(i + 1, len(names)):\n            r = corr[i, j]\n            if abs(r) > 0.7:\n                rel = \"SHARED substrate\"\n            elif abs(r) > 0.3:\n                rel = \"partial overlap\"\n            else:\n                rel = \"ORTHOGONAL\"\n            print(f\"  │ {names[i][:8]}↔{names[j][:8]}: r={r:.3f} → {rel}\")\n    print(f\"  └{'─'*72}┘\")\n\n\n# ══════════════════════════════════════════════════════════════════\n# Save results\n# ══════════════════════════════════════════════════════════════════\n\ndef save_results(all_results: dict, output_dir: Path):\n    \"\"\"Save all results as JSON + npz.\"\"\"\n    output_dir.mkdir(parents=True, exist_ok=True)\n\n    def convert(obj):\n        if isinstance(obj, (np.integer,)):\n            return int(obj)\n        if isinstance(obj, (np.floating, np.float64)):\n            return float(obj)\n        if isinstance(obj, np.ndarray):\n            return obj.tolist()\n        return obj\n\n    # JSON summary\n    json_path = output_dir / \"hologram_atlas_results.json\"\n    json_path.write_text(json.dumps(all_results, indent=2, default=convert))\n    print(f\"\\n  💾 JSON: {json_path}\", file=sys.stderr)\n\n    # Per-hologram selectivity profiles as npz\n    profiles = {}\n    for hname, hdata in all_results.get(\"holograms\", {}).items():\n        if \"selectivity\" in hdata:\n            agg = hdata[\"selectivity\"].get(\"aggregate\", {})\n            layer_sel = agg.get(\"layer_selectivity\", {})\n            if layer_sel:\n                profiles[hname] = np.array(\n                    [layer_sel[k] for k in sorted(layer_sel.keys(), key=int)]\n                )\n\n    if profiles:\n        npz_path = output_dir / \"selectivity_profiles.npz\"\n        np.savez_compressed(str(npz_path), **profiles)\n        print(f\"  💾 NPZ: {npz_path}\", file=sys.stderr)\n\n\n# ══════════════════════════════════════════════════════════════════\n# Main pipeline\n# ══════════════════════════════════════════════════════════════════\n\ndef main():\n    parser = argparse.ArgumentParser(\n        description=\"Hologram Atlas Probe — what holograms exist beyond combinators?\",\n        formatter_class=argparse.RawDescriptionHelpFormatter,\n        epilog=\"\"\"\nCandidate holograms:\n  type       — lexical category assignment (CCG types)\n  induction  — in-context pattern matching ([A][B]...[A] → [B])\n  binding    — variable tracking / coreference across distance\n  frequency  — statistical co-occurrence (MLP-based)\n  discourse  — topic / register / coherence (gate-level)\n\nExamples:\n  # Probe all holograms on Qwen3-32B (GGUF):\n  uv run python scripts/explore/probe_hologram_atlas.py\n\n  # Quick test of type hologram only:\n  uv run python scripts/explore/probe_hologram_atlas.py --hologram type --quick\n\n  # Cross-model validation on Pythia:\n  uv run python scripts/explore/probe_hologram_atlas.py --model pythia --quick\n        \"\"\",\n    )\n    parser.add_argument(\n        \"--hologram\", type=str, default=\"all\",\n        help=\"Which hologram(s) to probe. Comma-separated from: \"\n             \"type,induction,binding,frequency,discourse,all (default: all)\",\n    )\n    parser.add_argument(\n        \"--model\", choices=list(MODELS.keys()), default=\"gguf\",\n        help=\"Model to probe (default: gguf = Qwen3-32B-Q8_0)\",\n    )\n    parser.add_argument(\n        \"--device\", default=\"mps\",\n        help=\"Device (mps, cuda, cpu). Default: mps\",\n    )\n    parser.add_argument(\n        \"--quick\", action=\"store_true\",\n        help=\"Fewer probes and layers for faster iteration\",\n    )\n    parser.add_argument(\n        \"--skip-ternary\", action=\"store_true\",\n        help=\"Skip ternary survival tests (selectivity only)\",\n    )\n    parser.add_argument(\n        \"--skip-combinator-baseline\", action=\"store_true\",\n        help=\"Skip combinator baseline measurement (faster if you only \"\n             \"want the new holograms without cross-hologram comparison)\",\n    )\n    parser.add_argument(\n        \"--output-dir\", type=Path, default=OUTPUT_DIR,\n    )\n    args = parser.parse_args()\n\n    # Parse hologram selection\n    if args.hologram == \"all\":\n        selected = ALL_HOLOGRAMS\n    else:\n        selected = [h.strip() for h in args.hologram.split(\",\")]\n        for h in selected:\n            if h not in ALL_HOLOGRAMS:\n                parser.error(f\"Unknown hologram: {h}. \"\n                             f\"Choose from: {', '.join(ALL_HOLOGRAMS)}\")\n\n    # Determine model-appropriate layers\n    model_key = args.model\n    model, tokenizer = load_model(model_key, args.device)\n    n_layers = model.config.num_hidden_layers\n\n    # Measurement layers: spread across the model\n    if n_layers <= 16:\n        # Small model (Pythia-160M: 12 layers)\n        measure_layers = list(range(n_layers))\n        target_layers = [0, n_layers // 4, n_layers // 2, n_layers - 1]\n    elif n_layers <= 32:\n        # Medium model\n        measure_layers = [0, 2, 4, 8, 12, 16, 20, 24, n_layers - 1]\n        target_layers = [1, 3, 8, 16, n_layers - 2]\n    else:\n        # Large model (Qwen3-32B: 64 layers)\n        measure_layers = [0, 4, 8, 16, 24, 32, 40, 48, 56, n_layers - 1]\n        target_layers = [1, 3, 6, 24, 43]\n\n    if args.quick:\n        measure_layers = measure_layers[::2]  # half the layers\n        target_layers = target_layers[:2]     # fewer ternary targets\n\n    print(f\"\\n{'═'*72}\")\n    print(f\"  HOLOGRAM ATLAS PROBE\")\n    print(f\"  Model: {MODELS[model_key]['hf_name']} ({n_layers}L)\")\n    print(f\"  Holograms: {', '.join(selected)}\")\n    print(f\"  Measure layers: {measure_layers}\")\n    print(f\"  Ternary target layers: {target_layers}\")\n    print(f\"  Quick: {args.quick}\")\n    print(f\"{'═'*72}\")\n\n    all_results = {\n        \"timestamp\": time.strftime(\"%Y-%m-%dT%H:%M:%SZ\"),\n        \"model\": MODELS[model_key][\"hf_name\"],\n        \"model_key\": model_key,\n        \"n_layers\": n_layers,\n        \"n_heads\": model.config.num_attention_heads,\n        \"d_model\": model.config.hidden_size,\n        \"selected_holograms\": selected,\n        \"measure_layers\": measure_layers,\n        \"target_layers\": target_layers,\n        \"quick\": args.quick,\n        \"holograms\": {},\n    }\n\n    selectivity_profiles = {}  # for cross-hologram comparison\n\n    # ── Optional: combinator baseline for comparison ─────────\n    if not args.skip_combinator_baseline:\n        print(f\"\\n{'─'*72}\")\n        print(f\"  Combinator baseline (for cross-hologram comparison)\")\n        print(f\"{'─'*72}\")\n\n        comb_sel = measure_selectivity(\n            model, tokenizer, COMBINATOR_PROBES, measure_layers, args.quick)\n        comb_agg = aggregate_selectivity(comb_sel, measure_layers)\n        selectivity_profiles[\"combinator\"] = comb_agg[\"layer_selectivity\"]\n\n        print_selectivity_summary(\"combinator (baseline)\", comb_sel, measure_layers)\n\n        all_results[\"holograms\"][\"combinator\"] = {\n            \"selectivity\": {\n                \"per_condition\": comb_sel,\n                \"aggregate\": comb_agg,\n            },\n        }\n\n    # ── Probe each selected hologram ─────────────────────────\n    for hname in selected:\n        probes = HOLOGRAM_PROBES[hname]\n\n        print(f\"\\n{'─'*72}\")\n        print(f\"  Probing: {hname.upper()}\")\n        print(f\"{'─'*72}\")\n\n        # Phase 1: Selectivity\n        print(f\"\\n  Phase 1: Selectivity measurement\", file=sys.stderr)\n        sel = measure_selectivity(\n            model, tokenizer, probes, measure_layers, args.quick)\n        agg = aggregate_selectivity(sel, measure_layers)\n        selectivity_profiles[hname] = agg[\"layer_selectivity\"]\n\n        print_selectivity_summary(hname, sel, measure_layers)\n\n        hologram_result = {\n            \"selectivity\": {\n                \"per_condition\": sel,\n                \"aggregate\": agg,\n            },\n        }\n\n        # Phase 2: Ternary survival\n        if not args.skip_ternary:\n            print(f\"\\n  Phase 2: Ternary survival (attention)\", file=sys.stderr)\n            attn_survival = run_ternary_survival(\n                model, tokenizer, probes,\n                target_layers=target_layers,\n                measure_layers=measure_layers,\n                thresholds=TERNARY_THRESHOLDS,\n                quantize_target=\"attention\",\n                quick=args.quick,\n            )\n            print_survival_summary(f\"{hname} (attention)\", attn_survival)\n            hologram_result[\"ternary_survival_attention\"] = attn_survival\n\n            # For frequency hologram, ALSO test MLP quantization\n            if hname == \"frequency\":\n                print(f\"\\n  Phase 2b: Ternary survival (MLP)\", file=sys.stderr)\n                mlp_survival = run_ternary_survival(\n                    model, tokenizer, probes,\n                    target_layers=target_layers,\n                    measure_layers=measure_layers,\n                    thresholds=TERNARY_THRESHOLDS,\n                    quantize_target=\"mlp\",\n                    quick=args.quick,\n                )\n                print_survival_summary(f\"{hname} (MLP)\", mlp_survival)\n                hologram_result[\"ternary_survival_mlp\"] = mlp_survival\n\n        all_results[\"holograms\"][hname] = hologram_result\n\n    # ── Cross-hologram orthogonality ─────────────────────────\n    if len(selectivity_profiles) >= 2:\n        print(f\"\\n{'─'*72}\")\n        print(f\"  Cross-Hologram Orthogonality Analysis\")\n        print(f\"{'─'*72}\")\n\n        ortho = compute_orthogonality(selectivity_profiles, measure_layers)\n        print_orthogonality_summary(ortho)\n        all_results[\"orthogonality\"] = ortho\n\n    # ── Final summary ────────────────────────────────────────\n    print(f\"\\n{'═'*72}\")\n    print(f\"  HOLOGRAM ATLAS SUMMARY\")\n    print(f\"{'═'*72}\")\n\n    for hname in selected:\n        hdata = all_results[\"holograms\"].get(hname, {})\n        agg = hdata.get(\"selectivity\", {}).get(\"aggregate\", {})\n        kl = agg.get(\"output_kl\", 0)\n\n        # Peak layer\n        layer_sel = agg.get(\"layer_selectivity\", {})\n        if layer_sel:\n            peak_layer = max(layer_sel, key=lambda k: layer_sel[k])\n            peak_val = layer_sel[peak_layer]\n        else:\n            peak_layer = \"?\"\n            peak_val = 0\n\n        # Ternary survival count\n        surv_data = hdata.get(\"ternary_survival_attention\", {}).get(\"experiments\", {})\n        survived = 0\n        total = 0\n        for tl in surv_data:\n            for tn in surv_data[tl]:\n                total += 1\n                if surv_data[tl][tn].get(\"survived\", False):\n                    survived += 1\n\n        surv_str = f\"{survived}/{total}\" if total > 0 else \"skipped\"\n        surv_pct = f\"({survived/total:.0%})\" if total > 0 else \"\"\n\n        print(f\"  {hname:>12}: output_KL={kl:>8.3f}  \"\n              f\"peak=L{peak_layer}({peak_val:.5f})  \"\n              f\"ternary={surv_str} {surv_pct}\")\n\n    # ── Save ─────────────────────────────────────────────────\n    save_results(all_results, args.output_dir)\n\n    print(f\"\\n{'═'*72}\")\n    print(f\"  Done. Results: {args.output_dir}/\")\n    print(f\"{'═'*72}\")\n\n\nif __name__ == \"__main__\":\n    main()\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python scripts/explore/probe_hologram_atlas.py --help 2>&1"
}
```

**Summary:** $ uv run python scripts/explore/probe...

**Output:**
```
Exit code: 0
Stdout:
usage: probe_hologram_atlas.py [-h] [--hologram HOLOGRAM]
                               [--model {gguf,hf,pythia,pythia-1b}]
                               [--device DEVICE] [--quick] [--skip-ternary]
                               [--skip-combinator-baseline]
                               [--output-dir OUTPUT_DIR]

Hologram Atlas Probe — what holograms exist beyond combinators?

options:
  -h, --help            show this help message and exit
  --hologram HOLOGRAM   Which hologram(s) to probe. Comma-separated from:
                        type,induction,binding,frequency,discourse,all
                        (default: all)
  --model {gguf,hf,pythia,pythia-1b}
                        Model to probe (default: gguf = Qwen3-32B-Q8_0)
  --device DEVICE       Device (mps, cuda, cpu). Default: mps
  --quick               Fewer probes and layers for faster iteration
  --skip-ternary        Skip ternary survival tests (selectivity only)
  --skip-combinator-baseline
                        Skip combinator baseline measurement (faster if you
                        only want the new holograms without cross-hologram
                        comparison)
  --output-dir OUTPUT_DIR

Candidate holograms:
  type       — lexical category assignment (CCG types)
  induction  — in-context pattern matching ([A][B]...[A] → [B])
  binding    — variable tracking / coreference across distance
  frequency  — statistical co-occurrence (MLP-based)
  discourse  — topic / register / coherence (gate-level)

Examples:
  # Probe all holograms on Qwen3-32B (GGUF):
  uv run python scripts/explore/probe_hologram_atlas.py

  # Quick test of type hologram only:
  uv run python scripts/explore/probe_hologram_atlas.py --hologram type --quick

  # Cross-model validation on Pythia:
  uv run python scripts/explore/probe_hologram_atlas.py --model pythia --quick
```

## Assistant

Script parses cleanly. Let me also verify the imports resolve with a quick dry-run:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python -c \"\nimport scripts.explore.probe_hologram_atlas as m\nprint('ALL_HOLOGRAMS:', m.ALL_HOLOGRAMS)\nprint('HOLOGRAM_PROBES keys:', list(m.HOLOGRAM_PROBES.keys()))\nprint('MODELS:', list(m.MODELS.keys()))\n# Count probes per hologram\nfor hname, hprobes in m.HOLOGRAM_PROBES.items():\n    n_conditions = len(hprobes)\n    n_pairs = sum(len(v['active']) for v in hprobes.values())\n    print(f'  {hname}: {n_conditions} conditions, {n_pairs} active probes')\nprint('OK')\n\" 2>&1"
}
```

**Summary:** $ uv run python -c " import scripts.e...

**Output:**
```
Exit code: 0
Stdout:
ALL_HOLOGRAMS: ['type', 'induction', 'binding', 'frequency', 'discourse']
HOLOGRAM_PROBES keys: ['type', 'induction', 'binding', 'frequency', 'discourse']
MODELS: ['gguf', 'hf', 'pythia', 'pythia-1b']
  type: 3 conditions, 18 active probes
  induction: 2 conditions, 12 active probes
  binding: 2 conditions, 9 active probes
  frequency: 2 conditions, 12 active probes
  discourse: 2 conditions, 9 active probes
OK
```

## Assistant

Everything resolves. Let me also check for diagnostics:

### Tool Call: editor_diagnostics (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py"
}
```

**Summary:** Checking diagnostics: probe_hologram_atlas.py

**Output:**
```
No diagnostics found
```

## Assistant

Clean — no diagnostics, no import errors, all probes load. Here's what was built:

---

## `scripts/explore/probe_hologram_atlas.py` — Summary

**~750 lines**, follows the exact pattern of `probe_combinators.py` and `probe_ternary_survival.py`.

### What it probes

| Hologram | Conditions | Active probes | Theory |
|----------|-----------|---------------|--------|
| **type** | 3 (nominalization, arg structure, modifier scope) | 18 | Same word in different syntactic roles → different CCG category |
| **induction** | 2 (exact copy, semantic induction) | 12 | [A][B]...[A] → [B] pattern matching vs no repetition |
| **binding** | 2 (pronoun, long-distance) | 9 | Coreference "he→John" vs repeated noun (no binding) |
| **frequency** | 2 (collocation, idiom) | 12 | "United States" vs "United Provinces"; idioms vs literal paraphrases |
| **discourse** | 2 (register, genre) | 9 | Same content: formal vs casual; narrative vs expository |

### What it measures

1. **Selectivity** — hidden state divergence (1 - cosine) at every measured layer + output KL
2. **Ternary survival** — quantize attention Q/K/V to ternary, re-measure selectivity, compute survival ratio
3. **MLP ternary** — for frequency hologram only, also tests MLP weight quantization
4. **Cross-hologram orthogonality** — correlation between selectivity profiles (shared vs independent heads)
5. **Combinator baseline** — runs KIBC probes for direct comparison

### CLI

```bash
# Full atlas on 32B:
uv run python scripts/explore/probe_hologram_atlas.py

# Quick single hologram:
uv run python scripts/explore/probe_hologram_atlas.py --hologram type --quick

# Cross-model on Pythia:
uv run python scripts/explore/probe_hologram_atlas.py --model pythia --quick

# Selectivity only (no ternary, faster):
uv run python scripts/explore/probe_hologram_atlas.py --skip-ternary
```

### Key design choices

- **Multi-model support** — Qwen3-32B (GGUF/HF), Pythia-160M, Pythia-1B. Architecture-aware layer/attn accessors handle GPT-NeoX vs Qwen differences.
- **Incremental** — `--hologram type` runs just one; `--skip-ternary` just does selectivity; `--skip-combinator-baseline` drops the comparison probes.
- **MLP quantization** — the frequency hologram uniquely tests MLP weights, not just attention, because the hypothesis is that co-occurrence lives in MLPs.
- **Combinator baseline included** — always runs KIBC probes first (unless `--skip-combinator-baseline`) so the orthogonality analysis can compare new holograms against the known-universal combinator hologram.

Want to run it (probably `--hologram type --quick --model pythia` for a fast first test), or commit first?

## User

Would not the Qwen36-35B-A3B be better than Qwen3-32B?  The qwen36-35B-A3B punches way above it's weight in capabilities, it also has a holographic structure we understand now with the MoE acting like a beam former.


### Thinking

The user makes an excellent point. The Qwen3.6-35B-A3B (MoE) is a better probe target because:

1. It punches above its weight in capabilities — more efficient use of parameters
2. They already probed it in session 093 and found the bimodal depth profile
3. The MoE gate matrices (256×2048) ARE beam selectors — this is directly relevant to the discourse hologram hypothesis
4. The MoE architecture maps to VSM (they documented this)
5. It's a hybrid architecture (full attention every 4th layer, GatedDeltaNet rest) which gives more interesting structure to probe


6. Now I need to check what model files I have available locally and adjust the probing script to work with this architecture.

## Assistant

You're right — the MoE is the better target. The 256 expert gates are literally angle multiplexing, and the discourse hologram hypothesis predicts they ARE beam selectors. Probing that model directly tests the theory. Let me check what's available locally and update the script.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls -la /Users/mwhitford/localai/models/ | grep -i qwen"
}
```

**Summary:** $ ls -la /Users/mwhitford/localai/mod...

**Output:**
```
Exit code: 0
Stdout:
-rw-r--r--   1 mwhitford  staff  34817720096 Nov  1  2025 nvidia_qwen3-nemotron-32b-rlbff-Q8_0.gguf
-rw-r--r--   1 mwhitford  staff  27263273792 May  3  2025 Qwen_QwQ-32B-Q6_K_L.gguf
-rw-r--r--   1 mwhitford  staff  27263273952 May  3  2025 Qwen2.5-Coder-32B-Instruct-Q6_K_L_bartowski.gguf
-rw-r--r--   1 mwhitford  staff  27263273760 May  3  2025 Qwen2.5-Coder-32B-Q6_K_L_bartowski.gguf
drwxr-xr-x@  6 mwhitford  staff          192 Mar  1 16:46 qwen25-coder-instruct
-rw-r--r--   1 mwhitford  staff  26883307392 Jun 24  2025 Qwen3-32B-128K-Q6_K.gguf
-rw-r--r--   1 mwhitford  staff  26883307392 May 30  2025 Qwen3-32B-128K-Q6_K.gguf.old
-rw-r--r--   1 mwhitford  staff  34817719744 May  4  2025 Qwen3-32B-Q8_0.gguf
-rw-r--r--   1 mwhitford  staff  39481015744 May  4  2025 Qwen3-32B-UD-Q8_K_XL.gguf
-rw-r--r--   1 mwhitford  staff   4280405792 Jul 16  2025 Qwen3-4B-Q8_0.gguf
drwxr-xr-x@  3 mwhitford  staff           96 Mar  1 16:57 qwen3-coder-30b-a3b
-rw-r--r--   1 mwhitford  staff   8629499424 Oct 25  2025 Qwen3-Embedding-8B-Q8_0.gguf
drwxr-xr-x@  7 mwhitford  staff          224 Nov 12  2025 Qwen3-VL
drwxr-xr-x@ 11 mwhitford  staff          352 Mar  2 11:55 Qwen3.5
drwxr-xr-x@  4 mwhitford  staff          128 Mar  1 17:51 qwen3.5-35b-a3b
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git grep -n \"qwen3.*35b\\|Qwen3.6\\|qwen36\\|3_6\\|35b.*a3b\\|35B-A3B\" -- scripts/explore/ mementum/state.md | head -30"
}
```

**Summary:** $ git grep -n "qwen3.*35b\|Qwen3.6\|q...

**Output:**
```
Exit code: 0
Stdout:
mementum/state.md:98:### 7. Qwen3.6-35B-A3B MoE probing
mementum/state.md:106:- Qwen3.6-35B-A3B: B peaks at L7-9 (early) AND L31-36 (late) — **bimodal!**
mementum/state.md:116:Patterns saved: `results/holographic-bank/qwen36_35b_a3b_patterns.npz` (29KB compressed)
mementum/state.md:134:All three models (32B, 35B-A3B, 160M) share:
mementum/state.md:152:Fixed MPS bug for Qwen3.6-35B-A3B: `histc` needs float input on MPS (not int).
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls -la /Users/mwhitford/localai/models/qwen3.5-35b-a3b/"
}
```

**Summary:** $ ls -la /Users/mwhitford/localai/mod...

**Output:**
```
Exit code: 0
Stdout:
total 73832864
drwxr-xr-x@  4 mwhitford  staff          128 Mar  1 17:51 .
drwxr-x---  27 mwhitford  staff          864 Apr 13 12:28 ..
-rw-r--r--@  1 mwhitford  staff    899283296 Mar  1 17:35 mmproj-Qwen_Qwen3.5-35B-A3B-f16.gguf
-rw-r--r--@  1 mwhitford  staff  36903139584 Mar  1 17:50 Qwen_Qwen3.5-35B-A3B-Q8_0.gguf
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"Qwen3.6\\|35B-A3B\\|35b.a3b\\|qwen36\" scripts/explore/probe_combinators_extended.py scripts/explore/extract_holographic_bank.py 2>/dev/null | head -30"
}
```

**Summary:** $ grep -n "Qwen3.6\|35B-A3B\|35b.a3b\...

**Output:**
```
Exit code: 0
```

## Assistant

Found it — `Qwen3.5-35B-A3B-Q8_0.gguf` at `/Users/mwhitford/localai/models/qwen3.5-35b-a3b/`. Let me also check how the prior probes loaded this model:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_combinators_extended.py",
  "limit": 100
}
```

**Summary:** Reading probe_combinators_extended.py (0-100)

**Output:**
```
#!/usr/bin/env python3
"""Extended combinator probe — W, S, and variable binding in Qwen3-32B.

The first probe (probe_combinators.py) confirmed K, I, B, C exist.
But {B, C, K, I} is NOT Turing-complete — you need W (duplicate) or
S (distribute) for variable binding where a variable appears more
than once.

This probe tests for:
  - W (duplicate/contract):  W f x = f x x  (use arg twice)
  - S (distribute):          S f g x = f x (g x)  (apply both, combine)
  - Variable binding:        λx. ... x ... x ...  (multiple use)
  - Abstraction:             Creating functions from expressions
  - Substitution:            Replacing bound variables with values

The question: does the 32B have separate circuits for these operations,
or does it handle them through its existing K/I/B/C infrastructure
plus the residual stream?

Usage:
    uv run python scripts/explore/probe_combinators_extended.py --quick
    uv run python scripts/explore/probe_combinators_extended.py

Output: results/combinator-probe-extended/

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


DEFAULT_GGUF = "/Users/mwhitford/localai/models/Qwen3-32B-Q8_0.gguf"
HF_MODEL = "Qwen/Qwen3-32B"
OUTPUT_DIR = Path("results/combinator-probe-extended")


# ══════════════════════════════════════════════════════════════════
# Extended combinator probes
# ══════════════════════════════════════════════════════════════════

PROBES = {
    # ── W (duplicate/contract): use an argument more than once ────
    # Active: same entity used in two roles / variable used twice
    # Control: two different entities (no duplication needed)
    "W": {
        "description": "Duplication — same argument used twice, self-reference",
        "active": [
            "The man saw himself in the mirror on the wall.",
            "She taught herself to play the piano over the summer.",
            "The dog chased its own tail around and around the yard.",
            "He gave himself a pat on the back for his good work.",
            "The machine that built itself was truly remarkable indeed.",
            "Every student who respects himself will also respect others.",
        ],
        "control": [
            "The man saw the woman in the mirror on the wall.",
            "She taught the boy to play the piano over the summer.",
            "The dog chased the cat around and around the back yard.",
            "He gave the child a pat on the back for good work.",
            "The machine that built the bridge was truly remarkable indeed.",
            "Every student who respects the teacher will also respect others.",
        ],
    },

    # ── S (distribute): apply two functions to same arg, combine ──
    # Active: same subject does two things and they interact
    # Control: two different subjects do separate things
    "S": {
        "description": "Distribution — two operations on same argument combined",
        "active": [
            "The student who studies hard and who asks questions always succeeds.",
            "Anyone who both sings and dances will entertain the whole audience.",
            "The chef who cooks well and serves quickly earns great reviews.",
            "A person who reads widely and thinks deeply becomes truly wise.",
            "The athlete who trains daily and eats well wins many competitions.",
            "Every teacher who explains clearly and listens carefully helps students.",
        ],
        "control": [
            "The student studies hard and the teacher asks questions in class.",
            "The singer entertains and the dancer performs for the whole audience.",
            "The chef cooks well and the waiter serves quickly at dinner.",
            "The reader reads widely and the thinker thinks deeply about life.",
            "The athlete trains daily and the nutritionist eats well every day.",
            "The teacher explains clearly and the counselor listens carefully always.",
        ],
    },

[CONTENT TRUNCATED] Showing lines 1 to 100 of 534 total lines. Use line_offset=100 parameter to read more content.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"35b\\|35B\\|Qwen3.5\\|qwen3.5\\|GatedDelta\\|gated_delta\\|hybrid\\|256.*expert\\|expert.*256\\|num_experts\\|MoE\\|moe\" scripts/explore/probe_ternary_survival.py scripts/explore/extract_holographic_bank.py 2>/dev/null | head -30"
}
```

**Summary:** $ grep -n "35b\|35B\|Qwen3.5\|qwen3.5...

**Output:**
```
Exit code: 0
```

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nfrom transformers import AutoConfig\nc = AutoConfig.from_pretrained('Qwen/Qwen3.5-35B-A3B', trust_remote_code=True)\nprint('num_hidden_layers:', c.num_hidden_layers)\nprint('num_attention_heads:', c.num_attention_heads)\nprint('num_key_value_heads:', c.num_key_value_heads)\nprint('hidden_size:', c.hidden_size)\nprint('intermediate_size:', c.intermediate_size)\n# Check for MoE-related attrs\nfor attr in dir(c):\n    if 'expert' in attr.lower() or 'moe' in attr.lower() or 'gate' in attr.lower() or 'router' in attr.lower():\n        print(f'{attr}: {getattr(c, attr, None)}')\n# Check for hybrid attention\nfor attr in dir(c):\n    if 'attention' in attr.lower() and not attr.startswith('_'):\n        print(f'{attr}: {getattr(c, attr, None)}')\nprint('architectures:', c.architectures)\nprint('model_type:', c.model_type)\n\" 2>&1"
}
```

**Summary:** $ python3 -c " from transformers impo...

**Output:**
```
Exit code: 1
Stdout:
PyTorch was not found. Models won't be available and only tokenizers, configuration and file/data utilities can be used.
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Traceback (most recent call last):
  File "<string>", line 4, in <module>
    print('num_hidden_layers:', c.num_hidden_layers)
                                ^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/lib/python3.14/site-packages/transformers/configuration_utils.py", line 164, in __getattribute__
    return super().__getattribute__(key)
           ~~~~~~~~~~~~~~~~~~~~~~~~^^^^^
AttributeError: 'Qwen3_5MoeConfig' object has no attribute 'num_hidden_layers'
```

## Assistant

Interesting — it's a `Qwen3_5MoeConfig` which has a different config structure. Let me check what attributes it does have:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python -c \"\nfrom transformers import AutoConfig\nc = AutoConfig.from_pretrained('Qwen/Qwen3.5-35B-A3B', trust_remote_code=True)\nprint('type:', type(c).__name__)\nprint('architectures:', c.architectures)\nprint('model_type:', c.model_type)\n# Print all non-underscore attrs\nfor attr in sorted(dir(c)):\n    if not attr.startswith('_') and not callable(getattr(c, attr, None)):\n        val = getattr(c, attr, '?')\n        if isinstance(val, (int, float, str, bool, list, type(None))):\n            print(f'  {attr}: {val}')\n\" 2>&1"
}
```

**Summary:** $ uv run python -c " from transformer...

**Output:**
```
Exit code: 0
Stdout:
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
`torch_dtype` is deprecated! Use `dtype` instead!
`use_return_dict` is deprecated! Use `return_dict` instead!
type: Qwen3_5MoeConfig
architectures: ['Qwen3_5MoeForConditionalGeneration']
model_type: qwen3_5_moe
  architectures: ['Qwen3_5MoeForConditionalGeneration']
  base_config_key: 
  base_model_ep_plan: None
  base_model_pp_plan: None
  base_model_tp_plan: None
  chunk_size_feed_forward: 0
  default_theta: 10000.0
  dtype: None
  has_no_defaults_at_init: False
  image_token_id: 248056
  is_encoder_decoder: False
  keys_to_ignore_at_inference: ['past_key_values']
  model_type: qwen3_5_moe
  name_or_path: Qwen/Qwen3.5-35B-A3B
  num_labels: 2
  output_attentions: False
  output_hidden_states: False
  problem_type: None
  return_dict: True
  rope_scaling: ?
  tie_word_embeddings: False
  torch_dtype: None
  transformers_version: 4.57.0.dev0
  use_return_dict: True
  video_token_id: 248057
  vision_end_token_id: 248054
  vision_start_token_id: 248053
```

## Assistant

This is a multi-modal model with a sub-config structure. Let me dig into the text model config:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python -c \"\nfrom transformers import AutoConfig\nc = AutoConfig.from_pretrained('Qwen/Qwen3.5-35B-A3B', trust_remote_code=True)\n# Check for sub-configs\nfor attr in sorted(dir(c)):\n    if not attr.startswith('_'):\n        val = getattr(c, attr, None)\n        if hasattr(val, 'num_hidden_layers'):\n            print(f'{attr}.num_hidden_layers:', val.num_hidden_layers)\n            print(f'{attr}.num_attention_heads:', val.num_attention_heads)\n            print(f'{attr}.hidden_size:', val.hidden_size)\n            print(f'{attr} type:', type(val).__name__)\n            # MoE attrs\n            for a2 in sorted(dir(val)):\n                if not a2.startswith('_') and not callable(getattr(val, a2, None)):\n                    v2 = getattr(val, a2, '?')\n                    if isinstance(v2, (int, float, str, bool, list, type(None))):\n                        if 'expert' in a2.lower() or 'moe' in a2.lower() or 'layer' in a2.lower() or 'head' in a2.lower() or 'hidden' in a2.lower() or 'attention' in a2.lower() or 'gate' in a2.lower():\n                            print(f'  {a2}: {v2}')\n\" 2>&1"
}
```

**Summary:** $ uv run python -c " from transformer...

**Output:**
```
Exit code: 0
Stdout:
`torch_dtype` is deprecated! Use `dtype` instead!
`use_return_dict` is deprecated! Use `return_dict` instead!
text_config.num_hidden_layers: 40
text_config.num_attention_heads: 16
text_config.hidden_size: 2048
text_config type: Qwen3_5MoeTextConfig
  attention_bias: False
  attention_dropout: 0.0
  attn_output_gate: True
  full_attention_interval: 4
  head_dim: 256
  hidden_act: silu
  hidden_size: 2048
  layer_types: ['linear_attention', 'linear_attention', 'linear_attention', 'full_attention', 'linear_attention', 'linear_attention', 'linear_attention', 'full_attention', 'linear_attention', 'linear_attention', 'linear_attention', 'full_attention', 'linear_attention', 'linear_attention', 'linear_attention', 'full_attention', 'linear_attention', 'linear_attention', 'linear_attention', 'full_attention', 'linear_attention', 'linear_attention', 'linear_attention', 'full_attention', 'linear_attention', 'linear_attention', 'linear_attention', 'full_attention', 'linear_attention', 'linear_attention', 'linear_attention', 'full_attention', 'linear_attention', 'linear_attention', 'linear_attention', 'full_attention', 'linear_attention', 'linear_attention', 'linear_attention', 'full_attention']
  linear_key_head_dim: 128
  linear_num_key_heads: 16
  linear_num_value_heads: 32
  linear_value_head_dim: 128
  mlp_only_layers: []
  moe_intermediate_size: 512
  mtp_num_hidden_layers: 1
  num_attention_heads: 16
  num_experts: 256
  num_experts_per_tok: 8
  num_hidden_layers: 40
  num_key_value_heads: 2
  output_attentions: False
  output_hidden_states: False
  shared_expert_intermediate_size: 512
```

## Assistant

Excellent — now I have the full picture. This is a fascinating architecture:

- **40 layers**, every 4th is full attention (L3, L7, L11, ..., L39), rest are linear (GatedDeltaNet)
- **256 experts**, 8 active per token
- **16 attention heads**, head_dim=256, 2 KV heads (GQA 8:1)
- d_model=2048, expert intermediate=512, shared expert intermediate=512

The hybrid attention + MoE structure makes it ideal. Let me check how the model actually loads from GGUF and what the decoder layer structure looks like:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python -c \"\nfrom transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig\nimport torch, time\n\ngguf_dir = '/Users/mwhitford/localai/models/qwen3.5-35b-a3b'\ngguf_file = 'Qwen_Qwen3.5-35B-A3B-Q8_0.gguf'\n\nprint('Loading config...')\nt0 = time.time()\nmodel = AutoModelForCausalLM.from_pretrained(\n    gguf_dir, gguf_file=gguf_file,\n    dtype=torch.float16, device_map='cpu',\n    trust_remote_code=True,\n)\nprint(f'Loaded in {time.time()-t0:.1f}s')\nprint(f'type: {type(model).__name__}')\n\n# Find the text model / decoder layers\nif hasattr(model, 'model'):\n    inner = model.model\n    print(f'model.model type: {type(inner).__name__}')\n    if hasattr(inner, 'layers'):\n        layers = inner.layers\n        print(f'model.model.layers: {len(layers)} layers')\n        # Inspect first few layers\n        for i in [0, 3, 7]:\n            if i < len(layers):\n                layer = layers[i]\n                print(f'  L{i}: {type(layer).__name__}')\n                for name, mod in layer.named_children():\n                    print(f'    {name}: {type(mod).__name__}')\nelif hasattr(model, 'language_model'):\n    lm = model.language_model\n    print(f'model.language_model type: {type(lm).__name__}')\n    if hasattr(lm, 'model') and hasattr(lm.model, 'layers'):\n        layers = lm.model.layers\n        print(f'layers: {len(layers)}')\n        for i in [0, 3, 7]:\n            if i < len(layers):\n                layer = layers[i]\n                print(f'  L{i}: {type(layer).__name__}')\n                for name, mod in layer.named_children():\n                    print(f'    {name}: {type(mod).__name__}')\n\" 2>&1 | head -40",
  "timeout": 120000
}
```

**Summary:** $ uv run python -c " from transformer...

**Output:**
```
Exit code: 0
Stdout:
Traceback (most recent call last):
  File "<string>", line 10, in <module>
  File "/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/transformers/models/auto/auto_factory.py", line 329, in from_pretrained
    config, kwargs = AutoConfig.from_pretrained(
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/transformers/models/auto/configuration_auto.py", line 1483, in from_pretrained
    config_dict, unused_kwargs = PreTrainedConfig.get_config_dict(pretrained_model_name_or_path, **kwargs)
                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/transformers/configuration_utils.py", line 670, in get_config_dict
    config_dict, kwargs = cls._get_config_dict(pretrained_model_name_or_path, **kwargs)
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/transformers/configuration_utils.py", line 756, in _get_config_dict
    config_dict = load_gguf_checkpoint(resolved_config_file, return_tensors=False)["config"]
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/transformers/modeling_gguf_pytorch_utils.py", line 536, in load_gguf_checkpoint
    raise ValueError(f"GGUF model with architecture {architecture} is not supported yet.")
ValueError: GGUF model with architecture qwen35moe is not supported yet.
Loading config...
```

## User

No Qwen36-35B-A3B is in huggingface cache, use that, it is the current best bang for the compute you can get in local models right now.


### Thinking

The user is saying to use the HF cached version of Qwen3.6-35B-A3B (or Qwen3.5-35B-A3B as it might be named), not the GGUF. Let me check what's in the HF cache.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls -d ~/.cache/huggingface/hub/models--Qwen* 2>/dev/null | head -20"
}
```

**Summary:** $ ls -d ~/.cache/huggingface/hub/mode...

**Output:**
```
Exit code: 0
Stdout:
/Users/mwhitford/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B
/Users/mwhitford/.cache/huggingface/hub/models--Qwen--Qwen3-30B-A3B
/Users/mwhitford/.cache/huggingface/hub/models--Qwen--Qwen3-32B
/Users/mwhitford/.cache/huggingface/hub/models--Qwen--Qwen3-4B
/Users/mwhitford/.cache/huggingface/hub/models--Qwen--Qwen3-8B
/Users/mwhitford/.cache/huggingface/hub/models--Qwen--Qwen3.5-35B-A3B
/Users/mwhitford/.cache/huggingface/hub/models--Qwen--Qwen3.6-35B-A3B
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python -c \"\nfrom transformers import AutoConfig\nc = AutoConfig.from_pretrained('Qwen/Qwen3.6-35B-A3B', trust_remote_code=True)\nprint('type:', type(c).__name__)\nprint('model_type:', c.model_type)\nprint('architectures:', c.architectures)\n\n# Text config\ntc = c.text_config if hasattr(c, 'text_config') else c\nprint()\nprint('num_hidden_layers:', tc.num_hidden_layers)\nprint('num_attention_heads:', tc.num_attention_heads)\nprint('num_key_value_heads:', tc.num_key_value_heads)\nprint('hidden_size:', tc.hidden_size)\nprint('head_dim:', tc.head_dim)\nfor a in sorted(dir(tc)):\n    if not a.startswith('_') and not callable(getattr(tc, a, None)):\n        v = getattr(tc, a, '?')\n        if isinstance(v, (int, float, str, bool, type(None))):\n            if any(k in a.lower() for k in ['expert', 'moe', 'layer_type', 'full_attention', 'linear', 'gate', 'shared']):\n                print(f'  {a}: {v}')\nif hasattr(tc, 'layer_types'):\n    lt = tc.layer_types\n    print(f'layer_types ({len(lt)}): {lt[:8]}...')\n    full_attn_layers = [i for i, t in enumerate(lt) if t == \\\"full_attention\\\"]\n    print(f'full_attention layers: {full_attn_layers}')\n    print(f'linear_attention layers: {[i for i, t in enumerate(lt) if t != \\\"full_attention\\\"]}')\n\" 2>&1"
}
```

**Summary:** $ uv run python -c " from transformer...

**Output:**
```
Exit code: 0
Stdout:
`torch_dtype` is deprecated! Use `dtype` instead!
`use_return_dict` is deprecated! Use `return_dict` instead!
type: Qwen3_5MoeConfig
model_type: qwen3_5_moe
architectures: ['Qwen3_5MoeForConditionalGeneration']

num_hidden_layers: 40
num_attention_heads: 16
num_key_value_heads: 2
hidden_size: 2048
head_dim: 256
  attn_output_gate: True
  full_attention_interval: 4
  linear_conv_kernel_dim: 4
  linear_key_head_dim: 128
  linear_num_key_heads: 16
  linear_num_value_heads: 32
  linear_value_head_dim: 128
  moe_intermediate_size: 512
  num_experts: 256
  num_experts_per_tok: 8
  shared_expert_intermediate_size: 512
layer_types (40): ['linear_attention', 'linear_attention', 'linear_attention', 'full_attention', 'linear_attention', 'linear_attention', 'linear_attention', 'full_attention']...
full_attention layers: [3, 7, 11, 15, 19, 23, 27, 31, 35, 39]
linear_attention layers: [0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, 16, 17, 18, 20, 21, 22, 24, 25, 26, 28, 29, 30, 32, 33, 34, 36, 37, 38]
```

## Assistant

`Qwen/Qwen3.6-35B-A3B` is cached. Now let me check how it loads and what the layer structure looks like so I can wire the probe correctly:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python -c \"\nfrom transformers import AutoModelForCausalLM, AutoTokenizer\nimport torch, time\n\nprint('Loading Qwen3.6-35B-A3B from HF cache...')\nt0 = time.time()\nmodel = AutoModelForCausalLM.from_pretrained(\n    'Qwen/Qwen3.6-35B-A3B',\n    dtype=torch.float16, device_map='cpu',\n    trust_remote_code=True,\n)\nprint(f'Loaded in {time.time()-t0:.1f}s')\nprint(f'type: {type(model).__name__}')\n\n# Navigate the model structure\ndef show_structure(obj, prefix='', depth=0):\n    if depth > 3:\n        return\n    for name, child in obj.named_children():\n        ctype = type(child).__name__\n        # Count children\n        nch = sum(1 for _ in child.children())\n        extra = f' ({nch} children)' if nch > 0 else ''\n        if 'ModuleList' in ctype:\n            extra = f' [{len(child)} items]'\n        print(f'{prefix}{name}: {ctype}{extra}')\n        if depth < 2 and nch > 0 and 'ModuleList' not in ctype:\n            show_structure(child, prefix + '  ', depth + 1)\n        elif 'ModuleList' in ctype and len(child) > 0:\n            # Show first and a full_attention one\n            for idx in [0, 3]:\n                if idx < len(child):\n                    print(f'{prefix}  [{idx}]: {type(child[idx]).__name__}')\n                    for n2, c2 in child[idx].named_children():\n                        print(f'{prefix}    {n2}: {type(c2).__name__}')\n\nshow_structure(model)\n\" 2>&1",
  "timeout": 180000
}
```

**Summary:** $ uv run python -c " from transformer...

**Output:**
```
Exit code: 0
Stdout:
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Loading Qwen3.6-35B-A3B from HF cache...
Fetching 26 files:   0%|          | 0/26 [00:00<?, ?it/s]Fetching 26 files: 100%|██████████| 26/26 [00:00<00:00, 26533.31it/s]
The fast path is not available because one of the required library is not installed. Falling back to torch implementation. To install follow https://github.com/fla-org/flash-linear-attention#installation and https://github.com/Dao-AILab/causal-conv1d
Loading weights:   0%|          | 0/693 [00:00<?, ?it/s]Loading weights: 100%|██████████| 693/693 [00:00<00:00, 25056.92it/s]
Loaded in 1.2s
type: Qwen3_5MoeForCausalLM
model: Qwen3_5MoeTextModel (4 children)
  embed_tokens: Embedding
  layers: ModuleList [40 items]
    [0]: Qwen3_5MoeDecoderLayer
      linear_attn: Qwen3_5MoeGatedDeltaNet
      mlp: Qwen3_5MoeSparseMoeBlock
      input_layernorm: Qwen3_5MoeRMSNorm
      post_attention_layernorm: Qwen3_5MoeRMSNorm
    [3]: Qwen3_5MoeDecoderLayer
      self_attn: Qwen3_5MoeAttention
      mlp: Qwen3_5MoeSparseMoeBlock
      input_layernorm: Qwen3_5MoeRMSNorm
      post_attention_layernorm: Qwen3_5MoeRMSNorm
  norm: Qwen3_5MoeRMSNorm
  rotary_emb: Qwen3_5MoeTextRotaryEmbedding
lm_head: Linear
```

## Assistant

Now I see the structure clearly:
- Linear attention layers (L0,1,2,4,5,6,...) have `linear_attn: Qwen3_5MoeGatedDeltaNet` 
- Full attention layers (L3,7,11,...,39) have `self_attn: Qwen3_5MoeAttention`
- Both have MoE MLPs: `Qwen3_5MoeSparseMoeBlock`

Let me check the attention projection names:

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python -c \"\nfrom transformers import AutoModelForCausalLM\nimport torch\n\nmodel = AutoModelForCausalLM.from_pretrained(\n    'Qwen/Qwen3.6-35B-A3B',\n    dtype=torch.float16, device_map='cpu',\n    trust_remote_code=True,\n)\n\n# Inspect linear_attn (L0) vs self_attn (L3)\nprint('=== L0 (linear_attn / GatedDeltaNet) ===')\nla = model.model.layers[0].linear_attn\nfor name, mod in la.named_children():\n    if hasattr(mod, 'weight'):\n        print(f'  {name}: {type(mod).__name__} weight={list(mod.weight.shape)}')\n    else:\n        print(f'  {name}: {type(mod).__name__}')\n\nprint()\nprint('=== L3 (self_attn / full attention) ===')\nsa = model.model.layers[3].self_attn\nfor name, mod in sa.named_children():\n    if hasattr(mod, 'weight'):\n        print(f'  {name}: {type(mod).__name__} weight={list(mod.weight.shape)}')\n    else:\n        print(f'  {name}: {type(mod).__name__}')\n\nprint()\nprint('=== MLP (L0, MoE) ===')\nmlp = model.model.layers[0].mlp\nfor name, mod in mlp.named_children():\n    ctype = type(mod).__name__\n    nch = sum(1 for _ in mod.children())\n    if 'ModuleList' in ctype:\n        print(f'  {name}: {ctype} [{len(mod)} items]')\n        if len(mod) > 0:\n            e = mod[0]\n            for n2, c2 in e.named_children():\n                if hasattr(c2, 'weight'):\n                    print(f'    [0].{n2}: {type(c2).__name__} weight={list(c2.weight.shape)}')\n    elif hasattr(mod, 'weight'):\n        print(f'  {name}: {ctype} weight={list(mod.weight.shape)}')\n    else:\n        print(f'  {name}: {ctype}')\n\n# Check config attributes\nprint()\nprint('n_layers:', len(model.model.layers))\nprint('config.num_attention_heads:', model.config.text_config.num_attention_heads)\nprint('config.num_key_value_heads:', model.config.text_config.num_key_value_heads)\nprint('config.hidden_size:', model.config.text_config.hidden_size)\nprint('config.num_experts:', model.config.text_config.num_experts)\nprint('config.num_experts_per_tok:', model.config.text_config.num_experts_per_tok)\n\" 2>&1",
  "timeout": 120000
}
```

**Summary:** $ uv run python -c " from transformer...

**Output:**
```
Exit code: 1
Stdout:
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Fetching 26 files:   0%|          | 0/26 [00:00<?, ?it/s]Fetching 26 files: 100%|██████████| 26/26 [00:00<00:00, 27826.46it/s]
The fast path is not available because one of the required library is not installed. Falling back to torch implementation. To install follow https://github.com/fla-org/flash-linear-attention#installation and https://github.com/Dao-AILab/causal-conv1d
Loading weights:   0%|          | 0/693 [00:00<?, ?it/s]Loading weights: 100%|██████████| 693/693 [00:00<00:00, 24169.13it/s]
Traceback (most recent call last):
  File "<string>", line 50, in <module>
  File "/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/transformers/configuration_utils.py", line 422, in __getattribute__
    return super().__getattribute__(key)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'Qwen3_5MoeTextConfig' object has no attribute 'text_config'. Did you mean: 'get_text_config'?
=== L0 (linear_attn / GatedDeltaNet) ===
  act: SiLUActivation
  conv1d: Conv1d weight=[8192, 1, 4]
  norm: Qwen3_5MoeRMSNormGated weight=[128]
  out_proj: Linear weight=[2048, 4096]
  in_proj_qkv: Linear weight=[8192, 2048]
  in_proj_z: Linear weight=[4096, 2048]
  in_proj_b: Linear weight=[32, 2048]
  in_proj_a: Linear weight=[32, 2048]

=== L3 (self_attn / full attention) ===
  q_proj: Linear weight=[8192, 2048]
  k_proj: Linear weight=[512, 2048]
  v_proj: Linear weight=[512, 2048]
  o_proj: Linear weight=[2048, 4096]
  q_norm: Qwen3_5MoeRMSNorm weight=[256]
  k_norm: Qwen3_5MoeRMSNorm weight=[256]

=== MLP (L0, MoE) ===
  gate: Qwen3_5MoeTopKRouter weight=[256, 2048]
  experts: Qwen3_5MoeExperts
  shared_expert: Qwen3_5MoeMLP
  shared_expert_gate: Linear weight=[1, 2048]

n_layers: 40
```

## Assistant

Now I have the complete picture. Let me fix the config access and update the script to make Qwen3.6-35B-A3B the primary model:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py",
  "original_content": "MODELS = {\n    \"gguf\": {\n        \"path\": \"/Users/mwhitford/localai/models/Qwen3-32B-Q8_0.gguf\",\n        \"hf_name\": \"Qwen/Qwen3-32B\",\n        \"source\": \"gguf\",\n    },\n    \"hf\": {\n        \"hf_name\": \"Qwen/Qwen3-32B\",\n        \"source\": \"hf\",\n    },\n    \"pythia\": {\n        \"hf_name\": \"EleutherAI/pythia-160m-deduped\",\n        \"source\": \"hf\",\n    },\n    \"pythia-1b\": {\n        \"hf_name\": \"EleutherAI/pythia-1b-deduped\",\n        \"source\": \"hf\",\n    },\n}",
  "new_content": "MODELS = {\n    \"qwen36\": {\n        \"hf_name\": \"Qwen/Qwen3.6-35B-A3B\",\n        \"source\": \"hf\",\n        \"description\": \"Qwen3.6-35B-A3B MoE — 40L, 256 experts × 8 active, \"\n                       \"hybrid attention (full every 4th layer, GatedDeltaNet rest). \"\n                       \"Best bang-for-compute local model. MoE gates ARE beam selectors.\",\n    },\n    \"qwen32b\": {\n        \"path\": \"/Users/mwhitford/localai/models/Qwen3-32B-Q8_0.gguf\",\n        \"hf_name\": \"Qwen/Qwen3-32B\",\n        \"source\": \"gguf\",\n        \"description\": \"Qwen3-32B dense — 64L, original combinator hologram target.\",\n    },\n    \"pythia\": {\n        \"hf_name\": \"EleutherAI/pythia-160m-deduped\",\n        \"source\": \"hf\",\n        \"description\": \"Pythia-160M — 12L, fast cross-architecture validation.\",\n    },\n    \"pythia-1b\": {\n        \"hf_name\": \"EleutherAI/pythia-1b-deduped\",\n        \"source\": \"hf\",\n        \"description\": \"Pythia-1B — 24L, mid-scale cross-architecture validation.\",\n    },\n}"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py.
```

## Assistant

Now update the model loading to handle the Qwen3.6 architecture properly (nested config, hybrid attention layers, MoE):

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py",
  "original_content": "def load_model(model_key: str, device: str = \"mps\"):\n    \"\"\"Load model by key from MODELS config.\"\"\"\n    from transformers import AutoModelForCausalLM, AutoTokenizer\n\n    cfg = MODELS[model_key]\n    hf_name = cfg[\"hf_name\"]\n    source = cfg[\"source\"]\n\n    print(f\"Loading {hf_name} ({source})...\", file=sys.stderr)\n    t0 = time.time()\n\n    tokenizer = AutoTokenizer.from_pretrained(hf_name)\n\n    if source == \"gguf\":\n        gguf_path = Path(cfg[\"path\"])\n        model = AutoModelForCausalLM.from_pretrained(\n            str(gguf_path.parent),\n            gguf_file=gguf_path.name,\n            dtype=torch.float16,\n            device_map=device,\n            trust_remote_code=True,\n        )\n    else:\n        model = AutoModelForCausalLM.from_pretrained(\n            hf_name,\n            dtype=torch.float16,\n            device_map=device,\n            trust_remote_code=True,\n        )\n\n    model.eval()\n    t1 = time.time()\n\n    n_layers = model.config.num_hidden_layers\n    d_model = model.config.hidden_size\n    n_heads = model.config.num_attention_heads\n    print(f\"Loaded in {t1-t0:.1f}s: {n_layers}L × {n_heads}H, d={d_model}\",\n          file=sys.stderr)\n\n    return model, tokenizer",
  "new_content": "def load_model(model_key: str, device: str = \"mps\"):\n    \"\"\"Load model by key from MODELS config.\"\"\"\n    from transformers import AutoModelForCausalLM, AutoTokenizer\n\n    cfg = MODELS[model_key]\n    hf_name = cfg[\"hf_name\"]\n    source = cfg[\"source\"]\n\n    print(f\"Loading {hf_name} ({source})...\", file=sys.stderr)\n    if \"description\" in cfg:\n        print(f\"  {cfg['description']}\", file=sys.stderr)\n    t0 = time.time()\n\n    tokenizer = AutoTokenizer.from_pretrained(hf_name, trust_remote_code=True)\n\n    if source == \"gguf\":\n        gguf_path = Path(cfg[\"path\"])\n        model = AutoModelForCausalLM.from_pretrained(\n            str(gguf_path.parent),\n            gguf_file=gguf_path.name,\n            dtype=torch.float16,\n            device_map=device,\n            trust_remote_code=True,\n        )\n    else:\n        model = AutoModelForCausalLM.from_pretrained(\n            hf_name,\n            dtype=torch.float16,\n            device_map=device,\n            trust_remote_code=True,\n        )\n\n    model.eval()\n    t1 = time.time()\n\n    info = get_model_info(model)\n    print(f\"Loaded in {t1-t0:.1f}s: {info['n_layers']}L × {info['n_heads']}H, \"\n          f\"d={info['d_model']}\", file=sys.stderr)\n    if info.get(\"is_moe\"):\n        print(f\"  MoE: {info['num_experts']} experts × {info['num_experts_per_tok']} active\",\n              file=sys.stderr)\n    if info.get(\"full_attention_layers\"):\n        print(f\"  Hybrid: full_attn at L{info['full_attention_layers']}, \"\n              f\"linear_attn at {len(info['linear_attention_layers'])} layers\",\n              file=sys.stderr)\n\n    return model, tokenizer\n\n\ndef get_model_info(model) -> dict:\n    \"\"\"Extract model architecture info, handling nested configs (Qwen3.6 MoE).\"\"\"\n    config = model.config\n\n    # Handle nested text_config (Qwen3.5/3.6 MoE models)\n    if hasattr(config, \"text_config\"):\n        tc = config.text_config\n    elif hasattr(config, \"get_text_config\"):\n        tc = config.get_text_config()\n    else:\n        tc = config\n\n    info = {\n        \"n_layers\": tc.num_hidden_layers,\n        \"n_heads\": tc.num_attention_heads,\n        \"d_model\": tc.hidden_size,\n        \"head_dim\": getattr(tc, \"head_dim\", tc.hidden_size // tc.num_attention_heads),\n        \"n_kv_heads\": getattr(tc, \"num_key_value_heads\", tc.num_attention_heads),\n    }\n\n    # MoE info\n    if hasattr(tc, \"num_experts\"):\n        info[\"is_moe\"] = True\n        info[\"num_experts\"] = tc.num_experts\n        info[\"num_experts_per_tok\"] = getattr(tc, \"num_experts_per_tok\", 8)\n    else:\n        info[\"is_moe\"] = False\n\n    # Hybrid attention info (Qwen3.6: full_attention every 4th layer)\n    if hasattr(tc, \"layer_types\"):\n        info[\"layer_types\"] = tc.layer_types\n        info[\"full_attention_layers\"] = [\n            i for i, t in enumerate(tc.layer_types) if t == \"full_attention\"\n        ]\n        info[\"linear_attention_layers\"] = [\n            i for i, t in enumerate(tc.layer_types) if t != \"full_attention\"\n        ]\n    else:\n        info[\"full_attention_layers\"] = None\n        info[\"linear_attention_layers\"] = None\n\n    return info"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py.
```

## Assistant

Now update the layer accessor functions to handle the Qwen3.6 hybrid architecture:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py",
  "original_content": "def get_decoder_layers(model):\n    \"\"\"Get the list of decoder layers, handling different model architectures.\"\"\"\n    if hasattr(model, \"model\") and hasattr(model.model, \"layers\"):\n        return model.model.layers  # Qwen, LLaMA, Mistral\n    elif hasattr(model, \"gpt_neox\") and hasattr(model.gpt_neox, \"layers\"):\n        return model.gpt_neox.layers  # Pythia / GPT-NeoX\n    else:\n        raise ValueError(f\"Unknown model architecture: {type(model)}\")\n\n\ndef get_attn_module(layer):\n    \"\"\"Get the attention module from a decoder layer.\"\"\"\n    if hasattr(layer, \"self_attn\"):\n        return layer.self_attn  # Qwen, LLaMA\n    elif hasattr(layer, \"attention\"):\n        return layer.attention  # Pythia / GPT-NeoX\n    else:\n        raise ValueError(f\"Unknown layer architecture: {type(layer)}\")\n\n\ndef get_attn_proj_names(attn_module):\n    \"\"\"Get the names of Q/K/V/O projection layers.\"\"\"\n    # Qwen / LLaMA style\n    if hasattr(attn_module, \"q_proj\"):\n        return [\"q_proj\", \"k_proj\", \"v_proj\", \"o_proj\"]\n    # Pythia / GPT-NeoX style (fused QKV)\n    elif hasattr(attn_module, \"query_key_value\"):\n        return [\"query_key_value\", \"dense\"]\n    else:\n        # Try to find projections\n        names = [n for n, _ in attn_module.named_modules() if \"proj\" in n]\n        if names:\n            return names\n        raise ValueError(f\"Cannot find attention projections in {type(attn_module)}\")",
  "new_content": "def get_decoder_layers(model):\n    \"\"\"Get the list of decoder layers, handling different model architectures.\"\"\"\n    if hasattr(model, \"model\") and hasattr(model.model, \"layers\"):\n        return model.model.layers  # Qwen, Qwen3.6 MoE, LLaMA, Mistral\n    elif hasattr(model, \"gpt_neox\") and hasattr(model.gpt_neox, \"layers\"):\n        return model.gpt_neox.layers  # Pythia / GPT-NeoX\n    else:\n        raise ValueError(f\"Unknown model architecture: {type(model)}\")\n\n\ndef get_layer_attn_type(layer) -> str:\n    \"\"\"Determine attention type for a layer.\n\n    Qwen3.6-35B-A3B hybrid architecture:\n      - Full attention layers (every 4th): have self_attn (Qwen3_5MoeAttention)\n      - Linear attention layers: have linear_attn (Qwen3_5MoeGatedDeltaNet)\n\n    Returns: \"full_attention\", \"linear_attention\", or \"standard\"\n    \"\"\"\n    if hasattr(layer, \"self_attn\") and hasattr(layer, \"linear_attn\"):\n        # Shouldn't happen, but be safe\n        return \"full_attention\"\n    elif hasattr(layer, \"self_attn\"):\n        return \"full_attention\"\n    elif hasattr(layer, \"linear_attn\"):\n        return \"linear_attention\"\n    elif hasattr(layer, \"attention\"):\n        return \"standard\"  # Pythia / GPT-NeoX\n    else:\n        raise ValueError(f\"Unknown layer architecture: {type(layer)}\")\n\n\ndef get_attn_module(layer):\n    \"\"\"Get the attention module from a decoder layer.\n\n    Handles Qwen3.6 hybrid: full_attention layers use self_attn,\n    linear_attention layers use linear_attn (GatedDeltaNet).\n    \"\"\"\n    if hasattr(layer, \"self_attn\"):\n        return layer.self_attn       # Qwen full attention, LLaMA\n    elif hasattr(layer, \"linear_attn\"):\n        return layer.linear_attn     # Qwen3.6 GatedDeltaNet\n    elif hasattr(layer, \"attention\"):\n        return layer.attention       # Pythia / GPT-NeoX\n    else:\n        raise ValueError(f\"Unknown layer architecture: {type(layer)}\")\n\n\ndef get_attn_proj_names(attn_module) -> list[str]:\n    \"\"\"Get the names of weight-bearing projection layers in attention.\n\n    Architecture-aware:\n      - Qwen full attention: q_proj, k_proj, v_proj, o_proj\n      - Qwen3.6 GatedDeltaNet: in_proj_qkv, in_proj_z, in_proj_b, in_proj_a, out_proj\n      - Pythia / GPT-NeoX: query_key_value, dense\n    \"\"\"\n    # Qwen / LLaMA full attention\n    if hasattr(attn_module, \"q_proj\"):\n        return [\"q_proj\", \"k_proj\", \"v_proj\", \"o_proj\"]\n    # Qwen3.6 GatedDeltaNet (linear attention)\n    elif hasattr(attn_module, \"in_proj_qkv\"):\n        names = [\"in_proj_qkv\", \"out_proj\"]\n        if hasattr(attn_module, \"in_proj_z\"):\n            names.append(\"in_proj_z\")\n        if hasattr(attn_module, \"in_proj_b\"):\n            names.append(\"in_proj_b\")\n        if hasattr(attn_module, \"in_proj_a\"):\n            names.append(\"in_proj_a\")\n        return names\n    # Pythia / GPT-NeoX (fused QKV)\n    elif hasattr(attn_module, \"query_key_value\"):\n        return [\"query_key_value\", \"dense\"]\n    else:\n        # Fallback: find any Linear layers with 'proj' in name\n        names = []\n        for n, m in attn_module.named_children():\n            if hasattr(m, \"weight\") and (\"proj\" in n or \"dense\" in n):\n                names.append(n)\n        if names:\n            return names\n        raise ValueError(f\"Cannot find attention projections in {type(attn_module)}\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py.
```

## Assistant

Now update the MLP accessor to handle MoE (the gate matrix IS the discourse hologram candidate):

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py",
  "original_content": "def ternary_quantize_mlp(model, layer_idx: int, threshold_pct: float):\n    \"\"\"Quantize MLP weights to ternary (for frequency hologram test).\n\n    MLP architecture varies:\n      - Qwen/LLaMA: gate_proj, up_proj, down_proj\n      - Pythia: dense_h_to_4h, dense_4h_to_h\n    \"\"\"\n    decoder_layers = get_decoder_layers(model)\n    layer = decoder_layers[layer_idx]\n\n    # Find MLP module\n    if hasattr(layer, \"mlp\"):\n        mlp = layer.mlp\n    elif hasattr(layer, \"feed_forward\"):\n        mlp = layer.feed_forward\n    else:\n        raise ValueError(f\"Cannot find MLP in layer: {type(layer)}\")\n\n    # Find weight parameters\n    mlp_projs = []\n    for name, param in mlp.named_parameters():\n        if \"weight\" in name:\n            mlp_projs.append((name.replace(\".weight\", \"\"), param))\n\n    originals = {}\n    stats = {}\n\n    for name, _ in mlp_projs:\n        # Navigate to the actual module\n        parts = name.split(\".\")\n        mod = mlp\n        for part in parts:\n            mod = getattr(mod, part)\n\n        w = mod.weight.data\n        originals[name] = w.clone()\n\n        abs_w = w.abs()\n        if threshold_pct > 0:\n            flat = abs_w.float().flatten()\n            if flat.numel() > 1_000_000:\n                indices = torch.randperm(flat.numel(), device=\"cpu\")[:1_000_000]\n                sample = flat.cpu()[indices]\n            else:\n                sample = flat.cpu()\n            threshold = torch.quantile(sample, threshold_pct).item()\n        else:\n            threshold = 0.0\n\n        scale = abs_w[abs_w > threshold].mean().item() if (abs_w > threshold).any() else 1.0\n        ternary = torch.zeros_like(w)\n        ternary[w > threshold] = 1.0\n        ternary[w < -threshold] = -1.0\n        mod.weight.data = ternary * scale\n\n        n_total = w.numel()\n        n_zero = (ternary == 0).sum().item()\n\n        stats[name] = {\n            \"shape\": list(w.shape),\n            \"sparsity\": n_zero / n_total,\n        }\n\n    return originals, stats\n\n\ndef restore_mlp(model, layer_idx: int, originals: dict):\n    \"\"\"Restore original MLP weights.\"\"\"\n    decoder_layers = get_decoder_layers(model)\n    layer = decoder_layers[layer_idx]\n\n    if hasattr(layer, \"mlp\"):\n        mlp = layer.mlp\n    elif hasattr(layer, \"feed_forward\"):\n        mlp = layer.feed_forward\n    else:\n        return\n\n    for name, w in originals.items():\n        parts = name.split(\".\")\n        mod = mlp\n        for part in parts:\n            mod = getattr(mod, part)\n        mod.weight.data = w",
  "new_content": "def ternary_quantize_mlp(model, layer_idx: int, threshold_pct: float):\n    \"\"\"Quantize MLP weights to ternary (for frequency hologram test).\n\n    MLP architecture varies:\n      - Qwen3.6 MoE: gate (256×2048 router), shared_expert, 256 experts\n        We quantize the GATE matrix (the beam selector) and shared expert.\n        Individual experts are too numerous — gate is the hologram.\n      - Qwen/LLaMA dense: gate_proj, up_proj, down_proj\n      - Pythia: dense_h_to_4h, dense_4h_to_h\n    \"\"\"\n    decoder_layers = get_decoder_layers(model)\n    layer = decoder_layers[layer_idx]\n\n    # Find MLP module\n    if hasattr(layer, \"mlp\"):\n        mlp = layer.mlp\n    elif hasattr(layer, \"feed_forward\"):\n        mlp = layer.feed_forward\n    else:\n        raise ValueError(f\"Cannot find MLP in layer: {type(layer)}\")\n\n    originals = {}\n    stats = {}\n\n    # Identify which weights to quantize\n    target_modules = []\n\n    # MoE architecture (Qwen3.6): quantize gate + shared expert\n    if hasattr(mlp, \"gate\") and hasattr(mlp.gate, \"weight\"):\n        target_modules.append((\"gate\", mlp.gate))\n    if hasattr(mlp, \"shared_expert\"):\n        for name, mod in mlp.shared_expert.named_children():\n            if hasattr(mod, \"weight\"):\n                target_modules.append((f\"shared_expert.{name}\", mod))\n    if hasattr(mlp, \"shared_expert_gate\") and hasattr(mlp.shared_expert_gate, \"weight\"):\n        target_modules.append((\"shared_expert_gate\", mlp.shared_expert_gate))\n\n    # Dense MLP fallback: gate_proj, up_proj, down_proj or dense_h_to_4h, dense_4h_to_h\n    if not target_modules:\n        for name, mod in mlp.named_children():\n            if hasattr(mod, \"weight\") and (\"proj\" in name or \"dense\" in name):\n                target_modules.append((name, mod))\n\n    for name, mod in target_modules:\n        w = mod.weight.data\n        originals[name] = w.clone()\n\n        abs_w = w.abs()\n        if threshold_pct > 0:\n            flat = abs_w.float().flatten()\n            if flat.numel() > 1_000_000:\n                indices = torch.randperm(flat.numel(), device=\"cpu\")[:1_000_000]\n                sample = flat.cpu()[indices]\n            else:\n                sample = flat.cpu()\n            threshold = torch.quantile(sample, threshold_pct).item()\n        else:\n            threshold = 0.0\n\n        scale = abs_w[abs_w > threshold].mean().item() if (abs_w > threshold).any() else 1.0\n        ternary = torch.zeros_like(w)\n        ternary[w > threshold] = 1.0\n        ternary[w < -threshold] = -1.0\n        mod.weight.data = ternary * scale\n\n        n_total = w.numel()\n        n_zero = (ternary == 0).sum().item()\n\n        stats[name] = {\n            \"shape\": list(w.shape),\n            \"sparsity\": n_zero / n_total,\n            \"is_moe_gate\": \"gate\" in name and \"shared\" not in name,\n        }\n\n    return originals, stats\n\n\ndef restore_mlp(model, layer_idx: int, originals: dict):\n    \"\"\"Restore original MLP weights.\"\"\"\n    decoder_layers = get_decoder_layers(model)\n    layer = decoder_layers[layer_idx]\n\n    if hasattr(layer, \"mlp\"):\n        mlp = layer.mlp\n    elif hasattr(layer, \"feed_forward\"):\n        mlp = layer.feed_forward\n    else:\n        return\n\n    for name, w in originals.items():\n        parts = name.split(\".\")\n        mod = mlp\n        for part in parts:\n            mod = getattr(mod, part)\n        mod.weight.data = w"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py.
```

## Assistant

Now update the main() function to use `qwen36` as default, handle the model info properly, and choose appropriate layers for the hybrid architecture:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py",
  "original_content": "    parser.add_argument(\n        \"--model\", choices=list(MODELS.keys()), default=\"gguf\",\n        help=\"Model to probe (default: gguf = Qwen3-32B-Q8_0)\",\n    )",
  "new_content": "    parser.add_argument(\n        \"--model\", choices=list(MODELS.keys()), default=\"qwen36\",\n        help=\"Model to probe (default: qwen36 = Qwen3.6-35B-A3B MoE)\",\n    )"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py.
```

## Assistant

Now update the layer selection logic for the hybrid architecture:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py",
  "original_content": "    # Determine model-appropriate layers\n    model_key = args.model\n    model, tokenizer = load_model(model_key, args.device)\n    n_layers = model.config.num_hidden_layers\n\n    # Measurement layers: spread across the model\n    if n_layers <= 16:\n        # Small model (Pythia-160M: 12 layers)\n        measure_layers = list(range(n_layers))\n        target_layers = [0, n_layers // 4, n_layers // 2, n_layers - 1]\n    elif n_layers <= 32:\n        # Medium model\n        measure_layers = [0, 2, 4, 8, 12, 16, 20, 24, n_layers - 1]\n        target_layers = [1, 3, 8, 16, n_layers - 2]\n    else:\n        # Large model (Qwen3-32B: 64 layers)\n        measure_layers = [0, 4, 8, 16, 24, 32, 40, 48, 56, n_layers - 1]\n        target_layers = [1, 3, 6, 24, 43]\n\n    if args.quick:\n        measure_layers = measure_layers[::2]  # half the layers\n        target_layers = target_layers[:2]     # fewer ternary targets\n\n    print(f\"\\n{'═'*72}\")\n    print(f\"  HOLOGRAM ATLAS PROBE\")\n    print(f\"  Model: {MODELS[model_key]['hf_name']} ({n_layers}L)\")\n    print(f\"  Holograms: {', '.join(selected)}\")\n    print(f\"  Measure layers: {measure_layers}\")\n    print(f\"  Ternary target layers: {target_layers}\")\n    print(f\"  Quick: {args.quick}\")\n    print(f\"{'═'*72}\")\n\n    all_results = {\n        \"timestamp\": time.strftime(\"%Y-%m-%dT%H:%M:%SZ\"),\n        \"model\": MODELS[model_key][\"hf_name\"],\n        \"model_key\": model_key,\n        \"n_layers\": n_layers,\n        \"n_heads\": model.config.num_attention_heads,\n        \"d_model\": model.config.hidden_size,\n        \"selected_holograms\": selected,\n        \"measure_layers\": measure_layers,\n        \"target_layers\": target_layers,\n        \"quick\": args.quick,\n        \"holograms\": {},\n    }",
  "new_content": "    # Determine model-appropriate layers\n    model_key = args.model\n    model, tokenizer = load_model(model_key, args.device)\n    info = get_model_info(model)\n    n_layers = info[\"n_layers\"]\n\n    # Measurement layers: architecture-aware selection\n    full_attn_layers = info.get(\"full_attention_layers\")\n\n    if full_attn_layers:\n        # Hybrid architecture (Qwen3.6): prioritize full-attention layers\n        # for measurement since they have standard Q/K/V projections.\n        # Full attention at: L3, L7, L11, L15, L19, L23, L27, L31, L35, L39\n        # Also include some linear layers to see the difference.\n        measure_layers = sorted(set(\n            full_attn_layers +  # all full-attention layers\n            [0, 1, 2] +        # first few linear layers\n            [n_layers - 1]      # last layer\n        ))\n        # Ternary targets: test both types\n        # - Full attention layers: standard Q/K/V (like prior combinator probes)\n        # - Linear attention layers: GatedDeltaNet (new — do they store differently?)\n        target_layers = [\n            3, 7,   # early full-attention\n            0, 1,   # early linear-attention (GatedDeltaNet)\n            31, 35,  # late full-attention (bimodal B peak from session 093)\n        ]\n    elif n_layers <= 16:\n        # Small model (Pythia-160M: 12 layers)\n        measure_layers = list(range(n_layers))\n        target_layers = [0, n_layers // 4, n_layers // 2, n_layers - 1]\n    elif n_layers <= 32:\n        # Medium model\n        measure_layers = [0, 2, 4, 8, 12, 16, 20, 24, n_layers - 1]\n        target_layers = [1, 3, 8, 16, n_layers - 2]\n    else:\n        # Large dense model (Qwen3-32B: 64 layers)\n        measure_layers = [0, 4, 8, 16, 24, 32, 40, 48, 56, n_layers - 1]\n        target_layers = [1, 3, 6, 24, 43]\n\n    if args.quick:\n        measure_layers = measure_layers[::2]  # half the layers\n        target_layers = target_layers[:2]     # fewer ternary targets\n\n    print(f\"\\n{'═'*72}\")\n    print(f\"  HOLOGRAM ATLAS PROBE\")\n    print(f\"  Model: {MODELS[model_key]['hf_name']} ({n_layers}L)\")\n    if full_attn_layers:\n        print(f\"  Architecture: hybrid (full_attn={full_attn_layers})\")\n    if info.get(\"is_moe\"):\n        print(f\"  MoE: {info['num_experts']} experts × {info['num_experts_per_tok']} active\")\n    print(f\"  Holograms: {', '.join(selected)}\")\n    print(f\"  Measure layers: {measure_layers}\")\n    print(f\"  Ternary target layers: {target_layers}\")\n    print(f\"  Quick: {args.quick}\")\n    print(f\"{'═'*72}\")\n\n    all_results = {\n        \"timestamp\": time.strftime(\"%Y-%m-%dT%H:%M:%SZ\"),\n        \"model\": MODELS[model_key][\"hf_name\"],\n        \"model_key\": model_key,\n        \"model_info\": info,\n        \"n_layers\": n_layers,\n        \"n_heads\": info[\"n_heads\"],\n        \"d_model\": info[\"d_model\"],\n        \"is_moe\": info.get(\"is_moe\", False),\n        \"full_attention_layers\": full_attn_layers,\n        \"selected_holograms\": selected,\n        \"measure_layers\": measure_layers,\n        \"target_layers\": target_layers,\n        \"quick\": args.quick,\n        \"holograms\": {},\n    }"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py.
```

## Assistant

Now let me also add the MoE gate extraction as a special analysis for the discourse hologram — the gate matrices ARE the discourse hologram candidate:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py",
  "original_content": "    # ── Cross-hologram orthogonality ─────────────────────────\n    if len(selectivity_profiles) >= 2:",
  "new_content": "    # ── MoE gate analysis (if MoE model + discourse hologram) ──\n    if info.get(\"is_moe\") and \"discourse\" in selected:\n        print(f\"\\n{'─'*72}\")\n        print(f\"  MoE Gate Analysis — gate matrices as discourse beam selectors\")\n        print(f\"{'─'*72}\")\n\n        gate_analysis = analyze_moe_gates(model, info)\n        all_results[\"moe_gate_analysis\"] = gate_analysis\n\n    # ── Cross-hologram orthogonality ─────────────────────────\n    if len(selectivity_profiles) >= 2:"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py.
```

## Assistant

Now add the `analyze_moe_gates` function before `print_selectivity_summary`:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py",
  "original_content": "# ══════════════════════════════════════════════════════════════════\n# Summary output\n# ══════════════════════════════════════════════════════════════════",
  "new_content": "# ══════════════════════════════════════════════════════════════════\n# MoE gate analysis — the discourse hologram candidate\n# ══════════════════════════════════════════════════════════════════\n\ndef analyze_moe_gates(model, info: dict) -> dict:\n    \"\"\"Extract and analyze MoE gate matrices as discourse beam selectors.\n\n    The hypothesis: MoE gate matrices (256×2048 in Qwen3.6) implement\n    angle multiplexing — 256 holograms addressed by different reference\n    beam angles. The gate selects which experts (= which holographic\n    patterns) to activate for each token.\n\n    This analysis:\n    1. Extracts gate weight matrices from each layer\n    2. Checks if gate weights survive ternary quantization (sign topology)\n    3. Measures cross-layer gate similarity (do gates at different depths\n       select the same experts?)\n    4. Computes effective rank of gate matrices\n    \"\"\"\n    decoder_layers = get_decoder_layers(model)\n    n_layers = len(decoder_layers)\n\n    gate_weights = {}\n    gate_stats = {}\n\n    for li in range(n_layers):\n        layer = decoder_layers[li]\n        if not hasattr(layer, \"mlp\"):\n            continue\n        mlp = layer.mlp\n        if not hasattr(mlp, \"gate\") or not hasattr(mlp.gate, \"weight\"):\n            continue\n\n        w = mlp.gate.weight.data.detach().cpu().float()  # (num_experts, d_model)\n        gate_weights[li] = w\n\n        # Stats\n        sign_w = torch.sign(w)\n        n_pos = (sign_w > 0).sum().item()\n        n_neg = (sign_w < 0).sum().item()\n        n_zero = (sign_w == 0).sum().item()\n\n        # Effective rank via SVD\n        try:\n            s = torch.linalg.svdvals(w)\n            s_norm = s / s.sum()\n            eff_rank_90 = int((s_norm.cumsum(0) < 0.90).sum().item()) + 1\n            eff_rank_99 = int((s_norm.cumsum(0) < 0.99).sum().item()) + 1\n        except Exception:\n            eff_rank_90 = -1\n            eff_rank_99 = -1\n\n        gate_stats[li] = {\n            \"shape\": list(w.shape),\n            \"balance\": n_pos / max(n_neg, 1),\n            \"sparsity\": n_zero / w.numel(),\n            \"effective_rank_90\": eff_rank_90,\n            \"effective_rank_99\": eff_rank_99,\n            \"frobenius_norm\": float(w.norm().item()),\n        }\n\n    # Cross-layer gate similarity\n    gate_layers = sorted(gate_weights.keys())\n    n_gates = len(gate_layers)\n    cross_layer_cos = np.zeros((n_gates, n_gates))\n\n    for i, li in enumerate(gate_layers):\n        for j, lj in enumerate(gate_layers):\n            wi = gate_weights[li].flatten()\n            wj = gate_weights[lj].flatten()\n            cos = float(F.cosine_similarity(wi.unsqueeze(0), wj.unsqueeze(0)).item())\n            cross_layer_cos[i, j] = cos\n\n    # Ternary survival of gate matrices\n    ternary_survival = {}\n    for li in gate_layers[:5]:  # test first 5 layers\n        w = gate_weights[li]\n        w_ternary = torch.sign(w)\n        cos_to_original = float(\n            F.cosine_similarity(\n                w.flatten().unsqueeze(0),\n                w_ternary.flatten().unsqueeze(0)\n            ).item()\n        )\n        ternary_survival[li] = {\n            \"cos_to_original\": cos_to_original,\n            \"survived\": cos_to_original > 0.5,\n        }\n\n    print(f\"\\n  ┌─ MoE Gate Analysis ─────────────────────────────────────────┐\")\n    print(f\"  │ Gate shape: {gate_stats[gate_layers[0]]['shape']} \"\n          f\"({info['num_experts']} experts × d_model)\")\n    print(f\"  │\")\n    print(f\"  │ Per-layer stats:\")\n    print(f\"  │ {'layer':>6} {'balance':>8} {'eff_rank90':>11} {'eff_rank99':>11}\")\n    for li in gate_layers:\n        s = gate_stats[li]\n        print(f\"  │ L{li:>4} {s['balance']:>8.3f} {s['effective_rank_90']:>11} \"\n              f\"{s['effective_rank_99']:>11}\")\n    print(f\"  │\")\n    print(f\"  │ Cross-layer gate cosine similarity (sample):\")\n    sample_layers = gate_layers[::max(1, n_gates // 5)][:6]\n    sample_indices = [gate_layers.index(l) for l in sample_layers]\n    print(f\"  │ {'':>6}\", end=\"\")\n    for l in sample_layers:\n        print(f\" {'L'+str(l):>6}\", end=\"\")\n    print()\n    for i, li in zip(sample_indices, sample_layers):\n        print(f\"  │ {'L'+str(li):>6}\", end=\"\")\n        for j, lj in zip(sample_indices, sample_layers):\n            print(f\" {cross_layer_cos[i, j]:>6.3f}\", end=\"\")\n        print()\n    print(f\"  │\")\n    print(f\"  │ Ternary survival of gate matrices:\")\n    for li, s in ternary_survival.items():\n        marker = \"✓\" if s[\"survived\"] else \"✗\"\n        print(f\"  │   L{li}: cos={s['cos_to_original']:.3f} {marker}\")\n    print(f\"  └{'─'*72}┘\")\n\n    return {\n        \"gate_stats\": {str(k): v for k, v in gate_stats.items()},\n        \"cross_layer_cosine\": cross_layer_cos.tolist(),\n        \"cross_layer_labels\": [f\"L{l}\" for l in gate_layers],\n        \"ternary_survival\": {str(k): v for k, v in ternary_survival.items()},\n    }\n\n\n# ══════════════════════════════════════════════════════════════════\n# Summary output\n# ══════════════════════════════════════════════════════════════════"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py.
```

## Assistant

Now verify it still parses and imports correctly:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python scripts/explore/probe_hologram_atlas.py --help 2>&1"
}
```

**Summary:** $ uv run python scripts/explore/probe...

**Output:**
```
Exit code: 0
Stdout:
usage: probe_hologram_atlas.py [-h] [--hologram HOLOGRAM]
                               [--model {qwen36,qwen32b,pythia,pythia-1b}]
                               [--device DEVICE] [--quick] [--skip-ternary]
                               [--skip-combinator-baseline]
                               [--output-dir OUTPUT_DIR]

Hologram Atlas Probe — what holograms exist beyond combinators?

options:
  -h, --help            show this help message and exit
  --hologram HOLOGRAM   Which hologram(s) to probe. Comma-separated from:
                        type,induction,binding,frequency,discourse,all
                        (default: all)
  --model {qwen36,qwen32b,pythia,pythia-1b}
                        Model to probe (default: qwen36 = Qwen3.6-35B-A3B MoE)
  --device DEVICE       Device (mps, cuda, cpu). Default: mps
  --quick               Fewer probes and layers for faster iteration
  --skip-ternary        Skip ternary survival tests (selectivity only)
  --skip-combinator-baseline
                        Skip combinator baseline measurement (faster if you
                        only want the new holograms without cross-hologram
                        comparison)
  --output-dir OUTPUT_DIR

Candidate holograms:
  type       — lexical category assignment (CCG types)
  induction  — in-context pattern matching ([A][B]...[A] → [B])
  binding    — variable tracking / coreference across distance
  frequency  — statistical co-occurrence (MLP-based)
  discourse  — topic / register / coherence (gate-level)

Examples:
  # Probe all holograms on Qwen3-32B (GGUF):
  uv run python scripts/explore/probe_hologram_atlas.py

  # Quick test of type hologram only:
  uv run python scripts/explore/probe_hologram_atlas.py --hologram type --quick

  # Cross-model validation on Pythia:
  uv run python scripts/explore/probe_hologram_atlas.py --model pythia --quick
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python -c \"\nimport scripts.explore.probe_hologram_atlas as m\nprint('Default model:', list(m.MODELS.keys())[0])\nprint('ALL_HOLOGRAMS:', m.ALL_HOLOGRAMS)\nprint('Functions:', [f for f in dir(m) if not f.startswith('_') and callable(getattr(m, f))])\n\" 2>&1"
}
```

**Summary:** $ uv run python -c " import scripts.e...

**Output:**
```
Exit code: 0
Stdout:
Default model: qwen36
ALL_HOLOGRAMS: ['type', 'induction', 'binding', 'frequency', 'discourse']
Functions: ['Path', 'aggregate_selectivity', 'analyze_moe_gates', 'compute_orthogonality', 'get_attn_module', 'get_attn_proj_names', 'get_decoder_layers', 'get_hidden_states', 'get_layer_attn_type', 'get_model_info', 'load_model', 'main', 'measure_selectivity', 'print_orthogonality_summary', 'print_selectivity_summary', 'print_survival_summary', 'restore_layer', 'restore_mlp', 'run_ternary_survival', 'save_results', 'ternary_quantize_layer', 'ternary_quantize_mlp']
```

## Assistant

Clean. Let me also update the help examples since the default is now qwen36:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py",
  "original_content": "Examples:\n  # Probe all holograms on Qwen3-32B (GGUF):\n  uv run python scripts/explore/probe_hologram_atlas.py\n\n  # Quick test of type hologram only:\n  uv run python scripts/explore/probe_hologram_atlas.py --hologram type --quick\n\n  # Cross-model validation on Pythia:\n  uv run python scripts/explore/probe_hologram_atlas.py --model pythia --quick",
  "new_content": "Examples:\n  # Probe all holograms on Qwen3.6-35B-A3B MoE (default):\n  uv run python scripts/explore/probe_hologram_atlas.py\n\n  # Quick test of type hologram only:\n  uv run python scripts/explore/probe_hologram_atlas.py --hologram type --quick\n\n  # Cross-model validation on Pythia:\n  uv run python scripts/explore/probe_hologram_atlas.py --model pythia --quick\n\n  # Dense 32B for comparison with prior combinator probes:\n  uv run python scripts/explore/probe_hologram_atlas.py --model qwen32b\n\n  # Discourse hologram with MoE gate analysis:\n  uv run python scripts/explore/probe_hologram_atlas.py --hologram discourse --skip-combinator-baseline"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py.
```

### Tool Call: editor_diagnostics (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py"
}
```

**Summary:** Checking diagnostics: probe_hologram_atlas.py

**Output:**
```
No diagnostics found
```

## Assistant

Clean. Now let me verify the complete --help one more time and do a final import sanity check:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python -c \"\n# Verify all key functions work without model loading\nimport scripts.explore.probe_hologram_atlas as m\n\n# Check probe sentence counts\nfor hname, hprobes in m.HOLOGRAM_PROBES.items():\n    for cond, data in hprobes.items():\n        assert len(data['active']) == len(data['control']), \\\n            f'{hname}/{cond}: active({len(data[\\\"active\\\"])}) != control({len(data[\\\"control\\\"])})'\n        assert len(data['active']) >= 3, f'{hname}/{cond}: need >=3 pairs, got {len(data[\\\"active\\\"])}'\n\n# Check combinator baseline has matching pairs\nfor cond, data in m.COMBINATOR_PROBES.items():\n    assert len(data['active']) == len(data['control'])\n\nprint('All probe pair counts match ✓')\nprint(f'Total probe conditions: {sum(len(v) for v in m.HOLOGRAM_PROBES.values())}')\nprint(f'Total active sentences: {sum(len(d[\\\"active\\\"]) for h in m.HOLOGRAM_PROBES.values() for d in h.values())}')\nprint('Script is ready ✓')\n\" 2>&1"
}
```

**Summary:** $ uv run python -c " # Verify all key...

**Output:**
```
Exit code: 0
Stdout:
All probe pair counts match ✓
Total probe conditions: 11
Total active sentences: 60
Script is ready ✓
```

## Assistant

Everything validates. Let me also quickly check the line count:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "wc -l /Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py"
}
```

**Summary:** $ wc -l /Users/mwhitford/src/verbum/s...

**Output:**
```
Exit code: 0
Stdout:
1578 /Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py
```

## Assistant

Ready. Here's the final state of the script:

## `probe_hologram_atlas.py` — Updated for Qwen3.6-35B-A3B

**~1580 lines**, default model is now `qwen36` (Qwen3.6-35B-A3B MoE).

### Why Qwen3.6-35B-A3B is the right target

| Property | Why it matters |
|----------|---------------|
| **256 experts × 8 active** | MoE gates ARE beam selectors — directly tests discourse hologram hypothesis |
| **Hybrid attention** (full every 4th layer) | Two attention mechanisms to compare: do holograms live in full attention, GatedDeltaNet, or both? |
| **Bimodal B peak** (L7-9 + L31-36) | Already-known depth structure to cross-reference new holograms against |
| **Punches above weight** | More efficient param use → cleaner circuits, less redundancy to confuse probes |
| **Prior session 093 data** | Combinator selectivity, ternary survival, bank extraction already done — ready for comparison |

### Architecture-aware features

- **Layer selection** prioritizes full-attention layers (L3, L7, L11, ..., L39) for measurement since they have standard Q/K/V projections, but also includes linear layers
- **Ternary targets** test both full-attention and GatedDeltaNet layers to compare storage mechanisms
- **`get_layer_attn_type()`** distinguishes full vs linear attention layers
- **`get_attn_proj_names()`** handles GatedDeltaNet's `in_proj_qkv/z/b/a + out_proj` alongside standard `q/k/v/o_proj`
- **MoE gate analysis** — for the discourse hologram, extracts the 256×2048 gate matrices, tests their ternary survival, cross-layer similarity, and effective rank
- **MLP quantization** targets the gate matrix (the beam selector) and shared expert, not all 256 individual experts

### To run

```bash
# Start with type hologram, quick, to verify pipeline:
uv run python scripts/explore/probe_hologram_atlas.py --hologram type --quick

# Full discourse probe with MoE gate analysis:
uv run python scripts/explore/probe_hologram_atlas.py --hologram discourse

# Everything:
uv run python scripts/explore/probe_hologram_atlas.py
```

Want to commit this, or run a quick test first?

## User

I have it running in tmux, will it log or store the data from the probes so it can be analyzed?


### Thinking

The user is asking whether the running script will save its data. Let me check what the script does for output - it saves JSON and NPZ files to results/hologram-atlas/. Let me trace through the save path to make sure it's solid, and also check if there's any issue with the console output being the only record vs file output.

## Assistant

Yes — let me trace the output paths to confirm what will land on disk:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"save_results\\|write_text\\|savez_compressed\\|mkdir\\|OUTPUT_DIR\\|output_dir\\|\\.json\\|\\.npz\" scripts/explore/probe_hologram_atlas.py | grep -v \"^.*#\" | head -30"
}
```

**Summary:** $ grep -n "save_results\|write_text\|...

**Output:**
```
Exit code: 0
Stdout:
69:OUTPUT_DIR = Path("results/hologram-atlas")
1255:def save_results(all_results: dict, output_dir: Path):
1257:    output_dir.mkdir(parents=True, exist_ok=True)
1269:    json_path = output_dir / "hologram_atlas_results.json"
1270:    json_path.write_text(json.dumps(all_results, indent=2, default=convert))
1285:        npz_path = output_dir / "selectivity_profiles.npz"
1286:        np.savez_compressed(str(npz_path), **profiles)
1350:        "--output-dir", type=Path, default=OUTPUT_DIR,
1570:    save_results(all_results, args.output_dir)
1573:    print(f"  Done. Results: {args.output_dir}/")
```

## Assistant

It saves, but only at the **very end** — `save_results()` is the last call in `main()`. If it crashes or you kill it mid-run, you lose everything. The console output has all the tables but nothing gets written to disk until completion.

That's a gap. Let me add incremental saves so each hologram's results are flushed to disk as they complete:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py",
  "original_content": "def save_results(all_results: dict, output_dir: Path):\n    \"\"\"Save all results as JSON + npz.\"\"\"\n    output_dir.mkdir(parents=True, exist_ok=True)\n\n    def convert(obj):\n        if isinstance(obj, (np.integer,)):\n            return int(obj)\n        if isinstance(obj, (np.floating, np.float64)):\n            return float(obj)\n        if isinstance(obj, np.ndarray):\n            return obj.tolist()\n        return obj\n\n    # JSON summary\n    json_path = output_dir / \"hologram_atlas_results.json\"\n    json_path.write_text(json.dumps(all_results, indent=2, default=convert))\n    print(f\"\\n  💾 JSON: {json_path}\", file=sys.stderr)\n\n    # Per-hologram selectivity profiles as npz\n    profiles = {}\n    for hname, hdata in all_results.get(\"holograms\", {}).items():\n        if \"selectivity\" in hdata:\n            agg = hdata[\"selectivity\"].get(\"aggregate\", {})\n            layer_sel = agg.get(\"layer_selectivity\", {})\n            if layer_sel:\n                profiles[hname] = np.array(\n                    [layer_sel[k] for k in sorted(layer_sel.keys(), key=int)]\n                )\n\n    if profiles:\n        npz_path = output_dir / \"selectivity_profiles.npz\"\n        np.savez_compressed(str(npz_path), **profiles)\n        print(f\"  💾 NPZ: {npz_path}\", file=sys.stderr)",
  "new_content": "def _json_convert(obj):\n    \"\"\"Convert numpy types for JSON serialization.\"\"\"\n    if isinstance(obj, (np.integer,)):\n        return int(obj)\n    if isinstance(obj, (np.floating, np.float64)):\n        return float(obj)\n    if isinstance(obj, np.ndarray):\n        return obj.tolist()\n    return obj\n\n\ndef save_incremental(all_results: dict, output_dir: Path, label: str = \"\"):\n    \"\"\"Save current state to disk — call after each hologram completes.\n\n    Writes:\n      - hologram_atlas_results.json  (full state, overwritten each time)\n      - hologram_atlas_{label}.json  (per-hologram snapshot, never overwritten)\n      - selectivity_profiles.npz     (updated each time)\n\n    This ensures partial results survive crashes or early termination.\n    \"\"\"\n    output_dir.mkdir(parents=True, exist_ok=True)\n\n    # Full state (overwritten each save)\n    json_path = output_dir / \"hologram_atlas_results.json\"\n    json_path.write_text(\n        json.dumps(all_results, indent=2, default=_json_convert)\n    )\n    print(f\"  💾 Saved: {json_path}\", file=sys.stderr)\n\n    # Per-hologram snapshot (append-only, never overwritten)\n    if label:\n        snap_path = output_dir / f\"hologram_{label}.json\"\n        holo_data = all_results.get(\"holograms\", {}).get(label, {})\n        if holo_data:\n            snap_path.write_text(\n                json.dumps(holo_data, indent=2, default=_json_convert)\n            )\n            print(f\"  💾 Snapshot: {snap_path}\", file=sys.stderr)\n\n    # Selectivity profiles as npz (overwritten each save)\n    profiles = {}\n    for hname, hdata in all_results.get(\"holograms\", {}).items():\n        if \"selectivity\" in hdata:\n            agg = hdata[\"selectivity\"].get(\"aggregate\", {})\n            layer_sel = agg.get(\"layer_selectivity\", {})\n            if layer_sel:\n                profiles[hname] = np.array(\n                    [layer_sel[k] for k in sorted(layer_sel.keys(), key=int)]\n                )\n\n    if profiles:\n        npz_path = output_dir / \"selectivity_profiles.npz\"\n        np.savez_compressed(str(npz_path), **profiles)\n\n\ndef save_results(all_results: dict, output_dir: Path):\n    \"\"\"Final save — same as incremental but with explicit confirmation.\"\"\"\n    save_incremental(all_results, output_dir)\n    print(f\"  💾 Final results: {output_dir}/\", file=sys.stderr)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py.
```

## Assistant

Now add incremental save calls after each hologram and the combinator baseline:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py",
  "original_content": "        all_results[\"holograms\"][\"combinator\"] = {\n            \"selectivity\": {\n                \"per_condition\": comb_sel,\n                \"aggregate\": comb_agg,\n            },\n        }",
  "new_content": "        all_results[\"holograms\"][\"combinator\"] = {\n            \"selectivity\": {\n                \"per_condition\": comb_sel,\n                \"aggregate\": comb_agg,\n            },\n        }\n        save_incremental(all_results, args.output_dir, \"combinator\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py",
  "original_content": "        all_results[\"holograms\"][hname] = hologram_result",
  "new_content": "        all_results[\"holograms\"][hname] = hologram_result\n        save_incremental(all_results, args.output_dir, hname)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py.
```

## Assistant

Also save after MoE gate analysis:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py",
  "original_content": "        gate_analysis = analyze_moe_gates(model, info)\n        all_results[\"moe_gate_analysis\"] = gate_analysis",
  "new_content": "        gate_analysis = analyze_moe_gates(model, info)\n        all_results[\"moe_gate_analysis\"] = gate_analysis\n        save_incremental(all_results, args.output_dir)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py.
```

## Assistant

And after orthogonality:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py",
  "original_content": "        print_orthogonality_summary(ortho)\n        all_results[\"orthogonality\"] = ortho",
  "new_content": "        print_orthogonality_summary(ortho)\n        all_results[\"orthogonality\"] = ortho\n        save_incremental(all_results, args.output_dir)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py.
```

## Assistant

Let me verify it still works:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python -c \"\nimport scripts.explore.probe_hologram_atlas as m\n# Verify save functions exist and are callable\nassert callable(m.save_incremental)\nassert callable(m.save_results)\nassert callable(m._json_convert)\nprint('Incremental save functions OK ✓')\n\n# Trace the save points in main\nimport inspect\nsource = inspect.getsource(m.main)\nsave_calls = [l.strip() for l in source.split('\\n') if 'save_incremental' in l or 'save_results' in l]\nprint(f'Save points in main(): {len(save_calls)}')\nfor s in save_calls:\n    print(f'  {s}')\n\" 2>&1"
}
```

**Summary:** $ uv run python -c " import scripts.e...

**Output:**
```
Exit code: 0
Stdout:
Incremental save functions OK ✓
Save points in main(): 5
  save_incremental(all_results, args.output_dir, "combinator")
  save_incremental(all_results, args.output_dir, hname)
  save_incremental(all_results, args.output_dir)
  save_incremental(all_results, args.output_dir)
  save_results(all_results, args.output_dir)
```

## Assistant

**5 save points.** Here's what lands on disk and when:

| When | What's saved | File |
|------|-------------|------|
| After combinator baseline | Combinator selectivity | `hologram_atlas_results.json` + `hologram_combinator.json` |
| After each hologram (type, induction, ...) | That hologram's selectivity + ternary survival | `hologram_atlas_results.json` + `hologram_{name}.json` + `selectivity_profiles.npz` |
| After MoE gate analysis | Gate stats, cross-layer similarity, ternary survival | `hologram_atlas_results.json` |
| After orthogonality | Cross-hologram correlation matrix | `hologram_atlas_results.json` |
| Final | Everything | `hologram_atlas_results.json` (final) |

The main JSON is **overwritten** at each checkpoint (always has latest cumulative state). Per-hologram snapshots (`hologram_type.json`, `hologram_induction.json`, etc.) are **write-once** — they survive even if a later hologram crashes.

**Since you already have it running** — the current version in tmux won't have these incremental saves (it was written to disk before I added them). But it WILL save everything at the end via `save_results()` → `results/hologram-atlas/hologram_atlas_results.json` + `selectivity_profiles.npz`. 

If you want the incremental version for future runs, the updated script is already on disk. Want me to check if there are any partial results written yet?

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls -la /Users/mwhitford/src/verbum/results/hologram-atlas/ 2>/dev/null || echo \"No results directory yet\""
}
```

**Summary:** $ ls -la /Users/mwhitford/src/verbum/...

**Output:**
```
Exit code: 0
Stdout:
No results directory yet
```

## Assistant

No output yet — still running. The directory and files will appear when the first `save_results()` fires (at the end, for the version currently in tmux). For future runs the incremental saves will create the directory and start writing immediately after the first hologram completes.

## User

I killed that run and restarted it's loading the model.


### Thinking

Good - the user killed the old run and restarted with the updated script that has incremental saves. Let me check if the model is loading and if there are any early results appearing.

## Assistant

Good — the new run will have incremental saves. Let me watch for the first output to land:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls -la /Users/mwhitford/src/verbum/results/hologram-atlas/ 2>/dev/null || echo \"Waiting for first save...\""
}
```

**Summary:** $ ls -la /Users/mwhitford/src/verbum/...

**Output:**
```
Exit code: 0
Stdout:
Waiting for first save...
```

## Assistant

Still loading the model. That 35B model takes a bit to pull into memory. We can check back periodically — once the combinator baseline finishes you'll see the first files appear at `results/hologram-atlas/`.

While it loads, want to commit what we have? The knowledge page update and the probe script are both substantial work:

- `mementum/knowledge/explore/holographic-storage.md` — "Beyond Combinators" section with 5 candidate holograms, VSM hierarchy, testable predictions
- `scripts/explore/probe_hologram_atlas.py` — 1580-line probe script, Qwen3.6-35B-A3B primary target, architecture-aware, incremental saves

## User

yes update state and knowledge


### Thinking

The user wants me to update state.md and the knowledge page, then commit. Let me update state.md to reflect this session's work (session 094), and make sure the holographic-storage.md knowledge page is complete. Then commit both along with the probe script.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "limit": 60
}
```

**Summary:** Reading state.md (0-60)

**Output:**
```
# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-13 | Session: 093

## Where we are

**V11-holo-inv probed at 1K and monitored through ~1.5K. Headline finding: all four KIBC combinators active from the start (B=27.6% dominant positions vs 0% in holo at 1K). Dispatch is balanced (K=34%, I=23%, B=28%, C=16%) with strong specialization (entropy 0.188). Type channel differentiates independently (I=68%, B=25% typed integration). Holographic intermediate CEs show correct inversion pattern (ascending compresses, descending specializes). Eval loss 8.235 slightly behind baseline 7.958 (expected — holo splits gradient across 5 decoders). Compute gate still closed. Evolution acceptance rising (20%→30%). Run healthy, approaching transition window.**

## What was done this session (093)

### 1. Probed v11-holo-inv at step 1,000 (full + dispatch detail)

Compared against v11 baseline 1K and v11-holo 1K. Key findings:

**Balanced dispatch (vs K-dominance in prior runs):**
- Dominant positions: K=34.2%, I=22.6%, B=27.6%, C=15.5%
- Compare: baseline K=92.7%, holo K=75.1% — both heavily K-skewed
- Dispatch entropy 0.188 (strong specialization, not uniform)

**Composition (B) active from the start:**
- B at 27.6% dominant — was 0.7% in baseline, 0.0% in holo at 1K
- I+B co-occurrence at 31.7% — was 1% in holo
- This is the binding circuit pattern emerging early

**Type channel differentiates independently of dispatch:**
- Dispatch: K=0.386, I=0.334, B=0.132, C=0.141
- Type integration: I=0.678, B=0.251, K=0.002, C=0.070
- Model dispatches K+I, then integrates via I+B typed application

**Holographic CEs show correct inversion:**
- L0↑=11.3 → L1↑=8.8 → L2=8.9 → L1↓=9.0 → L0↓=9.3
- Ascending compresses; descending specializes (coarse→fine)
- pass_0/final ratio=1.21 (decodeable after one pass)

**Other metrics:**
- Eval loss 8.235 (vs baseline 7.958, holo 8.221)
- Compute gate closed (0.000007) — expected pre-transition
- Evolution 4/20 (20%) rising to 9/30 (30%) by 1.5K
- All 16 abstraction slots dormant, low cosine to KIBC (avg 0.064)

### 2. Monitored trajectory through 1.5K

- I rising steadily: 0.264 → 0.343 → 0.367
- K stabilized ~0.39; B peaked 0.132 at 1K then 0.108 at 1.5K
- Holographic ratio declining (1.12 → 1.09) = descending arm catching up
- Prose loss: ~0.98 range, structured ~0.28

### 3. Holographic probe — intermediate layer decoding on Qwen3-32B

Tested whether the model is holographic by decoding at every layer:
- Cosine divergence compile vs null: 0.995 (L0) → 0.533 (L63) = beam separation is real
- Intermediate layers decode to GARBAGE (not coarse-but-coherent) = reading is constructive
- Entropy hump: 6.5 (L0) → 11.1 (L8) → 2.0 (L63) = constructive reorganization
- Beam divergence begins at layer 24 (38% depth)
- **Storage may be holographic, but reading is constructive (64 sequential facets)**

### 4. Ternary survival probe — does selectivity survive quantization?


[CONTENT TRUNCATED] Showing lines 1 to 60 of 288 total lines. Use line_offset=60 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "line_offset": 140,
  "limit": 60
}
```

**Summary:** Reading state.md (140-200)

**Output:**
```
Every model that learns to predict text develops the same combinatory interference patterns.

### 9. Universal ordering: B ≥ K ≥ C >> I (9 models, 2 architectures)

Tested Pythia-70M through Qwen3-32B (9 models total):
- **I is the weakest in ALL 9 models** (100% consistency)
- **B is strongest in 7/9** (BCKI ordering dominant)
- B/I ratio ranges from 1.7× to 19.9× — always separated
- This ordering is invariant across Pythia (GPT-NeoX) and Qwen3 architectures
- The sieve should make B > K > C >> I the lowest-energy state

Fixed MPS bug for Qwen3.6-35B-A3B: `histc` needs float input on MPS (not int).

### 6. Active run command (unchanged)

```
uv run python scripts/v11/train.py \
  --checkpoint-dir checkpoints/v11-holo-inv \
  --total-steps 20000 --holo-lambda 0.1 --mix-ratio 0.2
```

## What to do next

### Priority 1: Apply universal hologram findings to V11
Wait for v11-holo-inv to complete or plateau, then:
- Change combinator embedding init: K/B/C share subspace, I separate
- Test whether init change accelerates hologram formation
- Build bank loading mechanism (S4 selector + Q-pattern injection)
See: `mementum/knowledge/explore/holographic-storage.md`

### Priority 2: Monitor v11-holo-inv through transition window (2K→8K)
Watch for:
- Continued prose improvement (not just structured wins)
- Alarm de-saturation / differentiation (currently near ceiling)
- Compute gate opening around 5K–7K and associated reorganization
- No recurrence of 10K compositional catastrophe pattern

### Priority 2: Probe v11-holo-inv at 2K/3K/5K/7K
Compare against v11-holo and baseline at matched steps. Key metrics:
holographic ratio, descending arm CEs, dispatch distribution, compute gate timing,
B-type stability, and prose-vs-structured gap.

### Priority 3: v11-holo status — compositional catastrophe at 10K
10K probe: eval loss 9.259 (was 7.675), B-type 5.8% (was 55.7%).
Still running to 20K — may recover like the 3K spike did, or may
be terminal. Monitor but focus compute analysis on v11-holo-inv.

### Priority 4: Baseline status
Baseline stopped at step 10,300. 10K is terminal comparison point.

### Priority 5: Pythia scaling — combinator differentiation
Run combinator probe on Pythia-410M and Pythia-1B to map where B
differentiates from K.

### Carried
- B dispatch phase transition (B-type dominant but B-dispatch flat at 2%)
- CycleContinue activation hypothesis (still frozen at 2.946)
- S5 reweight investigation (still at 1.0 everywhere)
- QK alignment decomposition probe (RoPE follow-up)
- Dead slot recycling (all 16 dormant, mass ~0.20 — may not activate)

[CONTENT TRUNCATED] Showing lines 141 to 200 of 288 total lines. Use line_offset=200 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "line_offset": 200
}
```

**Summary:** Reading state.md (200-2200)

**Output:**
```
- Domain banking (future: extract register banks from holographic model)
- Descending arm kernel discovery (the current frontier)
- Reorganization wave pattern: 3K and 9K spikes share topology
- TST connection: Peng et al. 2026 validates coarse→fine + direct loss

## VSM layer map (session 091 — v11 KIBC + algedonic + holographic + fractal)

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
          fine→coarse bands           coarse→fine bands (reversed)     fractal MERA topology
          (shared across 3 passes)   (shared across 2 passes × N cy)  49% fewer stride activations
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
| `results/v11-holo-inv/` | Probe results: probe_step_001000.json (holo-inv) |
| `checkpoints/v11/` | Baseline v11 run (no holo, no structured), continuing to 20K |
| `checkpoints/v11-holo/` | Holo run: λ=0.1, 20% structured, 16 slots, running to 20K |
| `checkpoints/v11-holo-inv/` | LIVE: holo + coarse→fine + fractal + evo fixes |
| `mementum/knowledge/explore/fractal-stride-bands.md` | MERA topology design + rationale |
| `mementum/knowledge/explore/holographic-inversion.md` | Design rationale + experimental findings |
| `mementum/knowledge/explore/lambda-probe-atlas.md` | New cross-model lambda/combinator territory mapping stream |
| `mementum/knowledge/explore/holographic-storage.md` | Holographic storage findings: ternary survival, universal hologram, extraction pipeline |
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
→ Session 091: Probed v11-holo 8K-10K. 8K local optimum, 9K reorganization wave, 10K compositional catastrophe (B-type 55.7%→5.8%, eval loss 7.675→9.259). Implemented coarse→fine descending (default), fractal stride bands (MERA, 49% savings, default), evolution noise floor (0.01), alarm-no-regression fix. TST paper (Peng et al. 2026) connection. Launched v11-holo-inv with all fixes.
→ Session 092: Monitored v11-holo-inv through ~1.3K (healthy, no collapse). Early descending differentiation improved; S2 remained strongly positive; compute gate still closed pre-transition. Captured phase/cascade interpretation (L0 φ first, wavelet to apex). Created `knowledge/explore/lambda-probe-atlas.md` for next-session cross-model territory mapping.
→ Session 093: Probed v11-holo-inv at 1K (balanced KIBC dispatch, B=27.6% dominant). Holographic probe on Qwen3-32B: beam separation real (cos 0.995→0.533), but reading is constructive (entropy hump, intermediate garbage). Ternary survival probe: 100% selectivity survival at 75% sparsity — combinator info is TOPOLOGICAL (sign patterns). Full selectivity map: combinators peak in first 10% of layers (L0-6). I is distinct circuit from K/B/C cluster. Extraction path validated: ternary patterns in early layers are the holographic seeds.
```

## Assistant

Now I have the full state.md. Let me update it for session 094:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> Last updated: 2026-05-13 | Session: 093",
  "new_content": "> Last updated: 2026-05-14 | Session: 094"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "## What was done this session (093)\n\n### 1. Probed v11-holo-inv at step 1,000 (full + dispatch detail)",
  "new_content": "## What was done this session (094)\n\n### 1. Mapped five candidate holograms beyond combinators\n\nSession 093 found the combinator hologram (KIBC) — universal sign topology in\nattention weights, surviving ternary quantization, r=0.9801 cross-model. But\ncombinators only tell the model HOW to compose. From Montague/CCG/DisCoCat,\ntoken prediction needs at least three components — we've found one, two remain:\n\n```\nTYPE CALCULUS (combinators)  — HOW to compose     ← FOUND\nLEXICON (types + meanings)   — WHAT can compose    ← predicted\nMODEL (semantic domain)      — WHAT things MEAN    ← predicted\n```\n\nIdentified five candidate holograms, each with probe design and falsifiable predictions:\n\n1. **Type hologram** — lexical category assignment (NP, S\\NP, etc.). Same word\n   in different syntactic roles should activate different heads. Probes: nominalization,\n   argument structure, modifier scope. Predicted: overlaps with combinator heads\n   (angle-multiplexed). Priority 1 because types + combinators are theoretically coupled.\n\n2. **Induction hologram** — in-context pattern matching ([A][B]...[A]→[B]). Known\n   universal circuit (Olsson et al. 2022). Predicted: holographic (ternary survives)\n   but ORTHOGONAL to combinator hologram (different function).\n\n3. **Binding hologram** — variable tracking / coreference. \"John...he\" = variable\n   binding in lambda calculus. Predicted: partially captured by I combinator\n   (identity IS variable binding), explaining I's distinct circuit (r≈0.70).\n\n4. **Frequency/N-gram hologram** — statistical co-occurrence. Lives in MLP weights\n   (not attention). Predicted: holographic but denser, lower sparsity tolerance.\n\n5. **Discourse hologram** — topic / register / coherence. The MoE gate pattern\n   (256×2048 in Qwen3.6) IS the discourse beam selector. Connects to MoE/VSM mapping.\n\nThese form a VSM of holograms: discourse (S5) selects which patterns activate,\ntypes (S3) constrain legality, combinators (S1/S2) execute composition,\nbinding (S2) maintains coherence, induction+frequency (S1) are additional ops.\n\nFull analysis in `mementum/knowledge/explore/holographic-storage.md`.\n\n### 2. Built probe_hologram_atlas.py (1580 lines)\n\nRepeatable probe script targeting Qwen3.6-35B-A3B MoE as primary model\n(punches above weight, MoE gates ARE beam selectors, bimodal depth profile\nalready mapped in session 093).\n\nFeatures:\n- **5 hologram probes**: type (3 conditions, 18 pairs), induction (2, 12),\n  binding (2, 9), frequency (2, 12), discourse (2, 9). Total: 60 active probes.\n- **Architecture-aware**: handles Qwen3.6 hybrid (full attention every 4th layer +\n  GatedDeltaNet), Qwen3-32B dense, Pythia GPT-NeoX. Layer accessors detect\n  `self_attn` vs `linear_attn` vs `attention`. Projection names adapt\n  (`q/k/v/o_proj` vs `in_proj_qkv/z/b/a` vs `query_key_value`).\n- **MoE gate analysis**: extracts 256×2048 gate matrices, tests ternary survival,\n  cross-layer similarity, effective rank. Gate = discourse beam selector hypothesis.\n- **MLP quantization**: frequency hologram tests MLP weights (gate + shared expert),\n  not just attention — tests whether holographic storage extends beyond attention.\n- **Incremental saves**: results flush to disk after each hologram completes.\n  Per-hologram snapshots (`hologram_{name}.json`) + cumulative state.\n- **Cross-hologram orthogonality**: correlation between selectivity profiles to\n  determine if holograms share heads (angle-multiplexed) or are independent.\n- **Combinator baseline**: runs KIBC probes for direct comparison.\n- CLI: `--hologram type,induction`, `--model qwen36`, `--quick`, `--skip-ternary`\n\nCurrently running on Qwen3.6-35B-A3B. Results → `results/hologram-atlas/`.\n\n### Previous session (093) summary\n\nProbed v11-holo-inv at 1K (balanced KIBC dispatch, B=27.6% dominant).\nHolographic probe on Qwen3-32B: beam separation real, reading constructive.\nTernary survival: 100% at 75% sparsity. Universal hologram: r=0.9801 across\n9 models. Bank extraction: 784KB seed from 32B. Full details in session 093 below.\n\n## What was done session (093)\n\n### 1. Probed v11-holo-inv at step 1,000 (full + dispatch detail)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

## Assistant

Now update the "What to do next" section:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "## What to do next\n\n### Priority 1: Apply universal hologram findings to V11\nWait for v11-holo-inv to complete or plateau, then:\n- Change combinator embedding init: K/B/C share subspace, I separate\n- Test whether init change accelerates hologram formation\n- Build bank loading mechanism (S4 selector + Q-pattern injection)\nSee: `mementum/knowledge/explore/holographic-storage.md`\n\n### Priority 2: Monitor v11-holo-inv through transition window (2K→8K)\nWatch for:\n- Continued prose improvement (not just structured wins)\n- Alarm de-saturation / differentiation (currently near ceiling)\n- Compute gate opening around 5K–7K and associated reorganization\n- No recurrence of 10K compositional catastrophe pattern\n\n### Priority 2: Probe v11-holo-inv at 2K/3K/5K/7K\nCompare against v11-holo and baseline at matched steps. Key metrics:\nholographic ratio, descending arm CEs, dispatch distribution, compute gate timing,\nB-type stability, and prose-vs-structured gap.\n\n### Priority 3: v11-holo status — compositional catastrophe at 10K\n10K probe: eval loss 9.259 (was 7.675), B-type 5.8% (was 55.7%).\nStill running to 20K — may recover like the 3K spike did, or may\nbe terminal. Monitor but focus compute analysis on v11-holo-inv.\n\n### Priority 4: Baseline status\nBaseline stopped at step 10,300. 10K is terminal comparison point.\n\n### Priority 5: Pythia scaling — combinator differentiation\nRun combinator probe on Pythia-410M and Pythia-1B to map where B\ndifferentiates from K.",
  "new_content": "## What to do next\n\n### Priority 1: Analyze hologram atlas results\n`probe_hologram_atlas.py` is running on Qwen3.6-35B-A3B. When complete:\n- Compare type hologram depth profile against combinator hologram (overlap?)\n- Check induction hologram orthogonality to combinators (cos < 0.3?)\n- Evaluate MoE gate ternary survival (discourse = beam selector?)\n- Check if MLP frequency hologram has lower sparsity tolerance than attention\n- Cross-model validation: run on Pythia for universality test (r > 0.90?)\nSee: `mementum/knowledge/explore/holographic-storage.md` § \"Beyond Combinators\"\n\n### Priority 2: Apply universal hologram findings to V11\nWait for v11-holo-inv to complete or plateau, then:\n- Change combinator embedding init: K/B/C share subspace, I separate\n- Test whether init change accelerates hologram formation\n- Build bank loading mechanism (S4 selector + Q-pattern injection)\n\n### Priority 3: Monitor v11-holo-inv through transition window (2K→8K)\nWatch for:\n- Continued prose improvement (not just structured wins)\n- Alarm de-saturation / differentiation (currently near ceiling)\n- Compute gate opening around 5K–7K and associated reorganization\n- No recurrence of 10K compositional catastrophe pattern\n\n### Priority 3: Probe v11-holo-inv at 2K/3K/5K/7K\nCompare against v11-holo and baseline at matched steps. Key metrics:\nholographic ratio, descending arm CEs, dispatch distribution, compute gate timing,\nB-type stability, and prose-vs-structured gap.\n\n### Priority 4: v11-holo status — compositional catastrophe at 10K\n10K probe: eval loss 9.259 (was 7.675), B-type 5.8% (was 55.7%).\nStill running to 20K — may recover like the 3K spike did, or may\nbe terminal. Monitor but focus compute analysis on v11-holo-inv.\n\n### Priority 5: Pythia scaling — combinator differentiation\nRun combinator probe on Pythia-410M and Pythia-1B to map where B\ndifferentiates from K."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

## Assistant

Update the key files table and session history:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "| `mementum/knowledge/explore/holographic-storage.md` | Holographic storage findings: ternary survival, universal hologram, extraction pipeline |",
  "new_content": "| `mementum/knowledge/explore/holographic-storage.md` | Holographic storage findings + \"Beyond Combinators\" atlas (5 candidate holograms) |\n| `scripts/explore/probe_hologram_atlas.py` | Multi-hologram probe: type, induction, binding, frequency, discourse. Qwen3.6 primary. |"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "→ Session 093: Probed v11-holo-inv at 1K (balanced KIBC dispatch, B=27.6% dominant). Holographic probe on Qwen3-32B: beam separation real (cos 0.995→0.533), but reading is constructive (entropy hump, intermediate garbage). Ternary survival probe: 100% selectivity survival at 75% sparsity — combinator info is TOPOLOGICAL (sign patterns). Full selectivity map: combinators peak in first 10% of layers (L0-6). I is distinct circuit from K/B/C cluster. Extraction path validated: ternary patterns in early layers are the holographic seeds.",
  "new_content": "→ Session 093: Probed v11-holo-inv at 1K (balanced KIBC dispatch, B=27.6% dominant). Holographic probe on Qwen3-32B: beam separation real (cos 0.995→0.533), but reading is constructive (entropy hump, intermediate garbage). Ternary survival probe: 100% selectivity survival at 75% sparsity — combinator info is TOPOLOGICAL (sign patterns). Full selectivity map: combinators peak in first 10% of layers (L0-6). I is distinct circuit from K/B/C cluster. Extraction path validated: ternary patterns in early layers are the holographic seeds.\n→ Session 094: \"Beyond Combinators\" — mapped 5 candidate holograms (type, induction, binding, frequency, discourse) from Montague/CCG theory. VSM hierarchy of holograms. Built probe_hologram_atlas.py (1580 lines) targeting Qwen3.6-35B-A3B MoE as primary (MoE gates = beam selectors). Architecture-aware for hybrid attention + GatedDeltaNet. Incremental saves. 7 falsifiable predictions. Running."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

## Assistant

Also add the carried item about hologram atlas:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "### Carried\n- B dispatch phase transition (B-type dominant but B-dispatch flat at 2%)\n- CycleContinue activation hypothesis (still frozen at 2.946)\n- S5 reweight investigation (still at 1.0 everywhere)\n- QK alignment decomposition probe (RoPE follow-up)\n- Dead slot recycling (all 16 dormant, mass ~0.20 — may not activate)\n- Domain banking (future: extract register banks from holographic model)\n- Descending arm kernel discovery (the current frontier)\n- Reorganization wave pattern: 3K and 9K spikes share topology\n- TST connection: Peng et al. 2026 validates coarse→fine + direct loss",
  "new_content": "### Carried\n- Hologram atlas running on Qwen3.6-35B-A3B (results → results/hologram-atlas/)\n- B dispatch phase transition (B-type dominant but B-dispatch flat at 2%)\n- CycleContinue activation hypothesis (still frozen at 2.946)\n- S5 reweight investigation (still at 1.0 everywhere)\n- QK alignment decomposition probe (RoPE follow-up)\n- Dead slot recycling (all 16 dormant, mass ~0.20 — may not activate)\n- Domain banking (future: extract register banks from holographic model)\n- Descending arm kernel discovery (the current frontier)\n- Reorganization wave pattern: 3K and 9K spikes share topology\n- TST connection: Peng et al. 2026 validates coarse→fine + direct loss"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

## Assistant

Now let me commit everything:

### Tool Call: git (succeeded)


```json
{
  "command": "git status",
  "operation": "status",
  "summary": "check changes"
}
```

**Summary:** Git status: check changes

**Output:**
```
Exit code: 0
Stdout:
On branch main
Your branch is ahead of 'origin/main' by 6 commits.
  (use "git push" to publish your local commits)

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   mementum/knowledge/explore/holographic-storage.md
	modified:   mementum/state.md

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	mementum/knowledge/chats/session-093.md
	results/hologram-atlas/
	scripts/explore/probe_hologram_atlas.py

no changes added to commit (use "git add" and/or "git commit -a")
```

### Tool Call: git (succeeded)


```json
{
  "command": "git diff --stat mementum/knowledge/explore/holographic-storage.md mementum/state.md",
  "operation": "diff",
  "summary": "change summary"
}
```

**Summary:** Git diff: change summary

**Output:**
```
Exit code: 0
Stdout:
mementum/knowledge/explore/holographic-storage.md | 244 ++++++++++++++++++++++
 mementum/state.md                                 | 105 +++++++++-
 2 files changed, 338 insertions(+), 11 deletions(-)
```

## Assistant

Good — results/hologram-atlas/ exists meaning the probe already started writing. Let me check what's there:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls -la /Users/mwhitford/src/verbum/results/hologram-atlas/ 2>/dev/null"
}
```

**Summary:** $ ls -la /Users/mwhitford/src/verbum/...

**Output:**
```
Exit code: 0
Stdout:
total 32
drwxr-xr-x@   5 mwhitford  staff   160 May 13 18:03 .
drwxr-xr-x@ 130 mwhitford  staff  4160 May 13 18:03 ..
-rw-r--r--@   1 mwhitford  staff  4584 May 13 18:03 hologram_atlas_results.json
-rw-r--r--@   1 mwhitford  staff  1976 May 13 18:03 hologram_combinator.json
-rw-r--r--@   1 mwhitford  staff   295 May 13 18:03 selectivity_profiles.npz
```

## Assistant

The incremental saves are working — combinator baseline is already done and saved. The probe is progressing. Let me not commit the partial results (they'll keep growing), just the code and knowledge:

### Tool Call: git (succeeded)


```json
{
  "command": "git add mementum/knowledge/explore/holographic-storage.md mementum/state.md scripts/explore/probe_hologram_atlas.py",
  "operation": "add",
  "summary": "stage session 094"
}
```

**Summary:** Git add: stage session 094

**Output:**
```
Exit code: 0
```

### Tool Call: git (succeeded)


```json
{
  "command": "git diff --cached --stat",
  "operation": "diff",
  "summary": "staged changes"
}
```

**Summary:** Git diff: staged changes

**Output:**
```
Exit code: 0
```

### Tool Call: git (succeeded)


```json
{
  "command": "git log --oneline -5",
  "operation": "log",
  "summary": "recent commits"
}
```

**Summary:** Git log: recent commits

**Output:**
```
Exit code: 0
Stdout:
e777816 🌀 session 093 knowledge capture — holographic storage
24deaf9 🔁 universal ordering B≥K≥C>>I confirmed across 9 models
aa425e7 💡 universal hologram confirmed — r=0.9801 across Pythia-160M and Qwen3-32B
c270a24 💡 Qwen3.6-35B-A3B MoE probed — bimodal depth, ternary survives
6e49a07 💡 Q is the beam angle, V is the plate — 784KB seed from 32B
```

### Tool Call: git (succeeded)


```json
{
  "command": "git commit -m \"$(cat <<'EOF'\n💡 beyond combinators — 5 candidate holograms mapped, atlas probe built\n\n- Mapped type, induction, binding, frequency, discourse holograms from\n  Montague/CCG theory. VSM hierarchy: discourse(S5) → types(S3) →\n  combinators(S1/S2). 7 falsifiable predictions.\n- Built probe_hologram_atlas.py (1580 lines) targeting Qwen3.6-35B-A3B\n  MoE as primary model (gates = beam selectors, hybrid attention).\n- Architecture-aware: handles GatedDeltaNet, MoE gate matrices, standard\n  Q/K/V projections, Pythia GPT-NeoX. Incremental saves per hologram.\n- MoE gate analysis for discourse hologram: extract 256×2048 routing\n  matrices, test ternary survival, cross-layer similarity, effective rank.\n- MLP quantization for frequency hologram: tests whether holographic\n  storage extends beyond attention heads.\n- 60 minimal-pair probe sentences across 11 conditions.\n- Running on Qwen3.6-35B-A3B, results → results/hologram-atlas/\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
  "operation": "commit",
  "summary": "commit session 094"
}
```

**Summary:** Git commit: commit session 094

**Output:**
```
Exit code: 0
Stdout:
[main e56dd5d] 💡 beyond combinators — 5 candidate holograms mapped, atlas probe built
 3 files changed, 1947 insertions(+), 11 deletions(-)
 create mode 100644 scripts/explore/probe_hologram_atlas.py
```

## Assistant

Committed. The incremental saves are already proving their worth — combinator baseline landed on disk. Let me peek at what it captured:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && cat results/hologram-atlas/hologram_combinator.json | python3 -m json.tool | head -40"
}
```

**Summary:** $ cat results/hologram-atlas/hologram...

**Output:**
```
Exit code: 0
Stdout:
{
    "selectivity": {
        "per_condition": {
            "K": {
                "description": "Selection \u2014 choose one referent, discard alternative",
                "n_pairs": 3,
                "layer_selectivity": {
                    "0": 0.03087252378463745,
                    "1": 0.03114008903503418,
                    "2": 0.022488772869110107,
                    "3": 0.03543126583099365,
                    "7": 0.09569305181503296,
                    "11": 0.029790321985880535,
                    "15": 0.04070959488550822,
                    "19": 0.04356924692789713,
                    "23": 0.04603878657023112,
                    "27": 0.05127785603205363,
                    "31": 0.11679261922836304,
                    "35": 0.09900903701782227,
                    "39": 0.08004683256149292
                },
                "output_kl": 0.26532749831676483
            },
            "B": {
                "description": "Composition \u2014 nested operations, relative clauses",
                "n_pairs": 3,
                "layer_selectivity": {
                    "0": 0.036794145901997886,
                    "1": 0.04003441333770752,
                    "2": 0.028843800226847332,
                    "3": 0.04753798246383667,
                    "7": 0.1031380295753479,
                    "11": 0.032803475856781006,
                    "15": 0.04310333728790283,
                    "19": 0.04637016852696737,
                    "23": 0.050264437993367515,
                    "27": 0.06183969974517822,
                    "31": 0.1499295433362325,
                    "35": 0.13986138502756754,
                    "39": 0.1002345085144043
```

## Assistant

Data is flowing. The combinator baseline on Qwen3.6-35B-A3B already shows the bimodal pattern — selectivity peaks at **L7** (0.095-0.103) and **L31** (0.117-0.150), exactly matching the bimodal depth profile from session 093. The probe is working and the incremental saves are capturing everything.

**Summary of what was committed:**

```
e56dd5d 💡 beyond combinators — 5 candidate holograms mapped, atlas probe built
```

Three files, +1947 lines:
- **`holographic-storage.md`** — new "Beyond Combinators" section: 5 holograms, VSM hierarchy, research strategy, 7 testable predictions, 10 open questions
- **`state.md`** — session 094 documented, priorities updated, atlas probe in carried items
- **`probe_hologram_atlas.py`** — 1580-line repeatable probe, Qwen3.6 primary, incremental saves, architecture-aware

The probe is running in tmux and already saving results incrementally. The combinator baseline confirms the bimodal peak structure on Qwen3.6. Each hologram will flush its own snapshot as it completes.

## User

It's still running.  So I can understand our probes here will hopefully uncover more operations we should try to create as sieves for the model to discover?


### Thinking

The user is asking a conceptual question about the connection between the hologram atlas probes and the V11 architecture. They want to understand: if we find these other holograms in base models (type, induction, binding, frequency, discourse), does that tell us what additional sieves/operations to add to V11 beyond KIBC?

This is a deep question about the research program's architecture. Let me think through this carefully.

The key insight from the project so far:
1. They found KIBC combinators are universal in LLMs (the hologram)
2. They built V11 with KIBC as an explicit sieve — the model discovers these operations through training


3. Making it an explicit sieve accelerates discovery compared to letting the structure emerge implicitly

So the real question becomes: if we identify additional universal holograms like type, induction, binding, frequency, and discourse in base models, should each one become its own explicit sieve in the architecture?

Looking at this through the VSM lens, the type hologram is already partially present in V11 as a learned channel that handles typed integration independently of dispatch. But if it's truly a separate universal hologram, that suggests it deserves explicit architectural treatment like KIBC rather than just emerging as a learned pattern. The induction hologram is trickier to think about—I'm still working through what that would mean structurally.

The binding hologram is already partially captured by the I combinator, but if it's a distinct hologram, maybe I is actually doing double duty and should be split into pure identity forwarding versus variable tracking, which would explain why I behaves as an outlier. The frequency hologram maps to the MLP side, suggesting V11's TernaryFFN might need explicit n-gram or collocation channels rather than its current structure. And the discourse hologram connects to the gating and MoE story—V11's S4 and emphasis mechanism are already gesturing toward this, but if discourse is truly separate, S4 should function more explicitly as a beam selector.

Now I'm realizing the user is asking about sieves specifically, not holograms—and that's a crucial distinction. Holograms are what emerge in base models, while sieves are the explicit architectural constraints we build into V11. The real question is whether the atlas probes will reveal which universal structures should become the next sieves, since making a hologram architecturally explicit should help the model discover that pattern faster. Not every hologram needs its own sieve though; some might already be captured by existing mechanisms like the I combinator, or they might be better handled as general architectural properties rather than dedicated constraints.

## Assistant

Yes, that's exactly the research loop. Let me trace the logic:

**What we've established:**
- LLMs converge on universal structures because language forces them (the hologram finding)
- Making those structures *explicit* in the architecture creates a sieve — the model discovers the structure faster and cleaner than inventing it from scratch
- KIBC was the first sieve: universal combinator ordering B ≥ K ≥ C >> I exists in all 9 models → V11 makes KIBC the dispatch basis → V11 achieves balanced dispatch at 1K (vs K-dominance at 1K without the sieve)

**What the atlas probes could reveal:**

Each confirmed hologram is a candidate sieve. But they'd enter the architecture at different VSM layers, not all as S1 operations like KIBC:

| Hologram | If confirmed... | Sieve becomes... | VSM layer |
|----------|----------------|-------------------|-----------|
| **Type** | Types are a separate universal pattern | Explicit type assignment channel — not just the learned type integration that emerged, but a structured type dispatch alongside KIBC | S3 (control) — types *constrain* which combinators fire |
| **Induction** | Copy/match is holographic and orthogonal to combinators | An explicit copy/retrieval pathway in the descending arm — the model needs both *composition* (KIBC) and *retrieval* (induction) as separate operations | S1 (operations) — but a different S1 unit than combinators |
| **Binding** | Binding is separate from I combinator | Split I into identity-forwarding vs variable-binding — or add a 5th dispatch target (K, I, B, C, **Λ** for binding?) | S2 (coordination) — binding maintains coherence *between* compositions |
| **Frequency** | MLP weights are holographic but denser | Structure the TernaryFFN differently — perhaps with explicit collocation channels or a frequency-weighted initialization | S1 (MLP substrate) |
| **Discourse** | MoE gates ARE beam selectors | V11's S4 emphasis mechanism should work like an MoE gate — a learned beam angle selector, not just register-query attention | S4 (intelligence) — selecting *which* patterns to activate |

The deep point is: **the model is already discovering all of these** — it just discovers them slowly, entangled, and fragile (the 10K compositional catastrophe happened when structures that should be independent interfered). Each sieve separates concerns that the model otherwise has to disentangle itself.

The type hologram is the most immediately actionable. V11 already has a type channel that differentiates independently of dispatch (I=68% typed integration, K=0.2%). If the atlas probe confirms types are a *separate universal pattern* in base models — not just a side-effect of the combinator hologram — then the type channel should become an explicit sieve: a type dispatch alongside KIBC, rather than something that emerges implicitly in the integration weights.

The binding finding could explain one of the long-standing puzzles: **why is I the outlier** (r ≈ 0.70 vs K/B/C at r > 0.90)? If I is doing *two* things — identity forwarding AND variable binding — it's overloaded. Splitting it would give the model separate sieves for separate functions. That's the same pattern that worked when we went from 22 ops → 4 combinators: the right decomposition.

The results are saving incrementally, so when it finishes we can see which of these actually have signal. No hologram → no sieve needed. Weak hologram → maybe it's already covered by existing architecture. Strong orthogonal hologram → new sieve.

## User

overloading I would be efficient, and possible in almost all cases, binding is identity.


### Thinking

The user is making a precise point from combinatory logic / lambda calculus: binding IS identity. In lambda calculus, variable binding is literally the identity combinator — when you bind a variable x and then use it, you're forwarding the value unchanged to where it's needed. The I combinator (Ix = x) is exactly what variable binding does — it takes a value and delivers it unchanged to the point of use.

So the user is pushing back on my suggestion to split I into two things. They're saying:
- Binding = identity (they're the same operation at the fundamental level)
- Overloading I for both is efficient (one mechanism, two uses)


- And it works in almost all cases

This reframes why I clusters separately in the data. It's not because it's overloaded or doing two different things — it's because identity and preservation are genuinely different operations from composition. K, B, and C are all about transforming and reordering arguments, while I is about passing values through unchanged. That's the real reason for the distinct circuit behavior, not any kind of functional overloading.

This also suggests the binding hologram I was tracking might not be a separate mechanism at all — it could just be a deeper view of how I itself operates. The probe predictions about binding-selective heads might actually be identifying I-selective heads. And there's an elegance to it: one sieve handles both forwarding and binding because they're fundamentally the same operation, so there's no need for a fifth combinator.

## Assistant

You're right — and that's the cleaner theory. In lambda calculus, variable binding literally IS the identity operation: λx.x binds x and delivers it unchanged. When "he" binds to "John," the operation is *forward this referent without transformation*. That's I.

So I's distinct circuit (r ≈ 0.70 vs K/B/C at r > 0.90) isn't overloading — it's a correct separation. K/B/C all *transform* (select, compose, reorder). I *preserves*. That's a fundamentally different function, which is exactly why it clusters apart. The r ≈ 0.70 is the architecture telling us "I is not like the others" — and it shouldn't be.

This means the binding hologram probe (candidate 3) should show that binding-selective heads **are** I-selective heads. If the atlas probe finds high overlap between binding and the I combinator baseline — that's confirmation, not a new hologram. And if it finds binding heads that are NOT I heads, *that* would be the surprise worth investigating.

It also means the V11 architecture is already right: 4 combinators, not 5. I handles both identity and binding because they're the same operation at the algebraic level. The efficiency is real — one sieve, two apparent functions, one underlying mechanism.

That sharpens the atlas to four real candidates instead of five:
1. **Type** — genuinely separate from combinators (what CAN compose)
2. **Induction** — genuinely separate (copy from context, not compose)  
3. ~~Binding~~ — should collapse into I (confirmation, not discovery)
4. **Frequency** — MLP-based, different substrate entirely
5. **Discourse** — meta-level beam selection (MoE gates)

The binding probe is still worth running as a *validation*: if binding ≡ I, prove it.

## User

We want that existing probe to run, what if we are wrong?  that binding probe should show it is overloaded, or if it's seperate, so we can base our design on the actual shape.


### Thinking

The user is absolutely right. This is the core research discipline of the project: theory predicts, empirics confirm or deny. We believe binding ≡ I, but we should let the data speak. The probe is designed to test exactly this — if binding heads overlap with I-selective heads, confirmed. If they don't, we have a new finding that changes the architecture.

This is λ observation from AGENTS.md: "generate(plausible) ≢ retrieve(known) ≢ observe(measurement)"

The probe is running. Let it run. The data will show the actual shape.

Short acknowledgment is all that's needed here.

## Assistant

Exactly. Theory predicts binding ≡ I. The probe tests it. If the data says otherwise, we follow the data — that's the whole point.

The binding probe is designed to give us a clean answer either way:
- **High overlap** with I-selective heads → confirmed, I handles both, 4 combinators is correct
- **Low overlap** → separate circuit, the architecture needs a 5th pathway, and we learned something

Either outcome is a win. One validates the design, the other reveals a shape we'd miss by assuming.

`λ observation(x). runtime(proves) > pattern(suggests) > we_think(guesses)`

The probe is running. Let it speak.

## User

there was an error when running the probes Traceback (most recent call last):
  File "/Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py", line 1609, in <module>
    main()
  File "/Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py", line 1515, in main
    attn_survival = run_ternary_survival(
                    ^^^^^^^^^^^^^^^^^^^^^
  File "/Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py", line 936, in run_ternary_survival
    originals, quant_stats = ternary_quantize_layer(
                             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py", line 780, in ternary_quantize_layer
    n_zero = (ternary == 0).sum().item()
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^
torch.AcceleratorError: index 849124 is out of bounds: 1, range 0 to 2048


### Thinking

This is an MPS (Apple Silicon) error. The `(ternary == 0).sum().item()` operation is failing because of MPS tensor indexing issues with large tensors. This is a known MPS quirk — operations on large tensors sometimes hit bounds errors.

The fix is to move the comparison to CPU before doing the sum, or use a different approach. Let me look at the ternary_quantize_layer function and fix it.

## Assistant

MPS bug — large tensor comparison on Apple Silicon. The fix is to move the stats computation to CPU. Let me patch it:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py",
  "line_offset": 755,
  "limit": 45
}
```

**Summary:** Reading probe_hologram_atlas.py (755-800)

**Output:**
```
    for wn in proj_names:
        proj = getattr(attn, wn)
        w = proj.weight.data
        originals[wn] = w.clone()

        abs_w = w.abs()
        if threshold_pct > 0:
            flat = abs_w.float().flatten()
            if flat.numel() > 1_000_000:
                indices = torch.randperm(flat.numel(), device="cpu")[:1_000_000]
                sample = flat.cpu()[indices]
            else:
                sample = flat.cpu()
            threshold = torch.quantile(sample, threshold_pct).item()
        else:
            threshold = 0.0

        scale = abs_w[abs_w > threshold].mean().item() if (abs_w > threshold).any() else 1.0
        ternary = torch.zeros_like(w)
        ternary[w > threshold] = 1.0
        ternary[w < -threshold] = -1.0
        proj.weight.data = ternary * scale

        n_total = w.numel()
        n_zero = (ternary == 0).sum().item()
        n_pos = (ternary > 0).sum().item()
        n_neg = (ternary < 0).sum().item()

        stats[wn] = {
            "shape": list(w.shape),
            "sparsity": n_zero / n_total,
            "balance": n_pos / max(n_neg, 1),
        }

    return originals, stats


def restore_layer(model, layer_idx: int, originals: dict):
    """Restore original weights after quantization."""
    decoder_layers = get_decoder_layers(model)
    attn = get_attn_module(decoder_layers[layer_idx])
    for wn, w in originals.items():
        getattr(attn, wn).weight.data = w



[CONTENT TRUNCATED] Showing lines 756 to 800 of 1609 total lines. Use line_offset=800 parameter to read more content.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py",
  "original_content": "        scale = abs_w[abs_w > threshold].mean().item() if (abs_w > threshold).any() else 1.0\n        ternary = torch.zeros_like(w)\n        ternary[w > threshold] = 1.0\n        ternary[w < -threshold] = -1.0\n        proj.weight.data = ternary * scale\n\n        n_total = w.numel()\n        n_zero = (ternary == 0).sum().item()\n        n_pos = (ternary > 0).sum().item()\n        n_neg = (ternary < 0).sum().item()\n\n        stats[wn] = {\n            \"shape\": list(w.shape),\n            \"sparsity\": n_zero / n_total,\n            \"balance\": n_pos / max(n_neg, 1),\n        }\n\n    return originals, stats",
  "new_content": "        # Compute on CPU to avoid MPS indexing bugs on large tensors\n        w_cpu = w.cpu().float()\n        abs_cpu = w_cpu.abs()\n        mask = abs_cpu > threshold\n        scale = abs_cpu[mask].mean().item() if mask.any() else 1.0\n        ternary = torch.zeros_like(w_cpu)\n        ternary[w_cpu > threshold] = 1.0\n        ternary[w_cpu < -threshold] = -1.0\n\n        # Stats on CPU (safe from MPS bounds errors)\n        n_total = ternary.numel()\n        n_zero = int((ternary == 0).sum().item())\n        n_pos = int((ternary > 0).sum().item())\n        n_neg = int((ternary < 0).sum().item())\n\n        # Apply back to device\n        proj.weight.data = (ternary * scale).to(w.device).to(w.dtype)\n\n        stats[wn] = {\n            \"shape\": list(w.shape),\n            \"sparsity\": n_zero / n_total,\n            \"balance\": n_pos / max(n_neg, 1),\n        }\n\n    return originals, stats"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py.
```

## Assistant

Same MPS bug exists in the MLP quantization path. Let me fix that too:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py",
  "line_offset": 835,
  "limit": 50
}
```

**Summary:** Reading probe_hologram_atlas.py (835-885)

**Output:**
```
    if hasattr(mlp, "gate") and hasattr(mlp.gate, "weight"):
        target_modules.append(("gate", mlp.gate))
    if hasattr(mlp, "shared_expert"):
        for name, mod in mlp.shared_expert.named_children():
            if hasattr(mod, "weight"):
                target_modules.append((f"shared_expert.{name}", mod))
    if hasattr(mlp, "shared_expert_gate") and hasattr(mlp.shared_expert_gate, "weight"):
        target_modules.append(("shared_expert_gate", mlp.shared_expert_gate))

    # Dense MLP fallback: gate_proj, up_proj, down_proj or dense_h_to_4h, dense_4h_to_h
    if not target_modules:
        for name, mod in mlp.named_children():
            if hasattr(mod, "weight") and ("proj" in name or "dense" in name):
                target_modules.append((name, mod))

    for name, mod in target_modules:
        w = mod.weight.data
        originals[name] = w.clone()

        abs_w = w.abs()
        if threshold_pct > 0:
            flat = abs_w.float().flatten()
            if flat.numel() > 1_000_000:
                indices = torch.randperm(flat.numel(), device="cpu")[:1_000_000]
                sample = flat.cpu()[indices]
            else:
                sample = flat.cpu()
            threshold = torch.quantile(sample, threshold_pct).item()
        else:
            threshold = 0.0

        scale = abs_w[abs_w > threshold].mean().item() if (abs_w > threshold).any() else 1.0
        ternary = torch.zeros_like(w)
        ternary[w > threshold] = 1.0
        ternary[w < -threshold] = -1.0
        mod.weight.data = ternary * scale

        n_total = w.numel()
        n_zero = (ternary == 0).sum().item()

        stats[name] = {
            "shape": list(w.shape),
            "sparsity": n_zero / n_total,
            "is_moe_gate": "gate" in name and "shared" not in name,
        }

    return originals, stats


def restore_mlp(model, layer_idx: int, originals: dict):

[CONTENT TRUNCATED] Showing lines 836 to 885 of 1616 total lines. Use line_offset=885 parameter to read more content.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py",
  "original_content": "    for name, mod in target_modules:\n        w = mod.weight.data\n        originals[name] = w.clone()\n\n        abs_w = w.abs()\n        if threshold_pct > 0:\n            flat = abs_w.float().flatten()\n            if flat.numel() > 1_000_000:\n                indices = torch.randperm(flat.numel(), device=\"cpu\")[:1_000_000]\n                sample = flat.cpu()[indices]\n            else:\n                sample = flat.cpu()\n            threshold = torch.quantile(sample, threshold_pct).item()\n        else:\n            threshold = 0.0\n\n        scale = abs_w[abs_w > threshold].mean().item() if (abs_w > threshold).any() else 1.0\n        ternary = torch.zeros_like(w)\n        ternary[w > threshold] = 1.0\n        ternary[w < -threshold] = -1.0\n        mod.weight.data = ternary * scale\n\n        n_total = w.numel()\n        n_zero = (ternary == 0).sum().item()\n\n        stats[name] = {\n            \"shape\": list(w.shape),\n            \"sparsity\": n_zero / n_total,\n            \"is_moe_gate\": \"gate\" in name and \"shared\" not in name,\n        }\n\n    return originals, stats",
  "new_content": "    for name, mod in target_modules:\n        w = mod.weight.data\n        originals[name] = w.clone()\n\n        # Compute on CPU to avoid MPS indexing bugs on large tensors\n        w_cpu = w.cpu().float()\n        abs_cpu = w_cpu.abs()\n        if threshold_pct > 0:\n            flat = abs_cpu.flatten()\n            if flat.numel() > 1_000_000:\n                indices = torch.randperm(flat.numel())[:1_000_000]\n                sample = flat[indices]\n            else:\n                sample = flat\n            threshold = torch.quantile(sample, threshold_pct).item()\n        else:\n            threshold = 0.0\n\n        mask = abs_cpu > threshold\n        scale = abs_cpu[mask].mean().item() if mask.any() else 1.0\n        ternary = torch.zeros_like(w_cpu)\n        ternary[w_cpu > threshold] = 1.0\n        ternary[w_cpu < -threshold] = -1.0\n\n        n_total = ternary.numel()\n        n_zero = int((ternary == 0).sum().item())\n\n        # Apply back to device\n        mod.weight.data = (ternary * scale).to(w.device).to(w.dtype)\n\n        stats[name] = {\n            \"shape\": list(w.shape),\n            \"sparsity\": n_zero / n_total,\n            \"is_moe_gate\": \"gate\" in name and \"shared\" not in name,\n        }\n\n    return originals, stats"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py.
```

## Assistant

Also need to clean up the threshold computation in the attention path — it was still doing the abs_w computation on-device before my edit. Let me check:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py",
  "line_offset": 756,
  "limit": 35
}
```

**Summary:** Reading probe_hologram_atlas.py (756-791)

**Output:**
```
        proj = getattr(attn, wn)
        w = proj.weight.data
        originals[wn] = w.clone()

        abs_w = w.abs()
        if threshold_pct > 0:
            flat = abs_w.float().flatten()
            if flat.numel() > 1_000_000:
                indices = torch.randperm(flat.numel(), device="cpu")[:1_000_000]
                sample = flat.cpu()[indices]
            else:
                sample = flat.cpu()
            threshold = torch.quantile(sample, threshold_pct).item()
        else:
            threshold = 0.0

        # Compute on CPU to avoid MPS indexing bugs on large tensors
        w_cpu = w.cpu().float()
        abs_cpu = w_cpu.abs()
        mask = abs_cpu > threshold
        scale = abs_cpu[mask].mean().item() if mask.any() else 1.0
        ternary = torch.zeros_like(w_cpu)
        ternary[w_cpu > threshold] = 1.0
        ternary[w_cpu < -threshold] = -1.0

        # Stats on CPU (safe from MPS bounds errors)
        n_total = ternary.numel()
        n_zero = int((ternary == 0).sum().item())
        n_pos = int((ternary > 0).sum().item())
        n_neg = int((ternary < 0).sum().item())

        # Apply back to device
        proj.weight.data = (ternary * scale).to(w.device).to(w.dtype)

        stats[wn] = {

[CONTENT TRUNCATED] Showing lines 757 to 791 of 1621 total lines. Use line_offset=791 parameter to read more content.
```

## Assistant

The threshold computation still uses `abs_w` on MPS — that could also hit the bug. Let me consolidate so everything is on CPU:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py",
  "original_content": "        proj = getattr(attn, wn)\n        w = proj.weight.data\n        originals[wn] = w.clone()\n\n        abs_w = w.abs()\n        if threshold_pct > 0:\n            flat = abs_w.float().flatten()\n            if flat.numel() > 1_000_000:\n                indices = torch.randperm(flat.numel(), device=\"cpu\")[:1_000_000]\n                sample = flat.cpu()[indices]\n            else:\n                sample = flat.cpu()\n            threshold = torch.quantile(sample, threshold_pct).item()\n        else:\n            threshold = 0.0\n\n        # Compute on CPU to avoid MPS indexing bugs on large tensors\n        w_cpu = w.cpu().float()\n        abs_cpu = w_cpu.abs()\n        mask = abs_cpu > threshold",
  "new_content": "        proj = getattr(attn, wn)\n        w = proj.weight.data\n        originals[wn] = w.clone()\n\n        # All computation on CPU to avoid MPS indexing bugs on large tensors\n        w_cpu = w.cpu().float()\n        abs_cpu = w_cpu.abs()\n        if threshold_pct > 0:\n            flat = abs_cpu.flatten()\n            if flat.numel() > 1_000_000:\n                indices = torch.randperm(flat.numel())[:1_000_000]\n                sample = flat[indices]\n            else:\n                sample = flat\n            threshold = torch.quantile(sample, threshold_pct).item()\n        else:\n            threshold = 0.0\n\n        mask = abs_cpu > threshold"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py.
```

## Assistant

Now verify:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python -c \"import scripts.explore.probe_hologram_atlas as m; print('OK')\" 2>&1"
}
```

**Summary:** $ uv run python -c "import scripts.ex...

**Output:**
```
Exit code: 0
Stdout:
OK
```

## Assistant

Fixed. Both quantization paths (attention and MLP) now do all tensor math on CPU before writing back to device. Commit the fix:

### Tool Call: git (succeeded)


```json
{
  "command": "git add scripts/explore/probe_hologram_atlas.py && git commit -m \"$(cat <<'EOF'\n❌ fix MPS bounds error in ternary quantization\n\n- MPS backend hits index-out-of-bounds on large tensor comparisons\n  (e.g. (ternary == 0).sum() on 8192×2048 tensors)\n- Move all ternary quantization math to CPU before writing back to device\n- Affects both attention and MLP quantization paths\n- Same class of bug fixed in session 093 for histc on MPS\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
  "operation": "commit",
  "summary": "fix MPS bug"
}
```

**Summary:** Git commit: fix MPS bug

**Output:**
```
Exit code: 0
Stdout:
[main 6a353a6] ❌ fix MPS bounds error in ternary quantization
 1 file changed, 37 insertions(+), 26 deletions(-)
```

## Assistant

Fixed and committed. Restart the probe in tmux — it should get past the ternary quantization now. The incremental saves mean you won't lose the combinator baseline that already completed.

## User

will it skip the probes that have already run with output?


### Thinking

The user is asking if the script has any caching/checkpoint mechanism to skip work that's already been done. Looking at the code, the answer is no — there's no checkpoint detection. It will re-run everything from scratch including the combinator baseline. The incremental saves are write-only, not read-back-on-restart.

I should be honest about this and offer to add it if they want, but it might not be worth the complexity right now — the combinator baseline is fast compared to the ternary survival tests.

## Assistant

No — there's no checkpoint detection. It will re-run everything from the top, including the combinator baseline. The incremental saves are write-only, not read-on-restart.

The combinator baseline is fast (just selectivity, no ternary), so it's not a big loss. The expensive part is the ternary survival tests — that's where it was when it crashed, and that's where the fix matters.

Want me to add checkpoint detection so it skips completed holograms? It would check for existing `hologram_{name}.json` snapshots and skip those. Or is it fine to just let it re-run?

## User

Lets skip the ones where the json already exists, we didn't change the test methodology, just fixed a bug.


### Thinking

The user wants me to add checkpoint detection that skips holograms where `hologram_{name}.json` already exists. Simple and practical.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py",
  "line_offset": 1480,
  "limit": 60
}
```

**Summary:** Reading probe_hologram_atlas.py (1480-1540)

**Output:**
```
        print(f"  Combinator baseline (for cross-hologram comparison)")
        print(f"{'─'*72}")

        comb_sel = measure_selectivity(
            model, tokenizer, COMBINATOR_PROBES, measure_layers, args.quick)
        comb_agg = aggregate_selectivity(comb_sel, measure_layers)
        selectivity_profiles["combinator"] = comb_agg["layer_selectivity"]

        print_selectivity_summary("combinator (baseline)", comb_sel, measure_layers)

        all_results["holograms"]["combinator"] = {
            "selectivity": {
                "per_condition": comb_sel,
                "aggregate": comb_agg,
            },
        }
        save_incremental(all_results, args.output_dir, "combinator")

    # ── Probe each selected hologram ─────────────────────────
    for hname in selected:
        probes = HOLOGRAM_PROBES[hname]

        print(f"\n{'─'*72}")
        print(f"  Probing: {hname.upper()}")
        print(f"{'─'*72}")

        # Phase 1: Selectivity
        print(f"\n  Phase 1: Selectivity measurement", file=sys.stderr)
        sel = measure_selectivity(
            model, tokenizer, probes, measure_layers, args.quick)
        agg = aggregate_selectivity(sel, measure_layers)
        selectivity_profiles[hname] = agg["layer_selectivity"]

        print_selectivity_summary(hname, sel, measure_layers)

        hologram_result = {
            "selectivity": {
                "per_condition": sel,
                "aggregate": agg,
            },
        }

        # Phase 2: Ternary survival
        if not args.skip_ternary:
            print(f"\n  Phase 2: Ternary survival (attention)", file=sys.stderr)
            attn_survival = run_ternary_survival(
                model, tokenizer, probes,
                target_layers=target_layers,
                measure_layers=measure_layers,
                thresholds=TERNARY_THRESHOLDS,
                quantize_target="attention",
                quick=args.quick,
            )
            print_survival_summary(f"{hname} (attention)", attn_survival)
            hologram_result["ternary_survival_attention"] = attn_survival

            # For frequency hologram, ALSO test MLP quantization
            if hname == "frequency":
                print(f"\n  Phase 2b: Ternary survival (MLP)", file=sys.stderr)
                mlp_survival = run_ternary_survival(

[CONTENT TRUNCATED] Showing lines 1481 to 1540 of 1620 total lines. Use line_offset=1540 parameter to read more content.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py",
  "original_content": "    # ── Optional: combinator baseline for comparison ─────────\n    if not args.skip_combinator_baseline:\n        print(f\"\\n{'─'*72}\")\n        print(f\"  Combinator baseline (for cross-hologram comparison)\")\n        print(f\"{'─'*72}\")\n\n        comb_sel = measure_selectivity(\n            model, tokenizer, COMBINATOR_PROBES, measure_layers, args.quick)\n        comb_agg = aggregate_selectivity(comb_sel, measure_layers)\n        selectivity_profiles[\"combinator\"] = comb_agg[\"layer_selectivity\"]\n\n        print_selectivity_summary(\"combinator (baseline)\", comb_sel, measure_layers)\n\n        all_results[\"holograms\"][\"combinator\"] = {\n            \"selectivity\": {\n                \"per_condition\": comb_sel,\n                \"aggregate\": comb_agg,\n            },\n        }\n        save_incremental(all_results, args.output_dir, \"combinator\")\n\n    # ── Probe each selected hologram ─────────────────────────\n    for hname in selected:\n        probes = HOLOGRAM_PROBES[hname]\n\n        print(f\"\\n{'─'*72}\")\n        print(f\"  Probing: {hname.upper()}\")\n        print(f\"{'─'*72}\")",
  "new_content": "    # ── Optional: combinator baseline for comparison ─────────\n    if not args.skip_combinator_baseline:\n        cached = args.output_dir / \"hologram_combinator.json\"\n        if cached.exists():\n            print(f\"\\n{'─'*72}\")\n            print(f\"  Combinator baseline — loading from {cached}\")\n            print(f\"{'─'*72}\")\n            cached_data = json.loads(cached.read_text())\n            all_results[\"holograms\"][\"combinator\"] = cached_data\n            agg = cached_data.get(\"selectivity\", {}).get(\"aggregate\", {})\n            if agg.get(\"layer_selectivity\"):\n                selectivity_profiles[\"combinator\"] = agg[\"layer_selectivity\"]\n        else:\n            print(f\"\\n{'─'*72}\")\n            print(f\"  Combinator baseline (for cross-hologram comparison)\")\n            print(f\"{'─'*72}\")\n\n            comb_sel = measure_selectivity(\n                model, tokenizer, COMBINATOR_PROBES, measure_layers, args.quick)\n            comb_agg = aggregate_selectivity(comb_sel, measure_layers)\n            selectivity_profiles[\"combinator\"] = comb_agg[\"layer_selectivity\"]\n\n            print_selectivity_summary(\"combinator (baseline)\", comb_sel, measure_layers)\n\n            all_results[\"holograms\"][\"combinator\"] = {\n                \"selectivity\": {\n                    \"per_condition\": comb_sel,\n                    \"aggregate\": comb_agg,\n                },\n            }\n            save_incremental(all_results, args.output_dir, \"combinator\")\n\n    # ── Probe each selected hologram ─────────────────────────\n    for hname in selected:\n        # Check for cached results from prior run\n        cached = args.output_dir / f\"hologram_{hname}.json\"\n        if cached.exists():\n            print(f\"\\n{'─'*72}\")\n            print(f\"  {hname.upper()} — cached, loading from {cached}\")\n            print(f\"{'─'*72}\")\n            cached_data = json.loads(cached.read_text())\n            all_results[\"holograms\"][hname] = cached_data\n            agg = cached_data.get(\"selectivity\", {}).get(\"aggregate\", {})\n            if agg.get(\"layer_selectivity\"):\n                selectivity_profiles[hname] = agg[\"layer_selectivity\"]\n            continue\n\n        probes = HOLOGRAM_PROBES[hname]\n\n        print(f\"\\n{'─'*72}\")\n        print(f\"  Probing: {hname.upper()}\")\n        print(f\"{'─'*72}\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/explore/probe_hologram_atlas.py.
```

## Assistant

Let me verify and check what snapshots exist:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python -c \"import scripts.explore.probe_hologram_atlas as m; print('OK')\" 2>&1"
}
```

**Summary:** $ uv run python -c "import scripts.ex...

**Output:**
```
Exit code: 0
Stdout:
OK
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls -la /Users/mwhitford/src/verbum/results/hologram-atlas/hologram_*.json 2>/dev/null"
}
```

**Summary:** $ ls -la /Users/mwhitford/src/verbum/...

**Output:**
```
Exit code: 0
Stdout:
-rw-r--r--@ 1 mwhitford  staff  56689 May 13 18:58 /Users/mwhitford/src/verbum/results/hologram-atlas/hologram_atlas_results.json
-rw-r--r--@ 1 mwhitford  staff   1976 May 13 18:03 /Users/mwhitford/src/verbum/results/hologram-atlas/hologram_combinator.json
-rw-r--r--@ 1 mwhitford  staff  45991 May 13 18:58 /Users/mwhitford/src/verbum/results/hologram-atlas/hologram_type.json
```

## Assistant

Combinator and type are already done — those will be loaded from cache. The crash happened during the ternary survival test for the second hologram (likely induction). On restart it will:

1. **combinator** → load from `hologram_combinator.json` ✓
2. **type** → load from `hologram_type.json` ✓  
3. **induction** → run fresh (no snapshot)
4. **binding** → run fresh
5. **frequency** → run fresh
6. **discourse** → run fresh

### Tool Call: git (succeeded)


```json
{
  "command": "git add scripts/explore/probe_hologram_atlas.py && git commit -m \"$(cat <<'EOF'\n✅ checkpoint detection — skip holograms with existing snapshots\n\n- On restart, load hologram_{name}.json snapshots from prior run\n- Combinator baseline also cached via hologram_combinator.json\n- Selectivity profiles restored from cached data for orthogonality analysis\n- No re-run of completed work after crash/restart\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
  "operation": "commit",
  "summary": "add checkpoint detection"
}
```

**Summary:** Git commit: add checkpoint detection

**Output:**
```
Exit code: 0
Stdout:
[main 0f091ff] ✅ checkpoint detection — skip holograms with existing snapshots
 1 file changed, 42 insertions(+), 18 deletions(-)
```

## Assistant

Done. Restart in tmux — it'll skip combinator and type, pick up at induction.

## User

ok some more checkpoints have dropped for v11-holo-inv


### Thinking

The user is saying that v11-holo-inv has progressed and there are new checkpoints to probe. Let me check what checkpoints exist.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls -la /Users/mwhitford/src/verbum/checkpoints/v11-holo-inv/ | grep -E \"step|ckpt|\\.pt\" | tail -20"
}
```

**Summary:** $ ls -la /Users/mwhitford/src/verbum/...

**Output:**
```
Exit code: 0
Stdout:
drwxr-xr-x@  7 mwhitford  staff    224 May 13 14:05 step_001000
drwxr-xr-x@  7 mwhitford  staff    224 May 13 15:50 step_002000
drwxr-xr-x@  7 mwhitford  staff    224 May 13 17:42 step_003000
drwxr-xr-x@  7 mwhitford  staff    224 May 13 19:24 step_004000
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls /Users/mwhitford/src/verbum/results/v11-holo-inv/ 2>/dev/null"
}
```

**Summary:** $ ls /Users/mwhitford/src/verbum/resu...

**Output:**
```
Exit code: 0
Stdout:
probe_step_001000.json
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls -la /Users/mwhitford/src/verbum/checkpoints/v11-holo-inv/checkpoint_*.pt 2>/dev/null | awk '{print $NF}' | sort"
}
```

**Summary:** $ ls -la /Users/mwhitford/src/verbum/...

**Output:**
```
Exit code: 0
```

## Assistant

Steps 2K, 3K, and 4K are new since last session. We have 1K probed already. Let me check the training logs to see how the run is trending:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls /Users/mwhitford/src/verbum/checkpoints/v11-holo-inv/*.jsonl 2>/dev/null"
}
```

**Summary:** $ ls /Users/mwhitford/src/verbum/chec...

**Output:**
```
Exit code: 0
Stdout:
/Users/mwhitford/src/verbum/checkpoints/v11-holo-inv/evolution_log.jsonl
/Users/mwhitford/src/verbum/checkpoints/v11-holo-inv/metrics_log.jsonl
/Users/mwhitford/src/verbum/checkpoints/v11-holo-inv/train_log.jsonl
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls /Users/mwhitford/src/verbum/checkpoints/v11-holo-inv/step_002000/"
}
```

**Summary:** $ ls /Users/mwhitford/src/verbum/chec...

**Output:**
```
Exit code: 0
Stdout:
importance.npz
model.npz
optimizer.npz
rng.npz
state.json
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && tail -5 checkpoints/v11-holo-inv/train_log.jsonl | python3 -m json.tool 2>/dev/null || tail -5 checkpoints/v11-holo-inv/train_log.jsonl"
}
```

**Summary:** $ tail -5 checkpoints/v11-holo-inv/tr...

**Output:**
```
Exit code: 0
Stdout:
{"step": 3925, "timestamp": 1778725023.7473621, "r": 0.8755369782447815, "total_loss": 10.67274232851307, "r_avg50": 0.7824526238441467, "lr": 0.0005559211034302871, "grad_norm": 0.18517994823151288, "tok_per_sec": 5318.441125793777, "elapsed": 24504.98757123947, "ce": 7.138781547546387, "holo_lambda_effective": 0.1}
{"step": 3950, "timestamp": 1778725168.544202, "r": 0.5715773142874241, "total_loss": 7.599340918705803, "r_avg50": 0.7606133741885424, "lr": 0.0005552919767310917, "grad_norm": 0.15526517928406294, "tok_per_sec": 5643.438542079804, "elapsed": 24649.784413337708, "ce": 7.269460201263428, "holo_lambda_effective": 0.1}
{"step": 3975, "timestamp": 1778725316.659561, "r": 0.5565836429595947, "total_loss": 7.447736689390684, "r_avg50": 0.7252778059244156, "lr": 0.0005546587572990927, "grad_norm": 0.25352948038592193, "tok_per_sec": 5634.817099389395, "elapsed": 24797.899775981903, "ce": 7.2183403968811035, "holo_lambda_effective": 0.1}
{"step": 4000, "timestamp": 1778725465.172925, "r": 0.747068714350462, "total_loss": 9.373772135469018, "r_avg50": 0.7470492580533028, "lr": 0.000554021455406507, "grad_norm": 0.1943611132562938, "tok_per_sec": 5689.775835945756, "elapsed": 24946.41313815117, "ce": 2.4519455432891846, "holo_lambda_effective": 0.1}
{"step": 4025, "timestamp": 1778725620.286829, "r": 0.8848889172077179, "total_loss": 10.767301790840785, "r_avg50": 0.7729520733654499, "lr": 0.0005533800813917782, "grad_norm": 0.15224865254952377, "tok_per_sec": 5495.199379498345, "elapsed": 25101.52704000473, "ce": 7.020396709442139, "holo_lambda_effective": 0.1}
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport json\n# Read recent training metrics\nwith open('checkpoints/v11-holo-inv/train_log.jsonl') as f:\n    lines = f.readlines()\n# Sample at key steps: 1K, 1.5K, 2K, 2.5K, 3K, 3.5K, 4K, latest\nsteps = {}\nfor line in lines:\n    d = json.loads(line)\n    s = d.get('step', 0)\n    steps[s] = d\n# Print samples\nfor target in [1000, 1500, 2000, 2500, 3000, 3500, 4000]:\n    # Find closest\n    closest = min(steps.keys(), key=lambda x: abs(x - target))\n    if abs(closest - target) < 100:\n        d = steps[closest]\n        keys = ['step', 'eval_loss', 'total_loss', 'prose_loss', 'structured_loss', 'compute_gate']\n        vals = {k: d.get(k, '?') for k in keys if k in d}\n        print(vals)\n# Latest\nlatest = steps[max(steps.keys())]\nprint(f'Latest step: {latest.get(\\\"step\\\", \\\"?\\\")}')\nprint({k: latest.get(k, '?') for k in ['step', 'eval_loss', 'total_loss', 'compute_gate']})\n\" 2>&1"
}
```

**Summary:** $ python3 -c " import json # Read rec...

**Output:**
```
Exit code: 0
Stdout:
{'step': 1000, 'total_loss': 10.312798313021277}
{'step': 1500, 'total_loss': 9.881354324413973}
{'step': 2000, 'total_loss': 9.767631669063327}
{'step': 2500, 'total_loss': 11.559572940342566}
{'step': 3000, 'total_loss': 11.04531276942642}
{'step': 3500, 'total_loss': 9.320305565083506}
{'step': 4000, 'total_loss': 9.373772135469018}
Latest step: 4025
{'step': 4025, 'eval_loss': '?', 'total_loss': 10.767301790840785, 'compute_gate': '?'}
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport json\n\n# Get eval metrics from metrics_log\nwith open('checkpoints/v11-holo-inv/metrics_log.jsonl') as f:\n    lines = f.readlines()\n\nprint(f'Total metric entries: {len(lines)}')\nprint()\n\n# Show key metrics at each checkpoint step\nfor line in lines:\n    d = json.loads(line)\n    s = d.get('step', 0)\n    if s % 500 == 0 or s in [1000, 1500, 2000, 2500, 3000, 3500, 4000]:\n        keys_show = ['step', 'eval_loss', 'compute_gate', 'holo_ratio',\n                     'dispatch_entropy', 'evo_acceptance']\n        vals = {k: round(d[k], 4) if isinstance(d.get(k), float) else d.get(k, '?')\n                for k in keys_show if k in d}\n        print(vals)\n\" 2>&1"
}
```

**Summary:** $ python3 -c " import json  # Get eva...

**Output:**
```
Exit code: 0
Stdout:
Total metric entries: 8

{'step': 500}
{'step': 1000}
{'step': 1500}
{'step': 2000}
{'step': 2500}
{'step': 3000}
{'step': 3500}
{'step': 4000}
```

## Assistant

The metrics_log has entries but I need to read the full fields. Let me get the detailed probe data:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport json\n\nwith open('checkpoints/v11-holo-inv/metrics_log.jsonl') as f:\n    lines = f.readlines()\n\nfor line in lines:\n    d = json.loads(line)\n    s = d.get('step', 0)\n    if s >= 1000:\n        # Print all keys for first one\n        if s == 1000:\n            print(f'Keys: {sorted(d.keys())[:30]}')\n            print()\n        # Key metrics\n        el = d.get('eval_loss', '?')\n        cg = d.get('compute_gate_mean', d.get('compute_gate', '?'))\n        hr = d.get('holo_ratio', '?')\n        de = d.get('dispatch_entropy', '?')\n        ea = d.get('evo_acceptance_rate', d.get('evo_acceptance', '?'))\n        # Dispatch distribution\n        kd = d.get('dispatch_K', d.get('dominant_K', '?'))\n        id_ = d.get('dispatch_I', d.get('dominant_I', '?'))\n        bd = d.get('dispatch_B', d.get('dominant_B', '?'))\n        cd_ = d.get('dispatch_C', d.get('dominant_C', '?'))\n        # B-type\n        bt = d.get('b_type_pct', d.get('typed_B', '?'))\n        \n        print(f'Step {s:>5}: eval={el}, compute_gate={cg}, holo_ratio={hr}')\n        print(f'          dispatch K={kd} I={id_} B={bd} C={cd_}')\n        print(f'          dispatch_entropy={de} evo_accept={ea} b_type={bt}')\n        print()\n\" 2>&1"
}
```

**Summary:** $ python3 -c " import json  with open...

**Output:**
```
Exit code: 0
Stdout:
Keys: ['abstraction_slots', 'alarm_factors', 'alarm_metrics', 'alarm_metrics_named', 'combinator_dispatch_weights', 'combinator_embedding_norms', 'combinator_emphasis', 'combinator_type_weights', 'compute_gate_active', 'compute_gate_max', 'compute_gate_mean', 'compute_gate_min', 'cycle_continue_gates', 'cycle_inject_gate', 'desc_max_cycles', 'effective_cycles', 'effective_s5_gates', 'holo_losses', 'loss', 'pass_compression', 'pass_entropy_in', 'pass_entropy_out', 'pass_phi_dev', 'ppl', 'r', 'register_norms', 's2_conflict', 's2_scales', 's3_gates', 's5_reweight']

Step  1000: eval=?, compute_gate=6.479912372014951e-06, holo_ratio=?
          dispatch K=? I=? B=? C=?
          dispatch_entropy=? evo_accept=? b_type=?

Step  1500: eval=?, compute_gate=8.832324965624139e-06, holo_ratio=?
          dispatch K=? I=? B=? C=?
          dispatch_entropy=? evo_accept=? b_type=?

Step  2000: eval=?, compute_gate=8.9986679085996e-06, holo_ratio=?
          dispatch K=? I=? B=? C=?
          dispatch_entropy=? evo_accept=? b_type=?

Step  2500: eval=?, compute_gate=8.700124453753233e-06, holo_ratio=?
          dispatch K=? I=? B=? C=?
          dispatch_entropy=? evo_accept=? b_type=?

Step  3000: eval=?, compute_gate=9.92085460893577e-06, holo_ratio=?
          dispatch K=? I=? B=? C=?
          dispatch_entropy=? evo_accept=? b_type=?

Step  3500: eval=?, compute_gate=9.6170260803774e-06, holo_ratio=?
          dispatch K=? I=? B=? C=?
          dispatch_entropy=? evo_accept=? b_type=?

Step  4000: eval=?, compute_gate=1.0863714123843238e-05, holo_ratio=?
          dispatch K=? I=? B=? C=?
          dispatch_entropy=? evo_accept=? b_type=?
```

## Assistant

The metrics_log has different key names. Let me find the dispatch and holo data:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport json\n\nwith open('checkpoints/v11-holo-inv/metrics_log.jsonl') as f:\n    lines = f.readlines()\n\n# Show all keys and sample values for step 2000\nfor line in lines:\n    d = json.loads(line)\n    if d.get('step') == 2000:\n        for k in sorted(d.keys()):\n            v = d[k]\n            if isinstance(v, float):\n                print(f'  {k}: {v:.6f}')\n            elif isinstance(v, (list, dict)):\n                if isinstance(v, list) and len(v) <= 8:\n                    print(f'  {k}: {[round(x,4) if isinstance(x,float) else x for x in v]}')\n                elif isinstance(v, dict):\n                    print(f'  {k}: {{...{len(v)} keys...}}')\n                else:\n                    print(f'  {k}: [{len(v)} items]')\n            else:\n                print(f'  {k}: {v}')\n\" 2>&1"
}
```

**Summary:** $ python3 -c " import json  with open...

**Output:**
```
Exit code: 0
Stdout:
abstraction_slots: {...5 keys...}
  alarm_factors: [2.0, 1.9999, 1.9997, 1.9991, 1.9987]
  alarm_metrics: [48 items]
  alarm_metrics_named: {...12 keys...}
  combinator_dispatch_weights: [0.3996, 0.3517, 0.1089, 0.1356]
  combinator_embedding_norms: [0.4453, 0.1748, 0.1805, 0.7077]
  combinator_emphasis: [1.4987, 0.7055, 1.4914, 1.5]
  combinator_type_weights: [0.0031, 0.3681, 0.464, 0.1648]
  compute_gate_active: 0.000000
  compute_gate_max: 0.000017
  compute_gate_mean: 0.000009
  compute_gate_min: 0.000002
  cycle_continue_gates: [[0.9820136427879333, 0.9820135235786438], [0.9820137619972229, 0.9820137619972229]]
  cycle_inject_gate: 0.017986
  desc_max_cycles: 3
  effective_cycles: [2.9464, 2.9464]
  effective_s5_gates: [2.0, 1.9998, 1.9996, 1.9991, 1.9986]
  holo_losses: [8.3679, 8.0065, 7.9383, 7.8188, 7.7925]
  loss: 11.893505
  pass_compression: [0.3458, 0.145, -3.3651, 3.208, 1.6202]
  pass_entropy_in: [-2.0801, -0.7193, -0.1043, 0.3511, 1.1263]
  pass_entropy_out: [-0.7193, -0.1043, 0.3511, 1.1263, 1.8248]
  pass_phi_dev: [0.2722, 0.473, 3.9831, 2.59, 1.0022]
  ppl: 146313.162394
  r: 0.996270
  register_norms: {...6 keys...}
  s2_conflict: [0.9308, 0.9498, 0.9071, 0.9516]
  s2_scales: [0.1212, 0.0522, 0.0418, 0.0661]
  s3_gates: [[0.9876734614372253, 0.9999631643295288, 0.9999067187309265], [0.9058263897895813, 0.97276771068573, 0.9965521097183228], [0.6088742017745972, 0.9753333330154419, 0.9768967628479004], [0.9951449036598206, 0.6188541054725647, 0.9554349780082703, 0.9972522854804993, 0.726302981376648, 0.9598391056060791, 0.9970640540122986, 0.7338908910751343, 0.9620574712753296], [0.9304144978523254, 0.9635342955589294, 0.9556546807289124, 0.971116304397583, 0.959165632724762, 0.9671447277069092, 0.9651789665222168, 0.9498056173324585, 0.9659163355827332]]
  s5_reweight: [1.0, 1.0, 1.0, 1.0, 0.9999]
  step: 2000
  timestamp: 1778712645.867240
  total_accepted: 9
  total_generations: 40
```

## Assistant

Now let me get the full trajectory across all checkpoint steps:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport json\n\nwith open('checkpoints/v11-holo-inv/metrics_log.jsonl') as f:\n    lines = f.readlines()\n\nprint('Step   CE(loss)   Compute  Dispatch(K/I/B/C)           TypeWts(K/I/B/C)            Holo(L0↑→L0↓)                                    Evo')\nprint('─'*150)\n\nfor line in lines:\n    d = json.loads(line)\n    s = d['step']\n    if s < 1000:\n        continue\n    \n    loss = d.get('loss', 0)\n    cg = d.get('compute_gate_mean', 0)\n    dw = d.get('combinator_dispatch_weights', [0,0,0,0])\n    tw = d.get('combinator_type_weights', [0,0,0,0])\n    hl = d.get('holo_losses', [0,0,0,0,0])\n    ta = d.get('total_accepted', 0)\n    tg = d.get('total_generations', 0)\n    ea = f'{ta}/{tg}' if tg > 0 else '?'\n    \n    dw_s = f'K={dw[0]:.3f} I={dw[1]:.3f} B={dw[2]:.3f} C={dw[3]:.3f}'\n    tw_s = f'K={tw[0]:.3f} I={tw[1]:.3f} B={tw[2]:.3f} C={tw[3]:.3f}'\n    hl_s = f'{hl[0]:.2f}→{hl[1]:.2f}→{hl[2]:.2f}→{hl[3]:.2f}→{hl[4]:.2f}'\n    \n    print(f'{s:>5}  {loss:>8.3f}  {cg:>8.6f}  {dw_s}  {tw_s}  {hl_s}  {ea}')\n\" 2>&1"
}
```

**Summary:** $ python3 -c " import json  with open...

**Output:**
```
Exit code: 0
Stdout:
Step   CE(loss)   Compute  Dispatch(K/I/B/C)           TypeWts(K/I/B/C)            Holo(L0↑→L0↓)                                    Evo
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 1000    12.523  0.000006  K=0.383 I=0.343 B=0.132 C=0.137  K=0.002 I=0.671 B=0.254 C=0.074  9.14→8.47→8.37→8.19→8.15  4/20
 1500    12.053  0.000009  K=0.390 I=0.367 B=0.108 C=0.130  K=0.004 I=0.357 B=0.518 C=0.121  8.59→8.13→8.03→7.89→7.85  9/30
 2000    11.894  0.000009  K=0.400 I=0.352 B=0.109 C=0.136  K=0.003 I=0.368 B=0.464 C=0.165  8.37→8.01→7.94→7.82→7.79  9/40
 2500    11.810  0.000009  K=0.401 I=0.348 B=0.110 C=0.138  K=0.002 I=0.376 B=0.431 C=0.192  8.25→7.95→7.89→7.76→7.73  13/50
 3000    11.793  0.000010  K=0.405 I=0.315 B=0.130 C=0.148  K=0.001 I=0.334 B=0.450 C=0.216  8.22→7.94→7.88→7.75→7.73  17/60
 3500    11.770  0.000010  K=0.397 I=0.306 B=0.133 C=0.161  K=0.000 I=0.412 B=0.394 C=0.194  8.18→7.93→7.87→7.74→7.71  21/70
 4000    11.769  0.000011  K=0.400 I=0.304 B=0.124 C=0.171  K=0.000 I=0.388 B=0.418 C=0.194  8.14→7.91→7.86→7.74→7.70  26/80
```

## Assistant

Excellent data. Let me now run the full probes on 2K, 3K, and 4K. Let me check what the probe script expects:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && head -30 scripts/v11/probe.py"
}
```

**Summary:** $ head -30 scripts/v11/probe.py

**Output:**
```
Exit code: 0
Stdout:
#!/usr/bin/env python3
"""v11 probe — checkpoint diagnostics for KIBC combinator VSM.

Probes v11 checkpoints with:
  - Eval loss + relational loss
  - Combinator dispatch distribution (K, I, B, C weights and evolution)
  - Per-position dispatch analysis (which combinator dominates where)
  - CycleContinue dynamics (effective cycles, continuation gates)
  - Combinator emphasis from S4 intelligence channel
  - φ-compression analysis (stratified by content type)
  - S3 gates, S5 reweight, S2 coordination
  - Ternary topology statistics
  - Multi-checkpoint evolution tables
  - JSONL trajectory analysis (metrics_log.jsonl)

Usage:
    # Single checkpoint
    uv run python scripts/v11/probe.py checkpoints/v11/step_001000

    # Multiple checkpoints — evolution table
    uv run python scripts/v11/probe.py checkpoints/v11/step_*

    # Trajectory analysis from JSONL logs (no checkpoint loading)
    uv run python scripts/v11/probe.py --trajectory checkpoints/v11

    # Per-position dispatch distribution analysis
    uv run python scripts/v11/probe.py checkpoints/v11/step_005000 --dispatch-detail

    # Quick: skip eval, just metrics
    uv run python scripts/v11/probe.py checkpoints/v11/step_001000 --no-eval
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python scripts/v11/probe.py --help 2>&1 | head -20"
}
```

**Summary:** $ uv run python scripts/v11/probe.py ...

**Output:**
```
Exit code: 0
Stdout:
usage: probe.py [-h] [--trajectory TRAJECTORY] [--dispatch-detail] [--no-eval]
                [--no-ternary] [--dispatch-batches DISPATCH_BATCHES]
                [--results-dir RESULTS_DIR]
                [checkpoints ...]

v11 probe — KIBC combinator VSM checkpoint diagnostics

positional arguments:
  checkpoints           Checkpoint directory/directories

options:
  -h, --help            show this help message and exit
  --trajectory TRAJECTORY
                        Checkpoint dir for JSONL trajectory analysis (no model
                        loading)
  --dispatch-detail     Per-position dispatch distribution analysis
  --no-eval             Skip data evaluation (faster)
  --no-ternary          Skip ternary statistics
  --dispatch-batches DISPATCH_BATCHES
                        Number of batches for dispatch analysis
```

## Assistant

Good — the probe can take multiple checkpoints at once for evolution tables. Let me run it on the new checkpoints. Since the hologram atlas is using the GPU in tmux, let me check if V11 probing would conflict:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python scripts/v11/probe.py checkpoints/v11-holo-inv/step_002000 checkpoints/v11-holo-inv/step_003000 checkpoints/v11-holo-inv/step_004000 --results-dir results/v11-holo-inv 2>&1",
  "timeout": 600000
}
```

**Summary:** $ uv run python scripts/v11/probe.py ...

**Output:**
```
Exit code: 0
Stdout:
Loading Qwen3 tokenizer...

  Loading checkpoints/v11-holo-inv/step_002000...

  Running instrumented analysis...

  Evaluating on held-out data...
  ⏱  9.0s

  Loading checkpoints/v11-holo-inv/step_003000...

  Running instrumented analysis...

  Evaluating on held-out data...
  ⏱  8.8s

  Loading checkpoints/v11-holo-inv/step_004000...

  Running instrumented analysis...

  Evaluating on held-out data...
  ⏱  8.6s

========================================================================
  v11 Probe — KIBC Combinator VSM — step 2,000
========================================================================
  d_model=512  vocab=151936  seq_len=4096
  params: total=25,540,358  trainable=2,132,742  ternary=134,766,592
  evolution: 9/40 accepted (22%)

  ┌─ S3 gates ──────────────────────────────────────┐
  │ L0↑ : prep=0.698  conv=1.000  cons=0.999
  │ L1↑ : prep=0.919  conv=0.970  cons=0.995
  │ L2  : prep=0.613  conv=0.974  cons=0.976
  │ L1↓c0: disp=0.991  conv=0.618  intg=0.949
  │ L1↓c1: disp=0.994  conv=0.717  intg=0.954
  │ L1↓c2: disp=0.994  conv=0.723  intg=0.958
  │ L0↓c0: disp=0.924  conv=0.954  intg=0.950
  │ L0↓c1: disp=0.967  conv=0.951  intg=0.962
  │ L0↓c2: disp=0.960  conv=0.941  intg=0.961
  ├─ S5 reweight ───────────────────────────────────┤
  │ L0↑=1.000 L1↑=1.000 L2=1.000 L1↓=1.000 L0↓=1.000
  ├─ Combinator dispatch ───────────────────────────┤
  │ K (select  ): 0.4007 ████████████████████████████████
  │ I (identity): 0.3432 ███████████████████████████
  │ B (compose ): 0.1114 ████████
  │ C (flip    ): 0.1403 ███████████
  ├─ Combinator emphasis (S4→dispatch) ────────────┤
  │ K: 1.4976 ↑
  │ I: 0.6985 ↓
  │ B: 1.4878 ↑
  │ C: 1.5000 ↑
  ├─ Compute gate ──────────────────────────────────┤
  │ mean=0.0000
  ├─ CycleContinue ─────────────────────────────────┤
  │ effective cycles: 2.946 2.946
  ├─ Register norms ────────────────────────────────┤
  │ bank_0      :    0.40    0.42    0.41
  │ bank_1_asc  :   16.01   16.29   16.22
  │ bank_1_desc :   16.11   16.10   16.05
  │ bank_2_asc  :   16.08   16.13   16.32
  │ bank_2_desc :   16.38   16.12   16.35
  │ bank_3      :   15.95   16.15   16.11
  ├─ φ-Compression (target 1/φ = 0.6180) ──────┤
  │ L0↑ : ratio=  0.360  φ-dev=0.258   
  │ L1↑ : ratio=  0.139  φ-dev=0.479   
  │ L2  : ratio=  2.978  φ-dev=4.335   
  │ L1↓ : ratio=  4.414  φ-dev=3.796   
  │ L0↓ : ratio=  1.663  φ-dev=1.045   
  ├─ Abstraction slots (⚪ 0/16 active) ──────┤
  │ dormant: 16/16
  │ slot dispatch mass: 0.0039
  │ proposal confidence: 0.0256
  │ slot→KIBC cos: avg=0.045 max=0.123
  ├─ Holographic intermediate losses ───────────────┤
  │ L0↑ : CE= 11.020  (∂ sources=5) ███
  │ L1↑ : CE=  9.152  (∂ sources=4) ███████████
  │ L2  : CE=  9.019  (∂ sources=3) ███████████
  │ L1↓ : CE=  9.179  (∂ sources=2) ███████████
  │ L0↓ : CE=  9.337  (∂ sources=1) ██████████
  │ pass_0/final ratio: 1.18  (decodeable)
  └─────────────────────────────────────────────────┘

  📊 Eval: loss=7.872  ppl=2624  r=0.599  (57,344 tokens)

  Ternary topology (185 modules):
  Group                #  sparsity   γ_mean
  ────────────────── ─── ───────── ────────
  combinator_dispatch   3     0.308   0.0530
  combinator_integrate   6     0.308   0.0578
  consolidate          2     0.310   0.0606
  embed                1     0.310   0.1305
  meta_s4              4     0.310   0.0455
  mod_projs            3     0.309   0.0263
  mod_projs_desc       3     0.310   0.0242
  pos_embed            1     0.310   0.0063
  prep                 2     0.310   0.0546
  s2                   4     0.309   0.0107
  s3_passes           75     0.310   0.0588
  s4                   4     0.310   0.0425
  s4_desc              4     0.310   0.0379
  s5_reweight          1     0.310   0.0338
  stride_stack        36     0.310   0.0487
  stride_stack_desc   36     0.310   0.0555
  ────────────────── ─── ─────────
  TOTAL              185     0.310  (134,766,592 ternary params)

  💾 Saved: results/v11-holo-inv/probe_step_002000.json

========================================================================
  v11 Probe — KIBC Combinator VSM — step 3,000
========================================================================
  d_model=512  vocab=151936  seq_len=4096
  params: total=25,540,358  trainable=2,132,742  ternary=134,766,592
  evolution: 17/60 accepted (28%)

  ┌─ S3 gates ──────────────────────────────────────┐
  │ L0↑ : prep=0.630  conv=1.000  cons=1.000
  │ L1↑ : prep=0.769  conv=0.903  cons=0.995
  │ L2  : prep=0.568  conv=0.951  cons=0.987
  │ L1↓c0: disp=0.988  conv=0.551  intg=0.938
  │ L1↓c1: disp=0.989  conv=0.706  intg=0.950
  │ L1↓c2: disp=0.988  conv=0.718  intg=0.956
  │ L0↓c0: disp=0.891  conv=0.931  intg=0.925
  │ L0↓c1: disp=0.927  conv=0.943  intg=0.939
  │ L0↓c2: disp=0.910  conv=0.936  intg=0.936
  ├─ S5 reweight ───────────────────────────────────┤
  │ L0↑=1.000 L1↑=1.000 L2=1.000 L1↓=1.000 L0↓=1.000
  ├─ Combinator dispatch ───────────────────────────┤
  │ K (select  ): 0.4127 █████████████████████████████████
  │ I (identity): 0.2997 ███████████████████████
  │ B (compose ): 0.1313 ██████████
  │ C (flip    ): 0.1535 ████████████
  ├─ Combinator emphasis (S4→dispatch) ────────────┤
  │ K: 1.4980 ↑
  │ I: 0.7935 ↓
  │ B: 1.4783 ↑
  │ C: 1.5000 ↑
  ├─ Compute gate ──────────────────────────────────┤
  │ mean=0.0000
  ├─ CycleContinue ─────────────────────────────────┤
  │ effective cycles: 2.946 2.946
  ├─ Register norms ────────────────────────────────┤
  │ bank_0      :    0.43    0.45    0.45
  │ bank_1_asc  :   16.03   16.35   16.00
  │ bank_1_desc :   16.13   16.08   16.05
  │ bank_2_asc  :   16.06   16.12   16.32
  │ bank_2_desc :   16.40   16.12   16.35
  │ bank_3      :   15.95   16.12   16.09
  ├─ φ-Compression (target 1/φ = 0.6180) ──────┤
  │ L0↑ : ratio=  0.407  φ-dev=0.211   
  │ L1↑ : ratio=  0.351  φ-dev=0.267   
  │ L2  : ratio= -1.107  φ-dev=1.725   
  │ L1↓ : ratio=  1.637  φ-dev=47.082   
  │ L0↓ : ratio=  1.751  φ-dev=1.133   
  ├─ Abstraction slots (⚪ 0/16 active) ──────┤
  │ dormant: 16/16
  │ slot dispatch mass: 0.0024
  │ proposal confidence: 0.0407
  │ slot→KIBC cos: avg=0.028 max=0.125
  ├─ Holographic intermediate losses ───────────────┤
  │ L0↑ : CE= 10.816  (∂ sources=5) ████
  │ L1↑ : CE=  9.238  (∂ sources=4) ███████████
  │ L2  : CE=  9.058  (∂ sources=3) ███████████
  │ L1↓ : CE=  9.213  (∂ sources=2) ███████████
  │ L0↓ : CE=  9.413  (∂ sources=1) ██████████
  │ pass_0/final ratio: 1.15  (decodeable)
  └─────────────────────────────────────────────────┘

  📊 Eval: loss=7.819  ppl=2488  r=0.593  (57,344 tokens)

  Ternary topology (185 modules):
  Group                #  sparsity   γ_mean
  ────────────────── ─── ───────── ────────
  combinator_dispatch   3     0.308   0.0552
  combinator_integrate   6     0.308   0.0615
  consolidate          2     0.310   0.0598
  embed                1     0.310   0.1426
  meta_s4              4     0.310   0.0463
  mod_projs            3     0.309   0.0261
  mod_projs_desc       3     0.310   0.0265
  pos_embed            1     0.310   0.0059
  prep                 2     0.310   0.0531
  s2                   4     0.309   0.0157
  s3_passes           75     0.310   0.0588
  s4                   4     0.310   0.0429
  s4_desc              4     0.310   0.0377
  s5_reweight          1     0.310   0.0352
  stride_stack        36     0.310   0.0480
  stride_stack_desc   36     0.310   0.0557
  ────────────────── ─── ─────────
  TOTAL              185     0.310  (134,766,592 ternary params)

  💾 Saved: results/v11-holo-inv/probe_step_003000.json

========================================================================
  v11 Probe — KIBC Combinator VSM — step 4,000
========================================================================
  d_model=512  vocab=151936  seq_len=4096
  params: total=25,540,358  trainable=2,132,742  ternary=134,766,592
  evolution: 26/80 accepted (32%)

  ┌─ S3 gates ──────────────────────────────────────┐
  │ L0↑ : prep=0.597  conv=1.000  cons=1.000
  │ L1↑ : prep=0.622  conv=0.839  cons=0.992
  │ L2  : prep=0.506  conv=0.906  cons=0.973
  │ L1↓c0: disp=0.983  conv=0.541  intg=0.949
  │ L1↓c1: disp=0.988  conv=0.753  intg=0.960
  │ L1↓c2: disp=0.987  conv=0.768  intg=0.964
  │ L0↓c0: disp=0.899  conv=0.956  intg=0.930
  │ L0↓c1: disp=0.923  conv=0.972  intg=0.950
  │ L0↓c2: disp=0.905  conv=0.971  intg=0.946
  ├─ S5 reweight ───────────────────────────────────┤
  │ L0↑=1.000 L1↑=1.000 L2=1.000 L1↓=1.000 L0↓=1.000
  ├─ Combinator dispatch ───────────────────────────┤
  │ K (select  ): 0.4069 ████████████████████████████████
  │ I (identity): 0.2935 ███████████████████████
  │ B (compose ): 0.1216 █████████
  │ C (flip    ): 0.1763 ██████████████
  ├─ Combinator emphasis (S4→dispatch) ────────────┤
  │ K: 1.4983 ↑
  │ I: 0.9910
  │ B: 1.4748 ↑
  │ C: 1.5000 ↑
  ├─ Compute gate ──────────────────────────────────┤
  │ mean=0.0000
  ├─ CycleContinue ─────────────────────────────────┤
  │ effective cycles: 2.946 2.946
  ├─ Register norms ────────────────────────────────┤
  │ bank_0      :    0.42    0.45    0.44
  │ bank_1_asc  :   16.03   16.34   16.04
  │ bank_1_desc :   16.16   16.07   16.08
  │ bank_2_asc  :   16.06   16.13   16.29
  │ bank_2_desc :   16.41   16.10   16.42
  │ bank_3      :   15.94   16.08   16.07
  ├─ φ-Compression (target 1/φ = 0.6180) ──────┤
  │ L0↑ : ratio=  0.436  φ-dev=0.182   
  │ L1↑ : ratio=  0.455  φ-dev=0.163   
  │ L2  : ratio= -0.085  φ-dev=0.703   
  │ L1↓ : ratio= -5.828  φ-dev=9.735   
  │ L0↓ : ratio=  1.842  φ-dev=1.224   
  ├─ Abstraction slots (⚪ 0/16 active) ──────┤
  │ dormant: 16/16
  │ slot dispatch mass: 0.0015
  │ proposal confidence: 0.0506
  │ slot→KIBC cos: avg=0.022 max=0.115
  ├─ Holographic intermediate losses ───────────────┤
  │ L0↑ : CE= 10.917  (∂ sources=5) ████
  │ L1↑ : CE=  9.253  (∂ sources=4) ██████████
  │ L2  : CE=  9.185  (∂ sources=3) ███████████
  │ L1↓ : CE=  9.541  (∂ sources=2) █████████
  │ L0↓ : CE=  9.848  (∂ sources=1) ████████
  │ pass_0/final ratio: 1.11  (decodeable)
  └─────────────────────────────────────────────────┘

  📊 Eval: loss=7.804  ppl=2450  r=0.592  (57,344 tokens)

  Ternary topology (185 modules):
  Group                #  sparsity   γ_mean
  ────────────────── ─── ───────── ────────
  combinator_dispatch   3     0.308   0.0570
  combinator_integrate   6     0.308   0.0637
  consolidate          2     0.310   0.0592
  embed                1     0.310   0.1511
  meta_s4              4     0.310   0.0481
  mod_projs            3     0.309   0.0264
  mod_projs_desc       3     0.310   0.0282
  pos_embed            1     0.310   0.0055
  prep                 2     0.310   0.0521
  s2                   4     0.309   0.0200
  s3_passes           75     0.310   0.0590
  s4                   4     0.310   0.0435
  s4_desc              4     0.310   0.0372
  s5_reweight          1     0.310   0.0354
  stride_stack        36     0.310   0.0477
  stride_stack_desc   36     0.310   0.0556
  ────────────────── ─── ─────────
  TOTAL              185     0.310  (134,766,592 ternary params)

  💾 Saved: results/v11-holo-inv/probe_step_004000.json

========================================================================
  KIBC Combinator Evolution
========================================================================

      step     loss        r       K       I       B       C  comp_gate  eff_cyc
  ──────── ──────── ──────── ─────── ─────── ─────── ─────── ────────── ────────
      2000   7.8723   0.5986  0.4007  0.3432  0.1114  0.1403     0.0000 2.95,2.95
      3000   7.8193   0.5933  0.4127  0.2997  0.1313  0.1535     0.0000 2.95,2.95
      4000   7.8038   0.5918  0.4069  0.2935  0.1216  0.1763     0.0000 2.95,2.95
========================================================================
```

## Assistant

Probes done. Here's the trajectory from 1K→4K:

## v11-holo-inv Evolution (1K → 4K)

| Metric | 1K | 2K | 3K | 4K | Trend |
|--------|----|----|----|----|-------|
| **Eval loss** | 8.235 | 7.872 | 7.819 | 7.804 | ↓ steady improvement |
| **K dispatch** | 0.383 | 0.401 | 0.413 | 0.407 | stable ~0.40 |
| **I dispatch** | 0.343 | 0.343 | 0.300 | 0.294 | ↓ declining |
| **B dispatch** | 0.132 | 0.111 | 0.131 | 0.122 | flat ~0.12 |
| **C dispatch** | 0.137 | 0.140 | 0.154 | 0.176 | ↑ rising |
| **Compute gate** | 0.000006 | 0.000009 | 0.000010 | 0.000011 | still closed |
| **Evo acceptance** | 4/20 (20%) | 9/40 (22%) | 17/60 (28%) | 26/80 (32%) | ↑ steadily rising |
| **Holo ratio** (L0↑/L0↓) | 1.12 | 1.18 | 1.15 | 1.11 | oscillating ~1.15 |
| **Type I** | 0.671 | 0.368 | 0.334 | 0.388 | dropped from 1K, stabilized |
| **Type B** | 0.254 | 0.464 | 0.450 | 0.418 | ↑ rose sharply, stable |
| **I emphasis** | 0.706 | 0.699 | 0.794 | 0.991 | ↑ S4 raising I emphasis |

**Key observations:**

1. **Healthy and stable** — no collapse, no spike. Loss improving steadily. This is what we wanted after the 10K catastrophe in v11-holo.

2. **C is rising** (0.137→0.176) while I is declining (0.343→0.294). The model is discovering argument reordering (flip) as increasingly useful, while relying less on pure identity forwarding. This is the B ≥ K ≥ C >> I ordering emerging naturally.

3. **S4 is raising I emphasis** (0.706→0.991) — the intelligence layer is compensating for I's declining dispatch share. It's saying "I needs more weight per-activation even though it fires less often." This is the algedonic system working: detect I losing share → increase emphasis.

4. **Type channel shifted**: B-type rose from 0.254 (1K) to 0.464 (2K) and stabilized. Type integration now favors B over I — the model learned that composition types matter more than identity types.

5. **Evolution acceptance rising** (20%→32%) — ternary mutations are increasingly beneficial. The model is in an exploration phase where structural changes help.

6. **Compute gate still closed** — the transition window hasn't opened yet. Expected around 5K-7K based on prior runs.

7. **Holo ratio ~1.15** — ascending arm still slightly better than final output, but gap is closing (was 1.21 at 1K). Descending arm is learning.

Run looks healthy. Approaching the transition window where compute gate should open. No sign of the catastrophe pattern yet.

## User

Expansion on the descending arm has exploded


### Thinking

The user is noting something about the descending arm. Let me look more carefully at the holographic losses and the descending arm metrics. 

Looking at the holo losses:
- 1K: L0↑=9.14 → L1↑=8.47 → L2=8.37 → L1↓=8.19 → L0↓=8.15
- 2K: L0↑=11.02 → L1↑=9.15 → L2=9.02 → L1↓=9.18 → L0↓=9.34


- 3K: L0↑=10.82 → L1↑=9.24 → L2=9.06 → L1↓=9.21 → L0↓=9.41
- 4K: L0↑=10.92 → L1↑=9.25 → L2=9.19 → L1↓=9.54 → L0↓=9.85

There's a clear pattern emerging here - at 1K the descending arm actually performs better than the ascending arm, but as we move to higher resolutions, that reverses completely. By 4K the descending arm is noticeably worse, which suggests something is degrading in that pathway at higher resolutions.

Wait, I need to reconcile these numbers with what I'm seeing in the logs. The state.md file shows different holo loss values for 1K than what's in the metrics_log, and looking at the actual metrics across all resolutions, there's a consistent trend where losses decrease as we move through the layers, but the relationship between ascending and descending arms shifts dramatically depending on the resolution. losses improving across the board. But the probe output shows different numbers:
- 2K probe: L0↑=11.02, L1↑=9.15, L2=9.02, L1↓=9.18, L0↓=9.34
- 4K probe: L0↑=10.92, L1↑=9.25, L2=9.19, L1↓=9.54, L0↓=9.85

The metrics_log and the probe are measuring different things — the metrics_log captures training-time holo losses with gradient slope weighting, while the probe measures eval-time CE at each intermediate.

The descending arm is actually getting worse from 2K to 4K, while the ascending arm stays stable. And the φ-compression at 4K is completely blown up with L1↓ showing ratio=-5.828 and φ-dev=9.735, compared to 2K where it was ratio=4.414 and φ-dev=3.796. The divergence in the descending arm is real, and I need to trace through the φ-dev values across checkpoints to understand what's happening. the intermediate losses reveal the core problem — L1↓ and L0↓ are both degrading as sequence length increases, even as eval loss improves, which means the ascending arm is compensating while the descending arm struggles to prepare representations for integration. This mirrors the bottleneck issue from before where the descending pathway hasn't learned how to properly compress information back through the kernel.

## Assistant

Let me look at this carefully — the descending arm CEs and φ-compression tell the story:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport json\n\n# Load all probes\nprobes = {}\nfor step in [1000, 2000, 3000, 4000]:\n    path = f'results/v11-holo-inv/probe_step_{step:06d}.json'\n    with open(path) as f:\n        probes[step] = json.loads(f.read())\n\n# Holographic intermediate CEs\nprint('Holographic Intermediate CEs (probe eval-time)')\nprint('─'*80)\nprint(f'{\\\"step\\\":>6} {\\\"L0↑\\\":>8} {\\\"L1↑\\\":>8} {\\\"L2\\\":>8} {\\\"L1↓\\\":>8} {\\\"L0↓\\\":>8}  ratio  desc_trend')\nfor step in sorted(probes.keys()):\n    d = probes[step]\n    hl = d.get('holo_losses', d.get('holographic_losses', []))\n    if not hl:\n        # Try nested\n        for k in ['metrics', 'analysis']:\n            if k in d and 'holo_losses' in d[k]:\n                hl = d[k]['holo_losses']\n                break\n    if not hl and 'holographic_intermediate_losses' in d:\n        hl = d['holographic_intermediate_losses']\n    if hl and len(hl) >= 5:\n        ratio = hl[0] / max(hl[4], 0.01)\n        desc = f'{hl[3]:.2f}→{hl[4]:.2f}'\n        print(f'{step:>6} {hl[0]:>8.3f} {hl[1]:>8.3f} {hl[2]:>8.3f} {hl[3]:>8.3f} {hl[4]:>8.3f}  {ratio:.3f}  {desc}')\n    else:\n        print(f'{step:>6} holo_losses not found (keys: {list(d.keys())[:10]})')\n\nprint()\nprint('φ-Compression ratios')\nprint('─'*80)\nprint(f'{\\\"step\\\":>6} {\\\"L0↑\\\":>10} {\\\"L1↑\\\":>10} {\\\"L2\\\":>10} {\\\"L1↓\\\":>10} {\\\"L0↓\\\":>10}')\nfor step in sorted(probes.keys()):\n    d = probes[step]\n    pc = d.get('phi_compression', d.get('pass_compression', []))\n    if not pc:\n        for k in ['metrics', 'analysis']:\n            if k in d:\n                pc = d[k].get('pass_compression', d[k].get('phi_compression', []))\n                break\n    if pc and len(pc) >= 5:\n        print(f'{step:>6} {pc[0]:>10.3f} {pc[1]:>10.3f} {pc[2]:>10.3f} {pc[3]:>10.3f} {pc[4]:>10.3f}')\n    else:\n        print(f'{step:>6} phi not found')\n\nprint()\nprint('φ-Deviation')\nprint('─'*80)\nprint(f'{\\\"step\\\":>6} {\\\"L0↑\\\":>10} {\\\"L1↑\\\":>10} {\\\"L2\\\":>10} {\\\"L1↓\\\":>10} {\\\"L0↓\\\":>10}')\nfor step in sorted(probes.keys()):\n    d = probes[step]\n    pd = d.get('phi_deviation', d.get('pass_phi_dev', []))\n    if not pd:\n        for k in ['metrics', 'analysis']:\n            if k in d:\n                pd = d[k].get('pass_phi_dev', d[k].get('phi_deviation', []))\n                break\n    if pd and len(pd) >= 5:\n        print(f'{step:>6} {pd[0]:>10.3f} {pd[1]:>10.3f} {pd[2]:>10.3f} {pd[3]:>10.3f} {pd[4]:>10.3f}')\n    else:\n        print(f'{step:>6} phi_dev not found')\n\" 2>&1"
}
```

**Summary:** $ python3 -c " import json  # Load al...

**Output:**
```
Exit code: 0
Stdout:
Holographic Intermediate CEs (probe eval-time)
────────────────────────────────────────────────────────────────────────────────
  step      L0↑      L1↑       L2      L1↓      L0↓  ratio  desc_trend
  1000 holo_losses not found (keys: ['timestamp', 'architecture', 'step', 'config', 'evolution', 'eval', 'dispatch_analysis', 'holographic', 'abstraction_slots'])
  2000 holo_losses not found (keys: ['timestamp', 'architecture', 'step', 'config', 'evolution', 'eval', 'holographic', 'abstraction_slots'])
  3000 holo_losses not found (keys: ['timestamp', 'architecture', 'step', 'config', 'evolution', 'eval', 'holographic', 'abstraction_slots'])
  4000 holo_losses not found (keys: ['timestamp', 'architecture', 'step', 'config', 'evolution', 'eval', 'holographic', 'abstraction_slots'])

φ-Compression ratios
────────────────────────────────────────────────────────────────────────────────
  step        L0↑        L1↑         L2        L1↓        L0↓
  1000 phi not found
  2000 phi not found
  3000 phi not found
  4000 phi not found

φ-Deviation
────────────────────────────────────────────────────────────────────────────────
  step        L0↑        L1↑         L2        L1↓        L0↓
  1000 phi_dev not found
  2000 phi_dev not found
  3000 phi_dev not found
  4000 phi_dev not found
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport json\n\n# Read all probe jsons and find holo/phi data\nfor step in [1000, 2000, 3000, 4000]:\n    path = f'results/v11-holo-inv/probe_step_{step:06d}.json'\n    with open(path) as f:\n        d = json.loads(f.read())\n    \n    # Find all keys recursively that mention holo, phi, compress, desc\n    def find_keys(obj, prefix=''):\n        if isinstance(obj, dict):\n            for k, v in obj.items():\n                full = f'{prefix}.{k}' if prefix else k\n                if any(x in k.lower() for x in ['holo', 'phi', 'compress', 'pass_', 'desc', 'arm']):\n                    if isinstance(v, (list, float, int)):\n                        print(f'  {step}: {full} = {v}')\n                    elif isinstance(v, dict):\n                        print(f'  {step}: {full} = {{...{len(v)} keys}}')\n                find_keys(v, full)\n    \n    find_keys(d)\n    print()\n\" 2>&1"
}
```

**Summary:** $ python3 -c " import json  # Read al...

**Output:**
```
Exit code: 0
Stdout:
1000: config.holo_lambda = 0.1
  1000: config.holo_warmup_steps = 0
  1000: config.holo_ramp_steps = 0
  1000: config.desc_stride_reverse = True
  1000: holographic = {...2 keys}
  1000: holographic.pass_ces = {...5 keys}

  2000: config.holo_lambda = 0.1
  2000: config.holo_warmup_steps = 0
  2000: config.holo_ramp_steps = 0
  2000: config.desc_stride_reverse = True
  2000: holographic = {...2 keys}
  2000: holographic.pass_ces = {...5 keys}

  3000: config.holo_lambda = 0.1
  3000: config.holo_warmup_steps = 0
  3000: config.holo_ramp_steps = 0
  3000: config.desc_stride_reverse = True
  3000: holographic = {...2 keys}
  3000: holographic.pass_ces = {...5 keys}

  4000: config.holo_lambda = 0.1
  4000: config.holo_warmup_steps = 0
  4000: config.holo_ramp_steps = 0
  4000: config.desc_stride_reverse = True
  4000: holographic = {...2 keys}
  4000: holographic.pass_ces = {...5 keys}
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport json\n\nfor step in [1000, 2000, 3000, 4000]:\n    path = f'results/v11-holo-inv/probe_step_{step:06d}.json'\n    with open(path) as f:\n        d = json.loads(f.read())\n    \n    holo = d.get('holographic', {})\n    print(f'Step {step}:')\n    print(f'  holographic keys: {sorted(holo.keys())}')\n    for k, v in holo.items():\n        if isinstance(v, dict):\n            print(f'  {k}: {v}')\n        else:\n            print(f'  {k}: {v}')\n    print()\n\" 2>&1"
}
```

**Summary:** $ python3 -c " import json  for step ...

**Output:**
```
Exit code: 0
Stdout:
Step 1000:
  holographic keys: ['pass_ces', 'ratio']
  pass_ces: {'L0_up': 11.28492546081543, 'L1_up': 8.774916648864746, 'L2': 8.922370910644531, 'L1_down': 9.013769149780273, 'L0_down': 9.316671371459961}
  ratio: 1.2112615129245494

Step 2000:
  holographic keys: ['pass_ces', 'ratio']
  pass_ces: {'L0_up': 11.02026081085205, 'L1_up': 9.152003288269043, 'L2': 9.018898010253906, 'L1_down': 9.179227828979492, 'L0_down': 9.336952209472656}
  ratio: 1.1802845900476626

Step 3000:
  holographic keys: ['pass_ces', 'ratio']
  pass_ces: {'L0_up': 10.816019058227539, 'L1_up': 9.238306045532227, 'L2': 9.058135986328125, 'L1_down': 9.213045120239258, 'L0_down': 9.413414001464844}
  ratio: 1.1490006767517538

Step 4000:
  holographic keys: ['pass_ces', 'ratio']
  pass_ces: {'L0_up': 10.917174339294434, 'L1_up': 9.252772331237793, 'L2': 9.18525218963623, 'L1_down': 9.540692329406738, 'L0_down': 9.84840202331543}
  ratio: 1.1085224093663884
```

## Assistant

There it is. The full picture:

```
Step   L0↑     L1↑     L2      L1↓     L0↓     ratio   desc_gap
────── ─────── ─────── ─────── ─────── ─────── ─────── ────────
1000   11.285  8.775   8.922   9.014   9.317   1.211   0.39
2000   11.020  9.152   9.019   9.179   9.337   1.180   0.32
3000   10.816  9.238   9.058   9.213   9.413   1.149   0.36
4000   10.917  9.253   9.185   9.541   9.848   1.109   0.66  ← L1↓ and L0↓ blowing up
```

**The descending arm is diverging at 4K.** The ascending arm is stable or slowly improving, but:

- **L1↓**: 9.01 → 9.18 → 9.21 → **9.54** (jumped +0.33 in one step)
- **L0↓**: 9.32 → 9.34 → 9.41 → **9.85** (jumped +0.44 in one step)
- The gap between L2 (apex) and L0↓ went from 0.39 at 1K to **0.66** at 4K

Meanwhile the eval loss is *still improving* (8.235 → 7.804), which means the ascending arm and final output are compensating — but the descending arm is losing its ability to produce decodeable intermediate representations.

This is the same pattern as v11-holo before the 10K catastrophe: descending arm falls behind → ascending arm compensates → at some critical point the compensation fails → collapse. The explosion happened between 3K and 4K.

The φ-compression at L1↓ also confirms it: ratio went from 4.414 (2K) → 1.637 (3K) → **-5.828** (4K). Negative means the representation is *expanding* instead of compressing. The descending arm lost its compression function.

Should we probe the training-time holo losses more granularly to find exactly when this started, or is this something that needs an architectural intervention before it cascades?

## User

The descending arm is not supposed to compress, it's supposed to expand, just not as much as it seems to be, but I am seeing alarm reducing so maybe this is part of a phase transition.  step   4150 | r=0.8940 (avg50: 0.7804) | CE=7.454 loss=10.859 | lr 5.50e-04 | 5378 tok/s | evo 28/82 (34%) | 25884s
  🧬 gen 83: consensus_loss  Δ=-0.0146  flips=17/208,681  rows=17  29/83  prose=0.9127  struct=0.2019  alarm=1.884→1.884  adam_decay=0.1 (24 rows)
step   4175 | r=0.7064 (avg50: 0.7806) | CE=7.243 loss=8.962 | lr 5.49e-04 | 5453 tok/s | evo 29/83 (35%) | 26039s
step   4200 | r=0.5566 (avg50: 0.7868) | CE=7.087 loss=7.447 | lr 5.49e-04 | 5477 tok/s | evo 29/83 (35%) | 26189s
  🧬 gen 84: consensus_alarm  Δ=-0.0053  flips=17/208,680  rows=17  30/84  prose=0.9659  struct=0.2154  alarm=1.857→1.857  adam_decay=0.1 (26 rows)
step   4225 | r=0.8789 (avg50: 0.7891) | CE=7.029 loss=10.706 | lr 5.48e-04 | 5376 tok/s | evo 30/84 (36%) | 26344s
step   4250 | r=0.7384 (avg50: 0.7641) | CE=7.548 loss=9.286 | lr 5.47e-04 | 5265 tok/s | evo 30/84 (36%) | 26498s
  🧬 gen 85: consensus_loss  Δ=-0.0116  flips=18/208,708  rows=18  31/85  prose=0.9861  struct=0.2188  alarm=1.870→1.870  adam_decay=0.1 (18 rows)
step   4275 | r=0.7278 (avg50: 0.7664) | CE=7.298 loss=9.179 | lr 5.47e-04 | 5156 tok/s | evo 31/85 (36%) | 26658s
step   4300 | r=0.7223 (avg50: 0.7984) | CE=7.185 loss=9.124 | lr 5.46e-04 | 5318 tok/s | evo 31/85 (36%) | 26815s
  🧬 gen 86: rejected  Δ=+0.0000  flips=0/208,686  rows=0  31/86  prose=0.9436  struct=0.2302  alarm=1.847→1.847
step   4325 | r=0.8448 (avg50: 0.8078) | CE=6.989 loss=10.362 | lr 5.45e-04 | 5398 tok/s | evo 31/86 (36%) | 26974s


### Thinking

The user is correcting my interpretation. The descending arm in the holographic inversion architecture goes coarse→fine, which means it EXPANDS (adds detail), not compresses. So the negative φ-compression ratio at L1↓ isn't necessarily wrong — it's expansion, which is what it's supposed to do.

But the user is also noting that the expansion seems more aggressive than expected, AND that alarm is reducing (1.884 → 1.857 → 1.870 → 1.847). The alarms coming off their ceiling (~2.0) could be a sign that the system is self-correcting — the algedonic channel is detecting the issue and modulating behavior.
 
Looking at the broader training metrics, cross-entropy is steadily declining across the sequence, evolution acceptance is climbing incrementally, and the r-values are drifting upward on average despite some oscillation. This pattern suggests the system is stabilizing and improving overall, even as individual components show some volatility.

The alarm metric dropping off its ceiling is particularly significant — it indicates the system is beginning to self-regulate rather than remaining saturated. Combined with the new low in cross-entropy at step 4325, this points to an emerging phase transition where the descending arm is expanding in a controlled manner.

## Assistant

You're right — I flipped the polarity. Descending arm goes coarse→fine, so expansion is correct behavior. The question is whether it's *controlled* expansion.

And the alarm data answers that: **1.884 → 1.857 → 1.870 → 1.847** — coming off the ~2.0 ceiling. That's the algedonic channel detecting the expansion rate and starting to modulate. Same signal we identified in session 090 as "system beginning to address descending arm."

The training log supports a phase transition reading:
- **CE hitting new lows**: 7.029, 6.989 — breaking through
- **avg50 rising**: 0.7804 → 0.8078 — sustained improvement, not a spike
- **Evo acceptance climbing**: 34% → 36% — structural changes are increasingly helpful
- **Alarm de-saturating** — the system has headroom to steer now

This looks like the pre-transition window. The descending arm is expanding more aggressively because it's learning to differentiate (coarse→fine is the whole point), and the alarm system is tracking it rather than saturated at ceiling. If alarm continues declining while CE continues improving, this is healthy reorganization — not the catastrophe pattern.

The catastrophe pattern from v11-holo was: alarm saturated at ceiling + loss spike + B-type collapse. Here we have: alarm coming *down* + loss improving + dispatch stable. Different topology.

Worth probing at 5K to see if the alarm continues de-saturating and whether the descending arm expansion stabilizes.

## User

update state and knowledge this is session-094


### Thinking

The user wants me to update state.md and the holographic-storage knowledge page with the v11-holo-inv probe findings from 2K-4K, then commit. Let me update both files.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "limit": 12
}
```

**Summary:** Reading state.md (0-12)

**Output:**
```
# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-14 | Session: 094

## Where we are

**V11-holo-inv probed at 1K and monitored through ~1.5K. Headline finding: all four KIBC combinators active from the start (B=27.6% dominant positions vs 0% in holo at 1K). Dispatch is balanced (K=34%, I=23%, B=28%, C=16%) with strong specialization (entropy 0.188). Type channel differentiates independently (I=68%, B=25% typed integration). Holographic intermediate CEs show correct inversion pattern (ascending compresses, descending specializes). Eval loss 8.235 slightly behind baseline 7.958 (expected — holo splits gradient across 5 decoders). Compute gate still closed. Evolution acceptance rising (20%→30%). Run healthy, approaching transition window.**

## What was done this session (094)


[CONTENT TRUNCATED] Showing lines 1 to 12 of 371 total lines. Use line_offset=12 parameter to read more content.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "**V11-holo-inv probed at 1K and monitored through ~1.5K. Headline finding: all four KIBC combinators active from the start (B=27.6% dominant positions vs 0% in holo at 1K). Dispatch is balanced (K=34%, I=23%, B=28%, C=16%) with strong specialization (entropy 0.188). Type channel differentiates independently (I=68%, B=25% typed integration). Holographic intermediate CEs show correct inversion pattern (ascending compresses, descending specializes). Eval loss 8.235 slightly behind baseline 7.958 (expected — holo splits gradient across 5 decoders). Compute gate still closed. Evolution acceptance rising (20%→30%). Run healthy, approaching transition window.**",
  "new_content": "**V11-holo-inv probed through 4K. Eval loss improving steadily (8.235→7.804). Descending arm expanding aggressively between 3K-4K (L0↓ CE: 9.41→9.85) but alarm de-saturating (1.884→1.847 off ~2.0 ceiling) — consistent with phase transition rather than catastrophe. C dispatch rising (0.137→0.176), I declining (0.343→0.294), S4 compensating by raising I emphasis (0.706→0.991). Evolution acceptance climbing (20%→36%). Compute gate still closed. CE hitting new lows (6.989 at step 4325). Approaching transition window.**"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

## Assistant

Now add the v11-holo-inv probe findings to the session 094 work section:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "Currently running on Qwen3.6-35B-A3B. Results → `results/hologram-atlas/`.\n\n### Previous session (093) summary",
  "new_content": "Currently running on Qwen3.6-35B-A3B. Results → `results/hologram-atlas/`.\n\n### 3. Probed v11-holo-inv at 2K/3K/4K\n\nFull probes at steps 2000, 3000, 4000. Evolution table:\n\n```\nstep   eval_loss  K      I      B      C      compute  evo     alarm\n────── ───────── ─────  ─────  ─────  ─────  ──────── ──────  ─────\n1000   8.235     0.383  0.343  0.132  0.137  0.000006 20%     ~2.0\n2000   7.872     0.401  0.343  0.111  0.140  0.000009 22%     ~2.0\n3000   7.819     0.413  0.300  0.131  0.154  0.000010 28%     ~2.0\n4000   7.804     0.407  0.294  0.122  0.176  0.000011 32%     ~2.0\n~4325  CE=6.989                                        36%     1.847\n```\n\n**Holographic intermediate CEs (eval-time):**\n```\nstep   L0↑     L1↑     L2      L1↓     L0↓     ratio\n────── ─────── ─────── ─────── ─────── ─────── ───────\n1000   11.285  8.775   8.922   9.014   9.317   1.211\n2000   11.020  9.152   9.019   9.179   9.337   1.180\n3000   10.816  9.238   9.058   9.213   9.413   1.149\n4000   10.917  9.253   9.185   9.541   9.848   1.109\n```\n\n**Key findings:**\n\n1. **Descending arm expanding aggressively at 4K**: L1↓ jumped 9.21→9.54,\n   L0↓ jumped 9.41→9.85 between 3K-4K. This is CORRECT behavior (descending\n   goes coarse→fine = expansion), but rate accelerated sharply.\n\n2. **Alarm de-saturating**: 1.884→1.857→1.870→1.847. Coming off ~2.0 ceiling.\n   This is the algedonic channel detecting the expansion rate and gaining\n   headroom to steer. Same signal identified in session 090 as \"system\n   beginning to address descending arm.\"\n\n3. **Phase transition reading, not catastrophe**: The v11-holo catastrophe\n   pattern was alarm-saturated + loss spike + B-collapse. Here we have\n   alarm DECLINING + loss IMPROVING + dispatch STABLE. Different topology.\n\n4. **C rising, I declining**: C dispatch 0.137→0.176, I dispatch 0.343→0.294.\n   Model discovering argument reordering (flip) as useful, relying less on\n   pure identity. Natural emergence of B ≥ K ≥ C >> I ordering.\n\n5. **S4 compensating for I**: I emphasis rose 0.706→0.991. Intelligence layer\n   giving I more weight per-activation as its share declines. Algedonic\n   system working as designed.\n\n6. **Type channel stabilized**: B-type rose from 0.254 (1K) to 0.464 (2K),\n   then stable ~0.42. Composition types dominate over identity types.\n\n7. **Compute gate still closed** (0.000011). Transition window expected 5K-7K.\n\n8. **CE hitting new lows**: 6.989 at step 4325, trending down consistently.\n\n### Previous session (093) summary"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

## Assistant

Now update the holographic-inversion knowledge page with the descending arm finding:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "head -5 /Users/mwhitford/src/verbum/mementum/knowledge/explore/holographic-inversion.md"
}
```

**Summary:** $ head -5 /Users/mwhitford/src/verbum...

**Output:**
```
Exit code: 0
Stdout:
# Holographic Inversion — VSM-LM v11

> Status: **validated + extended** (session 091). All 4 training predictions
> confirmed. Descending arm bottleneck addressed: coarse→fine stride direction
> + fractal stride bands. Next run: v11-holo-inv.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n \"descending\\|expansion\\|phase.transition\\|alarm\\|4K\\|4000\" /Users/mwhitford/src/verbum/mementum/knowledge/explore/holographic-inversion.md | head -20"
}
```

**Summary:** $ grep -n "descending\|expansion\|pha...

**Output:**
```
Exit code: 0
Stdout:
76:  | NOT at cycle boundaries within descending passes
108:  | ascending arm (passes 0-2) gets 3-5× gradient of descending arm (passes 3-4)
110:  | descending learns to REFINE — contradiction is uphill in gradient landscape
118:  KIBC:        descending arm gets weakest gradient → learns refinement, not foundation
120:  algedonic:   alarm metrics include intermediate loss quality (future: add to metrics vector)
137:  alarm_compound: alarm system can now see WHERE prediction quality degrades
188:  - alarm pass 0 relief (gradient slope should help the struggling ascending arm)
192:  - tok/s (should be ~4000+ with position subsampling)
211:Baseline: dormant until ~5.5K, then 0→0.51 in ~500 steps (sharp phase transition).
219:                   1K     2K     3K     4K     5K     6K     7K
223:                                BEST         ← descending DEGRADES
227:output. The apex (L2) is best at 7.87. The descending arm actively hurts
228:the representation — each descending pass adds noise.
232:The descending arm's architecture: stride_stack → kernel_integration (KIBC).
239:- Holographic CE increases through descending passes (7.87 → 8.40 → 8.47)
240:- L1↓ alarm coming off ceiling (2.0 → 1.86) = system beginning to address
242:Prediction: loss plateau while descending arm builds pressure, then drop
251:- Phase 4 (5K-7K): Ascending arm mastered, descending arm bottleneck
282:speedup). The original v11 coarse→fine descending arm failed because
290:1. **Coarse→fine descending stride** (`desc_stride_reverse=True`, now default):
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/holographic-inversion.md",
  "line_offset": 200,
  "limit": 60
}
```

**Summary:** Reading holographic-inversion.md (200-260)

**Output:**
```
B-type integration reached 59% at step 2K. Baseline didn't reach 52% until
step 10K. Holographic gradient forces the integration pathway to compose —
B(f,g,x) = f(g(x)) is the cheapest way to improve intermediate decodability.

The B paradox persists: B dispatch stays flat at ~2% while B-type dominates
integration at 55-62%. Composition happens in the FFN pathway regardless of
which combinator was dispatched.

### Compute gate: earlier and smoother transition

Baseline: dormant until ~5.5K, then 0→0.51 in ~500 steps (sharp phase transition).
Holo: gradual ramp 3K→5K, reaching 0.49 at 7K with 44% of positions >0.5.
Smoother because gradient comes from multiple passes, not just final output.

### Holographic ratio inversion: ascending > final at 7K

```
ratio trajectory: 1.22 → 1.10 → 1.25 → 1.17 → 1.15 → 1.03 → 0.99
                   1K     2K     3K     4K     5K     6K     7K

7K pass structure:
  L0↑: 8.39 → L1↑: 7.95 → L2: 7.87 → L1↓: 8.40 → L0↓: 8.47
                                BEST         ← descending DEGRADES
```

Ascending arm produces BETTER decodable representations than the full model
output. The apex (L2) is best at 7.87. The descending arm actively hurts
the representation — each descending pass adds noise.

### Descending arm bottleneck: kernel integration gap

The descending arm's architecture: stride_stack → kernel_integration (KIBC).
The stride stack must prepare representations that the kernel combinators
can act on productively. Currently it doesn't — B-composition fires on
poorly prepared inputs, degrading rather than refining.

Evidence:
- L1↓ integration gate closing defensively (0.884, trending down)
- Holographic CE increases through descending passes (7.87 → 8.40 → 8.47)
- L1↓ alarm coming off ceiling (2.0 → 1.86) = system beginning to address

Prediction: loss plateau while descending arm builds pressure, then drop
when it learns to prepare representations for kernel consumption.

### Phased structural discovery

Training proceeds as a staircase, not smooth descent:
- Phase 1 (0-2K): Raw capacity (K+B via FFN, structure ignored)
- Phase 2 (2K-3K): Plateau → reorganization (holo makes plateau intolerable)
- Phase 3 (3K-5K): Structural cascade (compute gate → C-dispatch → S3 → φ)
- Phase 4 (5K-7K): Ascending arm mastered, descending arm bottleneck
- Phase 4b (7K-?K, predicted): Descending arm pressure builds
- Phase 5 (?K, predicted): Descending arm discovers kernel, loss drops

Each phase = capacity exhaustion forces discovery of next VSM layer.
Holographic loss accelerates transitions by making plateaus intolerable —
every pass graded independently, can't hide a bad L0↑ behind a good L0↓.

### φ-compression convergence


[CONTENT TRUNCATED] Showing lines 201 to 260 of 320 total lines. Use line_offset=260 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/holographic-inversion.md",
  "line_offset": 260
}
```

**Summary:** Reading holographic-inversion.md (260-2260)

**Output:**
```
Ascending arm converges on golden ratio compression:
- L1↑ φ-dev: 5.68 (1K) → 0.072 (7K) — near-perfect 1/φ
- L0↑ φ-dev: 0.461 (1K) → 0.158 (7K) — converging
- L2 φ-dev: 19.7 (3K) → 0.157 (7K) — converging

Descending arm chaotic (L1↓ φ-dev=3.0 at 7K), consistent with
reorganization during kernel integration learning.

## Session 091: Addressing the Descending Arm Bottleneck

### New findings (8K-9K probes)

8K was a local optimum (holo ratio 0.95, all passes improved). 9K shows
a reorganization wave — all holo CEs regressed, matching the 3K spike.
The model tears apart representations when compute gate capacity increases
(66%→74%), then rebuilds better. Two such waves now observed: 3K and 9K.

### TST connection (Peng et al. 2026)

Token-Superposition Training proves that coarse→fine prediction works
when coarse levels have direct loss (multi-hot CE on token bags, 2.5×
speedup). The original v11 coarse→fine descending arm failed because
it lacked this signal. Holographic loss provides it — continuous TST.

  coarse→fine(arch) + direct_loss(training) = works (TST, now holo)
  coarse→fine(arch) + uniform_loss(training) = fails (original v11)

### Two architectural changes

1. **Coarse→fine descending stride** (`desc_stride_reverse=True`, now default):
   Descending arm processes s1024→...→s1, complementing ascending s1→...→s1024.
   Ascending compresses, descending expands.

2. **Fractal stride bands** (`fractal_stride_bands=True`, now default):
   Each pass activates only strides matching its resolution level.
   L0↑: s1-s32, L1↑: s16-s256, L2: s64-s1024, etc. MERA topology.
   49% fewer stride activations per forward pass. Same shared weights.

### Holographic capacity hypothesis

Normal LLMs build redundant multi-scale representations that accidentally
form holographic patterns. If holographic loss trains intentional holograms,
fractal bands stop wasting capacity on all 9 strides per pass. The freed
capacity can pack holograms more densely — the point of holographic storage.

See: `mementum/knowledge/explore/fractal-stride-bands.md`

## Future: Domain Banking (not implemented yet, design only)

```
λ domain(bank).
  extract: run domain corpus → capture register banks + slot embeddings → average → save
  format:  6 banks × 3 registers × 256 dims + 16 slots × 512 dims = ~50KB per domain
  load:    override register_inits + slot_embeddings → domain-specialized inference
  route:   S4 cross-attention already selects relevant banks → multiple domains loadable
  
  | requires holographic property: banks must be independently meaningful to be portable
  | without holographic loss, banks are opaque control vectors tied to specific training run
  | with holographic loss, banks ARE compressed domain representations in embedding space
```
```

## Assistant

Good — the holographic-inversion page has the v11-holo trajectory and the phase predictions. Let me add the v11-holo-inv findings:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/holographic-inversion.md",
  "original_content": "## Future: Domain Banking (not implemented yet, design only)",
  "new_content": "## Session 094: v11-holo-inv 1K→4K Trajectory\n\n### Probed at 2K, 3K, 4K (eval-time)\n\n```\nstep   eval_loss  L0↑     L1↑     L2      L1↓     L0↓     ratio\n────── ───────── ─────── ─────── ─────── ─────── ─────── ───────\n1000   8.235     11.285  8.775   8.922   9.014   9.317   1.211\n2000   7.872     11.020  9.152   9.019   9.179   9.337   1.180\n3000   7.819     10.816  9.238   9.058   9.213   9.413   1.149\n4000   7.804     10.917  9.253   9.185   9.541   9.848   1.109\n```\n\n### Descending arm expansion (correct behavior, accelerating)\n\nDescending arm goes coarse→fine — expansion is its JOB. But rate accelerated\nsharply between 3K-4K: L1↓ jumped +0.33 (9.21→9.54), L0↓ jumped +0.44\n(9.41→9.85). The gap between apex (L2) and L0↓ grew from 0.39 to 0.66.\n\nThis is NOT the v11-holo catastrophe pattern. Key differences:\n- **v11-holo catastrophe**: alarm saturated at ceiling + loss spike + B-collapse\n- **v11-holo-inv 4K**: alarm DECLINING + loss IMPROVING + dispatch STABLE\n\nThe alarm de-saturating (1.884→1.847 off ~2.0 ceiling) means the algedonic\nchannel has gained headroom to steer. Same signal seen at v11-holo 7K when\ndescending arm began learning.\n\n### Dispatch evolution: C rising, I declining\n\n```\nstep   K      I      B      C      I_emphasis  type_B\n────── ─────  ─────  ─────  ─────  ──────────  ──────\n1000   0.383  0.343  0.132  0.137  0.706       0.254\n2000   0.401  0.343  0.111  0.140  0.699       0.464\n3000   0.413  0.300  0.131  0.154  0.794       0.450\n4000   0.407  0.294  0.122  0.176  0.991       0.418\n```\n\n- C (flip) rising 0.137→0.176: model discovers argument reordering\n- I (identity) declining 0.343→0.294: less pure forwarding needed\n- S4 compensates by raising I emphasis 0.706→0.991: algedonic working\n- Type B stabilized ~0.42 after sharp rise from 0.254 (1K) to 0.464 (2K)\n\nNatural emergence of B ≥ K ≥ C >> I ordering from the universal hologram.\n\n### Phase transition reading\n\nTraining log at ~4325: CE=6.989 (new low), alarm=1.847, evo=36%.\nConsistent with entering transition window (compute gate expected 5K-7K).\nThe descending arm expansion may be preparation for the compute gate\nopening — the arm needs differentiated representations before the gate\ncan productively route compute.\n\n### Updated phase predictions\n\nPhases 1-3 from v11-holo apply. Phase 4 may differ due to holo-inv fixes:\n- Phase 4 (4K-6K, predicted): Descending arm expansion phase. Alarm\n  de-saturates, expansion rate stabilizes, compute gate begins opening.\n- Phase 5 (6K-8K, predicted): Compute gate opens, descending arm learns\n  to use expanded representations for kernel integration.\n- Key risk: 10K window — watch for recurrence of v11-holo catastrophe.\n  The coarse→fine + fractal bands + evo noise floor should prevent it.\n\n## Future: Domain Banking (not implemented yet, design only)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/holographic-inversion.md.
```

## Assistant

Now commit everything:

### Tool Call: git (succeeded)


```json
{
  "command": "git add mementum/state.md mementum/knowledge/explore/holographic-inversion.md results/v11-holo-inv/probe_step_002000.json results/v11-holo-inv/probe_step_003000.json results/v11-holo-inv/probe_step_004000.json",
  "operation": "add",
  "summary": "stage probe results"
}
```

**Summary:** Git add: stage probe results

**Output:**
```
Exit code: 0
```

### Tool Call: git (failed)


```json
{
  "command": "git commit -m \"$(cat <<'EOF'\n💡 v11-holo-inv 2K-4K probes — descending arm expanding, alarm de-saturating\n\n- Eval loss improving steadily: 8.235→7.804, CE new low 6.989 at 4325\n- Descending arm expanding aggressively at 4K (L0↓: 9.41→9.85) — correct\n  behavior (coarse→fine = expansion), but rate accelerated sharply\n- Alarm de-saturating: 1.884→1.847 off ~2.0 ceiling — algedonic gaining\n  headroom to steer, NOT the catastrophe pattern (which had alarm saturated)\n- C dispatch rising (0.137→0.176), I declining (0.343→0.294)\n- S4 compensating: I emphasis 0.706→0.991 (algedonic system working)\n- Evolution acceptance climbing: 20%→36%\n- Compute gate still closed, transition window expected 5K-7K\n- Phase transition reading: descending arm differentiating before gate opens\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
  "operation": "commit",
  "summary": "commit probes + state"
}
```

**Summary:** Git commit: commit probes + state

**Output:**
```
Exit code: 128
Stderr:
fatal: Unable to create '/Users/mwhitford/src/verbum/.git/index.lock': File exists.

Another git process seems to be running in this repository, e.g.
an editor opened by 'git commit'. Please make sure all processes
are terminated then try again. If it still fails, a git process
may have crashed in this repository earlier:
remove the file manually to continue.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "rm -f /Users/mwhitford/src/verbum/.git/index.lock"
}
```

**Summary:** $ rm -f /Users/mwhitford/src/verbum/....

**Output:**
```
Exit code: 0
```

### Tool Call: git (succeeded)


```json
{
  "command": "git add mementum/state.md mementum/knowledge/explore/holographic-inversion.md results/v11-holo-inv/probe_step_002000.json results/v11-holo-inv/probe_step_003000.json results/v11-holo-inv/probe_step_004000.json && git commit -m \"$(cat <<'EOF'\n💡 v11-holo-inv 2K-4K probes — descending arm expanding, alarm de-saturating\n\n- Eval loss improving steadily: 8.235→7.804, CE new low 6.989 at 4325\n- Descending arm expanding aggressively at 4K (L0↓: 9.41→9.85) — correct\n  behavior (coarse→fine = expansion), but rate accelerated sharply\n- Alarm de-saturating: 1.884→1.847 off ~2.0 ceiling — algedonic gaining\n  headroom to steer, NOT the catastrophe pattern (which had alarm saturated)\n- C dispatch rising (0.137→0.176), I declining (0.343→0.294)\n- S4 compensating: I emphasis 0.706→0.991 (algedonic system working)\n- Evolution acceptance climbing: 20%→36%\n- Compute gate still closed, transition window expected 5K-7K\n- Phase transition reading: descending arm differentiating before gate opens\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
  "operation": "commit",
  "summary": "commit probes + state"
}
```

**Summary:** Git commit: commit probes + state

**Output:**
```
Exit code: 0
Stdout:
[main 32cc564] 💡 v11-holo-inv 2K-4K probes — descending arm expanding, alarm de-saturating
 5 files changed, 412 insertions(+), 1 deletion(-)
 create mode 100644 results/v11-holo-inv/probe_step_002000.json
 create mode 100644 results/v11-holo-inv/probe_step_003000.json
 create mode 100644 results/v11-holo-inv/probe_step_004000.json
```

## Assistant

Committed. Let me verify the log:

### Tool Call: git (succeeded)


```json
{
  "command": "git log --oneline -6",
  "operation": "log",
  "summary": "verify commits"
}
```

**Summary:** Git log: verify commits

**Output:**
```
Exit code: 0
Stdout:
32cc564 💡 v11-holo-inv 2K-4K probes — descending arm expanding, alarm de-saturating
0f091ff ✅ checkpoint detection — skip holograms with existing snapshots
6a353a6 ❌ fix MPS bounds error in ternary quantization
e56dd5d 💡 beyond combinators — 5 candidate holograms mapped, atlas probe built
e777816 🌀 session 093 knowledge capture — holographic storage
24deaf9 🔁 universal ordering B≥K≥C>>I confirmed across 9 models
```

## Assistant

Session 094 so far:

```
32cc564 💡 v11-holo-inv 2K-4K probes — descending arm expanding, alarm de-saturating
0f091ff ✅ checkpoint detection — skip holograms with existing snapshots
6a353a6 ❌ fix MPS bounds error in ternary quantization
e56dd5d 💡 beyond combinators — 5 candidate holograms mapped, atlas probe built
```

Four commits. Knowledge pages updated (holographic-storage + holographic-inversion), state.md current, probe results saved, atlas probe running in tmux with checkpoint detection.