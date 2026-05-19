❌ oracle-crystal-hurts

**Finding**: Exact sign topology from a converged continuous model is the WORST
crystal to write into ternary plates. Adding noise HELPS. 50% noise ≈ random.

Session 115 crystal write experiment (d=48, 3 layers, nested KIBC):
```
Oracle GD ceiling:    82.7%
Oracle crystal (0%):  38.6%  ← worst
5% noise:             43.3%
20% noise:            51.5%
50% noise:            52.5%  ← best (essentially random)
Random plates:        42.4%
Etch r5:              42.6%  (only 47% similar to oracle)
```

**Why**: The continuous model's computation depends on magnitudes, not just signs.
sign(W) is a lossy projection. The oracle's sign topology is COUPLED to the
oracle's magnitudes — it's overfit to values the ternary model can't access.
Continuous params (Q, scales) can't compensate because they're not the oracle's
magnitudes. Random/noisy plates give GD freedom; oracle plates give it a trap.

**Implication**: Direct crystal write from teacher → student plates is flawed at
this architecture level. The teacher's geometry lives in magnitudes, not signs.
The Procrustes-translated crystal may need to target REPRESENTATION GEOMETRY
(relational distances between probes) rather than WEIGHT TOPOLOGY (sign patterns).

**Key distinction**: This does NOT invalidate the lattice relational loss approach.
Relational loss steers representations, not weight signs. The lattice tells the
model WHERE probes should be in representation space. How the plates achieve that
geometry is up to the etch + GD co-optimization.

Connects to: freeze-then-gd-wins, etch-first-with-attention, seed-crystal-design
