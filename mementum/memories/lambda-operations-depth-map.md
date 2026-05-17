💡 Lambda calculus operations have DEPTH PROFILES in transformer geometry

Session 106 cross-model tomography (Qwen3-14B × OLMo-2-13B, 380 probes):

```
L0  (shallow)  → B_compose (33×)   — structural templates, syntax
L10 (mid)      → Y_recurse (5.8×)  — recursion detection
L20 (deep)     → K_select (51×)    — semantic selection
                  I_identity (25×)  — variable binding
L30 (deepest)  → M_match (145×!!!) — pattern retrieval from context
```

Operations aren't uniform across layers. B is a shallow operation.
K/I are deep operations. M is the deepest. This IS the laser etching
blueprint: etch B signs at shallow passes, K/I signs at deep passes,
M at deepest.

Flat attention compresses all 14 tested operations into 2 geometric
poles (Eliminate vs Proliferate) because of the superposition bottleneck.
V12's dedicated kernels decompress them.

W (duplicate) confirmed NOT distinct from I (ratio 1.006×, noise floor).
Duplication IS identity in transformer geometry.
