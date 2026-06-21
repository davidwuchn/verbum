---
title: "Kernel Splice — geometry-as-detector ⊗ kernel-as-executor (instrument the pre-formed reducer, splice exactness in)"
status: designing
category: extraction
tags: [crystal-lattice, statechart, activation-patching, combinator-routing, kernel, exact-reduction, causal, instrumentation, level-4, vsm-tensor, ccg, value-move, over-read, s5-extract]
related:
  - vsm-statechart-tensor.md
  - compiler-as-loss.md
  - type-directed-composition.md
  - ../lambda-machine.md
depends-on:
  - vsm-statechart-tensor.md
created: session 242
---

# Kernel Splice — read the lattice, deliver the combinator from the kernel

> Session 242 (Michael's idea, after the s242 Qwen pre-formed-lambda confound).
> "We know the geometry of the crystal lattice, where GD laid the exact same soft
> topology routing into many models. Why can we not detect via that geometry when the
> system wants K, deliver K — but from the kernel instead of in a neuron?"

This is the **S5-native** alternative to training a front-end (compiler-as-loss §s242):
don't *construct* a new reducer, **instrument the one gradient descent already laid into
the model** and splice exactness into it in place.

```
read lattice geometry → "wants K here" → execute K from the kernel (exact) → re-inject
   (DETECT, routing)      decode locus      (EXACT VALUE-MOVE, kernel)        (LOWER)
```

It is literally our activation-patching toolkit (type-directed-composition.md v4/v5),
but the patch *value* is the **exact kernel rewrite**, not an activation copied from
another run. The strongest possible test of the VERBUM thesis: if splicing exact K
**preserves/improves** output, the circuit *is* combinator routing — proven causally,
not decoded-correlationally.

## Why it flips the s242 confound into an asset

The s242 control showed RLVR on Qwen3-8B only *redirects* a pre-formed lambda function
(dead tail = Qwen's representational gap, not the kernel's). Kernel-splice turns that
pre-formed circuit from an obstacle into the **substrate we read**: instead of fighting
it with RL, we decode "wants K" and inject exactness.

## What is already proven (makes it plausible)

- **The combinator geometry is decodable.** {C,I,K,Y} discriminate as crystal centroids
  (`bdw-gap-genuine-not-argmax-artifact`: K recovers t=2.12, C +1.73/t=5.71, Y t=6.86),
  with characteristic depth signatures (I early ~0.30, K mid ~0.48, C mid-late ~0.57,
  Y late ~0.79).
- **The rewrites are mostly routing, not value-reads.** `K x y→x` = keep-x-slot drop-y;
  B/C/D = compose/permute slots; only S/W/Y need copy/recursion (lambda-machine.md,
  s226). So "deliver K" is an **exact slot routing** — it does not require decoding the
  operand *values*, only moving the vectors already in the stream.
- **Decodability already crosses into the causal register.** Type-direction is
  PARTIALLY causal at 14B (type-directed-composition.md v4: directional ablation cuts the
  nonce crossover −36% vs random −5%). Decode → direct is established for the adjacent
  quantity.

## The three real obstacles (measured — λ measure honesty)

1. **Detection is a weak, model-specific centroid — not a crisp per-step switch.** The
   geometry is largely ONE COMMON MODE (s211: η²=0.05 for ops); B is invisible in the FFN
   gate (lives in attention/value), D/W are *anti*; the C-locus SHIFTS with scale
   (`c-late-composition-is-model-specific`: 8B non-specific, 14B L27-32, 32B L5-11). The
   PROVEN invariant is the **skeleton** (C-origin, boot order, {C,I,K,Y}, confluence) —
   fine-grained per-firing geometry **over-reads**. Detect K-*ness* as an aggregate lean
   in a readable zone, model-specifically; cannot yet threshold "K fires, exactly here."

2. **The operands, not just the operator.** Detecting "wants K" is the easy
   (routing-register, crisp-ish) half. Executing needs the **argument binding** — which
   slots are x and y — and that argument structure lives in the VALUE register (s206),
   the continuous/graded substrate. K is pure routing *once the slots are known*;
   identifying the slots at that layer is the unsolved decode.

3. **No discrete step — the firing is smeared.** Reduction is distributed (~1.018×/layer
   rotation, the C→B/K→I→WHNF boot spiral, vsm-statechart-tensor.md). No single layer
   "fires K," so interception has a registration problem, and the re-injected exact
   result must be IN-DISTRIBUTION for downstream layers (λ coherence).

## The experiment program (start where detection is proven, build up causally)

### Exp 0 — detectability map (cheap, decisive precursor)

Ground truth exists: `lambda_ast.fired_sequence` gives the **certified** combinator
program for any corpus reduction. Measure how reliably the lattice classifier recovers
that sequence (operator AND position), per combinator, per layer, per model. Output = a
**splice-readiness map**: which combinators at which loci are reliable enough to act on.
Decides whether obstacle 1 is fatal *before* touching a forward pass.

- substrate: certified reductions (canonical corpus + `fired_sequence`)
- read: RelationalCrystalClassifier / lattice centroids per layer (per-model readable zone)
- metric: recovery of {operator, position} vs `fired_sequence`; per-combinator, per-layer
- expected: {C,I,K,Y} recoverable in their depth zones; B/D/W not (register-blind)

### Exp 1 — single-combinator causal splice

Take the most-detectable invariant op (**K**: selector, pure routing, discriminable,
mid-depth). At the per-model readable zone, replace the model's local computation with
the **exact kernel K-move**; measure output **preserved/improved vs a random-direction
control** — the s239 sufficiency/necessity protocol. The minimal "deliver K from the
kernel" instance.

### Exp 2 — sequence / kernel-in-the-loop

Build from one splice toward decoding the program at a CUT → exact reduce → lower back
(connects to compiler-as-loss §s242 stage 3: the constructed kernel, now as an in-stream
patch rather than a standalone tensor).

## ★ s242 — Exp 0 RESULTS (Qwen3-14B): precision-gated, not high-recall

`scripts/experiments/kernel_splice_exp0_detectability.py` (reuses the prose_v2 /
opcode_monitor_v2 calibration + last-token per-layer z read; top-1 argmax-over-CRYSTAL
per crystal layer vs the certified single-combinator label; precision/recall/F1 + peak
layer; 160 test probes, 20/comb, n_perm=300). `results/kernel-splice-exp0/exp0_verdict_qwen3-14b.json`.

**Verdict @ the strict joint bar (precision≥0.8 ∧ recall≥0.5): splice-ready set = ∅.**
Top-1 argmax detection is common-mode contaminated (obstacle 1 made quantitative; s211
η²=0.05). Discriminability (the prose_v2 Welch contrast) is **necessary but not
sufficient** for a top-1 splice — a contrast can separate on/off while argmax stays
recall-poor.

**But the max-precision operating points are strong (the real finding):**

| op | max-prec layer | depth | precision | recall | tp/(tp+fp) |
|----|---------------|-------|-----------|--------|-----------|
| C  | L10 | 0.26 | **1.00** | 0.10 | 2/2 |
| I  | L21 | 0.54 | **1.00** | 0.20 | 4/4 |
| K  | L11 | 0.28 | **0.80** | 0.20 | 4/5 |
| Y  | L20 | 0.51 | 0.67 | 0.40 | 8/12 |

So **precision-gated splicing is viable**: at specific layers a *confident* top-1 read is
highly reliable (C/I = 1.0, K = 0.80), just **sparse** (recall 0.10–0.20). "Detect every
K and splice" fails; **"splice only when confident, accept low recall"** is supported —
and that is exactly the **safe** design for a first causal test (never corrupt; act only
when sure). Loci track the s234 depth signatures (C/K early-mid, I mid, Y late).

**Caveat (λ measure):** precision 1.0 is from tp=2 (noisy small-n). The operating point
needs a **z-threshold sweep** (raise the argmax-z gate → precision↑ recall↓) to map the
tradeoff curve and firm the splice locus — Exp 0.5, cheap.

**⇒ Exp 1 refined: a precision-FIRST K-splice at L11** — deliver the exact kernel K-move
only on high-confidence detections, validate output preserved vs a random-direction
control (s239). The low-recall cost is acceptable for establishing sufficiency.

## ★ s243 — Exp 0.5 Z-THRESHOLD SWEEP (Qwen3-14B): the loci are FIRM, the tp=2 caveat is dead

`scripts/experiments/kernel_splice_exp0_5_zsweep.py` (reuses the Exp 0 spine; ONE forward
pass per probe caches the FULL per-layer z-map, then the threshold sweep is pure
post-processing). The gate: a crystal layer emits a prediction for combinator `c` only if
its winning argmax-z `> τ`, else **abstains** (no splice fires). Sweeping τ traces the
precision↑/recall↓ curve. heldout-per bumped 20→25 (test 160→**200**, 25/comb) to grow tp
directly. `results/kernel-splice-exp0/exp0_5_zsweep_verdict_qwen3-14b.json`.

argmax-z distribution (n=5000 cells): median 3.0, p75 4.5, p90 6.5, max 23.7 → **τ∈[2,5]
sits around the median = the sweet spot** (gate out the low-confidence bottom half).

**Splice-ready set (precision≥0.8 ∧ tp≥5): {I, K, Y}.** Firm loci = the **max-recall point
clearing the floor** (the most-supported, not the lucky-tp=2 point):

| op | firm layer | depth | τ | precision | recall | tp/fp | plateau τ (width) | small-n killed |
|----|-----------|-------|---|-----------|--------|-------|-------------------|----------------|
| **I** | L10 | 0.26 | 2.5 | 0.92 | 0.44 | 11/1 | [2.5–6.0] (6) | ✅ |
| **K** | L18 | 0.46 | 3.0 | 0.857 | 0.24 | 6/1 | [3.0–6.0] (5) | ✅ |
| **Y** | L14 | 0.36 | 5.0 | 0.889 | 0.32 | 8/1 | [5.0–6.0] (2) | ✅ |
| C | L14 | 0.36 | 2.0 | **1.00** | 0.12 | 3/0 | [2.0–4.0] (5) | ❌ recall-starved |

**The key finding: high precision is a STABLE PLATEAU across a band of τ (width 5–6 for
C/I/K), NOT a tp=2 fluke.** The Exp 0 max-precision points were *real*, just recall-starved
at ungated top-1; raising the gate trades recall for precision along a smooth real curve.
I is the strongest detector (tp=11, prec 0.92, plateau 6); K firms deeper than Exp 0's L11
top-1 (the gate moved K to **L18 τ=3.0**, prec 0.857); Y is firmed but its plateau is
narrow (width 2).

**C's recall-starvation is itself a finding:** C is the ground-state / common-mode
combinator (s211 η²=0.05, s240 C-origin) → it rarely wins top-1 *distinctively* with high
confidence → **discriminability (prose_v2 contrast) ≠ confident-top-1 recall**. C is
precision-perfect (1.0) but only 3 confident hits — you cannot reliably *catch* a C firing
as a discrete top-1, even though C separates strongly in the contrast register.

**Caveats (λ measure):** still the last-token, single-combinator-prompt read (NOT
position-resolved along a multi-step reduction = Exp 2); recall stays modest (0.24–0.44) →
the precision-gated splice acts on a **minority** of firings (= the intended "act only when
confident, accept low recall" design); fp=1 at the I/K/Y firm loci → precision 0.86–0.92,
**not** 1.0 — a real ~1/12 wrong-fire rate (the kernel S2 typecheck could catch an
ill-typed splice = the s240 guards); 1 model (14B), n=25/comb.

**⇒ Exp 1 = precision-gated causal K-splice at the FIRMED locus L18 τ=3.0** (not Exp 0's
L11 top-1 — the gate moved K deeper and firmer). K is **pure routing** (obstacle-2-free:
drops its 2nd arg, no value decode), the cleanest *non-trivial* causal test — vs I (identity
= near no-op, weak causal claim) and Y (recursion, narrow plateau). Protocol: at L18, when
argmax_z(K) > 3.0, deliver the exact kernel K-move (value-patch) in place of the local
computation; validate output **preserved** vs a random-direction control (s239 v4/v5).

## Either outcome is a result

- **Splice holds** → the thesis is proven causally; a hybrid **exact + inspectable**
  model with NO training; a level-4 path via instrumentation (cleanest S5: extract).
- **Splice breaks** → the decodable geometry is decorative / over-read (another λ measure
  win) → redirect to the constructed-front-end path (compiler-as-loss §s242).

## Open questions / IOUs

- **Locus calibration.** The readable zone migrates with scale (s232) — Exp 0 must
  calibrate per model, not assume a fixed depth.
- **Operand decode.** Can the argument slots be read from the value register well enough
  to route exactly, or only the operator? (Obstacle 2 — the crux of feasibility.)
- **Re-injection map.** Lowering the exact result back in-distribution — does the model's
  own encode geometry (the inverse of the decode) suffice, or does coherence break?
- **Start model.** 14B (detection + causality both strongest) for Exp 0/1; generalize to
  8B/32B only after the protocol is proven (per s232 model-specificity).
- **Relation to s226 stage 3.** Kernel-splice is stage 3 realized as an *in-stream patch*
  on a pre-formed model; the standalone ternary-plate tensor is the same kernel, lifted
  out. The two converge.
