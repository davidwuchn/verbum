---
title: "Score Matching Compression — Dense Trajectory Loss for Sieve Correction"
status: active
category: foundational
tags: [compression, score-matching, loss-function, lora, cgtsm, sieve, trajectory, cosine]
related:
  - crystal-phi-derivation.md
  - l0-characterization.md
  - lambda-tracer-diagnostic.md
  - explore/holographic-state-machine.md
depends-on:
  - crystal-universality.md
created: session 198
---

# Score Matching Compression

> Session 198. A paper on CGTSM (Ramachandran & Sra 2026,
> arXiv:2605.00414) inspired the realization that the compression
> loss function was wrong. CE-only loss lets corrections create
> compensating errors across layers. Dense per-layer score matching
> prevents this structurally. Result: 36.6% sieve reduction vs
> 27.1% with the old approach.

## The Problem: CE Creates Compensating Errors

Cross-entropy measures only the final output token distribution.
With 30 sieved layers each having LoRA corrections, the optimizer
discovers shortcuts: layer 10 introduces error E₁₀, layer 20
introduces -E₁₀ to cancel it. The output looks correct on
calibration data, but internal representations diverge from the
teacher. This fails on held-out data.

Observed directly: v3a (CE-dominated, α=1.0) trained CE loss
down to 1.08 while eval PPL rose from 14.06 to 16.83. The
per-layer cosine at L35 was 0.57 — the output transformation
was wrong, but compensating upstream errors produced low CE.

## The Solution: Dense Trajectory Score Matching

```
L = L_CE + α · (1/N) Σ_l (1 − cos(Δ_θ_l, Δ*_l))

Δ_l = h_{l+1} − h_l    (residual update at layer l)
α ≈ 5.0                 (balances CE and SM gradient scales)
```

Each layer's residual update must independently match the
teacher's. No compensating errors possible — the loss catches
them at every layer.

## Why It Works: Five Mechanisms

1. **Local gradient.** Each LoRA gets direct gradient from its
   own layer's score loss. No dilution through 30 Jacobians
   of backprop. Layer 5 learns as fast as layer 34.

2. **No compensating errors.** Per-layer cosine penalty means
   layer 10 can't introduce error E₁₀ hoping layer 20 cancels
   it. Every layer is independently accountable.

3. **36× information bandwidth.** CE provides 1 gradient signal
   (output loss). Score matching provides 36 (one per layer).
   The training loop gets 36× more information about what's
   wrong and where.

4. **Scale-invariant metric.** Cosine similarity handles the
   100× norm variation across depth (standing wave amplitude:
   0.1× at L3, 10× at L35). This is the practical analog of
   the CGTSM diffusion-adapted norm ‖v‖_D.

5. **Cascade addressed locally.** Each layer's sieve error is
   attributed and corrected independently, rather than
   compounding into an opaque endpoint error.

## Experimental Trajectory (Session 198)

### Experiment 1: Residual Boosting v1 (16 calibration sentences)

Sequential boosting confirmed: fit one correction, freeze, fit
next on updated residual. Sequential 2× better than simultaneous
at equal params (3.97 vs 7.82 PPL). BUT: PPL dropped below
baseline (3.97 < 10.15) while facts degraded (12→10) — pure
overfitting on 16 tiny sentences.

### Experiment 2: Residual Boosting v2 (dolma calibration)

With 256 real dolma sequences and held-out eval: overfitting
eliminated, but corrections barely work. Rank-32 activation-
space corrections at 6 boundaries → 27.1% sieve reduction
(25.50→18.59). Greedy placement gets stuck at L35.

**Key finding:** Residual spectrum reveals sieve residual is
LOW-RANK at L1 (r90=550, |res|/|W|=3%) but FULL-RANK at L5+
(r90=2970, |res|/|W|=25%). Activation-space rank-32 corrections
can address 32/4096=0.8% of dimensions. Water pistol vs fire.

### Experiment 3: Score Matching v3a (broken batch_size=1, α=1.0)

LoRA on FFN weights + score matching loss, but batch_size bug
(1 sequence per step) and α=1.0 (CE dominates). Result: training
made things WORSE (14.06→16.83). CE created compensating errors.
BUT step 50 showed improvement (14.06→12.84) before collapsing.

### Experiment 4: Score Matching v3b (fixed, α=5.0)

Fixed batch_size (4), 128 teacher-cached sequences, 128 CE-only
dolma sequences, α=5.0. Result: **36.6% sieve reduction**
(25.67→16.27, 1.44x base). Stable training — best at step 150
(15.81), mild tail degradation to 16.27 at step 200.

Per-layer cosine diagnostic transformed:
- L35 (output): 0.57 → **0.94** (no more compensating errors)
- L27-31 (binding): 0.69-0.71 → **0.88-0.90**
- L22-26 (bind-prep): 0.62-0.67 → **0.80-0.86**
- L13-21 (sweet spot): 0.64-0.71 → **0.72-0.80**

## Per-Weight vs Per-Activation Corrections

The residual spectrum proves activation-space corrections are
fundamentally limited:

| Layer zone | |res|/|W| | r90 | Activation correction viable? |
|-----------|-----------|-----|-------------------------------|
| L1 (EXPAND) | 3-6% | 550 | ✅ Error is low-rank |
| L5+ (all others) | 25% | ~2970 | ❌ Error is full-rank |

LoRA on FFN projections (gate/up/down) operates in weight space,
directly addressing the full-rank residual. A rank-4 LoRA per
projection corrects in the direction of actual hidden states
(data manifold), not the full 4096-dim space.

