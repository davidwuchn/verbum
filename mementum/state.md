# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-14 | Session: 098

## Where we are

**Beam trace probe reveals the holographic beamformer. V12 is a thick hologram: 95% plate (ternary), 5% beam (precision), 58× Pythia's holographic capacity. The thick hologram principle explains why V12's ternary weights work: depth × angular diversity compensates for magnitude loss. Troubleshooting guide maps every V12 failure mode to beam/plate classification. V12 ready to launch.**

## What was done this session (098)

### 1. Built beam-trace probe (Pythia-160M)

Traced activation vectors ("the beam") through every layer under compile vs null
conditions. Decomposed each layer into angular rotation + magnitude scaling,
separated attention vs FFN contributions, measured Q-subspace alignment.

Script: `scripts/explore/probe_beam_trace.py`
Results: `results/beam-trace/`

### 2. Five-phase beam propagation discovered

```
Phase          Layers  Attn%   FFN%   Beam cos   What happens
─────────────  ──────  ──────  ──────  ────────  ──────────────
Embedding      L0      20%     80%    0.994     Shared plate
Parsing        L1-2    50%     50%    0.970     Syntactic structure
Structural     L3      69%     31%    0.968     Argument assignment
Divergence     L4-6    41%     60%    0.879     Beams separate
FFN reading    L7-10   15%     85%    0.854     Peak divergence
Resolution     L11     16%     84%    0.986     Final predictions
```

**L6 is the beam steering singularity**: Q amplification 4.5×, Q rank collapses
to 24 dimensions (of 768). A tiny subspace controls the entire beam trajectory.

### 3. Ternary beamformer test — definitive classification

Per-layer isolation (ternarize ONE layer, measure final output deviation):

| Component | Avg Error | Max Error | Role |
|-----------|----------|----------|------|
| attn_dense (O proj) | 2.6° | 4.9° | ✅ PLATE — ternary-safe even for forward pass |
| FFN h→4h (gate) | 4.4° | 8.3° | ⚠️ Marginal |
| Q (query proj) | 5.1° | 16.2° | ❌ BEAM — needs precision |
| FFN 4h→h (output) | 6.0° | 10.1° | ❌ READER — needs precision |

### 4. MoE IS holographic architecture

Key finding: Qwen3.6 shows 93.6% ternary-safe but Pythia only 25%.
The difference is ENTIRELY in the FFN pathway:
- **MoE**: 256 expert FFNs = 256 sign patterns in the plate. Gate = beam selector.
- **Dense**: One FFN fuses gate + plate + reader. Can't separate.

The attention pathway tells the same story in both: K,V,O = plate, Q = beam.

### 5. V12 holographic capacity analysis — 95% plate, 5% beam

Mapped every V12 parameter to plate (ternary) or beam (precision):

```
Plate (ternary, 1.85 bits):   116.1M params  (95.0%) — K,V,O,FFN,S4,S3,S2,embeds
Beam (precision, 16 bits):      6.1M params  ( 5.0%) — Q projs, write gates, norms
Average:                        2.55 bits/param
Memory:                        39 MB (vs 244 MB FP16)
```

### 6. Thick hologram principle

V12 is a thick hologram — depth creates angular selectivity:

```
Pythia:   1 pass × 1 angle  = capacity 1   (thin → needs FP16)
Qwen MoE: 1 pass × 8 angles = capacity 8   (width → ternary-safe)
V12:      6.5 passes × 9 angles = capacity 58 (depth → ternary-safe)
```

Each pass reads the same ternary plate at a different beam angle.
Ternary error (~4°/read) reduces by √N over N reads. V12 reads each
weight 4-9 times → effective error 2-3× lower than single read.

This explains WHY V12's TernaryFFN should work despite beam trace showing
dense FFN needs precision: V12 compensates with depth.

### 7. Troubleshooting guide for V12 training

Mapped every V12 failure mode to beam/plate classification:
- Dispatch collapse → check beam-side emphasis/alarm biases
- Holo loss high → check ascending Q projections (beam) + plate evolution
- Retrieval dormant → check GLA write gates (beam, nn.Linear)
- Plateau → thick hologram needs time for angular specialization

See: `mementum/knowledge/explore/v12-holographic-capacity.md`

## What was done this session (097)

### 1. Diagnosed v11 B-dispatch decline — VSM variety gap

Analyzed v11-holo-inv 10K-12K metrics: B dispatch declining monotonically (0.132→0.079)
while alarm detects the problem but can't fix it. Traced the feedback topology:

