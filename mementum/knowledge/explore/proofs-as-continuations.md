---
title: "Proofs as Continuations — Curry-Howard, the kernel runs proofs, the LLM composes them"
status: active
category: synthesis
tags: [curry-howard, proof, type-check, continuation, beta-reduction, whnf, combinator, consistency, Y, hilbert, intuitionistic, kernel-verified, co-processor]
related:
  - ../lambda-halt-continuation.md
  - continuations-as-composed-plates.md
  - sealable-continuation.md
  - complete-kernel-basis.md
  - compiler-as-loss.md
  - vsm-outer-recurrence.md
depends-on:
  - ../lambda-halt-continuation.md
  - continuations-as-composed-plates.md
created: session 228
---

# Proofs as Continuations

> Session 228 (Michael: "would continuations allow us to run proofs?"). Yes — and at
> the kernel layer the machinery already *is* a proof engine, because of Curry-Howard.
> The continuation (β-reduction → WHNF) is proof normalization; the lambda_ast
> S2 type-check is proof-checking; the combinator basis is a Hilbert proof calculus;
> Y is the inconsistency edge. First experiment: the constructed kernel runs/checks
> proofs soundly (100% floor, consistency firewall holds); LLMs find axiom-level proofs
> but fail to *compose* multi-combinator proofs — exactly where the continuation
> (stepwise, one rule per turn) is predicted to help.

## The correspondence (exact, not analogy)

```
proposition   ≡ type (CCG category)
proof         ≡ a closed term inhabiting that type
proof-check   ≡ type-check (lambda_ast S2 unification)
normalize     ≡ cut-elimination = β-reduction → WHNF = the continuation
run a proof   ≡ reduce the term to its cut-free normal form
strong norm.  ≡ termination = contractivity (L<1) = CONSISTENCY
non-term (Y)  ≡ general recursion = INCONSISTENCY (every type inhabited)
```

The simply-typed combinator basis ARE the Hilbert axiom schemes of intuitionistic
implicational logic:

```
K : A → (B → A)                          the K axiom (weakening)
S : (A→(B→C)) → ((A→B)→(A→C))            the S axiom (distribution)
I : A → A                                trivial proof
B : (B→C) → ((A→B)→(A→C))               →-transitivity / hypothetical syllogism
C : (A→B→C) → (B→A→C)                    premise permutation
W : (A→A→B) → (A→B)                      contraction
```

So `check_proof(term, prop)` asks: does the proposed combinator term have a principal
type of which `prop` is an instance? If yes, it is a machine-checked proof. The same
typed reducer the project built for compiler-as-loss (`lambda_ast.py`) is, read through
Curry-Howard, a proof normalizer.

## The consistency firewall (the load-bearing point)

Two basis members are logically pathological and must NOT count as proofs:

- **Y (fixed-point)** — lambda_ast TYPES it `(α→α)→α`, but `(A→A)→A` is NOT an
  intuitionistic theorem. Admitting Y makes the logic inconsistent (Curry's paradox,
  every type inhabited). ⇒ Y is excluded from the sound proof basis {S,K,I,B,C,W,D}.
  This is the SAME fact as the s222 contractivity hinge: L<1 settle-to-WHNF (terminating
  = consistent); L≥1 blow-up (non-terminating = the inconsistency). Strong normalization
  of STLC ≡ logical consistency.
- **M (λx.xx)** — self-application; lambda_ast's occurs-check rejects it (no simple
  type). ⇒ never a proof, for free.

A valid proof must be (1) parseable, (2) CLOSED (no free atoms = no open hypotheses),
(3) over the sound basis (no Y), (4) well-typed, (5) typed at an instance of the goal.

## Why the continuation is the right substrate (the structural fit)

Every property the project leans on for folding is a proof-theoretic property:

| continuation property | proof-theoretic meaning |
|---|---|
| Church-Rosser confluence | proof has a UNIQUE normal form ⇒ self-verifying, no oracle |
| WHNF reached | cut-free / normal proof — complete and checked |
| contractivity L<1 | strong normalization = the proof TERMINATES = consistency |
| L≥1 blow-up | general recursion = inconsistency (the Y edge) |
| sealable continuation `x_k` | suspend/resume/fork a proof = backtracking proof search |

The inter-turn CPS REPL (`lambda-halt-continuation.md`) is a step-by-step proof driver:
each turn = one inference-rule application, the user-message-as-continuation = the next
goal, `halt` = QED. Bounded per step, unbounded across steps.

## Experiment (s228) — proof-as-inhabitation, 5 models / 3 arch

