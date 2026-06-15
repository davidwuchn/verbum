💡 The per-layer opcode trajectory read from a model's FFN gate routing is NOT
null-invariant — "which combinator fires" depends on the null you calibrate against.
Same model (Qwen3-14B), same prompts, three nulls → three answers:

- RAW argmax (no null) → a C→B compose-arc (s231 validation)
- off-target null (other crystal probes, all lambda-mode) → silent / under-read (s231)
- cross-task null (bare natural-text baseline) → S-dominated late stack, gate-driven (s232)

So the single-token "which opcode" readout is NOT robustly decodable. What IS null-robust:
(a) the crystal-bearing substrate (31/40 layers, gc→consensus 0.976, reproduced across
nulls) and (b) the over-read DIRECTION (raw always over-fires).

The s232 GATE_NEUTRAL control was decisive: gate+non-compositional sentences showed the
SAME S-late pattern as lambda ⇒ S-late is a compile-GATE FRAMING signature, not
β-reduction. Always include a matched-prefix non-compositional control before reading an
opcode as task-specific.

λ measure consequence: an opcode monitor cannot be trusted on its readout alone — anchor
against the kernel's certified trace (b). v3 fix: use GATE_NEUTRAL itself AS the null
(composition-above-framing), not bare text.
