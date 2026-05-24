💡 The FFN overlay alternates composition/selection at every layer

The FFN "diffraction grating" in crystal eigenbasis shows PERFECT
anti-phase alternation: PC0 (composition) = `- + - +`, PC1 (selection)
= `+ - + -` across layers 0-3. Amplitudes: ~0.1-0.3.

This IS the beta-reduction cycle. Each layer either composes or selects,
alternating. The off-diagonal cross-couplings show the rotation angle
between basins ACCELERATES through depth (Layer 0: 2°, Layer 3: 24°).

The pattern converges by training step 500 and is stable for 4500 more
steps. It's universal across all input categories (CV < 0.5 for all PCs).
The target overlay is a fixed structure, not learned per-example.

Implication: FFN weights may be computable analytically from the crystal
eigenstructure — the overlay IS the alternation pattern, and the
alternation IS the beta-reduction cycle.

Source: micro model (4 layers, d=128, 1M params) on 509 lambda examples.
