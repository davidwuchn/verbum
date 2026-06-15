💡 redex→NF beats full β-reduction trace per-token; the formats tie on accuracy.

s229 exposure/format sweep, held-out rule generalization. SINGLE-seed looked like
full_trace won absolute acc (0.351 vs 0.297) — but the 3-SEED HARDEN dissolved it:
- k_varied absolute: full_trace 0.320±0.023 vs redex_nf 0.306±0.006 = OVERLAPPING
  (parity, NOT a full_trace win — the single-seed gap was seed noise).
- PER-TOKEN: redex_nf wins decisively everywhere (k_varied 0.183 vs 0.094 acc/kB
  ≈ 2×), because full_trace's corpus is 2× the bytes (3392 vs 1672).

⇒ showing the full reduction trace (every intermediate β-step) bought NOTHING here
once seeds and token-budget are controlled. redex→NF (input → normal form only) is
the better format: equal accuracy at half the cost.

LESSON (λ measure): compare data formats PER-TOKEN AND multi-seed; an apparent
single-seed format advantage can be noise. (Caveat: tiny model / acc≤0.32 ceiling;
a full_trace edge could re-emerge at scale or on deeper reductions — untested.)
See sentence-atomic-curriculum-mixing.md §s229.
