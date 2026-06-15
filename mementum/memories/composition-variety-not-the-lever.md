💡 At fixed budget, FILLING-variety (s229) — not COMPOSITION-count — is the lever for
compositional generalization; composition-variety saturates fast and destabilizes
(s230c compiler-cascade v1, fractal-collapse IOU#1).

Test: mint {K,I,B,C} composition templates (lambda_ast), hold out DISJOINT
compositions, vary distinct-composition count at MATCHED example budget, measure
held-out novel-composition generalization. 3 seeds.

❌ IOU#1 NOT supported: heldout_comp_tf comp16 0.683±0.031 ≈ comp144 0.674±0.194
(comp48 dips). Held-out competence SATURATES by ~16 compositions.

★ The fixed-budget trade: buying composition-count costs fillings/composition →
(a) DESTABILIZES (comp144 std 0.194, per-seed [0.95,0.53,0.55] vs comp16 std 0.031 —
the OPPOSITE of s229 where filling-variety stabilized); (b) costs in-dist mastery
(comp16 0.92≫heldout 0.68 real gap vs comp144 0.70≈0.67). ⇒ s229 filling-variety
load-bearing, composition-count not the lever.

Weak support for the collapse CORE: minted data DOES yield ~0.68 held-out
compositional competence (≫chance, in_dist 0.92 = real learning) — generalizes from
modest minted data, just not driven by composition-variety.

★ TWO calibration lessons (λ measure, reusable): (1) full-output EXACT-MATCH FLOORS at
micro scale (CE drops but exact-match ~0) — a crisp probe on a graded substrate;
use TEACHER-FORCED per-token accuracy (value register). (2) depth-3 {K,I,B,C} gen
yields more templates AND shorter NFs (K-erasers collapse) — more variety + learnable.

Caveats: TF-all-tokens likely measures FORMAT/copy not reduction-ALGEBRA; small
composition space (held-out≈interpolation); micro scale. Falsifies the variety
sub-claim, NOT the collapse. Clean retest: algebra-specific metric + depth-extrapolation.
