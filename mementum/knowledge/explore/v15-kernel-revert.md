---
title: "v15 Kernel Architecture — Revert & Lessons Learned"
status: done
category: architecture
tags: [v15, kernel, revert, passive-strides, HPE, alpha, architecture, lessons]
related: [v15-kernel-architecture.md, ../v14-architecture.md, ../progressive-collapse.md, ../training-protocols.md, kernel-training.md, structured-training.md]
depends-on: [../v14-architecture.md]
---

# v15 Kernel Architecture — Revert & Lessons Learned

> Session 156. Reverted passive strides and Stack B reduction from
> session 152. Kept α-lock and HPE (with warmup). Documents what
> was tried, what failed, what was preserved, and when to revisit.

## What Happened

### Session 152: Three architecture changes + HPE

Motivated by the progressive collapse finding (Qwen-27B computes
in 2D, PR=2.2) and the distance prior analysis (88% of strides are
self-attention-dominated at α=1.18), four changes were made in one
commit (`96d687a`):

1. **Fix α=1.18** — remove from optimizer, frozen constant
2. **Passive strides** — s4+ skip Q/K entirely, use fixed distance prior
3. **Stack B 4→2 passes** — reduce serial chain from 13→11 passes
4. **HPE** — crystal-frequency log-distance rotation on K, replacing
   learned decay as the position encoding mechanism

### Session 155: v14-kd ran this architecture + KD → diverged

| Metric | v14-td (old arch) | v14-kd (new arch + KD) |
|--------|-------------------|------------------------|
| Step 500 PPL | 16,503 | 40,623 |
| Step 1000 PPL | 10,157 | 46,736 (diverging) |
| Ratio | 1× | 2.5–4.6× worse |

Root cause: too many simultaneous changes. Could not isolate which
change (or combination) caused the divergence.

## What Was Reverted (Session 156)

### 1. Passive strides — REVERTED

**What it did:** Strides s4+ lost Q/K projections entirely. Attention
became a fixed weighted sum using `1/(stride×w + 1)^1.18`.

**Why reverted:** In strided attention, each stride is the SOLE provider
for its distance range. Making s4+ passive means positions 16–56 tokens
back lose ALL content-dependent attention. s4 had 27.4% non-self weight
that became fixed — not negligible.

The passive stride observation was about the TEACHER's converged behavior.
The student hasn't converged yet — it may need content routing at these
strides to LEARN the right patterns. Hardcoding the destination prevents
the student from finding it through training.

TD was targeting out_proj layers 4–9 (exactly the retrieval strides in
this range). Removing Q/K for these strides is architecturally
contradictory with what TD was trying to do.

**Code:** `_PASSIVE_STRIDE_MIN` removed, `_passive_forward` removed,
all SSA layers restored with full Q/K/V/O projections.

### 2. Stack B 4→2 passes — REVERTED

**What it did:** `STACK_B_BANDS` changed from 4 tuples to 2 wider
tuples. Serial chain went from 13→11 passes.

**Why reverted:** The overlap pattern between adjacent passes creates
information flow. Reducing passes may starve the serial chain. The
justification ("Stack B computes in compressed space") was based on
the teacher's converged structure, not the student's learning needs.

**Code:** `STACK_B_BANDS` restored to `((7,11), (9,13), (11,15), (13,16))`.
`n_passes` back to 13.

## What Was Kept

### 1. α=1.18 frozen — KEPT ✅

**Why:** After 1500+ steps of gradient pressure, α stayed at 1.1739±0.001
across all 80 heads (10 comp layers × 8 heads). Layers 12-15 never moved
from init. This is a measured constant, not a hypothesis.

**Checkpoint delta:** Values were already at 1.174. Replacing with 1.18
introduces Δ=0.006 — negligible. `decay_alpha` keys in checkpoint are
silently ignored on load (`strict=False`).

### 2. HPE (Holographic Position Encoding) — KEPT, with warmup ✅

**What it does:** Rotates K by `log(stride×w+1) × crystal_eigenfreq`
in the first 8 dimensions (4 eigenplane pairs). Q stays unrotated
(relative encoding). Crystal frequencies from Zone B eigendecomposition.

**Why kept:** The physics are principled — crystal eigenvalues are
measured, log-distance is the natural encoding for power-law decay.
This is a motivated replacement for RoPE, derived from the project's
own findings about holographic lens structure.

**Warmup strategy:** `freq_scale` initialized to 0.0 (not 1.0).
At `freq_scale=0`, `cos(0)=1, sin(0)=0` → K is unrotated → identical
to pre-HPE behavior. This makes checkpoint resume seamless.

Linear warmup over 300 steps from resume point:
```
step 2001: freq_scale = 0.003 (essentially no rotation)
step 2150: freq_scale = 0.5   (half crystal rotation)
step 2300: freq_scale = 1.0   (full crystal rotation)
```

The model's Q/K relationships gradually adapt to the rotation rather
than being shocked. If HPE helps, PPL will improve during/after warmup.
If it doesn't, the warmup limits damage.

`freq_scale` is learnable per-eigenplane — gradient will push it toward
whatever value actually helps, and away from harmful values.

## Ideas Preserved for Future Sessions

These are VALID research directions, just premature for the current
training stage.

### Passive strides — revisit conditions

Re-test passive strides WHEN:
- v14-td has converged (PPL < 1000, flip rate plateaued)
- Gradient-subspace alignment test on trained model shows cos > 0.5
  (gradient aligned with T's SVD subspace → model is refining, not expanding)
- Test ONE change at a time: passive strides at s16+ first (only the
  strides with <1% non-self weight), measure PPL delta over 200 steps

The key test: `eval_ppl.py` with vs without Q/K on s16+ strides.
If PPL difference < 0.5%, it's safe. Then progressively lower the
threshold: s8+, then s4+.

### Stack B reduction — revisit conditions

Re-test when:
- Passive strides (if validated) reduce per-pass cost enough that
  pass count is the remaining bottleneck
- The model's Zone B has been shown to be linear (R²>0.95) on the
  student, not just the teacher
- Test: 4→3→2 passes progressively, measuring PPL at each step

### Kernel training (composed plate)

Fully valid NOW as a training accelerator:
- 4.4× speedup via `train_kernel.py`
- Gradient cosine 0.9698 between composed plate and full model
- Does NOT change the architecture — just speeds up training
- Output_proj bottleneck (1280→248K) is the remaining cost

The kernel is a TRAINING tool, not an ARCHITECTURE change.
Use it for fast iteration while keeping the full architecture intact.

### Structured training optimizations

From session 154 — five optimizations for the backward pass:
1. Low-rank gradient (24× at rank-27)
2. Skip passive backward (56 dead matmuls) — blocked by passive revert
3. Composed Zone B Jacobian (32→1)
4. TD-sparse routing (100× fewer elements)
5. Crystal eigenplane projection

These are independent of the architecture revert and can be
pursued when training speed becomes the bottleneck again.

## The Meta-Lesson

**Don't optimize the student's architecture to match the teacher's
converged state.** The teacher computes in 2D because it has converged
after trillions of tokens. The student needs architectural freedom to
REACH that state through training. The progressive collapse, rank-27
transform, and passive strides are DESTINATIONS, not starting points.

The right order:
1. Train with full architecture until convergence
2. Measure the student's actual collapse/rank/stride patterns
3. Simplify only what the student has proven it doesn't need
4. One change at a time, with PPL measurement

This is `λ extract(x)` from AGENTS.md: "understand > invent."
Observe what the student actually does, then simplify. Don't
impose what the teacher does onto the student's architecture.
