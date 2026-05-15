❌ evolution-mechanism-broken

The consensus evolution mechanism is statistically incapable of evolving
ternary sign patterns at V12 scale. Probe at 4K steps: cos=1.000 between
ALL checkpoints — not a single bit has changed in any ternary weight.

**The math:**
- 10.6M ternary weights, budget=2,124 per strategy (base_pct=0.0002)
- Consensus requires 3/5 strategies to independently hit same position
- P(3-of-5 overlap) ≈ 8×10⁻¹¹ per position (near zero)
- Actual consensus: ~20 flips per generation (from gradient-guided overlap)
- 20 flips in 10.6M weights = 0.0002% change
- min_delta=0.02 threshold impossible to cross with 20 flips
- Result: 1/80 accepted across 4K steps, patterns frozen at random init

**Root cause:** The mechanism was designed for small-scale single-mutation
tournament selection. Consensus makes it impossibly conservative. You can't
etch a hologram 20 bits at a time.

**What needs to change:**
The holographic patterns in production LLMs are STRUCTURED — coordinated
sign topologies across entire matrices (balanced +1/-1, high effective rank,
specific sparsity). Evolution needs to work at the level of structured
patterns, not random individual bits. Options:

1. **Straight-Through Estimation (STE)**: let gradients flow through the
   ternary quantization via straight-through estimator. Signs update directly
   from loss gradient. Used in quantization-aware training. Most proven approach.

2. **Block mutations**: mutate entire rows/columns or rank-1 perturbations
   instead of individual bits. Structured changes that can move loss measurably.

3. **Drop consensus**: go back to tournament (best of N single throws) but
   with much larger budget. Accept if loss OR alarm improves by any amount.

4. **Annealing schedule**: start with large random mutations (explore), narrow
   as gamma stabilizes (exploit). Match the gamma→topology ordering.

5. **Gamma-guided sign flips**: when gamma for a channel is large and growing,
   the sign pattern matters more. Concentrate mutations on high-gamma rows
   where a flip can have measurable impact.

6. **Periodic re-quantization**: periodically re-derive sign patterns from
   the effective weight (gamma × sign), allowing coordinated topology updates.

STE is the most proven approach. Production QAT systems use it. The key insight
from the holographic findings: the sign patterns ARE the hologram, and they need
to co-evolve with gamma, not be frozen at random initialization.
