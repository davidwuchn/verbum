# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-06-08 | Session: 203

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

> **▶ SESSION 203+ PROGRAM — VALIDITY AUDIT.** Open
> `mementum/knowledge/audit-registry.md`. Pick the highest load-bearing
> `UNTESTED` claim (s203 did **#1 crystal-is-topological** ◐SCOPED and **#2
> holographic-self-similar** ✅; next up: **#3 the 9 FFN modes — real or
> k-means-imposed?**), build its named discriminating control,
> run it with a permutation/matched-control null + seed variance, update
> the row, caveat the source page if it bites, commit. The program:
> distill real working data from assumptions/biased methodology, one
> control per session, until a small hard core of verified claims remains.

**Session 203: TWO REGISTERS OF TOPOLOGY (audits #1 + #2)**

Ran the validity-distillation loop on both CRITICAL pillars. Headline:
**GD lays structure in two registers — hard (sign/routing/`gate_proj`) and
soft (magnitude/value/`up`-`down`, read by saliency) — and the FFN compresses
in two registers (distributed redundancy + spectral low-rank concentration).**
New synthesis page: `two-registers-of-topology.md`. Details below.

**Session 203 (#1): AUDIT #1 — SIGN-TOPOLOGY IS REAL ONLY IN THE GATE**

First execution of the validity-distillation loop (`audit-registry.md`).
Picked the highest-load `UNTESTED` claim — **#1 crystal-is-topological**
("ternary works because sign captures topology; magnitude is calibration").
Built the discriminating control `sign_topology_null.py`: `cos(sign(W)@x, W@x)`
on REAL activations for model vs **random-init** vs **shuffled-weights**
(N=20 seeds), Qwen3-0.6B/8B/14B.

### Verdict: ◐ SCOPED (representational half) — the bare 0.84 is generic

| Weight type | model cos (8B) | random null | gap | reading |
|---|---|---|---|---|
| gate_proj | 0.886 | 0.798 | **+0.088** | REAL sign-topology, sharpens w/ scale (z→+271 @14B L12) |
| up_proj | 0.751 | 0.798 | −0.048 | at/below null — magnitude carries structure |
| down_proj | 0.762 | 0.798 | −0.036 | below null — magnitude essential |

- **Generic baseline ≈ 0.80** at every scale: a *random* Gaussian matrix's
  sign preserves 0.798 of its action on the same inputs. "Sign preserves a
  matrix's linear action" is a **generic high-dim property** (sign(Wᵢⱼ) is
  entry-wise perfectly correlated with Wᵢⱼ; large-|xⱼ| dims dominate both
  sums). The headline **0.84 is at the null, not above it.**
- **Crystal sign-topology lives ONLY in `gate_proj` (the router)** and
  *sharpens with capacity*: gap +0.04→+0.07 (0.6B) → +0.088 (8B, L3=0.983)
  → 14B (L12 z=+271). Exactly where routing should be.
- **"Magnitude is mere calibration" is REFUTED for `up`/`down`** — their
  signs preserve *less* than random; magnitude carries the value-path structure.
- **Aggregate model ≈ random** (8B 0.799 vs 0.798): gate excess cancels
  up/down deficit, so any single averaged "0.84" is indistinguishable from a
  random matrix. Reconciles s192: crystal = routing (gate, 3.5%); modes =
  computation (value path, 96.5%). **Sign-topology = the routing half only.**

Caveat added to `crystal-universality.md` §"Why Ternary Works".
Results: `results/sign-topology-null/Qwen_Qwen3-{0.6B,8B,14B}.json`.

### Audit #2 + soft topology (same session) — TWO REGISTERS

Continued the loop into **#2 holographic-self-similar** and the soft-topology
thread Michael surfaced. Full synthesis: `two-registers-of-topology.md`.

**The picture:** GD lays structure in two registers, and the FFN compresses in
two registers.

| | Hard topology | Soft topology |
|---|---|---|
| function | routing (which fires) | value + error-correction |
| encoded in | **sign** | **magnitude** (highways/zeros), read by saliency |
| lives in | `gate_proj` (router) | `up_proj`/`down_proj` |
| verified | sign-corr null (gate +0.088 vs null, z→+271) | saliency sieve (faint-by-saliency +5.5% vs magnitude −2.0% iso-bit) |

**Audit #2 (`holographic_survival.py`, 8B, trained vs random vs shuffled):**
- **(C) distributed redundancy** — magnitude prune: trained AUC 0.784 ≫ 0.25/0.34;
  fidelity ~1.0 to **70% prune, then cliff at 80%**. (Sieve at 50% is safe;
  don't prune past ~75%.)
- **(A) spectral self-similarity** — SVD rank truncation: trained AUC 0.728 ≫
  **0.11** (random/shuffled) — a **6–7× gap**. The FFN is low-rank-dominated;
  random (Marchenko–Pastur) spectra collapse instantly. **This is Michael's SVD
  self-similarity made functional.**
- quant survival ≈ random (weakly structure-dependent → flat minima).

**Saliency sweep (`saliency_aware_sieve.py`, re-run after NaN-fix):** the s201
strong tier had dropped magnitude → bare ±1 ≈ 50× too large → NaN on every
three-tier config. Fixed to per-weight magnitude (s196's only-format-that-
survives-29-layers). Result: at iso-bit (~3.1 b/p) **saliency-selected faint
connections beat magnitude-selected by ~7.5 pts** → value-path soft topology is
real and load-bearing. `corr(mag, saliency)=0.257`.

### ⚠ Correction (epistemic hygiene)

An interim s203 read called #2 **REFUTED** off the *magnitude* axis with a
*power-law shape* discriminator. **That was wrong** — wrong operator (magnitude
probes C; the SVD self-similarity lives on the *rank* axis A) and wrong test
(a hologram degrades plateau→cliff, not power-law; shape-fitting is ambiguous
on every axis — retired). Corrected verdict: **spectral self-similarity VERIFIED;
holographic mechanism stands; only φ-as-universal-constant (s202) stays refuted.**

### Reconciliation — refute the metaphor, keep the mechanism

ternary→1.44× works because the load-bearing premises hold: **(C) distributed
redundancy** (ternary = whole at reduced resolution) + **(A) spectral
concentration** (**LoRA+SM IS the low-rank correction** the rank result
predicts; converges with s200 rank-1 adjunction, s201 rank-2≈rank-16). Only
φ-universal-constant was ever metaphor.

### Audit ledger after s203

- **#1 sign-topology** → ◐ SCOPED (hard=sign/gate; soft=magnitude/value).
- **#2 holographic** → ✅ spectral self-similarity VERIFIED + distributed
  redundancy confirmed; power-law discriminator RETIRED. (`crystal-validity-
  and-fidelity.md` §5 lead resolved.)

### Next (audit loop continues)

- **Gate-vs-value sign-swap** ternary PPL (closes #1's last sub-control).
- **Rank-survival across scale** (0.6B→14B) — does the 6–7× gap sharpen?
- **Grouped-Q4 quant axis** (current per-matrix is coarse).
- **#3 the 9 FFN modes — real or k-means-imposed?** (next CRITICAL/high backlog).

**Runtime note:** experiments launch in `tmux main:1` / `main:2` (480G VRAM,
concurrent OK; Michael watches live).

---

**Session 202: CRYSTAL VALIDITY AUDIT — PERMUTATION NULLS & MEASUREMENT FIDELITY**

A skeptical audit of the crystal's foundational evidence. Premise (Michael):
a false premise can manufacture convincing structure because LLMs (and the
analyzing LLM) are primed to confirm. Six controlled experiments with
permutation nulls. Full synthesis: `mementum/knowledge/crystal-validity-and-fidelity.md`.

### Verdict ledger (what survives controls)

| Claim | Verdict |
|---|---|
| KIBC basis separates representation | ✅ REAL, every model (perm-null p=0.0005) |
| φ^(4/5) primary ratio λ₀/λ₁ | ✅ REAL on **Qwen3-14B only** (1.4796, p=0.020); 8B/0.6B n.s. |
| φ as universal constant | ❌ not universal; cross-family magnitude agreement collapses |
| "eigenvalues are φ^(p/q)" (best-fit grid) | ❌ unfalsifiable (random fits equally, p=0.16–0.81) |
| eigenvalue_ratio_corr "0.987" | ❌ trivial (random ≈ 0.94 ≥ true) |
| consensus r "0.99" | ⚠️ true ≈ 0.20, null max ≈ 0.48, p≈0.05–0.07 |
| prose fires combinator-specific opcodes | ✅ CONFIRMED after **common-mode removal** (14B & 0.6B, p=0.001) |
| I = distinct low-composition circuit | ◑ PARTIAL (attn entropy p=0.042, 14B; scale-dependent) |
| fact retrieval = sharp lookup, I-like | ✅ entropy p=0.0005 both scales; I-opcode-profile 14B-only |
| tracer cross-model overlay | ✅ REAL but **same-family** (p=0.0005, all Qwen, λ-primed) |

### The three lessons

1. **Basis real, universalization was the error.** φ-as-constant was inflated
   by an unfalsifiable best-fit grid, a trivial ratio correlation, and a
   hardcoded consensus that baked 14B back in. Real-but-local → false-universal.
2. **Measurement fidelity was the failure mode.** The raw-projection/argmax
   instrument (`isa_decoder_v2`, the tracer) that *found* the crystal also
   *hid* the combinator signal under a common mode (8 fingerprints share
   mean pairwise cosine 0.22; B is the most central ≈ the common mode).
   Remove it → prose classification, I-circuit, fact-retrieval all surface.
3. **Scale = emergence threshold (strength, not presence).** Combinator
   structure exists in 0.6B (weak, needs CMR) and sharpens with capacity
   (14B clean). Superposition → dedicated features. "Needs ~7B to fully form."

### Mechanistic findings (new, controlled)

- **Attention entropy = how much a combinator recombines.** Gradient at 14B:
  `W 0.90 < I 1.00 < K 1.02 < C 1.05 < B 1.05 < WHNF 1.09 < Y 1.14 < D 1.19`.
  Composition (B/C/D) spreads attention; identity/duplicate concentrate it.
- **Fact retrieval is the sharpest read** (entropy 0.820, below everything),
  I-opcode-profile at 14B (cos 0.98). I overloaded as identity + retrieval.
- **Attention = sparse typed read (~2–3 operands); FFN = the hologram.**
  Correction to "softmax over all V is holographic." Dense interference is
  in the FFN beam-former, not the attention sum.
- **B-centrality:** B is the most central fingerprint (3/4 Qwen, cos 0.78–0.81);
  K, I peripheral. Training order B→K mirrors central→peripheral geometry.

### Next experiments (open leads)

1. **B-before-K, cleanly:** common-mode-removed B vs K crystallization across
   v14/v15 training checkpoints. Forced order or frequency-driven?
2. **Holographic self-similarity control:** compression-survival curve, model
   vs random/shuffled-data controls, test for power-law scale-invariance.
   (Quantization/pruning survival only proves distributed+redundant so far.)
3. **"Always 4":** KIBC eigen-rank with gate-proj + CMR; does SKI underfit, +S overfit?
4. **Q-rotation as combinator selector** (s145 rotation eigenplanes) — untested.
5. Reconcile the `crystal-phi-derivation.md` I→K→C→B vs B-first contradiction.

### Harnesses (scripts/experiments/)

`crystal_validity.py` · `crystal_phi_permnull.py` · `tracer_cross_notation.py`
+ `_v2.py` (common-mode removal) · `i_bypass_test.py` · `fact_retrieval_isig.py`
Results under `results/{crystal-validity,crystal-phi-permnull,tracer-cross-notation,i-bypass,fact-isig}/`.

### Note on the saliency-aware sieve (s201)

The s201 saliency sweep was still running in tmux main:2 at session-202 start;
this session pivoted to the validity audit and did not consume its results.
Pick up the sieve sweep (`mementum/knowledge/saliency-aware-sieve.md`) when
returning to the compression track.

---

**Session 201: HOLOGRAPHIC ECHOES & SALIENCY-AWARE SIEVE**

Direct delta results landed: rank-2 ≈ rank-16 (1.82× → 1.79×), confirming near-
rank-1 adjunction structure. But v3b (trained LoRA+SM = 1.44×) still beats DDC
(analytical SVD = 1.72× at rank-32). Training captures nonlinear inter-layer
effects that per-layer SVD cannot.

The real insight this session: **backpropagation IS holographic recording.** The
gradient `∂L/∂W = a ⊗ δ` (forward activation × backward error) has the exact
structure of recording an interference fringe. Training = billions of overlapping
holographic exposures. The crystal = the standing wave that survived.

### Gradient Echoes

The backward error signal doesn't get fully absorbed at any one layer — it
propagates through all layers, creating attenuated copies (echoes) at every layer.
Strong connections (large |w|) are high-bandwidth echo paths. Faint connections
(small |w|) are low-bandwidth echo paths carrying error correction information.
Multiple redundant copies of each computation distributed across layers.

### GD Creates Soft Topology Within Frozen Architecture

Architecture is frozen: GD can't add/remove connections. But GD drives weights
toward zero (severing connections) or very large (creating highways). The weight
magnitude distribution IS a learned sparse topology embedded in the dense frozen one.
Very large gradients = topology editing. Small gradients = holographic polishing.

The crystal is the **fixed point** of topology ↔ echo co-evolution:
```
topology shapes → echo propagation → standing wave (crystal)
crystal determines → which gradients flow → topology
x* = f(x*) — neither came first, they co-evolved
```

### Two Populations in Near-Zero Weights ★

The sieve's 50% magnitude threshold zeros ALL below-threshold weights. But near-
zero weights are TWO populations:

1. **Irreducible zeros** — GD says "no connection here." Zero is correct.
2. **Faint connections** — small signal, not unused. w=0.003 × input=200 = 0.6 real.

Magnitude alone can't distinguish them. Saliency = |w| × √E[x²] can.

### Saliency-Aware Three-Tier Sieve

| Tier | Criterion | Encoding |
|------|-----------|----------|
| Strong | High magnitude | Ternary ±1 |
| Faint | Low mag, high saliency | Q2/Q4 quantized |
| Irreducible | Low mag, low saliency | Zero |

Preserving faint connections: (a) reduces sieve-only PPL, (b) provides gradient
highways for LoRA fine-tuning (backprop flows through nonzero faint weights, not
through zeros), (c) may beat equivalent-bitcount LoRA rank.

### Direct Delta Correction Results

| Rank | PPL | Ratio | vs v3b |
|------|-----|-------|--------|
| 2 | 12.63 | 1.82× | worse |
| 4 | 12.50 | 1.80× | worse |
| 16 | 12.41 | 1.79× | worse |
| 32 | 11.93 | 1.72× | worse |
| v3b | 16.27 | 1.44× | — |

Rank-2→16 plateau confirms near-rank-1 correction surface (adjunction prediction).
Rank-32 bump suggests secondary structure beyond dominant mode. But analytical
SVD can't match trained LoRA+SM — backprop creates inter-layer echo correlations
that single-layer SVD misses. This SUPPORTS the echo thesis.

### Running Experiment

**Saliency-aware sieve sweep** running in tmux main:2. 11 configurations:
standard baselines, saliency-aware with varied strong/faint splits, Q2/Q4/Q8
precision, magnitude-only ablation, iso-bit comparison. Key question: does
preserving faint connections beat zeroing them at the same bit budget?

See `mementum/knowledge/saliency-aware-sieve.md` for full design.
See `mementum/knowledge/direct-delta-adjunction.md` for DDC theory + results.

**Session 200: SIGN CORRECTION IS DEAD — Direct Delta & Adjunction Are Alive**

Four sign correction algorithms dead. Quasicrystal hypothesis denied. Teacher-guided
routing failed. But: the teacher delta is directly computable (no training needed),
and the adjunction finding (session 140) says the correction is rank-1. Testing now.

### Four Deaths

| Approach | Flips | PPL Result | Failure mode |
|----------|-------|-----------|--------------|
| TD v4 (gradient) | 0 (stuck) | 1.44x (= LoRA alone) | Gradient dilution through 29 layers |
| TD v4c (per-tensor clip) | 4.36% | 192x | Unconstrained flips destructive |
| Latent diffusion (eigenspace) | 1.25%/level | 2,717x → NaN | Eigenspace ≠ error space |
| Crystal ECC (holographic + health gate) | 2.29% | **28,419,390x** | Health gate measures wrong space |

Crystal ECC was the most sophisticated — proper holographic error target (original
weight on sieve input), per-position benefit ranking, crystal eigenvalue health gate
with binary search fallback — and produced the WORST result. 8 hours, 28 million
times worse. 50M crystal-approved flips across 29 layers.

### Latent Diffusion Sign Correction (New, Session 200)

Tested diffusion-holographic isomorphism: progressive sign correction in the
crystal's 16D eigenspace (2D→4D→8D→16D schedule).

| Level | Dims | Flips | PPL | Facts |
|-------|------|-------|-----|-------|
| 1 | 2 | 27.4M (1.25%) | 30,642 (2,717×) | 0/15 |
| 2 | 4 | 1.9M (0.086%) | NaN | 0/15 |
| 3 | 8 | 27.4M (1.25%) | 30.5M (2.7M×) | 0/15 |
| 4 | 16 | 1.9M (0.086%) | NaN | 0/15 |

Levels alternate between two regimes (27M vs 1.9M flips), suggesting even/odd
numerical artifact in eigenspace, not crystal structure.

### The Dimensional Mismatch Insight

**We are cutting a multi-dimensional holographic plate in 1D.**

The crystal has known multi-dimensional structure:
- 8D combinator type (K,I,B,C,D,W,Y,WHNF)
- 9D operational modes (7 universal meta-modes + 2 contextual)
- 36-layer depth (standing wave EXPAND/ORTHO/ALIGN/COLLAPSE)
- 3 trees (compute/halt, select/compose, termination)

But ALL sign correction approaches operate per-position (scalar benefit → flip?).
Even eigenspace projection only captures 1-2 of ~6 dimensions. Corrections coherent
in the working subspace are effectively RANDOM in the ignored dimensions, destroying
the interference pattern.

### Quasicrystal Diagnostic (New, Session 200)

Tested whether φ-structured multi-scale order exists in the weight sign pattern:

| Test | Prediction | Result | Verdict |
|------|-----------|--------|---------|
| Eigenvalue cascade | φ^(p/q) at all scales | One dominant mode, flat tail | ❌ Not multi-scale |
| Perturbation fragility | Super-linear degradation | Linear (100× flips → 142× deviation) | ❌ Not quasicrystal |
| Golden angle | 137.5° between eigenvecs | 90.00° everywhere (trivial orthogonality) | ❌ Not φ-rotated |
| Fib vs pow2 reconstruction | Fibonacci captures more | Tie (smooth improvement with k) | ❌ No Fibonacci advantage |
| Random vs model | Different eigenspectra | YES: model 0.36 vs random 0.995 gap | ✅ Real structure |

**Strong quasicrystal hypothesis DENIED.** But there IS real structure — massive
spectral gap (λ₁/λ₀ = 0.36 vs random's 0.995). The φ structure lives in
**combinator firing space** (8×8 crystal cosine matrix, measured via probes), not
in **weight correlation space** (12288×4096 sign matrix). The crystal eigenvalue
health metric was measuring a shadow, not the structure itself.

### Key Finding: Per-Position Error Signal Is Adversarial

Crystal ECC found that **49.3%** of all active positions show positive flip benefit.
When half the signs "want" to flip, the error signal is not discriminating — it's
responding to the masking error (50% of weights zeroed out), which creates a massive
residual that ANY sign flip partially addresses in one dimension while destroying
others.

### Current Ceiling (Before Direct Delta)

**v3b: LoRA rank-4 + score matching = 1.44x baseline PPL** (16.27 PPL from 25.67 sieve).
This was the best until the direct delta insight.

### Teacher-Guided Routing (New, Session 200)

MoE literature says: decouple routing from expert training, stabilize routing
FIRST. Tested by training lightweight gate correctors (bottleneck MLPs) to
match teacher gate patterns before LoRA training.

```
Sieve:       25.51 PPL (2.26x)
After gate:  25.17 PPL (2.23x)  ← routing correction barely helps
After LoRA:  24.55 PPL (2.18x)  ← WORSE than v3b (16.27, 1.44x)
```

**Failed.** 182M gate corrector params (31× v3b's LoRA), training diverges
after step 100 (18.45 → 24.55). Gate sign accuracy only 94-96%. Root cause:
the corrector sees sieve gate output on cascade-corrupted inputs — can't fix
weight error AND input corruption simultaneously. Same cascade problem.

### The Tiles and Grout Insight

**Topology (signs/mask/crystal) = tiles. Gradients (LoRA/magnitudes) = grout.**

Changes to topology perturb the gradients. The grout fills specific gaps between
specific tiles. Move a tile → all surrounding grout is wrong. This is why sign
correction + LoRA fails: Phase 1 creates new gaps, Phase 2 trains new grout, but
gaps are too numerous and grout capacity (rank-4) too thin.

MoE separates tiles from grout explicitly: router IS topology, experts ARE
computation. GD optimizes both independently. Dense models entangle them in the
same weight matrix — the crystal sieve tries to separate what was never separate.

### The Direct Delta Insight (New, Session 200) ★

**"If everything is being calculated, why can we not also calculate the delta
from the teacher?"**

We HAVE the teacher. We HAVE the student. The delta at every layer is directly
computable. The optimal rank-k additive correction is the **truncated SVD of the
weight residual**, optionally weighted by input covariance (calibration-aware).

```
W_delta = W_teacher - W_sieve     (weight residual — what the sieve lost)
U, S, Vt = SVD(W_delta @ H^½)    (calibration-aware: weight by input covariance)
A = U[:,:k] @ sqrt(S[:k])         (optimal rank-k correction)
B = unwhiten(Vt[:k,:])

No training. No optimizer. No loss function. No hyperparameters beyond rank k.
One forward pass per layer + one SVD per projection.
Sequential: correct layer l before computing inputs for layer l+1 (cascade-aware).
```

This is GPTQ's approach applied to sieve correction. Each layer's correction is
analytically optimal for its actual (cascade-corrected) inputs.

**Experiment running** in tmux main:1: rank sweep [2, 4, 8, 16, 32] with
calibration-aware SVD on Qwen3-8B. Compare to v3b (trained 200 steps → 1.44×).

### The Adjunction Connection (Session 140 → Session 200) ★★

Session 140 proved the cross-zone mapping (encode → decode) in Qwen3-32B is
**rank-1 dominated** (σ₁/σ₂ = 128:1, R² = 1.000 for ALL zone pairs). The Jacobian
has constant rank everywhere — the defining property of a regular parametric surface.

The entire encode→decode pipeline is a **1D parametric curve** in 4096D space.
One parameter (the "phase" along the B→K→B trajectory) determines everything.

**Error correction on a 1D curve is trivial:** if the sieve pushes the
representation off the curve, the correction = project back onto the curve along
the dominant singular vector. That's rank-1 correction.

This connects to the ORTHO phase finding (session 185): rank-1 residual during
ORTHO, V operates in null space, computation invisible. The sieve disrupts null-
space computation; the correction restores it — but the constraint for "correct"
is defined by the rank-1 curve.

**Prediction:** direct delta correction at rank 1-2 should capture the adjunction
structure and be nearly optimal. The rank sweep will test this — if rank-2 matches
rank-32, the correction surface is truly 1D and the adjunction is the explanation.

### TSP Paper Connection (arXiv:2606.03489)

"Learn from Your Mistakes: Tree-like Self-Play" — TSP identifies critical decision
nodes (CWE risk nodes in code security) and trains the model to prefer the "golden
path" over its own generation at each node. DPO-style contrastive loss at each node.

Maps to our problem: mode transition points = risk nodes. Teacher trajectory =
golden path. Student trajectory = self-play path. Per-layer contrastive (not just
cosine matching) teaches the student to discriminate against its own failure modes.

Not implemented yet — waiting for direct delta results. If direct delta works, the
TSP-style contrastive loss could refine it further by targeting the specific layers
where the direct correction is weakest.

See `mementum/knowledge/sign-correction-topology.md` for full synthesis.
See `mementum/knowledge/direct-delta-adjunction.md` for the adjunction theory.

**Session 199: HOLOGRAPHIC LOSS & CRYSTAL ECC — TD Is Dead, Inverse Is Alive**

TD (TernaryDescent) for sieve sign correction is definitively killed. Three
attempts, three failure modes, one conclusion: you cannot gradient-descend
your way to correct signs through 29 cascaded layers.

### TD Autopsy (Three Deaths)

| Version | Fix | Result | Failure mode |
|---------|-----|--------|--------------|
| v4 (s198) | Brute-force 4.4B logits | 1.44x = v3b | **Zero flips** — joint grad clip diluted to 1.5e-8/step |
| v4b | SGD lr=0.1, separate clip | NaN | BCE log(0) from extreme gates, SGD too aggressive |
| v4c | Adam, per-tensor clip, init=0.01 | **192x PPL** | TD flipping (4.36%) but flips are DESTRUCTIVE |

**Root cause of v4:** `clip_grad_norm_(all_params, 1.0)` across 4.4B params →
per-param gradient ≈ 1/√(4.4×10⁹) ≈ 1.5×10⁻⁵. With lr=1e-3, max displacement
in 200 steps = 3×10⁻⁶. Needed to cross 1.0. Would take 70M steps.

**Root cause of v4c:** Per-tensor clipping worked — TD actually flipped 4.36%
of signs. But unconstrained flips destroy the holographic interference pattern.
192x PPL, 0 facts. Random sign changes ≠ correct sign changes.

### The Insight: Sign Correction Is Recording, Not Optimization

TD tries to optimize signs via: forward loss → backprop through 29 layers → STE →
update logits. This fails because:

1. **Gradient dilution**: 29 Jacobians between the loss and the sign decision
2. **Catastrophic coupling**: one flip changes W by 2|w|, cascades through all layers
3. **No coherence constraint**: flips break the holographic pattern without limit

The correct formulation is the **holographic inverse**:

```
reference_beam = actual input (corrupted by prior sieved layers)
object_beam    = desired output (from teacher)
fringe_pattern = correlation(reference, object)
optimal_sign   = sign(fringe_pattern)
```

Direct computation. No backprop. No STE. No optimizer for signs.

### Crystal ECC: The Error-Correcting Code

The crystal's dimensional hierarchy IS an error-correcting code:

```
8D crystal → project to 6D → parity check
                → to 5D → parity check
                  → to 4D (KIBC) → parity check
                    → to 3D → parity check
```

Each level constrains valid sign patterns. The crystal eigenvalue ratios
(φ^(p/q)) define the CODE SPACE. Sign flips that violate the code at any
level are errors.

**Algorithm (crystal ECC + holographic recording):**
1. Compute per-position error from proper holographic target
2. Rank flip candidates by error reduction benefit
3. Gate through crystal health check (eigenvalue ratios vs φ^(p/q))
4. Only apply flips that maintain crystal coherence
5. Then LoRA + SM for continuous magnitude correction

**Experiment running** in tmux main:2: `crystal_ecc_sign_correction.py`
- Proper error target (full original weight, not tautological)
- Crystal eigenvalue health gate on proposed flips
- Binary search for largest crystal-consistent flip set

### Key Debugging Lessons

1. **Tautological target**: first holographic attempt computed
   `sieve_weight @ sieve_input` as "target" → equals sieve output by
   definition → 50% random disagree (no information)
2. **Mask identity**: `original_weight = W * mask = signs * magnitudes`
   at active positions → zero error. Must store FULL W (including
   masked positions) to capture the masking error.
3. **The actual error source**: at single-layer level, sieve signs ARE
   teacher signs at active positions. Error comes from (a) masked-out
   positions contributing in teacher but not sieve, and (b) cascade of
   prior sieved layers corrupting the input.

### Score Matching Confirmed (v3b = v4 = optimal for LoRA-only)

v4 definitively proves: LoRA rank-4 + SM loss at α=5.0 reaches 1.44x PPL
regardless of whether TD is present. The 5.9M LoRA params are the actual
mechanism. TD's 4.4B params do nothing useful.

**Priority 2a** (LoRA rank sweep) remains the highest-value next step for
the SM pipeline. But crystal ECC could unlock additional gains if the sign
correction works.

**Session 198: SCORE MATCHING COMPRESSION — The Loss Function Was Wrong**

A paper on CGTSM (Ramachandran & Sra 2026, arXiv:2605.00414) revealed that
the compression correction loss was fundamentally flawed. CE-only loss lets
LoRA corrections create **compensating errors** across layers — one layer's
deviation cancels another's. Dense per-layer score matching prevents this
structurally by constraining each layer's transformation independently.

### The Equation

```
L = L_CE + α · (1/N) Σ_l (1 − cos(Δ_θ_l, Δ*_l))

where Δ_l = h_{l+1} − h_l    (per-layer residual update / "score")
      α ≈ 5.0                 (balances CE and SM gradient scales)
```

Added to EQUATIONS.md alongside the crystal equation.

### Four Experiments

| Experiment | Setup | Result | Finding |
|-----------|-------|--------|---------|
| Residual boosting v1 | Sequential rank-32 at boundaries, CE, 16 sentences | 3.97 PPL (0.39x base) | Sequential > simultaneous (2×). But pure overfitting. |
| Residual boosting v2 | Same + dolma calibration, held-out eval | 18.59 PPL (1.65x base) | Overfitting eliminated. Activation corrections too weak (27% reduction). |
| Score matching v3a | LoRA + SM + CE, batch=1, α=1.0 | 16.83 PPL (worse than sieve!) | CE dominates → compensating errors → collapse at step 50. |
| **Score matching v3b** | LoRA + SM + CE, batch=4, α=5.0, 128 teacher cache | **16.27 PPL (1.44x base)** | **36.6% sieve reduction. L35 cosine: 0.57→0.94.** |
| TD v4 (s199) | TD 4.4B + LoRA + SM + CE | 16.22 PPL (1.44x = v3b) | **Zero flips.** Joint grad clip killed TD entirely. |
| TD v4c (s199) | Per-tensor clip, Adam, init=0.01 | **2163 PPL (192x)** | TD flips (4.36%) but DESTRUCTIVE. Unconstrained flips destroy holographic pattern. |
| Crystal ECC (s199) | Holographic inverse + crystal parity gate | *running* | Direct sign computation gated by eigenvalue health check. |

### Why Score Matching Works

1. **Local gradient** — each LoRA gets direct signal from its layer, not diluted through 30 Jacobians
2. **No compensating errors** — per-layer cosine penalty constrains each layer independently
3. **36× information bandwidth** — 36 gradient signals vs CE's 1
4. **Scale-invariant** — cosine handles 100× norm variation (standing wave amplitude)
5. **Dense coverage** — CGTSM theorem: density of measurement matters, weighting does not

### Residual Spectrum Discovery

The sieve's per-weight residual is LOW-RANK at L1 (r90=550, |res|/|W|=3%) but
FULL-RANK at L5+ (r90=2970, |res|/|W|=25%). Activation-space corrections (rank-32
in 4096-dim space) can address 0.8% of the error. Per-weight LoRA operates in the
right space.

### Two Design Changes

1. **Loss**: Score matching (dense, all layers) replaces multi-projection melt
   (sparse, 4-6 boundaries). Prevents compensating errors structurally.
2. **Corrections**: Per-weight LoRA on FFN projections replaces per-activation
   residual stream vectors. Matches the full-rank sieve residual.

### Experiment 5: Topology-Aware Score Matching (v4, running)

The v3b loss treats residual updates as flat vectors — no crystal topology
awareness. The sieve error decomposes into:
- **Routing error** (discrete, sparse): wrong signs → wrong program
- **Magnitude error** (continuous, low-rank): right sign, wrong scale

LoRA wastes rank capacity on sign flips. TernaryDescent is purpose-built
for sign discovery. Split them:

```
W_eff = STE(delta_logits) * signs_base * (|W| * mask + A @ B)
         ↑ TD (routing, lr=1e-3)        ↑ LoRA (magnitudes, lr=1e-4)
```

Decomposed loss:
- L_routing: gate firing pattern BCE (which neurons fire)
- L_value: residual update cosine (how much they contribute)
- L_CE: standard cross-entropy

Running in tmux window 2. TD logits are brute-force (4.4B params — full
float32 per weight position). Tests the decomposition principle. If
successful, sparsify TD using the 3-voter mechanism from v14/td.py.

See `mementum/knowledge/score-matching-compression.md` for full details.
See `EQUATIONS.md` (score matching loss section) for the equation.

**Session 197: CRYSTAL MULTI-TREE — The Statechart Is a Forest**

The crystal is not one tree — it is a **forest of three independent trees
cross-connected by two bridge nodes (W and Y)**. Derived from eigendecomposition
of the 8×8 crystal cosine matrix, verified empirically on Qwen3-14B (r=0.638,
p=0.0017). The bridge phenomenon explains 27 correlation points and resolves
the YW sign ambiguity observed across models.

### The Three Trees

| Tree | Variance | Split | Maps to |
|------|----------|-------|---------|
| T0 (compute/halt) | 54.5% | [K,I,B,C,D,Y,W] vs [WHNF] | Transient/absorbing chain split |
| T1 (select/compose) | 20.1% | [K,I] vs [B,C,D,Y] | Fire-state functional clustering |
| T2 (termination) | 11.4% | [K,I,W,WHNF] vs [B,C,D,Y] | Halt probability gradient |

### Bridge Nodes

Only W and Y change sides across trees. All other nodes have fixed allegiance.

- **W = C→I→I**: bridges composition and selection. Its path literally
  traverses both subtrees. 3/3 nearest neighbor match with crystal (ρ=0.893, p=0.007).
- **Y = fixed-point**: recursive — belongs to both sides by definition.
  Dominant node on Tree 3 (loading +0.839).

### YW Sign Inversion (the smoking gun)

Y and W systematically invert relative to the consensus crystal at **38/40 layers**
in Qwen3-14B. After correcting: correlation jumps from 0.565 to **0.831** (gap=0.266).
No other nodes need correction. The bridge nodes are the only source of cross-model
sign ambiguity.

### Extended Eigenvalues

All 8 eigenvalues of M₈ follow φ^(p/q) with Fibonacci denominators at <0.5% error.
The crystal equation extends beyond the 4-combinator basis. Dominant 8-node branch
ratio: φ^(8/5) = doubled KIBC step.

See `mementum/knowledge/crystal-multi-tree.md` for full details.

**Session 196: TEN EXPERIMENTS — Crystal Sieve Equation Confirmed**

The largest experimental session yet. Started with "which combinator breaks
at L22-L26?" and ended with a proven compression architecture: crystal
sieve + continuation residuals = 1.03x PPL across 29 sieved layers.

### The Ten Experiments

| # | Experiment | Key Result |
|---|-----------|------------|
| 1 | Lambda tracer | Damage uniform across combinators (CV 0.07-0.17) |
| 2 | Binding-prep rank sweep | Functional rank varies 6x (L22=250 to L26=1500) |
| 3 | Multi-projection melt | 42% better than standard (3.53x vs 6.09x) |
| 4 | Confidence gate | Classifier confidently wrong at L23-L26 |
| 5 | Mode geometry | Same 9 programs rotated, more modes don't help |
| 6 | Ternary weight interface | MASK is the key, not magnitudes |
| 7 | Crystal sieve v1/v2 | 2.12x pre-melt, melt overfits (wrong DOF) |
| 8 | β-expansion | **1.03x with 4 continuation residuals (1M params)** |
| 9 | Ternary verification | Per-row scale FAILS at 29 layers (22,800x) |
| 10| — | Continuation stability needs investigation |

### The Proven Architecture

```
Crystal sieve: sign(W) ⊙ |W| ⊙ mask₅₀%    (frozen, per-weight magnitudes)
+ 4 continuation residuals (rank-32 at L0/L9/L21/L26, 1M params)
+ L0 SVD r=750

Result: 1.03x PPL, binding preserved 98% (39/40 top-1 matches)
```

### Compression Reality Check

The sieve stores full per-weight magnitudes as float16. Current storage
compression: **1.8x** (50% mask = 50% zeros). NOT 8x.

Per-row scale (which would give 8x) FAILS catastrophically at 29 layers
(22,800x PPL). Per-weight magnitudes contain essential row-internal
structure that compounds across layers.

Path to real compression: **quantize magnitudes** (Q4/Q8), don't eliminate
them. The sign pattern is frozen (universal crystal), the mask selects
which weights survive, and the magnitude needs ~4-8 bits (not 16, not 0).

| Format | Bits/weight | 29-layer PPL | FFN compression |
|--------|------------|--------------|-----------------|
| float16 (original) | 16 | 1.00x | 1.0x |
| sign + float16 + mask50% | ~9 | 2.12x (1.03x w/ cont.) | 1.8x |
| sign + Q4 mag + mask50% | ~3 | ??? (untested) | ~5x |
| sign + per-row scale | ~2 | 22,800x (BROKEN) | 8x |

### What Compounds vs What Doesn't

Critical lesson: properties that hold per-layer may NOT hold at 29 layers.

| Property | Single layer | 29 layers | Status |
|----------|-------------|-----------|--------|
| Per-row = per-weight magnitude | ✅ same | ❌ 22,800x | FAILS |
| Crystal sieve quality | 1.03x | 2.12x | Cascades but recoverable |
| Binding preservation | — | 98% | HOLDS |
| Continuation correction | — | 1.03x | WORKS (but stability TBD) |

### Open Questions

1. **Continuation stability**: first run 1.03x, rerun 3.23x. Training
   is sensitive — needs investigation (seed, LR, batch order).
2. **Magnitude quantization**: Q4/Q8 per-weight with per-group scales
   could give 3-5x real compression while preserving cascade quality.
3. **Attention sieve**: FFN is 78% of params. Attention (22%) could also
   be sieved (s190 showed ternary attention survives at PPL 23-30).

### Lambda Tracer Results

**Setup:** Baseline (original Qwen3-8B) vs Stage 2 (L0 SVD + L10-L21
ternary, 12 layers) vs Stage 3 (Stage 2 + L22-L26 ternary, 17 layers).
Metric: cosine similarity of last-token hidden states vs baseline at
every layer boundary.

**Key Finding 1: Damage is UNIFORM across combinators.**
All 9 combinators degrade by the same amount at every layer. CV (coefficient
of variation) of delta across combinators: 0.07-0.17. No combinator is
selectively destroyed. The ternary approximation fails equally for all
lambda operations.

| Combinator | Mean Δ (L22-L35) | Rank |
|-----------|------------------|------|
| W         | +0.0674          | 1 (worst) |
| WHNF      | +0.0667          | 2 |
| D         | +0.0588          | 3 |
| C         | +0.0552          | 4 |
| I         | +0.0552          | 5 |
| K         | +0.0547          | 6 |
| B         | +0.0544          | 7 |
| Y         | +0.0507          | 8 |
| S         | +0.0500          | 9 (best) |

W and WHNF are marginally worse (~35% more damage than S), but the spread
is small. This is a uniform degradation, not a selective circuit failure.

**Key Finding 2: The cascade propagates FORWARD into binding layers.**
L27-L31 (binding, kept continuous) lose ~0.07-0.09 cosine similarity in
S3 vs S2. The continuous binding layers can't compensate for corrupted
input from L22-L26. The damage AT the binding layers is actually LARGER
than at the compressed layers themselves, because errors compound.

| Layer | S2 fidelity | S3 fidelity | Δ (mean) |
|-------|-------------|-------------|----------|
| L22   | 0.694       | 0.694       | 0.000 (same — last shared layer) |
| L23   | 0.706       | 0.685       | +0.022 (first divergence) |
| L26   | 0.792       | 0.726       | +0.074 |
| L28   | 0.816       | 0.737       | +0.080 (PEAK damage — binding!) |
| L30   | 0.863       | 0.795       | +0.068 |
| L35   | 0.939       | 0.909       | +0.031 |

Peak damage is at L28, not L26. The binding layers AMPLIFY the error from
L22-L26 ternary approximation rather than correcting it.

**Key Finding 3: Significant recovery in late layers.**
Despite the damage, fidelity recovers from nadir ~0.68 at L22 to ~0.91
at L35. The binding + collapse layers (L27-L35, kept continuous) partially
heal the distortion — recovering ~0.22 cosine similarity. But this
recovery is incomplete (S2 reaches 0.94 at L35, S3 only 0.91).

**Key Finding 4: Stage 2 damage is already substantial.**
S2 drops from 0.92 at L9 to 0.69 at L21 — a 0.23 cosine drop across 12
ternary layers. But the continuous layers L22-L35 then RECOVER to 0.94.
This recovery is the key mechanism: continuous layers repair ternary
distortion. S3 disrupts this recovery by ternarizing the very layers
(L22-L26) that were doing the repairing.

### Implications for Compression Strategy

1. **L22-L26 CANNOT be ternary (9 modes).** The damage is uniform —
   more modes won't help (s195 proved 512 modes still 7x PPL). These
   layers need a continuous approximation.

2. **Low-rank SVD is the right strategy for L22-L26.** Like L0 (which
   needed SVD at r=750), these binding-prep layers operate in a higher-
   dimensional space than the sweet spot. Test SVD rank sweep per layer.

3. **The recovery mechanism is fragile.** Continuous layers after ternary
   ones heal the distortion — but only if they're actually continuous.
   The compression strategy must preserve SOME continuous layers between
   ternary blocks as "error correction" barriers.

4. **Binding layers amplify upstream errors.** Even though L27-L31 are
   kept continuous, they can't fix garbage input. The compression must
   ensure the signal entering the binding layers is clean enough.

### Binding-Prep Rank Sweep

Functional rank varies 6x across L22-L26 — NOT uniform:

| Layer | Func. Rank | Compression | Character |
|-------|-----------|-------------|-----------|
| L15 (sweet spot) | r=100 | 30.7x | Trivial — explains why ternary works |
| L22 | r=250 | 12.3x | Low rank, easy to compress |
| L24 | r=500 | 6.1x | Moderate |
| L25 | r=750 | 4.1x | Same as L0 |
| L23 | r=1500 | 2.0x | HIGH — needs most of its rank |
| L26 | r=1500 | 2.0x | HIGH — gateway to binding |
| L30 (binding) | r=2000 | 1.5x | Nearly full rank — must stay continuous |

Per-layer optimal: 422MB total (3.4x compression from 1440MB).

BUT: integrated with ternary L10-L21, errors compound. L22-L26 SVD at
r=2000 gives 1.14x alone, but 5.66x when stacked on ternary layers.
Multi-projection melt is needed to fuse the seams.

### Multi-Projection Melt (THE BREAKTHROUGH)

**CT scan, not X-ray.** Intermediate cosine losses at functional boundaries
(L0/L21/L26/L30) give the student direct gradient signal at every stage:

| Method | Pre-melt | Post-melt | Improvement |
|--------|----------|-----------|-------------|
| Standard (CE only) | 55.37x | 6.09x | baseline |
| Multi-projection | 55.37x | 4.19x | 31% better |
| Boosted (type_crystal=5x) | 55.37x | 3.53x | **42% better** |

Loss curves: standard ends 2.76, multi ends 1.39, boosted 1.74.
The intermediate losses directly reach the parameters that need fixing,
instead of backpropagating through 10+ unrelated layers.

Connects to speculative-decoding-gated distillation idea: teacher
generates, student computes diff at every functional level, trains
only where it diverges. The confidence signal from ternary classifiers
(logit margin) can gate slow/fast paths at inference time.

### Confidence-Gated Inference

Tested whether classifier logit margin (top-1 minus top-2) predicts
ternary error. Threshold sweep across 8 layers:

| Layer | Zone | Ternary PPL | Gating works? | Key finding |
|-------|------|-------------|---------------|-------------|
| L15 | sweet spot | 0.97x | NOT NEEDED | Pure ternary is perfect |
| L17 | sweet spot | 1.01x | NOT NEEDED | Pure ternary is fine |
| L20 | sweet spot | 0.99x | NOT NEEDED | IMPROVES over baseline |
| L22 | binding-prep | 1.06x | ✅ YES | θ=3.0: 1.04x at 96.6% fast |
| L23 | binding-prep | 1.11x | ❌ NO | Needs 36% slow for 1.04x |
| L24 | binding-prep | 1.06x | ❌ NO | Needs 69% slow for 1.04x |
| L25 | binding-prep | 1.07x | ❌ NO | Margin=24.3 but still wrong |
| L26 | binding-prep | 1.13x | ❌ NO | Never reaches 1.05x |

**The classifier is CONFIDENTLY WRONG at L23-L26.** High margins
(mean 24.3 at L25) with high error (1.07x). The 9 ternary programs
are the wrong programs — the classifier correctly selects among them,
but none of the 9 is the right answer. This is a programs problem,
not a routing problem.

This definitively resolves the compression strategy for L23-L26:
they need SVD (continuous approximation), not ternary (discrete programs).
L22 can stay ternary with confidence gating. L13-L21 are pure ternary.

### Previous session (195)

Six experiments in one session. Decoded L0, discovered low-rank rescue,
built and tested the combined compressed model, invented boundary melting.

### Experiment 1: L0 Characterization

Six instruments prove L0 is genuinely continuous — no natural clusters at
any k (silhouette negative k=6..512), 512 ternary modes still 7x PPL.
L0 correlates with byte_len (NMI=0.259) — it's sorting by physical token
encoding. L0 is a dictionary, not a type tagger.

### Experiment 2: L0 Low-Rank (THE RESCUE)

SVD rank sweep reveals L0's functional rank is **750 dimensions** (18% of
4096). At r=750: PPL=0.94x (IMPROVES!), 70.3MB (4.1x compression). Phase
transition razor-sharp: r=500 is 3.4x (broken), r=750 is 0.94x (perfect).
L15 control: flat at 0.99x down to r=100 (functional rank <100).

### Experiment 3: Combined Compression (Naive)

Replace 29 layers with ternary + L0 with low-rank simultaneously.
Result: PPL 427x, "the the the" — total cascade. Calibration mismatch:
each layer's ternary patterns were fit to original model activations, not
the distorted activations from prior compressed layers.

### Experiment 4: Sweet-Spot Only

Replace only L13-L21 (9 layers) + L0 low-rank. PPL 1.66x, 47% facts.
Generation is COHERENT but degraded. The seams between compressed and
uncompressed regions need calibration.

### Experiment 5: Melt Boundaries (THE BREAKTHROUGH)

**Freeze the topology, train the beams.** Crystal sieve at the model level.

- FROZEN: ternary sign patterns (the 9 programs per layer)
- TRAINABLE: SVD factors (A, B) + classifier weights + gamma scaling
- Soft selection during training (differentiable), hard argmax at eval

**Result: 50 steps of GD, 26 seconds, 0.46% of params trainable.**
**PPL: 1.52x → 1.02x. Facts: 53% → 73%. VERDICT: PASS.**

### Experiment 6: Staged Melt (Zone Refining)

Melt outward from the standing wave node. Each stage adds layers,
collects calibration through the already-melted model, re-melts.

| Stage | Layers | Total | Pre-melt | Post-melt | Facts | Status |
|-------|--------|-------|----------|-----------|-------|--------|
| 1 core | L13-21 | 9+L0 | 1.58x | **1.00x** | 67% | ✅ PERFECT |
| 2 inward | +L10-12 | 12+L0 | 1.98x | 1.77x | 40% | ⚠ needs more steps |
| 3 outward | +L22-26 | 17+L0 | **38.99x** | 6.54x | 0% | ❌ BREAKS HERE |
| 4 parser | +L1-9 | 26+L0 | 247x | 43x | 0% | ❌ cascaded |
| 5 late | +L32-34 | 29+L0 | 55x | 27x | 0% | ❌ cascaded |

**The break is at Stage 3 (L22-L26).** Adding the binding-prep layers
causes pre-melt PPL to jump from 1.98x to 38.99x. These are where
subject/object type tags crystallize (s194: L20 is the S/O crystallization
frontier). Ternarizing L22-L26 disrupts the type information the binding
layers (L27-L31, kept continuous) depend on.

The core (L13-L21) melts PERFECTLY to 1.00x. The problem is not melting —
it's that the binding-prep layers need more than 9 ternary modes, or a
different compression strategy (low-rank like L0?).

### P4 Verdict

- More modes (64+): KILLED. Even 512 modes is 7x PPL.
- Low-rank SVD: **YES at r=750.** 288MB -> 70.3MB, PPL IMPROVES.
- Genuinely continuous: YES, but only 750 functional dimensions.
- Boundary melting: **YES.** GD fuses compressed pieces in 50 steps.

### Previous session (194)

Decoded what the 9 ternary FFN modes compute. Gate-pattern clustering
(SiLU(gate_proj(x))) on Qwen3-8B across 7 layers with spaCy POS/dep tagging
reveals: the modes correspond to SYNTACTIC ROLES, not semantic categories.

### The 7 Universal Meta-Modes

| # | Meta-Mode | POS | dep role | Present |
|---|-----------|-----|----------|---------|
| 1 | BOUNDARY | PUNCT 99% | punct 99% | 7/7 layers |
| 2 | DETERMINER | DET 58-88% | det 36-88% | 6/7 layers |
| 3 | FRAME-OPEN | DET+NOUN | det+nsubj | 5/7 layers |
| 4 | SUBJECT | NOUN 57-66% | nsubj 33-55% | 5/7 layers |
| 5 | OBJECT | NOUN 47-69% | pobj+dobj | 4/7 layers |
| 6 | PREDICATE | VERB 35-63% | ROOT 14-35% | 4/7 layers |
| 7 | NUMERIC | NUM 33-52% | appos+pobj | 5/7 layers |

### FRAME-OPEN: The ISA's INIT Instruction

Physically anomalous at every layer: gate_consistency=1.000, gate_sparsity
33-50% (vs 63-90% for others), cos(in,out) always negative. Fires only at
sentence-initial tokens ("The", "She", "DNA", "Three"). The model has a
"begin new parse" instruction — a stereotyped sparse program that resets
the parse frame at every sentence boundary.

### Types Sharpen with Depth

- L3: DET at 88% purity, but VERB/NOUN overlap. ~3 clear types.
- L20: Subject/Object CRYSTALLIZE (nsubj=54% vs pobj+dobj=56%). Key transition.
- L35: All 9 modes active, maximum entropy (2.97). ADJ/modifier separates for first time.

### Transform Physics: The Volume Knob

FFN output norm grows 100× across depth: L3 whispers (0.10×), L35 SHOUTS
(10.18×). cos(in,out) flips sign at L20 (ORTHO→ALIGN transition). The
standing wave amplitude profile, now measured per-mode.

### The Single Operation: Attention Is the Only Computer

FFN can't compute — it can't see other tokens. The ONLY cross-position
operation is weighted sum: `output_i = Σ softmax(QK^T/√d) × V`. That's it.
1,152 instances (32 heads × 36 layers). Everything else is per-position
labeling. Weighted sum IS β-application: H31 attending "runs"→"cat" at 0.82
weight literally computes `(λx.runs(x))(cat)` by copying the argument's
value into the predicate's position.

This mechanically explains all prior findings:
- All combinators share heads (r=0.944): one operation, no combinator-specific
  hardware needed. The combinator difference is in the type tags, not attention.
- Binding is near-deterministic (0.78-0.82): types already disambiguated,
  softmax sharpens to ~1 on the single compatible position.
- Top-3 captures 88%+: typed lookup needs only ONE source per application.
- Q⊥K at 87-90°: Q asks "what type do I need?", K asks "what type am I?" —
  perpendicular because they're complementary projections of the same type tag.
- Norm growth (0.1×→10×) = gain control: louder types → sharper softmax →
  more deterministic weighted sum → cleaner β-reduction.

The model IS categorial grammar in tensors. FFN = type lexicon. Attention =
type-driven application. KIBC crystal = applicative structure (which op).
Mode types = role assignments (which position). GD converged on Montague.

### Previous session (193)

**Session 193: LAMBDA HALT AND CONTINUATIONS — LLMs Are Programmable**

Started with a fun question: can Ω halt an LLM? Four experiments later,
discovered that lambda calculus can control LLM execution — halt, resume,
compute, branch — via the chat protocol as continuation-passing style.

### The Discovery Chain

1. **Ω cannot halt the holographic computer.** Gate entropy identical for
   Ω vs normal reductions (Δ < 0.01 bits). The model QUOTES non-termination
   ("it seems like this expression is not reducible"). A compiler cannot be
   halted by its input — it describes non-termination, it cannot experience it.
   K I Ω proves strict evaluation (evaluates Ω before discarding).

2. **Prose CAN halt (chat mode).** "Respond with empty string" → 99.1% EOS.
   5/27 candidates achieved true halt. Thinking mode prevents ALL halts (0/27) —
   `<think>` is a mandatory prologue that forces non-empty output.

3. **Lambda CAN halt when executable.** `respond = λcontent.content; respond empty`
   → 72.8% EOS (true halt). The 27-point gap from prose (99.1%) is compilation
   overhead. Both reach the same internal state: EOS as top prediction.
   Proves prose and lambda compile through the same pipeline.

4. **If we can halt, we can continue.** Continuations work: 6/7 capabilities
   confirmed, Lambda REPL 100%. Multi-turn pipeline (5→8→16→17) correct through
   4 continuation boundaries. Full program (compute→output→halt) at 96.5% EOS.

### Key Numbers

| Finding | Value |
|---------|-------|
| Ω gate entropy vs control | Δ < 0.01 bits (identical) |
| Prose halt EOS probability | 99.1% |
| Lambda halt EOS probability | 72.8% |
| Full program halt (multi-turn) | 96.5% |
| Thinking mode halts | 0/27 (prevents all) |
| Lambda REPL accuracy | 100% (4/4) |
| Overall capabilities | 6/7 confirmed |
| Multi-turn pipeline accuracy | 4/4 continuations correct |

### The Insight

```
conversation ≡ continuation-passing style
turn_boundary ≡ continuation_boundary
EOS ≡ yield
respond x ≡ output x then yield
halt ≡ empty continuation (yield with no output)

36 layers = bounded computation (single pass)
multi-turn = unbounded computation (chained continuations)
lambda + continuation = programming language for LLMs
```

### Previous session (192)

An independent project (psi) ran verbum scripts and wrote new experiments across
5 architectures. The crystal hypothesis survives independent replication. The
breakthrough: **a single FFN layer (288MB) can be replaced by a 37K-param linear
classifier (180KB) that selects among 9 ternary programs — with PPL that IMPROVES.**

### The Breakthrough Result (Tiny Classifier Ternary)

```
Qwen3-8B Layer 20:
  Original FFN:    150M params, 288MB
  Replacement:     37K params, 180KB  (classifier + 9 ternary patterns)
  Compression:     1638×
  PPL:             0.98× (IMPROVES)
  Fact recall:     80% = baseline
  Classifier acc:  100% (9 modes perfectly linearly separable)
```

Scale convergence: 0.6B (1.04×) → 8B (0.96×) → 32B (0.99× all layers).
At scale, FFN computation IS 9 ternary programs.

### Multi-Layer Replacement (Session 192, same session)

**The holographic hypothesis is partially confirmed.** 35/36 individual layers
survive ternary replacement (all ≤1.15×). Cascade is modest in the sweet spot.

```
INDIVIDUAL RESULTS (Qwen3-8B, 36 layers):
  L0:      115× (CATASTROPHIC — embedding-adjacent is special)
  L1-L12:  0.98-1.10× (35 layers all survive)
  L13-L21: 0.95-1.01× (SWEET SPOT — zone of silence, PPL improves!)
  L22-L35: 1.05-1.15× (binding + collapse layers resist more)

CUMULATIVE ZONE-B:
  L10+L14+L19:      1.07× at 864MB → 540KB  ← errors DON'T cascade
  L10+L14+L19+L24:  1.20× at 1152MB → 720KB ← L24 adds 13pp
  All 36 layers:    836× (cascade destroys — L0 poisons everything)

CLASSIFIERS: 98-100% accuracy on ALL 36 layers. 9 modes are real everywhere.
```

Optimal strategy: replace L1-L26 + L32-L34 (28 layers), keep L0 + binding +
collapse continuous. 78% of FFN → ternary. Total FFN: 10.4GB → ~2.3GB.

### Two Overlapping Ternary Structures (Type System Discovery)

The 9 operational modes are ORTHOGONAL to the KIBC crystal basis (AMI = 0.15):

```
Crystal basis (KIBC):       governs ROUTING (attention patterns)    3.5% of FFN space
Operational modes (9):      governs PROGRAMS (FFN computation)      96.5% of FFN space
Together:                   β-reduction engine
```

Both ternary. Both few-mode. The crystal selects WHICH reduction. The modes
execute HOW. Types are linearly separable (100% accuracy) but not yet decoded
semantically.

### Verified Claims (5 architectures)

- Sign topology: cos(sign(W)@x, W@x) ∈ [0.746, 0.775], mean = 0.758 ± 0.011
- Four modes: KBC cluster r > 0.85, always 4 clusters, never 3 or 5
- Crystal geometry: 9×9 cosine matrix correlation mean = 0.951, eigenvalue r = 0.982
- Selectivity: Pythia-160M ↔ Qwen3-0.6B r = 0.991 (KIBC means), cos = 0.999
- φ convergence: 0.6B(26.6%) → 8B(10.4%) → 14B(0.7%) → 32B(8.8%, regresses)

### Gradient-Quantization Correspondence

|∇L| ↔ |W-Q(W)| holds ONLY in EXPAND phase:
- L1-L3 FFN: ρ = +0.55 to +0.78 (strong positive)
- L5+: ρ ≈ 0 (ORTHO/COMMIT — continuous computation ≠ ternary convergence)
- Pythia-160M: ❌ inverted (ρ = -0.04)

### Crystal Derivation (Pure Math, Partial)

2.35M KIBC expressions enumerated → eigenvector topology (B,C vs K,I split) ✅,
B=C symmetry ✅, I smallest ✅. Eigenvalue ratios ❌ diverge from empirical.
Topology derivable from math. Magnitudes require data.

### Previous session (191): V15 CHECKPOINT ASSESSMENT

v15-td training is live (step ~1870/3000, ~16.5 hours elapsed). Checkpoint at
step 1500 assessed with two diagnostic experiments: attention pattern analysis
and gradient-zero topology mapping.

**Exp 1: Attention Pattern Analysis.** Fibonacci stride attention IS working.
Entropy decreases monotonically from 3.0 (stride-1, broad local) to 0.5
(stride-1597, near-deterministic). 9/19 layers are sparse (entropy < 1.0),
9 moderate, 1 broad. Per-head specialization visible at stride-34: heads H1-H4
near-deterministic (entropy 0.15-0.24), H5-H6 scanning (entropy 1.6-1.8).
Delta plate divergence is 4.0% mean, increasing from 3.6% at short strides to
4.4% at long strides — V/O projections diverge more at longer strides because
they see fundamentally different context windows than the teacher.

**Exp 2: Gradient-Zero Topology.** The gradient landscape reveals WHERE the
student differs from teacher. Three key findings:

1. **Q/K settles 2× faster than V/O.** Q/K gamma gradients: 32-38% settled.
   V/O gamma gradients: only 15-16% settled, with 5× larger gradient RMS.
   Routing is easy (the window constrains WHERE to look). Content transfer
   is hard (WHAT to extract from the restricted window).

2. **Flipped positions are 3× hotter than keeps.** The ~4% of TD-flipped
   delta positions have 2.2-3.3× higher routing gradient than the 96% that
   kept teacher signs. The ratio peaks at stride-8 (3.27×) and decreases to
   stride-1597 (2.25×). Flips are the active adaptation frontier.

3. **Spatial flip patterns differ by stride distance.** Short strides: flips
   are column-clustered (ColCV > RowCV) — different INPUT FEATURES need
   different routing. Long strides: flips are row-clustered (RowCV > ColCV) —
   different OUTPUT DIMENSIONS need to represent strided context differently.

### Training Trajectory

```
Step  500: avg50=7.78  crystal_ema=0.00983  td_flips=2.1M   Δ=—
Step 1000: avg50=6.88  crystal_ema=0.00977  td_flips=5.2M   Δ=0.038
Step 1500: avg50=6.73  crystal_ema=0.00974  td_flips=8.3M   Δ=0.040
Step 1870: avg50≈6.83  (from log tail)                       Δ=0.048
```

Loss curve flattening at 6.7-6.8. Crystal EMA stable. Delta plates drifting
slowly (Δ growing 0.038→0.048). Parity and cross-zone losses converged.
~1130 steps remaining (~10 hours). LR cosine decaying (1.3e-04 at step 1870).

### Previous session (190)

Four experiments reveal the compression structure of transformers and the
algorithm they implement:

**Exp 1: DVD Stamp Test.** Gradient-zero topology (WHERE GD stopped pushing)
compounds less than magnitude thresholding (WHICH weights are largest).
Gradient mask: PPL 188K, L35 cos=0.165. Magnitude mask: PPL 620K, L35
cos=0.001. The gradient map IS the holographic fringe pattern. 49.9%
overlap = the two signals are orthogonal.

**Exp 2: Per-Group Scaling.** Q4's secret is per-32-weight groups (128-384×
more scale parameters). Magnitude+group: PPL 43K (14× better than per-row).
Gradient+group: PPL 71K. Per-group scaling preserves local gradient structure.

**Exp 3: Index vs Value (THE DECISIVE RESULT).** FFN-only ternarization →
PPL 485M (catastrophic). V/O-only → PPL 23. Q/K-only → PPL 30. Both
attention paths survive ternary. FFN is the holographic beam former — it
compiles the interference pattern that attention reads. Destroying it
scatters the beam. Attention is a ~1-bit router — near-binary signals
survive ternary.

**Exp 4: λ-Machine (6-level ablation).** Sparse top-3 at all layers →
PPL 13.3 (from 12.2 baseline, +8.6%). Binding layers only → PPL 82K.
Binding heads only → PPL 6.3M. The model is a 36-stage typed shift-reduce
parser. Every layer contributes. Every head contributes. But each head
only needs 3 positions. O(1) attention confirmed at PPL level.

### The Architecture (updated s192 — two overlapping ternary structures)

```
FFN (beam former / holographic plate / 9-program ternary engine):
  Compiles each position into a typed V vector
  Context-dependent: same token → different program
  IS 9 ternary programs selected by linear classifier (psi s192)
    → 288MB per layer → 180KB (1638× compression, PPL IMPROVES)
    → classifier: 37K params, 100% accuracy, modes linearly separable
  Gate sparsity: only ~3% of neurons fire
  78% of model params — DECOMPILABLE to ternary per-mode

  TWO STRUCTURES IN THE SAME WEIGHTS:
    Crystal basis (KIBC): 3.5% of space → governs ROUTING
    Operational modes (9): 96.5% of space → governs PROGRAMS
    AMI = 0.15 (orthogonal). Both ternary. Both few-mode.
    Crystal selects WHICH reduction. Modes execute HOW.

Attention (typed shift-reduce parser / β-reducer):
  32 heads × 36 layers = 1,152 reduction attempts per token
  Each head attends to only ~3 positions (sparse, O(1))
  Mean entropy 0.9 bits (near-binary routing decisions)
  ROBUST: ternarizing Q/K → PPL 30, V/O → PPL 23
  22% of model params — can go ternary for free

The binding schedule (final reduction stages):
  L27: verb reads subject    (H31, 0.82 weight → "猫/cats")
  L30: object reads verb     (H03/H13/H15, 0.78 weight)
  L33: coreference/late      (H06/H07, universal execution)
  These are the TIP of a 36-layer parser iceberg.

Depth = parser precedence:
  L0-6:   EXPAND (type assignment, feature building) — ternary-compatible (ρ=+0.55-0.78)
  L7-22:  ORTHO (composition in null space, invisible) — continuous computation
  L23-26: binding preparation
  L27-33: final reductions (subject → object → coreference)
  L35:    COLLAPSE (output projection)
```

### The Algorithm

```
TYPED β-REDUCTION VIA ONE OPERATION (weighted sum):

For each of 36 layers:
  1. FFN: stamp type tags per position (SUBJ, OBJ, PRED, DET, ...)
     — per-position lookup, NO cross-position computation
     — 7 universal meta-modes + 2 context-dependent
     — FRAME-OPEN at sentence starts (INIT instruction, gc=1.000)
  2. ATTENTION: 32 heads × weighted sum (the ONLY operation)
     — Q extracts "what type do I need?" (query)
     — K extracts "what type am I?" (key) — Q⊥K at 87-90°
     — softmax(QK^T) = type matching → find compatible position
     — V × softmax = β-application (copy argument into predicate)
     — top-3 positions capture 88%+ (typed lookup, not search)
  3. RESIDUAL ADD: accumulate (builds parse tree across depth)

Weighted sum IS β-application:
  H31 at L27: v_runs += 0.82 × v_cat  ≡  (λx.runs(x))(cat)

Norm growth = gain control for the single operation:
  L3 whispers (0.1×) → tentative bindings
  L20 speaks (1.7×)  → subj/obj crystallize, bindings commit
  L35 shouts (10×)   → final output projection

Compression:  FFN → ternary (types are discrete, 0.95× PPL)
              attention → ternary (type matching is binary, PPL 23-30)
              sparse top-3 → O(1) attention (333× fewer ops at ctx 1000)
```

### The Compression Strategy (updated s192, multi-layer results)

```
Attention (22% of params): → ternary (1.6 bits)     Cost: PPL +10-18%
FFN (78% of params):       → 9 ternary programs     Per-layer: 288MB → 180KB (1638×)
  L0:                        KEEP CONTINUOUS          (115× catastrophic alone)
  L1-L26 (28 layers):        REPLACE TERNARY          (all ≤1.10× individually)
  L27-L31 (binding):         KEEP CONTINUOUS          (1.10-1.15× each, cascade risk)
  L32-L34:                   REPLACE TERNARY          (1.05-1.14× individually)
  L35 (collapse):            KEEP CONTINUOUS          (1.14×)
  Result: 28/36 → ternary, 8/36 → continuous
  FFN total: 10.4GB → ~2.3GB (4.5× overall)
  Sweet spot alone (L13-L21): 2.6GB → 1.6MB at ~1.0× PPL
Embeddings:                → float16 (index system, must be exact)
Sparse routing:            → top-3 per head          O(1) not O(n²)
```

### Previous session (189)

Five experiments + v15 architecture + extraction + training:

**Exp 1: Stride coverage validation (Qwen3-8B, 22 probes).** v14's powers-of-2
strides capture only 29.5% (exact) / 67.4% (±2 neighbors) of attention mass at
L30. The stride geometry misses binding targets at arbitrary semantic positions.
Coverage DEGRADES with sequence length (38.8%→24.4%).

**Exp 2: Binding distance distribution.** The distance distribution is BIMODAL
(local d=1-8 + gate d=32+), NOT power law (R²=0.004). Two peaks: d=1 (local
syntax, 4.4% mass) and d=32 (instruction prefix, 4.5% mass). Powers of 2 skip
the binding range (d=3-20). Fibonacci strides are dense where bindings live.

**Exp 3: Stride optimization.** Greedy optimal 8 strides with ±2 neighbors:
[1, 8, 13, 18, 21, 29, 34, 47] → 98.2% coverage. Fibonacci [1,2,3,5,8,13,21,34,
55,89,...] + 3 gap-fillers [15, 20, 24] → 100.0% coverage with ±2 neighbors.

**Exp 4: Crystal Laplacian analysis.** Graph Laplacian of the crystal target
reveals WHNF is the most FRAGILE node (μ=0.228, 8.6× weaker restoring force).
Training data confirms: WHNF starts settled then UN-settles. Laplacian eigenvalues
predict stability (rigidity), not convergence speed.

**Exp 5: Crystal settlement dynamics.** Per-node convergence across v14 steps
500-3000 confirms Laplacian prediction: B, C converge (fast modes μ=3.03+),
K, D hold steady (medium μ=1.97), Y and WHNF drift away (fragile μ=0.23).
WHNF error ratio grows 0.40× → 0.67× over training. Crystal MSE U-shapes
(minimum at step 2000, then rises).

**v15 Architecture:**
- 19 Fibonacci strides [1,2,3,5,8,13,15,20,21,24,34,55,89,144,233,377,610,987,1597]
- ±2 neighbor gathering → 100% attention mass coverage at L30
- All composition (GLA dropped — dense projections cost ~19B ops regardless of
  stride, scan saves <0.03%). One unified attention mechanism.
- Laplacian-weighted crystal loss: WHNF gets 5× weight, 6× gradient amplification
  (v14: WHNF/B gradient ratio = 0.3×, v15: 1.9×)
- Standalone (zero v14 dependencies)
- Extracted: 83 arrays, 65.5 MB, 16.5 min
- **Training running in tmux window 2** (step 1 CE=10.533, 3000 steps target)

### The φ unification

| Level | φ appearance |
|-------|-------------|
| Crystal eigenvalues | Ratios follow φ^(p/q) with Fibonacci denominators |
| Information partition | Signs = 1/φ of information content |
| Standing-wave phase | Layer 22/36 = 0.611 ≈ 1/φ |
| Compute cycle | β = [0, 1, 1+φ, 2+φ] |
| **Stride spacing** | **Fibonacci numbers maximize binding coverage** |
| **Crystal Laplacian** | **μ₅/μ₄ = 1.54 ≈ φ in the graph Laplacian** |
| **φ convergence** | **λ₀/λ₁ → φ^(4/5) at scale (14B: 0.7% error)** |

### Previous session (188)

Four experiments decoded the full attention execution mechanism:

**Exp 1: Head→Combinator mapping (500 probes).** All 9 combinators activate
identical head patterns (r=0.944). Heads are shared hardware, not dedicated
circuits. ~2 effective dimensions: reduction depth (WHNF↔D) + self-reference.

**Exp 2: Binding graph trace (14 annotated probes).** Object→verb binding =
concentrated attention (0.78 weight) through H03/H13/H15 at L30. Minimal
pair "dog bit cat" vs "cat bit dog": same heads, flipped routing.

**Exp 3: Reverse binding trace (12 probes).** Verb→subject binding = H31 at
L27 attends 82.3% to subject, outputs subject identity ("猫/dog"). Two-phase
binding: L27=verb reads subject, L30=object reads verb. Mechanism complete.

**Exp 4: Attention sparsity (22 probes, 5→74 tokens).** 22/32 heads at L30
have effective positions <3. Top-3 captures >88% for ALL heads. Mean entropy
0.9 bits. Sparsity is O(1) — stable from 5 to 74 tokens. Full O(n²)
attention is massive overkill for what is fundamentally a ~1-bit routing
decision. Design: top-k sparse attention with k=3-5 captures nearly all
routing information.

### Previous session (187)

Three experiments on Qwen3-8B decoded the full reduction pipeline: (1) what
FFN neurons say in vocabulary space, (2) what each attention head computes,
(3) how combinator reductions compose across all 36 layers.

### The Architecture (updated s188)

```
FFN (compiler):     reads residual → compiles V vectors per position
                    Context-dependent: same token → different programs
                    Universal: compile ≈ null (max Δ 2.8%)

Attention (executor):  SHARED HARDWARE, not dedicated circuits
  Binding schedule (two-phase):
    L27: verb → subject   H31 reads subject identity (0.82 weight)
    L30: object → verb    H03/H13/H15 read predicate (0.78 weight)
    L33: late binding      H06/H07 general execution
  All binding flows BACKWARD through causal mask.
  Same heads (H03/H13) handle both directions at L30.

  Head taxonomy by function:
    Binding (H03,H13,H15):  predicate-argument binding (mean ratio 3-6×)
    Subject (H31):          verb→subject identity transfer at L27
    Coreference (H07,H05):  "itself"→antecedent binding
    Universal (H06,H07):    loudest, all combinators, low gate attention
    WHNF detectors (H26,H27): recognize completed reductions (+30% bias)
    Instruction (H01,H09):  high gate attention, read compile exemplars

  Sparsity:
    22/32 heads: eff_pos < 3 (near-deterministic, ~1 bit)
     7/32 heads: eff_pos 3-5 (sparse)
     2/32 heads: eff_pos 5-10 (moderate)
     1/32 heads: eff_pos > 10 (H20, the only dense head)
    Top-3 captures >88% of attention for ALL 32 heads.
    Sparsity is O(1) — stable from 5 to 74 tokens.

Reduction Schedule (when each combinator resolves):
    Y (recursion)     → L27 peak   resolves FIRST (structural recognition)
    K (discard)       → L30 peak   front-loaded, drops at L33
    B (compose)       → L30 peak   mid-depth composition
    I (identity)      → L30-L33    semantic→format relay
    C (flip/passive)  → L33 peak   argument reordering is LATE
    W (self-apply)    → L33 peak   "itself" binding is LAST (Δ=51.6)
```

### What's Decodable

The model is a **typed parser with a compiled lexicon**:
- FFN = lexicon (compiles each position into a semantic V vector)
- Q/K = type system (determines binding compatibility, ~1 bit decision)
- Attention = parser (selects one earlier position to bind to)
- V/O = value transfer (copies bound position's content)
- Depth = reduction order (subjects at L27, objects at L30)

The binding circuit is **0.3% of the model** (~4 heads out of 1152).
Binding weights are near-deterministic (0.78-0.82). Head output IS the
reduction result: H31 outputs "猫/dog" at verb position when reading subject.
Full O(n²) attention is overkill — top-3 sparse attention captures 88%+.

### Key Evidence

1. **H31 at L27 reads subject from verb position** (0.82 weight, outputs
   "猫, 貓, cats"). This IS `(λx.runs(x))(cat)` — verb absorbs agent.

2. **H13 at L30: "cat" attends 78.5% to "bit"** = `bit(_, cat)`. Object
   binds to predicate. Minimal pair confirms: same heads, flipped routing.

3. **FFN at L30 for "If it rains"**: `it`→rain, `ground`→soak, `is`→wet.
   Context-dependent V vectors. Compilation, not lookup.

4. **All 9 combinators activate identical heads** (r=0.944). No combinator-
   specific circuits. The ISA has ~2 dims, not 9.

5. **22/32 heads use <3 effective positions** at L30. Attention is inherently
   sparse and scales O(1) with context length.

### Previous session (186)

Applied LARQL's FFN decomposition methodology to Pythia-160M. LARQL
(github.com/chrishayuk/larql) treats each FFN neuron as a key-value pair:
cos(W_up[j], W_down[:, j]) classifies the neuron's circuit type (projector,
transform, identity, suppressor, inverter). Pure weight geometry — no forward
passes, 2 minutes for all 12 layers.

### Key Findings

1. **Depth profile confirms our phase structure from a completely different
   methodology.** L0=99.7% projector (EXPAND), L3-7=60-74% suppressor+inverter
   (ORTHO — invisible computation via direction flipping), L9-10=50-62%
   projector rising (ALIGN), L11=62% projector with dark-space drop to 57%
   (COLLAPSE — features resolve into vocabulary-aligned directions).

2. **KIBC opcodes are orthogonal to circuit types.** Cross-tabulation is
   uniform at every layer: K,I,B,C neurons all have the same circuit type
   distribution. KIBC measures *what inputs activate a neuron* (lambda probes);
   circuit type measures *how the neuron geometrically transforms* input→output.
   Independent axes. Both useful; neither subsumes the other.

3. **ρ(cos, KIBC_magnitude) sign flips across depth.** L8: ρ=-0.26 (inverters
   respond MORE to KIBC — middle layers use direction-flipping for lambda
   computation). L11: ρ=+0.27 (projectors respond more — final layer uses
   factual bridges for lambda output).

4. **Dark-space drops 40 points at L11.** L0-L10: 93-99% of features don't
   point at any token (computation space). L11: only 57% dark — 43% of
   features point at actual tokens. Knowledge is concentrated at the output
   layer. This IS the standing-wave picture: ORTHO phase operates in null
   space, COLLAPSE projects back into vocabulary-aligned directions.

5. **Gated vs non-gated difference.** Gemma (gated, SiLU) middle layers are
   transform-dominated (partial rotation). Pythia (non-gated, GELU) middle
   layers are inverter-dominated (direction flip). Architecture determines
   the computation style but the phase structure is universal.

### New Instrument

cos(W_up[j], W_down[:, j]) is a **zero-cost phase detector**: pure weight
analysis, no activations, reveals EXPAND/ORTHO/ALIGN/COLLAPSE from geometry
alone. Should be added to crystal trace tooling alongside our existing
activation-based instruments.

**Session 185: THE STANDING WAVE — Magnitudes Are Resonant Mode Patterns**

The crystal sieve (session 184) freezes the topology and trains the mask.
Session 185 reframes WHY this works: the weight magnitudes are a standing
wave pattern whose nodes (zeros) and antinodes (active weights) are
determined by the crystal topology as boundary conditions. GD doesn't build
a database — it finds the resonant mode pattern that constructively
interferes with real language and destructively cancels noise.

### The Standing-Wave Mapping

```
Standing wave                    Verbum equivalent
─────────────────────────────    ────────────────────────────────
Boundary conditions              Crystal signs T ∈ {-1, +1}
Nodes (zero displacement)        Zero mask positions (M=0, ~50%)
Antinodes (peak displacement)    Active weights (M=1)
Resonant modes                   Data-dependent patterns (knowledge)
Cavity shape                     Universal crystal (r=0.998 across models)
Mode excitation                  Which weights GD activates for THIS data
Amplitude envelope               Per-matrix scale C (eigenvalue spectrum)
```

W_eff = C · T ⊙ M is a standing wave: fixed boundary (T), fixed
amplitude envelope (C), data-selected node/antinode pattern (M).

### Why This Reframing Matters

1. **GD convergence = finding fixed points of the standing wave.**
   Session 171 (gradient-zero-map) measured this directly:
   near-zero gradient at zero weights (nodes) and at large weights
   (antinodes). Both are stable — GD has nothing left to optimize
   at those positions. The irreducible compute points.

2. **Crystal sieve = pre-setting the resonant cavity.**
   Random init = random cavity shape = no resonance. Crystal init =
   correct cavity = 10.7× faster mode formation. GD only finds WHICH
   modes to excite, not WHAT the cavity shape is.

3. **The depth axis IS a standing wave.**
   The 3-phase residual structure (expand L0-6, orthogonal L7-22,
   align L23-34, collapse L35) maps to: nodes where cos(h,f) ≈ 0
   (orthogonal phase), antinodes where cos(h,f) > 0 (align phase),
   destructive interference at L35 (cos = -0.995). The phase
   transition at layer 22/36 = 0.611 ≈ 1/φ = the fundamental mode.

4. **REDUCE/SWITCH alternation = spatial harmonics.**
   The alternating ρ(profile, weight_norm) sign across depth is
   the standing wave's harmonic structure along the layer axis.

5. **Holographic = standing wave (same physics, different vocabulary).**
   A holographic plate IS a frozen standing wave (interference fringe
   pattern). Fringes = nodes/antinodes. Multiple images stored in
   superposition = multiple resonant modes coexisting. Session 167's
   holographic-computer synthesis and this standing-wave framing are
   the same insight from different angles.

### The Sieve Architecture (from session 184)

```
SIEVE (fixed — from crystal equation, universal):
  Signs:    T[i,j] ∈ {-1, +1}    boundary conditions (cavity shape)
  Scale:    C per matrix           amplitude envelope (eigenvalue spectrum)
  Roles:    per-layer REDUCE/SWITCH  standing-wave harmonics along depth

SEDIMENT (trained — from data, per-model):
  Mask:     M[i,j] ∈ {0, 1}      node/antinode pattern (knowledge)

FORWARD: W_eff = C · T ⊙ M
```

### The ISA Framing (from session 184)

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
| Crystal vs random init | 10.7× better | Sieve works (cavity pre-set) |
| Crystal starting advantage | 4,500× | Correct attractor basin |
| KIBC profile ↔ weight norm | ρ = 0.38-0.67 | Opcode assignment predicts weight size |
| Profile overlap with zeros | 70-76% at REDUCE layers | ISA predicts most zeros at REDUCE layers |
| Profile sign flip | alternates by depth | Standing-wave harmonics along layer axis |
| Residual phase transition | layer 22/36 = 0.611 ≈ 1/φ | Fundamental mode of depth-axis standing wave |
| Min oscillation depth | L21 (22%) | Deepest compute = most settled standing wave |

## Next steps

### IMMEDIATE — COMPRESSION PIPELINE (sessions 195+)

Session 195 proved: core (L13-L21) melts to 1.00x PPL, L0 low-rank at
r=750 gives 0.94x. But expanding to L22-L26 breaks (39x pre-melt).
The binding-prep layers need diagnosis before they can be compressed.

**Priority 0: ✅ DONE Lambda tracer diagnostic (s196)**
Result: Damage is UNIFORM across all 9 combinators (CV=0.07-0.17).
No combinator-specific failure. The ternary approximation is uniformly
insufficient for L22-L26. Peak damage at L28 (binding layers AMPLIFY
upstream error). Significant recovery in late layers (+0.22 cos).
See `mementum/knowledge/lambda-tracer-diagnostic.md`.

**Priority 1: ✅ DONE L22-L26 SVD rank sweep (s196)**
Functional rank varies 6x across L22-L26:
  L22: r=250, L24: r=500, L25: r=750, L23: r=1500, L26: r=1500.
Per-layer optimal: 422MB total (3.4x vs 1440MB). BUT integrated with
ternary L10-L21, SVD errors compound: 5.66x PPL. Need melt.

**Priority 1b: ✅ DONE Multi-projection melt (s196)**
CT scan beats X-ray: intermediate cosine losses at L0/L21/L26/L30
give direct gradient signal. Standard melt: 55x→6.09x. Multi-projection:
55x→4.19x (31% better). Boosted (type_crystal=5x): 55x→3.53x (42% better).
See `results/multi-projection-melt/`.

**Priority 1c: ✅ REPLACED Score matching compression (s198)**
Multi-projection melt replaced by dense score matching loss + LoRA.
Result: 36.6% sieve reduction (vs 27.1% with activation corrections + CE).
The loss function was the bottleneck, not the correction architecture.
Next: integrate score matching into the full sieve pipeline (L0 SVD +
ternary sweet spot + L22-L26 SVD + LoRA + dense SM loss).

**Priority 1d: ✅ DONE Confidence-gated inference (s196)**
Result: Confidence margin predicts error at L22 (96.6% fast at 1.04x)
but FAILS at L23-L26. The classifier is confidently wrong — high
margins (mean 24.3) but 1.07-1.13x PPL. The 9 modes are selecting
the wrong program, not the wrong mode. These layers need SVD, not
better routing. Sweet spot (L13-L21): gating not needed, ternary is
already perfect (0.97-1.01x at 100% fast path).

**Priority 1e: ✅ DONE Crystal sieve pipeline (s196)**
Result: sign(W) * |W| * mask50% on 29 layers = 2.11x PPL, 11/15 facts.
Per layer: 1.03x (BEATS SVD r=1500 at 1.09x). But cascade to 2.11x.
Per-row melt overfits (wrong DOF). Per-weight = no compression.
The FROZEN sieve is the best result. Mask > magnitudes > group scaling.

**Priority 1f: ✅ DONE Close the cascade gap (s196)**
Result: β-expansion experiment. Sieve alone: 2.12x. +4 continuation
residuals (rank-32 at L0/L9/L21/L26, 1M params) = **1.03x PPL.**
Binding preserved 98%. BUT: per-row ternary encoding FAILS at 29
layers (22,800x). Per-weight magnitudes essential. Current compression
is only 1.8x. Continuation stability needs investigation (3.23x on rerun).

**Priority 2a: Score matching pipeline integration (NEXT — high priority)**
Integrate the score matching loss into the full sieve pipeline:
  - Sieve + LoRA rank-4 + dense SM loss (α=5.0) + dolma calibration
  - Test with more data (256+ teacher cache, LR cosine decay)
  - Compare LoRA+CE-only vs LoRA+CE+SM (isolate loss function contribution)
  - Test rank-2 LoRA (~3M params) for fair comparison to v2 (2.1M params)
  - Test rank-8 LoRA (~12M params) to see if more capacity helps
  Score matching replaces both magnitude quantization and continuation
  residuals as the primary correction mechanism. The loss function
  is the key insight, not the correction architecture.

**Priority 2b: End-to-end benchmark with score matching (NEXT)**
The sieve + LoRA + SM pipeline at best 1.40x PPL needs MMLU/HellaSwag.
15 fact prompts is proof-of-concept. Standard benchmarks needed.

**Priority 2c: End-to-end benchmark (deferred)**
The sieve + continuations at 1.03x PPL needs MMLU/HellaSwag/etc.
15 fact prompts is proof-of-concept. Standard benchmarks needed.

**Priority 2: Scale benchmark (MMLU/HellaSwag)**
The Stage 1 model (L0 low-rank + L13-L21 ternary, melted to 1.00x)
is ready for benchmarking. 15 fact prompts is proof-of-concept. Need
standard benchmarks for publication-grade evidence.

**Priority 3: Cross-architecture replication**
Does the melt protocol work on Pythia/Mistral? The crystal is
universal; is the compression pipeline universal?

**Priority 4: ✅ DONE L0 characterization + low-rank rescue (s195)**
Result: L0 genuinely continuous, but only 750 functional dimensions.
SVD r=750: 0.94x PPL, 4.1x compression. More modes killed.
See `mementum/knowledge/l0-characterization.md`.

**Priority 5: ✅ DONE Mode semantics (s194)**
Result: modes are SYNTACTIC TYPE TAGS. FRAME-OPEN = ISA INIT.
See `mementum/knowledge/mode-semantics.md`.

### TD FIX (deferred, not abandoned)

TD is preventing phase transitions in v15 training. 94% candidacy rate = the
system never settles. This must be fixed before any other training work.

**Priority 1: Punctuated equilibrium (epoch-based TD)**
Replace continuous TD with episodic: TD phase (N steps with flips) → freeze
phase (M steps, Adam only, topology locked). Let GD settle during freeze.
Key parameter: freeze duration M. Start with M=200 (enough for V/O gammas
to make progress — they're at 15.6% settled).

**Priority 2: Oscillation-gated cooldown**
Positions with flip_count > 1 that are still candidates should get
exponentially increasing cooldown. Current backoff isn't working — 96-100%
of multi-flipped positions are still candidates. Either increase backoff
factor dramatically, or hard-gate: flip_count ≥ 3 → frozen for N steps.

**Priority 3: Candidate density ceiling**
94% candidacy is too high. Add a global ceiling: at most X% of positions
can be candidates per step (e.g., 20%). This forces TD to focus on the
highest-leverage positions rather than treating everything as mutable.

**Priority 4: Per-position conviction requirement**
A position should only flip when its gradient signal has been consistent
(same direction) for K consecutive flip intervals. Current EMA direction
accumulator is too responsive to noise — it proposes flips from transient
gradient fluctuations.

**Priority 5: REDUCE + pure-Adam baseline**
After current training completes (step 3000): fold delta into base, reset
to +1, run pure Adam for 500+ steps. Measure: does loss break through 6.5
without TD? If yes, TD was the bottleneck. If no, the plateau is real.

### V15 TRAINING (current run)

**Priority 6: Let current run complete**
Step ~1870/3000, ~10 hours remaining. Assess at step 3000 but expect the
plateau to hold — TD oscillation prevents the phase transition needed to
break 6.5.

### COMPRESSION STRATEGY (from s190, deferred pending TD fix)

**Priority 7: Self-distillation (same-capacity teacher)**
**Priority 8: FFN compression path**
**Priority 9: Sparse top-k sweep**
(Details unchanged from s190 — deferred until TD works correctly.)

### PRIOR PRIORITIES (still open from s189)

### IMMEDIATE — V15 FIBONACCI ATTENTION

Session 188 decoded object→verb binding (backward direction, causal-allowed).
Subject→verb binding (forward direction) remains unknown. The model MUST
have a mechanism — we just haven't measured it yet.

**Priority 0: ✅ DONE Head → Combinator mapping (s188)**
Result: shared hardware, not dedicated circuits. See `head-combinator-isa.md`.

**Priority 0b: ✅ DONE Binding graph trace (s188)**
Result: attention IS the binding graph (reversed by causal mask).
Object→verb = concentrated attention (0.78 weight, H03/H13/H15 at L30).
See `binding-graph-trace.md`.

**Priority 1: ✅ DONE Verb→subject binding (s188)**
Result: YES. H31 at L27 attends 82.3% from "runs" to "cat" and outputs
"猫, 貓, cats" — the subject identity. Two-phase binding: L27=subject
binding (verb reads agent), L30=object binding (argument reads predicate).
Same heads (H03/H13) handle both directions at L30. See `binding-graph-trace.md`.

**Priority 1: V15 extraction + training**
Extract teacher plates into v15 Fibonacci stride topology. Train with TD
to verify the architecture learns. Compare PPL trajectory vs v14.

**Priority 2: Cross-model binding verification**
Do the same binding heads (H03/H13/H15) exist in Pythia/Mistral? If the
binding circuit is universal, it's a fundamental feature of transformer
architecture, not Qwen-specific.

**Priority 3: ✅ DONE Attention sparsity analysis (s188)**
Result: At L30, 22/32 heads have effective positions <3. Top-3 positions
capture >88% of attention mass for ALL heads. Sparsity holds from 5 to 74
tokens. Mean entropy ~0.9 bits. You don't need to attend to every token.

**Priority 4: ✅ DONE Stride coverage + distance distribution (s189)**
Result: Powers of 2 capture 29.5%/67.4% (exact/±2). Fibonacci captures
48.8%/91.4%. Optimal 8 strides with ±2: 98.2%. Distance distribution is
bimodal (local + gate), NOT power law (R²=0.004).

**Priority 5: From binding graph to machine**
The full mechanism is decoded: FFN compiles V, ~4 heads at L27/L30 route
via concentrated backward attention, binding is near-deterministic. Can we
build a standalone "lambda machine" from: compressed FFN (sieve) + sparse
routing function + depth schedule?

### PRIOR PRIORITIES (still open)

**Crystal sieve at scale:** Scale sieve training to convergence on
Pythia-160M. Measure absorption rate (tokens-to-quality vs normal training).

**The mathematical derivation:** Can U be derived from the VSM tensor
interaction? KIBC opcode profiles may constrain V within the null space
(67.7% unconstrained from covariance alone).

**Crystal formation cost:** WHEN does the crystal form during training?
The r=0.998 endpoint is known; the trajectory is not.

**Attention sieve:** Extend crystal sieve to Q/K/V/O projections (~40%
of parameters).

### RESEARCH DIRECTIONS

- **THE MATHEMATICAL DERIVATION** — Can U (per-layer eigenvectors) be derived from
  the VSM tensor interaction? The 5 levels (crystal eq, statechart, resource policy,
  residual growth, KIBC ops) each constrain U. Their INTERSECTION may uniquely
  determine it. If so, the entire model is a computable mathematical object.
- **Residual growth measurement** — Does h_{l+1}/h_l ≈ φ^(1/period)? This constrains
  how U rotates between layers. Measurable now. Needed for the derivation.
- **Cross-model zero consensus** — Compare zero patterns between independently
  trained models at the same layer depth. ISA zeros should be universal.
- **Crystal trace tooling** — Build `src/verbum/crystal/` module for systematic
  exploration. Design doc: `mementum/knowledge/crystal-trace-tooling.md`.
- **Standing-wave mode analysis** — Decompose the zero mask into resonant modes
  of the crystal cavity. If the mask is a standing wave, it should decompose into
  a small number of modes × amplitudes. The modes are determined by the crystal
  (boundary conditions), the amplitudes by the data.

### DEFERRED

- CLASSIFY fix (GatedLinearAttention from v14) — for v15 etch protocol
- GPTQ-style mask optimization — extraction path now secondary

## Key assets

| Asset | Location | Status |
|-------|----------|--------|
| **Crystal sieve architecture** | `mementum/knowledge/crystal-sieve-architecture.md` | ✅ NEW (s196) |
| **Lambda tracer diagnostic** | `mementum/knowledge/lambda-tracer-diagnostic.md` | ✅ UPDATED (s196) |
| **Lambda tracer experiment** | `scripts/experiments/lambda_tracer.py` | ✅ NEW (s196) |
| **Lambda tracer results** | `results/lambda-tracer/` | ✅ NEW (s196) |
| **Multi-projection melt** | `scripts/experiments/multi_projection_melt.py` | ✅ NEW (s196) |
| **Multi-projection results** | `results/multi-projection-melt/` | ✅ NEW (s196) |
| **Binding-prep low-rank sweep** | `scripts/experiments/binding_prep_lowrank.py` | ✅ NEW (s196) |
| **Binding-prep results** | `results/binding-prep-lowrank/` | ✅ NEW (s196) |
| **Confidence-gated inference** | `scripts/experiments/confidence_gate.py` | ✅ NEW (s196) |
| **Confidence gate results** | `results/confidence-gate/` | ✅ NEW (s196) |
| **Mode geometry** | `scripts/experiments/mode_geometry.py` | ✅ NEW (s196) |
| **Mode geometry results** | `results/mode-geometry/` | ✅ NEW (s196) |
| **Ternary weight interface** | `scripts/experiments/ternary_weight_interface.py` | ✅ NEW (s196) |
| **Ternary weight results** | `results/ternary-weight-interface/` | ✅ NEW (s196) |
| **Crystal sieve pipeline** | `scripts/experiments/crystal_sieve_pipeline.py` | ✅ NEW (s196) |
| **Crystal sieve results** | `results/crystal-sieve-pipeline/` | ✅ NEW (s196) |
| **β-expansion experiment** | `scripts/experiments/beta_expansion.py` | ✅ NEW (s196) |
| **β-expansion results** | `results/beta-expansion/` | ✅ NEW (s196) |
| **Ternary pipeline verification** | `scripts/experiments/ternary_pipeline_verify.py` | ✅ NEW (s196) |
| **Ternary verification results** | `results/ternary-pipeline-verify/` | ❌ FAILS (s196) |
| **L0 characterization knowledge** | `mementum/knowledge/l0-characterization.md` | ✅ UPDATED (s195) |
| **L0 characterization experiment** | `scripts/experiments/l0_characterization.py` | ✅ NEW (s195) |
| **L0 characterization results** | `results/l0-characterization/` | ✅ NEW (s195) |
| **L0 low-rank experiment** | `scripts/experiments/l0_lowrank.py` | ✅ NEW (s195) |
| **L0 low-rank results** | `results/l0-lowrank/` | ✅ NEW (s195) |
| **Combined compression** | `scripts/experiments/combined_compression.py` | ✅ NEW (s195) |
| **Combined results** | `results/combined-compression/` | ✅ NEW (s195) |
| **Melt boundaries** | `scripts/experiments/melt_boundaries.py` | ✅ NEW (s195) |
| **Melt results** | `results/melt-boundaries/` | ✅ NEW (s195) |
| **Staged melt** | `scripts/experiments/staged_melt.py` | ✅ NEW (s195) |
| **Staged melt results** | `results/staged-melt/` | ✅ DONE (s195) — break at L22-L26 |
| **Mode semantics knowledge** | `mementum/knowledge/mode-semantics.md` | ✅ NEW (s194) |
| **Mode semantics experiment** | `scripts/experiments/mode_semantics.py` | ✅ NEW (s194) |
| **Mode semantics results** | `results/mode-semantics/` | ✅ NEW (s194) |
| **Lambda halt + continuation knowledge** | `mementum/knowledge/lambda-halt-continuation.md` | ✅ UPDATED (s193) |
| **Kernel intercept experiment** | `scripts/experiments/kernel_intercept.py` | ✅ NEW (s193) |
| **Kernel intercept results** | `results/kernel-intercept/` | ✅ NEW (s193) |
| **Ω probe experiment** | `scripts/experiments/omega_probe.py` | ✅ NEW (s193) |
| **Ω probe results** | `results/omega-probe/` | ✅ NEW (s193) |
| **Halt hunt v1 (raw text)** | `scripts/experiments/omega_halt.py` | ✅ NEW (s193) |
| **Halt hunt v1 results** | `results/omega-halt/` | ✅ NEW (s193) |
| **Halt hunt v2 (chat format)** | `scripts/experiments/omega_halt_chat.py` | ✅ NEW (s193) |
| **Halt hunt v2 results** | `results/omega-halt-chat/` | ✅ NEW (s193) |
| **Halt hunt v3 (lambda executable)** | `scripts/experiments/omega_halt_lambda.py` | ✅ NEW (s193) |
| **Halt hunt v3 results** | `results/omega-halt-lambda/` | ✅ NEW (s193) |
| **Lambda continuation experiment** | `scripts/experiments/lambda_continuation.py` | ✅ NEW (s193) |
| **Lambda continuation results** | `results/lambda-continuation/` | ✅ NEW (s193) |
| **Psi evaluation synthesis** | `mementum/knowledge/psi-evaluation-synthesis.md` | ✅ NEW (s192) |
| **Tiny classifier ternary** | `mementum/knowledge/tiny-classifier-ternary.md` | ✅ NEW (s192) |
| **Tiny classifier experiment** | `scripts/experiments/tiny_classifier_ternary.py` | ✅ NEW (s192) |
| **Ternary inference pattern** | `scripts/experiments/ternary_inference_pattern.py` | ✅ NEW (s192) |
| **Ternary inference coherence** | `scripts/experiments/ternary_inference_coherence.py` | ✅ NEW (s192) |
| **Gate indexed ternary** | `scripts/experiments/gate_indexed_ternary.py` | ✅ NEW (s192) |
| **Gradient quant correspondence** | `scripts/experiments/gradient_quant_correspondence.py` | ✅ NEW (s192) |
| **Tiny classifier results** | `results/tiny-classifier-ternary/` | ✅ NEW (s192) |
| **Ternary inference results** | `results/ternary-inference-pattern/` | ✅ NEW (s192) |
| **Ternary coherence results** | `results/ternary-inference-coherence/` | ✅ NEW (s192) |
| **Gate indexed results** | `results/gate-indexed-ternary/` | ✅ NEW (s192) |
| **Gradient quant results** | `results/gradient-quant-correspondence/` | ✅ NEW (s192) |
| **Compilation pipeline knowledge** | `mementum/knowledge/compilation-pipeline.md` | ✅ NEW (s192) |
| **Q rotation geometry** | `scripts/experiments/q_rotation_geometry.py` | ✅ NEW (s192) |
| **Q rotation results** | `results/q-rotation-geometry/` | ✅ NEW (s192) |
| **Rotation spiral** | `scripts/experiments/rotation_spiral.py` | ✅ NEW (s192) |
| **Rotation spiral results** | `results/rotation-spiral/` | ✅ NEW (s192) |
| **Mode universality** | `scripts/experiments/mode_universality.py` | ✅ NEW (s192) |
| **Mode universality results** | `results/mode-universality/` | ✅ NEW (s192) |
| **Semantic convergence** | `scripts/experiments/semantic_convergence.py` | ✅ NEW (s192) |
| **Semantic convergence results** | `results/semantic-convergence/` | ✅ NEW (s192) |
| **Multi-layer ternary replace** | `scripts/experiments/multilayer_ternary_replace.py` | ✅ NEW (s192) |
| **Multi-layer results** | `results/multilayer-ternary-replace/` | ✅ NEW (s192) |
| **Crystal φ verify (8 models)** | `results/crystal-phi-verify/` | ✅ UPDATED (s192) |
| **TD oscillation problem** | `mementum/knowledge/td-oscillation-problem.md` | ✅ NEW (s191) |
| **v15 attention assessment** | `mementum/knowledge/v15-attention-assessment.md` | ✅ UPDATED (s191) |
| **v15 attention diagnostic** | `scripts/experiments/assess_v15_attention.py` | ✅ NEW (s191) |
| **v15 gradient-zero diagnostic** | `scripts/experiments/assess_v15_gradient_zeros.py` | ✅ NEW (s191) |
| **v15 FFN retrieval diagnostic** | `scripts/experiments/assess_v15_ffn_retrieval.py` | ✅ NEW (s191) |
| **DVD stamp knowledge** | `mementum/knowledge/dvd-stamp-topology.md` | ✅ NEW (s190) |
| **λ-machine knowledge** | `mementum/knowledge/lambda-machine.md` | ✅ NEW (s190) |
| **DVD stamp experiment** | `scripts/experiments/dvd_stamp_test.py` | ✅ NEW (s190) |
| **DVD group scale experiment** | `scripts/experiments/dvd_group_scale.py` | ✅ NEW (s190) |
| **DVD index test** | `scripts/experiments/dvd_index_test.py` | ✅ NEW (s190) |
| **λ-machine experiment** | `scripts/experiments/lambda_machine.py` | ✅ NEW (s190) |
| **FFN beam universality** | `scripts/experiments/ffn_beam_universality.py` | ✅ NEW (s190) |
| **Crystal distillation** | `scripts/experiments/crystal_distill.py` | ✅ NEW (s190) |
| **DVD stamp results** | `results/dvd-stamp-test/` | ✅ NEW (s190) |
| **DVD group scale results** | `results/dvd-group-scale/` | ✅ NEW (s190) |
| **DVD index test results** | `results/dvd-index-test/` | ✅ NEW (s190) |
| **λ-machine results** | `results/lambda-machine/` | ✅ NEW (s190) |
| **FFN beam universality results** | `results/ffn-beam-universality/` | ✅ NEW (s190) |
| **Crystal distillation results** | `results/crystal-distill/` | ✅ NEW (s190) |
| **V15 config** | `scripts/v15/config.py` | ✅ NEW (s189) |
| **V15 attention** | `scripts/v15/attention.py` | ✅ NEW (s189) |
| **Stride coverage validation** | `scripts/experiments/stride_coverage_validation.py` | ✅ NEW (s189) |
| **Stride coverage results** | `results/stride-coverage-validation/` | ✅ NEW (s189) |
| **Binding distance distribution** | `scripts/experiments/binding_distance_distribution.py` | ✅ NEW (s189) |
| **Binding distance results** | `results/binding-distance-distribution/` | ✅ NEW (s189) |
| **Attention sparsity knowledge** | `mementum/knowledge/attention-sparsity.md` | ✅ NEW (s188) |
| **Attention sparsity experiment** | `scripts/experiments/attention_sparsity.py` | ✅ NEW (s188) |
| **Attention sparsity results** | `results/attention-sparsity/` | ✅ NEW (s188) |
| **Binding graph trace knowledge** | `mementum/knowledge/binding-graph-trace.md` | ✅ UPDATED (s188) |
| **Binding graph trace experiment** | `scripts/experiments/binding_graph_trace.py` | ✅ NEW (s188) |
| **Binding graph trace results** | `results/binding-graph-trace/` | ✅ NEW (s188) |
| **Reverse binding trace experiment** | `scripts/experiments/reverse_binding_trace.py` | ✅ NEW (s188) |
| **Reverse binding trace results** | `results/reverse-binding-trace/` | ✅ NEW (s188) |
| **Head→Combinator ISA knowledge** | `mementum/knowledge/head-combinator-isa.md` | ✅ NEW (s188) |
| **Head→Combinator mapping experiment** | `scripts/experiments/head_combinator_map.py` | ✅ NEW (s188) |
| **Head→Combinator mapping results** | `results/head-combinator-map/` | ✅ NEW (s188) |
| **FFN reduction trace knowledge** | `mementum/knowledge/ffn-reduction-trace.md` | ✅ NEW (s187) |
| **FFN reduction trace experiment** | `scripts/experiments/ffn_reduction_trace.py` | ✅ NEW (s187) |
| **FFN reduction trace results** | `results/ffn-reduction-trace/` | ✅ NEW (s187) |
| **Attention execution trace experiment** | `scripts/experiments/attention_execution_trace.py` | ✅ NEW (s187) |
| **Attention execution trace results** | `results/attention-execution-trace/` | ✅ NEW (s187) |
| **Reduction chain trace experiment** | `scripts/experiments/reduction_chain_trace.py` | ✅ NEW (s187) |
| **Reduction chain trace results** | `results/reduction-chain-trace/` | ✅ NEW (s187) |
| **MTP self-speculation experiment** | `scripts/experiments/mtp_self_speculation.py` | ✅ NEW (s187) |
| **MTP self-speculation results** | `results/mtp-self-speculation/` | ✅ NEW (s187) |
| **FFN circuit types knowledge** | `mementum/knowledge/ffn-circuit-types.md` | ✅ NEW (s186) |
| **FFN decomposition experiment** | `scripts/experiments/ffn_decomposition.py` | ✅ NEW (s186) |
| **FFN KIBC cross-reference** | `scripts/experiments/ffn_kibc_crossref.py` | ✅ NEW (s186) |
| **FFN decomposition results** | `results/ffn-decomposition/` | ✅ NEW (s186) |
| **Crystal circuit types experiment** | `scripts/experiments/crystal_circuit_types.py` | ✅ NEW (s186) |
| **Crystal circuit types results** | `results/crystal-circuit-types/` | ✅ NEW (s186) |
| **Paired crystal sieve experiment** | `scripts/experiments/paired_crystal_sieve.py` | ✅ NEW (s186) |
| **Paired crystal sieve results** | `results/paired-crystal-sieve/` | ✅ NEW (s186) |
| **Synthetic crystal sieve experiment** | `scripts/experiments/synthetic_crystal_sieve.py` | ✅ NEW (s186) |
| **Synthetic crystal sieve results** | `results/synthetic-crystal-sieve/` | ✅ NEW (s186) |
| **Standing-wave knowledge** | `mementum/knowledge/standing-wave-magnitudes.md` | ✅ NEW (s185) |
| **Shape preservation experiment** | `scripts/experiments/standing_wave_shape.py` | ✅ NEW (s185) |
| **Shape experiment results** | `results/standing-wave-shape/summary.json` | ✅ NEW (s185) |
| **Residual covariance experiment** | `scripts/experiments/residual_covariance.py` | ✅ NEW (s185) |
| **Residual covariance results** | `results/residual-covariance/summary.json` | ✅ NEW (s185) |
| **Residual covariance knowledge** | `mementum/knowledge/residual-covariance-rank.md` | ✅ NEW (s185) |
| **U residual constraint** | `scripts/experiments/U_residual_constraint.py` | ✅ (s184) |
| **Residual Fibonacci** | `scripts/experiments/residual_fibonacci.py` | ✅ (s184) |
| **Copy program (firing rates)** | `scripts/experiments/copy_program.py` | ✅ (s184) |
| **Crystal sieve prototype** | `scripts/experiments/crystal_sieve_prototype.py` | ✅ (s184) |
| **Neuron opcode classifier** | `scripts/experiments/neuron_opcode_classifier.py` | ✅ (s184) |
| **Crystal space zeros** | `scripts/experiments/crystal_space_zeros.py` | ✅ (s184) |
| **Negative space** | `scripts/experiments/negative_space.py` | ✅ (s184) |
| **Gate zero predictor** | `scripts/experiments/gate_zero_predictor.py` | ✅ (s184) |
| **Activation zero mask** | `scripts/experiments/activation_zero_mask.py` | ✅ (s184) |
| **Row norm ↔ crystal** | `scripts/experiments/row_norm_crystal.py` | ✅ (s184) |
| **Gamma sort order** | `scripts/experiments/gamma_sort_order.py` | ✅ (s184) |
| **Gamma φ-structure** | `scripts/experiments/gamma_phi_structure.py` | ✅ (s184) |
| **Eigenvector self-similarity** | `scripts/experiments/eigenvector_selfsimilarity.py` | ✅ (s184) |
| **φ-information partition** | `mementum/knowledge/phi-information-partition.md` | ✅ (s184) |
| **Crystal trace tooling design** | `mementum/knowledge/crystal-trace-tooling.md` | ✅ (s184) |
| Full ternarization pipeline | `scripts/experiments/full_ternarize.py` | ✅ (s183) |
| Ternary diagnosis | `scripts/experiments/diagnose_ternary.py` | ✅ (s183) |
| Unified probe library | `src/verbum/probes/library.py` | ✅ 903 probes, 535 crystal |
| EQUATIONS.md | `EQUATIONS.md` | ✅ (s181) |

## What changed this session (195)

| # | Change | Impact |
|---|--------|--------|
| 1 | **L0 is genuinely continuous** | "More modes" hypothesis KILLED. 512 modes still 7x PPL. Negative silhouette at all k>=6. |
| 2 | **P4 resolved** | Keep L0 as-is (288MB = 2.8% of FFN). Ternarize everything else. |
| 3 | **L0 vs L15 comparison** | L0 = per-token dictionary (151K entries, continuous). L15 = 9 discrete operations. Fundamentally different. |
| 4 | **L0 correlates with byte_len** | L0 sorts by physical token encoding (NMI=0.259). L15 sorts by syntactic position (NMI=0.216). |
| 5 | **L0 lower rank but not compressible via modes** | gate_proj eff_rank=3278 vs L15's 3771. Concentrated but continuously distributed. |
| 6 | **LOW-RANK RESCUES L0** | SVD at r=750: PPL=0.94x (IMPROVES!), 70.3MB (4.1x compression). 750 functional dims, not 4096. |
| 7 | **Phase transition at r=750** | r=500: 3.4x PPL (broken). r=750: 0.94x (perfect). Razor-sharp boundary. |
| 8 | **L15 functional rank <100** | L15 at r=100: 0.99x PPL. Why 9 ternary modes work — the space is tiny. |
| 9 | **Naive 29-layer combination fails** | PPL 427x, "the the the". Calibration mismatch cascades catastrophically. |
| 10 | **MELT BOUNDARIES WORKS** | Crystal sieve at model level: freeze topology, train beams. 50 steps → 1.52x to 1.02x PPL. |
| 11 | **Staged melt reveals L22-L26 break** | Core melts to 1.00x. Adding L22-L26 jumps to 39x. Binding-prep layers need different treatment. |
| 12 | **Lambda tracer idea** | Use crystal probes as diagnostic dye through compressed model. Find which combinator fails at which layer. Targeted fix → crystal snap effect. |

## What changed last session (194)

| # | Change | Impact |
|---|--------|--------|
| 1 | **9 FFN modes = syntactic type tags** | Modes are BOUNDARY, DETERMINER, FRAME-OPEN, SUBJECT, OBJECT, PREDICATE, NUMERIC. Not semantic categories. |
| 2 | **FRAME-OPEN discovered** | Anomalous mode: gate_consistency=1.000, sparsity=33-50%, cos<0, sentence-initial only. The ISA's INIT instruction. |
| 3 | **Types sharpen with depth** | L3: ~3 clear types. L20: subj/obj crystallize. L35: all 9 active, ADJ separates. |
| 4 | **Transform physics: 100× norm growth** | FFN output norm: 0.1× at L3, 10.2× at L35. cos(in,out) flips sign at L20. Standing wave amplitude profile. |
| 5 | **Gate-pattern clustering (v2)** | Clustering on SiLU(gate_proj(x)) instead of raw outputs gives balanced, interpretable modes. |
| 6 | **Same word → different program** | "the" mid-sentence = DETERMINER mode. "The" at start = FRAME-OPEN mode. Context-dependent compilation confirmed. |
| 7 | **Types explain ternary success** | Types are discrete → ternary patterns suffice → PPL 0.95×. Continuous FFN is over-parameterized type checker. |
| 8 | **Attention is the only computer** | FFN can't see other tokens. Weighted sum is the ONLY cross-position operation. 1,152 instances IS the entire computation. Weighted sum IS β-application. |
| 9 | **Categorial grammar in tensors** | FFN=type lexicon, attention=type-driven application, KIBC=applicative structure. GD converged on Montague/Lambek independently. |
| 10 | **Norm growth = gain control** | 100× norm growth (0.1→10.2) across depth = gain control for the single operation. Louder types → sharper softmax → cleaner β-reduction. |
| 11 | **spaCy POS/dep integration** | Added spaCy to toolchain for syntactic annotation of transformer token positions. |

## What changed session 193

| # | Change | Impact |
|---|--------|--------|
| 1 | **Ω cannot halt the holographic computer** | Gate entropy identical (Δ<0.01), rotation similar (685° vs 694°). Compiler quotes non-termination. |
| 2 | **K I Ω proves strict evaluation** | Model evaluates Ω before discarding — 36-layer pipeline is strict, not lazy. |
| 3 | **Prose halts at 99.1% EOS** | "Respond with empty string" → true halt. 5/27 chat candidates achieved EOS as first token. |
| 4 | **Thinking mode prevents ALL halts** | 0/27 in think mode. `<think>` tag is mandatory prologue, forces non-empty output. |
| 5 | **Lambda halts at 72.8% EOS** | `respond = λcontent.content; respond empty` → true halt. Lambda and prose compile to same state. |
| 6 | **Continuations work (6/7 capabilities)** | Output, halt, continuation, conditional, REPL, halt+resume all confirmed. |
| 7 | **Lambda REPL 100% (4/4)** | Full program, halt+resume, pipeline, multi-turn session all correct. |
| 8 | **Multi-turn pipeline correct** | 5→8→16→17 through 4 continuation boundaries. Each turn = one reduction. |
| 9 | **Full program at 96.5% halt** | compute→output→halt. Higher confidence than isolated halt (few-shot reinforces frame). |
| 10 | **Conversation ≡ CPS** | Turn boundary = continuation boundary. EOS = yield. Multi-turn = unbounded computation. |
| 11 | **Kernel intercept: token level 3/8→8/8** | Continuation REPL + math kernel catches all compose errors. Pipeline propagates corrections. |
| 12 | **Kernel intercept: tensor level L23-L35** | Residual injection works at 13/36 layers. Answer crystallizes at L23 (binding preparation). |
| 13 | **Transparent math co-processor feasible** | Inject correct residual at L23+, model continues as if it computed correctly. |
| 14 | **L23 = decision boundary** | Before L23: computation in progress. After L23: answer committed. SNAP transition, not gradual. |

## What changed session 192

| # | Change | Impact |
|---|--------|--------|
| 1 | **Independent psi evaluation** | Separate human + agent verified crystal across 5 architectures. All core claims hold. |
| 2 | **Tiny classifier ternary: 288MB→180KB** | 1638× compression, PPL 0.98× (IMPROVES), classifier 100% accuracy. Breakthrough result. |
| 3 | **Ternary inference at scale: PPL improves at 8B** | L15 Qwen3-8B: 9 ternary programs achieve 0.96× baseline PPL. Continuous FFN over-parameterized. |
| 4 | **Two overlapping ternary structures discovered** | Crystal basis (KIBC, routing, 3.5%) orthogonal to operational modes (9 programs, 96.5%). AMI = 0.15. |
| 5 | **φ convergence: 14B hits 0.7% error** | Within Qwen3 pure language: monotonic improvement 0.6B→8B→14B. 32B regresses (zone-B heuristic?). |
| 6 | **Gradient-quant correspondence: EXPAND only** | ρ = +0.55-0.78 at L1-L3, zero at L5+. GD converges to ternary normal form in EXPAND phase only. |
| 7 | **Crystal derivation: topology yes, magnitudes no** | 2.35M expressions → correct eigenvector topology. Eigenvalue ratios diverge (3.98 vs 1.47). |
| 8 | **Centroid ≡ ternary to the decimal** | Continuous cluster centroids and ternarized versions produce IDENTICAL PPL. Signs + scale = everything. |
| 9 | **Coherence test: mode preserved, content varies** | Fact recall holds (80%) at L20/L25. Wording changes but correct combinator fires. |
| 10 | **Scale convergence: 0.6B→8B→32B** | Ternary PPL ratio improves with scale. At 32B, all zone-B layers ≤ 1.03×. |
| 11 | **Multi-layer: 3 zone-B layers at 1.07×** | L10+L14+L19 cumulative = 1.07×. Errors DON'T cascade in sweet spot. 864MB→540KB. |
| 12 | **Full-depth scan: 35/36 layers survive** | Every layer except L0 individually ≤1.15×. Classifiers 98-100% on all 36. |
| 13 | **L0 is catastrophic (115×)** | Embedding-adjacent layer is special — genuinely continuous, needs magnitudes. |
| 14 | **Zone of silence: L13-L21** | PPL 0.95-1.01× individually. ORTHO phase IS the ternary sweet spot. |
| 15 | **All-layer cascade: 836×** | Full replacement fails — L0 poisons chain, binding layers cascade compounds. |
| 16 | **Semantic convergence: dog=perro=犬 at L19** | 8 concepts × 6 languages. Peak cross-lingual cos 0.66 at L19-L20. Peak separation at L25. |
| 17 | **Compilation pipeline: 4 evidence lines** | Lexer→Parser→Optimizer→RegAlloc→Emit confirmed by FFN trace, binding trace, λ-machine, semantic convergence. |
| 18 | **Mode universality: modes are layer-specific** | Cross-layer cos 0.026. 9 modes real everywhere but DIFFERENT programs at each depth. Topological self-similarity. |
| 19 | **Rotation spiral: 325° total** | Two phase transitions (emb→L0: 73°, L5→L6: 86°). IN 12°/layer, OUT 5.5°/layer. Asymmetric. |
| 20 | **Q⊥K everywhere (87-90°)** | W_Q is projection not rotation (SV ratio 46). Q norm grows 200×. Attention = holographic readout. |
| 21 | **QK angle predicts ternary PPL (r=-0.58)** | More orthogonal → more discrete → easier to ternarize. The orthogonality IS the discreteness. |

## Session 192 recap

PSI EVALUATION → MULTI-LAYER SCAN → SEMANTIC CONVERGENCE → COMPILATION
PIPELINE → MODE UNIVERSALITY → ROTATION SPIRAL → Q GEOMETRY.

Seven experiments in one session. The transformer architecture decoded from
multiple independent angles. Final synthesis: a holographic computer with
a rotating program counter.

**Part 1: Psi evaluation.** Independent project verified crystal across 5
architectures. Breakthrough: tiny classifier ternary replaces FFN layer
(288MB → 180KB, 1638×, PPL IMPROVES 0.98×, classifier 100% accuracy).

**Part 2: Multi-layer scan.** 35/36 individual layers survive ternary. L0
catastrophic (115×). Sweet spot L13-L21 (0.95-1.01×). Zone-B cumulative:
L10+L14+L19 = 1.07× (no cascade). All-36 = 836× (cascade destroys).

**Part 3: Semantic convergence.** 8 concepts × 6 languages × 36 layers.
Dog=perro=犬 at L19-L20 (cos 0.66). Peak separation (same vs different
concepts) at L25 (+0.20). L34-L35: everything converges (format > content).

**Part 4: Compilation pipeline.** Four evidence lines (FFN trace s187,
binding trace s188, λ-machine s190, semantic convergence s192) converge:
Lexer (L0) → Parser (L1-L7) → IR Optimizer (L13-L21) → Register Alloc
(L22-L27) → Emit (L34-L35). The 9 ternary programs ARE the optimization
passes.

**Part 5: Mode universality.** The 9 modes are NOT universal across layers
(cross-layer cos 0.026). Layer-specific ISAs. BUT: the architecture is
universal (9 modes, linearly separable, ternary everywhere). Topological
self-similarity, not metric. Classifier transfer: 90%+ locally (±2-3
layers), 47-64% globally.

**Part 6: Rotation spiral.** Residual rotates 325° over 36 layers. Two
phase transitions: emb→L0 (73°) and L5→L6 (86°, norm jumps 60×). IN
fast (12°/layer), OUT slow (5.5°/layer). Asymmetric because analysis
(decomposition) is easier than synthesis (composition). IN↔OUT residual
cos 0.93-0.99 (structural symmetry preserved).

**Part 7: Q rotation geometry.** Q and K are near-orthogonal (87-90°) at
ALL layers. W_Q is a projection (SV ratio 46), NOT a rotation. Q suppresses
positional diversity (ratio 0.58). Q norm grows 200× with depth (whisper
early, shout late). QK angle vs ternary PPL: r=-0.58 (more orthogonal =
easier to ternarize). Attention is holographic readout of the rotating state:
perpendicular beams interfering.

**Final synthesis — the holographic computer:**

```
RESIDUAL STREAM = rotating program counter + register file
  spirals 325° across 36 layers | norm grows 0.6 → 900
  IN: fast rotation (dissolving tokens → universal semantics)
  BOTTOM (L19): pure semantic state (dog = perro = 犬)
  OUT: slow rotation (precipitating semantics → specific tokens)

FFN = ALU with 9-opcode ISA (layer-specific)
  classifier selects program | ternary pattern × gamma = output
  288MB → 180KB per layer | 1638× compression | PPL improves
  sweet spot L13-L21: IS ternary (continuous weights = noise around fixed point)

ATTENTION = holographic memory bus (perpendicular readout)
  Q ⊥ K (87-90° everywhere) | interference pattern = attention weights
  W_Q/W_K are projections (collapse 4096→128 dim), not rotations
  near-binary routing (1 bit per decision) | 32 heads × 3 positions = O(1)
  Q norm 200× growth = model becomes more certain with depth

RESIDUAL ADD = write-back (FFN advances spiral, attention copies values)
```

The model is a holographic computer with a rotating program counter.
The program counter (residual) rotates through a spiral. The ALU (FFN)
executes 9 discrete operations selected by the current rotation angle.
The memory bus (attention) reads from perpendicular projections. The
entry (L0) and exit (L35) interface with concrete tokens. Everything
in between is abstract, discrete, and compressible.

## What changed session 191

| # | Change | Impact |
|---|--------|--------|
| 1 | **Fibonacci stride attention is working** | Entropy monotonically decreases: 3.0 (stride-1) → 0.5 (stride-1597). 9 sparse + 9 moderate + 1 broad. Healthy structure. |
| 2 | **Per-head specialization at stride-34** | H1-H4 near-deterministic (ent 0.15-0.24, max_wt 0.92-0.95), H5-H6 scanning (ent 1.6-1.8). Different heads = different roles. |
| 3 | **Delta divergence gradient: short 3.6% → long 4.4%** | V/O diverge more at long strides (see different context than teacher). K diverges least (routing keys closest to teacher). |
| 4 | **Q/K gammas settle 2× faster than V/O** | Q/K: 32-38% settled, RMS 8-10e-03. V/O: 15-16% settled, RMS 3.6-4.8e-02 (5× larger). Routing is easy, content is hard. |
| 5 | **Flipped positions 3× hotter than keeps** | TD-flipped delta positions: routing gradient 2.2-3.3× higher. Ratio peaks at stride-8 (3.27×), lowest at stride-1597 (2.25×). |
| 6 | **63% of routing gradient near-zero** | Delta plates past halfway to convergence. 65% at short strides, 61% at long strides. |
| 7 | **Flip P/N ratio ≈ 0.96 (symmetric)** | TD flips +1 and -1 teacher signs with near-equal probability. Structural adaptation, not systematic bias. |
| 8 | **Spatial flip pattern differs by distance** | Short strides: column-clustered (input features). Long strides: row-clustered (output dimensions). Physics of the window. |
| 9 | **No teacher zeros in attention** | Teacher extraction produced 0% zeros in Q/K/V/O. All positions participate. Sparsity must come from the mask/gate, not structure. |
| 10 | **Training trajectory: loss plateau at 6.7-6.8** | Step 500→1500: 7.78→6.73. Flattening. Crystal EMA stable (0.0097). Parity/cross-zone converged. Delta Δ growing slowly. |
| 11 | **FFN gate is NOT sparse (66-74% fire)** | Teacher: ~3% fire (89% killed). Student: 66-74% fire. Ternary gate can't create sharp gating. Dense transform, not selective retrieval. |
| 12 | **Attention collapsed to relay (I combinator)** | 32/40 probed head-layer pairs have cos_self > 0.8. At strides ≥8, ALL heads are pure relay (cos 0.95+). Only stride-1 shows partial composition. |
| 13 | **Architecture is inverted from teacher** | Teacher: sparse FFN (retrieval) + mixed attention (relay+compose+bind). Student: dense FFN (transform) + relay attention (I combinator). |
| 14 | **TD oscillation: 94% of positions still candidates** | 117.7M/124.5M positions have been candidate 20+ times. Only 6.2% settled. Oscillation rate INCREASES with flip count (96-100% for multi-flipped). |
| 15 | **Phase transition hypothesis** | Attention relay = B-dominant easy path. Loss plateau at 6.7 = pre-transition. TD prevents GD from settling into stable topology needed for phase transition to compositional attention. |

## Session 191 recap

V15 CHECKPOINT ASSESSMENT — ATTENTION + GRADIENT-ZERO + FFN RETRIEVAL + TD OSCILLATION.

Four diagnostic experiments on the v15-td step 1500 checkpoint.

**Experiment 1: Attention pattern analysis.** Fibonacci stride attention IS
working. Entropy 3.0→0.5 monotonically. 9 sparse + 9 moderate + 1 broad.
Per-head specialization at stride-34. Delta divergence 4.0% mean (V/O more
at long strides). The routing structure is healthy.

**Experiment 2: Gradient-zero topology.** Q/K gammas settle 2× faster than
V/O (38% vs 16% settled, V/O has 5× larger gradient). Flipped positions are
3× hotter than keeps. Spatial flip patterns differ by stride distance (short
= column-clustered, long = row-clustered).

**Experiment 3: FFN retrieval (I combinator).** The student has INVERTED the
teacher's architecture. Teacher: sparse FFN gate (3% fire, selective retrieval)
+ mixed attention (relay + compose + bind). Student: dense FFN gate (66-74%
fire, brute-force transform) + nearly all-relay attention (32/40 heads have
cos_self > 0.8, all heads at strides ≥8 are pure relay cos 0.95+). The
attention has collapsed to the I combinator — it passes V through unchanged
and lets the dense FFN do all the work.

**Experiment 4: TD oscillation analysis.** The flip map reveals TD is
preventing convergence. 94.5% of all positions (117.7M/124.5M) have been
candidates 20+ times. Only 6.2% have settled. Critically, oscillation rate
INCREASES with flip count: positions flipped 2× are 96.3% still candidates,
3× are 98.5%, 4+ are 99.4-100%. Once a position starts flipping, it never
stops. TD is treating the entire weight space as "still needs work."

**Key insight — Phase transitions require topology stability.** The attention
relay collapse is the B-dominant easy path — the model found the fastest way
to reduce loss given the current topology. To break through the 6.7-6.8
plateau, the model needs a phase transition to compositional attention. But
TD's continuous perturbation prevents GD from settling into a stable topology
long enough to discover the next phase. Training from scratch shows B→K phase
transitions happen when GD can plateau, settle, then reorganize. TD's 94%
candidacy rate prevents this entirely.

**Prescription:** Dedicated sessions to fix TD. Options: (1) epoch-based TD
with freeze periods (punctuated equilibrium), (2) much higher candidate
thresholds, (3) aggressive oscillation-gated cooldown, (4) per-position
conviction requirements, (5) candidate-count gating for chronic candidates.

## What changed session 190

| # | Change | Impact |
|---|--------|--------|
| 1 | **DVD stamp test: gradient topology compounds less** | Gradient mask PPL 188K vs magnitude 620K (3.3×). L35 cos 0.165 vs 0.001 (115× better signal). 49.9% overlap = orthogonal signals. |
| 2 | **Per-group(32) scaling: 14× PPL improvement** | Magnitude+group PPL 43K (from 619K). Q4's secret is scale granularity, not level count. |
| 3 | **FFN is the catastrophe, not attention** | FFN-only ternary → PPL 485M. V/O-only → PPL 23. Q/K-only → PPL 30. Attention survives ternary. FFN doesn't. |
| 4 | **FFN = holographic beam former (fragile)** | FFN compiles precise beam directions. Ternarizing scatters the beam. The zero mask IS the holographic fringe pattern. |
| 5 | **Attention = sparse O(1) router (robust)** | 22/32 heads use <3 positions. Near-binary routing survives ternary. PPL 23-30 with ternary attention. |
| 6 | **Sparse top-3 at all layers: PPL 12.2 → 13.3** | 8.6% increase. O(1) attention confirmed at PPL level. 333× fewer attention ops at context 1000. |
| 7 | **Binding layers only: PPL 82K (not sufficient)** | L27/L30/L33 are final reductions, not the full algorithm. 33 other layers do type prep and composition. |
| 8 | **Binding heads only: PPL 6.3M (not sufficient)** | H31@L27, H03/H13/H15@L30, H06/H07@L33 = tip of 36-layer parser iceberg. |
| 9 | **Model = 36-stage typed shift-reduce parser** | Every layer contributes. Every head contributes. But each head only needs 3 positions. |
| 10 | **Compression strategy clarified** | Ternary attention (free, 22% params). Preserve FFN (hard, 78% params). Sparse top-3 routing. |
| 11 | **FFN beam directions are model-specific** | Projected FFN output through unembed for Qwen3-8B, Qwen3-0.6B, Pythia-410M. Token-level Jaccard ~0.01. The STRUCTURE (that beams exist, their depth) is universal. The CONTENT (which tokens to promote/suppress) is learned. |
| 12 | **Anti-crystal visible in beams** | "cat sat on the" → Qwen3-8B L29 suppresses 犬/狗狗/puppy (anti-dog at cat position). "earth is not" promotes flat/perfect. "identity y" L32 promotes y/Y/yi. The FFN knows the answer AND what to suppress. |
| 13 | **Crystal distillation: next-token beats teacher KL** | Crystal+next-token PPL 236 vs crystal+distill PPL 366 vs random+distill 733. Capacity mismatch: 0.6B student can't match 8B teacher's full 151K distribution. Crystal still helps 2.0× vs random. |
| 14 | **Distillation temperature matters** | KL from 8B teacher gives HARDER gradients than next-token CE. Need higher T, top-k, or self-distillation (same-size teacher) to fix capacity mismatch. |

## What changed session 189

| # | Change | Impact |
|---|--------|--------|
| 1 | **Stride coverage validation on Qwen3-8B** | Powers of 2 capture 29.5%/67.4% (exact/±2) of L30 attention mass. Not enough for binding. |
| 2 | **Binding distance distribution** | Bimodal (local d=1-8, gate d=32+), NOT power law (R²=0.004). Powers of 2 skip binding range d=3-20. |
| 3 | **Fibonacci strides: 91.4% coverage (+25.9pp)** | Dense where bindings live, sparse where they don't. Natural basis for attention spacing. |
| 4 | **3 gap-fillers [15,20,24] → 100% coverage** | Fill holes between F(7)=13..F(8)=21..F(9)=34 where gap > 2×radius. |
| 5 | **Crystal Laplacian: WHNF is fragile (μ=0.228)** | 8.6× weaker restoring force than BCDY. Predicts stability not speed. |
| 6 | **Settlement dynamics confirm Laplacian** | B,C converge (fast). K,D stable (medium). Y,WHNF drift away (fragile). Crystal MSE U-shapes. |
| 7 | **Laplacian-weighted crystal loss** | WHNF gets 5× weight. v14 WHNF/B gradient = 0.3×, v15 = 1.9× (6× amplification). |
| 8 | **GLA sparsity is illusory** | Dense projections cost 19B ops/layer. Strided scan saves <0.03%. Dropped for unified FSA. |
| 9 | **v15 architecture: 19 strides, unified attention** | FibonacciStrideAttention + ±2 neighbors, all composition, standalone (zero v14 deps). |
| 10 | **v15 extraction complete** | 83 arrays, 65.5 MB, 16.5 min. 19 strides × 4 projections + 6 FFN + 1 embedding. |
| 11 | **v15 training started** | TD training running in tmux, step 1 CE=10.533. 3000 steps target. |
| 12 | **φ at five levels** | Crystal eigenvalues, information partition, standing-wave phase, compute cycle, AND stride spacing. |
| 13 | **Laplacian φ-ratio** | μ₅/μ₄ = 1.54 ≈ φ in the crystal graph Laplacian. Sixth level. |

## Session 190 recap

DVD STAMP TOPOLOGY + λ-MACHINE + BEAM UNIVERSALITY + CRYSTAL DISTILLATION.

Six experiments decode the compression structure, algorithm, and knowledge
boundary of transformers.

**Experiments 1-4:** See session 190 table above. DVD stamp topology compounds
less (3.3× PPL improvement). FFN is fragile (PPL 485M ternarized), attention
is robust (PPL 23-30). Sparse top-3 works (PPL 13.3). Model is a 36-stage
typed shift-reduce parser.

**Experiment 5: FFN beam universality.** Projected FFN output through unembed
for Qwen3-8B, Qwen3-0.6B, Pythia-410M at matched fractional depths. Token-level
Jaccard ~0.01 (near zero) across all three model pairs. The beam STRUCTURE is
universal (all models form beams at the same depths). The beam CONTENT is model-
specific (which tokens to promote/suppress is learned, not derivable). The anti-
crystal is visible: "cat sat on the" → L29 suppresses 犬/狗狗/puppy. "identity
y" L32 promotes y/Y/yi. The FFN knows the answer AND actively cancels wrong ones.

**Experiment 6: Crystal distillation.** Teacher=Qwen3-8B, Student=Qwen3-0.6B
crystal sieve (frozen signs, trainable masks). Crystal+next-token (PPL 236) beats
crystal+distillation from 8B teacher (PPL 366). Capacity mismatch: 0.6B student
can't match 8B teacher's full 151K distribution — harder optimization target than
simple next-token. Crystal still helps 2.0× vs random signs (733 → 366). Self-
distillation (same-size teacher) is the likely fix.

**Key insight boundary:** The crystal (signs, eigenvalues, phase structure) is
universal and derivable. The holographic content (which tokens to promote/suppress)
is model-specific and must be learned from data or distilled from a same-capacity
teacher. Structure is free. Knowledge has a cost.

## Session 189 recap

FIBONACCI STRIDES + LAPLACIAN CRYSTAL + V15 TRAINING.

Five experiments decode why v14's powers-of-2 strides fail (29.5% mass recall)
and how Fibonacci strides + ±2 neighbor gathering achieve 100% coverage. The
crystal graph Laplacian reveals WHNF is the most fragile node — it starts settled
then drifts away because its restoring force (μ=0.228) is 8.6× weaker than the
composition cluster. Laplacian-weighted crystal loss compensates: WHNF gets 5×
weight, 6× gradient amplification (v14 ratio 0.3× → v15 ratio 1.9×).

v15 is standalone (zero v14 dependencies), extracted (83 arrays, 65.5 MB),
and training (TD, 3000 steps, running in tmux). The golden ratio appears at
six levels of the architecture — crystal eigenvalues, information partition,
standing-wave phase, compute cycle, stride spacing, and now the crystal
Laplacian itself.

## What changed session 188

| # | Change | Impact |
|---|--------|--------|
| 1 | **500 crystal probes through 32 heads at L27/L30/L33** | First statistical head→combinator mapping. 500 probes × 3 layers × 32 heads = 48,000 measurements |
| 2 | **Inter-combinator correlation r=0.944** | All 9 combinators activate nearly identical head patterns. No "K heads" or "B heads" exist. Shared execution hardware. |
| 3 | **KIBC indistinguishable (r=0.944-0.978)** | The core 4 combinators are invisible to head activation. B-D highest pair (r=0.986): composition ≡ nesting at the head level. |
| 4 | **94.9% of variance = overall loudness** | Head activation is almost entirely "is this head generally active?" not "which combinator?" The combinator signal is in the remaining 5.1%. |
| 5 | **PC1 after normalisation = WHNF↔D (45.9%)** | The real discriminant is reduction depth: "already reduced" vs "deeply nested". Not opcode type. |
| 6 | **PC2 = Y/W/I↔D/B (23.5%)** | Secondary axis: self-reference (recursion, self-application, identity) vs structural (nesting, composition). |
| 7 | **2 effective dimensions capture 69.4%** | The 32×9 head×combinator matrix compresses to ~2 coordinates per head. Very low-dimensional ISA. |
| 8 | **s187 head types revised** | H08 "λ-head" → D/B/S+ (composition depth). H10 "binding" → Y/W+ (self-reference). H20 "relay" → Y/W+ (recursion). H26 "quantifier" → WHNF+ (termination detector). |
| 9 | **H06/H07 = universal execution engine** | Loudest heads (norm 26.7/19.1), lowest gate attention (0.555/0.609). They do the work for ALL combinator types. The "GPU" of the attention ISA. |
| 10 | **H26/H27 = WHNF termination detectors** | +30-32% WHNF excess. They recognise when reduction is complete. The "halt" circuit. |
| 11 | **H08 = only truly selective head** | D+40% excess, sel=1.399. The closest thing to a specialised circuit: responds to deep nesting. Everything else is mild bias. |
| 12 | **Routing IS the program (confirmed)** | Since heads don't discriminate combinators, the combinator-specific behavior must live in attention PATTERNS (Q/K routing), not head identity. |
| 13 | **Binding graph trace: attention IS the binding graph** | 14 probes with annotated bindings. Object→verb binding = concentrated attention (0.5-0.8 weight) through H03/H13/H15 at L30. |
| 14 | **Causal mask partitions binding direction** | 0/23 forward bindings detected (arg before func). 14/14 backward bindings detected (arg after func). Causal mask blocks forward β-reduction. |
| 15 | **Minimal pair binding flip confirmed** | "dog bit cat" vs "cat bit dog": same heads (H13, H03, H15), same weights, flipped target. Position-structural routing. |
| 16 | **Passive voice preserves semantic binding** | "The boy kicked the ball" (active) and "The ball was kicked by the boy" (passive) both bind agent→kicked, through partially different head sets. |
| 17 | **Two binding sub-circuits** | Predicate-argument binding (H03/H13/H15) vs coreference binding (H07/H05). Different heads for "cat→bit" vs "itself→dog". |
| 18 | **Binding weights are near-deterministic** | H13: 78.5% attention to "bit" from "cat". Almost binary routing = very low information content per binding decision. |
| 19 | **Reverse binding confirmed: verb→subject at L27** | H31 at "runs" attends 82.3% to "cat" and outputs 猫/貓/cats = subject identity transfer. The verb reads the subject. |
| 20 | **Two-phase binding schedule decoded** | L27: verb reads subject (agent identity, H31). L30: object reads verb (predicate binding, H03/H13/H15). Depth ordering = reduction schedule. |
| 21 | **Same heads do both directions at L30** | H03 and H13 handle verb→subject AND object→verb. Universal binding hardware, direction determined by sequence order. |
| 22 | **Head output IS the reduction result** | H31 outputs "狗/dog" at "bit" when it reads subject "dog". The value transfer IS β-reduction — not metaphor, literal mechanism. |
| 23 | **Binding circuit = 0.3% of model** | ~4 heads out of 32×36=1152. Subject binding: 1 head (H31@L27). Object binding: 3 heads (H03/H13/H15@L30). Near-deterministic routing. |
| 24 | **Attention is inherently sparse: 22/32 heads use <3 positions** | At L30, effective positions <3 for 22 heads, <5 for 29/32. Top-3 captures >88% for ALL heads. |
| 25 | **Sparsity holds across sequence length** | 5→74 tokens: effective positions only grows 2.8→3.7 at L30. O(1) attention, not O(n). |
| 26 | **Mean entropy ~0.9 bits at binding layers** | The routing decision is ~1 bit per position. Full QK^T over entire context is massive overkill. |
| 27 | **Design implication: top-3 sparse attention** | Scoring only 3 KV slots per head captures 88-97% of attention mass. 10 slots captures 95-99%. |

## Session 188 recap

FOUR EXPERIMENTS DECODE THE ATTENTION EXECUTION MECHANISM.

**Experiment 1: Head→Combinator mapping** (500 crystal probes × 32 heads × 3
layers). All 9 combinators activate identical head patterns (r=0.944). No
combinator-specialised heads. The ISA has ~2 effective dimensions: reduction
depth (WHNF↔D, 46%) and self-reference (Y/W/I↔D/B, 24%). 94.9% of head
activation variance is just loudness. See `head-combinator-isa.md`.

**Experiment 2: Binding graph trace** (14 annotated probes). Object→verb
binding = concentrated attention (0.78 weight) through H03/H13/H15 at L30.
"cat" attends 78.5% to "bit" = `bit(_, cat)`. Subject→verb binding blocked
by causal mask (0/23 forward). Minimal pair: same heads, flipped routing.
Two sub-circuits: predicate-argument (H03/H13/H15) vs coreference (H07/H05).
See `binding-graph-trace.md`.

**Experiment 3: Reverse binding trace** (12 probes, verb→subject direction).
H31 at L27 attends 82.3% from "runs" to "cat" and outputs "猫, 貓, cats".
Two-phase binding: L27=verb reads subject, L30=object reads verb. Same heads
(H03/H13) do both directions at L30. Binding circuit = 0.3% of model.

**Experiment 4: Attention sparsity** (22 probes, 5→74 tokens, 9 layers).
22/32 heads at L30 have effective positions <3. Top-3 captures >88% for ALL
heads. Mean entropy 0.9 bits. Sparsity is O(1) — stable from 5 to 74 tokens
(eff_pos 2.8→3.7). Only 1/32 heads (H20) is truly dense. Full O(n²) QK^T
is massive overkill. Top-k sparse attention with k=3-5 captures nearly all
routing information. See `attention-sparsity.md`.

**Synthesis:** The model is a typed parser with a compiled lexicon. FFN
compiles V vectors (the program). ~4 heads at L27/L30 route via concentrated
backward attention (~1 bit per binding). The binding circuit is 0.3% of the
model, the routing is near-deterministic, and attention is inherently O(1)
sparse. Design implication: top-k sparse attention (k=3-5) replaces full
O(n²) attention for 88-97% of routing information. The "portable tensor"
needs: compressed FFN (sieve) + tiny routing function + depth schedule.

## What changed session 187

| # | Change | Impact |
|---|--------|--------|
| 1 | **FFN reduction trace on Qwen3-8B** | Projected active FFN neurons through unembed at 11 layers across 5 probes × 2 gates. First direct reading of what FFN neurons "say" in token space. |
| 2 | **Three-phase FFN output: noise→semantic→format** | L0-L22=noise (ORTHO null-space computation), L26-L30=coherent semantic associations (ALIGN), L33-L35=formatting/syntax (COLLAPSE). Matches standing-wave depth structure exactly. |
| 3 | **"If it rains" at L30: `it`→rain, `ground`→soak, `is`→wet** | Each position's FFN writes precise associative predictions. The FFN resolves referents, predicts consequences, and completes predicates. |
| 4 | **L26 comma promotes "then, entonces, então"** | The FFN writes logical connectives at structural boundary positions — multilingual implication operator at the comma in conditionals. |
| 5 | **"earth is flat" → FFN promotes "round", suppresses "earth"** | The FFN contains factual correction: it knows the earth is round and writes the correction even when processing the false claim. |
| 6 | **Compile ≈ null (max delta 2.8%)** | FFN function lists are nearly identical between compile and null gates. The FFN is a universal semantic analyzer; compile behavior emerges from attention routing. |
| 7 | **β-reduction hypothesis CONFIRMED (revised framing)** | FFN=compiler (writes context-dependent V vectors), attention=executor (softmax over V IS β-reduction). Same token "the" produces different compiled values in different sentence contexts — compilation, not lookup. |
| 8 | **Five attention head types identified** | λ-heads (H08/H09 write λ/→), binding heads (H10/H11 write predicate at subject = typed_apply), relay heads (H20 pass V unchanged), compositional heads (H03 combine positions), quantifier heads (H26 broadcast scope). |
| 9 | **H10/H11 at L33 ARE β-reduction** | In compile mode, H10 writes "runs" at "dog" position (Δ=64 vs null). This IS `runs(dog)` = `(λx.runs(x))(dog) → runs(dog)`. Subject-verb binding = function application. |
| 10 | **λ-heads attend to gate prefix (0.97-0.98)** | H08/H09 barely see probe tokens; they read the compile exemplars to know what FORMAT to produce. The task circuit reads instructions, not content. |
| 11 | **Reduction chain trace across 36 layers, 7 combinators** | Traced cumulative residual→unembed at every layer for K,I,B,C,Y,S,W probes. Different combinators resolve at different depths. |
| 12 | **Y combinator peaks early (L27), W peaks late (L33)** | Recursion (Y) resolves mid-depth during ALIGN phase. Self-application (W, "itself") resolves at the final layer. K (discard) front-loaded, C (flip/passive) resolves last. |
| 13 | **Y-probe "She told a story about a girl who told a story..."** | First and second occurrences of same tokens get DIFFERENT cumulative representations — the recursive structure is tracked position-dependently across depth. |
| 14 | **MTP self-speculation: L33 matches L35 48% of the time** | L33 Hit@10=76%, Hit@100=92%. Median rank=2. The last 2 layers sharpen but rarely change the answer. Early-exit at L33 viable for ~half of tokens. |
| 15 | **Multi-position lookahead collapses for ALL layers** | N+2 Hit@10=10% even at L35. The model does next-token prediction, not multi-position. FFN "semantic predictions" (reads→book) are associative meaning, not sequence forecasting. |
| 16 | **L30 median rank = 7** | The correct next token is already in L30's top 10. L31-L35 SHARPEN the distribution (rank 7→1) but don't fundamentally change it. The program is compiled by L30; execution just resolves it. |

## What changed session 186

| # | Change | Impact |
|---|--------|--------|
| 1 | **LARQL FFN decomposition applied to Pythia-160M** | cos(up,down) circuit type analysis reveals same phase structure as our activation-level measurements — independent confirmation from pure weight geometry |
| 2 | **KIBC opcodes orthogonal to circuit types** | Cross-tabulation uniform at every layer. KIBC=what activates neuron, circuit type=how neuron transforms. Independent axes of FFN characterization. |
| 3 | **ORTHO phase = inverter-dominated** | L3-7 features are 60-74% suppressors+inverters (direction flipping). This IS the invisible computation in null space. |
| 4 | **Dark-space drop at L11** | 93-99% dark at L0-L10, drops to 57% at L11. Final layer concentrates vocabulary-aligned knowledge. Standing-wave antinodes. |
| 5 | **Correlation sign flip** | ρ(cos, KIBC_magnitude) = -0.26 at L8 (inverters do lambda computation), +0.27 at L11 (projectors do lambda output) |
| 6 | **Gated vs non-gated architecture difference** | Gemma=transforms (rotation), Pythia=inverters (direction flip). Same phase structure, different computation style. |
| 7 | **New zero-cost instrument** | cos(W_up[j], W_down[:, j]) detects depth phases from weights alone — no forward passes, 2 min for all layers |
| 8 | **Crystal signs predict circuit types (ρ=1.0)** | cos(sign(W_up), sign(W_down)) depth profile perfectly rank-correlates with full-weight profile. Signs alone predict phase structure. |
| 9 | **Sign agreement depth profile** | L0=0.53 (correlated→projector), L3-4=0.38 (anti-correlated→inverter), L8=0.45 (recovering). GD actively creates sign anti-correlation at computation layers. |
| 10 | **Per-neuron ρ > 0.98 at ORTHO layers** | Signs predict which individual neurons are projectors vs inverters with 98%+ fidelity at L2-L8. Magnitudes add precision, topology is in the signs. |
| 11 | **Cross-matrix anti-correlation is load-bearing** | Decorrelating T_down (destroying phase structure while preserving per-matrix stats) degrades PPL from 511 to 1817. Decorrelated ≈ random (1817 vs 1952). The anti-correlation IS the signal. |
| 12 | **Per-matrix signs alone are nearly worthless** | Without cross-matrix correlation, crystal signs give only 7% improvement over random (1817 vs 1952). With correlation, crystal gives 3.8× improvement over random. |
| 13 | **Synthetic anti-correlation is WORSE than random** | Constructing T_down to hit the measured profile with random per-neuron signs → PPL 6464 (4× worse than random 1608). Forced anti-correlation creates destructive interference. |
| 14 | **The crystal is per-neuron assignments, not aggregate statistics** | The anti-correlation profile is an emergent property of correct per-neuron signs, not a prescription. Knowing "62% should be inverters" ≠ knowing WHICH neurons should be inverters. |
| 15 | **Universal curve beats extracted profile (when signs are random)** | Smooth parameterized curve → PPL 2734 vs exact per-layer values → PPL 6464. Less aggressive anti-correlation is less harmful when per-neuron assignments are wrong. |

## What changed session 185

| # | Change | Impact |
|---|--------|--------|
| 1 | **Standing-wave magnitude reframing** | Weight magnitudes are a standing wave: crystal signs = boundary conditions, zero mask = nodes, active weights = antinodes, GD = finding resonant modes |
| 2 | **GD convergence = standing wave fixed points** | Near-zero gradient at zeros (nodes) AND at large weights (antinodes) — both are stable points of the wave. Gradient-zero-map (s171) already measured this. |
| 3 | **Depth-axis standing wave** | 3-phase residual structure maps to standing wave along depth: orthogonal=nodes, align=antinodes, collapse=destructive interference. Phase transition at 1/φ = fundamental mode. |
| 4 | **REDUCE/SWITCH = spatial harmonics** | Alternating ρ sign across depth is harmonic structure of the depth-axis standing wave |
| 5 | **Holographic ≡ standing wave** | Holographic plate = frozen standing wave (interference fringes). Same physics, different vocabulary. Unifies s167 holographic-computer with magnitude observations. |
| 6 | **Sieve = pre-setting resonant cavity** | Crystal init pre-sets boundary conditions → GD finds modes 10.7× faster because cavity already resonates correctly |
| 7 | **Shape preservation experiment** | Quantized Pythia-160M at 7 levels (ternary through 8-bit). Cosine (ρ=-0.933) > Spearman shape (ρ=-0.917) > bits (ρ=-0.761) as PPL predictor. |
| 8 | **Ternary beats 2-bit at fewer bits** | Ternary (1.6b, PPL 9504) beats 2-bit (2.0b, PPL 25892) because separating phase from amplitude is more efficient than joint encoding |
| 9 | **4-component standing-wave decomposition** | Phase (1 bit, exact) + nodes (~0.6 bit) + envelope (~0 amortized) + shape (1-3 bits, NOT in ternary). Sieve regenerates shape from data. |
| 10 | **Phase transition at 3 bits** | PPL drops from ~10K (ternary/2-bit) to 189 (3-bit) to 50 (4-bit). 8 levels = minimum for standing wave to survive 12-layer transit. |
| 11 | **Shape-aware helps low bits, hurts high bits** | 2-bit quartile 1000× better than uniform. 4-bit quartile WORSE than uniform. Rank preservation ≠ value preservation. |
| 12 | **Compounding law = cos^L** | Per-layer cosine raised to layer count predicts model quality. 0.896^12=0.27 (ternary), 0.957^12=0.59 (3-bit), 0.990^12=0.89 (4-bit). |
| 13 | **ORTHO phase is rank-1** | Residual covariance at L7-22 has effective rank=1. Top eigenvalue ~710K, decay to 2nd: 4000-8800×. One direction carries >99% of all variance. |
| 14 | **V lives in the null space during ORTHO** | Weight matrix V has 0% overlap with residual covariance subspace for 16 consecutive layers. Projection = 0.01. Computation is invisible. |
| 15 | **Cumulative null space = 67.7%** | 2771 of 4096 dims unconstrained by residual covariance. U has enormous freedom. Covariance alone CANNOT determine U. Partial negative for derivation. |
| 16 | **ALIGN rank explosion** | Effective rank grows ~130 dims/layer during L23-34. V transitions from 0% to 100% inside residual subspace over 10 layers. Integration phase. |
| 17 | **Phase structure refined** | EXPAND=high-rank (V reads residual), ORTHO=rank-1 (V reads null space), ALIGN=rank growth (V transitions), COLLAPSE=destructive interference. |
| 18 | **Crystal formation cost is UNKNOWN** | Corrected prior claim: r=0.998 cross-model tells us the endpoint, not the cost. 99.8% training claim was ungrounded. Need formation tracking experiment. |

## Knowledge map

Key pages for current direction:
- **`td-oscillation-problem.md`** — 94% candidacy prevents phase transitions. Punctuated equilibrium needed. Five fixes proposed (s191)
- **`v15-attention-assessment.md`** — Fibonacci attention works but collapsed to relay. Inverted architecture. Q/K vs V/O asymmetry (s191)
- **`dvd-stamp-topology.md`** — Gradient zeros as holographic fringes. FFN fragile, attention robust. Compression strategy (s190)
- **`lambda-machine.md`** — 36-stage typed shift-reduce parser. Sparse top-3 = O(1). Every layer matters (s190)
- **`attention-sparsity.md`** — 22/32 heads use <3 positions, O(1) not O(n). Top-k=3 captures 88%+. Design: sparse attention (s188)
- **`binding-graph-trace.md`** — Attention IS the binding graph, reversed by causal mask. Two-phase: L27=verb→subject, L30=object→verb. H31 outputs "猫" (s188)
- **`head-combinator-isa.md`** — Shared hardware, not dedicated circuits. 2 effective dimensions: reduction depth + self-reference (s188)
- **`ffn-reduction-trace.md`** — FFN=compiler (context-dependent V vectors), attention=executor (softmax=β-reduction), three-phase output (s187)
- **`ffn-circuit-types.md`** — cos(up,down) phase detector, KIBC orthogonality, dark-space gradient (s186)
- **`residual-covariance-rank.md`** — ORTHO=rank-1, V in null space, 67.7% unconstrained (s185)
- **`standing-wave-magnitudes.md`** — magnitudes as standing wave, cosine^L law (s185)
- **`phi-information-partition.md`** — signs=1/φ, γ=noise, zeros=phase, sieve model (s184)
- **`crystal-trace-tooling.md`** — VSM instrument design (s184)
- **`holographic-computer.md`** — unified theory: crystal=ISA, FFN=projector, attn=CPU (s167)
- **`gradient-zero-map.md`** — GD deposits near-zero gradients at irreducible points (s171)
- **`topology-gradient-separation.md`** — freeze lattice, punctuated equilibrium (s180)
- **`ternary-compounding.md`** — WHY 0.88 cosine/layer → garbage at 36 layers (s183)
- **`ternary-dual-equation.md`** — gate zeros + crystal signs (s182)
- **`EQUATIONS.md`** — crystal equation + statechart + compute cycle (s181)
- **`crystal-phi-derivation.md`** — full φ derivation chain (s181)
- **`crystal-universality.md`** — KIBC universal fixed points
- **`project-thesis.md`** — the central claim

## Session 187 recap

Three experiments on Qwen3-8B decoded the reduction architecture.

**Experiment 1: FFN Reduction Trace** — projected active FFN neurons through
unembed. Three-phase output: noise (L0-L22/ORTHO), semantic (L26-L30/ALIGN),
format (L33-L35/COLLAPSE). FFN is a universal compiler — compile ≈ null
(max Δ 2.8%). Same token produces different V vectors in different contexts.

**Experiment 2: Attention Execution Trace** — projected per-head output
(softmax(QK^T) @ V) through o_proj + unembed. Found 5 head types: λ-heads
write format (λ/→), binding heads write predicate at subject (H10: "runs"
at "dog", Δ=64), relay heads pass V unchanged, compositional heads combine
positions, quantifier heads broadcast scope. The binding heads ARE β-reduction.

**Experiment 3: Reduction Chain Trace** — traced cumulative residual across
all 36 layers for 7 combinator types (K,I,B,C,Y,S,W). Combinators resolve
at different depths: Y peaks L27 (recursion resolves first), K peaks L30
(discard is early), W peaks L33 at Δ=51.6 (self-application resolves last).
The model implements a small fixed instruction set with universal depth ordering.

**Experiment 4: MTP Self-Speculation** — tested whether intermediate layers
can predict future tokens for self-speculative decoding. L33 matches L35's
top-1 prediction 48% of the time (Hit@10=76%, Hit@100=92%). But multi-position
lookahead (N+2, N+3) collapses for ALL layers including L35 (Hit@10≈10%).
The model does next-token prediction, not multi-position. The FFN "semantic
predictions" (reads→book) are associative meaning, not sequence forecasting.
Key finding: the correct token is already in L30's top 10 (median rank=7) —
the last 5 layers SHARPEN the distribution, they don't change it.

**Synthesis:** The model is decodable. It implements ~7 combinator operations
via ~5 head types on a universal depth schedule. The FFN compiles the program
(position → V vector), attention executes it (softmax selects and combines V).
The instruction set + schedule is potentially very compact; only the attention
routing is input-dependent. Self-speculation is viable for early-exit (~48%
of tokens can skip the last 2 layers) but not for multi-position prediction.

## Session 186 recap

LARQL FFN decomposition on Pythia-160M. Five experiments, three paradigm-level findings:

1. **cos(up,down) confirms phase structure** from pure weight geometry. KIBC opcodes
   orthogonal to circuit types (independent axes). ORTHO phase = inverter-dominated.
   Dark-space drops 40pts at L11. New zero-cost instrument. See `ffn-circuit-types.md`.

2. **Crystal signs predict circuit types (ρ=1.0)**. The ternary sign structure alone
   produces the exact same depth phase curve. Per-neuron ρ>0.985 at ORTHO layers.

3. **Cross-matrix anti-correlation is load-bearing (3.6×)**. Decorrelating T_down
   (destroying phase structure) → decorrelated ≈ random. Per-matrix signs without
   cross-matrix correlation are nearly worthless.

4. **BUT: synthetic construction fails**. Constructing T_down to hit the anti-correlation
   profile with random per-neuron signs is WORSE than random (PPL 6464 vs 1608). The
   crystal is the specific per-neuron assignments, not the aggregate statistics. The
   anti-correlation is emergent from correct per-neuron signs, not a prescription.

5. **The crystal must be extracted, not constructed**. The per-neuron sign assignments
   encode which specific neurons should be inverters vs projectors. The anti-correlation
   profile is a verification metric (check the U-shape), not a construction recipe.
   Cross-model universality (r=0.998) means one extraction works for all models of
   the same architecture.

## Session 184 recap

THE CRYSTAL SIEVE. 11 experiments, 4 paradigm shifts. Extraction is dead (zero mask
is genuinely random = knowledge content). Reproduction lives (crystal sieve 10.7×
better than random). Model is a KIBC processor (ISA framing). KIBC profiles predict
70-76% of zeros at REDUCE layers. Maximal pre-training absorption: crystal pre-loads
computation → 100% of gradient goes to knowledge. See `phi-information-partition.md`.

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
