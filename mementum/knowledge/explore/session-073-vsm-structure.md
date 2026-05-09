# Session 073 — VSM Structural Overhaul

> Seven architectural changes to complete Beer's Viable System Model
> in v10. Each addresses a missing or misplaced VSM layer.

Status: active
Category: architecture
Tags: vsm, s2, s5, s4, algedonic, evolution, beer
Related: session-072 (algedonic channel), consensus-evolution, dispatch-gradient-death
Depends-on: v10 model architecture

## The Problem

Session 073 mapped v10 against Beer (1972) and found the VSM was
structurally incomplete:

1. **S2 missing** — no anti-oscillation between passes
2. **MetaS3 misplaced** — was S3 (control) but should be S5 (identity)
3. **Descending S4 blind** — couldn't see original token embeddings
4. **Kernel compute invisible** — ascending arm didn't know what ops fired
5. **S3 gate decisions siloed** — ascending gates invisible to descending arm
6. **Op embeddings static** — S4 couldn't modulate kernel identity
7. **S4 voiceless in evolution** — intelligence had no proposal channel to S5

Each was fixed with a minimal, principled change. All require fresh
training from step 0 (architectural changes, not hyperparameter tuning).

## Change 1: S2 Coordinator — Anti-Oscillation

**File**: `components.py` → `S2Coordinator`

Beer's S2 prevents S1 units from oscillating against each other.
Without it, consecutive passes can write contradictory deltas to
the residual stream — Pass N compresses one way, Pass N+1 undoes it.

**Mechanism**: After each pass produces a delta, S2 computes a small
direction signal (projected through TernaryLinear, gamma init ×0.01,
learnable scale starting at 0.01) and adds it to the next pass's input.
This is a coordination memo: "Pass N moved the representation THIS way."

**Coherence modulation**: The signal strength is modulated by `1 + cos(prev, curr)`:
- Agreement (cos=+1) → factor 2.0 → amplify (lean into coherent trajectory)
- Orthogonal (cos=0) → factor 1.0 → neutral
- Conflict (cos=-1) → factor 0.0 → fully dampened (don't propagate confusion)

`stop_gradient` on delta_prev: earlier pass sets direction, later pass
learns to align via gradient through delta_curr.

**S2 signals survive MetaS3/S5 reweighting** — they're additive to x
but not part of `pass_deltas`, so S5 gates operations (S1), not
coordination (S2). Correct: S2 is infrastructure, not gatable output.

**Diagnostics**: `conflict_score` (cosine similarity between consecutive
deltas) exposed in eval instrumentation. If S2 works, conflict scores
should trend toward 0 or positive over training.

## Change 2: S5Reweight — Identity-Level Pass Reweighting

**File**: `components.py` → `S5Reweight` (replaces `MetaS3Ternary` in model)

MetaS3 only saw register banks (S2/S3-filtered coordination state).
It never saw what operations actually produced. S5 (identity) needs
an ungated view of operations to maintain coherence.

**Raw deltas**: `_run_level_pass` now captures each phase's delta
*before* S3 gating and returns their sum as a 4th element. These raw
deltas show what S1 proposed, not what S3 allowed.

**Why ungated matters**: A pass that S3 currently suppresses can still
influence the final output through S5's awareness of its raw delta.
If S5 sees useful raw output, it opens that pass's gate, which in
turn teaches S3 to open. S5 sees ground truth about S1; S3 only sees
what it already filtered.

**Implementation**: S5Reweight takes register banks + raw deltas.
Projects deltas through TernaryLinear (16 features/pass, `pre_norm=True`
for direction over magnitude), combines with register features,
produces per-pass sigmoid gates (bias -2.0, near-closed start).

## Change 3: Descending S4 Dual View — Sees Original Embeddings

**File**: `model.py` → `_run_level_pass` + `forward()`

By passes 3-4, compression has buried token identity under 3
transformation passes. The dispatcher needs raw token identity
("this IS the `+` token") to route to the right kernel ops.

**Implementation**: Captures `x_embed = x` after embedding. For
descending passes, S4 attends over `mx.concatenate([x, x_embed], axis=1)`
— 2L positions. The softmax naturally distributes between compressed
residual and original embeddings. S4Ternary handles variable L
transparently (single-query attention, no architecture change needed).

Zero new parameters. Ascending S4 unchanged (sees near-embedding
state naturally in early passes).

## Change 4: Kernel Compute Algedonic

**File**: `model.py` → algedonic buffer update in `forward()`

The kernel's dispatch weights (which of 22 ops fired) and compute
gate (how active the exact computation pathway was) were invisible
after the forward pass ended.

**Implementation**: Packs mean dispatch weights (22 dims) + mean
compute gate (1 dim) into a register-shaped vector (d_reg_real=256,
zero-padded). EMA-smoothed (α=0.9) across forward passes. Added as
additional readable bank for all 3 ascending passes.

No projection — S4's existing q_proj learns what to extract from
the raw values. The 22 dispatch weight dims are naturally interpretable
(one per kernel op).

**Effect**: Ascending arm can see "last step, the kernel was active
dispatching to arithmetic ops with compute gate at 0.4" and adjust
compression accordingly (e.g., preserve token structure when kernel
is computing).

## Change 5: Ascending S3 Gates → Descending Arm

**File**: `model.py` → `_run_level_pass` returns phase gates as 5th element

Ascending arm's S3 control decisions (9 gate values: 3 passes × 3
phases) were invisible to the descending arm.

