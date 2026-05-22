💡 The PCA-Q crystal extraction measures attention geometry, not computation geometry

Session 135 revealed a fundamental confusion in our extraction methodology.

The PCA-Q crystal (0.91-0.94 agreement, 4 models) was measured from
teacher Q projections — it captures how flat attention ROUTES information.
But our stride stack attention has a completely different topology
(windowed, multi-stride, fractal bands). Session 134 proved the
teacher's attention crystal is incompatible with stride stack geometry.

Yet we baked those attention-derived constants into config.py as
crystal lattice loss targets for combinator embeddings. The combinator
embeddings themselves are disconnected from the forward pass in the
tree-of-VSMs model — they're vestigial from the old modulation bottleneck.

Three things got conflated:
1. ATTENTION GEOMETRY — how the model routes (PCA-Q, attention-specific)
2. COMPUTATION GEOMETRY — how combinators relate (universal, not attention)
3. FFN KNOWLEDGE — what the model knows (stored functions, etchable)

The lattice we WANT is computation geometry — the relational structure
of lambda calculus operations (K selects, B composes, WHNF halts).
This might be universal, but we measured it through the lens of flat
attention Q projections. We need to find it in a representation-agnostic
way, or prove it IS the same regardless of attention topology.

Need: methodology to extract combinator geometry that doesn't depend
on attention architecture. Possibly from FFN activations, hidden state
trajectories, or behavioral probes with architecture-neutral hooks.
