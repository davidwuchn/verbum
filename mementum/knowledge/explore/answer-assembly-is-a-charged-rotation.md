---
title: Answer assembly is a charged rotation — §P-DEPTH-CARRIER
status: done
category: explore
tags: [depth-trajectory, dmd, rotation, answer-axis, late-layer, operator-register, frame-candidate]
related:
  - operator-geometry-la-toolkit.md              # §5a-§5d DMD transport operator (the instrument lineage)
  - rotation-is-iterated-soft-beta-reduction.md  # s128 date-circle rotation (sibling rotation family)
  - repl-driver-trampoline.md                    # the driver that captures the depth trajectory
  - ../memories/answer-assembly-is-a-charged-rotation.md   # the s346 exploratory discovery
depends-on: [src/verbum/driver.py, src/verbum/operator_dmd.py]
---

# Answer assembly is a charged rotation — §P-DEPTH-CARRIER

## The question

s346 REPL play (the ninth exploration, dug from the |λ|=1.003 DMD pair):
the DECIDING state's DEPTH trajectory — the residual stream of the state
that emits the answer token, read layer 0 → L — looked like a coherent
spiral that CHARGES while PRECESSING then DISCHARGES at the final layer,
in a 2-plane {generic carrier axis × answer axis}.

**Is there a real geometric rotation into the answer axis, or is it
generic norm growth that a DMD read misreads as rotation?**

## The s348 re-scope (instrument-first, route-map-v0 precedent)

The first freeze (c953705d) modeled a UNIFORM ~5°/layer precession and
tested it with a rank-2 DMD reconstruction residual. Building the
instrument and looking at real Qwen3-14B trajectories (via the resident
driver, s348) falsified that operationalization on two counts:

1. **The residual metric is order-blind and too brittle.** Real 14B
   trajectories are only ~40% rank-2 (resid 0.53–0.64); a *genuine*
   planted rotation with 15% noise already reads GENERIC. And the
   increment-shuffle null is never beaten because reordering in-plane
   increments keeps them rank-2 — the residual cannot see depth-order.
2. **The rotation is NOT uniform — it is LATE-CONCENTRATED.** The
   unwrapped phase is flat for layers ~0–27 (points collapsed near the
   −DC direction) then sweeps ~200° in the last ~10 layers as the
   amplitude explodes (radius 63 → 1536). The s346 pilot's clean
   `|λ|=1.003` uniform spiral was a DMD *average* of this flat-then-sweep
   shape.

Looking with a late-band reader (n=200 norm-matched nulls, 15 real 14B
trajectories) found a CLEAN, decisive separation — which this re-freeze
tests properly on a fresh battery with the full null battery:

- **swept angle in the late band** (L~30–40): real 5.7–6.2 rad (near a
  full turn) vs norm-matched q95 ~3.8 rad → 15/15. And `swept == wind`
  every time ⇒ the sweep is MONOTONE/one-directional (a coherent
  rotation, not a wandering walk).
- **answer-axis alignment** of the late-band plane: real 0.05–0.13 vs
  random-token q95 ~0.04 → 15/15 (weak margin, but consistent).
- top-2 energy fraction did NOT separate (3/15) — low-dim-ness is not
  the signal; the coherent SWEEP is.

(REPL numbers FEED this design per the capture-euphoria guard; the
frozen run on a fresh battery with full nulls is the test.)

## Why it matters

First live candidate for the decision-hold / answer-assembly slot: the
answer is written by a coherent late-layer rotation into the answer
direction (coheres the s343 transform→output flip and the WHNF-seal /
discharge read). Frame discipline (0-3 ledger, s326): a positive verdict
is a DESCRIPTIVE geometric fact — it does NOT license "homeostat" /
"persistent-mode" / "modulation" vocabulary; those owe separate contacts.

---

## Design (RE-FROZEN s348 — owes Michael GO before build/data)

**Model.** Qwen3-14B only (declared bound). Greedy. Last-token deciding
state. Single model.

**Object.** Per prompt, `H = driver.bounce(prompt).hidden[k]` ∈
R^{(L+1)×d}, k = frame emitting the first answer content token. Battery
~10 prompts × 5 task types (reduction / dates / arith / code_scope /
prose), each with one answer token.

**Late band (pre-registered).** `raw_norm[ℓ] = ‖H[ℓ]‖`; band = contiguous
layers from the first ℓ ≥ 4 with `raw_norm > 0.30·max(raw_norm)` to the
last layer. Require ≥ 5 band layers (else pid invalid). This is the
answer-assembly / discharge region (empirically L~30–40 for 14B).

**Metrics (on the late band).**
- Plane `B` = top-2 right singular vectors of the DC-centered band
  segment. `coords = (seg − mean) @ Bᵀ`.
- `swept` = Σ|Δθ| (total angular path), `wind` = |Σ Δθ| (net winding),
  θ = atan2(coords_y, coords_x). Monotone rotation ⇒ swept ≈ wind.
- `a_align` = max over the 2 axes of |cos(axis, unembed[answer_token])|.
- `charge` = raw_norm[last] / raw_norm[band_start] (validity).

**Null battery (band fixed at the real [lo,hi]; content randomized).**
- **N3 NORM-MATCHED (make-or-break):** same per-layer increment NORMS,
  isotropic-random DIRECTIONS → does matched-magnitude random motion
  sweep as much? Real `swept` must beat N3 q95.
- N1 SHUFFLED-LAYER (confirmatory/advisory): permute layer order.
- N2 INCREMENT-SHUFFLE (advisory only — documented order-blind for the
  low-dim subspace; reported, never gates).
- N4 RANDOM-TOKEN: `a_align` vs random unembedding-row cosines (q95).

