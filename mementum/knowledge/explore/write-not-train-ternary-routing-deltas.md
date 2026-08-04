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
dense-bf16 of the same matrix, not over the low-rank factorization. → **EXP-1b
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

s304 cont — VERDICT SURVIVES-TERNARY (frozen run, 3 seeds, cb73ad5). All gates
pass (T1 p≤1e-3, T2 p=1.8e-3, T3 p=1e-4, T5 CE lower than base); ternary plate
behaviorally IDENTICAL to the float delta (retention 1.0), shuffle null
collapses to base. STORAGE half CONFIRMED: wire = one ternary plate on a frozen
base. A-priori point-prediction MISSED — mag_cos 0.902 not ~0.7 (s269's 0.73
weight-collapse does not transfer to a rank-16 delta; low-rank sign structure is
ternary-aligned) — honest refinement, null still held. Artifact-size tension
surfaced (370M-trit expanded plate ≈73MB > ~5M factored float params) → EXP-1b
candidate (ternarize the factors, not the product). See §Result-ternarize-delta.
