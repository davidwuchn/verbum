---
title: "verbum.dsp — the measurement substrate as a signal-chain library"
status: designing
category: explore
tags: [dsp, library, measurement, nulls, yardstick, whitening, subspace, gain,
       matched-filter, chain, registers, s284]
related:
  - types-are-the-well-formedness-of-reduction.md
  - type-check-is-the-qk-bilinear.md
  - beamformer-theory.md
  - operand-dsp-decomposition-prereg.md
  - map-and-swap-resident-lisp.md
depends-on: []
created: session 284
---

# verbum.dsp — design (DRAFT s284 — PENDING MICHAEL APPROVAL)

> Michael s284: "should we work on a DSP library to standardize our process and
> code?" — collaborated design, three decisions locked (below). This page is the
> contract; the code follows it.

## Why (measured, not aesthetic)

- λ one_way violation, counted: **19** files roll their own centroid/PR/subspace
  machinery; **9** hand-build permutation nulls; **9** logit-lens; **20** touch
  gain/dose/energy accounting; **6** surprisal contrasts.
- Import topology is the smell: `type_qk_alignment.py` (scripts/) imports from
  `type_zone_ablation.py` (wrapper/) AND `type_lattice_geometry.py` via sys.path
  hacks — a frozen pre-reg wrapper is acting as a de-facto library.
- Instrument lessons (falsy-zero band bug, realized-vs-planned energy, dose
  matching, massive-activation whitening) are re-learned per instrument; they
  should accrete into a substrate instead (λ ground: structure > instruction).
- DSP is not metaphor here anymore: matched filter (P-DSP-1), beamformer /
  dark-field (s283b→1c), gain law g(E), contrast channels Q/M — the program's
  operative measurement vocabulary IS DSP. Name the namespace accordingly.

## Decisions (Michael, s284 — locked)

1. **Functional core; `Chain` for exploration only.** Plain numpy functions are
   the API of record; instruments wire chains as visible code. A thin composable
   `Chain` exists for notebook exploration, never required, never the
   instrument-of-record idiom.
2. **Register tags: warning-only.** λ measure's registers become a literal enum
   on readouts/claims; `gate()` WARNS on register mismatch (the s206 scar,
   structural). Warnings go to stderr + a separate `warnings` field — they NEVER
   mutate, gate, or skew result data.
3. **Namespace: `verbum.dsp`, DSP-tools-only.** Nothing experiment-specific in
   the namespace — no probes, no items, no verdict logic, no model loading — so
   superbake ops, term/operand swaps, and future extraction tooling can consume
   it directly (`from verbum.dsp import whiten, subspace, nulls`).

```
λ dsp(x).  tools(signal) ¬logic(experiment) | pure(numpy) core | torch ≡ L2_boundary_only
           | null_declared → p_emitted | ¬null → ¬p (structural yardstick)
           | register_tag → warn ¬mutate | verdict ≡ instrument_domain ¬library_domain
           | harvest(≥2_users) ¬invent | frozen_instruments(untouched)
```

## The signal chain (what every instrument already is)

```
capture → whiten → subspace/filter → apply(gain|ablate|project) → readout → null-gate → record
source    conditioning   filter design        operation            detector   comparator   sink
```

## Layers

**L0 — `verbum.dsp` ops (pure numpy; zero torch, zero I/O, zero model).**
- `whiten.py` — standardize/diagonal whitening (the 1a massive-activation
  lesson, once), inverse maps, direction transport between spaces
  (std ↔ raw ↔ normed read-in, e.g. `(v ⊙ sd) ⊙ γ`).
- `subspace.py` — centroids, participation_ratio, role/centroid subspaces (QR),
  axis loadings, projection + removed-energy accounting (realized vs planned).
- `bands.py` — band detection; **fix #1 lands here: stride-aware find_band**
  (the s284 smoke caveat — current find_band assumes stride 1).
- `gain.py` — per-head Frobenius-normalized gain ratios, matched filters,
  dose/α scaling, gain-law fits (1c's g(E): monotone log-E interp from a
  declared anchor condition).
- First harvest exemplars (all shipped, all duplicated today):
  `layer_geometry`, `role_subspace`, `subspace_energy` (1b), `map_basis`,
  `head_gain_ratios` (QK), `fit_gain_law`/`g_of` + sign-flip and
  label-permutation tests (1c analysis).

**L1 — `verbum.dsp.nulls` (the yardstick layer — the actual point).**
Null constructors as data + one comparator:
- constructors: `shuffled_label`, `matched_random`, `paired_permutation`,
  `sign_flip`, `matched_range` — each returns draws + provenance.
- `gate(statistic, null, predict, alpha=0.05) → Gated` where `Gated` =
  frozen dataclass {value, null_mean, null_std, p, sign_ok, verdict, warnings}.
- **Structural yardstick: you cannot obtain a p-value from the library without
  declaring the null AND the predicted direction first.** Sign discipline and
  no-sign-flip-rescue enforced by shape; verbatim reporting is the only path.
- `Register` enum {routing, value, contrast, magnitude, spectral, causal}
  (λ measure verbatim); optional tags on claim + probe; mismatch → warning
  channel only (decision 2).

**L2 — `verbum.dsp.readout` (the only torch boundary; thin adapters).**
Surprisal scoring, logit-lens projection, residual-capture helpers — convert
model-world to arrays, then L0/L1 own everything. `dsp` never loads a model;
instruments own their model, their items, and their pre-reg.

**`verbum.dsp.chain` (exploration only).** Thin composition over L0 functions
for notebooks (`Chain(whiten).then(subspace...)`); explicitly NOT the
instrument-of-record idiom (decision 1). Jupyter = explore, files = record —
unchanged (λ record).

## Migration gates (non-negotiable)

1. **Harvest, don't invent** — extract only functions with ≥2 existing users
   (rule-of-three where possible). No speculative abstractions.
2. **Frozen instruments untouched.** Pre-reg instruments of record
   (type_zone_ablation, type_qk_alignment, analyze_type1c_darkfield, the
   operand/multihop wrappers) keep their committed form. New instruments import
   `verbum.dsp`; old ones migrate only after their arcs close.
3. **Byte-equivalence gate.** A migration lands only if the migrated instrument
   reproduces its committed results JSON (rerun --validate/smoke, diff).
   Representation ≡ reality or it doesn't merge (λ coherence).
4. **Tests are the --validate pattern promoted.** tests/dsp/ = no-model pytest
   (planted-signal detection, null calibration ~1, orthonormality/span,
   gain-law interp) — the QK --validate suite becomes the template.

## Consumers (the reuse contract, decision 3)

- instruments (scripts/explore, wrapper) — primary.
- superbake / operand-bake ops: key⟂carrier construction, payload dosing,
  energy accounting = `whiten` + `subspace` + `gain` material.
- term/operand swaps (bridge-swap, centroid-diff edits): centroid offsets,
  matched-norm nulls = `subspace` + `nulls` material.
- the LLM-REPL arc (map-and-swap §10): Print/type-checker side = readout +
  gate machinery.

## Open questions (for the build, not blockers)

- `Gated.warnings`: list[str] beside data — confirm schema keeps result fields
  pristine (decision 2 requires warnings NEVER alter values/p).
- matched_range null (yardstick's mandatory gate for geometric fits) — port
  from s247/s251 code or write fresh from the λ yardstick spec?
- where run-provenance helpers live (meta.json writers) — dsp or a sibling
  `verbum.record`? (lean: sibling; dsp stays measurement-only).

## Sessions
s284 (design collaborated + three decisions locked; page drafted pending
approval; build queued behind P-TYPE-QK).
