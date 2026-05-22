💡 gradient-is-routing-plus-calibration

The gradient through a ternary weight encodes TWO signals that need different
optimizers. Compare the descent direction (-grad) to the current topology sign:

  descent agrees with sign → CALIBRATION → Adam (adjust magnitude)
  descent opposes sign     → ROUTING     → TernaryDescent (flip sign)

When mixed, Adam wastes gamma compensating for wrong signs (routing) and TD
gets noisy confidence from magnitude-adjustment gradients (calibration).
Decomposing them lets each optimizer handle only what it's good at.

Per-row routing fraction is a diagnostic: high = topology is wrong at this row.
Should decrease during training as TD fixes the topology.
