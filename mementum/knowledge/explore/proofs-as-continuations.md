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

## s228 — Continuation-driven prover: stepwise proving rescues composition (+0.25)

The predicted fix, BUILT and RUN. `src/verbum/proof_search.py` = a goal-directed
natural-deduction engine; the open goal stack IS the reified continuation; moves
`intro` / `exact h` / `apply h` act on the focused goal; at QED the kernel
RECONSTRUCTS the proof term via bracket abstraction (`lambda_compile.compile_expr`,
the exact compile oracle) and VERIFIES it. The model chooses one move per turn from
the legal menu; the kernel carries the continuation forward (`proof_repl.py`,
multi-turn). The engine floor is 100% (every theorem auto-solves + reconstructed term
kernel-verifies; every non-theorem unsolvable).

**★ VERDICT (5 models/3 arch; results/proof-repl/aggregate.json) — HYPOTHESIS
CONFIRMED.** Stepwise proving lifts sensitivity vs the single-shot baseline:

| model | 1-shot | REPL | Δ | spec | turns |
|---|---|---|---|---|---|
| Qwen3-8B | 0.58 | **1.00** | **+0.42** | 1.00 | 4.7 |
| OLMo-2-13B | 0.00 | 0.42 | **+0.42** | 1.00 | 3.2 |
| Mistral-7B | 0.25 | 0.58 | +0.33 | 1.00 | 4.2 |
| Qwen3-14B | 0.58 | 0.67 | +0.08 | 1.00 | 3.8 |
| Qwen3-32B | 0.67 | 0.67 | +0.00 | 1.00 | 4.1 |

- **Mean Δ +0.25, 4/5 improved, strongest where single-shot was weakest** (8B → perfect
  1.00; OLMo recovers from the single-shot `none`-anchor confound). The composition
  failures (`K I`, `C B`, `C I`, `B K K` the single-shot prover missed) are reachable
  one move at a time — `(A→B)→(B→C)→A→C` proves via `intro,intro,intro,apply h2,apply
  h1,exact h3` → `C B`.
- **★ Specificity 1.0 / ZERO false proofs is now STRUCTURAL** — a non-theorem has no
  closing derivation, so no move sequence can fabricate a proof. A strict upgrade over
  the single-shot setting where specificity was merely observed. This is the
  consistency firewall made *operational*: the continuation engine cannot reach QED on
  `(A→A)→A` / Peirce regardless of what the model proposes.

**Caveats (λ measure):** the REPL shows the legal-move MENU each turn ⇒ part of the
gain is menu-constraint, not pure reasoning (IOU: menu-less stepwise, or single-shot +
combinator menu, to separate). **32B flat** — already strong single-shot, and the
engine gives the model NO BACKTRACKING (greedy single-sample, one wrong move dead-ends
the branch) ⇒ sensitivity is bounded by greedy move selection (IOU: backtracking /
stuck→retry). Small n (12 positives), greedy decode, single few-shot.

## s247 — Cross-lineage proof consensus: the REPL removes the agreed-error ceiling

Session 247 (Michael: "create proofs that run on the lambda compiler in qwen3-14B
and gemma"). Two moves: (1) ran Gemma-4-31B-it on the s228 harness (a fourth, Google,
instruct lineage); (2) grew the probe set and applied cross-model output consensus
(`cross-model-output-consensus.md`) to the proof domain.

**Gemma on the s228 set (12+8).** Single-shot sensitivity **0.75** (the strongest
single-shot prover yet, > Qwen3-32B 0.67); REPL **1.00** (Δ +0.25). Specificity 1.0,
ZERO false proofs — including the Y-trap and Peirce. The composition-failure
signature reproduces exactly: the three single-shot misses (`K I`, `C B`, `B K K`) are
all multi-combinator terms, all composed one move at a time by the REPL. The
consistency firewall now holds across Qwen (3 sizes), Mistral, OLMo, AND Gemma.

**Expanded probe set (35 theorems + 13 non-theorems).** `proof_tasks.py` grew via
`scripts/experiments/_gen_proof_tasks.py`: candidate props are auto-solved
(`proof_search.solve`), the term reconstructed (bracket abstraction), and
kernel-certified (`check_proof == VALID`) — zero hand-derivation. Adds deep
compositional theorems (triple-compose `B (B (C B)) (C B)`, S-prime `C S`, the
intuitionistic self-apply `((A→B)→A)→(A→B)→B` = `S I`, the provable cousin of Peirce)
and harder non-theorems. On this set single-shot collapses (Qwen 0.20, Gemma 0.31 —
composition-bound), REPL recovers (Qwen 0.77, Gemma 1.00).

