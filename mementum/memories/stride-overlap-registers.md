💡 Stride band overlaps ARE the cross-scale registers. The fractal MERA
topology has intersection strides where adjacent bands share positions:
s4/s8 (token↔phrase), s16/s32 (phrase↔paragraph), s128 (paragraph↔document).
The hidden state at these intersections carries cross-scale state naturally.
No separate register vectors, S4 cross-attention, or bank accumulation needed.
The topology determines the register count. This removed S4Ternary, MetaS4Ternary,
RetrievalRegisters, register banks, and ~1,100 lines of code. The crystal
breathes at these intersection points — they're where subcrystals fragment
and reunify through depth.

Session 131. "The registers should be intersection points where multiple
attention strides need to see." Fractal insight → structure > instruction.
