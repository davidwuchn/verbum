💡 B (composition) CLIMBS MONOTONICALLY with DERIVATIVE ORDER — its strongest signal yet
is in the SECOND-ORDER (curvature) register, exactly where chain-rule predicts. s235 v5
lead 2d prong 1c-ii (kernel_reference_jacobian_v7.py, Qwen3-14B). Michael: "proceed with 1"
(the Jacobian/second-order probe). Rationale: B=Bfgx=f(gx)=chain rule = PRODUCT of
derivatives = a SECOND-order quantity (d²L/dz² carries g'ᵀ[f''·]g', a quadratic form in g').
The first-order gradient (prong 1c) is a single factor / sum-over-paths — it WASHES OUT the
product. Clean register-swap of v6: same RelationalCrystalClassifier, feature = DIAGONAL
HESSIAN of probe LM-CE w.r.t. gate_proj (Hutchinson diag(H)_a=E_v[v_a(Hv)_a], v~Rademacher,
double-backward of g·v with create_graph=True), pooled over supervised positions, n_hutch=4.

❌ STRICT: B still does NOT reach significance (discr_z +0.118, t=1.90 < 2.0) — chain-rule
not confirmed at the bar; B's gap survives into the second order.
✅ DIRECTIONAL: the MONOTONIC CLIMB — B activation t=−0.05 → first-order gradient t=+1.07 →
second-order curvature t=+1.90 (on +0.045 > off −0.073). Strongest B ever, in the PREDICTED
register, sitting ON the 2.0 threshold — power-limited (n=20/comb), not absent.
✅✅ INTERNAL CONSISTENCY (the structural win): the curvature register reweights combinators
EXACTLY as the math demands. I (identity = LINEAR, Ix=x → zero curvature) COLLAPSES: t=3.83
(act) → 1.02 (grad) → 0.68 (curv) = monotone DOWN, the mirror image of B's climb. Y
(recursion = self-application = higher-order) DOMINATES t=4.53. Composers {B,C} hold/rise
(C 2.52 ✓), selectors {K,I} fade. The two opposite monotones (B↑, I↓) are the signature:
derivative ORDER is a real axis combinators sort along, and B sorts UP it while the linear
combinator sorts DOWN. Instrument works (C ✓, Y ✓).

★ NEXT (B is ON the bar in the right register): (1) POWER — raise n / n_hutch, does t=1.90
cross 2.0? cheapest decisive; (2) OFF-DIAGONAL Jacobian — diag-Hessian only captures
g'ᵀ(diag)g'; the literal f∘g coupling lives in the OFF-DIAGONAL / interlayer Jacobian
(Gauss-Newton/JVP) = next fidelity; (3) prong 2 trace-order. Caveats (λ measure): 1 model
(14B), n=20/comb (ON the bar), n_hutch=4 diag-only, single-combinator labels,
pooled-supervised locus. Code: kernel_reference_jacobian_v7.py.
