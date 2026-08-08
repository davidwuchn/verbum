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
> discussion (Michael-approved); no verbum measurement yet — the probe is
> queued (⚪ flip-rate ↔ gradient-conflict). External math cited from
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

## 5. The probe (queued ⚪, unfrozen — s222 freeze-first applies)

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
