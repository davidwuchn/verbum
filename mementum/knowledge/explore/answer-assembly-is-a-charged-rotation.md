---
title: Answer assembly is a charged rotation — §P-DEPTH-CARRIER
status: designing
category: explore
tags: [depth-trajectory, dmd, rotation, answer-axis, persistent-mode, operator-register, frame-candidate]
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
that emits the answer token, read layer 0 → L — looked like a **coherent
spiral in a 2-plane**: it CHARGES geometrically (~15-20%/layer, amp
0.3→782) while PRECESSING (~5°/layer, task-independent across
trace/dates/λ/scope) then DISCHARGES at the final layer (×12 amplitude
collapse + 30° phase snap into emission). The plane = span{a GENERIC
high-norm carrier axis (shared across trajectories, verbalizes to junk)
× a PRIVATE answer axis (verbalizes to the answer tokens, cos 0.152 vs
unembed, chance 0.014)}.

**Is this a real geometric object — a phase-coherent rotation INTO the
answer axis — or is it generic norm growth (charging) that a DMD read
MISREADS as rotation?** Charging alone is unremarkable (norm grows with
depth in every transformer). The claim under test is the *coherent,
answer-aligned rotation*, not the charge.

Exploration-grade evidence (n=1, greedy, today's contexts, **NOT
evidence** per λ observation capture-euphoria guard — it FEEDS this
design, it does not pre-load the prior): survives DC-centering;
shuffled-layer null 0/20 (max 0.966 vs real 1.003); increment-shuffle
smoothness surrogate 0/20 (rotation vanishes, 8/20 angle exactly 0 ⇒
phase-coherent depth-ordered, ¬drift); plane overlap = one shared + one
private axis (principal cos 0.5-0.72 / 0.04-0.27, chance 0.02).

## Why it matters

First live candidate for the **decision-hold / homeostat slot** (the
s338/s340 named gap: DMD found the transport operator STATIONARY-
CONTRACTING with NO persistent |λ|≈1 mode; the answer might be carried
on a rotating frame while charging = a lock-in-amplifier geometry).
Would connect the rotation family (s128 date-circle, §P-ITERATED-SOFT)
to the operator register. **Frame discipline (0-3 ledger, s326
modulation died):** CHARGED-ROTATION is a DESCRIPTIVE geometric verdict;
it does NOT license "homeostat" / "persistent-mode" / "modulation"
vocabulary — those are separate frame contacts that must be earned by
their own pre-registered tests. `|λ|≈1` here is a DMD-average artifact
of charge(>1) × discharge(<1), NOT a genuine persistent mode (s340 G2
already found persist_frac 0.0).

---

## Design (FROZEN s348 — owes Michael GO before build/data)

**Model.** Qwen3-14B only (single-model bound, declared; the designated
deep-read model, s344). Cross-model = optional cheap RIDER, never
required for the primary verdict.

**Object.** For each prompt, the DECIDING-state depth trajectory
`H ∈ R^{(L+1)×d}` = `driver.bounce(prompt, n).hidden[0]` (frame 0 = the
state that emits the FIRST answer content token), d=5120, L=40. One
trajectory per prompt. Greedy. Verify the model actually emits the
expected answer token; else exclude the prompt (need ≥ MIN_PER_TASK
surviving per task type, else that task VOIDs).

