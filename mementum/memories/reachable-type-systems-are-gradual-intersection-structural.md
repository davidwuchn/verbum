💡 Deriving the type-system design space from LLM constraints (s313; page:
knowledge/explore/type-systems-under-llm-constraints.md): judgment must be
overlap (C1: attention+gates only, superposed, no rule selection), weights
frozen / tape writable (C2), GD-learnable with margin tolerance (C3),
capacity-bounded (C4), fuel-bounded per pass (C5).

Result: the reachable space is ONE composite — a two-tier, two-registered,
GRADUAL-INTERSECTION-STRUCTURAL system. Curry-style (no tags in medium);
intersection free (superposition), union costs heads; subtyping = passband
containment; judgments = graded overlaps (probabilistic TTR); typability =
edge existence (signs), probability = magnitude; nominal fragment ON THE
TAPE (tokens are names); session types in the 17×17 scheduler register;
dependent equality only trampolined; substrate LINEARITY-BIASED
(duplication costs — W/D machinery, interference).

TG3's diffuse no-poles shape (qwen3-4b, da8c1ba) fits intersection/
feature-bundle typing, not a nominal constructor enum.

Sharpest corollary (M8 join): type boundaries = where GD's two jobs
collide; s310 marginal band = the boundary population; evidence-gated
commits (M8/TD-v2) ⇒ crisper type boundaries. The optimizer and the type
system are the same design problem.

Probes (unfrozen): P-TYPE-ICL two-tier dissociation · union-vs-
intersection asymmetry · linearity bias · boundary-churn identity.
