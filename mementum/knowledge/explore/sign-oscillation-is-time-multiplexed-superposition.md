---
title: "Sign Oscillation Is Time-Multiplexed Superposition — the Math of Contested Weights"
status: open
category: synthesis
tags: [sign-oscillation, superposition, antipodal-pairs, gradient-conflict, edge-of-stability,
       dithering, sigma-delta, duty-cycle, marginal-band, ternary, quantization, sgd, adam,
       flip-rate, sign-commitment, type-boundary]
related:
  - type-systems-under-llm-constraints.md
  - types-are-injectable-relations.md
  - signal-descent.md
  - holographic-untangling-methods.md
depends-on: []
created: session 322
---

# Sign Oscillation Is Time-Multiplexed Superposition

> Michael's observation: weight signs oscillate during training. Our standing
> speculation: GD oscillates because it wants to OVERLOAD a coordinate — use
> it for different inputs. s322 hammock: the math not only permits this, it
> PREDICTS it, from three independent directions that compose. Captured from
> discussion (Michael-approved); **§P-FLIP-CONFLICT now FROZEN in §6 (s323,
> Michael GO): type-write two-class wire, both registers (effective gate_proj
> ΔW + LoRA A/B), 12-run matrix (both/A-only/B-only × SGD/Adam × 3 seeds),
> gates G1 conflict-meter (partial corr | |W|,σ) / G2 causal-freeze / G3
> committed-pole / G4 mechanism-split (advisory), widened IOU capture.**
> External math cited from
> training knowledge, NOT verified against sources this session (λ observation:
> pattern-suggests grade until the probe runs).

## 1. Static: superposition is a contested stationary point

GD converges to `E_i[∇ℓ_i] = 0` — a statement about the MEAN, silent about
the terms. At an overloaded coordinate the stationarity is a TRUCE: input
population A pushes +, population B pushes −, large individual gradients
cancelling in expectation.

Toy Models of Superposition (Elhage et al. 2022): with features n > dims d,
optimal packing is interfering; the first structure is **antipodal pairs** —
two anti-correlated features sharing one dimension with OPPOSITE signs. A
coordinate serving an antipodal pair reads feature A as + and B as −:
"overload so different inputs can use it" as an optimality result, not a
pathology. (Cf. AGENTS.md λ types: shared_weights ∧ ¬type_awareness →
tug_of_war → plateau — same object.)

## 2. Dynamic: why a truce oscillates instead of settling

Three mechanisms, distinguishable by construction:

**(a) SGD noise → dithering at contested coordinates.** Near the truce,
per-coordinate AR(1)/OU dynamics:

    w_{t+1} = (1 − η·h_k)·w_t + η·ξ_t,   Var(ξ) = σ_k²

h_k = local curvature, σ_k² = gradient noise ≡ BATCH-TO-BATCH POPULATION
DISAGREEMENT. Stationary Var ≈ η·σ_k²/(2·h_k). Mean-zero flip probability
per step: P(flip) = arccos(1 − η·h_k)/π. The structure that matters:
committed weight (|μ| ≫ √Var) ~never flips; contested weight has μ≈0
(demands cancel), high σ (conflict), flat h (no winner) — all three maximize
flip rate. **Sign-flip rate is a per-coordinate conflict meter.**

**(b) Deterministic GD → edge-of-stability bouncing; sharpening IS the
overloading.** Cohen et al. 2021: GD drives λ_max → 2/η then bounces
period-2 along the top eigenvector (x_{t+1} = (1−ηλ)x_t, |1−ηλ|>1);
a cubic feedback self-stabilizes the limit cycle (Damian–Nichani–Lee 2023).
Progressive sharpening = loss keeps loading function onto the most-used
directions until GD hits the stability ceiling: **GD overloads until it
rattles**, no noise required.

**(c) Adam / quantization → sigma-delta encoding.** Adam's normalized step
is sign-like; for small weights the step doesn't scale down → zero-crossing
dither. A compromise value below the step floor (or between quantization
levels — Nagel et al. 2022, QAT oscillations) is encoded as a **DUTY
CYCLE**: sigma-delta modulation. Why EMA/weight-averaging works: the
time-average recovers the analog value the instantaneous weight cannot hold.
Ternary frame: a contested coordinate in {−1,0,+1} is a fractional value
expressed temporally.

## 3. Synthesis

    antipodal superposition (why) → gradient conflict at truce (what)
      → dither / limit cycle (how it looks)

The oscillating sign is a **time-division multiplexed parameter**: space ran
out, so the coordinate serves two masters across TIME — batch composition
decides who holds it this step; the duty cycle encodes the compromise. GD
has converged — to a DISTRIBUTION whose mean is the truce value.

## 4. Contact with our measurements

