❌ Zone-ablation instrument lessons (P-TYPE-1b v1→v4, one session,
bc1d242→0961819): (1) `p or 1.0` treats p=0.0 as missing — falsy-zero
excluded the MOST significant layers from band detection; two runs shipped
accidental sub-bands. Use `p if p is not None else 1.0`. (2) Never compare
subspace ablations at full projection — variance along them differs ×10⁴;
match on REALIZED removed energy (E = mean(coeff²)·‖σ⊙v‖², accumulated live
in the hooks). Planned-vs-realized drifts ~×25 between capture exemplars and
behavioral text — realized is the honest number. (3) Amplified random
steering (α≫1) CASCADES across stacked layer hooks (realized 10¹⁰⁺ E/tok).
(4) Absolute-dose grids ≻ subspace-relative budgets — anchor to the model's
tolerance window, not the subspace's energy. (5) Breakage gates on
tiny-surprisal baselines must use top-1 ACCURACY, not surprisal ratios.
(6) Class-centroid subspaces all share the dominant lattice axis — a
"role-specific" slice is mostly common component; measure the overlap before
claiming role identity.
