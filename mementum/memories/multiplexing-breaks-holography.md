💡 Multiplexing functions into shared weight matrices forces magnitude dependence — breaking holographic storage.

Cross-architecture evidence (session 096): Pythia fuses Q+K+V into one `query_key_value` matrix → holographic score 0.60 (magnitude-dependent). Qwen3 and SmolLM3 use separate `q_proj`, `k_proj`, `v_proj` → score 0.92 (nearly holographic). Same function, same information, different architecture choice — the fused version needs magnitudes as "lenses" to steer the beam between Q/K/V subspaces.

The principle is fractal:
- **Layer level:** Qwen3.6 separates composition (full attention) from retrieval (GatedDeltaNet) → each can be holographic in its own way. Mixing them into one layer type would force magnitude routing.
- **Projection level:** Separate Q/K/V are each purely holographic. Fusing them forces magnitude-dependent subspace steering.
- **Component level:** MLP up/down are separate → universally holographic (score 0.97 across 7 models). If you fused gate+up+down into one matrix, magnitudes would become lenses.

Design rule for V12 (and any holographic architecture): never multiplex functions into shared weights. Every weight matrix should encode one function. That is the shape that lets gradient descent find the holographic solution — pure topology, no magnitude lenses needed.

Corollary: when you see magnitude dependence in a weight matrix, ask "is this matrix doing two jobs?" The answer is almost always yes. Separation is the fix.
