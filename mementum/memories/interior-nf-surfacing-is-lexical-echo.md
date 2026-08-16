❌ "Subterm normal forms surface at their closing cells in the prefill interior"
did NOT survive the clean-dissociation check. s335, Qwen3-14B, 810 cells,
logit-lens rank of a subterm's NF first token at that subterm's closing cell vs
a shuffled-position null. As frozen it PASSED: median rank gain 13.0, p=1e-4 →
qualifier INTERIOR-VISIBLE. Split by whether reduction actually changes the
string (the s321/s323 discipline):

    DIRTY (NF already written in the span's own surface): gain +17.0, 68.9% positive
    CLEAN (reduction genuinely changes the string):       gain  +0.0, 46.1% positive

The whole effect is lexical echo — the lens reads the token that is THERE, not
a computed normal form. INTERIOR-VISIBLE is not licensed; interior NF surfacing
remains unmeasured.

This replicates "routing tracks what is WRITTEN and what FIRES, not the
function computed" (s321 CL-COLLAPSE, s323 CL-COLLAPSE-2) at the VALUE register
on the prefill grid — a third register, same law. Standing rule reinforced: any
lens/rank claim about a computed value owes a clean/dirty split where the
target symbol is ABSENT from the surface; a gate can pass and still be an
artifact. Page: explore/latent-reasoning-and-the-prefill-triangle.md §Result.
