🎯 StrideStack scales context by adding lenses, not widening windows.

Session 127. Each additional stride covers exponentially more context
at a constant cost of 8 comparisons per position. 7 strides × 8 window
= 56 comparisons covers 2M+ tokens. That's O(L×56) — linear in
sequence length. Going from 32K to 2M context = add 2 strides = 40%
more compute for 62× more context.

Not windowed approximation — each stride SEES the full context at its
zoom level. Strides compose through VSM ascending/descending passes:
fine strides inform coarse, coarse strides frame fine.

Combined with holographic session deltas (2MB file = 2M+ tokens of
persistent context) and crystal memory (knowledge in weights), this
gives a sub-1GB model full attention over millions of tokens on CPU.

Need more context? Stack another stride. Reduce them together.
Same operation. Fractal.