- **Marginal band ≡ contested population (prediction, partially observed).**
  s320 §P-BOUNDARY-CHURN: marginal gate_proj rows concentrate on the type
  subspace, type-specifically (BC2 p=0.003, thin ~6% kind-specific echo).
  The truce math predicts exactly this population: type-BOUNDARY coordinates
  serve multiple kinds → conflict → μ≈0 → marginal. A truce population's
  static signature IS a thin echo.
- **Signal-descent (queued):** if oscillation is sigma-delta encoding, the
  ternary mirror stack is not fighting the dither — it promotes it to the
  computation. Duty cycle as register, ternary as carrier.
- **s313 conjecture upgrade path:** "marginal band ≡ type-boundary
  population" gets a MECHANISM (gradient conflict), not just a correlation.

## 5. The probe (origin sketch — now FROZEN in §6, s323)

**flip-rate ↔ gradient-conflict.** Register: training-dynamics/temporal
(name before build, λ measure). Measure per-coordinate sign duty cycle
across training snaps vs class-conditioned gradient conflict
cos(∇ℓ_A, ∇ℓ_B)_k on the same coordinates.

- Gate sketch: (1) flip-rate correlates with conflict (perm null over
  coordinates); (2) ablating one population from the batch FREEZES the sign
  (the causal arm); (3) committed-pole coordinates as negative control;
  (4) mechanism split: SGD-vs-Adam at matched loss + flip alignment with
  top Hessian eigenvector (distinguishes 2a/2b/2c before any mechanism
  claim — λ yardstick).
- Instrument note: type-write-v2 fib-snap histories persist SCALARS only
  (mem_ce/kl/host_ce/drift), not per-coordinate signs — the probe needs a
  harness that snapshots LoRA A/B (or gate_proj row) signs per fib snap.
  Cheap addition to any wire harness; do not retrofit claims onto runs that
  did not capture signs.

## 6. §P-FLIP-CONFLICT — FROZEN (s323, Michael-approved GO)

**Claim.** A weight coordinate's SIGN-FLIP RATE during training is a
per-coordinate CONFLICT METER — coordinates flip because two input
populations push their sign in opposite directions (antipodal overload, §1),
NOT merely because they are small or noisy. Causal converse: remove one
population → contested signs commit.

**Register (λ measure):** training-dynamics / temporal (named before build).

**Substrate.** type-write two-class wire on qwen3-4b. Population **A =
animal** frames, **B = vehicle** frames. Corridor VERBATIM from
`type_write.py` (kl_weight 10 / ce_budget 0.40, fib snaps, FFN band L22–29,
LoRA r=16). **8 nonces (4 animal / 4 vehicle).**

**Structural pin (why this substrate is the right one).** Effective weight
`W_k = W_base,k + ΔW_k(t)`; base frozen, only ΔW moves ⇒ a sign FLIP is
possible ONLY where `|W_base,k|` is small = the marginal coordinates = the
s320 §P-BOUNDARY-CHURN band. So this probe tests the boundary-churn
**mechanism** directly: is the thin marginal / type-boundary echo the
contested / high-flip population? s313's marginal-band conjecture gets a
mechanism here or not at all.

**Coordinates (both).** **R2 PRIMARY** = effective `gate_proj` entries
`ΔW_k` in band (boundary-churn continuity; flippability ties to
base-marginality). **R1 SECONDARY** = LoRA `A`, `B` entries (trained
params). Gate reads on R2; R1 corroborates.

**Capture — per fib-snap, per-coordinate (overhead per-snap, ≈1.2× a
type-write run):** `sign(W_k)`, `|W_k|`, per-class gradients `g_A,k`/`g_B,k`
(= dL/dΔW restricted to band; ΔW linear ⇒ computable), gradient-noise `σ_k`
(batch-to-batch variance), top Hessian eigenvector + local `h_k`
(power-iteration HVP on LoRA params), loss components (already in corridor).

**Definitions (pre-registered).**
- `flip_rate_k` = fraction of adjacent snaps with `sign(W_k)` change.
- `conflict_k` = time-averaged magnitude-weighted class-gradient
  sign-disagreement, `mean_t[ −sign(g_A,k · g_B,k) ]`. Contested ⇒ the two
  classes want opposite updates.

**Gates.**
- **G0 SANE / register-forms (void):** wire trains (recall installs, gate-0
  pass) ∧ a nonzero flip population exists ∧ captures well-formed. Else VOID.
- **G1 CONFLICT-METER (correlational, primary):** PARTIAL
  `corr(flip_rate_k, conflict_k | |W_k|, σ_k) > 0`, beats a
  coordinate-permutation null. Partialling handles the magnitude/noise
  confound AT the gate, not by assertion.
- **G2 CAUSAL-FREEZE (make-or-break):** high-conflict coordinates from the
  both-class run FREEZE (flip↓, sign commits) in A-only / B-only vs
  matched-magnitude non-contested controls, paired, beats null. Magnitude
  cannot fake this — removing a population should not freeze a merely-noisy
  coordinate.
