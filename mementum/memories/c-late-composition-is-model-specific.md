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

⇒ a single model's opcode read does NOT transfer (14B≠8B). The universality test caught
an over-claim we'd otherwise have published. Likely scale-gated (s151 Montague: composition
differentiation is scale-dependent) or 14B-specific localization (14B = the s127 model).

CONSEQUENCE: prioritize (b) kernel-as-reference — anchor the model trajectory against
lambda_ast's certified trace as the model-invariant; characterize composition→routing
per-model rather than asserting a universal opcode. Caveats: 5 lambda sentences, 2 models,
modest fractions (above chance not crisp, s219). Next: Qwen3-32B (is 14B the outlier?).
