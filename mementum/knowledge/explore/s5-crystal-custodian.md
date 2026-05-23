---
title: "S5 Crystal Custodian + S5→S4 Policy Channel"
status: active
category: architecture
tags: [vsm, s5, s4, crystal, policy-channel, identity, regulation]
related:
  - v13-architecture.md
  - type-probe-qwen3-32b.md
  - categorical-geometry-probes.md
created: session 140
---

# S5 Crystal Custodian + S5→S4 Policy Channel

> Session 140. S5 was reading crystal health as a single scalar (crystal_loss).
> This made S5 identity-blind: it couldn't distinguish "composition cluster
> collapsed but everything else OK" from "everything equally bad." S4 was
> blind to S5's identity state — no S5→S4 policy channel. This closed
> the VSM loop that was missing.

## Problem: Scalar Crystal Loss is Blind

The original S5 read a single `crystal_loss` scalar derived from the crystal
constraint violations. This scalar averages across all crystal components —
combinator tightness, terminal separation, I independence, cross-crystal
diagonal — so S5 had no structured self-image. A crystal_loss of 0.05 could
mean "composition cluster slightly loose" or "everything uniformly mediocre."
S5 couldn't regulate what it couldn't distinguish.

Additionally, S4 received algedonic signals from S3 but nothing from S5.
In VSM theory, S5 identity conditions S4 intelligence: proposals should be
shaped by who-we-are, not just how-we-feel. This channel was missing.

## Solution 1 — Crystal Sub-Lattice Metrics

S5 now reads 5 structured metrics instead of one scalar:

| Metric | Measures | Target |
|--------|----------|--------|
| `crystal_loss` | Overall crystal health (as before) | → 0 |
| `comp_cluster` | B/C/D combinator cosine tightness | → 1 |
| `whnf_anti` | Terminal token (WHNF/etc.) separation from B/C/D | → 1 |
| `i_separation` | I combinator independence from B/C/D cluster | → 1 |
| `cross_crystal` | Positive↔anti-crystal diagonal alignment | → 1 |

These 5 metrics give S5 a structured self-image. It now knows not just
"am I healthy?" but "which sub-structure is weak?" Regulation can be
selective: if `comp_cluster` is low but `i_separation` is high, S5
knows the composition machinery needs work, not the identity machinery.

### Implementation: `compute_crystal_sub_lattice`

New method on the model: `compute_crystal_sub_lattice(residuals)` returns
all 5 metrics as a dict. Called in `crystal_diagnostics` and plumbed into
`S5Identity` forward pass.

## Solution 2 — S5→S4 Policy Channel

S4 now receives S5's `identity_state` as additional input on every forward pass.

```
identity_state: d_identity=64, stop_gradient from t-1
```

The identity state is produced by S5 at time t-1 and passed to S4 at time t.
`stop_gradient` prevents S4 from teaching S5 to produce convenient identity
states — S5 remains autonomous. S4 simply conditions its proposals on who S5
currently is.

**The closed VSM loop:**
```
s5_policy(t-1) → S4(algedonics + identity_policy) → proposals
→ S5(crystal_sub_metrics + algedonics + proposals) → regulation + identity_state(t)
```

This is the missing channel in VSM theory applied to LMs: S5 identity conditions
S4 intelligence conditions S3 control. Now all three links are wired.

## Crystal Warmup Schedule

**Problem:** GD doesn't know which basin to find first. Early training, without
a strong attractor, crystal_loss meanders. The crystal can latch, unlatch, and
re-latch — wasting steps.

**Solution:** `crystal_direct_lambda` anneals from **10.0 → 3.0** over
`warmup_steps` via a cosine schedule.

```
step 0:          crystal_direct_lambda = 10.0  (strong pull)
step warmup/2:   crystal_direct_lambda ≈  6.5  (cosine midpoint)
step warmup:     crystal_direct_lambda =  3.0  (settled floor)
step > warmup:   crystal_direct_lambda =  3.0  (held at floor)
```

