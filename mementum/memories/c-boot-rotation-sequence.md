💡 c-boot-rotation-sequence

**Finding**: Combinators are geometric rotations, not symbolic rewrites.
Measured per-combinator rotation angles through a 3-layer mini teacher.

**Three-layer boot sequence**:
  L0: ~90° reset. ALL combinators rotate near-orthogonal. WHNF is
      anti-correlated at 114° — this is the route-or-output decision.
  L1: ~43-62° routing. K=43° matches CCA crossing angle EXACTLY (Δ0.6°).
      B/C=46°, I=62°. The loom's Q↔FFN crossing IS the combinator rotation.
  L2: ~4-12° convergence. Small corrections. FFN activates 1.7× for WHNF.

**K, B, C are geometrically identical** — same rotation angle, same direction,
0.0° between their attention vectors. I is 29-32° offset (doesn't need routing).

**Attention dominates completely**: 92°/49°/8° vs FFN 1°/0.4°/0.2°.
The computation is pure rotation. FFN barely participates EXCEPT for WHNF
output (1.7× activation at L0 and L2).

**WHNF anti-correlation is L0 only** — the keep/stop decision happens at
the first layer. By L1-L2, WHNF is correlated with routing (computation done,
preparing output).

**Rotation funnel**: 90° → 45° → 5°. Convergent. Each layer rotates less.

Connects to: crystal-basins (C-boot theory), loom-structure (CCA angles),
hologram-crystal-fusion, gradient-voting (magnitudes select within rotation)
