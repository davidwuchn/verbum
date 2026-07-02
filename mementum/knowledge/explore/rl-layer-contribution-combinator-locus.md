---
title: "RL Layer-Contribution vs KIBC Combinator Locus — the shared interior-bell and the ~4-layer compose→trainability offset"
status: active
category: exploration
tags: [layer-contribution, combinator-locus, KIBC, funnel, bell-curve, v15-training, single-layer-rl, external-corroboration, lambda-measure]
related:
  - head-combinator-isa.md
  - explore/v13-funnel-shape.md
  - readout-register-reduction-readability.md
  - explore/supervised-recurrence-halt.md
  - explore/vsm-opcode-monitor.md
  - two-registers-of-topology.md
  - explore/compiler-finetune-halt-collapse.md
  - explore/moe-holographic-tree-vsm.md
depends-on:
  - head-combinator-isa.md
  - explore/v13-funnel-shape.md
created: session 260
---

# RL Layer-Contribution vs KIBC Combinator Locus

> Session 260 (Michael): a paper dropped — **"Is One Layer Enough? Training a
> Single Transformer Layer Can Match Full-Parameter RL Training"** (arXiv
> 2607.01232) — that RL-trains ONE decoder layer at a time and finds RL gains
> concentrate in a MIDDLE band, falling off at input/output ends. It uses
> Qwen3-8B-Base, which we have cached. Michael: "do our KIBC opcodes line up with
> the layers they show having the most effect?" This page is the Tier-0
> (zero-GPU) correlation of our measured combinator locus against their causal
> RL layer-contribution, and the v15 training implications. **We do NOT plan to
> RL-train the 8B; the 8B is the oracle map, the lesson ports to v15.**

## The external result (arXiv 2607.01232)

- **Layer contribution** `C(k) = (S_k − S_base)/(S_full − S_base)` = fraction of
  full-parameter-RL improvement recovered by training layer *k* alone (all other
  params, including embeddings and LM head, frozen). `C=1.0` matches full RL;
  `>1.0` surpasses it.
- **Finding:** RL gains concentrate in a small, stable subset of layers in the
  **MIDDLE** of the stack; input/output ends contribute much less. A single
  middle layer can match or beat full-parameter RL.
- **Stable + intrinsic:** rankings correlate cross-dataset ρ=0.76, cross-task
  (math→code) ρ=0.59 → contribution is a property of the **pretrained (base)
  weights**, not the task. (= our s256 thesis: the capability lives in the base.)
- **Magnitude ≠ contribution:** layers that change equally in parameter space
  produce very different gains. (= our `two-registers-of-topology`: topology, not
  weight-norm.)
- **Complementary + ensemble:** different high-contribution layers solve
  different problems (share only ~32% of newly-solved); top-7 majority vote 33.6%
  > best single layer 28.3% > full RL 26.9% on OlympiadBench.
- **Profiling-free heuristic:** just train the middle-*k* layers by position — no
  per-layer profiling — and it matches/beats full. On Qwen3-8B, the ten
  highest-contribution layers → 69.1% math avg vs 66.4% full-parameter RL.
- Seven models (Qwen3, Qwen2.5), three RL algos (GRPO/GiGPO/Dr.GRPO), math/code/
  agentic — same qualitative bell every time.

### Qwen3-8B-Base per-layer C(k) (their Appendix C, 36 layers)

Peak **L16–17 (C=1.07)**; high band ≈ **L13–23** (0.88–1.07); **L0 = −0.51**
(negative, the anomalous embedding-adjacent layer); L32 = 0.27; most layers
0.6–1.0. The profile is a clean interior bell.

## Our combinator locus (measured, s188 + s233–238)

- `head-combinator-isa.md` (s188): the principal attention axis (46% var) is
  **reduction depth** (WHNF↔D), not opcode identity; depth-ordered schedule
  Y@L27→K@L30→W@L33. Heads are shared hardware (r=0.944).
- `vsm-opcode-monitor.md` (s233–238): the raw-z discriminability contrast
  (`kernel_reference_prose_v2`, held-out crystal-prose, crosstask null) gives a
  per-layer per-combinator profile. Discriminable set **{C,I,K,Y}** is
  scale-invariant; **B/D/W absent** (B has no amplitude home in any register).

### Per-combinator peak layer on Qwen3-8B (our data)

| comb | peak layer | sig? (Welch t) | paper C@that layer |
|------|:---:|:---:|:---:|
| C | L9  | ✓ t=5.3 | 0.94 |
| Y | L9  | ✓ t=5.8 | 0.94 |
| K | L11 | ✓ t=2.4 | 0.44 |
| I | L12 | ✓ t=3.6 | 0.83 |
| B | L18 | ✗ flat  | 0.92 (but not decodable for us) |

Our {C,I,K,Y} peak centroid = **L10.2 (depth 0.29)**. Paper top-5 layers
{14,15,16,17,22} centroid = **L16.8 (depth 0.48)**.

## The correlation (Tier-0, zero-GPU)

