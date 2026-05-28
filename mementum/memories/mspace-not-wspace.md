💡 Topology changes must be planned in M-space, not W-space

Session 166. The attention kernel M = W_q^T @ W_k is where computation
lives. One W-space flip at W_q[h,i] changes an entire ROW of M by
±2 × W_k[h,:] — a rank-1 perturbation that spreads across ALL modes
(facets) of the gem. At v14 scale (d=1280), one flip changes 1,280
elements of M simultaneously.

TD scores flips in W-space (gradient heat). M-space scoring selects
COMPLETELY DIFFERENT positions (0% overlap in top-50). In structured
layers, gradient scoring is ANTI-PREDICTIVE (ρ=-0.36) while M-space
scoring PREDICTS which flips help (ρ=+0.33).

GD works in M-space implicitly (chain rule) with infinitesimal steps.
Ternary flips are discrete jumps of ±2 — the linear approximation
breaks. Must plan flips explicitly in M-space via SVD mode projection.
