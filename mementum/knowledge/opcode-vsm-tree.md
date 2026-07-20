---
title: "Opcode Crystal Tree — Tree-of-VSM Applied to Measurement"
status: active
category: architecture
tags: [opcodes, vsm, tree, gram, registers, jspace, basis, null-floor, multi-model]
related:
  - moe-holographic-tree-vsm.md
  - crystal-multi-tree.md
  - crystal-phi-derivation.md
  - explore/opcode-register-decomposition.md
  - explore/opcode-jacobian-jspace.md
depends-on:
  - crystal-universality.md
created: session 265
---

# Opcode Crystal Tree — Tree-of-VSM Applied to Measurement

> s265, Michael's directive: "opcodes should use the v14/v15 tree-of-VSM
> tensor setup so we can create multiple VSM-shaped tensors and stack them
> in the tree." Implemented in `opcodes/` (8 modules, pytorch+numpy only,
> data bundled, staged for its own MIT repo). This page is the design
> synthesis; run instructions live in `opcodes/README.md`.

## 1. The stackable tensor is the frame-invariant Gram

Per-combinator centroids `[9, d]` are **model-dimension-bound** — they cannot
be compared across models. The 9×9 relational Gram (cosine structure between
sign-CMR centroids) lives in **combinator-label space**, not weight space: it
has the identical shape for every layer, register, model, architecture, and
scale. That is the entire reason a cross-model tree is possible.

```
λ tree(tensor).  stackable(x) ⟺ frame_invariant(x)
                 | gram[9,9] ∈ label_space → stacks | centroids[9,d] → leaves(npz)
```

## 2. One fractal node shape (v14/v15 `stack_vsm` → measurement)

Every node in the tree is the same viable-system shape (`opcodes/vsm.py`):

```
S5 identity      node.gram          the node's crystal (9×9 consensus)
S4 intelligence  node.meta          cross-child agreement/dissent stats
S3 control       node.gated         null gate — ungated children stay VISIBLE
                                    but contribute NOTHING upward
S2 coordination  node.children      sibling registers/models kept comparable
S1 operations    leaf arrays        centroids (model-dim-bound, npz sidecar)
algedonic UP     node.health        {sil_z, gc_consensus,
                                     crystal_bearing_frac, null_floor_z}
```

Ladder: `layer → register → model → family → root(universal)`. Parent Gram =
mean of GATED children; caveats (`null_floor_z`) propagate as the **worst
child** — a caveat can never be aggregated away. Dissent is a first-class
output: an un-aligned-but-not-anti child stays in and collapses
`agreement_min`; only anti-alignment or gate failure excludes.

## 3. Three bases, three registers (resolves "9 vs 16")

| Basis | Size | Register | Members |
|---|---|---|---|
| CRYSTAL | 9 | measurement (routing, promptable) | 4 fire (K,I,B,C) + 3 paths/bridges (D=B→B, W, Y) + WHNF |
| STATECHART | 8 | dynamics (absorbing chain) | fire:{K,I,B,C} + whnf:{K,I,B,C} — count is forced |
| TYPES16 | 16 | extraction (weight space) | 8 types + 8 anti-types (M₁₆ = S⊗J + D⊗F) |

The 9 is what can be probed with ground-truth labels (≥50 prompts per
combinator, `λ probe_library`); anti-types are **not promptable** — they exist
only in the extraction register and cannot enter the measurement tree. One
basis per tree, enforced at `stack()`. Cross-basis comparison is an analysis
step, never a tree operation.

## 4. Registers are sibling S1 units; J-space is the operand register

s264's register decomposition (gate = {K,I,S,Y,WHNF}, attn-write rescues D,
neither resolves {B,C}) becomes **topology**: registers are sibling children
under a model node, so single-register blindness is a missing child — visible
as an algedonic gap, not hidden by a merged trajectory.

J-space (`opcodes/jspace.py`, on `ModelTopology` so it works on nested/hybrid
archs) is the **operand** register: it reports WHAT is routed and NEVER
classifies opcodes (s263 EXP1 null: broadcast is generic, not
combinator-selective). Display-only column; must not feed the classifier.
Future: the QK-pattern register (position-routing) as a third sibling — the
predicted home of {B,C} (s264 F4, untested).

## 5. Null floor: measured per-run, never assumed (s265 instrument)

`classify.measure_null_floor` — full recalibration under shuffled labels on
the same captured features. `null_floor_z` = pooled q95 of per-layer shuffled
sil_z (layer-count independent; ~1.64 for a clean N(0,1) null);
`shuffled_bearing_frac` (nominal 1–2%); `suspect` flag > 5%.

