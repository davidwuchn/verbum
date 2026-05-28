✅ Crystal backbone 30% zeros + etch beats float32 on loss (diverse data)

Session 167. Micro model on 1.2M diverse tokens (arithmetic, lambda,
lists, combinators). Four variants:

  A. Float32 (full GD):           loss 6.6828  L2:r90=13
  C. Backbone 30% + etch:         loss 6.4603  L2:r90=43  ← WINNER
  B. Backbone 20% + etch:         loss 6.7404  L2:r90=42
  D. Frozen 30% (no etch):        loss 7.0221  L2:r90=25

Backbone zeros from M-space SVD of teacher. Teacher signs for ±1.
Etch mechanism adapts signs via TD (direction EMA + flip tracking).
Gamma learned by GD (per-row scale).

Etch adds 0.56 over frozen signs (C vs D). M-space blurs when adapting
to diverse data (teacher's r90=13 was lambda-only), but loss improves.
The topology adapts to the actual data distribution — correct behavior.

Confirms session 166 finding with richer data and adaptive mechanism.
The crystal backbone + etch architecture is validated.
