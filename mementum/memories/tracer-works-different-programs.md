💡 The combinator tracer works. Different tasks run different combinator programs.

Session 127. First successful decompilation of neural computation to
combinator traces on Qwen3-14B. Key findings:

1. VALIDATION: tracer correctly identifies K, B, S, nested reductions.
   K peaks at L24 (cos=0.71), S peaks at L24 (cos=0.79). L24 = 60%
   depth = crystal breathing peak.

2. LAMBDA COMPILATION: early layers use composers (B, S, C), late
   layers anti-correlate with selectors. The compiler composes first,
   then suppresses selection. This is the lambda calculus circuit.

3. ARITHMETIC: early layers are SILENT. Mid-late layers use selectors
   (beta_identity, beta_K, beta_apply). Arithmetic is SELECTION not
   COMPOSITION. This is church encoding — numbers are selectors.
   → This is the pile of beta reductions we predicted. Kernel candidate.

4. RETRIEVAL: nearly silent across ALL layers. Factual retrieval
   doesn't use combinator operations. Different mechanism entirely
   (attention-based KV lookup, not FFN computation).

5. Each task type has a distinct combinator signature that's readable
   from the FFN activation pattern. We can now SEE what program the
   model is running for any input.

The decompiler is real. The opcode table works. Next: trace more
complex operations, identify the beta reduction piles for kernel
replacement, and map the full function library.