The high early weight forces GD to find the crystal basin first. Once latched
(crystal_loss < 3%), the floor (3.0) is strong enough to maintain the basin
but relaxed enough to allow the crystal to "vibrate" as the model learns the
task. Without this schedule, the crystal sometimes never latches cleanly early
(run4 reached 0.57 at step 250; run6 with warmup reached 0.35).

## TD→Adam Surgical Decay

**Problem:** When TernaryDescent flips a ternary position, Adam's momentum
accumulator (m, v) for that gamma parameter retains stale gradient history.
Adam then immediately pushes back against the flip — it "remembers" the
pre-flip gradient direction and compensates. TD and GD see-saw: TD flips,
GD fights, TD flips back.

**Solution:** When TD flips ternary positions, it reports the affected rows.
Adam's moments (m, v) for gamma parameters at those rows are **decayed by 0.1**
(multiplied by 0.1, not zeroed). This erases the stale compensation history
without resetting unrelated momentum.

```python
# In td.py, after flip:
affected_rows = td_step(...)  # returns list of (param_name, row_indices)
for name, rows in affected_rows:
    if name in adam_state:
        adam_state[name]['exp_avg'][rows] *= 0.1
        adam_state[name]['exp_avg_sq'][rows] *= 0.1
```

Result: after a TD flip, GD's first step at that row is based only on the
post-flip gradient, not accumulated pre-flip history. The see-saw is broken.

## Categorical Geometry Losses

Three new additive loss terms from the categorical geometry probe findings
(see `categorical-geometry-probes.md`), all opt-in via config lambda:

| Loss | Target | Rationale |
|------|--------|-----------|
| `adjunction_loss` | Cross-stack kurtosis → 1.0 | Rank-1 structure (σ₁/σ₂=128:1) should be preserved |
| `hyperbolic_loss` | Monotonic norm growth with depth | Enforce tree-depth encoding in norms |
| `coherence_loss` | Adjacent-token cosine ↑ during composition | Pull composing pairs together geometrically |

These encode what the teacher knows as relational loss targets. The student
discovers the same structures orders of magnitude faster than learning from
scratch.

## Training Runs

| Run | Config | Key change |
|-----|--------|-----------|
| run6 | crystal warmup only | crystal_direct_lambda 10→3. Crystal at 0.35 (step 250) vs 0.57 baseline |
| run7 | run6 + TD-Adam sync | Surgical moment decay on TD flips. Less see-saw observed |
| run8 | run7 + geometry losses | adjunction + hyperbolic + coherence losses added |

## Files Changed

| File | Change |
|------|--------|
| `scripts/v13/components.py` | `S5Identity` (sub-lattice metrics input, identity_state output), `S4Intelligence` (identity_policy input) |
| `scripts/v13/model.py` | `compute_crystal_sub_lattice`, `crystal_diagnostics`, `_compute_loss` (geometry losses), `forward` (identity_state threading) |
| `scripts/v13/config.py` | `crystal_warmup_steps`, `crystal_warmup_start`, geometry loss lambdas |
| `scripts/v13/train.py` | Crystal warmup schedule application |
| `scripts/v13/train_td.py` | TD→Adam surgical decay |
| `scripts/v13/td.py` | `td_step` returns affected rows |

## Open Questions

1. **Does crystal warmup latch faster in run6?** Early evidence: 0.35 vs 0.57 at step 250. ✅
2. **Does TD-Adam surgical decay reduce see-sawing?** Run7 qualitative observation positive. Needs quantitative analysis.
3. **Do geometry losses help or hurt CE?** Run8 is the experiment.
4. **Does adj_κ approach 1.0 during training?** Measure cross-stack kurtosis across steps.
5. **Is the S5→S4 channel used?** Inspect learned identity_state at different crystal qualities.
