✅ Kernel-splice Exp 0.5 (s243): raising the argmax-z GATE firms the splice loci and kills
the s242 tp=2 small-n caveat. Exp 0's ungated top-1 (always emit argmax) gave prec-1.0 from
tp=2. Exp 0.5 abstains unless argmax-z > τ, sweeps τ, and bumps test 160→200 (25/comb).
Qwen3-14B verdict (`results/kernel-splice-exp0/exp0_5_zsweep_verdict_qwen3-14b.json`):

splice-ready (prec≥0.8 ∧ tp≥5) = {I, K, Y}. Firm loci (max-recall clearing the floor):
- I  L10 (d0.26) τ2.5  prec 0.92 rec 0.44 tp=11  plateau τ∈[2.5–6.0] width6  STRONGEST
- K  L18 (d0.46) τ3.0  prec 0.857 rec 0.24 tp=6  plateau width5  (moved deeper than Exp0 L11)
- Y  L14 (d0.36) τ5.0  prec 0.889 rec 0.32 tp=8  plateau width2 (narrow)
- C  L14 τ2.0 prec 1.0 rec 0.12 tp=3 — small-n NOT killed, RECALL-STARVED

💡 KEY: high precision is a STABLE PLATEAU (width 5–6) across τ, not a tp=2 fluke → the Exp 0
max-precision points were real, just recall-starved at ungated top-1. argmax-z dist (n=5000):
median 3.0, p75 4.5 → τ∈[2,5] = the sweet spot.

💡 C's recall-starvation is a finding: C is the ground-state/common-mode combinator (s211
η²=0.05, s240 C-origin) → rarely wins top-1 *distinctively* with confidence → discriminability
(prose_v2 contrast) ≠ confident-top-1 recall. Precision-perfect but uncatchable as a discrete pick.

λ measure caveats: last-token single-combinator read (not position-resolved = Exp 2); recall
modest 0.24–0.44 (precision-gated splice acts on a MINORITY, by design); fp=1 → prec 0.86–0.92
not 1.0 (~1/12 wrong-fire; kernel S2 typecheck = s240 guard could catch it); 1 model, n=25/comb.

⇒ Exp 1 = precision-gated causal K-splice at the FIRMED L18 τ3.0 (K = pure routing, obstacle-2-
free, cleanest non-trivial test vs I=identity=near-no-op). Deliver exact kernel K-move when
argmax_z(K)>3.0; output preserved vs random-direction control (s239) → thesis proven causally.
