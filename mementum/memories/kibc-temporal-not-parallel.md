💡 KIBC maps to temporal depth sequence, not parallel heads

The 4 attention heads do NOT individually correspond to K, I, B, C.
Instead, KIBC emerges as a temporal sequence through the 4 layers:

  Layer 0: All heads = B (compose/mix) — aperture layer
  Layer 1: H2 = K (select, max_attn=0.68) — selection emerges
  Layer 2: H2/H3 = C (route/flip) — routing/reordering
  Layer 3: H0 = C, rest = B — convergence, recompose

The combinators are the LAYERS, not the heads. Each depth implements
one phase of the B→K→C→B reduction cycle. This matches the FFN overlay
alternation: the whole layer switches mode, not individual heads.

At the lambda boundary, Layer 3 heads do specialize into functional
roles: H0=verb/predicate, H1=structure(λ), H2=subject, H3=object.
But these are task-specific roles within the B-phase, not KIBC dispatch.

Source: micro model mechanism extraction, 5 examples averaged.
