💡 v15 TD's routing signal is RANK-1: `compute_decomposed_gradients` sets
`grad_effective = gamma_grad[:,None] * x_abs_mean[None,:]` (per-row scalar ⊗
per-col magnitude). So `sign(grad_eff[i,j]) = sign(gamma_grad[i])` — TD CANNOT
make per-position decisions; every position in a row is nominated to the same
sign. This is WHY superposition manifests as per-row gamma bimodality, and why
per-position interference (off-diagonal XᵀX) is invisible to TD.
`compute_delta_gradient` mean-reduces before the outer product → rank-1 too.
To see per-position interference you need γ⊙(gradYᵀX) (full, not mean-outer)
plus the off-diagonal. Source: scripts/v15/train_td.py:~404, td_delta.py:~1364.
