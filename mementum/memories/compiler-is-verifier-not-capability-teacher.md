🔄 Compiler-as-loss CORRECTION (Michael, s225). The s224 compiler-as-loss page
over-rotated: it put the lambda compiler in the L_capability slot
(`CE(student, compiler reduction)`). That is the wrong slot.

WHY: the diverse big models are the BETTER capability teacher. s219's universality
(combinator geometry agrees +0.78 across the ecosystem) came FROM diverse, grounded,
natural next-token training — diversity is the CAUSE of the robust composable
function, not incidental. A deterministic β-reducer on isolated combinator terms is
the thinnest slice of usage → risks a brittle function "too narrow to compose"
(Michael's phrase). Compounds with s224 (capability=usage), s222 (superposition
needs diverse pressure), s223 (narrow data is Goodhart-friendly).

THE FIX — separate two jobs the page conflated: the compiler is a poor GENERATOR
(narrow by construction) but a perfect VERIFIER (Church-Rosser → unique normal form,
exactly checkable). A judge needn't be more creative than the contestants, only
correct. So: compiler = VERIFIER/canonicalizer + exact-trace generator (the trees
the LLMs can't expose, s221 "fakes it with depth") + MIT-clean anchor. NOT the
capability teacher.

"Pin the WHAT, free the HOW" applies to the DATA: train on DIVERSE realizations,
use the compiler to CERTIFY each reduces to the correct normal form. Diversity →
composition; compiler → correctness; labels' correctness certified by MIT code even
if inputs came from AGPL models.

Experiment reframe: diverse-verified vs compiler-only vs combo; metric = held-out
COMPOSITIONAL GENERALIZATION (not just route_z+CE) = the test for "too narrow to
compose". See `knowledge/explore/compiler-as-loss.md`.
