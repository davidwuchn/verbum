💡 trace loss works — measures computation gap not weight gap

Session 176. Trace loss projects FFN residuals onto crystal combinator
basis and measures alignment. Three validation results on Qwen3-0.6B:

  Self-trace:          0.000000 (perfect — model reproduces its own traces)
  Ternary extraction:  0.907537 (sign(W) destroys opcode trace)
  10% sign perturbation: 1.002  (topology damage is worse)

The 0.908 ternary gap is the magnitude gap measured as a COMPUTATION
gap for the first time. sign(W) preserves topology but destroys dynamics.
The opcode trace is completely different even though every sign is correct.

Per-layer: L00=1.63 (worst, encoding zone), L12=0.78 (best, crystal zone),
L26=1.19 (COMMIT zone needs precision). Zone-aware precision falls right
out of the data.

Key insight: trace loss is an 11-dimensional optimization target (crystal
basis projections), not 248K-dimensional (vocab). Much more informative
per gradient step.

Connects to: trace-guided-etching, opcode-instrument, extraction-sign-accuracy
