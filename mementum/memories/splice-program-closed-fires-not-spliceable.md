🔄 The kernel-splice program (geometry-as-detector ⊗ kernel-as-executor, in-place
per-combinator patch) CLOSES on a two-sided negative — the intersection is empty:
`fires` ∩ `robustly-spliceable` = ∅. Redirect to the constructed front-end (s242).

THE POWER TEST (Exp 0.5 --targets B C --heldout-per 35, Qwen3-14B): raising power did
NOT lift tp — it EXPOSED the firing-set prec-1.0 loci as SPLIT-FRAGILE FLUKES. B never
clears the precision floor (best 0.50 across all layers/τ; its heldout-25 prec-1.0@L16
tp4 was a split artifact). C prec-1.0 survives only at tp=1 (rec 0.029, L10) — locus
MOVED L14→L10, tp SHRANK 3→1 vs heldout-25. splice-ready=∅; tp never crossed 5.

THE CLOSURE: {I,K,Y} are well-detected (tp 6–11) but NEVER fire (0/559, s244 survey);
{B,S,C} fire (behavioral register) but are NOT robustly detectable (B≤0.50, C tp=1,
S<0.8). The combinators that execute are exactly the common-mode-contaminated ones
(s211 η²=0.05; B no amplitude home s238; C recall-starved ground-state s242). Obstacle 1
is fatal for the in-place per-combinator splice in the behavioral register.

NOT ruled out (the negative is scoped to in-place last-token single-combinator):
(a) multi-position program-decode along fired_sequence; (b) a model where the firing
combinators are less common-mode. ⇒ Live path = compiler-as-loss §s242: small learned
prose→LF ∘ EXACT kernel. The splice was the no-training hybrid hope; closure refocuses
on the s242 pivot (freeze routing topology + exact kernel calls + thin front-end).