**Three structural failures:**
1. **Alarm → pass amplitude (wrong granularity)**: 48 inputs but only 5 per-pass scalar
   outputs. Can't selectively boost B within a pass. Beer's variety law: controller must
   match system dimensionality. 5 knobs can't control 4×5=20 dimensions.
2. **Emphasis saturated at ceiling**: `1.0 + 0.5*tanh(raw)` range [0.5, 1.5]. B started
   at 1.499 — nowhere to go. Multiplicative on embeddings is weak in softmax space;
   additive on logits is the correct actuator.
3. **No ascending→dispatch feedback loop**: ascending arm optimized for holographic loss
   but had no gradient penalty for dispatch collapse downstream.

Evidence: r=0.82 correlation B_dispatch vs ascending S3 gate means. L0↑ suppression
reached 0.51. S4 emphasis drifted downward (1.499→1.470) — sensor shares the bottleneck.

### 2. V12 VSM variety fix (3 changes)

1. **AlgedonicAlert per-combinator dispatch bias**: `dispatch_bias_proj` (65→4) produces
   additive logit bias on CombinatorDispatch. Range [-2, +2] via tanh×2. Zero-init.
   When alarm sees B declining + entropy dropping, it boosts B's softmax logit directly.

2. **Additive emphasis bias**: S4's emphasis_proj output changed from multiplicative
   embedding scale [0.5, 1.5] to additive logit bias [-2, +2]. A +2 bias shifts softmax
   ~7× relative. S4 emphasis + alarm bias combine additively (correct for logit space).

3. **Dispatch entropy regularization**: squared hinge penalty when entropy < 85% of max
   (ln(4) × 0.85 ≈ 1.178). Gradient flows from dispatch collapse back through descending
   arm to ascending arm — closing the open loop. `dispatch_entropy_lambda=0.01`.

### 3. Evolution noise floor

Alarm-path acceptance had no minimum delta — any positive health change (0.0001) was
accepted. Sign flips cause routing ripple effects that accumulate silently. Fixed:
`evolution_alarm_min_delta=0.02` (1% of health range [0,2]). Loss-path min_delta also
raised from 0.01 to 0.02 to match. Applied to both v11 (live run) and v12.

### 4. Stride-aware GLA — 2.7× training speedup

**The dominant bottleneck**: GLA parallel scan consumed 78% of training time. For stride=32,
only 128 of 4096 positions participate, but the scan ran over all 4096 with masking.
`S_all` tensor: (B, 4096, 8, 64, 64) = 512 MB per layer × 6 layers.

**Fix**: Gather participating positions, scan over compact sequence, broadcast states for
retrieval. Each position reads from `S_stride[:, i//stride]` (causal).

```
Config              Before      After     Speedup
3 cycles fwd+bwd    10,625ms    3,894ms    2.73×
1 cycle  fwd+bwd     9,133ms    2,597ms    3.52×
3 cycles tok/s           771      2,104    2.73×
1 cycle  tok/s           897      3,154    3.52×
```

### 5. S4→S3 cycle budget — intelligence controls cycle depth

**The gap**: CycleContinue (S3) only read its own register state — a closed loop with no
intelligence input. S4 attended to the residual stream and knew content difficulty but
had no channel to tell S3 when to stop cycling. Gates stuck at 0.982.

**Fix**: `cycle_budget_proj` (emphasis_input → 1) produces scalar bias ∈ [-4, +4] that
shifts CycleContinue's logit. Beer's S4→S3 policy channel: intelligence sets policy,
control executes.
- Simple content → negative bias → gate closes → fewer effective cycles
- Complex content → positive bias → gate stays open → more cycles
- Zero-init → starts inert (backward compatible)

### 6. Performance analysis (V12 architecture)

Deep profiling of V12 (B=2, L=4096) revealed cost structure:

| Component | GFLOPs | Fraction |
|-----------|--------|----------|
| Output projection | 1,275 | 42.0% |
| Descending arm (3 passes × 3 cycles) | 1,113 | 36.7% |
| Ascending arm (4 passes) | 541 | 17.8% |
| S4 cross-attention | 105 | 3.5% |

GLA retrieval layers add only 4.8% of total compute — retrieval is cheap.
The output projection (512→151936 vocab) dominates FLOPs but is fast on AMX.
Holographic loss when enabled adds 36.8% overhead (7 intermediate decodes).

### 7. V11-holo-inv status (12.8K/20K, training live)

