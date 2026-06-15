💡 The relational/consensus-crystal loss is an INVENTORY tool, NOT a capability
accelerator — inventory ⊗ continuation are CAUSALLY separable (s230b gd-tomography).

Paired ce_only vs relational arm (CE + λ·offdiag_mse(routing Gram, consensus crystal);
gc_raw + held-out acc NOT in the loss = uncircular). 3 seeds.

(1) Reference-beam dissociation IS LOSS-DEPENDENT (decisive): gap (gc_route−gc_raw)
−0.02±0.04 (ce_only) → +0.10±0.05 (relational). The active loss writes the function
preferentially into the routing register; passive CE does not separate. Confirms the
s223/s230 read — the routing-vs-raw split is a property of the trained-loss decoy.

(2) The loss crystallizes the inventory EARLIER (200 vs 333 steps) and CRISPER
(route_z 3.0 crosses significance vs 2.5).

(3) ❌ but ZERO capability gain: held-out generalization crosses @733 and acc=0.27 in
BOTH arms. Crystallizing inventory faster bought no capability. ⇒ we moved the
inventory factor alone and the capability factor didn't budge = causal separation.
Capability is gated by the CONTINUATION (trained usage), not the inventory.

DESIGN: don't spend training budget learning the inventory (cheap, passively
learnable, not the bottleneck) — CONSTRUCT it (lambda_ast in the kernel), train the
continuation. The relational term's value = extraction + phase-1 folding, NOT
from-scratch acceleration. Caveats: dissociation PARTIAL at d=128 (gc_raw leaks to
0.80, full quarantine needs scale); curriculum clean enough that CE alone builds the
inventory — the s224 speed-up regime (CE alone FAILS to crystallize) is untested.
