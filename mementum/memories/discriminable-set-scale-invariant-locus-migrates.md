💡 The {C,I,K,Y} discriminable set is SCALE-INVARIANT (the WHICH), but the LOCUS migrates
deeper with scale (the WHERE). s238 v5 lead 2d prong 3 (kernel_reference_prose_v2.py, raw-z
contrast NO argmax, held-out crystal-prose, n_test=160, heldout 20/comb) on Qwen3 8B(36L) /
14B(40L) / 32B(64L). Completes the per-model sweep the s234 prong-1 result asked for.

★★ SET MEMBERSHIP ROBUST — all three scales n_sig=4, exactly {C,I,K,Y}; B flat, D anti, W
anti/n.s. at EVERY scale:
  C   8B 5.33✓  14B 5.71✓  32B 6.28✓
  Y   8B 5.83✓  14B 6.86✓  32B 9.37✓   (STRENGTHENS monotonically with scale)
  I   8B 3.64✓  14B 3.83✓  32B 3.42✓
  K   8B 2.36✓  14B 2.12✓  32B 2.09✓
  B   8B −0.06  14B −0.05  32B +0.64 n.s.   (flat everywhere)
  D   8B −5.98  14B −4.61  32B −5.55         (robustly ANTI, shallow L3 frac 0.05-0.08)
  W   8B −1.82  14B −2.27  32B −1.95         (anti/n.s.)

⇒ discriminability-is-a-combinator-property (s234) is SCALE-ROBUST, NOT 14B-specific. The
composers/recursion {C,Y} get MORE discriminable at scale (Y especially).

⚠️ THE LOCUS MIGRATES DEEPER (fractional depth) with scale — the WHERE is NOT invariant:
  C frac 0.25 → 0.33 → 0.39
  Y frac 0.25 → 0.35 → 0.58
  I frac 0.33 → 0.33 → 0.55
  K frac 0.31 → 0.30 → 0.77 (jumps deep at 32B)
This RECONCILES s232 ("C-locus shifts with scale", and the fixed-depth≥0.6 detector
mislocated 8B/32B): the locus genuinely migrates, but the SET MEMBERSHIP is the scale-
invariant. The s232 fixed-depth detector was reading a migrating WHERE as a changing WHICH.
LESSON: when sweeping scale, the discriminable SET is the robust observable; the per-layer
peak is scale-dependent — calibrate locus per-model, don't fix a depth zone.

★ D is the most consistent anti-signal: shallow fixed L3 (frac ~0.06), t≈−5/−6 at all
scales — D-prose routes D LESS than baseline, robustly. (Still unexplained; a real wrinkle.)

CAVEATS (λ measure): 1 model CLASS (Qwen); last-token locus; single-combinator labels (not
composite trace-order); crosstask null; raw-z layer-AVERAGED headline (peak-layer read
localizes). Code: kernel_reference_prose_v2.py (model-tagged outputs, no new code).