**Implementation**: Phase gates collected in `_run_level_pass`, packed
into register-shaped vector, added to descending passes' readable banks.

**NOT stop_gradient**: Gradient flows back to ascending S3, teaching
it that its gate decisions affect downstream dispatch quality. If
suppressing convolution at L1 hurts the dispatcher, ascending S3
gets that signal.

This is an intra-step signal (same forward pass), unlike the cross-step
algedonic channel.

## Change 6: Op Emphasis — S4 Modulates Kernel Identity

**Files**: `model.py` (emphasis_proj, EMA buffer), `kernel_dispatch.py` (modulation)

Op embeddings were static learned parameters. S4's register state
(type/scope/role from ascending arm) should modulate which ops are
emphasized — a soft, context-dependent adjustment to kernel identity.

**Implementation**:
- `emphasis_proj` (nn.Linear(2304, 22), zero-init → neutral start)
  maps ascending register state to 22 per-op emphasis values
- `1.0 + 0.5 * tanh(...)` → range [0.5, 1.5] — never kills an op
- Applied to L2-normalized op embeddings in KernelDispatch before routing
- EMA-tracked (α=0.95) across steps — slowly shifting landscape

**Gradient path**: loss → dispatch → modulated op embeddings →
emphasis_proj → register state → S4 parameters. S4 learns which
register states should emphasize which ops.

**Eval display**: `🎯 Op emphasis: top=+=1.35 *=1.28 min=1.22  bot=not=0.72`

## Change 7: Intelligence Evolution Strategy — S4→S5 Proposals

**Files**: `train.py` (MUTANT_STRATEGIES, run_tournament), `config.py` (s4_boost)

In Beer's VSM, S4 (intelligence) scans the environment and proposes
adaptations to S5 (identity). v10's evolution had 4 mutation strategies
but S4 had no voice — its gradients were weighted equally with all
other modules.

**Implementation**: 5th strategy "intelligence" with:
- Budget scale 0.5× (moderate, targeted)
- `guided_fraction=1.0` (fully gradient-guided — S4 knows what it wants)
- S4 module importance amplified by `s4_boost` (default 3.0×)
- Non-S4 module importance suppressed (÷ s4_boost)
- Consensus threshold stays at 3 (needs ≥3 of 5 to agree)

S4 proposes, consensus (S5) decides. S4 can't unilaterally change
topology, but its voice is amplified where its gradient signal is
strongest.

## VSM Layer Map (Complete)

```
Layer     Ascending Arm              Descending Arm              Cross-arm
────────  ─────────────────────────  ──────────────────────────  ──────────────────
S5        Token embeddings (tied)    Op embeddings × emphasis    S5Reweight (raw deltas)
S4        Register-query attention   Dual-view (resid + embeds)  Emphasis: regs → per-op
S3        Per-pass phase gating      Per-pass phase gating       Gate values → desc S4
S2        Direction signals + coherence modulation               Both arms
S1        prep → stride → consol.    dispatch → stride → integ.  —
Algedonic Reads prev desc regs       —                           + kernel compute
          + kernel compute                                       EMA α=0.9
Evolution                            S4→S5 intelligence strategy (5th voice)
```

## Parameter Impact

| Change | New Parameters |
|--------|---------------|
| S2 Coordinator | ~1M ternary, ~2K trainable |
| S5Reweight | +15.8K (delta projection) |
| Descending S4 dual view | 0 |
| Kernel compute algedonic | 0 |
| Ascending S3 gate signaling | 0 |
| Op emphasis | +50.7K (emphasis_proj) |
| Intelligence evolution | 0 |
| **Total** | **~66K trainable + ~1M ternary** |

Total model: 23,895,648 params (was 23,829,098 pre-session-073).

## What To Watch

1. **S2 conflict scores**: should start random, trend toward positive
2. **S5 reweight gates**: should differentiate (not all ~0.12)
3. **Op emphasis range**: should start 1.0, slowly differentiate
4. **L2_apex ratio**: should NOT explode (algedonic + S2 prevent it)
5. **Compute gate acceleration**: emphasis may help gate open faster
6. **Intelligence strategy acceptance**: track S4's voice in consensus