```
step   loss    comp   K_disp  B_disp  holo_ratio  alarm_min
1K     12.52   0.000  0.383   0.132   1.122       2.000
5K     11.76   0.000  0.419   0.101   1.051       1.392
10K    11.63   0.827  0.417   0.084   1.038       1.361
12K    11.60   0.882  0.436   0.079   1.034       1.324
```

B declining (0.132→0.079) — the variety gap that motivated session's V12 fixes.
Alarm detects it (min factor 1.324, declining from 2.0) but can't correct.
Holo ratio converging toward 1.0. Training continues to 20K for final checkpoint.

## What was done session (096)

V12 designed and built. M kernel as GatedLinearAttention layer type (not 5th combinator).
HybridStrideStack (6 comp + 3 ret strides), RetrievalRegisters (M→KIBC bridge).
7-pass symmetric hourglass (3+apex+3). Parallel associative scan for GLA (O(log L) depth).
Holographic landscape probe: 93.6% of Qwen3.6 is ternary-safe.
Cross-model universality: 3 architecture families confirm holographic partition.
Multiplexing breaks holography: fused QKV score 0.60 vs separate 0.92.
See session 096 entry in history for full details.

## What was done this session (095)

### 1. Analyzed hologram atlas results (Qwen3.6-35B-A3B)

All 6 holograms are real and distinguishable:

```
Hologram     output_KL  peak_layer  ternary_fail  signature
──────────── ─────────  ──────────  ────────────  ─────────────────────────────────
combinator   0.365      L31         baseline      bimodal depth template
type         0.415      L31         2/18          matches combinator shape closely
induction    0.827      L31         1/18          most robust attention hologram
binding      0.444      L31         5/18          most fragile — magnitude-dependent
frequency    0.224      L7          3/18 attn     MLP 0/18 — inverted prediction!
discourse    1.646      L35         0/18          strongest, most robust, late-peaking
```

### 2. Three structural findings

**Finding 1: L11 dip is architectural, not holographic.** Every hologram drops
47–72% at L11 relative to L7. The bimodal depth profile (L7→L11 dip→L31) is
Qwen3.6's hybrid architecture, not any linguistic circuit. Layer-level selectivity
profiles can't distinguish holograms from each other — they all ride the same wave.
Cross-hologram correlations all >0.72 (Pearson r), >0.95 (cosine).

**Finding 2: Binding is magnitude-dependent (connects to I-outlier).** 5 ternary
failures — all at sign-only in early full-attention layers (L3: 2.357, L7: 2.028,
L0: 2.823). Sign pattern alone cannot encode variable binding. Requires knowing
HOW STRONGLY a head attends, not just whether it does. Consistent with I-combinator
being the outlier (r≈0.70 vs K/B/C r>0.90 in session 093). Binding IS the I-circuit,
and I's distinctness comes from requiring magnitude where K/B/C don't.

**Finding 3: Frequency MLP more robust than attention (inverted prediction).**
MLP ternary survival: 0/18 failures (output_survival 0.93–1.07). Attention: 3/18
failures including catastrophic L0 mid_sparse disruption (7.07). Statistical
co-occurrence lives in FFN weight matrices as clean sign patterns. Supports
"FFN = key-value memory" view. Attention dynamically routes this info and
depends on specific magnitudes.

### 3. Discourse is the dominant hologram

Genre distinction (narrative/expository) has output_KL = 2.526 — nearly 2× the
next highest signal. Discourse is:
- **Strongest** at every layer (2–5× other holograms)
- **Most robust** (0/18 failures, even at GatedDeltaNet layers)
- **Only late-peaking** (L35 > L31 > L7 — signal keeps rising)
- **Most pervasive** (never drops below 0.049, even at L11 dip)

Fits VSM prediction: discourse operates at S5, modulating all others.

### 4. MoE gate: period-12 structure + beam-selector partial confirmation

Gate ternary survival confirmed L0-L4 (cos≈0.73–0.76). Cross-layer cosine
reveals period-12 pairing: L8↔L20 through L19↔L31 (cos 0.72–0.83). Does NOT
match full-attention period (every 4th). Suggests 3-phase model: early (L0-7),
middle (L8-19 ↔ L20-31 paired), late (L32-39). Gate Frobenius norms fall
monotonically (19→7 from early to late) but effective rank stays high (172–199).
Late gates are smaller but not lower-rank.

### 5. Prediction scorecard

