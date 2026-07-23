✅ The lambda compiler survives 1.58-bit ternarization at full strength.
Ternary Bonsai 27B (PrismML end-to-end ternary build of Qwen3.6-27B,
{-1,0,+1} + group-wise FP16 scales, ~1.71 bpw, HF rev abbae7230) vs
QWEN36 base reference, same harness, same compile-gradient n=40, same
day (runs *-20260722-214611): binder P(λ) 0.650 vs 0.625, lenient
0.625 vs 0.625 — parity. kernel_valid 0.525 vs 0.750, but autopsy
shows all 17 binder-but-not-kernel outputs are well-formed rich FOL
(nested quantifiers, ¬, uniqueness, Church-style λx.λy) — notation
drift, not core damage (grading.py: "notation ≠ failure"). Cost
surfaces as path length: +40% reasoning chars (11137 vs 7938), ~2.7×
wall time. Loss profile exactly as holographic-llm.md predicts: sign
and zero carry the program (routing topology), magnitudes carry
calibration/gloss. Michael pre-registered the outcome before data
landed (this session), reasoning from benchmark retention: core
damage compounds multiplicatively through reasoning chains — 90%
retention entails intact core, the alternative was PPL-296K noise
(s174). Caveat: baseline is the 35B-A3B MoE fleet reference, not the
exact dense-27B parent. Next: crystal-spine 9×9 Gram on ternary
weights (F16-container GGUF); per-vertex lesion map.
