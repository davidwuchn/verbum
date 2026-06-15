💡 Full β-reduction trace vs redex→NF is a budget-dependent trade, not a winner.

s229 exposure/format sweep (held-out rule generalization):
- full_trace gives higher ABSOLUTE acc (k_varied 0.351 vs redex_nf 0.297)
- but full_trace corpus = 2× the bytes (3392 vs 1672) → redex_nf wins PER-TOKEN
- full_trace's advantage appears ONLY under instance variety; at one/k_same the
  two formats are tied (0.122/0.135 vs 0.149/0.122).

So showing the work (every intermediate step = a long-exposure photograph) helps
absolute generalization but costs more tokens per photo; the snapshot (redex→NF)
is cheaper. Which wins depends on the token budget — the predicted crossover.

Rule: compare reduction-data formats PER-TOKEN, not per-photo; and expect the
format effect to interact with variety. See sentence-atomic-curriculum-mixing.md §s229.
