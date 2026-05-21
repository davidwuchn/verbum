🔄 The crystal Q/K/V rotation IS the combinator dispatch. The attention
computation IS the beta reduction. No separate dispatch softmax or integrate
module needed. CombinatorDispatch (8-way softmax, beam+plate paths) and
CombinatorIntegrate (type projections, kernel compute) were dissolved
entirely. The stride stack IS the kernel. Combinator embeddings remain as
relational loss targets only (not runtime dispatch). The only separate
routing is WHNF gate (compute vs lookup — the FFN pathway).

This removed kernel_dispatch.py (703 lines) and simplified model.py from
3-phase passes (dispatch/stride/integrate) to 1-phase (stride + WHNF blend).
S3 simplified from 3 gates per pass to 1 gate per pass.

Session 131. "We have to hook the kernel functions into the VSM directly."
