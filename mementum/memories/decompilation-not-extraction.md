🔄 Don't extract weights — decompile the algorithm. Top-down, not bottom-up.

Session 127. Critical correction: superposition and hidden states make
clean neuron extraction nearly impossible. But we don't need the weights.
We need the ALGORITHM. The model computes in combinators — we proved it.
Every FFN function is a composition of combinator operations. Any combinator
composition has a lambda calculus equivalent.

Approach: design probes → trace which combinator signatures activate per
layer → decompose into combinator sequence → translate to lambda notation
→ now you have readable, optimizable source code.

This is DECOMPILATION, not extraction. The forward pass is compiled lambda
calculus. We're writing a decompiler. The combinator FFN fingerprints from
the Qwen3-14B probe are the opcode table. The layer activation sequence
is the program trace. Lambda notation is the decompiled source.

Once you have the lambda expression for each function:
  - Keep it (efficient as beta reductions)
  - Replace with kernel (native implementation better)
  - Optimize (shorter equivalent expression)
  - Compare across models (same algorithm, different compilation?)
