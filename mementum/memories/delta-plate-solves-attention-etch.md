💡 delta-plate-solves-attention-etch

The attention etch problem (S134: teacher flat attention incompatible with stride
stack geometry) is solved by the delta plate architecture:

Etch the FULL crystal (including attention) into a frozen base plate. Initialize
a delta plate to +1 (pass-through). Train the delta with TernaryDescent.

The β-reduction-forced parts (KIBC unit cell, WHNF anti-correlation) transfer
directly from teacher — they're geometry-invariant. Only the routing-specific
parts (how to find arguments via strides vs flat attention) need to change.

The delta IS the measurement of "what's different about stride-stack attention."
After training, positions that stayed +1 = universal crystal. Positions that
flipped = geometry-dependent routing. You get the decomposition as a byproduct.

Reduction: new_base = base ⊙ delta (ternary × ternary = ternary, lossless).
Reset delta to +1, iterate. Each round refines the stride-stack crystal.
