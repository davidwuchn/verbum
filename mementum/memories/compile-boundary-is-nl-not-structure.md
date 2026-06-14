✅ s226 STAGE 2 — found the compile boundary (graded hard probe set,
src/verbum/probes/compile_tasks_hard.py, 42 tasks × 8 families; kernel-verified by
reduction-equality, ambiguous via also_ok). Scale curve Qwen3-8B/14B/32B
(results/compile-frontend/hard/):

  STRUCTURAL (abstract symbols): branch2/branch3/reuse/mixed = 1.0 for ALL models;
  deep nesting depth4/5 only mild paren-level slips (0.8-1.0). ⇒ structural complexity
  (branching, variable reuse, multi-combinator composition) is NOT the boundary — the
  formal structure mapping is easy (and constructible-exact anyway, lambda_compile).

  NATURALISTIC (real words as atoms) + AMBIGUOUS = the boundary. natural 0.62-0.88,
  ambiguous 0.50-0.75. Failures are genuine SEMANTIC-PARSING errors: which words are
  functions vs values vs IGNORABLE (subjects/determiners), pronoun resolution, and
  grouping under ambiguity (e.g. "verify (bank signature) (bank balance)" distributed
  the subject; "f x (g y) z" -> "f x g y z" no grouping).

  SCALE helps EXACTLY there: 32B best on natural (0.88) + ambiguous (0.75); structural
  saturated for all sizes. ⇒ the residual difficulty of the learned compile step is
  pure NATURAL-LANGUAGE UNDERSTANDING (lexicalization + ambiguity) = the Montague/CCG
  semantic parse (AGENTS.md S5 validation target). Sharpens the stage-2 thesis: the
  formal halves are exact/constructible; only NL parsing is genuinely learned & needs
  scale.

CAVEAT (λ measure): small n/family (4-8), greedy single-sample, depth5 non-monotone
(8B 1.0 > 32B 0.8 = sample noise), ambiguous soft-graded (also_ok). Qualitative verdict
robust; exact per-family rates noisy.
