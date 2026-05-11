❌ Sigmoid gates on high-norm inputs saturate instantly and die. CycleContinue
(Linear 768→1 + sigmoid) received register input with ||x|| ≈ 27.7. After one
gradient step, logit ≈ 30, sigmoid gradient ≈ 0, gate locked at 1.0 forever.
Fix: RMSNorm input + tanh(·)×4.0 clamp → gate ∈ [0.018, 0.982], always learnable.
Rule: any sigmoid gate needs normalized input or logit clamping. Session 076.
