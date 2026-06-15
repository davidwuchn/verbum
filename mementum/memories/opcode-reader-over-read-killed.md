💡 The validated relational opcode reader KILLS the raw-argmax over-read on a real model
(Qwen3-14B) — but at z=3 last-token it now UNDER-reads. The truth is between; v2 needs a
cross-task null + per-token reading.

s231 (a): built `RelationalCrystalClassifier` (scripts/instruments/relational_opcode.py)
— reads FFN-routing opcodes in the GATE register (sign(gate)-CMR), against the consensus
crystal, null-calibrated per op, emits an opcode ONLY if z>thresh else NO-OP. Validated
on Qwen3-14B (the s127 model) vs a raw-argmax control (opcode_audit_validation.py,
results/opcode-audit-validation/verdict.json, `143ccda`):

- ✅✅ OVER-READ KILLED: RAW fires an opcode for 100% of tokens — `W` across ~all
  retrieval layers (W = this model's common-mode/gauge direction) = the audit-meta-
  pattern false signal (s202). RELATIONAL no-ops retrieval (0.8), never a uniform winner.
- ✅ substrate real: 31/40 layers crystal-bearing, gc-to-consensus up to 0.98 (the
  universal crystal IS in Qwen3-14B's gate register).
- ✅ retrieval-silent reproduced (s127 FFN-silent retrieval).
- ⚠️ UNDER-read: RAW per-layer shows a consistent C→B compose-arc across ALL 5 lambda
  prompts (C L2–12, B L13–33 = the real s127 compose signature, task-specific not common
  mode). Relational at z=3 last-token no-ops it entirely. Causes: last-token LOCUS (a
  sentence's final token isn't one opcode; s227 wrong-locus) + NULL mis-spec (off-target
  null = other crystal probes, all lambda-mode → low power).

FIX (v2, the key one): build the null vs a NON-combinator baseline (natural text /
retrieval), NOT vs other crystal probes. Plus per-token reading + z-sweep + per-layer
trajectory output. Then real lambda B-structure clears while retrieval stays silent.
This is also the trustworthy per-token trace the kernel-reference audit (b) needs.

Architecture note: the gate routing register needs a GATED MLP (SwiGLU) — pythia
(GPTNeoX) is NOT gated, can't carry the sign-gate crystal; OLMo-2/Qwen3/Mistral are.
See knowledge/explore/vsm-opcode-monitor.md.
