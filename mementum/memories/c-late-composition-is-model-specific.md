💡 The composition-specific C-late opcode signal (s232 v3/v4: lambda routes C in the
readable-zone gate-routing register, matched non-compositional controls do not) is
MODEL-SPECIFIC to Qwen3-14B — it does NOT generalize to Qwen3-8B.

v4 added the proper specificity test: framing-matched GATED guards (gate_retrieval,
gate_arithmetic) under the gate-matched null, plus detect_c_late (readable-zone depth>=0.6
C-dominant fraction).

- Qwen3-14B: composition_specific=True both z. lambda C-late 0.556/0.333 vs gate_neutral
  0.111/0, gate_retrieval 0/0, gate_arithmetic 0/0. Among gated prompts ONLY composition
  routes C-late. Clean.
- Qwen3-8B: composition_specific=False. gate_neutral C-late 0.714 EXCEEDS lambda 0.333 at
  z=2; all silent at z=3. The non-compositional control out-routes lambda.

- Qwen3-32B (64L): composition_specific=False, but C-late=0 for ALL conditions in the
  depth>=0.6 zone — because the lambda C signal SHIFTED EARLY (C-dominant L5,10,11, depth
  ~0.1; gate_neutral C only at L0). 32B DOES show lambda-specific C-early; the fixed
  detector misses it.

⇒ 3 models: composition->C routing exists in all, but the C-LOCUS SHIFTS with scale (8B
non-specific, 14B C-late L27-32, 32B C-early L5-11). composition_specific=True ONLY for 14B
because its locus matches the fixed depth>=0.6 zone. NOT scale-monotone, NOT universal —
14B is the outlier for the C-LATE framing. A single model's opcode read does not transfer.

CONSEQUENCE: (1) the fixed-depth C-late detector is the WRONG cross-model instrument —
needs per-model C-locus calibration or a locus-agnostic full-profile lambda-vs-control
compare. (2) Prioritize (b) kernel-as-reference — anchor the model trajectory against
lambda_ast's certified trace as the model-invariant; characterize composition->routing
per-model. Caveats: 5 lambda sentences, 3 models, modest fractions (above chance not crisp,
s219).
