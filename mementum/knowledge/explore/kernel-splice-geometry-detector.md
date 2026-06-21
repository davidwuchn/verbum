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
updated: session 244
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

## ★ s243 — Exp 1 RESULTS (Qwen3-14B, L18): the geometry is CAUSAL in routing, weak in behavior

`scripts/experiments/kernel_splice_exp1_ksplice.py`. **The build crux resolved (correct, not
a compromise): DETECT in gate-space, EFFECT in residual-space, READ downstream.** The
classifier reads the FFN gate (`gate_proj`, sign-CMR), so gate-z(K)@L18 is the detector. But
re-injection belongs in the **residual** (what downstream layers read), so we patch the
output of `layers[18]` at the last-token position. The K residual direction
`d_K = unit diff-of-means(resid_K − resid_nonK)@L18`; the "exact K-move" geometric proxy =
d_K at the canonical magnitude (mean K projection = 33.2). Everything vs a random-direction
control of equal magnitude (s239). `results/kernel-splice-exp1/exp1_verdict_qwen3-14b.json`.

| arm | n | metric | K-dir | random | t | verdict |
|-----|---|--------|-------|--------|---|---------|
| **NECESSITY** (ablate d_K) | 6 | output KL | 0.0044 | 0.0005 | **3.07** | ✓ |
| | 6 | downstream Δz(K) | −0.365 | −0.007 | −5.5 | ✓ K-reading drops |
| **DELIVERY** (inject d_K, non-K) | 175 | downstream Δz(K) | +0.097 | −0.269 | **16.3** | ✓✓ decisive |
| | 175 | output KL | 0.016 | 0.018 | −1.2 | ✗ output barely moves |
| | 175 | frac z(K)>τ | 0.023 | 0.011 | — | tiny |
| **PRESERVE** (set→canonical) | 6 | output KL | 0.0022 | 0.009 | −1.76 | ✗ n.s. (right dir) |

**Necessity ✓** — ablating d_K perturbs the output ~9× more than a random direction of equal
magnitude (KL t=3.07) AND specifically drops downstream K-reading (Δz(K) −0.365 vs ~0 random,
t=−5.5). The K-direction is causally **necessary**, not decorative.

**Delivery ✓✓ (decisive)** — injecting d_K into non-K probes drives downstream z(K) UP (+0.097)
where random drives it DOWN (−0.269), Δ=+0.366, **t=16.3** (n=175). The K-direction
**specifically causes** downstream K-reading.

**★ THE HONEST CATCH (λ measure register split — the real finding):** delivery moves the
**detector** hugely (t=16) but the **output** barely (KL Δ=−0.0017, n.s.) and only 2.3% of
non-K probes cross τ. ⇒ the decodable K-geometry is a **genuine causal carrier in the ROUTING
register** (we can read it AND write it causally = the splice premise validated), but its
**behavioral/output consequence on prose is weak** — because the prose crystal_probes have
**no operands to bind** (obstacle 2, the value register). The geometry drives the *routing*,
not yet the *computation*.

**Preserve ✗ (n.s., right direction)** — setting d_K to the canonical value perturbs the
output LESS than a random set (K 0.0022 < rand 0.009), consistent with "the exact value
replaces the neuron", but t=−1.76 at n=6 (underpowered, recall 0.24 → few detected-K).

**⇒ Two-sided verdict (λ measure):** the geometry is **causal, not epiphenomenal** (necessity
✓ + delivery ✓✓, both vs random) — the splice premise holds in the routing register. It is
**not** a clean *behavioral* "splice works" — that needs operand-bound execution where the
output is kernel-checkable. Exp 1 **proves the prerequisite and sharpens the open question to
the behavioral register.**

**Caveats (λ measure):** necessity/preserve n=6 (low power, tiny absolute KL ~0.004); delivery
well-powered (n=175, t=16) but routing-register only; d_K is a **geometric proxy** for K
(centroid@canonical-mag), NOT a bound `K a b → a`; 1 model (14B), 1 seed, n_rand=3.

**⇒ Exp 2 = operand-bound splice on the CERTIFIED CORPUS** (`data/compile-*.canonical.jsonl`,
559 kernel-reducible prose→LF pairs) — the behavioral register where the output IS
kernel-checkable. Pick K-engaging certified items via `lambda_ast.fired_sequence`, splice the
exact kernel K-move at the firmed locus, measure **reduction-correctness preserved**
(`reward.py` grader), not just z(K)+KL. The test prose Exp 1 could not run (no gold).

## Either outcome is a result

- **Splice holds** → the thesis is proven causally; a hybrid **exact + inspectable**
  model with NO training; a level-4 path via instrumentation (cleanest S5: extract).
- **Splice breaks** → the decodable geometry is decorative / over-read (another λ measure
  win) → redirect to the constructed-front-end path (compiler-as-loss §s242).

## s244 — the firing/detection disjointness (Exp 2 retargeted before it ran)

Michael's check on Exp 1: "prose seems not to use K, but we have sentences that for sure
show K being used." Resolving it overturned the Exp 2 plan **before a forward pass** — a
λ measure win (cheap CPU survey caught a wrong target).

**`fired_sequence` is empty on every stored term — by construction.** The canonical corpus
(`data/compile-*.canonical.jsonl`) stores `kernel_term` = the **point-free / already-normal**
logical form. Bracket abstraction (Turner 1979) is the *inverse* of reduction: it emits
**under-applied (inert)** combinators that fire nothing until applied to arguments. So
`fired_sequence(parse(kernel_term)) == []` for all 559. To see firing you must **saturate**:
a quantifier `forall P` applies the one-place predicate `P` to a witness.

