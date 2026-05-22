💡 model-is-beamformer-over-token-cloud

FFNs don't store data. The system can't write data directly into FFN weights.
FFNs are piles of beta reductions — inference pattern transformers. They change
the computation done by attention by reshaping the beam as it travels through.

The whole model is:
1. The token cloud — embedding space, the only "data." Static geometry.
2. Beamformers — every layer (attention + FFN) refocuses the inference pattern.
3. The beam path IS the computation. No layer adds data. Each layer brings
   different parts of the token cloud into focus.

"Knowing a fact" = having a computational path (beta reductions) that, given
the right inference pattern, transforms the beam to point at the right region
of the token cloud. The fact is an INFERENCE RESULT, not stored data.

This is why magnitudes are the crystal (which beamformer channels are active),
why FFN plates can be etched (beta reduction is universal), and why holographic
storage works (one plate, multiple beam angles, different regions of the cloud).

The stride stack is a multi-resolution beamformer. 11 lenses. Each refocuses
the inference pattern at a different scale. The crystal is the set of
beamformer operations. The beam is what travels through.