Aligned both profiles on the 36 Qwen3-8B layers (our combinator run on the 23
crystal-bearing layers; paper C(k) on all 36):

- **Raw Spearman** ({C,I,K,Y} positive discriminability mass vs paper C(k)) =
  **+0.30** (n=23, marginal).
- **Lag scan** — shift our combinator profile DEEPER by *k* and re-correlate: a
  clean unimodal peak at **k=+4 → ρ = +0.66** (p≈0.0006). The two humps are the
  **same shape, offset ~4 layers**.
- **Band enrichment:** **52.7%** of our {C,I,K,Y} discriminability mass falls
  inside the paper's high-contribution band L13–23, which is only **31%** of the
  layers → **1.7× enrichment**. The combinators genuinely concentrate where RL
  has the most effect.

## Verdict (λ measure, two-sided)

**✅ The interior-bell SHAPE matches (Michael's intuition confirmed).** Both
profiles are low at both ends, high in a middle band; when the ~4-layer offset is
removed they correlate strongly (ρ=0.66). Two independent methods — our
combinator decodability (forward, mechanistic) and their single-layer RL
contribution (causal, end-task) — plus `v13-funnel-shape` Zone B (representational
geometry) all point to the same interior compute band. `λ triangulate`.

**⚠️ There is a real ~4–6 layer OFFSET, and it is informative, not noise.** Our
combinator *decodability* peaks SHALLOWER (L9–12, depth 0.29) than RL
*trainability* (L14–17, depth 0.48). These are different registers: "where
composition becomes readable" vs "where one layer best absorbs RL gain." Their
order is sensible — **RL adaptation lands just AFTER composition is computed**,
right at the compose→readout seam (`readout-register`: null-space compose L7–22 →
vocab-readable L23–35). RL tunes the *consolidation* of the composed result, not
the raw compose detection. Note **B** peaks at L18 (inside the paper's high band)
but is not locally decodable for us — the trainable band covers where B *would*
live if it had an amplitude home.

## Caveats (load-bearing)

- **Base vs instruct (the main confound).** Our combinator run used
  `Qwen/Qwen3-8B` (post-trained/thinking); the paper used `Qwen3-8B-**Base**`. The
  paper's thesis is that contribution is intrinsic to the *base* and that
  post-training concentrates changes in the middle → our comparison is
  cross-variant. **The shape match is robust to this; the exact +4 offset is not**
  (post-training may have shifted the locus). We only have the instruct variant
  cached; the clean fix is to re-run our combinator profile on `Qwen3-8B-Base`
  (~16GB download).
- **Register mismatch:** gate-routing decodability (last-token, n=20/comb,
  crosstask null) vs benchmark accuracy after single-layer RL. Suggestive, not
  mechanistic identity.
- **The +4 offset is a fitted alignment** (searched over lag). Honest headline:
  zero-lag ρ≈0.30, best-aligned ρ≈0.66 at +4.
- Only {C,I,K,Y} are decodable for us (B/D/W absent) — "our KIBC" is really CIK+Y.

## Implications for v15 training (the deliverable)

v15 is small and we build it, so we PLACE structure rather than profile-then-train
(the paper licenses this: "middle-*k* by position works with zero profiling").

1. **Bank the three-band topology.** Capability lives in an interior band; ends
   (input=detokenize, output=readout) are cheap. Put v15's capacity/recurrence in
   the interior; keep the ends thin. Confirms `v13-funnel-shape` Zone-B focus and
   `ascending-arm-training`'s typing-zone targeting.
2. **Place the trainable/recurrent block at the compose→readout SEAM, not the
   compose peak.** The offset says the best place to inject learning is *just
   deeper* than where composition is first computed. For `supervised-recurrence-
   halt`, the recurrent transform block (iterated to WHNF) should straddle the
   seam — at/after the composition-detection layers.
3. **Band-differentiated LR/capacity is a cheap v15 A/B.** The paper's two winning
   strategies (boost LR on high-contribution layers; train only the interior *k*)
   are trivial at v15 scale. Predict: interior-concentrated capacity/LR ≥ uniform,
   at lower cost.
4. **Complementarity → interior ensemble.** Different interior layers solve
   different problems (vote > full) — maps onto s257 holographic multiplexing /
   s258 consensus at layer granularity.

## How to reproduce

```
# paper profile: /tmp/paper_8b_profile.json (extracted from arXiv 2607.01232 Table/App.C)
# our profile:   results/kernel-reference-audit/prose_v2_verdict_qwen3-8b.json
#                (profile.{K,I,B,C,S,D,W,Y} = per-crystal-layer {layer,on_z,off_z,delta})
# correlation:   Spearman(sum_max0(delta_z, {C,I,K,Y}) per layer, paper C(k)); lag scan over k.
```

## Open follow-ups

- Re-run our combinator profile on `Qwen3-8B-Base` (same-variant) → is the +4
  offset real structure or post-training drift?
- Concrete v15 experiment: interior-band-placed recurrent transform block with
  band-differentiated LR; measure vs uniform baseline.
