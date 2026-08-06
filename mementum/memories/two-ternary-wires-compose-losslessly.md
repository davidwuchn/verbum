💡 Two independently-baked ternary wires compose LOSSLESSLY on one frozen base
(§P-PLATE-LINKER-1, s312, `scripts/explore/plate_linker.py`, results `0576a3f`).

Additive merge `base + Δ1 + Δ2` (LoRA r=16 ternary factors, FFN L22–L29): BOTH
wires pass their own frozen G1 under merge — wire-1 B1 +0.812 (p=3e-4) / B2
+0.455 (p=1e-3); wire-2 B1 +1.0 (p=1.5e-3) / B2 +0.391 (p=2.3e-3). Retention
~1.0 both wires on every split (`merge == solo`). Zero measurable interference.
`c_nat 0.0072` (disjoint countries → near-orthogonal keys); `mag_cos 0.839`;
restore bit-exact. The git-for-weights primitive (device A co-existence) WORKS.

Frozen verdict was `NO-COMPOSE` — a G3-saturation MISLABEL (3rd don't-over-read
instance after s310 SIGN-CHURN, s311 LOOKUP-ONLY). PL1 fails only on G3
(specificity gap saturates because composition is lossless). The keystone (PL2
ANGLE-PREDICTS) is UNTESTABLE here: `nat_deg = 0.0`, and even forced full
collision `c=1.0` (θ-sweep, matched norm, fixed B2) causes NO degradation
(`rot_maxc == solo`). r=16 in ~2560-dim FFN = ample capacity → collision costs
nothing. L6 "compose by angle separation" is sufficient but not shown necessary.

Next lever: force an interference regime (stack N wires / higher rank / narrower
band) → then test angle-predicts-onset = §P-PLATE-LINKER-2 (queued, not frozen).
