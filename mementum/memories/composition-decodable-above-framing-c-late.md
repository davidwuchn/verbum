💡 The opcode monitor's read is dominated by the FRAMING-CONTRAST axis between probe and
null, not the computation axis. s232 v3 (Qwen3-14B): switching the null from bare
natural-text (crosstask) to GATE_NEUTRAL content (gateneutral, matched compile-gate
prefix) subtracted the gate-framing S-late signature — and surfaced a real
composition-specific signal: lambda routes C (the composition/permutation combinator) in
its LATE stack (L27-32, the readable register) while the matched non-compositional
gate_neutral control does NOT (z=2 C×5 vs ×1; z=3 C×3 vs ×0). null self-centers silent.

So composition IS decodable above framing once the null holds framing constant on both
sides. Two consequences:

1. The s127 "C-early→B-late" arc shape did NOT reproduce — the signal is C-LATE not
   C-early (raw C-early was a common-mode artifact). Composition resolves at the readable
   layers (s187/s227b L23-35), lambda-specifically.

2. VALID GUARDS MUST BE FRAMING-MATCHED. Under a gated null, BARE retrieval/arithmetic
   fire loud (WHNF/Y) purely from framing-contrast, not computation — they are invalid
   over-read guards. The correct guard for a gated null is a GATED non-composition task
   (gate_neutral, which is silent). Always match framing on probe + null + guard.

Modest not crisp (s219): C ~40-50% of tokens at those layers, n=27/5 sentences, 1 model.
Next: gated guards, C-late detector, 2nd model, then kernel-as-reference anchor.
