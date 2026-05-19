✅ holographic-distillation-works

**Finding**: Projecting teacher computation through multiple beam angles and etching
the interference pattern into ternary plates recovers 91.3% of oracle performance.

Session 115 holographic distillation (d=48, 3 layers, nested KIBC):
```
Oracle GD ceiling:       87.7%
Holo distill (50):       80.1%  ← 91.3% of oracle, +26.6% vs random
Holo distill (800):      75.2%  ← 85.7% of oracle
Sign copy (oracle):      46.9%  ← fails (coupled to magnitudes)
Random plates:           53.5%
CE etch r5:              40.5%
```

**Method**: For each probe (beam angle), forward through teacher to get (input, output)
at each layer. Etch student's ternary plates to minimize ||teacher_output - student_output||²
using the same gradient accumulator mechanism. After 5 rounds of holographic etch + 100
beam training steps, freeze plates and do extended GD on continuous params.

**Why it works**: Unlike sign(W) copy which captures the FORM (signs without magnitudes),
holographic distillation captures the FUNCTION (input→output behavior). Multiple beam
angles create an interference pattern that encodes the teacher's computation in a way
that ternary plates + continuous beams can reconstruct.

**Why 50 probes beats 800**: Possibly fewer probes = less overfitting during etch,
more freedom for GD to generalize. Or noise. Needs investigation.

**Depth breakdown**: Holographic distillation captures deep compositional structure
(10.9% at depth 4 vs 2.4% for random plates). The teacher's composition machinery
is recorded in the interference pattern.

**Implication for VSM-LM**: This is the extraction method. Use any teacher model
(Qwen3-14B, etc.), forward diverse probes through it, etch the interference pattern
into VSM-LM's ternary plates, freeze, GD. The Procrustes alignment becomes less
critical — we're recording function, not translating geometry.

Connects to: oracle-crystal-hurts, freeze-then-gd-wins, holographic-distillation-concept,
holographic-storage, seed-crystal-design