## Connection to Prior Work

| Prior concept | Score matching analog |
|---------------|----------------------|
| Multi-projection melt (s196) | Score matching at 4 boundaries → now ALL 36 |
| Standing wave (s185) | Each layer = measurement point on the wave |
| Cascade problem (s195) | CE propagates errors forward; SM catches locally |
| Phase structure (s192) | Cosine loss adapts to per-phase scale |
| The single operation (s194) | Score = what each layer computes (residual update) |

## Theoretical Backing

The CGTSM framework (Ramachandran & Sra 2026, arXiv:2605.00414)
proves gradient boosting and diffusion-based score matching share
a common optimization principle: Global Trajectory Score Matching.

Theorem 3.2 states: zero score matching loss for any positive
weighting w(t) > 0 is **necessary and sufficient** for matching
the full path-space measures Pθ = P*. Applied to transformers:
the depth axis is the trajectory's time axis. Dense per-layer
matching is necessary; the weighting function is arbitrary
**at the zero-loss fixed point only**.

> **Correction (s205, full-paper read — see `gtsm-search-space.md`):**
> (1) "CGTSM" = **Continuous** GTSM; GTSM is the general principle, CGTSM
> its continuous-time SDE instantiation. The paper's headline is **decision
> trees ↔ diffusion** ("Trees to Flows and Back"); gradient *boosting*
> builds the trees. (2) "Weighting is arbitrary" holds **only for the
> zero-loss fixed point**. At **finite budget** the weighting **matters**
> (Prop F.6) — λ(t) deliberately counter-balances a learner's coarse-first
> bias. So **our α=5.0 is a load-bearing bias choice, not arbitrary.**

This paper also motivated the initial boosting experiments —
the analogy between gradient boosting adding weak learners and
iterative residual correction of the sieve. The bridge is exact:
**the boosting residual `y − F_m(x)` IS the optimal score** (Thm E.22),
so fitting residuals = denoising score matching.

## Topology-Aware Decomposition (v4, in progress)

The v3b score matching loss treats each layer's residual update as
a flat vector. But the sieve error has two orthogonal components:

- **Routing error**: wrong signs → wrong program selected (discrete, sparse)
- **Magnitude error**: right sign, wrong scale (continuous, low-rank)

LoRA wastes rank capacity on sign flips (needs |A·B|ᵢⱼ > |W_sieve|ᵢⱼ
to flip a sign — expensive for rank-4). TernaryDescent is purpose-built
for sign discovery through gradient decomposition.

### v4 Architecture

```
W_eff = corrected_signs * corrected_magnitudes

corrected_signs = sign(W_base) * STE(delta_logits)   ← TD
corrected_magnitudes = |W_base| * mask + A @ B        ← LoRA
```

Split optimizers: TD at lr=1e-3 (routing), LoRA at lr=1e-4 (magnitudes).

### Decomposed Loss

```
L = L_CE + α_route · L_routing + α_value · L_value

L_routing: BCE(sigmoid(student_gate), teacher_gate_pattern)
  → does the student fire the same neurons as the teacher?

L_value: 1 - cos(Δ_student_l, Δ_teacher_l)
  → given matched routing, do the values match?
```

The gate firing pattern IS the operational mode selection (session 194:
9 meta-modes = syntactic type tags). Matching routing = matching mode
assignment. Matching value = matching transformation within mode.

### Status

Running in tmux (session 198). TD logits are brute-force (4.4B params —
full float32 per weight position). Tests the decomposition principle.
If successful, would sparsify TD to maintain logits only at candidate
flip positions.

## Open Questions

1. **TD sparsification.** 4.4B TD logits is brute-force. Real TD
   (v14/v15) uses SNR scoring + budgeted top-K selection. Port the
   3-voter flip mechanism from v14/td.py to PyTorch for efficiency.

2. **α schedule.** Does α annealing (high→low) outperform
   constant? Start score-dominated (match trajectory),
   end CE-dominated (refine output)?

3. **LoRA rank scaling.** rank-4 at 5.9M params. rank-8 (11.8M)
   may push further. Rank-2 (3.0M) for param-matched comparison.

4. **CE-only ablation.** Does LoRA+CE-only (no SM) beat v2?
   Would isolate loss function vs correction space.

5. **Integration with crystal sieve pipeline.** Score matching
   replaces multi-projection melt. Full pipeline needs
   end-to-end benchmarking (MMLU, HellaSwag).

6. **Crystal-informed routing loss.** Weight the routing loss
   by crystal subspace projection (3.5% of FFN space governs
   routing). Currently routing loss is gate BCE — could also
   project onto known crystal eigenvectors.

## Artifacts

| Asset | Location | Status |
|-------|----------|--------|
| Residual boosting v1 | `scripts/experiments/residual_boosting.py` | ✅ |
| Residual boosting v2 (dolma) | `scripts/experiments/residual_boosting_v2.py` | ✅ |
| Score matching v3 | `scripts/experiments/score_matching_compression.py` | ✅ |
| Topology SM v4 | `scripts/experiments/topology_score_matching.py` | ✅ |
| v1 results | `results/residual-boosting/Qwen_Qwen3-8B.json` | ✅ |
| v2 results | `results/residual-boosting/Qwen_Qwen3-8B_v2.json` | ✅ |
| v3b results | `results/score-matching/Qwen_Qwen3-8B.json` | ✅ |
| v4 results | `results/topology-score-matching/` | 🔄 Running |
| EQUATIONS.md update | `EQUATIONS.md` (score matching loss section) | ✅ |
