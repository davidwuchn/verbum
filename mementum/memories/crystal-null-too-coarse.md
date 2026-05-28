💡 Crystal null space identifies correct dims but column-level zeros too coarse

Session 166. Crystal subspace lives in 15/128 dims (90% of crystal energy).
113 dims are crystal null space. Zeroing entire null-space columns gives
great gem sharpness (rank90=26) but terrible loss (7.13 — worst variant).

The problem: zeroing a column removes that dimension from EVERY row.
Some rows need non-crystal dimensions for position encoding, syntax,
content. M-noise zeros are per-position — different rows keep or discard
the same column. This per-position flexibility is why M-noise (C, loss
6.6972) beats crystal-null (F, loss 7.1312).

Crystal energy should be a PRIOR for M-noise scoring (weight noise scores
by crystal-null-ness) rather than a hard column mask. The crystal tells
you which dims are candidates; M-noise tells you which rows actually
need them zeroed. Structure × surgery = the right combination.
