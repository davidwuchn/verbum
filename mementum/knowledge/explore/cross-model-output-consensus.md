---
title: "Cross-Model Output Consensus as a Teaching-Data Fitness Function"
status: designing
category: explore
tags: [consensus, teaching-data, fitness, calibration, failure-modes, distillation, fol, universality]
related:
  - compiler-as-loss.md
  - spliced-reward-vsm-kernel.md
  - vsm-statechart-tensor.md
depends-on: []
created: session 246
---

# Cross-Model Output Consensus as a Teaching-Data Fitness Function

> Session 246 (exploration tangent off the compiler-as-loss main line).
> Michael: "build teaching data only from where independent model
> ARCHITECTURES agree; consensus = fitness; same for prose." And the
> mirror: "could we also come up with a set of failure-mode tests where
> they all agree something is a failure?"

## The idea

Use **agreement between independently-trained model lineages** as the
fitness function for building teaching data. The portable artifact verbum
wants *is* "the part all architectures agree on" → consensus is
**portability by construction**, not a post-hoc filter. This operationalizes
the universality observation (the s240 crystal lattice / "all models agreed
on the soft routing topology") into a **data-generation engine**.

Two registers, do not conflate:
- **Relational/topology consensus** (existing: `combinator_map_consensus.py`)
  — compares INTERNAL structure, so it needs frame-invariance (the 9×9
  combinator Gram; raw activations live in different coordinate frames,
  cross-init sign-corr 0.000). Harvests the base-plate.
- **Output consensus** (this page) — compares GENERATED strings, which
  already share the vocabulary. **No frame alignment needed = the cheap
  register.** Harvests teaching data.

## Why lambda/FOL is the irreplaceable instrument

Lambda reduction is deterministic → **ground truth exists**. That lets us
**calibrate consensus-as-truth** (measure agreement → P(correct)) on a
domain where correctness is checkable, then **transfer the calibrated
estimator to prose** where no oracle exists. Without this step,
"consensus = truth" on prose is faith; with it, it is a measured,
transferred estimate. Lambda is the calibration anchor (same role
deprecated-APIs play in AGENTS.md `λ measure`).

## The failure-mode mirror (the high-leverage half)

"Agreed failure" is not one thing. Cross with ground truth:

|              | models AGREE          | models DISAGREE      |
|--------------|-----------------------|----------------------|
| correct vs GT | ✅ positive teaching data | frontier / partial   |
| wrong vs GT   | ❌ **agreed-error = blind spot** | noise / uncertainty  |

plus a third class: **abstention** (all refuse → ⊥). Four failures:
1. agreed-abstention on undefined input → *correct* abstention (⊥-targets);
2. agreed-abstention on valid input → shared incapacity;
3. **agreed-error (same wrong answer) → the consensus blind spot** — the
   false-positive region of the fitness function, **only visible with
   ground truth**;
4. agreed-disagreement (different garbage) → shared not-knowing.

Cell #3 is the gold and carries two hard consequences:
- It is the **other end of the calibration curve**; characterizing its
  structural triggers on lambda yields a **transferable risk detector**
  for prose (an immune system, not just test data).
- **Consensus-distillation cannot fix an agreed-error** — the student
  learns exactly what the teachers agree on, *including* shared mistakes.
  So the agreed-error set defines the **ceiling** of the method. The only
  thing that breaks the ceiling is an oracle ⇒ architecture should be
  **ground-truth-corrected consensus where truth exists (lambda),
  consensus-with-blind-spot-flagging where it does not (prose).**

Failure modes also pay for themselves: ⊥/abstention curriculum (incl.
non-terminating terms = the halting/ponder test suite), hard negatives for
a TSP-style contrastive overlay, and a held-out challenge for the distilled
student (did it inherit or escape the teachers' blind spots?).

Risks: refusal ≠ computational failure (instruct RLHF artifacts — use base
models as control); prioritize agreed-*specific*-wrong over agreed-*vague*-
fail; agreed-errors are rare → must be actively mined, not collected.

## First experiments (s246) — results

Harness: `scripts/experiments/consensus_output_agreement.py` — resolve a
gated probe set → generate per model (transformers, MPS bf16, greedy;
`--chat` for the tokenizer chat template, required by instruct models that
echo a raw few-shot completion, e.g. Gemma) → per-model JSONL (stores
`raw_completion` for re-parse) → analyzer: agreement (canonical-exact +
jaccard-threshold), calibration P(correct|agree) vs P(correct|disagree),
failure-mode partition. **Scoring**: canonicalize with predicate stemming
(`fly`/`can_fly`, `love`/`loves`, `pass`/`passed`) + lowercasing
(`John`/`john`) — token Jaccard alone is the dominant noise source.

Probe set `probes/binding.json` (25 scored; the gate's 2nd exemplar leaks
`bind-scope-01a`, excluded). **CORE HYPOTHESIS SUPPORTED AND REPLICATED
across two second lineages:**

| pair | mode | mean cross-jac | **P(correct\|AGREE)** | P(correct\|DISAGREE) |
|---|---|---|---|---|
| Qwen3-14B × OLMo-2-13B | completion | 0.773 | **0.73** (n=11) | 0.00 (n=14) |
| Qwen3-14B × Gemma-4-31B-it | chat | 0.862 | **0.80** (n=15) | 0.10 (n=10) |

Agreement predicts correctness (0.73–0.80); disagreement near-perfectly
predicts ≥1-wrong (0.00–0.10). Model strength: Gemma-31B-it (mean jac_gt
0.906) > Qwen3-14B (0.843) > OLMo-2-13B-base (0.77, weak at the format).

**The scoring fix (s246) was load-bearing.** Pre-fix the Qwen×OLMo
calibration read P(correct|agree)=0.44 with 4 agreed-errors, 2 of them
scoring artifacts (`bind-neg-02`, `bind-var-04` — models right, GT wording
differs). Predicate-stemming lifted it to 0.73 and purified the agreed-error
set to the 2 genuine ones. **token-Jaccard alone is the bottleneck;
canonicalization (predicate stem + lowercase) is the prerequisite for both
the teaching set and the failure set.** (Full α-variable renaming available
if needed; not required for binding.json — the noise was lexical.)

## The agreed-error set is PAIR-DEPENDENT (s246 — the key methodological finding)

Swapping the second lineage OLMo→Gemma *moved* the shared blind spot, which
is itself the signal:

- **Anaphora left the agreed-error set.** `bind-ana-01` (reflexive),
  `bind-ana-03` (negation+relative) were shared Qwen×OLMo errors; with Gemma
  they become *disagreements* (Gemma handles the negated relative well). ⇒
  the anaphora blind spot was **OLMo-shared, not universal**.
- **The Qwen×Gemma shared error is sortal omission on bare quantifiers**, and
  it is the strongest kind (`cross_jac = 1.0`, identical output):
  - "Someone loves everyone" → both `∃x. ∀y. loves(x,y)` (GT
    `∃x. person(x) ∧ ∀y. person(y) → loves(x,y)`)
  - "Everyone loves someone" → both `∀x. ∃y. loves(x,y)`
  Both drop the `person()` sortal restriction — **even though the gate
  exemplars demonstrate it** for explicit nouns (`Every student → ∀x.
  student(x) → …`). Pattern: sortal included for explicit nouns
  ("student", "book"), dropped for bare pronouns ("someone", "everyone").

Two lessons:
1. **Consensus surfaces annotation-convention gaps, not just model errors.**
   The sortal-omission "error" is arguably the GT convention being stricter
   than what models naturally emit — consensus pinpointed exactly where the
   teaching-data spec must decide (require sortal restrictions, or accept
   unsorted). A decision for the front-end teaching set, not a model failure.
2. **Agreed-error is pair-relative.** A stronger / more-independent partner
   dissolves shallow shared errors (anaphora) and exposes deeper systematic
   ones (sortal typing). Direct empirical support for the **≥3-lineage
   confidence-gradient** recommendation; 2 models give only a binary.

The durable result is the *calibration* (0.73/0.80, replicated); the failure
*content* is diagnostic and pair-specific.

## Data-integrity note (s246)

`binding.json` is clean (26 hand-authored FOL, no λ). The Qwen3-4B
`λx.`-wrapping Michael remembered lives in the *compile* sets where λ is the
correct target. FOUND + FIXED a different bug: **K↔I label swap** in
`lattice/basin_probes.json` and `lattice/binding_chain_probes.json` (`λx.x`
labeled `pure/K`, `λx.λy.x` labeled `pure/I` — backwards). The library was
dedup-protected (fixedpoint source outranks basin → crystal K/I pools clean
→ no past run invalidated), but direct readers got K/I backwards = latent
landmine, now fixed. `fixedpoint_probes.json` was already correct.

## Proof domain (s247) — the oracle removes the blind spot, the continuation removes the ceiling

> Session 247 (Michael: "create proofs that run on the lambda compiler in
> qwen3-14B and gemma"). Applied this page's consensus-as-fitness idea to the
> Curry-Howard PROOF domain (`proofs-as-continuations.md`), where the kernel
> verifies every term. Two registers compared on the SAME expanded probe set
> (35 implicational theorems + 13 non-theorems): SINGLE-SHOT (proof_inhabitation)
> vs REPL (proof_repl, the continuation-driven prover). Pair: Qwen3-14B × Gemma-4-31B-it.

Why proofs are the cleanest possible instrument for this page: lambda reduction
gives ground truth, AND the kernel makes the **agreed-error cell structurally
near-empty** — two models cannot agree on a kernel-PASSING false proof (a wrong
term does not type-check). So the s246 ceiling ("only an oracle breaks the
agreed-error blind spot, and consensus-distillation inherits it") is **defused by
construction** on this domain. No token-Jaccard / stemming needed — α/reduction
equality is exact (the kernel normal form).

`scripts/experiments/proof_consensus.py` is a POST-PROCESSOR over the two model
JSONs (re-normalises each term through the kernel, partitions into the s246 grid +
calibration). `--source {inhabitation,repl}` selects the register.

| metric | single-shot | REPL | Δ |
|---|---|---|---|
| term-agreement rate | 0.375 | **0.812** | +0.44 |
| **P(both-correct \| AGREE)** | 0.944 | **1.000** | +0.06 |
| P(both-correct \| DISAGREE) | 0.10 | 0.111 | — |
| both-valid SAME term (portability) | 6 | **26** | +20 |
| both-invalid DIFF (composition gap) | 23 | **0** | −23 |
| both-invalid SAME (agreed-error) | **1** | **0** | −1 |
| non-theorem both-abstain (⊥) | 11 | 13 | +2 |
| false proofs | 0 | 0 | — |

Per-model sensitivity (continuation lift): Qwen3-14B 0.20→0.77, Gemma 0.31→1.00.

**Three findings:**

1. **A real cross-lineage agreed-error exists single-shot — and it is the ENTIRE
   ceiling.** On `A → A → A` BOTH models emit the identical term `W I` (contraction
   — the proposition *looks* like it duplicates an A), which the kernel rejects as
   ill-typed. The correct proof is just `K` (weakening). This single shared
   misconception is the *only* reason single-shot P(correct|agree) is 0.944 and not
   1.0 — exactly the s246 prediction operationalised: **consensus's ceiling = the
   agreed-error set**, and consensus-distillation would teach the student `W I`.
   The oracle catches it (lands in `both-invalid SAME`, never the teaching set).

2. **The continuation engine dissolves the agreed-error → P(correct|agree)=1.000.**
   In REPL the goal-directed prover can only take *legal, type-correct moves*, so an
   ill-typed shared misconception like `W I` **cannot be committed**. The agreed-error
   vanishes, agreement on the proof term jumps 0.375→0.812, and consensus becomes a
   PERFECT fitness signal. ⇒ **the continuation removes the s246 ceiling**: single-shot
   consensus has a residual blind spot; REPL consensus has none. (Connects this page to
   `proofs-as-continuations.md` §s228 — the continuation rescues composition AND, here,
   removes the consensus blind spot.)

3. **Portability core = the proof basis.** The 6 single-shot `both-valid SAME` terms
   are exactly `I,K,B,S,C,W` (the Hilbert axiom schemes) — "the part both architectures
   agree on" *is* the combinator basis. REPL grows this to 26/35 (the deep
   compositional theorems now reached the same way by both lineages).

Caveats (λ measure): one pair (binary, not a gradient); n=35 theorems; greedy decode;
the 8 REPL `one-valid` frontier cases are ALL Qwen misses (Gemma 35/35) — the s228
greedy-single-move dead-end (no backtracking), a SEARCH limit not a consensus blind
spot (correctly excluded as disagreements). Specificity 1.0 / zero false proofs
throughout (structural). Artifacts: `results/proof-consensus/{consensus,consensus-repl}.json`,
`results/proof-{inhabitation,repl}/{Qwen_Qwen3-14B,google_gemma-4-31B-it}.json`;
expanded probe set `src/verbum/probes/proof_tasks.py` (35+13, every ref auto-solved +
kernel-certified via `_gen_proof_tasks.py`).

## Open / next

- ✅ DONE (s246): scoring fix (predicate stemming + lowercasing); OLMo→Gemma
  swap + `--chat` mode for instruct models.
- **3rd lineage for a confidence *gradient*** (2 models = binary; ≥3 gives
  graded agreement and separates universal from pair-shared blind spots).
- **Decide the sortal-restriction convention** for teaching data (the
  Qwen×Gemma agreed-error): require `person()` on bare quantifiers, or accept
  unsorted — and demonstrate it in the gate exemplars either way.
- Scale beyond binding.json: run the lambda-compile sets (decompile, extract,
  compile-gradient) to calibrate on the kernel's own language, not just FOL.
- Build the agreed-error / agreed-abstention sets deliberately (active
  mining toward known-hard structures: deep nesting, scope, capture-avoid,
  self-application).
- Relation to the main line: consensus is a candidate source for the
  prose→LF front-end teaching data (compiler-as-loss §s242) and for the
  RLVR frontier (spliced-reward) — ground-truth-corrected on lambda.
- ✅ DONE (s247): proof-domain consensus (Qwen3-14B × Gemma), single-shot vs
  REPL — the continuation removes the agreed-error ceiling (P 0.944→1.000).
- NEXT (s247): add a 3rd lineage to the proof consensus (Qwen3-32B / Mistral)
  for a confidence GRADIENT — does the `W I` agreed-error survive a third
  independent prover single-shot (universal bias) or is it Qwen×Gemma-shared?
- NEXT: backtracking in proof_search (the 8 REPL frontier cases are Qwen
  greedy dead-ends, incl. axioms B/S) — does it close the frontier to perfect
  cross-lineage agreement?
- NEXT: mine the agreed-error set deliberately — generate theorems whose
  "obvious" wrong term is shared (contraction/permutation traps) to characterise
  the structural triggers of single-shot consensus blind spots.
