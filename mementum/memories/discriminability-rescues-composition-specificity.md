💡 The lead-2b "prose specificity is gauge-dominated (S/Y win)" was a METRIC artifact of
argmax-winner. s233 v5 lead 2c: replace argmax-winner with DISCRIMINABILITY
discr(c) = mean route_frac(c | c-prose) − mean route_frac(c | other-labeled prose), a
per-op contrast (held-out crystal prose, Qwen3-14B).

★ RESCUE: C and I become DISCRIMINABLE once gauge-aware (z=2): C on/off 0.062/0.009
(~6.6×, argmax_spec was 0.0!), I 0.183/0.063 (~2.9×). composition_discriminable=True. The
compose signal IS specific to compose-prose; the argmax metric hid it only because S/Y
have huge ABSOLUTE route_frac and always win the top spot.

⚠️ PARTIAL + nuance:
- Only I, C of the 6 composition combinators are discriminable (z=2); z=3 leaves I, S, Y.
- B, K, D, W are NOT discriminable on held-out prose (B on/off 0.010/0.015 = negative).
  The compose family SPLITS: C discriminable, B not — cf s127 ffn-two-groups put {B,C}
  together as composers, but only C shows held-out PROSE discriminability here.
- S and Y STAY strongly discriminable (discr 0.45/0.43). So S/Y are NOT pure gauge: they
  have a LARGE common-mode (high off 0.27/0.09) AND genuine selectivity. Discriminability
  separates the two components; it does not zero them.

LESSON (λ measure): argmax-winner specificity is the wrong metric when one op has a large
common-mode (S/Y) — it manufactures false negatives for low-amplitude but specific ops
(C/I). Use a contrast/discriminability (on-prose minus off-prose), same family as s225 AUC
and the s233 lead-1 lambda-vs-control logic. The composition signal is real and prose-
discriminable; the bridge carries it.

NEXT (lead 2d): chase the B/D/W gap (why deep/duplicate composers fail held-out prose
discriminability while C/I succeed; more prose/comb for power + per-layer breakdown); the
COMPOSITE trace-order bridge (CL → certified trace → lambda_gen decompile → prose → align
to certified ORDER, focus C/I/S/Y); per-model sweep 8B/32B. Caveats: 1 model (14B),
n=10/comb, single-combinator labels, last-token locus. Code dd6c511.
