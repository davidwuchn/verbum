🎯 Composed model rotation decomposes into 3 eigenplanes

The total transformation across all 4 layers of the micro model
(composed as (I+O₃)(I+O₂)(I+O₁)(I+O₀)) decomposes into:

  Rotation:  ±48.8° (comp↔sel), ±13.9° (secondary), ±2.1° (fine)
  Stretch:   1.58× (amplify comp) to 0.76× (compress sel)
  Ratio:     2.08:1 composition:selection

The 48.8° rotation is in the comp(B)↔sel(K) eigenplane — the primary
beta-reduction plane. The model rotates the residual stream ~49° from
selection toward composition while amplifying composition 2× relative
to selection.

The rotation generator (Lie algebra element) has dominant coupling
comp↔sel at 0.678° per unit, with secondary couplings sel↔rout (0.209°)
and term↔rout (0.197°).

The comp→sel rotation angle accelerates through depth:
  L0: 2° → L1: 9° → L2: 14° → L3: 24°

This is the LENS profile in angular form. Deeper = stronger rotation.

Source: micro model Givens decomposition + eigenanalysis.
