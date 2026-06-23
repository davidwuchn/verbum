💡 DISTRIBUTED confirmation (INLP) that the s249/s250 applicative-C routing field
is a READOUT REGISTER, not the object-application mechanism (Qwen3-14B, s250 cont.,
program_cfield_subspace_ablation.py).

The s250 single-direction null left one caveat: a rank-1 diff-of-means is the wrong
probe if C is distributed. INLP (Ravfogel 2020) iteratively fits a linear C-probe
(C-present vs C-absent, L30 content-mean residuals) and projects it out, building the
k=16 subspace carrying ALL linearly-decodable C; ablate span(W) at L30+L31 vs a random
k-dim subspace.

ERASURE ✓: C-decodability 0.9185 → 0.6667 (=majority); curve collapses at iteration 1
→ linear C-presence is essentially RANK-1 (strongly readable, 92%, along ONE direction).
NECESSITY c=2 ✓: ablate span(W) crashes downstream z(C) (Δ -5.10 vs rand +0.09, t=-84) —
this time we removed the readable signal at source (s250 single-dir RAISED it +0.85).
DIFFERENTIAL ✗ (REVERSED again): net-KL c2 4.77 < c0 5.83, t=-2.47 — erasing ALL
linearly-decodable C does NOT selectively hurt object-application; objectless c0 is
perturbed MORE than two-object c2.

⇒ DECISIVE, distributed-robust: the applicative-C field is a register/correlate, NOT
the mechanism — rank-1 (s250) AND rank-16 INLP agree. decodability ≠ causality, doubly
proven. CAVEAT: INLP erases only LINEAR decodability — a nonlinear C-encoding is the
remaining escape hatch. NEXT: nonlinear/SAE C-ablation; hunt the mechanism in attention
OV (value register, s127/s206), not the FFN C-field.
