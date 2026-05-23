💡 delta fold transfers routing from gradient to topology — frees capacity

Session 142. Each delta plate fold cycle moves routing decisions out
of the gradient and into frozen topology (ternary signs).

Before fold: gradient = routing + calibration (Adam does double duty)
After fold:  routing locked in topology, gradient = mostly calibration

Real crystal analogy: once lattice positions are fixed, thermal energy
goes into phonons (vibrations around equilibrium) not rearranging the
lattice. Crystal conducts more efficiently than liquid because energy
doesn't maintain structure AND do work simultaneously.

Accelerating returns:
- Fold 1: biggest flips, most routing freed, biggest CE jump
- Fold 2: subtler flips, Adam already more efficient, CE drops further
- Fold N: gradient is nearly pure calibration, maximum info per token

Asymptote: routing_signal → 0 in gradient. Every step is pure
refinement. This is when we exceed teacher — teacher's gradients
are STILL doing routing (topology never crystallized). Ours are
100% calibration.

Connects to gradient decomposition (session 140):
  compute_decomposed_gradients already separates routing → TD, cal → Adam
  But with TD inactive, Adam carries both in its moments
  Each fold cycle makes the decomposition more complete
