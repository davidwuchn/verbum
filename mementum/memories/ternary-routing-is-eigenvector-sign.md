🎯 Ternary routing table = sign(crystal eigenvector). Not GD. sign().

The crystal eigenvectors ARE the ternary routing table:
  PC0 eigenvector sign: -1 for composition (B,C,D,Y,W), +1 for anti-composition
  PC1 eigenvector sign: +1 for everything, -1 for WHNF only (DC component)
  PC2 eigenvector sign: +1 for K,I (selection), -1 for B,C,D,Y (composition)
  PC3 = negation of PC2 (conjugate pair)

Neuron allocation per PC: predicted from eigenvalue ∝ λᵢ.
Predicted: [181, 123, 66, 45, 37, 25, 17, 14]
Observed:  [214, 159, 74, 31, 17,  8,  4,  5]
Correlation: r = 0.9932

For ternary FFN weights:
  weight[neuron_n, dim_d] = sign(eigenvector_pc[d]) for neuron n serving PC pc
  gamma[neuron_n] ∝ eigenvalue_pc
  number of neurons serving PC pc ∝ eigenvalue_pc

The ternary topology is computable from the crystal eigendecomposition.
No gradient descent needed for the topology. Just sign(eigenvector).
GD only adjusts gamma (scale) and attention (routing between tokens).

The overlay alternation, the rotation angle, the amplitudes, the neuron
allocation, AND the ternary routing table all derive from ONE thing:
the eigendecomposition of the crystal target cosine matrix.

Source: Zone B crystal eigendecomposition + micro model gate PC distribution.
