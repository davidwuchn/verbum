💡 GROSS composition-is-native-order is now UNIVERSAL across 4 MODEL CLASSES spanning 2
ARCHITECTURES — and Pythia (non-gated GPT-NeoX) proves the order-cost read is GATE-
INDEPENDENT. s240 v5 lead 2d path 1 (the Pythia-proper 4th-class point;
kernel_reference_order_cost_v9_prose.py + v10_frame.py on EleutherAI/pythia-2.8b-deduped,
rev 7d977fed, flat n=24).

WHY PYTHIA MATTERS: it is NON-gated (GPT-NeoX FFN, not SwiGLU) so it CANNOT carry the
FFN-gate crystal the routing reads use. But the order-cost read is PURE softmax-over-V
surprisal (teacher-force the certified trace, per-step −log p, atom-only de-confound) — NO
gate crystal. Pythia confirming it = direct proof the order-cost signal is gate-independent
and architecture-general, not a Qwen/SwiGLU artifact.

★ THE 4th-CLASS VERDICT (applied_to flat, n=24):
  ✅ GROSS holds — composite B-vs-C-multi atom t=−9.11; B is the CHEAPEST op atom (1.37 ≪
     C 1.77/K 1.57/S 1.75/W 1.62); pooled preserve 1.40 ≪ break 1.68 (cheaper=True).
  ◑ strict single-step n.s. — B-vs-C single t=−0.67 (directional B<C), exactly like OLMo
     (−1.25) and Gemma (−0.56). The sharp f-a-b↔f-b-a swap stays Qwen-family-specific.
  ⚠ wrinkle: B-vs-S single t=+3.70 (B>S — S atoms cheap on the clean single-step).
⇒ composition-is-native-order is now Qwen ⊗ OLMo ⊗ Gemma ⊗ Pythia = 4 classes, 2 arch
(gated SwiGLU + non-gated GPT-NeoX). GROSS universal; sharp single-step Qwen-specific.

★ FRAME-ROBUSTNESS IS SCALE-GATED, NOT CLASS-GATED: Pythia-2.8b (the SMALLEST class) is
frame-FRAGILE under result_of (composite collapses −9.11 → −1.96; single-step +1.38),
exactly like Qwen-8B (s239). Reinforces s239 — small models sit BELOW the frame-robustness
threshold regardless of architecture; the frame-robust strengthening is a large-model
(14B/32B) property.

CAVEATS (λ measure): Pythia-2.8b is the SMALLEST class (2.8B vs 13–31B others) → its weak
single-step conflates class-generality with small-scale; base model; deduped Pile;
B-vs-S single-step reversal. Composite + pooled metrics carry the gross claim.
