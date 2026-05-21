❌ Weight signs in SVD-projected subspaces are 50% correlated across
layers (= random noise). Three independent projection methods confirmed:
per-matrix SVD, fixed random projection, L0-SVD as shared basis. The
crystal lives in ACTIVATION space (how inputs transform through weights)
not WEIGHT space (what signs the weights store). Per-matrix SVD finds
matrix-specific principal directions that are unrelated across matrices.
The etch-from-weights approach is a dead end for cross-model transfer.
Activation-space distillation (Procrustes-aligned hidden states) is the
correct path. Session 129.
