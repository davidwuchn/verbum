💡 The certified corpus only ever FIRES {B, S, C}; the s243 firmed splice set
{I, K, Y} fires in 0 items — disjoint. K fires in 0/559. This fully explains Exp 1
(K causal in ROUTING, behaviorally null): K never executes a reduction in this corpus,
so there was nothing behavioral to preserve.

WHY `fired_sequence(parse(kernel_term))`==[] for all 559: the stored `kernel_term` is
the POINT-FREE / already-NORMAL form. Bracket abstraction (Turner 1979) is the inverse
of reduction — it emits UNDER-APPLIED (inert) combinators that fire nothing until
applied to arguments. To see firing you must SATURATE: a quantifier `forall P` applies
the one-place predicate P to a witness. `corpus_firing_survey.py` does this → fires
B (68×, 55 items), S (55×, 54), C (15×, 15), all in `quantified`; never K/W/D/Y/M/I.

TIES TO THE Qwen3-4B `λx.` ARTIFACT (the distilled probes): a vacuous binder compiles
to K (the const), but the real compiler emits S/B/C for "Every X verbs a Y", never K.
So Qwen's inserted `λx.` was manufacturing spurious K-structure the kernel never
produces — the splice mismatch and the bad-probe artifact are the SAME bug, two sides.

⇒ Exp 2 retargeted {I,K,Y}→{B,S,C}. Exp 0.5 z-sweep (Qwen3-14B, --targets B S C):
splice-ready=∅. C FIRM L14 τ2.0 prec 1.0 fp0 rec 0.12 tp3 (plateau w5, reproduces s243);
B FIRM L16 τ5.0 prec 1.0 fp0 rec 0.16 tp4; S never clears prec 0.8. Precision-attainable
but RECALL-STARVED — none clears tp≥5 (mirror of {I,K,Y}: well-powered but never fire).
The firing combinators are exactly the hardest to detect (B no amplitude home s238, C
recall-starved ground-state s242, S most common-mode). A behavioral splice is feasible in
principle (B/C prec-1.0 fp-0 loci) but acts on only 12–16% of firings. Decisive next test:
raise power (heldout-per 25→35 for B/C) — does tp cross 5 at the prec-1.0 plateau?
