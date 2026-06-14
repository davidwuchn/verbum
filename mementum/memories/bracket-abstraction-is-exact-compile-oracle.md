✅ s226 STAGE 2. "Compile" factors further than the s226 dyad assumed — and most is
constructible:
  prose → logical-form     : LEARNED (NL understanding; Montague/CCG parse)
  logical-form → term      : EXACT (bracket abstraction, src/verbum/lambda_compile.py)
  term → normal form       : EXACT (reduction, lambda_ast stage 1)

Bracket abstraction = the INVERSE of reduction (combinatory completeness, Turner 1979);
Turner-style [x] over {S,K,I,B,C} + K/B/C/η opts. The two symbolic halves cross-validate
through the kernel: reduce(compile([x..], e) applied to [x..]) ≡ e.

★ CERTIFIED (scripts/experiments/compile_roundtrip.py, n=5000, strat 1-3 vars × depth
1-5; results/compile-roundtrip/summary.json): round-trip rate **1.0000** — abstraction
and reduction are EXACT INVERSES on every sample ⇒ compiler correct by construction.
LIMITS quantified (λ measure): well-typed 0.941 (~6% operationally-correct-but-not-
simply-typable = the type-directedness/S2 boundary is real even where reduction is
exact); term/expr size mean 2.84× max 7× (S/W duplication = the representational limit).

⇒ the LEARNED surface shrinks to prose→logical-form only — exactly the Montague/DisCoCat
semantic parse (AGENTS.md S5 validation target). Both formal steps are constructible-
exact. Reinforces s226: more is constructible than the dyad assumed. 28 pytest pass.
Pages: compiler-as-loss.md §s226 stage 2.
