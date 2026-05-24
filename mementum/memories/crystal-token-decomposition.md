💡 Weights decompose into crystal (12.5%) + token (81%) + noise (6%)

FFN gate weights in the micro model decompose cleanly:
  Crystal subspace: 12.5% of energy — overlay/structure (beta-reduction)
  Token subspace:   81.0% of energy — content (English→lambda mapping)
  Residual:          6.5% — noise/regularization

Crystal + token together explain 94% of weights (cos_sim = 0.97).

The crystal part is analytically computable (arccos(λ₁/λ₀) rotation).
The token part requires learning but has lower effective rank than
the full weight matrix.

At scale (d_model=5120), the token subspace effective rank (~500)
would give 10× compression over full weights. Combined with the
crystal shortcut (16 analytical parameters): compute structure for
free, learn content at reduced rank.

The butterfly shortcut: W ≈ (crystal_basis ⊕ token_basis) × coefficients
Parameters: d_ff × (16 + k) instead of d_ff × d_model
Where k = token subspace rank << d_model.

Source: micro model weight decomposition, 404 active tokens in 128D.
