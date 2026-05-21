🎯 Extract the equivalent of 70B dense into <1GB ternary, 200 tok/s on CPU.

Session 127. The north star target. A 70B model is 70B parameters
mostly encoding the same crystal geometry a 0.6B model already has.
The difference is the function library — more reductions, more
knowledge, more coverage. Taxonomy extraction doesn't copy 70B
parameters — it extracts the functions, discards redundant encoding,
designs an optimal layout, etches into ternary crystal.

The paradigm shift: everyone else scales up (bigger = more GPU = $$$).
We scale down — concentrate, don't expand. More source models = more
to extract = better sub-1GB crystal. Models get better without
getting bigger. Same operation at every scale: beta reduction.

Evidence chain: crystal universality across model sizes, magnitude
spectrum 0.995 agreement, Q2 27%-wrong-signs still reads, 220×
compression target already validated in principle.

Full stack: ternary crystal (CPU-native) + StrideStack (88 lenses,
O(L×704) not O(L²)) + holographic memory (no KV cache for stored
knowledge) = laptop inference at 200 tok/s.
