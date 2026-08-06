💡🔁 Round-trip reversibility (bidirectional-diffusion paper, s311) + multi-teacher
consensus = ONE label-free training objective. Direction flag (compile↔decompile =
our probe categories); forward-then-backward must return to start; discrepancy Cᵢ =
measurement-free error proxy, no ground truth.

**Surface round-trip FAILS (semantic equality: decompile∘compile is many-to-one) →
move the checkpoint to OPCODES** (the invariant across prose surfaces; opcodes =
microcode). Round-trip returns the same PROGRAM, not the same words. β-equivalence,
checkable because λ has a canonical normal form.

**We already have the opcode reader:** the gram route-map — reduction trajectories in
frame-invariant gram coordinates (9×9 = alphabet, 11 models), teacher↔student directly
comparable = "judge the loss easily." Per-step divergence LOCALIZES the drift =
GTSM dense-trajectory move applied to round-trip = a ROUTING-register loss (M8's
target, not value endpoint KL).

**The join (Michael):** per-step teacher AGREEMENT = the self-calibrating loss weight
(coherent→trust, disagree→cancel = A2 coherent-gain as a loss, GTSM w(L) data-derived
not hand-set). Consensus = reference trajectory; round-trip = label-free per-example
trust off-reference. Guardrail: calibrate to CONSENSUS not one teacher (else certify
its mistakes).

Page: round-trip-consensus-opcode-loss.md. First test (§P-OPCODE-CONSENSUS, existing
teachers, no student): do opcode TRAJECTORIES align per-step or only distributionally?
= the load-bearing uncertainty. Wires M6+M7+M8 into one objective.
