🎯 Zeros are the crystal backbone — structural, not emergent from training

Session 167. Three experiments confirm: oscillation-based zero detection
produces zero zeros across all runs. The zero signal is too weak for
training dynamics to discover.

Zeros come from the crystal / M-space SVD of the teacher. They're the
gaps between facets — the dark fringes that give the hologram its
structure. Without them, sign quantization creates a 35-facet noisy blob.
With 30% M-noise zeros as permanent backbone, the model beats float32
on loss (6.46 vs 6.68 on diverse data).

The architecture: zeros are computed once from the teacher and etched
permanently. They never un-etch. The etch mechanism operates only on
the ±1 positions — confirming/adapting signs via TD, improving loss by
0.56 over frozen signs. Backbone zeros + adaptive signs + learned gamma
= the complete topology stack.

20% backbone insufficient (barely matches float32). 30% works. Optimal
fraction is likely scale-dependent.