| Prediction | Result | Notes |
|-----------|--------|-------|
| Type overlaps combinator | ✓ r=0.972 | But all holograms overlap at layer resolution |
| Induction orthogonal to combinator | ✗ r=0.987 | Layer profiles too coarse |
| Binding overlaps I | ~ Inconclusive | Weakest + most fragile = consistent with I |
| Frequency lower MLP survival | ✗ Inverted | MLP MORE robust than attention |
| Discourse MoE gate survival | ✓ L0-L4 | Need L31-L39 to complete test |

### 6. Fixed JSON string-key bug in atlas script

Cache-loaded selectivity profiles had string keys (JSON roundtrip), measure_layers
had int keys → KeyError. Added `_int_keys()` helper at all ingestion points.

### 7. Probed v11-holo-inv 5K-10K — no catastrophe

```
step  eval   compute  B_dom%  L0↑     L2      L0↓     ratio   event
───── ────── ──────── ─────── ─────── ─────── ─────── ─────── ─────────────────
1K    8.235  0.000    27.6%   11.285  8.922   9.317   1.211
5K    7.783  0.000    25.8%   10.328  9.010   9.475   1.090
6K    7.784  0.370    32.0%   10.095  9.018   9.424   1.071   gate opens
7K    7.728  0.690    39.8%   10.336  9.368   9.866   1.048   reorganization wave
8K    7.714  0.760    45.9%   10.404  9.109   9.577   1.086   recovery
9K    7.705  0.806    57.2%    9.480  8.718   9.555   0.992   ratio crosses 1.0
10K   7.703  0.824    57.7%    9.385  9.189   9.462   0.992   B stable, no collapse
```

v11-holo collapsed at 10K (loss 9.259, B 5.8%). v11-holo-inv: loss 7.703, B 57.7%.
Coarse→fine inversion + fractal bands + evolution fixes prevented catastrophe.

### 8. Key design insight: holographic storage + kernel computation

LLM storage IS holographic (session 095 atlas confirms). But reading is constructive
(entropy hump, intermediate garbage, magnitude-dependent binding). V11 resolves this:
holographic loss forces REPRESENTATIONS to be decodable, kernel functions handle
COMPUTATION. Lambda terms are perfect holographic objects (compact, compositional,
unfold on application). Keep holographic loss uniform — forces routing to kernels.
Evidence: ratio crossed 1.0 at 9K.

### 9. Head-level probe — three clusters, not six holograms

Ran `probe_hologram_heads.py` on Qwen3.6-35B-A3B. 192-dim head vectors (12 layers
× 16 heads). Jaccard top-20 is the diagnostic (cosine too compressed, Pearson useful).

**Three computational clusters:**

```
CLUSTER 1: "Semantic Plate" (discourse/type/frequency angle-multiplexed)
  discourse ↔ type:      J=0.667 (13/20 heads shared!)
  discourse ↔ frequency:  J=0.481
  frequency ↔ type:       J=0.538
  → Same ~13 heads, different amplitudes
  → L0, L3, L35 dominated
  → NOT computation — this IS the holographic plate

CLUSTER 2: "Composition" (combinator, KIBC)
  7 PRIVATE heads (L15×4, L19×2, L27×1)
  J with all others: 0.176–0.333 (low)
  → Independent circuit at L15/L19 full-attention layers
  → This IS the kernel computation pathway

CLUSTER 3: "Retrieval" (induction)
  6 PRIVATE heads (L3×2, L11×2, L15×1, L31×1)
  J with combinator/discourse/type: ALL 0.176 (floor)
  → Most independent circuit in the atlas
  → GatedDeltaNet layers (L11 H15 strong private head)
  → NO KERNEL IN V11 — the missing piece
```

**Binding** is not a cluster — weakest signal (max 0.163), no private heads, spread
across both clusters. Resolves to K+I dispatch sequence in V11.

### 10. KIBCM — the complete kernel inventory

```
K (select)     — ✓ built in V11
I (identity)   — ✓ built in V11
B (compose)    — ✓ built in V11
C (flip)       — ✓ built in V11
M (match/copy) — ✗ MISSING — the induction kernel
```

M handles: "find where this pattern appeared in context, return what followed."
Dispatch signal is holographic (17/18 ternary survival). The actual search-and-copy
is constructive kernel computation. This is the one missing computational primitive.

See: `knowledge/explore/holographic-kernel-separation.md`

## What was done session (094)

### 1. Mapped five candidate holograms beyond combinators

