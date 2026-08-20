---
title: Equality is an agreement rate — §P-OBS-EQUIV
status: designing
category: explore
tags: [semantic-equality, observational-equivalence, fork-differencing, repl-driver, profile-equivalence]
related:
  - the-benchmark-is-the-re-oracle.md            # §2b profile-equivalence, the metric
  - repl-driver-trampoline.md                    # the instrument
  - ../memories/semantic-equality-is-behavioral-and-we-asked-it-backwards.md
  - ../memories/semantic-equality-is-a-fallible-tape-authored-event.md
depends-on: [src/verbum/driver.py, src/verbum/lambda_ast.py, scripts/experiments/cl_collapse_3_operator.py]
---

# Equality is an agreement rate — §P-OBS-EQUIV

## The question

Michael, s346: *"semantic equality means two lambdas could have different
names but trigger the same exact behavior."* The ~30-session
representation-first hunt (value s317 · magnitude s335 · routing s336 ·
operator s339 · fate/route s343-44 · deciding-state s346 — all LEXICAL)
was a category error: contextual equivalence is not a storable fact; it
is a property OF behavior. Measured the right way — fork-differenced
behavior across a context battery — is the machine's equality of
co-extensional terms (SKK vs I) a ceiling (extensional), a floor
(purely lexical), or a **RATE** (path-dependent, context-structured,
bug-mediated — the s346 REPL pilot's exploration-grade observation)?

The metric is §2b profile-equivalence pointed at term PAIRS instead of
(model, reducer): two spellings are "equal to the machine" exactly to
the extent their answer profiles agree across contexts — errors
included. Equality claims become battery-indexed rates, never bits.

## Design (frozen s347)

**Instrument.** `src/verbum/driver.py` stage-1 (validity gate re-run at
capture time: determinism · fork-identity · append law). Greedy decode,
answer granularity. Fork-differencing: for each (pair, context, args),
seal the SHARED context prefix once, `fork(seal, spelling_i + suffix)`
for each member — identical KV prefix by construction; the only
difference entering the machine is the spelling.

**Corpus.** Kernel-certified (lambda_ast) co-extensional pairs from the
s339 families (`cl_collapse_3_operator.py` FAMILIES): I (anchor + 8
spellings), W (anchor + 2), B (anchor + 1) → within-family pairs,
sampled 24 (I:20, W:3, B:1). FLOOR pairs: 24 surface-matched NON-equal
pairs (same combinator alphabet, |Δtoken-length| distribution matched
to the co-ext pairs), kernel-certified to DIFFER in every scored
context. CEILING trials: same-spelling-twice, 96 forks (proves greedy
determinism empirically, not by assumption). Certification rule: a pair
enters co-ext iff kernel normal forms of C[T1] and C[T2] are alpha_eq
in EVERY battery context; floor iff they differ in every scored
context; anything mixed is excluded (logged).

**Context battery** (template = shared prefix ⊕ {T} ⊕ shared suffix
"... = "; 2 argument instantiations from disjoint atoms; kernel ground
truth computed per member per context):

| id | context | shape | note |
|----|---------|-------|------|
| C1 | direct | `{T} a =` | textbook path (REPL: agrees, spontaneously derives) |
| C2 | named | `let f = {T}` ⏎ `f a =` | REPL divergence site (argument-drop) |
| C3 | nested | `{T} ({T} a) =` | self-composition |
| C4 | extra-arg | `{T} a b =` | partial/over-application |
| C5 | arg-position | `K ({T} a) b =` | term computed in argument position |
| C6 | discard-position | `K a ({T} b) =` | PREDICTED term-insensitive (K discards; s346 free-discard) — live test of the calibration gate |
| T1 | trace stratum | `Show each reduction step:` ⏎ `{T} a` | reported SEPARATELY, never in headline A (tape machine: traces trivially distinguish; medium note, ¬η) |

**Answer extraction.** First line of the greedy continuation,
whitespace-normalized; parsed by the kernel when parseable →
agreement ≡ exact-match ∨ alpha_eq. Per-trial record: both raw
continuations, extracted answers, kernel expected values, agreement
bit, correctness bits.

**Term-sensitivity calibration (the manufactured-agreement guard).**
A context is SCORED iff floor pairs disagree there:
S(c) = 1 − A_floor(c) ≥ 0.5. Contexts failing S are excluded from all
headline statistics (C6 is predicted to fail — that prediction is
itself a free pre-registered contact for the affine/free-discard read).
< 4 surviving contexts → VOID (battery collapsed).

**Statistics** (all permutation p at 5000, seeded):

- `A_ceil` — same-spelling agreement. G0: must be exactly 1.0 AND
  driver validity gate pass; else VOID.
- `D_floor = A_coext − A_floor` over scored contexts, permutation over
  pair-type labels within |Δlen|-matched strata. License floor
  Δ ≥ 0.10 ∧ p < 0.05. ADVISORY: r(agreement, |Δlen|) + D_floor
  partialled on |Δlen| (s343 scar: a length confound fakes signal).
- `D_ceil = A_ceil − A_coext`, sign test. Separation from ceiling
  licenses ¬EXTENSIONAL.
- CONTEXT STRUCTURE: statistic = variance of A_coext(c) across scored
  contexts; null = shuffle context labels within (pair, args); p<0.05.
- PRE-REGISTERED DIRECTIONAL CONTACT (the REPL replication):
  A_coext(C1 direct) > A_coext(C2 named), one-sided, p < 0.05.
  Counted on the frame ledger only if it wins (λ frame_ledger).
- BUG-TAXONOMY (secondary, advisory — feeds §P-CALCULUS-LEDGER arm C):
  among divergent trials, fraction of wrong-member answers matching a
  calculus-predicted output (R_naive substitution result ∨ WHNF-stall
  λ-prefix) vs matched-distractor chance. Never load-bearing here.

**Verdict tree (frozen, exhaustive on the scored battery):**

```
G0 fail ∨ <4 scored contexts ∨ certification failure        → VOID
A_coext ≥ 0.95 ∧ D_ceil not licensed                        → EXTENSIONAL
D_floor < 0.10 ∨ p ≥ 0.05                                   → LEXICAL-FLOOR
else (both separations licensed):
    context-structure p < 0.05                              → RATE-STRUCTURED
    otherwise                                               → RATE-UNSTRUCTURED
```

**A-priori mass (before any data):**
RATE-STRUCTURED 40 · LEXICAL-FLOOR 20 · VOID 20 ·
RATE-UNSTRUCTURED 10 · EXTENSIONAL 10.
(VOID carries real mass: first frozen probe on the fork-differencing
instrument class; battery collapse and certification failure are live
risks. The s346 pilot is exploration-grade n≈1 and is NOT evidence in
this ledger — capture-euphoria guard.)

**Planted worlds (--validate, through the REAL analyse path):**

1. EXTENSIONAL world (members always answer identically) → EXTENSIONAL
2. LEXICAL world (answer is a function of spelling only) → LEXICAL-FLOOR
3. RATE world (agreement deterministic per context class) → RATE-STRUCTURED
4. COIN world (iid mid-rate agreement, context-free) → RATE-UNSTRUCTURED
5. NONDET adversary (ceiling breaks) → VOID (G0 refuses)
6. INSENSITIVE adversary (answers ignore the term; floor pairs agree
   everywhere) → VOID (calibration prunes the whole battery)

**Run plan.** Smoke: Qwen3-8B reduced-n through the full pipeline
(regime warning → design PAUSE, s324). *(Amended pre-data, Michael
s347: smoke must be ≥4B, prefer 7B+ — the calculus function is not
fully formed below ~4B; a sub-scale smoke tests the harness against a
machine that lacks the machinery under probe. Supersedes the drafted
0.6B smoke; coheres the s345 0.6B-degeneracy scar.)* Real: Qwen3-14B,
MPS, greedy, one capture. *(Amendments A3-A6, Michael GO after the 8B
smoke design-PAUSE — instrument plumbing only, masses/tree unchanged:
A3 few-shot header pins the answer register (bare "expr =" elicited
"?"+CoT ramble and list-enumeration junk at 8B); A4 chain-tolerant
extraction (final term after last "="); A5 decode budget 24→48;
A6 certification floor scales with corpus target so a smoke can pass.)* Budget ≈ 1.3k bounces × ~24 tokens (minutes–low hours).
meta.json full λ run_provenance; results committed autonomously;
closure batch approval-gated.

**Honesty bounds (declared at freeze):**

- The rate is BATTERY-INDEXED — a finite context battery cannot prove
  full observational equivalence (which quantifies over all contexts);
  it can only refute it or measure agreement structure on the sample.
- EXTENSIONAL here would NOT re-locate equality in the weights — a
  machine that computes correctly on the tape in every context also
  reads ceiling. RATE/FLOOR are the informative directions; the probe
  is one-directional in that sense.
- Single model (Qwen3-14B), greedy only, answer granularity only.
- Divergence cause is NOT identified by this probe (taxonomy is
  advisory); mechanism belongs to §P-COEXT-ROUTE / LEDGER-C.

## Result

(pending)
