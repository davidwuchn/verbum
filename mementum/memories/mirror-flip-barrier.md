❌ mirror-flip-barrier

**Finding**: Soft mirrors initialized at 1.0 NEVER learn to flip to -1.
They only learn to block (→0). Tested with per-dimension AND per-position
(d×d) mirrors. Both show 0.0% flips, 0.5-1.0% blocks.

**Why**: From 1.0, the gradient pushes toward 0 (reduces noisy contribution).
At 0, the position is silent — no loss signal says "-1 would be better."
The gradient has to change direction at the 0 barrier. There's no path from
blocking to flipping through the continuous loss landscape.

**Fixes** (untested):
1. Stack: mirror_1 = loom signs (frozen), mirror_2 = correction at 1.0.
   Product already has correct signs; mirror_2 never needs to cross 0.
2. STE: quantize forward, continuous backward. Standard ternary trick.
3. Random init: some mirrors start near -1, GD refines from there.

**Rule**: Never init soft mirrors at 1.0 if you need them to learn flips.
The continuous optimization landscape has a basin at blocking, not flipping.

Connects to: soft-mirror-etch, crystal-gates-hologram, oracle-crystal-hurts
