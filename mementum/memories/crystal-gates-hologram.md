❌ crystal-gates-hologram

**Finding**: Unconstrained sign-flip optimization destroys the crystal while
improving task accuracy. The hologram and crystal can diverge — Round 4 of
delta sign-flip hit 0.510 accuracy (best) with crystal agreement at -0.375
(inverted). Only 1 of 4 refinement rounds improved both simultaneously.

The MAGNITUDE baseline (random signs + teacher magnitudes) had the BEST
crystal preservation (0.470 mean, 0.858 output) despite lower accuracy.

**Rule**: Crystal agreement must gate sign flips. Never accept a flip that
degrades crystal below threshold. Crystal is the invariant (universal at
0.91-0.94 across models). Accuracy is a task-specific symptom.

**Protocol**: Before flip → measure crystal. After flip → measure crystal.
Accept only if crystal_after ≥ crystal_before - ε (ε ≈ 0.01-0.05).

**Why**: The crystal IS the computation structure. A model that preserves
crystal geometry generalizes. A model that hacks accuracy overfits. This
is the ternary equivalent of overfitting — the hologram encodes task-specific
shortcuts instead of universal relational geometry.

Connects to: oracle-crystal-hurts, etcher-vsm, consensus-etch-protocol