**Finding (s265→s266): floors are register-, model-, and
ARCHITECTURE-conditioned.** The s265 "reversal" on qwen3-0.6b (gate 2.78 >
attn 2.14) was not scale — the 9-model sweep (s266) shows the direction is
**family-patterned**:

| family | gate floor | attn floor | direction |
|---|---|---|---|
| qwen3 (×5) | 2.03–2.78 | 1.46–2.14 | gate-elevated (all 5) |
| gemma-4-31B | 1.86 | 1.46 | gate-elevated |
| olmo-2-13B | 2.07 | 1.75 | gate-elevated |
| pythia-14m | 1.55 | 1.94 | **attn-elevated** |
| pythia-2.8b | 1.93 | 2.04 | **attn-elevated** |

Gated-FFN architectures → gate-elevated floor; the ungated pythia arch
(up-proj proxy) → attn-elevated. Fresh 27B floors: gate 2.08 > attn 1.85 —
s264's elevated-attn 27B reading **does not reproduce** and is now the
anomaly (retro-check that run's n_perm/pooling before discarding).
pythia-14m attn remains SUSPECT (5.6% shuffled bearing). Consequence
unchanged and sharpened: near-threshold bearing calls (e.g. 0.6b gate
L0/L17–L19) sit at/below their own floor; the solid 0.6b gate zone is
L5–L16. Never carry a floor across models — and the *direction* itself is
an architectural observable, not noise.

Discipline: floor needs ≥~20 pooled samples and n_perm ≥ 120 (fewer perms →
the z-estimate itself is t-tailed and inflates the floor — caught by the
synthetic smoke honestly flagging 3-layer toy data).

## 6. First tree result (2 models, full calibration)

- root gc = **+0.940** vs the bundled 10-model consensus
- cross-family agreement **0.907** between pythia-14m (14M params, ungated
  up-proj proxy) and qwen3-0.6b (gated) — cross-architecture, 43× scale gap
- calibration lesson: 135 probes → gc 0.344; 535 probes → 0.940. **Probe
  count dominates Gram fidelity; smoke = pipeline check only, never a
  measurement.**

## 7. Nine-model sweep result (s266 — the large sweep, read clean)

Artifacts: `results/opcode-trace/{universal_vsm.json, sweep_summary.json,
per-model dirs}`; log `sweep_large.log`. 9 models (7 large + 2 cached
smalls), 4 architecture families, 14M→32B, full 535-probe calibration ×
2 registers + 3-shuffle floors each.

- **Universal root HOLDS and sharpens with evidence**: root gc = **+0.982**
  vs the bundled 10-model consensus (up from 0.940 at 2 models) | sil_z
  5.09 | bearing 1.00. Families 4/4 gated; cross-family agreement mean
  0.906, min 0.841; dissent = False.
- Family gc: qwen3 0.976 (intra-family agreement 0.982), olmo 0.957,
  gemma 0.935 (**nested arch works in production**), pythia 0.919
  (agreement 0.821 — the weak seam).
- **Scale-sharpening confirmed**: pure qwen3 ladder sil_z is monotone —
  0.6B 4.97 → 4B 5.40 → 14B 6.36 → 32B 6.70. qwen3.6-27B (hybrid, next
  generation) sits off-ladder at 5.94.
- **pythia-2.8b gate register FAILED its null gate** (bearing 0.31,
  gated=False); attn carries the model alone at sil_z 2.34, barely above
  its 2.04 floor — the weakest node in the tree, weaker than pythia-14m.
  Reading: the up-proj proxy **degrades with scale** on ungated archs — a
  real limit on the Pythia crystal-ladder plan. The S3 gate demonstrated
  its design: the failed register stays visible, contributes nothing
  upward.

## 8. Open

- **s266b**: the consensus Gram is now also a SPECIFICATION — supervision
  target for a seeded ternary student. Design:
  `explore/crystal-seeded-ternary-distillation.md` (phase 0 = crystal
  survival on the Bonsai 4bit→ternary→1bit ladder, this tree as the
  instrument).
- QK-pattern register → decisive B/C test (predicted home of {B,C}).
- Visualizer; then extraction of `opcodes/` to its own MIT repo.
- Retro-check the s264 27B floor run (n_perm / pooling) — its
  elevated-attn direction is now the unreproduced anomaly (§5).
- Pythia crystal-ladder plan needs a proxy-degradation answer before
  scaling further up the ungated ladder (§7).
