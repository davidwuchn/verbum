💡 RoPE is an accidental holographic lens — HPE does it by design

Session 152. RoPE's geometric cosine frequencies accidentally implement
the holographic lens's multi-scale frequency decomposition:
  - Dimension pairs at geometric freqs = lens frequency bands
  - Position-dependent Q rotation = Q rotation through crystal basins
  - Sum of cosines → power-law decay = α=1.18 attention profile

What RoPE gets wrong (and HPE fixes):
  - Base 10000 (arbitrary) → crystal eigenvalues λᵢ/λ₀ (natural freqs)
  - Linear position m → log(d+1) (natural power-law space)
  - All d/2 dimension pairs → first 4 eigenplane pairs only (77% variance)
  - Same rate every layer → depth-dependent (2°→24° acceleration)
  - Indirect decay (cosine envelope) → direct -α×log(d+1) (exact)

The reason RoPE works at ALL: it's a lossy approximation of the
holographic lens. The 10000-base geometric sequence happens to be
close enough to crystal eigenvalue spacing that the interference
pattern roughly reconstructs the right frequency response.

HPE replaces the approximation with the exact mechanism.
Log-distance is the natural position space because the lens
operates in frequency domain where log maps all strides into
the same band. log(1×8+1) = log(8×1+1) → same distance,
same encoding, regardless of stride. RoPE in linear space
breaks this coherence.