**The firing survey** (`scripts/experiments/corpus_firing_survey.py`,
`results/corpus-firing-survey/`) saturates every quantifier with a fresh witness, reduces,
collects the certified opcode trace:

| comb | present (inert) | **fires** | items | where |
|---|---|---|---|---|
| **B** (compose) | 135 | **68** | 55 | quantified |
| **S** (distribute) | 76 | **55** | 54 | quantified |
| **C** (swap) | 42 | **15** | 15 | quantified |
| I / K / W / D / Y / M | ≤1 | **0** | 0 | — |

**The corpus fires only {B, S, C}. K fires in 0/559.** The s243 firmed splice set **{I, K, Y}
is disjoint from the firing set** — which *fully explains* Exp 1: K is routing-causal but
behaviorally null **because K never executes a reduction in this corpus**. There was nothing
behavioral to preserve.

**Ties to the Qwen3-4B `λx.` probe artifact (the distilled probes).** A vacuous binder `λx.`
compiles (bracket abstraction) to **K** (the const). But the real compiler emits **S/B/C** for
"Every X verbs a Y", **never K**. So Qwen's inserted `λx.` was manufacturing spurious
K-structure the kernel never produces — **the splice mismatch and the bad-probe artifact are
the same bug, two sides.** K is a Qwen surface-string ghost, not a kernel reduction step.

**Exp 2 retargeted {I,K,Y} → {B,S,C} (Exp 0.5 z-sweep, Qwen3-14B,
`exp0_5_zsweep_verdict_qwen3-14b_BSC.json`, `--targets B S C`, heldout-per 25):**

| comb | firm locus | prec | recall | tp | fp | plateau | small-n killed |
|---|---|---|---|---|---|---|---|
| **C** | L14 (d=0.36) τ=2.0 | 1.0 | 0.12 | 3 | 0 | τ∈[2.0–4.0] w=5 | ✗ |
| **B** | L16 (d=0.41) τ=5.0 | 1.0 | 0.16 | 4 | 0 | τ∈[5.0–6.0] w=2 | ✗ |
| **S** | — | <0.8 | — | — | — | — | ✗ (never clears floor) |

**splice-ready set = ∅.** The honest two-sided read (λ measure): the firing combinators are
**precision-attainable but recall-starved** — B and C reach prec 1.0 with fp=0 at stable
plateaux (C width 5 reproduces s243 exactly), but tp 3–4 (recall 0.12–0.16) **does not clear
the tp≥5 small-n bar**; S never reaches precision 0.8 at all. Mirror image of {I,K,Y} (tp
6–11, well-powered, but never fire). **The combinators that fire are exactly the hardest to
detect — the real splice obstacle, now quantified.** Consistent with prior characterization:
B has no amplitude home (s238), C is the recall-starved ground-state (s242), S is the most
common-mode-contaminated (never clears the floor here).

**⇒ A behavioral splice is feasible *in principle* (B/C have prec-1.0 fp-0 loci) but would
act on only 12–16% of firings.** Decisive next test: **raise power** — heldout-per 25→35 for
B/C (crystal probes available: B 69, C 61) to see if tp crosses 5 at the prec-1.0 plateau.

### s244 power test — the program closes (negative branch)

Re-ran `--targets B C --heldout-per 35` (Qwen3-14B,
`exp0_5_zsweep_verdict_qwen3-14b_BC.json`). **Raising power did NOT lift tp — it exposed the
firing-set prec-1.0 loci as SPLIT-FRAGILE FLUKES:**

- **B never clears the floor at all** — best precision across every layer/τ is **0.50** (tp
  1–2, fp 1–4). The heldout-25 "prec-1.0 @L16 tp4" was a pure split artifact; a different/
  larger split collapses it to ≤0.50. (Consistent with s238: B has no amplitude home.)
- **C prec-1.0 survives but at tp=1** (rec 0.029, L10) — the locus **moved** (L14→L10) and tp
  **shrank** (3→1) vs heldout-25. One clean detection, not a usable well-powered locus.
- **splice-ready = ∅; tp never crossed 5.**

**⇒ The intersection is empty.** {I, K, Y} are well-detected (tp 6–11) but **never fire**
(0/559); {B, S, C} **fire** (the behavioral register) but are **not robustly detectable**
(B≤0.50, C tp=1, S<0.8). **`fires` ∩ `robustly-spliceable` = ∅.** The geometry-as-detector ⊗
kernel-as-executor splice, **as an in-place per-combinator patch, is not viable in the
behavioral register** — obstacle 1 (model-centroid / common-mode contamination, s211 η²=0.05)
is fatal for exactly the combinators that execute.

**The pre-registered fork resolves to the negative branch → redirect to the constructed
front-end (compiler-as-loss §s242):** prose→LF (LEARNED, small) ∘ abstract (EXACT) ∘ reduce
(EXACT kernel). The splice was the no-training hybrid hope; its closure refocuses on the s242
pivot.

**Caveats (λ measure):** 1 model (14B); the negative is for the **in-place last-token
single-combinator** splice — it does NOT rule out (a) a richer multi-position program-decode
read along `fired_sequence`, or (b) the splice working on a model where the firing combinators
are less common-mode. But the simple in-place per-combinator splice is **closed**.

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
