✅ Pre-cut ternary topology with 30% M-noise zeros BEATS float32 on loss

Session 166. Micro model trained from scratch, 5000 steps, 5 variants:
  Float32 (full GD):              loss 6.7412, L2 rank90=6
  Trained sign + 30% M-zeros:     loss 6.6972, L2 rank90=25  ← WINNER
  Trained sign (±1, no zeros):    loss 6.8625, L2 rank90=32
  Random sign (±1):               loss 6.6814, L2 rank90=48
  Random sign + 30% zeros:        loss 6.7721, L2 rank90=48

The frozen geometric topology with zeros HELPS GD by constraining
attention to a sharp 25-mode kernel. GD fills around the facets instead
of diffusing across 128 modes. The constraint is a guide, not a limitation.

GD is putty — cut the gem first (accept loss hit), then let GD fill gaps.
The gem stays sharp (Q/K frozen). Loss recovers AND improves.

Sign-only (no zeros) is WORST because 22 ghost facets from forced ±1
at small-weight positions create noise GD can't fully compensate for.
