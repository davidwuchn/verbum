✅ §P-TYPE-WRITE-V2 (s323, qwen3-4b) closed the §14 coverage gap and landed the
modal a-priori arm: VERDICT MEMORIZED-ONLY. Under FAIR coverage (bare-NP licensed
frames gradient-touched on TRAIN_PREDS, held predicates eval-only, true 1-labels
derangement) the weight write binds the trained predicate associations enormously
(train licensing base 0.356 → wire 8.833 nats, contrast vs deranged +17.47 p=1e-4;
recall p=5e-4) but the membership ABSTRACTION does not install own-class-specifically
on held predicates.

The crux is one discriminating negative inside three positives: held transfer is
real and content-dependent (V1 +1.337 beats shuffled-label p=5e-4; V3 beats the
deranged wire which anti-licenses held frames at −0.955, p=1e-4) — NOT zero
generalization — but it is NOT own-class-specific (V2 own-vs-anti fails paired-perm
p=0.16). held_ok=V1∧V2∧V3=False ∧ train_lift=True → MEMORIZED-ONLY.

Consequence: fixing the coverage gap did NOT overturn tape-residency. §9/§13 are
honestly re-qualified (predicate memories weight-bindable; abstraction not).
s317's DELIVER leg (demoted one-sided s322) is RESOLVED two-sided — tape-residency
of type JUDGMENTS supported under fair coverage. Causality S5 cell stays
weight-negative for the abstraction (TYPE-WRITTEN did not fire). Two-tier holds:
weights = predicate memories + relation/checker; tape = the class judgments.

Caveat: V1 DID pass — MEMORIZED-ONLY sits at the TYPE-WRITTEN boundary, separated
only by V2 class-specificity; single model, band-LoRA r=16. Claim licensed is
"abstraction does not install own-class-specifically on held preds," not "no
generalization of any kind."
