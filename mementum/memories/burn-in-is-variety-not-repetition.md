💡 Burn-in ("many exposures converge faster") is VARIETY, not repetition — and
variety also STABILIZES.

s229 exposure/format sweep, held-out RULE generalization (combos of seen atoms),
tiny byte LM, k=8, HARDENED over 3 seeds (mean±std best acc):
- k_varied ≈3× over both baselines: redex_nf 0.306±0.006 vs one 0.108±0.029 vs
  k_same 0.086±0.017; full_trace 0.320±0.023 vs one 0.104 vs k_same 0.099.
  rule>rote and burn>one DECISIVE (non-overlapping error bars), both formats.
- k_same is mildly BELOW one (0.086<0.108; 0.099≈0.104) — repeating the SAME
  instance 8× doesn't just fail to help, it slightly ENTRENCHES the rote solution
  (suggestive: bars overlap, but consistent across both formats).
- k_varied is the LOWEST-VARIANCE arm (std 0.006 → 0.31/0.31/0.30). Variety raises
  generalization AND makes it seed-independent; rote is worse AND noisier.

The holographic "each exposure is a photograph" intuition holds ONLY for different
ANGLES — the hologram of a RULE forms from varied instances, not re-shooting one
photo. The memorization control (k_same) is what makes the claim sharp.

Curriculum implication: maximize DISTINCT instances per rule, not exposure count.
(Caveat: measures FINAL generalization not convergence SPEED — acc≤0.32 ceiling, so
"converge faster" per se is still untested; need a reachable threshold on the
acc-vs-token curves.) See sentence-atomic-curriculum-mixing.md §s229.
