---
title: "Relational-Loss Distillation — the Lambda Compiler Teaches Geometry, GD Picks the Frame"
status: open
category: strategy
tags: [distillation, relational-loss, RDM, gram, routing, frame-invariance, teacher-student, normal-form, distributed, compression, construct-path]
related:
  - consensus-delta-folding.md
  - combinator-function-shape.md
  - combinator-training-beta-reduction.md
  - function-extraction-system.md
  - self-teaching-loop  # consensus-delta-folding.md §s217
  - ../function-discovery.md
  - ../two-registers-of-topology.md
  - ../crystal-universality.md
  - gradient-voting.md
  - exact-ternary-fitting.md
  - procrustes-lens-and-crystal-comparison.md
  - relational-loss-phi-compression.md  # DISAMBIGUATION: the OLDER, scalar sense — NOT this
depends-on:
  - combinator-function-shape.md
  - consensus-delta-folding.md
created: session 223
---

# Relational-Loss Distillation

> Session 223. Michael's idea: *"Because we have the lambda compiler, extract from
> the teacher a set of training for the student. With relational loss we could
> guide GD into any geometry that falls out."*
>
> The lambda compiler (the teacher's extracted, **self-verifying** combinator
> normal forms) mints a curriculum whose target is not the teacher's tokens nor
> the teacher's weights, but the teacher's **relational geometry** — the routing-
> register combinator Gram. A relational loss pulls the student's geometry toward
> the teacher's *relations* while leaving its *absolute frame* free ("any geometry
> that falls out"). This page captures the mechanism, why it is the right tool, the
> honest catches, and the first falsifiable experiment.
>
> Register: **functional + topological/routing**.

## DISAMBIGUATION (do not conflate)

`relational-loss-phi-compression.md` (session 030) uses "relational loss" in a
**different, scalar** sense: `r = (L−E)/(logV−E)`, a dimensionless normalization of
CE. That page itself concludes it is "an affine transform … doesn't change
optimization geometry." **This page means the RSA / representational sense:** match
the *pairwise relational geometry* (RDM / Gram of representations), not point-wise
outputs and not a scalar. The two share a name and nothing else.

## The idea, made precise

```
teacher (lambda compiler) ⊢ for each crystal combinator (K I B C S D W Y WHNF):
   inputs   ≡ the 535 crystal probes                         (have: probes/library)
   target   ≡ WHNF / reduction trace (Church-Rosser unique)  (self-verifying labels)
   GEOMETRY ≡ routing-register CMR centroid Gram  G_teacher  (have: combinator map)

student GD: minimize   CE(corpus)  +  λ·‖ G_student − G_teacher ‖   (relational loss)
            G_student = cosine Gram of the student's per-combinator centroids
                        in the SAME register (routing, CMR)
            verdict gate: student also reaches WHNF (Δx→0) on the combinator   [IOU]
```

The student is *not* asked to copy outputs or weights. It is asked to reproduce the
teacher's **relations between combinators** and is free to realize them in whatever
absolute coordinates it likes. That freedom is the feature, not a bug.

## Why relational loss is the RIGHT tool (not just a tool)

The most robust empirical fact in the project is the **frame asymmetry**:

```
absolute weights/signs : cross-init correlation 0.000   (incommensurable; gradient-voting)
relational Gram         : cross-model +0.66→+0.78, z up to +4  (universal; combinator-function-shape)
```

A relational loss targets **exactly that invariant and nothing else**.

- **Output-matching distillation** forces the student toward the teacher's
  *absolute frame* → fights the 0.000 sign-corr → wastes gradient carving a frame
  that does not transfer.
- **Relational loss** constrains the **equivalence class** (the function /
  behavior), not the **representative** (the encoding). This is the s216
  non-unique-composite turned into a training objective: *uniqueness is
  per-behavior, so train the behavior's geometry and leave per-realization plumbing
  free.* "Any geometry that falls out" = the desired degeneracy.

## The three-way division of labor (this is the clean part)

The recurring wall is that **GD cannot carve discrete topology** (softmax dispatch →
winner-take-all → 20/22 ops dead, `dispatch-gradient-death.md`). Relational loss
resolves the division of labor the project has circled:

