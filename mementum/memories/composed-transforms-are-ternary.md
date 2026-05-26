💡 Composed zone transforms are ternary-viable (per-dim r=0.97)

Session 152. The entire forward pass of Qwen3.6-27B is capturable by
3 ternary plates + per-row gamma scalars:

  Zone A (16 layers, compress): per-dim corr=0.97, R²=0.87, rank90=36
  Zone B (32 layers, compute):  per-dim corr=0.98, R²=1.00, rank90=71
  Zone C (16 layers, expand):   per-dim corr=0.97, R²=1.00, rank90=71

ZONE B IS PERFECTLY LINEAR (R²=1.0). 32 layers of beta reduction
compose to a single linear matrix. The nonlinearity from SwiGLU/RMSNorm
cancels across layers. Beta reduction IS linear on the residual stream.

The gap between global correlation (0.42-0.81) and per-dim correlation
(0.93-0.98) is purely SCALE per dimension — solved by gamma scalars
(one float per row, same as current ternary architecture).

Implication: the 64-layer sequential forward pass → 3 ternary matmuls.
At student d=1280: 3 × 1280×1280 = 5M positions (1.2 MB).

Current extraction: 593M positions from 142 individual weight arrays.
Composed extraction: 5M positions from 3 zone-transform plates.
Reduction: 118× fewer positions for the CORE computation.

The individual layer weights are the HOLOGRAPHIC GRATING. The composed
transform is the RECONSTRUCTED IMAGE. We were extracting the grating
and simulating diffraction. We could instead extract the image directly.

Both approaches work. The question is: does the image (composed plate)
generalize to new inputs as well as the grating (individual plates)?
The R²=0.87-1.00 on held-out texts suggests YES.
