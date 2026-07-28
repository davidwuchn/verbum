💡 Q4 quantization re-routes the ROUTING register (gate), not the VALUE register — Michael's
Fact 1, confirmed register-clean (s279, wrapper/q4_routing_topology.py, portable RTN-Q4 on
Qwen3-0.6B + 4B). Register-attributed Q4 damage on the covering task: routing-Q4 (gate_proj)
flips gate SIGNS (5.1% @0.6B, 4.0% @4B, concentrated mid-stack L12–20 = the compute zone);
value-Q4 (up/down_proj) flips EXACTLY 0 gate signs. So a 4-bit step crosses sign thresholds in
the routing register → re-routes the compute (two-registers-of-topology + C3 topology-dominates);
value-Q4 only perturbs magnitude. Routing dominates DECISIONS (0.6B argmax flip 0.111 vs value
0.056 = 2×).

⚠ MARGIN is a value-magnitude CONFOUND: value-Q4 drops the covering margin MORE (1.14 vs 0.28)
without flipping decisions (the value register scales logits directly) → use decision-flip +
gate-sign-flip as the routing metrics, NOT margin (a λ measure lesson).

⚠ REDUNDANCY-GATING: easy LEARNED covering is Q4-invariant at 4B (acc 1.0, flip 0) even though
the re-route fires (4% gate flips) → Q4 fragility needs a NON-REDUNDANT target = the installed
operand. This IS why the installed-vs-learned discriminator works: installed value is
non-redundant (flips), learned behavior is redundant (absorbs the re-route).

Reframes R5 (ffn-function-bake-prereg §Stage-f): routing-topology measurement + ternary-mirror
robustification (signal-descent), NOT a bnb int8/int4 bar. bnb demoted to a cross-check.
