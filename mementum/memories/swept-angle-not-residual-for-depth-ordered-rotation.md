🔁 To test "coherent DEPTH-ORDERED rotation" in a residual-stream trajectory,
use the SWEPT ANGLE in an amplitude-defined band vs a NORM-MATCHED null — NOT
the rank-2 DMD reconstruction residual (§P-DEPTH-CARRIER method, s348).

Why residual FAILS (learned the hard way, instrument-first re-scope):
- ORDER-BLIND: a set of in-plane increments is rank-2 in ANY order, so
  increment-shuffle is never beaten — the residual cannot see depth-order.
- TOO BRITTLE: a genuinely clean planted rotation with just 15% amplitude
  noise already reads GENERIC (resid 0.38→0.76); real neural trajectories
  (resid 0.53-0.64) always read GENERIC regardless of truth.

Why SWEPT ANGLE works:
- swept = Σ|Δθ| in the top-2 SVD plane of the DC-centered band; wind = |ΣΔθ|.
- Beats the NORM-MATCHED null (same per-layer step norms, isotropic-random
  directions) ⟺ the rotation is more than matched-magnitude random motion
  (defeats the Karhunen-Loève artifact: PCA of ANY random walk traces smooth
  arcs).
- wind/swept ≈ 1 ⇒ MONOTONE (one-directional, coherent).
- increment-shuffle DOES reduce swept ⇒ order-sensitivity IS captured.
- GUARD: shuffled-layer is NOT a valid null for swept (permuting positions
  INFLATES swept by jumping around the plane) → non-gating.

The DMD phase/|λ| is a per-step AVERAGE — it flattens a late-concentrated
flat-then-sweep shape into a fake uniform rate. Read the actual per-layer
phase, band it by amplitude, and null it against norm-matched.