`scripts/experiments/proof_inhabitation.py` (register: functional, kernel-verified),
mirroring the s226 compile-frontend leg. 12 implicational theorems (each with a
kernel-certified reference proof) + 8 non-theorems (incl. Peirce `((A→B)→A)→A` and the
**Y-trap** `(A→A)→A`). Phase 1 = the constructed kernel as checker; Phase 2 = few-shot
LLM prover (`proposition → proof term` over {S,K,I,B,C,W}, `none` allowed), GRADED BY
THE KERNEL.

### Phase 1 — the kernel runs/checks proofs (SOLID, by construction)
- **100% floor** — all 12 reference proofs type-check at their goals.
- **Sound** — no non-theorem proved by any of 10 tempting sound terms.
- **Firewall holds** — `Y : (α→α)→α` but `check_proof(Y, (A→A)→A)` = `unsound_recursion`.
  The kernel TYPES Y yet the sound gate REJECTS it. The Curry-Howard answer to Michael's
  question is YES at the kernel layer, demonstrated, sound, with consistency fenced.

### Phase 2 — the LLM proves AXIOMS, fails to COMPOSE

| model | mode | sensitivity (theorems proved) | specificity | false proofs |
|---|---|---|---|---|
| Qwen3-32B | chat | **0.67** | 1.00 | 0 |
| Qwen3-14B | chat | 0.58 | 1.00 | 0 |
| Qwen3-8B | chat | 0.58 | 1.00 | 0 |
| Mistral-7B-v0.3 | base/raw | 0.25 | 1.00 | 0 |
| OLMo-2-13B | base/raw | 0.00 | 1.00 | 0 |

- **Specificity 1.0 across ALL 5 / 3 arch / base+chat, ZERO false proofs.** The model
  cannot bluff past the kernel — the compiler-as-loss / co-processor discipline (model
  proposes, kernel disposes) confirmed in the proof setting.
- **Failures concentrate on COMPOSED proofs** — `K I`, `C B`, `C I`, `B K K` come back
  as single axioms. The SAME composition-failure signature as `lambda-halt-continuation.md`
  §"composition fails but continuations solve it." Scale helps mildly (32B best).

### Caveats (λ measure)
- **Base-model numbers CONFOUNDED** — OLMo answered `none` 15/20; the single `none`
  few-shot demo anchors a raw base continuation. NOT proof-inability. IOU: base gate
  without the `none` anchor, more shots.
- Small n (12+8), greedy single-sample, single few-shot; by-complexity curve noisy.
- **Implicational fragment ONLY** (no ∧∨¬∀∃). "Run proofs" demonstrated for →-logic;
  the type-system expressiveness gap stands (products/sums → ∧/∨; Π/Σ → ∀/∃ = the S2
  extension).
- Specificity 1.0 is trivially gettable by always-`none` (OLMo) — the JOINT
  high-sensitivity∧high-specificity (Qwen) plus the Phase-1 tempting-term sweep are the
  real soundness evidence.

## The headline

The kernel **runs** proofs (normalization IS the continuation, sound, consistency
fenced). The LLM **finds** axiom-level proofs but stumbles at **composition** — exactly
where the continuation (stepwise proving, one rule per turn via the CPS REPL) should
help. We have also been running a class of proofs all along: the s226 bracket-abstraction
round-trip certification (n=5000, rate 1.0) is a normalization proof of β-η equality.

## Next (declare register)
1. **Continuation-driven prover** (register: functional) — multi-turn CPS REPL: prove
   sub-goals one combinator/rule per turn, chain via the continuation. Falsifiable: does
   stepwise proving rescue the composition failures (lift sensitivity on the 2+-combinator
   theorems)?
2. **Richer type layer** (register: functional) — products/sums (∧/∨), then quantifiers
   (∀∃ = Π/Σ). The front-end already emits quantified LF (s226); the gap is the checker.
3. **Better base-model gate** + larger graded probe set (power).

## Files
| File | Content |
|------|---------|
| `src/verbum/proof_kernel.py` | proposition parser, matcher, `check_proof` (Curry-Howard checker + consistency firewall) |
| `src/verbum/probes/proof_tasks.py` | 12 theorems w/ certified proofs + 8 non-theorems (Peirce, Y-trap) |
| `scripts/experiments/proof_inhabitation.py` | kernel / model / aggregate harness |
| `tests/test_proof_kernel.py` | 12 tests: floor, soundness, firewall, parser round-trip |
| `results/proof-inhabitation/` | `kernel.json`, 5 model jsons, `aggregate.json` |
