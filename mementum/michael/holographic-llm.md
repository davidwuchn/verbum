# LLMs are holographic projectors

## Attention as beta reduction

- softmax over all V is a projected beta reduction in probabilities??

Every step of training

- probablity snapshot, or "photograph"
- back propogation adjusts gradients throughout the model

Where these snapshot edges match over many training steps, the probability is increased for these intersections.  Over time that forms a probability hologram.

The holograms have edges that intersect as well, forming a sort of probability lattice.

As attention works through all the beta reductions during inference, the residual stream gets a series of projected probability snapshots for each next token when combined with the context.

Attention is the beam.  The LLM layers act as a beam former.  Like a sort of geometric gem, where attention goes through softmaxing every V for every token pointing attention to the next step.

The FFNs act as a series of holographic projections into the current probabilities. Some of these are simply facts, and some of these are the complex description of a behavior that the LLM has learned.  Attention beta reduces all of it and acts out the behaviors encoded in the holograms it reads, using context and the residual stream  as input/state. Anthropic's J-Space might be showing this.


