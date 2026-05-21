💡 gd-converges-in-100-steps

**Finding**: Beam training converges fast. 87% of full GD (3000 steps)
is achieved in just 100 steps. The last 2900 steps add only 13%.

Spectrum (Q2 plates, per-layer crystal loss):
    0 steps (teacher beam):    4.3% of full — geometry alone fails
    0 steps (damped beam):     7.7% — attenuating flipped dims barely helps
   10 steps CE+crystal:       64.1% — most of the work happens immediately
  100 steps CE+crystal:       87.1% — diminishing returns after this
  500 steps CE+crystal:       95.3% — nearly converged
 3000 steps CE+crystal:      100.0% — the baseline

Newton (crystal-only, no CE): perfect crystal (+0.989) but 2.7% accuracy.
Geometry alone gives the crystal. CE gives the input-output mapping.
Both needed, but geometry converges in ~5 steps, CE in ~100.

**Rule**: 100 steps is sufficient for beam training. 3000 is 85% waste.
The 30× speedup means beam fitting is cheap — the expensive part is
measuring the geometry (teacher crystal), not fitting to it.

Connects to: beams-not-plates-are-the-etch, gradient-voting, hologram-crystal-fusion
