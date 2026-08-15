💡 KV continuations are MODEL-PRIVATE; the canonical textual state is the bus.
s334 capture 2 (Michael: "can we install the repl onto qwen3-32b? … a way for
one model to interact with another model step-wise"). Install: yes — 32B
already runs in the harness (s332); driver v0 = KV seal/fork (~256KB/token on
GQA 32B), greedy+fork-identity plant, with the APPEND/REWRITE law: KV resume
is only valid on append — canonical hard-writes re-prefill, so fork points
live at the pre-emission seal. Cross-model: no shared-KV handoff exists
(different weights/shapes/geometry) — model-to-model stepwise interaction
works EXACTLY because the driver re-serializes to canonical form each bounce:
shared tape ≡ canonical text (the hard write ≡ the bus), private state ≡ each
model's sealed KV lineage. Two-model config: B=S1 (bounced reducer), canonical
serialization=S2, A=S3 (policy: order/forks/repair proposals/probe selection),
lambda_ast kernel=S3* STAYS MECHANICAL (model-as-auditor destroys the
instrument), ledger=S4, pre-reg=S5. A-driving-B ≡ tool-calling recursed (§10b:
B is A's tool, A is B's effect handler). Buys: adaptive probing (fuzzer row) ·
cross-face driving (instruct operates base = §P-TOOL-ABI other side) ·
composition tutoring (compose vs decompose split). Frozen experiments keep the
mechanical driver; A-in-loop = exploration or own pre-registered arm, policy
pinned. Page: explore/repl-driver-trampoline.md §8.
