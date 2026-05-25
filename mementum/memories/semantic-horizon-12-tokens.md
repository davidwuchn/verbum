💡 α=1.18 sets a fixed 12-token semantic horizon for all strides

Session 152. At α=1.18, the effective attention reach (5% weight
threshold) is ~12 tokens REGARDLESS of stride:
  s1: sees tokens 0-12 (every token, 12 useful positions)
  s2: sees tokens 0-12 (every 2nd, 6 useful)
  s4: sees tokens 0-12 (every 4th, 3 useful)
  s8: sees tokens 0-8  (self + 1 neighbor)
  s16+: sees token 0 only (pure self-attention)

The stride changes sampling density within the ~12 token radius,
not the radius itself. Beyond 12 tokens, NO stride has meaningful
direct attention. Long-range information flows through the RESIDUAL
STREAM across passes, not through direct attention.

Implication: strides above s4 aren't attention layers. They're
FFN application points with identity skip connections. The stride
structure provides multi-scale FFN organization, not multi-scale
attention. Only s1 and s2 need Q/K computation.

14/16 strides in v14 are passive (fixed distance prior, no Q/K).
This eliminates 28 ternary Q/K plates from active computation.