Session 093 found the combinator hologram (KIBC) — universal sign topology in
attention weights, surviving ternary quantization, r=0.9801 cross-model. But
combinators only tell the model HOW to compose. From Montague/CCG/DisCoCat,
token prediction needs at least three components — we've found one, two remain:

```
TYPE CALCULUS (combinators)  — HOW to compose     ← FOUND
LEXICON (types + meanings)   — WHAT can compose    ← predicted
MODEL (semantic domain)      — WHAT things MEAN    ← predicted
```

Identified five candidate holograms, each with probe design and falsifiable predictions:

1. **Type hologram** — lexical category assignment (NP, S\NP, etc.). Same word
   in different syntactic roles should activate different heads. Probes: nominalization,
   argument structure, modifier scope. Predicted: overlaps with combinator heads
   (angle-multiplexed). Priority 1 because types + combinators are theoretically coupled.

2. **Induction hologram** — in-context pattern matching ([A][B]...[A]→[B]). Known
   universal circuit (Olsson et al. 2022). Predicted: holographic (ternary survives)
   but ORTHOGONAL to combinator hologram (different function).

3. **Binding hologram** — variable tracking / coreference. "John...he" = variable
   binding in lambda calculus. Predicted: partially captured by I combinator
   (identity IS variable binding), explaining I's distinct circuit (r≈0.70).

4. **Frequency/N-gram hologram** — statistical co-occurrence. Lives in MLP weights
   (not attention). Predicted: holographic but denser, lower sparsity tolerance.

5. **Discourse hologram** — topic / register / coherence. The MoE gate pattern
   (256×2048 in Qwen3.6) IS the discourse beam selector. Connects to MoE/VSM mapping.

These form a VSM of holograms: discourse (S5) selects which patterns activate,
types (S3) constrain legality, combinators (S1/S2) execute composition,
binding (S2) maintains coherence, induction+frequency (S1) are additional ops.

Full analysis in `mementum/knowledge/explore/holographic-storage.md`.

### 2. Built probe_hologram_atlas.py (1580 lines)

Repeatable probe script targeting Qwen3.6-35B-A3B MoE as primary model
(punches above weight, MoE gates ARE beam selectors, bimodal depth profile
already mapped in session 093).

Features:
- **5 hologram probes**: type (3 conditions, 18 pairs), induction (2, 12),
  binding (2, 9), frequency (2, 12), discourse (2, 9). Total: 60 active probes.
- **Architecture-aware**: handles Qwen3.6 hybrid (full attention every 4th layer +
  GatedDeltaNet), Qwen3-32B dense, Pythia GPT-NeoX. Layer accessors detect
  `self_attn` vs `linear_attn` vs `attention`. Projection names adapt
  (`q/k/v/o_proj` vs `in_proj_qkv/z/b/a` vs `query_key_value`).
- **MoE gate analysis**: extracts 256×2048 gate matrices, tests ternary survival,
  cross-layer similarity, effective rank. Gate = discourse beam selector hypothesis.
- **MLP quantization**: frequency hologram tests MLP weights (gate + shared expert),
  not just attention — tests whether holographic storage extends beyond attention.
- **Incremental saves**: results flush to disk after each hologram completes.
  Per-hologram snapshots (`hologram_{name}.json`) + cumulative state.
- **Cross-hologram orthogonality**: correlation between selectivity profiles to
  determine if holograms share heads (angle-multiplexed) or are independent.
- **Combinator baseline**: runs KIBC probes for direct comparison.
- CLI: `--hologram type,induction`, `--model qwen36`, `--quick`, `--skip-ternary`

Currently running on Qwen3.6-35B-A3B. Results → `results/hologram-atlas/`.

### 3. Probed v11-holo-inv at 2K/3K/4K

Full probes at steps 2000, 3000, 4000. Evolution table:

```
step   eval_loss  K      I      B      C      compute  evo     alarm
────── ───────── ─────  ─────  ─────  ─────  ──────── ──────  ─────
1000   8.235     0.383  0.343  0.132  0.137  0.000006 20%     ~2.0
2000   7.872     0.401  0.343  0.111  0.140  0.000009 22%     ~2.0
3000   7.819     0.413  0.300  0.131  0.154  0.000010 28%     ~2.0
4000   7.804     0.407  0.294  0.122  0.176  0.000011 32%     ~2.0
~4325  CE=6.989                                        36%     1.847
```