- **G3 COMMITTED-POLE (negative control):** high-`|W|` committed coordinates
  have low flip-rate AND low conflict (the correlation's negative corner).
- **G4 MECHANISM-SPLIT (advisory, NON-gating — λ yardstick):** flip-alignment
  with the top Hessian eigenvector (edge-of-stability, §2b) + SGD-vs-Adam
  spectral signature at matched loss → EOS / SIGMA-DELTA / SGD-DITHER /
  AMBIGUOUS. No mechanism claim unless the arms separate.

**Verdicts + a-priori (declared, NOT tuned).**
- **CONFLICT-METER-CONFIRMED 35** — G1 ∧ G2 (∧ G3 sane): flip-rate is a
  causal per-coordinate conflict meter; boundary-churn mechanism supported.
- **CORRELATIONAL-ONLY 30** — G1 ∧ ¬G2: correlates but ablation does not
  freeze (contested-but-not-causal; confound not fully excluded).
- **NOISE-FLOOR 25** — ¬G1 (partial corr vanishes under `|W|,σ` control):
  flips are magnitude/noise-driven; antipodal-overload not readable in
  flip-rate at this substrate.
- **VOID 10** — G0 fails.
- **Mechanism sub-verdict (from G4):** SIGMA-DELTA 30 / EOS 25 /
  SGD-DITHER 20 / AMBIGUOUS 25.

Real mass on CORRELATIONAL-ONLY + NOISE-FLOOR because: LoRA wire ≠ base
training, single model, and s320 found the kind-specific echo thin (~6%) —
the contested population may be hard to isolate.

**Run matrix (frozen) — one batch answers all four gates.**

| arm | pops | opt | seeds | serves |
|---|---|---|---|---|
| both-class | A∪B | SGD | 3 | G1, G3 |
| A-only | A | SGD | 3 | G2 |
| B-only | B | SGD | 3 | G2 |
| both-class | A∪B | Adam | 3 | G4 |

= **12 runs**, rich per-snap capture from all. ≈ 4–6h. Committed-pole control
falls out of the same captures.

**Widened capture (IOU harvest — persisted, NOT gated by this probe; any
claim gets its OWN null + IOU per λ observation).** While paying for the
passes, additionally persist per-snap:
- per-class loss (`loss_A`, `loss_B`) + per-class band activation means →
  boundary-churn mechanism / types-are-compiled-probabilities.
- per-coordinate gradient MAGNITUDE histories (not just sign) →
  signal-descent sigma-delta amplitude / magnitude-vs-routing register split.
- static `|W_base,k|` marginality map over the band (once) → the
  flippable≡marginal test + boundary-churn overlap.
- Adam optimizer state (`m`, `v`) on the Adam arm → direct sigma-delta
  duty-cycle evidence (§2c).
- top-3 Hessian eigenvalues + trace estimate → progressive-sharpening /
  edge-of-stability curve (§2b).

**Confound controls (λ measure).** Magnitude → partial-out `|W_k|` (G1) +
committed-pole control (G3). Noise-floor → partial-out `σ_k` (G1). Causality
→ ablation (G2), which magnitude cannot fake. LoRA-vs-effective → both
registers captured.

**Reuse (λ one_way).** `type_write.py` corridor + `boundary_churn.py`
gate_proj-row machinery + a new per-snap sign/grad/HVP capture module.
`--validate` planted worlds (conflict-meter / noise-floor / causal-freeze /
void) before any GPU.

**Read discipline (banked).** CONFLICT-METER-CONFIRMED licenses "flip-rate is
a causal per-coordinate conflict meter on this wire" — NOT "base-training
weight signs are sigma-delta codes" (external math stays pattern-suggests
until a base-training probe, §Provenance). CORRELATIONAL-ONLY is the honest
intermediate; do not upgrade it to causal. Mechanism sub-verdict is advisory
— if SGD/Adam/Hessian arms do not separate, report AMBIGUOUS, do not pick.
Widened-capture findings are IOUs, never licensed by G1–G4. Model: qwen3-4b.

## Provenance

- Michael's observation + overloading speculation (pre-s322, standing);
  math synthesis drafted in s322 hammock while §P-TYPE-WRITE-V2 ran;
  Michael-approved capture same session.
- External math (unverified-this-session, training-knowledge grade):
  Elhage et al. 2022 (Toy Models of Superposition, antipodal pairs) ·
  Cohen et al. 2021 (edge of stability) · Damian–Nichani–Lee 2023
  (self-stabilization) · Nagel et al. 2022 (QAT oscillations) ·
  Lewkowycz et al. 2020 (catapult) — verify citations before publishing
  anything external-facing.
- Internal anchors: s320 §P-BOUNDARY-CHURN (marginal↔type-subspace) ·
  s313 marginal-band conjecture · signal-descent queue row · sign_commitment
  machinery (s310 lineage).