```
relational loss  → WHICH geometry   | shapes continuous γ toward target relations (GD is good at smooth)
TD / routing     → make it DISCRETE | the flips that crystallize the shape into ternary topology
contractivity/WHNF → VERIFY         | Δx→0 confirms the student EXECUTES the normal form (Exp B +0.712)
```

GD never invents the topology — the teacher's Gram tells it *which* topology, TD
discretizes, the continuation certifies. Maps onto s222 "routing ⊕ continuation =
complete basis" with relational loss as the **steering signal that was missing**
(TD nominated flips rank-1, blind to a target; the teacher Gram supplies the target).

## Why it fits the compression north star

Relational loss is a **weaker constraint** than output-matching — it
under-determines the student. That large null space is where the <1GB ternary
student finds a *small* realization. You do not force the 70B's frame (which needs
70B capacity to hold); you force only its relations, and let the student pack them
into the smallest superposition-/ternary-friendly geometry. This is `λ smallest` as
a loss function, and it respects the **precision inversion** (s222): relational loss
constrains *angles/relations* (where superposition lives → stay continuous) while
leaving *magnitudes* free to ternarize where capacity allows.

## The distributed connection (third frame-unification mechanism)

Two prior ways to beat the frame problem for distributed folding:
1. shared frozen base B₀ (forward folding), 2. reduce-to-canonical-NF then donate.
Relational loss adds a **third: a shared relational target.** If every contributor
trains to match the *same teacher Gram*, they end up **relationally identical by
construction** ⇒ align-before-fold (the hard open piece of reverse-harvest) becomes
**well-posed**: a rigid Procrustes alignment is *guaranteed to exist* (the Grams are
equal), instead of the generic case where it might not. Turns "alignment is the hard
open problem" into "alignment is guaranteed solvable."

## Honest catches (audit discipline — these are the ways to fool ourselves)

1. **Register, or it is worthless (`λ measure`).** The combinator shape is invisible
   in raw activation geometry (silhouette −0.035, z=−1.65) and only appears in the
   **routing register after CMR** (silhouette +0.101, z=7.97). A relational loss on
   the *raw activation Gram* would match the **common-mode crystal** (generic
   structured language — the thing everything shares, s216) → a false positive that
   transfers nothing function-specific. The loss MUST target the gate/routing-CMR
   Gram. **This is the single most likely way to manufacture a fake success — so it
   is the experiment's control condition.**
2. **Goodhart / collapse needs the WHNF gate.** A Gram-matching objective has
   degenerate optima (collapse points → trivially matchable if unnormalized). The
   contractivity oracle is not decoration — it keeps the student *executing* the
   function, not statistically mimicking a relation table. Relational loss = target;
   WHNF Δx→0 = acceptance gate (Exp B). *(WHNF gate is an IOU in the first
   experiment — see below.)*
3. **Sufficiency: transfers the SKELETON, not the plumbing.** A Gram is an
   equivalence-class summary; matching it transfers the forced universal skeleton
   (the +0.78 shared part: B–D/B–C/K–C/S–D/S–Y) but **under-determines** the
   domain-distinctive content (per-model plumbing, the superposition residual).
   Relational loss is cleanest *exactly where the content is least novel.* Not
   fatal, on-thesis (transfer the skeleton cheaply, let forward-folding / continuous
   residual carry the plumbing) — but expect it and measure it, don't be surprised.

## First experiment (s223) — does relational loss transfer the combinator geometry, and only in the routing register?

`scripts/experiments/relational_loss_distillation.py` (register: functional +
topological/routing). Smallest version that fails informatively.

```
teacher  = saved routing-CMR Gram G_teacher (results/combinator-relationship-map/
           Qwen_Qwen3-14B.npz :: gram_route_cmr_L12, best layer) +
           the raw-register control target (gram_hidden_cmr)
student  = tiny from-scratch byte-level transformer with SwiGLU gate (the routing
           register); trained on a small text corpus with CE
conditions:
   (a) CE only
   (b) CE + relational loss on the RAW hidden-CMR Gram      (the control / decoy)
   (c) CE + relational loss on the routing-CMR gate Gram     (the hypothesis)
measure (same instrument as combinator_relationship_map): student sign(gate)-CMR
   combinator silhouette vs permutation null (z) + GramCorr(student, teacher)
```

**Falsifiable predictions:**
- (c) ≫ (b) ≈ (a) on function transfer (silhouette z clears null; GramCorr-to-teacher
  rises). Proves the **register claim** — relational loss only transfers in the
  routing register.
