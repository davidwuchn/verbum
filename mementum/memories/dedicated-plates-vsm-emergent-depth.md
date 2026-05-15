🎯 dedicated-plates-vsm-emergent-depth

**Decision**: KIBCM dedicated ternary plates with VSM-emergent depth (Option C).

Each combinator gets its own plate at all 9 strides. CycleContinue (S3) decides
how many cycles each combinator needs per input. S4 emphasis biases dispatch.
Alarm monitors per-combinator health independently. Depth is DISCOVERED not designed.

**Why dedicated**: multiplexing-breaks-holography (session 096, score 0.60 vs 0.92).
I is fundamentally different from K/B/C (session 093, r≈0.70 vs r>0.90). Binding
is the bottleneck (session 101: 0/6 stable compositions with binding sites > 0).
Shared weights force magnitude lenses between combinator subspaces.

**Why emergent depth**: the VSM should self-regulate. CycleContinue already gates
per-cycle. With dedicated plates, it becomes a per-combinator depth controller.
K self-discovers 1 cycle is enough. I self-discovers it needs 3 cycles for binding
chains. B finds its own depth for composition. No hardcoded assumptions.

**Why this simplifies the VSM**: with shared plates, the alarm had to detect collapse
AND recover drifted weights — too hard, alarm latency was the risk (session 097).
With dedicated plates, weights are always there. Alarm's job: adjust routing only.
Per-combinator health signals become clean (no cross-contamination).

**Cost**: 24.6 MB ternary plate + 12.2 MB beam + 8.1 MB infra + 2.4 MB mirrors
= ~47 MB. Still smaller than Pythia-160M at FP16 (320 MB).

**Evidence base**: fixed-point decomposition (session 101) — clause holograms
converge independently (90%), composition unlocks 2.2× capacity, binding wall
maps exactly to I-combinator territory. Dedicated I-plate = dedicated binding
capacity = structural solution to the binding wall.

Connects to: multiplexing-breaks-holography, vsm-variety-gap,
combinator-dispatch-floors, three-clusters-kibcm, fixed-point-holograms.md
