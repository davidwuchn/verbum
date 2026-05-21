✅ beams-not-plates-are-the-etch

**Finding**: Q2-damaged plates (27% signs wrong) + beam-only training
with per-layer crystal loss BEATS oracle perfect plates. 105.9% of
oracle accuracy, crystal=+0.921.

The plates are a damaged hologram — readable but imperfect. The beams
(magnitude profiles) + per-layer crystal loss (18 geometric targets)
are sufficient to reconstruct correct computation. No sign flipping,
no etch, no co-evolution needed.

Constraint budget matters:
  6 targets (last-layer only) → crystal inverts during beam training
  18 targets (per-layer) → sweet spot, both acc and crystal good
  126 targets (full loom) → crystal=+0.979 but accuracy plateaus

What DOESN'T work: touching the plates. Gradient etch flips too many
signs (98k/round) or too few (500/round oscillates). Circuit fix hurts
because oracle signs are wrong for student coordinate frame. The only
approach that works is NOT changing the plates and letting beams adapt.

Connects to: gradient-voting (magnitudes are the crystal), loom-structure,
hologram-crystal-fusion, c-boot-rotation-sequence