- (c) reaches teacher-like binding with **fewer tokens** than (a). Proves the
  **curriculum-from-compiler leverage**.
- If (b) matches (c) → the register claim is WRONG and we want to know immediately
  (raw geometry would be carrying the function, contradicting the two-registers
  finding).

**Why this is the cleanest MIT level-4 path (`λ provenance`):** the student is
*constructed* from a verified compiler's relational targets, not extracted from a
licensed model — the teacher contributes only a frame-invariant 9×9 Gram (a
measurement, not weights).

### Result (s223) — ✅ CLEAN DOUBLE DISSOCIATION; register claim CONFIRMED

Ran 1500 steps × 3 conditions, tiny byte-level student (d=128, 4 layers, d_ff=256),
teacher = Qwen3-14B routing-CMR Gram (L12). Verdict instrument = student sign(gate)
CMR silhouette vs 1000-perm null + GramCorr off-diagonal vs teacher. (main:2,
`/tmp/relational_loss_distillation.log`, `results/relational-loss-distillation/verdict_run.json`.)

| condition | route_z | route_p | GC(route) | hidden_z | GC(hidden) | CE |
|---|---|---|---|---|---|---|
| (a) CE only | +0.33 | 0.370 | +0.474 | +2.17 | +0.453 | 1.527 |
| (b) CE + raw-Gram | +0.64 | 0.273 | +0.590 | +1.02 | **+0.9995** | 1.534 |
| (c) CE + route-Gram | **+2.21** | **0.013** | **+0.781** | +3.16 | +0.411 | 1.531 |

