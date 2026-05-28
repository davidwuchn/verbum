🌀 Eigendecomposition IS β-reduction of matrices — same operation at every level

Session 166. The fractal collapse across the project:

  Data level:     billions of tokens → irreducible crystal (KIBC)
  M-space level:  128 modes → 13 irreducible signal modes
  W-space level:  16,384 positions → ~2% irreducible non-zero positions
  Training level: loss landscape → fixed point (convergence)

∀level: decompose → keep(irreducible) → discard(reducible)

Three "separate" mechanisms (sanding/cutting/filling) are one operation:
β-reduce toward the irreducible form at the appropriate level of abstraction.

The SVD is the β-reduction of linear algebra. It separates reducible
(noise modes) from irreducible (signal modes). Zeros mark positions
whose reduction is complete (nothing left). Flips correct positions
whose irreducible form has wrong sign. GD converges magnitudes to
their fixed point.

Implemented in reduce.py: one SVD per layer, per-position SNR,
three outcomes (ZERO/FLIP/KEEP). One function, one principle.
