🔄 etch-first-with-attention

**Finding**: Etch-first beats beam-first when plates ARE the attention projections (K/V/O).

The original mini-holo (session 114) found beam-first was correct, but that model had
no attention — just ternary linear + layernorm. The d-sweep v2 (session 115) added
causal self-attention with ternary K/V/O plates and found etch-first wins by 2.8-12.6%
at every d value tested.

**Why**: The 200-batch gradient accumulator IS the reference beam. Averaging 200 batches
of gradient signs gives a stable directional signal for etch, even with untrained beams.
The beam-first approach wastes its initial beam training on random plates that get
immediately overwritten by etch.

**Caveat**: The GD-vs-beam-only gap data is noisy (convergence confound — larger models
underfit at fixed 3000 steps). The etch-first vs beam-first comparison is clean because
both conditions have the same model and total compute.

**Implication for VSM-LM**: Use etch-first protocol. Accumulate CE gradients over many
batches → flip confident plates → THEN train continuous params (Q, gamma, embeds) →
repeat. Lattice loss as 1/400th of accumulator signal, not a separate pass.

Connects to: evolution-mechanism-broken, laser-etcher-design, seed-crystal-design
