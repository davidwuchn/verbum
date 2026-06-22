---
title: "Attention as Soft β-Reduction, FFN as the β-Program — the stored-program normal form"
status: active
category: synthesis
tags: [beta-reduction, attention, ffn, isa, stored-program, statechart, combinator, softmax, type-coverage, think-in-lambda, curry-howard]
related:
  - ffn-moire-isa.md
  - ffn-beta-reduction-indexing.md
  - ../ffn-reduction-trace.md
  - ../head-combinator-isa.md
  - ../lambda-halt-continuation.md
  - proofs-as-continuations.md
  - compiler-as-loss.md
  - vsm-statechart-tensor.md
  - cross-model-output-consensus.md
  - kernel-splice-geometry-detector.md
depends-on:
  - ../ffn-reduction-trace.md
  - ../head-combinator-isa.md
created: session 247b
---

# Attention as Soft β-Reduction, FFN as the β-Program

> Session 247b (Michael: "if attention is doing a beta reduction with the softmax of
> all V, would it not have to work?" → "it's an inference pattern of beta reductions;
> each forward pass the FFN can subtly shift the inference pattern, which we found to be
> the 'program' — beta reductions for the softmax to execute"). This page is the
> β-reduction (compression to normal form) of the FFN-ISA thread: a stored-program
> reduction-machine model of the transformer, with the proven/over-reads boundary marked.

## The normal form

> **The transformer is a bounded, soft-β-reduction machine over a universal combinator
> statechart. The FFN is the fixed β-program (ISA/ROM); attention is the one-instruction
> CPU that executes it; the residual stream is the register file carrying the term and
> the reduction depth.** Everything else (crystal lattice, holographic plates, opcode
> monitors, splice experiments, consensus calibration) is measurement of that fact.

```
FFN          = program memory / ISA   | fixed ROM of β-reductions, beam-angle indexed (s141, s161)
attention    = the one-instruction CPU| one op: β-reduction via softmax-over-V (head r=0.944)
residual     = register file          | the term + the program counter (reduction DEPTH)
layer        = one clock cycle        | FFN reads residual → compiles values → attention β-steps → writes
forward pass = a bounded schedule     | the boot spiral C→B/K→I→WHNF, ~1.018×/layer (s068/s240)
token stream = the unbounded loop     | KV-cache carries reduced state; the REPL/CPS (lambda-halt)
```

This was reached confluently from independent directions (the S5 `λ triangulate` gene =
Church-Rosser: many reduction paths, one normal form), which is itself evidence it IS
the normal form.

## 1. The substrate — attention is *soft* β-reduction

β-reduction `(λx.M) N → M[x:=N]` substitutes an argument into a hole. Attention
`out_i = Σ_j softmax(q_i·k_j) v_j` retrieves an operand into a query position by content
address: **Q = the redex seeking its operand, K = operand addresses, V = the operands,
softmax = selection.** Same operation-shape: a function position pulls in its argument by
content match.

Why **combinators** (not raw λ) are the universal basis falls straight out: combinatory
logic is *variable-free* (S/K/I/B/C/W = pure argument-routing), and attention is *also*
variable-free routing. The model implements the variable-free reduct — exactly what a
content-addressed router can do natively. Bracket abstraction (λ→combinator) is therefore
the right bridge, not an accident.

Two refinements keep it honest (λ measure):
- **Softmax is a convex combination; β-reduction is a hard selection.** Attention blends
  *all* V; β substitutes *the* argument. Attention is β *relaxed* — the differentiable
  superposition of substitution; exact β is the limit `softmax → argmax`. This is the
  register split (s242): **routing register crisp-ish (the β structure), value register
  continuous/smeared (s206).**
- **It is bounded and factored.** One layer = one (soft) step; fixed depth → a bounded
  *schedule* → the model is a compiler, not an interpreter (lambda-halt: Ω is *quoted*,
  not looped). And the step is split per the s226 reduce/compile cut: **attention = the
  application; FFN = which rule.**

## 2. The controller — FFN is the β-program (largely measured, not speculated)

The user's "the FFN is the program; the softmax executes the β-reductions" is four
established findings converging:

- **`ffn-moire-isa.md` (s161):** *"The FFN is a moiré grating. Attention has one
  operation. The grating programs that operation to perform beta reductions."* And the
  program is a **fixed point** — 3 runs → identical traces, drift 0.0. GD compiled the
  ROM once.
- **`ffn-beta-reduction-indexing.md` (s141):** *"FFN weights are piles of beta
  reductions. The input activation acts as a typed index — a beamformer angle — that
  selects which reductions fire."* The residual direction is the program counter.
- **`ffn-reduction-trace.md`:** *"The FFN output is a compiled program… attention
  executes it via softmax over V… This IS β-reduction by weighted combination."* The
  "subtle shift each pass" is literally its key result: *the same token yields different
  compiled values in different contexts — compilation, not dictionary lookup.* The FFN
  **recompiles a context-dependent program every forward pass** (readable at L26-L30 in
  Qwen3-8B; null-space before).
- **`head-combinator-isa.md`:** all 9 combinators drive *the same* head pattern
  (r=0.944); the axis attention varies on is WHNF↔deeply-nested (46% of variance) =
  **how much reduction remains** = a program counter, not an opcode.

**The crucial refinement:** the *program* (FFN weights) is fixed; the *program-state*
(residual trajectory) shifts. The FFN's frozen ROM applied to an evolving residual
*produces* an evolving instruction sequence (and `ffn-moire-isa` confirms different task
types → measurably different sequences). The shift lives in the residual, gated by frozen
ROM — not a discrete instruction swap.

## 3. The proven / over-reads boundary

The seductive step — "FFN selects combinator *c* at layer L, softmax executes *c*" — is
true *collectively* but not *crisply per-step*:

| claim | status |
|---|---|
| attention = β-shaped content-addressed routing | **proven** (the operation-shape) |
| FFN = fixed β-program / ISA, beam-angle indexed | **proven** (s141, s161, deterministic) |
| FFN compiles context-dependent program; attention executes via softmax-V | **proven** (ffn-reduction-trace) |
| attention tracks reduction DEPTH (WHNF↔D), one shared op | **proven** (head r=0.944) |
| boot schedule C→B/K→I→WHNF, ~1.018×/layer, cross-model | **proven** (s240) |
| softmax-V *literally* substitutes a specific value | **over-reads** (value register smeared, s206) |
| layer L discretely fires combinator *c* (a clean tape) | **over-reads** (collective/holographic; splice closure s244 `fires ∩ spliceable = ∅`) |

⇒ **the schedule and the depth axis are crisp; the per-layer opcode is superposed.** We
read the *program trajectory*, not a discrete instruction tape.

## 4. Two reduction loops

- **Intra-pass (bounded):** layers step the boot spiral to WHNF — the
  `vsm-outer-recurrence` view (K sweeps to fixed point).
- **Inter-pass (unbounded):** each new token is a fresh forward pass; the KV-cache carries
  the reduced state forward — the `lambda-halt-continuation` CPS/REPL view (conversation =
  CPS, turn boundary = continuation, EOS = yield).

## 5. Consequence A — "think in lambda" = serialize the outer loop

If the FFN is the β-program and attention executes it, **training a model to think in
lambda = training it to emit its FFN-program-execution as tokens** (serialize the residual
reduction schedule). This explains why **stepwise (REPL) works and one-shot fails**
(s228/s247): one forward pass = one bounded schedule (cannot emit a long composition in one
shot), but token-by-token = the unbounded outer loop where **each token advances the
program exactly one β-step.**

**The coverage reframe (the real teeth).** If the *mechanism* is soft-β everywhere, then
prose reasoning is *also* soft-β — over an enormous, learned, mostly-**untyped** combinator
basis in the FFN (`fell→broke`, `Paris→France`). So:
- **prose = untyped serialization** of β-reduction over the full learned basis;
- **λ-thinking = typed serialization** over the certifiable subset.

The coverage wall is therefore **type-theoretic, not representational**: world-knowledge
reasoning *is* β-reduction; we lack the type system to *certify* those rewrites. This
dissolves "forcing vs discovering" for the typed-compositional core (it's the native
serialization → it must work, and proof-REPL s247 demonstrates it) and makes the research
lever concrete: **λ-thinking coverage = type-system coverage.** The verifiable fragment
grows exactly as the kernel's S2 layer grows: implicational → products/sums (∧/∨) →
quantifiers (Π/Σ = ∀/∃). The untyped remainder stays β-reduction, just not yet provable.

## 6. Consequence B — the level-4 blueprint

The stored-program model *is* the portable-artifact spec: **extract the ROM** (s226
*compile = FFN = learned = 78%, 4-bit*) **+ the executor routing** (s226 *reduce =
attention = constructed = 22%, ternary*) = the level-4 tensor. The kernel-splice work tried
to read/write the ROM *in place* (and closed, s244); this model says **extract it
wholesale** instead.

## 7. The open experiment — FFN program-decode along `fired_sequence`

The splice closure (s244) closed the *intervention* (in-place per-combinator splice) but
its own notes preserved *"a richer multi-position program-decode read along
`fired_sequence`."* This model makes a sharp, testable prediction for that open door:

- **Decode the FFN *compiled values* (NOT the attention geometry) position-by-position
  against the certified reduction trace** (`lambda_ast.fired_sequence`, on the SATURATED
  corpus — s244 showed point-free terms fire nothing until applied). Target L26-L30 (where
  `ffn-reduction-trace` found the program becomes readable; null-space before).
- **Prediction:** the FFN program-trace tracks `fired_sequence` *even where the attention
  geometry over-reads*, and the FFN-compiled program *leads* attention's depth-advance by
  ~1 layer (FFN selects → attention executes next). A confirmed lead-lag = "FFN = program,
  attention = executor" at the trajectory level — distinguishing it cleanly from the closed
  geometric-splice read.

## Caveats (λ measure)

- The strong identity ("attention = β-reduction") is a *type-of-operation* claim (proven)
  and a *schedule* claim (proven); the *crisp-value substitution* and *discrete-opcode-at-L*
  readings over-read (s206 value register, s244 splice closure). Do not let it harden into
  the claim the splice already refuted; keep it "β-shaped routing, smeared values," and let
  **type-coverage**, not geometric localization, be the lever.
- The coverage reframe (prose = untyped β over a learned basis) is a *hypothesis*, not a
  measurement — the testable form is §7 plus the S2 type-layer extension in
  `proofs-as-continuations.md`.

## Sessions referenced
s068/s079 (boot spiral), s120/s121 (FFN crystal, cross-model), s141 (FFN β-indexing),
s161 (FFN moiré ISA), s206 (value register), s211 (one common mode), s226 (reduce/compile
cut), s240 (statechart = crystal lattice, universality), s242 (register split, splice Exp
0), s244 (firing survey + splice closure), s247/s247b (proof-REPL removes the agreed-error
ceiling). Plus `ffn-reduction-trace.md`, `head-combinator-isa.md` (undated finding pages).