- **Prediction CONFIRMED: c(route) ≫ b(raw) ~ a** on the function-transfer metrics.
  Only (c) clears the silhouette null (z=+2.21, p=0.013) and reaches GC(route)=+0.781
  (vs teacher's internal ecosystem +0.78). The combinator function shape transferred
  **only** when the relational loss targeted the ROUTING register.
- **Near-perfect DOUBLE DISSOCIATION** (the strong form of the register claim): each
  condition maximizes the register it was trained on and *not* the other. (b) drove
  GC(**hidden**)=+0.9995 (matched its raw target almost exactly) yet left routing at
  the null (route_z +0.64, GC(route) +0.590). (c) drove the **routing** register
  (route_z +2.21, GC +0.781) while GC(hidden) fell to +0.411. ⇒ the two registers are
  separately targetable and **only routing carries the combinator function** — the
  `two-registers-of-topology` finding reproduced as a *training* result, not just a
  measurement. Matching raw geometry (b) buys the common-mode crystal, not the function.
- **Geometry shaped for FREE:** CE is identical across conditions (1.527/1.534/1.531)
  — the relational loss is a weak/compatible constraint (confirms the under-
  determination / "any geometry that falls out" thesis; it rode on top of CE).
- **★ Goodhart caveat made concrete (catch #2 is real):** (b) hit GC(hidden)=+0.9995
  but its hidden *silhouette* z was only +1.02 — **matching the centroid Gram does
  NOT imply crisp per-probe clusters**. GramCorr (centroid relations) and silhouette
  (per-probe separability) are different; a Gram-match can be satisfied without
  execution-grade structure. ⇒ the **WHNF acceptance gate (open lead 1) is load-
  bearing, not optional** — relational loss is a target, not a proof of execution.

**Caveats (functional register):** absolute route silhouettes are NEGATIVE (c:
−0.079); the z is vs the (also-negative) permutation null ⇒ "more clustered than
chance," not crisp partitions (same modest-cosine caveat as the teacher instrument).
Single seed, single teacher (14B), single λ=1.0, single capture layer (L2=middle),
smoke-scale student. The **tokens-to-transfer leverage** prediction (c reaches
binding in *fewer tokens* than a) was NOT measured here — endpoint comparison only;
it is an IOU (open lead 3). Plain CE already gives a partial crystal echo
(GC(route) a=+0.474); (c)'s contribution is lifting it to significant clustering.

### Multi-seed + λ-sweep confirm (s223) — ✅ DECISIVE across 3 seeds × 3 λ

`--sweep` mode: 3 seeds {0,1,2} × 3 λ {0.3,1.0,3.0} × 3 conditions, 1000 steps
(27 runs, 4468s). Aggregate (mean ± std over seeds), `verdict_sweep.json`:

| cond @ λ | route_z | GC(route) | hidden_z | GC(hidden) |
|---|---|---|---|---|
| a CE-only @ any | +0.38±0.51 | +0.436±0.012 | +2.01±0.38 | +0.424±0.015 |
| b raw-Gram @0.3 | +0.95±0.76 | +0.564±0.015 | +1.59±0.24 | **+0.999±0.000** |
| b raw-Gram @1.0 | +1.04±0.37 | +0.539±0.007 | +1.59±0.23 | **+1.000±0.000** |
| b raw-Gram @3.0 | +0.66±0.19 | +0.552±0.020 | +1.83±0.22 | **+1.000±0.000** |
| c route-Gram @0.3 | **+2.44±0.73** | +0.780±0.032 | +2.67±0.71 | +0.431±0.041 |
| c route-Gram @1.0 | **+2.83±0.50** | +0.795±0.032 | +2.91±0.81 | +0.430±0.041 |
| c route-Gram @3.0 | **+2.41±0.42** | **+0.847±0.007** | +3.15±0.86 | +0.440±0.050 |

- **DECISIVE check PASSES at every λ:** `c.route_z(mean−std) > a.route_z(mean+std)`
  AND `c.gc_route > b.gc_route`. The double dissociation is robust to seed and λ, not
  an n=1 artifact.
- **c clears the null robustly** (route_z +2.41…+2.83, mean−std still > a's +0.89
  upper); **b NEVER clears** (route_z +0.66…+1.04) despite GC(hidden) = **0.999–1.000
  with zero std** (perfect, deterministic raw burn-in). The cleanest possible form of
  the register claim: matching the raw register is *solved exactly* and transfers
  *nothing* to routing.
- **GC(route) for c is ecosystem-grade and RISES with λ:** +0.780 → +0.795 → **+0.847**
  (λ=3.0, std 0.007 — tightest). At strong pull the student exceeds the ecosystem's
  own internal +0.78. route_z peaks at λ=1.0 (+2.83); λ=3.0 best Gram. Best c-cell:
  route_z +2.88 p=**0.0010** GC +0.842.
- **a identical across λ** (lambda-independent, same seeds) = seeding determinism
  sanity check.

**Verdict: CONFIRMED.** Relational loss transfers the combinator function shape ONLY
in the routing register, robustly across seeds and λ, at ecosystem-grade GramCorr
(+0.78–0.85). The b-column (GC(hidden)≈1.0, route null) is also the live proof of the
`holographic-burn-in-learning-rule.md` reference-beam catch: naive raw burn-in =
a perfect hologram of the common mode, zero function.

### Artifacts (s223)
`scripts/experiments/relational_loss_distillation.py` (ruff-clean, smoke-validated,
`--sweep` mode); `results/relational-loss-distillation/verdict_run.json`
(+ `verdict_smoke.json`; `verdict_sweep.json` pending the running sweep);
`/tmp/relational_loss_distillation.log`, `/tmp/rld_sweep.log`.

## Open leads (declare register first)

1. **WHNF acceptance gate** (register: functional) — add an outer-recurrence to the
   student so Δx is measurable; require Δx→0 on combinator probes as the accept gate
   (the Exp B discipline). Currently an IOU.
2. **Map/fold composition geometry** (register: topological/routing) — target the
   `map = B(C B)(C B)` *composition* direction (built from the measured B,C
   centroids) rather than per-combinator centroids alone; does relational loss
   transfer a composition, not just the atoms?
3. **Tokens-to-transfer curve** — sweep λ and corpus size; quantify the leverage of
   compiler-minted curriculum vs plain CE.
4. **Distributed test** — N students to one shared teacher Gram → are their routing
   deltas foldable with a *guaranteed* Procrustes alignment (the §distributed claim)?

## Files

| File | Content |
|------|---------|
| `scripts/experiments/relational_loss_distillation.py` | s223 first experiment: tiny student, 3 conditions (CE / CE+raw-Gram / CE+route-Gram), silhouette+GramCorr verdict |
| `results/relational-loss-distillation/` | per-condition verdict json |
| `results/combinator-relationship-map/Qwen_Qwen3-14B.npz` | teacher targets: `gram_route_cmr_L12` (hypothesis), `gram_hidden_cmr` (control) |