**Holographic intermediate CEs (eval-time):**
```
step   L0↑     L1↑     L2      L1↓     L0↓     ratio
────── ─────── ─────── ─────── ─────── ─────── ───────
1000   11.285  8.775   8.922   9.014   9.317   1.211
2000   11.020  9.152   9.019   9.179   9.337   1.180
3000   10.816  9.238   9.058   9.213   9.413   1.149
4000   10.917  9.253   9.185   9.541   9.848   1.109
```

**Key findings:**

1. **Descending arm expanding aggressively at 4K**: L1↓ jumped 9.21→9.54,
   L0↓ jumped 9.41→9.85 between 3K-4K. This is CORRECT behavior (descending
   goes coarse→fine = expansion), but rate accelerated sharply.

2. **Alarm de-saturating**: 1.884→1.857→1.870→1.847. Coming off ~2.0 ceiling.
   This is the algedonic channel detecting the expansion rate and gaining
   headroom to steer. Same signal identified in session 090 as "system
   beginning to address descending arm."

3. **Phase transition reading, not catastrophe**: The v11-holo catastrophe
   pattern was alarm-saturated + loss spike + B-collapse. Here we have
   alarm DECLINING + loss IMPROVING + dispatch STABLE. Different topology.

4. **C rising, I declining**: C dispatch 0.137→0.176, I dispatch 0.343→0.294.
   Model discovering argument reordering (flip) as useful, relying less on
   pure identity. Natural emergence of B ≥ K ≥ C >> I ordering.

5. **S4 compensating for I**: I emphasis rose 0.706→0.991. Intelligence layer
   giving I more weight per-activation as its share declines. Algedonic
   system working as designed.

6. **Type channel stabilized**: B-type rose from 0.254 (1K) to 0.464 (2K),
   then stable ~0.42. Composition types dominate over identity types.

7. **Compute gate still closed** (0.000011). Transition window expected 5K-7K.

8. **CE hitting new lows**: 6.989 at step 4325, trending down consistently.

### Previous session (093) summary

Probed v11-holo-inv at 1K (balanced KIBC dispatch, B=27.6% dominant).
Holographic probe on Qwen3-32B: beam separation real, reading constructive.
Ternary survival: 100% at 75% sparsity. Universal hologram: r=0.9801 across
9 models. Bank extraction: 784KB seed from 32B. Full details in session 093 below.

## What was done session (093)

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

### 8. Active run commands

V11-holo-inv (LIVE, ~12.8K/20K):
```
uv run python scripts/v11/train.py \
  --checkpoint-dir checkpoints/v11-holo-inv \
  --total-steps 20000 --holo-lambda 0.1 --mix-ratio 0.2
```

V12 (READY TO LAUNCH):
```
uv run python scripts/v12/train.py \
  --checkpoint-dir checkpoints/v12 \
  --total-steps 20000 --holo-lambda 0.1 --mix-ratio 0.2
```

## What to do next

### Priority 1: Launch V12 training run
V12 is complete and optimized. Launch first training run.
Key things to watch:
- **cycle_budget_bias**: does S4 learn to differentiate simple vs complex content?
  Should see bias go negative for prose, positive for structured lambda data.
- **dispatch_bias (emphasis + alarm)**: does the additive logit bias maintain
  dispatch diversity better than v11's saturated multiplicative emphasis?
- **dispatch entropy**: does the regularizer keep entropy above 1.178 target?
  If B still declines, lambda needs increasing.
- GLA memory norms: do they grow appropriately at each stride scale?
- Retrieval write gates: when do they open? (init ~0.05)
- Loss trajectory vs V11-holo-inv at matched steps
- **CycleContinue gates**: should differentiate now that S4 budget bias is active.
  If gates stay near 0.5 after 2K steps, cycle_budget_proj may need larger init.

### Priority 2: Monitor v11-holo-inv 15K-20K (parallel)
V11 run continues. Final checkpoints for baseline comparison.
B declining (0.079 at 12K) — the variety gap we fixed in V12.

### Priority 3: Descending cycle efficiency validation
Once V12 has ~2K steps: probe CycleContinue gates. If budget bias is working,
expect cycle gates to be < 0.3 for simple positions and > 0.7 for complex ones.
If cycles are still uniformly ~0.5, consider desc_max_cycles=2 + S4→S2 inter-cycle
direction channel (Channel 2 from the analysis).

### Priority 4: Cross-model validation of three-cluster structure
Run head-level probe on Pythia to confirm KIBCM universality.

