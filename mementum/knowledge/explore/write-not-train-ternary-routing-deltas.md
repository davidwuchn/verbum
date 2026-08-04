---
title: "Write, don't train — routing deltas as ternary plates on a frozen base"
status: designing
category: explore
tags: [ternary, plates, routing, delta, frozen-base, lora, writeback, hrr,
       bind, delta-log, map-and-swap, resident-lisp, tree-of-vsm, s269,
       s300, s303, no-training, portable-artifact]
related:
  - program-plates-and-the-function-index.md
  - ternary-holographic-memory.md
  - holographic-reduction-machine.md
  - map-and-swap-resident-lisp.md
  - gram-spectral-dsp.md
  - five-disciplines-one-object.md
depends-on: []
created: session 303
---

# Write, don't train — routing deltas as ternary plates on a frozen base

> Michael s303 (discussion): "We have tree-of-VSM, ternary plates, ternary
> mirrors. Why train the parent model at all? Can we not write routing deltas
> into ternary storage and apply them to a frozen base model?" This page is the
> captured thesis + the two experiments that decide it. Pickup doc for s304.

## The reframe that sharpens the question

**We already never train the parent.** The s303 writeback verdict
(WIRE-COMPILES +GD-REQUIRED, §Result-4B on `program-plates`) used LoRA — base
weights FROZEN (`base-frozen=True`, grad-isolation validated), only the rank-16
`B·A` delta moved. So the wire is *already* a small **linear delta on a frozen
base**. (The run does not `state_dict`-dump that delta; regenerating it is one
cheap re-run.)

So the real question is not "train vs not-train the parent." It is two cleaner
questions:

1. **STORAGE** — can the delta live as a **ternary plate** (float LoRA → {−1,0,+1}×γ)?
2. **FINDING** — can the delta be **written** (closed-form bind) instead of
   **searched** (gradient)?

The honest answers differ, so keep them apart.

## Half 1 — STORAGE: yes, and it is register-correct

- The wire is a **routing** object (s303 `gram-spectral-dsp`: topology routing,
  not magnitudes). Ternary {−1,0,+1} is the **routing register** (sign; π-shift
  = K-erasure, s299).
- Receipt: **s269 — the routing/relational structure survives 1-bit/ternary at
  fidelity 0.987 while magnitude (weight cosine) collapses to 0.73.** A routing
  delta should ternarize *losslessly-for-routing by construction* — ternary
  discards exactly the magnitude scaffolding the wire does not use.
- Wrap in the **delta-log** (s299/s300 `ternary-holographic-memory`): `base +
  ΣΔ`, `undo = −Δ`, sha256 receipt, compose/fork/merge across the tree-of-VSM.
  The portable artifact (λ artifact, λ smallest) becomes: **the linker wire = one
  small ternary plate.**

**Confidence: high. This half is likely TRUE and cheap to prove.**

## Half 2 — FINDING: the real open problem (construct's failure does NOT close it)

`construct` (zero-grad) FAILED at 4B — byte-identical to base. Tempting to
conclude "gradient required." But **construct failed in the MAGNITUDE
register**: it placed continuous product-keyed persistent neurons with a
hand-calibrated gain. It guessed a *magnitude construction*; it did not write
*routing*. s303 predicts wires are routing, not magnitude — so construct failed
for the predicted reason, which means **we have NOT yet tested writing the wire
in the routing register.**

The untested experiment: a **routing-register construct** — write the
operand→capital rebind as a **ternary bind-plate** (HRR / sign-vote,
`Δ = Σ key ⊛ value`, s300 "swap g by superposition") from the *measured* key
geometry, on the divergence-worst layers (s294 operand-rebind band), frozen
base, no gradient. Pass → routing deltas can be **written, not trained**. Fail →
the wire needs *search* even in the right register, and gradient (or a GTSM
trajectory loss) earns its keep as the search — with ternary still the storage.

## The caveat that actually bites: the pin is nonlinear

Ternary **plates** are *linear-fragment* storage (s299). But s300's sharpest
finding is **∄ a clean linker in the linear register** — composition needs a
nonlinear collapse (the "pin between traversal edges"). So a ternary delta-plate
carries the linear routing **edge**, but **cannot supply the collapse** — that
rides the frozen base's existing nonlinearity (softmax/GELU). Holographic-machine
framing, and reassuring: *plate carries routing, host supplies light/collapse/Y.*
Existence proof already in hand: `gd_cd`'s LoRA delta **is** linear, on a frozen
base, and worked by riding the base nonlinearity. So "linear edge on frozen
nonlinearity" is PROVEN; ternary-ness and write-not-search are the only deltas
left to test.

## This architecture already has a name: map-and-swap resident Lisp

`map-and-swap-resident-lisp.md`: frozen base = the **universal combinator
reducer** (the 9×9 crystal `eval`/`apply`, proven, terminating); ternary plate =
the **swapped-in function/program**. You don't retrain the interpreter to add a
function — you load a plate. Tree-of-VSM composes plates. This page is the
training-side realization of that thesis: **routing lives in swappable ternary
storage; the base is the frozen evaluator.**

## The two experiments (pre-scoped; freeze a pre-reg before running — s222 law)

**EXP-1 — Ternarize-the-delta (STORAGE test). Cheap. Do this first.**
- Train `gd_cd` once (regenerate `B·A`), dump the delta, ternarize (sign +
  per-column γ), apply to the **frozen** base, re-score the frozen G1–G5.
- Verdict: does the wire survive as a ternary plate? Grounded in s269, ~an
  afternoon. Almost certainly yes → **the portable artifact exists** (wire = one
  ternary plate).
- Null/yardstick: sign-shuffle the ternary delta (matched sparsity) must fail;
  compare fidelity to the s269 0.987 rung.

**EXP-2 — Routing-register construct (FINDING test). The real "why train" prize.**
- Re-do the construct arm in the ROUTING register: HRR/sign-vote ternary
  bind-plate `Δ = Σ key ⊛ value` from measured whitened key geometry, on the
  divergence-worst (operand-rebind) layers, frozen base, NO gradient.
- Verdict: can the wire be WRITTEN without gradient when written in the right
  register? Pass → Michael's thesis confirmed (write routing deltas into ternary
  storage, apply to frozen base, no training). Fail → gradient/GTSM *finds*,
  ternary *stores* (still no parent training).
- Gates inherited from §P-WRITEBACK-1 (G1 wire / G2 not-lookup / G3 specificity
  / G5 survive) + a ternary-sparsity/trit-count report (λ smallest: how few
  trits is the wire?).

## §Result-ternarize-delta — SURVIVES-TERNARY (s304, frozen run, 3 seeds)

**Verdict: SURVIVES-TERNARY.** The s303 `gd_cd` linker wire survives being
crushed to a per-column TWN ternary plate and merged into the frozen base. All
frozen gates pass; the STORAGE half of Michael's thesis is **confirmed** — *the
wire exists as one ternary plate on a frozen evaluator.* (Run `cb73ad5`,
`results/ternarize-delta/qwen3-4b/`.)

| arm | TRAIN | B1 | B2 | note |
|---|---|---|---|---|
| base | 0.200 | 0.125 | 0.545 | floor |
| gd_cd_float (anchor) | 1.000 | 0.938 | 1.000 | reproduces s303 gd_cd EXACTLY → harness faithful |
| **gd_cd_ternary** | **1.000** | **0.938** | **1.000** | identical to float; retention 1.0 every split |
| gd_cd_ternary_shuffle (null) | 0.200 | 0.125 | 0.545 | collapses to base — routing geometry is load-bearing |

