💡 B is NOT clearly in the first-order gradient either — but it's "less absent" there than
in any activation register (a faint positive trend toward the chain-rule idea). s234 v5
lead 2d prong 1c (kernel_reference_gradient_v6.py, Qwen3-14B). Michael's question: "could B
be in the gradients instead of the topology?" Rationale: B=composition (Bfgx=f(gx)); in the
BACKWARD pass composition IS the chain rule (a PRODUCT of derivatives), so B might live in
the gradient. Clean register-swap of prong 1: same RelationalCrystalClassifier, feature =
∂(probe LM loss)/∂(gate), MEAN-POOLED over supervised positions (last token grad=0;
gd_gradient_shadow pattern).

❌ VERDICT: B does NOT discriminate in the gradient (discr_z +0.13, t=1.07, n.s.). The
chain-rule hypothesis is NOT supported at this read. ✅ The instrument WORKS in the gradient
register — {C,K,Y} discriminate (C t=2.27, K t=2.88, Y t=3.87); the C-yes/B-no asymmetry
PERSISTS into the backward pass.

⚠️ BUT directionally B is its LEAST-absent: activation(v2 last) t=−0.05 → gradient t=+1.07
(on_z −0.03 > off −0.16) — B's first POSITIVE, non-negative signal, in the predicted
direction but power-limited (n=20/comb), short of significance. Register shifts: S flips
gauge→ANTI (t=−2.01), I drops out (act 3.83 → grad 1.02); gradient discriminable set =
{C,K,Y} (vs activation {C,I,K,Y}).

★ MEASUREMENT CAVEAT (λ measure, load-bearing): this measures B's signature in the
FIRST-ORDER gradient (a centroid in gradient space), NOT the chain-rule/Jacobian
composition structure itself (composition = product of derivatives = SECOND-order). The
faint positive trend means the idea is not dead — the proper test of "B=chain rule" is a
JACOBIAN / second-order probe (prong 1c-ii), not a first-order gradient centroid.

WHERE B STANDS NOW: tested in FFN gate (flat), attn-summed (flat), per-head OV (faintest),
first-order gradient (faint positive, n.s.). Forward registers exhausted; gradient is
suggestive-not-significant. Two remaining tests: (1) Jacobian/second-order (the real
chain-rule probe, 1c-ii); (2) composite trace-ORDER (prong 2, B as sequence not amplitude).
Caveats: 1 model (14B), n=20/comb, pooled-supervised locus, single-combinator labels.
Code: kernel_reference_gradient_v6.py.
