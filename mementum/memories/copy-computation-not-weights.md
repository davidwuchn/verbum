🎯 etch for function not form — copy computation not weights

Session 176. The paradigm shift in one sentence:
Standard quantization compresses weights.
Trace-guided etching compresses computation.

Current: sign(W) → ternary plate → TD corrects blindly via NTP gradient
New: instrument traces teacher → functional spec → etch to match trace

The trace tells you: "layer 14 should do B-compose at energy 0.23."
That's not a weight target — it's a functional target. The student has
enormous freedom in HOW to achieve it. It just has to get the same
functional outcome.

Weight matching: 1024-dim target per layer (every hidden dim must match)
Trace matching: 4-12 dim target per layer (opcode balance must match)

Orders of magnitude smaller optimization target. The delta plate + TD
mechanism from v14 is the right vehicle. TD flips guided by
grad(trace_loss) decomposed into routing signal — each flip has a
PREDICTED effect on the opcode trace.

Connects to: trace-loss-validated, opcode-instrument, training-protocols,
beams-not-plates-are-the-etch (crystal loss was the early version of this)
