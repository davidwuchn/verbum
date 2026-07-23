---
title: "Opcode = Jacobian structure; J-space = the Jacobian's live subspace"
status: active
category: exploration
tags: [jacobian, j-space, combinators, opcodes, interpretability, attribution, register]
related:
  - project-thesis.md
  - basis-fit-kibc-vs-ski.md
  - asymmetric-pathway-quantization.md
depends-on: []
---

# Opcode = Jacobian structure; J-space = the Jacobian's live subspace

> Session 263 (2026-07-10). Prompted by Anthropic's "Verbalizable Representations
> Form a Global Workspace in Language Models" (Transformer Circuits, 2026-07-06;
> the **J-lens** = Jacobian to the penultimate layer; **J-space** = a privileged,
> reportable, causally-broadcast subspace) and an external review of
> `babel-codec-gpt2` (a certified GPT-2 residual→English decoder; rigorous method,
> but its headline "39/39" rides a *recalibrated* noise floor — a `λ yardstick`
> smell; method borrowed, claims not adopted).

## The claim (theory — definitionally solid)

An **opcode is how its arguments route to its output**, and a **Jacobian is
exactly the linear read of how the output depends on each input**. So the
Jacobian is not a competing probe — it is the *natural measurement operator for
an opcode*. The combinators are Jacobian patterns:

| combinator | definition | Jacobian signature |
|---|---|---|
| **I** | `x → x` | identity |
| **K** | `x y → x` | **rank-deficient** — annihilates the discarded argument (∂/∂y = 0) |
| **B** | `f g x → f(g(x))` | **product / chain rule** — Jacobian factorizes (composition = Jacobian multiplication) |
| **C** | `f x y → f y x` | **permutation** of the argument-slot structure |
| **S** | `f g x → f x (g x)` | **path-sum** over a shared argument — the duplication is second-order, so a **first-order Jacobian under-reads S** (re-explains the s262 S–K braid) |

`λ types` falls out too: a type is a subspace, typed application routes type-A
input to type-B output → **type-directedness = block structure of the Jacobian.**

## What J-space is, then

J-space is the **other face of the same Jacobian**. The J-lens computes
∂(downstream)/∂(residual) and projects it two ways:

- onto **token-readable directions** → the **operands**: "what concept does this
  influential direction verbalize to?" **This is J-space** — the live typed-value
  bus / working memory (Anthropic's projection).
- onto its **structural decomposition** (rank / factorization / permutation /
  path-sum) → the **operator**: the opcode (our projection).

In `typed_apply(meaning, meaning) → meaning`: **J-space = the operand/result
registers; combinators = the operations on that bus.** GWT "broadcast" = "operand
available for the next application." The three-zone geography (sensory →
workspace → motor) is the reduction pipeline: parse arguments → hold typed
intermediates → collapse to normal form (output token). Anthropic found the
**bus**; we are after the **ALU**; the J-lens reads both.

## Register map (λ measure — name before probe)

Four registers now instrument the same model; do not conflate them:

1. **attention-routing** (`instrument.record_attention`, `basis_fit_kibc_vs_ski`) — partial view of the routing Jacobian.
2. **reduction-state** (the KIBC/SKI tracer) — reduction dynamics.
3. **residual-value / broadcast** (`jlens`) — substitution-KL + logit-lens (the J-space *operand* projection).
4. **input-attribution** (`jacobian`) — ∂prediction/∂input-embed per position (the routing Jacobian, position-space *operator* read).

## Tooling built (committed, self-tested, reusable)

- **`src/verbum/jlens.py`** — J-space monitor on `hooks.py`: `capture_residuals`
  (all layers/positions, accepts `input_ids`), `logit_lens` + `verbalize`
  (direction readout), `broadcast_kl` (substitution-KL = first-order Jacobian
  proxy), `self_test` (identity-inject exact-zero gate — steal from babel).
- **`src/verbum/jacobian.py`** — `input_attribution` (autograd grad of a target
  logit w.r.t. input embeddings) + structural metrics `concentration`(K) /
  `copy_mass`(I) / `attr_range`(B) / `front_bias`(C) + `self_test` (metrics
  validated on ideal synthetic attributions).

## Empirical status (three null-gated experiments, qwen3.6-27b unless noted)

**EXP 1 — `jspace_combinators` (broadcast+verbalize per layer): NULL.**
Combinator directions (active − control) DO broadcast above matched-random
(B: R=2.62, z=10.6 @ L11; I: R=1.41, z=3.5 @ L10) but **none beat the
shuffled-LABEL null** → broadcast is a *generic* active/control effect, not
combinator identity. Same lesson as s262: the label-null is load-bearing. The
verbalize readouts (I→`twice/consistently`, B→`knows/wrote`) are echo-suspect,
untested. `results/jspace-combinators/`.