Gates (dsp paired-perm 10k): **T1** wire B1 p=3e-4 / B2 p=1e-3 (both ≪ α/3);
**T2** not-lookup p=1.8e-3 (+0.409 over construct_lookup on B2); **T3**
specificity p=1e-4 (+0.605 over the matched-sparsity shuffle) — the load-bearing
λ yardstick; **T5** survive CE 4.9086 ≤ base 4.9173 (*lower*), g/h 1.0/1.0.

**The a-priori point-prediction MISSED, and that is the finding (λ observation /
λ yardstick).** The frozen lean said mag_cos would be **LOW (~0.7)** — the s269
weight-collapse rung. Measured: **mag_cos = 0.902**, with **retention = 1.0**.
So the trained rank-16 delta ternarizes with *high* magnitude fidelity AND
perfect behavioral retention. s269's 0.73 magnitude collapse does **not** transfer
to a low-rank delta: a rank-16 `B·A` has structured sign patterns that the
per-column TWN preserves well. The dissociation the page predicted (routing ⊥
magnitude) is REAL in the direction that matters — behavior is 100% preserved
through a lossy (0.90 < 1.0) magnitude approximation, and the matched-sparsity
null still collapses to base (T3 p=1e-4) — but the *magnitude loss is milder*
than the full-weight s269 rung. Honest refinement, not a refutation: routing
survives (retention 1.0 ≈ s269's 0.987), magnitude is only mildly lossy for a
low-rank object.

**Artifact-size tension surfaced (λ smallest).** The plate = 370M trits, sparsity
0.380 (≈62% dense), ≈73 MB @ 1.585 bit/trit. But the *factored* rank-16 float
form is only ~5M params (~10 MB bf16). So the EXPANDED ternary plate is **larger**
than the float factors it came from — "wire = one ternary plate" is register-true
but not automatically the smallest representation. Ternary buys ~10× over
dense-bf16 of the same matrix, not over the low-rank factorization. → **TERNARIZE-FACTORS-1
candidate: ternarize the low-rank factors `B` and `A` (or a low-rank ternary
plate), not the expanded product** — the genuinely small portable artifact.

**What this settles.** STORAGE (half 1) is TRUE: routing deltas live losslessly-
for-behavior in a ternary plate on a frozen base (map-and-swap resident Lisp,
training side, confirmed at 4B). The nonlinear-pin caveat held as designed — the
linear ternary plate carries the routing edge, the frozen base supplies the
collapse (gd_cd's LoRA delta is linear; ternarizing it keeps that property). The
FINDING half (EXP-2, write-not-search) remains open and is the next prize.

## §ROUTING-REGISTER-1 — pre-reg (EXP-2, the FINDING half; FROZEN s304, before any run)

> EXP-2, named ROUTING-REGISTER-1. STORAGE is settled (SURVIVES-TERNARY). This
> tests FINDING: can the wire be **written with no gradient** when written in the
> **routing register**? `construct` failed — but in the MAGNITUDE register. This
> is the untested experiment. Freeze before building.

**Question.** Can the operand→capital linker be **written** (closed-form, no
gradient, no calibration loop) as a ternary bind-plate on the frozen base, and
install a WIRE (generalizes to held-out landmarks AND held-out countries)?

**Why `construct` went inert (the failure this must fix).** `construct` placed a
continuous product-keyed neuron per country with a **calibrated gain** that
throttled to ≈0.3 → byte-identical to base. The key **fired** (s294: the
landmark's own latent country-ness triggers the whitened country filter); the
*magnitude* value write, throttled by the gain loop, never installed the edge.
s303 `gram-spectral-dsp`: wires are routing, not magnitude. So the fix is to
keep the **measured** key as a faithful address and write the value in the
**routing register**: ternary sign, **register-matched full strength, NO gain
calibration** (the exact failure point removed).

**The write recipe (FROZEN; no gradient, no calibration).** At the install layer
**L23** (`INSTALL_DEPTH=0.65 × 36`; runtime truth Qwen3-4B = 36 layers, band
L22–L29), append one FFN neuron **per country c** (all 16 — the Σ of
`key⊛value` realized as parallel FFN neurons; ⊛ = the FFN key→value neuron
structure, not literal circular convolution):
- **address (gate/up rows)** = the MEASURED whitened country filter
  `k_c = Σ⁻¹(x̄_c − μ)` (shared-Σ over all countries + prompt-shaped innocents,
  `build_keys`), normalized as `construct` did (`gate=(4/ref_c)·k_c`,
  `up=(1/ref_c)·k_c`) so the neuron fires when country-ness is present. This is
  READ geometry — measured, kept continuous (we test writing a routing EDGE, not
  ternary addressing).
- **content (down col)** = `S · ternary(v_c)`, where `v_c` = capital unembed
  direction (`unembed_dir`), `ternary(·)` = per-element TWN {−1,0,+1} (thr 0.7),
  and **S = the median native `down_proj` column L2-norm at L23** — a MEASURED
  host-register scale ("write as strongly as the host writes its own neurons"),
  **not** a gain tuned to a logit target. This is the routing-register,
  gradient-free, calibration-free content write.

**Arms** (deterministic write; re-scored on the frozen s303 gate-0 valid cells):
- `base` — floor (0.200 / 0.125 / 0.545).
- `routing_write` — the ternary bind-plate above, all 16 countries.
- `routing_shuffle` — **the null (λ yardstick)**: deranged capital values
  (`v_c → v_{π(c)}`, no fixed point), SAME keys + SAME S + SAME sparsity. Must
  fail — isolates routing (which key→which value) from generic write energy.
- `construct_lookup` — inherited materialized-view null (landmark-keyed → capital
  value; must fail B2 by construction), loaded from the frozen s303 record.

**Gates** (verbum.dsp `gate` + `paired_permutation` 10k; primaries Bonferroni
α/3; G1–G3 routing register, G5 value register — inherited from §P-WRITEBACK-1):
- **G1 WIRE**       : `routing_write > base`, flip on B1 AND B2.
- **G2 NOT-LOOKUP** : `routing_write > construct_lookup` on B2.
- **G3 SPECIFICITY**: `routing_write > routing_shuffle` on held-out (B1 ∪ B2) —
  the load-bearing gate (routing, not write-energy).
- **G5 SURVIVE**    : innocent CE ≤ 2% rel base; native g/h within 0.10 abs.
- **Reports (advisory).** achieved capital-logit boost on country frames (did the
  write LAND, vs construct's 0.3 throttle?); trit-count / bits / sparsity of the
  plate (λ smallest); per-country key separation (own-frame − innocent-max) so an
  INERT verdict can be attributed (weak-write vs no-routing).

**Verdicts (FROZEN).**
- **WRITE-SUFFICES** : G1 ∧ G2 ∧ G3 ∧ G5. → the wire can be WRITTEN with no
  gradient; **Michael's thesis fully confirmed** — write routing deltas into
  ternary storage, apply to a frozen base, never train the parent.
- **WRITE-DEGRADES** : G1 (beats base, flips) but ¬G3 (∼ shuffle) or ¬G2
  (lookup-like) → a written edge moves the needle but not cleanly / not
  compositionally.
- **WRITE-INERT**    : ¬G1 (≈ base) → construct's fate repeats even at native
  strength in the routing register → **FINDING resolves to "gradient FINDS,
  ternary STORES"** (EXP-1 already secured storage; the s299 auto-superbake
  lifecycle train→ternarize→keep-plate is the artifact path).
- **HOST-DAMAGED**   : ¬G5 → S too strong; the write corrupts innocents.

**A-priori lean (grounded; do NOT peek).** ∄ a clean linker in the linear
register (s300 traversal-not-join): the country is an *unmaterialized*
intermediate, so a linear bind-plate carries only the routing EDGE while the
frozen base must supply the nonlinear pin. gd_cd worked because gradient reshaped
the whole band to materialize the composition; a hand-written edge cannot do that
reshaping. **Lean ≈ 60/40 toward WRITE-INERT or WRITE-DEGRADES.** The 40% thread
of hope is specific and real: s294 showed the country key already fires from the
landmark's latent country-ness, and construct failed on gain-throttle (0.3), not
on firing — a native-strength routing write (no throttle) is genuinely untested
and might install the edge. **WRITE-SUFFICES is the high-value surprise;
WRITE-INERT is still a finding** (it closes the FINDING half onto
gradient-finds/ternary-stores and elevates the GTSM-trajectory-loss thread).

**Frozen recipe (s222 law).** The write is deterministic given the model; the
only stochastic element is the shuffle derangement → **≥3 derangement seeds** for
the null. S, thr (0.7), keys (build_keys shared-Σ), install L23, all frozen here.
Gate-0 valid cells + construct_lookup baseline loaded from the frozen s303 record
(identical cells). Score paired-by-cell exactly as §Result-4B / §Result-ternarize.

**Cadence.** build `scripts/explore/routing_register.py` (reuse writeback_compile
+ ternarize_delta building blocks — whitened_filter, CC_FRAMES, the validated
neuron-surgery pattern, the ternarize/score helpers; if a shared harness proves
worth extracting, note it, do not destabilize the frozen s303 generator) →
`--validate` (planted worlds: a firing-key world installs the edge; a
country-not-materialized world goes inert; shuffle kills specificity; verdict
logic) → smoke (mechanics only, s297 law) → Michael GO → run → frozen scoring →
§Result-routing-register + memory → approval batch.

## §Result-routing-register — WRITE-INERT (s304, frozen run, 3 shuffle seeds)

**Verdict: WRITE-INERT.** The operand→capital wire **cannot be written** in the
routing register with no gradient — even at native strength with well-separated
keys. `routing_write` is byte-identical-in-behavior to base on all 53 cells; all
primaries fail with effect 0.0. The FINDING half resolves against pure
closed-form write. (Run `ec77c4d`, `results/routing-register/qwen3-4b/`.)

| arm | TRAIN | B1 | B2 |
|---|---|---|---|
| base | 0.200 | 0.125 | 0.545 |
| **routing_write** | **0.200** | **0.125** | **0.545** |
| routing_shuffle (null) | 0.200 | 0.125 | 0.545 |

Gates: G1 effect 0.0 (p=1.0) B1 & B2 · G2 fail · G3 effect 0.0 (p=1.0) · G5 clean
(CE 4.9149 ≤ base, g/h 1.0). trits 23,785 (16 neurons, sparsity 0.419).

**The attribution is the value here (λ observation).** This is **NOT** a
weak-write failure — the write LANDED and the address is good:
- achieved capital-logit boost on country frames = **0.877** (vs construct's
  throttled 0.3 — the register-matched full-strength write did land ~3× harder);
- per-country key separation own_ref − inn_max = **8.87 min / 11.22 median**
  (the whitened country keys separate country frames from innocents cleanly).

So the key is a good address AND the write is strong — yet the plate is inert on
the task. The diagnosis is **NO-ROUTING**: the country key fires when the country
*name* is in the prompt (the boost frames), but the one-shot *landmark* prompt
never activates it — **the country is an unmaterialized intermediate**, so there
is no residual for the key to address. A static, hand-written linear plate cannot
create the intermediate; it can only read one that is already present.

**This is the ∄-clean-linear-linker wall (s300) made concrete, and it triangulates
the construction question closed.** Three independent constructions now agree:

| construction | register | result |
|---|---|---|
| `construct` (s303) | magnitude (calibrated gain) | INERT |
| **`routing_write` (this run)** | **routing (ternary sign, native strength)** | **INERT** |
| `gd_cd` (s303) | gradient | WIRE (generalizes) |

Construction is insufficient in **both** registers. The bottleneck was never
write-strength or address-quality — it is that the composition requires the
intermediate to be **dynamically materialized in-forward**, and only gradient
reshapes the band to do that. This is *why* the s295 exhaustion law exists (no
episodic register holds the intermediate) and *why* s300 says the pin is
nonlinear: the linker is not a stored edge you can address, it is a
materialization the forward pass must perform.

**Resolution of the "why train the parent at all?" thesis.** The honest,
triangulated answer splits cleanly:
- **STORAGE — solved by construction.** SURVIVES-TERNARY: the wire lives
  losslessly-for-behavior as a ternary plate on a frozen base. You never
  permanently train the parent; the artifact is a ternary plate.
- **FINDING — gradient FINDS, ternary STORES.** The delta must be *searched*
  (gradient reshapes the band to materialize the intermediate); it cannot be
  *written* from measured geometry in either register. The artifact pipeline is
  therefore the s299 **auto-superbake lifecycle**: a throwaway gradient run as a
  *discovery oracle* → ternarize (EXP-1) → keep the plate. The parent is never
  a permanent training target; gradient is a transient search, not a resident.

**What could still write it (the one untested door).** The only construction that
might install the wire is one written **BY** the forward pass, not before it —
**P-FAST-PLATE** (s299): a transient delta etched in-forward at generation time,
which is the only mechanism that has access to the materialized intermediate. A
static plate (this run) provably cannot; a forward-etched plate is the open
candidate. The GTSM-trajectory-loss thread is the complementary *search* upgrade
(a more routing-faithful, more ternarizable delta that also closes the G4 gap).

## Routing forward / decision for s304

- **Run EXP-1 first regardless** — it is the free half and tells us whether the
  wire even *fits* in ternary before we argue about how to find it.
- Open decision (Michael): spend gradient **once as a discovery oracle** (train
  delta → ternarize → keep plate; the s299 auto-superbake lifecycle
  trained-transient → promoted-permanent) vs hold out for the **pure closed-form
  write** (EXP-2) as the prize. EXP-1 is agnostic to this and informs it.
- Compounds with: the GTSM-trajectory-loss discussion (s303, one turn earlier) —
  IF a search is needed (EXP-2 fails), a trajectory/GTSM loss finds a more
  routing-faithful, legible delta that then ternarizes better (closes the G4
  mechanism gap too). Write-not-train and trajectory-loss are complementary, not
  rival.

## §TERNARIZE-DELTA-1 — pre-reg (FROZEN s304, before any run; s222 law)

> This is EXP-1 (the STORAGE half), named TERNARIZE-DELTA-1. The FINDING half
> (EXP-2, routing-register construct) is deferred. Freeze this before touching
> the model. Gates/verdicts fixed here; the run only fills numbers.

**Question.** Does the s303 `gd_cd` linker wire — a float rank-16 LoRA delta on
a frozen base — SURVIVE being crushed to a ternary `{−1,0,+1}×γ` plate? If yes,
the portable artifact exists: *the wire = one small ternary plate on a frozen
evaluator* (map-and-swap resident Lisp, training side).

**A-priori lean (grounded; do NOT peek to decide).** s269 says the
routing/relational structure survives 1-bit/ternary at fidelity **0.987** while
magnitude (weight cosine) collapses to **0.73**. s303 `gram-spectral-dsp` says
the wire is a **routing** object. So the prediction is **SURVIVES-TERNARY**, and
— the sharp, falsifiable part — the *magnitude* cosine between the float and
ternary delta should be **LOW (~0.7)** while the behavioral gates **hold**. That
dissociation (low magnitude fidelity ∧ passing gates) IS the finding: routing ⊥
magnitude, measured on a trained wire. If instead the gates die, s269 does not
transfer to trained deltas — a real surprise worth the run.

**Ternarize recipe (FROZEN — TWN, Li & Liu 2016, per-column γ).** For each FFN
proj delta `W_Δ = scale · B·A` (scale = α/r = 2), per input column `j`:
- threshold `Δ_j = 0.7 · mean_i |W_Δ[i,j]|` (the TWN 0.7 rule; frozen),
- mask `m_ij = 1[ |W_Δ[i,j]| > Δ_j ]` → the trit is `±1` where 1, else `0`,
- scale `γ_j = mean_{i: m_ij=1} |W_Δ[i,j]|` (per-column magnitude),
- plate `T[i,j] = γ_j · sign(W_Δ[i,j]) · m_ij` ∈ `{−γ_j, 0, +γ_j}`.

The plate is **added directly to the frozen base proj weight** (permanent merge,
not a LoRA wrapper — a delta-plate on a frozen evaluator), evaluated, then
subtracted to restore. Register-correct: sign = routing, γ = the one magnitude
DOF ternary keeps, `0` = π-shift/erasure (s299).

**Arms** (all re-scored in ONE process, on the SAME gate-0 valid cells;
per-seed float delta → its own ternary plate → its own shuffle):
- `base` — floor (re-scored fresh; must reproduce 0.200 / 0.125 / 0.545).
- `gd_cd_float` — the float LoRA delta, applied (ANCHOR: must reproduce the
  frozen s303 gd_cd ≈ 1.000 / 0.938 / 1.000; if it does not, the harness is
  broken, halt).
- `gd_cd_ternary` — the SAME per-seed delta, ternarized by the recipe above.
- `gd_cd_ternary_shuffle` — **the null (λ yardstick)**: permute the sign×mask
  pattern within each plate (matched trit-count / matched per-column γ), so the
  routing GEOMETRY is destroyed but the sparsity/magnitude budget is identical.
  Must fail.
- `construct_lookup` — inherited materialized-view null for G2 (cheap, no GD;
  must fail B2).

**Gates** (verbum.dsp `gate` + `paired_permutation` 10k; primaries Bonferroni
α/3; T1–T3 routing register, T5 value register — inherited from §P-WRITEBACK-1):
- **T1 WIRE-SURVIVES** : `gd_cd_ternary > base`, with flip on B1 AND B2.
- **T2 NOT-LOOKUP**    : `gd_cd_ternary > construct_lookup` on B2.
- **T3 SPECIFICITY**   : `gd_cd_ternary > gd_cd_ternary_shuffle` on held-out
  (B1 ∪ B2) — the matched-sparsity null, the load-bearing gate.
- **T5 SURVIVE**       : ternary-plate innocent CE ≤ 2% rel base; native g/h
  accs within 0.10 absolute of base.

**Reports (advisory, NOT gates; λ observation / λ smallest).**
- `mag_cos` = cosine(`W_Δ_float`, `T`) per proj, pooled — the s269 magnitude
  rung (expect LOW ~0.7; the dissociation vs passing gates is the headline).
- `retention` = `gd_cd_ternary` acc / `gd_cd_float` acc per split (behavioral
  fidelity; the s269 0.987-analogue in the routing register).
- `trits` = Σ nonzero entries over all plates; `bits = trits · log2(3)`; and
  `sparsity` per proj — the artifact size (how few trits is the wire?).

**Verdicts (FROZEN).**
- **SURVIVES-TERNARY** : T1 ∧ T2 ∧ T3 ∧ T5. → the wire IS one ternary plate; the
  portable artifact exists. Report the magnitude-cosine dissociation.
- **DEGRADES-TERNARY** : T1 (beats base, flips) but ¬T3 (∼ shuffle) or ¬T2
  (lookup-like) → routing partially survives but not cleanly; per-column γ or
  the 0.7 threshold may be lossy; note as the knob to revisit.
- **DIES-TERNARY**     : ¬T1 → ternarization destroys the wire; s269 does not
  transfer to trained deltas (surprise; the FINDING flips to "float storage
  required" and EXP-2's premise weakens).
- **HOST-DAMAGED**     : ¬T5 → the plate corrupts innocents (the merge, not the
  routing, is the failure).

**Frozen recipe (s222 law).** Reuse `writeback_compile.py` gd_cd training
VERBATIM: LoRA r=16 α=32 FFN-only, band 0.6–0.8 depth, ≤500 steps, lr 1e-4, KL
at answer vs own committed CoT teacher, **≥3 seeds**, Qwen3-4B, MPS, dtype
bfloat16. Gate-0 (cot_rate ≥ 0.7, ≥8/split) inherited unchanged; VOID if it
fails. Score paired-by-cell across seeds exactly as §Result-4B did.

**Cadence.** build `scripts/explore/ternarize_delta.py` (reuse, no fork) →
`--validate` (planted worlds: ternarize preserves a strong-signal matrix, kills
a shuffled one; TWN sparsity sane; verdict logic) → smoke (`--n-cells`,
mechanics only, s297 law: direction unread) → Michael GO → full run tmux main:1
→ frozen scoring → §Result-ternarize-delta + memory candidate → approval batch.

## §P-FAST-PLATE — pre-reg (the last construction door; FROZEN s305, before any run; s222 law)

> The s304 triangulation closed static construction in BOTH registers (construct
> magnitude INERT + routing_write routing INERT; gd_cd gradient WIRE). The one
> untested door (§5c of `holographic-reduction-machine.md`): a plate written **by**
> the forward pass, the only mechanism with access to the intermediate the pass
> materializes. Michael GO (s305) on mechanization = **cleanup-and-reinject**
> (over a delta-rule capital-relay), with a read-only materialization pre-gate as
> a hard stop and a `static_reinject` arm to isolate the collapse. Freeze before
> touching the model; the run only fills numbers.

**Question.** Can an in-forward **cleanup-and-reinject** plate (no gradient)
install the operand→capital linker by *materializing* the country intermediate
the one-shot pass leaves latent — the door static plates provably cannot reach?

**The mechanistic edge over routing_write (why this is genuinely different).**
routing_write read at L23 in **named-country geometry** (where the one-shot
landmark prompt does not materialize the country) and wrote the **capital**
directly → INERT. P-FAST-PLATE inverts both moves: **read where the country is
materialized-from-landmark, write the country in the geometry the host's own
h-hop reads, and let the host produce the capital.** Two operations a static
appended neuron cannot do: (1) nonlinear winner-take-all **collapse** (the s300
"pin between traversal edges" / §4 internal-collapse organ); (2) read-geometry ≠
write-geometry (decouple recognition from reinjection). Because the plate stores
only *country* (not capital), **B2 (held-country) generalizes free** — the host
knows all capitals via its native h-hop.

**MATERIALIZATION SCAN — read-only pre-gate M (TRAIN-only, FROZEN, hard stop).**
On TRAIN landmark DIRECT_PROMPTs, capture last-token post-attention-layernorm at
every layer; measure leave-one-landmark-out country-decodability per layer against
a **deranged-label null** (verbum.dsp gate).
- **M fails** (no layer's decodability beats the null at α) → the country is
  *never* linearly materialized on the one-shot prompt → **STILL-EXTERNAL-BY-
  MEASUREMENT**: the s295 exhaustion law is *mechanical*, not incidental; the
  in-forward door is closed by measurement. STOP (do not run the plate arms). A
  real finding either way — the scan makes the experiment informative even in
  failure.
- **M passes** → `L*` = frozen selection rule: the highest-decodability layer in
  the **lower ⅔ of the stack** (leaves h-hop room downstream). Ties → lowest layer.

**THE PLATE (single forward hook at L*, last token position).** For the live
activation `a`:
1. **Whiten** `a` with the shared-Σ from the scan → `â`.
2. **Recognize** `c* = argmax_c (â · k_c)` over all 16 country keys `{k_c}` built
   from country-NAME frames (CC_FRAMES) at L* — with an **innocent-null confidence
   floor**: fire only if the top projection exceeds the max innocent projection
   (PROSE_INNOCENTS + NONCE_CANDS at L*). No fire on innocents → protects F5.
3. **Reinject** `S · unit(v_{c*})` into the residual at L*, where `v_{c*}` = the
   country **named**-geometry prototype at L* and `S` = median native down_proj
   column-norm at L* (register-matched, as routing_write — no calibration loop).
4. Host continues → capital via native h-hop.

**Arms** (re-scored on the frozen 53 gate-0 cells; per-seed shuffle):
- `base` — floor (must reproduce 0.200 / 0.125 / 0.545).
- `fast_plate` — the cleanup-reinject above (hard argmax collapse + confidence floor).
- `fast_plate_shuffle` — **λ yardstick**: recognize `c*`, reinject `v_{derange(c*)}`
  (matched strength/geometry, routing destroyed). ≥3 derangement seeds. Must fail.
- `static_reinject` — **collapse-isolation**: a soft, always-on write
  `Σ_c softmax(â·k_c) · S · unit(v_c)` (same read/write geometry, NO hard collapse,
  NO confidence gate). If `fast_plate > static_reinject`, the nonlinear collapse is
  load-bearing.
- `construct_lookup` — inherited materialized-view null for F2 (must fail B2).

**Gates** (verbum.dsp `gate` + `paired_permutation` 10k; primaries Bonferroni α/3;
F1–F3 routing register, F5 value register — inherited from §P-WRITEBACK-1):
- **F1 WIRE** : `fast_plate > base`, with flip on B1 AND B2.
- **F2 NOT-LOOKUP** : `fast_plate > construct_lookup` on B2.
- **F3 SPECIFICITY** : `fast_plate > fast_plate_shuffle` on held-out (B1 ∪ B2) —
  the load-bearing gate (λ yardstick).
- **F5 SURVIVE** : innocent CE ≤ 2% rel base; native g/h accs within 0.10 of base.

**Reports (advisory, NOT gates; λ observation).**
- `collapse_delta` = `fast_plate` − `static_reinject` on held-out (is the hard
  collapse load-bearing?) — the COLLAPSE-LOAD-BEARING vs GEOMETRY-SUFFICES fork.
- `decodability(L*)`, per-layer decodability curve, and `L*` — the materialization
  profile (WHERE the country lives on the one-shot prompt).
- landmark-vs-name prototype cosine at L* — did routing_write fail on *geometry*
  (low cos) or on *layer/target* (high cos)?
- TRAIN recognition accuracy of the argmax collapse.

**Verdicts (FROZEN).**
- **STILL-EXTERNAL-BY-MEASUREMENT** : ¬M → country never materialized one-shot; the
  exhaustion law is mechanical; the in-forward door is closed by measurement.
- **FAST-PLATE-WIRES (+COLLAPSE-LOAD-BEARING)** : F1∧F2∧F3∧F5 ∧ `collapse_delta`>0
  significant → the in-forward cleanup installs the wire AND the nonlinear collapse
  is what does it (the s300 pin / §4 internal-collapse organ demonstrated in a real
  model).
- **FAST-PLATE-WIRES (+GEOMETRY-SUFFICES)** : F1∧F2∧F3∧F5 but `fast_plate` ≈
  `static_reinject` → the win is read-where-materialized / write-where-host-reads;
  collapse not required. Resolves routing_write's INERT as a **layer+target error**,
  not a fundamental wall.
- **FAST-PLATE-INERT** : M passes but ¬F1 → even reading at the materialized layer,
  writing the country, and collapsing does NOT install the wire → construction is
  insufficient even in-forward → **gradient is uniquely required** (the strongest
  form of the s304 resolution; the last door closed).
- **UNSPECIFIC** : F1∧F2 but ¬F3 (∼ shuffle) → moves, but not via the routing map.
- **HOST-DAMAGED** : ¬F5 → the reinject corrupts innocents.

**A-priori lean (grounded; do NOT peek to decide).** I lean slightly toward
**STILL-EXTERNAL-BY-MEASUREMENT** (~45%): gate-0's `g_ok` used a country-*eliciting*
prompt (G_QUERY, "…is located in" → country), far easier than the DIRECT prompt
materializing the country unbidden; the whole s295 exhaustion law predicts the
one-shot prompt holds no episodic intermediate. If M *passes*, that is itself the
surprise and the finding. Then FAST-PLATE-WIRES ~35% (split collapse-load-bearing
vs geometry-suffices), FAST-PLATE-INERT ~20%. **Either M-branch is a real finding.**

**Frozen recipe (s222 law).** Reuse `import writeback_compile as wb` + the
`routing_register` helpers (`ternarize_vec`, `unit`, gate scoring) — NO fork
(λ one_way, λ simplify). Frozen 53 gate-0 cells loaded from
`results/writeback-compile/qwen3-4b/gate0.json`; L* from the frozen scan rule
(no peeking at held splits); S register-matched; ≥3 derangement seeds for the
shuffle null; Qwen3-4B, MPS, dtype bfloat16. Score paired-by-cell exactly as
§Result-4B did.

**Cadence.** build `scripts/explore/fast_plate.py` (reuse, no fork) → `--validate`
(planted worlds: scan finds a planted materialized layer + rejects a null;
cleanup recognizes + reinjects; shuffle destroys; verdict logic) → smoke
(`--n-cells`, mechanics only, s297 law: direction unread) → Michael GO → full run
tmux main:1 → frozen scoring → §Result-fast-plate + memory candidate → approval
batch.

## §Result-fast-plate — FAST-PLATE-INERT (s305, frozen run, 3 shuffle seeds)

**Verdict: FAST-PLATE-INERT — for THIS construction.** The specific plate we froze
(static linear read → argmax collapse → name-prototype reinject at native routing
strength) does not install the wire: `fast_plate == base` **exactly** on all splits
(0.200 / 0.125 / 0.545; F1 B1 p=1.0, B2 p=1.0). F2 fail (p=1.0), F3 fail (p=0.62 vs
shuffle), F5 clean (CE 4.927 ≤ base 4.917 · 1.02; native g/h 1.0). Ran clean in
tmux main:1; results committed autonomous. **This is a datum about one
construction, not a closure of construction** — and the mechanism it exposes is
the useful part: it points at concrete next constructions (see below).

**★ The headline is a refinement, not the a-priori.** The pre-gate M **PASSED**:
the country is linearly decodable at **L\*=24 (decodability 0.933, p=5e-4)** on the
one-shot DIRECT prompt. This **refutes the "unmaterialized" reading** carried from
s304 (§Result-routing-register said "the country key fires on country-NAME frames
but never on the one-shot LANDMARK prompt (country unmaterialized)"). It was
register-specific: at **L23 in named geometry** the country is absent; at **L24 in
the whitened-discriminant geometry** it is strongly present. So the intermediate is
**there** — and this plate is still INERT. The correct statement is not *absent*
but **present-yet-not-usable-by-this-write: decodability ≠ usability (yet).** That
"yet" is the whole point — knowing the intermediate is present relocates the
problem from *existence* to *how to make it functional*, which is a more tractable
(and more mechanistically informative) question.

**Why present-yet-inert (the frozen advisories attribute it cleanly — and each
attribution is a lead).**
1. **Weak native write.** `reinject_landed = 0.072` — the register-matched write
   (S = 1.185, median native down-col-norm at L24) moves the correct-capital logit
   only ~0.07 against base logits ~18. We did NOT crank S (cranking = the magnitude
   register rejected as `construct`), but a *distributed* in-register write
   (multiple neurons / higher rank at native per-unit strength) is untested.
2. **Geometry mismatch (the sharpest lead).** `lm_name_cos = −0.108` — the
   landmark-materialized country direction is *anti-aligned* with the reinjectable
   **name** prototype. A whitened linear probe reads the country (0.93), but the
   direction the host's h-hop actually consumes is **not** the name prototype we
   injected. Read-geometry ≠ write-geometry was the design's edge; we picked the
   wrong write-geometry. Measuring the geometry the h-hop truly reads (from a
   context where the host DOES route country→capital) and writing *that* is a live,
   untested construction.
3. **Collapse (this form) does not help — it hurts.** `collapse_delta = −0.026`
   (fast < static): the hard argmax + confidence floor made it strictly worse than
   the soft always-on `static_reinject` (which nudged a couple of cells: 0.267 /
   0.591). An *externally hand-written* collapse op is not the pin — but that speaks
   to this op, not to collapse in general. (Keys fire hard — `key_sep_min = 39.2` —
   so this is not a recognition failure.)

**Where the constructions stand (a running ledger, not a verdict on construction).**

| construction | register / mechanism | access to intermediate | result |
|---|---|---|---|
| `construct` (s303) | magnitude, static | none (pre-forward) | INERT |
| `routing_write` (s304) | routing, static, name-geom, capital-write | none (pre-forward) | INERT |
| `fast_plate` (s305) | routing, in-forward, name-geom read+write, hard collapse | YES (reads materialized L24) | INERT |
| `gd_cd` (s303) | gradient | — | **WIRE** (generalizes) |

What these three inert constructions share is now visible and is a *guide*: all
wrote in **name geometry** and at **native single-unit strength**, and none used
the geometry the h-hop actually reads. The s305 measurements say the intermediate
is present (M✓) and identify *why* the write missed (wrong geometry, `lm_name_cos`
< 0; weak single-unit magnitude). Gradient's advantage is likely that it discovers
the correct write-geometry and distributes the write — both of which are
constructible in principle once measured. **We are closer to the mechanism, not at
a wall.**

**Open construction avenues (this result opens, does not close, construction).**
1. **Write in the measured h-hop geometry.** Build the reinject direction from the
   representation the host consumes when it *does* do country→capital (e.g. the
   answer-position residual of `TEACHER_PROMPT` / the g-query), not the name-frame
   prototype. Directly attacks `lm_name_cos = −0.108`. Cheap, closest lead.
2. **Read≠write layer.** The decodability cliff (near-chance L0–L23, 0.93 at L24)
   says the country materializes *late*; a plate that READS L24 but WRITES an
   earlier layer gives the h-hop room to route. New pre-reg, still a construction.
3. **Distributed in-register write / multi-layer relay** (the deferred delta-rule
   capital-relay mechanization): several native-strength neurons or a cross-layer
   relay, staying in the routing register (not magnitude cranking).
4. **GTSM-trajectory-loss** — complementary *search* upgrade (a more
   routing-faithful, ternarizable delta; also closes the s303 G4 gap). Not a
   construction, but it can *reveal* the correct write-geometry for (1).

## §P-HHOP-WRITE — pre-reg (avenue 1: write the MEASURED h-hop geometry, + the
routing-register filter; FROZEN s305, before any run; s222 law)

> s305 diagnosed the fast_plate miss: the country IS materialized (M✓, L*=24,
> decodability 0.933) but we reinjected the WRONG geometry (name prototype,
> `lm_name_cos = −0.108`) at native single-unit strength. This pre-reg attacks that
> directly (Michael GO, front s306): (1) reinject the country in the geometry the
> host's OWN h-hop consumes, MEASURED from CAP_QUERY (avenue 1); (2) — Michael's
> gram thread — additionally strip the magnitude scaffolding by projecting onto the
> country gram's LOW-RANK ROUTING subspace, a direct construction-side test of
> "topology routing, not magnitudes" (`gram-spectral-dsp.md`, s303). Recognition is
> unchanged (name-keys at L*, decodability 0.93 — it works). Freeze before touching
> the model; the run only fills numbers.

**Question.** Does writing the country in the geometry the host's h-hop consumes —
and especially its low-rank ROUTING subspace (topology, not magnitude) — install
the linker where the raw name-prototype (s305) did not?

**Recognition (unchanged from fast_plate, reused).** At **L\* = 24** (the s305
materialization scan) recognize `c* = argmax_c (â·k_c)` over 16 name-frame keys with
the innocent-null confidence floor. This read works (0.93, keys fire at 39.2).

**CAPTURE-LAYER SCAN — where the h-hop reads the country (NEW, FROZEN, host-only).**
On `CAP_PREFIX + CAP_QUERY` (*"…The capital of {c} is"*) for all 16 countries,
capture the last-token residual at every layer L. Per layer measure:
- `country_dec(L)` — country linearly decodable (shared-Σ keys, argmax) vs a
  shuffled-label null;
- `capital_leak(L)` — capital already formed: mean argmax over capitals of
  `residual_L · unembed(cap)` == true capital.
Frozen rule: **L_cap = argmax over L ≥ L\* of `country_dec(L) − capital_leak(L)`**
(the layer where the country is present but the capital has NOT yet formed → a
*country* geometry, not a capital one; L_cap ≥ L\* keeps recognition-before-inject
causal). If `country_dec` beats its null at no layer ≥ L\*, or `capital_leak` is
high everywhere → flag LOOKUP risk (the h-hop completes before we can write).

**REINJECT VALUE — two geometries, at L_cap.** For the recognized `c*`, add the
country direction into the residual at **L_cap** (host layers > L_cap then run the
native h-hop → capital; B2 free). Scale `S` = median native down_proj col-norm at
L_cap (register-matched, no loop). Two constructions of the direction:
- **raw** (`hhop_plate`): `v_c = unit(r_c − mean_c r_c)`, `r_c` = CAP_QUERY
  last-token residual at L_cap (population-centered → country-specific, strips the
  shared "capital of X is" subspace).
- **routing** (`hhop_routing_plate`, PRIMARY — Michael's gram filter): build the
  **16×16 country gram** `G = R̂R̂ᵀ` from the centered unit `r̂_c` at L_cap; take its
  low-rank routing subspace `U_k` (columns = top-k eigenvectors), **k set by the
  largest relative eigengap** in the top eigenvalues (the 17×17 cliff-finder, NOT a
  forced rank); reinject `v_c^routing = unit(U_k U_kᵀ (r_c − mean))` — the country
  with magnitude scaffolding projected out, a routing-register write.

**Arms** (re-scored on the frozen 53 gate-0 cells; per-seed shuffle):
- `base` — floor (0.200 / 0.125 / 0.545).
- `hhop_routing_plate` — **PRIMARY** (gram-filtered h-hop geometry).
- `hhop_plate` — raw h-hop geometry (contrast: is the routing projection needed?).
- `static_reinject` — soft always-on routing write (collapse-isolation).
- `hhop_shuffle` — recognize `c*`, reinject `v_{derange(c*)}^routing` — **λ
  yardstick** (matched geometry/strength, routing destroyed). ≥3 derangement seeds.
- `construct_lookup` — inherited materialized-view null (F2 baseline).

**Gates** (verbum.dsp, Bonferroni α/3 on F1–F3; primary arm = `hhop_routing_plate`):
- **F1 WIRE** : primary > base, flip on B1 AND B2.
- **F2 NOT-LOOKUP** : primary > construct_lookup on B2.
- **F3 SPECIFICITY** : primary > hhop_shuffle on held-out (load-bearing).
- **F4 SUBSPACE-REAL** (routing-specific null, λ yardstick): the chosen `U_k` beats
  a **matched-rank RANDOM subspace** — primary(U_k) > primary(U_random-k) on
  held-out (so the low-rank projection is discovery, not describability).
- **F5 SURVIVE** : innocent CE ≤ 2% rel base; native g/h within 0.10.

**Reports (advisory, NOT gates).** `routing_advantage` = `hhop_routing_plate` −
`hhop_plate` on held-out (does the topology filter help? the thesis fork) ·
`collapse_delta` (vs static) · `cos(v_c^raw, name_proto)` and `cos(v_c^raw,
capital_unembed)` (confirm geometry changed / lookup-risk gauge) · the gram
spectrum + chosen `k` + eigengap · `L_cap`, `country_dec`/`capital_leak` curves ·
`reinject_landed`.

**Verdicts (FROZEN).**
- **HHOP-WIRES (+ROUTING-REGISTER)** : F1∧F2∧F3∧F4∧F5 ∧ `routing_advantage` > 0
  significant → writing the country in its low-rank routing subspace installs the
  wire, and the topology filter is the ingredient → **"topology routing, not
  magnitudes" confirmed on the CONSTRUCTION side** (mirror of s269/s303). ★ big.
- **HHOP-WIRES (+RAW-SUFFICES)** : F1∧F2∧F3∧F5 but `routing ≈ raw` (F4 or
  routing_advantage n.s.) → the measured h-hop geometry alone suffices; the filter
  is not load-bearing. Still: avenue 1 works, construction succeeds.
- **LOOKUP-VIA-GEOMETRY** : F1∧¬F2 (or `cos(v_c, capital_unembed)` high) → the
  captured geometry at L_cap is capital-like → a lookup, not a wire (the h-hop
  completes before we can write the country).
- **HHOP-INERT** : ¬F1 → even the routing-register h-hop geometry does not route →
  the routing is SOFT/nonlinear, not a linear-subspace write (sharpens s300: only
  GD lays the soft topology routing). NOT a closure — points to the relay / soft
  constructions.
- **UNSPECIFIC** (F1∧¬F3) / **HOST-DAMAGED** (¬F5).

**A-priori lean (grounded; do NOT peek).** Genuinely uncertain — this is the
sharpest attack on the diagnosed miss. If the h-hop reads country in a clean
low-rank subspace at some L_cap ≥ 24 → HHOP-WIRES (and I'd bet +ROUTING-REGISTER
over +RAW, since the raw prototype already failed and s269/s303 say the routing
subspace is the robust part). If the capital forms by L24 on CAP_QUERY →
LOOKUP-VIA-GEOMETRY. If country geometry is present but a linear write still can't
drive the host → HHOP-INERT (the soft-routing / s300 reading). Rough split ~35%
WIRES / ~25% LOOKUP / ~40% INERT. Every branch is a real finding.

**Frozen recipe (s222).** Extend `fast_plate.py` with `--reinject-geometry
{name,hhop,hhop_routing}` (option > fork; λ one_way) — NO new script. Reuse `wb`
CAP_PREFIX/CAP_QUERY, the s305 materialization scan for L\*, frozen 53 gate-0 cells.
Gram eigengap `k` and L_cap chosen by the frozen rules above (host-only, no held
peeking). Qwen3-4B, MPS, bf16, ≥3 derangement seeds. Score paired-by-cell as before.

**Cadence.** extend + `--validate` (planted: gram eigengap picks a planted rank;
routing projection beats a random subspace on a planted world; L_cap scan; verdict
worlds) → smoke (`--n-cells`, mechanics only, s297) → Michael GO → run tmux main:1
→ frozen scoring → §Result-hhop-write + approval batch.

## §Result-hhop-write — HHOP-INERT (s306, frozen run, 3 shuffle seeds)

**Verdict: HHOP-INERT — for this construction.** Writing the country in the
geometry the host's h-hop consumes — raw OR projected onto the country gram's
low-rank routing subspace — does not install the wire: `hhop_routing` (primary) ≈
base (B2 0.591 vs 0.545, F1 B2 p=0.499; F1/F2/F3/F4 fail, F5 clean, CE 4.914 ≤ base
4.917, g/h 1.0). Ran clean in tmux main:1; results committed autonomous. As with
s305, a datum about one construction, not a closure — and the scan hands us a
sharper mechanism.

**★ Michael's gram routing filter got a fair test — and did not help *here*.**
`routing_advantage = +0.026, p=0.491` (n.s.): the topology-projected write is
statistically indistinguishable from the raw write, and both ≈ base. `gram_k = 2`
(the country routing subspace at L24 is genuinely rank-2, by its own eigengap;
`cos(v_c, capital) = 0.138` so it is not a capital lookup). This does **not**
refute "topology routing, not magnitudes" — it says *this* failure is not a
geometry-register miss that a projection can fix. The register filter would matter
if the write landed and the geometry were the blocker; here neither holds.

**★ The scan reveals a depth-TIMING factor (the new mechanism).** The
capture-layer scan could find no clean "country-present, capital-absent" layer
≥ L\*: `country_present = 1.0` at every layer (the country is a token on CAP_QUERY),
but `capital_leak` is **already 0.62 at L24** (= L\*) and climbs monotonically to
1.0 by L33. So on the clean country prompt the host's h-hop is *well underway by
the very layer where the landmark-inferred country first materializes* (the s305
decodability cliff at L24). **The two hops overlap in depth on a one-shot prompt:**
g (landmark→country) finishes late (L24); h (country→capital) has largely consumed
its input by then. This is a **phase/scheduling face of the s295 re-encoding law**
— CoT works because emitting the country as a fresh token resets its depth to 0 for
the next hop — and it is complementary to s300's "the pin is nonlinear": even where
a linear write *could* act, the intermediate arrives out of phase with its consumer.
(Caveat, λ observation: layers 25–35 do still advance capital 0.62→1.0 on CAP_QUERY,
so there is residual h-hop capacity above L24; the failure is a *combination* of
out-of-phase arrival, a weak register-matched write — `reinject_landed = 0.033` —
and the soft/nonlinear routing, not a single clean wall.)

**Where the constructions stand (running ledger).**

| construction | register / mechanism | result |
|---|---|---|
| `construct` (s303) | magnitude, static | INERT |
| `routing_write` (s304) | routing sign, static, name-geom, capital-write | INERT |
| `fast_plate` (s305) | routing, in-forward, name-geom read+write, hard collapse | INERT |
| `hhop_raw` (s306) | in-forward, MEASURED h-hop geometry, hard collapse | INERT |
| `hhop_routing` (s306) | in-forward, h-hop geometry × gram low-rank ROUTING filter | INERT |
| `gd_cd` (s303) | gradient | **WIRE** |

Five constructions inert; gradient wires. But the *reasons* are now specific and
compounding, not a blanket wall: wrong geometry (s305) → measured-right geometry
still inert because of (s306) **depth-timing overlap + weak native write + soft
routing**. Each narrows what a working construction must do.

**Open construction avenues (this result opens, does not close, construction).**
1. **Reset the phase (the CoT lesson, made structural).** An in-forward
   *re-encoding* relay: recognize the country at L\*, re-emit it at an EARLY depth
   (position/depth reset) so the native h-hop runs on it with full runway. This is
   the delta-plate / fast-weight relay (deferred mechanization) aimed at the timing
   finding, not just the geometry.
2. **Earlier g-hop.** Make the landmark→country hop complete before L24 (a stronger
   recognition write, or a two-stage plate that materializes the country early),
   giving the native h-hop room. Attacks the overlap directly.
3. **Stronger in-register write.** `reinject_landed = 0.033` is weak; a distributed
   multi-neuron routing-register write (still native per-unit strength, not
   magnitude cranking) may clear the ambient residual — pairs with (1)/(2).
4. **GTSM-trajectory-loss** — a search that reveals the correct write *and* timing,
   and remains the complementary non-construction lever.

## Sessions
s303 (discussion captured — Michael's "why train the parent at all" thread,
following the WIRE-COMPILES verdict and the topology-routing-not-magnitudes
finding same session. Thesis: routing deltas → ternary plates → frozen base =
map-and-swap resident Lisp on the training side. Two experiments pre-scoped
(EXP-1 ternarize-the-delta = storage, cheap, first; EXP-2 routing-register
construct = finding, the real test). Nonlinear-pin caveat named. NOT yet run —
s304 pickup).

s304 (EXP-1 named TERNARIZE-DELTA-1 by Michael; §TERNARIZE-DELTA-1 pre-reg
FROZEN before any run — TWN per-column ternarize of the s303 gd_cd float LoRA
delta, applied as a permanent plate on the frozen base, re-scored on the
frozen G1–G5 with a matched-sparsity sign-shuffle null; a-priori lean
SURVIVES-TERNARY with a LOW magnitude-cosine / passing-gates dissociation as
the headline. Instrument + run pending Michael GO).

s304 cont-2 — EXP-2 named ROUTING-REGISTER-1, frozen + run: VERDICT WRITE-INERT
(ec77c4d). The wire cannot be written with no gradient in the routing register
either — routing_write == base on all 53 cells. NOT weak-write (boost 0.877 >>
construct's 0.3, key sep min 8.87) → genuine no-routing: the country key fires on
country-NAME frames but never on the one-shot LANDMARK prompt (country
unmaterialized; ∄-clean-linear-linker wall, s300). Triangulated: construct
(magnitude) INERT + routing_write (routing) INERT + gd_cd (gradient) WIRE →
construction insufficient in BOTH registers. RESOLUTION: gradient FINDS, ternary
STORES; artifact = s299 auto-superbake lifecycle (gradient-oracle → ternarize →
keep plate). One untested door: P-FAST-PLATE (forward-etched plate). See
§Result-routing-register.

s304 cont — VERDICT SURVIVES-TERNARY (frozen run, 3 seeds, cb73ad5). All gates
pass (T1 p≤1e-3, T2 p=1.8e-3, T3 p=1e-4, T5 CE lower than base); ternary plate
behaviorally IDENTICAL to the float delta (retention 1.0), shuffle null
collapses to base. STORAGE half CONFIRMED: wire = one ternary plate on a frozen
base. A-priori point-prediction MISSED — mag_cos 0.902 not ~0.7 (s269's 0.73
weight-collapse does not transfer to a rank-16 delta; low-rank sign structure is
ternary-aligned) — honest refinement, null still held. Artifact-size tension
surfaced (370M-trit expanded plate ≈73MB > ~5M factored float params) → TERNARIZE-FACTORS-1
candidate (ternarize the factors, not the product). See §Result-ternarize-delta.

s305 — P-FAST-PLATE picked (Michael's call: front (a), the last construction
door). Mechanization = cleanup-and-reinject (Michael GO over the delta-rule
capital-relay). §P-FAST-PLATE pre-reg FROZEN before any run: a read-only
MATERIALIZATION SCAN as a hard-stop pre-gate M (is the country linearly
decodable anywhere on the one-shot DIRECT prompt?) → if ¬M, STILL-EXTERNAL-BY-
MEASUREMENT (exhaustion law is mechanical); if M, an in-forward hook at L* reads
the materialized country, argmax-collapses to the nearest of 16 name-frame
country keys (confidence-floored), reinjects the country in named geometry, host
h-hop makes the capital (B2 free). Arms base / fast_plate / fast_plate_shuffle
(λ yardstick, ≥3 seeds) / static_reinject (collapse-isolation) / construct_lookup.
Gates F1 wire / F2 not-lookup / F3 specificity / F5 survive. A-priori lean
STILL-EXTERNAL-BY-MEASUREMENT (~45%) — gate-0 g_ok used a country-eliciting
prompt, easier than the DIRECT prompt materializing it unbidden. Instrument
(fast_plate.py) + run pending. Both M-branches are real findings.

s305 cont — VERDICT FAST-PLATE-INERT for THIS construction (frozen run, 3
shuffle seeds, ran in Michael's tmux main:1). ★ pre-gate M PASSED — the country
IS linearly materialized at L*=24 (decodability 0.933, p=5e-4), REFUTING the
s304 "unmaterialized" reading (register-specific: absent at L23-named, present
at L24-whitened). Yet this plate == base EXACTLY on all splits (F1 p=1.0 both)
→ decodability ≠ usability (yet): the intermediate is present; this write
doesn't route it. Attribution = concrete leads, not a wall: reinject_landed
0.072 (weak native single-unit write), lm_name_cos −0.108 (we wrote the WRONG
geometry — name proto, not what the h-hop reads), collapse (this form) hurts
(Δ −0.026), keys fire hard (key_sep_min 39.2), F5 clean. A DATUM about one
construction, not a closure of construction — the mechanism it exposes points
at next constructions: write the MEASURED h-hop geometry (attacks lm_name_cos),
read≠write layer (late materialization), distributed in-register / relay write.
Michael: not a final verdict; other construction avenues remain. See
§Result-fast-plate open-avenues list.

s305 cont-2 — §P-HHOP-WRITE pre-reg FROZEN (avenue 1, Michael GO). Attacks the
s305 miss (wrong geometry) directly: recognize the country at L*=24 (name-keys,
reused), SCAN CAP_QUERY for the country-not-capital layer L_cap≥L* (where the
h-hop reads country before the capital forms), reinject the country there in the
geometry the host's h-hop consumes. ★ Michael's gram thread folded in: the PRIMARY
arm reinjects the country projected onto the 16×16 country gram's LOW-RANK ROUTING
subspace (k by eigengap, the 17×17 cliff-finder, NOT forced rank; gated F4 vs a
matched-rank RANDOM subspace) — a construction-side test of "topology routing, not
magnitudes" (s303 gram thesis, s269 parallel). Arms base / hhop_routing (primary)
/ hhop_raw (contrast) / static_reinject / hhop_shuffle (λ yardstick) /
construct_lookup. Gates F1 wire / F2 not-lookup / F3 specificity / F4 subspace-real
/ F5 survive. routing_advantage (routing − raw) advisory = the thesis fork.
Verdicts HHOP-WIRES (+ROUTING-REGISTER = thesis confirmed on construction side |
+RAW-SUFFICES) / LOOKUP-VIA-GEOMETRY (F1∧¬F2) / HHOP-INERT (¬F1 → routing is
soft/nonlinear, only GD, sharpens s300) / UNSPECIFIC / HOST-DAMAGED. Extend
fast_plate.py --reinject-geometry {name,hhop,hhop_routing} (option>fork). A-priori
~35 WIRES / 25 LOOKUP / 40 INERT; every branch a real finding. Instrument + run
pending.

s306 cont — VERDICT HHOP-INERT for this construction (frozen run, 3 shuffle seeds,
tmux main:1). Writing the MEASURED h-hop geometry (raw OR gram-routing-filtered)
does not wire it: hhop_routing ≈ base (B2 p=0.499; F1-F4 fail, F5 clean). ★
Michael's gram routing filter got a fair test and did NOT help HERE
(routing_advantage +0.026, p=0.491; gram_k=2, cos_capital 0.138 = not lookup) —
does NOT refute topology-routing; the failure isn't a register miss a projection
fixes. ★ NEW MECHANISM from the CAP scan: no country-present/capital-absent layer
≥ L* exists — capital_leak already 0.62 at L24 (=L*, the s305 cliff) → 1.0 by L33.
The g-hop finishes late (L24) exactly as the h-hop has consumed its input → the two
hops OVERLAP in depth on a one-shot prompt = a phase/scheduling face of the s295
re-encoding law, complementary to s300's nonlinear pin. Weak native write again
(reinject_landed 0.033). NOT a closure — opens: in-forward re-encoding relay (reset
the phase, the CoT lesson structural), earlier g-hop, distributed in-register
write, GTSM search. Also fixed a --out footgun (per-experiment default; the run had
overwritten the s305 results.json, recovered from git). See §Result-hhop-write.
