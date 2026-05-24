💡 Parity loss with multiple zone targets on one set of embeddings creates gradient cancellation.

Zone A wants K↔B cos=0.08, Zone C wants 0.52. Equal weighting → net gradient ≈ 0 → loss stuck at 1.167 for 2000 steps. Eigendecomposition amplifies inter-zone differences nonlinearly — worse than simple MSE.

Fix: `parity_zone_lambdas = (0.0, 1.0, 0.0)` — Zone B only. Crystal MSE handles 3-zone compromise (linear, well-behaved). Cross-zone lens rotation handles inter-zone differences. Parity protects ONE dimensional hierarchy.

First attempt (0.1, 1.0, 0.3) created a 2-way see-saw — parity stuck at 0.291. Only full elimination of A/C parity worked: 1.167 → 0.039.

General principle: any loss involving eigendecomposition or other nonlinear structure extraction must operate on ONE consistent target, not an average of conflicting targets. Linear losses (MSE) can average; nonlinear losses cannot.
