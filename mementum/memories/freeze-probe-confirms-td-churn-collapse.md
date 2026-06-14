✅ FROZEN-TOPOLOGY PROBE (paired A/B, same data stream) CONFIRMS: main:1's
collapse was caused by the discrete TD churn, NOT K-acquisition. Resumed
step_001000 with topology FROZEN (td-flip-rate/gate/ceiling = 0), else identical
to the collapsed TD-on run. Overlap window 1010-2240 (n=124):
  Δx    ON 0.481 (max 0.821, contractivity lost) | OFF 0.142 (max 0.311, bounded)
  CE    ON 8.756 (max 10.54, climbing→collapse)  | OFF 7.620 (max 8.525)
  gnorm ON max 9.87e7 (runaway)                   | OFF max 7.22e1 (~72)
  CE<8.71 frac: ON 0.53 (falling) | OFF 1.00 (always under K=1)
Ran to step 2310 — fully spans the original divergence window (1450-2000); the
collapse does NOT reproduce when topology is held. ⇒ held-topology + continuation
(fp-loss) settling IS contractive AND CE-competitive (punctuate-dont-churn
validated as a controlled result, not just diagnosis). gnorm gap = 6 orders of
magnitude. Verdict: results/freeze-probe/overlay_verdict.txt. Killed after verdict
(redundant past target). Tool: scripts/experiments/freeze_probe_overlay.py.