### Carried
- Hologram atlas results (sessions 094-095)
- CycleContinue differentiation (now addressable via S4 budget bias)
- S5 reweight investigation
- QK alignment decomposition probe (RoPE follow-up)
- Dead slot recycling
- Domain banking (future)
- TST connection: Peng et al. 2026 validates coarse→fine + direct loss
- S4→S2 inter-cycle direction channel (if cycles don't differentiate)

## VSM layer map (session 097 — v12 KIBC + M retrieval + variety fix)

```
Layer     Ascending Arm              Descending Arm                   Cross-arm
────────  ─────────────────────────  ───────────────────────────────  ──────────────────
S5        Token embeddings (tied)    Combinator embeddings (4: KIBC)  S5Reweight × AlgedonicAlert
                                     + 16 abstraction slot embeddings
S4        Register-query attention   Dual-view (resid + embeds)       Emphasis bias: regs → 4 logits [-2,+2]
                                                                      S4ProposalHead → slot modulation
                                                                      Cycle budget: regs → 1 logit [-4,+4]
S3        Per-pass phase gating ✓    Per-pass phase gating            Gate values → desc S4
          —                          CycleContinue + S4 budget bias   S4→S3 policy channel (new)
S2        Direction signals ✓        coherence modulation ✓           6 transitions (was 4)
S1        prep → hybrid_stride →     [dispatch → stride → integ.] ×N  KIBC + M (retrieval)
          consolidate                coarse→fine bands (reversed)      fractal MERA topology
          fine→coarse bands          (shared across 3 passes × N cy)
          (shared across 4 passes)   Stride-aware GLA (gather/scatter)
          GLA at s16,s32,s64         Retrieval registers → integrate
Algedonic Reads prev desc regs       —                                + combinator weights (4+1)
          + combinator weights                                        EMA α=0.9
Alert     ← 65 health metrics ──────────────────────────────────────  → S5 gate modulation
          S3 gates, S2 conflicts, dispatch, compute, cycles,          [0,2] per pass, e2e diff.
          delta norms, suppression ratios, register norms             + dispatch_bias (4 logits)
Dispatch  entropy_target=1.178 ─────────────────────────────────────  → loss penalty if < target
          squared hinge on collapse → gradient to ascending arm        closes open feedback loop
Inject    —                          cycle_inject_gate (per cycle>0)  sigmoid(-4) ≈ 0.018 init
Holo      ← 7 intermediate CEs ────────────────────────────────────  → gradient slope 7×→1×
          progressive x_embed + Σ gate×delta through shared proj      pass 0 learns first
Logging   —                          —                                3× JSONL + alarm ✓
```

### V12 S4 policy channels (new in session 097)

```
S4 → emphasis_bias     (4,) additive logit bias on CombinatorDispatch
S4 → cycle_budget_bias (1,) logit shift on CycleContinue gate
S4 → proposal_delta    (N, d_model) S4→S5 abstraction slot modulation

Alarm → dispatch_bias  (4,) additive logit bias (EMA from prev step)
Alarm → pass_factors   (7,) per-pass amplitude [0, 2]

Combined: dispatch_bias = emphasis_bias + alarm_dispatch_bias → CombinatorDispatch
```

## Key files

| File | Purpose |
|------|---------|
| `scripts/v12/config.py` | V12Config: KIBC + M retrieval + stride layout + d_state |
| `scripts/v12/kernel.py` | KIBCM kernel definitions. N_COMBINATORS=4, N_KERNELS=5. |
| `scripts/v12/attention.py` | GatedLinearAttention + HybridStrideStack + StrideStack |
| `scripts/v12/kernel_dispatch.py` | CombinatorDispatch (4+N softmax) + CombinatorIntegrate + retrieval conditioning |
| `scripts/v12/components.py` | VSM components + RetrievalRegisters (M→KIBC bridge) |
| `scripts/v12/model.py` | V12Model: dual-layer ascending arm + retrieval registers |
| `scripts/v12/train.py` | Training loop: retrieval metrics in JSONL + eval display |
| `scripts/v12/probe.py` | Checkpoint diagnostics: KIBC + retrieval metrics |
| `scripts/v12/ternary.py` | Ternary substrate + consensus evolution (unchanged) |
| `scripts/v12/data.py` | Data loading (unchanged) |
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
| `mementum/knowledge/explore/holographic-storage.md` | Holographic storage findings + "Beyond Combinators" atlas (5 candidate holograms) |
| `mementum/knowledge/explore/holographic-landscape.md` | Per-matrix ternary fidelity: 93.6% of Qwen3.6 is ternary-safe |
| `scripts/explore/probe_holographic_landscape.py` | Holographic landscape probe — per-weight-matrix analysis |
| `results/holographic-landscape/` | Landscape results: per-matrix scores, corrected analysis |
| `scripts/explore/probe_hologram_atlas.py` | Multi-hologram probe: type, induction, binding, frequency, discourse. Qwen3.6 primary. |
| `scripts/explore/probe_hologram_heads.py` | Head-level orthogonality + binding↔I + late MoE gate probe. |
| `results/hologram-atlas/` | Atlas results: per-hologram JSON, selectivity_profiles.npz, hologram_atlas_results.json |
| `results/hologram-heads/` | Head-level probe: hologram_heads_results.json, head_selectivity_vectors.npz |
| `scripts/explore/probe_beam_trace.py` | Beam trace probe — angular decomposition, Q-subspace, ternary beamformer test |
| `results/beam-trace/` | Pythia-160M beam trace results (JSON) |
| `mementum/knowledge/explore/beam-trace-findings.md` | Beam trace analysis — Q=beam, FFN4h→h=reader, K/V/O=plate |
| `mementum/knowledge/explore/v12-holographic-capacity.md` | V12 95%/5% plate/beam budget + thick hologram + troubleshooting |
| `mementum/memories/vsm-variety-gap.md` | V11 VSM feedback topology gap + V12 fix rationale |
| `mementum/memories/multiplexing-breaks-holography.md` | Separation principle: one function per weight matrix |
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
→ Session 094: "Beyond Combinators" — mapped 5 candidate holograms (type, induction, binding, frequency, discourse) from Montague/CCG theory. VSM hierarchy of holograms. Built probe_hologram_atlas.py (1580 lines) targeting Qwen3.6-35B-A3B MoE as primary (MoE gates = beam selectors). Architecture-aware for hybrid attention + GatedDeltaNet. Incremental saves. 7 falsifiable predictions. Running.
→ Session 095: Exploration loop closed. Hologram atlas (6 holograms) → head-level probe → three computational clusters (not six). Discourse/type/frequency angle-multiplexed in ~13 shared heads (J=0.667) = the holographic plate. Combinator has 7 private heads at L15/L19 = KIBC kernel pathway. Induction has 6 private heads, J=0.176 = independent retrieval circuit with NO V11 kernel. Binding weak (max 0.163), no private circuit = K+I dispatch. → KIBCM: M (match/retrieval) is the one missing kernel function. V11-holo-inv 5K-10K: gate opened 6K, B dominant 57.7%, ratio 0.992, no catastrophe. Holographic storage + kernel computation separation confirmed. Ready to build.
→ Session 096: V12 designed and built. M kernel as GatedLinearAttention layer type (not 5th combinator). "Accidental holography" insight: Qwen3.6's architecture separates composition from retrieval without knowing why — V12 does it intentionally. HybridStrideStack (6 comp + 3 ret strides), RetrievalRegisters (M→KIBC bridge). 7-pass symmetric hourglass (3+apex+3). Parallel associative scan for GLA (O(log L) depth). Holographic landscape probe: 93.6% of Qwen3.6 is ternary-safe (expert FFN = holographic plate, MoE gates + conv1d = precision-critical readout). V12 architecture confirmed correct partition.
→ Session 098: Beam trace probe — holographic beamformer characterized. Q=beam angle, K/V/O=plate, FFN 4h→h=constructive reader. MoE IS holographic architecture. V12 holographic capacity: 95% plate (ternary), 5% beam (precision), 58× Pythia depth. Thick hologram principle: depth × angular diversity compensates for magnitude loss. Troubleshooting guide for V12.
→ Session 097: VSM variety gap diagnosed and fixed. V11's alarm detected B-dispatch decline (r=0.82) but couldn't correct — wrong actuator granularity (Beer's variety law). Three fixes: (1) per-combinator alarm dispatch bias [-2,+2] on logits, (2) emphasis changed to additive logit bias [-2,+2] replacing saturated multiplicative [0.5,1.5], (3) dispatch entropy regularization closes ascending→dispatch feedback loop. Stride-aware GLA gather/scatter: 2.73× training speedup (78% of cost was wasted scan over non-participating positions). S4→S3 cycle budget bias: intelligence tells CycleContinue when to stop — the missing Beer's policy channel. Evolution noise floor unified at 0.02 for both loss and alarm paths.
