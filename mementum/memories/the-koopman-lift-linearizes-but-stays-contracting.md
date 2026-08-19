💡 The Koopman lift linearizes but stays contracting (s340, §P-DMD-KOOPMAN-LIFT).

Near-free re-analysis of the s338 §5a transport trajectories (saved H, no new
inference). Lift the last-token residual trajectory through a degree-2 polynomial
dictionary (324 observables on a P_LIFT=24 PCA frame) BEFORE DMD, re-estimate the
operator. Verdict STILL-CONTRACTING (a-priori modal 30). Two-sided:

- G1 RESIDUAL-DROP PASS: the lift GENUINELY helps. Next-state prediction residual
  drops linear 0.354 → poly 0.193 (rank 240, monotone in rank), beating the
  matched-dim random-lift null (dR=+0.265, p=0) AND shuffled-layer (gap +0.758,
  p=0). So the ~half-nonlinear remainder from s338 is REAL, layer-ordered,
  poly-liftable structure — not a capacity artifact. Answers s338 caveat 1 (+).

- G2 PERSISTENCE FAIL: persist_frac 0.000 (null 0.046), top|λ| 0.942, all
  contracting. NO persistent |λ|≈1 modes even after lifting; random lifts
  manufactured ~4.6% spurious persistence, poly produced ZERO. The pre-registered
  "persistent-mode ≡ sign-is-the-decision" does NOT surface in the operator
  spectrum, linear OR Koopman-lifted. Answers s338 caveat 2 (−, now airtight).

READING: homeostasis is nonlinear too; sign-is-the-decision is not an
operator-spectrum persistent mode. It lives in the thin late-decision mode below
rank/last-token resolution (s329/s336) or a non-operator register. FIFTH
tape-residency confirmation: value s317 · magnitude s335 · routing s336 ·
operator/decay s339 · Koopman-persistence s340.

BUILD-TIME LESSONS (reusable): (a) a degree-2 dictionary is NEVER Koopman-closed
for nonlinear state dynamics (driven-coord squares are degree-4) → measure the
next-STATE prediction residual (rank-r EDMD, read state back), NOT the full
lifted-vector residual, else the lift looks worse than linear. (b) The 324-dim
lift needs high DMD rank (240, not 80) to represent the operator / surface
conserved modes. (c) A conserved LINEAR mode co-conserves its square (degenerate
|λ|=1 subspace) → the register trap (norm vs decision) must gate on the MIN
square-fraction across persistent modes (∃ a non-norm mode), not the median.

Bounds: single model Qwen3-14B, last-token, poly-2 only, top|λ| 0.942 near the
0.95 bar. Harness scripts/experiments/koopman_lift.py; results
results/p_dmd_koopman_lift_s340/ (meta.json only, no npz).
