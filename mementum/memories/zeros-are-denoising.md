💡 Zeros in ternary topology are denoising, not blocking

Session 166. Sign quantization of a 13-facet attention kernel creates
a 35-facet noisy blob. The 22 extra facets are ghost modes from
small-weight positions forced to ±1 (same magnitude as signal).

Each zero removes one ghost route and sharpens the real facets.
M-noise zeros at 60% recover the gem from 74% → 92% energy
concentration (float32 target: 91%). Monotonic improvement — every
zero helps. Random zeros DESTROY the gem (→ 57%), proving zeros
need geometric guidance.

The no-block constraint on attention (session 148) costs performance.
v14 attention has 0% zeros in base plates. FFN has 31% natural zeros.
The attention needs zeros too — not for blocking routes, but for
sharpening the interference pattern.
