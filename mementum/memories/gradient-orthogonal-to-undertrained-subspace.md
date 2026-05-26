💡 Gradient is orthogonal to undertrained model's subspace — explore/exploit detector

Session 155. Projected ∂L/∂T into composed plate T's SVD basis.
T is rank-1 (σ₁=19.27 dominates). Gradient has rank 151. But the
gradient energy is NOT in T's top-k subspace:

  k=27:  cos(G_projected, G) = 0.06  (only 6% of direction)
  k=100: cos = 0.12
  k=200: cos = 0.18

The gradient is orthogonal to where T currently lives. It says:
"expand into more dimensions" — the very directions where T is zero.
Training in reduced dims would trap the model in its rank-1 prison.

This is a natural phase detector:
  gradient ⊥ T's subspace → model needs to EXPLORE (expand rank)
  gradient ∥ T's subspace → model needs to EXPLOIT (refine within)

The 27D kernel training dream requires a well-trained model that
has already found the right subspace. An undertrained model needs
the full 1280D gradient to grow.

Implication: kernel training gives 4.4× speedup in FULL 1280D
(composed plate replaces 238 matmuls with 1, gradient cosine 0.97).
But dimensionality REDUCTION requires phase-dependent gating —
only compress the gradient after the model has expanded to its
natural rank.