**Battery.** ~10 prompts × 5 task types = ~50, each with ONE
well-defined answer token so the answer axis is defined:
- `reduction`  — SKI/λ term → normal form (answer = the NF's lead token)
- `dates`      — "N days after <day> is" → weekday token
- `arith`      — "a + b =" → number token
- `code_scope` — variable-in-scope readout → value token
- `prose`      — deterministic cloze → next token

**Plane extraction (pre-registered, DMD-first with SVD fallback).**
1. DC-center: `H' = H − mean_ℓ H`.
2. `d = reduced_dmd(H'[:-1].T, H'[1:].T, rank=R)` (R=min(L, 16)).
   Take the leading COMPLEX-conjugate eigenpair (largest |λ| with
   |phase| > 5°). Plane = span{Re(v), Im(v)} of that eigenvector
   (lifted through `Ur`), orthonormalized.
3. FALLBACK RULE (pre-registered): if NO eigenpair has |phase| > 5°
   (DC-dominated, as in the s339 frequency sweep), plane = top-2 right
   singular vectors of `H'`. A run that takes the fallback is flagged
   `plane=svd` and CANNOT score CHARGED-ROTATION on the rotation gate
   from DMD phase alone — it must still beat the coherence nulls.

**Charging band (pre-registered).** Project H' onto the plane →
`(x_ℓ, y_ℓ)`; amplitude `a_ℓ = √(x²+y²)`. Band = contiguous layers from
the first ℓ with `a_ℓ > 0.1·max(a)` up to `argmax(a) − 1` (excludes the
final-layer discharge, read separately).

**Metrics.**
- `R_coh` = `|mean_{ℓ∈band} exp(i·Δθ_ℓ)|` ∈ [0,1], circular
  concentration of per-layer phase increments `Δθ_ℓ = θ_{ℓ+1}−θ_ℓ`
  (θ = atan2(y,x)). Coherent rotation → R_coh→1; drift → R_coh→0.
- `ρ` = median Δθ_ℓ over band, °/layer (the precession rate; REPORTED,
  not fit to a target — λ yardstick / φ-ladder scar).
- `A_align` = max over the 2 plane basis vectors of
  `|cos(axis, unembed[answer_token])|`. The higher-aligned axis is the
  "answer axis"; the other is the "carrier."
- `discharge` (advisory) = `a_L / a_{L−1}` collapse ratio + `|Δθ|` at
  the top layers; localizes to the s343 flip band (L36-39).

**Null battery (per prompt, 2000 draws each).**
- N1 SHUFFLED-LAYER: permute layer order of H, recompute R_coh
  (confirms the pilot 0/20; kills "any monotone charge looks coherent").
- N2 INCREMENT-SHUFFLE: shuffle per-layer step vectors Δh_ℓ, cumsum,
  recompute R_coh (order-destroying, norm-preserving; pilot 0/20).
- **N3 NORM-MATCHED RANDOM-PLANE (the make-or-break for GENERIC):**
  synth trajectory with the SAME per-layer amplitude profile `a_ℓ` but
  ISOTROPIC-random increment directions in R^d → "does matched charging
  in a random plane manufacture this R_coh?" Real must beat N3 q95.
- N4 RANDOM-TOKEN answer-axis null: `A_align` vs the distribution of
  `|cos(plane axis, unembed[random tokens])|`. Real must beat q95.

**Gates → verdict tree (frozen, exhaustive).**
```
G0 validity: determinism (sign_dev 0, det ids) ∧ plane recoverable
   (DMD pair ∨ SVD fallback) ∧ amplitude charges (a grows ≥ 4× over
   band) — per battery. FAIL → VOID.
G1 ROTATION (make-or-break): per-prompt R_coh beats N3 q95 AND survives
   N1,N2; aggregate = fraction passing ∧ combined p across battery
   (sign test, p<0.05). FAIL → GENERIC-NORM-GROWTH-ONLY.
G2 ANSWER-ALIGNMENT: A_align beats N4 q95, aggregate across battery
   (median A_align − q95 > 0, combined p<0.05).
G3 TASK-INDEPENDENCE (qualifier): CV(ρ across task types) < shuffled-
   task-label null q05 → rate is task-independent (reported, does NOT
   flip the verdict).

G0 fail                       → VOID
G1 fail                       → GENERIC-NORM-GROWTH-ONLY
G1 pass ∧ G2 fail             → MIXED (coherent rotation, generic plane)
G1 pass ∧ G2 pass ∧ G3 pass   → CHARGED-ROTATION (universal rate)
G1 pass ∧ G2 pass ∧ ¬G3       → CHARGED-ROTATION (per-task rate)
```

**A-priori mass (before any data):**
CHARGED-ROTATION 35 · GENERIC-NORM-GROWTH-ONLY 30 · MIXED 25 · VOID 10.
*(CHARGED-ROTATION modal but not dominant: the pilot already killed N1
and N2, but N3 — norm-matched random-plane — and N4 — the answer-axis
null — are the freeze's untested make-or-break, and the battery is new
prompts, not the single pilot context. GENERIC carries real mass: charge
is genuinely generic and the answer-alignment could be the artifact.)*

**Planted worlds (--validate, ≥5, through the REAL analyse path):**
1. PURE-CHARGED-ROTATION — clean rotation in an answer-aligned plane +
   charging → CHARGED-ROTATION.
2. NORM-GROWTH-ONLY — charge along a fixed direction, no rotation →
   GENERIC-NORM-GROWTH-ONLY (R_coh fails N3).
3. ROTATION-OFF-AXIS — coherent rotation, plane ⊥ the answer axis →
   MIXED (G1 pass, G2 fail).
4. DRIFT — random walk, matched step norms → GENERIC (N1/N2/N3 refuse).
5. DEGENERATE — flat / pure noise, no charge → VOID (G0).

**Honesty bounds (declared at freeze):**
- n=1 model (Qwen3-14B), greedy, last-token deciding state, today's
  battery. The verdict is a DESCRIPTIVE geometric fact about THIS model.
- CHARGED-ROTATION does NOT re-locate meaning in the weights, does NOT
  prove a homeostat/persistent-mode, does NOT license modulation
  vocabulary (frame_ledger 0-3; those owe separate contacts).
- Charging is expected generic norm growth — the FINDING is the
  coherent answer-aligned rotation, not the charge. One-directional:
  GENERIC/MIXED are the informative kills.
- The answer axis is defined only where a single answer token exists;
  multi-token answers use the first content token (a bound on `code`/
  `dates` verbalization).

## Result

(pending freeze + Michael GO)
