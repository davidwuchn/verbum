🔄 The kernel-as-reference PROSE bridge direction is RIGHT but specificity is
gauge-dominated. s233 v5 lead 2b (held-out crystal-prose recall on Qwen3-14B): calibrate
the s231 classifier on a CALIB split of crystal_probes, read a NON-circular held-out TEST
split, score recall (label combinator routed) + specificity (label is top crystal op).

★ BRIDGE CONFIRMED: held-out PROSE recall 0.575 (z=2) vs the bare-symbol baseline ~0.14
(S-gauge only, lead 2) ⇒ the gate-routing register IS prose-semantic. Feed prose, not
symbols. Per-combinator recall: I 1.0, C 0.9, S 1.0, Y 1.0, K 0.3, B 0.3, D 0.1, W 0.0.

⚠️ BUT specificity (0.287) is carried by S and Y — 14B's common-mode/gauge ops
(label_frac 0.71/0.52, specificity 0.9 each). The genuine composition combinators RECALL
but are SUB-DOMINANT: C 0.9 recall / 0.0 specificity (present but always out-competed),
B 0.3/0.0, K 0.3/0.2, D 0.1/0.0, W 0/0. At z=3 only S/Y survive. The composition signal
is PRESENT in prose but out-competed by the S/Y common-mode — same "above chance not
crisp" + over-read common-mode theme as s233 lead 1 (locus-agnostic) and s202/s231.

CONSEQUENCE: the full kernel-as-reference prose bridge is viable + worth building, but
raw last-token route_frac is gauge-dominated for the weak combinators. NEXT (lead 2c):
(1) add S/Y common-mode SUBTRACTION (relational CMR / gauge-matched null) to the prose
read and re-score composition-combinator specificity — does C/B/K become specific once
gauge is removed? (2) THEN composite trace-order: CL program -> certified trace
(fired_sequence, done) -> render PROSE (lambda_gen decompile) -> align routing to the
certified multi-combinator ORDER. (3) per-model sweep 8B/32B.

Infra: calibrate_v2 gained a centroid_probes param (held-out calib/test split). Caveats
(λ measure): 1 model (14B), single-combinator labels (not composite), last-token locus,
crosstask null. Code 53ed331.