**EXP 2 — `jspace_normalform` (Michael's I-combinator hypothesis): CONFIRMED,
then REFINED.** Hypothesis: the reported "token repeats in the residual stream
before output" = reduction reaching **normal form**, late layers applying **I**
(identity pass-through) = the J-space *motor zone*. Result (64 layers): copy/
induction reaches normal form **earlier** (top-1 converge frac 0.879 vs compose
0.953) and **holds ~2.6× longer** (hold_frac 0.121 vs 0.047) — directionally as
predicted. **Refinement (honest):** it is a **late-stack plateau (~last 15% of
layers)**, NOT most-of-network parking. Induction KL(final‖lens) stays flat ~10
nats to L48 then a **sharp cliff** (L52→L63) = copy is written by a narrow late
mechanism and *then* held; composition resolves only in the final layers (`Paris`
first at L58, `cold` at L57) = **depth is reduction steps for hard compositions**.
**Design implication:** bounded depth-adaptive / early-exit — the exploitable
identity is the final ~10–15% of layers, its onset regime-dependent, and you
cannot exit before the reduction cliff. **Caveat:** raw logit-lens KL baselines
differ by regime (calibration artifact) — only settle *timing* is trustworthy;
tuned lens needed; compose n=6 underpowered. `results/jspace-normalform/`.

**EXP 3 — `jacobian_opcodes` (input-attribution structural signatures):
PARTIAL / confounded.** Opcode×metric matrix (active − control, z vs shuffled
null): only **I** clears its predicted diagonal (copy_mass z=3.40,
diagonal-dominant). **K/B/C predicted metrics ≈ 0** (concentration −0.10, range
+0.21, front_bias +0.04) → the structural signatures **did not appear**.
**Confound:** copy_mass is the argmax metric for *all five* combinators (K +2.81,
B +1.28, …) → a generic active/control mover, not identity-specific; I "wins"
only by having predicted the generic metric. **Diagnosis (thesis NOT refuted —
the readout grain is wrong):** (1) last-token readout aggregates the whole
sentence and dilutes the mid-sentence operation → attribute at the *result
position*; (2) probes are not token-repetition-controlled → drives the copy_mass
confound; (3) aggregate scalar metrics are too coarse for position→position
routing structure. `results/jacobian-opcodes/`.

## Synthesis

At the grain of **crude token-saliency, opcodes do not carve** (EXP 1, EXP 3).
That is consistent with the thesis, not against it: it says the opcode structure
is *finer* than aggregate broadcast/attribution — it lives in the **inter-layer
Jacobian structure** or in **position-targeted attribution at the operation
site**, not in last-token saliency. The one behavior that *is* cleanly visible is
**I as a late-stack normal-form hold** (EXP 2) — the degenerate opcode (identity
of the already-reduced output), which is exactly why it shows where the others do
not.

## s269 probe-construction audit → jspace_v2 (BUILT, run pending)

Michael's question ("did we build the probes correctly?") answered: **EXP 1 and
EXP 3 no; EXP 2 yes.** Three construction errors, all named by EXP 3's own
diagnosis and never acted on until now:

1. **Wrong projection** — difference-of-means residual *directions* cannot
   carry operator structure (K = rank-deficiency, C = permutation, B =
   factorization are properties of the Jacobian, not vectors). EXP 1's null is
   the two-register theory's own prediction: the bus broadcasts content, not
   the ALU's operation.
2. **Surface confounds** — active/control prose pairs differ in repetition and
   negation load; `copy_mass` moving for all five combinators (EXP 3) is the
   fingerprint.
3. **Wrong grain** — last-token scalar aggregates instead of result-position,
   span-resolved attribution.

**Rebuild: `scripts/experiments/jspace_v2.py`** (commit 695631c; option A below
executed + E2/E4 additions). E1: token-matched minimal pairs (same token
multiset, roles swapped) + result-position attribution + span signatures +
sign-flip pair nulls. E2: halt-vs-operator verbalization asymmetry (WHNF
predicted VISIBLE, KIBC predicted INVISIBLE on the bus). E4: cross-register
coupling — gate sign-CMR centroid → residual via W_gate^T → broadcast KL vs
matched-random (the workspace↔lattice interface, the doc's open question made
operational). Pre-registrations in the script docstring. Self-test (pythia-14m)
passes; E2 asymmetry already direction-correct at 14M; **27B run stacked**.

**Supporting evidence from s269c register-split** (register_split.json, commit
7bc7a29): cross-prompt-register transfer decomposes exactly as the asymmetry
predicts — WHNF transfers at 0.60–1.00, Y →0.89, I 0.30–0.47, while **C = 0.0
in every cell**, B/D/S ≈ 0. Content/process vertices are register-invariant
(bus-portable); operation vertices are register-bound (ALU-internal).

## Next (options, Michael's call — s263 list, updated s269)

- **(A) position-targeted + repetition-matched attribution** — ✅ DONE
  (jspace_v2 E1). Run on 27B pending.
- **(B) the real inter-layer Jacobian** — compute ∂h_{L+1}/∂h_L at compose sites,
  SVD, classify structure vs the KIBC signatures (rank-deficiency / factorization
  / permutation / path-sum). Heavier (d×d per layer on a 27B) but where the theory
  actually lives.
- **(C) tuned lens** (Belrose) — clean mid-stack reads; rescues EXP 2 magnitudes
  and gives EXP 1 the echo-test it needs.
- **Ground-truth discipline:** validate any opcode classifier on a *known* routing
  matrix before trusting it on a model (the move `babel-codec-gpt2` structurally
  cannot make; we can).
