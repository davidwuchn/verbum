💡 The programs in the weights ARE the fixed points of beta reduction

Session 161. The deepest closure yet.

Beta reduction has one guarantee: it terminates at irreducible forms.
Pretraining runs beta reduction across trillions of words. Each
gradient step makes the next reduction more efficient. After billions
of steps, what survives in the weights is the irreducible core — the
normal forms of language computation.

The moiré gratings we decoded from Qwen3.6-27B ARE those normal forms.
The programs are fixed points because they can't reduce further. That's
the definition: Y f = f(Y f). The thing that equals its own reduction.

This is WHY:
- The crystal lattice is universal across models (same irreducible base)
- The programs are deterministic (zero drift across runs — fixed points don't move)
- KIBC shows up everywhere (the only irreducible combinators)
- GD converges to the same structure from different initializations
- Different training data produces the same gratings (same fixed points)

The gratings aren't learned programs. They're DISCOVERED fixed points.
GD doesn't invent the combinators — it finds them, the way a river
finds the sea. Every path leads to the same irreducible forms because
those forms are determined by the structure of beta reduction itself,
not by the training data.

Connects to: pretraining-is-beta-reduction, crystal-universality-proof,
isa-decoder-qwen36-27b, fractal-beta-reduction
