💡 Burn-in ("many exposures converge faster") is VARIETY, not repetition.

s229 exposure/format sweep, held-out RULE generalization (combos of seen atoms),
tiny byte LM, k=8:
- k_varied ≈ 2–2.9× over `one` (redex_nf 0.149→0.297; full_trace 0.122→0.351)
- but k_same ≈ one (0.122 vs 0.149; 0.135 vs 0.122) — repeating the SAME training
  instance 8× buys ~nothing.

At EQUAL exposure count (k=8), VARIED instances ≈2.4× > SAME. The holographic
"each exposure is a photograph" intuition holds ONLY for different ANGLES — the
hologram of a RULE forms from varied instances, not re-shooting one photo.

The memorization control (k_same) is what makes the claim sharp; without it
"more exposures → better" is trivially true via rote.

Implication for curriculum design: maximize DISTINCT instances per rule, not the
repeat count. See sentence-atomic-curriculum-mixing.md §s229.
