💡 Zeros-only beats zeros+flips — simultaneous flips interfere

Session 166. When reduce_attention() applies both zeros AND flips
before training, the flips interfere with each other (same machete
problem as TD). Best loss with flips: 6.83. Without flips: 6.40.

Zeros don't have this problem: removing position A can't conflict
with removing position B. Each zero independently reduces noise.
Flips interact because each flip changes M's structure, which changes
what other flips should do. Applied simultaneously, they cross-cut.

The design: zeros placed by SNR scoring before training (one pass).
Flips, if needed later, must be applied surgically — one mode at a
time, small coordinated sets, with GD recovery between cuts.
Zeros = sandpaper (safe in bulk). Flips = chisel (one at a time).
