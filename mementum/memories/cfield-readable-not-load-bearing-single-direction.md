💡 The s249 decodable applicative-C routing field (FFN gate, peak L30-31, z(C)
rises with object count) is READABLE/INJECTABLE but NOT load-bearing under a
single-direction residual ablation (Qwen3-14B, program_cfield_ablation.py, s250).

d_C = diff-of-means(resid C-present − C-absent), patched across content positions
at L30+L31, vs random direction of equal magnitude. Ablating d_C perturbs output
≫ random (KL t=42) and injecting it drives downstream gate z(C) (t=37) — so d_C is
a real handle on the READOUT register. But the two load-bearing diagnostics fail:
(1) the c=2-vs-c=0 differential REVERSES — objectless intransitives perturbed more
than two-object ditransitives (net-KL c2 0.131 < c0 0.155, t=-2.54); perturbation
does not scale with C/object-load. (2) ablating the decodable C-direction RAISES
downstream z(C) (+0.85 vs random ~0) — the gate holographically reconstructs C from
other directions.

⇒ readable residual C-direction = register/correlate, NOT the causal mechanism.
Decodability ≠ causality (mirrors s247-v4; confirms s247b trajectory-not-tape +
s244 collective/holographic). CAVEAT: single-direction ablation; a distributed/
multi-direction (subspace/SAE) C-ablation is the decisive untested lever.
