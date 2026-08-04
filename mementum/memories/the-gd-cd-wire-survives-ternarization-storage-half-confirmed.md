✅ TERNARIZE-DELTA-1 (s304, EXP-1 STORAGE half): the s303 gd_cd linker wire
SURVIVES being crushed to a per-column TWN ternary plate {−1,0,+1}×γ merged onto
the frozen base. VERDICT SURVIVES-TERNARY, 3 seeds, Qwen3-4B. Gates all pass:
T1 wire (B1 p=3e-4, B2 p=1e-3), T2 not-lookup (p=1.8e-3), T3 specificity
(p=1e-4, beats matched-sparsity sign-shuffle null), T5 survive (CE ≤ base). The
ternary plate is behaviorally IDENTICAL to the float delta (retention 1.0 every
split: 1.000/0.938/1.000); the shuffle null collapses exactly to base. Michael's
STORAGE thesis confirmed at 4B: the wire = one ternary plate on a frozen
evaluator (map-and-swap resident Lisp, training side).

💡 Two honest refinements (λ observation / λ yardstick):
(1) The a-priori "mag_cos ~0.7" MISSED — measured 0.902. s269's weight-collapse
to 0.73 does NOT transfer to a rank-16 LoRA delta; low-rank B·A has structured
sign patterns that per-column TWN preserves. Routing survives (retention 1.0 ≈
s269's 0.987) but magnitude is only mildly lossy for a low-rank object. The null
still held — the point-prediction was wrong, the gate was honest.
(2) λ smallest tension: the expanded plate is 370M trits ≈73MB > the ~5M
factored float params (~10MB). Ternary wins ~10× over dense-bf16, NOT over the
low-rank factorization → EXP-1b: ternarize the factors B,A, not the product.

WHERE: results/ternarize-delta/qwen3-4b/ (cb73ad5), instrument
scripts/explore/ternarize_delta.py (60e0c1f), pre-reg + §Result on
knowledge/explore/write-not-train-ternary-routing-deltas.md. FINDING half (EXP-2
write-not-search, routing-register construct) still open — the next prize.