**Gates → verdict tree (frozen, exhaustive).**
```
G0 validity: determinism (sign_dev 0) ∧ ≥ MIN_TOTAL valid pids across
   ≥ 2 tasks ∧ charge ≥ 4 ∧ late band ≥ 5 layers.  FAIL → VOID
G1 SWEEP (make-or-break): per-pid swept beats N3 q95; aggregate binomial
   over valid pids, p < 0.05.
G2 ANSWER-ALIGN: per-pid a_align beats N4 q95; aggregate binomial.

G0 fail             → VOID
G1 fail             → NO-EXCESS-SWEEP   (late rotation ≤ norm-matched; the
                                         pilot spiral was a norm-growth
                                         / PCA-arc artifact)
G1 pass ∧ G2 fail   → GENERIC-LATE-SWEEP (real coherent late rotation, but
                                          NOT directed at the answer axis)
G1 pass ∧ G2 pass   → LATE-ANSWER-ROTATION (coherent late rotation INTO the
                                            answer axis)
```
Qualifier: `monotone` if median(wind/swept) ≥ 0.8 (one-directional).

**A-priori mass (before the frozen run):**
LATE-ANSWER-ROTATION 45 · GENERIC-LATE-SWEEP 25 · NO-EXCESS-SWEEP 20 ·
VOID 10.
*(The late-band REPL look was strong on both gates, but on a fresh
battery with the full aggregate nulls the thin answer-alignment margin
(0.05–0.13 vs 0.04) could fail → GENERIC-LATE-SWEEP carries real mass;
the sweep could regress under the frozen per-pid null → NO-EXCESS-SWEEP.)*

**Planted worlds (--validate, ≥5, through the REAL analyse path).**
1. late_answer_rotation — early flat + late coherent sweep in an
   answer-aligned plane → LATE-ANSWER-ROTATION.
2. late_generic_sweep — late coherent sweep, plane ⊥ answer axis →
   GENERIC-LATE-SWEEP.
3. random_walk — norm-matched random walk (swept ≈ null) →
   NO-EXCESS-SWEEP.
4. ray — norm-growth along a fixed axis (swept ≈ 0) → NO-EXCESS-SWEEP.
5. degenerate — no charge → VOID.

**Honesty bounds.** n=1 model (Qwen3-14B), greedy, last-token, today's
battery; descriptive verdict only (no modulation/homeostat vocabulary);
the answer axis is defined only where a single answer token exists;
one-directional (NO-EXCESS-SWEEP / GENERIC are the informative kills);
N2 (increment-shuffle) is documented order-blind for a low-dim subspace
and is advisory only — the make-or-break is N3 (norm-matched).

## Result

**✅ LATE-ANSWER-ROTATION / monotone (a-priori modal 45) — Qwen3-14B,
re-frozen `6931a070`, det 0.0, results `5d5d20ad`.** Fresh 50-prompt
battery, 34/50 valid trajectories.

The answer is written by a **coherent, monotone, late-layer rotation
into the answer axis:**

- **N3 norm-matched (make-or-break): 34/34, p=6e-45.** The late-band
  swept angle (median 5.83 rad ≈ a full turn) far exceeds what
  matched-magnitude random motion produces (~3.8 rad). The rotation is
  real, not a norm-growth artifact.
- **wind/swept = 1.0000 → MONOTONE.** The sweep is one-directional (net
  winding = total angular path) — a coherent rotation, not a wandering
  walk.
- **N2 increment-shuffle: 34/34.** The sweep is ORDER-dependent
  (depth-ordered) — reordering the increments destroys it. (The swept
  metric captures the order-sensitivity the rank-2 residual could not;
  see the s348 re-scope above.)
- **N4 answer-axis: 34/34, p=6e-45.** The late plane is directed at the
  emitted answer token, above the random-token null.

This is the first **answer-assembly-slot** positive — it coheres the
s343 transform→output flip and the WHNF-seal / discharge read (the
rotation IS the seal watched per-trajectory). The s346 pilot's uniform
`|λ|=1.003` spiral was, as the re-scope predicted, a DMD *average* of
this late-concentrated flat-then-sweep shape.

**Honest asterisks:**

- **Answer-alignment is weak** — median `a_align` 0.089 (vs random-token
  q95 ~0.04). Consistent (34/34, p tiny) but SMALL: the answer axis is a
  minor component of the late plane, which is dominated by the generic
  high-norm carrier. Answer-*directed* but weakly.
- **Reduction: 0/34 valid** — λ-reduction trajectories did not meet
  charge ≥ 4 / band ≥ 5, so the finding rests on arith/dates/prose/
  code_scope, not λ-reduction. A genuine scope bound.
- **N1 shuffled-layer 0/34 = uninformative for this statistic** —
  permuting layer positions INFLATES swept (the trajectory jumps around
  the plane), so N1 goes the wrong way; correctly non-gating (advisory).
  The depth-order evidence is N2 + monotonicity, not N1.
- n=1 model (Qwen3-14B), greedy, last-token, single battery. DESCRIPTIVE
  verdict only — no homeostat / persistent-mode / modulation vocabulary
  (frame_ledger 0-3).

**Method banked:** for "coherent depth-ordered rotation," the rank-2 DMD
reconstruction residual is the WRONG operationalization (order-blind: a
set of in-plane increments is rank-2 in any order; and too brittle — a
clean rotation + 15% noise reads GENERIC). The right statistic is the
**swept angle in the amplitude-defined late band vs a norm-matched null**
(same step norms, random directions), with monotonicity (wind/swept) as
the coherence signature. Instrument-first (route-map-v0) caught this at
the smoke gate before the frozen run.
