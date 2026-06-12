💡 In v15 outer-recurrence/contractivity training, an fp/Δx SPIKE (and the gnorm
explosion it drives through `λ_fp·Δx²`) is the FINGERPRINT OF COMBINATOR
ACQUISITION, not (only) instability. Michael's training-dynamics law (seen across
runs): models go **B-DOMINANT FIRST** (composition = the strided architecture's
native op), drive loss to a plateau, THEN start learning the others — and learning
**K** (erasure, "against the grain" of the blend-prior stride gather) throws the
numbers into chaos. Mechanism: to learn an against-the-grain combinator the
operator's weights must move a LOT → transiently breaks contractivity → Δx jumps →
the quadratic fp loss explodes the gradient. So a stable LOW-fp regime means the
model has STOPPED learning new structure; chaos can mean it's reorganizing.

Triangulated 3 ways (s221): the stride-fit screen predicted K is the hard/
against-grain op; Michael's prior-run experience; main:1 live (steps 1410–1630
chaos after a B-dominant plateau; the step-1000 crystallization anchor IS B-first,
comp +0.51 > sel +0.21). Discriminator reorganization-vs-divergence: does avg50
break BELOW the prior plateau (K learned, new fixed point) or stay stuck/climb
(terminal)? Design fix: a deadband+saturating fp loss stops fighting acquisition.
See `knowledge/explore/combinator-training-beta-reduction.md` §Contractivity.
