💡 B (composition) IS the model's NATIVE softmax-over-V order — the FIRST CRISP POSITIVE
for B in the whole opcode saga, and the resolution of "the B gap". s236 v5 lead 2d prong 2
(kernel_reference_order_cost_v8.py, Qwen3-14B). Michael (s235): "if B is an ordering of
operations then maybe it defaults to the order the softmax over all V uses natively?"
Grounded in ffn-reduction-trace: attention executes the FFN-compiled program via softmax
over V = β-reduction by weighted combination ⇒ softmax-over-V IS the execution order.

THE TEST (no amplitude classifier — pure surprisal): take a composite CL program, get its
CERTIFIED reduction trace (step_fired → contractum + opcode/step), teacher-force
"t0 -> t1 -> ... -> tn", read per-step SURPRISAL (mean −log p under LM softmax over V).
Minimal pairs ("B f a b → f (a b)" order-KEPT vs "C f a b → f b a" SWAPPED, paired by
atom-set) + multi-step composites; ATOM-ONLY de-confound (drop parens/length, keep
order-bearing leaves) = the headline. BCKW = structural rules of logic: B=COMPOSITION
(preserves order), C=PERMUTATION (swaps), K=DELETION (drops), W=contraction (copies).

✅✅ DECISIVE at 14B (n_each=24, 216 programs): b_is_native_order=True — clean atom B-vs-C
single-step minimal pair d=−1.26, t=−7.02; B atom-surprisal 0.81 ≪ C 2.14 / S 2.66 / W
2.71; B cheaper than EVERY permute/copy combinator (B<S t=−11.3, B<C-multi −11.7, B<W
−14.5); pooled order-preserving < breaking (atoms Δ=−1.06, full Δ=−0.52). D≈K once
deletion-length de-confounded (atom D−K t=−1.22 n.s.); K=deletion stays cheapest (short
predictable contractum — taxonomy wrinkle, not order).
⚠️ POWER-LIMITED at 8B smoke (n=8): same DIRECTION but headline B<C atom minpair n.s.
(t=−0.55); multi-step/aggregate already sig (B<C-multi −4.22, B<S −5.31, B<W −11.1). Crisp
only at full power — the entire B-saga pattern (real-but-faint, n-limited) resolving once
n rises.

★ RESOLVES THE B GAP: B's amplitude-absence everywhere (s234: FFN gate flat, attn flat,
per-head faintest, gradient faint) is NOT diffuseness — composition is the FREE
autoregressive default, carries no marked amplitude feature; the instrument looked for a
marked signal where B is the UNMARKED baseline the others deviate from.
★ UNIFIES with prong 1c-ii (b-climbs-with-derivative-order): composition has TWO faces —
token-side the native order (cheap surprisal HERE, t=−7.02), gradient-side the product/
2nd-order (curvature climb t=1.90). B = the chain rule (gradient) AND the native order
(forward). Both confirmed.

★ NEXT: (1) cross-model — 8B at full n + 32B (universal or 14B-specific? cf C-locus shifts
with scale); (2) PROSE-rendered order-cost (kills the bare-symbol caveat — feed prose not
symbols, the lead-2 lesson); (3) off-diagonal Jacobian (the s235 curvature path).
Caveats (λ measure): BARE SYMBOLIC input (bare-symbol surprisal may reflect a generic
copy/induction preference for source-order atoms — which IS the proposed mechanism); 14B
decisive / 8B directional / 0.6B too small (1 model class, 2 scale points); single-
combinator + within-program contrasts. Code: kernel_reference_order_cost_v8.py.
