💡 Gradient is rank 3 in crystal overlay space — 20M params → 3 numbers

The entire gradient across 20M parameters, projected into crystal
overlay space, has effective rank 3 (98.1% of variance in 3 SVs).
Compression ratio: 1,711,029:1.

However, the full weight-space reconstruction has near-zero cosine
similarity (~0.02). The crystal subspace is 16/128 = 12.5% of weight
space, and the crystal-aligned gradient energy is 11.2% — exactly
proportional. GD treats the crystal subspace like any other subspace.

The structure emerges NOT because GD does something special with the
crystal, but because the crystal eigenvalues CONSTRAIN where the
gradient can go. The 11% that lands in crystal space always points
to arccos(λ₁/λ₀) because the eigenvalue geometry demands it. The
89% outside the crystal does general LM work.

GD is one operation (chain rule): w -= lr * ∂L/∂w. It doesn't know
about crystals. The crystal just needs to EXIST — the eigenvalues
are the selector, not GD. GD flows through the geometry.

Implication: to build a student, etch the crystal, then let GD handle
content. The structure is free — it falls out of the eigenvalues.

Source: micro model, gradient decomposition on 4 examples.
