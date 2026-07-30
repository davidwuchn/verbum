💡 The installed operand's quant fragility lives in the VALUE register — because that is
where the operand lives. f2 (s280, Qwen3-4B, RTN-Q4, commit 8fed4a0): quantizing the
ROUTING register (`gate_proj`, all layers) produces ZERO installed-operand flips despite
genuinely re-routing (4% activation gate-sign flips, 26% of gate weights zero-snapped);
quantizing the VALUE register (`up/down`, slot col bf16) flips 0.118 away from truth;
all-Q4 flips 0.176 while the native LEARNED covering flips 0.0 in every condition.
Register-coherent with s276 (rows = value objects, joins = routing): a single installed
row is non-redundant → Q4-fragile; the crystal/join machinery absorbs its own re-route
even for the installed target. Slot key robust (z ≥ 4.9/6.0 everywhere) → damage =
payload dose, not key misfire. = the installed-vs-learned discriminator measured
register-attributed, and the s273 superbake-write-access prediction (baked facts
quant-fragile, crystal quant-robust) confirmed on our own bake. Corollary lesson
(λ measure): f0's "value-Q4 flips exactly 0 gate signs" was by-construction unmeasured —
the activation cascade is real (0.053); only the weight-level statement holds by
definition. f3 target: mirror-stack the VALUE payload, not routing protection.