**Consensus result (Qwen3-14B × Gemma, `proof_consensus.py`).** The cross-model
agreement, kernel-verified:

| metric | single-shot | REPL |
|---|---|---|
| term-agreement | 0.375 | **0.812** |
| P(both-correct \| agree) | 0.944 | **1.000** |
| both-valid SAME proof | 6 | **26** |
| composition gap (both-invalid DIFF) | 23 | **0** |
| agreed-error (both-invalid SAME) | **1** (`W I` for `A→A→A`) | **0** |

- **The single-shot agreed-error is real and is the whole ceiling.** Both lineages
  emit the IDENTICAL ill-typed `W I` for `A → A → A` (reaching for contraction; the
  answer is weakening `K`). It is the sole reason P(correct|agree) ≠ 1.0 single-shot —
  consensus's blind spot, made visible by the oracle (cf. cross-model page §"agreed
  error = the ceiling").
- **The continuation dissolves it.** The goal-directed engine only takes legal,
  type-correct moves ⇒ an ill-typed shared misconception cannot be committed ⇒
  agreed-error → 0, P(correct|agree) → 1.000. The continuation is not just the
  composition fix (s228); it is also the **consensus immune system** — it removes the
  s246 agreed-error ceiling on the proof domain.
- **Portability core = the basis.** The 6 terms both lineages agree on single-shot are
  exactly `I,K,B,S,C,W` — the Hilbert axiom schemes. "The part all architectures agree
  on" IS the combinator basis.

Caveats (λ measure): one pair (binary); n=35; greedy; the 8 REPL `one-valid` frontier
cases are ALL Qwen misses (Gemma 35/35), incl. axioms B/S — the s228 greedy-dead-end
(no backtracking), a search limit, correctly excluded as disagreements not blind spots.

## Next (declare register)
1. **Backtracking + menu ablation** (register: functional) — let the model see a dead
   end and retry (the engine already exposes `legal_moves`); and run a menu-less variant
   to isolate stepwise-reasoning from menu-constraint. Does 32B then improve?
2. **Richer type layer** (register: functional) — products/sums (∧/∨), then quantifiers
   (∀∃ = Π/Σ). The front-end already emits quantified LF (s226); the gap is the checker.
3. **Better base-model gate** + larger graded probe set (power).

## Files
| File | Content |
|------|---------|
| `src/verbum/proof_kernel.py` | proposition parser, matcher, `check_proof` (Curry-Howard checker + consistency firewall) |
| `src/verbum/probes/proof_tasks.py` | 12 theorems w/ certified proofs + 8 non-theorems (Peirce, Y-trap) |
| `scripts/experiments/proof_inhabitation.py` | single-shot: kernel / model / aggregate harness |
| `tests/test_proof_kernel.py` | 12 tests: floor, soundness, firewall, parser round-trip |
| `results/proof-inhabitation/` | single-shot: `kernel.json`, 5 model jsons, `aggregate.json` |
| `src/verbum/proof_search.py` | s228 goal-directed ND engine (goal stack = continuation; intro/exact/apply; bracket-abstraction term reconstruction; auto solver) |
| `scripts/experiments/proof_repl.py` | s228 continuation-driven prover: engine / model / aggregate (vs single-shot Δ) |
| `tests/test_proof_search.py` | 7 tests: engine floor, structural soundness, apply-chain composition, move legality |
| `results/proof-repl/` | s228 REPL: `engine.json`, 5 model jsons, `aggregate.json` (+Δ) |
| `scripts/experiments/_gen_proof_tasks.py` | s247 authoring aid: auto-solve + kernel-certify candidate theorems → ready-to-paste ProofTasks |
| `scripts/experiments/proof_consensus.py` | s247 cross-lineage proof consensus (post-processor; `--source inhabitation\|repl`; s246 grid + calibration) |
| `results/proof-consensus/` | s247: `consensus.json` (single-shot), `consensus-repl.json` (REPL) |
